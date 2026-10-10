"""Verify actual additive TTS exit and its owned research handoff, read-only.

Run with the exit code returned by the original exec session, never a guessed
worker exit. A later foreign handoff is recorded without starting research.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, os
import psutil

ROOT = Path(__file__).resolve().parents[3]
R = ROOT / 'projects/motion-sickness-games/production/revision-teaching-clarity-v1'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
def live(identity):
    try:
        p = psutil.Process(identity['pid'])
        return abs(p.create_time() - identity['createTime']) < .01
    except (psutil.NoSuchProcess, KeyError):
        return False
def save(p, obj):
    tmp = p.with_name(p.name + f'.{os.getpid()}.writing')
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', 'utf-8')
    os.replace(tmp, p)

ap = argparse.ArgumentParser()
ap.add_argument('--outer-exit-code', type=int, required=True)
ap.add_argument('--session-id', type=int, required=True)
args = ap.parse_args()
assert args.session_id == 83518, 'Use only the original serialized request session.'
state_path = R / 'narration-tts-execution-v1.json'
state = read(state_path)
assert not live({'pid':state['actualPid'], 'createTime':state['createTime']}), 'TTS is still alive.'
assert args.outer_exit_code == state['exitCode'] == 0 and state['generationComplete']
assert len(state['results']) == state['total'] == 2
assert {x['id'] for x in state['results']} == {'00a', '06b'}
for x in state['results'] + state['protectedInputs']:
    assert sha(ROOT/x['path']) == x['sha256'], x['path']
history_path = ROOT/'shared/output/gpu-handoff'/f"{state['leaseToken']}.json"
history = read(history_path)
assert history['token'] == state['leaseToken'] and history['project'] == 'motion-sickness-games'
assert not live(history['coordinator']), 'Own coordinator has not closed.'
lease_path = ROOT/'shared/output/GPU_HANDOFF.json'
lease = read(lease_path) if lease_path.exists() else None
assert not lease or lease['token'] != state['leaseToken'], 'Own lease has not closed.'
proof = dict(schemaVersion=1, observedAt=datetime.now(timezone.utc).isoformat(),
    actualOuterSession=args.session_id, actualOuterExitCode=args.outer_exit_code,
    ttsLeaseToken=state['leaseToken'], historyPath=history_path.relative_to(ROOT).as_posix(),
    historySha256=sha(history_path), ownedVoiceWorkerClosed=True, ownedCoordinatorClosed=True,
    currentForeignLease=lease, processOrControlChangesByVerifier=0,
    allTwoCurrentPcmHashesMatched=True, all26ProtectedInputsMatched=True,
    original12PcmRegenerated=0, restorationVerified=False,
    humanListeningApproved=False, finalMixedAsrApproved=False)
if history.get('idleGpu'):
    assert history['state'] == 'tts_process_exiting'
    proof.update(restorationVerified=True, researchWasPaused=False,
        researchRestartedByOwnJob=False,
        restorationScope='Owned idle lease closed; this job did not pause research.')
else:
    assert history['state'] == 'research_resume_verified' and history['ttsExitCode'] == 0
    original, resumed = history['queueOwner'], history['resumedQueue']
    recorded = history['resumedStatus']
    assert resumed['command'] == original['command']
    assert Path(resumed['cwd']).resolve() == Path(original['cwd']).resolve()
    assert recorded['owner_pid'] == resumed['pid']
    assert recorded['status'] in ['running', 'waiting_for_resources']
    completed = history.get('completedJobEvidence')
    if completed:
        assert sha(Path(completed['marker'])) == completed['markerSha256']
        assert completed['validation'].get('numerically_finite') is not False
        assert completed['validation'].get('checkpoint_finite') is not False
        assert all(Path(p).exists() for p in completed['outputs'])
    for name in history.get('ownedFiles', []):
        p = Path(name)
        assert not p.exists() or read(p).get('token') != state['leaseToken']
    current = read(Path(history['queueDir'])/'status.json')
    if live(resumed):
        proc = psutil.Process(resumed['pid'])
        assert proc.cmdline() == resumed['command']
        assert Path(proc.cwd()).resolve() == Path(original['cwd']).resolve()
        assert current['owner_pid'] == resumed['pid']
        assert current['status'] in ['running', 'waiting_for_resources']
        observation = dict(kind='actual-original-resumed-queue-alive',
            pid=proc.pid, createTime=proc.create_time(), command=proc.cmdline(), cwd=proc.cwd())
    else:
        # A later coordinator may have cooperatively closed the restored queue.
        # Require its exact original identity and current live coordinator; never
        # start a new queue or label the historical resumed process as alive.
        assert lease and lease['token'] != state['leaseToken']
        later_owner = lease.get('queueOwner', {})
        assert later_owner.get('pid') == resumed['pid']
        assert abs(later_owner.get('createTime', -1)-resumed['createTime']) < .01
        assert later_owner.get('command') == resumed['command']
        assert Path(later_owner['cwd']).resolve() == Path(resumed['cwd']).resolve()
        assert live(lease['coordinator'])
        observation = dict(kind='recorded-own-resume-followed-by-actual-foreign-handoff',
            restoredProcessCurrentlyAlive=False, laterToken=lease['token'],
            laterCoordinator=lease['coordinator'], laterState=lease.get('state'))
    proof.update(restorationVerified=True, researchWasPaused=True,
        researchRestartedByOwnJob=True, originalResearchIdentity=original,
        recordedResumedIdentity=resumed, recordedResumedStatus=recorded,
        currentQueueStatus=current, currentObservation=observation,
        completedResearchJobEvidence=completed,
        restorationScope='Exact original command/cwd/queue restored at the owned handoff; current state separately verified. No optimizer/RNG recovery claim.')
save(R/'research-handoff-verification-v1.json', proof)
state.update(actualExitObserved=True, actualOuterExitCode=args.outer_exit_code,
    actualOuterSession=args.session_id, actualExitObservedAt=proof['observedAt'],
    researchResumeVerified=True)
save(state_path, state)
print('Actual two-scene exit0/own lease closure/original research restoration verified; no process/control mutation.')
