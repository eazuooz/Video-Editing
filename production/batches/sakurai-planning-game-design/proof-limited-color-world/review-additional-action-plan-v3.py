"""Cull candidate quota from already read action notes, without adopting footage."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json
ROOT=Path(__file__).resolve().parents[4];BASE=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
prior=read(BASE/'additional-action-candidates-v2.json')
total=sum(x['candidateSeconds'] for x in prior['candidates']);assert total==49
assert sha(ROOT/prior['protectedOriginalBank']['path'])==prior['protectedOriginalBank']['sha256']
coarse=read(BASE/'chicory-coarse-direct-review-v1.json')
boards=[]
source=coarse['verifiedSources'][0]
for number in [9,11,12,14,15]:
    p=ROOT/f'shared/output/limited-color-world/preflight/chicory-official-v1/chicory-b-roll-1/board-{number:03}.jpg'
    expected=next(x for x in source['boards'] if x['path']==rel(p))
    assert sha(p)==expected['sha256'];boards.append(dict(path=rel(p),sha256=sha(p),reviewPurpose='Distinguish initial room sweeping/particles from paint, route and state examples; no fresh coarse extraction or new blanket approval.'))
held={
    'palette-before-current':'Existing full native notes place these strokes outside playable geometry; retain held rather than count4.5s.',
    'room-paint-continuation':'Existing full native notes identify unrelated outside-room doodles after158.5; retain held9.5s.',
    'mushroom-arrival':'Existing native notes identify repeated lower bouncing27–28; distinct source frames alone do not justify duplicate mechanism quota.',
    'flower-stack-state-continuation':'Existing native notes identify wait56.5–58.5 and repeated bouncing58.5–61.5; retain held.',
    'flower-route-arrival':'Existing native notes place lower-ground walking after95.5 beyond the demonstrated changed flower heights; retain held.',
}
remaining=[]
for x in prior['candidates']:
    if x['key'] in held:continue
    if x['key']=='room-to-corridor':
        for key,a,b in [('room-door-approach',99,102),('portrait-corridor-travel',108,111)]:
            remaining.append(dict(key=key,sourceKey=x['sourceKey'],startSeconds=a,endSeconds=b,candidateSeconds=b-a,
                                  caveat='Coarse movement only. Exclude door/area transition102–103 and corridor dialogue103–107; exact native boundary/framing not approved.',provisionalInsertion='02-contours'))
    else:
        remaining.append(dict(key=x['key'],sourceKey=x['sourceKey'],startSeconds=x['plannedStartFrame']/60,endSeconds=x['plannedEndFrameExclusive']/60,
                              candidateSeconds=x['candidateSeconds'],caveat=x['caution'],provisionalInsertion=x['provisionalInsertion']))
assert sum(x['candidateSeconds'] for x in remaining)==19.5
further=[
    dict(key='portrait-corridor-continuation',sourceKey='chicory-b-roll-1',startSeconds=123,endSeconds=125,candidateSeconds=2,
         provisionalInsertion='02-contours',caveat='Native verification needed for active navigation and no portrait dialogue/transition. Announces the different corridor object, not house painting.'),
    dict(key='town-path-first-part',sourceKey='chicory-b-roll-1',startSeconds=207,endSeconds=210,candidateSeconds=3,
         provisionalInsertion='06-route-information',caveat='Coarse route travel only; exclude210+ until transition211 is bounded. Needs stated path-boundary focus, not unrelated walking quota.'),
    dict(key='town-path-second-part',sourceKey='chicory-b-roll-1',startSeconds=212,endSeconds=215,candidateSeconds=3,
         provisionalInsertion='06-route-information',caveat='Different source shot after211 transition. Native route/actor/caption clarity and dialogue216 onset must be checked; no single continuous-route claim.'),
    dict(key='fence-route-part1',sourceKey='chicory-b-roll-1',startSeconds=357,endSeconds=359.5,candidateSeconds=2.5,
         provisionalInsertion='06-route-information',caveat='Coarse outlined-fence travel toward shop. Exclude transition360, announce changed route and verify visible before/action/after.'),
    dict(key='fence-route-part2',sourceKey='chicory-b-roll-1',startSeconds=363,endSeconds=365,candidateSeconds=2,
         provisionalInsertion='06-route-information',caveat='Separated from360/362 transitions. Verify actor/path/destination boundary rather than use unrelated transit as filler.'),
]
all_candidates=remaining+further
bank=read(BASE/'source-action-bank-v1.json')
original_windows=bank.get('actions',bank.get('selectedActions',bank.get('cuts',[])))
for x in all_candidates:
    x.update(plannedStartFrame=round(x['startSeconds']*60),plannedEndFrameExclusive=round(x['endSeconds']*60),nativePtsPerFrame=256,
             exactNativeBoundaryApproved=False,allContinuousFramesReviewed=False,normalPlaybackApproved=False,
             finalCueUiApproved=False,sourceAdoptionApproved=False,selected=False,sourceAudio=False,loop=False,slowdown=False)
out=BASE/'additional-action-editorial-review-v3.json';assert not out.exists()
record=dict(schemaVersion=3,reviewedAt=datetime.now(timezone.utc).isoformat(),
    priorPlan=rel(BASE/'additional-action-candidates-v2.json'),priorPlanSha256=sha(BASE/'additional-action-candidates-v2.json'),
    candidateArithmeticCorrection=dict(actualOriginalPlanSum=49.0,priorManualResourceSummary=49.5,approvedFootageUnchanged=True),
    fullCoarseAndFullNativeObservationNotesDirectlyRead=True,initialRoomBoardsDirectlyReexamined=boards,
    initialRoomActionHeld='Initial room sweeping and particles around furniture are not the later paint/erase/height demonstrations. Do not relabel the broom or intrinsic story color loss as a color-vision preview or add its whole duration to fill quota.',
    heldCandidates=[dict(key=k,reason=v) for k,v in held.items()],
    splitRoomCandidate='99–111 is not continuously clean: split99–102 and108–111, hold103–107 dialogue and transitions.',
    remainingOriginalPlanPotentialSeconds=19.5,furtherCoarseOnlyCandidateSeconds=12.5,
    candidates=all_candidates,totalPotentialSeconds=sum(x['candidateSeconds'] for x in all_candidates),
    protectedOriginalBankSha256=sha(BASE/'source-action-bank-v1.json'),protectedOriginalPlanningSeconds=101.5,
    potentialTimeIsNotApprovedFootage=True,additionalAdoptionApproved=False,
    sourceMediaGenerated=False,sourceFramesExtracted=False,sourceDecodeRepeated=False,gitImagesAdded=0,
    nextAction='After measured retained8PCM and3additive bridges determine the exact deficit. Only new useful, action-led intervals with native in-out/before-action-after/fixed-caption clearance can be adopted. Reject unresolved walking/dialogue/idle; secure fresh concept-matched official footage if this bank cannot cover the measured60% without duplication.')
assert record['totalPotentialSeconds']==32
out.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Original proposal49s corrected; held5 weak candidates and split dialogue.32s potential remains, adoption0; protected101.5s unchanged.')
