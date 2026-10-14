"""Record the five CUA-observed, normally played corrected input clips."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib
R = Path(__file__).resolve().parents[3]
P = R / 'projects/game-lighting-history-04/production'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
rp = P / 'part1-corrected-moving-review-request-v257.json'
request = read(rp)
observations = {
    'horizon-detail-motion:native': 'CUA tab69 played0–5.683333s at rate1 and stopped at the actual end. Original CNN/New Transformer labels and the green comparison divider remain visible. At the enlarged embroidery endpoint, red/teal rectangles enclose the corresponding bag patches; the upper Korean observation label stays above them. Actual Aloy motion and bag-detail comparison remain visible.',
    'outer-displayed-frames:native': 'CUA tab69 played0–16.333333s at rate1 and stopped at the actual end. The center5X/211FPS source card is enclosed initially; the upper-right4X/198FPS and5X/203FPS cards remain fully readable later. The lower matte preserves the upper source FPS. A separate UI seek to2.8s showed the card transition without a stale red rectangle. The Korean label distinguishes displayed FPS from simulation frequency.',
    'cyber-light-reconstruction:native': 'CUA tab69 played0–18.083333s at rate1 and stopped at the actual end. The initial interior action retains its RTX ON badge. Later aimed-weapon motion retains101FPS/DLSS3.5, Full RT On inside the upper-right red observation rectangle; RTX ON remains unobscured at the lower right. The Korean condition label explicitly describes bundled conditions, not an isolated feature-speed measurement.',
    'cyber-surface-observation:native': 'CUA tab69 played0–25.133333s at rate1 and stopped at the actual end. The wet street and later split surface comparisons retain their original RTX and DLSS Off/DLSS3.5 labels, vertical comparison divider and moving street surfaces. The upper matte removes the old irrelevant top material while preserving the lower feature conditions. The final wet-reflection view remains visible on both halves; narration identifies surface-light differences rather than disappearing geometry.',
    'fortnite-mobile-test:native': 'CUA tab69 played0–19s at rate1 and stopped at the actual end. The phone gameplay view shows the character/camera traversing material rocks with quality labels and a left diagnostic graph. The red rectangle encloses the graph and excludes the lower-left joystick. The Korean graph/surface distinction stays above the action; original device-interface controls and diagnostic values remain visible.'
}
assert set(observations) == {r['id'] for r in request['rows']}
records = []
for row in request['rows']:
    assert sha(R / row['path']) == row['sha256']
    records.append({**row, 'normalSpeedPlaybackDirectlyObserved': True,
                    'fullSelectedIntervalActuallyPlayed': True, 'rate': 1,
                    'movingPixelsApproved': True, 'actualObservation': observations[row['id']]})
record = {'reviewedAt': datetime.now(timezone.utc).isoformat(),
          'method': 'CUA actual encoded inputs, full selected playback at rate1 plus explicit card-transition pixel inspection',
          'requestSha256': sha(rp), 'visualBuildSha256': request['visualBuildSha256'],
          'planSha256': request['planSha256'], 'records': records, 'unresolvedIssues': [],
          'allCorrectedEncodedMovingPixelsReviewed': True, 'allFinalPixelsReviewed': False,
          'finalCaptionPixelsStillSeparate': True, 'qaApproved': False, 'uploaded': False, 'newGitImages': 0}
dest = P / 'part1-corrected-moving-input-direct-review-v257.json'
assert not dest.exists()
dest.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', 'utf-8')
print(json.dumps({'directlyReviewedCorrectedInputs': 5, 'finalCaptionPixelsApproved': False}))
