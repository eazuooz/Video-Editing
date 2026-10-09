"""Acquire the observed official file and inspect it once on CPU2/GPU0."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os,subprocess,time,psutil,traceback
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
DEST=ROOT/'shared/output/similar-game-design/preflight/fresh-engineer02-v1'
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe';PROBE='C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe'
def now():return datetime.now(timezone.utc).isoformat()
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return p.relative_to(ROOT).as_posix()
def save(p,x):
    t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8')
    for n in range(40):
        try:os.replace(t,p);return
        except PermissionError:
            if n==39:raise
            time.sleep(.15)
ap=argparse.ArgumentParser();ap.add_argument('--resource',required=True);args=ap.parse_args();resource=read(ROOT/args.resource)
assert (datetime.now(timezone.utc)-datetime.fromisoformat(resource['observedAt'].replace('Z','+00:00'))).total_seconds()<240
assert resource['ownHeavyJobs']==0 and resource['cpuLoadPercent']<85 and resource['freePhysicalMemoryKiB']>8000000
STATE=BASE/'fresh-primary-engineer02-inspection-v1.json';assert not STATE.exists() and not DEST.exists()
DEST.mkdir(parents=True);me=psutil.Process();source=DEST/'drgs-engineer-crystalline-02.mp4'
state=dict(schemaVersion=1,startedAt=now(),pid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),sessionId=None,status='single-CPU2-fresh-official-acquisition',cpuThreads=2,gpuJobs=0,resource=resource,sourceUrl='https://drive.google.com/file/d/1amv63bfqpQzq3qj9U7GxLi7DlxXlYmdM/view',officialFolderUrl='https://drive.google.com/drive/folders/15ZzRXk3LWNZ4cH7Ms8_ocJ3Q6IkR4nmy',officialPressOwner='Funday Games',sourceVersion='2024-02-14 early-access official press B-roll',browserObservation='407.1MB/2560x1440/02:42/Funday Games; actual selected file link copied from official folder UI. The browser event wait did not return a local path; acquire the same observed public file using the existing repository downloader.',sourcePath=rel(source),allBoardsDirectlyRead=False,finalSourceAllocationApproved=False,localOnly=True,exitCode=None)
def checkpoint():
    sp=BASE/'fresh-primary-engineer02-inspection-v1.session.json'
    if sp.exists():state['sessionId']=read(sp)['sessionId']
    state['updatedAt']=now();save(STATE,state)
    cp=read(BASE/'latest-checkpoint.json');job=dict(status=state['status'],pid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),sessionId=state['sessionId'],state=rel(STATE),cpuThreads=2,gpu=0,exitCode=state['exitCode'],workerExpectedRunning=state['exitCode'] is None)
    cp.update(recordedAt=now(),stage='fresh-primary-source-before-additional-observation',ownedJob=job,nextAction='Read every fresh source board and exact chosen action interval before writing added narration. Keep current67 approved PCM and every original white explanation.');save(BASE/'latest-checkpoint.json',cp)
    qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json'
    for n in range(40):
        raw=qp.read_text('utf-8-sig');q=json.loads(raw);item=next(x for x in q['items'] if x['slug']=='similar-game-design');item.update(stage=cp['stage'],currentExecution=job,nextAction=cp['nextAction']);q.update(updatedAt=now(),lastProgressAt=now())
        if qp.read_text('utf-8-sig')==raw:save(qp,q);break
        time.sleep(.15)
    else:raise RuntimeError('Concurrent queue write')
def run(cmd,name):
    state['currentCommand']=cmd;state['currentLog']=rel(DEST/name)
    with (DEST/name).open('w',encoding='utf-8') as f:
        p=subprocess.Popen(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT);state['childPid']=p.pid;checkpoint();code=p.wait()
    state['childPid']=None;assert code==0,f'{name} exit{code}'
try:
    checkpoint();run([str(ROOT/'qwen3-tts/.venv/Scripts/python.exe'),'-m','yt_dlp','--no-playlist','--newline','--progress-delta','15','--write-info-json','-o',str(DEST/'drgs-engineer-crystalline-02.%(ext)s'),state['sourceUrl']],'download.log')
    assert source.exists();state.update(sourceSha256=sha(source),bytes=source.stat().st_size,status='single-CPU2-fresh-probe-whole-decode')
    result=subprocess.run([PROBE,'-v','error','-show_entries','stream=codec_name,width,height,r_frame_rate,nb_frames:format=duration,size','-of','json',str(source)],capture_output=True,text=True);assert result.returncode==0;state['probe']=json.loads(result.stdout)
    run([FF,'-hide_banner','-v','error','-threads','2','-i',str(source),'-f','null','-'],'whole-decode.log');state['wholeDecodeExitCode']=0
    state['status']='single-CPU2-fresh-whole-coarse-observation';run([FF,'-hide_banner','-v','error','-threads','2','-i',str(source),'-an','-vf','fps=1,crop=2272:1278:144:0,scale=640:360','-filter_threads','2','-threads','2','-q:v','2',str(DEST/'frame-%04d.jpg')],'extract.log')
    files=sorted(DEST.glob('frame-*.jpg'));assert len(files)>=160;state['frames']=[dict(index=i+1,sourceApproxSeconds=i+.5,path=rel(p),sha256=sha(p)) for i,p in enumerate(files)];state['boards']=[]
    font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',23)
    for offset in range(0,len(files),6):
        board=Image.new('RGB',(1280,1158),'white');draw=ImageDraw.Draw(board)
        for j,p in enumerate(files[offset:offset+6]):
            x=(j%2)*640;y=(j//2)*386;board.paste(Image.open(p),(x,y+26));draw.text((x+8,y+1),f'Engineer02 approximate {(offset+j)+.5:.1f}s',font=font,fill='black')
        out=DEST/f'board-{offset//6+1:02d}.jpg';board.save(out,quality=94);state['boards'].append(dict(path=rel(out),sha256=sha(out),frameIndices=list(range(offset+1,min(offset+7,len(files)+1))),directlyRead=False))
    state.update(status='closed-fresh-source-awaiting-direct-action-review',exitCode=0,finishedAt=now());checkpoint();print(json.dumps(dict(frames=len(files),boards=len(state['boards']),wholeDecodeExitCode=0,sourceSha256=state['sourceSha256'])))
except Exception:
    state.update(status='failed-preserve-fresh-checkpoint',exitCode=1,error=traceback.format_exc(),finishedAt=now());checkpoint();raise
