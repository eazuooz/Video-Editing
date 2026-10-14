"""Preserve direct readings of all six complete current-mix contexts."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib
R = Path(__file__).resolve().parents[3]
P = R / 'projects/game-lighting-history-04/production'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
manual = {
 'artifact-context-outer-comparison-before': (False, 'All three complete embroidery/transition/display-frequency paragraphs and every timestamp directly read through29.06s. Initial 자수의 is still recognized as 수의 at5.90–6.22s, even with the complete preceding Aloy sentence. This does not resolve the initial syllable. Previous unmixed whole recognized 가수의; preserve the conflict. 앞의/앞에 is a separate particle variant. No invented ending or repeated sentence. Focused alternative decoding required.'),
 'artifact-context-runtime-texture-consumer': (False, 'All three producer/consumer/size paragraphs and every timestamp directly read through62.00s. 정보 again appears as 전구 at17.78–18.02s, whereas current whole04 and prior unmixed whole/context read 정보. This conflict is unresolved. 변위/변이, 텍셀/택셀 and 예산/계산 variants are preserved; the next complete ordinary-streaming context correctly reads 예산. A0.22s alignment overlap is not repeated speech. Focused alternative decoding required.'),
 'artifact-context-texture-streaming-input': (True, 'All three resource-address/material-input/shared-coordinate paragraphs and every timestamp directly read through86.06s. No invented news ending, backward timestamp repeat or repeated sentence: resolves whole03 chunk insertion/reversal. 무늬/문의, 자산/자상, 셰이더/쉐이더, 맡습니다/맞습니다 and particles remain human pronunciation variants. Small0.24s/0.16s alignment overlaps do not repeat sentences.'),
 'artifact-context-ordinary-streaming-budget': (True, 'All three address/pool-budget/virtual-pool paragraphs and every timestamp directly read through62.60s. No goodbye insertion, backward repeat or missing sentence. 예산으로, 편집하는 동안, matching-size and full settings-record ending are present. Resolves whole04 chunk artifact and the runtime-size 예산/계산 context variant. Two0.22s alignment overlaps are retained without an audio-repeat claim.'),
 'artifact-context-original-18t-3': (False, 'All three resolution-count/quarter-pixel/motion-vector paragraphs and every timestamp directly read through42.50s.8x4=32 and4x2=8 are correctly recognized, but both quarter fractions are still transcribed1분의4 at18.70–19.28s and21.96–22.58s. Do not approve the numerical inversion from the surrounding equation alone. 기하/기아 remains documented. A0.08s overlap is an alignment result. Focused alternative decoding required.'),
 'artifact-context-07-pre-visibility-interpolation': (True, 'All three diagnostic-view/interpolation/courtyard paragraphs and every timestamp directly read through94.54s. Coordinates00/10/01, weights1/2,1/4,1/4, result0.25/0.25 and sum1 are present. No duplicated1입니다, invented greeting or backward repetition. Resolves whole07 numeric duplicate. 세/새, 같게/갖게, 바뀌므로/바뀜으로 and 앞의/앞에 remain pronunciation/particle variants;0.24s/0.08s/0.14s overlaps are alignment evidence.')
}
state = read(P / 'part1-artifact-context-execution-v255.json')
assert state['status'] == 'complete' and state['exitCode'] == 0
assert set(manual) == {r['label'] for r in state['results']}
rows = []
for done in state['results']:
 assert sha(R / done['path']) == done['sha256']
 approved, finding = manual[done['label']]
 rows.append({**done, 'expectedParagraphsAndFullActualTextDirectlyRead': True,
              'allWordTimestampsDirectlyRead': True, 'contentApproved': approved,
              'observedResolution': finding, 'humanPronunciation': 'pending'})
settings = read(P / 'part1-final-mix-settings-v242.json')
record = {'reviewedAt': datetime.now(timezone.utc).isoformat(),
          'currentMixSha256': settings['wavSha256'], 'planSha256': settings['planSha256'],
          'records': rows, 'allFullTextsAndTimestampsDirectlyCompared': True,
          'allObservedRecognitionConcernsResolved': False, 'approvedContexts': 3,
          'unresolvedLabels': [r['label'] for r in rows if not r['contentApproved']],
          'next': 'Different beam decoding of three unresolved complete current-mix contexts; no recognizer prompt.',
          'finalMixedAsrApproved': False, 'allFinalPixelsReviewed': False,
          'humanWholeListening': 'pending', 'humanPronunciation': 'pending', 'uploaded': False}
dest = P / 'part1-artifact-context-direct-progress-v273.json'
assert not dest.exists()
dest.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', 'utf-8')
print(json.dumps({'contextsFullyRead': 6, 'resolved': 3, 'unresolved': 3, 'finalMixedApproval': False}))
