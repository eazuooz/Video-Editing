"""Verify only the actual01/05 correction render and24 motion samples, CPU2."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,ctypes,hashlib,json,os,subprocess,time,sys,traceback
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
STATE=BASE/'white-fixes-verification-v2.json';SESSION=BASE/'white-fixes-verification-v2.session.json'
OUT=ROOT/'shared/output/player-customization/white-fixes-v2'
RAW=OUT/'player-customization-white-fixes-v2.mp4';EXACT=OUT/'player-customization-white-fixes-v2.exact.mp4'
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe';PROBE='C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe'
def now():return datetime.now(timezone.utc).isoformat()
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return p.relative_to(ROOT).as_posix()
def save(p,v):
 t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
 for n in range(40):
  try:os.replace(t,p);return
  except OSError:
   if n==39:raise
   time.sleep(.15)
parser=argparse.ArgumentParser();parser.add_argument('--resource',required=True);args=parser.parse_args()
assert not STATE.exists() and not EXACT.exists()
resource=read(ROOT/args.resource);prep=read(BASE/'scoped-white-fixes-preparation-v2.json')
assert resource['ownHeavyJobs']==0 and resource['cpuLoadPercent']<85 and resource['freePhysicalMemoryKiB']>16000000
assert (datetime.now(timezone.utc)-datetime.fromisoformat(resource['observedAt'].replace('Z','+00:00'))).total_seconds()<240
assert prep['plannedFrames']==3001 and 'RENDER' in (ROOT/'shared/output/player-customization/preflight/white-fixes-render-returned-v2.ax.txt').read_text('utf-8')
assert sha(ROOT/prep['originalSourcePreserved']['path'])==prep['originalSourcePreserved']['sha256']
if os.name=='nt':ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x00004000)
state={'schemaVersion':1,'slug':'player-customization','pid':os.getpid(),'commandLine':[sys.executable,*sys.argv],'startedAt':now(),
 'status':'verifying-scoped-white-fixes','sessionId':None,'resourceEvidence':args.resource,'cpuThreads':2,'gpu':0,'singleJob':True,
 'operations':[],'exitCode':None,'fixPixelsApproved':False,'allFinalPixelsReviewed':False,'finalVideoComplete':False}
def checkpoint():
 if SESSION.exists():
  se=read(SESSION)
  if se['pid']==os.getpid():state.update(sessionId=se['sessionId'],processIdentity=se['processIdentity'])
 state['updatedAt']=now();save(STATE,state)
 job={'status':state['status'],'pid':os.getpid(),'commandLine':state['commandLine'],'sessionId':state['sessionId'],
  'processIdentity':state.get('processIdentity'),'state':rel(STATE),'cpuThreads':2,'gpu':0,'singleJob':True,'exitCode':state['exitCode'],
  'next':'Read the six boards/24 samples of01/05 fixes, then measure source-grounded observation-guide voice in one CPU2 job.'}
 cp=read(BASE/'latest-checkpoint.json');cp.update(recordedAt=now(),stage=state['status'],ownedJob=job,nextAction=job['next']);save(BASE/'latest-checkpoint.json',cp)
 qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qp);item=next(i for i in q['items'] if i['slug']=='player-customization');item.update(stage=cp['stage'],currentExecution=job,nextAction=job['next']);q['updatedAt']=now();save(qp,q)
def run(name,cmd):
 op={'name':name,'commandLine':cmd,'startedAt':now()};state['operations'].append(op);state['status']=name;checkpoint()
 p=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE);op['pid']=p.pid;checkpoint();out,err=p.communicate()
 op.update(exitCode=p.returncode,finishedAt=now());(OUT/(name+'.stderr.log')).write_bytes(err);checkpoint();assert p.returncode==0,err.decode('utf-8','replace');return out
try:
 checkpoint()
 rawprobe=json.loads(run('probe-actual-fix-render',[PROBE,'-v','error','-show_entries','stream=codec_type,width,height,r_frame_rate,time_base,duration,nb_frames','-of','json',str(RAW)]))
 v=rawprobe['streams'][0];assert v['nb_frames']=='3002' and v['time_base']=='1/90000'
 state['rawRender']={'path':rel(RAW),'sha256':sha(RAW),'probe':rawprobe,'actualGuiReturnedToRenderObserved':True,'encoder59552AbsentObserved':True,'encoderExitCodeObserved':False}
 state['endpointAdjustment']={'rawFrames':3002,'currentFrames':3001,'displayOrderTrim':True,'audioTrimmed':False,'allOriginalPcmPreserved':True}
 run('trim-one-terminal-display-frame',[FF,'-nostdin','-v','error','-threads','2','-i',str(RAW),'-map','0:v:0','-an','-vf','trim=end_frame=3001,setpts=N/(60*TB)',
  '-frames:v','3001','-c:v','libx264','-threads','2','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-r','60','-video_track_timescale','90000','-movflags','+faststart',str(EXACT)])
 probe=json.loads(run('probe-exact-fixes',[PROBE,'-v','error','-show_entries','stream=codec_type,width,height,r_frame_rate,time_base,duration,nb_frames','-of','json',str(EXACT)]))
 assert probe['streams'][0]['nb_frames']=='3001' and probe['streams'][0]['time_base']=='1/90000'
 frames=json.loads(run('probe-all-fix-pts',[PROBE,'-v','error','-threads','2','-select_streams','v:0','-show_frames','-show_entries','frame=best_effort_timestamp','-of','json',str(EXACT)]))['frames']
 pts=[int(f['best_effort_timestamp']) for f in frames];assert pts==list(range(0,3001*1500,1500))
 run('whole-exact-fix-decode',[FF,'-nostdin','-v','error','-threads','2','-i',str(EXACT),'-an','-f','null','-'])
 samples=[];offset=0
 for row in prep['scenes']:
  for pi,(a,b) in enumerate(zip(row['paragraphStarts'],row['paragraphStarts'][1:]+[row['durationSeconds']]),1):
   for phase in [.18,.5,.82]:
    f=min(offset+row['frames']-1,offset+round((a+(b-a)*phase)*60));samples.append({'scene':row['id'],'paragraph':pi,'phase':phase,'frame':f})
  offset+=row['frames']
 assert offset==3001 and len(samples)==24 and len({x['frame'] for x in samples})==24
 native=OUT/'motion-qa-native';boards=OUT/'motion-qa-boards';native.mkdir();boards.mkdir()
 expression='+'.join(f'eq(n,{s["frame"]})' for s in samples)
 run('extract24-fix-motion-samples',[FF,'-nostdin','-v','error','-threads','2','-i',str(EXACT),'-vf',f"select='{expression}'",'-fps_mode','vfr','-an','-threads','2',str(native/'frame-%03d.png')])
 from PIL import Image,ImageDraw,ImageFont
 font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',21);boardrows=[]
 for i,s in enumerate(samples,1):s.update(path=rel(native/f'frame-{i:03d}.png'),sha256=sha(native/f'frame-{i:03d}.png'))
 for bi,start in enumerate(range(0,24,4),1):
  board=Image.new('RGB',(1920,1170),'white');d=ImageDraw.Draw(board);group=samples[start:start+4]
  for j,s in enumerate(group):
   x=j%2*960;y=j//2*585;d.text((x+8,y+6),f'{s["scene"]} p{s["paragraph"]} phase{s["phase"]} frame{s["frame"]}',fill='black',font=font)
   im=Image.open(ROOT/s['path']).convert('RGB');im.thumbnail((960,540));board.paste(im,(x,y+45))
  path=boards/f'board-{bi:02d}.png';board.save(path);boardrows.append({'path':rel(path),'sha256':sha(path),'entries':group})
 state.update(status='two-white-fixes-exact24-samples-await-direct-review',exitCode=0,finishedAt=now(),
  currentWhite={'path':rel(EXACT),'sha256':sha(EXACT),'probe':probe,'frames':3001,'firstPts':0,'lastPts':4500000,'allPtsContiguous1500':True,'wholeDecodeExitCode':0},
  preservedOtherSixWhite=prep['originalSourcePreserved'],samplePlan=samples,boards=boardrows,allOriginalPcmPreserved=True)
 render=read(BASE/'white-fixes-render-execution-v2.json');render.update(status='actual-GUI-returned-encoder-absent',guiReturnedObserved=True,encoderAbsentObserved=True,encoderExitCodeObserved=False);save(BASE/'white-fixes-render-execution-v2.json',render)
 checkpoint();print(json.dumps({'fixFrames':3001,'decode':0,'pts':True,'samples':24,'boards':6,'fixPixelsApproved':False}),flush=True)
except BaseException:
 state.update(status='failed-white-fixes-verification',exitCode=1,error=traceback.format_exc(),finishedAt=now());checkpoint();raise
