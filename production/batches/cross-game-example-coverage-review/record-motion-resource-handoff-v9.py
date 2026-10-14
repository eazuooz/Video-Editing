"""Seal completed observer v9 without starting synthesis or repeating reviews."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, psutil

ROOT = Path(__file__).resolve().parents[3]
B = Path(__file__).parent
R = ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
def save(p, value):
    tmp = p.with_name(p.name+f'.{os.getpid()}.writing')
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', 'utf-8')
    os.replace(tmp, p)

out = R/'resource-and-annotation-handoff-v9.json'
assert not out.exists()
resource_path = R/'voice-retry-resource-verification-v9.json'
resource = read(resource_path)
assert not resource['voiceRequestEligible'] and not resource['stableGpuIdle20SecondsVerified']
assert resource['currentForeignLease'] is None and resource['all68ProtectedHashesMatched']
for x in resource['protectedInputs']:
    assert sha(ROOT/x['path']) == x['sha256'], x['path']
request = read(R/'narration-tts-request-v1.json')
assert not any((ROOT/x['path']).exists() for x in request['scenes'])
current = resource['currentOriginalResearch']
proc = psutil.Process(current['pid'])
assert abs(proc.create_time()-current['createTime']) < .01
assert proc.cmdline() == current['command'] and proc.cwd() == current['cwd']
processes = []
for p in psutil.process_iter(['pid', 'cmdline', 'create_time', 'name']):
    if (p.info['name'] or '').lower() not in ['python.exe', 'ffmpeg.exe']:
        continue
    command = ' '.join(p.info['cmdline'] or []).lower()
    assert 'observe-motion-four-voice-resource-v9.py' not in command
    assert 'render-motion-four-additions-' not in command
    try:
        processes.append(dict(pid=p.pid, createTime=p.create_time(), command=p.cmdline(), cwd=p.cwd()))
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass
stamp = datetime.now(timezone.utc).isoformat()
proof = dict(schemaVersion=1, observedAt=stamp,
    completedReadOnlyObservation=dict(actualSessionId=68836, actualShellChunk='b3843a',
        actualExitCode=0, path=resource_path.name, sha256=sha(resource_path),
        observations=len(resource['gpuObservations']), stableGpuIdle20SecondsVerified=False),
    foreignRestoration=resource['subsequentForeignRestorationLineage'],
    currentOriginalResearch=current, currentResearchStatus=resource['currentResearchStatus'],
    currentForeignLease=None, currentPythonAndFfmpeg=processes,
    currentResourceEligibility=False, currentOwnedVoiceOrGpuJobs=0,
    newPcmCount=0, all68ProtectedInputsMatched=True,
    ownResearchResumeClaim=False, processOrPauseOrLeaseMutations=0,
    currentDuplicateCheckPassed=False, currentDuplicateReviewPending='duplicate-refresh-pending-v6.json',
    conditionalTimingPreparation='conditional-timing-feasibility-v1.json',
    conditionalUniqueActualCapacityFrames=4915, conditionalMaxAddedBodySeconds=136.55,
    conditionalTimingIsMeasuredApproval=False,
    completedSourceAndPilotReviewsRepeated=False, baselineScheduleChanged=False,
    replacementVideoId=None, oldUploadDeleted=False,
    next='Observer v9 finished exit0, stable20s false. Preserve foreign ASR workers and exact restored research. Do not run prepared V5 against false resource or repeat completed observer. After an actual resource change, create one new read-only version; require stable20s/current identity/no foreign lease/protected hashes. Then review all current changed full duplicate contents/current Studio and pass current --check before one new TTS request. Preserve useful explanations; measure three PCM before unique footage allocation/mix/QA/private/settings/Git/same09schedule and corresponding obsolete deletion.')
save(out, proof)
cp_path = R/'latest-checkpoint.json'
cp_raw = cp_path.read_text('utf-8-sig')
cp = json.loads(cp_raw)
cp.update(recordedAt=stamp, currentHandoff=out.name,
    currentResourceVerification=resource_path.name, currentForeignHandoff=None,
    currentOriginalResearchPid=current['pid'], currentOriginalResearchCreateTime=current['createTime'],
    stableGpuIdle20SecondsVerified=False, currentOwnedVoiceWorkerAlive=False,
    currentOwnedGpuJobs=0, newVoiceRequestStarted=False, newPcmCount=0, next=proof['next'])
assert cp_path.read_text('utf-8-sig') == cp_raw
save(cp_path, cp)
qp = B/'queue.json'
raw = qp.read_text('utf-8-sig')
q = json.loads(raw)
q['currentMotionReview'].update(currentHandoff=out.relative_to(ROOT).as_posix(),
    currentResourceVerification=resource_path.relative_to(ROOT).as_posix(), currentForeignHandoff=None,
    currentDuplicateCheckPassed=False, next=proof['next'])
q['updatedAt'] = stamp
assert qp.read_text('utf-8-sig') == raw
save(qp, q)
print(json.dumps(dict(actualCompletedObserverExitCode=0, observations=len(resource['gpuObservations']),
    stableGpuIdle20SecondsVerified=False, currentResearchPid=current['pid'],
    foreignRestorationLinks=len(resource['subsequentForeignRestorationLineage']), newPcmCount=0)))
