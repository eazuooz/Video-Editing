"""Finite selected111 voice controller. Default preflight is read-only.

Only --execute may stage inputs/start the exact prepared Qwen command. Qwen alone
owns its GPU lease. The wrapper never creates, reclaims or removes any GPU lease,
never closes apps and never edits checkpoints/other films. All selected raw scene
PCM is preserved; the canonical aggregate is an exact separate CPU concatenation.
"""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,math,os,shutil,subprocess,sys,time,uuid,wave
from pathlib import Path
sys.dont_write_bytecode=True
import psutil
from initialize import ROOT,HERE,MEDIA,read,save

spec=importlib.util.spec_from_file_location('selected_voice_preparer',HERE/'prepare-selected-voice.py');prep=importlib.util.module_from_spec(spec);spec.loader.exec_module(prep)
spec=importlib.util.spec_from_file_location('selected_voice_resource_instance',HERE/'run-zen-view-native.py');zen=importlib.util.module_from_spec(spec);spec.loader.exec_module(zen)
runtime=zen.runtime
PROTOCOL='architectural111-selected-voice-v1'
CREATE=getattr(subprocess,'CREATE_NO_WINDOW',0)
DECLINES=('GPU capacity is insufficient for this profile:','Unregistered GPU activity is present.')

class ResourceWait(RuntimeError):pass

def sha(p):
 with Path(p).open('rb') as handle:return hashlib.file_digest(handle,'sha256').hexdigest()
def digest(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def identity(pid=None):
 p=psutil.Process(os.getpid() if pid is None else pid);args=p.cmdline()
 return dict(pid=p.pid,createTime=p.create_time(),argv=args,commandSHA256=digest(args))
def alive(rec):
 if not rec:return False
 try:
  p=psutil.Process(rec['pid'])
  if 'createTime' not in rec:return True
  if abs(p.create_time()-rec['createTime'])>=.01:return False
  if not rec.get('argv') or not rec.get('commandSHA256'):return True
  # Same PID/time with an unexpected/unknown argv remains protected, never called dead.
  if digest(rec['argv'])!=rec['commandSHA256'] or p.cmdline()!=rec['argv']:return True
  return True
 except psutil.NoSuchProcess:return False
 except (psutil.AccessDenied,KeyError,TypeError):return True

def configure(topic):
 if not __import__('re').fullmatch(r'\d{2}\.\d{2}',topic):raise ValueError('Exact topicId required')
 tag=topic.replace('.','-');owner='architectural-111-'+tag+'-voice'
 runtime.PROTOCOL=PROTOCOL;runtime.OWNER=owner
 def archive_owned(path,token):
  target=MEDIA/(tag+'-voice-history')/(Path(path).name+'.'+token+'.'+uuid.uuid4().hex+'.json')
  target.parent.mkdir(parents=True,exist_ok=True);os.replace(path,target);return target
 runtime.archive=archive_owned
 return dict(topicId=topic,slug='shorts-leveldesign-'+tag,owner=owner,worker=MEDIA/(tag+'-voice-worker.json'),state=MEDIA/(tag+'-voice-progress.json'),evidence=MEDIA/(tag+'-voice-evidence.json'),history=MEDIA/(tag+'-voice-history'))

def project_children(slug):
 found=[]
 for p in psutil.process_iter(['pid','name','cmdline']):
  try:
   args=p.info['cmdline'] or []
   if p.pid==os.getpid() or not any(Path(a).name.lower()=='render_narration.py' for a in args):continue
   if '--project' not in args:continue
   n=args.index('--project')
   if n+1<len(args) and args[n+1]==slug:found.append(identity(p.pid))
  except psutil.NoSuchProcess:continue
  except psutil.AccessDenied:raise ResourceWait('A possible Qwen child cannot be inspected; preserve it')
 return found

def busy_reason():
 reason=zen.busy_reason()
 if reason:return reason
 raw=subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True,creationflags=CREATE)
 free,use=map(int,raw.splitlines()[0].replace(' ','').split(','))
 return f'Strict Qwen headroom gate: {free}MiB/{use}% (need8192MiB and below15%)' if free<8192 or use>=15 else None

def prepared(args):
 slug='shorts-leveldesign-'+args.topic.replace('.','-')
 try:return prep.prepare(args.topic,args.native_evidence or f'projects/{slug}/native-evidence-v1.json',args.native_qa or f'projects/{slug}/native-visual-qa-v1.json',args.semantic_components)
 except FileNotFoundError as error:raise prep.Pending('A required preparation input is missing: '+str(error)) from error

def wav_info(path):
 pcm=hashlib.sha256();total=0
 with wave.open(str(path),'rb') as w:
  frames,rate,channels,width=w.getnframes(),w.getframerate(),w.getnchannels(),w.getsampwidth()
  if w.getcomptype()!='NONE' or frames<=0 or (rate,channels,width)!=(24000,1,2):raise ValueError('Expected nonempty raw24kHz mono PCM16 WAV')
  while True:
   data=w.readframes(65536)
   if not data:break
   total+=len(data);pcm.update(data)
 if total!=frames*channels*width:raise ValueError('Truncated PCM WAV')
 return dict(path=str(Path(path).resolve()),sha256=sha(path),pcmSHA256=pcm.hexdigest(),sampleRate=rate,channels=channels,sampleWidthBytes=width,frames=frames,durationSeconds=frames/rate)

def immutable(path,data):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
 if path.exists():
  if path.read_bytes()!=data:raise RuntimeError('Existing derived/request file differs; preserve it: '+str(path))
  return
 try:
  with path.open('xb') as handle:handle.write(data)
 except FileExistsError:
  if path.read_bytes()!=data:raise RuntimeError('Concurrent output collision')
def immutable_json(path,obj):immutable(path,(json.dumps(obj,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
def scenes(prov):return prov['identity']['scenes']
def output_of(prov):
 out=Path(prov['voiceOutputDirectory']).resolve();parent=(ROOT/'shared/output'/prep.BATCH_ID/prov['topicId'].replace('.','-')/'voice-attempts').resolve()
 if out.parent!=parent or out.name!=prov['fingerprint'][:24]:raise RuntimeError('Selected voice output scope differs')
 return out

def validate_receipt(prov,out):
 p=out/'voice-inputs.json'
 if not p.is_file():raise RuntimeError('Existing output lacks proven voice inputs; preserve and inspect')
 r=read(p)
 if r.get('protocol')!=PROTOCOL or r.get('fingerprint')!=prov['fingerprint'] or r.get('identity')!=prov['identity']:raise RuntimeError('Existing voice identity differs; preserve and inspect')
 return r

def initialize_output(prov):
 out=output_of(prov);receipt=out/'voice-inputs.json'
 if out.exists() and any(out.iterdir()):validate_receipt(prov,out)
 else:
  out.mkdir(parents=True,exist_ok=True)
  immutable_json(receipt,dict(protocol=PROTOCOL,fingerprint=prov['fingerprint'],identity=prov['identity'],initialPreparationFingerprint=prov['preparationFingerprint'],inputs=prov['inputs'],rawPcmPolicy=prov['identity']['rawPcmPolicy']))
 return out

def progress(prov,out):
 path=out/'scene-progress.json';r=read(path) if path.exists() else dict(protocol=PROTOCOL,fingerprint=prov['fingerprint'],scenes={})
 if r['protocol']!=PROTOCOL or r['fingerprint']!=prov['fingerprint']:raise RuntimeError('Partial scene proof identity differs')
 expected={s['id']:s['lines'][0] for s in scenes(prov)}
 for sid,row in r['scenes'].items():
  if sid not in expected or row['spokenText']!=expected[sid]:raise RuntimeError('Partial spoken-scene mapping differs')
  now=wav_info(out/'chunks'/f'{sid}-scene.wav')
  if any(now[k]!=row[k] for k in ['sha256','pcmSHA256','frames','sampleRate']):raise RuntimeError('Preserved partial scene changed outside a recorded launch')
 return r

def register_scenes(prov,out,attempt):
 path=out/'scene-progress.json';old=read(path) if path.exists() else dict(protocol=PROTOCOL,fingerprint=prov['fingerprint'],scenes={})
 if old.get('protocol')!=PROTOCOL or old.get('fingerprint')!=prov['fingerprint']:raise RuntimeError('Partial proof belongs to different voice inputs')
 if path.exists():immutable(out/'scene-proof-history'/(sha(path)+'.json'),path.read_bytes())
 result=dict(protocol=PROTOCOL,fingerprint=prov['fingerprint'],scenes=dict(old['scenes']))
 for scene in scenes(prov):
  p=out/'chunks'/(scene['id']+'-scene.wav')
  if not p.exists():continue
  info=wav_info(p);saved=out/'selected-raw-preserved'/(info['sha256']+'.wav')
  immutable(saved,p.read_bytes())
  result['scenes'][scene['id']]=dict(info,spokenText=scene['lines'][0],attempt=str(attempt),preservedExactRawPath=str(saved),structuralOnly=True,independentAsrVerified=False,humanListening=False)
  save(path,result)  # A valid earlier scene survives a later malformed scene.
 return result

def audio_inventory(out):
 return {p.relative_to(out).as_posix():sha(p) for p in sorted((out/'chunks').glob('*.wav'))} if (out/'chunks').exists() else {}

def preserve_engine_files(out,attempt):
 rows=[]
 for p in ([x for x in sorted((out/'chunks').glob('*.wav'))] if (out/'chunks').exists() else [])+[out/'narration.wav',out/'narration.timing.json',out/'narration.srt']:
  if not p.is_file():continue
  target=attempt/'prior-artifacts'/p.relative_to(out);immutable(target,p.read_bytes());rows.append(dict(path=str(p),sha256=sha(p),preservedPath=str(target)))
 immutable_json(attempt/'prior-artifacts.json',rows);return rows

def validate_engine_outputs(prov,out):
 expected=scenes(prov);chunks=[wav_info(out/'chunks'/f'{s["id"]}-scene.wav') for s in expected]
 timing=read(out/'narration.timing.json');aggregate=wav_info(out/'narration.wav');entries=timing['entries'];position=0;rate=24000
 if len(entries)!=len(expected) or timing.get('render_mode')!='scene' or timing.get('sample_rate')!=rate:raise ValueError('Engine timing scene count/format differs')
 for scene,entry,chunk in zip(expected,entries,chunks):
  if entry['scene_id']!=scene['id'] or entry['text']!=' '.join(scene['lines']):raise ValueError('Engine timing spoken text/order differs')
  if abs(entry['start']-position/rate)>2/rate or abs(entry['end']-(position+chunk['frames'])/rate)>2/rate:raise ValueError('Engine timing boundaries differ from raw scenes')
  position+=chunk['frames']
 if aggregate['frames']!=position or abs(timing['duration_seconds']-position/rate)>2/rate:raise ValueError('Engine aggregate frame count differs')
 srt=out/'narration.srt'
 if not srt.is_file() or not srt.read_text(encoding='utf-8').strip():raise ValueError('Engine SRT missing')
 return chunks,dict(aggregateWav=aggregate,timing=dict(path=str(out/'narration.timing.json'),sha256=sha(out/'narration.timing.json')),srt=dict(path=str(srt),sha256=sha(srt)))

def canonical_outputs(prov,out,engine):
 """Retain natural raw samples; avoid the engine's import-bound6ms aggregate fade."""
 expected=scenes(prov);canonical=out/'canonical';rate=24000;position=0;entries=[];chunks=[];pcm=hashlib.sha256();payload=[]
 for scene in expected:
  p=out/'chunks'/f'{scene["id"]}-scene.wav';info=wav_info(p);chunks.append(info)
  with wave.open(str(p),'rb') as source:data=source.readframes(info['frames'])
  payload.append(data);pcm.update(data);start=position;position+=info['frames']
  entries.append(dict(index=len(entries)+1,scene_id=scene['id'],scene_title=scene['id'],text=' '.join(scene['lines']),start=start/rate,end=position/rate))
 import io
 stream=io.BytesIO()
 with wave.open(stream,'wb') as target:target.setparams((1,2,rate,position,'NONE','not compressed'));target.writeframes(b''.join(payload))
 immutable(canonical/'narration.wav',stream.getvalue())
 timing=dict(sample_rate=rate,duration_seconds=position/rate,render_mode='scene',example_seconds=0,narration_placement='continuous-across-example-and-explanation',entries=entries)
 immutable_json(canonical/'narration.timing.json',timing)
 def stamp(seconds):
  n=round(seconds*1000);s,ms=divmod(n,1000);m,s=divmod(s,60);h,m=divmod(m,60);return f'{h:02}:{m:02}:{s:02},{ms:03}'
 srt='\n\n'.join(f"{e['index']}\n{stamp(e['start'])} --> {stamp(e['end'])}\n{e['text']}" for e in entries)+'\n'
 immutable(canonical/'narration.srt',srt.encode('utf-8'));actual=wav_info(canonical/'narration.wav')
 if actual['pcmSHA256']!=pcm.hexdigest() or actual['frames']!=position:raise AssertionError('Canonical aggregate is not exact selected raw PCM')
 return dict(protocol=PROTOCOL,topicId=prov['topicId'],fingerprint=prov['fingerprint'],identity=prov['identity'],status='raw-voice-structurally-complete-independent-ASR-listening-pending',output=str(out),sceneWavs=chunks,aggregateWav=actual,timing=dict(path=str(canonical/'narration.timing.json'),sha256=sha(canonical/'narration.timing.json')),engineSrt=dict(path=str(canonical/'narration.srt'),sha256=sha(canonical/'narration.srt')),paragraphMapping=prov['paragraphMapping'],engineOutputsPreserved=engine,canonicalPcmOrigin='Exact concatenation of selected raw scene PCM; no added gaps, trimming, fades, level changes or time warp',engineAggregateFadeFact='Trusted engine _apply_edge_fades default captured0.006s at import, regardless of manifest edgeFadeSeconds0; original engine aggregate is preserved unchanged.',internalUnsavedRetryWaveformsClaimedPreserved=False,independentAsrVerified=False,actualListening=False,humanApproval=False,finalFilmComplete=False,platformActions=[])

def verify_complete(prov,out):
 p=out/'voice-complete-proof.json'
 if not p.is_file():return None
 proof=read(p)
 if proof.get('protocol')!=PROTOCOL or proof.get('fingerprint')!=prov['fingerprint'] or proof.get('identity')!=prov['identity']:raise RuntimeError('Completed voice proof identity differs')
 for row in proof['sceneWavs']+[proof['aggregateWav']]:
  now=wav_info(row['path'])
  if any(now[k]!=row[k] for k in ['sha256','pcmSHA256','frames','sampleRate']):raise RuntimeError('Completed selected voice PCM changed')
 for row in [proof['timing'],proof['engineSrt']]:
  if sha(row['path'])!=row['sha256']:raise RuntimeError('Completed voice timing/SRT changed')
 engine=proof.get('engineOutputsPreserved',{})
 for key in ['aggregateWav','timing','srt']:
  if key in engine and sha(engine[key]['path'])!=engine[key]['sha256']:raise RuntimeError('Preserved engine artifact changed')
 for row in engine.get('existingArtifacts',[]):
  if sha(row['path'])!=row['sha256']:raise RuntimeError('Preserved interrupted engine artifact changed')
 return proof

def publish_proof(ctx,prov,proof):
 # Never overwrite a parent-added same-voice ASR/listening/human review with a pending flag.
 p=ctx['evidence']
 if p.exists():
  old=read(p)
  if old.get('fingerprint')==proof['fingerprint']:
   for key in ['identity','sceneWavs','aggregateWav','timing','engineSrt']:
    if old.get(key)!=proof[key]:raise RuntimeError('Same-fingerprint published raw evidence differs; preserve parent review and inspect')
   return
  immutable(ctx['history']/(sha(p)+'.evidence.json'),p.read_bytes())
 save(p,proof)

def premodel_decline(code,log,before,after):
 text=Path(log).read_text(encoding='utf-8',errors='replace').strip()
 return bool(code and before==after and text.startswith(DECLINES) and not any(x in text for x in ['Project:','Rendering ','Inference device:','Traceback']))

def validate_launch_request(prov,out,pending):
 attempt=Path(pending['attempt']).resolve();request_path=attempt/'request.json'
 if not attempt.is_relative_to((out/'engine-attempts').resolve()):raise RuntimeError('Pending attempt escaped output')
 pinned={Path(r['path']).resolve():r['sha256'] for r in pending['requestPins']}
 if request_path not in pinned:raise RuntimeError('Pending launch lacks its exact request pin')
 request=read(request_path)
 if request.get('protocol')!=PROTOCOL or request.get('fingerprint')!=prov['fingerprint'] or request.get('identity')!=prov['identity']:raise RuntimeError('Pending request differs from selected synthesis identity')
 command=request['command'];expected=prov['qwenSynthesisArgv']
 if len(command)!=len(expected) or command[:8]!=expected[:8] or command[9:]!=expected[9:]:raise RuntimeError('Pending engine argv differs from approved prepared command')
 manifest_path=(ROOT/command[8]).resolve();stage=(ROOT/'projects'/prov['slug']/'production/voice-preparation').resolve()
 if not manifest_path.is_relative_to(stage) or manifest_path not in pinned:raise RuntimeError('Pending manifest is outside immutable selected staging')
 manifest=read(manifest_path);script_path=(ROOT/manifest['paths']['script']).resolve()
 if script_path.parent!=manifest_path.parent or script_path not in pinned:raise RuntimeError('Pending script is not the pinned immutable scene prose')
 if [{'id':s['id'],'lines':s['lines']} for s in read(script_path)['scenes']]!=scenes(prov):raise RuntimeError('Pending script spoken scenes differ')
 if manifest.get('slug')!=prov['slug'] or (ROOT/manifest['tts']['outputDir']).resolve()!=out:raise RuntimeError('Pending manifest/output selection differs')
 if any(manifest['tts'].get(k)!=v for k,v in prov['identity']['tts'].items()):raise RuntimeError('Pending speech profile differs')
 for key in ['model','reference','referenceText']:
  if manifest['tts'].get(key)!=prov['manifest']['tts'][key]:raise RuntimeError('Pending approved model/reference differs')
 return attempt

def recover_pending(prov,out):
 pointer=out/'pending-launch.json'
 if not pointer.is_file():return
 pending=read(pointer)
 if pending.get('fingerprint')!=prov['fingerprint'] or pending.get('identity')!=prov['identity']:raise RuntimeError('Pending launch identity differs')
 if not pending.get('child'):raise RuntimeError('Unverifiable launch gap; preserve pending request and inspect before duplicate')
 if alive(pending['child']) or project_children(prov['slug']):raise ResourceWait('Existing selected Qwen child remains alive')
 for row in pending['requestPins']:
  if sha(row['path'])!=row['sha256']:raise RuntimeError('Pending request/helper changed')
 attempt=validate_launch_request(prov,out,pending)
 if pending.get('exitCode') not in (None,0) and not pending.get('preModelResourceDecline'):raise RuntimeError('Prior Qwen failure requires inspection; no automatic rerun')
 if not pending.get('preModelResourceDecline'):
  registered=register_scenes(prov,out,attempt)
  # A crash after selected chunks finished never requires another model load.
  if len(registered['scenes'])==len(scenes(prov)) and not (out/'voice-complete-proof.json').exists():
   try:_,engine=validate_engine_outputs(prov,out)
   except FileNotFoundError:
    if pending.get('exitCode')==0:raise RuntimeError('Successful engine lacks required outputs; preserve and inspect')
    engine=dict(incompleteEngineOutputsAtInterruption=True,exitCodeUnobserved=True,remainingSelectedRawChunksComplete=True,existingArtifacts=[dict(path=str(p),sha256=sha(p)) for p in [out/'narration.wav',out/'narration.timing.json',out/'narration.srt'] if p.is_file()])
   proof=canonical_outputs(prov,out,engine);proof['recovery']=dict(requestPath=str(attempt/'request.json'),observedEngineExitCode=pending.get('exitCode'),actualChildProvenDead=pending['child'],structuralRecoveryOnly=True)
   immutable_json(out/'voice-complete-proof.json',proof)
 resolved=attempt/'resolved-launch.json';immutable_json(resolved,pending);pointer.unlink()  # only own launch pointer, never GPU lease

def execute(args):
 ctx=configure(args.topic)
 if project_children(ctx['slug']):raise RuntimeError('Existing project Qwen child must finish; existing records preserved')
 if ctx['state'].exists():
  old=read(ctx['state'])
  if old.get('protocol')!=PROTOCOL or old.get('owner')!=ctx['owner'] or alive(old) or alive(old.get('child')):raise RuntimeError('Existing live/unknown selected voice state preserved')
 worker=runtime.SingleWorker(ctx['worker'],is_alive=alive).acquire();worker.update(**identity(),topicId=args.topic,stage='voice')
 child=None;log_handle=None;state=dict(protocol=PROTOCOL,owner=ctx['owner'],token=worker.record['token'],**identity(),child=None,status='waiting-for-preparation',completed=False,engineLaunched=False,externalGpuLeaseAcquired=False,engineOwnsGpuLease=True)
 if ctx['state'].exists():immutable(ctx['history']/(sha(ctx['state'])+'.progress.json'),ctx['state'].read_bytes())
 save(ctx['state'],state);deadline=time.monotonic()+args.wait_hours*3600
 try:
  while True:
   try:
    if time.monotonic()>=deadline:raise RuntimeError('Finite voice wait ended; preserve other jobs/apps')
    prov=prepared(args)
    if project_children(ctx['slug']):raise ResourceWait('Existing project Qwen child is running')
    out=output_of(prov)
    if out.exists() and any(out.iterdir()):
     validate_receipt(prov,out);recover_pending(prov,out)
     failure=out/'failed-launch.json'
     if failure.exists():raise RuntimeError('Previous non-resource synthesis failure is preserved; inspect before retry')
     proof=verify_complete(prov,out)
     if proof:
      publish_proof(ctx,prov,proof);state.update(status=proof['status'],completed=True,reusedCompleteVoice=True,fingerprint=prov['fingerprint'],output=str(out),evidence=str(ctx['evidence']));break
    else:out=initialize_output(prov)
    progress(prov,out)
    reason=busy_reason()
    if reason:raise ResourceWait(reason)
    current=prepared(args)
    if current['fingerprint']!=prov['fingerprint']:continue
    prov=current
    prep.immutable_stage(prov)
    if project_children(ctx['slug']):raise ResourceWait('Project Qwen child appeared before launch')
    reason=busy_reason()
    if reason:raise ResourceWait(reason)
    attempt=out/'engine-attempts'/(time.strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:8]);attempt.mkdir(parents=True)
    preserve_engine_files(out,attempt);before=audio_inventory(out);command=prov['qwenSynthesisArgv']
    request=dict(protocol=PROTOCOL,fingerprint=prov['fingerprint'],identity=prov['identity'],command=command,preparationFingerprint=prov['preparationFingerprint'],inputs=prov['inputs'],beforeAudio=before)
    immutable_json(attempt/'request.json',request)
    immutable(attempt/'controller-source.py',Path(__file__).read_bytes())
    pins=[dict(path=str(attempt/'request.json'),sha256=sha(attempt/'request.json'))]+[dict(path=str(ROOT/prov['manifest']['paths']['script']),sha256=sha(ROOT/prov['manifest']['paths']['script'])),dict(path=str(Path(prov['stagingDirectory'])/'voice-manifest.json'),sha256=sha(Path(prov['stagingDirectory'])/'voice-manifest.json')),dict(path=str(attempt/'controller-source.py'),sha256=sha(attempt/'controller-source.py'))]
    pending=dict(protocol=PROTOCOL,fingerprint=prov['fingerprint'],identity=prov['identity'],attempt=str(attempt),requestPins=pins,child=None,phase='launching',exitCode=None)
    save(out/'pending-launch.json',pending);worker.update(phase='launching',launchIntent=request,child=None)
    log_path=attempt/'engine.log';log_handle=log_path.open('ab')
    child=subprocess.Popen(command,cwd=ROOT,stdout=log_handle,stderr=subprocess.STDOUT,creationflags=CREATE)
    child_id=identity(child.pid);pending.update(child=child_id,phase='running');save(out/'pending-launch.json',pending);worker.update(child=child_id,phase='running')
    state.update(status='engine-running',child=child_id,engineLaunched=True,fingerprint=prov['fingerprint'],preparationFingerprint=prov['preparationFingerprint'],output=str(out),log=str(log_path));save(ctx['state'],state)
    while child.poll() is None:
     if time.monotonic()>=deadline:raise ResourceWait('Finite wrapper wait ended with its Qwen child still alive; preserve child and worker record')
     time.sleep(5)
    code=child.returncode;log_handle.close();log_handle=None;after=audio_inventory(out);declined=premodel_decline(code,log_path,before,after)
    pending.update(exitCode=code,phase='exited',preModelResourceDecline=declined,log=dict(path=str(log_path),sha256=sha(log_path)));save(out/'pending-launch.json',pending)
    state.update(engineExitCode=code,child=None,documentedPreModelResourceDecline=declined);worker.update(child=None,phase='exited')
    if code:
     if declined:
      recover_pending(prov,out);child=None;raise ResourceWait('Trusted engine declined before model load; wait without modifying foreign GPU work')
     register_scenes(prov,out,attempt);immutable_json(out/'failed-launch.json',pending);raise RuntimeError('Qwen returned nonzero; selected raw chunks/log/attempt preserved, no success or automatic retry')
    register_scenes(prov,out,attempt)
    try:
     chunks,engine=validate_engine_outputs(prov,out);proof=canonical_outputs(prov,out,engine)
     after_prov=prepared(args)
    except (OSError,ValueError,KeyError,prep.Pending) as error:raise RuntimeError('Post-synthesis verification failed; preserve outputs without automatic model retry: '+str(error)) from error
    if after_prov['fingerprint']!=prov['fingerprint']:raise RuntimeError('Synthesis inputs changed during generation; preserve generated PCM without adopting it for the new version')
    immutable_json(out/'voice-complete-proof.json',proof);recover_pending(prov,out);publish_proof(ctx,prov,proof)
    state.update(status=proof['status'],completed=True,child=None,evidence=str(ctx['evidence']),canonicalWav=proof['aggregateWav'],independentAsrVerified=False,actualListening=False,humanApproval=False);break
   except (prep.Pending,ResourceWait) as error:
    live=bool(child and child.poll() is None)
    state.update(status='waiting-for-preparation-or-resources' if not live else 'yielded-child-still-alive',reason=str(error),checkedAt=time.time());save(ctx['state'],state)
    if live or time.monotonic()>=deadline:break
    time.sleep(10)
 except BaseException as error:
  state.update(status='failed-preserved',error=repr(error),completed=False,checkedAt=time.time());save(ctx['state'],state);raise
 finally:
  live=bool(child and child.poll() is None) or alive(state.get('child')) or bool(project_children(ctx['slug']))
  state.update(childStillAlive=live,finishedOrYieldedAt=time.time())
  if live:state['status']='yielded-child-still-alive'
  save(ctx['state'],state)
  if log_handle:log_handle.close()
  worker.close(remove=not live)
 print(json.dumps(dict(status=state['status'],completed=state['completed'],state=str(ctx['state']),engineOwnsGpuLease=True,independentAsrVerified=False,actualListening=False),ensure_ascii=False))

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--topic',default='07.04');parser.add_argument('--execute',action='store_true');parser.add_argument('--wait-hours',type=float,default=6);parser.add_argument('--native-evidence');parser.add_argument('--native-qa');parser.add_argument('--semantic-components');args=parser.parse_args()
 if not math.isfinite(args.wait_hours) or not 0<args.wait_hours<=6:raise ValueError('Finite wait must be above0 and at most6hours')
 if not args.execute:
  try:
   prov=prepared(args);ctx=configure(args.topic);out=output_of(prov);reuse=verify_complete(prov,out) if out.exists() and (out/'voice-complete-proof.json').exists() else None
   reason=busy_reason()
   print(json.dumps(dict(ready=True,resourceReady=reason is None,resourceWaitReason=reason,topicId=args.topic,fingerprint=prov['fingerprint'],sceneCount=len(scenes(prov)),paragraphCount=len({r['paragraph'] for r in prov['paragraphMapping']}),existingCompleteVoice=bool(reuse),existingProjectChildren=project_children(ctx['slug']),state=str(ctx['state']),staged=False,modelStarted=False),ensure_ascii=False))
  except (prep.Pending,FileNotFoundError) as error:print(json.dumps(dict(ready=False,reason=str(error),staged=False,modelStarted=False),ensure_ascii=False))
  return
 execute(args)

if __name__=='__main__':main()
