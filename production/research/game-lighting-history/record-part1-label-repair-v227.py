"""Record the directly inspected 35 ordered source boards; final caption QA is separate."""
from pathlib import Path
import json, hashlib, datetime
ROOT=Path(__file__).resolve().parents[3]
B=ROOT/'projects/game-lighting-history-04/production'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ref=lambda p:dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p))
qp=ROOT/'production/research/game-lighting-history/local/part1-label-repair-v225/qa-v226/execution.json'
q=read(qp)
assert q['exitCode']==0 and len(q['boards'])==35 and len(q['items'])==137
for x in q['boards']+q['items']:assert sha(ROOT/x['path'])==x['sha256']
notes={
 'horizon-comparison-before':'Raised CNN/SR and Transformer/SR names remain clear during projected bag growth and boundary drawing.',
 'cyber-comparison-before':'Surface/output names remain above boxes and arrows throughout the ordered stages.',
 'fortnite-comparison-before':'Left condition name is above the three materials; both labels and measured-data illustration remain separated.',
 'tsr-silhouette-history':'Past/current names are above the gold objects; closed boundary and correspondence arrow develop in order.',
 'tsr-rotation-vectors':'Surface names are above orange boundary paths; red footprint and teal correspondence remain distinguishable.',
 'cyber-light-reconstruction':'Both input names remain above projected samples; reconstruction roles are distinguished without claiming game internal values.',
 'mobile-compiler-availability':'Confirm/unavailable names are above the hollow outline; comparable-data label is separate from geometry and unavailable is not zero.'}
out=B/'part1-label-repair-direct-review-v227.json'
assert not out.exists()
out.write_text(json.dumps(dict(reviewedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),extraction=ref(qp),
 priorFailedPixelReview=ref(B/'part1-spatial-source-direct-review-v223.json'),source=q['source'],
 all35BoardsDirectlyViewed=True,ordered137SamplesDirectlyViewed=True,
 boards=[dict(x,directlyViewed=True) for x in q['boards']],sceneFindings=notes,
 scopedSourceLabelCollisionsResolved=True,projectedFacesDepthOcclusionObserved=True,
 orderedNarrationStagesObserved=True,sourcePixelSelectionApproved=True,
 preservedUnchangedScenes=['outer-comparison-before','four-game-transfer-conclusion','shadow-wheel-change'],
 actualBrowserPlaybackObserved=False,allMovingPixelsReviewed=False,allFinalCaptionPixelsReviewed=False,
 humanListening='pending',imagesLocalOnly=True,newGitImages=0,uploaded=False),ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(boards=35,images=137,sourceLabelReview=True,finalCaptionReview=False)))
