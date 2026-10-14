"""Record an observed outer ASR exit without repeating a model job."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, os, subprocess, psutil
ROOT = Path(__file__).resolve().parents[3]
B = Path(__file__).resolve().parent
O = ROOT / 'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
ap = argparse.ArgumentParser()
ap.add_argument('--mode', choices=['whole', 'contexts'], required=True)
ap.add_argument('--session', type=int, required=True)
ap.add_argument('--outer-exit', type=int, required=True)
ap.add_argument('--completion', required=True)
args = ap.parse_args()
path = O / f'additions-{args.mode}-asr-execution-v1.json'
raw = path.read_bytes()
state = read(path)
session = read(path.with_name(path.stem + '.session.json'))
assert session['sessionId'] == args.session == state['sessionId']
assert session['pid'] == state['pid'] and session['createTime'] == state['createTime']
assert not state.get('actualExitObserved'), 'An observed exit is already recorded.'
assert not psutil.pid_exists(state['pid']), 'Wait for the actual worker to close.'
cim = subprocess.check_output(['powershell', '-NoProfile', '-Command',
    f'Get-CimInstance Win32_Process -Filter "ProcessId={state["pid"]}" | Select-Object ProcessId,CreationDate,CommandLine | ConvertTo-Json'],
    text=True, encoding='utf-8', errors='replace')
assert not cim.strip()
tts = read(O / 'narration-tts-execution-v2.json')
for row in tts['protectedInputs'] + tts['results']:
    assert sha(ROOT / row['path']) == row['sha256'], row['path']
assert state['exitCode'] == args.outer_exit
assert state['completed'] == state['total'] if args.outer_exit == 0 else True
at = datetime.now(timezone.utc).isoformat()
state.update(actualExitObserved=True, actualOuterExitCode=args.outer_exit,
    actualOuterSession=args.session, actualCompletionChunk=args.completion,
    workerClosedObservedAt=at, actualCimAbsence=cim,
    protectedInputsMatchedAfterActualExit=True, currentAdditivePcmUnchanged=True)
assert path.read_bytes() == raw
path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n', 'utf-8')
for target in [O / 'latest-checkpoint.json', B / 'queue.json']:
    before = target.read_bytes()
    obj = read(target)
    if target.name == 'latest-checkpoint.json':
        obj.update(recordedAt=at, stage=f'additive-{args.mode}-ASR-closed-awaiting-direct-review',
            ownedJob=None, activeOwnedWorkers=0, currentUnmixedAsrApproved=False)
    else:
        obj['updatedAt'] = at
        obj['currentOrientationReview'].update(stage=f'existing6PCM-{args.mode}-ASR-actual-exit-verified',
            actualSession=args.session, actualOuterExitCode=args.outer_exit,
            completionChunk=args.completion, ownedJob=None, activeOwnedWorkers=0,
            next='Read all current expected/recognized words; prepare independent complete contexts. No TTS rerun.')
    assert target.read_bytes() == before, 'Preserve concurrent updates.'
    temp = target.with_name(target.name + f'.{os.getpid()}.writing')
    temp.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', 'utf-8')
    os.replace(temp, target)
print(json.dumps(dict(mode=args.mode, session=args.session, outerExit=args.outer_exit,
    completion=args.completion, workerClosed=True, protectedCount=len(tts['protectedInputs']),
    pcmCount=len(tts['results']), hashesMatched=True)))
