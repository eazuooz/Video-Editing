"""Record the direct M11 source review performed at the current checkpoint."""
import datetime
from polish_common import *
e=Episode('M11');e.authorized();p=e.H/'uncle-cut-review-v2.json';d=read(p)
assert [(s['in'],s['frames']) for s in d['segments']]==[(342,720),(366,840),(402,1680)]
assert len(d['samples'])==54
for s in d['samples']:assert sha(R/s['path'])==s['sha256']
save(e.H/'uncle-source-cut-review.json',{'status':'passed-source-cut-inspection','reviewedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'candidateSha256':sha(p),'previewSha256':sha(R/d['preview']),'rawClipSha256':sha(R/d['rawClip']),
 'directStillInspection':{'samples':54,'sheets':d['sheets'],'method':'Directly viewed all six current captioned contact sheets at one-second sampling.'},
 'movingReview':{'method':'Local native browser playback started at36s; start and advanced ending states directly observed. This is selected playback observation, not continuous-frame inspection or a fresh full audio listening pass.','window':[36,54],'result':'decoded and advanced without a playback failure'},
 'findings':['Bright triangular glyph and hand-to-rock grapple are visible during the opening.',
  '38.5–39.5s shows the glyph beside an active grapple while the existing connection-position sentence is on screen.',
  'Source pixels do not expose mesh vertices or barycentric coordinates; preserve the existing narration disclaimer and use editorial guides only.',
  'Falls/resets and unrelated tutorial banners excluded; three native-speed excerpts preserve the exact3240-frame slot.'],
 'annotationReview':'pending-new-source-anchors','audio':'Unchanged recovered narration and caption clock; no source audio or new TTS.',
 'humanReview':'pending','fullMasterApproval':False})
