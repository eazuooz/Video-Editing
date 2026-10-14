"""Seal completed read-only resource observation; never request TTS here."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, psutil

ROOT = Path(__file__).resolve().parents[3]
B = Path(__file__).parent
R = ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
def save(p, obj):
    tmp = p.with_name(p.name + f'.{os.getpid()}.writing')
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', 'utf-8')
    os.replace(tmp, p)

out = R/'resource-and-annotation-handoff-v6.json'
assert not out.exists()
resource = read(R/'voice-retry-resource-verification-v7.json')
assert resource['restorationVerified'] and resource['all68ProtectedHashesMatched']
assert not resource['stableGpuIdle20SecondsVerified'] and not resource['voiceRequestStarted']
request = read(R/'narration-tts-request-v1.json')
assert not any((ROOT/x['path']).exists() for x in request['scenes'])
for row in resource['protectedInputs']:
    assert sha(ROOT/row['path']) == row['sha256'], row['path']
original = resource['currentOriginalResearch']
proc = psutil.Process(original['pid'])
assert abs(proc.create_time()-original['createTime']) < .01
assert proc.cmdline() == original['command'] and proc.cwd() == original['cwd']
status = read(Path('C:/Users/eazuo/renderformer/tmp/placement_focus_20261008/status.json'))
rows = []
for candidate in psutil.process_iter(['pid', 'create_time', 'cmdline', 'name']):
    try:
        if (candidate.info['name'] or '').lower() in ['python.exe', 'ffmpeg.exe']:
            rows.append(dict(pid=candidate.pid, createTime=candidate.create_time(),
                command=candidate.cmdline(), cwd=candidate.cwd()))
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass
stamp = datetime.now(timezone.utc).isoformat()
proof = dict(schemaVersion=1, observedAt=stamp,
    completedReadOnlyObservation=dict(actualSessionId=97551, actualExitCode=0,
        path='voice-retry-resource-verification-v7.json', sha256=sha(R/'voice-retry-resource-verification-v7.json'),
        samples=len(resource['gpuObservations']), stableGpuIdle20SecondsVerified=False),
    duplicateReview=dict(path='duplicate-content-and-studio-direct-review-v5.json',
        sha256=sha(R/'duplicate-content-and-studio-direct-review-v5.json'),
        actualDecisionExitCode=0, actualCheckExitCode=0),
    currentResearchStatus=status, pythonAndFfmpeg=rows,
    previousOwnRestorationRemainsVerified=True, currentResearchCurrentlyAlive=True,
    newVoiceRequestStarted=False, newPcmCount=0, all68ProtectedInputsMatched=True,
    processOrResearchPauseOrLeaseMutations=0, newMediaOrGitImages=0,
    preservedPilotReviews=['portal-annotation-pilot-direct-review-v2.json', 'alyx-annotation-pilot-direct-review-v1.json'],
    baselineVideoId='mBDd9VzSTkA', replacementOrDeletionPerformed=False,
    next='Do not run prepared V5 against false resourceV6/V7. A later fresh resource observation must pass stable20s and current restoration/foreign-lease checks before preparing one new version request. Preserve completed native/pilot/structural reviews. Refresh changed full duplicate contents/current Studio if needed; then actual3PCM/currentASR/timing/mix/finalQA/private/settings/Git/same09schedule before obsolete deletion.')
save(out, proof)
cp = read(R/'latest-checkpoint.json')
cp.update(recordedAt=stamp, currentHandoff=out.name,
    currentResourceVerification='voice-retry-resource-verification-v7.json',
    currentDuplicateReview='duplicate-content-and-studio-direct-review-v5.json',
    stableGpuIdle20SecondsVerified=False, newVoiceRequestStarted=False,
    currentOwnedVoiceWorkerAlive=False, currentOwnedGpuJobs=0, newPcmCount=0,
    next=proof['next'])
save(R/'latest-checkpoint.json', cp)
qp = B/'queue.json'
raw = qp.read_text('utf-8-sig')
q = json.loads(raw)
q['currentMotionReview'].update(currentHandoff=out.relative_to(ROOT).as_posix(),
    currentResourceVerification=(R/'voice-retry-resource-verification-v7.json').relative_to(ROOT).as_posix(),
    currentDuplicateReview=(R/'duplicate-content-and-studio-direct-review-v5.json').relative_to(ROOT).as_posix(),
    next=proof['next'], status=cp['stage'])
q['updatedAt'] = stamp
assert qp.read_text('utf-8-sig') == raw, 'Preserve a concurrent queue update.'
save(qp, q)
print(json.dumps(dict(resourceSession=97551, actualExitCode=0,
    stableGpuIdle20SecondsVerified=False, newPcmCount=0, currentResearchStatus=status), ensure_ascii=False))
