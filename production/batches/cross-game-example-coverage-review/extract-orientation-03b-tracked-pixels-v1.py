"""One CPU2 encoded sample extraction, with cut, reveal and hidden-guide boundaries."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,hashlib,os,subprocess,re,traceback,psutil
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent;O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe';read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return p.relative_to(ROOT).as_posix()
def now():return datetime.now(timezone.utc).isoformat()
def save(p,x):
 t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
ap=argparse.ArgumentParser();ap.add_argument('--resource',required=True);a=ap.parse_args()
sp=O/'03b-tracked-pixels-execution-v1.json';assert not sp.exists()
r=read(ROOT/a.resource);assert (datetime.now(timezone.utc)-datetime.fromisoformat(r['observedAt'])).total_seconds()<240
assert r['ownHeavyJobs']==0 and r['cpuLoadPercent']<85 and r['freePhysicalMemoryKiB']>8_000_000
s=read(O/'03b-tracked-render-execution-v1.json');assert s['actualExitObserved'] and s['actualOuterExitCode']==0 and s['workerDead'];assert sha(ROOT/s['output'])==s['outputSha256']
p=read(ROOT/s['plan']);protected=read(O/'narration-07b-guide-repair-execution-v1.json')
for x in protected['protectedInputs']+protected['results']:assert sha(ROOT/x['path'])==x['sha256']
frames=set(range(0,p['frames'],15));frames.add(p['frames']-1)
events=[int(t*60) for t in [3.06,6.84,11.06,12.66,13.56,14.28,15.2,16.04,21.42,25.14,25.5,26.1]]
for seg in p['segments']:
 events += [seg['frameIn'],seg['frameOut']]
 if seg['classification']=='actual':
  for h in p['hideSourceSeconds']:
   for sec in h:
    native=int(round(sec*60))
    if seg['nativeIn']<=native<=seg['nativeOutExclusive']:events.append(seg['frameIn']+native-seg['nativeIn'])
for v in events:
 for delta in (-1,0,1):
  if 0<=v+delta<p['frames']:frames.add(v+delta)
frames=sorted(frames);local=ROOT/s['output'];qa=local.parent/'qa';assert not qa.exists();qa.mkdir()
me=psutil.Process();state=dict(startedAt=now(),pid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),cwd=me.cwd(),sessionId=None,resource=a.resource,cpuThreads=2,gpuJobs=0,status='03b-encoded-samples-extracting',actualOuterExitCode=None,newImageGit=0,allMovingPixelsApproved=False)
save(sp,state)
cp=read(O/'latest-checkpoint.json');cp.update(stage=state['status'],ownedJob=state,activeOwnedWorkers=1);save(O/'latest-checkpoint.json',cp)
q=read(B/'queue.json');q['currentOrientationReview'].update(stage=state['status'],ownedJob=state,activeOwnedWorkers=1);save(B/'queue.json',q)
select='+'.join(f'eq(pts,{f*1500})' for f in frames)
cmd=[FF,'-hide_banner','-nostdin','-v','info','-threads','2','-filter_threads','1','-i',str(local),'-an','-vf',f"select='{select}',showinfo,scale=1280:720",'-fps_mode','passthrough','-frames:v',str(len(frames)),'-threads','2','-compression_level','3',str(qa/'sample-%04d.png')]
try:
 with (qa/'extract.log').open('wb') as l:
  ff=subprocess.Popen(cmd,stdout=l,stderr=subprocess.STDOUT,cwd=ROOT);state.update(ffmpegPid=ff.pid,ffmpegCreateTime=psutil.Process(ff.pid).create_time(),command=cmd,log=rel(qa/'extract.log'));save(sp,state);code=ff.wait();assert code==0
 pts=[int(v) for v in re.findall(r'\bn:\s*\d+\s+pts:\s*(\d+)',(qa/'extract.log').read_text('utf-8',errors='replace'))];assert pts==[f*1500 for f in frames]
 samples=[]
 for i,f in enumerate(frames,1):
  file=qa/f'sample-{i:04d}.png';seg=next(x for x in p['segments'] if x['frameIn']<=f<x['frameOut']);samples.append(dict(frame=f,pts=f*1500,classification=seg['classification'],nativeFrame=None if seg['classification']=='explanation' else seg['nativeIn']+f-seg['frameIn'],path=rel(file),sha256=sha(file)))
 font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20);boards=[]
 for i in range(0,len(samples),5):
  group=samples[i:i+5];im=Image.new('RGB',(1280,1176),'#181818');d=ImageDraw.Draw(im)
  for j,x in enumerate(group):
   xx=(j%2)*640;yy=(j//2)*392
   with Image.open(ROOT/x['path']) as tile:im.paste(tile.resize((640,360)),(xx,yy))
   d.text((xx+5,yy+362),f"f{x['frame']} PTS{x['pts']} {x['frame']/60:.3f}s {x['classification']}",font=font,fill='white')
  file=qa/f'board-{i//5+1:03d}.png';im.save(file,compress_level=3);boards.append(dict(path=rel(file),sha256=sha(file),samplePaths=[x['path'] for x in group]))
 for x in protected['protectedInputs']+protected['results']:assert sha(ROOT/x['path'])==x['sha256']
 state.update(status='03b-encoded-samples-awaiting-direct-review',workerExitCode=0,finishedAt=now(),ffmpegExitCode=code,exactEncodedPtsMatched=True,samples=samples,boards=boards,protectedShaMatched=True);save(sp,state)
 print(json.dumps(dict(samples=len(samples),boards=len(boards),workerExitCode=0)),flush=True)
except BaseException as e:
 state.update(status='failed',workerExitCode=1,error=repr(e),traceback=traceback.format_exc(),finishedAt=now());save(sp,state);raise
