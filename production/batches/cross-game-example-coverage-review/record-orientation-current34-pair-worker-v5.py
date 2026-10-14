"""Bind a real final-pair session and close only after its observed actual exit."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, os, subprocess
import psutil
ROOT = Path(__file__).resolve().parents[3]; B = Path(__file__).resolve().parent
O = ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
now = lambda: datetime.now(timezone.utc).isoformat()
def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(1048576), b''): h.update(b)
    return h.hexdigest()
def save(p, v):
    t = p.with_name(p.name+'.record-writing'); t.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8'); os.replace(t,p)
ap = argparse.ArgumentParser(); ap.add_argument('--session',type=int,required=True); ap.add_argument('--initial'); ap.add_argument('--outer-exit',type=int); ap.add_argument('--completion'); a = ap.parse_args()
sp = O/'current34-final-pair-execution-v5.json'; ss = sp.with_name(sp.stem+'.session.json'); s = read(sp)
try:
    p = psutil.Process(s['pid']); same = abs(p.create_time()-s['createTime']) < .01
    if same: assert p.cmdline() == s['commandLine'] and p.cwd() == s['cwd']
    alive = same and p.is_running()
except psutil.NoSuchProcess: alive = False
cim = subprocess.check_output(['powershell','-NoProfile','-Command', f"Get-CimInstance Win32_Process -Filter 'ProcessId={s['pid']}' | Select-Object ProcessId,ParentProcessId,CreationDate,CommandLine | ConvertTo-Json -Depth 3"],text=True,encoding='utf-8',errors='replace')
if a.outer_exit is None:
    assert a.initial and not ss.exists() and alive
    save(ss,dict(recordedAt=now(),sessionId=a.session,initialChunk=a.initial,pid=s['pid'],createTime=s['createTime'],commandLine=s['commandLine'],cwd=s['cwd'],workerAliveAtRegistration=True,cimActual=cim)); s['sessionId'] = a.session
else:
    assert a.completion and not alive and s['exitCode'] == a.outer_exit and read(ss)['sessionId'] == a.session
    proof = read(O/'narration-07b-guide-repair-execution-v1.json')
    for x in proof['protectedInputs']+proof['results']: assert sha(ROOT/x['path']) == x['sha256']
    if a.outer_exit == 0:
        assert s['frames'] == 65917 and len(s['pieces']) == 37 and len(s['pair']) == 2
        assert s['retainedByteIdenticalPieceCount'] == 3 and abs(s['bodyMeasured']['ratioErrorFrames']) <= 1
        for x in s['pair']:
            assert sha(ROOT/x['path']) == x['sha256'] and x['wholeDecodeExitCode'] == 0 and x['allPts1500Verified'] and x['identicalReviewedWholeAacPackets']
    s.update(actualOuterExitCode=a.outer_exit,actualExitObserved=True,actualSession=a.session,completionChunk=a.completion,workerDead=True,closureObservedAt=now(),all79ProtectedInputsUnchanged=True,repairCandidateUnchanged=True,closureCimActual=cim)
    cp = read(O/'latest-checkpoint.json'); cp.update(recordedAt=now(),stage=s['status']+'-actual-closed',activeOwnedWorkers=0,ownedJob=None,next='Fresh resource, then inspect new final changed06a samples and37 cut boundaries; preserve approved unchanged36 evidence; explicit main promotion,4outputs,private settings,Git and current schedule replacement remain pending.'); save(O/'latest-checkpoint.json',cp)
    qp = B/'queue.json'; old = qp.read_bytes(); q = read(qp); q['currentOrientationReview'].update(stage=cp['stage'],activeOwnedWorkers=0,ownedJob=None,next=cp['next']);q['updatedAt'] = now();assert qp.read_bytes() == old;save(qp,q)
save(sp,s)
print(json.dumps(dict(session=a.session,alive=alive,registered=a.outer_exit is None,outerExit=a.outer_exit)))
