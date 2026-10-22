"""Record inspected M12 replacement with the distracting tutorial ending removed."""
import datetime
from polish_common import *
e=Episode('M12');e.authorized();p=e.H/'uncle-cut-review-v2.json';d=read(p)
assert [(s['in'],s['frames']) for s in d['segments']]==[(406,960),(342,840),(366,840),(422,809)]
assert len(d['samples'])==57
for s in d['samples']:assert sha(R/s['path'])==s['sha256']
save(e.H/'uncle-source-cut-review.json',{'status':'passed-source-cut-inspection','reviewedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'candidateSha256':sha(p),'previewSha256':sha(R/d['preview']),'rawClipSha256':sha(R/d['rawClip']),
 'directStillInspection':{'samples':57,'sheets':d['sheets'],'method':'Directly viewed all seven current captioned contact sheets at one-second sampling.'},
 'movingReview':{'method':'Native browser playback started at52s and reached the end; the start/end states were directly observed. Opening replay advanced into the next excerpt. Not continuous-frame inspection or a new full listening pass.','windows':[[52,57.483333],[0,26]],'result':'Decoded and advanced; no tutorial banner at the final frame.'},
 'findings':['Visible hand-to-rock connection, triangular glyph and changing screen projection preserve the existing example role.',
  'Whole3449-frame slot remains unchanged; source406–422,342–356,366–380,422–435.483333 have no repeated source interval in this scene.',
  'Prior revision showed a tutorial banner near56.5s. Current ending stops before that banner.',
  'Actual world coordinates, mesh vertices and weights are not observed; existing narration explicitly distinguishes illustrative calculation from source measurements. New editorial annotations remain necessary.'],
 'annotationReview':'pending-new-source-anchors','audio':'Recovered narration, exact scene duration and caption clock unchanged; replacement source audio unused.',
 'humanReview':'pending','fullMasterApproval':False})
