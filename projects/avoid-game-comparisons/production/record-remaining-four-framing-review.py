"""Persist the directly read local trial, without granting final motion approval."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
p=BASE/'measured-edit-v5/remaining-four-framing-local-v1/execution.json'
d=json.loads(p.read_text(encoding='utf-8-sig'));now=datetime.now(timezone.utc).isoformat()
assert d['exitCode']==0 and len(d['images'])==16 and len(d['sheets'])==3
for r in d['images']+d['sheets']:
 assert hashlib.sha256((ROOT/r['path']).read_bytes()).hexdigest()==r['sha256']
 r.update(directlyRead=True,directlyReadAt=now)
d.update(status='closed-16-targeted-pixels-directly-read-two-cuts-still-need-reframing',updatedAt=now)
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
review={'reviewedAt':now,'execution':p.relative_to(ROOT).as_posix(),'imagesRead':d['images'],'sheetsRead':d['sheets'],
 'findings':[
  {'cut':'02-p1-action-10-600-630','sampledFocusClear':True,'observation':'Three samples show the entire avatar and late feet clear of the fixed single-line box after left/lower source crop. Unsampled motion remains pending.'},
  {'cut':'02-p4-action-21-1410-1455','sampledFocusClear':False,'observation':'The correctly matched dynamic crop now runs, but the upper avatar is clipped at the last sample and the lower green enemy crosses the caption. Reject this trial for the complete cut.'},
  {'cut':'06-p2-action-31-900-945','sampledFocusClear':False,'observation':'Early airborne motion is clear; the later descending avatar and burst meet the caption top. A narrower left crop must be tested while preserving the airborne start.'},
  {'cut':'10-p2-action-75-1464-1530','sampledFocusClear':True,'observation':'Bottom-oriented source crop shows the water vehicle and drill above the fixed caption at all three samples. Unsampled motion remains pending.'}],
 'allFinalPixelsApproved':False,'finalMixBuilt':False,'captionCenter':[960,970],'pcmChanged':False,'newGitImages':0}
(BASE/'remaining-four-framing-direct-review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'imagesDirectlyRead':16,'sampledCutsClear':2,'cutsStillPending':2,'newGitImages':0}))
