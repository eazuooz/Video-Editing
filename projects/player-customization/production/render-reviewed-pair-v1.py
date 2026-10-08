"""Single CPU2/GPU0 final pair, gated by direct review of the current32 windows."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, ctypes, hashlib, json, os, subprocess, sys, time, traceback
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent;W=BASE/'final-v1'
STATE=W/'review-pair-execution.json';SESSION=W/'review-pair-session.json'
FF=Path('C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe');FP=FF.with_name('ffprobe.exe')
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
plan=read(W/'plan.json');mix=read(W/'mix-settings.json');review=read(W/'full-mix-asr-review.json')
assert review['technicallyApproved'] and review['all32WindowsDirectlyCompared'] and not review['unresolvedContentDefects']
assert review['currentMixedAudioSha256']==mix['wavSha256'] and review['planSha256']==mix['planSha256']==sha(W/'plan.json')
assert len(review['windows'])==32 and all(x['directlyCompared'] for x in review['windows'])
for x in review['windows']:assert sha(ROOT/x['path'])==x['sha256']
assert read(W/'mixed-asr-execution.json')['exitCode']==0
assert sha(W/'final-mix.wav')==mix['wavSha256'] and sha(W/'final-mix.m4a')==mix['aacSha256']
assert plan['allInputSegmentCaptionPixelsReviewed'] and plan['finalTimingApproved'] and plan['bodyRatioApproved']
assert sha(ROOT/plan['selectedInputReview'])==plan['selectedInputReviewSha256']
captionClock=read(W/'caption-clock-adoption.json');assert captionClock['finalAssSha256']==sha(W/'captions.ko.ass')
assert captionClock['koCueCount']==415 and captionClock['enCueCount']==162 and captionClock['captionCenter']==[960,970]
assert plan['finalFrames']==36041 and plan['bodyFrames']==35321 and plan['body60_40ErrorFrames']<=1
assert sha(ROOT/plan['bodySilentVideo'])==plan['bodySilentSha256']
for x in [plan['intro'],plan['membership']]:assert sha(ROOT/x['path'])==x['sha256']
assert not STATE.exists(),'Read actual rendering checkpoint; never repeat completed outputs.'
visual=W/'current.silent.mp4';clean=W/'player-customization.clean.review.mp4';captioned=W/'player-customization.captioned.review.mp4'
assert not any(p.exists() for p in [visual,clean,captioned])
if os.name=='nt':ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x00004000)
s=dict(schemaVersion=1,slug='player-customization',pid=os.getpid(),sessionId=None,commandLine=[sys.executable,*sys.argv],startedAt=now(),
 status='assembling-current-final-visual',resourceEvidence=a.resource,cpuThreads=2,gpu=0,singleJob=True,commands=[],activeTask=None,exitCode=None,
 planSha256=sha(W/'plan.json'),currentMixedAudioSha256=mix['wavSha256'],mixedAsrDirectReview=rel(W/'full-mix-asr-review.json'),
 finalMixedAsrApproved=True,rendered=False,allFinalPixels=False,qaApproved=False,collected=False,uploaded=False,newTts=0,sourceAudioStreams=0)
def checkpoint():
 if SESSION.exists():
  x=read(SESSION)
  if x['pid']==os.getpid():s.update(sessionId=x['sessionId'],processIdentity=x['processIdentity'])
 s['observedAt']=now();save(STATE,s)
 job=dict(pid=s['pid'],sessionId=s['sessionId'],processIdentity=s.get('processIdentity'),commandLine=s['commandLine'],state=rel(STATE),status=s['status'],
  cpuThreads=2,gpu=0,singleJob=True,activeTask=s['activeTask'],exitCode=s['exitCode'],workerExpectedRunning=s['exitCode'] is None)
 cpPath=BASE/'latest-checkpoint.json';cp=read(cpPath);cp.update(stage=s['status'],ownedJob=job,recordedAt=now(),renderPairExecution=rel(STATE),
  finalMixedAsrApproved=True,rendered=s['rendered'],allFinalPixels=False,qaApproved=False,collected=False,uploaded=False,
  nextAction='After both pair decodes/PTS/AAC pass, extract every current encoded cue/cut/paragraph sample and directly inspect all boards. Then QA/4file collection/single private settings/Git.');save(cpPath,cp)
 qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qp);i=next(x for x in q['items'] if x['slug']=='player-customization')
 i.update(stage=s['status'],currentExecution=job,renderPairExecution=rel(STATE),finalMixedAsrApproved=True,rendered=s['rendered'],
  allFinalPixels=False,qaApproved=False,collected=False,uploaded=False,nextAction=cp['nextAction']);q['updatedAt']=now();save(qp,q)
def run(exe,args,kind):
 log=W/f'review-pair-{len(s["commands"])+1:02d}.log';cmd=[str(exe),*map(str,args)];op=dict(kind=kind,commandLine=cmd,log=rel(log),startedAt=now());s['commands'].append(op)
 with log.open('w',encoding='utf-8') as f:
  p=subprocess.Popen(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW);op['pid']=p.pid;s.update(status=kind,activeTask=op);checkpoint();code=p.wait()
 op.update(exitCode=code,endedAt=now());s['activeTask']=None;checkpoint();assert code==0,f'{kind} exit{code}: preserve {log}'
 return log.read_text('utf-8-sig')
def ff(args,kind):return run(FF,['-v','error','-nostdin','-threads','2','-filter_threads','1','-filter_complex_threads','1',*args],kind)
def probe_clock(p,N,audio):
 data=json.loads(run(FP,['-v','error','-threads','2','-count_frames','-show_streams','-show_format','-of','json',p],'CPU2-probe-current-final-streams'))
 v=next(x for x in data['streams'] if x['codec_type']=='video')
 assert len(data['streams'])==(2 if audio else 1)
 assert int(v['nb_read_frames'])==N and v['width']==1920 and v['height']==1080 and v['avg_frame_rate']=='60/1'
 assert v['time_base']=='1/90000' and int(v['duration_ts'])==N*1500
 assert abs(float(data['format']['duration'])-N/60)<=.022
 packets=json.loads(run(FP,['-v','error','-select_streams','v:0','-show_packets','-show_entries','packet=pts,duration','-of','json',p],'CPU2-exact-final-packet-PTS'))['packets']
 assert len(packets)==N and sorted(int(x['pts']) for x in packets)==list(range(0,N*1500,1500))
 assert all(int(x['duration'])==1500 for x in packets)
 assert not ff(['-i',p,'-f','null','-'],'CPU2-whole-current-final-decode').strip()
 return dict(probe=data,wholeDecodeExitCode=0,exactPresentationClock=dict(timeBase='1/90000',count=N,firstPts=0,lastPts=(N-1)*1500,step=1500,allPacketPtsExact=True))
try:
 checkpoint();N=plan['finalFrames']
 sequence=[dict(path=plan['intro']['path'],frames=120),dict(path=plan['bodySilentVideo'],frames=35321),dict(path=plan['membership']['path'],frames=600)]
 concat=W/'current-final-concat.txt';concat.write_text('ffconcat version 1.0\n'+''.join("file '"+(ROOT/x['path']).as_posix()+"'\nduration "+f"{x['frames']/60:.12f}"+'\n' for x in sequence),'utf-8')
 ff(['-f','concat','-safe','0','-i',concat,'-an','-c:v','copy','-video_track_timescale','90000','-movflags','+faststart',visual],'CPU2-copy-original-branding-reviewed-body-membership')
 visualCheck=probe_clock(visual,N,False)
 visualBuild=dict(createdAt=now(),video=rel(visual),sha256=sha(visual),planSha256=sha(W/'plan.json'),frames=N,seconds=N/60,**visualCheck,
  originalBrandingReused=True,originalMembershipReused=True,sourceAudioStreams=0,allFinalPixels=False)
 save(W/'visual-build.json',visualBuild)
 ff(['-i',visual,'-i',W/'final-mix.m4a','-map','0:v:0','-map','1:a:0','-c','copy','-video_track_timescale','90000','-movflags','+faststart',clean],'CPU2-clean-current-visual-AAC-copy')
 ff(['-i',clean,'-map','0:v:0','-map','0:a:0','-vf','ass=projects/player-customization/production/final-v1/captions.ko.ass',
  '-c:v','libx264','-preset','veryfast','-crf','18','-threads','2','-pix_fmt','yuv420p','-fps_mode','passthrough','-frames:v',str(N),
  '-video_track_timescale','90000','-c:a','copy','-movflags','+faststart',captioned],'CPU2-current-fixed-Korean-caption-encode')
 records=[]
 for p in [clean,captioned]:
  checks=probe_clock(p,N,True)
  ah=ff(['-i',p,'-map','0:a:0','-c:a','copy','-f','hash','-hash','sha256','-'],'CPU2-current-AAC-payload-hash').strip();assert ah.startswith('SHA256=')
  records.append(dict(path=rel(p),sha256=sha(p),**checks,aacPayloadHash=ah))
 sourceHash=ff(['-i',W/'final-mix.m4a','-map','0:a:0','-c:a','copy','-f','hash','-hash','sha256','-'],'CPU2-source-AAC-payload-hash').strip()
 assert all(x['aacPayloadHash']==sourceHash for x in records)
 save(W/'review-pair-build.json',dict(createdAt=now(),planSha256=sha(W/'plan.json'),captionAssSha256=sha(W/'captions.ko.ass'),sourceMixAacSha256=mix['aacSha256'],
  records=records,frames=N,seconds=N/60,identicalAacPayload=True,inheritedSameAacLufs=float(mix['finalAacMeasurement']['input_i']),
  inheritedSameAacTruePeakDbtp=float(mix['finalAacMeasurement']['input_tp']),allFinalFixedCaptionPixelsReviewed=False,qaApproved=False,completedVideo=False))
 s.update(status='closed-current-review-pair-awaiting-all-final-pixels',rendered=True,exitCode=0,endedAt=now(),activeTask=None);checkpoint()
 print(json.dumps(dict(exitCode=0,frames=N,bothWholeDecodeExitCode=0,identicalAacPayload=True,allFinalPixels=False)),flush=True)
except BaseException:
 s.update(status='closed-current-review-pair-failed',exitCode=1,endedAt=now(),activeTask=None,error=traceback.format_exc());checkpoint();raise
