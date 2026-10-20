"""Final V6 integrity, explicitly run only after the immutable pair is ready.

One FFmpeg video framemd5 + audio null decode per new master. Packet probes and
AAC ADTS hashes use compressed streams, not another video decode. No ASR,
rendering, extraction, mix, upload or unrelated process control is performed.
Default/help and --self-test do not start media jobs.
"""
from pathlib import Path
from fractions import Fraction
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
import argparse
import ctypes
import hashlib
import json
import os
import re
import subprocess
import uuid

R=Path(__file__).resolve().parents[4]
P=R/'projects/game-math-euler-axis-angle'
H=Path(__file__).parent
O=P/'production/local/revision-v6'
Q=O/'qa'
FLAGS=(subprocess.CREATE_NO_WINDOW|subprocess.BELOW_NORMAL_PRIORITY_CLASS) if os.name=='nt' else 0

def read(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def rel(path):return Path(path).resolve().relative_to(R).as_posix()
def now():return datetime.now(timezone.utc).isoformat()
def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(1048576),b''):h.update(block)
    return h.hexdigest()
def save(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_name(path.name+'.'+uuid.uuid4().hex+'.tmp')
    tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    os.replace(tmp,path)
def selected():
    control=read(R/'shared/publishing/video-production-control.json')
    assert control['selectedVideo']==P.name and control['newProductionAuthorization']['fullProductionAuthorized']
    assert not (R/'shared/output/GPU_HANDOFF.json').exists(),'Another costly-job lease is active; preserve it and wait for handoff'
def command(args):
    return subprocess.check_output(list(map(str,args)),cwd=R,creationflags=FLAGS)
def probe(path):return json.loads(command(['ffprobe','-v','error','-show_streams','-show_format','-of','json',path]))
def packets(path,stream):
    return json.loads(command(['ffprobe','-v','error','-select_streams',stream,'-show_packets','-show_entries','packet=pts,dts,duration','-of','json',path]))['packets']
def packet_digest(rows):return hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def packet_times(rows,time_base):
    tb=Fraction(time_base)
    return [tuple(Fraction(int(row[k]))*tb for k in ['pts','dts','duration']) for row in rows]


def verify_video_packets(rows,n,time_base):
    step=Fraction(1,60)/Fraction(time_base)
    assert step.denominator==1,('Nonintegral native video presentation step',time_base)
    step=int(step)
    assert len(rows)==n,('Video packets',len(rows),n)
    assert sorted(int(row['pts']) for row in rows)==[i*step for i in range(n)],'Packet presentation times have a gap, duplicate or nonzero start'
    assert all(int(row['duration'])==step for row in rows),'Packet durations are not uniformly1/60s'
    assert all(int(b['dts'])>int(a['dts']) for a,b in zip(rows,rows[1:])),'Decode packet times are not strictly monotonic'
    return dict(presentationStart=0,presentationStep=step,timeBase=time_base,packets=n,ptsUniform=True,dtsStrictlyMonotonic=True)


def parse_decoded_frames(text,n):
    match=re.search(r'^#tb 0: (\d+/\d+)$',text,re.M)
    assert match,'Decoded framehash has no declared time base'
    tb=Fraction(match[1]);rows=[]
    for line in text.splitlines():
        if not line.strip() or line.startswith('#'):continue
        parts=[x.strip() for x in line.split(',')]
        assert len(parts)==6 and re.fullmatch('[0-9a-f]{32}',parts[5]),line
        row=dict(stream=int(parts[0]),dts=int(parts[1]),pts=int(parts[2]),duration=int(parts[3]),size=int(parts[4]),md5=parts[5])
        i=len(rows)
        assert row['stream']==0 and row['pts']*tb==Fraction(i,60) and row['dts']*tb==Fraction(i,60),('Decoded PTS/DTS gap, duplicate or nonzero start',i,row,tb)
        assert row['duration']*tb==Fraction(1,60),('Decoded frame duration',i,row,tb)
        assert row['size']==1920*1080*3//2,('Decoded raster size',i,row['size'])
        rows.append(row)
    assert len(rows)==n,('Decoded video frame count',len(rows),n)
    return rows,match[1]


def aac_hash(path):
    selected();h=hashlib.sha256()
    proc=subprocess.Popen(['ffmpeg','-hide_banner','-v','error','-nostdin','-i',str(path),'-map','0:a:0','-c:a','copy','-f','adts','-'],cwd=R,stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=FLAGS)
    for block in iter(lambda:proc.stdout.read(1048576),b''):h.update(block)
    error=proc.stderr.read();code=proc.wait()
    assert code==0 and not error.strip(),error.decode(errors='replace')
    return h.hexdigest()


@contextmanager
def immutable_reads(paths):
    """Windows read handles allow other readers but deny master replacement."""
    handles=[]
    if os.name!='nt':
        yield
        return
    from ctypes import wintypes
    kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    kernel.CreateFileW.argtypes=[wintypes.LPCWSTR,wintypes.DWORD,wintypes.DWORD,wintypes.LPVOID,wintypes.DWORD,wintypes.DWORD,wintypes.HANDLE]
    kernel.CreateFileW.restype=wintypes.HANDLE
    kernel.CloseHandle.argtypes=[wintypes.HANDLE];kernel.CloseHandle.restype=wintypes.BOOL
    try:
        for path in paths:
            handle=kernel.CreateFileW(str(path),0x80000000,1,None,3,0x80,None)
            if handle==ctypes.c_void_p(-1).value:raise ctypes.WinError(ctypes.get_last_error())
            handles.append(handle)
        yield
    finally:
        for handle in handles:kernel.CloseHandle(handle)


def decode(kind,path,digest,n,tb):
    selected();dest=Q/(kind+'-framehash.txt');receipt=Q/(kind+'-decode.json');log=Q/(kind+'-decode.log');progress=Q/(kind+'-decode.progress')
    contract=dict(sha256=digest,frames=n,width=1920,height=1080,fps=60,outputTimeBase=tb,implementationSha256=sha(Path(__file__)))
    if receipt.exists():
        old=read(receipt)
        assert old['inputs']==contract,'A different existing decode attempt must be preserved/investigated; no automatic duplicate decode'
        assert old.get('fullDecodePassed') and old['returnCode']==0 and old.get('audioNullDecodePassed'),'A failed/interrupted attempt needs investigation, not an automatic repeat'
        assert dest.exists() and sha(dest)==old['frameHashSha256']
        parse_decoded_frames(dest.read_text(encoding='utf8'),n)
        print(kind,'reuses successful identical single-decode proof',flush=True)
        return old
    assert not dest.exists(),'Unreceipted framehash must be investigated before duplicate decoding'
    args=['ffmpeg','-hide_banner','-loglevel','error','-nostdin','-xerror','-err_detect','explode','-copyts','-threads','2','-i',str(path),
          '-map','0:v:0','-an','-sn','-dn','-c:v','rawvideo','-threads:v','1','-pix_fmt','yuv420p','-fps_mode','passthrough','-enc_time_base:v',tb,'-f','framemd5','-y',str(dest),
          '-map','0:a:0','-vn','-sn','-dn','-c:a','pcm_s16le','-ar','48000','-ac','2','-f','null','-','-progress',str(progress),'-nostats']
    start=now()
    with log.open('wb') as errors:
        proc=subprocess.Popen(args,cwd=R,stdout=subprocess.DEVNULL,stderr=errors,creationflags=FLAGS)
        report=dict(kind=kind,file=rel(path),inputs=contract,startedAt=start,pid=proc.pid,status='running',fullDecodePassed=False,audioNullDecodePassed=False,returnCode=None,command=args)
        save(receipt,report);print(kind,'single video/audio decode started; PID',proc.pid,flush=True)
        code=proc.wait()
    clean_log=not log.read_bytes().strip()
    passed=code==0 and clean_log
    report.update(completedAt=now(),returnCode=code,status='complete' if passed else 'failed',fullDecodePassed=passed,audioNullDecodePassed=passed,
                  frameHashFile=rel(dest),frameHashSha256=sha(dest) if dest.exists() else None,log=rel(log),progress=rel(progress),videoDecodePasses=1)
    save(receipt,report)
    assert passed,log.read_text(encoding='utf8',errors='replace')[-4000:]
    parse_decoded_frames(dest.read_text(encoding='utf8'),n)
    return report


def verify(workers):
    selected();timeline_path=H/'timeline.json';timeline=read(timeline_path);n=timeline['totalFrames']
    assert (timeline['fps'],timeline['width'],timeline['height'],timeline['introFrames'],timeline['outroFrames'])==(60,1920,1080,120,600)
    assert timeline['sceneCount']==41 and timeline['beatCount']==106 and timeline['plannedHoldFrames']==527*60
    assert n==120+sum(s['frames'] for s in timeline['scenes'])+600
    masters={kind:O/('euler-'+kind+'.mp4') for kind in ['clean','captioned']}
    pair_receipts={kind:path.with_suffix('.json') for kind,path in masters.items()}
    inputs=dict(implementationSha256=sha(Path(__file__)),timelineSha256=sha(timeline_path),audioFile=rel(O/'final-mix.m4a'),audioFileSha256=sha(O/'final-mix.m4a'),
                captions={name:dict(file=rel(O/name),sha256=sha(O/name)) for name in ['captions.ko.ass','captions.en.ass','captions.ko.srt','captions.en.srt']},
                mixReceiptSha256=sha(O/'audio-build.json'),pairReceiptSha256={k:sha(v) for k,v in pair_receipts.items()})
    expected_audio=O/'final-mix.m4a';info=probe(expected_audio);audio=next(s for s in info['streams'] if s['codec_type']=='audio')
    assert (audio['codec_name'],int(audio['sample_rate']),audio['channels'])==('aac',48000,2)
    expected_packets=packet_times(packets(expected_audio,'a:0'),audio['time_base']);expected_aac=aac_hash(expected_audio)
    sources={};source_base=R/'projects/game-reward-planning/production/local/reference-preserving-v2/edit'
    for name,count in [('branding',120),('membership',600)]:
        path=source_base/(name+'.mp4');v=next(s for s in probe(path)['streams'] if s['codec_type']=='video')
        assert (v['width'],v['height'],v['r_frame_rate'],int(v['nb_frames']))==(1920,1080,'60/1',count)
        sources[name]=dict(file=rel(path),sha256=sha(path),frames=count)
    preflight=[]
    for kind,path in masters.items():
        selected();receipt=read(pair_receipts[kind]);digest=sha(path)
        assert receipt['file']==rel(path) and receipt['sha256']==digest
        assert receipt['inputs']['audioSha256']==inputs['audioFileSha256'] and receipt['inputs']['timelineSha256']==inputs['timelineSha256']
        original_sources=receipt['inputs']['files']
        assert tuple(original_sources[0])==(sources['branding']['file'],sources['branding']['sha256'])
        assert tuple(original_sources[-1])==(sources['membership']['file'],sources['membership']['sha256'])
        assert len(original_sources)==43,'One original branding +41complete scene clips +one original membership'
        info=probe(path);assert len(info['streams'])==2
        video=next(s for s in info['streams'] if s['codec_type']=='video');a=next(s for s in info['streams'] if s['codec_type']=='audio')
        assert (video['codec_name'],video['width'],video['height'],video['r_frame_rate'],video['avg_frame_rate'],int(video['nb_frames']))==('h264',1920,1080,'60/1','60/1',n)
        assert video['pix_fmt']=='yuv420p' and video.get('sample_aspect_ratio','1:1')=='1:1'
        assert Fraction(video['start_pts'])*Fraction(video['time_base'])==0
        assert (a['codec_name'],int(a['sample_rate']),a['channels'])==('aac',48000,2)
        assert abs(float(a['duration'])-n/60)<=1024/48000+.005,'Audio track duration exceeds one AAC-frame padding allowance'
        assert abs(float(info['format']['duration'])-n/60)<=1024/48000+.005
        vp=packets(path,'v:0');packet_report=verify_video_packets(vp,n,video['time_base'])
        ap=packet_times(packets(path,'a:0'),a['time_base'])
        assert ap==expected_packets,'Encoded audio packet timing differs from final-mix.m4a'
        aac=aac_hash(path);assert aac==expected_aac,'AAC stream differs; final mix/ASR evidence cannot be reused'
        preflight.append((kind,path,digest,info,video,packet_report,packet_digest(vp),aac))
    outputs=[]
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures={k:pool.submit(decode,k,p,d,n,v['time_base']) for k,p,d,info,v,pr,ph,aac in preflight}
        for kind,path,digest,info,video,packet_report,packet_sha,aac in preflight:
            proof=futures[kind].result()
            assert sha(path)==digest and sha(timeline_path)==inputs['timelineSha256']
            assert sha(pair_receipts[kind])==inputs['pairReceiptSha256'][kind]
            output=dict(kind=kind,file=rel(path),sha256=digest,bytes=path.stat().st_size,width=1920,height=1080,fps=60,frames=n,startSeconds=0,
                        fullDecodePassed=True,audioNullDecodePassed=True,ptsMonotonicAndUniform=True,decodedFrameTimesChecked=n,compressedPacketTiming=packet_report,
                        compressedPacketTimingSha256=packet_sha,audioSampleRate=48000,audioChannels=2,aacSha256=aac,exactAACStreamEqual=True,audioPacketTimingExactlyEqual=True,
                        durationSeconds=float(info['format']['duration']),decodeReceipt=rel(Q/(kind+'-decode.json')),frameHashFile=proof['frameHashFile'],frameHashSha256=proof['frameHashSha256'],fullDecodePasses=1)
            outputs.append(output);save(Q/'integrity-progress.json',dict(inputs=inputs,status='complete' if len(outputs)==2 else 'partial',outputs=outputs))
            print(kind,'passed native FHD60,',n,'decoded frames, identical expected AAC',flush=True)
    for name,row in sources.items():assert sha(R/row['file'])==row['sha256']
    assert sha(expected_audio)==inputs['audioFileSha256']
    assert all(sha(O/name)==row['sha256'] for name,row in inputs['captions'].items())
    assert sha(O/'audio-build.json')==inputs['mixReceiptSha256']
    assert sha(Path(__file__))==inputs['implementationSha256']
    report=dict(schemaVersion=1,revision='article-flow-v6',completedAt=now(),inputs=inputs,outputs=outputs,frames=n,fps=60,exactAACStreamEqual=True,aacSha256=expected_aac,
                fullDecodePassesPerMaster=1,sourceASRRerun=False,newASRRun=False,brandingAndMembership=dict(sources=sources,authenticatedAssemblySourceSha256Equal=True,sourceFrameCountsEqual=True,
                    proofScope='Existing source files are SHA256-identical and authenticated as first/last packet-copy assembly inputs. Independent reference-pixel equality is not claimed by this verifier; root current final visual review covers their visible content.'),
                humanWholeListening='pending unless separately completed',visualMeaningAndCaptionReview='separate current root/footage review; this technical check does not approve semantic content',status='technical-integrity-passed')
    save(Q/'integrity.json',report)
    print('Integrity receipt:',rel(Q/'integrity.json'),sha(Q/'integrity.json'),flush=True)


def self_test():
    # Pure synthetic metadata; no media, real output or filesystem mutation.
    line='#tb 0: 1/60000\n'+''.join(f'0, {i*1000}, {i*1000}, 1000, 3110400, '+('a'*32)+'\n' for i in range(3))
    rows,tb=parse_decoded_frames(line,3);assert len(rows)==3 and tb=='1/60000'
    failures=0
    for broken in [line.replace('0, 1000, 1000','0, 0, 0'),line.replace('1000, 3110400','999, 3110400',1),line.replace('0, 0, 0','0, 1000, 1000',1),line.rsplit('\n',2)[0]+'\n']:
        try:parse_decoded_frames(broken,3)
        except AssertionError:failures+=1
    assert failures==4
    pp=[dict(pts=p,dts=d,duration=1000) for p,d in [(0,-2000),(2000,-1000),(1000,0)]]
    verify_video_packets(pp,3,'1/60000')
    for field in ['pts','duration']:
        altered=[dict(x) for x in pp];altered[1][field]+=1
        try:verify_video_packets(altered,3,'1/60000')
        except AssertionError:failures+=1
    assert failures==6
    print('Pure CPU verifier self-test passed: valid reordered packets +decoded PTS, six broken contracts rejected; media jobs0')


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--run',action='store_true');ap.add_argument('--self-test',action='store_true');ap.add_argument('--workers',type=int,choices=[1,2],default=2);args=ap.parse_args()
    if args.self_test:self_test();return
    if not args.run:ap.print_help();return
    selected();Q.mkdir(parents=True,exist_ok=True);lock=Q/'verify.lock.json';token=uuid.uuid4().hex
    with lock.open('x',encoding='utf8') as f:json.dump(dict(pid=os.getpid(),token=token,startedAt=now()),f)
    try:
        required=[O/'euler-clean.mp4',O/'euler-captioned.mp4',O/'final-mix.m4a',H/'timeline.json',O/'euler-clean.json',O/'euler-captioned.json']
        assert all(p.exists() for p in required),'Final current immutable pair/receipts are not ready'
        with immutable_reads(required):verify(args.workers)
    finally:
        if lock.exists() and read(lock).get('token')==token:lock.unlink()


if __name__=='__main__':main()
