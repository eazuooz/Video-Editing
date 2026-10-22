"""Version-bound partial inspection; remaining M09 sources are still missing."""
import datetime
from polish_common import *
e=Episode('M09');e.authorized();now=datetime.datetime.now(datetime.timezone.utc).isoformat()
p=e.H/'observed-guide-preflight.json';d=read(p);assert len(d['samples'])==7 and d['assSha256']==sha(e.O/'composition-polish.ass')
for s in d['samples']:assert sha(R/s['image'])==s['imageSha256']
d.update(status='passed-still-preflight',reviewedAt=now,partial=True,fullMasterReady=False,
 directlyInspectedSheets=[1],directNativeStates=[12.5,25.54],
 findings=['All7 composited states inspected at375px; red marks the visible hand-side connection, blue marks the visible rock-side endpoint.','25.5s blue anchor corrected after native composite exposed vertical drift; all7 corrected composites reinspected.','No fabricated world length or collision implementation; original luminous connection remains visible.'],
 finalMovingReview='Selected native playback start/end observations only; full master pending');save(p,d)
mp=e.H/'moving-available-guide-preflight.json';m=read(mp)
for c in m['clips']:
 assert sha(R/c['path'])==c['sha256'];c['currentPixels']='Native-speed browser start/end states observed with guide visible near start; current half-second stills inspected. Not continuous listening approval.'
m.update(status='selected-native-playback-states-observed',reviewedAt=now,fullMasterApproval=False);save(mp,m)
save(e.H/'available-guides-review.json',{'status':'partial-guides-inspected-full-episode-pending','reviewedAt':now,
 'preflight':rel(p),'preflightSha256':sha(p),'sampleCount':7,'sheetCount':1,
 'selectedPlayback':rel(mp),'selectedPlaybackSha256':sha(mp),'sourceRestoration':rel(e.H/'gameplay-restoration.json'),
 'restoredSceneCount':1,'findings':d['findings'],'fullMasterReady':False,'humanReview':'pending','newTts':False,'timelineChanged':False})
a=read(e.H/'cue-guide-additions.json');a.update(status='passed-partial-current-composited-review',review=rel(e.H/'available-guides-review.json'));save(e.H/'cue-guide-additions.json',a)
print('M09 scene02 partial source/guide preflight passed; remaining sources and full-master QA pending')
