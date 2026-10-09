"""Record only encoded boards explicitly read in this review."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json
ROOT=Path(__file__).resolve().parents[3]
W=Path(__file__).resolve().parent/'revision-balatro60-v2/final-v3'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ap=argparse.ArgumentParser();ap.add_argument('--through',type=int,required=True);ap.add_argument('--note',required=True);a=ap.parse_args()
ex=read(W/'encoded-caption-qa-execution.json');assert ex['exitCode']==ex['outerExitCode']==0
assert (ex['sampleCount'],ex['boardCount'])==(1112,186)
assert 1<=a.through<=len(ex['boards'])
p=W/'encoded-caption-qa-direct-progress.json';previous=read(p) if p.exists() else {}
assert a.through>=len(previous.get('reviewedBoards',[]))
boards=ex['boards'][:a.through];samples={i for b in boards for i in b['sampleIndices']}
for b in boards:assert sha(ROOT/b['path'])==b['sha256']
for s in ex['samples']:
    if s['index'] in samples:assert sha(ROOT/s['path'])==s['sha256']
result=dict(recordedAt=datetime.now(timezone.utc).isoformat(),sourceSha256=ex['sourceSha256'],
    directlyReadBoards=[b['index'] for b in boards],reviewedSampleIndices=sorted(samples),
    reviewedBoards=[dict(b,directlyRead=True) for b in boards],
    observations=previous.get('observations',[])+[dict(through=a.through,note=a.note)],
    unresolvedPixelDefects=previous.get('unresolvedPixelDefects',[]),allFinalPixels=False,qaApproved=False,
    collected=False,uploaded=False,imagesLocalOnly=True,newGitImages=0)
p.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(directlyReadBoards=a.through,reviewedSamples=len(samples),allFinalPixels=False)))
