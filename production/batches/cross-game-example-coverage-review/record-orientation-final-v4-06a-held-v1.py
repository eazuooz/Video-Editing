"""Record the new actual V4 boundary finding before any additional render."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
ROOT=Path(__file__).resolve().parents[3];O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
rd=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sp=O/'current34-pair-pixel-execution-v3.json';s=rd(sp);assert s['workerDead'] and s['actualOuterExitCode']==0
x=next(x for x in s['results'][0]['samples'] if x['frame']==14232);assert sha(ROOT/x['path'])==x['sha256']
out=O/'current34-final-v4-additional-clearance-findings-v1.json';assert not out.exists()
r=dict(recordedAt=datetime.now(timezone.utc).isoformat(),state='held-additional-06a-label-clearance',pairExecution=s['pairExecution'],pairExecutionSha256=s['pairExecutionSha256'],pixelExecution=sp.relative_to(ROOT).as_posix(),pixelExecutionSha256=sha(sp),
 findings=[dict(id='ex06a-body-axes-label-caption-contact',scene='06a',confirmedAtAbsoluteFrame=14232,severity='requires_repair',proof=dict(path=x['path'],sha256=x['sha256'],originalResolutionDirectlyRead=True),observations='At the actual assembled scene start, the lower-right part of the blue label 몸에 붙인 세 축 meets and is partly covered by the top-left border of the two-line fixed caption. The last 축 lower stroke is obscured.',requiredRepair='Raise only the lower axis legend/body-axis label using the reserved-area adjustment already reviewed for09a/13a/16a/21a. Preserve the aircraft, math, sequence, timing, narration, palette and ratio. Review this newly repaired scene and final captioned bindings.',repairCompleted=False)],
 allFinalSelectedSamplesApproved=False,all244CuePixelsApproved=False,humanListeningApproved=False,next='Continue remaining new finalV4 direct pixels before consolidating additional targeted repair; do not repeat completed7 repair renders or557 current-caption binding review.')
out.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(finding=out.relative_to(ROOT).as_posix(),sha256=sha(out),heldFrame=14232)))
