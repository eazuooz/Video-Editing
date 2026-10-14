"""Retain the first45 review and seal the next55 directly read contexts."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json
ROOT = Path(__file__).resolve().parents[3]
O = ROOT / 'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
out = O / 'current34-mixed-context-partial-direct-review-v2.json'
assert not out.exists()
prior = read(O / 'current34-mixed-context-partial-direct-review-v1.json')
s = read(O / 'current34-mixed-contexts-asr-execution-v1.json')
assert len(s['results']) >= 100 and prior['reviewedCount'] == 45
rows = list(prior['rows'])
for r in rows:
    assert sha(ROOT / r['resultPath']) == r['resultSha256']
for i, r in enumerate(s['results'][45:100], 46):
    path = O / 'current34-mixed-contexts-asr-v1' / (r['id']+'.json')
    assert read(path) == r
    rows.append(dict(index=i, id=r['id'], expectedKo=r['expectedKo'], currentText=r['text'],
        resultPath=path.relative_to(ROOT).as_posix(), resultSha256=sha(path),
        fullExpectedAndCurrentDirectlyRead=True, firstThreeAndLastThreeWordsDirectlyRead=True,
        readEvidence='7d66a6' if i <= 70 else '598afa'))
notes = {**prior['recognitionNotes'],
    '06-p06': '전치하지/전체하지 alternative.',
    '07-p03': '음의 방향/음해방향 alternative; negative axis and (-1,0,0) context remains.',
    '07-p06': '가중합/가중압 alternative; result(-1,2,0) recovered.',
    '07b-p02': '탈것을/다 할 것을 alternative persists; correct device/action context and full ending present.',
    '07b-p06': '화면에/화면의 and 수학/수확 persist; separate90degree example and complete ending present.',
    '09-p02': '정규직교라면/정규직결하면 alternative.',
    '09-p03': '세/새 alternative.',
    '09-p04': '왼쪽에/왼쪽의 particle alternative; inverse numerical result(2,1,0) recovered.',
    '10-p05': '축의/축에 particle alternative; obtains3 world components recovered.',
    '10b-p03': '놓기 전의/전에 particle alternative.',
    '12-p01': '자식 prefix remains unrecognized in independent current AAC; whole used 즉. Original PCM and placements are exact. Do not mark exact pronunciation or every expected word recognized.',
    '12-p03': '곱/cოპ/cop recognizer alternative; B then A and productAB context and ending present.',
    '12-p04': '코드에/코드의 particle alternative.'}
data = dict(recordedAt=datetime.now(timezone.utc).isoformat(), reviewedCount=100, total=180,
    priorReview='projects/game-math-orientation-matrices/revision-teaching-clarity-v1/current34-mixed-context-partial-direct-review-v1.json',
    rows=rows, recognitionNotes=notes, all180Reviewed=False, allExpectedWordsRecognized=False,
    currentMixedAudioApproved=False, humanListeningApproved=False, humanPronunciationApproved=False,
    timingLimit=prior['timingLimit'], sourceAacSha256=s['mixAacSha256'], decodedAacSha256=s['decodedAacSha256'])
out.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', 'utf-8')
print(json.dumps(dict(sealedPartial=100, all180=False, noTtsRetry=True)))
