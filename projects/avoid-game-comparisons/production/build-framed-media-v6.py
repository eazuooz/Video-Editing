"""Compile source-only reviewed candidate framing; keep native/old media unchanged."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,subprocess,os,time,traceback
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent;WORK=BASE/'measured-edit-v6';DEST=WORK/'framed-media-local'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
now=lambda:datetime.now(timezone.utc).isoformat()
def write(p,d):
 t=p.with_name(p.name+f'.{os.getpid()}.writing')
 for n in range(30):
  try:t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');os.replace(t,p);return
  except OSError:
   if n==29:raise
   time.sleep(.1)
assert not DEST.exists();DEST.mkdir()
plan=read(WORK/'plan.json');native=read(WORK/'native-review-v1/compiled.json');trials=read(BASE/'measured-edit-v5/framing-corrections-local/execution.json')
assert len(native['cuts'])==111
adopted=read(BASE/'targeted-framing-adoption-review.json')['adoptedCropFilters']
latest_filters={r['cut']:r['trialCrop'].rstrip(',') for r in trials['images']}
latest_filters['13-p1-action-88-4850-5035']=latest_filters.get('13-p1-action-88-4838-5028','crop=1600:900:160:180')
profiles=[]
for s in plan['scenes']:
 for c in s['segments']:
  if c['classification']!='actual-existing-game':continue
  crop=''
  if c['sourceVideoId']=='KWDk-csu460':crop='crop=1600:900:0:0' if c['bankCutId']=='action-98' else 'crop=1600:900:320:0'
  elif c['sourceVideoId']=='CJ0_Xh59b98':crop='crop=1600:900:160:0'
  elif c['sourceVideoId']=='h27ZF-hKKYM' and c['bankCutId'] in ['action-62','action-63','action-64','action-68','action-69','action-70','action-71']:crop='crop=1600:900:160:0'
  crop=adopted.get(c['id'],latest_filters.get(c['id'],crop))
  context='개발 과정의 실제 플레이' if c['sourceVideoId']=='KWDk-csu460' else c.get('requiredContextLabel')
  label=f"drawtext=fontfile='C\\:/Windows/Fonts/malgun.ttf':text='{context}':fontsize=26:fontcolor=black:box=1:boxcolor=white@0.94:boxborderw=12:x=38:y=36" if context else ''
  vf=','.join(x for x in [crop,'scale=1920:1080' if crop else '', 'setsar=1',label] if x)
  profiles.append(dict(id=c['id'],sceneId=s['id'],sourceVideoId=c['sourceVideoId'],sourceStartFrame=c['sourceStartFrame'],sourceEndFrameExclusive=c['sourceEndFrameExclusive'],startFrame=c['startFrame'],frames=c['frames'],cropFilter=crop,contextLabel=context,filter=vf,narrationCaptionCenter=[960,970],finalPixelsApproved=False))
write(WORK/'source-framing-profile.json',dict(createdAt=now(),planSha256=sha(WORK/'plan.json'),profiles=profiles,evidence=['projects/avoid-game-comparisons/production/all-actual-cue-trial-direct-review-v3.json','projects/avoid-game-comparisons/production/framing-corrections-direct-review-v5.json','projects/avoid-game-comparisons/production/targeted-framing-adoption-review.json'],newGitImages=0,allFinalPixelsApproved=False))
state=dict(startedAt=now(),pid=os.getpid(),sessionId=None,status='CPU-compiling-source-framing',threads=2,activeTasks=[],completed=[],processes=[],planSha256=sha(WORK/'plan.json'),profileSha256=sha(WORK/'source-framing-profile.json'),allFinalPixelsApproved=False,finalVideoComplete=False)
def checkpoint():
 session=DEST/'session.json'
 if session.exists():
  ss=read(session)
  if ss['pid']==os.getpid():state['sessionId']=ss['sessionId']
 write(DEST/'execution.json',state)
 qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qp);i=next(x for x in q['items'] if x['slug']=='avoid-game-comparisons')
 i.update(stage='current15-clean-source-framing-compilation-final-pixels-pending',updatedAt=now(),nextAction='Read every current framed cut/caption pixel and timed white diagram. The integer535s candidate and preserved edited voice are not a finished video.')
 i['execution'].update(observedAt=now(),phase=i['stage'],status=state['status'],pid=os.getpid(),sessionId=state['sessionId'],alive='endedAt' not in state,activeTasks=state['activeTasks'],cpuProductionJobs=0 if 'endedAt' in state else 1,gpuSynthesisJobs=0,renderJobs=0,uploads=0,state=rel(DEST/'execution.json'))
 q['updatedAt']=now();write(qp,q)
 for p in [BASE/'latest-checkpoint.json',ROOT/'production/batches/sakurai-planning-game-design/proof-avoid-game-comparisons/latest-checkpoint.json']:
  d=read(p)
  for k in ['stage','execution','updatedAt','nextAction']:d[k]=i[k]
  write(p,d)
def run(cmd,label):
 log=DEST/(label+'.log')
 with log.open('wb') as f:
  p=subprocess.Popen(cmd,stdout=f,stderr=f,creationflags=subprocess.CREATE_NO_WINDOW)
  state['activeTasks']=[dict(kind='CPU-source-framing',pid=p.pid,command=cmd,log=rel(log))];checkpoint();code=p.wait()
 state['activeTasks']=[];state['processes'].append(dict(label=label,pid=p.pid,exitCode=code,log=rel(log)));checkpoint()
 assert code==0;return log.read_text(encoding='utf-8')
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe';FP='C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe'
try:
 checkpoint()
 for profile in profiles:
  prior=next(c for c in native['cuts'] if c['id']==profile['id']);assert sha(ROOT/prior['video'])==prior['sha256']
  if not profile['cropFilter'] and not profile['contextLabel']:
   state['completed'].append({**profile,'video':prior['video'],'sha256':prior['sha256'],'reusedByteIdentical':True,'wholeDecodeExitCode':prior['wholeDecodeExitCode'],'audioStreams':0});checkpoint();continue
  video=DEST/(profile['id']+'.mp4')
  run([FF,'-v','error','-nostdin','-threads','2','-i',str(ROOT/prior['video']),'-map','0:v:0','-vf',profile['filter'],'-frames:v',str(profile['frames']),'-an','-c:v','libx264','-threads','2','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-r','60','-video_track_timescale','90000','-movflags','+faststart',str(video)],profile['id']+'-framing')
  info=json.loads(run([FP,'-v','error','-show_streams','-of','json',str(video)],profile['id']+'-probe'));v=next(x for x in info['streams'] if x['codec_type']=='video')
  assert int(v['nb_frames'])==profile['frames'] and v['avg_frame_rate']=='60/1' and v['width']==1920 and v['height']==1080 and len(info['streams'])==1
  assert not run([FF,'-v','error','-threads','2','-i',str(video),'-f','null','-'],profile['id']+'-decode').strip()
  state['completed'].append({**profile,'video':rel(video),'sha256':sha(video),'reusedByteIdentical':False,'nativeMediaSha256':prior['sha256'],'wholeDecodeExitCode':0,'audioStreams':0});checkpoint()
  print(f"Framed {len(state['completed'])}/111: {profile['id']}",flush=True)
 assert len(state['completed'])==111 and sum(c['frames'] for c in state['completed'])==18828
 write(WORK/'framed-media-index.json',dict(createdAt=now(),planSha256=state['planSha256'],profileSha256=state['profileSha256'],cuts=state['completed'],allFinalPixelsApproved=False,sourceAudioStreams=0,finalVideoComplete=False))
 state.update(status='closed111-framed-cuts-awaiting-current-final-pixel-review',endedAt=now(),exitCode=0);checkpoint()
except BaseException:
 state.update(status='closed-source-framing-failed',endedAt=now(),exitCode=1,error=traceback.format_exc(),activeTasks=[]);checkpoint();raise
