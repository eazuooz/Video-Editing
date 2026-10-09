"""Resume only the final gain/AAC stage; preserve completed timeline and music."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, ctypes, hashlib, json, os, re, subprocess, sys, time, traceback
import soundfile as sf
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent;W=BASE/'final-v1'
STATE=W/'mix-level-repair-execution.json';SESSION=W/'mix-level-repair-session.json'
FF=Path('C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe')
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
old=read(W/'mix-execution.json');assert old['exitCode']==1 and len(old['commands'])==8
assert all(x['exitCode']==0 for x in old['commands'])
assert "'-18.09'" in old['error'] and 'AssertionError' in old['error']
assert not STATE.exists() and not (W/'mix-settings.json').exists()
wav=W/'final-mix.wav';aac=W/'final-mix.m4a';N=37098
assert sf.info(wav).frames==N*800
inputs={rel(p):sha(p) for p in [wav,aac,W/'narration-timed.wav',W/'voice-normalized.wav',W/'nimbus-continuous.wav',W/'bgm-before-ducking.wav',W/'plan.json',W/'pcm-timeline-preservation.json']}
if os.name=='nt':ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x00004000)
s=dict(schemaVersion=1,slug='similar-game-design',pid=os.getpid(),sessionId=None,commandLine=[sys.executable,*sys.argv],startedAt=now(),
 status='repair-only-final-output-gain',resourceEvidence=a.resource,cpuThreads=2,gpu=0,singleJob=True,exitCode=None,commands=[],
 originalFailedExecution=rel(W/'mix-execution.json'),originalExecutionSha256=sha(W/'mix-execution.json'),preservedInputs=inputs,
 gainDb=2.1,newTts=0,sourceAudioStreams=0,finalMixedAsrApproved=False,allFinalPixels=False,collected=False,uploaded=False)
def checkpoint():
 if SESSION.exists():
  v=read(SESSION)
  if v['pid']==os.getpid():s.update(sessionId=v['sessionId'],processIdentity=v['processIdentity'])
 s['observedAt']=now();save(STATE,s)
 job=dict(pid=s['pid'],sessionId=s['sessionId'],commandLine=s['commandLine'],processIdentity=s.get('processIdentity'),state=rel(STATE),status=s['status'],
  cpuThreads=2,gpu=0,singleJob=True,activeTask=s.get('activeTask'),exitCode=s['exitCode'],workerExpectedRunning=s['exitCode'] is None)
 cpPath=BASE/'latest-checkpoint.json';cp=read(cpPath);cp.update(stage=s['status'],ownedJob=job,recordedAt=now(),finalMixExecution=rel(STATE),
  nextAction='Direct comparison of48 current final mixed whole/context windows, then guarded pair/final pixels/QA/collection/private/Git.');save(cpPath,cp)
 qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qp);i=next(x for x in q['items'] if x['slug']=='similar-game-design')
 i.update(stage=s['status'],currentExecution=job,finalMixExecution=rel(STATE),nextAction=cp['nextAction']);q['updatedAt']=now();save(qp,q)
def ff(args,kind):
 log=W/f'mix-level-repair-{len(s["commands"])+1:02d}.log';cmd=[str(FF),'-hide_banner','-nostdin','-threads','2','-filter_threads','1','-filter_complex_threads','1',*map(str,args)]
 op=dict(kind=kind,commandLine=cmd,log=rel(log),startedAt=now());s['commands'].append(op)
 with log.open('w',encoding='utf-8') as f:
  p=subprocess.Popen(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW);op['pid']=p.pid
  s.update(status=kind,activeTask=op);checkpoint();code=p.wait()
 op.update(exitCode=code,endedAt=now());s['activeTask']=None;checkpoint();assert code==0,log
 return log.read_text('utf-8-sig')
try:
 checkpoint();fixed=W/'final-mix.level-fixed.wav';faac=W/'final-mix.level-fixed.m4a'
 assert not fixed.exists() and not faac.exists()
 ff(['-i',wav,'-af','volume=2.1dB','-c:a','pcm_s16le',fixed],'CPU2-final-level-only-correction')
 assert sf.info(fixed).frames==N*800
 ff(['-i',fixed,'-c:a','aac','-b:a','192k',faac],'CPU2-corrected-final-AAC')
 out=ff(['-i',faac,'-af','loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json','-f','null','-'],'CPU2-corrected-final-AAC-level-scan')
 final=json.loads(re.search(r'\{\s*"input_i"[\s\S]*?\}',out).group())
 assert abs(float(final['input_i'])+16)<=.6 and float(final['input_tp'])<=-1.5,final
 for p,h in inputs.items():assert sha(ROOT/p)==h,p
 assert not (W/'final-mix.pre-level-fix.wav').exists() and not (W/'final-mix.pre-level-fix.m4a').exists()
 wav.rename(W/'final-mix.pre-level-fix.wav');aac.rename(W/'final-mix.pre-level-fix.m4a');fixed.rename(wav);faac.rename(aac)
 raw=json.loads(re.search(r'\{\s*"input_i"[\s\S]*?\}',(W/'mix-01.log').read_text('utf-8-sig')).group())
 music=read(BASE.parent/'project.json')['audio']['backgroundMusic']
 settings=dict(createdAt=now(),durationSeconds=N/60,frames=N,planSha256=sha(W/'plan.json'),voiceSourceSha256=sha(W/'narration-timed.wav'),
  narration=raw,finalAacMeasurement=final,wavSha256=sha(wav),aacSha256=sha(aac),bgmSha256=sha(W/'bgm-before-ducking.wav'),
  approvedNimbusReferenceSha256=music['restoration']['sha256'],continuousApprovedNimbus=True,sourceAudioStreams=0,newTts=0,
  originalNimbusFileVerified=False,currentFinalMixedWindowAsr='pending',humanWholeListening='pending',humanPronunciation='pending',
  originalMixExecution=rel(W/'mix-execution.json'),originalExitCode=1,repairExecution=rel(STATE),repairGainDb=2.1,
  allCompletedOriginalTimelineAndBgmStepsPreserved=True,preLevelWavSha256=inputs[rel(wav)],preLevelAacSha256=inputs[rel(aac)])
 save(W/'mix-settings.json',settings)
 s.update(status='closed-current-Nimbus-mix-level-repaired-awaiting-direct-ASR',exitCode=0,endedAt=now(),activeTask=None,
  finalAacMeasurement=final,wavSha256=settings['wavSha256'],aacSha256=settings['aacSha256']);checkpoint()
 print(json.dumps(dict(exitCode=0,lufs=final['input_i'],truePeak=final['input_tp'],frames=N,finalMixedAsrApproved=False)),flush=True)
except BaseException:
 s.update(status='closed-final-level-repair-failed',exitCode=1,endedAt=now(),error=traceback.format_exc(),activeTask=None);checkpoint();raise
