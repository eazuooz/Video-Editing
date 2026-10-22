"""Record the actual limited new-source checks; never approve a whole master."""
import datetime
from polish_common import *
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
for ident,sid,count,windows in [('M11','08',30,[[13.1,15.1],[37.8,39.5]]),('M12','14',31,[[7.8,9.5],[31.1,33.1]])]:
 e=Episode(ident);e.authorized();pre=e.H/'observed-guide-preflight.json';moving=e.H/'moving-available-guide-preflight.json'
 p=read(pre);m=read(moving);assert len(p['samples'])==count
 assert p['assSha256']==sha(e.O/'composition-polish.ass')==m['assSha256']
 for s in p['samples']:assert sha(R/s['image'])==s['imageSha256']
 for r in m['clips']:assert sha(R/r['path'])==r['sha256']
 p.update(status='passed-still-preflight',reviewedAt=now,
  directInspection=f'All{count} current captioned samples across4 sheets directly inspected at375px tiles. Selected native1080 states also inspected; this is not a whole-master review.',
  finalMovingReview='selected short previews played; direct start/end observations only, plus separately inspected current still states; full master pending')
 save(pre,p)
 m.update(status='partial-selected-playback-observed',reviewedAt=now,
  currentReview={'scene':sid,'windows':windows,'method':'Browser playback started and advanced to the end; directly inspected start/end states. Current captioned source samples inspected separately. No continuous all-frame or full listening claim.',
   'result':'Target departure clears the guide; caption and hand/UI clearance retained.'})
 save(moving,m)
 path=e.H/'available-guides-review.json';d=read(path)
 d.update(reviewedAt=now,preflightSha256=sha(pre),sampleCount=count,sheetCount=4,selectedPlaybackSha256=sha(moving),restoredSceneCount=len(read(e.H/'gameplay-restoration.json')['scenes']))
 d['findings']=[x for x in d['findings'] if not x.startswith('Remaining source')]
 d['findings'].extend([f'New{sid} FHD glyph/connection guide: screen-space open contours follow observed quarter-second source states; labels explicitly deny inferred mesh data. Hide outside observed intervals and keep fixed captions.',
  'Remaining Portal2 source replacements and complete encoded master QA remain pending. Partial sample checks do not grant human or whole-master approval.'])
 d['newSourceGuideScope']={'scene':sid,'sourceReview':rel(e.H/'uncle-source-cut-review.json'),'sourceReviewSha256':sha(e.H/'uncle-source-cut-review.json'),'compositedReview':'passed-limited-preflight','continuousMotionReview':'pending-whole-master','sourceAudioUsed':False}
 save(path,d)
 additions=read(e.H/'cue-guide-additions.json');additions.update(status='passed-partial-current-composited-review',review=rel(path),reviewedAt=now);save(e.H/'cue-guide-additions.json',additions)
 print(ident,'current partial guide checks recorded; full master still pending',flush=True)
