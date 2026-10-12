"""Once-only local encoded QA samples of measured02a; no visual approval."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,hashlib,os,re,subprocess,psutil
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent;O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def now():return datetime.now(timezone.utc).isoformat()
def rel(p):return p.relative_to(ROOT).as_posix()
def save(p,x):
 t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
ap=argparse.ArgumentParser();ap.add_argument('--resource',required=True);a=ap.parse_args()
r=read(ROOT/a.resource);assert (datetime.now(timezone.utc)-datetime.fromisoformat(r['observedAt'])).total_seconds()<240
assert r['ownHeavyJobs']==0 and r['cpuLoadPercent']<85 and r['freePhysicalMemoryKiB']>8_000_000
s=read(O/'02a-tracked-render-execution-v1.json');assert s['actualExitObserved'] and s['actualOuterExitCode']==0
assert sha(ROOT/s['output'])==s['outputSha256']
plan=read(O/'02a-observation-track-plan-v1.json');local=ROOT/'shared/output/unpublished-teaching-clarity-revision/orientation/current34-02a-tracked-v1/qa';sp=O/'02a-tracked-pixel-execution-v1.json';assert not local.exists() and not sp.exists()
local.mkdir();me=psutil.Process()
state=dict(startedAt=now(),pid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),cwd=me.cwd(),sessionId=None,resource=a.resource,cpuThreads=2,gpuJobs=0,status='02a-encoded-sample-extraction',actualOuterExitCode=None,newImageGit=0,allMovingPixelsApproved=False)
save(sp,state)
cp=read(O/'latest-checkpoint.json');cp.update(stage=state['status'],ownedJob=state,activeOwnedWorkers=1);save(O/'latest-checkpoint.json',cp)
q=read(B/'queue.json');q['currentOrientationReview'].update(stage=state['status'],ownedJob=state,activeOwnedWorkers=1);save(B/'queue.json',q)
samples=set(range(0,1033,15))|{1032}
samples.update(min(1032,int(round(x*60))+d) for x in plan['reveals'].values() for d in [-1,0,1])
for a0,b0 in plan['hideSeconds']:
 for v in [a0,b0]:samples.update(min(1032,max(0,int(round((v-79.5)*60))+d)) for d in [-1,0,1])
samples=sorted(samples);select='+'.join(f'eq(pts,{n*1500})' for n in samples)
cmd=[FF,'-hide_banner','-nostdin','-v','info','-threads','2','-filter_threads','1','-i',str(ROOT/s['output']),'-an','-vf',f"select='{select}',showinfo,scale=1280:720",'-fps_mode','passthrough','-frames:v',str(len(samples)),'-threads','2','-compression_level','3',str(local/'sample-%04d.png')]
save(local/'command.json',cmd)
with (local/'extract.log').open('wb') as log:
 p=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT,cwd=ROOT);state.update(ffmpegPid=p.pid,ffmpegCreateTime=psutil.Process(p.pid).create_time(),ffmpegCommandLine=cmd,log=rel(local/'extract.log'));save(sp,state);rc=p.wait()
assert rc==0
pts=[int(x) for x in re.findall(r'\bn:\s*\d+\s+pts:\s*(\d+)',(local/'extract.log').read_text('utf-8',errors='replace'))];assert pts==[n*1500 for n in samples]
records=[dict(frame=f,pts=f*1500,sourceFrame=min(4770+f,5801),roundingHold=f==1032,path=rel(local/f'sample-{i:04d}.png'),sha256=sha(local/f'sample-{i:04d}.png')) for i,f in enumerate(samples,1)]
boards=[];font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',18)
for start in range(0,len(records),5):
 board=Image.new('RGB',(1280,1176),'#15191e');d=ImageDraw.Draw(board)
 for j,x in enumerate(records[start:start+5]):
  xx=(j%2)*640;yy=(j//2)*392
  with Image.open(ROOT/x['path']) as im:board.paste(im.resize((640,360)),(xx,yy))
  d.text((xx+5,yy+363),f"encoded{x['frame']} PTS{x['pts']} source{x['sourceFrame']}",font=font,fill='white')
 out=local/f'board-{start//5+1:03d}.png';board.save(out);boards.append(dict(path=rel(out),sha256=sha(out),samplePaths=[x['path'] for x in records[start:start+5]]))
t=read(O/'narration-07b-guide-repair-execution-v1.json')
for x in t['protectedInputs']+t['results']:assert sha(ROOT/x['path'])==x['sha256']
state.update(status='02a-encoded-samples-awaiting-direct-review',workerExitCode=0,finishedAt=now(),ffmpegExitCode=rc,exactEncodedPtsMatched=True,samples=records,boards=boards,protectedShaMatched=True)
save(sp,state);print(json.dumps(dict(workerExitCode=0,samples=len(records),boards=len(boards),exactPts=True)),flush=True)
