"""Persist only the current boards the operator has actually read."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json
ROOT=Path(__file__).resolve().parents[3]
B=Path(__file__).parent/'revision-balatro60-v2'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ap=argparse.ArgumentParser()
ap.add_argument('--through',type=int,required=True)
ap.add_argument('--observation',action='append',required=True)
ap.add_argument('--issue',action='append',default=[])
a=ap.parse_args()
source=B/'selected-input-preflight-v3.json';d=read(source)
state=read(B/'selected-input-preflight-execution-v3.json')
assert state['exitCode']==state['outerExitCode']==0 and state['outerExitDirectlyObserved']
assert 1<=a.through<=len(d['boards'])
dest=B/'selected-input-direct-progress-v3.json'
old=read(dest) if dest.exists() else None
if old:
 assert old['sourceSha256']==sha(source)
 assert a.through>old['directlyReadBoardCount']
boards=d['boards'][:a.through]
frames={v for b in boards for v in b['sampleFrames']}
samples=[s for s in d['samples'] if s['frame'] in frames]
for x in [*boards,*samples]:assert sha(ROOT/x['path'])==x['sha256']
observations=(old['observations'] if old else [])+a.observation
issues=(old['unresolvedIssues'] if old else [])+a.issue
complete=a.through==len(d['boards']) and not issues
progress=dict(schemaVersion=3,reviewedAt=datetime.now(timezone.utc).isoformat(),
 source=source.relative_to(ROOT).as_posix(),sourceSha256=sha(source),
 planSha256=d['planSha256'],captionCandidateSha256=d['captionCandidateSha256'],
 bodySha256=d['bodySha256'],directlyReadBoardNumbers=list(range(1,a.through+1)),
 directlyReadBoardCount=a.through,totalBoards=len(d['boards']),
 directlyReadSampleCount=len(samples),totalSamples=len(d['samples']),boards=boards,
 observations=observations,unresolvedIssues=issues,allBoardsDirectlyRead=complete,
 allInputCaptionPixelsReviewed=complete,allFinalPixels=False,
 finalMixedAsrApproved=False,qa=False,collected=False,private=False,
 scope='Listed current ASS cue/cut/clause-onset/spatial-motion samples only. Not every native continuous frame or final encoded pair or human listening.',
 localOnly=True,imagesGitAdded=0)
dest.write_text(json.dumps(progress,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(boards=a.through,totalBoards=len(d['boards']),samples=len(samples),totalSamples=len(d['samples']),complete=complete)))
