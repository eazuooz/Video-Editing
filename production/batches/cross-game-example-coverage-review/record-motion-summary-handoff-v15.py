"""Seal completed voice/summary work and observe research without changing controls."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, psutil

ROOT = Path(__file__).resolve().parents[3]
R = ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
B = ROOT/'production/batches/cross-game-example-coverage-review'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
out = R/'resource-and-annotation-handoff-v15.json'
assert not out.exists(), 'Preserve completed evidence.'
verification = read(R/'first-paragraph-repair-handoff-verification-v1.json')
history_path = ROOT/verification['historyPath']
history = read(history_path)
assert sha(history_path) == verification['historySha256']
assert history['state'] == 'research_resume_verified'
identity = history['resumedQueue']

def live(ident):
    try:
        p = psutil.Process(ident['pid'])
        return (abs(p.create_time()-ident['createTime']) < .01 and
                p.cmdline() == ident['command'] and p.cwd() == ident['cwd'] and p.is_running())
    except psutil.NoSuchProcess:
        return False

status_path = Path(history['queueDir'])/'status.json'
status = read(status_path)
assert not live(identity), 'Inspect current live identity before changing this completion observation.'
assert status['status'] == 'complete_pending_visual_review'
assert status['completed'] == status['total'] == 1088
assert not (ROOT/'shared/output/GPU_HANDOFF.json').exists()
code_path = Path(identity['cwd'])/'lora_experiment/analysis/placement_focus/gpu_queue.py'
code_lines = code_path.read_text('utf-8').splitlines()
assert any("status='complete_pending_visual_review'" in s for s in code_lines)
execution = read(R/'narration-first-paragraph-repair-execution-v1.json')
protected = execution['protectedInputs']
assert len(protected) == 71
for row in protected:
    assert sha(ROOT/row['path']) == row['sha256'], row['path']
for ident in (history['coordinator'], history['ttsOwner']):
    assert not live(ident)
summary = read(R/'narration-timed-summary-sampled-direct-review-v1.json')
normal = read(R/'narration-timed-summary-normal-playback-observation-v1.json')
stamp = datetime.now(timezone.utc).isoformat()
proof = dict(schemaVersion=1, recordedAt=stamp, userResumeEvidence='계속 끝날때까지 재게해줘',
    automationStatus='ACTIVE', activeOwnedWorkers=0,
    ownRepairResearchRestorationHistoricallyVerified=verification,
    currentOriginalResearchIdentity=history['resumedQueue'], currentOriginalResearchAlive=False,
    currentResearchStatus=status, currentResearchStatusPath=str(status_path),
    currentResearchStatusSha256=sha(status_path),
    currentResearchInterpretation='Original restored research queue completed 1088/1088 and exited; visual review remains pending. No restart, optimizer/RNG or visual-quality approval claimed.',
    completionWriterSource=dict(path=str(code_path), sha256=sha(code_path), line=264),
    currentForeignLease=None, foreignResearchOrPauseOrLeaseMutations=0,
    all71ProtectedHashesMatched=True,
    repairActualSession=12937, repairActualOuterExitCode=0,
    spliceWholeAsr=dict(session=25068, exitCode=0), spliceSeamAsr=dict(session=8998, exitCode=0),
    summaryRender=dict(session=22262, exitCode=0, frames=1997, pcmSeconds=33.28,
        sampledReview='narration-timed-summary-sampled-direct-review-v1.json',
        sampledReviewSha256=sha(R/'narration-timed-summary-sampled-direct-review-v1.json'),
        normalPlayback='narration-timed-summary-normal-playback-observation-v1.json',
        normalPlaybackSha256=sha(R/'narration-timed-summary-normal-playback-observation-v1.json')),
    cutAllocationProposal='narration-led-cut-allocation-proposal-v1.json',
    cutAllocationApproved=False, finalRatioMeasured=False, currentMixedAudioApproved=False,
    allFinalPixelsApproved=False, fourOutputsCollected=False, actualReplacementVideoId=None,
    privateSettingsVerified=False, gitDelivered=False, scheduleReplacementVerified=False, oldUploadDeleted=False,
    stopAfter='game-math-normal-transform-uv', startRemainingSixSakurai=False,
    next='Preserve completed repair/ASR/33.28-second summary and QA. Align native before/action/result cuts with current PCM; proposed 8085 new body frames/4851 actual/3234 explanation is conditional. Render measured 07b/08b and tracked gameplay annotations, then mix/KOEN/chapters/ending/current mixed ASR/final pixels/two decodes/four outputs/private settings/Git/current original 09:00 schedule replacement before corresponding obsolete deletion. Pause at Part2 normal-transform-UV completion boundary.')
out.write_text(json.dumps(proof, ensure_ascii=False, indent=2)+'\n', 'utf-8')
cp_path = R/'latest-checkpoint.json'
cp = read(cp_path)
cp.update(recordedAt=stamp, currentHandoff=out.name,
    currentOriginalResearchPid=history['resumedQueue']['pid'],
    currentOriginalResearchCreateTime=history['resumedQueue']['createTime'],
    currentOriginalResearchAlive=False, currentOriginalResearchObservationAt=stamp,
    currentOriginalResearchStatus=status, researchCompletedPendingVisualReview=True,
    stableGpuIdle20SecondsVerified=False, voiceRequestEligibleAtObservation=False,
    currentResourceVerificationScope='Historical repair eligibility; no fresh GPU eligibility approval.',
    next=proof['next'])
cp_path.write_text(json.dumps(cp, ensure_ascii=False, indent=2)+'\n', 'utf-8')
queue_path = B/'queue.json'
queue = read(queue_path)
motion = queue['currentProduction'] if 'currentProduction' in queue else None
if motion is None:
    for value in queue.values():
        if isinstance(value, dict) and value.get('currentCheckpoint', '').endswith('revision-cross-game-four-v1/latest-checkpoint.json'):
            motion = value
            break
assert motion is not None, 'Require exact owned production entry.'
motion['currentHandoff'] = out.relative_to(ROOT).as_posix()
motion['currentDuplicateCheckVerification'] = (R/'duplicate-current-check-verification-v9.json').relative_to(ROOT).as_posix()
motion['activeOwnedWorkers'] = 0
queue.update(status='active', next=proof['next'], recordedAt=stamp)
queue_path.write_text(json.dumps(queue, ensure_ascii=False, indent=2)+'\n', 'utf-8')
print(json.dumps(dict(handoff=out.relative_to(ROOT).as_posix(), protected=len(protected), researchStatus=status, activeOwnedWorkers=0)))
