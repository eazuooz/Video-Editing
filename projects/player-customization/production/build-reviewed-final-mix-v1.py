"""Prepared CPU2 mixer. Refuse before state creation until current input review.

No new TTS, native render or source audio. Human listening remains pending.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse, ctypes, hashlib, json, os, re, subprocess, sys, time, traceback
import numpy as np
import soundfile as sf

ROOT=Path(__file__).resolve().parents[3]; BASE=Path(__file__).resolve().parent
FINAL=BASE/'final-v1'; STATE=FINAL/'mix-execution.json'; SESSION=FINAL/'mix-session.json'
FF=Path('C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'); FP=FF.with_name('ffprobe.exe')
read=lambda p:json.loads(p.read_text('utf-8-sig')); now=lambda:datetime.now(timezone.utc).isoformat()
rel=lambda p:p.relative_to(ROOT).as_posix()
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
ap=argparse.ArgumentParser(); ap.add_argument('--resource',required=True); a=ap.parse_args()
r=read(ROOT/a.resource)
assert r['ownHeavyJobs']==0 and r['cpuLoadPercent']<85 and r['freePhysicalMemoryKiB']>8000000
assert (datetime.now(timezone.utc)-datetime.fromisoformat(r['observedAt'].replace('Z','+00:00'))).total_seconds()<240
planPath=FINAL/'plan.json'; plan=read(planPath); reviewPath=ROOT/plan['selectedInputReview']
assert sha(reviewPath)==plan['selectedInputReviewSha256']; review=read(reviewPath)
assert review['allBoardsDirectlyRead'] and review['sourceAllocationApproved'] and not review['unresolvedDefects']
assert plan['finalTimingApproved'] and plan['bodyRatioApproved'] and plan['allInputSegmentCaptionPixelsReviewed']
assert plan['finalFrames']==36041 and plan['bodyFrames']==35321 and plan['body60_40ErrorFrames']<=1
timingPath=ROOT/plan['voiceTiming']; assert sha(timingPath)==plan['voiceTimingSha256']; timing=read(timingPath)
assert timing['wholePcmSamples']==14125441
for row in timing['rows']:assert sha(ROOT/row['audioPath'])==row['audioSha256']
manifest=read(BASE.parent/'project.json'); musicApproval=manifest['audio']['backgroundMusic']
music=ROOT/musicApproval['file']; assert musicApproval['approvalStatus']=='approved'
assert sha(music)==musicApproval['restoration']['sha256']
assert not STATE.exists(),'Read the actual mix checkpoint; never repeat completed work.'
if os.name=='nt':ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x00004000)
s=dict(schemaVersion=1,slug='player-customization',pid=os.getpid(),sessionId=None,commandLine=[sys.executable,*sys.argv],
 startedAt=now(),status='preserving-current16-PCM-timeline',resourceEvidence=a.resource,cpuThreads=2,gpu=0,singleJob=True,
 planPath=rel(planPath),planSha256=sha(planPath),commands=[],exitCode=None,sourceAudioStreams=0,newTts=0,
 finalMixedAsrApproved=False,humanWholeListening='pending',humanPronunciation='pending',allFinalPixels=False,collected=False,uploaded=False)
def checkpoint():
 if SESSION.exists():
  x=read(SESSION)
  if x['pid']==os.getpid():s.update(sessionId=x['sessionId'],processIdentity=x['processIdentity'])
 s['observedAt']=now();save(STATE,s)
 job=dict(status=s['status'],pid=os.getpid(),sessionId=s['sessionId'],processIdentity=s.get('processIdentity'),commandLine=s['commandLine'],
  state=rel(STATE),cpuThreads=2,gpu=0,singleJob=True,activeTask=s.get('activeTask'),exitCode=s['exitCode'],workerExpectedRunning=s['exitCode'] is None)
 cp=read(BASE/'latest-checkpoint.json');cp.update(stage=s['status'],ownedJob=job,recordedAt=now(),finalMixExecution=rel(STATE),
  nextAction='Compare current final mixed16whole chapters and independent complete contexts against full expected and actual text. Then guarded review pair/final pixels/QA/collection/private/Git.');save(BASE/'latest-checkpoint.json',cp)
 qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qp);i=next(x for x in q['items'] if x['slug']=='player-customization')
 i.update(stage=cp['stage'],currentExecution=job,finalMixExecution=rel(STATE),nextAction=cp['nextAction']);q['updatedAt']=now();save(qp,q)
def run(exe,args,kind):
 log=FINAL/f'mix-{len(s["commands"])+1:02d}.log';cmd=[str(exe),*map(str,args)]
 op=dict(kind=kind,commandLine=cmd,log=rel(log),startedAt=now());s['commands'].append(op)
 with log.open('w',encoding='utf-8') as f:
  p=subprocess.Popen(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
  op['pid']=p.pid;s.update(status=kind,activeTask=op);checkpoint();code=p.wait()
 op.update(exitCode=code,endedAt=now());s['activeTask']=None;checkpoint()
 assert code==0,f'{kind} exit{code}: preserve {log}'
 return log.read_text('utf-8-sig')
def ff(args,kind):return run(FF,['-hide_banner','-nostdin','-threads','2','-filter_threads','1','-filter_complex_threads','1',*args],kind)
def scan(path,I=-16,TP=-2):
 out=ff(['-i',path,'-af',f'loudnorm=I={I}:TP={TP}:LRA=11:print_format=json','-f','null','-'],'CPU2-loudness-scan')
 return json.loads(re.search(r'\{\s*"input_i"[\s\S]*?\}',out).group())
try:
 checkpoint(); N=plan['finalFrames']; D=N/60; timeline=np.zeros(N*400,dtype='int16');placements=[]
 for row in timing['rows']:
  p=ROOT/row['audioPath'];x,rate=sf.read(p,dtype='int16');assert rate==24000 and x.ndim==1 and len(x)==row['samples']
  start=row['startFrame']*400;assert len(x)<=row['frames']*400
  timeline[start:start+len(x)]=x
  assert np.array_equal(timeline[start:start+len(x)],x)
  placements.append(dict(scene=row['id'],startFrame=row['startFrame'],frames=row['frames'],samples=len(x),
   source=rel(p),sha256=row['audioSha256'],allOriginalSamplesIdentical=True,tailPaddingSamples=row['frames']*400-len(x)))
 assert sum(p['samples'] for p in placements)==14125441
 assert np.count_nonzero(timeline[:48000])==0 and np.count_nonzero(timeline[-240000:])==0
 voice=FINAL/'narration-timed.wav';sf.write(voice,timeline,24000,subtype='PCM_16')
 back,rate=sf.read(voice,dtype='int16');assert rate==24000 and np.array_equal(back,timeline)
 save(FINAL/'pcm-timeline-preservation.json',dict(createdAt=now(),planSha256=sha(planPath),voice=rel(voice),sha256=sha(voice),
  totalSamples=N*400,originalSamples=14125441,all16CurrentPcmSamplesIdentical=True,placements=placements,newTts=0))
 raw=scan(voice);normalPass=FINAL/'voice-normalized-pass.wav'
 lf=f"loudnorm=I=-16:TP=-2:LRA=11:measured_I={raw['input_i']}:measured_TP={raw['input_tp']}:measured_LRA={raw['input_lra']}:measured_thresh={raw['input_thresh']}:offset={raw['target_offset']}:linear=true,aresample=48000,aformat=channel_layouts=stereo"
 ff(['-i',voice,'-af',lf,'-c:a','pcm_s16le',normalPass],'CPU2-two-pass-current-voice-normalization')
 x,rate=sf.read(normalPass,dtype='int16',always_2d=True);assert rate==48000 and len(x)==N*800
 outside=int(np.count_nonzero(x[:96000])+np.count_nonzero(x[-480000:]));x[:96000]=0;x[-480000:]=0
 normalized=FINAL/'voice-normalized.wav';sf.write(normalized,x,48000,subtype='PCM_16')
 save(FINAL/'normalization-outside-body-silence.json',dict(createdAt=now(),originalPassSha256=sha(normalPass),
  normalizedSha256=sha(normalized),outsideBodyNonzeroSamplesBefore=outside,changedOnlyBrandingAndMembership=True,allBodyNormalizedSamplesRetained=True))
 md=float(json.loads(run(FP,['-v','error','-show_format','-of','json',music],'CPU2-Nimbus-probe'))['format']['duration'])
 originalMusicSha=sha(music);count=int(np.ceil((D-1)/(md-1)))
 if count>1:
  chain=';'.join(f"{'[0:a]' if k==1 else '[b'+str(k-1)+']'}[{k}:a]acrossfade=d=1:c1=tri:c2=tri[b{k}]" for k in range(1,count))
  continuous=FINAL/'nimbus-continuous.wav'
  ff([*sum((['-i',music] for _ in range(count)),[]),'-filter_complex',chain,'-map',f'[b{count-1}]','-c:a','pcm_s16le',continuous],'CPU2-continuous-approved-Nimbus')
  music=continuous
 bg=FINAL/'bgm-before-ducking.wav'
 ff(['-i',music,'-af',f'atrim=duration={D},asetpts=PTS-STARTPTS,loudnorm=I=-28:TP=-3:LRA=11,aresample=48000,aformat=channel_layouts=stereo,afade=t=in:d=0.45,afade=t=out:st={D-.45}:d=0.45','-c:a','pcm_s16le',bg],'CPU2-background-level')
 mix=FINAL/'final-mix.wav';aac=FINAL/'final-mix.m4a'
 filt='[0:a]asplit[n][d];[1:a][d]sidechaincompress=threshold=.08:ratio=2.2:attack=15:release=280[bg];[n][bg]amix=inputs=2:normalize=0,alimiter=limit=.80:level=false:latency=true[mix]'
 ff(['-i',normalized,'-i',bg,'-filter_complex',filt,'-map','[mix]','-ar','48000','-ac','2','-c:a','pcm_s16le',mix],'CPU2-final-current-Nimbus-ducked-mix')
 assert sf.info(mix).frames==N*800
 ff(['-i',mix,'-c:a','aac','-b:a','192k',aac],'CPU2-final-current-AAC')
 final=scan(aac,-16,-1.5);assert abs(float(final['input_i'])+16)<=.6 and float(final['input_tp'])<=-1.5,final
 save(FINAL/'mix-settings.json',dict(createdAt=now(),durationSeconds=D,frames=N,planSha256=sha(planPath),
  voiceSourceSha256=sha(voice),narration=raw,finalAacMeasurement=final,wavSha256=sha(mix),aacSha256=sha(aac),bgmSha256=sha(bg),
  approvedNimbusReferenceSha256=originalMusicSha,continuousApprovedNimbus=True,sourceAudioStreams=0,newTts=0,
  originalNimbusFileVerified=False,currentFinalMixedWindowAsr='pending',humanWholeListening='pending',humanPronunciation='pending'))
 s.update(status='closed-final-current-Nimbus-mix-awaiting-direct-ASR',exitCode=0,endedAt=now(),activeTask=None);checkpoint()
 print(json.dumps(dict(exitCode=0,frames=N,seconds=D,lufs=final['input_i'],truePeak=final['input_tp'],finalMixedAsrApproved=False)),flush=True)
except BaseException:
 s.update(status='closed-final-current-mix-failed',exitCode=1,endedAt=now(),activeTask=None,error=traceback.format_exc());checkpoint();raise
