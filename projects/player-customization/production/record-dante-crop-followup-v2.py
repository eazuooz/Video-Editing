"""Record actual CUA crop samples; prepare unique research capacity, never quota approval."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
def read(p): return json.loads(p.read_text('utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p): return p.relative_to(ROOT).as_posix()
def write(p, d):
    assert not p.exists(), f'Preserve existing record: {p}'
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2)+'\n', 'utf-8')
now = datetime.now(timezone.utc).isoformat()
proof = ROOT/'shared/output/player-customization/preflight'
crop = dict(x=654, y=108, width=1104, height=621)
rows = [
    (68,85,85.009,'Caster/effect lines and forward targets remain in the crop; the left part of the caster is clipped. Use only actually visible origin/target claims.'),
    (221,228,228.184,'At221 the caster arm is visible at left and a target is ahead; at228.184 a large cyan rounded effect fills the space near the caster. Supports comparing a forward line and a nearby round shape, not equipment causality.'),
    (233,244,244.151,'Endpoint244.151 shows raised arms, blue bird-like particles around the caster and a forward target. This endpoint supports a cast/target relationship, not a persistent rounded-sphere claim; keep the distinct earlier sphere pixels separate.'),
    (258,268,268.120,'Cyan projectiles cross toward a target beside the gold doorway. Target and doorway remain above the fixed caption prototype.'),
    (431,440,440.031,'The endpoint camera looks downward along the stone wall; target clarity is weaker than the prior doorway action. Reject the late downward/wall tail;431–437.8 is a research refinement candidate, not an approved edge.'),
    (109,124,124.161,'Caster, cyan lines and multiple foreground/forward targets are visible at the endpoint. Names/stats partly clipped at right cannot support numerical claims.'),
    (134,154,154.181,'Progress sample149.393 showed a cast toward targets in the gold-walled space. Endpoint154.181 has cast fragments/smoke obscuring the left targets. Trim or reframe exact sections where the target relation becomes unclear.'),
    (285,295,295.089,'Endpoint295.089 points at a wall with no clearly readable forward target. Reject this endpoint/tail;285–291 remains only a research candidate for exact action review.'),
    (455,477,477.065,'Endpoint477.065 contains a small cast flare and mostly empty forward floor. Reject this tail for target-placement narration; earlier455–473 needs precise action review.'),
    (500,524,524.191,'Progress sample521.265 showed caster at left, forward targets and crossing projectiles. Endpoint524.191 shows a raised arm and a nearby target reaction. Stop before the sampled525 POWERTRIP notification; browser overshoot is not a selected final edge.'),
]
observations = []
for a,b,end,finding in rows:
    p = proof/f'dante-crop654-108-1104-621-{a}-{b}-end-v2.png'
    assert p.exists(), p
    observations.append(dict(requestedLocalSeconds=[a,b], observedEndSeconds=end,
        nominalSourceEndSeconds=2530+end, finding=finding, boundedPlaybackRequested=True,
        returnedEndpointPixelsDirectlyRead=True,
        endpointEvidence=dict(path=rel(p),sha256=sha(p)),
        allContinuousFramesRead=False, finalNativeEdgeApproved=False))
record = dict(schemaVersion=1,reviewedAt=now,sourceVideo='vy_vtGx8vq8',
    sourceSha256='557d72314427c03fd018c1e546675dbfe9ccfe652ad03b8bb5c9db42d77d0917',
    sourceOffsetSeconds=2530,priorReview=rel(BASE/'dante-continuous-crop-review-v1.json'),
    nativeReview=rel(BASE/'dante-native-direct-review-v1.json'),
    method='CUA requested bounded local playback, actual returned playback times and directly read start/progress/endpoint pixels; supplemented by earlier125 native samples/32boards. These observations do not cover every continuous frame.',
    cropCandidate=crop,captionPrototype=dict(enabled=True,position1920=[960,970],actualCueText=False),
    histories=[
        dict(crop=dict(x=634,y=150,width=1152,height=648),requestedLocalSeconds=[49,64],observedEndSeconds=64.140,
             finding='Source POWERTRIP task text remains below the fixed prototype box. Exclude the popup; never move the narration caption.',
             evidence=dict(path=rel(proof/'dante-crop49-64-end-v2.png'),sha256=sha(proof/'dante-crop49-64-end-v2.png'))),
        dict(crop=dict(x=634,y=130,width=1152,height=648),observedSeconds=64.140,
             finding='Moving crop upward still leaves part of source task text; not an accepted fix.',
             evidence=dict(path=rel(proof/'dante-crop-y130-64-v2.png'),sha256=sha(proof/'dante-crop-y130-64-v2.png'))),
        dict(crop=crop,observedSeconds=64.140,
             finding='Presenter and broadcast borders are excluded; a small task icon/text remainder still requires rejecting the64–67 popup window. Left caster arm can be clipped.',
             evidence=dict(path=rel(proof/'dante-crop654-108-1104-621-64-v2.png'),sha256=sha(proof/'dante-crop654-108-1104-621-64-v2.png')))
    ],observations=observations,
    additionalReturnedProgressSamples=[dict(localSeconds=149.393,requestedRange=[134,154],pixelsDirectlyRead=True,savedLocalImage=None),
        dict(localSeconds=521.265,requestedRange=[500,524],pixelsDirectlyRead=True,savedLocalImage=None)],
    limitations=['No claim that every continuous frame, final crop boundary or actual Korean cue has been approved.',
        'Choose origin/hand claims only when those pixels remain visible; right-edge clipped HUD values and cropped ability menu cannot prove verse order or settings.',
        'POWERTRIP, PHORID and failure popups remain excluded. Empty transit, long waits, severe effect occlusion, presenter/model-only footage are not actual-action quota.',
        '2024 developer-preview footage is an observed historical demonstration, not a claim about current game balance.'],
    allFinalNativeBoundariesReviewed=False,finalCaptionPixelsReviewed=False,sourceAudioUsed=False,
    gameplayQuotaApproved=False,allRasterLocalOnly=True)
write(BASE/'dante-continuous-crop-review-v2.json',record)

bank = read(ROOT/'projects/player-customization/sources/native-source-bank-v1.json')
bank.update(schemaVersion=2,preparedAt=now,status='unique-research-capacity-only-awaiting-measured-guide-audio',
    historicalBank='projects/player-customization/sources/native-source-bank-v1.json',
    currentDanteCropReview=rel(BASE/'dante-continuous-crop-review-v2.json'))
for r in bank['rows']:
    if r['source']=='yareli' and r['localInSeconds']==65:
        r.update(historicalLocalOutSeconds=r['localOutSeconds'],localOutSeconds=66.5,
            nominalSourceOutSeconds=66.5,candidateSeconds=1.5,
            refinement='Earlier bounded65–68.193 review showed staged NPC tail; reserve only65–66.5 pending exact native edge review.')
bank['sources']['dante']=dict(videoId='vy_vtGx8vq8',sourceOffsetSeconds=2530,
    path='shared/output/player-customization/research/dante-demo-v1/vy_vtGx8vq8-dante-2530-3155.mp4',
    sha256=record['sourceSha256'],review=record['nativeReview'],cropReview=rel(BASE/'dante-continuous-crop-review-v2.json'),
    version='2024 work-in-progress Dante developer preview',sourceAudioUsed=False,
    owner='PlayWarframe / @Warframe',rights=bank['sources']['jade']['rights'],cropCandidate=crop)
pockets=[
 (30,48.8,['09','10'],'Caster aiming/casting and forward projectiles; precise transit trimming pending.'),
 (49,63.3,['09','10'],'Aim/projectile spatial relationship; leave margin before64 task popup.'),
 (68,85,['10','13'],'Cyan effect lines and targets near gold walls; visible-origin selection pending.'),
 (85.2,99.8,['09','10'],'Forward casts/target reaction native-sample candidate; exact transitions pending.'),
 (100.2,109,['10','13'],'Approach/aim at target/doorway; reject movement-only portions.'),
 (109.2,124,['10','13'],'Forward effect lines, nearby orb and visible targets; separate actual chosen effect with exact edge inspection.'),
 (134,154,['13'],'Target arrangement across gold-walled space; remove target-occluding smoke/effect sections.'),
 (154.2,161,['13','14'],'Forward cast/target candidate; end before task-notification region.'),
 (170,175,['14'],'Cast action after notification; precise popup clearance remains pending.'),
 (215,220.8,['14'],'Cast/aim starts; no claim that a loadout changed.'),
 (221,228,['10','12'],'Raised caster action and nearby round cyan effect.'),
 (228.2,233,['12'],'Round effect/target relation after previous action; no repeated source seconds.'),
 (233.2,244,['14'],'Raised-arm cast and blue particles/forward target before245 task popup; do not call this endpoint a rounded sphere.'),
 (258,267.8,['14'],'Forward cast/projectile lines at gold doorway; PHORID255 excluded.'),
 (268,279,['14','15'],'Forward action/targets after prior cast; stop before280 failure notification.'),
 (285,291,['15'],'Post-notification aim/cast candidate; reject later wall-only tail.'),
 (410,430.8,['15','16'],'Cast/aim toward pale-stone doorway targets; remove any transit and waits.'),
 (431,437.8,['13','16'],'Doorway action candidate; reject440 downward/wall endpoint.'),
 (455,473,['16'],'Later cast/target action; reject477 mostly empty-floor endpoint.'),
 (478,490,['16'],'Nearby/far cast and target-reaction candidate before495 severe effect occlusion.'),
 (500,523.8,['16'],'Forward projectiles/targets and raised cast; stop before525 task popup.')
]
for n,(a,b,guides,focus) in enumerate(pockets,1):
    bank['rows'].append(dict(id=f'dante-v2-{n:02}',source='dante',localInSeconds=a,localOutSeconds=b,
        nominalSourceInSeconds=2530+a,nominalSourceOutSeconds=2530+b,candidateSeconds=round(b-a,6),
        classification='actual-action-research-reserve',eligibleGuidePrefixes=guides,
        insertionScene=None,visibleAction=focus,viewerFocus=focus,
        diagramConnection='Projected caster/start, trajectory or surrounding space and target relationship. Final source-to-paragraph allocation is pending actual guide PCM and full recognition.',
        selection='research-reserve-not-final-selection',exactNativePtsApproved=False,
        continuousFinalCutApproved=False,finalCaptionPixelsApproved=False,actualQuotaApproved=False))
for key in bank['sources']:
    ordered=sorted((r for r in bank['rows'] if r['source']==key),key=lambda r:r['localInSeconds'])
    assert all(a['localOutSeconds']<=b['localInSeconds'] for a,b in zip(ordered,ordered[1:])),key
actual=[r for r in bank['rows'] if r['source']!='ui']
bank.update(candidateActualSeconds=round(sum(r['candidateSeconds'] for r in actual),6),
    candidateDanteSeconds=round(sum(r['candidateSeconds'] for r in actual if r['source']=='dante'),6),
    uniqueIntervalsDoNotOverlap=True,finalActualSeconds=None,ratioApproved=False,exactNativePtsApproved=False,
    actionCapacityIsNotQuota=True,measuredNarrationAllocationApproved=False)
bank['notes'].extend(['Candidate capacity can overestimate usable action until continuous selected cuts are reviewed.',
    'No source interval may be assigned twice. Research context overlaps in earlier authoring are not final repeat permission.',
    'Preserve original useful explanations/PCM. Allocate short narration-timed 2.5D bridges where named-game action capacity is limited, then match other guide paragraphs to distinct observed action; never pad unrelated idle.'])
write(ROOT/'projects/player-customization/sources/native-source-bank-v2.json',bank)
print(json.dumps(dict(review=rel(BASE/'dante-continuous-crop-review-v2.json'),boundedWindowEndpointsRead=len(rows),
    bank=rel(ROOT/'projects/player-customization/sources/native-source-bank-v2.json'),researchActionCapacitySeconds=bank['candidateActualSeconds'],
    danteResearchCapacitySeconds=bank['candidateDanteSeconds'],finalQuotaApproved=False),ensure_ascii=False))
