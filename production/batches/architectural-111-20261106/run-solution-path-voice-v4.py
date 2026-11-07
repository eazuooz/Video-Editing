"""Thin finite11.05 voice entry; current provisional preflight never queues work.

The pinned selected-voice core retains PCM/recovery/launch/singleton functions.
Only actual --execute with ready inputs may invoke it. Qwen alone owns its lease.
"""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,math,sys,time,uuid
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];TOPIC='11.05'
BASE=Path('C:/Users/1/Videos/YamyamProduction/architectural-111-20261106/shorts-leveldesign-11-05')
PINS={
 'run-selected-voice.py':'55ec247dafdef34bf2f31e9054e5a9fd3629ea2f220847b19694c48b59e26a99',
 'prepare-solution-path-voice-v4.py':'840889c38734f6a01511511bcfcdd1c123402fd387b2f6bda59e484555268292',
 'prepare-selected-voice.py':'7fc1afac8b7c44b7752f0b53620150cd0989238cc4cc5866a14f40480034a020',
 'approved-selected-voice-profile-v1.json':'378e12edc96c5d006ca9407ed36da13d1eff7e882cdc2670acdfd749b15b0075',
 'run-solution-path-native-v4.py':'9429b70773f3a334dd5fd45d76ecb6b2fa8b2360dfe576aac341099d7adaea5e',
 'prepare-solution-path-unity-v4.py':'74b9c7231f1a98b440d5aaee33a8de367436941e2c353730103f4aae56b8ffe0',
 'prospect-refuge-resource-qualification.py':'2dbb128a891fabf9c440e5790b88481c7901fbf087098557c540b19b8ecd5f5d',
 'run-first-native.py':'a38205dac134e58da35a772290f0a151c7377b115b89910585277de76983a1f9',
 'run-zen-view-native.py':'64ebe5e6c2c44ef9e461e3ae82c875637ea1ba6be63fdceb049e105274154943',
 'initialize.py':'3968ca6abe9c8c4c35f67b55427dfaec8bd083af0bac1c30d85b674a383df179'}
def sha(p):
 with Path(p).open('rb')as h:return hashlib.file_digest(h,'sha256').hexdigest()
SELF_SHA=sha(__file__)
def check_sources():
 if sha(__file__)!=SELF_SHA:raise RuntimeError('Voice wrapper changed after import')
 for name,expected in PINS.items():
  if sha(HERE/name)!=expected:raise RuntimeError('Reviewed voice source changed: '+name)
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
check_sources()
base=module('solution_voice_v4_private_base',HERE/'run-selected-voice.py')
prep=module('solution_voice_v4_preparer',HERE/'prepare-solution-path-voice-v4.py')
resource=module('solution_voice_v4_native_resource',HERE/'run-solution-path-native-v4.py')
original_configure=base.configure
COMMON_NAMES=['wav_info','initialize_output','progress','register_scenes','canonical_outputs','verify_complete','validate_launch_request','recover_pending','execute','alive','project_children']
COMMON_FUNCTIONS={name:getattr(base,name)for name in COMMON_NAMES}
def configure(topic):
 check_sources()
 if topic!=TOPIC:raise ValueError('Only current11.05 voice is scoped')
 return original_configure(topic)
def prepared(args):
 check_sources()
 if args.topic!=TOPIC:raise ValueError('Only current11.05 voice is scoped')
 return prep.prepare(topic=TOPIC,native_path=args.native_evidence,native_qa_path=args.native_qa,component_path=getattr(args,'semantic_components',None),narration=getattr(args,'narration',None))
def audited_native_busy():
 check_sources()
 return resource.busy_reason()  # Read-only resource/lease inspection, never native acquire/recover.
base.prep=prep;base.prepared=prepared;base.configure=configure
base.zen.busy_reason=audited_native_busy  # Keep original voice busy_reason's extra >=15% gate.
def finite_wait(hours):
 if not math.isfinite(hours)or not 0<hours<=6:raise ValueError('Finite wait must be above0 and at most6hours')
def invocation(prov,args):
 check_sources()
 if prov.get('ready')is not True or prov.get('voiceReady')is not True:raise prep.Pending('Only actual ready voice inputs may create an invocation')
 identity=base.identity()
 if not any(str(Path(x).resolve())==str(Path(__file__).resolve())for x in identity['argv']if isinstance(x,str)):
  raise RuntimeError('Invocation argv must identify this exact voice wrapper')
 folder=BASE/'voice-controller-invocations'/prov['fingerprint'][:24]/(time.strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:10])
 folder.mkdir(parents=True,exist_ok=False);snapshots=[]
 sources=[('adapter',Path(__file__))]+[(name.removesuffix('.py').removesuffix('.json'),HERE/name)for name in PINS]
 for i,(role,path)in enumerate(sources):
  data=path.read_bytes();value=hashlib.sha256(data).hexdigest();expected=SELF_SHA if path.resolve()==Path(__file__).resolve()else PINS[path.name]
  if value!=expected:raise RuntimeError('Invocation source changed before snapshot: '+str(path))
  target=folder/'source-snapshots'/f'{i:02}.bin';base.immutable(target,data);snapshots.append(dict(role=role,source=dict(path=str(path.resolve()),sha256=value),snapshot=dict(path=str(target),sha256=sha(target))))
 check_sources()
 record=dict(schemaVersion='11-05-voice-controller-invocation-v4',topicId=TOPIC,createdAt=time.time(),wrapperProcess=identity,synthesisIdentity=prov['identity'],fingerprint=prov['fingerprint'],preparationFingerprint=prov['preparationFingerprint'],inputs=prov['inputs'],sources=snapshots,waitHours=args.wait_hours,engineOwnsGpuLease=True,wrapperGpuLeaseAcquired=False,actualSpeechListening=False,humanApproval=False)
 path=folder/'invocation.json';base.immutable_json(path,record);return path
def completion_observation(path,ctx,error):
 # This separate observation never rewrites the core proof or its ASR/review flags.
 state=base.read(ctx['state'])if ctx['state'].is_file()else None
 invocation_record=base.read(path);process=invocation_record['wrapperProcess'];selected=bool(state and state.get('protocol')==base.PROTOCOL and state.get('owner')==ctx['owner']and state.get('fingerprint')==invocation_record['fingerprint']and state.get('pid')==process['pid']and type(state.get('createTime'))in(int,float)and abs(state['createTime']-process['createTime'])<.01 and state.get('argv')==process['argv']and state.get('commandSHA256')==process['commandSHA256'])
 pins={name:dict(path=str(ctx[name]),sha256=sha(ctx[name]))for name in('state','evidence','worker')if ctx[name].is_file()}
 result=dict(schemaVersion='11-05-voice-controller-completion-observation-v4',topicId=TOPIC,observedAt=time.time(),invocation=dict(path=str(path),sha256=sha(path)),artifactsObserved=pins,currentStateMatchesInvocation=selected,completedObserved=bool(selected and state.get('completed')is True),statusObserved=state.get('status')if selected else None,error=repr(error)if error else None,callReturnedWithoutError=error is None,observationOnly=True,asrStatusNotReassessed=True,existingEvidenceReviewFlagsUnmodified=True,actualSpeechListening=False,humanApproval=False)
 base.immutable_json(path.parent/'completion-observation.json',result)
def execute(args):
 finite_wait(args.wait_hours);prov=prepared(args)  # Reject provisional input before worker/queue/GPU queries.
 if prov.get('ready')is not True or prov.get('voiceReady')is not True:raise prep.Pending('Actual selected inputs are not voice-ready')
 ctx=configure(args.topic);path=invocation(prov,args);error=None
 try:return base.execute(args)
 except BaseException as exc:error=exc;raise
 finally:completion_observation(path,ctx,error)
def main(argv=None):
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--topic',default=TOPIC);parser.add_argument('--execute',action='store_true');parser.add_argument('--wait-hours',type=float,default=6);parser.add_argument('--native-evidence');parser.add_argument('--native-qa');parser.add_argument('--narration');args=parser.parse_args(argv);args.semantic_components=None;finite_wait(args.wait_hours)
 try:
  if args.execute:execute(args);return
  prov=prepared(args)
  print(json.dumps(dict(topicId=TOPIC,ready=prov['ready'],voiceReady=prov['voiceReady'],fingerprint=prov['fingerprint'],preparationFingerprint=prov['preparationFingerprint'],sceneCount=len(prov['identity']['scenes']),paragraphCount=len({r['paragraph']for r in prov['paragraphMapping']}),readOnly=True,resourceChecked=False,staged=False,modelStarted=False,jobLaunched=False),ensure_ascii=False))
 except(prep.Pending,FileNotFoundError)as error:print(json.dumps(dict(topicId=TOPIC,ready=False,voiceReady=False,reason=str(error),staged=False,modelStarted=False,jobLaunched=False,resourceChecked=False),ensure_ascii=False))
if __name__=='__main__':main()
