"""Read-only identity snapshot and conditional timing arithmetic; no media jobs."""
from pathlib import Path
from datetime import datetime, timezone
from fractions import Fraction
import hashlib, json, os, subprocess, psutil

ROOT = Path(__file__).resolve().parents[3]
B = Path(__file__).parent
R = ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def save(p, data):
    tmp = p.with_name(p.name+f'.{os.getpid()}.writing')
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', 'utf-8')
    os.replace(tmp, p)

def matches(a, b):
    return (a.get('pid') == b.get('pid') and
        abs(a.get('createTime', -1)-b.get('createTime', 0)) < .01 and
        a.get('command') == b.get('command') and a.get('cwd') == b.get('cwd'))

def live(identity):
    try:
        proc = psutil.Process(identity['pid'])
        if abs(proc.create_time()-identity['createTime']) >= .01:
            return False
        assert proc.cmdline() == identity['command'] and proc.cwd() == identity['cwd']
        return proc.is_running()
    except psutil.NoSuchProcess:
        return False

out = R/'resource-and-annotation-handoff-v8.json'
timing_out = R/'conditional-timing-feasibility-v1.json'
assert not out.exists() and not timing_out.exists(), 'Inspect saved results; do not repeat.'
previous = read(R/'voice-retry-resource-verification-v8.json')
ident = previous['currentOriginalResearch']
lineage = []
lease_path = ROOT/'shared/output/GPU_HANDOFF.json'
while not live(ident):
    lease = read(lease_path) if lease_path.exists() else None
    if lease and matches(lease.get('queueOwner', {}), ident):
        assert live(lease['coordinator'])
        break
    histories = []
    for path in (ROOT/'shared/output/gpu-handoff').glob('*.json'):
        history = read(path)
        if history.get('state') == 'research_resume_verified' and matches(history.get('queueOwner', {}), ident):
            histories.append((path, history))
    assert len(histories) == 1, 'Require an exact restoration link; never launch research.'
    path, history = histories[0]
    resumed = history['resumedQueue']
    assert resumed['command'] == ident['command'] and resumed['cwd'] == ident['cwd']
    assert resumed['createTime'] > ident['createTime']
    assert history['resumedStatus']['owner_pid'] == resumed['pid']
    lineage.append(dict(path=path.relative_to(ROOT).as_posix(), sha256=sha(path),
        token=history['token'], state=history['state'], original=ident, resumed=resumed,
        recordedResumedStatus=history['resumedStatus'], restorationBelongsToThisMotionJob=False))
    ident = resumed
    assert len(lineage) <= 20

lease = read(lease_path)
assert lease['project'] != 'motion-sickness-games' and matches(lease['queueOwner'], ident)
assert live(lease['coordinator']) and live(ident)
gpu = [int(x.strip()) for x in subprocess.check_output(
    ['nvidia-smi', '--query-gpu=memory.free,utilization.gpu', '--format=csv,noheader,nounits'], text=True).strip().split(',')]
status = read(Path(lease['queueDir'])/'status.json')
assert status['owner_pid'] == ident['pid']
for row in previous['protectedInputs']:
    assert sha(ROOT/row['path']) == row['sha256'], row['path']
request = read(R/'narration-tts-request-v1.json')
assert not any((ROOT/x['path']).exists() for x in request['scenes'])
own_jobs = []
for proc in psutil.process_iter(['pid', 'cmdline']):
    command = ' '.join(proc.info['cmdline'] or []).lower()
    if 'render-motion-four-additions-' in command:
        own_jobs.append(proc.pid)
assert not own_jobs

# This is a capacity ceiling, not an allocation or timing approval. Source
# intervals remain conditional and must be matched to measured narration.
bank_path = R/'sources/source-action-bank-v1.json'
bank = read(bank_path)
baseline_path = ROOT/'projects/motion-sickness-games/production/revision-teaching-clarity-v1/measured-additive-plan-v1.json'
baseline = read(baseline_path)
assert baseline['fps'] == 60 and baseline['bodyFrames'] == 39473
rows = []
for action in bank['actions']:
    assert action['speed'] == 1 and not action['loop'] and not action['slowdown']
    duration = Fraction(action['sourceEndExclusivePts']-action['sourceFirstPts'])*Fraction(action['nativeTimeBase'])
    frames = duration*60
    rows.append(dict(id=action['id'], exactDurationFraction=str(duration),
        conservativeOutputCapacityFrames=frames.numerator//frames.denominator,
        actualFinalAllocationFrames=None))
capacity = sum(x['conservativeOutputCapacityFrames'] for x in rows)
actual = baseline['actualFrames']
body = baseline['bodyFrames']
explanation = baseline['explanationFrames']
assert actual+explanation == body
target = Fraction(3, 5)
surplus = Fraction(actual)-target*body
# Upper bound allows the specified one-frame rounding tolerance. It does not
# grant permission to pad narration or remove useful explanations.
max_addition = (Fraction(actual+capacity+1)/target-body).__floor__()
scenarios = []
for seconds in [90, 120, 140, 180]:
    added_body = seconds*60
    needed = target*(body+added_body)-actual
    nearest = (needed+Fraction(1, 2)).__floor__()
    scenarios.append(dict(illustrativeAddedBodySeconds=seconds,
        requiredAddedActualFrames=nearest, requiredAddedExplanationFrames=added_body-nearest,
        extraUniqueActualFramesBeyondCurrentBank=max(0, nearest-capacity),
        measuredNarration=False))
stamp = datetime.now(timezone.utc).isoformat()
timing = dict(schemaVersion=1, recordedAt=stamp, preparedOnly=True,
    sourceBank=bank_path.relative_to(ROOT).as_posix(), sourceBankSha256=sha(bank_path),
    baselinePlan=baseline_path.relative_to(ROOT).as_posix(), baselinePlanSha256=sha(baseline_path),
    baselineBodyFrames=body, baselineActualFrames=actual, baselineExplanationFrames=explanation,
    baselineActualSurplusFrames=str(surplus), fps=60, bodyActualRatio='3/5',
    capacityMethod='Sum floor(exact native PTS interval seconds * 60) independently; no loop or slowdown.',
    conditionalActionCapacity=rows, conditionalUniqueActualCapacityFrames=capacity,
    conditionalMaximumAddedBodyFramesWithOneFrameTolerance=max_addition,
    conditionalMaximumAddedBodySeconds=max_addition/60, illustrativeScenarios=scenarios,
    calculation='required added actual = 3/5 * (baseline body + added body) - baseline actual; equivalently added actual = 3/2 * added explanation - baseline surplus / (2/5).',
    next='Measure the three actual PCM durations and pauses; map visible claims before allocation. If required unique actual exceeds usable bank capacity, secure more clear concept-matched footage. Preserve good explanation/PCM; do not shorten them or loop/slow footage to fit.',
    narrationMeasured=False, footageAdopted=False, finalRatioApproved=False,
    finalCueOrMovingAnnotationApproved=False, newMediaCreated=0)
save(timing_out, timing)
proof = dict(schemaVersion=1, observedAt=stamp,
    previousHandoff='resource-and-annotation-handoff-v7.json',
    previousCompletedResourceObservation='voice-retry-resource-verification-v8.json',
    additionalForeignRestorationLineage=lineage, currentOriginalResearch=ident,
    currentResearchStatus=status, currentForeignLease=lease,
    gpuSingleObservation=dict(freeMiB=gpu[0], utilization=gpu[1]),
    stableGpuIdle20SecondsVerified=False, voiceRequestEligible=False,
    observationScope='One current identity/lease/status/GPU snapshot, not a repeated stable-idle observer.',
    all68ProtectedInputsMatched=True, newPcmCount=0, currentOwnedVoiceOrGpuJobs=0,
    ownResearchResumeClaim=False, processOrPauseOrLeaseMutations=0,
    conditionalTimingPreparation=timing_out.name,
    completedSourceAndPilotReviewsRepeated=False,
    currentDuplicateCheckPassed=False, currentDuplicateReviewPending='duplicate-refresh-pending-v6.json',
    replacementVideoId=None, baselineScheduleChanged=False, oldUploadDeleted=False,
    next='Preserve active foreign handoff. After it closes, verify exact research restoration and one fresh stable20s resource observation. Then review all current changed duplicate contents/current Studio before one new single TTS request. Measure voice and allocate unique footage with the conditional capacity calculation; preserve the original schedule until reviewed replacement/settings/Git/schedule are verified.')
save(out, proof)
cp_path = R/'latest-checkpoint.json'
cp_raw = cp_path.read_text('utf-8-sig')
cp = json.loads(cp_raw)
cp.update(recordedAt=stamp, currentHandoff=out.name,
    currentForeignHandoff=lease['token'], conditionalTimingPreparation=timing_out.name,
    next=proof['next'])
assert cp_path.read_text('utf-8-sig') == cp_raw
save(cp_path, cp)
qp = B/'queue.json'
q_raw = qp.read_text('utf-8-sig')
q = json.loads(q_raw)
q['currentMotionReview'].update(currentHandoff=out.relative_to(ROOT).as_posix(),
    currentForeignHandoff=lease['token'], conditionalTimingPreparation=timing_out.relative_to(ROOT).as_posix(),
    next=proof['next'])
q['updatedAt'] = stamp
assert qp.read_text('utf-8-sig') == q_raw
save(qp, q)
print(json.dumps(dict(foreignRestorationLinks=len(lineage), currentResearchPid=ident['pid'],
    foreignToken=lease['token'], conditionalCapacityFrames=capacity,
    conditionalMaxAddedBodySeconds=max_addition/60, newPcmCount=0)))
