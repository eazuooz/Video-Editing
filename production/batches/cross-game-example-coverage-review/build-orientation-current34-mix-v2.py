"""One CPU2, no-BGM current34 mix. Preserve every source PCM sample and pause."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, ctypes, hashlib, json, os, re, subprocess, traceback, wave
for k in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS']:os.environ[k]='2'
import psutil
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
OUT=ROOT/'shared/output/unpublished-teaching-clarity-revision/orientation/current34-mix-v2'
STATE=O/'current34-mix-execution-v2.json'
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
NODE='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
now=lambda:datetime.now(timezone.utc).isoformat()
def rel(p):return p.resolve().relative_to(ROOT).as_posix()
def save(p,x):
 t=p.with_name(p.name+'.writing');t.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
def wav(p,raw,rate,channels):
 with wave.open(str(p),'wb') as w:w.setnchannels(channels);w.setsampwidth(2);w.setframerate(rate);w.writeframes(raw)
def params(p):
 with wave.open(str(p),'rb') as w:return (w.getnframes(),w.getframerate(),w.getnchannels(),w.getsampwidth())
def checkpoint():
 session=O/'current34-mix-execution-v2.session.json'
 if session.exists():
  v=read(session);assert v['pid']==me.pid and abs(v['createTime']-me.create_time())<.01;state['sessionId']=v['sessionId']
 state['updatedAt']=now();save(STATE,state)
 cp=read(O/'latest-checkpoint.json');cp.update(recordedAt=now(),stage=state['status'],activeOwnedWorkers=1 if state['actualExitCode'] is None else 0,
  ownedJob=dict(active=state['actualExitCode'] is None,pid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),cwd=me.cwd(),sessionId=state['sessionId'],state=rel(STATE),cpuThreads=2,gpuJobs=0,actualExitCode=state['actualExitCode']),
  current34MixExecution=rel(STATE),currentMixedAudioApproved=False,next='Verify actual current34 mix exit; review whole34 and independent complete current AAC contexts before timing/pixel approval. Preserve baseline24/10 additions/no BGM.')
 save(O/'latest-checkpoint.json',cp)
 qp=B/'queue.json';old=qp.read_text('utf-8-sig');q=json.loads(old);v=q['currentOrientationReview']
 v.update(stage=cp['stage'],activeOwnedWorkers=cp['activeOwnedWorkers'],ownedJob=cp['ownedJob'],current34MixExecution=rel(STATE),next=cp['next'])
 q.update(updatedAt=now());assert qp.read_text('utf-8-sig')==old;save(qp,q)
def run(args,name):
 command=[FF,'-hide_banner','-nostdin','-threads','2','-filter_threads','2','-filter_complex_threads','2',*args]
 with (OUT/(name+'.log')).open('wb') as log:
  child=subprocess.Popen(command,stdout=log,stderr=log,cwd=ROOT);p=psutil.Process(child.pid)
  row=dict(name=name,pid=p.pid,createTime=p.create_time(),commandLine=p.cmdline(),cwd=p.cwd(),exitCode=None,log=rel(OUT/(name+'.log')))
  state['subprocesses'].append(row);checkpoint();code=child.wait();row['exitCode']=code;checkpoint()
 assert code==0,name
def scan(p,name):
 run(['-i',str(p),'-af','loudnorm=I=-16:TP=-2:LRA=11:print_format=json','-f','null','-'],name)
 return json.loads(re.search(r'\{\s*"input_i"[\s\S]*?\}',(OUT/(name+'.log')).read_text('utf-8',errors='replace'))[0])
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--resource',required=True);a=ap.parse_args();resource=read(ROOT/a.resource)
 assert (datetime.now(timezone.utc)-datetime.fromisoformat(resource['observedAt'])).total_seconds()<240
 assert resource['ownHeavyJobs']==0 and resource['cpuLoadPercent']<85 and resource['freePhysicalMemoryKiB']>8_000_000
 assert not OUT.exists() and not STATE.exists()
 launcher=psutil.Process().parent();same_launcher=launcher is not None and launcher.name().lower()=='python.exe' and launcher.cmdline()[1:]==psutil.Process().cmdline()[1:]
 allowed_launcher_pid=launcher.pid if same_launcher else None
 for p in psutil.process_iter(['pid','name','cmdline']):
  try:
   cmd=' '.join(p.info['cmdline'] or [])
   assert p.pid in (os.getpid(),allowed_launcher_pid) or (p.info['name'] or '').lower() not in ('python.exe','ffmpeg.exe','node.exe') or not ('cross-game-example-coverage-review' in cmd and any(s in cmd for s in ['build-orientation-current34','review-orientation','render-orientation','extract-orientation']))
  except (psutil.NoSuchProcess,psutil.AccessDenied):pass
 subprocess.run([NODE,'scripts/review-video-duplicates.cjs','game-math-orientation-matrices','--candidate-file',str(O/'duplicate-candidate-v1.json'),'--check'],cwd=ROOT,check=True)
 proof=read(O/'narration-07b-guide-repair-execution-v1.json');protected=proof['protectedInputs'];assert len(protected)==79
 for r in protected+proof['results']:assert sha(ROOT/r['path'])==r['sha256']
 planpath=O/'current34-measured-timing-plan-v1.json';plan=read(planpath)
 assert plan['noBgm'] and plan['noSourceAudio'] and plan['sceneCount']==34 and len(plan['voicePlacements'])==76
 assert plan['all24BaselineScenesAndPcmRetained'] and plan['current10AdditionsPcmAllSamplesMappedExactly']
 assert (plan['bodyFrames'],plan['actualFrames'],plan['explanationFrames'])==(65197,26079,39118)
 assert all(r['exactBaselineDistributedBytesMatched'] for r in plan['baselineDistributedPcmProof'])
 OUT.mkdir(parents=True);me=psutil.Process()
 if os.name=='nt':ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x00004000)
 state=dict(schemaVersion=1,pid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),cwd=me.cwd(),sessionId=None,startedAt=now(),status='assembling-current34-preserved-PCM-no-BGM',actualExitCode=None,resource=resource,
  cpuThreads=2,gpuJobs=0,researchManipulations=0,subprocesses=[],placements=[],protectedInputs=protected,additionalPcmProtected=proof['results'],plan=rel(planpath),planSha256=sha(planpath),currentMixedAudioApproved=False,humanListeningApproved=False,humanPronunciationApproved=False,noBgm=True,noSourceAudio=True,originalPcmRegenerated=False,newGitMedia=0)
 checkpoint()
 try:
  full=plan['totalFrames']*400;body=plan['bodyFrames']*400;raw=bytearray(full*2);coverage={};dest=[];byid={s['id']:s for s in plan['scenes']}
  for r in plan['voicePlacements']:
   path=ROOT/r['voice'];assert sha(path)==r['sha256'];s=byid[r['scene']]
   with wave.open(str(path),'rb') as w:
    assert (w.getframerate(),w.getnchannels(),w.getsampwidth())==(24000,1,2)
    ns=w.getnframes();w.setpos(r['sourceStartSample']);pcm=w.readframes(r['sourceEndSample']-r['sourceStartSample'])
   n=r['sourceEndSample']-r['sourceStartSample'];start=r['destinationStartSample'];end=start+n
   assert n>0 and len(pcm)==n*2 and s['frameIn']*400<=start<end<=s['frameOut']*400
   assert start==s['frameIn']*400+r['sceneStartSample']
   assert all(end<=x or start>=y for x,y in dest);dest.append((start,end));raw[start*2:end*2]=pcm
   assert bytes(raw[start*2:end*2])==pcm
   coverage.setdefault(r['voice'],[]).append((r['sourceStartSample'],r['sourceEndSample'],ns))
   state['placements'].append(dict(r,pcmSha256=hashlib.sha256(pcm).hexdigest(),exactOriginalPcmBytesMatched=True,destinationEndSample=end))
  assert len(coverage)==34
  for spans in coverage.values():
   cursor=0
   for start,end,ns in sorted(spans):assert start==cursor;cursor=end
   assert cursor==ns
  for proofrow in plan['baselineDistributedPcmProof']:
   s=byid[proofrow['id']];distributed=raw[s['frameIn']*800:s['frameOut']*800]
   assert hashlib.sha256(distributed).hexdigest()==proofrow['distributedPcmSha256'],s['id']
  assert not any(raw[:96000]) and not any(raw[(120+plan['bodyFrames'])*800:])
  rawp=OUT/'current34.raw-placement.wav';wav(rawp,raw,24000,1)
  bodyp=OUT/'current34.body.raw.wav';wav(bodyp,raw[96000:(120+plan['bodyFrames'])*800],24000,1)
  measured=scan(bodyp,'raw-body-loudness');normalbody=OUT/'voice-normalized-body.wav'
  filt=f"loudnorm=I=-16:TP=-2:LRA=11:measured_I={measured['input_i']}:measured_TP={measured['input_tp']}:measured_LRA={measured['input_lra']}:measured_thresh={measured['input_thresh']}:offset={measured['target_offset']}:linear=true,aresample=48000,aformat=channel_layouts=stereo"
  run(['-i',str(bodyp),'-af',filt,'-c:a','pcm_s16le',str(normalbody)],'normalize-body')
  assert params(normalbody)==(body*2,48000,2,2)
  with wave.open(str(normalbody),'rb') as w:normalized=w.readframes(w.getnframes())
  padded=b'\0'*96000*4+normalized+b'\0'*480000*4;assert len(padded)==full*2*4
  passp=OUT/'voice-loudnorm-pass.wav';wav(passp,padded,48000,2);passmeasure=scan(passp,'voice-pass-loudness')
  gain=min(-16-float(passmeasure['input_i']),-2-float(passmeasure['input_tp']))
  final=OUT/'current34.final-mix.wav';run(['-i',str(passp),'-af',f'volume={gain}dB','-c:a','pcm_s16le',str(final)],'constant-voice-gain')
  assert params(final)==(full*2,48000,2,2);finalmeasure=scan(final,'final-WAV-loudness')
  assert abs(float(finalmeasure['input_i'])+16)<=.6 and float(finalmeasure['input_tp'])<=-1.5
  aac=OUT/'current34.final-mix.m4a';run(['-i',str(final),'-c:a','aac','-b:a','192k',str(aac)],'encode-AAC')
  decoded=OUT/'current34.AAC-decoded.wav';run(['-i',str(aac),'-af',f'atrim=end_sample={full*2}','-ar','48000','-ac','2','-c:a','pcm_s16le',str(decoded)],'decode-current-AAC')
  assert params(decoded)==params(final);aacmeasure=scan(decoded,'AAC-decoded-loudness')
  assert abs(float(aacmeasure['input_i'])+16)<=.6 and float(aacmeasure['input_tp'])<=-1.45
  for r in protected+proof['results']:assert sha(ROOT/r['path'])==r['sha256']
  files=[rawp,bodyp,normalbody,passp,final,aac,decoded]
  state.update(status='current34-mix-created-awaiting-actual-exit-and-mixed-ASR',actualExitCode=0,finishedAt=now(),all79ProtectedInputsUnchanged=True,all34RawPcmPlacementsExact=True,all24BaselineDistributedPcmExact=True,rawNarration=measured,voicePass=passmeasure,constantVoiceGainDb=gain,finalWavMeasurement=finalmeasure,aacDecodedMeasurement=aacmeasure,totalFrames=plan['totalFrames'],seconds=plan['seconds'],files=[dict(path=rel(p),sha256=sha(p),size=p.stat().st_size) for p in files],mixWav=rel(final),mixWavSha256=sha(final),mixAac=rel(aac),mixAacSha256=sha(aac),decodedAac=rel(decoded),decodedAacSha256=sha(decoded))
  checkpoint();print(json.dumps(dict(totalFrames=plan['totalFrames'],seconds=plan['seconds'],raw34PcmExact=True,baseline24DistributedExact=True,final=finalmeasure,decodedAac=aacmeasure),ensure_ascii=False),flush=True)
 except BaseException:
  state.update(status='failed-current34-mix-preserve-local-files',actualExitCode=1,error=traceback.format_exc(),finishedAt=now());checkpoint();raise
