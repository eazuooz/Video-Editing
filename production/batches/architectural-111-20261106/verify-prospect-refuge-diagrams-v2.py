"""Finite synthetic CPU tests only; no SDK/browser/server/encoder/model start."""
import copy,hashlib,importlib.util,json,subprocess,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
HERE=Path(__file__).resolve().parent
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
c=load('prospect_diagram_cue_test',HERE/'build-prospect-refuge-diagram-cues-v2.py')
r=load('prospect_diagram_worker_test',HERE/'run-prospect-refuge-diagrams-v2.py')
fixture_path=HERE/'verify-prospect-refuge-caption-timing-v2.py'
assert hashlib.sha256(fixture_path.read_bytes()).hexdigest()=='6c994b8ced115dd171fb48a442dfdc6ac850d6962b0d756d6db53b388c4f7902'
fixture=load('prospect_diagram_synthetic_words',fixture_path)

class DiagramTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  fixture.Caption103Tests.setUpClass();cls.f=fixture.Caption103Tests;cls.expected=c.source_contract();cls.plans={s:c.build_segment(cls.f.result,[x for x in cls.expected if x['paragraph']==int(s[1:])],s,fixture.m)for s in ('p04','p25')}
 @classmethod
 def tearDownClass(cls):fixture.Caption103Tests.tearDownClass()
 def test_exact_eight_cues_two_complete_paragraphs(self):
  self.assertEqual(sum(len(x['cues'])for x in self.plans.values()),8)
  for s,p in self.plans.items():
   para=next(x for x in self.f.result['paragraphs']if x['paragraph']==int(s[1:]));self.assertEqual([p['segmentStartGlobalFrame'],p['segmentEndGlobalFrameExclusive']],[para['startFrame'],para['endFrameExclusive']])
 def test_first_whole_sentence_ends_after_frame_zero(self):
  for p in self.plans.values():self.assertGreater(p['cues'][0]['frame'],0);self.assertTrue(p['cues'][0]['exactSpokenAnchorKo'].endswith('.'))
 def test_actual_samples_not_character_ratio(self):
  for p in self.plans.values():
   for cue in p['cues']:self.assertEqual(cue['actualRawSample'],cue['literalInterval']['actualEndBoundary']['sample']if 'actualEndBoundary'in cue['literalInterval']else cue['literalInterval']['endSample']);self.assertEqual(cue['globalFrame'],fixture.m.frame_from_sample(cue['actualRawSample']))
 def test_phase_endpoints_are_exact(self):
  for p in self.plans.values():self.assertEqual(p['phaseFrameMap'][0],{'frame':0,'phase':0.});self.assertEqual(p['phaseFrameMap'][-1],{'frame':p['totalFrames']-1,'phase':1.})
 def test_first_frame_zero_duplicate_rejected(self):
  p=copy.deepcopy(self.plans['p04']);p['cues'][0]['frame']=0
  with self.assertRaises(c.Pending):c.phase_map(p['cues'],p['totalFrames'],self.expected[:4])
 def test_last_endpoint_collision_rejected(self):
  p=copy.deepcopy(self.plans['p25']);p['cues'][-1]['frame']=p['totalFrames']-1
  with self.assertRaises(c.Pending):c.phase_map(p['cues'],p['totalFrames'],self.expected[4:])
 def test_duplicate_reordered_cue_rejected(self):
  p=copy.deepcopy(self.plans['p04']);p['cues'][0],p['cues'][1]=p['cues'][1],p['cues'][0]
  with self.assertRaises(c.Pending):c.phase_map(p['cues'],p['totalFrames'],self.expected[:4])
 def test_noninteger_frame_rejected(self):
  p=copy.deepcopy(self.plans['p04']);p['cues'][0]['frame']=1.5
  with self.assertRaises(c.Pending):c.phase_map(p['cues'],p['totalFrames'],self.expected[:4])
 def test_regressed_author_phase_rejected(self):
  expected=copy.deepcopy(self.expected[:4]);expected[1]['normalizedAuthorPhase']=.01
  with self.assertRaises(c.Pending):c.phase_map(self.plans['p04']['cues'],self.plans['p04']['totalFrames'],expected)
 def test_missing_exact_phrase_never_guessed(self):
  expected=copy.deepcopy(self.expected[:4]);expected[1]['exactSpokenAnchorKo']='없는 원문 문구'
  with self.assertRaises(c.Pending):c.build_segment(self.f.result,expected,'p04',fixture.m)
 def test_missing_actual_boundary_pending(self):
  timing=copy.deepcopy(self.f.result);target=next(s for s in timing['sentences']if s['paragraph']==4);target['canonicalWordBoundaries']=[]
  with self.assertRaises(fixture.m.Pending):c.build_segment(timing,self.expected[:4],'p04',fixture.m)
 def test_last_p25_cue_is_before_closing_end(self):
  p=self.plans['p25'];last=p['cues'][-1];sentence=next(s for s in self.f.result['sentences']if s['sceneId']==last['sceneId']);self.assertLess(last['actualRawSample'],sentence['endSample']);self.assertLess(last['frame'],p['totalFrames']-1)
 def test_unknown_source_hash_rejected(self):
  with patch.dict(c.PINS,{'project.ts':'0'*64}),self.assertRaises(c.Pending):c.source_contract()
 def test_default_readiness_never_starts_process(self):
  with patch.object(r.subprocess,'Popen',side_effect=AssertionError('no child')),patch.object(r.native,'busy_reason',side_effect=AssertionError('no expensive scan')):self.assertFalse(r.prepare()['ready'])
 def test_no_actual_timing_no_model_write(self):
  with patch.object(c,'caption_module',side_effect=AssertionError('no timing read')),self.assertRaises(c.Pending):c.prepare()
 def test_unknown_current_topic_rejected_before_render(self):
  original=r.read
  def changed(path):return {'currentTopicId':'07.04'}if Path(path).name=='checkpoint.json'else original(path)
  with patch.object(r,'read',side_effect=changed),self.assertRaisesRegex(ValueError,'Only current06.02'):r.prepare()
 def test_foreign_lease_never_recovered(self):
  with tempfile.TemporaryDirectory()as d:
   path=Path(d)/'lease.json';path.write_text(json.dumps({'protocol':'foreign','owner':'foreign','token':'foreign'}));before=path.read_bytes()
   with patch.object(r.runtime,'LEASE',path),patch.object(r.runtime,'archive',side_effect=AssertionError('foreign preserved')):r.recover_own({'foreign'})
   self.assertEqual(path.read_bytes(),before)
 def test_live_owned_child_keeps_lease(self):
  with tempfile.TemporaryDirectory()as d:
   path=Path(d)/'lease.json';row={'protocol':r.PROTOCOL,'owner':r.OWNER,'token':'ours','pid':1,'createTime':1,'child':{'pid':2,'createTime':1},'output':str(r.ATTEMPTS/'synthetic')};path.write_text(json.dumps(row));before=path.read_bytes()
   with patch.object(r.runtime,'LEASE',path),patch.object(r.runtime,'alive',side_effect=lambda x:x.get('pid')==2),patch.object(r.runtime,'archive',side_effect=AssertionError('live child preserved')):r.recover_own({'ours'})
   self.assertEqual(path.read_bytes(),before)
 def test_dead_parent_orphan_owned_browser_keeps_lease(self):
  with tempfile.TemporaryDirectory()as d:
   path=Path(d)/'lease.json';path.write_text(json.dumps({'protocol':r.PROTOCOL,'owner':r.OWNER,'token':'ours','pid':1,'createTime':1,'output':str(r.ATTEMPTS/'synthetic')}));before=path.read_bytes()
   with patch.object(r.runtime,'LEASE',path),patch.object(r.runtime,'alive',return_value=False),patch.object(r,'matching_owned_processes',return_value=[{'pid':2}]),patch.object(r.runtime,'archive',side_effect=AssertionError('orphan preserved')):r.recover_own({'ours'})
   self.assertEqual(path.read_bytes(),before)
 def test_node_pure_contracts_and_hidden_settings(self):
  command=['node',str(HERE/'verify-prospect-refuge-diagrams-v2.cjs')];p=subprocess.run(command,capture_output=True,text=True,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0));self.assertEqual(p.returncode,0,p.stdout+p.stderr);self.assertIn('10 pure Node checks PASS',p.stdout)

if __name__=='__main__':unittest.main(verbosity=2)
