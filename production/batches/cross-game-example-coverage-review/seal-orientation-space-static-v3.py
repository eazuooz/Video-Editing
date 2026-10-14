"""Seal eight directly inspected enlarged static frames; no moving approval."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib
ROOT=Path(__file__).resolve().parents[3]
O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=O/'space-enlarged-static-direct-review-v3.json'
assert not out.exists()
plan=O/'space-enlarged-static-plan-v3.json'; p=read(plan)
assert [r['nativeFrame'] for r in p['rows']]==[10320,10428,10464,10620,10668,10692,10800,10890]
for r in p['rows']:
    assert sha(ROOT/r['sourceSample'])==r['sourceSha256']
    assert sha(ROOT/r['path'])==r['sha256']
    assert r['pts']==r['nativeFrame']*256
    assert r['sourceCrop1920']==[320,255,1280,720]
notes={10320:'Upright small green preview and whole box clear.',10428:'Horizontal small preview and whole box clear.',10464:'Upright preview with different visible face clear.',10620:'Horizontal preview clear.',10668:'Tall upright preview now wholly above footer; top and green-box base both retained. Native help text crosses its lower area, so annotation labels must avoid it.',10692:'Horizontal preview and box clear.',10800:'Placed solid component and whole green base above footer.',10890:'Solid left-facing component and whole green base above footer.'}
data=dict(reviewedAt=datetime.now(timezone.utc).isoformat(),plan=plan.relative_to(ROOT).as_posix(),planSha256=sha(plan),actualPreparationExitCode=0,actualPreparationCompletion='f5d05c',allEightStaticPixelsDirectlyRead=True,allSourceAndOutputShaMatched=True,rows=[dict(**r,observation=notes[r['nativeFrame']]) for r in p['rows']],
    heldHistory=[dict(plan='space-enlarged-static-plan-v1.json',reason='10668 top clipped by tighter crop/lift.'),dict(plan='space-enlarged-static-plan-v2.json',reason='10668 green-box base and10800 solid base intrude into blur footer.')],
    objectFramingApproved=True,scope='Eight enlarged static object-framing samples only. Original1920 source must supply moving pixels.',sourceCrop1920=[320,255,1280,720],sameExactFrameBlurFooter1920=[0,900,1920,180],allOriginalUiApproved=False,
    uiLimit='Right/top rotation-axis widget is cropped; show prerequisite/full-source rotation-key context before relying on an enlarged object shot. Keys on screen do not establish which key was actually pressed or game-world axes.',
    allBetweenFramesApproved=False,movingAnnotationApproved=False,narrationTimedApproved=False,finalCaptionApproved=False,finalNativeCutApproved=False,rightsApproved=False,newSourceExtraction=0,localOnly=True,gitImagesAdded=0)
out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf-8')
cp=read(O/'latest-checkpoint.json'); cp.update(spaceEnlargedStaticReview=out.relative_to(ROOT).as_posix(),stage='cross-game-native-and-enlarged-static-approved-script-pending',next='Confirm recent-use/source permissions; write paired causal3game additions and scoped21a-p01 repair. Moving crop/UI/annotations and finalfourgame approval remain pending.',recordedAt=data['reviewedAt'])
cp['ownedJob']['status']='closed-native-pixels-directly-reviewed';cp['ownedJob']['allSamplesDirectlyRead']=True;cp['ownedJob']['sourceSelectionApproved']=True
(O/'latest-checkpoint.json').write_text(json.dumps(cp,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(staticSamples=8,objectFramingApproved=True,movingApproved=False)))
