"""Read-only restoration lineage and bounded GPU observation. No TTS request."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, subprocess, time, psutil

ROOT = Path(__file__).resolve().parents[3]
R = ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
out = R/'voice-retry-resource-verification-v13.json'
assert not out.exists(), 'Inspect completed observation rather than repeating it.'
failure = read(R/'research-handoff-premodel-failure-verification-v4.json')
assert failure['restorationVerified'] and failure['newPcmCount'] == 0
hp = ROOT/'shared/output/gpu-handoff/a5373dcb-af59-4431-b6b9-41eb1b89f07a.json'
own = read(hp)
assert own['state'] == 'research_resume_verified' and sha(hp) == failure['historySha256']
expected = own['resumedQueue']
ident = expected
lineage = []
lease_path = ROOT/'shared/output/GPU_HANDOFF.json'

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

# Follow only exact identity-matched, sealed historical restorations. A later
# foreign restoration is explicitly separate from this video's own v4 resume.
while not live(ident):
    lease = read(lease_path) if lease_path.exists() else None
    if lease and matches(lease.get('queueOwner', {}), ident):
        assert live(lease['coordinator'])
        break
    candidates = []
    for path in (ROOT/'shared/output/gpu-handoff').glob('*.json'):
        history = read(path)
        if history.get('state') == 'research_resume_verified' and matches(history.get('queueOwner', {}), ident):
            candidates.append((history.get('updatedAt', 0), path, history))
    assert len(candidates) == 1, 'Require a single exact restoration link; never start research here.'
    _, path, history = candidates[0]
    resumed = history['resumedQueue']
    assert resumed['command'] == expected['command'] and resumed['cwd'] == expected['cwd']
    assert history['resumedStatus']['owner_pid'] == resumed['pid']
    assert resumed['createTime'] > ident['createTime']
    lineage.append(dict(path=path.relative_to(ROOT).as_posix(), sha256=sha(path),
        token=history['token'], project=history['project'], state=history['state'],
        original=ident, resumed=resumed, recordedResumedStatus=history['resumedStatus'],
        restorationBelongsToThisMotionJob=False))
    ident = resumed
    assert len(lineage) <= 20

rows = []
started = time.monotonic()
idle_since = None
stable = False
lease = None
while True:
    lease = read(lease_path) if lease_path.exists() else None
    vals = [int(x.strip()) for x in subprocess.check_output(
        ['nvidia-smi', '--query-gpu=memory.free,utilization.gpu', '--format=csv,noheader,nounits'], text=True).strip().split(',')]
    stamp = time.monotonic()
    rows.append(dict(observedAt=datetime.now(timezone.utc).isoformat(),
        elapsedSeconds=stamp-started, freeMiB=vals[0], utilization=vals[1]))
    if lease:
        assert lease['project'] != 'motion-sickness-games', 'Inspect a live owned request instead of duplicating it.'
        assert matches(lease['queueOwner'], ident) and live(lease['coordinator'])
        break
    assert live(ident), 'Original research identity changed; inspect actual new handoff.'
    if vals[0] >= 18000 and vals[1] < 15:
        if idle_since is None:
            idle_since = stamp
        stable = stamp-idle_since >= 20
    else:
        idle_since = None
    if stable or stamp-started >= 56:
        break
    time.sleep(2)

old = read(R/'voice-retry-resource-verification-v12.json')
for row in old['protectedInputs']:
    assert sha(ROOT/row['path']) == row['sha256'], row['path']
request = read(R/'narration-tts-request-v1.json')
assert not any((ROOT/x['path']).exists() for x in request['scenes'])
status = read(Path(own['queueDir'])/'status.json')
if live(ident):
    assert status['owner_pid'] == ident['pid']
proof = dict(schemaVersion=1, observedAt=datetime.now(timezone.utc).isoformat(),
    previousObservation='voice-retry-resource-verification-v12.json',
    restorationVerified=True, historicalOwnRestoration=expected,
    restorationScope='Own v4 restoration remains historically verified. Later exact foreign restoration links/current foreign handoff are separately identified; this observer starts or resumes no research.',
    historyPath=hp.relative_to(ROOT).as_posix(), historySha256=sha(hp),
    subsequentForeignRestorationLineage=lineage, currentOriginalResearch=ident,
    currentOriginalQueueAlive=live(ident), currentResearchStatus=status,
    gpuObservations=rows, stableGpuIdle20SecondsVerified=stable,
    currentForeignLease=lease, voiceRequestEligible=stable and lease is None and live(ident),
    all68ProtectedHashesMatched=True, protectedInputs=old['protectedInputs'],
    freePhysicalMemoryKiB=psutil.virtual_memory().available//1024,
    cpuLoadPercent=psutil.cpu_percent(interval=1), ownHeavyCpuJobs=0,
    processOrPauseOrLeaseMutations=0, newPcmCount=0, voiceRequestStarted=False)
out.write_text(json.dumps(proof, ensure_ascii=False, indent=2)+'\n', 'utf-8')
print(json.dumps(dict(observations=len(rows), stableGpuIdle20SecondsVerified=stable,
    foreignToken=lease['token'] if lease else None, currentResearchPid=ident['pid'],
    foreignRestorationLinks=len(lineage), newPcmCount=0)))
