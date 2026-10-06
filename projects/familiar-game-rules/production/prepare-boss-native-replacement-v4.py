"""Exclude the source's internal shot change while preserving ninety timeline frames."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,copy
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
PROOF=ROOT/'production/batches/sakurai-planning-game-design/proof-familiar-game-rules'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
write=lambda p,j:p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
oldpath=BASE/'word-action-source-candidate-v3.json';old=read(oldpath);new=copy.deepcopy(old)
dest=BASE/'word-action-source-candidate-v4.json';assert not dest.exists()
cuts=[c for p in new['pieces'] for c in p['selectedSourceCuts']]
c=next(x for x in cuts if x['id']=='06-part3-cut07')
assert c['durationFrames']==90 and c['inFrameInclusive']==3530
assert not any(x['id']!=c['id'] and x['sourceVideoId']==c['sourceVideoId'] and max(x['inFrameInclusive'],3515)<min(x['outFrameExclusive'],3605) for x in cuts)
c['historicalV3Interval']={k:c[k] for k in ['inFrameInclusive','outFrameExclusive','sourceCrop','framingMode']}
c.update(inFrameInclusive=3515,outFrameExclusive=3605,inSeconds=3515/60,outSeconds=3605/60,
         sourceIntervalSeconds=1.5,framingMode='native-boss-exchange-before-source-shot-change',
         visibleActionConnection='Native umbrella jump, platform firing and landing left of the caption; same articulated-turret shot3515–3605. Outcome is checked separately. No win or key-binding inference.',
         exactNewEdgesApproved=False,completeMotionReviewed=False,sourceAndCaptionPixelsReviewed=False,wordActionAlignmentApproved=False)
notes=dict(reviewedAt=datetime.now(timezone.utc).isoformat(),source=rel(oldpath),sourceSha256=sha(oldpath),
           method='CUA normal-speed playback and direct gallery/screenshots; no pixel gate inferred from events',
           historicalV2=dict(interval=[3480,3570],rejectedCropReason='Crop removes upper projectile row; native early feet are under fixed caption.'),
           historicalV3=dict(interval=[3530,3620],rejectedReason='Source switches to a different monster/beam fight before out point. Direct frames3613/3619 and manual3609 show it; manual3604 still shows original turret.'),
           proposedV4=dict(interval=[3515,3605],directFirst=3515,directLast=3604,firstAndLastVisible=True,all90PixelsPending=True,normalSpeedPlaybackPending=True),
           unusedSource3330='Observed monster fight still only; no interval motion approval.',
           rejectedSource2850='Repair Shop BUY/QUIT menu, excluded from actual action quota.',
           allFinalCaptionPixelsReviewed=False,newGitImages=0)
proofpath=PROOF/'boss-source-replacement-direct-review-v4.json';write(proofpath,notes)
new.update(preparedAt=datetime.now(timezone.utc).isoformat(),status='native-boss-shot-change-excluded-candidate-only',
           baselineCandidate=rel(oldpath),baselineCandidateSha256=sha(oldpath),
           bossReplacementDirectReview=rel(proofpath),bossReplacementDirectReviewSha256=sha(proofpath),
           scope='Boss07 only changed3530–3620 to native3515–3605. Timeline23570frames, allPCM,70paragraphs,253KO/118EN preserved. Every motion/edge/final gate remains separate.')
assert len(cuts)==78 and new['finalFrameBudget']==23570
write(dest,new)
print(json.dumps(dict(interval=[3515,3605],frames=90,sourceCandidate=rel(dest),sha256=sha(dest),approved=False)))
