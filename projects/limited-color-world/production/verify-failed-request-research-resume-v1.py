"""Verify the observed failed first request and exact own research restoration."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, psutil

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
rel = lambda p: p.relative_to(ROOT).as_posix()
def save(path, value):
    temp = path.with_name(path.name + f'.{os.getpid()}.writing')
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    os.replace(temp, path)
def live(identity):
    try:
        return abs(psutil.Process(identity['pid']).create_time() - identity['createTime']) < .01
    except psutil.NoSuchProcess:
        return False

session_path = BASE / 'narration-tts-session-v1.json'
session = read(session_path)
assert session['sessionId'] == 1912
assert not live(dict(pid=session['actualPid'], createTime=session['createTime']))
history_path = ROOT / 'shared/output/gpu-handoff/f41dafd0-6437-4804-8236-253c74ae5db0.json'
history = read(history_path)
assert history['project'] == 'limited-color-world'
assert history['ttsExitCode'] == 1 and history['state'] == 'research_resume_verified'
assert not live(history['coordinator']) and not live(history['ttsOwner'])
lease_path = ROOT / 'shared/output/GPU_HANDOFF.json'
lease = read(lease_path) if lease_path.exists() else None
assert lease is None or lease['token'] != history['token']
original, resumed = history['queueOwner'], history['resumedQueue']
assert original['command'] == resumed['command']
assert Path(original['cwd']).resolve() == Path(resumed['cwd']).resolve()
assert live(resumed)
process = psutil.Process(resumed['pid'])
assert process.cmdline() == resumed['command']
assert Path(process.cwd()).resolve() == Path(original['cwd']).resolve()
status_path = Path(history['queueDir']) / 'status.json'
status = read(status_path)
assert status['owner_pid'] == resumed['pid'] and status['status'] in ['running', 'waiting_for_resources']
controls = []
for path in history['ownedFiles']:
    p = Path(path)
    current = read(p) if p.exists() else None
    assert current is None or current.get('token') != history['token']
    controls.append(dict(path=str(p), exists=p.exists(), current=current))
request = read(BASE / 'narration-tts-request-v1.json')
protected = [dict(**x, currentSha256=sha(ROOT/x['path']), matches=sha(ROOT/x['path']) == x['sha256']) for x in request['protectedInputs']]
assert all(x['matches'] for x in protected)
pcm = [x['path'] for x in request['scenes'] if (ROOT/x['path']).exists()]
assert len(pcm) == 0 and not (BASE/'narration-tts-execution-v1.json').exists()
log_path = Path(history['ttsLog'])
log = log_path.read_text(encoding='utf-8-sig')
assert 'Content and current channel-upload review must establish a distinct topic' in log
out = BASE / 'failed-request-research-resume-verification-v1.json'
assert not out.exists()
record = dict(schemaVersion=1, observedAt=datetime.now(timezone.utc).isoformat(),
    actualOuterSession=1912, actualOuterExitCode=1, actualExitToolObservation='028cfa',
    token=history['token'], history=dict(path=rel(history_path), sha256=sha(history_path)),
    log=dict(path=rel(log_path), sha256=sha(log_path)),
    reason='During inventory refresh the report was pending; the coordinated child rejected the duplicate gate before model/state/PCM creation. Full changed manifest/current Studio review was subsequently sealed in content-studio-change-review-v4.json.',
    modelLoaded=False, ownPcmCount=0, ownExecutionStateCreated=False,
    protectedInputs=protected, originalResearchIdentity=original,
    actualResumedIdentity=dict(pid=process.pid, createTime=process.create_time(), command=process.cmdline(), cwd=process.cwd()),
    recordedRestorationStatus=history['resumedStatus'], currentResearchStatus=status,
    originalCommandCwdQueueRestorationVerified=True, resumedTrainingJobStarted=status['status'] == 'running',
    completedJobEvidence=history.get('completedJobEvidence'),
    optimizerOrRngResumeClaim=False, ownLeaseClosed=True, foreignLeasePreserved=lease,
    ownedControlObservations=controls, processOrControlMutationByVerifier=0,
    pcmRegenerationOrCompletedWorkRepeated=False)
save(out, record)
for name in ['narration-tts-session-v1.json', 'narration-tts-waiting-v1.json', 'render-voice-v1.py']:
    source = BASE/name
    target = BASE/(source.stem + '-attempt1-preserved' + source.suffix)
    assert not target.exists()
    target.write_bytes(source.read_bytes())
session.update(actualExitObserved=True, actualOuterExitCode=1, actualExitObservedAt=record['observedAt'],
               ownLeaseToken=history['token'], failedBeforeModel=True, researchRestorationVerified=True,
               failureVerification=rel(out))
save(session_path, session)
print(json.dumps(dict(session=1912, actualExitCode=1, model=False, pcm=0, protected10=True,
                     ownResearchRestorationVerified=True, actualResumedPid=process.pid, actualStatus=status['status'])))
