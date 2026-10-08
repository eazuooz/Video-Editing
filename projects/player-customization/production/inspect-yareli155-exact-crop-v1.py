"""One CPU2 exact-native research crop extraction; no final approval."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,bisect,ctypes,hashlib,json,os,subprocess,sys,time,traceback
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
OUT=ROOT/'shared/output/player-customization/research/yareli155-exact-crop-v1'
STATE=BASE/'yareli155-exact-crop-execution-v1.json';SESSION=STATE.with_name(STATE.stem+'.session.json')
SOURCE=ROOT/'shared/output/player-customization/research/yareli-devstream155-v1/8eUfnQ8mWXs-yareli-2721-3087.mp4'
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
read=lambda p:json.loads(p.read_text('utf-8-sig'));now=lambda:datetime.now(timezone.utc).isoformat();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rel=lambda p:p.relative_to(ROOT).as_posix()
ap=argparse.ArgumentParser();ap.add_argument('--resource',required=True);args=ap.parse_args();r=read(ROOT/args.resource)
assert r['ownHeavyJobs']==0 and r['cpuLoadPercent']<85 and r['freePhysicalMemoryKiB']>8000000
assert (datetime.now(timezone.utc)-datetime.fromisoformat(r['observedAt'].replace('Z','+00:00'))).total_seconds()<240
native=read(BASE/'yareli155-native-inspection-execution-v1.json');assert native['exitCode']==0 and native['allNativePixelsReviewed']
assert sha(SOURCE)==native['sourceSha256']
assert not STATE.exists() and not OUT.exists(),'Read actual checkpoint; never repeat extraction.'
if os.name=='nt':ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x00004000)
OUT.mkdir(parents=True)
windows=[[112,138],[142,154],[157,164],[169,191],[208,212],[218,236],[239,247],[273,282]]
s=dict(schemaVersion=1,slug='player-customization',pid=os.getpid(),commandLine=[sys.executable,*sys.argv],sessionId=None,startedAt=now(),status='prepare-exact-yareli-crop',resourceEvidence=args.resource,cpuThreads=2,gpu=0,singleJob=True,sourcePath=rel(SOURCE),sourceSha256=native['sourceSha256'],sourceVideoId='8eUfnQ8mWXs',windows=windows,crop=dict(x=550,y=25,w=1216,h=684),operations=[],exitCode=None,allCropSamplesDirectlyRead=False,actualActionApproved=False,finalAllocationApproved=False,bodyRatioApproved=False,sourceAudioUsed=False,newGitImages=0)
def save(p,j):
 t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
 for n in range(40):
  try:os.replace(t,p);return
  except OSError:
   if n==39:raise
   time.sleep(.15)
def checkpoint():
 if SESSION.exists():
  l=read(SESSION)
  if l['pid']==os.getpid():s.update(sessionId=l['sessionId'],processIdentity=l['processIdentity'])
 s['updatedAt']=now();save(STATE,s)
 job=dict(status=s['status'],pid=os.getpid(),commandLine=s['commandLine'],sessionId=s['sessionId'],processIdentity=s.get('processIdentity'),state=rel(STATE),cpuThreads=2,gpu=0,singleJob=True,exitCode=s['exitCode'],workerExpectedRunning=s['exitCode'] is None)
 cp=read(BASE/'latest-checkpoint.json');cp.update(stage=s['status'],ownedJob=job,recordedAt=now(),nextAction='Directly read every selected native crop sample, trim clipped caster/targets/idle/popups, then source-grounded integer allocation. Final caption/ratio/mix/private gates remain false.');save(BASE/'latest-checkpoint.json',cp)
 qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qp);i=next(i for i in q['items'] if i['slug']=='player-customization');i.update(stage=cp['stage'],currentExecution=job,nextAction=cp['nextAction']);q['updatedAt']=now();save(qp,q)
try:
 checkpoint();fs=read(ROOT/'shared/output/player-customization/research/yareli-devstream155-native-v1/native-frame-pts.json')['frames'];pts=[float(f['best_effort_timestamp_time']) for f in fs]
 targets=[]
 for wi,(a,b) in enumerate(windows,1):
  t=a
  while t<b:
   targets.append((wi,bisect.bisect_left(pts,t)));t+=.75
  targets.append((wi,bisect.bisect_left(pts,b)-1))
 indices=sorted(set(n for _,n in targets));assert max(indices)<len(pts)
 folder=OUT/'cropped';folder.mkdir();expr='+'.join(f'eq(n,{n})' for n in indices)
 cmd=[FF,'-nostdin','-v','error','-threads','2','-i',str(SOURCE),'-vf',f"select='{expr}',crop=1216:684:550:25",'-fps_mode','vfr','-an','-threads','2',str(folder/'frame-%04d.png')]
 s['status']='extract-exact-yareli155-crops';op=dict(name=s['status'],commandLine=cmd,startedAt=now());s['operations'].append(op);checkpoint();p=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE);op['pid']=p.pid;checkpoint();stdout,stderr=p.communicate();(OUT/'extract.stderr.log').write_bytes(stderr);op.update(exitCode=p.returncode,finishedAt=now());assert p.returncode==0,stderr.decode('utf-8','replace')
 lookup={n:i for i,n in enumerate(indices,1)};samples=[]
 for wi,n in targets:
  p=folder/f'frame-{lookup[n]:04d}.png';samples.append(dict(window=wi,frameIndex=n,nativePts=int(fs[n]['best_effort_timestamp']),nativeSeconds=pts[n],sourceSeconds=2721+pts[n],path=rel(p),sha256=sha(p)))
 from PIL import Image,ImageDraw,ImageFont
 boards=[];bf=OUT/'boards';bf.mkdir();font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22)
 for start in range(0,len(samples),4):
  group=samples[start:start+4];im=Image.new('RGB',(1920,1160),'white');d=ImageDraw.Draw(im)
  for i,e in enumerate(group):
   x,y=i%2*960,i//2*580;d.text((x+5,y+4),f"Yareli155 window{e['window']} actual{e['nativeSeconds']:.4f}s n{e['frameIndex']}",fill='black',font=font);im.paste(Image.open(ROOT/e['path']).convert('RGB').resize((960,540)),(x,y+35))
  p=bf/f'board-{start//4+1:02d}.png';im.save(p);boards.append(dict(index=start//4+1,path=rel(p),sha256=sha(p),entries=group))
 s.update(status='exact-yareli155-crops-await-direct-review',exitCode=0,finishedAt=now(),samples=samples,sampleCount=len(samples),uniqueFrameCount=len(indices),boards=boards,boardCount=len(boards));checkpoint();print(json.dumps({'exitCode':0,'sampleCount':len(samples),'boards':len(boards)}),flush=True)
except BaseException:
 s.update(status='exact-yareli155-crop-failed',exitCode=1,error=traceback.format_exc(),finishedAt=now());checkpoint();raise
