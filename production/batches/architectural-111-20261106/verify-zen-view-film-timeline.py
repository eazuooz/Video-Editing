"""Synthetic picture-clock fixtures only; no real ASR/timing/media/process work."""
import copy,importlib.util,unittest
from pathlib import Path
P=Path(__file__).resolve().parent
def load(name,file):
 s=importlib.util.spec_from_file_location(name,P/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
m=load('zen_picture_timeline_fixture','build-zen-view-film-timeline.py');renderer=load('zen_picture_renderer_fixture','render-zen-view-film.py')
def fixture():
 # Explicit synthetic seconds chosen to exercise the7-paragraph layout, not
 # generated narration timing and never saved as a production timeline.
 values={'P1d':8,'P1e':10,'P1f':14,'P3b':45,'P3c':48,'P3e':57,'P4b':67,'P4c':70,'P4d':73,'P4g':80,'P4h':83,'P5d':96,'P5g':104}
 boundaries=[0,20,40,64,88,110,132,154]
 paragraphs=[dict(paragraph=n,startFrame=boundaries[n-1]*60,endFrameExclusive=boundaries[n]*60)for n in range(1,8)]
 timing=dict(groups=[dict(id=k,startFrame=v*60)for k,v in values.items()],paragraphs=paragraphs,totalFrames=154*60,captions={'ko':[],'en':[]},diagramCues=[dict(id='07.04-p6-01-same-visible-chest',startFrame=117*60)])
 crops={}
 for n,start in [(2,20),(6,117),(7,132)]:
  end=boundaries[n];crops['p'+str(n)]=dict(contract=dict(frames=(end-start)*60),output=dict(path='synthetic-'+str(n)+'.mp4',sha256='1'*64),_pin=dict(path='synthetic-manifest-'+str(n),sha256='2'*64))
 game=dict(id='synthetic-independent-game',path='synthetic-game.mp4',sha256='3'*64)
 return timing,game,crops
class PictureClockTests(unittest.TestCase):
 def test_every_frame_covered_native_clocks_once_and_only_one_game_observation(self):
  out=m.plan(*fixture());r=renderer.validate_structure(out);self.assertEqual(r['movingNativeFrames'],{'narrow':480,'wide':480});self.assertEqual(r['observationFreezes'],1);self.assertEqual(r['totalFrames'],154*60);self.assertEqual(out['screenTime']['actualMovingGameplayFrames'],390)
 def test_first_frame_is_independent_game_and_exact_sign_freeze_retained(self):
  out=m.plan(*fixture());self.assertEqual(out['sections'][0]['kind'],'gameplay');freeze=next(s for s in out['sections']if s['kind']=='observation-freeze');self.assertEqual(freeze['sourceFrameIndex'],150);self.assertEqual(freeze['sourceLocalPts'],2.5);self.assertEqual(freeze['endFrameExclusive']-freeze['startFrame'],90)
 def test_narrow_hold_does_not_replay_motion_and_wide_can_cross_paragraph(self):
  out=m.plan(*fixture());moving=[s for s in out['sections']if s['kind']=='native'and not s['native']['holdPolicy']];self.assertEqual([s['native']['startNativeFrame']for s in moving],[0,240,0]);self.assertTrue(moving[-1]['startFrame']<88*60<moving[-1]['endFrameExclusive'])
 def test_mc_p6_entry_and_final_clock_coverage_are_exact(self):
  out=m.plan(*fixture());maps=[s for s in out['sections']if s['kind']=='mc'];self.assertEqual([s['startFrame']for s in maps],[20*60,117*60,132*60]);self.assertEqual(maps[-1]['endFrameExclusive'],out['totalFrames'])
 def test_shorter_speech_cannot_silently_speed_or_loop_the_native_pass(self):
  args=list(fixture());args[0]=copy.deepcopy(args[0]);next(x for x in args[0]['groups']if x['id']=='P3e')['startFrame']=49*60
  with self.assertRaises(m.Pending):m.plan(*args)
 def test_wrong_mc_duration_is_rejected_before_media(self):
  args=list(fixture());args[2]=copy.deepcopy(args[2]);args[2]['p7']['contract']['frames']-=1
  with self.assertRaises(m.Pending):m.plan(*args)
 def test_short_opener_cannot_create_negative_observation_padding(self):
  args=list(fixture());args[0]=copy.deepcopy(args[0]);next(x for x in args[0]['groups']if x['id']=='P1d')['startFrame']=300
  with self.assertRaises(m.Pending):m.plan(*args)
 def test_reactions_stay_clear_of_actual_dual_ab_and_dense_maps(self):
  out=m.plan(*fixture());self.assertEqual(len(out['catCues']),2)
  for cue in out['catCues']:
   self.assertTrue(all(renderer.cat_allowed(s)for s in out['sections']if max(cue['startFrame'],s['startFrame'])<min(cue['endFrameExclusive'],s['endFrameExclusive'])))
if __name__=='__main__':unittest.main(verbosity=2)
