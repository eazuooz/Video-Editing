"""Save limited current-pixel evidence; this is not whole-episode approval."""
import datetime,subprocess,json
from polish_common import *
e=Episode('M10');e.authorized();now=datetime.datetime.now(datetime.timezone.utc).isoformat()
p=e.H/'observed-guide-preflight.json';d=read(p)
old=json.loads(subprocess.check_output(['git','show','HEAD:'+rel(p)]))
before={s['image']:s['imageSha256'] for s in old['samples']}
same=[s for s in d['samples'] if before.get(s['image'])==s['imageSha256']]
new=[s for s in d['samples'] if before.get(s['image'])!=s['imageSha256']]
assert len(same)==59 and len(new)==11 and all(s['scene']=='19' for s in new)
assert d['assSha256']==sha(e.O/'composition-polish.ass')
for s in d['samples']:assert sha(R/s['image'])==s['imageSha256']
d.update(status='passed-still-preflight',reviewedAt=now,partial=True,fullMasterReady=False,
 directNewSamples=11,unchangedPreviouslyInspectedSamples=59,priorEvidenceCommit=subprocess.check_output(['git','rev-parse','HEAD']).decode().strip(),
 directNewEvidence='All11 scene19 captioned states inspected at375px;45.75s also inspected at1920x1080.',
 findings=['Red traces selected visible wood; blue bounds only that screen-space portion, with an explicit non-world-bound label.','Post portion ends above the hand; plank guide ends before the grapple flash. No labels overlap fixed captions or native dialogue.','Prior59 sample images are byte-identical to the previously inspected record; no new claim of rewatching those scenes.'],
 finalMovingReview='Selected preview start/end states only; full-master review pending')
save(p,d)
mp=e.H/'moving-available-guide-preflight.json';m=read(mp)
assert m['assSha256']==d['assSha256']
for c in m['clips']:
 assert sha(R/c['path'])==c['sha256']
 if c['name'].startswith('19-'):c['currentPixels']='Browser native-speed start/end states observed; intermediate half-second stills inspected. No continuous listening approval.'
m.update(status='selected-native-playback-states-observed',reviewedAt=now,fullMasterApproval=False);save(mp,m)
r=read(e.H/'available-guides-review.json');r.update(reviewedAt=now,preflightSha256=sha(p),sampleCount=70,sheetCount=d['sheets'],selectedPlaybackSha256=sha(mp),restoredSceneCount=8,
 findings=r['findings']+['Scene19 new FHD village:63 source states and56 dense target states inspected;11 new composited states plus two selected preview start/end observations. Prior59 composite images identical.'],fullMasterReady=False)
save(e.H/'available-guides-review.json',r)
a=read(e.H/'cue-guide-additions.json');a.update(status='passed-partial-current-composited-review',review=rel(e.H/'available-guides-review.json'));save(e.H/'cue-guide-additions.json',a)
print('M10 partial preflight registered; whole master still pending')
