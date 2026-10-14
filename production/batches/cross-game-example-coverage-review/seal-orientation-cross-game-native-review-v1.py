"""Seal directly read native sample boards and bounded concept-matched cut planning."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
ROOT=Path(__file__).resolve().parents[3]
B=Path(__file__).resolve().parent
O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=O/'cross-game-native-direct-review-v1.json';assert not out.exists()
mp=O/'cross-game-native-v1/manifest.json';m=read(mp)
closure=read(O/'cross-game-native-actual-exit-verification-v1.json')
assert closure['workerClosed'] and closure['actualOuterExitCode']==0 and closure['manifestSha256']==sha(mp)
for row in m['samples']+m['boards']:assert sha(ROOT/row['path'])==row['sha256']
for row in m['sources']:assert sha(ROOT/row['sourcePath'])==row['sourceSha256']
notes={
 'descenders':dict(boardsDirectlyRead=16,samplesDirectlyRead=77,
  observations=[
   '680–688: rear rider/bicycle turns through alternating bends; camera follows. Screen location and body tilt are separable observations, not measured world-axis values.',
   '690–693.5: ramp approach, upside-down bicycle/rider at691.5–692, upright at692.483/692.5 and landing/backflip HUD at693. Use one observed flip for before/action/result.',
   '694–696.2 and697.8–700 also contain distinct jumps; preserve as optional unique action bank, not repeat/pad the first jump.',
   '703 already shows fallen rider/bicycle beneath finish gate;703.5 onwards finish menu and detached/fallen rider. Exclude these from normal rigid-bicycle comparison.',
   'Rider limbs articulate and camera changes perspective: a body screen direction is illustrative, not one rigid rotation for the entire rider/bicycle.'],
  plannedNativeWindows=[dict(id='desc-turn',nativeIn=40800,nativeOutExclusive=41280,seconds=[680,688],purpose='Screen position versus observed body lean through bends.'),
   dict(id='desc-first-flip',nativeIn=41400,nativeOutExclusive=41610,seconds=[690,693.5],purpose='Upright approach → inverted bicycle → upright result.'),
   dict(id='desc-second-flip',nativeIn=41640,nativeOutExclusive=41820,seconds=[694,697],purpose='Distinct optional action, not replayed first flip.'),
   dict(id='desc-third-flip',nativeIn=41820,nativeOutExclusive=42060,seconds=[697,701],purpose='Optional distinct flip/landing with visible trail; no finish menu.')],
  rejected=[dict(seconds=[703,705],reason='Crash and finish-result menu change actor state and camera.'),dict(seconds=[700,735],reason='Prior normal-playback review shows day-to-night/task discontinuity; not same-world continuous comparison.')]),
 'trailmakers':dict(boardsDirectlyRead=17,samplesDirectlyRead=81,
  observations=[
   '665–667.5 aircraft remains on runway with0MPH while viewpoint moves around it. Do not narrate this apparent rotation as measured airframe roll.',
   '668–674.5: rear runway acceleration, takeoff and increasingly tilted wings above sea/cliff. Nose, wings and underside offer an asymmetric frame; camera also moves.',
   '675–681 changes to side view and banks above sea; keep a distinct declared shot, no interpolated track across abrupt viewpoint change.',
   '682–684: bridge beam/pillar crosses the view/aircraft wing region. Hide occluded endpoints; for primary comparison use clearer668–674.5 and684.5–689.5 cuts.',
   '684.5–689.5: nose-on view and wings changing from tilted to near-level, followed by a side/top view.684.5 viewpoint change is a cut boundary.',
   '690–695.5 mostly near-level ocean flight is a comparison result, not unrelated quota.695.5–696 view changes sharply again; new shot required.'],
  plannedNativeWindows=[dict(id='trail-takeoff-bank',nativeIn=40080,nativeOutExclusive=40470,seconds=[668,674.5],purpose='Runway before → takeoff/wing tilt → banked flight.'),
   dict(id='trail-bank-level',nativeIn=41070,nativeOutExclusive=41370,seconds=[684.5,689.5],purpose='Clearly declared new viewpoint: tilted wings → near-level result.'),
   dict(id='trail-runway-view',nativeIn=39900,nativeOutExclusive=40050,seconds=[665,667.5],purpose='Optional view-change example at0MPH; no physical-roll assertion.')],
  rejected=[dict(seconds=[681.5,684.5],reason='Cliff/bridge occlusion is weaker than clear selected wing views.'),dict(seconds=[674.5,675],reason='Viewpoint discontinuity cannot support continuous object/world tracking.')]),
 'space-engineers':dict(boardsDirectlyRead=12,samplesDirectlyRead=59,
  observations=[
   '170–171.5 large preview;172 small preview. A size/grid selection change occurs before the first rotation. Do not describe that jump as rotation.',
   '172–173.6 small upright green-box ghost;173.8–174.2 small horizontal ghost;174.4–175 upright again. These are actual sampled orientation changes; exact first transition frame not established.',
   '175.4 preview absent,175.5–176.8 large preview,176.833 small horizontal preview. Two size/grid changes, not one rigid rotation trajectory.',
   '177–177.6 horizontal small ghost;177.8–178 upright/front-facing;178.2–178.8 horizontal.178.983/179 orange preview overlaps solid component;180–183.983 placed gear with green base and no rotation-key overlay.',
   'Lower help/inventory/facecam conflict with960970 captions. Proposed source crop480,240,960,540 makes the small part readable and excludes the lower facecam; exact cropped pixels require review before adoption.',
   'Rotation-key arrows are UI for placement, not proof of game-world axis conventions, numerical engine matrix or physical90° measurement. Place preview versus solid part must be narrated.'],
  plannedNativeWindows=[dict(id='space-preview-rotation',nativeIn=10320,nativeOutExclusive=10500,seconds=[172,175],purpose='Upright ghost → horizontal ghost → upright ghost. Crop/readability review required.'),
   dict(id='space-rotation-placement',nativeIn=10620,nativeOutExclusive=10890,seconds=[177,181.5],purpose='Small horizontal preview → upright/sideways changes → placed solid part. Crop/readability review required.')],
  rejected=[dict(seconds=[170,172],reason='Grid/size selection changes confound rigid-rotation comparison.'),dict(seconds=[175,177],reason='Absent/large/small preview changes need separate explanation; exclude primary orientation action.')])}
data=dict(reviewedAt=datetime.now(timezone.utc).isoformat(),manifest=mp.relative_to(ROOT).as_posix(),manifestSha256=sha(mp),
    actualSession=6852,actualOuterExitCode=0,actualCompletion='8cd13e',sampleCount=217,boardCount=45,
    all217NativeSamplesAnd45BoardsDirectlyRead=True,allSampleBoardAndSourceHashesMatched=True,
    exactNativePtsVerified=True,normalPlaybackReview='cross-game-normal-playback-direct-review-v1.json',
    observations=notes,boardProofs=m['boards'],sampleProofs=m['samples'],
    sourcePlanningOnly=True,selectedCutsSourcePlanningApproved=True,croppedSpacePixelsApproved=False,
    nativeAllBetweenFramesApproved=False,narrationTimedAnnotationsApproved=False,finalNativeCutAllocationApproved=False,
    finalFourGameTeachingApproved=False,sourceOrHumanRightsApproved=False,
    unchangedBaseline24AndExisting6Pcm=True,newSourceCopies=0,foreignFilesChanged=0,
    next='Review enlarged Space Engineers pixels; confirm official source/permissions and recent use. Write independent matching KOEN bridges describing observed before/action/result and common/different frame use. Keep21a-p01 repair held.')
out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf-8')
cp=read(O/'latest-checkpoint.json');cp.update(crossGameNativeReview=out.relative_to(ROOT).as_posix(),
    crossGameNativeSamplesRead=217,crossGameNativeBoardsRead=45,activeOwnedWorkers=0,
    stage='cross-game-native-planning-approved-crop-and-script-pending',next=data['next'],recordedAt=data['reviewedAt'])
(O/'latest-checkpoint.json').write_text(json.dumps(cp,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(samples=217,boards=45,directReview=True,sourcePlanningOnly=True,finalApproval=False)))
