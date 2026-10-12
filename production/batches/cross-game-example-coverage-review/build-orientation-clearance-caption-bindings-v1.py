"""One CPU2/GPU0 job: patched07b plus current-caption bindings for seven repairs."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, os, subprocess, traceback
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key] = '2'
import psutil
from PIL import Image, ImageDraw, ImageFont
from orientation_07b_caption_clearance_v1 import affected, reframe

ROOT = Path(__file__).resolve().parents[3]; B = Path(__file__).resolve().parent
O = ROOT / 'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
L = ROOT / 'shared/output/unpublished-teaching-clarity-revision/orientation/current34-clearance-caption-bindings-v1'
STATE = O / 'current34-clearance-caption-bindings-execution-v1.json'
FF = 'C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
FP = 'C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe'
rd = lambda p: json.loads(p.read_text('utf-8-sig'))
rel = lambda p: p.relative_to(ROOT).as_posix()
now = lambda: datetime.now(timezone.utc).isoformat()
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for buf in iter(lambda:f.read(1048576),b''): h.update(buf)
    return h.hexdigest()
def save(p,v):
    temp=p.with_name(p.name+'.writing');temp.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(temp,p)

ap=argparse.ArgumentParser();ap.add_argument('--resource',required=True);args=ap.parse_args()
assert not STATE.exists() and not L.exists()
r=rd(ROOT/args.resource)
assert r['guardPassed'] and r['ownHeavyJobs']==0 and r['cpuLoadPercent']<85 and r['freePhysicalMemoryKiB']>8_000_000
assert (datetime.now(timezone.utc)-datetime.fromisoformat(r['observedAt'])).total_seconds()<240
me=psutil.Process(); own=[]
for p in psutil.process_iter(['pid','name','cmdline']):
    try:
        cmd=p.info['cmdline'] or []; text=' '.join(cmd)
        if p.pid==me.pid or (me.parent() and p.pid==me.parent().pid and cmd[1:]==me.cmdline()[1:]): continue
        if (p.info['name'] or '').lower() in ('python.exe','ffmpeg.exe','node.exe') and 'cross-game-example-coverage-review' in text and any(v in text for v in ('render-orientation','review-orientation','extract-orientation','build-orientation','assemble-orientation','render-motion','review-motion','extract-motion')):own.append(p.pid)
    except (psutil.NoSuchProcess,psutil.AccessDenied):pass
assert not own and rd(O/'latest-checkpoint.json')['activeOwnedWorkers']==0
subprocess.run(['node','scripts/review-video-duplicates.cjs','game-math-orientation-matrices','--candidate-file',str(O/'duplicate-candidate-v1.json'),'--check'],cwd=ROOT,check=True)
proof=rd(O/'narration-07b-guide-repair-execution-v1.json');protected=proof['protectedInputs']+proof['results']
for v in protected:assert sha(ROOT/v['path'])==v['sha256']
review=rd(O/'current34-final-pixels-partial-direct-review-v1.json');assert review['samplesDirectlyRead']==3168
repair=rd(O/'current34-caption-clearance-render-execution-v2.json');assert repair['workerDead'] and repair['actualOuterExitCode']==0
assert rd(O/'current34-caption-clearance-sampled-direct-review-v2.json')['all210SamplesDirectlyRead']
assert rd(O/'current34-caption-clearance-normal-direct-review-v2.json')['all7NormalStartEndObserved']
assert rd(O/'07b-caption-clearance-static-direct-review-v1.json')['framingApprovedForMovingRender']
prep=rd(O/'07b-caption-clearance-static-preparation-v1.json');assert sha(ROOT/prep['code'])==prep['codeSha256']
assembly=rd(O/'current34-assembly-inputs-v3.json')
ass=O/'current34.captions.ko.ass';assert sha(ass)==prep['actualCaptionAssSha256']
sources={v['id']:(ROOT/v['output'],v['outputSha256']) for v in repair['scenes']}
for path,digest in sources.values():assert sha(path)==digest
prior=ROOT/prep['sourceVideo'];assert sha(prior)==prep['sourceVideoSha256']
L.mkdir(parents=True);me.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
state=dict(startedAt=now(),pid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),cwd=me.cwd(),sessionId=None,
    resource=args.resource,resourceSha256=sha(ROOT/args.resource),cpuThreads=2,gpuJobs=0,
    code=rel(Path(__file__).resolve()),codeSha256=sha(Path(__file__).resolve()),reframingCodeSha256=sha(ROOT/prep['code']),
    ass=rel(ass),assSha256=sha(ass),status='building-eight-current34-clearance-caption-bindings',
    scenes=[],jobs=[],exitCode=None,actualOuterExitCode=None,newTts=0,newAsr=0,newMix=0,
    final244CaptionPixelsApproved=False,newImageGit=0,researchChanges=0)
def checkpoint():
    ss=STATE.with_name(STATE.stem+'.session.json')
    if ss.exists():state['sessionId']=rd(ss)['sessionId']
    state['updatedAt']=now();save(STATE,state)
    cp=rd(O/'latest-checkpoint.json');cp.update(recordedAt=now(),stage=state['status'],activeOwnedWorkers=int(state['exitCode'] is None),ownedJob=dict(active=state['exitCode'] is None,pid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),cwd=me.cwd(),state=rel(STATE),sessionId=state['sessionId'],currentScene=state.get('currentScene'),cpuThreads=2,gpuJobs=0),next='Inspect all new eight-scene current-caption samples and07b normal1x endpoints. Preserve completed3168-sample finalV3 review and all source/audio history; bind new final assembly only after new selected pixels pass.');save(O/'latest-checkpoint.json',cp)
    qp=B/'queue.json';old=qp.read_bytes();q=rd(qp);q['currentOrientationReview'].update(stage=cp['stage'],activeOwnedWorkers=cp['activeOwnedWorkers'],ownedJob=cp['ownedJob'],next=cp['next']);q['updatedAt']=now();assert qp.read_bytes()==old;save(qp,q)
def run(cmd,log):
    with log.open('wb') as f:
        p=subprocess.Popen(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT);v=dict(pid=p.pid,createTime=psutil.Process(p.pid).create_time(),commandLine=cmd,log=rel(log));state['jobs'].append(v);checkpoint();ex=p.wait();v['exitCode']=ex;checkpoint();assert ex==0,(cmd,ex)
    return ex
checkpoint()
try:
    patched=L/'07b.clearance.silent.mp4'
    dec=[FF,'-hide_banner','-nostdin','-v','error','-threads','1','-i',str(prior),'-an','-pix_fmt','rgb24','-f','rawvideo','pipe:1']
    enc=[FF,'-hide_banner','-nostdin','-v','error','-f','rawvideo','-pixel_format','rgb24','-video_size','1920x1080','-framerate','60','-i','pipe:0','-frames:v','2080','-an','-c:v','libx264','-threads','2','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-video_track_timescale','90000',str(patched)]
    original=hashlib.sha256();passed=hashlib.sha256();unchanged=changed=0
    with (L/'07b-source-read.log').open('wb') as dl,(L/'07b-encode.log').open('wb') as el:
        dp=subprocess.Popen(dec,cwd=ROOT,stdout=subprocess.PIPE,stderr=dl);ep=subprocess.Popen(enc,cwd=ROOT,stdin=subprocess.PIPE,stderr=el)
        for p,c,log in [(dp,dec,'07b-source-read.log'),(ep,enc,'07b-encode.log')]:state['jobs'].append(dict(pid=p.pid,createTime=psutil.Process(p.pid).create_time(),commandLine=c,log=rel(L/log)))
        checkpoint()
        for frame in range(2080):
            raw=dp.stdout.read(1920*1080*3);assert len(raw)==1920*1080*3
            if affected(frame):out=reframe(Image.frombytes('RGB',(1920,1080),raw)).tobytes();changed+=1
            else:out=raw;original.update(raw);passed.update(out);unchanged+=1
            ep.stdin.write(out)
            if frame%120==0:state.update(currentScene='07b',writtenFrames=frame+1);checkpoint()
        assert dp.stdout.read(1)==b'';dp.stdout.close();ep.stdin.close();dx=dp.wait();ex=ep.wait()
        state['jobs'][-2]['exitCode']=dx;state['jobs'][-1]['exitCode']=ex;assert dx==ex==0
    assert (changed,unchanged)==(360,1720) and original.hexdigest()==passed.hexdigest()
    state['07bFraming']=dict(source=rel(prior),sourceSha256=sha(prior),output=rel(patched),outputSha256=sha(patched),changedFrames=changed,unchangedInputRgbFrames=unchanged,unchangedInputRgbSha256=original.hexdigest(),passedRgbSha256=passed.hexdigest(),actualFrames=1630,explanationFrames=450,totalFrames=2080)
    sources['07b']=(patched,sha(patched));start=0
    for piece in assembly['pieces']:
        sid=piece['id'];frames=piece['frames'];absolute=start;start+=frames
        if sid not in sources:continue
        state['currentScene']=sid;checkpoint();folder=L/f'scene-{sid}';folder.mkdir()
        source,digest=sources[sid];assert sha(source)==digest
        stream=json.loads(subprocess.check_output([FP,'-v','error','-select_streams','v:0','-show_entries','stream=nb_frames','-of','json',str(source)]))['streams'][0];count=int(stream['nb_frames']);pad=frames-count;assert pad in (0,1)
        captioned=folder/f'{sid}.current-captioned.mp4'
        filter=f'tpad=stop_mode=clone:stop_duration={pad/60:.12f},trim=end_frame={frames},settb=1/90000,setpts=N*1500+{absolute*1500},ass={rel(ass)},setpts=PTS-STARTPTS,setsar=1'
        ex=run([FF,'-hide_banner','-nostdin','-v','error','-threads','2','-filter_threads','1','-i',str(source),'-vf',filter,'-frames:v',str(frames),'-an','-c:v','libx264','-threads','2','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-r','60','-video_track_timescale','90000',str(captioned)],folder/'caption-binding.log')
        probe=json.loads(subprocess.check_output([FP,'-v','error','-select_streams','v:0','-show_streams','-of','json',str(captioned)]));v=probe['streams'][0];assert (v['width'],v['height'],v['r_frame_rate'],v['time_base'],int(v['nb_frames']))==(1920,1080,'60/1','1/90000',frames)
        dx=run([FF,'-hide_banner','-nostdin','-v','error','-threads','2','-i',str(captioned),'-f','null','-'],folder/'decode.log')
        wanted=sorted({s['frame']-absolute for s in review['reviewedSamples'] if absolute<=s['frame']<absolute+frames})
        select='+'.join(f'eq(pts\\,{f*1500})' for f in wanted)
        xx=run([FF,'-hide_banner','-nostdin','-v','info','-threads','2','-filter_threads','1','-i',str(captioned),'-vf','select='+select,'-fps_mode','passthrough','-frames:v',str(len(wanted)),'-threads','2',str(folder/'sample-%04d.png')],folder/'extract.log')
        paths=sorted(folder.glob('sample-*.png'));assert len(paths)==len(wanted)
        samples=[dict(frame=f,absoluteFrame=absolute+f,pts=f*1500,path=rel(p),sha256=sha(p)) for f,p in zip(wanted,paths)]
        boards=[];font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',21)
        for offset in range(0,len(samples),4):
            im=Image.new('RGB',(1920,1140),'#171a1e');draw=ImageDraw.Draw(im)
            for j,sample in enumerate(samples[offset:offset+4]):
                x=j%2*960;y=j//2*570
                with Image.open(ROOT/sample['path']) as picture:im.paste(picture.resize((960,540)),(x,y+30))
                draw.text((x+8,y+3),f'{sid} local{sample["frame"]} final{sample["absoluteFrame"]}',font=font,fill='white')
            p=folder/f'board-{offset//4+1:03d}.png';im.save(p);boards.append(dict(path=rel(p),sha256=sha(p)))
        state['scenes'].append(dict(id=sid,source=rel(source),sourceSha256=digest,output=rel(captioned),outputSha256=sha(captioned),plannedFrames=frames,absoluteStartFrame=absolute,explanationTailPadFrames=pad,renderExitCode=ex,wholeDecodeExitCode=dx,extractExitCode=xx,probe=probe,samples=samples,boards=boards));checkpoint()
        print(json.dumps(dict(id=sid,frames=frames,samples=len(samples),boards=len(boards))),flush=True)
    assert len(state['scenes'])==8
    for v in protected:assert sha(ROOT/v['path'])==v['sha256']
    state.update(status='built-eight-current34-clearance-caption-bindings-awaiting-direct-review',exitCode=0,finishedAt=now(),all79ProtectedUnchanged=True,repairCandidateUnchanged=True);checkpoint()
except BaseException:
    state.update(status='failed-current34-clearance-caption-bindings-preserve-history',exitCode=1,error=traceback.format_exc(),finishedAt=now());checkpoint();raise
