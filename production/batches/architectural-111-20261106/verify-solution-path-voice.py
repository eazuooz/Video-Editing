"""Bounded CPU fixtures for the thin11.05 voice preparer; no jobs/models/media."""
from __future__ import annotations
import copy,importlib.util,json,sys,unittest
from pathlib import Path
from unittest.mock import patch
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('solution_voice_under_test',HERE/'prepare-solution-path-voice.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)

class VoicePreparation(unittest.TestCase):
 def setUp(self):
  self.cp,self.path,self.d,self.source=v.current_inputs()
 def test_current_draft_exact14_to48_complete_sentences(self):
  plan,*_=v.draft_plan();self.assertEqual((plan['paragraphCount'],plan['componentCount']),(14,48));self.assertFalse(plan['voiceReady'])
  for n,text in enumerate(self.d['narrationKo'],1):
   rows=[r for r in plan['paragraphMapping']if r['paragraph']==n]
   self.assertEqual(' '.join(r['canonicalText']for r in rows),text)
   for r in rows:self.assertEqual(text[slice(*r['sourceCharRange'])],r['canonicalText'])
 def test_component_count_is_derived_not_hardcoded48(self):
  draft=copy.deepcopy(self.d);draft['narrationKo']=['첫 문장입니다. 두 번째 문장입니다.']+['온전한 설명입니다.']*13
  script,rows=v.sentence_plan(draft,'a'*64);self.assertEqual(len(script['scenes']),15);self.assertEqual(len(rows),15)
 def test_current_not_ready_precedes_profile_and_source_media_validation(self):
  with patch.object(v.core,'validate_profile',side_effect=AssertionError('must not read weights')),patch.object(v,'source_rows',side_effect=AssertionError('must not read source media')):
   with self.assertRaisesRegex(v.Pending,'all8-mode native evidence missing.*provisional'):v.prepare()
 def test_false_original_finality_is_never_overridden(self):
  original=copy.deepcopy(self.d);before=copy.deepcopy(self.cp)
  with patch.object(v.core,'validate_narration',side_effect=AssertionError('must not normalize false')):
   with self.assertRaisesRegex(v.Pending,'preserve false'):v.final_narration(self.d,self.cp)
  self.assertEqual(self.d,original);self.assertEqual(self.cp,before)
 def test_only_true_finality_normalizes_legacy_flags_in_copy(self):
  draft=copy.deepcopy(self.d);cp=copy.deepcopy(self.cp);draft['narrationFinalized']=draft['ttsReady']=True
  cp['expandedNarrationDraft']['finalized']=True;cp['currentProduction']['narrationFinalized']=cp['currentProduction']['ttsReady']=True
  out=v.final_narration(draft,cp);self.assertTrue(out['preTtsEligibility']);self.assertFalse(draft['preTtsEligibility'])
 def test_changed_checkpoint_hash_is_rejected(self):
  changed=copy.deepcopy(self.cp);changed['expandedNarrationDraft']['sha256']='0'*64
  with patch.object(v,'authority',return_value=changed):
   with self.assertRaisesRegex(v.Pending,'actual checkpoint current pin'):v.current_inputs()
 def test_conflicting_duplicate_checkpoint_pin_is_rejected(self):
  changed=copy.deepcopy(self.cp);changed['currentProduction']['expandedNarrationDraft']['sha256']='0'*64
  with patch.object(v,'authority',return_value=changed):
   with self.assertRaisesRegex(v.Pending,'Checkpoint narration pins disagree'):v.current_inputs()
 def test_immutable_provisional_v3_rejects_changed_bytes(self):
  real=v.sha
  with patch.object(v,'sha',side_effect=lambda p:'f'*64 if Path(p).resolve()==self.path else real(p)):
   with self.assertRaises(v.Pending):v.current_inputs()
 def test_source_id_alias_is_private_and_preserves_native_fps(self):
  source=v.read(self.source);before=copy.deepcopy(source);seen=[]
  with patch.object(v.core,'validate_source_row',side_effect=lambda row,slug:seen.append(row)or row):out=v.source_rows(self.source)
  self.assertEqual(source,before);self.assertNotIn('id',source['sources'][0]);self.assertEqual(out[0]['id'],source['sources'][0]['sourceId']);self.assertNotEqual(out[0]['id'],'S-HD')
  self.assertEqual(out[0].get('fps'),source['sources'][0].get('fps'));self.assertEqual(seen[0]['sourceId'],seen[0]['id'])
 def test_conflicting_source_id_is_rejected(self):
  source=v.read(self.source);source['sources'][0]['id']='S-HD'
  with patch.object(v,'read',return_value=source):
   with self.assertRaisesRegex(v.Pending,'Conflicting source identity'):v.source_rows(self.source)
 def test_old_topic_and_clause_policy_cannot_enter(self):
  with self.assertRaisesRegex(v.Pending,'only prepares'):v.prepare(topic='07.04')
  with self.assertRaisesRegex(v.Pending,'no old06/07'):v.prepare(component_path=Path('old-clause-plan.json'))
 def test_placeholder_and_changed_paragraph_counts_are_rejected(self):
  for value in ('TODO placeholder','[pending]'):
   draft=copy.deepcopy(self.d);draft['narrationKo'][0]=value
   with self.assertRaises(v.Pending):v.sentence_plan(draft,'a'*64)
  draft=copy.deepcopy(self.d);draft['paragraphsEn'].pop()
  with self.assertRaisesRegex(v.Pending,'Complete14'):v.sentence_plan(draft,'a'*64)
 def test_subset_pilot_and_boolean_qa_are_not_all8_capture(self):
  with patch.object(v,'read',side_effect=[{'topicId':'11.05','captureComplete':True,'capturedModes':['construction'],'remainingModes':[],'modeSources':{}},{'voicePreparationAllowed':True},v.read(v.CONFIG)]):
   with self.assertRaisesRegex(v.Pending,'All8 actual modes'):v.native_qa('unused-evidence','unused-qa')
 def test_other_topic_native_preview_scope_is_rejected(self):
  with self.assertRaisesRegex(v.Pending,'selected11.05 media'):v.media_file(v.MEDIA/'shorts-leveldesign-07-04/preview.png')
 def test_forged_ready_cannot_stage_around_actual_gates(self):
  forged={'topicId':'11.05','voiceReady':True,'sourceNarration':v.pin(self.path),'nativeEvidence':{'path':str(v.PROJECT/'native-evidence-v1.json')},'nativeVisualQa':{'path':str(v.PROJECT/'native-visual-qa-v1.json')}}
  with patch.object(v.core,'immutable_stage',side_effect=AssertionError('must not write')):
   with self.assertRaisesRegex(v.Pending,'all8-mode native evidence missing'):v.immutable_stage(forged)

if __name__=='__main__':unittest.main(verbosity=2)
