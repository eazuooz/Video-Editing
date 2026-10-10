"""Seal actual direct contact-sheet observations; no native action adoption."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os

ROOT = Path(__file__).resolve().parents[4]
PROOF = Path(__file__).resolve().parent
STATE = PROOF / 'official-source-review-execution-v1.json'
TARGET = PROOF / 'official-coarse-direct-review-v1.json'
stamp = lambda: datetime.now(timezone.utc).isoformat()
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
if TARGET.exists():
    raise SystemExit('Preserve completed direct review; do not repeat.')
state = json.loads(STATE.read_text(encoding='utf-8-sig'))
assert state['status'] == 'coarse-extracted-awaiting-direct-review'
assert state['totalSamples'] == 286 and state['totalBoards'] == 50
short = {
 'zetterburn-gameplay1': 'Jumping/attacking versus Orcane; opponent has burning effect in later samples around 6.51–8.5s. Last samples show offscreen opponent/recovery. Not a numeric fire amplification measurement.',
 'zetterburn-gameplay2': 'Forest-stage attacks versus green opponent; opponent burning visible around 1.5–2s and subsequent attacks around 3–3.5s. Coarse samples do not establish a placed wildfire sequence.',
 'orcane-gameplay1': 'Water/puddle-like location at left platform, blue character versus Zetterburn below, bubbles around 3.5s and blue character in water around 4s; final orange fire above arena. Exact teleport input/order remains unverified.',
 'orcane-gameplay2': 'Orcane versus Kragg, bubbles around 1–1.5s, rocky platform breakup around 2.5s, attacks and movement through 6s, opponent offscreen near end. Exact puddle teleport remains unverified.',
 'forsburn-gameplay1': 'Two Forsburn figures visible at native sample near 1.02s; smoke builds and obscures figures around 4–7.65s against Orcane. Candidate decoy/smoke example; no invulnerability or clone AI claim.',
 'forsburn-gameplay2': 'Forsburn versus Wrastor; initial right-side smoke, smoky confrontation around 1.5s, cloud gone around 2.01s, later orange charged figure around 4.5s. Exact three-cloud charge/consume sequence requires native context.',
}
match = [
 '0–10s: commentators at 0/2/4/6; transition/countdown at 8; first Etalus/Ori exchange at 10. Exclude commentary and countdown.',
 '12–22s: ground and aerial exchanges, Ori/Sein projectile changing position; offstage chase around 20. Fast action, no measured universal mobility ranking.',
 '24–34s: close exchange then Etalus knocked upward/right; dark armor-like sprite state at 32. Need native context before attributing exact armor activation.',
 '36–46s: Ori pressures ground and ledge, Etalus airborne/returns; rising damage percentages. Percent display is not a base-character stat.',
 '48–58s: dark/light Etalus states, aerial pressure and impacts; no isolated damage-strength comparison established.',
 '60–70s: stock/respawn transition at 62, then further offstage/ground exchange. Exclude respawn-only samples from quota.',
 '72–82s: Etalus exits dark state around 72; attacks continue, new stock around 78/80. Exclude respawn-only intervals.',
 '84–94s: ledge return, Ori/Sein effect at 88, near-ground exchange; attack sequence candidate.',
 '96–106s: alternating grounded/aerial attacks; projectile and pointed falling objects at 98. Need exact continuous native sequence.',
 '108–118s: left offstage exchange, red knockout at 110, respawn at 112, resumed attacks by 114. Exclude stock transition.',
 '120–130s: close ground attack, right air chase then Etalus launched; native player action candidate.',
 '132–142s: Ori/Sein combined visible positions and Etalus armor-like state at 138; no claim of permanent armor.',
 '144–154s: continuing exchanges at 144–148; GAME at 150, winner illustration at 152, commentary at 154. Exclude result/art/commentary.',
 '156–166s: commentator portraits only; excluded.',
 '168–178s: commentator portraits only; excluded.',
 '180–190s: dissolve at 180, GO at 182, different flat arena starts at 184; attacks at 184–190. Exclude transition/countdown.',
 '192–202s: Ori hit upward while Etalus ground/air attacks; armor-like sprite at 200. Not evidence that one character is globally stronger.',
 '204–214s: close/aerial impacts followed by Etalus launched above platform; Ori/Sein separated screen positions visible.',
 '216–226s: edge exchange, Etalus offstage/recovery; projectiles move independently from Ori. Native exact cuts required.',
 '228–238s: falling/offstage Etalus at 228/230, respawn 232; new exchange by 234, dark state at 236. Exclude respawn.',
 '240–250s: stock transition for Ori at 240/242; action resumes 244–250. Exclude respawn-only segment.',
 '252–262s: close hit then opposite ledge recovery/air-to-ground chase; no inferred input commands.',
 '264–274s: ground exchanges, Ori launched/recovering and armor-like Etalus state at 270/272.',
 '276–286s: edge skirmish and dark/light Etalus sprite; Ori drops below edge at 286. No auto-recovery guarantee.',
 '288–298s: Ori respawn at 288; subsequent aerial/ground attacks from 290; opponent briefly offscreen at 298. Exclude respawn.',
 '300–310s: Etalus respawn at 300 then exchanges from 302 onward; source game remains normal speed.',
 '312–322s: Etalus close hit and upward launch, Ori aerial approach, changing spacing; candidate role/counterplay example.',
 '324–334s: near-ground effects, falling pointed objects at 332 and large circular effect at 334. Exact causal mechanic remains native-review pending.',
 '336–346s: Etalus repeatedly in air/knocked away, Ori/Sein trajectories. Not proof of permanent character imbalance.',
 '348–358s: edge chase, offscreen marker at 350/352; game-and-set at 356, black at 358. Exclude result/black.',
 '360–370s: replay winner illustration transition then commentator portraits; excluded.',
 '372–382s: commentator portraits only; excluded.',
 '384–394s: commentator portraits only; excluded.',
 '396–401.966667s: commentator portraits only, last native frame12059; excluded.',
]
checked = []
for src in state['sources']:
    assert sha(ROOT / src['localPath']) == src['sha256']
    for sample in src['samples']:
        assert sha(ROOT / sample['path']) == sample['sha256']
    boards = []
    for i, board in enumerate(src['boards']):
        assert sha(ROOT / board['path']) == board['sha256']
        note = match[i] if src['kind'] == 'official-tournament-recording' else short[Path(src['localPath']).stem]
        boards.append({**board, 'directlyRead': True, 'observations': note})
    checked.append({'sourcePath':src['localPath'], 'sha256':src['sha256'],
                    'nativeVideo':src['video'], 'samplesDirectlyRead':len(src['samples']),
                    'wholeDecodeExitCode':src['wholeDecodeExitCode'], 'boards':boards})
record = {'schemaVersion':1, 'slug':'character-parameters', 'recordedAt':stamp(),
          'executionState':str(STATE.relative_to(ROOT)).replace('\\','/'),
          'executionSha256':sha(STATE), 'actualOuterSessionId':37099, 'actualOuterExitCode':0,
          'sources':checked, 'totalSamplesDirectlyRead':286, 'totalBoardsDirectlyRead':50,
          'coarseSamplePixelReviewApproved':True, 'allNativeFramesReviewed':False,
          'wholeContinuousViewingOrListeningApproved':False, 'exactInOutApproved':False,
          'sourceAdoptionApproved':False, 'finalCueUiApproved':False,
          'newNarrationTtsOrRender':False, 'humanListeningApproved':False, 'publicRightsApproved':False,
          'sourceAudioUse':False, 'loopOrSlowdownUse':False, 'rasterGitAdditions':0,
          'limitations':['Coarse native PTS samples show candidates, not every action transition.',
                         'Six official web clips are400x200 native pixel art; full-frame upscale/readability still requires direct review.',
                         'Tournament commentary, countdown, respawn-only, winner cards, transitions and black frames are excluded from actual-game quota.',
                         'Recorded 2017 match is historical footage, not current-patch balance or optimal strategy evidence.'],
          'nextAction':'Review exact native action windows and caption-safe full-screen framing; secure second concept-matched official game before dependent script.'}
TARGET.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'sealed':str(TARGET),'sources':7,'samples':286,'boards':50,'adopted':False},ensure_ascii=False))
