"""Actual CUA normal-rate endpoints, bounded to silent7 scene playback."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
ROOT=Path(__file__).resolve().parents[3];O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sample=O/'measured-manim-sampled-direct-review-v2.json';execution=O/'measured-manim-execution-v2.json'
s=read(execution);assert s['actualOuterExitObserved'] and s['actualOuterExitCode']==0
out=O/'measured-manim-normal-playback-direct-review-v2.json';assert not out.exists()
rows=[('06a',.014819,12.633008),('09a',.019780,14.065690),('13a',.029908,14.866016),('16a',.012814,15.349023),('21a',.009183,14.266667),('12',.015467,32.681706),('18',.029255,36.932357)]
for r in s['scenes']:assert sha(ROOT/r['output'])==r['outputSha256']
out.write_text(json.dumps(dict(reviewedAt=datetime.now(timezone.utc).isoformat(),tabId='106',url='http://127.0.0.1:9250/orientation-measured-manim-v2-review.html',execution=execution.relative_to(ROOT).as_posix(),executionSha256=sha(execution),sampledPixelReview=sample.relative_to(ROOT).as_posix(),sampledPixelReviewSha256=sha(sample),observations=[dict(scene=i,startCurrentTime=a,startPaused=False,startEnded=False,endCurrentTime=b,endDuration=b,endPaused=True,endEnded=True,playbackRate=1,muted=True,action='native-controls locator Space; no seek/rate mutation') for i,a,b in rows],normalRateEndpointPlaybackVerified=True,all181EncodedSamplesAnd34BoardsDirectlyRead=True,allIntermediateFramesContinuouslyApproved=False,continuousHumanListeningApproved=False,finalCaptionsApproved=False,finalMixedApproved=False,finalRatioApproved=False),ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(scenes=7,normalRate=1,muted=True,allFinalApproval=False)))
