"""Single CPU2 focused correction probes; preserve all previous native QA and PCM."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, os, subprocess, psutil
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[3]; BASE=Path(__file__).resolve().parent
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
DEST=ROOT/'shared/output/similar-game-design/action-alignment-qa-v2'
STATE=BASE/'action-alignment-probes-v2.json'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return p.relative_to(ROOT).as_posix()
def now():return datetime.now(timezone.utc).isoformat()
ap=argparse.ArgumentParser();ap.add_argument('--resource',required=True);a=ap.parse_args()
resource=read(ROOT/a.resource)
assert (datetime.now(timezone.utc)-datetime.fromisoformat(resource['observedAt'].replace('Z','+00:00'))).total_seconds()<240
assert resource['ownHeavyJobs']==0 and resource['cpuLoadPercent']<85 and resource['freePhysicalMemoryKiB']>8_000_000
assert not STATE.exists() and not DEST.exists()
plan=read(BASE/'measured-allocation-v1/plan.json');me=psutil.Process()
state=dict(schemaVersion=1,startedAt=now(),pid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),sessionId=None,status='single-CPU2-action-alignment-probes',cpuThreads=2,gpuJobs=0,resource=resource,sources=[],allBoardsDirectlyRead=False,exitCode=None,localOnly=True,finalApproval=False)
def save():STATE.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n','utf-8')
targets={
 'drgs-engineer-crystalline-02':[4331,4346,4391,4451,4511,4571,4631,4691,4751,4811,4873],
 'drgs-scout-crystalline-01':[5773,5788,5848,6023,6359],
 'drgs-driller-magma-core-01':[1980,1995,2070,2160,2295,2400,2488,2489,2504,2624,2699,2780,2879,3300,3403,3505,3506,3521,3788,4069],
}
DEST.mkdir();save()
try:
 for sid,frames in targets.items():
  src=next(x for x in plan['sources'] if x['id']==sid);source=ROOT/src['path'];assert sha(source)==src['sha256']
  folder=DEST/sid;folder.mkdir();expr='+'.join(f'eq(n,{f})' for f in frames);crop=src['crop'];crop=crop if crop.startswith('crop=') else 'crop='+crop
  cmd=[FF,'-hide_banner','-v','error','-threads','2','-i',str(source),'-an','-vf',f"select='{expr}',{crop},scale=640:360",'-vsync','0','-filter_threads','2','-threads','2','-q:v','2',str(folder/'frame-%04d.jpg')]
  with (folder/'extraction.log').open('x',encoding='utf-8') as log:
   proc=subprocess.Popen(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT);state.update(childPid=proc.pid,currentCommand=cmd);save();code=proc.wait()
  assert code==0;state['childPid']=None
  imgs=sorted(folder.glob('frame-*.jpg'));assert len(imgs)==len(frames)
  font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18);boards=[]
  for k in range(0,len(imgs),6):
   board=Image.new('RGB',(1920,796),'white');draw=ImageDraw.Draw(board)
   for j,img in enumerate(imgs[k:k+6]):
    x=j%3*640;y=j//3*398;board.paste(Image.open(img),(x,y));f=frames[k+j]
    draw.text((x+5,y+364),f'{sid} f{f} / {f/60:.4f}s',font=font,fill='black')
   p=folder/f'board-{k//6+1:02d}.jpg';board.save(p,quality=96);boards.append(dict(path=rel(p),sha256=sha(p),sourceFrames=frames[k:k+6],directlyRead=False))
  state['sources'].append(dict(id=sid,sourcePath=src['path'],sourceSha256=src['sha256'],exactCrop=crop,frames=[dict(sourceFrame=f,path=rel(p),sha256=sha(p)) for f,p in zip(frames,imgs)],boards=boards));assert sha(source)==src['sha256'];save()
  print(json.dumps(dict(source=sid,frames=len(frames),boards=len(boards))),flush=True)
 state.update(status='closed-probes-awaiting-direct-review',exitCode=0,finishedAt=now());save()
except BaseException:
 state.update(status='closed-probes-failed-preserving-files',exitCode=1,finishedAt=now());save();raise
