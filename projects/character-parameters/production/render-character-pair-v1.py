"""Single CPU2 final pair; refuse before state until all49 mixed windows read."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,ctypes,hashlib,json,os,subprocess,time,traceback
import psutil
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent;W=BASE/'final-v1'
STATE=W/'review-pair-execution.json';SESSION=W/'review-pair-session.json'
FF=Path('C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe');FP=FF.with_name('ffprobe.exe')
read=lambda p:json.loads(p.read_text('utf-8-sig'));now=lambda:datetime.now(timezone.utc).isoformat();rel=lambda p:p.relative_to(ROOT).as_posix()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def save(p,j):
 t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
 for n in range(40):
  try:os.replace(t,p);return
  except OSError:
   if n==39:raise
   time.sleep(.15)
ap=argparse.ArgumentParser();ap.add_argument('--resource');ap.add_argument('--check-gates',action='store_true');a=ap.parse_args()
review_path=W/'full-mix-asr-review.json'
if a.check_gates:
 ready=review_path.exists() and read(review_path).get('technicallyApproved',False)
 print(json.dumps(dict(ready=ready,required='All49 current mixed windows directly compared and current mix/plan hashes sealed',stateCreated=STATE.exists())))
 raise SystemExit(0)
assert review_path.exists(),'Current49-window direct mixed review required before any state/render.'
review=read(review_path);plan=read(W/'plan.json');mix=read(W/'mix-settings.json')
assert review['technicallyApproved'] and review['all49WindowsDirectlyCompared'] and not review['unresolvedContentDefects']
assert review['currentMixedAudioSha256']==mix['wavSha256'] and review['currentAacSha256']==mix['aacSha256']
assert review['planSha256']==mix['planSha256']==sha(W/'plan.json')
assert len(review['windows'])==49 and all(x['directlyCompared'] for x in review['windows'])
for x in review['windows']:assert sha(ROOT/x['path'])==x['sha256']
asr=read(W/'mixed-asr-execution.json');assert asr['exitCode']==asr['outerExitCode']==0 and asr['outerExitDirectlyObserved']
assert sha(W/'final-mix.wav')==mix['wavSha256'] and sha(W/'final-mix.m4a')==mix['aacSha256']
assert plan['allInputSegmentCaptionPixelsReviewed'] and plan['finalTimingApproved'] and plan['bodyRatioApproved']
assert sha(ROOT/plan['selectedInputReview'])==plan['selectedInputReviewSha256']
clock=read(W/'caption-clock-adoption.json');assert clock['finalAssSha256']==sha(W/'captions.ko.ass')
assert clock['captionJsonSha256']==sha(W/'captions.json') and (clock['koCueCount'],clock['enCueCount'],clock['captionCenter'])==(201,95,[960,970])
visual=W/'silent-visual.mp4';v=read(W/'visual-build.json');assert sha(visual)==v['sha256'] and v['wholeDecodeExitCode']==0 and v['allPtsVerified']
assert (plan['finalFrames'],plan['bodyFrames'])==(23397,22677) and plan['body60_40ErrorFrames']<=1
assert a.resource;r=read(ROOT/a.resource)
assert r['ownHeavyJobs']==0 and r['cpuLoadPercent']<85 and r['freePhysicalMemoryKiB']>8000000
assert (datetime.now(timezone.utc)-datetime.fromisoformat(r['observedAt'])).total_seconds()<240
subprocess.run(['C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe','scripts/review-video-duplicates.cjs','character-parameters','--check'],cwd=ROOT,check=True)
clean=W/'character-parameters.clean.mp4';captioned=W/'character-parameters.captioned.mp4'
assert not STATE.exists() and not clean.exists() and not captioned.exists(),'Read actual rendering checkpoint; never repeat.'
if os.name=='nt':ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x00004000)
p=psutil.Process();s=dict(schemaVersion=1,slug='character-parameters',pid=p.pid,createTime=p.create_time(),command=p.cmdline(),cwd=p.cwd(),
 sessionId=None,startedAt=now(),status='current-final-review-pair-running',resourceEvidence=a.resource,cpuThreads=2,gpu=0,
 singleJob=True,operations=[],activeTask=None,exitCode=None,planSha256=sha(W/'plan.json'),currentMixedAudioSha256=mix['wavSha256'],
 mixedAsrDirectReview=rel(review_path),mixedAsrDirectReviewSha256=sha(review_path),finalMixedAsrApproved=True,
 rendered=False,allFinalPixels=False,qaApproved=False,collected=False,uploaded=False,newTts=0,sourceAudioStreams=0)
def checkpoint():
 if SESSION.exists():
  x=read(SESSION)
  if x['pid']==s['pid'] and abs(x['createTime']-s['createTime'])<.01:s['sessionId']=x['sessionId']
 s['observedAt']=now();save(STATE,s)
 job=dict(pid=s['pid'],createTime=s['createTime'],command=s['command'],cwd=s['cwd'],sessionId=s['sessionId'],state=rel(STATE),status=s['status'],
  cpuThreads=2,gpu=0,singleJob=True,activeTask=s['activeTask'],exitCode=s['exitCode'],workerExpectedRunning=s['exitCode'] is None)
 cp=read(BASE/'latest-checkpoint.json');cp.update(stage=s['status'],ownedJob=job,recordedAt=now(),renderPairExecution=rel(STATE),
  finalMixedAsrApproved=True,pairRendered=s['rendered'],allFinalPixels=False,qa=False,collected=False,private=False,
  nextAction='After both exact PTS/decode/AAC checks, extract all encoded cue/cut/clause/PCM/spatial/member samples and directly read every board. Then QA/4files/private/Git.');save(BASE/'latest-checkpoint.json',cp)
 qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json'
 for _ in range(8):
  raw=qp.read_text('utf-8-sig');q=json.loads(raw);i=next(x for x in q['items']if x['slug']=='character-parameters')
  i.update(stage=s['status'],currentExecution=job,currentJob=job,ownedJob=job,renderPairExecution=rel(STATE),finalMixedAsrApproved=True,
   pairRendered=s['rendered'],allFinalPixels=False,qa=False,collected=False,uploaded=False,nextAction=cp['nextAction']);q['updatedAt']=now()
  if qp.read_text('utf-8-sig')==raw:save(qp,q);break
 else:raise RuntimeError('Concurrent queue preserved')
def run(exe,args,kind):
 log=W/f'review-pair-{len(s["operations"])+1:02d}-{kind}.log';cmd=[str(exe),*map(str,args)];op=dict(kind=kind,command=cmd,log=rel(log),startedAt=now());s['operations'].append(op)
 with log.open('w',encoding='utf-8')as f:
  child=subprocess.Popen(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
  op.update(pid=child.pid,createTime=psutil.Process(child.pid).create_time());s['activeTask']=op;checkpoint();code=child.wait()
 op.update(exitCode=code,endedAt=now());s['activeTask']=None;checkpoint();assert code==0,f'{kind} exit{code}; preserve {log}'
 return log.read_text('utf-8-sig')
def ff(args,kind):return run(FF,['-v','error','-nostdin','-threads','2','-filter_threads','1','-filter_complex_threads','1',*args],kind)
def check(path,N):
 data=json.loads(run(FP,['-v','error','-count_frames','-show_streams','-show_format','-of','json',path],'probe'))
 assert len(data['streams'])==2;v=next(x for x in data['streams']if x['codec_type']=='video')
 assert (v['width'],v['height'],v['avg_frame_rate'],v['time_base'],int(v['nb_read_frames']),int(v['duration_ts']))==(1920,1080,'60/1','1/90000',N,N*1500)
 assert abs(float(data['format']['duration'])-N/60)<=.022
 packets=json.loads(run(FP,['-v','error','-select_streams','v:0','-show_packets','-show_entries','packet=pts,duration','-of','json',path],'all-packet-PTS'))['packets']
 assert len(packets)==N and sorted(int(x['pts'])for x in packets)==list(range(0,N*1500,1500))
 assert all(int(x['duration'])==1500 for x in packets)
 assert not ff(['-i',path,'-f','null','-'],'whole-pair-decode').strip()
 return dict(probe=data,wholeDecodeExitCode=0,timebase='1/90000',allPacketPtsExact=True,ptsStep=1500,frames=N)
try:
 checkpoint();N=23397
 ff(['-i',visual,'-i',W/'final-mix.m4a','-map','0:v:0','-map','1:a:0','-c','copy','-map_metadata','-1','-video_track_timescale','90000','-movflags','+faststart',clean],'copy-current-clean-AAC')
 ff(['-reinit_filter','0','-i',clean,'-map','0:v:0','-map','0:a:0','-vf','ass=projects/character-parameters/production/final-v1/captions.ko.ass',
  '-c:v','libx264','-preset','veryfast','-crf','18','-threads','2','-pix_fmt','yuv420p','-fps_mode','passthrough','-frames:v',N,
  '-video_track_timescale','90000','-c:a','copy','-movflags','+faststart',captioned],'encode-current-fixed-Korean-captions')
 records=[]
 for path in [clean,captioned]:
  checks=check(path,N);payload=ff(['-i',path,'-map','0:a:0','-c:a','copy','-f','hash','-hash','sha256','-'],'AAC-payload-hash').strip();assert payload.startswith('SHA256=')
  records.append(dict(path=rel(path),sha256=sha(path),aacPayloadHash=payload,**checks))
 source_hash=ff(['-i',W/'final-mix.m4a','-map','0:a:0','-c:a','copy','-f','hash','-hash','sha256','-'],'source-AAC-payload-hash').strip()
 assert all(x['aacPayloadHash']==source_hash for x in records)
 save(W/'review-pair-build.json',dict(createdAt=now(),planSha256=sha(W/'plan.json'),captionAssSha256=sha(W/'captions.ko.ass'),
  sourceMixAacSha256=mix['aacSha256'],records=records,frames=N,seconds=N/60,identicalAacPayload=True,
  inheritedSameAacLufs=float(mix['finalAacMeasurement']['input_i']),inheritedSameAacTruePeakDbtp=float(mix['finalAacMeasurement']['input_tp']),
  allFinalFixedCaptionPixelsReviewed=False,qaApproved=False,completedVideo=False))
 s.update(status='closed-current-review-pair-awaiting-all-final-pixels',rendered=True,exitCode=0,endedAt=now(),activeTask=None);checkpoint()
 print(json.dumps(dict(exitCode=0,frames=N,bothWholeDecodeExitCode=0,identicalAacPayload=True,allFinalPixels=False)),flush=True)
except BaseException:
 s.update(status='closed-current-review-pair-failed',exitCode=1,endedAt=now(),activeTask=None,error=traceback.format_exc());checkpoint();raise
