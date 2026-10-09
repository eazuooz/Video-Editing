"""One CPU2 extraction for new exact montage/interval-boundary observations.
Completed raw whole decodes and coarse boards are not repeated. All pixels are
local-only; extraction itself never approves footage or the body ratio.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os,re,subprocess,time,traceback
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
def now():return datetime.now(timezone.utc).isoformat()
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return p.relative_to(ROOT).as_posix()
def save(p,x):
    t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8')
    for retry in range(40):
        try:os.replace(t,p);return
        except PermissionError:
            if retry==39:raise
            time.sleep(.15)
ap=argparse.ArgumentParser();ap.add_argument('--resource',required=True);ap.add_argument('--resume-missing-only',action='store_true');args=ap.parse_args()
resource=read(ROOT/args.resource)
assert (datetime.now(timezone.utc)-datetime.fromisoformat(resource['observedAt'].replace('Z','+00:00'))).total_seconds()<240
assert resource['ownHeavyJobs']==0 and resource['cpuLoadPercent']<85 and resource['freePhysicalMemoryKiB']>8_000_000
STATE=BASE/'current-source-edge-extraction-v2.json';DEST=ROOT/'shared/output/similar-game-design/preflight/current-native-edge-v2'
import psutil
me=psutil.Process()
if args.resume_missing_only:
    state=read(STATE);assert state['exitCode']==1 and len(state['sources'])==2
    if psutil.pid_exists(state['pid']):assert abs(psutil.Process(state['pid']).create_time()-state['createTime'])>.01
    for s in state['sources']:
        for frame in s['frameEntries']:assert sha(ROOT/frame['path'])==frame['sha256']
        for board in s['boards']:assert sha(ROOT/board['path'])==board['sha256']
    history=BASE/'current-source-edge-extraction-failure-history-v2.json';assert not history.exists();save(history,state)
    state.update(resumeStartedAt=now(),pid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),sessionId=None,
                 status='single-CPU2-resume-missing-Engineer03-only',exitCode=None,resource=resource,
                 failureHistory=rel(history),completedTwoSourcesAnd34FramesPreserved=True)
    state.pop('error',None)
else:
    assert not STATE.exists() and not DEST.exists(),'Read existing extraction; do not recreate it.'
    state=dict(schemaVersion=1,startedAt=now(),pid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),
 sessionId=None,status='single-CPU2-new-source-edge-extraction',cpuThreads=2,gpuJobs=0,resource=resource,sources=[],
 wholeSourceDecodeRepeated=False,localOnly=True,allBoardsDirectlyRead=False,actualActionApproved=False,exitCode=None)
    DEST.mkdir(parents=True)
def checkpoint():
    sp=BASE/'current-source-edge-extraction-v2.session.json'
    if sp.exists():state['sessionId']=read(sp)['sessionId']
    state['updatedAt']=now();save(STATE,state)
    cp=read(BASE/'latest-checkpoint.json');job=dict(status=state['status'],pid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),sessionId=state['sessionId'],
       state=rel(STATE),cpuThreads=2,gpu=0,exitCode=state['exitCode'],workerExpectedRunning=state['exitCode'] is None)
    cp.update(recordedAt=now(),stage='measured-voice-new-native-source-boundaries',ownedJob=job,
      nextAction='Directly read all native cut/edge boards; source interval extensions require actual action, no title/menu/fade/loop/slowdown. Then measured67 paragraph source/timing/captions and60FPS depth review.')
    save(BASE/'latest-checkpoint.json',cp)
    qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json'
    for _ in range(8):
        raw=qp.read_text('utf-8-sig');q=json.loads(raw);item=next(x for x in q['items'] if x['slug']=='similar-game-design');item.update(stage=cp['stage'],currentExecution=job,nextAction=cp['nextAction']);q.update(updatedAt=now(),lastProgressAt=now())
        if qp.read_text('utf-8-sig')==raw:save(qp,q);break
        time.sleep(.15)
    else:raise RuntimeError('Concurrent queue write.')
def run(cmd,log):
    with log.open('w',encoding='utf-8') as f:
        p=subprocess.Popen(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT);state['childPid']=p.pid;state['currentCommand']=cmd;checkpoint();code=p.wait()
    assert code==0,f'{log} exit{code}'
    state['childPid']=None
allSources=read(ROOT/'shared/output/similar-game-design/preflight/primary-acquisition-v1.json')['sources']+read(ROOT/'shared/output/similar-game-design/preflight/additional-primary-acquisition-v1.json')['sources']
stems=['brotato-full-release','drgs-engineer-crystalline-01','drgs-engineer-crystalline-03']
try:
    checkpoint()
    for stem in stems:
        if any(s['stem']==stem for s in state['sources']):continue
        src=next(s for s in allSources if s['stem']==stem);source=ROOT/src['path'];assert sha(source)==src['sha256'];folder=DEST/stem;folder.mkdir(exist_ok=args.resume_missing_only)
        assert not list(folder.glob('frame-*.jpg'))
        state['currentSource']=stem;checkpoint();cuts=[]
        if stem=='brotato-full-release':
            log=folder/'native-montage-candidate-detection.log'
            run([FF,'-hide_banner','-threads','2','-i',str(source),'-an','-vf',"trim=end_frame=3180,scale=320:180,select='gt(scene,0.22)',showinfo",'-filter_threads','2','-threads','2','-f','null','-'],log)
            cuts=sorted(set(round(float(t)*60) for t in re.findall(r'pts_time:([\d.]+)',log.read_text('utf-8')) if 2<float(t)<52))
            frames=sorted({120,3119,*[n for c in cuts for n in [c-1,c,c+1] if 120<=n<3120]})
        elif stem.endswith('01'):
            frames=[0,30,60,120,179,239,240,2759,2760,3059,3060,3779,3780,3809,3828,3840,3858]
        else:
            frames=[0,30,59,60,1439,1499,1500,1515,1530,1559,1560,1590,2459,2460,4019,4020,4030,4049,4080]
        expression='+'.join(f'eq(n,{n})' for n in frames)
        crop='crop=1920:1080:0:0' if stem.startswith('brotato') else 'crop=2272:1278:144:0'
        cmd=[FF,'-hide_banner','-v','error','-threads','2','-i',str(source),'-an','-vf',f"select='{expression}',{crop},scale=640:360",'-vsync','0','-filter_threads','2','-threads','2','-q:v','2',str(folder/'frame-%04d.jpg')]
        run(cmd,folder/'extraction.log');images=sorted(folder.glob('frame-*.jpg'));assert len(images)==len(frames)
        entries=[dict(sourceFrame=f,sourceSeconds=f/60,path=rel(p),sha256=sha(p)) for f,p in zip(frames,images)]
        boards=[];font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',19)
        for offset in range(0,len(images),6):
            board=Image.new('RGB',(1920,776),'white');draw=ImageDraw.Draw(board)
            for j,img in enumerate(images[offset:offset+6]):
                x=j%3*640;y=j//3*388;board.paste(Image.open(img),(x,y));draw.text((x+5,y+363),f'{stem} source f{frames[offset+j]} / {frames[offset+j]/60:.6f}s',font=font,fill='black')
            p=folder/f'board-{offset//6+1:02d}.jpg';board.save(p,quality=96)
            boards.append(dict(path=rel(p),sha256=sha(p),frames=frames[offset:offset+6],directlyRead=False))
        assert sha(source)==src['sha256'];state['sources'].append(dict(stem=stem,sourcePath=src['path'],sourceSha256=src['sha256'],
          nativeCutCandidates=cuts,frameEntries=entries,boards=boards,crop=crop,allBoardsDirectlyRead=False,intervalExtensionsApproved=False))
        checkpoint();print(json.dumps(dict(stem=stem,candidateCuts=len(cuts),frames=len(frames),boards=len(boards))),flush=True)
    state.update(status='closed-new-native-edges-awaiting-direct-pixel-review',exitCode=0,finishedAt=now());checkpoint()
except BaseException:
    state.update(status='closed-native-extraction-failed-preserving-files',exitCode=1,error=traceback.format_exc(),finishedAt=now());checkpoint();raise
