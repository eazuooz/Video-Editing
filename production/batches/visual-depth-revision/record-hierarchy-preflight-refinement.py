from pathlib import Path
import json,hashlib,datetime
ROOT=Path(__file__).resolve().parents[3];folder=ROOT/'projects/hierarchical-game-outlines/production/visual-depth-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
record=folder/'caption-safe-repair-request.json';r=json.loads(record.read_text('utf-8-sig'));source=ROOT/r['source'];old=folder/'depth-explanations-caption-safe-v3.tsx'
if old.read_text('utf-8-sig').replace('y={-255} fill={P.blue}','y={-272} fill={P.blue}')!=source.read_text('utf-8-sig'):raise RuntimeError('Exact single phase-line placement correction expected')
review=dict(reviewedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),revision='v3',sourceSha256=sha(old),rawBoardsRead=10,captionBoardsRead=10,rawFramesRead=60,captionFramesRead=60,allFinalPixelsReviewed=False,preflightPixelsApproved=False,observations=['All raw/captioned v3 boards read. Fixed caption/footnote spacing now clear.','Chapter06 small 배치 label comes too close to blue phase sentence during camera yaw. Move only fixed phase sentence from y=-255 to -272; retain literal content, geometry, timeline and captions.'],indices=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in [folder/'white-preflight-v3-local/index.json',folder/'white-caption-preflight-v3-local/index.json']])
(folder/'white-v3-preflight-direct-rejection.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n','utf-8')
r.update(revision='v4',sourceSha256=sha(source),preflightPixelsApproved=False,allFinalPixelsReviewed=False,phaseLineRefinement=dict(oldY=-255,newY=-272,previousSource=old.relative_to(ROOT).as_posix(),previousSourceSha256=sha(old),reason='Direct v3 raw/ASS samples show label proximity during yaw'))
record.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n','utf-8')
