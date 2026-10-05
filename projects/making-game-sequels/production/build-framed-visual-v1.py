"""Frame existing unique native cuts and concatenate measured independent MC inputs."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, subprocess, time, traceback
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent;FINAL=BASE/'final-v1'
FF=Path('C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe');FP=FF.with_name('ffprobe.exe')
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
now=lambda:datetime.now(timezone.utc).isoformat()
STATE=FINAL/'framed-visual-execution.json';assert not STATE.exists()
plan=read(FINAL/'plan.json');assert plan['finalTimingApproved'] and plan['bodyRatioApproved'] and plan['allInputSegmentCaptionPixelsReviewed']
assert read(FINAL/'mix-recovery-execution.json')['exitCode']==0
state=dict(schemaVersion=1,pid=os.getpid(),sessionId=None,startedAt=now(),status='framing-reviewed-native-inputs',
    cpuThreads=2,gpuJobs=0,commands=[],activeTasks=[],cuts=[],white=[],newImages=0,
    completedNativeCuts=0,totalNativeCuts=85,finalCompositeApproved=False)
def write(p,d):
    t=p.with_name(p.name+f'.{os.getpid()}.writing')
    for n in range(30):
        try:t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');os.replace(t,p);return
        except OSError:
            if n==29:raise
            time.sleep(.1)
def checkpoint():
    sp=FINAL/'framed-visual-session.json'
    if sp.exists() and read(sp).get('pid')==os.getpid():state['sessionId']=read(sp)['sessionId']
    state['observedAt']=now();write(STATE,state)
    qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qp);i=next(i for i in q['items'] if i['slug']=='making-game-sequels')
    i.update(stage='current13-guided60-final-framed-inputs-and-visual-preparing',updatedAt=state['observedAt'],
        nextAction='Complete85 reviewed source crops and exact-frame visual assembly; review final Nimbus13chapters/joins, encode fixed captions, inspect every final cue/cut and technical QA, collect/private/Git.')
    alive='endedAt' not in state
    i['execution'].update(status=state['status'],phase=i['stage'],observedAt=state['observedAt'],pid=os.getpid(),
        sessionId=state['sessionId'],commandLine='build-framed-visual-v1.py CPU2/GPU0',state=rel(STATE),alive=alive,
        activeTasks=state['activeTasks'],cpuProductionJobs=int(alive),primaryCpuProductionJobs=int(alive),
        gpuSynthesisJobs=0,renderJobs=int(alive),uploads=0,
        framedNativeProgress=dict(completed=state['completedNativeCuts'],total=85))
    q['updatedAt']=i['updatedAt'];write(qp,q)
    for p in [BASE/'latest-checkpoint.json',ROOT/'production/batches/sakurai-planning-game-design/proof-making-game-sequels/latest-checkpoint.json']:
        d=read(p)
        for k in ['stage','updatedAt','nextAction','execution']:d[k]=i[k]
        d.update(finalMixBuilt=True,finalMixAsrApproved=False,rendered=False,qaApproved=False,collected=False,privateUploaded=False)
        write(p,d)
def run(exe,args,kind):
    log=FINAL/f'framed-visual-{len(state["commands"])+1:03d}.log'
    command=[str(exe),*map(str,args)]
    with log.open('w',encoding='utf-8') as fh:
        p=subprocess.Popen(command,cwd=ROOT,stdout=fh,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
        state['status']=kind;state['activeTasks']=[dict(kind=kind,pid=p.pid,command=command,log=rel(log))];checkpoint();code=p.wait()
    state['commands'].append(dict(command=command,pid=p.pid,exitCode=code,log=rel(log)));state['activeTasks']=[];checkpoint()
    if code:raise RuntimeError(f'{kind} exit{code}: {log}')
    return log.read_text(encoding='utf-8')
def ff(args,kind):return run(FF,['-v','error','-nostdin','-threads','2',*args],kind)
def probe(p,frames):
    pr=json.loads(run(FP,['-v','error','-threads','2','-count_frames','-show_streams','-show_format','-of','json',p],'CPU-count-current-input'))
    assert len(pr['streams'])==1
    s=pr['streams'][0]
    assert s['width']==1920 and s['height']==1080 and s['avg_frame_rate']=='60/1' and int(s['nb_read_frames'])==frames
    assert abs(float(pr['format']['duration'])-frames/60)<.017
    return pr
try:
    checkpoint();(FINAL/'framed-native').mkdir();(FINAL/'white-segments').mkdir()
    for s in plan['scenes']:
        for c in s['segments']:
            if c['classification']=='actual-existing-game':
                raw=ROOT/c['rawCompiledVideo'];assert sha(raw)==c['rawCompiledSha256']
                x,y,w,h=c['sourceFraming'];out=ROOT/c['video']
                if [x,y,w,h]==[0,0,1920,1080]:
                    video=raw;reused=True
                else:
                    ff(['-i',raw,'-an','-vf',f'crop={w}:{h}:{x}:{y},scale=1920:1080,setsar=1,setpts=N/(60*TB)',
                        '-fps_mode','passthrough','-frames:v',c['frames'],'-c:v','libx264','-preset','veryfast','-crf','18',
                        '-threads','2','-pix_fmt','yuv420p','-video_track_timescale','90000','-movflags','+faststart',out],'CPU-reviewed-native-crop')
                    video=out;reused=False
                pr=probe(video,c['frames'])
                text=ff(['-i',video,'-f','null','-'],'CPU-current-framed-cut-decode');assert not text.strip()
                state['cuts'].append(dict(id=c['id'],sceneId=s['id'],startFrame=c['startFrame'],frames=c['frames'],
                    video=rel(video),sha256=sha(video),classification=c['classification'],sourceFraming=c['sourceFraming'],
                    rawVideo=c['rawCompiledVideo'],rawSha256=c['rawCompiledSha256'],rawReused=reused,
                    audioStreams=0,probe=pr,wholeDecodeExitCode=0,finalPixelApproved=False))
                state['completedNativeCuts']+=1;checkpoint();print(f'Framed {state["completedNativeCuts"]}/85',flush=True)
            else:
                raw=ROOT/c['video'];assert sha(raw)==c['videoSha256']
                out=FINAL/'white-segments'/f"{s['id']}-{c['id']}.mp4"
                ff(['-i',raw,'-map','0:v:0','-an','-c:v','copy','-video_track_timescale','90000','-movflags','+faststart',out],'CPU-white-timescale-remux-no-render')
                pr=probe(out,c['frames'])
                state['white'].append(dict(id=c['id'],sceneId=s['id'],startFrame=c['startFrame'],frames=c['frames'],
                    video=rel(out),sha256=sha(out),classification=c['classification'],sourceVideo=c['video'],
                    sourceSha256=c['videoSha256'],probe=pr,reencoded=False,finalPixelApproved=False))
                checkpoint()
    assert state['completedNativeCuts']==85 and len(state['white'])==7
    original=ROOT/'projects/game-reward-planning/production/final-v1/white-segments'
    branding=original/'branding.mp4';member=original/'membership.mp4'
    assert sha(branding)=='706a0738dcd160b80ace24e54e16c09604c0173aba095fcd221a227c541fffb2'
    assert sha(member)=='181e5c5dd37672349542aa590629fe2f2d00a83f4cd3c811a29a21c029612123'
    segments=[dict(id='branding',startFrame=0,frames=120,video=rel(branding),sha256=sha(branding),classification='branding')]
    segments+=sorted(state['cuts']+state['white'],key=lambda x:x['startFrame'])
    segments.append(dict(id='membership',startFrame=34983,frames=600,video=rel(member),sha256=sha(member),classification='membership'))
    pos=0
    for s in segments:assert s['startFrame']==pos;pos+=s['frames']
    assert pos==35583
    listing=FINAL/'visual-concat.txt';listing.write_text('\n'.join("file '"+(ROOT/s['video']).as_posix()+"'" for s in segments)+'\n',encoding='utf-8')
    visual=FINAL/'visual-silent-review.mp4'
    ff(['-f','concat','-safe','0','-i',listing,'-map','0:v:0','-an','-c:v','copy','-video_track_timescale','90000','-movflags','+faststart',visual],'CPU-silent-exact-segment-assembly')
    pr=probe(visual,35583)
    text=ff(['-i',visual,'-f','null','-'],'CPU-whole-silent-visual-decode');assert not text.strip()
    write(FINAL/'visual-build.json',dict(createdAt=now(),planSha256=sha(FINAL/'plan.json'),
        segments=segments,frames=35583,seconds=593.05,video=rel(visual),sha256=sha(visual),probe=pr,
        sourceAudioStreams=0,originalBrandingMembershipByteIdentical=True,wholeDecodeExitCode=0,
        cleanWhiteReencoded=False,finalFixedCaptionPixelsApproved=False,finalMixAsrApproved=False,
        silentVisualIsCompletedVideo=False))
    state.update(status='closed-framed-visual-built-final-mixed-ASR-and-caption-QA-pending',endedAt=now(),exitCode=0,activeTasks=[]);checkpoint()
except BaseException:
    state.update(status='closed-framed-visual-failed',endedAt=now(),exitCode=1,error=traceback.format_exc(),activeTasks=[]);checkpoint();raise
