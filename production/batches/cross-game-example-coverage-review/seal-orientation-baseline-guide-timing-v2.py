"""Approve bounded guide meanings against retained narration, not moving pixels."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os
ROOT=Path(__file__).resolve().parents[3];O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=O/'current34-baseline-guide-timing-direct-review-v2.json';assert not out.exists()
pp=O/'current34-baseline-guide-plan-v2.json';raw=pp.read_bytes();plan=read(pp)
review=read(O/'current34-mixed-complete-direct-review-v1.json')
assert review['all180ContextsDirectlyCompared'] and review['all34WholeTextsDirectlyCompared']
assert review['mixAacSha256']==plan['currentAacSha256']
assert not plan['renderExecuted'] and not plan['currentNarrationGuideTimingDirectlyReviewed']
rows=[]
for r in plan['scenes']:
    assert not r['worldOrBodyAxisOverlay'] and not r['armAxisOverlay'] and not r['observedScreenShiftIsInternalNumericDrift']
    assert r['originalPcmAndDistributedPausesUnchanged']
    assert sum(x['frames'] for x in r['windows'])==r['frames']
    for x in r['pointWindow']['keyframes']:assert sha(ROOT/x['inspectedImage'])==x['inspectedImageSha256']
    rows.append(dict(scene=r['id'],retainedParagraphs=r['retainedParagraphs'],pointRange=r['pointVisibleSceneFrameRange'],
        redRange=r['redScreenDisplacementSceneFrameRange'],goldRange=r['goldImageUpSceneFrameRange'],guideMeaning=r['guideMeaning'],
        fullRetainedCueAndMeaningsDirectlyRead=True,readEvidence='2d6406',nativeSelectionAlreadyReviewed=True,
        rationale='Cyan is the observed torso image point within the visible anchor window only. Camera-relative screen shift remains distinct from forward/body/world axes; hide every uncertain occlusion bracket. Original narration and observation pauses preserved.',
        movingPixelsApproved=False,allIntermediateFramesApproved=False))
assert len(rows)==8 and sum(x['frames'] for x in plan['scenes'])==21370
reasons={
    '02':'Red half-second screen delta is shown in the observation pause after the retained position/tilt explanation, ending before the next arm/attitude sentence. It never labels forward direction, velocity or arm roll.',
    '05':'Gold image-up arrow appears only with paragraph3 comparing camera image up and tilted body. It is fixed screen geometry, not a recovered game-world axis.',
    '23':'Gold arrow follows paragraph3 screen/object-reference comparison. Across the native cut it remains image-up only and does not claim continuous world tracking.',
    '20':'Torso mark ends before the next matrix interpolation topic and never identifies the unobserved input implementation.',
    '17':'The observed torso point does not claim a numeric drift measurement. Preserved narration explicitly distinguishes visible smooth motion and internal conditions.'}
oldsha=hashlib.sha256(raw).hexdigest()
plan.update(currentNarrationGuideTimingDirectlyReviewed=True,guideTimingReview=out.relative_to(ROOT).as_posix(),
    guideTimingReadEvidence='2d6406',currentNarrationGuideReviewScope='Retained wording, exact PCM/distributed cue placement and bounded screen-guide meaning only. Moving/final caption/UI pixels require encoded review.')
assert pp.read_bytes()==raw
tmp=pp.with_name(pp.name+'.review-writing');tmp.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(tmp,pp)
data=dict(recordedAt=datetime.now(timezone.utc).isoformat(),preparedPlanSha256=oldsha,currentReviewedPlanSha256=sha(pp),
    currentMixedReviewSha256=sha(O/'current34-mixed-complete-direct-review-v1.json'),rows=rows,sceneSpecificRationale=reasons,
    all8RetainedNarrationAndGuideMeaningsDirectlyCompared=True,movingFinalPixelApproved=False,finalCaptionPixelApproved=False,
    renderExecuted=False,newTts=0,sourceOrAnchorReExtraction=False,newImageGit=0)
out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(guideTimingRead=True,scenes=8,movingPixels=False)))
