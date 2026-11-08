"""Temp PCM/metadata-only subset fixtures; no model/resource/Unity/FFmpeg job."""
import copy, importlib.util, json, struct, sys, tempfile, unittest, wave
from contextlib import ExitStack
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE));sys.dont_write_bytecode=True
spec=importlib.util.spec_from_file_location('solution_repair_v3_cpu',HERE/'run-solution-path-voice-repair-v3.py');w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)
p=w.prep
def dump(path,value):
 path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes((json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode());return path
def wav(path,frames,value=1):
 path.parent.mkdir(parents=True,exist_ok=True)
 with wave.open(str(path),'wb')as f:f.setparams((1,2,24000,frames,'NONE','not compressed'));f.writeframes(struct.pack('<h',value)*frames)

class Repair(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(prefix='solution-three-repair-cpu-');self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name);self.project=self.root/'projects/shorts-leveldesign-11-05'
  self.stack=ExitStack();self.addCleanup(self.stack.close)
  self.stack.enter_context(patch.object(p,'ROOT',self.root));self.stack.enter_context(patch.object(p,'PROJECT',self.project))
  self.stack.enter_context(patch.object(w.base,'ROOT',self.root));self.stack.enter_context(patch.object(w.life,'ROOT',self.root));self.stack.enter_context(patch.object(p.prep.core,'ROOT',self.root))
  actual=HERE.parents[2]/'projects/shorts-leveldesign-11-05';self.project.mkdir(parents=True)
  for name in('narration-final-v4.json','narration-final-v5.json'):(self.project/name).write_bytes((actual/name).read_bytes())
  old_draft=p.read(self.project/'narration-final-v5.json');new_draft=copy.deepcopy(old_draft)
  oldscript,oldmap=p.prep.sentence_plan(old_draft,p.OLD_NAR_SHA);newscript,newmap=p.prep.sentence_plan(new_draft,p.NARRATION_SHA)
  actualproof=p.read(Path(p.read(actual/'voice-subset-repair-plan-v3.json')['oldVoiceEvidence']['path']))
  oldidentity=copy.deepcopy(actualproof['identity']);self.oldout=self.root/'shared/output/architectural-111-20261106/11-05/voice-attempts'/p.OLD_FP[:24]
  for i,scene in enumerate(oldidentity['scenes']):wav(self.oldout/'chunks'/(scene['id']+'-scene.wav'),480+i,i+1)
  self.old=p.base.canonical_outputs(dict(topicId='11.05',fingerprint=p.OLD_FP,identity=oldidentity,paragraphMapping=oldmap),self.oldout,{})
  oldproof=dump(self.oldout/'voice-complete-proof.json',self.old);dump(self.oldout/'voice-inputs.json',dict(protocol=p.base.PROTOCOL,fingerprint=p.OLD_FP,identity=oldidentity,inputs=[p.pin(self.project/'narration-final-v5.json')]))
  dump(self.oldout/'repair-inputs.json',dict(fingerprint='prior-six-only',preserved=True))
  self.qa=p.module('solution_repair_v3_fixture_blind',HERE/'run-solution-path-voice-qa-v6.py');qa=self.qa;tasks=qa.qa.build_tasks(self.old,p.read(self.old['timing']['path']))
  self.stack.enter_context(patch.object(p,'prior_tools',return_value=qa))
  # These tests exercise full48/review95/scalars/launch recovery with temp PCM.
  # The separate PriorRepairOrigin cases below require every prior6 delegate.
  self.stack.enter_context(patch.object(p,'verify_prior_origin',return_value=dict(priorVoiceInputs=p.pin(self.oldout/'voice-inputs.json'),priorRepairInputs=p.pin(self.oldout/'repair-inputs.json'))))
  folder=self.oldout/'review/independent-asr-selected-v1'/('c'*24);folder.mkdir(parents=True);snapshot=folder/'adapter-source.py';snapshot.write_bytes((HERE/'run-solution-path-voice-qa-v6.py').read_bytes())
  ji=dict(profile=qa.PROFILE,modelPins=qa.qa.APPROVED['modelPins'],trustedUtilitySHA256=qa.qa.APPROVED['trustedSHA256'],adapterSHA256=p.PINS['run-solution-path-voice-qa-v6.py'],tasks=tasks,voiceFingerprint=p.OLD_FP,sourceNarration=p.pin(self.project/'narration-final-v5.json'),aggregateSHA256=self.old['aggregateWav']['sha256'],timingSHA256=self.old['timing']['sha256'])
  job=dict(protocol=qa.PROTOCOL,identity=ji,fingerprint=p.digest(ji),output=str(folder),voiceOutput=str(self.oldout),voiceEvidence=p.pin(oldproof),sourcePins=[p.pin(snapshot)])
  dump(folder/'job.json',job)
  for task in tasks:
   raw=dict(text=task['expected'],chunks=[dict(text=task['expected'],timestamp=[.001,task['durationSeconds']-.001])])if task['kind']=='take'else dict(text='',chunks=[])
   dump(folder/(task['key']+'.json'),qa.qa.recognition_record(job,task,raw))
  review=qa.summary(job)
  trends={scene['id']:dict(wordCount=1,spanSeconds=7 if scene['id']=='p013-c01'else 5.9,lateEarlyDb=-9 if scene['id']=='p013-c01'else-7,flag=scene['id']=='p013-c01')for scene in oldidentity['scenes']}
  lp=dump(folder/'raw-level-review/synthetic/review.json',dict(voiceFingerprint=p.OLD_FP,canonicalWav=self.old['aggregateWav'],asrReview=p.pin(folder/'review.json'),takes=[dict(sceneId=scene['id'],wordTrend=trends[scene['id']])for scene in oldidentity['scenes']],paragraphs=[dict(paragraph=i)for i in range(1,15)],joins=review['boundaryObservations'],levelPrimitive=p.pin(HERE/'first-level-continuity-review.py'),flags=[dict(kind='sustained-take-word-body-decline',sceneId='p013-c01')]))
  peer=dump(folder/'content-peer.json',dict(schemaVersion='11.05-voice-asr-content-peer-review-v6',identity=dict(voiceFingerprint=p.OLD_FP),inputs=dict(immutableVoiceProof=p.pin(oldproof),review=p.pin(folder/'review.json'),rawNumericalLevelReview=p.pin(lp)),numericalContext=dict(technicalScalarPreparationAllowed=False,neededHolds=[dict(sceneId=sid)for sid in('p013-c01','p008-c01','p008-c02')]),limits=dict(actualListening=False,humanApproval=False,automaticSpeechPass=False)))
  newidentity={key:copy.deepcopy(value)for key,value in oldidentity.items()if key!='repairSelection'}
  self.full=dict(topicId='11.05',slug='shorts-leveldesign-11-05',ready=True,voiceReady=True,identity=newidentity,fingerprint=p.digest(newidentity),inputs=[p.pin(self.project/'narration-final-v5.json')],script=newscript,paragraphMapping=newmap,manifest=dict(slug='shorts-leveldesign-11-05',sourceNarrationSHA256=p.NARRATION_SHA,paths=dict(script='placeholder'),tts=dict(outputDir='placeholder'),editing=dict(exampleSeconds=0),rawPcmPolicy=newidentity['rawPcmPolicy']),qwenSynthesisArgv=['python','-u','-X','utf8','render_narration.py','--project','shorts-leveldesign-11-05','--manifest','placeholder','--batch-size','1','--device','cuda:0'])
  self.plan=dict(schemaVersion='11.05-voice-subset-repair-plan-v3',topicId='11.05',oldVoiceEvidence=p.pin(oldproof),oldVoiceFingerprint=p.OLD_FP,oldNarration=p.pin(self.project/'narration-final-v5.json'),newNarration=p.pin(self.project/'narration-final-v5.json'),oldVoiceInputs=p.pin(self.oldout/'voice-inputs.json'),oldRepairInputs=p.pin(self.oldout/'repair-inputs.json'),rawAsrJob=p.pin(folder/'job.json'),rawAsrReview=p.pin(folder/'review.json'),rawLevelReview=p.pin(lp),contentPeerReview=p.pin(peer),subsetReuse=[],replacementScenes=[])
  for scene,row in zip(oldidentity['scenes'],self.old['sceneWavs']):
   if scene['id']in p.TARGETS:self.plan['replacementScenes'].append(dict(sceneId=scene['id'],oldCanonicalText=scene['lines'][0],canonicalText=scene['lines'][0],previousSelectedRaw=row,reason='Synthetic numerical hold',numericalTrend=trends[scene['id']]))
   else:self.plan['subsetReuse'].append(dict(oldSceneId=scene['id'],newSceneId=scene['id'],canonicalText=scene['lines'][0],sourceWav=row,sourceVoiceEvidence=dict(p.pin(oldproof),fingerprint=p.OLD_FP),reuseReason='Exact current6691 bytes'))
  self.planpath=dump(self.project/'repair-plan.json',self.plan)
 def selected(self):return p.reselect(self.full,self.plan,self.planpath,p.pin(w.__file__))
 def bad(self,fn,*args):
  with self.assertRaises((p.Pending,RuntimeError,ValueError,KeyError)):fn(*args)
 def test_exact48_45_3_and_fresh_identity(self):
  v=self.selected();self.assertEqual(len(v['identity']['scenes']),48);self.assertEqual(len(v['repair']['rows']),45);self.assertEqual([s['id']for s in v['repair']['missing']],list(p.TARGETS));self.assertNotEqual(v['fingerprint'],p.OLD_FP);self.assertNotEqual(v['fingerprint'],self.full['fingerprint']);self.assertIn('repairSelection',v['identity'])
 def test_all48_texts_and_both14paragraphs_exact(self):
  self.assertEqual(self.old['identity']['scenes'],self.full['identity']['scenes']);self.assertEqual(self.plan['oldNarration'],self.plan['newNarration'])
  self.assertTrue(all(row['oldCanonicalText']==row['canonicalText']for row in self.plan['replacementScenes']))
 def test_all_current_p5_three_are_in45_reuse(self):
  v=self.selected();rows={r['newSceneId']:r for r in v['repair']['rows']}
  for sid in('p005-c01','p005-c02','p005-c03'):
   self.assertIn(sid,rows);self.assertEqual(Path(rows[sid]['sourceWav']['path']).parent,self.oldout/'chunks')
 def test_missing_script_never_contains_reused45(self):
  v=self.selected();ids=[s['id']for s in v['repair']['script']['scenes']];self.assertEqual(ids,list(p.TARGETS));self.assertFalse(set(ids)&{r['newSceneId']for r in v['repair']['rows']});self.assertEqual(v['repair']['manifest']['engineSceneScope'],'missing-subset-only')
 def test_profile_change_rejected(self):
  self.full['identity']['tts']['speed']=1.01;self.bad(p.validate_reuse,self.full,self.plan)
 def test_second_text_change_rejected(self):
  self.full['identity']['scenes'][0]['lines']=['다른 말입니다.'];self.bad(p.validate_reuse,self.full,self.plan)
 def test_wrong_p13_expansion_rejected(self):
  next(s for s in self.full['identity']['scenes']if s['id']=='p013-c01')['lines']=['짧게 바꿉니다.'];self.bad(p.validate_reuse,self.full,self.plan)
 def test_target_cannot_reenter_reuse(self):
  row=copy.deepcopy(self.plan['subsetReuse'][0]);row['oldSceneId']=row['newSceneId']='p008-c01';self.plan['subsetReuse'][0]=row;self.bad(p.validate_reuse,self.full,self.plan)
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
 def test_seed_instruct_reference_or_unlisted_identity_change_rejected(self):
  for key,value in(('seed',1),('instruct','different'),('arbitraryProfileExtension',True)):
   full=copy.deepcopy(self.full);full['identity'][key]=value;self.bad(p.validate_reuse,full,self.plan)
 def test_omitted45row_or_e51_p5_substitution_rejected(self):
  self.plan['subsetReuse'].pop();self.bad(p.validate_reuse,self.full,self.plan)
 def test_p5_historical_path_even_samebytes_is_not_current6691(self):
  row=next(r for r in self.plan['subsetReuse']if r['newSceneId']=='p005-c01');oldpath=Path(row['sourceWav']['path']);foreign=self.root/'historical-e51/p005-c01-scene.wav';foreign.parent.mkdir();foreign.write_bytes(oldpath.read_bytes());row['sourceWav']=p.base.wav_info(foreign);self.bad(p.validate_reuse,self.full,self.plan)
 def test_sample_clock_one_sample_tamper_rejected_even_rebound_timing(self):
  path=Path(self.old['timing']['path']);timing=p.read(path);timing['entries'][0]['end']+=1/24000;dump(path,timing);self.old['timing']['sha256']=p.sha(path);dump(Path(self.plan['oldVoiceEvidence']['path']),self.old);self.plan['oldVoiceEvidence']=p.pin(self.plan['oldVoiceEvidence']['path']);self.bad(p.validate_reuse,self.full,self.plan)
 def test_missing_content_peer_or_lost_nearthreshold_hold_rejected(self):
  path=Path(self.plan['contentPeerReview']['path']);peer=p.read(path);peer['numericalContext']['neededHolds'].pop();dump(path,peer);self.plan['contentPeerReview']=p.pin(path);self.bad(p.validate_reuse,self.full,self.plan)
 def test_changed_measured_target_trend_rejected(self):
  self.plan['replacementScenes'][0]['numericalTrend']['lateEarlyDb']=-1;self.bad(p.validate_reuse,self.full,self.plan)
 def test_current_asr_wrong_protocol_or_job_pin_rejected(self):
  path=Path(self.plan['rawAsrJob']['path']);job=p.read(path);job['protocol']='old-asr-v5';dump(path,job);self.plan['rawAsrJob']=p.pin(path);self.bad(p.validate_reuse,self.full,self.plan)
 def test_nar5_bilingual_change_rejected(self):
  path=self.project/'narration-final-v5.json';old=p.read(path);new=copy.deepcopy(old);new['paragraphsEn'][0]+=' Changed.'
  self.bad(p.sentence_delta,old,new,self.old['identity']['scenes'],self.full['identity']['scenes'])
 def stage(self):
  v=self.selected();args=SimpleNamespace(topic='11.05',repair_plan=str(self.planpath),native_evidence=None,native_qa=None,narration=str(self.project/'narration-final-v5.json'))
  self.stack.enter_context(patch.object(p,'prepare',return_value=v));w.install_hooks();w.CURRENT=v;w.CURRENT_ARGS=args;w.life.CURRENT=v
  out=w.base.output_of(v);w.life.initialize_output(v);w.life.stage(v);return v,out
 def test_stage_copies_only45_exact_bytes_and_source_snapshot(self):
  v,out=self.stage();self.assertEqual(len(list((out/'chunks').glob('*.wav'))),45)
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

class PriorRepairOrigin(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(prefix='prior-six-proof-cpu-');self.addCleanup(self.tmp.cleanup);self.out=Path(self.tmp.name)
  self.nar=dump(self.out/'narration.json',dict(frozen=True));self.old=dict(identity=dict(text='unchanged'));self.prov=dict(fingerprint=p.OLD_FP,identity=self.old['identity'])
  self.plan=dict(oldNarration=p.pin(self.nar),oldVoiceInputs=p.pin(dump(self.out/'voice-inputs.json',{})),oldRepairInputs=p.pin(dump(self.out/'repair-inputs.json',{})))
  self.engine=dict(engineSceneCount=6,fullCanonicalSceneCount=48,reusedSceneIds=['s'+str(i)for i in range(42)])
  from unittest.mock import Mock
  self.verify=Mock(return_value=self.old);self.receipt=Mock(return_value=dict(inputs=[p.pin(self.nar)]));self.subset=Mock(return_value=self.engine)
  self.qa=SimpleNamespace(prepared_repair=Mock(return_value=self.prov),voice_worker=SimpleNamespace(life=SimpleNamespace(verify_complete=self.verify,validate_receipt=self.receipt)),verify_subset_engine=self.subset)
 def call(self):
  with patch.object(p,'prior_tools',return_value=self.qa):return p.verify_prior_origin(self.plan,self.old,self.out)
 def test_full_prior_v2_context_and_actual6engine_delegate_required(self):
  result=self.call();self.verify.assert_called_once_with(self.prov,self.out);self.receipt.assert_called_once_with(self.prov,self.out);self.subset.assert_called_once_with(self.prov,self.out,self.old);self.assertEqual(result['priorRepairInputs'],self.plan['oldRepairInputs'])
 def test_wrong_prior_identity_or_original_e51_cannot_substitute(self):
  self.prov['fingerprint']='e51bc0ed82c4bea1233f6840'+'0'*40;self.assertRaises(p.Pending,self.call)
 def test_missing_repair_receipt_or_real6_artifacts_rejected(self):
  for fn in(self.receipt,self.subset):
   fn.side_effect=RuntimeError('missing prior actual proof');self.assertRaises(RuntimeError,self.call);fn.side_effect=None
 def test_prior_scope6_full48_reused42_not_merely_base_pcm(self):
  for key,value in(('engineSceneCount',48),('fullCanonicalSceneCount',6),('reusedSceneIds',[])):
   old=self.engine[key];self.engine[key]=value;self.assertRaises(p.Pending,self.call);self.engine[key]=old
 def test_missing_nar_receipt_or_mutable_input_alias_rejected(self):
  self.receipt.return_value=dict(inputs=[]);self.assertRaises(p.Pending,self.call);self.receipt.return_value=dict(inputs=[p.pin(self.nar)])
  other=dump(self.out/'mutable.json',{});self.plan['oldVoiceInputs']=p.pin(other);self.assertRaises(p.Pending,self.call)


class ExecuteParentV3(unittest.TestCase):
 def fixture(self):
  capture=Path('C:/Users/1/Videos/YamyamProduction/architectural-111-20261106/11-05-repair-v1-actual-launcher-self-block-v1.json')
  self.assertEqual(p.sha(capture),'111435427dc5c85ed2ab18f3635bb513b93577f37dee40266cb3e021b2926cbe')
  r=p.read(capture)
  def normalized(row):return dict(pid=row['pid'],ppid=row['ppid'],create_time=row['ctime'],name='python.exe',exe=row['exe'],cmdline=copy.deepcopy(row['argv']))
  own,parent=normalized(r['ownActual']),normalized(r['parentActual'])
  for row in(own,parent):row['cmdline'][4]=str(Path(w.__file__).resolve())
  return copy.deepcopy(parent),own,parent,r
 def marker(self,own):return dict(protocol=w.base.PROTOCOL,owner='architectural-111-11-05-voice',topicId='11.05',stage='voice',token='a'*32,pid=own['pid'],createTime=own['create_time'],argv=copy.deepcopy(own['cmdline']),commandSHA256=w.base.digest(own['cmdline']),child=None)
 def test_actual_capture_proves_old_self_block_and_new_exact_shape(self):
  info,own,parent,r=self.fixture();self.assertNotEqual(own['cmdline'][0],parent['cmdline'][0]);self.assertEqual(own['cmdline'][1:],parent['cmdline'][1:])
  self.assertIn('model/recognizer',w.original_process_reason(info,own['pid']));self.assertTrue(w.execute_parent_matches(info,own,parent))
  for row in(info,own,parent):row['cmdline'][4]=r['ownActual']['argv'][4]
  self.assertFalse(w.execute_parent_matches(info,own,parent))
 def test_wrong_pid_and_reused_creation_time_rejected(self):
  for key,value in(('pid',123),('create_time',1.)):
   info,own,parent,_=self.fixture();info[key]=value;self.assertFalse(w.execute_parent_matches(info,own,parent))
 def test_indirect_parent_or_foreign_parent_identity_rejected(self):
  for key,value in(('ppid',123),('pid',456)):
   info,own,parent,_=self.fixture();parent[key]=value;self.assertFalse(w.execute_parent_matches(info,own,parent))
 def test_wrong_body_or_launcher_exe_and_argv0_rejected(self):
  for which,field in(('own','exe'),('own','argv0'),('parent','exe'),('parent','argv0')):
   info,own,parent,_=self.fixture();row=own if which=='own'else parent
   if field=='argv0':row['cmdline'][0]='C:/unapproved/python.exe'
   else:row[field]='C:/unapproved/python.exe'
   self.assertFalse(w.execute_parent_matches(info,own,parent))
 def test_extra_tail_abbreviation_other_wait_or_recognize_never_exempted(self):
  for transform in(lambda a:a+['--topic','11.05'],lambda a:[s.replace('--execute','--exec')for s in a],lambda a:a[:-1]+['6.0'],lambda a:[s.replace('--execute','--recognize')for s in a]):
   info,own,parent,_=self.fixture();own['cmdline']=transform(own['cmdline']);parent['cmdline']=transform(parent['cmdline']);info['cmdline']=copy.deepcopy(parent['cmdline']);self.assertFalse(w.execute_parent_matches(info,own,parent))
 def test_matching_tail_still_cannot_exempt_other_process(self):
  info,own,parent,_=self.fixture();info['pid']+=1;self.assertFalse(w.execute_parent_matches(info,own,parent))
 def test_nonfinite_unknown_and_long_spawn_time_rejected(self):
  for key,value in(('create_time',float('nan')),('exe',None),('cmdline',None)):
   info,own,parent,_=self.fixture();info[key]=value;self.assertFalse(w.execute_parent_matches(info,own,parent))
  info,own,parent,_=self.fixture();own['create_time']=parent['create_time']+30;self.assertFalse(w.execute_parent_matches(info,own,parent))
 def test_only_current_exact_direct_parent_bypasses_classifier(self):
  info,own,parent,_=self.fixture();factory=lambda pid:SimpleNamespace(as_dict=lambda fields:own if pid==own['pid']else parent)
  with patch.object(w.os,'getpid',return_value=own['pid']),patch.object(w.os,'getppid',return_value=parent['pid']),patch.object(w.resource.psutil,'Process',side_effect=factory),patch.object(w.base,'read',return_value=self.marker(own)),patch.object(w,'original_process_reason',return_value='strict-foreign')as original:
   self.assertIsNone(w.scoped_process_reason(info,own['pid']));original.assert_not_called()
   other=copy.deepcopy(info);other['pid']+=10;self.assertEqual(w.scoped_process_reason(other,own['pid']),'strict-foreign')
 def test_uninspected_parent_goes_to_unchanged_strict_classifier(self):
  info,own,parent,_=self.fixture()
  with patch.object(w.os,'getpid',return_value=own['pid']),patch.object(w.os,'getppid',return_value=parent['pid']),patch.object(w.resource.psutil,'Process',side_effect=w.resource.psutil.AccessDenied(own['pid'])),patch.object(w,'original_process_reason',return_value='strict-unknown'):
   self.assertEqual(w.scoped_process_reason(info,own['pid']),'strict-unknown')
 def test_runtime_and_old_sources_remain_pinned(self):
  self.assertEqual(p.sha(HERE/'run-solution-path-voice-repair-v1.py'),'9b12d46bcbb893619331418119b01cf342ab7f40ba3e95d1ad0ee95061f73660');self.assertEqual(p.sha(HERE/'prepare-solution-path-voice-repair-v1.py'),'97e3e87ee7e95a06e7b0837b8bb7214c5fbf50b506124981ade184b1ad6339de')
  rows=copy.deepcopy(p.RUNTIME_PINS);rows[1]['sha256']='0'*64
  with patch.object(p,'RUNTIME_PINS',rows):self.assertRaises(p.Pending,w.check_sources)
 def test_only_new_private_resource_instance_is_patched(self):
  self.assertIs(w.resource,p.voice_entry.resource);self.assertIs(w.resource.process_reason,w.scoped_process_reason)
  self.assertEqual(w.resource.sha(w.resource.__file__),'9429b70773f3a334dd5fd45d76ecb6b2fa8b2360dfe576aac341099d7adaea5e')
 def test_singleton_owner_token_pid_time_and_command_required(self):
  _,own,_,_=self.fixture();record=self.marker(own);self.assertTrue(w.own_wrapper_marker(record,own))
  for key,value in(('token',''),('owner','foreign'),('pid',123),('createTime',1.),('commandSHA256','0'*64),('child',dict(pid=999))):
   row=copy.deepcopy(record);row[key]=value;self.assertFalse(w.own_wrapper_marker(row,own))
 def test_missing_or_changing_own_marker_cannot_exempt_parent(self):
  info,own,parent,_=self.fixture();factory=lambda pid:SimpleNamespace(as_dict=lambda fields:own if pid==own['pid']else parent);record=self.marker(own);changed=copy.deepcopy(record);changed['token']='changed'
  for effect in(FileNotFoundError('unknown'),[record,changed]):
   with patch.object(w.os,'getpid',return_value=own['pid']),patch.object(w.os,'getppid',return_value=parent['pid']),patch.object(w.resource.psutil,'Process',side_effect=factory),patch.object(w.base,'read',side_effect=effect),patch.object(w,'original_process_reason',return_value='strict-preserved'):
    self.assertEqual(w.scoped_process_reason(info,own['pid']),'strict-preserved')

if __name__=='__main__':unittest.main(verbosity=1)
