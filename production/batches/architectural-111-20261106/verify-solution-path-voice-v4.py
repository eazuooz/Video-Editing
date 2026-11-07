"""Fifteen bounded CPU fixtures; synthetic pixels are never native QA evidence."""
from __future__ import annotations
import copy,importlib.util,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('solution_voice_v4_under_test',HERE/'prepare-solution-path-voice-v4.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
class VoicePreparationV4(unittest.TestCase):
 def setUp(self):self.cp,self.path,self.d,self.source=v.current_inputs()
 def test_current14_to48_exact_reconstruction(self):
  plan,*_=v.draft_plan();self.assertEqual((plan['paragraphCount'],plan['componentCount']),(14,48));self.assertFalse(plan['voiceReady'])
  for n,text in enumerate(self.d['narrationKo'],1):
   rows=[r for r in plan['paragraphMapping']if r['paragraph']==n];self.assertEqual(' '.join(r['canonicalText']for r in rows),text)
   for r in rows:self.assertEqual(text[slice(*r['sourceCharRange'])],r['canonicalText'])
 def test_component_count_is_derived(self):
  d=copy.deepcopy(self.d);d['narrationKo']=['첫 문장입니다. 두 번째 문장입니다.']+['온전한 설명입니다.']*13
  script,rows=v.sentence_plan(d,'a'*64);self.assertEqual(len(script['scenes']),15);self.assertEqual(len(rows),15)
 def test_current_rejects_before_profile_or_media(self):
  with patch.object(v.core,'validate_profile',side_effect=AssertionError('no weights')),patch.object(v,'source_rows',side_effect=AssertionError('no media')):
   with self.assertRaisesRegex(v.Pending,'provisional'):v.prepare()
 def test_false_finality_is_not_overridden(self):
  before=copy.deepcopy(self.d);cp=copy.deepcopy(self.cp)
  with patch.object(v.core,'validate_narration',side_effect=AssertionError('no false normalization')):
   with self.assertRaisesRegex(v.Pending,'preserve false'):v.final_narration(self.d,self.cp)
  self.assertEqual(before,self.d);self.assertEqual(cp,self.cp)
 def test_all_actual_finality_fields_are_required(self):
  d=copy.deepcopy(self.d);d['narrationFinalized']=d['ttsReady']=True
  with self.assertRaisesRegex(v.Pending,'provisional'):v.final_narration(d,self.cp)
 def test_changed_or_disagreeing_checkpoint_pins_rejected(self):
  for location in('expandedNarrationDraft','currentProduction'):
   cp=copy.deepcopy(self.cp)
   if location=='expandedNarrationDraft':cp[location]['sha256']='0'*64
   else:cp[location]['expandedNarrationDraft']['sha256']='0'*64
   with patch.object(v,'authority',return_value=cp):self.assertRaises(v.Pending,v.current_inputs)
 def test_actual_checkpoint_can_select_new_version_path(self):
  with tempfile.TemporaryDirectory()as tmp:
   project=Path(tmp);source=project/'footage-current.json';source.write_text(json.dumps(v.read(self.source)),encoding='utf-8');d=copy.deepcopy(self.d);d['sourceFootage']=v.pin(source)
   narration=project/'narration-future-fixture.json';narration.write_text(json.dumps(d,ensure_ascii=False),encoding='utf-8');cp=copy.deepcopy(self.cp);cp['expandedNarrationDraft']=dict(v.pin(narration),finalized=False);cp['narrationDraftSHA256']=v.sha(narration);cp['sourceFootage']=v.pin(source);cp['currentProduction']['expandedNarrationDraft']=v.pin(narration);cp['currentProduction']['sourceFootage']=v.pin(source)
   with patch.object(v,'PROJECT',project),patch.object(v,'authority',return_value=cp):
    actual=v.current_inputs();self.assertEqual(actual[1],narration);self.assertFalse(actual[2]['ttsReady'])
 def test_source_id_alias_is_private_and_native_fps_retained(self):
  before=v.read(self.source)
  with patch.object(v.core,'validate_source_row',side_effect=lambda r,slug:r):rows=v.source_rows(self.source)
  self.assertNotIn('id',before['sources'][0]);self.assertEqual(rows[0]['id'],before['sources'][0]['sourceId']);self.assertNotEqual(rows[0]['id'],'S-HD');self.assertEqual((rows[0]['fpsNumerator'],rows[0]['fpsDenominator']),(60000,1001));self.assertEqual(v.read(self.source),before)
 def test_source_footage_hash_change_rejected(self):
  cp=copy.deepcopy(self.cp);cp['sourceFootage']['sha256']='0'*64
  with patch.object(v,'authority',return_value=cp):
   with self.assertRaisesRegex(v.Pending,'source-footage pins disagree'):v.current_inputs()
 def test_old_topics_clause_policies_and_placeholders_rejected(self):
  self.assertRaises(v.Pending,v.prepare,topic='07.04');self.assertRaises(v.Pending,v.prepare,component_path=Path('old06-clause.json'))
  d=copy.deepcopy(self.d);d['narrationKo'][0]='TODO placeholder';self.assertRaises(v.Pending,v.sentence_plan,d,'a'*64)
 def test_subset_native_boolean_qa_is_insufficient(self):
  cfg=v.read(v.CONFIG)
  with patch.object(v,'read',side_effect=[dict(topicId='11.05',captureComplete=True,capturedModes=['construction'],remainingModes=[],modeSources={}),dict(voicePreparationAllowed=True),cfg]):
   with self.assertRaisesRegex(v.Pending,'All8 actual modes'):v.native_qa('unused','unused')
 def test_wrong_native_physical_fingerprint_rejected(self):
  cfg=v.read(v.CONFIG);modes=[r['id']for r in cfg['modes']];e=dict(topicId='11.05',captureComplete=True,capturedModes=modes,remainingModes=[],modeSources={m:{}for m in modes},physicalInputFingerprint='a'*64);staged=dict(sourceStageComplete=True,fingerprint='b'*64,config=cfg)
  with patch.object(v,'read',side_effect=[e,{},cfg,staged]):
   with self.assertRaisesRegex(v.Pending,'source/config fingerprint differs'):v.native_qa('unused','unused')
 def synthetic_sample(self):
  from PIL import Image,ImageDraw
  tmp=tempfile.TemporaryDirectory();self.addCleanup(tmp.cleanup);base=Path(tmp.name)/v.SLUG;folder=base/'native-attempts/fixture/capture/construction';image_path=folder/'player/0000.jpg';image_path.parent.mkdir(parents=True);im=Image.new('RGB',(1920,1080),(25,60,90));ImageDraw.Draw(im).rectangle((250,100,900,750),fill=(210,160,40));im.save(image_path,quality=93)
  phone=base/'qa/actual375.png';phone.parent.mkdir();
  with Image.open(image_path)as im:im.convert('RGB').resize((375,211),Image.Resampling.LANCZOS).save(phone)
  sample=dict(camera='player',frame=0,nativeImage=v.pin(image_path),mobilePreview=v.pin(phone));index={str(image_path):dict(mode='construction',camera='player',sha256=v.sha(image_path))};previews={str(phone):v.sha(phone)}
  return base,folder,sample,v.read(v.CONFIG),index,previews
 def test_native_image_source_sha_is_required(self):
  base,folder,sample,cfg,index,previews=self.synthetic_sample()
  with patch.object(v,'BASE',base):
   self.assertEqual(len(v.sample_proof(sample,'construction',folder,cfg,index,previews)),2)
   sample['nativeImage']['sha256']='0'*64;self.assertRaises(v.Pending,v.sample_proof,sample,'construction',folder,cfg,index,previews)
 def test_mobile_pixel_identity_and_selected_scope_required(self):
  from PIL import Image
  base,folder,sample,cfg,index,previews=self.synthetic_sample();phone=Path(sample['mobilePreview']['path']);Image.new('RGB',(375,211),(1,2,3)).save(phone);sample['mobilePreview']=v.pin(phone);previews[str(phone)]=v.sha(phone)
  with patch.object(v,'BASE',base):
   with self.assertRaisesRegex(v.Pending,'375 preview pixels'):v.sample_proof(sample,'construction',folder,cfg,index,previews)
   self.assertRaises(v.Pending,v.media_file,base.parent/'shorts-leveldesign-07-04/preview.png')
 def test_forged_ready_cannot_stage(self):
  forged=dict(topicId='11.05',voiceReady=True,sourceNarration=v.pin(self.path),nativeEvidence=dict(path=str(v.PROJECT/'native-evidence-v4.json')),nativeVisualQa=dict(path=str(v.PROJECT/'native-visual-qa-v4.json')))
  with patch.object(v.core,'immutable_stage',side_effect=AssertionError('no staging')):
   with self.assertRaisesRegex(v.Pending,'provisional'):v.immutable_stage(forged)
if __name__=='__main__':unittest.main(verbosity=2)
