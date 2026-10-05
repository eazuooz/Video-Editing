"""Record the direct read of all124 trial images; final approval stays false."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
now=datetime.now(timezone.utc).isoformat()
p=BASE/'measured-edit-v5/framing-corrections-local/execution.json';s=read(p)
assert s['pid']==31008 and s['exitCode']==0 and len(s['images'])==124 and len(s['sheets'])==21
observations=[
([1,2,3],'repair-required','02p1: single-line cue is narrower, but late avatar feet/body still touch it.'),
(list(range(4,9)),'repair-required','02p4: early drill is clipped and the falling red enemy reaches the last caption. The extractor matched a wrong cut ID, so its proposed dynamic crop was never used.'),
(list(range(9,14)),'sampled-focus-clear','04p3: cup entry/glow/avatar clear at the selected frames with single-line cues.'),
(list(range(14,21)),'sampled-focus-clear','04p5: stronger lower crop keeps avatar, key and printed footer clear at selected frames.'),
(list(range(21,26)),'repair-required','06p2: dynamic vertical crop preserves the early airborne avatar; later descending avatar still touches the caption.'),
(list(range(26,31)),'sampled-focus-clear','06p3: rocket, targets and platforms clear at sampled frames.'),
(list(range(31,35)),'spoken-boundary-review-required','06p3: entry/hero clear. The next cup caption starts about1.2frames before the cup image; exact preserved PCM paragraph boundary requires correction/review.'),
(list(range(35,42)),'sampled-cup-focus-clear-with-framing-limit','06p4: cup entry/down/up and glow visible. Crop partially excludes the irrelevant bottom fuel UI; it cannot establish a refilling rule. Cup edge/glow proximity still needs final motion review.'),
(list(range(42,51)),'sampled-focus-clear','06p5: reordered descent/landing, preparatory coin/attack and active combat are visible under the negative claim; no infinite-flight/refill rule is asserted.'),
([51,52,53],'sampled-focus-clear','06p5: reallocated active combat tail has no caption at sampled frames.'),
([54,55,56],'native-context-pending','13p1: first layered book/map frame requires its own raw continuity review; do not classify it from another transition.'),
(list(range(57,76)),'sampled-focus-clear','13p1/2: hero, entry, left/right key movement, rope/book tilt and printed footer visible. Entry ring proximity is subject to final motion review.'),
(list(range(76,81)),'sampled-launcher-focus-clear-with-framing-limit','10p1: ball launcher and health UI visible; some upper boss portrait clipped. Scoped visibility only.'),
(list(range(81,88)),'Pepper-word-aligned-water-framing-pending','10p1/2: Pepper caption now appears on Pepper footage, not the previous Plucky boat. Water vehicle/drill bottom still grazes the box in86/87.'),
(list(range(88,93)),'sampled-focus-clear','10p3: avatar/burst clear with single-line cue.'),
(list(range(93,98)),'sampled-focus-clear','15p1: stronger lower crop/single-line cue preserves dark-path hero/enemy/feet at selected frames.'),
(list(range(98,104)),'sampled-focus-clear','15p2: desk hero and combat clear at selected frames.'),
(list(range(104,109)),'sampled-focus-clear-near-box-edge','15p3: lava movement/avatar/drill above the narrow caption at selected frames; proximity needs final motion review.'),
(list(range(109,114)),'sampled-clean-boundary','15p4: combat visible; new native1269 end has no different-map dissolve.'),
(list(range(114,121)),'sampled-flight-word-aligned','12p1: the rocket ascent is now visible during the spoken rocket phrase, followed by a separate desk-combat/ascent cut; no continuous causal action is inferred.'),
(list(range(121,125)),'sampled-focus-clear','12p5: cave hero remains above the caption; light halo proximity is subject to final motion review.'),
]
assert sorted(i for ids,_,_ in observations for i in ids)==list(range(1,125))
for r in s['images']+s['sheets']:
 assert sha(ROOT/r['path'])==r['sha256']
 r.update(directlyRead=True,directlyReadAt=now)
s.update(sessionId=74580,updatedAt=now,status='closed124-corrected-framing-images-directly-read-targeted-repairs-required',allTrialImagesDirectlyRead=True,allFinalPixelsApproved=False)
p.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
d={'schemaVersion':1,'reviewedAt':now,'execution':p.relative_to(ROOT).as_posix(),'executionSha256':sha(p),'imagesRead':s['images'],'sheetsRead':s['sheets'],
 'observations':[{'imageIndices':ids,'status':status,'finding':finding} for ids,status,finding in observations],
 'scope':'All21 sheets/124 sampled images directly read; unsampled motion and final composites are not approved.',
 'planSha256':s['planSha256'],'captionLayoutSha256':s['captionLayoutSha256'],'fixedCaptionCenter':[960,970],'fontSize':48,
 'finalTimingApproved':False,'framingApproved':False,'allFinalCaptionPixelsApproved':False,'finalMixAsrApproved':False,
 'newGitImages':0,'allCurrent15PcmPreserved':True,
 'nextAction':'Repair only the four remaining occluded cuts, inspect the distinct layered-entry source context and review new quiet joins. Preserve all15 PCM and fixed caption position.'}
(BASE/'framing-corrections-direct-review-v5.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'imagesDirectlyRead':124,'sheetsDirectlyRead':21,'finalApproved':False}))
