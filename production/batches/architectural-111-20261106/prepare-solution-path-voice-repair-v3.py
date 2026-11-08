"""11.05 V3 three-complete-sentence candidate; read-only, no stage/model.

Current6691 is immutable history. All48 sentences/NarV5/profile stayexact;
45currentrawtakes are retained andonly3numericdecline targets are redrawn.
"""
from __future__ import annotations
import argparse, copy, hashlib, importlib.util, json, math, sys, types, wave
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
if str(HERE)not in sys.path:sys.path.insert(0,str(HERE))
PROJECT=ROOT/'projects/shorts-leveldesign-11-05';TOPIC='11.05'
PLAN=PROJECT/'voice-subset-repair-plan-v3.json';PLAN_SHA='3a2b6890f4607c17249b6f5c08004334fad2f908a37bc0d33bb9c9fa7d590fca'
NARRATION=PROJECT/'narration-final-v5.json';NARRATION_SHA='e3179da81b2a23135eb6a8907ebb6205c14fc2d66e528a37372d491d0ffeaa91'
OLD_FP='6691614beecda682a8130136a3dfd952b472e7acdba769a83cd1ca7212df8cc1'
OLD_NAR_SHA=NARRATION_SHA
TARGETS=('p008-c01','p008-c02','p013-c01')
PROTOCOL='architectural111-11-05-voice-subset-repair-v3'
ADAPTER=HERE/'run-solution-path-voice-repair-v3.py'
PINS={'prepare-solution-path-voice-repair-v2.py':'11377373c0a2d7624216f60e0219beed7601e2ec423bb9df7cf8aa88bcba95db','run-solution-path-voice-repair-v2.py':'06825b9fbfd213b6a1a0dcfdf73ece0e3d46ca2624a6f8a5c3bbe182c37086a1','run-solution-path-voice-qa-v6.py':'59618eb71570190ec78cbae98f94b15078cfd852d3325aab7ac10531400d727e','prepare-solution-path-voice-repair-v1.py':'97e3e87ee7e95a06e7b0837b8bb7214c5fbf50b506124981ade184b1ad6339de','run-solution-path-voice-repair-v1.py':'9b12d46bcbb893619331418119b01cf342ab7f40ba3e95d1ad0ee95061f73660','run-solution-path-voice-v4.py':'f94852008cc919308b995866ac35510163f3eabd72de45066d6c5d0f60807910',
 'prepare-solution-path-voice-v4.py':'840889c38734f6a01511511bcfcdd1c123402fd387b2f6bda59e484555268292',
 'run-selected-voice.py':'55ec247dafdef34bf2f31e9054e5a9fd3629ea2f220847b19694c48b59e26a99',
 'run-selected-voice-repair-v4.py':'c70ba7ff185f048bbb53c3b7845b5af2237d14de1ea3ef511e9afacdf8171366',
 'run-solution-path-voice-qa-v5.py':'1e03fc9b071e2542c662e2d27c6a8a5bcff65402c9e769d56dcf9d0bc7c7437c'}
RUNTIME_PINS=[dict(path=str(ROOT/'qwen3-tts/.venv/Scripts/python.exe'),sha256='cac98e94324b5462d41a5c6ad1847b57508a1068ba56014cf67a3d33a493dcdf'),dict(path=str(ROOT/'qwen3-tts/.venv/pyvenv.cfg'),sha256='2a28384eeef94485ae21f13ab5721d9dbe14d0736111b0ea2cc05212ea19c5e4'),dict(path='C:/Anaconda3/envs/pytorch-gpu/python.exe',sha256='124cbe6203f939ff138c0ce68e26c12e4ca5836562286572ed040173daf0b787')]
SELF_SHA=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
class Pending(RuntimeError):pass
def need(ok,reason):
 if not ok:raise Pending(reason)
def read(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def sha(path):
 with Path(path).open('rb')as h:return hashlib.file_digest(h,'sha256').hexdigest()
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
def pin(path):return dict(path=str(Path(path).resolve()),sha256=sha(path))
def checked(row,role):
 need(isinstance(row,dict)and isinstance(row.get('path'),str)and isinstance(row.get('sha256'),str),'Missing pinned '+role)
 need(Path(row['path']).is_file()and pin(row['path'])=={k:row[k]for k in('path','sha256')},'Changed pinned '+role)
 return dict(path=str(Path(row['path']).resolve()),sha256=row['sha256'])
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def check_sources():
 need(sha(__file__)==SELF_SHA,'Repair preparer changed after import')
 for name,expected in PINS.items():need(sha(HERE/name)==expected,'Reviewed repair dependency changed: '+name)
 for row in RUNTIME_PINS:need(sha(row['path'])==row['sha256'],'Reviewed launcher/runtime changed: '+row['path'])
check_sources()
voice_entry=module('solution_repair_v3_current_voice',HERE/'run-solution-path-voice-v4.py')
prep=voice_entry.prep;base=voice_entry.base

def load_plan(path=PLAN):
 path=Path(path).resolve();need(path==PLAN.resolve()and path.is_file()and sha(path)==PLAN_SHA,'Frozen V3 three-take plan missing/changed')
 plan=read(path);need(plan.get('schemaVersion')=='11.05-voice-subset-repair-plan-v3'and plan.get('topicId')==TOPIC,'Wrong repair scope')
 need((plan.get('canonicalSceneCount'),plan.get('paragraphCount'),plan.get('exactReuseCount'),plan.get('newSynthesisCount'))==(48,14,45,3),'Exact48/14/45/3 repair scope required')
 need(plan.get('profileReferenceEngineUnchanged')is True and plan.get('canonicalTextChanged')is False and plan.get('changedCanonicalSceneIds')==[] and [r['sceneId']for r in plan['replacementScenes']]==list(TARGETS),'Exact unchanged-text three targets required')
 need(plan['newNarration']==plan['oldNarration']==pin(NARRATION)and plan['sourceNarrationSHA256']==NARRATION_SHA==sha(NARRATION),'Both operative and source narration must be exact NarV5')
 checked(plan['protectedProjectCheckpoint'],'protected current project checkpoint')
 need(Path(plan['protectedProjectCheckpoint']['path']).resolve()==PROJECT/'checkpoint.json'and plan['protectedProjectCheckpoint']['sha256']=='7123b2dffc7203700a296b2ceac45c23b3dece912d0da6887f3ee09e8a2512bb','Frozen project input checkpoint changed')
 for name in ('prepare-solution-path-voice-repair-v2.py','run-solution-path-voice-repair-v2.py','run-solution-path-voice-qa-v6.py'):
  need(checked(plan['priorRepairSources'][name],'prior repair source')==pin(HERE/name)and plan['priorRepairSources'][name]['sha256']==PINS[name],'Prior6691 source pins differ')
 need(plan['oldVoiceFingerprint']==OLD_FP and plan['oldRepairFingerprint']=='10b7ed1345e8075db6d4f0ee9bf706d52951f2a163fbd60c9d7d278b4d6a839a','Only current6691/10b7 origin supported')
 policy=plan['policy'];need(all(policy.get(k)is False for k in('trimOrTimeStretch','dynamicGainCompression','rawOrHistoricalEvidenceOverwrite','lowerResourceGate','actualListening','automaticSpeechPass','humanApproval','sourceTextChange','normalizationOnlyAcceptance')),'Repair cannot waive PCM/resource/review boundaries')
 draw=plan['randomDraw'];need(draw.get('newBoundedCandidate')is True and draw.get('existingEngineMaxAttemptsUnchanged')is True and all(draw.get(k)is False for k in('seedParameterAdded','instructChanged','profileParameterChanged','successPromised')),'Only same-profile bounded draw is allowed')
 return plan

def sentence_delta(old_draft,new_draft,old_scenes,new_scenes):
 need(len(old_draft['narrationKo'])==len(new_draft['narrationKo'])==len(old_draft['paragraphsEn'])==len(new_draft['paragraphsEn'])==14,'Exact14 bilingual paragraphs required')
 need(old_draft['narrationKo']==new_draft['narrationKo']and old_draft['paragraphsEn']==new_draft['paragraphsEn'],'V3 cannot change any KO/EN paragraph')
 need(len(old_scenes)==len(new_scenes)==48 and old_scenes==new_scenes,'All48 complete sentence IDs/order/text must remain exact')

def prior_tools():
 return module('solution_repair_v3_immutable_prior_qa6',HERE/'run-solution-path-voice-qa-v6.py')

def verify_prior_origin(plan,old,out):
 # The source itself is a prior six-only repair. Validate with its FULL V2
 # context, including repair-inputs and the real6engine artifacts/fourpins.
 qa=prior_tools();prov=qa.prepared_repair()
 need(prov['fingerprint']==OLD_FP and prov['identity']==old['identity'],'Prior V2 full identity differs')
 need(qa.voice_worker.life.verify_complete(prov,out)==old,'Prior full48 repaired proof differs')
 receipt=qa.voice_worker.life.validate_receipt(prov,out)
 need(plan['oldNarration']in receipt['inputs'],'Prior input receipt lacks NarV5')
 need(checked(plan['oldVoiceInputs'],'prior immutable voice inputs')==pin(Path(out)/'voice-inputs.json')and checked(plan['oldRepairInputs'],'prior immutable repair inputs')==pin(Path(out)/'repair-inputs.json'),'Prior immutable input receipt paths differ')
 engine=qa.verify_subset_engine(prov,Path(out),old)
 need(engine['engineSceneCount']==6 and engine['fullCanonicalSceneCount']==48 and len(engine['reusedSceneIds'])==42,'Prior origin must truthfully preserve6engine+42reuse')
 return dict(priorVoiceInputs=pin(Path(out)/'voice-inputs.json'),priorRepairInputs=pin(Path(out)/'repair-inputs.json'))

def verify_old_review(plan,old):
 """Existing current0fe/cache95 only; never restore/write/recognize/use mutableC."""
 qa=prior_tools();ap=checked(plan['rawAsrReview'],'current ASR');lp=checked(plan['rawLevelReview'],'current levels');peerpin=checked(plan['contentPeerReview'],'current content peer');review=read(ap['path']);levels=read(lp['path']);peer=read(peerpin['path'])
 path=Path(ap['path']);job=read(path.parent/'job.json')
 need(checked(plan['rawAsrJob'],'actual current raw job')==pin(path.parent/'job.json')and path.name=='review.json'and path.parent==Path(job['output']).resolve()and job.get('protocol')==qa.PROTOCOL and digest(job['identity'])==job['fingerprint']==review['fingerprint'],'Current exact ASR job identity differs')
 need(job['identity']['voiceFingerprint']==OLD_FP and job['identity']['sourceNarration']==plan['oldNarration']and job['voiceEvidence']==plan['oldVoiceEvidence'],'Current ASR source/immutable6691 binding differs')
 need(job['identity']['profile']==qa.PROFILE and job['identity']['modelPins']==qa.qa.APPROVED['modelPins']and job['identity']['trustedUtilitySHA256']==qa.qa.APPROVED['trustedSHA256'],'Current independent recognizer differs')
 for row in job['sourcePins']:checked(row,'current ASR source')
 need(sha(path.parent/'adapter-source.py')==job['identity']['adapterSHA256']==PINS['run-solution-path-voice-qa-v6.py'],'Current ASR snapshot differs')
 need(job['identity']['tasks']==qa.qa.build_tasks(old,read(old['timing']['path']))and len(job['identity']['tasks'])==95,'Current48/47 PCM windows differ')
 need(all(qa.cached(job,t)is not None for t in job['identity']['tasks']),'Current ASR cache incomplete')
 def existing(destination,value):need(Path(destination).resolve()==path.resolve()and value==review,'Current ASR summary differs from exact caches')
 fn=qa.summary;scope=dict(fn.__globals__,voice=types.SimpleNamespace(immutable_json=existing));rebuilt=types.FunctionType(fn.__code__,scope,'verify_current_summary_without_write')(job)
 need(rebuilt==review and review['voiceFingerprint']==OLD_FP and review['aggregateSHA256']==old['aggregateWav']['sha256']and review['timingSHA256']==old['timing']['sha256']and len(review['takes'])==48 and len(review['boundaryWindows'])==47 and len(review['paragraphs'])==14,'Current full ASR review differs')
 need(review['aliasesApplied']is False and review['expectedPrompt']is None and review['humanListening']is False and review['automaticSpeechPass']is False,'Raw differences cannot be waived')
 need(levels['voiceFingerprint']==OLD_FP and levels['canonicalWav']==old['aggregateWav']and levels['asrReview']==ap and len(levels['takes'])==48 and len(levels['paragraphs'])==14 and len(levels['joins'])==47,'Current numerical proof differs')
 need([r['sceneId']for r in levels['takes']]==[s['id']for s in old['identity']['scenes']]and [r['paragraph']for r in levels['paragraphs']]==list(range(1,15)),'Current numerical order differs')
 for observed,wanted in zip(levels['joins'],review['boundaryObservations']):need(all(observed[k]==wanted[k]for k in('previousScene','nextScene','joinType','boundarySample')),'Numerical join/sample order differs')
 checked(levels['levelPrimitive'],'current level primitive');need(levels['levelPrimitive']['sha256']==qa.qa.APPROVED['firstLevelPrimitiveSHA256'],'Numerical primitive differs')
 need(all(f.get('sceneId')in TARGETS for f in levels['flags']if f.get('kind')=='sustained-take-word-body-decline'),'A formally declining take cannot enter45 reuse')
 need(peer.get('schemaVersion')=='11.05-voice-asr-content-peer-review-v6'and peer.get('identity',{}).get('voiceFingerprint')==OLD_FP and checked(peer['inputs']['immutableVoiceProof'],'peer immutable voice')==plan['oldVoiceEvidence']and checked(peer['inputs']['review'],'peer raw ASR')==ap and checked(peer['inputs']['rawNumericalLevelReview'],'peer raw levels')==lp,'Content peer belongs to another voice/review')
 need(peer['numericalContext']['technicalScalarPreparationAllowed']is False and [r['sceneId']for r in peer['numericalContext']['neededHolds']]==['p013-c01','p008-c01','p008-c02']and all(peer['limits'].get(k)is False for k in('actualListening','humanApproval','automaticSpeechPass')),'All three numerical holds and no-hearing limits must remain explicit')
 for target in plan['replacementScenes']:
  need(target['numericalTrend']==next(r['wordTrend']for r in levels['takes']if r['sceneId']==target['sceneId']),'Target numerical observation changed')
 return dict(rawAsrReview=ap,rawLevelReview=lp,contentPeerReview=peerpin,rawAsrJob=pin(path.parent/'job.json'),rawAsrAdapter=pin(path.parent/'adapter-source.py'))

def validate_reuse(full,plan):
 oldpin=checked(plan['oldVoiceEvidence'],'immutable prior voice');old=read(oldpin['path']);expected=(ROOT/'shared/output/architectural-111-20261106/11-05/voice-attempts'/OLD_FP[:24]/'voice-complete-proof.json').resolve()
 need(Path(oldpin['path'])==expected and old['topicId']==TOPIC and old['fingerprint']==plan['oldVoiceFingerprint']==OLD_FP and digest(old['identity'])==OLD_FP,'Old immutable proof identity/path differs')
 prior_receipts=verify_prior_origin(plan,old,expected.parent)
 need({k:v for k,v in old['identity'].items()if k!='repairSelection'}=={k:v for k,v in full['identity'].items()if k!='repairSelection'},'Only prior repairSelection may differ; all text/profile/model/ref/engine/guard/raw policy remain exact')
 old_scenes=old['identity']['scenes'];new_scenes=full['identity']['scenes'];sentence_delta(read(plan['oldNarration']['path']),read(plan['newNarration']['path']),old_scenes,new_scenes)
 old_script,old_mapping=prep.sentence_plan(read(plan['oldNarration']['path']),OLD_NAR_SHA)
 need(old_scenes==[dict(id=s['id'],lines=s['lines'])for s in old_script['scenes']]and old['paragraphMapping']==old_mapping,'Old source paragraph mapping differs')
 timing=read(old['timing']['path']);position=0;pcm=hashlib.sha256()
 need(timing['sample_rate']==24000 and len(timing['entries'])==48,'Old raw timing format/count differs')
 for scene,row,entry in zip(old_scenes,old['sceneWavs'],timing['entries']):
  need(entry['scene_id']==scene['id']and entry['text']==scene['lines'][0]and all(type(entry[k])in(int,float)and math.isfinite(entry[k])and abs(entry[k]-v)<1e-9 for k,v in(('start',position/24000),('end',(position+row['frames'])/24000))),'Old raw sample clock differs')
  with wave.open(row['path'],'rb')as source:pcm.update(source.readframes(source.getnframes()))
  position+=row['frames']
 need(position==old['aggregateWav']['frames']and pcm.hexdigest()==old['aggregateWav']['pcmSHA256'],'Old canonical is not exact raw concatenation')
 oldmap={s['id']:(s,w)for s,w in zip(old_scenes,old['sceneWavs'])};safe=[s['id']for s in new_scenes if s['id']not in TARGETS]
 need(len(oldmap)==48 and [r['oldSceneId']for r in plan['subsetReuse']]==[r['newSceneId']for r in plan['subsetReuse']]==safe,'Exact45 ordered current6691 raw reuses required')
 rows=[]
 for row in plan['subsetReuse']:
  sid=row['oldSceneId'];scene,wav=oldmap[sid];actual=base.wav_info(checked(row['sourceWav'],'retained raw')['path'])
  need(actual==wav==row['sourceWav']and Path(actual['path']).resolve()==expected.parent/'chunks'/(sid+'-scene.wav'),'Reuse raw WAV/PCM/header/source path differs')
  need(scene['lines']==[row['canonicalText']]==next(s for s in new_scenes if s['id']==sid)['lines']and bool(row.get('reuseReason')),'Retained complete sentence differs')
  need(checked(row['sourceVoiceEvidence'],'row source voice')==oldpin and row['sourceVoiceEvidence']['fingerprint']==OLD_FP,'Reuse row immutable voice differs');rows.append(copy.deepcopy(row))
 for row in plan['replacementScenes']:
  sid=row['sceneId'];scene,wav=oldmap[sid];need(row['oldCanonicalText']==scene['lines'][0]and row['canonicalText']==next(s for s in new_scenes if s['id']==sid)['lines'][0]and row['previousSelectedRaw']==wav and bool(row['reason']),'Selected replacement source/text differs')
 return rows,oldpin,dict(verify_old_review(plan,old),**prior_receipts)

def reselect(full,plan,plan_path,adapter):
 rows,oldpin,reviews=validate_reuse(full,plan);selection=dict(protocol=PROTOCOL,plan=pin(plan_path),sourceVoiceEvidence=oldpin,sourceVoiceFingerprint=OLD_FP,newNarration=plan['newNarration'],repairSceneIds=list(TARGETS),expectedFullCount=48,expectedNewCount=3,expectedByteReusedCount=45,adapterSHA256=adapter['sha256'],preparerSHA256=SELF_SHA,baseControllerSHA256=PINS['run-selected-voice.py'],launcherRuntimePins=copy.deepcopy(RUNTIME_PINS),launcherClassification='exact-direct-venv-execute-wrapper-v3')
 identity=dict(full['identity'],repairSelection=selection);fp=digest(identity);need(fp!=OLD_FP,'New repair output must not collide with old voice')
 inputs=full['inputs']+[pin(plan_path),oldpin,adapter,pin(__file__)]+copy.deepcopy(RUNTIME_PINS)+[pin(HERE/name)for name in PINS]+list(reviews.values())+[dict(path=r['sourceWav']['path'],sha256=r['sourceWav']['sha256'])for r in rows]
 inputs=list({r['path']:{k:r[k]for k in('path','sha256')}for r in inputs}.values());preparation=digest(dict(synthesisIdentity=fp,inputs=inputs,script=full['script'],paragraphMapping=full['paragraphMapping']))
 folder=PROJECT/'production/voice-preparation'/preparation[:24];out=ROOT/'shared/output/architectural-111-20261106/11-05/voice-attempts'/fp[:24]
 manifest=copy.deepcopy(full['manifest']);manifest['paths']['script']=(folder/'narration-qwen.json').relative_to(ROOT).as_posix();manifest['tts']['outputDir']=out.relative_to(ROOT).as_posix();manifest['synthesisIdentity']=fp;manifest['repairSelection']=selection
 command=list(full['qwenSynthesisArgv']);command[8]=(folder/'voice-manifest.json').relative_to(ROOT).as_posix()
 selected=dict(full,identity=identity,fingerprint=fp,preparationFingerprint=preparation,inputs=inputs,stagingDirectory=str(folder),voiceOutputDirectory=str(out),manifest=manifest,qwenSynthesisArgv=command,qwenDryRunArgv=command+['--dry-run'])
 missing=[s for s in identity['scenes']if s['id']in TARGETS];need([s['id']for s in missing]==list(TARGETS),'Engine must receive only exact3 replacements')
 ri=dict(protocol=PROTOCOL,fullVoiceFingerprint=fp,repairSelection=selection,oldVoiceEvidence=dict(oldpin,fingerprint=OLD_FP),previousReviewPins=reviews,reuse=rows,missingScenes=missing,plan=pin(plan_path),adapterSHA256=adapter['sha256'],baseWorkerSHA256=PINS['run-selected-voice.py'],lifecycleSource=pin(HERE/'run-selected-voice-repair-v4.py'))
 rfp=digest(ri);rfolder=folder/('repair-subset-'+rfp[:24]);script=copy.deepcopy(full['script']);script['scenes']=[s for s in script['scenes']if s['id']in TARGETS]
 rm=copy.deepcopy(manifest);rm['paths']['script']=(rfolder/'narration-missing-only.json').relative_to(ROOT).as_posix();rm.update(engineSceneScope='missing-subset-only',fullSynthesisIdentity=fp,repairFingerprint=rfp,engineSceneIds=list(TARGETS));cmd=list(command);cmd[8]=(rfolder/'voice-missing-only-manifest.json').relative_to(ROOT).as_posix()
 repair=dict(fingerprint=rfp,identity=ri,rows=rows,missing=missing,stagingDirectory=str(rfolder),script=script,manifest=rm,command=cmd)
 return dict(selected,_basePrepared=selected,repair=repair,qwenSynthesisArgv=cmd,qwenDryRunArgv=cmd+['--dry-run'])

def prepare(plan_path=PLAN,native_evidence=None,native_qa=None,narration=None):
 check_sources();plan=load_plan(plan_path);need(Path(narration or NARRATION).resolve()==NARRATION.resolve(),'Only frozen new final narration supported')
 try:full=prep.prepare(topic=TOPIC,native_path=native_evidence,native_qa_path=native_qa,component_path=None,narration=NARRATION)
 except prep.Pending as error:raise Pending(str(error))from error
 adapter=pin(ADAPTER);result=reselect(full,plan,Path(plan_path).resolve(),adapter);check_sources();need(pin(ADAPTER)==adapter,'Repair entry source changed during preparation');return result

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repair-plan',default=str(PLAN));p.add_argument('--native-evidence');p.add_argument('--native-qa');p.add_argument('--narration');a=p.parse_args()
 try:
  v=prepare(a.repair_plan,a.native_evidence,a.native_qa,a.narration);print(json.dumps(dict(ready=True,fullVoiceFingerprint=v['fingerprint'],repairFingerprint=v['repair']['fingerprint'],fullSceneCount=48,reuseCount=45,missingOnlyCount=3,output=v['voiceOutputDirectory'],staged=False,reuseCopied=False,modelLoaded=False)))
 except(Pending,FileNotFoundError)as e:print(json.dumps(dict(ready=False,reason=str(e),staged=False,reuseCopied=False,modelLoaded=False)))
if __name__=='__main__':main()
