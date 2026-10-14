"""Record the actual tool session and, only after actual exit, close its worker."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import os
import psutil

ROOT = Path(__file__).resolve().parents[3]
V = ROOT / 'projects/hierarchical-game-outlines/revision-teaching-clarity-v1'
B = ROOT / 'production/batches/cross-game-example-coverage-review'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):
            h.update(block)
    return h.hexdigest()
def save(p,o):
    t=p.with_name(p.name+'.'+str(os.getpid())+'.writing')
    t.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n','utf-8')
    os.replace(t,p)
ap=argparse.ArgumentParser()
ap.add_argument('--mode',choices=['register','closed'],required=True)
ap.add_argument('--session',type=int,required=True)
ap.add_argument('--chunk',required=True)
ap.add_argument('--outer-exit',type=int)
a=ap.parse_args()
state_path=V/'source-acquisition-execution-v1.json'
sidecar=V/'source-acquisition-execution-v1.session.json'
state=read(state_path)
identity=state['worker']
alive=False
actual=None
try:
    p=psutil.Process(identity['pid'])
    alive=abs(p.create_time()-identity['createTime'])<.02
    if alive:
        actual=dict(pid=p.pid,createTime=p.create_time(),command=p.cmdline(),cwd=p.cwd())
        assert actual['command']==identity['command'] and actual['cwd']==identity['cwd']
except psutil.NoSuchProcess:
    pass
stamp=datetime.now(timezone.utc).isoformat()
if a.mode=='register':
    assert not sidecar.exists(), 'Already registered; reuse the current session'
    record=dict(actualSession=a.session,initialShellChunk=a.chunk,registeredAt=stamp,
        exactWorker=identity,workerAliveAtRegistration=alive,actualCurrentWorker=actual,
        actualOuterExitCode=None,completionShellChunk=None)
    save(sidecar,record)
else:
    record=read(sidecar)
    assert record['actualSession']==a.session and record['actualOuterExitCode'] is None
    assert a.outer_exit is not None and not alive
    child_alive=[]
    for child in state['children']:
        try:
            cp=psutil.Process(child['pid'])
            if abs(cp.create_time()-child['createTime'])<.02:
                child_alive.append(child)
        except psutil.NoSuchProcess:
            pass
    assert not child_alive, child_alive
    preservation=read(V/'baseline-preservation-v1.json')
    for item in preservation['protectedInputs']:
        assert sha(ROOT/item['path'])==item['sha256'],item['path']
    if a.outer_exit==0:
        assert state['status']=='acquired-decoded-awaiting-direct-action-review'
        assert len(state['results'])==3
        for source in state['results']:
            assert sha(ROOT/source['localMediaPath'])==source['fileSha256']
            assert source['wholeDecode']['actualExitCode']==0 and source['wholeDecode']['diagnostics']==0
    record.update(actualOuterExitCode=a.outer_exit,completionShellChunk=a.chunk,closedAt=stamp,
        exactWorkerDead=True,exactChildrenDead=True,protectedInputsShaIdentical=True,
        sourceResultCount=len(state['results']),normalPlaybackApproved=False,
        allIntermediatePixelsApproved=False,humanWholeListeningApproved=False,publicRightsApproved=False)
    save(sidecar,record)
    state.update(actualOuterSession=a.session,actualOuterExitCode=a.outer_exit,
        completionShellChunk=a.chunk,workerClosedAt=stamp)
    save(state_path,state)
qpath=B/'queue.json'
raw=qpath.read_bytes()
q=read(qpath)
q['currentHierarchicalReview']['sourceAcquisitionActualSession']=dict(
    session=a.session,sidecar=sidecar.relative_to(ROOT).as_posix(),actualOuterExitCode=record['actualOuterExitCode'])
if a.mode=='closed':
    q['currentHierarchicalReview'].update(ownedJob=None,stage='source-acquired-and-closed;direct-action-review-pending')
    q['next']='All source acquisition/decode completed. Do not reacquire/decode; inspect the three new candidate sources and native normal1x actions. Continue current duplicate content/Studio review before narration. Preserve baseline jBR Oct14 reservation and both pending obsolete-delete questions.'
    cp_path=V/'latest-checkpoint.json'
    cp=read(cp_path)
    cp.update(recordedAt=stamp,stage='source-candidates-acquired;duplicate-and-native-action-review-next',
        activeOwnedWorkers=0,sourceExecution=state_path.relative_to(ROOT).as_posix(),
        actualSourceOuterSession=a.session,actualSourceOuterExitCode=a.outer_exit,next=q['next'])
    save(cp_path,cp)
assert qpath.read_bytes()==raw
save(qpath,q)
print(json.dumps(dict(mode=a.mode,actualSession=a.session,workerAlive=alive,
    actualOuterExitCode=record['actualOuterExitCode'],sources=len(state['results']))))
