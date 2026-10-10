"""Seal direct sparse source/framing review; do not adopt or regenerate media."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json
import psutil

ROOT = Path(__file__).resolve().parents[4]
PROOF = Path(__file__).resolve().parent
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
state_path = PROOF/'additional-role-action-execution-v2.json'
state = read(state_path)
assert state['actualExtractExitCode'] == 0
assert len(state['samples']) == 38 and len(state['boards']) == 14
for pid, created in [(state['pid'], state['createTime']), (state['child']['pid'], state['child']['createTime'])]:
    try:
        assert abs(psutil.Process(pid).create_time()-created) > .01, 'Recorded extraction still alive'
    except psutil.NoSuchProcess:
        pass
assert sha(ROOT/state['priorBankPath']) == state['priorBankSha256']
for row in read(ROOT/state['protectedRequest'])['protectedInputs']:
    assert sha(ROOT/row['path']) == row['sha256'], row['path']
for row in state['samples']:
    assert row['pts'] == row['nativeFrame']*3000
    assert sha(ROOT/row['path']) == row['sha256']
    assert sha(ROOT/row['trialPath']) == row['trialSha256']
for row in state['boards']:
    assert sha(ROOT/row['path']) == row['sha256']
review = dict(
    schemaVersion=1, reviewedAt=datetime.now(timezone.utc).isoformat(),
    execution=state_path.relative_to(ROOT).as_posix(),
    executionSha256=sha(state_path), actualOuterSession=72730,
    actualOuterExitCode=0, actualExitObserved=True, recordedWorkersClosed=True,
    candidate=state['candidate'], sourceSha256=state['sourceSha256'],
    samples=state['samples'], individuallyReadBoards=state['boards'],
    all38NativeAnd38FramedSamplesDirectlyRead=True,
    sparseBoundaryAndFramingApproved=True,
    observations=[
        'Start native8040 at268s is an active exchange: Etalus60%, Ori77%, timer6:34; adjacent8037–8043 remain active without a title, result or respawn.',
        '8130–8205 shows close ground/air exchanges and projectiles. Etalus displayed damage rises66→73→78→85→91 while Ori remains77 at these samples. Damage percentages are current match state, not base attack ratings.',
        '8220–8295 shows a charged/color-changing pose, airborne projectiles and contact; Ori displayed damage77→86. No multiplier, exact ability property, optimal strategy or guaranteed outcome is inferred.',
        '8310–8385 shows jumps, landing/platform movement and another exchange. Etalus displayed damage91→98; no idle/menu/black/result appears in the reviewed samples.',
        '8396–8403 remains an airborne close exchange at timer6:22, Etalus101→105 and Ori86. End8400 is a half-open editorial cut within ongoing action, not a completed combo or victory.',
        'All framed trial samples retain full upper gameplay and readable bottom-corner player values. The centered test cue and lower commentator strip have separate space; this is a test cue, not every final narration cue.'
    ],
    noOverlapWithPrior19Windows=True, normalSpeedRequired=True,
    sourceAudioAdopted=False, sourceAdoptionApproved=False,
    currentBankAndMainScriptsUnchanged=True,
    allNativeFramesReviewed=False, wholeContinuousPlaybackApproved=False,
    allFinalCueUiApproved=False, finalPixelsApproved=False,
    humanListening='pending', finalPublicRights='pending',
    rasterGitAdditions=0, mediaGitAdditions=0, processOrResearchControlChanges=0)
out = PROOF/'additional-role-action-direct-review-v2.json'
assert not out.exists(), 'Read the existing review; never repeat the seal'
out.write_text(json.dumps(review, ensure_ascii=False, indent=2)+'\n', 'utf-8')
print(json.dumps(dict(review=out.relative_to(ROOT).as_posix(), native=38, framed=38,
                     boards=14, originalInputsPreserved=True, adopted=False)))
