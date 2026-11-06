"""Focused fixtures for preparation only. Never imports/launches the TTS engine."""
import importlib.util,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('selected_voice',HERE/'prepare-selected-voice.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)

def draft():return {'topicId':'07.04','titleKo':'풍경을 가리는 이유','readyForDraftIntegration':True,'preTtsEligibility':True,'narrationKo':['벽이 시선을 막습니다. 틈에서는 등대가 보입니다.'], 'paragraphsEn':['The wall blocks the view. The lighthouse appears through the gap.']}
class SelectedVoice(unittest.TestCase):
    def test_false_finality_flag_rejected(self):
        d=draft();d['preTtsEligibility']=False
        with self.assertRaisesRegex(v.Pending,'not finalized'):v.validate_narration(d)
    def test_placeholder_rejected_even_if_flags_claim_ready(self):
        d=draft();d['narrationKo'][0]='[실제 게임 도입 미확정]'
        with self.assertRaisesRegex(v.Pending,'placeholder'):v.validate_narration(d)
        d=draft();d['placeholderParagraphs']=[1]
        with self.assertRaises(v.Pending):v.validate_narration(d)
    def test_semantic_groups_reconstruct_actual_sentences(self):
        d=draft();ko=v.validate_narration(d);p={'sourceNarrationSHA256':'exact','paragraphs':[{'paragraph':1,'components':[{'text':'벽이 시선을 막습니다.','reason':'원인 설명 완료'},{'text':'틈에서는 등대가 보입니다.','reason':'가시 결과 설명'}]}]}
        groups=v.components_for(ko,p,'exact');scenes,mapping=v.make_scenes(d,groups)
        self.assertEqual(' '.join(s['lines'][0] for s in scenes['scenes']),ko[0]);self.assertEqual([r['sceneId'] for r in mapping],['p001-c01','p001-c02'])
        self.assertEqual(mapping[1]['sourceCharRange'][1],len(ko[0]))
    def test_arbitrary_mid_sentence_split_and_stale_plan_rejected(self):
        ko=draft()['narrationKo'];p={'sourceNarrationSHA256':'exact','paragraphs':[{'paragraph':1,'components':[{'text':'벽이 시선을','reason':'bad cut'},{'text':'막습니다. 틈에서는 등대가 보입니다.','reason':'bad cut'}]}]}
        with self.assertRaisesRegex(v.Pending,'bisects'):v.components_for(ko,p,'exact')
        with self.assertRaisesRegex(v.Pending,'stale'):v.components_for(ko,p,'different')
    def test_rights_unverified_source_rejected_before_file_read(self):
        r={'selectedForCut':True,'rightsReviewed':False}
        with self.assertRaisesRegex(v.Pending,'rights'):v.validate_source_row(r,'shorts-leveldesign-07-04')
    def test_selected_source_requires_actual_hash_fhd_and_view(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'footage-fixture.bin';p.write_bytes(b'fixture-not-real-footage')
            r={'id':'fixture','path':str(p),'sha256':v.sha(p),'selectedForCut':True,'rightsVerified':True,'decodedDimensionsVerified':True,'width':1920,'height':1080,'visualSequenceInspected':True,'editorialRole':'independent-gameplay'}
            with patch.object(v,'selected_path',side_effect=lambda p,slug:Path(p)):
                self.assertEqual(v.validate_source_row(r,'fixture')['id'],'fixture')
                for key,bad in [('height',720),('visualSequenceInspected',False),('sha256','0'*64)]:
                    changed=dict(r);changed[key]=bad
                    with self.assertRaises(v.Pending):v.validate_source_row(changed,'fixture')
    def test_native_sample_qa_stale_or_missing_capture_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'evidence.json';p.write_text('{}');e={'topicId':'07.04','fingerprint':'a'*64,'captureComplete':True,'captureProofs':[]}
            q={'voicePreparationAllowed':True,'nativeFingerprint':'a'*64,'nativeEvidenceSHA256':'stale'}
            with self.assertRaisesRegex(v.Pending,'stale'):v.validate_native(e,q,p,'shorts-leveldesign-07-04')
            q['nativeEvidenceSHA256']=v.sha(p)
            with self.assertRaisesRegex(v.Pending,'artifact pins'):v.validate_native(e,q,p,'shorts-leveldesign-07-04')
    def test_unready_object_cannot_write_stage(self):
        with self.assertRaisesRegex(v.Pending,'Unready'):v.immutable_stage({'ready':False})

if __name__=='__main__':unittest.main()
