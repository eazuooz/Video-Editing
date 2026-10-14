"""Attach observed outer completion; verify exact worker death, hashes and protected bytes."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,hashlib,os,psutil
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent;O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):
 t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=['render','pixels'],required=True);ap.add_argument('--session',type=int);ap.add_argument('--outer-exit',type=int,required=True);ap.add_argument('--completion',required=True);a=ap.parse_args()
p=O/f'03b-tracked-{a.mode}-execution-v1.json';s=read(p);assert not s.get('actualExitObserved')
assert not psutil.pid_exists(s['pid'])
if a.mode=='render':
 assert not psutil.pid_exists(s['encodePid'])
 for x in s['decoders']:assert not psutil.pid_exists(x['pid'])
 assert sha(ROOT/s['output'])==s['outputSha256']
 reg=read(p.with_name(p.name.replace('.json','.session.json')));assert reg['actualSession']==a.session
else:
 assert not psutil.pid_exists(s['ffmpegPid'])
 for x in s['samples']+s['boards']:assert sha(ROOT/x['path'])==x['sha256']
t=read(O/'narration-07b-guide-repair-execution-v1.json')
for x in t['protectedInputs']+t['results']:assert sha(ROOT/x['path'])==x['sha256']
assert s['workerExitCode']==a.outer_exit==0
s.update(actualExitObserved=True,actualOuterExitCode=a.outer_exit,actualSession=a.session,actualShellReturnedNoSession=a.session is None,actualCompletion=a.completion,workerDead=True,protectedShaMatched=True,closedAt=datetime.now(timezone.utc).isoformat());save(p,s)
cp=read(O/'latest-checkpoint.json');cp.update(recordedAt=s['closedAt'],activeOwnedWorkers=0,ownedJob=None,stage=s['status']);cp['tracked03b'+('Render' if a.mode=='render' else 'PixelExecution')]=p.relative_to(ROOT).as_posix();save(O/'latest-checkpoint.json',cp)
qp=B/'queue.json';before=qp.read_bytes();q=read(qp);q['currentOrientationReview'].update(stage=s['status'],activeOwnedWorkers=0,ownedJob=None);q['currentOrientationReview']['tracked03b'+('Render' if a.mode=='render' else 'PixelExecution')]=p.relative_to(ROOT).as_posix();q['updatedAt']=s['closedAt'];assert before==qp.read_bytes();save(qp,q)
print(json.dumps(dict(mode=a.mode,session=a.session,outerExit=a.outer_exit,workerDead=True,protected=len(t['protectedInputs']))))
