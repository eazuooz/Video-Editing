"""Record the actual serialized exec session; do not start or stop workers."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, json, os, time
import psutil

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
read = lambda p: json.loads(p.read_text('utf-8-sig'))
def save(p, value):
    temp = p.with_name(p.name + '.session-record-writing')
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf-8')
    os.replace(temp, p)

ap = argparse.ArgumentParser()
ap.add_argument('--mode', choices=['whole', 'contexts', 'targets'], required=True)
ap.add_argument('--session-id', type=int, required=True)
ap.add_argument('--actual-exit-code', type=int)
args = ap.parse_args()
path = BASE / f'current-{args.mode}-asr-execution-v1.json'
state = read(path)
stamp = datetime.now(timezone.utc).isoformat()
if args.actual_exit_code is None:
    process = psutil.Process(state['pid'])
    assert abs(process.create_time() - state['createTime']) < .01
    assert state['exitCode'] is None
    identity = dict(pid=process.pid, createTime=process.create_time(),
                    commandLine=process.cmdline(), cwd=process.cwd())
else:
    assert state['exitCode'] == args.actual_exit_code
    try:
        process = psutil.Process(state['pid'])
        assert abs(process.create_time() - state['createTime']) > .01, 'Recorded worker still alive'
    except psutil.NoSuchProcess:
        pass
    identity = state['processIdentity']
session_path = path.with_name(path.stem + '.session.json')
if session_path.exists():
    previous = read(session_path)
    assert previous['sessionId'] == args.session_id and previous['pid'] == state['pid']
session = dict(observedAt=stamp, pid=state['pid'], createTime=state['createTime'],
               sessionId=args.session_id, processIdentity=identity,
               actualOuterExitCode=args.actual_exit_code,
               actualExitObserved=args.actual_exit_code is not None,
               processOrControlMutations=0)
save(session_path, session)
state.update(sessionId=args.session_id, processIdentity=identity)
if args.actual_exit_code is not None:
    state.update(actualExitObserved=True, actualOuterExitCode=args.actual_exit_code,
                 actualExitObservedAt=stamp)
save(path, state)
cp_path = BASE / 'latest-checkpoint.json'
cp = read(cp_path)
if cp.get('ownedJob', {}).get('pid') == state['pid']:
    cp['ownedJob'].update(sessionId=args.session_id, processIdentity=identity,
                         workerExpectedRunning=args.actual_exit_code is None,
                         actualExitObserved=args.actual_exit_code is not None,
                         exitCode=args.actual_exit_code)
cp['researchResumeVerification'] = 'projects/character-parameters/production/research-handoff-verification-v2.json'
cp['researchRestorationVerified'] = True
cp['recordedAt'] = stamp
save(cp_path, cp)
qp = ROOT / 'production/batches/sakurai-planning-game-design/queue.json'
for _ in range(8):
    raw = qp.read_text('utf-8-sig')
    queue = json.loads(raw)
    item = next(x for x in queue['items'] if x['slug'] == 'character-parameters')
    item['currentExecution'] = cp['ownedJob']
    item['researchResumeVerification'] = cp['researchResumeVerification']
    item['researchRestorationVerified'] = True
    queue['updatedAt'] = stamp
    if qp.read_text('utf-8-sig') == raw:
        save(qp, queue)
        break
    time.sleep(.15)
else:
    raise RuntimeError('Concurrent queue write; preserve foreign bytes')
print(json.dumps(session, ensure_ascii=False))
