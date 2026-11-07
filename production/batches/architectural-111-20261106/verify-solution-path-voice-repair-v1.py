"""Temp PCM/metadata-only subset fixtures; no model/resource/Unity/FFmpeg job."""
import copy, importlib.util, json, struct, sys, tempfile, unittest, wave
from contextlib import ExitStack
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE));sys.dont_write_bytecode=True
spec=importlib.util.spec_from_file_location('solution_repair_v1_cpu',HERE/'run-solution-path-voice-repair-v1.py');w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)
p=w.prep
def dump(path,value):
 path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes((json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode());return path
def wav(path,frames,value=1):
 path.parent.mkdir(parents=True,exist_ok=True)
 with wave.open(str(path),'wb')as f:f.setparams((1,2,24000,frames,'NONE','not compressed'));f.writeframes(struct.pack('<h',value)*frames)

class Repair(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(prefix='solution-six-repair-cpu-');self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name);self.project=self.root/'projects/shorts-leveldesign-11-05'
  self.stack=ExitStack();self.addCleanup(self.stack.close)
  self.stack.enter_context(patch.object(p,'ROOT',self.root));self.stack.enter_context(patch.object(p,'PROJECT',self.project))
  self.stack.enter_context(patch.object(w.base,'ROOT',self.root));self.stack.enter_context(patch.object(w.life,'ROOT',self.root));self.stack.enter_context(patch.object(p.prep.core,'ROOT',self.root))
  actual=HERE.parents[2]/'projects/shorts-leveldesign-11-05';self.project.mkdir(parents=True)
  for name in('narration-final-v4.json','narration-final-v5.json'):(self.project/name).write_bytes((actual/name).read_bytes())
  old_draft=p.read(self.project/'narration-final-v4.json');new_draft=p.read(self.project/'narration-final-v5.json')
  oldscript,oldmap=p.prep.sentence_plan(old_draft,p.OLD_NAR_SHA);newscript,newmap=p.prep.sentence_plan(new_draft,p.NARRATION_SHA)
  actualproof=p.read(Path(p.read(actual/'voice-subset-repair-plan-v1.json')['oldVoiceEvidence']['path']))
  oldidentity=copy.deepcopy(actualproof['identity']);self.oldout=self.root/'shared/output/architectural-111-20261106/11-05/voice-attempts'/p.OLD_FP[:24]
  for i,s in enumerate(oldidentity['scenes']):wav(self.oldout/'chunks'/(s['id']+'-scene.wav'),480+i,i+1)
  self.old=p.base.canonical_outputs(dict(topicId='11.05',fingerprint=p.OLD_FP,identity=oldidentity,paragraphMapping=oldmap),self.oldout,{})
  oldproof=dump(self.oldout/'voice-complete-proof.json',self.old);dump(self.oldout/'voice-inputs.json',dict(protocol=p.base.PROTOCOL,fingerprint=p.OLD_FP,identity=oldidentity,inputs=[p.pin(self.project/'narration-final-v4.json')]))
  qa=p.module('solution_repair_fixture_blind',HERE/'run-solution-path-voice-qa-v5.py');tasks=qa.qa.build_tasks(self.old,p.read(self.old['timing']['path']))
  folder=self.oldout/'review/independent-asr-selected-v1'/('c'*24);folder.mkdir(parents=True);snapshot=folder/'adapter-source.py';snapshot.write_bytes((HERE/'run-solution-path-voice-qa-v5.py').read_bytes())
  ji=dict(profile=qa.PROFILE,modelPins=qa.qa.APPROVED['modelPins'],trustedUtilitySHA256=qa.qa.APPROVED['trustedSHA256'],adapterSHA256=p.PINS['run-solution-path-voice-qa-v5.py'],tasks=tasks,voiceFingerprint=p.OLD_FP,sourceNarration=p.pin(self.project/'narration-final-v4.json'),aggregateSHA256=self.old['aggregateWav']['sha256'],timingSHA256=self.old['timing']['sha256'])
  job=dict(identity=ji,fingerprint=p.digest(ji),output=str(folder),voiceOutput=str(self.oldout),voiceEvidence=p.pin(oldproof),sourcePins=[p.pin(snapshot)])
  # Directory label is only fixture-local; the source validator binds exact job/output and raw identity.
  dump(folder/'job.json',job)
  for t in tasks:
   raw=dict(text=t['expected'],chunks=[dict(text=t['expected'],timestamp=[.001,t['durationSeconds']-.001])])if t['kind']=='take'else dict(text='',chunks=[])
   dump(folder/(t['key']+'.json'),qa.qa.recognition_record(job,t,raw))
  review=qa.summary(job);lp=dump(folder/'raw-level-review/synthetic/review.json',dict(voiceFingerprint=p.OLD_FP,canonicalWav=self.old['aggregateWav'],asrReview=p.pin(folder/'review.json'),takes=[dict(sceneId=s['id'])for s in oldidentity['scenes']],paragraphs=[dict(paragraph=i)for i in range(1,15)],joins=review['boundaryObservations'],levelPrimitive=p.pin(HERE/'first-level-continuity-review.py'),flags=[dict(kind='sustained-take-word-body-decline',sceneId='p008-c01')]))
  newidentity=copy.deepcopy(oldidentity);newidentity['scenes']=[dict(id=s['id'],lines=s['lines'])for s in newscript['scenes']]
  self.full=dict(topicId='11.05',slug='shorts-leveldesign-11-05',ready=True,voiceReady=True,identity=newidentity,fingerprint=p.digest(newidentity),inputs=[p.pin(self.project/'narration-final-v5.json')],script=newscript,paragraphMapping=newmap,manifest=dict(slug='shorts-leveldesign-11-05',sourceNarrationSHA256=p.NARRATION_SHA,paths=dict(script='placeholder'),tts=dict(outputDir='placeholder'),editing=dict(exampleSeconds=0),rawPcmPolicy=newidentity['rawPcmPolicy']),qwenSynthesisArgv=['python','-u','-X','utf8','render_narration.py','--project','shorts-leveldesign-11-05','--manifest','placeholder','--batch-size','1','--device','cuda:0'])
  self.plan=dict(schemaVersion='11.05-voice-subset-repair-plan-v1',topicId='11.05',oldVoiceEvidence=p.pin(oldproof),oldVoiceFingerprint=p.OLD_FP,oldNarration=p.pin(self.project/'narration-final-v4.json'),newNarration=p.pin(self.project/'narration-final-v5.json'),rawAsrReview=p.pin(folder/'review.json'),rawLevelReview=p.pin(lp),subsetReuse=[],replacementScenes=[])
  for s,row in zip(oldidentity['scenes'],self.old['sceneWavs']):
   if s['id']in p.TARGETS:self.plan['replacementScenes'].append(dict(sceneId=s['id'],oldCanonicalText=s['lines'][0],canonicalText=next(x for x in newidentity['scenes']if x['id']==s['id'])['lines'][0],previousSelectedRaw=row,reason='Explicit synthetic replacement'))
   else:self.plan['subsetReuse'].append(dict(oldSceneId=s['id'],newSceneId=s['id'],canonicalText=s['lines'][0],sourceWav=row,sourceVoiceEvidence=dict(p.pin(oldproof),fingerprint=p.OLD_FP),reuseReason='Exact synthetic old bytes'))
  self.planpath=dump(self.project/'repair-plan.json',self.plan)
 def selected(self):return p.reselect(self.full,self.plan,self.planpath,p.pin(w.__file__))
 def bad(self,fn,*args):
  with self.assertRaises((p.Pending,RuntimeError,ValueError,KeyError)):fn(*args)
 def test_exact48_42_6_and_fresh_identity(self):
  v=self.selected();self.assertEqual(len(v['identity']['scenes']),48);self.assertEqual(len(v['repair']['rows']),42);self.assertEqual([s['id']for s in v['repair']['missing']],list(p.TARGETS));self.assertNotEqual(v['fingerprint'],p.OLD_FP);self.assertNotEqual(v['fingerprint'],self.full['fingerprint']);self.assertIn('repairSelection',v['identity'])
 def test_only_p13_changed_other47_source_texts_exact(self):
  self.assertEqual([a['id']for a,b in zip(self.old['identity']['scenes'],self.full['identity']['scenes'])if a!=b],['p013-c01']);self.assertEqual(next(s for s in self.full['identity']['scenes']if s['id']=='p013-c01')['lines'],[p.NEW_P13])
 def test_missing_script_never_contains_reused42(self):
  v=self.selected();ids=[s['id']for s in v['repair']['script']['scenes']];self.assertEqual(ids,list(p.TARGETS));self.assertFalse(set(ids)&{r['newSceneId']for r in v['repair']['rows']});self.assertEqual(v['repair']['manifest']['engineSceneScope'],'missing-subset-only')
 def test_profile_change_rejected(self):
  self.full['identity']['tts']['speed']=1.01;self.bad(p.validate_reuse,self.full,self.plan)
 def test_second_text_change_rejected(self):
  self.full['identity']['scenes'][0]['lines']=['다른 말입니다.'];self.bad(p.validate_reuse,self.full,self.plan)
 def test_wrong_p13_expansion_rejected(self):
  next(s for s in self.full['identity']['scenes']if s['id']=='p013-c01')['lines']=['짧게 바꿉니다.'];self.bad(p.validate_reuse,self.full,self.plan)
 def test_target_cannot_reenter_reuse(self):
  row=copy.deepcopy(self.plan['subsetReuse'][0]);row['oldSceneId']=row['newSceneId']='p005-c01';self.plan['subsetReuse'][0]=row;self.bad(p.validate_reuse,self.full,self.plan)
 def test_duplicate_reuse_or_reordered_mapping_rejected(self):
  self.plan['subsetReuse'][0],self.plan['subsetReuse'][1]=self.plan['subsetReuse'][1],self.plan['subsetReuse'][0];self.bad(p.validate_reuse,self.full,self.plan)
 def test_changed_retained_pcm_rejected(self):
  path=Path(self.plan['subsetReuse'][0]['sourceWav']['path']);data=bytearray(path.read_bytes());data[-1]^=1;path.write_bytes(data);self.bad(p.validate_reuse,self.full,self.plan)
 def test_foreign_mutable_old_pointer_rejected(self):
  other=dump(self.root/'voice-evidence.json',self.old);self.plan['oldVoiceEvidence']=p.pin(other);self.bad(p.validate_reuse,self.full,self.plan)
 def test_old_asr_missing_cache_rejected(self):
  folder=Path(self.plan['rawAsrReview']['path']).parent;(folder/'take-p001-c01.json').unlink();self.bad(p.validate_reuse,self.full,self.plan)
 def test_old_level_voice_or_join_order_rejected(self):
  path=Path(self.plan['rawLevelReview']['path']);r=p.read(path);r['joins'][0]['boundarySample']+=1;dump(path,r);self.plan['rawLevelReview']=p.pin(path);self.bad(p.validate_reuse,self.full,self.plan)
 def test_declining_reused_take_rejected(self):
  path=Path(self.plan['rawLevelReview']['path']);r=p.read(path);r['flags'].append(dict(kind='sustained-take-word-body-decline',sceneId='p001-c01'));dump(path,r);self.plan['rawLevelReview']=p.pin(path);self.bad(p.validate_reuse,self.full,self.plan)
 def test_old_asr_expected_prompt_or_alias_not_waived(self):
  path=Path(self.plan['rawAsrReview']['path']);r=p.read(path);r['aliasesApplied']=True;dump(path,r);self.plan['rawAsrReview']=p.pin(path);self.bad(p.validate_reuse,self.full,self.plan)
 def stage(self):
  v=self.selected();args=SimpleNamespace(topic='11.05',repair_plan=str(self.planpath),native_evidence=None,native_qa=None,narration=str(self.project/'narration-final-v5.json'))
  self.stack.enter_context(patch.object(p,'prepare',return_value=v));w.install_hooks();w.CURRENT=v;w.CURRENT_ARGS=args;w.life.CURRENT=v
  out=w.base.output_of(v);w.life.initialize_output(v);w.life.stage(v);return v,out
 def test_stage_copies_only42_exact_bytes_and_source_snapshot(self):
  v,out=self.stage();self.assertEqual(len(list((out/'chunks').glob('*.wav'))),42)
  for row in v['repair']['rows']:self.assertEqual((out/'chunks'/(row['newSceneId']+'-scene.wav')).read_bytes(),Path(row['sourceWav']['path']).read_bytes())
  self.assertEqual(w.life.subset_pins(v)[3]['sha256'],v['repair']['identity']['adapterSHA256'])
 def test_stage_changed_inputs_abort_before_copy(self):
  v=self.selected();w.CURRENT_ARGS=SimpleNamespace(topic='11.05',repair_plan='',native_evidence=None,native_qa=None,narration=None)
  changed=copy.deepcopy(v);changed['_basePrepared']['preparationFingerprint']='changed'
  with patch.object(p,'prepare',return_value=changed):self.bad(w.fresh_stage,v['_basePrepared'])
 def pending(self):
  v,out=self.stage();attempt=out/'engine-attempts'/'synthetic';attempt.mkdir(parents=True)
  request=dict(protocol=w.base.PROTOCOL,fingerprint=v['fingerprint'],identity=v['identity'],command=v['repair']['command'],repairFingerprint=v['repair']['fingerprint'],engineSceneScope='missing-subset-only',engineSceneIds=list(p.TARGETS),subsetPins=w.life.subset_pins(v))
  rp=dump(attempt/'request.json',request);pending=dict(attempt=str(attempt),requestPins=[p.pin(rp)]);return v,out,attempt,rp,pending
 def test_pending_exact_subset_source_proof_valid(self):
  v,out,attempt,rp,pending=self.pending();self.assertEqual(w.life.validate_launch_request(v,out,pending),attempt)
 def test_pending_tampered_adapter_even_rebound_outer_pin_rejected(self):
  v,out,attempt,rp,pending=self.pending();request=p.read(rp);ap=Path(request['subsetPins'][3]['path']);ap.write_bytes(b'wrong adapter');request['subsetPins'][3]=p.pin(ap);dump(rp,request);pending['requestPins']=[p.pin(rp)];self.bad(w.life.validate_launch_request,v,out,pending)
 def test_pending_reused_scene_injection_rejected(self):
  v,out,attempt,rp,pending=self.pending();request=p.read(rp);request['engineSceneIds'].append('p001-c01');dump(rp,request);pending['requestPins']=[p.pin(rp)];self.bad(w.life.validate_launch_request,v,out,pending)
 def test_full_completion_requires_actual_subset_engine_proof(self):
  v=self.selected();self.bad(w.life.canonical_outputs,v,Path(v['voiceOutputDirectory']),{})
 def test_retry_one_or_multiple_transient_winerror5_only(self):
  for count in(1,3):
   calls=[];error=PermissionError('synthetic');error.winerror=5
   def save(*args):
    calls.append(1)
    if len(calls)<=count:raise error
   with patch.object(w,'retry_owner_token',return_value='own'),patch.object(w,'original_save',side_effect=save),patch.object(w.time,'sleep'):w.metadata_save('synthetic',{})
   self.assertEqual(len(calls),count+1)
 def test_retry_persistent_foreign_and_other_error_not_hidden(self):
  for token,code,count in[('own',5,10),(False,5,1),('own',32,1)]:
   error=PermissionError('synthetic');error.winerror=code
   with patch.object(w,'retry_owner_token',return_value=token),patch.object(w,'original_save',side_effect=error)as save,patch.object(w.time,'sleep'):
    self.assertRaises(PermissionError,w.metadata_save,'synthetic',{});self.assertEqual(save.call_count,count)
 def test_scope_wait_and_no_execute_by_default(self):
  self.assertFalse(w.arguments([]).execute)
  for args in(['--topic','06.02'],['--wait-hours','nan'],['--wait-hours','7']):self.assertRaises(ValueError,w.arguments,args)
 def test_current_resource_and_base_lifecycle_unchanged(self):
  self.assertEqual(w.LIFECYCLE_SHA,'c70ba7ff185f048bbb53c3b7845b5af2237d14de1ea3ef511e9afacdf8171366');self.assertEqual(p.PINS['run-selected-voice.py'],'55ec247dafdef34bf2f31e9054e5a9fd3629ea2f220847b19694c48b59e26a99')
  self.assertIs(w.base.zen.busy_reason,p.voice_entry.audited_native_busy)
 def test_unready_execute_cannot_start_worker_or_copy(self):
  with patch.object(p,'prepare',side_effect=p.Pending('synthetic unavailable')),patch.object(w.base,'execute',side_effect=AssertionError('No worker/launch')):
   self.assertRaises(SystemExit,w.main,['--execute'])

if __name__=='__main__':unittest.main(verbosity=1)
