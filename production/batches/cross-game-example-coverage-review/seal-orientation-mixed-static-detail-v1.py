"""Seal directly inspected static candidates only; no moving/final approval."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
ROOT=Path(__file__).resolve().parents[3]
O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=O/'current34-mixed-detailed-subject-replacement-plan-v4.json';plan=json.loads(p.read_text('utf-8-sig'))
assert sha(ROOT/plan['editableModule'])==plan['editableModuleSha256']
for x in plan['preparedSamples']+plan['preparedBoards']:assert sha(ROOT/x['path'])==x['sha256']
assert len(plan['preparedSamples'])==18
out=O/'current34-mixed-detailed-static-direct-review-v1.json';assert not out.exists()
out.write_text(json.dumps(dict(recordedAt=datetime.now(timezone.utc).isoformat(),plan=p.relative_to(ROOT).as_posix(),planSha256=sha(p),samples=plan['preparedSamples'],all18CurrentStaticSamplesDirectlyRead=True,currentBoards=plan['preparedBoards'],allCurrentStaticBoardsDirectlyRead=True,priorGoodStaticSamplesReused=10,clearance='V1 late arrow/footer conflicts, V2 header margin and V3 wingtip/formula proximity are preserved as static held history. V4 framing separates header/formula/footer and reserved fixed-caption area in directly read samples.',subjects='03b readable rider face/helmet, bent clothed limbs/gloves/shoes and frame/fork/tires/spokes/drivetrain;07b cockpit/glass,swept wings,engines/tail;10b same aircraft and mechanically differentiated pad,mount,shaft,cylinders,pivots,bolts,hose.',rotationAndRevealContractReviewed=True,staticIllustrativeSubjectDetailApproved=True,movingRenderApproved=False,allInterveningFramesReviewed=False,final244CaptionPixelsApproved=False,newImageGit=0),ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(staticSamples=18,moving=False,finalPixels=False,review=out.relative_to(ROOT).as_posix())))
