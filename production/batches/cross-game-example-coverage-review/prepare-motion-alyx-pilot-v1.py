"""Seal six static pixels and prepare one conservative transition pilot."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent;R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
plan=read(R/'alyx-annotation-observation-plan-v3.json')
for x in plan['samples']:assert sha(ROOT/x['staticPath'])==x['staticSha256'] and sha(ROOT/x['path'])==x['sha256']
proof=dict(schemaVersion=1,reviewedAt=datetime.now(timezone.utc).isoformat(),planSha256=sha(R/'alyx-annotation-observation-plan-v3.json'),
    allSixStaticMocksDirectlyRead=True,samples=plan['samples'],
    findings=['Both yellow feet are visible and red outline surrounds their destination UI in all three before-arrival mocks.',
        'ShiftY-180 preserves full boots above fixed906caption top; the curve remains visible above the box.',
        'All post-arrival cyan leaders target actual wall/window trim next to the doorway. Labels and source credit stay readable.',
        'Unknown3063..3069 jump bracket will have no marker and no interpolated path.'],
    boundedStaticRoleAndCaptionClearanceApproved=True,movingAnnotationApproved=False,narrationTimed=False,allFinalPixelsApproved=False,gitImagesAdded=0)
p=R/'alyx-annotation-static-direct-review-v2.json';assert not p.exists();p.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf-8')
print('Six static v2 samples sealed; moving and final narration approval remain false.')
