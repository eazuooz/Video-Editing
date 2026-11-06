"""CPU-only exact authored-clause guard fixtures; no real voice/job/model action."""
import copy,importlib.util,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('semantic_repair_preparer',HERE/'prepare-selected-voice.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)

class ClauseGuard(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.source=self.root/'projects/shorts-leveldesign-07-04/caption-clauses-v1.json';self.source.parent.mkdir(parents=True)
  self.text='눈에서 시작해, 틈을 통과합니다. 벽에서 막힙니다.'
  values=['눈에서 시작해,','틈을 통과합니다.','벽에서 막힙니다.'];pos=0;rows=[]
  for i,v in enumerate(values,1):rows.append(dict(id='G'+str(i),paragraph=1,ko=v,koSourceCharRange=[pos,pos+len(v)]));pos+=len(v)+1
  self.rows=rows;self.source.write_text(json.dumps(dict(topicId='07.04',sourceNarration=dict(sha256='narration'),groups=rows),ensure_ascii=False),encoding='utf-8')
  self.plan=dict(topicId='07.04',sourceNarrationSHA256='narration',clauseBoundaryPolicy=dict(kind='exact-current-caption-group-boundaries-v1',clauseSource=m.pin(self.source)),paragraphs=[dict(paragraph=1,components=[dict(text=r['ko'],reason='Authored explanatory clause.',captionGroupIds=[r['id']],sourceCharRange=r['koSourceCharRange'],clauseBoundaryReason='Show eye origin before the following aperture requirement.')for r in rows])])
  self.patch=patch.object(m,'ROOT',self.root);self.patch.start()
 def tearDown(self):self.patch.stop();self.tmp.cleanup()
 def run_plan(self,plan=None):return m.components_for([self.text],plan or self.plan,'narration')
 def test_exact_authored_clauses_reconstruct_source_and_mapping(self):
  groups=self.run_plan();scenes,mapping=m.make_scenes(dict(narrationKo=[self.text],titleKo='fixture'),groups)
  self.assertEqual(' '.join(x['lines'][0]for x in scenes['scenes']),self.text);self.assertEqual(mapping[-1]['sourceCharRange'][1],len(self.text))
 def test_without_explicit_policy_legacy_sentence_guard_remains(self):
  p=copy.deepcopy(self.plan);p.pop('clauseBoundaryPolicy')
  with self.assertRaisesRegex(m.Pending,'bisects'):self.run_plan(p)
 def test_midword_split_rejected_even_with_policy(self):
  p=copy.deepcopy(self.plan);p['paragraphs'][0]['components'][0]['text']='눈에서 시'
  with self.assertRaisesRegex(m.Pending,'exact contiguous'):self.run_plan(p)
 def test_wrong_group_or_range_rejected(self):
  for key,value in [('captionGroupIds',['G2']),('sourceCharRange',[0,999])]:
   p=copy.deepcopy(self.plan);p['paragraphs'][0]['components'][0][key]=value
   with self.assertRaisesRegex(m.Pending,'exact contiguous'):self.run_plan(p)
 def test_unsupported_policy_tampered_source_and_stale_narration_rejected(self):
  p=copy.deepcopy(self.plan);p['clauseBoundaryPolicy']['kind']='split-by-six-seconds'
  with self.assertRaisesRegex(m.Pending,'Unknown'):self.run_plan(p)
  p=copy.deepcopy(self.plan);p['clauseBoundaryPolicy']['clauseSource']['sha256']='0'*64
  with self.assertRaisesRegex(m.Pending,'exact authored'):self.run_plan(p)
  data=json.loads(self.source.read_text(encoding='utf-8'));data['sourceNarration']['sha256']='old';self.source.write_text(json.dumps(data),encoding='utf-8');p=copy.deepcopy(self.plan);p['clauseBoundaryPolicy']['clauseSource']=m.pin(self.source)
  with self.assertRaisesRegex(m.Pending,'stale'):self.run_plan(p)
 def test_dependent_clause_without_specific_reason_rejected(self):
  p=copy.deepcopy(self.plan);p['paragraphs'][0]['components'][0].pop('clauseBoundaryReason')
  with self.assertRaisesRegex(m.Pending,'explicit teaching'):self.run_plan(p)

if __name__=='__main__':unittest.main(verbosity=2)
