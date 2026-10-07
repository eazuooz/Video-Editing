"""Record an explicitly completed direct read; never promotes encoded-pixel QA."""
from pathlib import Path
import json,sys,hashlib,datetime,re
ROOT=Path(__file__).resolve().parents[3]
slug=sys.argv[1]; count=int(sys.argv[2]); findings=sys.argv[3:]
revision='v1'
for a in findings[:]:
 if a.startswith('--revision='):revision=a.split('=',1)[1];findings.remove(a)
if not re.fullmatch(r'v[1-9][0-9]*',revision):raise RuntimeError('Explicit reviewed revision required')
folder=ROOT/'projects'/slug/'production/visual-depth-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
index=read(folder/f'white-preflight-{revision}-local/index.json')
execution=read(folder/f'white-lookdev-execution-{revision}.json')
source=ROOT/'motion-canvas/src/projects'/slug/'depth-explanations-v1.tsx'
if len(index['boards'])!=count or not findings:raise RuntimeError('Exact directly read board count and observations required')
if any(row['sourceSha256']!=sha(source) for row in execution['completed']):raise RuntimeError('Source changed since samples')
records=[]
for board in index['boards']:
 p=ROOT/board['path'];records.append(dict(path=board['path'],sha256=sha(p),frames=[dict(path=(p.parent/n).relative_to(ROOT).as_posix(),sha256=sha(p.parent/n)) for n in board['frames']]))
result=dict(reviewedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),slug=slug,sourceSha256=sha(source),sharedGeometrySha256=sha(ROOT/'motion-canvas/src/shared/depth-diagrams.tsx'),preflightPixelsApproved=True,boardsDirectlyRead=count,framesDirectlyRead=index['frames'],boards=records,observations=findings,scope='Authored CPU Canvas preflight samples only; exact encoded white and final captioned pixels still pending',selectedWhitePixelsApproved=False,allFinalPixelsReviewed=False)
result['revision']=revision
if revision!='v1':
 overlay=read(folder/f'white-caption-preflight-{revision}-local/index.json')
 if overlay['sourceSha256']!=sha(source) or overlay['frames']!=index['frames']:raise RuntimeError('Current exact ASS overlay coverage required')
 result['captionedPreflight']=dict(index=f'white-caption-preflight-{revision}-local/index.json',indexSha256=sha(folder/f'white-caption-preflight-{revision}-local/index.json'),boardsDirectlyRead=len(overlay['boards']),framesDirectlyRead=overlay['frames'])
 old=folder/'white-preflight-direct-review.json';history=folder/'white-preflight-direct-review-pre-caption-safe.json'
 if old.exists() and not history.exists():history.write_bytes(old.read_bytes())
(folder/'white-preflight-direct-review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(slug=slug,preflightApproved=True,boards=count,frames=index['frames'],encodedFinalApproved=False)))
