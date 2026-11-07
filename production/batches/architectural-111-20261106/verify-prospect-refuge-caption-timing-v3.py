"""Bounded CPU-only actual-word proof + synthetic tamper checks; no jobs/writes."""
import copy,hashlib,importlib.util,unittest
from pathlib import Path
from unittest.mock import patch
HERE=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('prospect_caption_v3_cpu',HERE/'build-prospect-refuge-caption-timing-v3.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)

class WholeWordDisplayTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.n,cls.plan,cls.clauses,cls.anchors=m.previous.sources();cls.proof=m.read(m.SUPPORT);cls.voice=m.read(cls.proof['sourceVoiceEvidence']['path']);cls.review=m.read(cls.proof['sourceAsrReview']['path']);cls.binding=m.previous.voice_binding(cls.voice,cls.review,cls.n,cls.plan);cls.takes={t['task']['sceneId']:t for t in cls.review['takes']};cls.parts={p['sceneId']:p for p in cls.binding['physicalComponents']};cls.support=m.boundary_support(cls.binding);cls.result=m.previous.build(cls.n,cls.plan,cls.clauses,cls.anchors,cls.review,cls.binding,cls.support)
 def reject(self,change,binding=None):
  p=copy.deepcopy(self.proof);change(p)
  with self.assertRaises(m.Pending):m.validate_added_support(p,self.binding if binding is None else binding)
 def test_actual_missing_whole_word_edge_is_exact_sample_not_ratio(self):
  p=self.parts['p010-c04'];aligned=m.previous.old.aligned_sentence(p,self.takes['p010-c04']);ss=next(s for s in self.binding['sentences']if s['sceneId']=='p010-c04');before=m.previous.assemble_logical(ss,[p],{'p010-c04':aligned})
  for offset in(42,43):
   with self.assertRaises(m.Pending):m.previous.char_boundary(before,offset)
  current=next(s for s in self.result['sentences']if s['sceneId']=='p010-c04')
  for offset in(42,43):self.assertEqual(m.previous.char_boundary(current,offset)['sample']-p['startSample'],124320)
  self.assertIn('5',current['alignmentReview']['recognizedLiteral']);self.assertTrue(current['alignmentReview']['comparison']['characterDifferences']);self.assertFalse(current['alignmentReview']['aliasesApplied'])
 def test_all472_requested_boundaries_resolve_without_rewriting(self):
  count=0
  for s,g,a in zip(self.result['sentences'],self.clauses['groups'],self.anchors['groups']):
   offsets={0,len(g['ko'])}
   for cue in g['koCues']:offsets.update(cue['groupCharRange'])
   for cue in a['cues']:offsets.update(cue['koGroupCharRange'])
   for offset in offsets:m.previous.char_boundary(s,offset);count+=1
  self.assertEqual(count,472)
 def test_same190ko234en_literal_ids_and_source_text(self):
  for lang,count in[('ko',190),('en',234)]:
   expected=[c for g in self.clauses['groups']for c in g[lang+'Cues']];actual=self.result['captions'][lang];self.assertEqual(len(actual),count);self.assertEqual([(r['id'],r['text'])for r in actual],[(r['id'],r['text'])for r in expected]);self.assertTrue(all(len(r['lines'])<=2 for r in actual))
  self.assertFalse(self.result['automaticSpeechPass']);self.assertFalse(self.result['actualListening'])
 def test_inherited_p14_whole_word_support_and_raw_diff_unchanged(self):
  p=self.parts['p014-c03'];ss=next(s for s in self.result['sentences']if s['sceneId']=='p014-c03')
  self.assertEqual(m.previous.char_boundary(ss,13)['sample']-p['startSample'],36000);self.assertEqual(m.previous.char_boundary(ss,14)['sample']-p['startSample'],36000);self.assertIn('세자리',ss['alignmentReview']['recognizedLiteral']);self.assertFalse(ss['alignmentReview']['aliasesApplied'])
 def test_changed_pcm_rejected(self):self.reject(lambda p:p['bindings'][0]['rawWav'].__setitem__('pcmSHA256','0'*64))
 def test_changed_wav_rejected(self):self.reject(lambda p:p['bindings'][0]['rawWav'].__setitem__('sha256','0'*64))
 def test_changed_char_scope_rejected(self):self.reject(lambda p:p['bindings'][0].__setitem__('canonicalCharOffsets',[41,43]))
 def test_changed_word_index_rejected(self):self.reject(lambda p:p['bindings'][0].__setitem__('recognizedWordIndex',7))
 def test_one_sample_timestamp_drift_rejected(self):self.reject(lambda p:p['bindings'][0].__setitem__('boundaryRawSampleInTake',124321))
 def test_changed_word_end_rejected(self):self.reject(lambda p:p['bindings'][0].__setitem__('recognizedWordLocalSeconds',[4.68,5.18+1/24000]))
 def test_numeral_alias_rejected(self):self.reject(lambda p:p['bindings'][0].__setitem__('followingRecognizedWordLiteral',' 다섯 요소입니다.'))
 def test_other_voice_rejected(self):self.reject(lambda p:p.__setitem__('voiceFingerprint','0'*64))
 def test_other_source_rejected(self):self.reject(lambda p:p['sourceNarration'].__setitem__('sha256','0'*64))
 def test_extra_support_rejected(self):self.reject(lambda p:p['bindings'].append(copy.deepcopy(p['bindings'][0])))
 def test_two_physical_units_rejected(self):
  b=copy.deepcopy(self.binding);next(s for s in b['sentences']if s['sceneId']=='p010-c04')['physicalSceneIds']=['p010-c04','p010-c05'];self.reject(lambda p:None,b)
 def test_no_hearing_or_alias_claim_allowed(self):self.reject(lambda p:p.__setitem__('automaticSpeechPass',True))
 def test_frozen_previous_source_and_v3_input_fingerprint(self):
  self.assertEqual(m.sha(m.PREVIOUS),m.PREVIOUS_SHA)
  base=dict(schemaVersion='old',inputs=[dict(role='captionAdapter',**m.pin(m.PREVIOUS))],policy={},fingerprint='old')
  with patch.object(m.previous,'prepare',return_value=base):out=m.prepare()
  self.assertEqual(out['schemaVersion'],m.SCHEMA);roles={r['role']:r for r in out['inputs']};self.assertEqual(roles['previousCaptionAdapter'],dict(role='previousCaptionAdapter',**m.pin(m.PREVIOUS)));self.assertEqual(roles['additionalWholeWordDisplaySupport']['sha256'],m.SUPPORT_SHA);self.assertNotEqual(out['fingerprint'],'old')

if __name__=='__main__':unittest.main(verbosity=2)
