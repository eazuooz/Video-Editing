"""Record explicit reviewed boards, reusing only byte-identical prior reviews."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json
ROOT=Path(__file__).resolve().parents[3]
B=Path(__file__).parent/'revision-balatro60-v2'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ap=argparse.ArgumentParser()
ap.add_argument('--boards',type=int,nargs='+',required=True)
ap.add_argument('--observation',required=True)
a=ap.parse_args()
source=B/'selected-input-preflight-v4.json';d=read(source)
state=read(B/'selected-input-preflight-execution-v4.json')
assert state['exitCode']==state['outerExitCode']==0 and state['outerExitDirectlyObserved']
dest=B/'selected-input-direct-progress-v4.json'
old=read(dest) if dest.exists() else None
numbers=set(old['directlyReadBoardNumbers']) if old else set()
observations=old['observations'] if old else []
inherited=[]
if not old:
 prior=read(B/'selected-input-direct-progress-v3.json')
 observations=prior['observations']+['Prior equality issue is historical. Current source-only correction and exact numeric anchors require explicit v4 review.']
else:
 assert old['sourceSha256']==sha(source)
 inherited=old['inheritedByteIdenticalBoardNumbers']
prior=read(B/'selected-input-direct-progress-v3.json')
for n in prior['directlyReadBoardNumbers']:
 current=d['boards'][n-1];previous=prior['boards'][n-1]
 if n not in numbers and all(current[k]==previous[k] for k in ['path','sha256','sampleFrames']):
  assert current.get('reusedUnchangedCurrentPixels') and sha(ROOT/current['path'])==current['sha256']
  numbers.add(n);inherited.append(n)
for n in a.boards:
 assert 1<=n<=len(d['boards']) and n not in numbers
 numbers.add(n)
boards=[d['boards'][n-1] for n in sorted(numbers)]
frames={v for b in boards for v in b['sampleFrames']}
samples=[s for s in d['samples'] if s['frame'] in frames]
for x in [*boards,*samples]:assert sha(ROOT/x['path'])==x['sha256']
observations.append(a.observation)
complete=len(numbers)==len(d['boards'])
progress=dict(schemaVersion=4,reviewedAt=datetime.now(timezone.utc).isoformat(),
 source=source.relative_to(ROOT).as_posix(),sourceSha256=sha(source),planSha256=d['planSha256'],
 captionCandidateSha256=d['captionCandidateSha256'],bodySha256=d['bodySha256'],
 directlyReadBoardNumbers=sorted(numbers),directlyReadBoardCount=len(numbers),totalBoards=len(d['boards']),
 directlyReadSampleCount=len(samples),totalSamples=len(d['samples']),boards=boards,
 inheritedByteIdenticalBoardNumbers=inherited,observations=observations,unresolvedIssues=[],
 equalityCorrectionDirectlyReviewed=all(n in numbers for n in [19,20,21,22,23,24,25,26,118,119]),
 allBoardsDirectlyRead=complete,allInputCaptionPixelsReviewed=complete,allFinalPixels=False,
 finalMixedAsrApproved=False,qa=False,collected=False,private=False,
 scope='Explicitly listed current cue/cut/clause/spatial-motion samples. Byte-identical prior samples retain direct review. Not every continuous native frame, final pair or human listening.',
 localOnly=True,imagesGitAdded=0)
dest.write_text(json.dumps(progress,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(boards=len(numbers),totalBoards=len(d['boards']),samples=len(samples),totalSamples=len(d['samples']),complete=complete)))
