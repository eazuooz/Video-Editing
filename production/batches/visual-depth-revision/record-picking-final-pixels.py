"""Record completed direct read of both boundary boards plus byte-identical decoded reviewed body."""
from pathlib import Path
import json,hashlib,datetime
ROOT=Path(__file__).resolve().parents[3];folder=ROOT/'projects/picking-sides/production/visual-depth-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
comparison=read(folder/'boundary-pixel-comparison.json');previous=read(folder/'encoded-pixel-direct-review-pre-outro-fix.json');qa=read(folder/'pair-technical-qa.json')
if comparison['changedBodyFrames']!=[36290,36291,36292] or len(comparison['boards'])!=2 or previous['boardsRead']!=100:raise RuntimeError('Exact direct review scope changed')
for board in comparison['boards']:
 if sha(ROOT/board['path'])!=board['sha256']:raise RuntimeError('Directly read board changed')
 for f in board['frames']:
  if sha(ROOT/f['path'])!=f['sha256']:raise RuntimeError('Directly read frame changed')
current=next(o for o in qa['outputs'] if o['variant']=='captioned')
if current['sha256']!=comparison['videoSha256']:raise RuntimeError('Current pair changed')
result=dict(checkedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),videoSha256=current['sha256'],srtSha256=previous['srtSha256'],allFinalPixelsReviewed=True,captionPixelsApproved=True,gameUiPixelsApproved=True,depthMotionApproved=True,memberOuttroPixelsApproved=True,cuesRead=151,gameCutsRead=45,previousDirectlyReadBoards=100,previousDirectlyReadFrames=600,decodedUnchangedBodyFrames=36290,decodedComparison='boundary-pixel-comparison.json',newBoundaryBoardsDirectlyRead=2,newBoundaryFramesDirectlyRead=len(comparison['sampledFrames']),newBoundaryBoards=comparison['boards'],observations=['All first 36290 decoded body frames exactly match the prior directly read 600-sample/100-board pair, preserving all narration cue and gameplay UI checks.','The three encoding-changed last body frames were directly read and show the same legible projected four-question diagram with no misplaced caption.','New encoded outro frame0 now shows the original member image/identities and coaching URL, with no old-PPT flash. Frames1/2/15/30/60/300/599 were directly read; the exact membership title and cat logo remain visible through their original fade.'],humanFullListening='pending',truncatedMemberHandles='pending',privateUploadCompleted=False)
(folder/'encoded-pixel-direct-review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf-8')
fix=read(folder/'outro-boundary-fix.json');fix.update(pixelsPending=False,pixelReview='encoded-pixel-direct-review.json');(folder/'outro-boundary-fix.json').write_text(json.dumps(fix,ensure_ascii=False,indent=2)+'\n','utf-8')
print('Current picking-sides final pixels approved; private upload remains false')
