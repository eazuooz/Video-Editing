"""Seal only the completed direct sample review; keep source adoption pending."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, os

ROOT = Path(__file__).resolve().parents[4]
PROOF = Path(__file__).resolve().parent
TARGET = PROOF / 'native-trial-direct-review-v3.json'
stamp = lambda: datetime.now(timezone.utc).isoformat()
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
def write(p, value):
    tmp = p.with_name(p.name + '.' + str(os.getpid()) + '.tmp')
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    os.replace(tmp, p)

assert not TARGET.exists(), 'Preserve completed review; do not repeat.'
state_path = PROOF / 'native-framing-execution-v3.json'
s = json.loads(state_path.read_text(encoding='utf-8-sig'))
assert s['status'] == 'prepared-awaiting-direct-review'
assert s['pid'] == 65420 and s['processCreateTime'] == 1791579657.6722112
assert s['totalTrialSamples'] == 897 and s['totalTrialBoards'] == 152
sessions = {'sessionId': 29022, 'pid': 65420,
    'processCreateTime': 1791579657.6722112, 'outerExitCode': 0,
    'exitObservation': 'Actual write_stdin session29022 returned exit_code0 and prepared-awaiting-direct-review samples897 boards152 adoptionfalse before context compaction.',
    'exitRecordedAt': stamp(), 'closedSessionRepolled': False}
session_path = PROOF / 'native-framing-execution-v3.json.session.json'
assert not session_path.exists()
write(session_path, sessions)
notes = {
 'zetterburn-gameplay1': 'Boards001–008 all read: close hits, fire projectile and opponent burn. The water column belongs to opposing Orcane. After native f280/8.4s Zetterburn is alone; proposed end280 is pending exact boundary review.',
 'zetterburn-gameplay2': 'Boards001–004 all read: close attack/grab, circular fire and airborne burning opponent; last3.99–4.08s is alone. Proposed shorter end129/3.87s is pending boundary review.',
 'orcane-gameplay1': 'Boards001–005 all read: puddle emergence, air attack, droplets and bubbles, ending roll/emergence. Source itself partly clips an opponent at its top edge; framing must not be described as repairing unseen source pixels.',
 'orcane-gameplay2': 'Boards001–007 all read: water/bubbles, break effect, pursuit and ending swirl. After6.39s alone. No looping to expand the available interval.',
 'forsburn-gameplay1': 'Boards001–007 all read: multiple figures and smoke obscure silhouettes, followed by wall/air interactions. Smoke is a visible rule effect, not automatically unrelated idle.',
 'forsburn-gameplay2': 'Boards001–005 all read: smoke clears, crouch and airborne fight/burst. Last4.89–4.98s is alone; proposed end153/4.59s is pending boundary review.',
 'gBbKFYZYvbc': 'Boards001–078 all read, including051–078 in this continuation. Ground/air attacks, sliding, gray block/ice armor, orb movement and offstage recovery. Window06:203.5–216s trades and air pursuit; armor breaks at209.5s. Window07:246–268s close attacks and offstage recovery253.5–258.5s. Window08:310–340s exchanges, armor at319.5s and shatter325–326.5s, offstage recovery330–333s. Displayed damage percentages sometimes reset around armor; no inferred damage formula, edit/VFR diagnosis, win or optimal strategy. Source is a historical2017 official tournament, not current balance. All original HUD remains in v3 but the1600x900 image is an inset; final fullscreen approval is false.',
 'a8nwpiCqyTQ': 'Boards001–038 all read: transition/name reveal and tooltips precede selected actions; aftermath/next draft/defeat result and wipes are excluded. Proposed native half-open windows Slade1710–1783, Hamir1902–2077, Artemis2139–2380, FleetSNIPE2424–2577, FleetSTRIKE4533–4612. These are sampled proposals, not adopted exact boundaries. Hamir initial state5ATK/3DEF/4ACC/4SPD/7STA; earlier coarseACC2 is corrected to4 from the native UI. REACT−1HP/DEF3→6/STA7→6 thenBLOCKED+1STA; Artemis STUN enemyATK8→3 and discard-die text, no regeneration shown. Slade coins106→111 and enemy−2HP; not high-speed dodge evidence. FleetSNIPE−1HP and two+3STA dice; STRIKE is a different shot. v3 entireHUD fits but game is an inset, so final fullscreen approval remains false.'
}
sources = []
for src in s['sources']:
    for t in src['samples']:
        assert sha(ROOT / t['path']) == t['sha256']
        assert sha(ROOT / t['trialPath']) == t['trialSha256']
        step = 3000 if src['sourceKey'] == 'gBbKFYZYvbc' else 256 if src['sourceKey'] == 'a8nwpiCqyTQ' else 384
        assert t['pts'] == t['nativeFrame'] * step
    bs = []
    for b in src['trialBoards']:
        assert sha(ROOT / b['path']) == b['sha256']
        bs.append({**b, 'directlyRead': True})
    sources.append({'sourceKey': src['sourceKey'], 'samples': src['samples'],
        'trialBoards': bs, 'directObservations': notes[src['sourceKey']]})
review = {'schemaVersion': 1, 'slug': 'character-parameters', 'recordedAt': stamp(),
 'executionState': str(state_path.relative_to(ROOT)).replace('\\','/'), 'executionSha256': sha(state_path),
 'actualSession': sessions, 'totalSamplePixelsDirectlyRead': 897, 'totalTrialBoardsDirectlyRead': 152,
 'nativeOriginalBoardsAllRead': False, 'allNativeFramesReviewed': False,
 'sampleContentDirectReviewComplete': True, 'sources': sources,
 'nativeExactSelectionApproved': False, 'sourceAdoptionApproved': False,
 'finalFullscreenCompositionApproved': False, 'finalCueUiApproved': False,
 'wholeContinuousViewingOrListeningApproved': False, 'humanListeningApproved': False,
 'publicRightsApproved': False, 'newNativeExtractionCount': 0, 'sourceAudioUse': False,
 'loopOrSlowdownUse': False, 'rasterGitAdditions': 0, 'externalResearchChanges': 0,
 'nextAction': 'Prepare small full-width gameplay trials preserving exact native HUD in clear regions; inspect problem frames before extending trials. Then native boundaries and normal-speed playback, current duplicate check and source bank before narration.'}
write(TARGET, review)
qp = ROOT / 'production/batches/sakurai-planning-game-design/queue.json'
before = qp.read_bytes(); q = json.loads(before)
item = next(i for i in q['items'] if i['slug'] == 'character-parameters')
assert not item.get('videoId') and not any(item['checkpoints'].values())
item.update(stage='native-samples-reviewed-fullscreen-framing-pending', updatedAt=stamp())
item['execution'].update(status='completed', sessionId=29022, outerExitCode=0)
item['nativeTrialReview'] = {'evidence': str(TARGET.relative_to(ROOT)).replace('\\','/'),
    'samples':897, 'boards':152, 'sampleContentReviewComplete':True,
    'exactSelectionApproved':False, 'fullscreenApproved':False, 'finalCueUiApproved':False}
item['nextAction'] = review['nextAction']; q['updatedAt'] = q['lastProgressAt'] = stamp()
assert qp.read_bytes() == before
write(qp, q)
print(json.dumps({'sealedSamples':897, 'sealedTrialBoards':152, 'adoption':False}))
