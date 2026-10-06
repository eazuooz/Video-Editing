"""A same-length source replacement candidate, preserving the full native view."""
from pathlib import Path
from datetime import datetime, timezone
import json, copy, hashlib
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source_path=BASE/'word-action-source-candidate-v2.json';old=read(source_path);new=copy.deepcopy(old)
dest=BASE/'word-action-source-candidate-v3.json';assert not dest.exists()
cuts=[c for p in new['pieces'] for c in p['selectedSourceCuts']];target=next(c for c in cuts if c['id']=='06-part3-cut07')
assert target['inFrameInclusive']==3480 and target['outFrameExclusive']==3570 and target['durationFrames']==90
assert not any(c['id']!=target['id'] and c['sourceVideoId']==target['sourceVideoId'] and max(c['inFrameInclusive'],3530)<min(c['outFrameExclusive'],3620) for c in cuts)
target['historicalCandidateInterval']={k:target[k] for k in ['inFrameInclusive','outFrameExclusive','sourceCrop','framingMode']}
target.update(inFrameInclusive=3530,outFrameExclusive=3620,inSeconds=3530/60,outSeconds=3620/60,
              sourceIntervalSeconds=1.5,sourceCrop=[0,0,1920,1080],framingMode='native-same-boss-jump-and-platform-fire-replacement-candidate',
              bankCutIds=[],previouslyBankedSourceFrames=0,newSourceBoundaryFrames=90,
              sourceAndCaptionPixelsReviewed=False,completeMotionReviewed=False,exactNewEdgesApproved=False,wordActionAlignmentApproved=False,
              visibleActionConnection='Same boss exchange: complete native projectile arc, leftward umbrella jump and platform firing. Visible functions only; no win or button-setting claim. New3530–3620 interval requires direct playback/caption/edge review.')
new.update(preparedAt=datetime.now(timezone.utc).isoformat(),status='native-boss-same90-frame-replacement-candidate-only',
           baselineCandidate=str(source_path.relative_to(ROOT)).replace('\\','/'),baselineCandidateSha256=sha(source_path),
           scope='Only boss07 source changes from3480–3570 targeted crop to native3530–3620. All23570 timeline frames, PCM,70 paragraphs and253KO/118EN unchanged. Replacement direct review pending.')
new['targetedCropIds']=[x for x in old['targetedCropIds'] if x!=target['id']]
new['unresolved'].append('Native boss replacement3530–3620 is a candidate. Browser comparison identified clipping/feet overlap in historical3480–3570; do not approve new source before direct review.')
assert len(cuts)==78 and new['finalFrameBudget']==23570
dest.write_text(json.dumps(new,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(replacementId=target['id'],nativeInterval=[3530,3620],frames=90,timelineFrames=23570,approved=False)))
