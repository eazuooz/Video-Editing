"""Verify one actual MC render, correct its terminal export frame, inspect motion."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,ctypes,hashlib,json,os,subprocess,sys,time,traceback
import psutil
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
OUT=ROOT/'shared/output/similar-game-design/white-measured-v1'
RAW=OUT/'authoring-project-v1.mp4';EXACT=OUT/'white-measured-v1.exact.mp4'
STATE=BASE/'white-measured-verification-v1.json';SESSION=BASE/'white-measured-verification-v1.session.json'
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe';PROBE='C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe'
now=lambda:datetime.now(timezone.utc).isoformat()
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
def save(p,j):
 t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
 for n in range(40):
  try:os.replace(t,p);return
  except OSError:
   if n==39:raise
   time.sleep(.15)
args=argparse.ArgumentParser();args.add_argument('--resource',required=True);args=args.parse_args()
assert not STATE.exists() and not EXACT.exists(),'Preserve prior execution/output'
resource=read(ROOT/args.resource);assert resource['ownHeavyJobs']==0 and resource['cpuLoadPercent']<85 and resource['freePhysicalMemoryKiB']>8000000
assert (datetime.now(timezone.utc)-datetime.fromisoformat(resource['observedAt'])).total_seconds()<180
ui=OUT/'preflight/gui-render-returned.ax.txt';assert 'button RENDER' in ui.read_text('utf-8') and '[ 14551 ]' in ui.read_text('utf-8')
owner=read(BASE/'white-measured-actual-process-v1.json')
if psutil.pid_exists(owner['ProcessId']):
 p=psutil.Process(owner['ProcessId']);assert abs(p.create_time()-datetime.fromisoformat(owner['CreationDate']).timestamp())>1,'Original encoder still alive'
planPath=BASE/'measured-allocation-v2/plan.json';plan=read(planPath)
timingPath=ROOT/'motion-canvas/src/projects/similar-game-design/measured-timing-v1.json';timing=read(timingPath)
captionsPath=BASE/'caption-candidate-v2/captions.json';captions=read(captionsPath)
assert timing['plan']['sha256']==sha(planPath)==captions['plan']['sha256']
assert timing['whiteFrames']==14551 and len(timing['white'])==19 and plan['sourceAllocationApproved']
if os.name=='nt':ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x00004000)
state=dict(schemaVersion=1,slug='similar-game-design',startedAt=now(),status='verify-white-measured-starting',pid=os.getpid(),createTime=psutil.Process().create_time(),commandLine=[sys.executable,*sys.argv],sessionId=None,cpuThreads=2,gpuJobs=0,singleJob=True,resourceEvidence=args.resource,operations=[],exitCode=None,plan=dict(path=rel(planPath),sha256=sha(planPath)),timing=dict(path=rel(timingPath),sha256=sha(timingPath)),captionCandidate=dict(path=rel(captionsPath),sha256=sha(captionsPath)),guiCompletionObserved=True,encoderExitCodeObserved=False,finalTimingApproved=False,allAnimatedMeasuredPixelsReviewed=False,allFinalPixelsReviewed=False,finalMixedAsrApproved=False,render=False,qa=False,collected=False,uploaded=False)
def checkpoint():
 if SESSION.exists():
  se=read(SESSION)
  if se['pid']==os.getpid():state['sessionId']=se['sessionId']
 state['updatedAt']=now();save(STATE,state)
 cp=read(BASE/'latest-checkpoint.json');cp.update(stage=state['status'],ownedJob=dict(pid=os.getpid(),createTime=state['createTime'],commandLine=state['commandLine'],sessionId=state['sessionId'],cpuThreads=2,gpuJobs=0,state=rel(STATE),workerExpectedRunning=state['exitCode'] is None,exitCode=state['exitCode'],actualExitObserved=False),whiteMeasuredVerification=rel(STATE),captionCandidate=rel(captionsPath),nextAction='Directly read all measured white paragraph-motion boards; final captions/mix/pair/all-final-pixel gates remain false.',updatedAt=now());save(BASE/'latest-checkpoint.json',cp)
 qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qp);item=next(i for i in q['items']if i['slug']=='similar-game-design');item.update(stage=cp['stage'],currentExecution=cp['ownedJob'],whiteMeasuredVerification=rel(STATE),captionCandidate=rel(captionsPath),nextAction=cp['nextAction'],updatedAt=now());save(qp,q)
def run(name,cmd):
 state['status']=name;op=dict(name=name,commandLine=cmd,startedAt=now());state['operations'].append(op);checkpoint()
 p=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE);op['pid']=p.pid;checkpoint();out,err=p.communicate();op.update(exitCode=p.returncode,finishedAt=now());(OUT/(name+'.stderr.log')).write_bytes(err);checkpoint();assert p.returncode==0,err.decode('utf-8','replace');return out
def probe(p,name):return json.loads(run(name,[PROBE,'-v','error','-threads','2','-show_entries','stream=codec_type,codec_name,width,height,r_frame_rate,time_base,duration,nb_frames','-of','json',str(p)]))
try:
 checkpoint();raw=probe(RAW,'probe-raw-white');v=raw['streams'][0]
 assert v['nb_frames']=='14552' and v['r_frame_rate']=='60/1' and v['time_base']=='1/90000' and len(raw['streams'])==1
 state['rawRender']=dict(path=rel(RAW),sha256=sha(RAW),probe=raw,guiCompleted=True,encoderAbsentObserved=True,actualEncoderExitCodeObserved=False)
 state['terminalAdjustment']=dict(rawFrames=14552,expectedFrames=14551,removedDisplayFrames=[14551],reason='Actual MC export includes its terminal endpoint frame. Preserve raw render and every PCM sample; trim only the extra final visual display frame.',streamCopyAvoided='Prior verified producer encountered missing middle B-frame with packet-order trimming; use display-order trim and exact re-encode.')
 run('trim-terminal-display-frame',[FF,'-nostdin','-v','error','-threads','2','-i',str(RAW),'-map','0:v:0','-an','-vf','trim=end_frame=14551,setpts=N/(60*TB)','-frames:v','14551','-c:v','libx264','-threads','2','-filter_threads','1','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-r','60','-video_track_timescale','90000','-movflags','+faststart',str(EXACT)])
 current=probe(EXACT,'probe-exact-white');v=current['streams'][0];assert v['nb_frames']=='14551' and v['time_base']=='1/90000' and v['duration']=='242.516667'
 pts=json.loads(run('probe-all-white-pts',[PROBE,'-v','error','-threads','2','-select_streams','v:0','-show_frames','-show_entries','frame=best_effort_timestamp','-of','json',str(EXACT)]));ticks=[int(f['best_effort_timestamp'])for f in pts['frames']];assert ticks==list(range(0,14551*1500,1500))
 run('decode-entire-exact-white',[FF,'-nostdin','-v','error','-threads','2','-i',str(EXACT),'-an','-f','null','-'])
 state['currentWhite']=dict(path=rel(EXACT),sha256=sha(EXACT),probe=current,wholeDecodeExitCode=0,allPtsCount=len(ticks),firstPts=ticks[0],lastPts=ticks[-1],contiguousTicks1500=True)
 samples=[]
 for row in timing['white']:
  a=row['timeOffsetSeconds'];b=a+row['durationSeconds'];offset=row['whiteProjectStartFrame'];frames=row['frames'];scene=next(s for s in plan['scenes']if s['id']==row['id'])
  samples.extend([dict(scene=row['id'],part=row['part'],paragraph=None,phase=phase,frame=offset+f)for phase,f in [('part-start',0),('part-end',frames-1)]])
  for p in captions['paragraphs']:
   if p['scene']!=row['id']:continue
   start=max(a,p['sourceSpeechStart']);end=min(b,p['sourceSpeechEnd'])
   if end<=start:continue
   for phase in [.12,.5,.88]:
    f=min(frames-1,max(0,round((start+(end-start)*phase-a)*60)));samples.append(dict(scene=row['id'],part=row['part'],paragraph=p['paragraph'],phase=phase,frame=offset+f))
 byframe={}
 for s in samples:byframe.setdefault(s['frame'],[]).append(s)
 frames=sorted(byframe);native=OUT/'motion-qa-native';boards=OUT/'motion-qa-boards';native.mkdir();boards.mkdir()
 expr='+'.join(f'eq(n,{n})'for n in frames)
 run('extract-all-measured-white-paragraph-motion',[FF,'-nostdin','-v','error','-threads','2','-i',str(EXACT),'-vf',f"select='{expr}'",'-fps_mode','vfr','-an','-threads','2',str(native/'frame-%03d.png')])
 assert len(list(native.glob('frame-*.png')))==len(frames)
 images=[]
 for i,f in enumerate(frames,1):
  p=native/f'frame-{i:03d}.png';images.append(dict(frame=f,path=rel(p),sha256=sha(p),observations=byframe[f]))
 font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20);boardrows=[]
 for bi,start in enumerate(range(0,len(images),6),1):
  board=Image.new('RGB',(1920,1224),'white');draw=ImageDraw.Draw(board);group=images[start:start+6]
  for ci,p in enumerate(group):
   x=(ci%3)*640;y=(ci//3)*612;description='; '.join(f'{s["scene"]} p{s["paragraph"]} {s["phase"]}'for s in p['observations']);draw.text((x+8,y+6),description[:68],font=font,fill='black')
   image=Image.open(ROOT/p['path']).convert('RGB');image.thumbnail((640,360));board.paste(image,(x,y+40));draw.text((x+8,y+408),f'white frame {p["frame"]} | {p["frame"]/60:.3f}s',font=font,fill='black')
  p=boards/f'board-{bi:02d}.jpg';board.save(p,quality=94);boardrows.append(dict(path=rel(p),sha256=sha(p),entries=group,directlyRead=False))
 state.update(status='measured-white-exact-decoded-motion-await-direct-review',exitCode=0,finishedAt=now(),frames=14551,whiteParts=19,samplePlan=samples,uniqueSampleFrames=len(images),boards=boardrows,allOriginalPcmPreserved=True)
 checkpoint();print(json.dumps(dict(frames=14551,whiteParts=19,motionFrames=len(images),boards=len(boardrows),wholeDecodeExitCode=0,pixelsReviewed=False)),flush=True)
except BaseException:
 state.update(status='failed-white-measured-verification',exitCode=1,finishedAt=now(),error=traceback.format_exc());checkpoint();raise
