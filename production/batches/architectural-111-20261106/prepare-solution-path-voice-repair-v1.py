"""11.05 six-complete-sentence repair preparation; read-only, no stage/model.

The frozen root plan retains42 exact raw takes. Only P013c01 changes canonical
text; five other replacements retain their complete approved sentences.
"""
from __future__ import annotations
import argparse, copy, hashlib, importlib.util, json, math, sys, types, wave
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
if str(HERE)not in sys.path:sys.path.insert(0,str(HERE))
PROJECT=ROOT/'projects/shorts-leveldesign-11-05';TOPIC='11.05'
PLAN=PROJECT/'voice-subset-repair-plan-v1.json';PLAN_SHA='6a1da172ce19a274c853454930ecee1cd8b4b8f9feab117c306f9d52c295a16e'
NARRATION=PROJECT/'narration-final-v5.json';NARRATION_SHA='e3179da81b2a23135eb6a8907ebb6205c14fc2d66e528a37372d491d0ffeaa91'
OLD_FP='e51bc0ed82c4bea1233f68409e62decdb98ca2b5e035e68e9a72a97f6266b772'
OLD_NAR_SHA='8a35438d9b12131a60a1ec817aaa11d2f4df21b59c2f645dfd69143a71d92a53'
TARGETS=('p005-c01','p005-c02','p005-c03','p008-c01','p008-c02','p013-c01')
NEW_P13='HD 화면에서도 보물을 든 캐릭터가 발판을 지나 출구 근처까지 내려오지만, 굴러오는 큰 바위에 부딪혀 쓰러지죠.'
NEW_P13_EN='In the HD footage, the character carrying treasure passes the ledges and descends near the exit, but is struck by a large rolling boulder.'
PROTOCOL='architectural111-11-05-voice-subset-repair-v1'
ADAPTER=HERE/'run-solution-path-voice-repair-v1.py'
PINS={'run-solution-path-voice-v4.py':'f94852008cc919308b995866ac35510163f3eabd72de45066d6c5d0f60807910',
 'prepare-solution-path-voice-v4.py':'840889c38734f6a01511511bcfcdd1c123402fd387b2f6bda59e484555268292',
 'run-selected-voice.py':'55ec247dafdef34bf2f31e9054e5a9fd3629ea2f220847b19694c48b59e26a99',
 'run-selected-voice-repair-v4.py':'c70ba7ff185f048bbb53c3b7845b5af2237d14de1ea3ef511e9afacdf8171366',
 'run-solution-path-voice-qa-v5.py':'1e03fc9b071e2542c662e2d27c6a8a5bcff65402c9e769d56dcf9d0bc7c7437c'}
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
check_sources()
voice_entry=module('solution_repair_v1_current_voice',HERE/'run-solution-path-voice-v4.py')
prep=voice_entry.prep;base=voice_entry.base

def load_plan(path=PLAN):
 path=Path(path).resolve();need(path==PLAN.resolve()and path.is_file()and sha(path)==PLAN_SHA,'Frozen root six-take repair plan missing/changed')
 plan=read(path);need(plan.get('schemaVersion')=='11.05-voice-subset-repair-plan-v1'and plan.get('topicId')==TOPIC,'Wrong repair scope')
 need((plan.get('canonicalSceneCount'),plan.get('paragraphCount'),plan.get('exactReuseCount'),plan.get('newSynthesisCount'))==(48,14,42,6),'Exact48/14/42/6 repair scope required')
 need(plan.get('profileReferenceEngineUnchanged')is True and [r['sceneId']for r in plan['replacementScenes']]==list(TARGETS),'Exact six root replacements required')
 need(plan['newNarration']==pin(NARRATION)and plan['sourceNarrationSHA256']==NARRATION_SHA==sha(NARRATION),'New operative narration differs')
 old_path=PROJECT/'narration-final-v4.json';need(plan['oldNarration']==pin(old_path)and sha(old_path)==OLD_NAR_SHA,'Old narration history differs')
 policy=plan['policy'];need(all(policy.get(k)is False for k in('trimOrTimeStretch','dynamicGainCompression','rawOrHistoricalEvidenceOverwrite','lowerResourceGate','actualListening','automaticSpeechPass','humanApproval')),'Repair cannot waive PCM/resource/review boundaries')
 return plan

def sentence_delta(old_draft,new_draft,old_scenes,new_scenes):
 need(len(old_draft['narrationKo'])==len(new_draft['narrationKo'])==len(old_draft['paragraphsEn'])==len(new_draft['paragraphsEn'])==14,'Exact14 bilingual paragraphs required')
 need(len(old_scenes)==len(new_scenes)==48 and [s['id']for s in old_scenes]==[s['id']for s in new_scenes],'Stable48 sentence IDs/order required')
 changed=[s['id']for s,t in zip(old_scenes,new_scenes)if s!=t]
 need(changed==['p013-c01']and next(s for s in new_scenes if s['id']=='p013-c01')['lines']==[NEW_P13],'Only declared P13 complete-sentence delta permitted')
 for i,(a,z)in enumerate(zip(old_draft['narrationKo'],new_draft['narrationKo'])):
  if i!=12:need(a==z,'Other canonical KO paragraph changed')
 for i,(a,z)in enumerate(zip(old_draft['paragraphsEn'],new_draft['paragraphsEn'])):
  if i!=12:need(a==z,'Other canonical EN paragraph changed')
  else:
   old_first,separator,tail=a.partition('. ');need(bool(separator)and z==NEW_P13_EN+' '+tail,'Only declared P13 first EN sentence may change')

def verify_old_review(plan,old):
 """Validate immutable prior cache bytes without current-source prepare/model."""
 qa=module('solution_repair_v1_old_blind_asr',HERE/'run-solution-path-voice-qa-v5.py')
 ap=checked(plan['rawAsrReview'],'old ASR');lp=checked(plan['rawLevelReview'],'old levels');review=read(ap['path']);levels=read(lp['path'])
 path=Path(ap['path']);job=read(path.parent/'job.json')
 need(path.name=='review.json'and path.parent==Path(job['output']).resolve()and digest(job['identity'])==job['fingerprint']==review['fingerprint'],'Old exact ASR job identity differs')
 need(job['identity']['voiceFingerprint']==OLD_FP and job['identity']['sourceNarration']==plan['oldNarration']and job['voiceEvidence']==plan['oldVoiceEvidence'],'Old ASR source/immutable voice binding differs')
 need(job['identity']['profile']==qa.PROFILE and job['identity']['modelPins']==qa.qa.APPROVED['modelPins']and job['identity']['trustedUtilitySHA256']==qa.qa.APPROVED['trustedSHA256'],'Old independent recognizer differs')
 for row in job['sourcePins']:checked(row,'old ASR source')
 need(sha(path.parent/'adapter-source.py')==job['identity']['adapterSHA256']==PINS['run-solution-path-voice-qa-v5.py'],'Old actual ASR adapter snapshot differs')
 need(job['identity']['tasks']==qa.qa.build_tasks(old,read(old['timing']['path'])),'Old ASR take/join PCM windows differ')
 need(all(qa.cached(job,t)is not None for t in job['identity']['tasks']),'Old ASR cache incomplete')
 def existing(destination,value):need(Path(destination).resolve()==path.resolve()and value==review,'Old ASR summary differs from caches')
 fn=qa.summary;scope=dict(fn.__globals__,voice=types.SimpleNamespace(immutable_json=existing));rebuilt=types.FunctionType(fn.__code__,scope,'verify_old_summary_without_write')(job)
 need(rebuilt==review and review['voiceFingerprint']==OLD_FP and review['aggregateSHA256']==old['aggregateWav']['sha256']and review['timingSHA256']==old['timing']['sha256']and len(review['takes'])==48 and len(review['boundaryWindows'])==47 and len(review['paragraphs'])==14,'Old full ASR review differs')
 need(review['aliasesApplied']is False and review['expectedPrompt']is None and review['humanListening']is False,'Old literal unknowns must remain raw')
 need(levels['voiceFingerprint']==OLD_FP and levels['canonicalWav']==old['aggregateWav']and levels['asrReview']==ap and len(levels['takes'])==48 and len(levels['paragraphs'])==14 and len(levels['joins'])==47,'Old numerical proof differs')
 need([r['sceneId']for r in levels['takes']]==[s['id']for s in old['identity']['scenes']]and [r['paragraph']for r in levels['paragraphs']]==list(range(1,15)),'Old numerical take/paragraph order differs')
 for observed,expected in zip(levels['joins'],review['boundaryObservations']):
  need(all(observed[k]==expected[k]for k in('previousScene','nextScene','joinType','boundarySample')),'Old numerical join/sample order differs')
 checked(levels['levelPrimitive'],'old level primitive');need(levels['levelPrimitive']['sha256']==qa.qa.APPROVED['firstLevelPrimitiveSHA256'],'Old numerical primitive differs')
 need(all(f.get('sceneId')in TARGETS for f in levels['flags']if f.get('kind')=='sustained-take-word-body-decline'),'Declining take cannot enter42 reuse')
 return dict(rawAsrReview=ap,rawLevelReview=lp,rawAsrJob=pin(path.parent/'job.json'),rawAsrAdapter=pin(path.parent/'adapter-source.py'))

def validate_reuse(full,plan):
 oldpin=checked(plan['oldVoiceEvidence'],'immutable prior voice');old=read(oldpin['path']);expected=(ROOT/'shared/output/architectural-111-20261106/11-05/voice-attempts'/OLD_FP[:24]/'voice-complete-proof.json').resolve()
 need(Path(oldpin['path'])==expected and old['topicId']==TOPIC and old['fingerprint']==plan['oldVoiceFingerprint']==OLD_FP and digest(old['identity'])==OLD_FP,'Old immutable proof identity/path differs')
 need(base.verify_complete(dict(identity=old['identity'],fingerprint=OLD_FP),expected.parent)==old,'Old preserved raw/engine proof differs')
 receipt=base.validate_receipt(dict(identity=old['identity'],fingerprint=OLD_FP),expected.parent);need(plan['oldNarration']in receipt['inputs'],'Old immutable input receipt lacks exact original narration')
 for key in('tts','modelPins','referenceSHA256','referenceTextSHA256','engine','guard','rawPcmPolicy'):need(old['identity'][key]==full['identity'][key],'Profile/model/reference/guard changed: '+key)
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
 need(len(oldmap)==48 and [r['oldSceneId']for r in plan['subsetReuse']]==[r['newSceneId']for r in plan['subsetReuse']]==safe,'Exact42 ordered unchanged raw reuses required')
 rows=[]
 for row in plan['subsetReuse']:
  sid=row['oldSceneId'];scene,wav=oldmap[sid];actual=base.wav_info(checked(row['sourceWav'],'retained raw')['path'])
  need(actual==wav==row['sourceWav']and Path(actual['path']).resolve()==expected.parent/'chunks'/(sid+'-scene.wav'),'Reuse raw WAV/PCM/header/source path differs')
  need(scene['lines']==[row['canonicalText']]==next(s for s in new_scenes if s['id']==sid)['lines']and bool(row.get('reuseReason')),'Retained complete sentence differs')
  need(checked(row['sourceVoiceEvidence'],'row source voice')==oldpin and row['sourceVoiceEvidence']['fingerprint']==OLD_FP,'Reuse row immutable voice differs');rows.append(copy.deepcopy(row))
 for row in plan['replacementScenes']:
  sid=row['sceneId'];scene,wav=oldmap[sid];need(row['oldCanonicalText']==scene['lines'][0]and row['canonicalText']==next(s for s in new_scenes if s['id']==sid)['lines'][0]and row['previousSelectedRaw']==wav and bool(row['reason']),'Selected replacement source/text differs')
 return rows,oldpin,verify_old_review(plan,old)

def reselect(full,plan,plan_path,adapter):
 rows,oldpin,reviews=validate_reuse(full,plan);selection=dict(protocol=PROTOCOL,plan=pin(plan_path),sourceVoiceEvidence=oldpin,sourceVoiceFingerprint=OLD_FP,newNarration=plan['newNarration'],repairSceneIds=list(TARGETS),expectedFullCount=48,expectedNewCount=6,expectedByteReusedCount=42,adapterSHA256=adapter['sha256'],preparerSHA256=SELF_SHA,baseControllerSHA256=PINS['run-selected-voice.py'])
 identity=dict(full['identity'],repairSelection=selection);fp=digest(identity);need(fp!=OLD_FP,'New repair output must not collide with old voice')
 inputs=full['inputs']+[pin(plan_path),oldpin,adapter,pin(__file__)]+[pin(HERE/name)for name in PINS]+list(reviews.values())+[dict(path=r['sourceWav']['path'],sha256=r['sourceWav']['sha256'])for r in rows]
 inputs=list({r['path']:{k:r[k]for k in('path','sha256')}for r in inputs}.values());preparation=digest(dict(synthesisIdentity=fp,inputs=inputs,script=full['script'],paragraphMapping=full['paragraphMapping']))
 folder=PROJECT/'production/voice-preparation'/preparation[:24];out=ROOT/'shared/output/architectural-111-20261106/11-05/voice-attempts'/fp[:24]
 manifest=copy.deepcopy(full['manifest']);manifest['paths']['script']=(folder/'narration-qwen.json').relative_to(ROOT).as_posix();manifest['tts']['outputDir']=out.relative_to(ROOT).as_posix();manifest['synthesisIdentity']=fp;manifest['repairSelection']=selection
 command=list(full['qwenSynthesisArgv']);command[8]=(folder/'voice-manifest.json').relative_to(ROOT).as_posix()
 selected=dict(full,identity=identity,fingerprint=fp,preparationFingerprint=preparation,inputs=inputs,stagingDirectory=str(folder),voiceOutputDirectory=str(out),manifest=manifest,qwenSynthesisArgv=command,qwenDryRunArgv=command+['--dry-run'])
 missing=[s for s in identity['scenes']if s['id']in TARGETS];need([s['id']for s in missing]==list(TARGETS),'Engine must receive only exact6 replacements')
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
  v=prepare(a.repair_plan,a.native_evidence,a.native_qa,a.narration);print(json.dumps(dict(ready=True,fullVoiceFingerprint=v['fingerprint'],repairFingerprint=v['repair']['fingerprint'],fullSceneCount=48,reuseCount=42,missingOnlyCount=6,output=v['voiceOutputDirectory'],staged=False,reuseCopied=False,modelLoaded=False)))
 except(Pending,FileNotFoundError)as e:print(json.dumps(dict(ready=False,reason=str(e),staged=False,reuseCopied=False,modelLoaded=False)))
if __name__=='__main__':main()
