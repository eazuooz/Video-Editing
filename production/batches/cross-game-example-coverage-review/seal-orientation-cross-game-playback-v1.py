"""Seal bounded actual 1x UI observations; source in/out still needs native review."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, re, os
ROOT=Path(__file__).resolve().parents[3]
O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=O/'cross-game-normal-playback-direct-review-v1.json'
assert not out.exists()
plan=read(O/'cross-game-native-candidate-plan-v1.json')
bygame={x['game']:x for x in plan['candidates']}
obs=[
 dict(game='descenders',prefix='cross-game-descenders',requestedIn=700,requestedOut=735,
      play=700.0043,pause=735.011153,decision='held',
      observation='Initial bright rear-rider view changes to a dark night route by observed718.277335. Night silhouettes hide wheel/frame cues. This whole35s window cannot serve a continuous same-world comparison.'),
 dict(game='descenders',prefix='cross-game-descenders-day',requestedIn=680,requestedOut=705,
      play=680.003681,pause=705.190142,decision='recut-needed-before-result-menu',
      observation='Bright same-route rider/bike at680.00412 and ramp approach696.948033. By705.190142 finish UI and fallen rider replace active bike riding. Exclude finish menu/crash from a rigid bicycle-frame comparison; select exact useful turn/jump result from native samples.'),
 dict(game='trailmakers',prefix='cross-game-trailmakers',requestedIn=665,requestedOut=700,
      play=665,pause=700.164326,decision='native-audit-candidate',
      observation='First immediate screenshot was buffering solid-blue, not a visible start-frame approval. At679.346629 blue/yellow aircraft has distinct nose/wings and banks above sea. At700.164326 same aircraft appears side-on with island behind. Camera follows/orbits; engine world axes and pure roll cannot be inferred. Prior owner noted bridge occlusion near683, to be verified by own native samples.'),
 dict(game='space-engineers',prefix='cross-game-space-engineers',requestedIn=170,requestedOut=184,
      play=170.008339,pause=184.147271,decision='native-audit-candidate',
      observation='170.008725 shows enlarged landing-gear ghost plus rotation-key helper.184.147271 shows small upright placed gear on floor. Native samples must distinguish resizing/rotation/translation/placement; endpoints alone do not establish a single rigid rotation. Facecam and lower instruction UI need safe reframing.')]
for item in obs:
    source=bygame[item['game']]
    assert sha(ROOT/source['sourcePath'])==source['sourceSha256']
    ax=O/(item['prefix']+'-end-v1.ax.txt')
    text=ax.read_text('utf-8')
    assert str(item['pause']) in text and '"rate": 1' in text and '"muted": true' in text
    item.update(sourcePath=source['sourcePath'],sourceSha256=source['sourceSha256'],
        actualEndAx=ax.relative_to(ROOT).as_posix(),actualEndAxSha256=sha(ax),
        screenshot=(O/(item['prefix']+'-end-v1.png')).relative_to(ROOT).as_posix(),
        screenshotSha256=sha(O/(item['prefix']+'-end-v1.png')),
        normalSpeedReachedRequestedEnd=True,normalSpeedScope='Actual UI play/pause endpoints and listed directly viewed samples only',
        browserOvershootUsedAsNativeOut=False,allIntermediateFramesApproved=False,
        nativeInOutApproved=False,rightsHumanApproval=False)
data=dict(reviewedAt=datetime.now(timezone.utc).isoformat(),observations=obs,
    baselineGame='Superflight',prospectiveDistinctGames=['Superflight','Descenders','Trailmakers','Space Engineers'],
    fourGameTeachingApproved=False,sourceSelectionApproved=False,
    recentUse='Descenders source used in polar lesson, bright680+ interval newly considered. Trailmakers/Space Engineers reused from separate quaternion owner; disclose conceptual difference and only retain if own clarity review beats alternatives.',
    semanticLimits='Projected screen directions/observed object cues; no measured world axes, numerical pose, engine internals or physical rigid-rider claims.',
    rights='Internal CC/official source evidence retained; third-party recording/game-IP human review stays pending. Besiege description-link authorization is episode-specific and not assumed for this lesson.',
    mediaCopied=0,newServerStarted=0,foreignFilesChanged=0,finalNarrationTimedAnnotationApproved=False)
out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(review=out.relative_to(ROOT).as_posix(),actualWindows=4,normalSpeedEndpoints=True,nativeCutApproval=False)))
