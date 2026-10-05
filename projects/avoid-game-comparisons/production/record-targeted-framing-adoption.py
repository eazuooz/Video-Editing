"""Record directly inspected local-only trials and the independent action88 trim."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
now=datetime.now(timezone.utc).isoformat()
specs=[('remaining-two-motion-framing-local-v2',37,7),('remaining-two-motion-framing-local-v3',37,7),('remaining-one-motion-framing-local-v4',33,6),('action88-independent-context-local',39,7),('action88-exact-boundary-local',17,3)]
trials=[]
for name,ni,ns in specs:
 p=BASE/'measured-edit-v5'/name/'execution.json';d=read(p)
 assert d['exitCode']==0 and len(d['images'])==ni and len(d['sheets'])==ns
 for r in d['images']+d['sheets']:
  assert sha(ROOT/r['path'])==r['sha256'];r.update(directlyRead=True,directlyReadAt=now)
 d.update(status='closed-all-targeted-local-images-directly-read',updatedAt=now)
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 trials.append(dict(execution=p.relative_to(ROOT).as_posix(),sha256=sha(p),imagesDirectlyRead=ni,sheetsDirectlyRead=ns,allImagesAndSheets=d['images']+d['sheets']))
review=dict(schemaVersion=1,reviewedAt=now,status='four-sampled-crops-adopted-independent-dissolve-trim-required',trials=trials,
 captionCenter=[960,970],fontSize=48,newGitImages=0,pcmChanged=False,allFinalPixelsApproved=False,finalMixBuilt=False,
 observations=[
 '02p1 uses the earlier three clear samples with crop1280x720 x0 y360; entire avatar and late feet remain clear. Full final motion still requires review.',
 '10p2 uses the earlier three clear samples with crop1600x900 x160 y180; water vehicle and drill remain above the caption. Full final motion still requires review.',
 '02p4 v2/v3 hold the upper hero clear but partially hide a falling red tail at the end. v4 samples at20fps use1600x900 x320 with y180*n/89: the upper hero/drill/attack and large falling red body remain visible. A partial lower tail meets the fixed box in the last two sampled frames; lower green enemy is left of the box until leaving frame. This is not approval of unsampled motion or every secondary sprite.',
 '06p2 v2 late descent is still too close to the fixed box. v3 uses1120x630 x0 with y450*n/89; all18 selected samples, including10fps motion and the last frame, keep the airborne/descent/drill/body and feet clear to the right of or above the box.',
 'Action88 independently has an editorial dissolve between two different mine-map layouts. Earlier grey companion/hero at lower left and old rail/rectangle remain ghosted through4846, with faint residual old map through4848.4850 is conservatively selected as the first clean start. This is not the later actual game portal emergence and does not inherit action94 approval.',
 '5028 and5032 continue the same character walking/turning on the virtual desk. Extend action88 only to5035 exclusive, exactly before the already assigned action89. Do not use5035 onward twice.',
 'Action88 current[4838,5028) becomes[4850,5035). The first12 native frames are discarded; seven newly inspected adjacent active native frames replace part of that loss. Five output frames are removed. Do not pad with a dissolve, idle, loop or slowdown.' ],
 adoptedCropFilters={
 '02-p1-action-10-600-630':'crop=1280:720:0:360',
 '02-p4-action-21-1410-1455':"crop=1600:900:320:'180*min(1,n/89)'",
 '06-p2-action-31-900-945':"crop=1120:630:0:'450*min(1,n/89)'",
 '10-p2-action-75-1464-1530':'crop=1600:900:160:180'},
 action88=dict(source='CJ0_Xh59b98',oldStart=4838,oldEndExclusive=5028,start=4850,endExclusive=5035,sourceFps='60000/1001',nextAssignedStart=5035,editorialDissolveExcluded=True,finalCompiledBoundaryPixelsApproved=False))
(BASE/'targeted-framing-adoption-review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(newImagesRead=sum(s[1] for s in specs),newSheetsRead=sum(s[2] for s in specs),newGitImages=0,finalApproved=False)))
