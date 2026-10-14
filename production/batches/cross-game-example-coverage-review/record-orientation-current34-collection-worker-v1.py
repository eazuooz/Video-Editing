"""Register/close the collector actual process and preserve intentional root transition."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os,psutil
ROOT=Path(__file__).resolve().parents[3];O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
rd=lambda p:json.loads(p.read_text('utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def save(p,v):
 t=p.with_name(p.name+'.writing');t.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
ap=argparse.ArgumentParser();ap.add_argument('--session',type=int);ap.add_argument('--initial');ap.add_argument('--outer-exit',type=int);ap.add_argument('--completion');a=ap.parse_args()
p=O/'current34-output-collection-execution-v1.json';v=rd(p)
try:
 worker=psutil.Process(v['pid']);alive=worker.is_running() and 'collect-orientation-current34-outputs-v1.cjs' in ' '.join(worker.cmdline())
except psutil.NoSuchProcess:alive=False
if a.outer_exit is None:
 assert a.session and a.initial;v.update(actualSession=a.session,initialChunk=a.initial,aliveAtRegistration=alive)
else:
 assert a.completion and not alive and v['exitCode']==a.outer_exit
 promotion=rd(O/'current34-main-promotion-v1.json')
 assert sha(ROOT/promotion['currentMain']['path'])==promotion['currentMain']['sha256']
 for f in promotion['otherProtectedInputs']+promotion['repairCandidates']:assert sha(ROOT/f['path'])==f['sha256']
 if a.outer_exit==0:assert rd(O/'current34-four-output-collection-verification-v1.json')['fourOutputsCollected']
 v.update(actualOuterExitCode=a.outer_exit,completionChunk=a.completion,actualSession=a.session,
    actualExitObserved=True,workerDead=True,closureObservedAt=datetime.now(timezone.utc).isoformat(),
    intentionalMainTransitionVerified=True,other78ProtectedInputsUnchanged=True,repairCandidateUnchanged=True)
save(p,v)
print(json.dumps(dict(session=a.session,outerExit=a.outer_exit,alive=alive)))
