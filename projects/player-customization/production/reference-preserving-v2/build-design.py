"""Build D21's single design package; no media jobs or external mutations.

The current narration and source selection are inputs, never rewritten here.
All times below are inspected LOCAL source windows, not final timeline cues.
"""
from pathlib import Path
import datetime
import hashlib
import json

ROOT = Path(__file__).resolve().parents[4]
HOME = ROOT / 'projects/player-customization/production/reference-preserving-v2'
SCRIPT = ROOT / 'projects/player-customization/script/reference-preserving-v2'
LOCAL = ROOT / 'projects/player-customization/production/local/reference-preserving-v2'
VISUAL = ROOT / 'motion-canvas/src/projects/player-customization/revision-v2/visuals.tsx'


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def link(path):
    path = Path(path)
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': digest(path)}


selection = read(HOME / 'source-selection.json')
audit = read(HOME / 'script-audit.json')
reference = read(HOME / 'reference-audit.json')
auth = read(HOME / 'authorization.json')
control = read(ROOT / 'shared/publishing/video-production-control.json')
assert auth['slug'] == 'player-customization' and auth['fullProductionAuthorized']
assert not auth['automaticNextVideo'] and not auth['youtubeUploadAuthorized']
assert selection['allSelectedClaimsActuallyViewed'] and selection['referenceOnlyMediaExcluded']
texts = {lang: read(SCRIPT / f'narration.{lang}.json') for lang in ('ko', 'en', 'spoken-ko')}
assert all(t['status'] == 'locked-after-independent-footage-and-complete-text-review' for t in texts.values())
assets = read(LOCAL / 'assets/provenance.json')
asset_ids = {a['id'] for a in assets}
sources = {s['key']: s for s in selection['sources']}
assert len(sources) == 6 and sum(s['nintendoGame'] for s in sources.values()) == 2
paragraph_audit = {(p['sceneId'], p['paragraph']): p for p in audit['paragraphReviews']}
assert len(paragraph_audit) == 35
for lang, ak in [('ko', 'ko'), ('en', 'en'), ('spoken-ko', 'spokenKo')]:
    for scene in texts[lang]['scenes']:
        for n, line in enumerate(scene['lines'], 1):
            actual = hashlib.sha256(line.encode('utf-8')).hexdigest()
            assert actual == paragraph_audit[(scene['id'], n)]['paragraphSha256'][ak], (lang, scene['id'], n)

# A source-bank window may support multiple narrated references, but is not
# automatically a duplicated production cut. Final local in/out is root-owned.
window_rows = [
    ('J1', 'jets2-shop', 4, 68, 'Equipment selection and adjacent firing-result layout', ['01', '02'], 'Read selected equipment and its corresponding test ship together; exclude another ship as an alleged effect of this selection.'),
    ('J2', 'jets2-shop', 68, 116, 'Decision-relevant shot pattern and shop/test adjacency', ['02'], 'A moving result supports reach/direction/sequence only where visible; no invented weapon statistics.'),
    ('J3', 'jets2-shop', 120, 158, 'Further choices and distinguishable two-ship shots', ['02', '06'], 'Keep the selected item, correct ship and shot origin linked; do not identify both ships as one weapon.'),
    ('J4', 'jets2-shop', 158, 196, 'Choice and adjacent trial, revisited for iteration cost', ['06', '08'], 'A return to the principle uses unused necessary source moments, not a replay to fill duration.'),
    ('A1', 'acvi-assembly', 154.8, 161.5, 'BST-G2/P04 prospective booster comparison', ['03'], 'Menu Boost Speed306→320 and QB EN Consumption480→560; candidate preview is not installed state or measured movement speed.'),
    ('A2', 'acvi-assembly', 234.6, 240.8, 'Preview then installed booster, Boost Speed320 retained', ['03', '08'], 'Show EQ/retained menu state only if the narration needs confirmation; never substitute unrelated TRAINING footage as this loadout test.'),
    ('B1', 'botw-menu', 203.5, 211.5, 'Armor category, clothing choices, equip and changed appearance', ['04'], 'No temperature-resistance symbol, sort operation, late-game inventory or mirror claimed.'),
    ('M1', 'mh-menu', 6, 18, 'Forge Armor body-part icons, selected details and preview', ['04'], 'This is armor-forging preview, not completed crafting or permanent equipment.'),
    ('M2', 'mh-menu', 26, 38, 'Further body-part selection linked to character preview', ['04'], 'Sorting is explained separately in our fictional list; do not announce actual sorting here.'),
    ('T1', 'terratech-build', 44, 62.5, 'Cab/block chassis construction with connection markers', ['06'], 'Only meaningful attachment changes are usable; no idle campaign travel or claim that this is a new-world tutorial.'),
    ('T2', 'terratech-build', 62.5, 71.8, 'Held GSO Dirt Wheel→solid wheel→front GSO Rock Drill', ['06'], '63.5s is held part,65.5s solid wheel,71.5s solid drill. Explain connection markers and green preview before calling a part attached.'),
    ('T3', 'terratech-build', 71.8, 100, 'Additional clearly visible assembly choices', ['06'], 'Camera orbit is not driving. Only relevant actual part changes are capacity, not every second of the window.'),
    ('T4', 'terratech-build', 150, 176.5, 'In-world edit→actual drive→reopen inventory→edit result', ['06'], '154.5s held Riser Wheel;158–160s includes detachment/adjustment;162–166.5s actual translation;167s reopen;171.5s block preview;175.5s solid raised blocks. No measured improvement claimed.'),
    ('N1', 'acnh-appearance', 139, 148.7, 'Initial character appearance selection context', ['07'], 'Initial creation, not a mirror/wardrobe operation or Switch2Edition.'),
    ('N2', 'acnh-appearance', 148.7, 154.5, 'Hairstyle choice changes same-avatar preview', ['07'], '150.5/151.5 still pair uses the same source/crop; no synthetic morph or claimed power increase.'),
    ('N3', 'acnh-appearance', 154.5, 177.3, 'Eyes/nose/mouth and color choices change preview', ['07'], 'Only actually visible choices are shown; no combat-stat claim.'),
    ('N4', 'acnh-appearance', 177.3, 179.5, 'Confirm OK and retain chosen appearance', ['07', '08'], 'Confirmation result is distinct from a hover-only preview; no unobserved later mirror behavior.')
]
windows = []
for wid, key, start, end, purpose, scene_ids, limits in window_rows:
    source = sources[key]
    assert any(start >= r['localIn'] and end <= r['localOut'] for r in source['recommendedRanges'])
    windows.append(dict(id=wid, sourceKey=key, sourceFile=source['media']['path'], sourceSha256=source['media']['sha256'],
                        localIn=start, localOut=end, upperBoundSeconds=round(end-start, 6), sceneIds=scene_ids,
                        semanticPurpose=purpose, classification='independent-gameplay', speed=1, loop=False,
                        limits=limits, exactFinalCut='pending measured narration and direct moving-output review',
                        internalSourceCutHandling='Split any original source cut into separate production cuts; clear/retarget every annotation.'))


def evidence(ids=(), stills=(), diagram=None, caveat=''):
    return dict(sourceWindows=list(ids), explanationAssets=list(stills), authoredDiagram=diagram,
                caveat=caveat or 'Follow source-window scope; a screenshot is explanation, not additional actual-footage capacity.')


# Each row is one current paired paragraph: prerequisite → visual/cue → next
# original point. Claim text and all105 hashes come from the completed audit.
P = {
 '01': [
  (evidence(['N1', 'N2'], ['acnh-before']), 'Start from spending time choosing a character or equipment; no prior knowledge of customization is assumed.', 'Greeting stays one continuous spoken sentence; show the recognizable appearance screen, without a reset after the brand.', 'The familiar experience becomes the claim that choosing is part of the fun.'),
  (evidence(['J1', 'N2'], ['jets-preview', 'acnh-after'], 'three-step overview'), 'Result, ease of selection/testing, and taste are three design viewpoints, not mandatory player steps.', 'Reveal result→choice/test→expression in that spoken order; only the current step is emphasized.', 'End on the first promised viewpoint: see the result of a choice.'),
  (evidence(['J1'], ['jets-preview'], 'equipment→firing result'), 'A shop equips a ship; a nearby test area displays the shot result.', 'Keep the shop image visible; trace weapon choice→visible shot result with destination appearing after the arrow.', 'Carry the same shop/test state directly into02-1.')
 ],
 '02': [
  (evidence(['J1'], ['jets-preview'], 'selection→firing'), 'Define side-scrolling shooter and equipment/test area before describing its interface.', 'Identify the equipped weapon selection, then the adjacent right test area; two-ship distinction remains readable.', 'Now the viewer knows where the numeric description and moving result are.'),
  (evidence(['J2', 'J3'], ['jets-weapons'], 'decision-relevant differences'), 'Damage/fire rate are descriptions; reach, spread and sequence are observable behaviors.', 'Reveal only a label matching the currently visible shot pattern; no fabricated range or cadence measurement.', 'Move from general differences to reading this particular test window.'),
  (evidence(['J2', 'J3'], ['jets-weapons'], 'two origin labels', 'Both ships are visible; link a shot to its own origin. Do not call all visible projectiles the chosen weapon.'), 'A projectile has a visible origin; separate the two ships before comparing direction/timing.', 'Named hollow outlines on verified ship origins and right test region appear with the cue, track/hide on occlusion, clear at source cut.', 'Having seen how to read it, define the useful preview function.'),
  (evidence(['J2'], ['jets-preview'], 'Preview definition'), 'Preview means seeing an outcome before committing; visual spectacle alone does not explain a choice.', 'Replace the right explanation with 프리뷰 / Preview and decision-relevant result; image remains the same actual shop.', 'A readable effect is necessary; next ask whether its difference gives a reason to choose.'),
  (evidence(['J3'], ['jets-preview'], 'visible difference→reason to choose'), 'If one option wins in every respect, comparing others has less purpose; this is a conditional principle.', 'Retain the shop while question emphasis replaces the preview definition. Do not insert an unrelated battle.', 'Carry the visible-difference question into03 real booster benefit/cost.')
 ],
 '03': [
  (evidence(['A1'], ['acvi-assembly'], 'movement part label'), 'ACVI combines robot parts; define booster as the component for movement before reading stats.', 'Name the booster candidate and component context; retain visible comparison table, not unrelated paint/logo screen.', 'Read one displayed benefit and one linked cost.'),
  (evidence(['A1', 'A2'], ['acvi-assembly'], 'benefit then cost', 'Historic captured menu values; no actual speed measurement, current patch claim, or claim that preview is already equipped.'), 'Define Quick Boost as a short evasive move and energy as its consumed resource; trade-off links benefit and sacrifice.', 'Highlight Boost Speed306→320 first, QB EN Consumption480→560 second; use words/numbers and semantic colors together.', 'With a real benefit/cost understood, test the same reasoning with a small explicit calculation.'),
  (evidence([], [], 'fictional A/B rate calculation', 'Fictional weapons and values, visibly labeled. No ACVI stat attribution.'), 'One-shot damage and time between shots are separate quantities; sustained hits allow an average per second.', 'Introduce drawn A/B weapons, then100/2=50 and40/0.5=80; reveal formula after quantities and keep sustained-hit condition visible.', 'The higher average raises the concrete question of a single firing opportunity.'),
  (evidence([], [], 'one-shot opportunity at90 health', 'One opportunity; misses, armor, first-shot transient timing and other real-game conditions are excluded.'), 'Remaining health is the damage requirement and one chance permits only one shot.', 'Keep the same A/B objects; replace average formula with100≥90 and40<90. Do not show a second shot or a new unrelated enemy.', 'Conclude that the situation defines which strength matters.'),
  (evidence(['A2'], [], 'strengths→finding burden'), 'Distinct options create meaningful combinations, but locating a desired item is a separate interaction cost.', 'Preserve A/B identity as the message changes to finding candidates; actual booster confirmation can be a short necessary bridge only.', 'Carry the unresolved finding burden directly into04 categories/icons.')
 ],
 '04': [
  (evidence(['B1'], ['botw-armor'], 'category→item choice', 'No thermal-resistance symbols or observed sorting claim in this opening capture.'), 'A category groups item types; a selection belongs to that category.', 'Show actual armor category and clothing candidates before explaining generic icons; keep equipment preview readable.', 'The category picture becomes the concrete definition of an icon.'),
  (evidence(['B1'], ['botw-armor'], 'authored same-shape icons plus names', 'Right-hand sword/boot drawings are our explanatory icons, not copied BOTW inventory items.'), 'Define icon as a small type-identifying picture; similar shapes also require readable names/functions.', 'Compare two authored swords with distinct names/function labels beside the real category screenshot; never imply invented icons are native game UI.', 'Apply the same selection→information relationship to a different menu structure.'),
  (evidence(['M1', 'M2'], ['mh-menu'], 'body-part icon→details→character preview', 'Forge Armor preview only; no completed craft, permanent equip or sort operation.'), 'Head/chest/arm/body-part columns identify which armor slot is previewed.', 'Trace body-part icon→selected details→character preview in the narrated order. Each destination responds after its arrow.', 'Switch explicitly to an authored list to demonstrate the missing sorting function honestly.'),
  (evidence([], [], 'fictional three-item sorting', 'Large sword12, dagger8, bow10 are illustrative values, not measured MH or BOTW items.'), 'Sorting changes order by a criterion; filtering/categories narrow a set and must not be conflated with reordering.', 'Keep the original three-item list left; right changes12,8,10→12,10,8. Same candidates retain shapes/names; only row positions change.', 'The narrowed, legible list persists as the next question: which starting combination?'),
  (evidence([], [], 'sorted candidates→starting combination'), 'A newcomer can find candidates and still lack a starting set.', 'Retain the same three candidates rather than reset the interface; introduce the starting-combination need on the right.', 'Carry the sorted candidate set and need into05 automatic equipment.')
 ],
 '05': [
  (evidence([], [], 'criterion→candidates→equipped slots', 'Wholly authored UI; not a claim that BOTW or Iceborne implements this shown auto-equip system.'), 'Automatic equipment selects and equips using a rule; candidates and equipment slots are different states.', 'Show the three columns with empty destination; recognizable authored sword/shield/boots establish slots without generic cubes.', 'The selection rule needs an explicit objective.'),
  (evidence([], [], 'attack goal versus cold-survival goal', 'Illustrative objectives; no observed resistance operation or universal-optimum claim.'), 'Strongest requires a criterion; attack total and cold survival can favor different sets.', 'Keep the same candidate objects; expose attack/cold labels as alternate goals, with no invented numeric optimization.', 'Choose one goal before filling the starting equipment.'),
  (evidence([], [], 'attack-goal automatic starting set'), 'A rule chooses eligible candidates and then fills slots; the animation is a teaching model, not a solved commercial-game optimization.', 'Attack goal outline→trace to candidates→candidate response→trace to equipped set→green equipped objects. Persistent explanation-only label.', 'The resulting starting set remains on screen so one manual revision is understandable.'),
  (evidence([], [], 'one boot manually revised'), 'An automatic starting point need not remove player choice.', 'Retain the auto-equipped set and change only boots B with a named outline; carry that changed object toward the test loop.', 'A usable set is prepared;06 asks whether it feels right in motion.')
 ],
 '06': [
  (evidence(['J4'], ['jets-preview'], 'selection/test distance'), 'Menu expectation and actual feel may differ; effort between editing and trial is an iteration cost, not a measured statistic here.', 'Keep a selected setup visible and introduce 바꾸기; show the next needed action rather than an unexplained loop.', 'A construction sandbox provides an actual change→motion→change sequence.'),
  (evidence(['T1', 'T2', 'T3', 'T4'], ['terratech-build'], 'in-world edit→drive→edit', '160s screenshot is assembly context, not by itself motion proof. Actual movement is162–166.5; returned editing167–175.5.'), 'Define TerraTech as constructing vehicles from attachable parts; explain held preview versus solid part and editing state.', 'Show wheel/drill attachment before actual movement, then reopen inventory and retain the changed raised blocks. Mark these specific states; hide labels across occlusion/cuts.', 'The same loop can also be close in screen space, returning to the earlier shop.'),
  (evidence(['J4'], ['jets-preview'], 'adjacent equipment/test area'), 'The long trip is a conditional design counterexample; Jets2 actually keeps test area adjacent.', 'Return to unused meaningful Jets2 shop moments; label actual equipment/test regions and draw a short connection. No claimed measured travel time.', 'The two actual examples establish the general short iteration loop.'),
  (evidence(['T4', 'J4'], ['jets-preview'], 'change→test→change loop'), 'A trial provides feedback for the next choice; it can occur during selection.', 'Reveal test node only after change, then return arrow and revised node. Show source→trace→response; never use a decorative cyclic pulse.', 'The liked outcome is now contrasted with performance alone.'),
  (evidence(['N1'], ['jets-preview'], 'performance versus preference handoff'), 'Liking a result need not imply improved combat or movement.', 'Keep the completed loop state and shift only its result label to the preference question; begin the new avatar shot when07 introduces appearance.', 'Carry the changed-result question into07 without reset music/title sequence.')
 ],
 '07': [
  (evidence(['N1', 'N2'], ['acnh-before'], 'same avatar appearance selection', 'This is initial creation, not demonstrated mirror operation. Do not label the original Switch capture Switch2.'), 'Introduce ACNH and face/hair choices before showing changed appearance.', 'Show the actual creation menu and the current avatar. Same full-frame crop/anchor throughout the before/after pair.', 'Read the visible response to choosing another option.'),
  (evidence(['N2', 'N3', 'N4'], ['acnh-before', 'acnh-after'], 'same-anchor actual before/after'), 'Preview responds to choice; confirmation is distinct from hovering. Taste is not a combat-stat measurement.', 'At the corresponding spoken change replace150.5s still with151.5s still at exactly the same anchor; no pan or fabricated morph. Actual clip shows real choices and optional confirmation.', 'Having seen the preference result, broaden to different tastes without adding unrelated games.'),
  (evidence(['N3'], ['acnh-after'], 'performance question versus preference question'), 'A robot-looking/cute-looking preference is a general comparison; unchanged performance is a design possibility, not measured here.', 'Keep recognizable avatar evidence and separate 잘 싸우는가 from 마음에 드는가 using labels as well as color.', 'Return to the design choice of linking or separating appearance and function.'),
  (evidence(['N4'], ['acnh-after'], 'what changed→visible chosen result'), 'Games can link or separate performance/appearance; the player must understand what a choice changes.', 'Retain chosen avatar and name 성능/외형; avoid a fabricated buff icon or power statistic.', 'Carry 무엇을 바꾸는가 and 결과 확인 into08 process-level conclusion.')
 ],
 '08': [
  (evidence([], ['jets-preview', 'acvi-assembly'], 'choosing process synthesis'), 'All evidence has already been introduced; recap does not require a new game or new rule.', 'Pair inspected shop/booster stills at790px width, emphasizing the act of choosing instead of resetting to an unrelated montage.', 'Connect the existing viewpoints in original order.'),
  (evidence([], ['jets-preview', 'acvi-assembly'], 'result→comparison→finding→trial'), 'These are design considerations, not a mandatory five-step player workflow.', 'Reveal the result/comparison/find/trial labels in order while retaining source evidence; no replay used as actual-time padding.', 'Make room for the fifth original viewpoint: expression without a power requirement.'),
  (evidence([], ['acvi-assembly', 'acnh-after'], 'performance fun versus expression fun'), 'Combat/movement and appearance can provide different pleasures.', 'Switch the right inspected image to the chosen avatar, retaining the left booster context; use independent labels rather than implying an in-game stat relationship.', 'Finish on both the customizable object and its selection/check/revision interface.'),
  (evidence([], ['acvi-assembly', 'acnh-after'], 'what/how plus viewer experience question'), 'The viewer can inspect what changes and how players choose, check and revise it.', 'Keep both concrete examples, show the exact viewer-question text above the fixed caption area, then enter the preserved10s member ending.', 'End of authorized selected episode; no next-video production or platform publication is implied.')
 ]
}

layouts = {
 '01': dict(kind='overview', objects=['ACNH avatar menu', 'Jets2 equipment/test screenshot', 'three-step overview'],
            placement='Cue0: one1040×585 image atMC(0,-26). Cue1: two790×444.375 images at(-440,-55)/(440,-55). Cue2:880×495 shop at(-420,-35), right labelsMCx525.',
            motion='Three corresponding paragraph cues replace, rather than stack, image states. Equipment→firing arrow traces down and destination fades in only after trace.',
            endState='Jets2 shop plus choice→firing result; carry this source state to02.'),
 '02': dict(kind='effects', objects=['Jets2 selected item', 'adjacent test area', 'two distinct ships', 'Preview definition'],
            placement='880×495 contained16:9 source still atMC(-420,-35); right explanation atMCx525, y-295…238. Image caption33px below image; bottom noteMCy311.',
            motion='Cue0 equipment→firing flow; cue1 source still changes to140s; cue2 two-ship warning; cue3 actual shop100s plus Preview; cue4 replaces definition with selection-reason question.',
            endState='A visible effect invites a meaningful benefit/cost comparison in03.'),
 '03': dict(kind='tradeoffs', objects=['BST-G2/P04 comparison', 'Boost Speed306/320', 'QB EN Consumption480/560', 'fictional A/B weapons', 'one-shot health90'],
            placement='First two cues:880×495 ACVI screenshot left, right numbers58px. Cues2–4:drawn A/B centeredMCx-460/+460; gun bodiesMCy-180, damage/intervalMCy-45; calculationMCy144 and conditionMCy238.',
            motion='Boost benefit appears before energy cost. Replace the actual screenshot model with visibly fictional guns at cue2; quantities→formula→50/80. Cue3 retains guns, changes only opportunity/health and shows100≥90 versus40<90. Cue4finding need.',
            endState='Distinct options remain useful only if desired candidates can be found.'),
 '04': dict(kind='find', objects=['BOTW armor category', 'authored icon/name/function examples', 'Iceborne body-part details/preview', 'fictional sorted list'],
            placement='BOTW/Iceborne source880×495 atMC(-420,-35); right icons/labelsx380/670 or525. Sorting:two listsMCx-440/+440 with rowsy-146,-10,126; explanation-only noteMCy311.',
            motion='Cue0real categories; cue1authored similar swords plus names/functions; cue2body-part→detail→preview progressive arrows; cue3clear game screenshot and animate same candidates12,8,10→12,10,8; cue4retain narrowed list for starting-set handoff.',
            endState='Sorted candidates are available, but a starting combination is still needed.'),
 '05': dict(kind='auto', objects=['criterion', 'three candidate equipment shapes', 'initial equipment slots', 'manually changed boots B'],
            placement='Three columnsMCx-590/0/+590, headingsMCy-227; recognizable sword/shield/boots nearMCy-48; permanent explanation-only disclaimerMCy-300. Target outline330×100; candidate outline465×213.',
            motion='Empty equipment state→alternate objectives→select attack objective→trace to candidate response→trace to equipped sword/shield/boots. In last cue replace only the boots and name the changed slot; do not shuffle the whole set.',
            endState='The revised starting set must now be tried; preserve the object identity into06.'),
 '06': dict(kind='test', objects=['actual TerraTech constructed vehicle', 'same-world drive', 'inventory reopen', 'Jets2 adjacent trial', 'change/test/change loop'],
            placement='880×495 source evidence atMC(-420,-35). Right flow nodesMC(525,-218),(525,-27),(525,169), widths300/300/340; return path viaMCx811. Notesy270/311 stay above captions.',
            motion='Cue0change; cue1TerraTech image plus test node; cue2return to earlierJets2 screenshot; cue3return arrow plus renewed-change node. Actual footage cuts must separately show attachment→motion→re-edit. Cue4result/preference question.',
            endState='Short feedback loop established; its result need not mean stronger performance.'),
 '07': dict(kind='appearance', objects=['same ACNH avatar before/after', 'face/hair options', 'preference result', 'performance/appearance distinction'],
            placement='1000×562.5 full16:9 image atMC(-360,-55), same position/scale for both actual captures. Right labelsMCx640; bottom noteMCy311.',
            motion='Keep150.5s image until paragraph1+0.8motionScale; switch to151.5s actual image at the identical anchor without pan or synthetic interpolation. Later replace only right interpretation labels; chosen avatar stays.',
            endState='Chosen appearance is observable; what changes and how it is checked jointly inform08.'),
 '08': dict(kind='conclusion', objects=['already-introduced shop', 'already-introduced booster', 'chosen avatar', 'what/how design question'],
            placement='Two790×444.375 source stills atMC(-440,-65)/(440,-65); summarylineMCy294 at40–43px; no new inset slideshow or decorative panels.',
            motion='First pairJets2/ACVI; cue2switch pairACVI/ACNH. One concise sentence per current cue changes while underlying known objects preserve context.',
            endState='Concrete viewer question, then preserved branded member ending; no forced new chapter.')
}

annotation_rows = [
 ('jets-selection', ['J1', 'J2', 'J3'], 'Selected weapon/list and matching firing origin', '선택한 무기', 'blue/teal', '02-1…02-3', 'Trace the selected item to its own ship; keep the second ship separately named. Protect native list/stats and Test Range header.'),
 ('jets-trial', ['J2', 'J4'], 'Actual right test-area boundary and visible shot path', '시험 공간', 'green', '02-3 and06-3', 'Hollow boundary plus short origin-linked path only when visible. Hide path at occlusion/out-of-frame, never fabricate trajectories or ballistic measurements.'),
 ('acvi-benefit', ['A1'], 'Boost Speed menu row', '부스트 속도306→320', 'blue/teal', '03-2 first change', 'Underline/empty rectangle on exact row without covering numbers. Label menu comparison, never m/s.'),
 ('acvi-cost', ['A1'], 'QB EN Consumption menu row', '퀵부스트 에너지480→560', 'orange/red', '03-2 second change', 'Move focus from benefit to cost; do not imply every colored row is an improvement. QB definition precedes label use.'),
 ('acvi-equipped', ['A2'], 'EQ/installed indication and retained Boost Speed320', '장착 후 표시', 'green', '03-2 optional confirmation', 'Different source/local interval; clear old labels before showing retained state. Not a measured combat demonstration.'),
 ('botw-category', ['B1'], 'Actual armor category and clothing item icons', '방어구 분류', 'blue/teal', '04-1/04-2', 'Show category and actual candidate clothing, then equipped avatar result. No invented resistance icon or sort callout.'),
 ('mh-selection', ['M1', 'M2'], 'Body-part column, selected detail panel, character preview', '부위→상세→미리보기', 'blue/green', '04-3', 'Reveal the three real targets in order, protect item names/materials and label forging preview rather than completed craft/equip.'),
 ('terra-attach', ['T1', 'T2', 'T3'], 'Held/preview part and verified solid wheel/drill connection', '미리보기 / 장착', 'blue/green', '06-2 build', 'Name pending versus installed states using text, not color alone. Held green part must never receive an installed-success label.'),
 ('terra-move', ['T4'], 'Whole vehicle then world-relative movement/tracks', '조립→움직여 보기', 'green', '06-2 movement162–166.5', 'Track vehicle through camera motion without hiding wheel/body result. A camera orbit alone is not vehicle translation.'),
 ('terra-return', ['T4'], 'Inventory reopen and raised solid block row', '다시 수정', 'orange', '06-2 returned editing167–175.5', 'At171.5the central block is still a preview. Solid retained raised blocks at175.5 establish the result; hide markers at occlusion.'),
 ('acnh-choice', ['N1', 'N2', 'N3'], 'Selected appearance option and same-avatar hair/face', '고른 모양→캐릭터', 'blue/green', '07-1/07-2', 'Keep the same avatar anchor; reveal changed target in speech order; do not assert a synthetic before/after or combat improvement.'),
 ('acnh-confirm', ['N4'], 'Confirm OK and retained chosen look', '선택 확인', 'green', '07-2 optional ending', 'Only call it confirmation when actual OK/result is shown, not a hover preview. Clear at the final source cut.')
]
annotations = [dict(id=i, sourceWindows=w, namedTarget=target, label=label, semanticColor=color, narrationCue=cue,
                    motionAndProtection=guard, shape='thick hollow contour/rectangle/arrow as target requires; no fill',
                    nativeLineWidthPx=[8, 12], nativeLabelFontPx=[36, 44], numericTrackingKeyframes=None,
                    trackingStatus='root to author from actual final cut; no guessed coordinates',
                    sourceCutReset=True, editorialGuideNotDetector=True, confidenceOrMeasuredValuesInvented=False)
               for i, w, target, label, color, cue, guard in annotation_rows]

boundary_carriers = [
 ('01','02','Jets2 shop/test screen','Keep the shop/test object visible; first full-screen footage elaborates the already-named shop.'),
 ('02','03','Visible difference needs a reason to choose','Retain the benefit-versus-choice question while replacing shot example with named booster comparison; no fresh intro sting.'),
 ('03','04','Distinct options create finding burden','A/B comparison resolves situation dependence, then desired-candidate label leads into an actual category menu.'),
 ('04','05','Narrowed candidate set still lacks a starting combination','Keep candidate identity across sort→automatic starting-set model; explain authored illustration at the switch.'),
 ('05','06','Manually revised starting set needs feel-in-use confirmation','Carry the selected-set result into the test node and then real TerraTech before/action/result.'),
 ('06','07','Liked result is not necessarily performance improvement','Keep result/check language, then introduce the actual avatar appearance choice; Nimbus continues without reset.'),
 ('07','08','What changes and seeing its chosen result','Retain the chosen avatar as one known example when summarizing the choosing process and what/how design.')
]
boundaries = []
ko_scenes = {s['id']: s for s in texts['ko']['scenes']}
en_scenes = {s['id']: s for s in texts['en']['scenes']}
for a, b, carrier, visual_join in boundary_carriers:
    boundaries.append(dict(fromScene=a, toScene=b, closingParagraph=f'{a}-{len(ko_scenes[a]["lines"])}', openingParagraph=f'{b}-1',
                           closingKo=ko_scenes[a]['lines'][-1], openingKo=ko_scenes[b]['lines'][0],
                           closingEn=en_scenes[a]['lines'][-1], openingEn=en_scenes[b]['lines'][0],
                           inheritedObjectOrNeed=carrier, visualAndAudioCarry=visual_join,
                           textualReview='Complete current script-audit confirms concrete handoff; paragraph hashes rechecked by this builder.',
                           realizedAudioVisualJoinReview='pending current audio/cuts/captions'))

scenes = []
for sid, rows in P.items():
    assert len(rows) == len(ko_scenes[sid]['lines'])
    paragraphs = []
    for n, (ev, prerequisite, motion, handoff) in enumerate(rows, 1):
        assert set(ev['sourceWindows']) <= {w['id'] for w in windows}
        assert set(ev['explanationAssets']) <= asset_ids
        ar = paragraph_audit[(sid, n)]
        paragraphs.append(dict(id=f'{sid}-{n}', index=n, claim=ar['meaning'], languageContent='Existing KO/EN/spoken files remain the sole full-text source.',
                               textSha256=ar['paragraphSha256'], prerequisite=prerequisite, visualEvidence=ev,
                               speechLinkedMotion=motion, returnToNextOriginalPoint=handoff,
                               timingCue='current measured paragraph start; exact scene/timeline frames pending',
                               factualScope='Actual observations and authored models remain separately labeled.'))
    refids = {'01':['opening'],'02':['effect'],'03':['tradeoffs'],'04':['selection'],'05':['selection'],'06':['trial'],'07':['appearance'],'08':['conclusion']}[sid]
    scenes.append(dict(id=sid, title=ko_scenes[sid]['title'], referencePointIds=refids, renderer='Motion Canvas',
                       rendererReason='2D menu relationships, readable stat comparison, state labels and progressive paths explain this point. No new3D/spatial implementation is taught, so duplicating it inUnity adds no explanatory value.',
                       illustrationNotMeasuredImplementation=True, independentlyEditableScene=True,
                       implementation={'module':VISUAL.relative_to(ROOT).as_posix(),'kind':layouts[sid]['kind'],
                                       'perSceneWrapper':'root-authored independent makeScene2D wrapper, linked after creation; not claimed to exist by this package'},
                       detailedLayoutAndMotion=layouts[sid], paragraphs=paragraphs,
                       learningSteps={'concreteSituation':rows[0][1], 'termAndPrerequisites':'Defined beside first use in paragraph map and canonical glossary.',
                                      'oneChangeAndVisibleResult':'See exact source windows or explicitly labeled authored model in each paragraph.',
                                      'numericalExample':'03:fictional damage/interval and single opportunity;04:fictional12/8/10sorting. No unnecessary invented calculation in appearance/menu definitions.',
                                      'specialistPrinciple':'Decision-relevant feedback, trade-offs, information grouping, rule-based starting set, short iteration and expression; preserve source-order role.',
                                      'limits':'No universal best build, fabricated game measurements, or forced player workflow.'},
                       nextBoundary=(f'{sid}→{int(sid)+1:02d}' if sid!='08' else 'preserved member ending'),
                       pixelAndCaptionPreflight='pending current rendered native1080p +375px with actual captions'))

ui_primary = {
 'preview': {'url':'https://support.microsoft.com/en-us/office/foundations-experiences/office-options-the-general-tab', 'read':'Official Live Preview definition: see a formatting result before applying; general UI terminology support only, not evidence of a game mechanic.'},
 'icon': {'url':'https://learn.microsoft.com/en-us/windows/apps/develop/ui/controls/icons', 'read':'Official icon definition as visual shorthand, small-size meaning/readability and icon+text examples; no imported Microsoft icons.'},
 'sorting': {'url':'https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/sort', 'read':'Primary API documentation describes ordering and comparison; authored numeric-order diagram is independently specified, not a claim that the games run this implementation.'},
 'acvi': {'url':'https://en.bandainamcoent.eu/armored-core/news/armored-core-6-fires-of-rubicon-starter-guide', 'read':'Official assembly/control context; exact Boost Speed/QB EN Consumption spelling and values come from directly inspected native menu156s in linked ACVI source audit. The guide landing page is not claimed to contain every glossary sentence.'}
}
glossary_rows = [
 ('customization','커스터마이징','Customization',None,'Changing equipment/parts/appearance; different games expose different changeable properties.','01-1 concrete introduction; spoken name06-2','커스터마이징','reference-audit#opening',None),
 ('preview','프리뷰 / 미리보기','Preview',None,'See what a choice will look or act like before committing; distinguish preview from equipped/applied state.','02-4','프리뷰','preview','Do not label a hover preview already equipped.'),
 ('booster','부스터','Booster',None,'ACVI movement component, not a gun or measured speed value.','03-1','부스터','acvi','Source BST-G2/P04, not an invented current patch.'),
 ('quick-boost','퀵부스트','Quick Boost','QB','Brief evasive move; its displayed energy cost differs from Boost Speed.','03-2','퀵부스트','acvi','Keep Quick Boost distinct from ordinaryBoost or Assault Boost.'),
 ('tradeoff','트레이드오프','Trade-off',None,'A linked gain and sacrifice; circumstances/objective determine which benefit matters.','03-2','트레이드오프','reference-audit#tradeoffs','ACVI menu comparison supplies actual example; not a universal optimization proof.'),
 ('dps','초당 평균 피해','Damage per second','DPS','Sustained average damage rate in the explicit hypothetical model: one-shot damage÷shot interval.','03-3','초당 평균 피해','authored arithmetic03-3/03-4','A100/2=50;B40/0.5=80. Single-opportunity health90 reverses preference. Ignore misses/armor only as declared; finite-window first shot can change average.'),
 ('icon','아이콘','Icon',None,'Small identifying picture; similar-looking symbols need readable name/function clues.','04-1/04-2','아이콘','icon','Authored sword/boots diagrams are explanatory, not native game item icons.'),
 ('sorting','정렬','Sorting',None,'Reorder the same candidate set according to a criterion; category/filtering narrows a set instead.','04-4','정렬','sorting','Only our12/8/10list is sorted; actual sorting execution not asserted forBOTW/MH.'),
 ('automatic-equipment','자동 장비','Automatic equipment / Auto-equip',None,'Choose and equip by a defined objective/rule, then permit manual revision.','05-1','자동 장비','reference-audit#selection','Authored attack-focused model; no universal strongest result or specific commercial-game automatic operation claimed.')
]
terminology=[]
for key,ko,en,abbr,meaning,first,spoken,primary,limits in glossary_rows:
    basis=ui_primary.get(primary, {'internalEvidence':primary,'scope':'Linked fully reviewed primary lesson or independently authored mathematical model; not an invented official game feature.'})
    terminology.append(dict(id=key, canonicalKo=ko,canonicalEn=en,abbreviation=abbr,plainMeaning=meaning,firstAppearance=first,
                            displayRule='Canonical KO/EN on first explanation; reuse consistent labels/captions; do not introduce unexplained abbreviations.',
                            ttsPronunciation=spoken,primaryEvidence=basis,limits=limits))

thumbnail = ROOT / 'projects/player-customization/publishing/thumbnail-v1.png'
for a in assets:
    assert digest(ROOT/a['image'])==a['sha256']
    assert digest(ROOT/'output/player-customization/preproduction-assets'/Path(a['image']).name)==a['sha256']

package = {
 'schemaVersion':1,'slug':'player-customization','revision':'reference-preserving-v2',
 'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'status':'complete-eight-scene-design; current timed-native/mobile-captioned preflight pending',
 'authority':'One design package linked from the root existing production-plan/review-ledger; no new approval loop.',
 'authorization':link(HOME/'authorization.json'),
 'preservation':{'globalSelectedVideoObserved':control['selectedVideo'],'globalControlChanged':False,'foreignJobsTouched':False,'baselineUpload':'lf765yYhPdM','baselineReplacementAuthorized':False,'youtubeUploadAuthorized':False,'automaticNextVideo':False},
 'inputs':[link(SCRIPT/f'narration.{lang}.json') for lang in ('ko','en','spoken-ko')]+[
     link(HOME/'source-selection.json'),link(HOME/'script-audit.json'),link(HOME/'reference-audit.json'),
     link(HOME/'duplicate-review.json'),link(LOCAL/'assets/provenance.json'),link(VISUAL),
     link(ROOT/'motion-canvas/src/styles/research-dark.ts')],
 'scriptLock':{'scenes':8,'paragraphs':35,'languageParagraphHashesVerified':105,
               'fullCurrentKoEnReadByDesigner':True,'spokenAliasesBoundByCompletedAuditAndHash':True,
               'wholeNarrationContinuousTextReview':{'evidence':'projects/player-customization/production/reference-preserving-v2/script-audit.json','all35FullPairedParagraphsRead':True,'all7ConcreteTextualJoinsReviewed':True,'realizedSpeechAndJoins':'pending actual current audio'},
               'statusOnlyLockChange':'write-script.py changed draft→locked metadata after the complete text audit. This builder matches all105 current paragraph hashes to that audit; old whole-file hashes are not falsely reused as current file hashes.',
               'viewerNarrationIndependent':True,'sourceCreatorFramingRemoved':True,'sourceBiographyNotReassigned':True},
 'referenceMapping':{'audit':'projects/player-customization/production/reference-preserving-v2/reference-audit.json','researchReferenceOnly':True,'referenceMediaInCutBank':False,
    'centralQuestion':reference['centralQuestion'],'pointOrder':['opening','effect','tradeoffs','selection','trial','appearance','conclusion'],
    'map':[{'referencePointId':b['id'],'researchReferenceSeconds':b['approxReferenceSeconds'],'retainedClaim':b['claim'],
            'currentScenes':{'opening':['01'],'effect':['02'],'tradeoffs':['03'],'selection':['04','05'],'trial':['06'],'appearance':['07'],'conclusion':['08']}[b['id']],
            'nearbyAddedExplanation':{'opening':'Familiar experience and three-part overview, no new chapter.','effect':'Preview definition and two-ship origin distinction.','tradeoffs':'Actual booster benefit/cost plus clearly fictional damage/interval and single-opportunity calculation.','selection':'Categories/readable icons, explicit fictional sorting, rule-based automatic equipment and manual edit.','trial':'Verified TerraTech attachment→drive→re-edit plus earlier Jets2 adjacent trial.','appearance':'Actual ACNH initial hair/face preview and confirmation; no power increase inferred.','conclusion':'What can change and how choosing/checking/revision work, retaining other kinds of fun.'}[b['id']],
            'return':'Proceed to the next original point after the adjacent clarification; no inserted unrelated lesson.'} for b in reference['backbone']],
    'exampleRoleDifferences':'General roles preserved with actual independent evidence: ACVI captured booster rather than unverified gun-balance comparison; BOTW clothing category rather than unobserved heat symbol; Iceborne forging preview plus authored sorting; authored auto-equip instead of falsely claimingMusashi footage; ACNH initial face/hair rather than unobserved room operation. These are explicitly bounded role-equivalent illustrations, not claims that all original source titles must appear.'},
 'renderer':{'primary':'Motion Canvas','implementation':VISUAL.relative_to(ROOT).as_posix(),'newUnitySceneNeeded':False,
              'why':'All eight points compare menus, images, quantities, choices and2D relationships. No3D spatial principle or new self-authored game mechanics need a duplicateUnity simulation. Actual commercial gameplay remains independent footage.',
              'perSceneKinds':[layouts[s]['kind'] for s in P],'imagesRemainExplanation':True,'fictionalEquipmentAndGuns':'Recognizable independently drawn sword/shield/boots/guns in the source module, not captured commercial assets or generic cubes.'},
 'layoutContract':{'output':[1920,1080],'fps':60,'style':'research-black-v1 / yamyam-video-ui-v1','tokens':'motion-canvas/src/styles/research-dark.ts',
   'font':'Segoe UI, Malgun Gothic, sans-serif','background':'black','title':'warm yellow','body':'white','semanticColorRoles':{'blue/teal':'choice/input/benefit','green':'visible result/retained state','orange/red':'cost/manual revision/caution','muted':'inactive/limits; never sole status signal'},
   'commonHeader':{'brandMc':[-615,-482],'brandFontPx':29,'titleMc':[0,-393],'titleFontPx':55,'creditMc':[545,-482],'creditWidthPx':700,'creditFontPx':23},
   'caption':{'policy':'boxed-white-forest-v1','nativeAnchor':[960,970],'motionCanvasAnchor':[0,430],'fontSizePx':48,'maxLines':2,'anchorMovesAllowed':False,'actualCurrentCaptionRequiredForPreflight':True},
   'safeContent':{'maxMcY':340,'nativeBottom':880,'sourceImageFit':'contain original16:9, no stretch; no assumed target crop','imageCaptionFontPx':33,'bottomNoteMcY':311,'regularMeaningfulLabelPx':[36,49],'keyNumberPx':[57,60]},
   'oneFocusAtATime':True,'noDecorativeGradientGlowEmoji':True,'imageProvenance':link(LOCAL/'assets/provenance.json'),
   'assetCount':8,'verifiedOutputAssetCopiesMatch':True,'screenshots':[{'id':a['id'],'image':a['image'],'imageSha256':a['sha256'],'sourceLocalSeconds':a['extraction']['localSeconds'],'sourceKey':next(s['key'] for s in sources.values() if s['media']['path']==a['sourceFile']),'aspectRatio':'16:9','crop':'none','provenanceOwner':'existing assets/provenance.json; source and rights not duplicated'} for a in assets],
   'motionTiming':'timing.cues are current measured paragraph starts, zero-indexed. Code evenly spaced fallback is authoring-only and must not certify production. Trace/reveal defaults0.55/0.8s, staggered source→connection→destination; map to actual speech and shorten/split only if needed for comprehension.',
   'preflightStatus':'pending actual final captions, native1080p,375px and moving transitions; source code dimensions are not pixel approval.',
   'mobileRisksToResolve':'Small23–33px credit/notes and long labels can be unreadable at375px. Inspect actual pixels; use necessary magnification, split labels or reflow while preserving fixed captions and real source context. No automatic pass from nominal font size.'},
 'sourcesAndRights':{'selection':link(HOME/'source-selection.json'),'linkedPixelAudits':selection['inputAudits'],
                     'allNativeMinimum1080':all(s['nativeSource']['minimum1080Passed'] for s in sources.values()),
                     'sourceFpsVsMaster':'Five sources60fps; BOTW genuine1080p30 is placed into60fps master with normal-speed frame duplication, not invented60fps game motion.',
                     'rightsAndAudio':'Use each current selected-source assessment and required recorder/publisher credits. Publisher sharing guidance does not replace recorder rights; limited educational quotations are not labeledCC/granted. Preserve original locally; no unreviewed narration/music in final mix.',
                     'finalRightsAndListeningPendingAsRecorded':True},
 'sourceCutBank':windows,
 'sourceCapacity':{'selectedBankUpperBoundSeconds':round(sum(w['upperBoundSeconds'] for w in windows),6),
                   'thisIsNotFinalUsableDuration':True,'actualFinalFrames':None,'explanationFinalFrames':None,'ratioPassed':False,
                   'targetBodyActualFraction':0.6,'targetBodyExplanationFraction':0.4,'excludeBrandFrames':120,'excludeMemberFrames':600,'maxRoundingErrorFrames':1,
                   'timingAfter':'One current full narration ASR and source-safe paragraph alignment, then root exact edit-plan. No fabricated current runtime.',
                   'capacityRule':'Trim out idle menus, irrelevant selection, duplicated seconds and source cuts without a useful stated observation. A source-bank maximum does not guarantee enough meaningful footage. Keep required explanation; resolve any shortage with relevant unique evidence rather than loops, slowdowns, repeated clips or silent padding.'},
 'gameExampleCoverage':{'policy':'concept-matched-genre-variety-v1','selectedDistinctMeaningfulGames':6,'nintendoMeaningfulGames':2,'fraction':2/6,
                        'counting':'Each meaningful game once, not source cuts, stills, game mentions or recorder names. No fixed total game quota.',
                        'nintendoSources':['botw-menu','acnh-appearance'],'nintendoOwnershipEvidence':'nintendo-footage-review.json primaryNintendo game/support pages; device release alone is insufficient.',
                        'genres':[{'key':s['key'],'genre':s['genre']} for s in sources.values()],
                        'previousD20':'familiar-game-rules current edit: FPS-family11216/17126actual frames=65.491%; detailed audit in footage-candidates.json#recentActualUseReview.d20.',
                        'contrast':'Side-on shooter, mech equipment menus, exploration clothing, armor-forging grid, visible vehicle construction and social appearance creation use different player actions and information, instead of another FPS-heavy title montage.',
                        'finalGenreTimeAudit':'pending exact final cut frames; count diversity alone is not proof of screen-time balance','actual60Explanation40IsSeparate':True},
 'canonicalTerminology':terminology,
 'annotations':annotations,
 'annotationContract':{'namedTargetBeforeShape':True,'nativeClearance':'Protect source item names/stats, avatar/part change, credit, native game UI and fixed current captions. Border only, no colored fills covering evidence.',
                       'motionTracking':'Root verifies numeric target anchors from actual selected local frames, interpolation through real camera/subject movement, hides at occlusion/out-of-frame, resets on every source cut. No guessed detector boxes or confidence scores.',
                       'calibrationAndPixelPreflight':'pending exact final edit; these semantic target plans are not numeric tracking completion'},
 'scenes':scenes,'chapterBoundaryLinks':boundaries,
 'audioContract':{'voice':'ElevenLabs own clone, user-approved sampleB; follow current authorization and root generator settings','narrationTargetLufs':-16,
                  'music':'Nimbus — Eveningland, approved game-design contract','musicInitialTargetLufs':-31,
                  'lectureNoBgmNotAppliedToGameDesign':True,'foreignGpuOrResearchProcessChanges':False,
                  'quality':'Continuous greeting; pronunciation aliases from existing spokenKO, speech-safe joins, whole narration/full-mix ASR once each, local speech-active level continuity and actual contextual listening remain root execution checks.',
                  'sourceGameAudio':'Unreviewed source soundtrack/narration excluded; only separately reviewed cleared useful game audio may be used under root current audio plan.'},
 'publishingDesign':{'titlePolicy':'viewer-question-first-titles-v1','candidates':[
     {'title':'장비창에서 나오기 아쉬운 게임은 무엇이 다를까?','support':['01-1','02-4','06-4','07-3','08-4'],'promise':'The choosing process itself can be enjoyable.'},
     {'title':'게임 시작도 안 했는데, 장비 고르는 게 왜 재밌을까?','support':['01-1','01-2','03-5','07-3'],'promise':'Preview, meaningful differences, easy navigation/trial and expression explain the familiar experience.'},
     {'title':'장비 고르기가 귀찮은 게임과 재밌는 게임의 차이','support':['02-2','03-5','04-1','05-1','06-3'],'promise':'Concrete interface decisions reduce comparison and iteration burden; no unsupported ranking of whole games.'}],
     'thumbnail':{'reuseExisting':True,**link(thumbnail),'headline':'장비를 고르는게 왜 재밌을까?','parentActuallyViewed':True,
                   'design':'Existing yellowbrand header, white ground, natural concept illustration, black/red Korean headline, integratedcat and얌얌코딩. Reuse without a duplicate image-generation job; platform/captioned-final consistency review pending.'},
     'uploadBoundary':'Completed current Drive final-review copy→human review→same approved1080p60captioned master YouTube private only after authorization; existing baseline preserved.'},
 'preflightAndFinalReview':{'designContentMapped':True,'currentScriptAuditParagraphHashesMatch':True,'actualAssetsExistAndOutputCopiesMatch':True,
                           'canonicalDisplayFollowThrough':{'status':'pending root implementation/pixel check','required':'03 first relevant appearance must visibly connect 퀵부스트 / Quick Boost / QB and 초당 평균 피해 / Damage per second / DPS. Current visual code has QB EN Consumption and the Korean damage formula, but the full bilingual labels are not claimed already rendered. Preserve the already audited narration meaning.'},
                           'nativeAnd375ActualCaptionedMovingSample':'pending root current timing/captions/render; no sample approval inferred',
                           'allEightSceneLayoutsReviewedInPixels':False,'allFinalCutsAndCaptionCuesReviewed':False,'fullFinalDecodePtsAudioIntegrity':'pending new encoded output',
                           'wholeCurrentNarrationAsr':'pending','wholeCurrentFinalMixAsr':'pending','humanFinalListening':'pending','localLevelContinuity':'pending',
                           'requiredEvidenceReuse':'Only identical relevant hashes/timing/settings or verified decoded-equivalent ranges. New output still needs full integrity checks.',
                           'noTtsRenderOrGpuJobLaunchedByBuilder':True},
 'ownedFiles':['projects/player-customization/production/reference-preserving-v2/build-design.py','projects/player-customization/production/reference-preserving-v2/design-plan.json']
}
assert len(scenes)==8 and sum(len(s['paragraphs']) for s in scenes)==35 and len(boundaries)==7
assert round(package['sourceCapacity']['selectedBankUpperBoundSeconds'],1)==355.9
out=HOME/'design-plan.json'
out.write_text(json.dumps(package,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'path':out.relative_to(ROOT).as_posix(),'scenes':8,'paragraphs':35,'paragraphHashesVerified':105,'assets':len(assets),'sourceWindows':len(windows),'boundaryLinks':7,'status':package['status']},ensure_ascii=False))
