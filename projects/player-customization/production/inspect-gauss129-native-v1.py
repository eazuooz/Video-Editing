"""Single CPU2 native decode/probe and exact-time research frames, no approval."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,bisect,ctypes,hashlib,json,os,subprocess,sys,time,traceback
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
OUT=ROOT/'shared/output/player-customization/research/gauss-devstream129-native-v1'
SOURCE=ROOT/'shared/output/player-customization/research/gauss-devstream129-v1/h7qntXMufKk-gauss-2244-2683.mp4'
STATE=BASE/'gauss129-native-inspection-execution-v1.json';SESSION=STATE.with_name(STATE.stem+'.session.json')
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe';PROBE='C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe'
read=lambda p:json.loads(p.read_text('utf-8-sig'));now=lambda:datetime.now(timezone.utc).isoformat();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rel=lambda p:p.relative_to(ROOT).as_posix()
ap=argparse.ArgumentParser();ap.add_argument('--resource',required=True);args=ap.parse_args();r=read(ROOT/args.resource)
assert r['ownHeavyJobs']==0 and r['cpuLoadPercent']<85 and r['freePhysicalMemoryKiB']>8000000
assert (datetime.now(timezone.utc)-datetime.fromisoformat(r['observedAt'].replace('Z','+00:00'))).total_seconds()<240
assert read(BASE/'gauss129-acquisition-execution-v1.json')['exitCode']==0
assert not STATE.exists() and not OUT.exists(),'Read actual checkpoint; never repeat inspection.'
if os.name=='nt':ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x00004000)
OUT.mkdir(parents=True)
s=dict(schemaVersion=1,slug='player-customization',pid=os.getpid(),commandLine=[sys.executable,*sys.argv],sessionId=None,startedAt=now(),status='fresh-gauss-native-probe',resourceEvidence=args.resource,cpuThreads=2,gpu=0,singleJob=True,sourcePath=rel(SOURCE),sourceSha256=sha(SOURCE),sourceVideoId='h7qntXMufKk',sourceOffsetSeconds=2244,operations=[],exitCode=None,allNativePixelsReviewed=False,actualActionApproved=False,finalAllocationApproved=False,bodyRatioApproved=False,sourceAudioUsed=False,newGitImages=0)
def save(p,j):
 t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
 for n in range(40):
  try:os.replace(t,p);return
  except OSError:
   if n==39:raise
   time.sleep(.15)
def checkpoint():
 if SESSION.exists():
  launch=read(SESSION)
  if launch['pid']==os.getpid():s.update(sessionId=launch['sessionId'],processIdentity=launch['processIdentity'])
 s['updatedAt']=now();save(STATE,s)
 job=dict(status=s['status'],pid=os.getpid(),commandLine=s['commandLine'],sessionId=s['sessionId'],processIdentity=s.get('processIdentity'),state=rel(STATE),cpuThreads=2,gpu=0,singleJob=True,exitCode=s['exitCode'],workerExpectedRunning=s['exitCode'] is None)
 cp=read(BASE/'latest-checkpoint.json');cp.update(stage=s['status'],ownedJob=job,recordedAt=now(),nextAction='Directly read all fresh exact-native research boards, identify unique ring/movement/target relations, then allocate matching actions and white bridges without loops or idle. Final cue/crop/ratio/mix/private approval remains false.');save(BASE/'latest-checkpoint.json',cp)
 qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qp);i=next(i for i in q['items'] if i['slug']=='player-customization');i.update(stage=cp['stage'],currentExecution=job,nextAction=cp['nextAction']);q['updatedAt']=now();save(qp,q)
def run(name,cmd):
 op=dict(name=name,commandLine=cmd,startedAt=now());s['operations'].append(op);s['status']=name;checkpoint();p=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE);op['pid']=p.pid;checkpoint();out,err=p.communicate();op.update(exitCode=p.returncode,finishedAt=now());(OUT/(name+'.stderr.log')).write_bytes(err);checkpoint();assert p.returncode==0,err.decode('utf-8','replace');return out
try:
 checkpoint();raw=run('probe-gauss-native',[PROBE,'-v','error','-threads','2','-show_streams','-show_format','-of','json',str(SOURCE)]);probe=json.loads(raw);(OUT/'probe.json').write_bytes(raw);s['probe']=probe
 v=next(x for x in probe['streams'] if x['codec_type']=='video');assert v['width']==1920 and v['height']==1080
 run('decode-whole-gauss-native',[FF,'-nostdin','-v','error','-threads','2','-i',str(SOURCE),'-an','-f','null','-']);s['wholeDecodeExitCode']=0
 raw=run('probe-gauss-native-frames',[PROBE,'-v','error','-threads','2','-select_streams','v:0','-show_frames','-show_entries','frame=best_effort_timestamp,best_effort_timestamp_time','-of','json',str(SOURCE)]);(OUT/'native-frame-pts.json').write_bytes(raw);fs=json.loads(raw)['frames'];pts=[float(f['best_effort_timestamp_time']) for f in fs];assert all(b>a for a,b in zip(pts,pts[1:]))
 indices=sorted(set([0,len(pts)-1]+[bisect.bisect_left(pts,t+.025) for t in range(0,int(pts[-1]),5)]));assert max(indices)<len(pts)
 folder=OUT/'native';folder.mkdir();expr='+'.join(f'eq(n,{n})' for n in indices)
 run('extract-gauss-native-research',[FF,'-nostdin','-v','error','-threads','2','-i',str(SOURCE),'-vf',f"select='{expr}'",'-fps_mode','vfr','-an','-threads','2',str(folder/'frame-%04d.png')])
 samples=[dict(frameIndex=n,nativePts=int(fs[n]['best_effort_timestamp']),nativeSeconds=pts[n],sourceSeconds=2244+pts[n],path=rel(folder/f'frame-{ix:04d}.png'),sha256=sha(folder/f'frame-{ix:04d}.png')) for ix,n in enumerate(indices,1)]
 from PIL import Image,ImageDraw,ImageFont
 boards=[];bf=OUT/'boards';bf.mkdir();font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',23)
 for start in range(0,len(samples),4):
  group=samples[start:start+4];im=Image.new('RGB',(1920,1160),'white');draw=ImageDraw.Draw(im)
  for i,e in enumerate(group):
   x,y=i%2*960,i//2*580;draw.text((x+8,y+5),f"Gauss129 actual{e['nativeSeconds']:.4f}s / source{e['sourceSeconds']:.4f}s n{e['frameIndex']}",fill='black',font=font);im.paste(Image.open(ROOT/e['path']).convert('RGB').resize((960,540)),(x,y+35))
  target=bf/f'board-{start//4+1:02d}.png';im.save(target);boards.append(dict(index=start//4+1,path=rel(target),sha256=sha(target),entries=group))
 s.update(status='fresh-gauss-native-boards-await-direct-reading',exitCode=0,finishedAt=now(),nativeFrameCount=len(fs),nativeDuration=float(probe['format']['duration']),samples=samples,boards=boards,sampleCount=len(samples),boardCount=len(boards));checkpoint();print(json.dumps({'exitCode':0,'samples':len(samples),'boards':len(boards),'sourceSha256':s['sourceSha256']}),flush=True)
except BaseException:
 s.update(status='fresh-gauss-native-inspection-failed',exitCode=1,error=traceback.format_exc(),finishedAt=now());checkpoint();raise
