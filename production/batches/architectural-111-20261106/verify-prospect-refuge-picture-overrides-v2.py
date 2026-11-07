"""CPU-only current-clock routing fault fixtures; no writing/render/models."""
import copy,importlib.util,json,pathlib,sys,unittest
from unittest.mock import patch
HERE=pathlib.Path(__file__).resolve().parent
def load(name):
 s=importlib.util.spec_from_file_location(name,HERE/(name+'.py'));m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
picture=load('build-prospect-refuge-picture-overrides-v2');builder=load('build-prospect-refuge-film-timeline-v2')
CAPTION=picture.MEDIA/'caption-timing-v3/340e246acfb0badde148ed76/caption-timing.json'
class CurrentClockRouting(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.s=picture.read(picture.PROJECT/'native-teaching-selection-v3.json');cls.t=picture.read(CAPTION)
 def setUp(self):self.timing=copy.deepcopy(self.t)
 def make(self):
  # These fixtures test routing faults. Actual source pin verification is kept
  # in the separate real read-only prepare() preflight, never claimed here.
  with patch.object(builder,'bound',side_effect=lambda q:pathlib.Path(q['path']).resolve()):return picture.make_payload(self.s,self.timing,builder,CAPTION)
 def test_13_selected_runs_remain_native1x_across23_explicit_rows(self):
  r=self.make();self.assertEqual(sum(q['playback']=='native-1x'for q in r['overrides']),13);self.assertEqual(len(r['overrides']),23);self.assertEqual(len(r['compiledSegments']),24);self.assertFalse(r['voiceModified'])
 def test_main_run_has_one_clock_with_actual_sentence_view_cut(self):
  r=self.make();q=next(q for q in r['overrides']if q['id']=='main-controlled-full-run');self.assertEqual(q['sourceFrameRange'],[0,600]);segs=[s for s in r['compiledSegments']if s['id'].startswith('override-main-controlled-full-run-')];self.assertEqual(len(segs),2);self.assertEqual(sum(s['frameCount']for s in segs),600);self.assertEqual(segs[1]['sourceStartFrame'],segs[0]['frameCount'])
 def test_footings_whole270_frames_end_at_actual_s2_end(self):
  r=self.make();q=next(q for q in r['compiledSegments']if q['id'].startswith('override-footings-placement-before-game-'));clock=next(q for q in self.timing['sentences']if(q['paragraph'],q['sentenceIndexZeroBased'])==(23,2));self.assertEqual(q['endFrameExclusive'],clock['endFrameExclusive']);self.assertEqual(q['sourceStartFrame'],90);self.assertEqual(q['frameCount'],270);self.assertEqual(q['startFrame'],q['endFrameExclusive']-270)
 def test_H_samefile_additional_window_has_exact_actual_sentence_length(self):
  r=self.make();q=next(q for q in r['overrides']if q['id']=='hl2-already-arranged-board');clock=next(q for q in self.timing['sentences']if(q['paragraph'],q['sentenceIndexZeroBased'])==(23,3));self.assertEqual(q['sourceFrameRange'],[1320,1320+clock['endFrameExclusive']-clock['startFrame']]);self.assertLessEqual(q['sourceFrameRange'][1],1652)
 def test_unknown_lowered_refuge_word_edge_remains_pending(self):
  q=next(q for q in self.timing['sentences']if(q['paragraph'],q['sentenceIndexZeroBased'])==(8,2));q['canonicalWordBoundaries']=[]
  with self.assertRaisesRegex(builder.Pending,'never interpolate'):self.make()
 def test_changed_root_recommendations_fail_before_caption_derivation(self):
  actual=picture.sha
  def altered(p):return'0'*64 if pathlib.Path(p).name=='picture-context-recommendations-v2.json'else actual(p)
  with patch.object(picture,'sha',side_effect=altered):
   with self.assertRaisesRegex(picture.Pending,'Root13 picture decisions changed'):picture.prepare(CAPTION)
 def test_default_does_not_materialize_or_launch(self):
  import contextlib,io
  with patch.object(sys,'argv',[str(picture.__file__)]),patch('subprocess.Popen')as popen,contextlib.redirect_stdout(io.StringIO())as out:picture.main()
  self.assertFalse(json.loads(out.getvalue())['ready']);popen.assert_not_called()
if __name__=='__main__':unittest.main(verbosity=2)
