"""One current-master decode per output, with authenticated retained-pixel reuse.

Video framemd5 and audio null decode share one FFmpeg invocation per output.
Packet inspection and ADTS hashing use compressed streams, never a second video
decode. Unchanged successful decode receipts are reused; ASR is never launched.
"""
from pathlib import Path
from fractions import Fraction
from datetime import datetime, timezone
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor
import hashlib, json, os, re, subprocess, sys, uuid

ROOT=Path(__file__).resolve().parents[4]
PROJECT=ROOT/'projects/game-math-euler-axis-angle'
HERE=Path(__file__).resolve().parent
OUT=PROJECT/'production/local/revision-v5'
QA=OUT/'qa'
CONTROL=ROOT/'shared/publishing/video-production-control.json'
PLAN=HERE/'assembly-plan.json'
PAIR=OUT/'pair-source.json'
OLD_QA=PROJECT/'production/local/revision-v3/qa'
PRIOR_PROOF=PROJECT/'production/revision-v4/video-reuse-proof.json'
FLAGS=(subprocess.CREATE_NO_WINDOW|subprocess.BELOW_NORMAL_PRIORITY_CLASS) if os.name=='nt' else 0

def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def rel(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def now():return datetime.now(timezone.utc).isoformat()
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def save(p,v):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 tmp=p.with_name(p.name+'.'+uuid.uuid4().hex+'.tmp')
 tmp.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');os.replace(tmp,p)
def command(cmd):return subprocess.check_output([str(v) for v in cmd],cwd=ROOT,creationflags=FLAGS)
def selected():
 assert read(CONTROL)['selectedVideo']==PROJECT.name,'Selected video changed; no media job started'
 assert not (ROOT/'shared/output/GPU_HANDOFF.json').exists(),'Exclusive voice/GPU lease is active'
def probe(p):return json.loads(command(['ffprobe','-v','error','-show_streams','-show_format','-of','json',p]))
def packets(p,stream):
 return json.loads(command(['ffprobe','-v','error','-select_streams',stream,'-show_packets','-show_entries','packet=pts,dts,duration','-of','json',p]))['packets']
def adts_sha(p):
 selected();h=hashlib.sha256()
 cmd=['ffmpeg','-v','error','-i',str(p),'-map','0:a:0','-c:a','copy','-f','adts','-']
 process=subprocess.Popen(cmd,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=FLAGS)
 for b in iter(lambda:process.stdout.read(1024*1024),b''):h.update(b)
 err=process.stderr.read();rc=process.wait();assert rc==0,err.decode(errors='replace')
 return h.hexdigest()
def parsed_frames(p,n):
 lines=Path(p).read_text(encoding='utf-8').splitlines()
 assert '#tb 0: 1/60' in lines,'framemd5 time base must retain60Hz presentation ticks'
 rows=[]
 for line in lines:
  if not line.strip() or line.startswith('#'):continue
  a=[v.strip() for v in line.split(',')]
  assert len(a)==6 and re.fullmatch(r'[0-9a-f]{32}',a[5]),line
  rows.append(dict(stream=int(a[0]),dts=int(a[1]),pts=int(a[2]),duration=int(a[3]),size=int(a[4]),md5=a[5]))
 assert len(rows)==n,('Decoded frame count',len(rows),n)
 assert all(r['stream']==0 and r['dts']==i and r['pts']==i and r['duration']==1 and r['size']==1920*1080*3//2 for i,r in enumerate(rows)),'Decoded presentation timestamps, duration or dimensions differ'
 return rows
def full_decode(kind,p,digest):
 selected();dest=QA/f'{kind}-framehash.txt';receipt=QA/f'{kind}-decode.json';log=QA/f'{kind}-decode.log';progress=QA/f'{kind}-decode.progress'
 cmd=['ffmpeg','-hide_banner','-loglevel','error','-xerror','-err_detect','explode','-threads','2','-i',str(p),
      '-map','0:v:0','-an','-sn','-dn','-c:v','rawvideo','-threads:v','1','-pix_fmt','yuv420p','-fps_mode','passthrough','-f','framemd5','-y',str(dest),
      '-map','0:a:0','-vn','-sn','-dn','-c:a','pcm_s16le','-f','null','-','-progress',str(progress),'-nostats']
 if receipt.exists():
  cached=read(receipt)
  if cached.get('sha256')==digest:
   assert cached.get('returnCode')==0 and cached.get('fullDecodePassed'),'Existing failed/interrupted decode requires investigation, not an automatic repeat'
   assert dest.exists() and sha(dest)==cached['frameHashSha256'],'Cached decode proof changed; do not silently repeat'
   print(json.dumps(dict(kind=kind,status='reusing successful current-output single decode',sha256=digest)),flush=True)
   return cached
 assert not dest.exists(),'Unreceipted decode artifact exists; inspect before starting a duplicate decode'
 start=now()
 with log.open('wb') as stderr:
  process=subprocess.Popen(cmd,cwd=ROOT,stdout=subprocess.DEVNULL,stderr=stderr,creationflags=FLAGS)
  running=dict(kind=kind,sha256=digest,startedAt=start,pid=process.pid,command=cmd,status='running',fullDecodePassed=False,returnCode=None)
  save(receipt,running);print(json.dumps(dict(kind=kind,status='full decode started',pid=process.pid,startedAt=start)),flush=True)
  rc=process.wait()
 running.update(completedAt=now(),returnCode=rc,status='complete' if rc==0 else 'failed',fullDecodePassed=rc==0,audioNullDecodePassed=rc==0,frameHashFile=rel(dest),frameHashSha256=sha(dest) if dest.exists() else None,log=rel(log),progress=rel(progress))
 save(receipt,running)
 assert rc==0,log.read_text(encoding='utf-8',errors='replace')[-3000:]
 assert not log.read_bytes().strip(),'FFmpeg emitted error diagnostics despite a successful exit'
 return running

@contextmanager
def immutable_master_reads(paths):
 # Allow simultaneous readers (including Drive upload), but deny overwriting
 # or deleting either authenticated input while the final QA pass consumes it.
 handles=[]
 if os.name=='nt':
  import ctypes
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
 else:yield

def main():
 selected();QA.mkdir(parents=True,exist_ok=True)
 lock=QA/'verify.lock.json';token=uuid.uuid4().hex
 with lock.open('x',encoding='utf-8') as f:json.dump(dict(pid=os.getpid(),token=token,startedAt=now()),f)
 try:
  pair=read(PAIR)
  with immutable_master_reads([ROOT/o['file'] for o in pair['outputs'].values()]):verify()
 finally:
  if lock.exists() and read(lock).get('token')==token:lock.unlink()

def verify():
 plan,pair=read(PLAN),read(PAIR);n=plan['totalFrames'];assert n==93100 and plan['fps']==60
 inputs=dict(assemblyPlanSha256=sha(PLAN),pairSourceSha256=sha(PAIR),audioFileSha256=sha(ROOT/plan['audio']['file']),timelineSha256=sha(PROJECT/'production/revision-v3/timeline.json'))
 assert inputs['assemblyPlanSha256']==pair['inputs']['assemblyPlanSha256']
 assert inputs['audioFileSha256']==plan['audio']['sha256']==pair['inputs']['audioSha256']
 assert inputs['timelineSha256']==plan['timelineSha256']==pair['inputs']['timelineSha256']
 prior=read(PRIOR_PROOF);meta=read(OLD_QA/'repaired-framehash.json');old_hash=OLD_QA/'repaired-framehash.txt'
 assert sha(old_hash)==meta['frameHashSha256']
 assert prior['frames']==n and prior['fps']==60 and not prior['visualChanges'] and not prior['captionTimingChanges']
 old_rows=parsed_frames(old_hash,n)
 for kind in ['clean','captioned']:
  prior_stream=next(s for s in prior['streams'] if s['kind']==kind)
  assert prior_stream['exactCompressedVideoStreamEqual'] is True
  assert prior_stream['currentFile']==plan['baseline'][kind]['file'] and prior_stream['currentSha256']==plan['baseline'][kind]['sha256']
  assert sha(ROOT/prior_stream['currentFile'])==prior_stream['currentSha256'],'Authenticated baseline changed'
  if kind=='captioned':assert prior_stream['previousSha256']==meta['videoSha256'],'V3 decoded proof is not tied to V4 baseline'
 audio=ROOT/plan['audio']['file'];ai=probe(audio);aa=next(s for s in ai['streams'] if s['codec_type']=='audio')
 assert aa['codec_name']=='aac' and int(aa['sample_rate'])==48000 and aa['channels']==2
 base_packets=packets(audio,'a:0');base_timing=[tuple(Fraction(int(p[k]))*Fraction(aa['time_base']) for k in ['pts','dts','duration']) for p in base_packets]
 base_aac=adts_sha(audio)
 outputs=[];streams=[];preflight=[]
 for kind in ['clean','captioned']:
  selected();p=ROOT/pair['outputs'][kind]['file'];digest=sha(p);assert digest==pair['outputs'][kind]['sha256']
  info=probe(p);assert len(info['streams'])==2
  v=next(s for s in info['streams'] if s['codec_type']=='video');a=next(s for s in info['streams'] if s['codec_type']=='audio')
  assert (v['codec_name'],v['width'],v['height'],v['r_frame_rate'],v['avg_frame_rate'],int(v['nb_frames']))==('h264',1920,1080,'60/1','60/1',n)
  assert (v['pix_fmt'],v['color_range'],v['color_space'],v['sample_aspect_ratio'])==('yuv420p','tv','bt709','1:1')
  assert a['codec_name']=='aac' and int(a['sample_rate'])==48000 and int(a['channels'])==2
  assert abs(float(a['duration'])-n/60)<.1
  pp=packets(p,'v:0');tb=Fraction(v['time_base']);step=Fraction(1,60)/tb;assert step.denominator==1
  assert len(pp)==n and sorted(int(x['pts']) for x in pp)==[i*int(step) for i in range(n)]
  assert all(int(x['duration'])==step for x in pp)
  assert all(int(b['dts'])>int(a0['dts']) for a0,b in zip(pp,pp[1:]))
  ap=packets(p,'a:0');audio_timing=[tuple(Fraction(int(x[k]))*Fraction(a['time_base']) for k in ['pts','dts','duration']) for x in ap]
  assert audio_timing==base_timing,'Compressed audio timestamps or durations differ from baseline mix'
  aac=adts_sha(p);assert aac==base_aac,'AAC payload changed; old ASR must not be reused'
  preflight.append((kind,p,digest,info,pp,aac))
 with ThreadPoolExecutor(max_workers=2) as pool:
  futures={kind:pool.submit(full_decode,kind,p,digest) for kind,p,digest,info,pp,aac in preflight}
  for kind,p,digest,info,pp,aac in preflight:
   decode=futures[kind].result();rows=parsed_frames(ROOT/decode['frameHashFile'],n)
   assert sha(p)==digest and sha(PAIR)==inputs['pairSourceSha256'] and sha(PLAN)==inputs['assemblyPlanSha256'],'Current master or assembly changed during QA'
   output=dict(kind=kind,file=rel(p),sha256=digest,bytes=p.stat().st_size,frames=n,width=1920,height=1080,fps=60,
               fullDecodePassed=True,audioNullDecodePassed=True,ptsMonotonicAndUniform=True,ptsEvidence='All decoded presentation ticks0..93099 and compressed packet PTS, DTS and durations checked; no second video decode.',
               audioSampleRate=48000,audioChannels=2,sampleRate='48000',channels=2,audioPacketTimingExactlyEqual=True,
               aacSha256=aac,exactAACStreamEqual=True,frameHashFile=decode['frameHashFile'],frameHashSha256=decode['frameHashSha256'],
               packetTimingSha256=hashlib.sha256(json.dumps(pp,sort_keys=True,separators=(',',':')).encode()).hexdigest(),duration=float(info['format']['duration']),decodeReceipt=rel(QA/f'{kind}-decode.json'),decodePasses=1)
   save(QA/f'{kind}-integrity.json',output);outputs.append(output)
   kp=plan['kindPlans'][kind];ranges=[[x['startFrame'],x['startFrame']+x['frames']] for x in kp['parts'] if not x['modified']]
   assert sum(b-a0 for a0,b in ranges)==kp['retainedFrames']
   stream=dict(kind=kind,currentFile=rel(p),currentSha256=digest,modifiedFrameRanges=kp['modifiedFrameRanges'],retainedRanges=ranges,retainedFrames=kp['retainedFrames'],decodedComparisonPerformed=kind=='captioned')
   if kind=='captioned':
    mismatches=[i for a0,b in ranges for i in range(a0,b) if rows[i]['md5']!=old_rows[i]['md5']]
    assert not mismatches,('Retained captioned frames changed unexpectedly',mismatches[:20],len(mismatches))
    stream.update(retainedFramesCompared=kp['retainedFrames'],retainedRangesExactDecodedEqual=True,priorDecodedMasterSha256=meta['videoSha256'],priorFrameHashFile=rel(old_hash),priorFrameHashFileSha256=meta['frameHashSha256'],reuseBasis='Direct current-vs-V3 decoded MD5 equality within each retained GOP-excluded range, plus authenticated V3-to-V4 compressed-video equality proof.')
   else:
    stream.update(retainedRangesExactDecodedEqual=None,reuseBasis='Assembly uses packet copy for retained clean ranges; a separate authenticated baseline-clean decoded hash inventory was not supplied, so decoded equality is not claimed.')
   streams.append(stream)
   save(QA/'integrity-progress.json',dict(inputs=inputs,outputs=outputs,status='partial' if len(outputs)<2 else 'complete'))
   print(json.dumps(dict(kind=kind,status='passed',frames=n,retainedFramesCompared=stream.get('retainedFramesCompared'),exactAACStreamEqual=True)),flush=True)
 prior_asr=PROJECT/'production/local/revision-v4-clarity/final-asr-execution.json';asr=read(prior_asr)
 assert asr['status']=='complete' and asr['returnCode']==0 and asr['inputs']['videoSha256']==plan['baseline']['captioned']['sha256']
 timeline=read(PROJECT/'production/revision-v3/timeline.json')
 integrity=dict(schemaVersion=1,revision=plan['revision'],completedAt=now(),inputs=inputs,outputs=outputs,exactAACStreamEqual=True,
                frames=n,bodyFrames=timeline['bodyFrames'],actualFrames=timeline['actualFrames'],explanationFrames=timeline['explanationFrames'],ratioErrorFrames=timeline['ratioErrorFrames'],
                asrReused=True,newAsrRun=False,humanWholeListening='pending',fullDecodePassesPerOutput=1,changedPixelAndJoinReview='Recorded separately by root/footage; integrity does not approve visual meaning.')
 save(QA/'integrity.json',integrity)
 cap=next(s for s in streams if s['kind']=='captioned')
 proof=dict(schemaVersion=1,revision=plan['revision'],completedAt=now(),pairSourceSha256=inputs['pairSourceSha256'],cleanVideoSha256=pair['outputs']['clean']['sha256'],captionedVideoSha256=pair['outputs']['captioned']['sha256'],
            captionedRetainedFramesExactlyEqual=True,captionedRetainedFramesCompared=cap['retainedFramesCompared'],streams=streams,
            inputs=dict(assemblyPlanSha256=inputs['assemblyPlanSha256'],priorV4VideoReuseProof=rel(PRIOR_PROOF),priorV4VideoReuseProofSha256=sha(PRIOR_PROOF),priorFrameHashFileSha256=sha(old_hash),priorFrameHashMetadata=rel(OLD_QA/'repaired-framehash.json'),priorFrameHashMetadataSha256=sha(OLD_QA/'repaired-framehash.json')),
            audio=dict(file=plan['audio']['file'],fileSha256=inputs['audioFileSha256'],aacSha256=base_aac,exactAACStreamEqual=True,packetTimingExactlyEqual=True,asrReused=True,priorAsrExecution=rel(prior_asr),priorAsrExecutionSha256=sha(prior_asr),basis='Both new outputs retain exactly the baseline ADTS AAC stream and packet timing; current-output full audio decode passed. Existing complete baseline ASR is reused without recognition.'),
            integrityReport=rel(QA/'integrity.json'),integrityReportSha256=sha(QA/'integrity.json'),humanWholeListening='pending',changedRangesVisualReview='Separate current root/footage reports; no old pixel evidence reused for changed GOP ranges.')
 save(HERE/'visual-reuse-proof.json',proof)
 print(json.dumps(dict(status='complete',integrity=rel(QA/'integrity.json'),visualReuseProof=rel(HERE/'visual-reuse-proof.json'),captionedRetainedFramesCompared=cap['retainedFramesCompared'])),flush=True)

if __name__=='__main__':main()
