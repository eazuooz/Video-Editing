"""Verify the actual CUA render and sample narration-timed motion once, CPU2."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, ctypes, hashlib, json, os, subprocess, sys, time, traceback
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
STATE=BASE/'current-white-source-verification-v1.json';SESSION=BASE/'current-white-source-verification-v1.session.json'
OUT=ROOT/'shared/output/player-customization/white-current-voice-v1'
RAW=OUT/'player-customization-current-voice-white-v1.mp4';CURRENT=OUT/'player-customization-current-voice-white-v1.exact.mp4'
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe';PROBE='C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe'
def now():return datetime.now(timezone.utc).isoformat()
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return p.relative_to(ROOT).as_posix()
def save(p,d):
 t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf-8')
 for n in range(40):
  try:os.replace(t,p);return
  except OSError:
   if n==39:raise
   time.sleep(.15)
parser=argparse.ArgumentParser();parser.add_argument('--resource',required=True);parser.add_argument('--resume-timestamp-repair',action='store_true');args=parser.parse_args()
assert RAW.exists()
prior=read(STATE) if args.resume_timestamp_repair else None
if prior:
 assert prior['status']=='failed-white-source-verification' and CURRENT.exists()
 assert prior['operations'][-1]['name']=='probe-all-current-pts' and all(o['exitCode']==0 for o in prior['operations'])
 assert prior['rawRender']['sha256']==sha(RAW)
else:assert not STATE.exists() and not CURRENT.exists()
resource=read(ROOT/args.resource)
assert resource['ownHeavyJobs']==0 and resource['cpuLoadPercent']<85 and resource['freePhysicalMemoryKiB']>16000000
assert (datetime.now(timezone.utc)-datetime.fromisoformat(resource['observedAt'])).total_seconds()<240
assert 'RENDER' in (ROOT/'shared/output/player-customization/preflight/measured-mc-render-returned.ax.txt').read_text('utf-8')
if os.name=='nt':ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x00004000)
state={'schemaVersion':1,'slug':'player-customization','startedAt':now(),'pid':os.getpid(),'commandLine':[sys.executable,*sys.argv],
 'status':'probing-actual-white-source','sessionId':None,'cpuThreads':2,'gpuJobs':0,'singleJob':True,'resourceEvidence':args.resource,
 'operations':[],'exitCode':None,'actualAnimatedPixelsReviewed':False,'finalCaptionPixelsReviewed':False,'finalVideoComplete':False}
if prior:
 state.update(history=[prior],rawRender=prior['rawRender'],endpointAdjustment=prior['endpointAdjustment'],
  timestampRepair={'failedCopyPtsCount':13439,'failedCopyLastPts':20158500,'requiredLastPts':20157000,
   'reason':'Stream-copy packet trimming retained the last B-frame while omitting the preceding display frame. Decode-order trimming and CPU re-encoding are required. Original CUA render and every original PCM sample are preserved.',
   'actualFailureExitObserved':True,'previousSessionId':18218,'previousWorkerPid':prior['pid']})
def checkpoint():
 if SESSION.exists():
  se=read(SESSION)
  if se.get('pid')==os.getpid():state['sessionId']=se['sessionId'];state['processIdentity']=se['processIdentity']
 state['updatedAt']=now();save(STATE,state)
 job={'pid':state['pid'],'commandLine':state['commandLine'],'sessionId':state['sessionId'],'processIdentity':state.get('processIdentity'),
   'state':rel(STATE),'status':state['status'],'cpuThreads':2,'gpu':0,'singleJob':True,'operations':state['operations'],'exitCode':state['exitCode'],
   'next':'Read all96 source motion samples before approval; additional observation guides and final ratio/mixed captions/render remain pending.'}
 cp=read(BASE/'latest-checkpoint.json');cp.update(recordedAt=now(),stage=state['status'],ownedJob=job,nextAction=job['next']);save(BASE/'latest-checkpoint.json',cp)
 qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qp);i=next(i for i in q['items'] if i['slug']=='player-customization')
 i.update(stage=cp['stage'],currentExecution=job.copy(),nextAction=cp['nextAction']);q['updatedAt']=now();q['lastProgressAt']=now();save(qp,q)
def run(name,cmd):
 state['status']=name;op={'name':name,'commandLine':cmd,'startedAt':now()};state['operations'].append(op);checkpoint()
 p=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE);op['pid']=p.pid;checkpoint();out,err=p.communicate()
 op.update(exitCode=p.returncode,finishedAt=now());(OUT/(name+'.stderr.log')).write_bytes(err);checkpoint()
 assert p.returncode==0,err.decode('utf-8','replace');return out
try:
 checkpoint()
 raw=read(BASE/'current-voice-spatial-render-preparation-v1.json');assert raw['plannedWhiteSourceFrames']==13439
 if prior:
  historical=OUT/'player-customization-current-voice-white-v1.failed-copy-pts.mp4'
  assert not historical.exists();CURRENT.replace(historical)
  state['timestampRepair']['failedCopyPreserved']={'path':rel(historical),'sha256':sha(historical)};checkpoint()
  run('trim-display-order-terminal-frame-cpu-reencode',[FF,'-nostdin','-v','error','-threads','2','-i',str(RAW),'-map','0:v:0','-an',
   '-vf','trim=end_frame=13439,setpts=N/(60*TB)','-frames:v','13439','-c:v','libx264','-threads','2','-preset','veryfast','-crf','18',
   '-pix_fmt','yuv420p','-r','60','-video_track_timescale','90000','-movflags','+faststart',str(CURRENT)])
 else:
  probe=json.loads(run('probe-raw-render',[PROBE,'-v','error','-threads','2','-show_entries','stream=codec_type,codec_name,width,height,r_frame_rate,time_base,duration,nb_frames','-of','json',str(RAW)]))
  video=probe['streams'][0];assert video['nb_frames']=='13440' and video['time_base']=='1/90000' and video['r_frame_rate']=='60/1'
  state.update(rawRender={'path':rel(RAW),'sha256':sha(RAW),'probe':probe,'actualGuiReturnedToRenderButton':True,'encoder56528AbsentObserved':True,'encoderExitCodeObserved':False},
   endpointAdjustment={'plannedFrames':13439,'actualRawFrames':13440,'adjustmentFrames':1,'reason':'Actual exported file includes one extra terminal video frame; no narration/audio input is trimmed. Raw preserved.'})
  run('trim-one-terminal-video-frame',[FF,'-nostdin','-v','error','-threads','2','-i',str(RAW),'-map','0:v:0','-an','-c:v','copy','-frames:v','13439','-video_track_timescale','90000','-movflags','+faststart',str(CURRENT)])
 currentProbe=json.loads(run('probe-current-exact',[PROBE,'-v','error','-show_entries','stream=codec_type,codec_name,width,height,r_frame_rate,time_base,duration,nb_frames','-of','json',str(CURRENT)]))
 cv=currentProbe['streams'][0];assert cv['nb_frames']=='13439' and cv['time_base']=='1/90000' and cv['duration']=='223.983333'
 pts=json.loads(run('probe-all-current-pts',[PROBE,'-v','error','-threads','2','-select_streams','v:0','-show_frames','-show_entries','frame=best_effort_timestamp','-of','json',str(CURRENT)]))
 ticks=[int(f['best_effort_timestamp']) for f in pts['frames']];assert ticks==list(range(0,13439*1500,1500))
 run('whole-current-white-decode',[FF,'-nostdin','-v','error','-threads','2','-i',str(CURRENT),'-an','-f','null','-'])
 timing=read(ROOT/'motion-canvas/src/projects/player-customization/current-voice-timing-v1.json')
 rows=timing['rows'];plan=[];offset=0
 for row in rows:
  starts=row['paragraphStarts'];ends=starts[1:]+[row['durationSeconds']]
  for pi,(a,b) in enumerate(zip(starts,ends),1):
   for fraction in [.18,.5,.82]:
    frame=min(offset+row['frames']-1,offset+round((a+(b-a)*fraction)*60))
    plan.append({'scene':row['id'],'paragraph':pi,'phase':fraction,'frame':frame,'seconds':frame/60})
  offset+=row['frames']
 assert offset==13439 and len(plan)==96 and len({p['frame'] for p in plan})==96
 native=OUT/'motion-qa-native';boards=OUT/'motion-qa-boards';native.mkdir();boards.mkdir()
 expr='+'.join(f'eq(n,{p["frame"]})' for p in plan)
 run('extract96-narration-timed-motion-frames',[FF,'-nostdin','-v','error','-threads','2','-i',str(CURRENT),'-vf',f"select='{expr}'",'-fps_mode','vfr','-an','-threads','2',str(native/'frame-%03d.png')])
 from PIL import Image,ImageDraw,ImageFont
 font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',21);boardrows=[]
 assert len(list(native.glob('frame-*.png')))==96
 for i,p in enumerate(plan,1):p.update(path=rel(native/f'frame-{i:03d}.png'),sha256=sha(native/f'frame-{i:03d}.png'))
 for bi,start in enumerate(range(0,96,4),1):
  board=Image.new('RGB',(1920,1170),'white');draw=ImageDraw.Draw(board);group=plan[start:start+4]
  for ci,p in enumerate(group):
   x=(ci%2)*960;y=(ci//2)*585
   draw.text((x+8,y+6),f'{p["scene"]} p{p["paragraph"]} phase{p["phase"]} | frame{p["frame"]}',fill='black',font=font)
   image=Image.open(ROOT/p['path']).convert('RGB');image.thumbnail((960,540));board.paste(image,(x,y+45))
  path=boards/f'board-{bi:02d}.png';board.save(path);boardrows.append({'path':rel(path),'sha256':sha(path),'entries':group})
 state.update(status='exact-white-source-decoded96-motion-pixels-await-direct-review',exitCode=0,finishedAt=now(),
  currentWhite={'path':rel(CURRENT),'sha256':sha(CURRENT),'probe':currentProbe,'wholeDecodeExitCode':0,'allPtsCount':len(ticks),'firstPts':ticks[0],'lastPts':ticks[-1],'contiguousTicks1500':True},
  samplePlan=plan,boards=boardrows,allOriginalPcmPreserved=True,allOriginalWhiteDurationPreserved=True,
  finalMixedAsrApproved=False,bodyRatioApproved=False,allFinalPixelsReviewed=False)
 checkpoint();print(json.dumps({'sourceFrames':13439,'rawFrames':13440,'decodeExitCode':0,'samples':96,'boards':24,'pixelsReviewed':False}),flush=True)
except BaseException:
 state.update(status='failed-white-source-verification',exitCode=1,finishedAt=now(),error=traceback.format_exc());checkpoint();raise
