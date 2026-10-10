"""Record directly read boards without granting unfinished review approval."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, argparse
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'projects/game-math-polar-3d/revision-teaching-clarity-v1'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
ap=argparse.ArgumentParser();ap.add_argument('--boards-read',type=int,required=True);args=ap.parse_args()
state=read(OUT/'final-pixel-extraction-execution-v2.json')
assert state['exitCode']==0 and state['boardsCount']==386 and state['samplesCount']==2262
assert 0<args.boards_read<=386
path=OUT/'final-pixel-direct-review-progress-v2.json'
if path.exists():assert read(path)['boardsDirectlyRead']<=args.boards_read
boards=state['boards'][:args.boards_read]
assert all(sha(ROOT/b['path'])==b['sha256'] for b in boards)
v={'schemaVersion':1,'reviewedAt':datetime.now(timezone.utc).isoformat(),
 'sourceSha256':'8b1aacd54034faca55809702ab332e08b80403d32a113b2834e7fa7af867d372',
 'extractionState':'projects/game-math-polar-3d/revision-teaching-clarity-v1/final-pixel-extraction-execution-v2.json',
 'actualOuterExitCode':0,'exitObservedChunk':'0a51b9','processAbsenceObservedChunk':'c558f2',
 'boardsDirectlyRead':args.boards_read,'totalBoards':386,'totalSamples':2262,
 'reviewedBoards':boards,'unresolvedObservedSoFar':[],
 'allListedSamplesDirectlyRead':False,'allFinalCueCutPixelsApproved':False,
 'humanWholeListeningApproved':False,'publicRightsApproved':False,
 'note':'Progress only; every remaining listed board still requires direct reading. Intro/overview/game02 observations are recorded in the review session; fixed captions, current action/labels/UI checked.'}
write(path,v)
qpath=ROOT/'production/batches/unpublished-teaching-clarity-revision/queue.json';q=read(qpath);e=q['execution']
if e.get('heavyJob',{}).get('sessionId')==58791:
    job=e.pop('heavyJob');job.update(actualExitCode=0,actualOuterExitCode=0,exitObservedChunk='0a51b9',processAbsenceObservedChunk='c558f2')
    e['completedJobs'].append(job)
e['stage']='polar-final-cue-cut-pixel-direct-review-in-progress'
e['finalPixelReviewProgress']={'path':path.relative_to(ROOT).as_posix(),'boardsRead':args.boards_read,'boardsTotal':386,'finalApproval':False}
write(qpath,q)
print(json.dumps({'boardsRead':args.boards_read,'remaining':386-args.boards_read,'finalApproved':False}))
