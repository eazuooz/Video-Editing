"""Record an evidenced source-only correction; no narration or timeline revision."""
from pathlib import Path
import importlib.util, copy
spec=importlib.util.spec_from_file_location('common',Path(__file__).with_name('review-media-common-v15.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
R=m.ROOT;P=R/'projects/game-lighting-history-04/production'
pp=P/'part1-final-input-plan-v309.json';vp=P/'part1-final-visual-build-v322.json'
plan=m.read(pp);visual=m.read(vp)
cut=copy.deepcopy(next(c for c in plan['cuts'] if c['id']=='geometry-road-mask:native'))
old=next(c for c in visual['cuts'] if c['id']==cut['id'])
assert cut['frames']==1037 and (cut['fromFrame'],cut['toFrame'])==(53967,55004)
assert m.sha(R/cut['video']['path'])==cut['video']['sha256']
assert m.sha(R/old['path'])==old['sha256']
progress=P/'part1-current-moving-direct-progress-v325.json'
failed=next(r for r in m.read(progress)['records'] if r['id']==cut['id'])
assert not failed['normalSpeedPixelsApproved'] and failed['issues']
out=P/'part1-road-native-repair-proposal-v329.json';assert not out.exists()
cut['proposedCuts']=[{'inFrame':2160,'outFrame':3197}]
proof={
 'preparedAt':m.stamp(),'id':cut['id'],'input':cut,
 'inputPlan':{'path':m.rel(pp),'sha256':m.sha(pp)},
 'previousVisual':{'path':m.rel(vp),'sha256':m.sha(vp)},
 'previousInput':old,
 'failedFinalMovingReview':{'path':m.rel(progress),'sha256':m.sha(progress),'record':failed},
 'sourceReview':{'viewer':'production/research/game-lighting-history/local/part1-road-source-review-v328.html',
  'rangeSeconds':[36,53.28333333333333],'fullCandidateActuallyPlayed':True,'playbackRate':1,
  'observedStartToEnd':'Normal shaded curved spline/sign; at38.390 the source view-mode menu opens;44.506 shows the green diagnostic Mask view with red sign;52.211 returns to ordinary shading;automatic stop observed53.544. Existing24–41.283 source ended before the green display. No speed, freeze, loop or simulated diagnostic added.',
  'selectedForInputReview':True,'finalEncodedPixelsApproved':False},
 'captionAlignment':{'cue204':'00:15:06,167–00:15:09,367','inputOffsetSeconds':[6.716666666666667,9.916666666666667],
  'proposedSourceSeconds':[42.71666666666667,45.91666666666667],
  'required':'Green Mask visualization must be visible throughout the spoken green-region sentence; verify encoded preview directly.'},
 'retainedNarrationPcm':cut['pcm'],'framesUnchanged':True,'allOther93InputsUnchanged':True,
 'mixAndKoEnCaptionBytesUnchanged':True,'newTts':0,'newAudioMix':0,'newGitImages':0,
 'allFinalPixelsReviewed':False,'qaApproved':False,'collected':False,'uploaded':False,
 'humanWholeListening':'pending','humanPronunciation':'pending'}
m.save(out,proof)
cp=R/'production/research/game-lighting-history/checkpoint.json';j=m.read(cp);j['updatedAt']=m.stamp()
j['episode04Part1RoadMismatchV329']={'proposal':m.rel(out),'status':'source-only-correction-prepared','affectedFrames':[53967,55004],
 'issue':'Old source cut ended before narrated green Mask view. Current323 final approval stays false.',
 'next':'One CPU native/preview encode; direct moving caption alignment; then one current pair and affected-region QA','finalApproved':False}
m.save(cp,j)
print(m.rel(out))
