"""Record limited current-pixel evidence, not whole-master approval."""
import datetime
from polish_common import *
e=Episode('M17');e.authorized();now=datetime.datetime.now(datetime.timezone.utc).isoformat()
pre=e.H/'observed-guide-preflight.json'; p=read(pre);moving=e.H/'moving-available-guide-preflight.json';m=read(moving)
assert len(p['samples'])==33 and p['sheets']==5
assert p['assSha256']==sha(e.O/'composition-polish.ass')==m['assSha256']
for x in p['samples']:assert sha(R/x['image'])==x['imageSha256']
for x in m['clips']:assert sha(R/x['path'])==x['sha256']
p.update(status='passed-still-preflight',reviewedAt=now,
 directInspection='All33 current captioned states on5 sheets inspected at375px tiles; native1080 zoom state inspected. Front-roof region was narrowed after the first pass; zoom anchor was corrected by20 source pixels and its leader moved off buildings.',
 finalMovingReview='Selected11.8–14.7s and83.1–85.5s excerpts played in browser; start/end directly observed. Quarter-second source and current composited stills inspected separately; no full-motion/all-frame or whole-listening claim.')
save(pre,p)
m.update(status='partial-selected-playback-observed',reviewedAt=now,
 currentReview=dict(scene='14',windows=[[11.8,14.7],[83.1,85.5]],method='Browser playback launched; start and end frames directly inspected. Current quarter-second composited states separately inspected.',
 result='Guide clears outside the observed spans. Same-roof target, game palette and fixed caption region remain readable.',fullMasterApproval=False))
save(moving,m)
path=e.H/'available-guides-review.json';d=read(path)
d.update(reviewedAt=now,preflightSha256=sha(pre),sampleCount=33,sheetCount=5,selectedPlaybackSha256=sha(moving),
 findings=['Existing scene05/08 guides unchanged and resampled.',
 'Scene14 uses inspected original-recording647–727s and735–757.6s excerpts. Camera orbit and zoom now overlap preserved spoken cues; exact6156frames remain.',
 'Front-roof guide follows only visible roof pixels; same-gabled-roof marker follows the zoom comparison. No inferred camera matrix, near plane or world distance.',
 'Current source103one-second states/12sheets,33dense target states/4sheets and33captioned preflight states/5sheets inspected. Selected browser playback start/end checked.',
 'Portal2 FHD inputs and complete encoded master QA remain pending. No human review or whole-master approval.'],
 cueRepair=rel(e.H/'camera-cue-repair-review.json'),cueRepairSha256=sha(e.H/'camera-cue-repair-review.json'))
save(path,d)
plan=read(e.H/'observed-guides.json');plan['currentPixelReview']='passed-limited-captioned-preflight'
# Keep plan bytes stable: its hash is already bound to the current ASS/preflight.
print('M17 current limited cue/guide QA recorded; full master remains pending')
