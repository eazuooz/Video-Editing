"""Build local review inputs sequentially; source/pixel/final approvals stay false."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os,subprocess,psutil
ROOT=Path(__file__).resolve().parents[3]
PROD=ROOT/'projects/game-lighting-history-03/production'
OUT=ROOT/'production/research/game-lighting-history/local/native-framing-v16'
FFMPEG=Path('C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe')
FFPROBE=FFMPEG.with_name('ffprobe.exe')
def stamp():return datetime.now(timezone.utc).isoformat()
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def save(p,x):
 p.parent.mkdir(parents=True,exist_ok=True);t=p.with_name(p.name+'.writing-'+str(os.getpid()));t.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
def owned_media():
 jobs=[]
 for p in psutil.process_iter(['pid','name','cmdline','create_time']):
  if p.info['name'].lower()!='ffmpeg.exe':continue
  cmd=' '.join(p.info['cmdline']or[])
  if 'game-lighting-history' in cmd:jobs.append(p.info)
 return jobs
def run(cmd,label,state):
 log=OUT/(label+'.log')
 with log.open('wb')as f:
  p=subprocess.Popen([str(x)for x in cmd],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
  state['active']=dict(pid=p.pid,createTime=psutil.Process(p.pid).create_time(),commandLine=[str(x)for x in cmd],cwd=str(ROOT),log=log.relative_to(ROOT).as_posix(),startedAt=stamp(),cpuThreads=2,gpuJobs=0)
  save(PROD/'native-framing-execution-v16.json',state)
  code=p.wait()
 state['lastCommand']=dict(state['active'],exitCode=code,completedAt=stamp());state['active']=None;save(PROD/'native-framing-execution-v16.json',state)
 if code:raise RuntimeError(f'{label} exit{code}; partial output preserved, inspect {log}')
 return dict(command=[str(x)for x in cmd],exitCode=0,log=log.relative_to(ROOT).as_posix())
args=argparse.ArgumentParser();args.add_argument('--plan-only',action='store_true');a=args.parse_args()
ap=PROD/'native-range-allocation-candidate-v16.json';tp=PROD/'measured-native-timeline-candidate-v15.json'
allocation=read(ap);timeline=read(tp)
assert sha(tp)==allocation['timeline']['sha256']
assert allocation['sourceOverlapCount']==0 and allocation['rateChanges']==0 and allocation['loops']==0
slots={s['id']:s for s in timeline['slots']};cuts=[]
for alloc in allocation['allocations']:
 s=slots[alloc['id']];assert s['role']=='actual' and s['frames']==alloc['frames'];f=s['fromFrame']
 for i,r in enumerate(alloc['ranges']):
  assert r['rate']==1 and not r['sourceAudio'];name=alloc['id']+'-'+str(i+1).zfill(2)
  cuts.append(dict(id=name,slotId=alloc['id'],scene=s['scene'],fromFrame=f,toFrame=f+r['frames'],frames=r['frames'],source=r['source'],media=r['media'],sourceSha256=r['sourceSha256'],sourceFromSeconds=r['fromSeconds'],sourceToSeconds=r['toSeconds'],crop=r['crop'],output=(OUT/(name+'.mp4')).relative_to(ROOT).as_posix(),rate=1,sourceAudio=False,sourceMotionApproved=False,finalCaptionPixelsApproved=False));f+=r['frames']
 assert f==s['toFrame']
assert len(cuts)==allocation['nativeCuts'] and sum(c['frames']for c in cuts)==allocation['actualFrames']
plan=dict(preparedAt=stamp(),allocation=dict(path=ap.relative_to(ROOT).as_posix(),sha256=sha(ap)),timeline=dict(path=tp.relative_to(ROOT).as_posix(),sha256=sha(tp)),cuts=cuts,cpuThreads=2,gpuJobs=0,outputResolution=[1920,1080],outputFps=60,outputTimebase=90000,frameRateConversion='Native cadence to60fps at rate1; no speed change or quota loop.',sourceStartOffsetsVerified=False,sourceMotionApproved=False,allFinalPixelsReviewed=False,rightsApproved=False,collected=False,uploaded=False)
pp=PROD/'native-framing-plan-v16.json'
if pp.exists():
 old=read(pp);assert old['allocation']==plan['allocation'] and old['timeline']==plan['timeline'] and old['cuts']==plan['cuts']
else:save(pp,plan)
if a.plan_only:
 print(json.dumps(dict(cuts=len(cuts),frames=allocation['actualFrames'],planOnly=True,mediaCreated=0,imagesCreated=0)));raise SystemExit(0)
assert not owned_media(),'Owned media job is active; do not start another.'
resources=subprocess.run(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader'],capture_output=True,text=True,check=True)
for source in allocation['sources'].values():assert sha(ROOT/source['media'])==source['sha256'],'Source changed'
sp=PROD/'native-framing-execution-v16.json'
state=read(sp)if sp.exists()else dict(startedAt=stamp(),results=[],active=None,cpuThreads=2,gpuJobs=0,allFinalPixelsReviewed=False,finalUseApproved=False)
if state.get('active'):
 p=state['active'];assert not psutil.pid_exists(p['pid'])or abs(psutil.Process(p['pid']).create_time()-p['createTime'])>1,'Recorded worker still alive'
state.update(status='running',resourceObservation=dict(observedAt=stamp(),nvidiaSmi=resources.stdout.strip()),worker=dict(pid=os.getpid(),createTime=psutil.Process().create_time(),commandLine=psutil.Process().cmdline(),cwd=str(ROOT)))
OUT.mkdir(parents=True,exist_ok=True);save(sp,state)
try:
 for c in cuts:
  rp=OUT/(c['id']+'.verification.json');output=ROOT/c['output']
  if rp.exists():
   r=read(rp);assert r['outputSha256']==sha(output) and r['observedFrames']==c['frames'] and r['wholeDecode']['exitCode']==0;continue
  assert not output.exists(),'Unverified output preserved; inspect before any retry.'
  assert not owned_media(),'Another owned media job started'
  filters=[]
  if c['crop']:
   x,y,w,h=c['crop'];filters.append(f'crop={w}:{h}:{x}:{y}')
  filters+=['fps=60','scale=1920:1080:flags=lanczos','setsar=1','setpts=N/(60*TB)']
  cmd=[FFMPEG,'-n','-v','error','-threads','2','-ss',f"{c['sourceFromSeconds']:.9f}",'-i',ROOT/c['media'],'-an','-vf',','.join(filters),'-frames:v',str(c['frames']),'-c:v','libx264','-threads','2','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-video_track_timescale','90000','-movflags','+faststart',output]
  encode=run(cmd,c['id']+'-encode',state)
  probeCmd=[str(FFPROBE),'-v','error','-count_frames','-show_entries','stream=codec_type,width,height,r_frame_rate,time_base,nb_read_frames,duration','-of','json',str(output)]
  p=subprocess.run(probeCmd,capture_output=True,text=True,check=True);probe=json.loads(p.stdout);v=probe['streams'][0]
  assert len(probe['streams'])==1 and v['codec_type']=='video'and v['width']==1920 and v['height']==1080 and v['r_frame_rate']=='60/1'and v['time_base']=='1/90000'and int(v['nb_read_frames'])==c['frames']
  packetCmd=[str(FFPROBE),'-v','error','-select_streams','v:0','-show_entries','packet=pts','-of','json',str(output)]
  p=subprocess.run(packetCmd,capture_output=True,text=True,check=True);pts=sorted(x['pts']for x in json.loads(p.stdout)['packets']);assert pts==list(range(0,c['frames']*1500,1500))
  decode=run([FFMPEG,'-v','error','-threads','2','-i',output,'-f','null','NUL'],c['id']+'-decode',state)
  record=dict(verifiedAt=stamp(),cut=c,outputSha256=sha(output),encode=encode,probe=probe,probeCommand=probeCmd,packetCommand=packetCmd,observedFrames=len(pts),allPresentationPtsContinuous=True,wholeDecode=decode,allPixelsReviewed=False,sourceMotionApproved=False,finalUseApproved=False,localOnly=True)
  save(rp,record);state['results'].append(dict(id=c['id'],frames=c['frames'],verification=rp.relative_to(ROOT).as_posix(),sha256=record['outputSha256']));save(sp,state)
  print(json.dumps(dict(done=len(state['results']),total=len(cuts),id=c['id'],frames=c['frames'],decode=0)),flush=True)
 state.update(status='complete',completedAt=stamp(),exitCode=0,allFinalPixelsReviewed=False,finalUseApproved=False);save(sp,state)
except Exception as e:
 state.update(status='failed',failedAt=stamp(),error=str(e),exitCode=1);save(sp,state);raise
