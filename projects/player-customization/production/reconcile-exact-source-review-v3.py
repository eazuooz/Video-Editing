"""Save observed review/hash evidence; never approve final footage or ratio."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os
ROOT=Path(__file__).resolve().parents[3]
BASE=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text('utf-8-sig'))
now=lambda:datetime.now(timezone.utc).isoformat()
def save(p,j):
    t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
p=BASE/'source-bank-exact-pts-direct-progress-v3.json';j=read(p)
assert j['reviewedBoardCount']==j['totalBoardCount']==137 and j['reviewedNativeSamples']==690
paths={}
for b in j['boards']:
    paths[b['path']]=b['sha256']
    for e in b['entries']:paths[e['path']]=e['sha256']
errors=[f for f,s in paths.items() if hashlib.sha256((ROOT/f).read_bytes()).hexdigest()!=s]
assert not errors,errors
j.update(allBoardAndFrameHashesVerified=True,hashVerification={'observedAt':now(),'uniqueFiles':len(paths),'mismatches':0},updatedAt=now())
save(p,j)
cp=read(BASE/'latest-checkpoint.json')
cp.update(stage='all-native-PTS-candidate-boards-read-capacity-and-allocation-pending',recordedAt=now(),sourceExactPtsDirectReview=p.relative_to(ROOT).as_posix(),sourceCandidateBoardsDirectlyRead=True,sourceCandidateHashVerification=j['hashVerification'],nextAction='Allocate only unique clear matched actions. Resolve the actual-action capacity deficit with fresh related developer gameplay, preserving every approved PCM and useful explanation. Final ratio/mix/pair/QA/collection/private remain unapproved.')
cp['ownedJob'].update(status='completed-native-PTS-candidate-extraction',workerExpectedRunning=False,exitCode=0)
save(BASE/'latest-checkpoint.json',cp)
qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qp);i=next(i for i in q['items'] if i['slug']=='player-customization')
i.update(stage=cp['stage'],currentExecution=cp['ownedJob'],sourceExactPtsDirectReview=cp['sourceExactPtsDirectReview'],sourceCandidateBoardsDirectlyRead=True,nextAction=cp['nextAction'])
q['updatedAt']=now();save(qp,q)
print(json.dumps({'uniqueHashFiles':len(paths),'mismatches':0,'boardsRead':137,'finalAllocationApproved':False}))
