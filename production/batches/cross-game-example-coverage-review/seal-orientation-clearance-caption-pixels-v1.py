"""Seal only new captioned boards actually read; retain the completed finalV3 review."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, os
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
sp=O/'current34-clearance-caption-bindings-execution-v1.json';s=rd(sp)
assert s['workerDead'] and s['actualOuterExitCode']==0 and len(s['scenes'])==8
boards=[]
for scene in s['scenes']:
 for i,board in enumerate(scene['boards']):
  boards.append(dict(scene=scene['id'],**board,samples=scene['samples'][i*4:i*4+4]))
rp=O/'current34-clearance-caption-pixels-partial-direct-review-v1.json'
if rp.exists():r=rd(rp);assert r['executionSha256']==sha(sp)
else:r=dict(recordedAt=datetime.now(timezone.utc).isoformat(),execution=sp.relative_to(ROOT).as_posix(),executionSha256=sha(sp),totalBoards=len(boards),totalSamples=sum(len(v['samples']) for v in s['scenes']),chunks=[],reviewedBoards=[],reviewedSamples=[],boardsDirectlyRead=0,samplesDirectlyRead=0,nextBoard=1,allSelectedPixelsDirectlyRead=False,allIntermediateFramesApproved=False,humanListeningApproved=False,final244PixelsApproved=False,scope='New eight-scene current-caption bindings only; all completed3168 finalV3 samples retained as historical source approval. Final assembled changed pixels remain pending.')
assert a.first==r['nextBoard'] and a.first<=a.last<=len(boards)
for board in boards[a.first-1:a.last]:
 assert sha(ROOT/board['path'])==board['sha256']
 for sample in board['samples']:assert sha(ROOT/sample['path'])==sample['sha256']
 r['reviewedBoards'].append(dict(scene=board['scene'],path=board['path'],sha256=board['sha256']))
 r['reviewedSamples'].extend(dict(scene=board['scene'],**v) for v in board['samples'])
r['chunks'].append(dict(recordedAt=datetime.now(timezone.utc).isoformat(),firstBoard=a.first,lastBoard=a.last,observation=a.observation,boundedSelectedPixelsDirectlyRead=True))
r.update(boardsDirectlyRead=len(r['reviewedBoards']),samplesDirectlyRead=len(r['reviewedSamples']),nextBoard=a.last+1,allSelectedPixelsDirectlyRead=a.last==len(boards),recordedAt=datetime.now(timezone.utc).isoformat());save(rp,r)
cp=rd(O/'latest-checkpoint.json');cp.update(recordedAt=r['recordedAt'],stage='new-eight-current-caption-pixels-direct-review',clearanceCaptionPixelReview=rp.relative_to(ROOT).as_posix(),clearanceCaptionBoardsReviewed=r['boardsDirectlyRead'],clearanceCaptionSamplesReviewed=r['samplesDirectlyRead'],activeOwnedWorkers=0,ownedJob=None,next=('Complete07b current-caption normal playback and bind reviewed eight repairs into finalV4; review actual final changed pixels/cuts before promotion.' if r['allSelectedPixelsDirectlyRead'] else f'Continue new clearance-caption board{r["nextBoard"]}; never repeat completed3168 finalV3 samples or completed210 silent repair samples.'));save(O/'latest-checkpoint.json',cp)
qp=B/'queue.json';raw=qp.read_bytes();q=rd(qp);q['currentOrientationReview'].update(stage=cp['stage'],clearanceCaptionPixelReview=cp['clearanceCaptionPixelReview'],clearanceCaptionBoardsReviewed=r['boardsDirectlyRead'],clearanceCaptionSamplesReviewed=r['samplesDirectlyRead'],next=cp['next']);q['updatedAt']=r['recordedAt'];assert qp.read_bytes()==raw;save(qp,q)
print(json.dumps(dict(boards=r['boardsDirectlyRead'],samples=r['samplesDirectlyRead'],totalBoards=len(boards),allSelected=r['allSelectedPixelsDirectlyRead'],nextBoard=r['nextBoard'])))
