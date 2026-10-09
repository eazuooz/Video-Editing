"""Single CPU2 missing changed-target frames only; reuse previously hashed native pixels."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, os, subprocess, psutil
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[3]; BASE=Path(__file__).resolve().parent
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
DEST=ROOT/'shared/output/similar-game-design/aligned-native-qa-v2'; STATE=BASE/'aligned-native-extraction-v2.json'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return p.relative_to(ROOT).as_posix()
def now():return datetime.now(timezone.utc).isoformat()
ap=argparse.ArgumentParser();ap.add_argument('--resource',required=True);args=ap.parse_args();resource=read(ROOT/args.resource)
assert (datetime.now(timezone.utc)-datetime.fromisoformat(resource['observedAt'].replace('Z','+00:00'))).total_seconds()<240
assert resource['ownHeavyJobs']==0 and resource['cpuLoadPercent']<85 and resource['freePhysicalMemoryKiB']>8_000_000
assert not STATE.exists() and not DEST.exists()
planpath=BASE/'measured-allocation-v2/plan.json';plan=read(planpath);prior=read(BASE/'measured-allocation-v1/plan.json')
old={(p['scene'],p['source'],p['sourceInFrame'],p['sourceOutFrameExclusive'],p['startFrame'],p['endFrameExclusive']) for p in prior['selectedNativeCuts']}
changed=[p for p in plan['selectedNativeCuts'] if (p['scene'],p['source'],p['sourceInFrame'],p['sourceOutFrameExclusive'],p['startFrame'],p['endFrameExclusive']) not in old]
me=psutil.Process();state=dict(schemaVersion=1,startedAt=now(),pid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),sessionId=None,status='single-CPU2-aligned-native-delta',cpuThreads=2,gpuJobs=0,resource=resource,planPath=rel(planpath),planSha256=sha(planpath),changedCuts=changed,sources=[],allBoardsDirectlyRead=False,exitCode=None,localOnly=True,finalApproval=False)
def save():
 t=STATE.with_suffix('.writing');t.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,STATE)
reuse={}
for name in ['measured-source-extraction-v1.json','action-alignment-probes-v2.json']:
 for s in read(BASE/name)['sources']:
  for f in s['frames']:reuse[(s['id'],f['sourceFrame'])]=f
DEST.mkdir();save()
try:
 for src in plan['sources']:
  cuts=[p for p in changed if p['source']==src['id']]
  if not cuts:continue
  targets={}
  def target(f,tag):targets.setdefault(f,[]).append(tag)
  for p in cuts:
   a,z=p['sourceInFrame'],p['sourceOutFrameExclusive']
   for f,k in [(a,'first'),(z-1,'last'),((a+z-1)//2,'middle')]:target(f,dict(scene=p['scene'],kind=k,finalFrame=p['startFrame']+f-a))
  for s in plan['scenes']:
   for para in s['paragraphs']:
    for f,k in [(para['localStartFrame']+15,'spoken-onset'),((para['localStartFrame']+para['localEndFrame'])//2,'paragraph-middle')]:
     p=next((p for p in cuts if p['scene']==s['id'] and p['startFrame']<=s['startFrame']+f<p['endFrameExclusive']),None)
     if p:target(p['sourceInFrame']+s['startFrame']+f-p['startFrame'],dict(scene=s['id'],kind=k,expectedKo=para['ko'],finalFrame=s['startFrame']+f))
  for sid,seconds in [('06-follow-the-space',18.9),('06-follow-the-space',20.0),('07-purpose-combination',2.0),('09-combination-in-motion',10.0),('12-check-your-reason',21.4),('12-check-your-reason',21.8)]:
   s=next(s for s in plan['scenes'] if s['id']==sid);f=s['startFrame']+round(seconds*60);p=next((p for p in cuts if p['scene']==sid and p['startFrame']<=f<p['endFrameExclusive']),None)
   if p:target(p['sourceInFrame']+f-p['startFrame'],dict(scene=sid,kind='named-action-word',finalFrame=f))
  frames=sorted(targets);folder=DEST/src['id'];folder.mkdir();source=ROOT/src['path'];assert sha(source)==src['sha256']
  missing=[f for f in frames if (src['id'],f) not in reuse]
  new={}
  if missing:
   expr='+'.join(f'eq(n,{f})' for f in missing);crop=src['crop'];crop=crop if crop.startswith('crop=') else 'crop='+crop
   cmd=[FF,'-hide_banner','-v','error','-threads','2','-i',str(source),'-an','-vf',f"select='{expr}',{crop},scale=640:360",'-vsync','0','-filter_threads','2','-threads','2','-q:v','2',str(folder/'new-frame-%04d.jpg')]
   with (folder/'extraction.log').open('x',encoding='utf-8') as log:
    proc=subprocess.Popen(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT);state.update(childPid=proc.pid,currentCommand=cmd);save();code=proc.wait()
   assert code==0;state['childPid']=None;imgs=sorted(folder.glob('new-frame-*.jpg'));assert len(imgs)==len(missing);new=dict(zip(missing,imgs))
  entries=[]
  for f in frames:
   if (src['id'],f) in reuse:
    oldf=reuse[(src['id'],f)];p=ROOT/oldf['path'];assert sha(p)==oldf['sha256'];was_reused=True
   else:p=new[f];was_reused=False
   entries.append(dict(sourceFrame=f,sourceSeconds=f/60,path=rel(p),sha256=sha(p),targets=targets[f],priorPixelsReused=was_reused))
  boards=[];font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
  for off in range(0,len(entries),6):
   board=Image.new('RGB',(1920,796),'white');draw=ImageDraw.Draw(board)
   for j,e in enumerate(entries[off:off+6]):
    x=j%3*640;y=j//3*398;board.paste(Image.open(ROOT/e['path']),(x,y));draw.text((x+5,y+361),f"{src['id']} f{e['sourceFrame']} / {e['sourceSeconds']:.4f}s",font=font,fill='black');draw.text((x+5,y+380),' | '.join(t['scene'][:2]+':'+t['kind'] for t in e['targets'])[:80],font=font,fill='black')
   p=folder/f'board-{off//6+1:02d}.jpg';board.save(p,quality=96);boards.append(dict(path=rel(p),sha256=sha(p),sourceFrames=[e['sourceFrame'] for e in entries[off:off+6]],directlyRead=False))
  state['sources'].append(dict(id=src['id'],sourceSha256=src['sha256'],frames=entries,boards=boards,newFrames=len(missing),reusedFrames=len(entries)-len(missing)));save();assert sha(source)==src['sha256'];print(json.dumps(dict(source=src['id'],frames=len(entries),new=len(missing),boards=len(boards))),flush=True)
 assert sha(planpath)==state['planSha256'];state.update(status='closed-aligned-native-awaiting-direct-review',exitCode=0,finishedAt=now());save()
except BaseException:
 state.update(status='closed-aligned-native-failed-preserving-files',exitCode=1,finishedAt=now());save();raise
