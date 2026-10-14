"""Record direct full text/timestamp review; alternative decoding did not resolve words."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, psutil
R = Path(__file__).resolve().parents[3]
P = R / 'projects/game-lighting-history-04/production'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
manual = {
 'artifact-context-outer-comparison-before': 'All three paragraphs and every timestamp directly read through29.06s. The transition still reads 수의 at5.90–6.22 instead of 자수의. The preceding 가방자/수가 token split preserves the bag embroidery sentence, but it does not establish the next initial syllable. No invented greeting or repeated sentence. Human pronunciation remains pending.',
 'artifact-context-runtime-texture-consumer': 'All three paragraphs and every timestamp directly read through62.00s. The same 전구 at17.78–18.02 remains instead of 정보. Whole04 and unmixed contexts recognized 정보; that conflict remains. 변위/변이, 텍셀/택셀, 예산/계산 and 앞의/앞에 variants are retained.0.22s word alignment overlap is not an audio repetition finding.',
 'artifact-context-original-18t-3': 'All three paragraphs and every timestamp directly read through42.50s.8x4=32 and4x2=8 are present, but both quarter fractions still read1분의4 at18.70–19.28 and21.96–22.58. Numerical inversion remains unresolved and cannot be approved from the surrounding equation alone. 기하/기아 and0.08s alignment overlap are preserved.'
}
executionPath = P / 'part1-recognition-ambiguities-execution-v272.json'
execution = read(executionPath)
assert execution['status'] == 'complete' and execution['exitCode'] == 0
w = execution['worker']
if psutil.pid_exists(w['pid']):
 assert abs(psutil.Process(w['pid']).create_time() - w['createTime']) > .01
assert set(manual) == {r['label'] for r in execution['results']}
rows = []
for r in execution['results']:
 assert sha(R / r['path']) == r['sha256']
 rows.append({**r, 'expectedParagraphsAndFullActualTextDirectlyRead': True, 'allWordTimestampsDirectlyRead': True,
              'contentApproved': False, 'observedResolution': manual[r['label']], 'humanPronunciation': 'pending'})
record = {'reviewedAt': datetime.now(timezone.utc).isoformat(), 'execution': {'path': executionPath.relative_to(R).as_posix(), 'sha256': sha(executionPath)},
          'currentMixSha256': execution['currentMixSha256'], 'planSha256': execution['planSha256'], 'records': rows,
          'allFullTextsAndTimestampsDirectlyCompared': True, 'allObservedRecognitionConcernsResolved': False,
          'unresolvedCount': 3, 'expectedTextUsedAsPrompt': False, 'finalMixedAsrApproved': False,
          'next': 'Independent full32-decoder Whisper large-v3 CPU2/GPU0 on the same exact three complete mixed contexts; preserve all audio.',
          'humanWholeListening': 'pending', 'humanPronunciation': 'pending', 'uploaded': False}
dest = P / 'part1-alternative-recognition-direct-review-v276.json'
assert not dest.exists()
dest.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', 'utf-8')
print(json.dumps({'directlyRead': 3, 'unresolved': 3, 'finalMixedAsrApproved': False}))
