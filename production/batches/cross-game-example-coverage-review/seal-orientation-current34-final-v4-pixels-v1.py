"""Seal only newly displayed V4 pixels; preserve exact cached prior-pixel evidence."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
rd=lambda p:json.loads(p.read_text('utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for buf in iter(lambda:f.read(1048576),b''):h.update(buf)
 return h.hexdigest()
def save(p,v):
 t=p.with_name(p.name+'.writing');t.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
ap=argparse.ArgumentParser();ap.add_argument('--first',type=int,required=True);ap.add_argument('--last',type=int,required=True);ap.add_argument('--observation',required=True);a=ap.parse_args()
sp=O/'current34-pair-pixel-execution-v3.json';s=rd(sp);assert s['workerDead'] and s['actualOuterExitCode']==0
x=s['results'][0];samples=x['directReviewSamples'];boards=x['boards'];assert len(samples)==818 and len(boards)==205 and len(x['inheritedExactPixelSamples'])==2352
rp=O/'current34-final-v4-pixels-partial-direct-review-v1.json'
if rp.exists():r=rd(rp);assert r['executionSha256']==sha(sp)
else:r=dict(recordedAt=datetime.now(timezone.utc).isoformat(),execution=sp.relative_to(ROOT).as_posix(),executionSha256=sha(sp),pairExecution=s['pairExecution'],pairExecutionSha256=s['pairExecutionSha256'],captionedVideo=x['video'],captionedVideoSha256=x['videoSha256'],totalSelectedSamples=len(x['samples']),totalNewDirectSamples=len(samples),totalNewDirectBoards=len(boards),inheritedExactPixelSampleCount=2352,priorCompleteReview=s['priorCompleteReview'],priorCompleteReviewSha256=s['priorCompleteReviewSha256'],chunks=[],reviewedBoards=[],reviewedSamples=[],boardsDirectlyRead=0,samplesDirectlyRead=0,nextBoard=1,allNewDirectPixelsRead=False,all244CuePixelsApproved=False,allFinalSelectedSamplesApproved=False,allIntermediateFramesApproved=False,humanListeningApproved=False,publicRightsApproved=False,scope='New actual assembled V4 output;2352 cached prior pixels inherited only through exact RGB comparison;818 new differing/repair/cut/branding samples require direct reading. No prior review redisplay.')
assert a.first==r['nextBoard'] and a.first<=a.last<=len(boards)
for i in range(a.first-1,a.last):
 board=boards[i];assert sha(ROOT/board['path'])==board['sha256'];r['reviewedBoards'].append(board)
 for sample in samples[i*4:i*4+4]:assert sha(ROOT/sample['path'])==sample['sha256'];r['reviewedSamples'].append(sample)
r['chunks'].append(dict(recordedAt=datetime.now(timezone.utc).isoformat(),firstBoard=a.first,lastBoard=a.last,observation=a.observation,boundedNewSelectedPixelsDirectlyRead=True))
r.update(recordedAt=datetime.now(timezone.utc).isoformat(),boardsDirectlyRead=len(r['reviewedBoards']),samplesDirectlyRead=len(r['reviewedSamples']),nextBoard=a.last+1,allNewDirectPixelsRead=a.last==len(boards));save(rp,r)
cp=rd(O/'latest-checkpoint.json');cp.update(recordedAt=r['recordedAt'],stage='current34-final-v4-new-pixels-direct-review',activeOwnedWorkers=0,ownedJob=None,currentFinalV4PixelReview=rp.relative_to(ROOT).as_posix(),finalV4BoardsReviewed=r['boardsDirectlyRead'],finalV4SamplesReviewed=r['samplesDirectlyRead'],next=('Seal finalV4 pixel/ratio/technical review after actual new normal endpoint; then explicit root backup/promotion and4outputs/private/settings/Git/current09schedule.' if r['allNewDirectPixelsRead'] else f'Continue only new finalV4 direct board{r["nextBoard"]}; cached prior2352 exact pixels are preserved without redisplay; CUA113 normal playback runs once.'));save(O/'latest-checkpoint.json',cp)
qp=B/'queue.json';raw=qp.read_bytes();q=rd(qp);q['currentOrientationReview'].update(stage=cp['stage'],activeOwnedWorkers=0,ownedJob=None,currentFinalV4PixelReview=cp['currentFinalV4PixelReview'],finalV4BoardsReviewed=r['boardsDirectlyRead'],finalV4SamplesReviewed=r['samplesDirectlyRead'],next=cp['next']);q['updatedAt']=r['recordedAt'];assert qp.read_bytes()==raw;save(qp,q)
print(json.dumps(dict(boards=r['boardsDirectlyRead'],samples=r['samplesDirectlyRead'],totalBoards=len(boards),inheritedExact=2352,nextBoard=r['nextBoard'])))
