"""Seal the four directly read source/static samples; no moving approval."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib

ROOT = Path(__file__).resolve().parents[3]
R = ROOT / 'projects/motion-sickness-games/production/revision-cross-game-four-v1'
plan_path = R / 'portal-annotation-observation-plan-v1.json'
plan = json.loads(plan_path.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
rows = []
for row in plan['observations']:
    assert sha(ROOT / row['sourceSample']) == row['sourceSampleSha256']
    assert sha(ROOT / row['staticPath']) == row['staticSha256']
    rows.append({**row, 'sourceAndStaticDirectlyRead': True})
out = R / 'portal-annotation-static-direct-review-v1.json'
assert not out.exists()
proof = dict(schemaVersion=1, reviewedAt=datetime.now(timezone.utc).isoformat(),
    planSha256=sha(plan_path), samples=rows, directStaticClearanceReview=True,
    findings=['Red marker identifies the visible upper cube face, not a physical centroid.',
        'Blue marker identifies a visible wall region; the observed points do not establish a fixed world feature.',
        'Four inspected static labels, credit and leader lines leave the fixed mock caption and cube/device details readable.',
        'Frame1199 is an exclusive endpoint anchor outside the proposed cut.'],
    captionScope='Prepared single mock sentence only; all final narration cues remain unapproved.',
    movingAnnotationApproved=False, narrationTimed=False, finalCueApproval=False,
    allIntermediateFramesReviewed=False, engineWorldAxisClaim=False,
    comfortOutcomeClaim=False, gitImagesAdded=0)
out.write_text(json.dumps(proof, ensure_ascii=False, indent=2)+'\n', 'utf-8')
print('Four source/static observations sealed with matching hashes; moving/final approval false.')
