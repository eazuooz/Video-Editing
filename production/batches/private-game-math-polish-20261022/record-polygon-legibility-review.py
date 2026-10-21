"""Record the directly viewed numeric font/header-clearance preflight."""
import datetime
from polish_common import *
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
for ident,count,source_count,sheets,native in [
 ('M13',24,68,9,['07-3.png','07-5.png']),
 ('M14',18,60,8,['18-3.png'])]:
 e=Episode(ident);e.authorized();p=e.H/'polygon-legibility-preflight.json';d=read(p)
 assert len(d['samples'])==count
 for path,digest in d['sourceCode'].items():assert sha(R/path)==digest
 for item in d['samples']:assert sha(R/item['image'])==item['imageSha256']
 d.update(status='passed-still-preflight',reviewedAt=now,directlyInspectedSheets=[1,2,3],directlyInspectedNativeImages=native,
  review='All current first/middle/last numeric beat states reviewed with actual captions at375px, plus native frames. Retained vertex indices, logical lengths/angles/areas, worked values and palette. Font enlargement is readable; circle and vertex labels now clear the header; notes/captions remain separate. Full encoded moving review remains pending.')
 save(p,d)
 p=e.H/'restored-source-review-explanation.json';d=read(p)
 assert len(d['samples'])==source_count
 d.update(status='reviewed-with-legibility-repairs',reviewedAt=now,directlyInspectedSheets=list(range(1,sheets+1)),
  findings=['Original numeric19px vertex labels and26px equations need enlargement; repaired by separately reviewed visual-only wrapper.','Native review found original circumcircle overlapping subtitle and enlarged top vertex labels touching rule; preserve logical geometry and adjust only screen mapping.','Original supplementary explanation objects/order retained; no new narration or examples.'],repairPreflight=rel(e.H/'polygon-legibility-preflight.json'),finalEncodedReview='pending')
 save(p,d)
cp=read(B/'checkpoint.json');cp['updatedAt']=now
cp['completedJobs'].append('M13/M14 original explanation sources directly inspected:68/60 samples. Numeric wrapper enlarges existing labels/formulas and fixes observed circumcircle/header and L-vertex/header conflicts only. All42 current captioned first/middle/last states on6sheets and3native frames inspected; still preflight passed. Existing PID34688 will render14 numeric replacements through fresh prepare-observed-composition.py; no duplicate worker, no final visual approval.')
for ident in ['M13','M14']:
 e=Episode(ident);cp['newVisualPreflightEvidence'][ident]['diagram']=rel(e.H/'polygon-legibility-preflight.json')
cp['nextAction']=cp['nextAction'].replace('Polygon numeric font/header-safe mapping preflight is being revised; preserve original logical geometry/clock.','Polygon numeric font/header-safe mapping preflight passed; existing PID34688 now renders/merges these14 reviewed numeric replacements before final assembly, preserving original logical geometry/clock.')
save(B/'checkpoint.json',cp)
print('M13/M14 numeric preflight recorded; full encoded moving review pending')
