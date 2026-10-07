"""Record the six source-boundary boards directly read before this correction."""
from pathlib import Path
import json,hashlib,datetime
ROOT=Path(__file__).resolve().parents[3]
slugs=['motion-sickness-games','hierarchical-game-outlines','game-reward-planning','avoid-game-comparisons','making-game-sequels','familiar-game-rules']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for slug in slugs:
 folder=ROOT/'projects'/slug/'production/visual-depth-v1'
 index=json.loads((folder/'source-outro-preflight-local/index.json').read_text('utf-8-sig'))
 if sha(ROOT/index['source'])!=index['sourceSha256'] or sha(ROOT/index['board'])!=index['boardSha256']:raise RuntimeError('Directly read source or board changed')
 target=folder/'source-outro-direct-review.json'
 if target.exists():raise RuntimeError('Preserve prior review')
 motion=slug=='motion-sickness-games'
 result=dict(index)
 result.update(reviewedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),directlyRead=True,framesDirectlyRead=index['frames'],oldPptFirstFrameObserved=motion,requiresBoundaryCorrection=motion,observations=['Source frames 0,1,2,15,30,60 directly read.','Old flat explanation at frame0; actual original member identities visible from frame1, with exact thank-you title during fade.' if motion else 'Member identities present from frame0; no old explanation flash at these boundary frames. Preserve original source.','Original profile/name/badge rows and channel cat retained; truncated handles remain pending.'],allFinalPixelsReviewed=False)
 target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(slug+' source boundary reviewed; correction='+str(motion))
