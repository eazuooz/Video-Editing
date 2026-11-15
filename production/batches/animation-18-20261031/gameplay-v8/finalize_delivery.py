"""Publish only the local finite review collection after recorded internal checks."""
from common import *
import review
def main():
 log=read(HERE/'internal-review-log.json')
 assert set(log['encodedEpisodes'])==set(SCOPE)
 for ep in SCOPE:
  d=read(OUTPUT/ep/'delivery.json')
  assert not d['visualReviewPending'] and not d['humanReviewed']
  assert log['encodedEpisodes'][ep]['masterSha256']==next(f['sha256'] for f in d['files'] if f['kind']=='captioned.mp4')
 audio=read(HERE/'audio-verification.json');assert not audio['flagged'] and not audio['levelFlags']
 a=read(HERE/'preflight-review.json');a.update(encodedMotionReviewPending=False,internallyReviewedEpisodes=SCOPE,humanReview=False,fullHumanListening='pending-local-user-review',updatedAt=stamp());save(HERE/'preflight-review.json',a)
 review.main()
 runtime=read(WORK/'runtime.json');runtime.update(stage='local-review-hub-built-browser-check-pending',renderSession=None,scopedRenderSession=None,pendingAfterMain=[],updatedAt=stamp());save(WORK/'runtime.json',runtime)
 print('All15 revised, A06 preserved;16-video local review collection built. No platform mutations.',flush=True)
if __name__=='__main__':main()
