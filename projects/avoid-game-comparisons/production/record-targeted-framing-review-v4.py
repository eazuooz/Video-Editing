"""Lock the direct read of91 local framing trials; keep final approval false."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json
ROOT=Path(__file__).resolve().parents[3]; BASE=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
path=BASE/'measured-edit-v4/targeted-lower-framing-local/execution.json'
state=read(path); now=datetime.now(timezone.utc).isoformat()
assert state['exitCode']==0 and state['pid']==58508
assert len(state['images'])==91 and len(state['sheets'])==16 and state['completedCuts']==19
observations=[
 ([1,2,3],'partial-repair','02p1: avatar is raised, but late feet/body still touch the caption.'),
 (list(range(4,9)),'partial-repair','02p4: avatar and hanging enemy are clear earlier; falling enemy enters the last one-line caption. Early drill effect is cropped above.'),
 (list(range(9,13)),'partial-repair','04p3: cup entry is largely clear, but glow touches caption in sample11.'),
 (list(range(13,19)),'partial-repair','04p5: avatar is clear; printed English footer may still touch two-line box in15/16.'),
 (list(range(19,24)),'partial-repair','06p2: lower avatar becomes visible, but airborne avatar is cropped at the top in20.'),
 (list(range(24,29)),'sampled-focus-clear','06p3: rocket, targets and platforms stay visible at the sampled caption/anchor frames.'),
 (list(range(29,33)),'sampled-focus-clear-boundary-pending','06p3: entry and avatar clear; next cup words in31/32 still require exact spoken-boundary alignment.'),
 (list(range(33,39)),'UI-repair-required','06p4: cup avatar is visible; fuel/puck UI is still under the caption. A downward crop alone does not resolve it.'),
 (list(range(39,42)),'entry-clear-context-pending','13p1: entry ring is visible. First layered-book effect still needs its own continuity review; do not blanket-classify it by another interval.'),
 (list(range(42,49)),'sampled-focus-clear','13p1: hero, entry, key and printed footer clear at selected samples.'),
 (list(range(49,54)),'sampled-focus-clear','13p2: key moves left as the book tilts; hero and printed footer clear.'),
 (list(range(54,61)),'sampled-focus-clear','13p2: key, rope, book tilt, hero and printed footer remain visible.'),
 (list(range(61,66)),'sampled-launcher-clear-framing-limit','10p1: ball launcher and health UI are visible; crop clips some upper boss portrait/head. Approval is limited to sampled ball-focus visibility.'),
 (list(range(66,69)),'partial-repair','10p3: avatar is visible; green burst may still touch the two-line caption in67.'),
 (list(range(69,74)),'focus-repair-required','15p1: dark-path avatar/enemy remain behind the two-line box in70/71.'),
 (list(range(74,80)),'sampled-focus-clear','15p2: desk hero/feet and combat remain visible at the sampled cues.'),
 (list(range(80,83)),'partial-repair','15p3: larger lava movement visible; avatar/drill tip still touches two-line caption in81.'),
 (list(range(83,88)),'sampled-focus-clear','15p4: fight avatar is visible; new last-clean1269 contains no different-map dissolve.'),
 (list(range(88,92)),'sampled-focus-clear','12p5: cave avatar is visible at all selected frames.'),
]
for r in state['images']+state['sheets']:
 assert sha(ROOT/r['path'])==r['sha256']
 r.update(directlyRead=True,directlyReadAt=now)
 if 'finalApproved' in r:r['finalApproved']=False
state.update(sessionId=71258,updatedAt=now,status='closed91-targeted-framing-images-directly-read-repairs-required',allTrialImagesDirectlyRead=True,allFinalPixelsApproved=False)
path.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
review={'schemaVersion':1,'reviewedAt':now,'execution':path.relative_to(ROOT).as_posix(),'executionSha256':sha(path),
 'planSha256':state['planSha256'],'captionLayoutSha256':state['captionLayoutSha256'],
 'cuts':19,'imagesRead':state['images'],'sheetsRead':state['sheets'],
 'observations':[{'imageIndices':a,'status':s,'finding':f} for a,s,f in observations],
 'fixedCaptionCenter':[960,970],'fontSize':48,'sourceAudioStreams':0,'newGitImages':0,
 'allCurrentPcmPreserved':True,'scope':'Direct read of16 contact sheets/91 sampled tiles; unsampled motion and final composite are not approved.',
 'finalTimingApproved':False,'allFinalCaptionPixelsApproved':False,'framingApproved':False,'finalVideoRendered':False,
 'nextAction':'Repair remaining occlusion with source framing/cue splitting and align12p1 rocket and10p2 spoken game name. Never move narration captions.'}
(BASE/'targeted-framing-direct-review-v4.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'imagesDirectlyRead':91,'sheetsDirectlyRead':16,'finalApproval':False}))
