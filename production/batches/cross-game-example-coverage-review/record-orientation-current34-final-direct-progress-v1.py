"""Record explicitly read final boards; keep final approval false until complete review."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
now=lambda:datetime.now(timezone.utc).isoformat()
def save(p,v):
 t=p.with_name(p.name+'.direct-writing');t.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
ap=argparse.ArgumentParser();ap.add_argument('--first-board',type=int,required=True);ap.add_argument('--last-board',type=int,required=True);ap.add_argument('--note',required=True);a=ap.parse_args()
sp=O/'current34-pair-pixel-execution-v2.json';s=read(sp);assert s['actualOuterExitCode']==0 and s['workerDead']
pairp=O/'current34-final-pair-execution-v3.json';pair=read(pairp);assert pair['actualOuterExitCode']==0 and pair['workerDead']
row=s['results'][0];assert len(row['samples'])==3168 and len(row['boards'])==792
proof=read(O/'narration-07b-guide-repair-execution-v1.json')
for x in proof['protectedInputs']+proof['results']:assert sha(ROOT/x['path'])==x['sha256']
p=O/'current34-final-pixels-partial-direct-review-v1.json'
if p.exists():
 d=read(p);assert d['pixelExecutionSha256']==sha(sp) and d['pairExecutionSha256']==sha(pairp)
else:
 d=dict(recordedAt=now(),pixelExecution=rel(sp),pixelExecutionSha256=sha(sp),pairExecution=rel(pairp),pairExecutionSha256=sha(pairp),captionedVideo=row['video'],captionedVideoSha256=row['videoSha256'],totalSamples=3168,totalBoards=792,chunks=[],reviewedBoards=[],reviewedSamples=[],all244CuePixelsApproved=False,allFinalSelectedSamplesApproved=False,allIntermediateFramesApproved=False,humanListeningApproved=False,humanPronunciationApproved=False,publicRightsApproved=False)
assert a.first_board==len(d['reviewedBoards'])+1 and a.first_board<=a.last_board<=792
boards=row['boards'][a.first_board-1:a.last_board];samples=row['samples'][(a.first_board-1)*4:a.last_board*4]
for x in boards+samples:assert sha(ROOT/x['path'])==x['sha256']
d['chunks'].append(dict(recordedAt=now(),firstBoard=a.first_board,lastBoard=a.last_board,firstSample=(a.first_board-1)*4+1,lastSample=a.last_board*4,observations=a.note,boundedSelectedPixelsReviewed=True))
d['reviewedBoards'].extend(boards);d['reviewedSamples'].extend(samples);d.update(recordedAt=now(),boardsDirectlyRead=len(d['reviewedBoards']),samplesDirectlyRead=len(d['reviewedSamples']),nextBoard=a.last_board+1,all79ProtectedUnchanged=True,repairCandidateUnchanged=True)
save(p,d)
if a.first_board==1:
 bp=O/'current34-branding-pixel-execution-v3.json';bs=read(bp);assert bs['actualOuterExitCode']==0 and bs['workerDead'];br=bs['results'][0]
 for x in br['samples']+br['boards']:assert sha(ROOT/x['path'])==x['sha256']
 bout=O/'current34-branding-supplement-direct-review-v3.json';assert not bout.exists()
 save(bout,dict(recordedAt=now(),execution=rel(bp),executionSha256=sha(bp),actualOuterExitCode=0,workerDead=True,samples=br['samples'],boards=br['boards'],all3SamplesDirectlyRead=True,observations='Original cat-logo branding and 얌얌코딩 at exact frames30/60/90 are readable and preserved. No added narration caption over branding in these samples. These three selected pixels supplement the final audit, not every intro frame.',allIntermediateFramesApproved=False))
cp=read(O/'latest-checkpoint.json');cp.update(recordedAt=now(),stage='current34-final-pixels-partial-direct-review',activeOwnedWorkers=0,ownedJob=None,finalPixelPartialReview=rel(p),finalBoardsDirectlyRead=d['boardsDirectlyRead'],finalSamplesDirectlyRead=d['samplesDirectlyRead'],next=f"Continue final direct pixel review at board{d['nextBoard']:03d}; do not rerun completed render/extraction/audio. Final QA, promotion, four outputs and publishing remain pending.");save(O/'latest-checkpoint.json',cp)
qp=B/'queue.json';raw=qp.read_bytes();q=read(qp);q['currentOrientationReview'].update(stage=cp['stage'],activeOwnedWorkers=0,ownedJob=None,finalPixelPartialReview=rel(p),finalBoardsDirectlyRead=d['boardsDirectlyRead'],finalSamplesDirectlyRead=d['samplesDirectlyRead'],next=cp['next']);q['updatedAt']=now();assert qp.read_bytes()==raw;save(qp,q)
print(json.dumps(dict(boards=d['boardsDirectlyRead'],samples=d['samplesDirectlyRead'],nextBoard=d['nextBoard'],finalApproved=False)))
