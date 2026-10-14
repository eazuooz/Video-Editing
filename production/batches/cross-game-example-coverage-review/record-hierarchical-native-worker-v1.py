"""Register/close the actual candidate extraction, preserving the original source QA."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import os
import psutil

ROOT=Path(__file__).resolve().parents[3]
V=ROOT/'projects/hierarchical-game-outlines/revision-teaching-clarity-v1'
B=ROOT/'production/batches/cross-game-example-coverage-review'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def save(p,o):
    t=p.with_name(p.name+'.'+str(os.getpid())+'.writing')
    t.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=['register','closed'],required=True)
ap.add_argument('--session',type=int,required=True);ap.add_argument('--chunk',required=True)
ap.add_argument('--outer-exit',type=int);a=ap.parse_args()
state_path=V/'native-candidate-extraction-execution-v1.json'
sidecar=V/'native-candidate-extraction-execution-v1.session.json'
state=read(state_path);identity=state['worker'];alive=False
try:
    p=psutil.Process(identity['pid']);alive=abs(p.create_time()-identity['createTime'])<.02
    if alive:assert p.cmdline()==identity['command'] and p.cwd()==identity['cwd']
except psutil.NoSuchProcess:pass
stamp=datetime.now(timezone.utc).isoformat()
if a.mode=='register':
    assert not sidecar.exists()
    record=dict(actualSession=a.session,initialShellChunk=a.chunk,registeredAt=stamp,
        exactWorker=identity,workerAliveAtRegistration=alive,actualOuterExitCode=None)
else:
    record=read(sidecar);assert record['actualSession']==a.session and record['actualOuterExitCode'] is None
    assert a.outer_exit is not None and not alive
    for child in state['children']:
        try:assert abs(psutil.Process(child['pid']).create_time()-child['createTime'])>.02
        except psutil.NoSuchProcess:pass
    if a.outer_exit==0:
        assert state['status']=='completed-awaiting-direct-review'
        assert state['sampleCount']==371 and state['boardCount']==64
        for group in state['groups']:
            index_path=ROOT/group['indexPath'];assert sha(index_path)==group['indexSha256']
            index=read(index_path)
            for item in index['samples']+index['boards']:assert sha(ROOT/item['path'])==item['sha256']
    for item in read(V/'baseline-preservation-v1.json')['protectedInputs']:
        assert sha(ROOT/item['path'])==item['sha256'],item['path']
    record.update(actualOuterExitCode=a.outer_exit,completionShellChunk=a.chunk,closedAt=stamp,
        exactWorkerDead=True,exactChildrenDead=True,all49ProtectedInputsShaIdentical=True,
        sampleCount=state['sampleCount'],boardCount=state['boardCount'],directPixelReviewApproved=False,
        normalPlaybackApproved=False,newGitImages=0)
    state.update(actualOuterSession=a.session,actualOuterExitCode=a.outer_exit,workerClosedAt=stamp)
    save(state_path,state)
save(sidecar,record)
qpath=B/'queue.json';raw=qpath.read_bytes();q=read(qpath)
q['currentHierarchicalReview']['nativeCandidateActualSession']=dict(session=a.session,
    sidecar=sidecar.relative_to(ROOT).as_posix(),actualOuterExitCode=record['actualOuterExitCode'])
if a.mode=='closed':
    q['currentHierarchicalReview'].update(ownedJob=None,stage='native-candidate-worker-closed;direct-source-review-next')
    cp_path=V/'latest-checkpoint.json';cp=read(cp_path)
    cp.update(recordedAt=stamp,stage='native-candidate-pixels-extracted;direct-review-and-cut-selection-next',
        activeOwnedWorkers=0,nativeExecution=state_path.relative_to(ROOT).as_posix(),
        actualNativeOuterSession=a.session,actualNativeOuterExitCode=a.outer_exit,
        next='Do not reacquire/decode/extract completed candidates. Read64new boards/371native samples once, selected full-resolution detail as needed, and current normal1x playback before independent causal KOEN additions. Preserve original12PCM/60paragraphs/14pieces/white/Nimbus/Oct14 reservation; both deletion questions remain pending without repetition.')
    save(cp_path,cp);q.update(next=cp['next'])
assert qpath.read_bytes()==raw;save(qpath,q)
print(json.dumps(dict(mode=a.mode,session=a.session,workerAlive=alive,
    actualOuterExitCode=record['actualOuterExitCode'],completedGroups=len(state['groups']))))
