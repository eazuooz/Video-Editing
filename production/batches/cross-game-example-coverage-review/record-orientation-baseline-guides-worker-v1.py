"""Register or close the exact returned baseline guide session."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, os, subprocess
import psutil

ROOT = Path(__file__).resolve().parents[3]
B = Path(__file__).resolve().parent
O = ROOT / 'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
now = lambda: datetime.now(timezone.utc).isoformat()
def save(p, data):
    tmp = p.with_name(p.name+'.record-writing')
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', 'utf-8')
    os.replace(tmp, p)
ap = argparse.ArgumentParser()
ap.add_argument('--session', type=int, required=True)
ap.add_argument('--initial')
ap.add_argument('--outer-exit', type=int)
ap.add_argument('--completion')
a = ap.parse_args()
sp = O / 'current34-baseline-guides-render-execution-v1.json'
ss = sp.with_name(sp.stem+'.session.json'); s = read(sp)
try:
    p = psutil.Process(s['pid']); same = abs(p.create_time()-s['createTime']) < .01
    if same:
        assert p.cmdline() == s['commandLine'] and p.cwd() == s['cwd']
    alive = same and p.is_running()
except psutil.NoSuchProcess:
    alive = False
cim = subprocess.check_output(['powershell', '-NoProfile', '-Command',
    f"Get-CimInstance Win32_Process -Filter 'ProcessId={s['pid']}' | Select-Object ProcessId,ParentProcessId,CreationDate,CommandLine | ConvertTo-Json -Depth 3"],
    text=True, encoding='utf-8', errors='replace')
if a.outer_exit is None:
    assert a.initial and not ss.exists() and alive
    save(ss, dict(recordedAt=now(), sessionId=a.session, initialChunk=a.initial, pid=s['pid'],
        createTime=s['createTime'], commandLine=s['commandLine'], cwd=s['cwd'],
        workerAliveAtRegistration=alive, cimActual=cim))
    s['sessionId'] = a.session
else:
    assert a.completion and not alive and s['workerExitCode'] == a.outer_exit
    assert read(ss)['sessionId'] == a.session
    proof = read(O / 'narration-07b-guide-repair-execution-v1.json')
    for x in proof['protectedInputs'] + proof['results']:
        assert sha(ROOT / x['path']) == x['sha256']
    if a.outer_exit == 0:
        assert s['completedScenes'] == 8 and sum(x['frames'] for x in s['results']) == 21370
        for x in s['results']:
            assert x['allNativePtsExact'] and x['encoderExitCode'] == x['wholeDecodeExitCode'] == 0
            assert sha(ROOT / x['output']) == x['outputSha256']
            audit = read(ROOT / x['frameAudit'])
            assert sha(ROOT / x['frameAudit']) == x['frameAuditSha256']
            assert len(audit['frames']) == x['frames']
    s.update(actualOuterExitCode=a.outer_exit, actualExitObserved=True, completionChunk=a.completion,
        actualSession=a.session, workerDead=True, closureObservedAt=now(), all79ProtectedInputsUnchanged=True,
        closureCimActual=cim)
    cp = read(O / 'latest-checkpoint.json')
    cp.update(recordedAt=now(), stage=s['status']+'-actual-closed', activeOwnedWorkers=0, ownedJob=None,
        next='Directly inspect current encoded guide anchor/cut/caption samples and normal1x playback. Final current34 captions/pair/pixels/delivery/settings/Git/actual schedule remain pending.')
    save(O / 'latest-checkpoint.json', cp)
    qp = B / 'queue.json'; before = qp.read_bytes(); q = read(qp)
    q['currentOrientationReview'].update(stage=cp['stage'], activeOwnedWorkers=0, ownedJob=None, next=cp['next'])
    q['updatedAt'] = now(); assert qp.read_bytes() == before; save(qp, q)
save(sp, s)
print(json.dumps(dict(session=a.session, registered=a.outer_exit is None, alive=alive,
    outerExit=a.outer_exit, workerDead=a.outer_exit is not None)))
