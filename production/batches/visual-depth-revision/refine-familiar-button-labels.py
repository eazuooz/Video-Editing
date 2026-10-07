from pathlib import Path
import json,hashlib,datetime
ROOT=Path(__file__).resolve().parents[3]
folder=ROOT/'projects/familiar-game-rules/production/visual-depth-v1'
source=ROOT/'motion-canvas/src/projects/familiar-game-rules/depth-explanations-v1.tsx'
history=folder/'depth-explanations-caption-safe-v3.tsx'
if history.exists():raise RuntimeError('Preserve prior correction; inspect rather than repeat')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
s=source.read_text('utf-8-sig');changes={
 's.label(name,x,y,160,29)':'s.label(name,x,y,135,29)',
 "text('같은 역할의 연결',-450,-170":"text('같은 역할의 연결',-450,-232",
 "text('가상의 재배치 예시',-450,-170":"text('가상의 재배치 예시',-450,-232",
 "text('단순 버튼 상태',-450,-170":"text('단순 버튼 상태',-450,-232",
 'y={-255} fill={P.blue}':'y={-272} fill={P.blue}',
}
for a in changes:
 if s.count(a)!=1:raise RuntimeError('Exact project-local source match required: '+a)
history.write_bytes(source.read_bytes())
for a,b in changes.items():s=s.replace(a,b)
source.write_text(s,'utf-8')
record=folder/'caption-safe-repair-request.json';r=json.loads(record.read_text('utf-8-sig'))
review=dict(reviewedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),revision='v3',sourceSha256=sha(history),rawBoardsDirectlyRead=12,rawFramesDirectlyRead=67,captionBoardsDirectlyRead=0,preflightPixelsApproved=False,allFinalPixelsReviewed=False,observations=['All 12 raw v3 boards directly read. Chapter03 input label intersects left comparison title; chapter05 input1 label overlaps virtual remapping title.','Move only labels and their three comparison titles, and open the phase-line gap. Retain all literal words, geometry, narration, timing and fixed captions. Actual-ASS v3 boards were generated but are not claimed read.'],changes=changes)
(folder/'white-v3-preflight-direct-rejection.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n','utf-8')
r.update(revision='v4',sourceSha256=sha(source),preflightPixelsApproved=False,allFinalPixelsReviewed=False,buttonLabelRefinement=dict(previousSource=history.relative_to(ROOT).as_posix(),previousSourceSha256=sha(history),changes=changes,reason='Direct raw samples show input/title collisions during camera yaw'))
record.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n','utf-8')
print('Familiar v4 label spacing prepared; preflight and final approval remain false')
