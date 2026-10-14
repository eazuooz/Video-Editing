"""Seal directly read contexts101--130, retaining the first100 SHA-bound review."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json
ROOT = Path(__file__).resolve().parents[3]
O = ROOT / 'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
out = O / 'current34-mixed-context-partial-direct-review-v3.json'
assert not out.exists()
prior = read(O / 'current34-mixed-context-partial-direct-review-v2.json')
s = read(O / 'current34-mixed-contexts-asr-execution-v1.json')
assert prior['reviewedCount'] == 100 and len(s['results']) >= 130
rows = list(prior['rows'])
for r in rows:
    assert sha(ROOT / r['resultPath']) == r['resultSha256']
for i, r in enumerate(s['results'][100:130], 101):
    path = O / 'current34-mixed-contexts-asr-v1' / (r['id'] + '.json')
    assert read(path) == r
    rows.append(dict(index=i, id=r['id'], expectedKo=r['expectedKo'], currentText=r['text'],
        resultPath=path.relative_to(ROOT).as_posix(), resultSha256=sha(path),
        fullExpectedAndCurrentDirectlyRead=True, firstThreeAndLastThreeWordsDirectlyRead=True,
        readEvidence='260d3c'))
notes = {**prior['recognitionNotes'],
    '13a-p02': '자가/차가 recognizer alternative; ruler analogy and deformation result preserved in raw PCM and the surrounding context.',
    '13-p03': '전치/전체 recognizer alternative; R-transpose times R inspection remains an exact script/formula contract, not exact pronunciation approval.',
    '16-p04': '정규화/정교화 alternatives twice. Original PCM and current placement are byte-exact; do not claim every term recognized or human pronunciation approved.'}
data = dict(recordedAt=datetime.now(timezone.utc).isoformat(), reviewedCount=130, total=180,
    priorReview='projects/game-math-orientation-matrices/revision-teaching-clarity-v1/current34-mixed-context-partial-direct-review-v2.json',
    rows=rows, recognitionNotes=notes, all180Reviewed=False, allExpectedWordsRecognized=False,
    currentMixedAudioApproved=False, humanListeningApproved=False, humanPronunciationApproved=False,
    timingLimit=prior['timingLimit'], sourceAacSha256=s['mixAacSha256'], decodedAacSha256=s['decodedAacSha256'])
out.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', 'utf-8')
print(json.dumps(dict(sealedPartial=130, all180=False, noTtsRetry=True)))
