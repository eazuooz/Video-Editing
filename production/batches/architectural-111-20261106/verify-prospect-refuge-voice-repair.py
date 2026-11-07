"""Synthetic CPU WAV/provenance checks only; never real stage/model/lease jobs."""
import argparse,copy,hashlib,importlib.util,json,struct,tempfile,unittest,wave
from pathlib import Path
from unittest.mock import patch
HERE=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('prospect_voice_repair_cpu',HERE/'run-prospect-refuge-voice-repair.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
def dump(p,obj):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf8');return dict(path=str(p),sha256=m.sha(p))
def wav(p,value,n=48):
 p.parent.mkdir(parents=True,exist_ok=True)
 with wave.open(str(p),'wb')as w:w.setparams((1,2,24000,n,'NONE','not compressed'));w.writeframes(struct.pack('<h',value)*n)
 return m.base.wav_info(p)

class RepairTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory(prefix='06-only-subset-repair-cpu-');cls.root=Path(cls.tmp.name);cls.original_root=m.ROOT;cls.original_base_root=m.base.ROOT;cls.original_fp=m.SOURCE_OLD_FINGERPRINT;m.ROOT=cls.root;m.base.ROOT=cls.root
  realplan=m.read(m.PLAN);realold=m.read(realplan['oldVoiceEvidence']['path']);ids=[s['id']for s in realold['identity']['scenes']]
  cls.scenes=[dict(id=sid,lines=[f'Synthetic complete sentence {sid}.'])for sid in ids];profile=dict(protocol='synthetic-profile',topicId='06.02',tts=dict(language='Korean',speechSpeed=1),modelPins=[dict(path='model',sha256='1'*64)],referenceSHA256='2'*64,referenceTextSHA256='3'*64,engine=dict(path='engine',sha256='4'*64),guard=dict(path='guard',sha256='5'*64),rawPcmPolicy=dict(noFade=True,speechSpeed=1))
  identity=dict(profile,scenes=cls.scenes);oldfp=m.digest(identity);m.SOURCE_OLD_FINGERPRINT=oldfp;cls.oldout=cls.root/'shared/output/architectural-111-20261106/06-02/voice-attempts'/oldfp[:24]
  for i,s in enumerate(cls.scenes):wav(cls.oldout/'chunks'/(s['id']+'-scene.wav'),i+1)
  mapping=[dict(sceneId=s['id'],paragraph=int(s['id'][1:4]),canonicalText=s['lines'][0])for s in cls.scenes];oldprov=dict(topicId='06.02',fingerprint=oldfp,identity=identity,paragraphMapping=mapping)
  old=m.original['canonical_outputs'](oldprov,cls.oldout,{})
  cls.oldpin=dump(cls.oldout/'voice-complete-proof.json',old);cls.old=old
  semantic=dump(cls.root/'projects/shorts-leveldesign-06-02/semantic.json',dict(sceneIds=ids));asr=dump(cls.root/'old-asr.json',dict(voiceFingerprint=oldfp,aggregateSHA256=old['aggregateWav']['sha256'],timingSHA256=old['timing']['sha256'],takes=[{}]*96,boundaryWindows=[{}]*95));levels=dump(cls.root/'old-levels.json',dict(voiceFingerprint=oldfp,canonicalWav=old['aggregateWav'],asrReview=asr,takes=[{}]*96,paragraphs=[{}]*25,joins=[{}]*95,flags=[dict(kind='sustained-take-word-body-decline',sceneId='p004-c04')]))
  targetOrder=[s['id']for s in cls.scenes if s['id']in m.REPAIR_OLD_IDS];content=dump(cls.root/'root-content.json',dict(schemaVersion='06-02-root-raw-voice-content-review-v1',topicId='06.02',oldVoiceEvidence=cls.oldpin,rawAsrReview=asr,rawLevelReview=levels,repairSceneIds=targetOrder))
  rows=[dict(oldSceneId=s['id'],newSceneId=s['id'],canonicalText=s['lines'][0],sourceWav=w,sourceVoiceEvidence=dict(cls.oldpin,fingerprint=oldfp),reuseReason='Synthetic exact safe raw byte reuse')for s,w in zip(cls.scenes,old['sceneWavs'])if s['id']not in m.REPAIR_OLD_IDS]
  cls.plan=dict(schemaVersion='06-02-voice-subset-repair-plan-v1',topicId='06.02',sourceNarrationSHA256='a'*64,semanticComponents=semantic,oldVoiceEvidence=cls.oldpin,oldAsrReview=asr,oldLevelReview=levels,rootContentReview=content,repairSceneIds=targetOrder,expectedFullComponentCount=96,expectedMissingComponentCount=15,expectedReuseComponentCount=81,subsetReuse=rows)
  cls.planpath=cls.root/'plan.json';dump(cls.planpath,cls.plan);stage=cls.root/'projects/shorts-leveldesign-06-02/production/voice-preparation/old-stage'
  cls.full=dict(oldprov,slug='shorts-leveldesign-06-02',ready=True,inputs=[semantic],script=dict(scenes=[dict(s,title='synthetic')for s in cls.scenes]),manifest=dict(slug='shorts-leveldesign-06-02',sourceNarrationSHA256='a'*64,paths=dict(script='old.json'),tts=dict(model='model',reference='reference',referenceText='reftext',outputDir=cls.oldout.relative_to(cls.root).as_posix()),editing=dict(exampleSeconds=0),rawPcmPolicy=identity['rawPcmPolicy'],synthesisIdentity=oldfp),stagingDirectory=str(stage),voiceOutputDirectory=str(cls.oldout),qwenSynthesisArgv=['python','-u','-X','utf8','render_narration.py','--project','shorts-leveldesign-06-02','--manifest','old.json','--batch-size','1','--device','cuda:0'])
  cls.new=m.reselect_full(cls.full,cls.plan,cls.planpath);cls.repair=m.repair_spec(cls.new,cls.plan,cls.planpath);cls.prov=dict(cls.new,repair=cls.repair);cls.out=Path(cls.new['voiceOutputDirectory']);cls.folder=Path(cls.repair['stagingDirectory'])
  cls.stage_fixture();cls.attempt=cls.out/'engine-attempts/synthetic';cls.attempt.mkdir(parents=True);cls.req=dict(protocol=m.base.PROTOCOL,fingerprint=cls.prov['fingerprint'],identity=cls.prov['identity'],repairFingerprint=cls.repair['fingerprint'],command=cls.repair['command'],engineSceneScope='missing-subset-only',engineSceneIds=[s['id']for s in cls.repair['missing']],subsetPins=m.subset_pins(cls.prov));cls.reqpin=dump(cls.attempt/'request.json',cls.req);cls.pending=dict(attempt=str(cls.attempt),requestPins=[cls.reqpin])
 @classmethod
 def stage_fixture(cls):
  for name,obj in [('narration-missing-only.json',cls.repair['script']),('voice-missing-only-manifest.json',cls.repair['manifest']),('subset-repair-preparation.json',dict(repairFingerprint=cls.repair['fingerprint'],fullVoiceFingerprint=cls.prov['fingerprint'],repairIdentity=cls.repair['identity'],command=cls.repair['command']))]:dump(cls.folder/name,obj)
  (cls.folder/'repair-adapter-source.py').write_bytes(Path(m.__file__).read_bytes())
 @classmethod
 def tearDownClass(cls):m.ROOT=cls.original_root;m.base.ROOT=cls.original_base_root;m.SOURCE_OLD_FINGERPRINT=cls.original_fp;cls.tmp.cleanup()
 def test_same96_text_new_identity_output_and_staging(self):
  self.assertEqual(self.new['identity']['scenes'],self.full['identity']['scenes']);self.assertNotEqual(self.new['fingerprint'],self.full['fingerprint']);self.assertNotEqual(self.new['voiceOutputDirectory'],self.full['voiceOutputDirectory']);self.assertNotEqual(self.new['stagingDirectory'],self.full['stagingDirectory']);self.assertEqual(m.digest(self.new['identity']),self.new['fingerprint'])
 def test_exact15_missing_81_reuse(self):self.assertEqual((len(self.repair['missing']),len(self.repair['rows'])),(15,81));self.assertEqual({s['id']for s in self.repair['missing']},m.REPAIR_OLD_IDS)
 def test_81_never_enter_engine_retry(self):self.assertFalse({x['newSceneId']for x in self.repair['rows']}&{s['id']for s in self.repair['script']['scenes']})
 def test_engine_preserves_exact15_original_order_and_text(self):self.assertEqual(self.repair['missing'],[s for s in self.scenes if s['id']in m.REPAIR_OLD_IDS])
 def test_profile_model_reference_guard_raw_policy_unchanged(self):
  for k in('tts','modelPins','referenceSHA256','referenceTextSHA256','engine','guard','rawPcmPolicy'):self.assertEqual(self.new['identity'][k],self.full['identity'][k])
 def test_full_and_subset_manifest_bind_new_output(self):self.assertEqual(self.new['manifest']['synthesisIdentity'],self.new['fingerprint']);self.assertEqual(self.repair['manifest']['tts']['outputDir'],self.new['manifest']['tts']['outputDir']);self.assertEqual(self.repair['manifest']['repairSelection'],self.new['identity']['repairSelection'])
 def test_only_manifest_cli_argument_changes(self):self.assertEqual(self.repair['command'][:8],self.full['qwenSynthesisArgv'][:8]);self.assertEqual(self.repair['command'][9:],self.full['qwenSynthesisArgv'][9:])
 def test_old_same_text_output_cannot_be_adopted_as_new(self):
  with self.assertRaises(ValueError):m.validate_reuse(self.full,self.plan)
 def test_target_cannot_reenter_reuse(self):
  p=copy.deepcopy(self.plan);p['subsetReuse'][0]['oldSceneId']='p004-c01'
  with self.assertRaises(ValueError):m.validate_reuse(self.new,p)
 def test_changed_repair_set_rejected(self):
  p=copy.deepcopy(self.plan);p['repairSceneIds'][0]='p001-c01'
  with self.assertRaises(ValueError):m.validate_reuse(self.new,p)
 def test_changed_reused_text_rejected(self):
  p=copy.deepcopy(self.plan);p['subsetReuse'][0]['canonicalText']+='wrong'
  with self.assertRaises(ValueError):m.validate_reuse(self.new,p)
 def test_changed_pcm_metadata_rejected(self):
  p=copy.deepcopy(self.plan);p['subsetReuse'][0]['sourceWav']['pcmSHA256']='0'*64
  with self.assertRaises(ValueError):m.validate_reuse(self.new,p)
 def test_duplicate_remapped_reuse_rejected(self):
  p=copy.deepcopy(self.plan);p['subsetReuse'][0]['newSceneId']=p['subsetReuse'][1]['newSceneId']
  with self.assertRaises(ValueError):m.validate_reuse(self.new,p)
 def test_changed_reference_rejected(self):
  p=copy.deepcopy(self.new);p['identity']['referenceSHA256']='0'*64
  with self.assertRaises(ValueError):m.validate_reuse(p,self.plan)
 def test_changed_current_complete_sentence_rejected(self):
  p=copy.deepcopy(self.new);p['identity']['scenes'][0]['lines']=['rewrite']
  with self.assertRaises(ValueError):m.validate_reuse(p,self.plan)
 def test_changed_narration_hash_rejected(self):
  p=copy.deepcopy(self.plan);p['sourceNarrationSHA256']='0'*64
  with self.assertRaises(ValueError):m.validate_reuse(self.new,p)
 def test_mutable_publication_pointer_rejected(self):
  p=copy.deepcopy(self.plan);p['oldVoiceEvidence']=dump(self.root/'mutable-evidence.json',self.old)
  with self.assertRaises(ValueError):m.validate_reuse(self.new,p)
 def test_asr_different_old_identity_rejected(self):
  p=copy.deepcopy(self.plan);a=m.read(p['oldAsrReview']['path']);a['voiceFingerprint']='0'*64;p['oldAsrReview']=dump(self.root/'wrong-asr.json',a)
  with self.assertRaises(ValueError):m.repair_spec(self.new,p,self.planpath)
 def test_reused_declining_take_rejected(self):
  p=copy.deepcopy(self.plan);a=m.read(p['oldLevelReview']['path']);a['flags'].append(dict(kind='sustained-take-word-body-decline',sceneId='p001-c01'));p['oldLevelReview']=dump(self.root/'wrong-levels.json',a)
  with self.assertRaises(ValueError):m.repair_spec(self.new,p,self.planpath)
 def test_full25_scope_not_partial_asr(self):
  p=copy.deepcopy(self.plan);a=m.read(p['oldAsrReview']['path']);a['takes']=a['takes'][:-1];p['oldAsrReview']=dump(self.root/'partial-asr.json',a)
  with self.assertRaises(ValueError):m.repair_spec(self.new,p,self.planpath)
 def test_root_selection_disposition_required(self):
  p=copy.deepcopy(self.plan);a=m.read(p['rootContentReview']['path']);a['repairSceneIds']=[];p['rootContentReview']=dump(self.root/'wrong-content.json',a)
  with self.assertRaises(ValueError):m.repair_spec(self.new,p,self.planpath)
 def test_pending_request_exact_subset_source_provenance(self):self.assertEqual(m.validate_launch_request(self.prov,self.out,self.pending),self.attempt)
 def test_pending_cannot_switch_back_to_full_script(self):
  req=copy.deepcopy(self.req);req['engineSceneIds']=[s['id']for s in self.scenes];p=dump(self.attempt/'bad-request.json',req)
  with patch.object(m,'read',side_effect=lambda path:req if Path(path)==self.attempt/'request.json'else json.loads(Path(path).read_text(encoding='utf8'))),patch.object(m,'sha',side_effect=lambda path:p['sha256']if Path(path)==self.attempt/'request.json'else hashlib.sha256(Path(path).read_bytes()).hexdigest()):
   with self.assertRaises(RuntimeError):m.validate_launch_request(self.prov,self.out,dict(self.pending,requestPins=[dict(path=str(self.attempt/'request.json'),sha256=p['sha256'])]))
 def test_adapter_snapshot_tamper_even_rebound_outer_pins_rejected(self):
  file=self.folder/'repair-adapter-source.py';old=file.read_bytes();file.write_bytes(b'changed adapter');req=copy.deepcopy(self.req);req['subsetPins']=m.subset_pins(self.prov);oldreq=(self.attempt/'request.json').read_bytes();rp=dump(self.attempt/'request.json',req)
  try:
   with self.assertRaises(RuntimeError):m.validate_launch_request(self.prov,self.out,dict(self.pending,requestPins=[rp]))
  finally:file.write_bytes(old);(self.attempt/'request.json').write_bytes(oldreq)
 def test_canonical_requires_validated_missing_only_engine(self):
  with self.assertRaises(RuntimeError):m.canonical_outputs(self.prov,self.out,{})
 def test_exact_full_concat_retains81bytes_and_marks15new(self):
  chunks=self.out/'chunks';chunks.mkdir(parents=True,exist_ok=True);oldmap={s['id']:w for s,w in zip(self.scenes,self.old['sceneWavs'])};parts=[]
  for i,s in enumerate(self.scenes):
   dest=chunks/(s['id']+'-scene.wav')
   if s['id']in m.REPAIR_OLD_IDS:wav(dest,1000+i)
   else:dest.write_bytes(Path(oldmap[s['id']]['path']).read_bytes());self.assertEqual(m.sha(dest),oldmap[s['id']]['sha256'])
   with wave.open(str(dest),'rb')as w:parts.append(w.readframes(w.getnframes()))
  engine=dict(engineSceneScope='missing-subset-only',subsetAggregateAndTimingValidated=True,engineSceneIds=[s['id']for s in self.repair['missing']],subsetInputs=[])
  proof=m.canonical_outputs(self.prov,self.out,engine);self.assertFalse(proof['engineSpokeFullCombinedScript']);self.assertEqual(proof['rawSceneCount'],96);self.assertEqual(len(proof['reusedRawScenes']),81);self.assertEqual(proof['aggregateWav']['pcmSHA256'],hashlib.sha256(b''.join(parts)).hexdigest())
 def test_readonly_prepare_never_stage_or_launch(self):
  args=argparse.Namespace(topic='06.02',repair_plan=str(self.planpath),semantic_components='not-used',native_evidence='not-used',native_qa='not-used')
  with patch.object(m,'PLAN',self.planpath),patch.object(m,'PLAN_SHA256',m.sha(self.planpath)),patch.dict(m.original,{'prepared':lambda args:self.full}),patch.object(m.base.prep,'immutable_stage',side_effect=AssertionError('no stage')),patch.object(m.base.subprocess,'Popen',side_effect=AssertionError('no model')):
   result=m.prepared(args);self.assertEqual(len(result['repair']['missing']),15)

if __name__=='__main__':unittest.main(verbosity=2)
