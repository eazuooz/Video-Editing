"""Local-only candidate cue/cut/continuous-action samples; no automatic approval."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, ctypes, hashlib, json, math, os, subprocess, sys, time, traceback
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
OUT=ROOT/'shared/output/player-customization/nearby-repaired-pixels-v3'
STATE=BASE/'nearby-repaired-pixels-execution-v3.json';SESSION=STATE.with_name(STATE.stem+'.session.json')
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
read=lambda p:json.loads(p.read_text('utf-8-sig'));now=lambda:datetime.now(timezone.utc).isoformat();rel=lambda p:p.relative_to(ROOT).as_posix()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def save(p,j):
 t=p.with_name(p.name+f'.{os.getpid()}.writing')
 for n in range(60):
  try:t.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p);return
  except OSError:
   if n==59:raise
   time.sleep(.15)
ap=argparse.ArgumentParser();ap.add_argument('--resource',required=True);a=ap.parse_args();r=read(ROOT/a.resource)
assert r['ownHeavyJobs']==0 and r['cpuLoadPercent']<85 and r['freePhysicalMemoryKiB']>8000000
assert (datetime.now(timezone.utc)-datetime.fromisoformat(r['observedAt'].replace('Z','+00:00'))).total_seconds()<240
build=read(BASE/'selected-inputs-execution-v3.json');assert build['exitCode']==0
planPath=ROOT/build['allocationPath'];capPath=ROOT/build['captionPath'];assert sha(planPath)==build['allocationSha256'] and sha(capPath)==build['captionSha256']
plan=read(planPath);cap=read(capPath);video=ROOT/build['captionedSilentVideo'];assert sha(video)==build['captionedSilentSha256']
changed=[c for c in plan['cuts'] if c.get('repairNativeOnly')]
assert len(changed)==1
spans=[(c['outputStartFrame']-120,c['outputStartFrame']-120+c['frames']) for c in changed]
windows=[(max(0,a-120),min(35321,b+120)) for a,b in spans]
def in_window(n):return any(a<=n<b for a,b in windows)
assert not OUT.exists() and not STATE.exists(),'Resume existing extraction/checkpoint instead of repeating images.'
if os.name=='nt':ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x00004000)
OUT.mkdir(parents=True);frames=OUT/'frames';boards=OUT/'boards';frames.mkdir();boards.mkdir()
points={}
def add(n,why):
 if 0<=n<35321 and in_window(n):points.setdefault(n,[]).append(why)
for c in plan['cuts']:
 start=c['outputStartFrame']-120;end=start+c['frames'];add(start,'cut-first');add(end-1,'cut-last');add(start-1,'before-cut');add(end,'after-cut')
 if c['role']=='actual-game-candidate':
  for n in range(start,end,15):add(n,'action-every-quarter-second')
for c in cap['ko']:
 # Preview ASS clock is rounded to centiseconds, exactly as in the encoder.
 first=math.ceil(round((c['startSeconds']-2)*100)/100*60-1e-7)
 end=math.ceil(round((c['endSeconds']-2)*100)/100*60-1e-7)
 assert end>first
 add((first+end-1)//2,'cue-mid-'+str(c['index']))
 add(first,'cue-first-'+str(c['index']))
 add(end-1,'cue-last-'+str(c['index']))
for row in read(BASE/'current16-voice-timing-candidate-v1.json')['rows']:
 for p,sample in enumerate(row['paragraphStartSamples'],1):
  add(row['startFrame']-120+math.ceil(sample/400),'PCM-paragraph-onset-'+row['id']+'-'+str(p))
indices=sorted(points)
s=dict(schemaVersion=1,slug='player-customization',pid=os.getpid(),commandLine=[sys.executable,*sys.argv],sessionId=None,
 startedAt=now(),status='extract-selected-candidate-cue-cut-pixels',resourceEvidence=a.resource,cpuThreads=2,gpu=0,singleJob=True,
 allocationPath=build['allocationPath'],allocationSha256=build['allocationSha256'],captionPath=build['captionPath'],captionSha256=build['captionSha256'],
 sourcePath=rel(video),sourceSha256=build['captionedSilentSha256'],targetFrames=len(indices),koCueCount=415,totalCuts=139,changedCuts=1,repairWindows=windows,reviewScope="One newly replaced nearby-target sentence with two-second adjacent context; prior355+46boards retained, four other repairs passed; final full-pair pixels pending",
 samples=[],boards=[],exitCode=None,allBoardsDirectlyRead=False,allSelectedPixelsApproved=False,allFinalPixels=False,sourceAllocationApproved=False,
 finalTimingApproved=False,finalMixedAsrApproved=False,collected=False,uploaded=False,imagesLocalOnly=True,newGitImages=0)
def checkpoint():
 if SESSION.exists():
  x=read(SESSION)
  if x['pid']==os.getpid():s.update(sessionId=x['sessionId'],processIdentity=x['processIdentity'])
 s['observedAt']=now();save(STATE,s)
 job=dict(status=s['status'],pid=os.getpid(),sessionId=s['sessionId'],processIdentity=s.get('processIdentity'),commandLine=s['commandLine'],
  state=rel(STATE),cpuThreads=2,gpu=0,singleJob=True,activeTask=s.get('activeTask'),exitCode=s['exitCode'],workerExpectedRunning=s['exitCode'] is None)
 cp=read(BASE/'latest-checkpoint.json');cp.update(stage=s['status'],ownedJob=job,recordedAt=now(),actionRepairedPixelExecution=rel(STATE),
  nextAction='Read every focused repair board and affected full action/caption clause. Preserve baseline355board review and all five historical defects. Adopt current inputs only after zero unresolved defects; final mix/current mixed ASR/final full-pair pixels/QA/collection/private/Git pending.');save(BASE/'latest-checkpoint.json',cp)
 qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qp);i=next(x for x in q['items'] if x['slug']=='player-customization');i.update(stage=cp['stage'],currentExecution=job,actionRepairedPixelExecution=rel(STATE),nextAction=cp['nextAction']);q['updatedAt']=now();save(qp,q)
try:
 offset=build['captionPreviewBodyStartFrame'];assert all(0<=n-offset<build['captionPreviewFrames'] for n in indices)
 expr="select='"+'+'.join(f'eq(n,{n-offset})' for n in indices)+"'"
 filt=OUT/'extract.filter.txt';filt.write_text(expr,'utf-8')
 log=OUT/'extract.log';cmd=[FF,'-nostdin','-v','error','-threads','2','-i',str(video),'-an','-filter_threads','1','-filter_script:v',str(filt),'-fps_mode','vfr','-threads','2',str(frames/'frame-%04d.png')]
 with log.open('w',encoding='utf-8') as f:
  p=subprocess.Popen(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
  s['activeTask']=dict(pid=p.pid,commandLine=cmd,log=rel(log));checkpoint();code=p.wait()
 s.update(activeTask=None,extractExitCode=code);assert code==0,log.read_text('utf-8')
 assert len(list(frames.glob('frame-*.png')))==len(indices)
 for index,n in enumerate(indices,1):
  c=next(c for c in plan['cuts'] if c['outputStartFrame']-120<=n<c['outputStartFrame']-120+c['frames'])
  cue=[c for c in cap['ko'] if round((c['startSeconds']-2)*100)/100<=n/60<round((c['endSeconds']-2)*100)/100]
  path=frames/f'frame-{index:04d}.png'
  s['samples'].append(dict(index=index,bodyFrame=n,outputFrame=n+120,outputSeconds=(n+120)/60,scene=c['scene'],paragraph=c['paragraph'],
   role=c['role'],sourceKey=c.get('sourceKey','white'),sourceNativeFrame=c['sourceInFrame']+n-(c['outputStartFrame']-120),
   reasons=points[n],activeCues=[dict(index=c['index'],text=c['ko']) for c in cue],path=rel(path),sha256=sha(path),directlyRead=False))
 font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22)
 for start in range(0,len(s['samples']),6):
  group=s['samples'][start:start+6];im=Image.new('RGB',(2880,1240),'white');d=ImageDraw.Draw(im)
  for i,e in enumerate(group):
   x=i%3*960;y=i//3*620
   d.text((x+5,y+3),f"{e['scene']} p{e['paragraph']} / {e['sourceKey']} n{e['sourceNativeFrame']} output{e['outputFrame']}",fill='black',font=font)
   d.text((x+5,y+30),f"{e['outputSeconds']:.4f}s / cues {','.join(str(c['index']) for c in e['activeCues']) or 'none'} / {e['role']}",fill='black',font=font)
   with Image.open(ROOT/e['path']) as img:im.paste(img.convert('RGB').resize((960,540)),(x,y+65))
  path=boards/f'board-{start//6+1:03d}.png';im.save(path)
  s['boards'].append(dict(index=start//6+1,path=rel(path),sha256=sha(path),sampleIndices=[e['index'] for e in group],directlyRead=False))
 s.update(status='closed-selected-candidate-pixels-await-direct-review',exitCode=0,endedAt=now(),sampleCount=len(s['samples']),boardCount=len(s['boards']))
 checkpoint();print(json.dumps(dict(exitCode=0,frames=len(indices),boards=len(s['boards']),allApproved=False)),flush=True)
except BaseException:
 s.update(status='closed-selected-candidate-pixel-extraction-failed',exitCode=1,endedAt=now(),error=traceback.format_exc());checkpoint();raise
