"""One read-only foreign handoff snapshot. This does not approve stable GPU idle."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, os, subprocess, psutil

ROOT = Path(__file__).resolve().parents[3]
B = Path(__file__).parent
R = ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
args = argparse.ArgumentParser()
args.add_argument('--version', required=True, type=int)
args.add_argument('--previous', required=True)
args = args.parse_args()
out = R/f'resource-and-annotation-handoff-v{args.version}.json'
assert not out.exists(), 'Inspect existing observation; do not repeat it.'
prior_path = R/args.previous
prior = read(prior_path)
ident = prior['currentOriginalResearch']
expected_command, expected_cwd = ident['command'], ident['cwd']
lease_path = ROOT/'shared/output/GPU_HANDOFF.json'

def matches(a, b):
    return (a.get('pid') == b.get('pid') and
        abs(a.get('createTime', -1)-b.get('createTime', 0)) < .01 and
        a.get('command') == b.get('command') and a.get('cwd') == b.get('cwd'))

def live(identity):
    try:
        p = psutil.Process(identity['pid'])
        if abs(p.create_time()-identity['createTime']) >= .01:
            return False
        assert p.cmdline() == identity['command'] and p.cwd() == identity['cwd']
        return p.is_running()
    except psutil.NoSuchProcess:
        return False

def save(path, value):
    tmp = path.with_name(path.name+f'.{os.getpid()}.writing')
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', 'utf-8')
    os.replace(tmp, path)

lineage = []
while not live(ident):
    lease = read(lease_path) if lease_path.exists() else None
    if lease and matches(lease.get('queueOwner', {}), ident):
        assert live(lease['coordinator'])
        break
    candidates = []
    for path in (ROOT/'shared/output/gpu-handoff').glob('*.json'):
        history = read(path)
        if history.get('state') == 'research_resume_verified' and matches(history.get('queueOwner', {}), ident):
            candidates.append((path, history))
    assert len(candidates) == 1, 'Require one exact restoration link. Never launch research.'
    path, history = candidates[0]
    resumed = history['resumedQueue']
    assert resumed['command'] == expected_command and resumed['cwd'] == expected_cwd
    assert resumed['createTime'] > ident['createTime']
    assert history['resumedStatus']['owner_pid'] == resumed['pid']
    lineage.append(dict(path=path.relative_to(ROOT).as_posix(), sha256=sha(path),
        token=history['token'], project=history['project'], state=history['state'],
        original=ident, resumed=resumed, recordedResumedStatus=history['resumedStatus'],
        restorationBelongsToThisMotionJob=False))
    ident = resumed
    assert len(lineage) <= 20

lease = read(lease_path)
assert lease['project'] != 'motion-sickness-games' and matches(lease['queueOwner'], ident)
assert live(lease['coordinator'])
research_alive = live(ident)
status = read(Path(lease['queueDir'])/'status.json')
if research_alive:
    assert status['owner_pid'] == ident['pid']
else:
    assert status['status'] == 'stopped' and lease['state'] in ['waiting_for_gpu_idle', 'tts_running', 'resuming_research']
gpu = [int(x.strip()) for x in subprocess.check_output(
    ['nvidia-smi', '--query-gpu=memory.free,utilization.gpu', '--format=csv,noheader,nounits'], text=True).strip().split(',')]
protected = read(R/'voice-retry-resource-verification-v9.json')['protectedInputs']
for row in protected:
    assert sha(ROOT/row['path']) == row['sha256'], row['path']
request = read(R/'narration-tts-request-v1.json')
assert not any((ROOT/x['path']).exists() for x in request['scenes'])
rows = []
for p in psutil.process_iter(['pid', 'cmdline', 'name']):
    if (p.info['name'] or '').lower() not in ['python.exe', 'ffmpeg.exe']:
        continue
    command = ' '.join(p.info['cmdline'] or []).lower()
    assert 'render-motion-four-additions-' not in command
    try:
        rows.append(dict(pid=p.pid, createTime=p.create_time(), command=p.cmdline(), cwd=p.cwd()))
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass
stamp = datetime.now(timezone.utc).isoformat()
proof = dict(schemaVersion=1, observedAt=stamp,
    previousHandoff=args.previous, previousHandoffSha256=sha(prior_path),
    additionalForeignRestorationLineage=lineage, currentOriginalResearch=ident,
    currentOriginalResearchAlive=research_alive, currentResearchStatus=status,
    currentForeignLease=lease, pythonAndFfmpeg=rows,
    gpuSingleObservation=dict(freeMiB=gpu[0], utilization=gpu[1]),
    stableGpuIdle20SecondsVerified=False, voiceRequestEligible=False,
    observationScope='Single actual foreign handoff identity/status/GPU snapshot; no stable-idle observer or TTS.',
    freePhysicalMemoryKiB=psutil.virtual_memory().available//1024,
    cpuLoadPercent=psutil.cpu_percent(interval=1),
    all68ProtectedInputsMatched=True, newPcmCount=0, currentOwnedVoiceOrGpuJobs=0,
    ownResearchResumeClaim=False, processOrPauseOrLeaseMutations=0,
    currentDuplicateCheckPassed=False, currentDuplicateReviewPending='duplicate-refresh-pending-v6.json',
    conditionalTimingPreparation='conditional-timing-feasibility-v1.json',
    completedSourceAndPilotReviewsRepeated=False, newMediaCreated=0,
    baselineScheduleChanged=False, replacementVideoId=None, oldUploadDeleted=False,
    next='Preserve active foreign handoff and its owned controls. After closure, follow exact sealed restoration to the actual original research and create one new stable20s read-only resource observation. Do not run V5 against false resources or repeat completed observer v9. After resource eligibility, review all current changed full contents/Studio and pass current duplicate --check before one new TTS request. Preserve original schedule until complete replacement/QA/settings/Git/same09schedule, then delete only corresponding obsolete ID.')
save(out, proof)
cp_path = R/'latest-checkpoint.json'
raw = cp_path.read_text('utf-8-sig')
cp = json.loads(raw)
cp.update(recordedAt=stamp, currentHandoff=out.name, currentForeignHandoff=lease['token'],
    currentOriginalResearchPid=ident['pid'], currentOriginalResearchCreateTime=ident['createTime'],
    currentOriginalResearchAlive=research_alive, stableGpuIdle20SecondsVerified=False,
    currentOwnedVoiceWorkerAlive=False, currentOwnedGpuJobs=0,
    newVoiceRequestStarted=False, newPcmCount=0, next=proof['next'])
assert cp_path.read_text('utf-8-sig') == raw
save(cp_path, cp)
qp = B/'queue.json'
raw = qp.read_text('utf-8-sig')
q = json.loads(raw)
q['currentMotionReview'].update(currentHandoff=out.relative_to(ROOT).as_posix(),
    currentForeignHandoff=lease['token'], next=proof['next'])
q['updatedAt'] = stamp
assert qp.read_text('utf-8-sig') == raw
save(qp, q)
print(json.dumps(dict(foreignRestorationLinks=len(lineage), originalResearchPid=ident['pid'],
    originalResearchAlive=research_alive, foreignToken=lease['token'],
    foreignState=lease['state'], newPcmCount=0, foreignControlsModified=0)))
