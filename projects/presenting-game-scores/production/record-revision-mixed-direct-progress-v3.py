"""Record only explicitly specified current mixed windows already read in full."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json

ROOT = Path(__file__).resolve().parents[3]
W = Path(__file__).resolve().parent / 'revision-balatro60-v2' / 'final-v3'
D = W / 'mixed-asr-v1'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
ap = argparse.ArgumentParser()
ap.add_argument('--through', type=int, required=True)
a = ap.parse_args()
data = read(D / 'asr.json')
assert 1 <= a.through <= len(data['results']) <= 52
notes = {
    'whole-03': 'All four complete paragraphs present, including equality guide and final conclusion. Current timestamps progress forward; earlier baseline reversal is not present here.',
    'whole-04': '7/3/6 selection and actual scoring distinction complete. ASR drops possessive particle in 점수의 이름; preserve minor pronunciation review.',
    'whole-05': '560/1327 and transient-versus-final distinction complete. 중의/중에 particle alternative remains human pronunciation review.',
    'whole-06': '27/14096/17016/2920/141 and provisional lead versus victory distinction complete. 왼쪽의/왼쪽에 and 경기 중의/중에 remain particle alternatives.',
    'whole-08': 'Current whole recognition has 기여/기어 and 읽게/잃게 alternatives. Require current independent context comparison; human pronunciation remains pending.',
    'whole-09': '704/1200 and persistent-versus-transient distinction complete. Word boundary 계속/비교할 overlaps by .02s in ASR timestamps; no repeated content inferred.',
    'whole-10': 'Both Tetris and Balatro audit and coaching ending present. Current independent19 context correctly recognizes 어떤 이름의 from the exact same mixed interval. 카드의/카드에 and 기여/기어 remain human pronunciation questions.',
    'context-04-evaluation-weights-p3-c1': 'Entire clause and ending present. Possessive 점수의 recognized as 점수; human particle pronunciation remains pending.',
    'context-05-events-and-total-p2-c1': 'Event, running total and transient value distinctions complete. 중의/중에 recognition alternative remains a human particle question.',
    'context-06-relative-gap-p2-c1': 'Independent window reads27주를 where whole06 reads27줄을 for the same exact mixed interval. Numeric2920 and complete ending present; unit consonant pronunciation remains pending.',
    'context-16-observe-later-point-lead-p1-c1': 'Complete provisional lead clause and ending. 왼쪽의/왼쪽에 remains a human particle pronunciation question.',
    'context-08-scoring-feedback-p3-c1': 'Both complete sentences and final 하죠 present. Current independent recognition repeats 기어/잃게 alternatives to intended 기여/읽게; human lexical pronunciation unresolved. No sentence omission or added greeting observed.',
    'context-10-audit-and-close-p2-c2': 'Entire Balatro recap and ending present. 카드의/카드에 and 기여/기어 recognition alternatives remain explicit human pronunciation questions.',
    'context-19-observe-reading-audit-p1-c1': 'Complete current independent mixed clause correctly recognizes 어떤 이름의 and 기여하는지 with forward timestamps and full ending; resolves whole10 어떤의 omission as a recognition-context artifact, not an audio omission.',
}
rows = []
for x in data['results'][:a.through]:
    p = D / (x['label'] + '.json')
    d = read(p)
    assert d['text'] == x['text'] and d['expectedKo'] == x['expectedKo']
    assert d['exactStereoMixSampleBytesMatched'] and not d['expectedWasRecognizerPrompt']
    assert sha(ROOT / d['windowPath']) == d['windowSha256']
    rows.append(dict(label=x['label'], path=p.relative_to(ROOT).as_posix(), sha256=sha(p),
        directlyCompared=True, fullExpectedAndActualTextRead=True, allWordTimestampsRead=True,
        observation=notes.get(x['label'], 'Complete expected and recognized text plus all word timestamps directly compared; complete ending present. Spacing/punctuation do not rewrite the approved script. Human listening/pronunciation remain pending.'),
        fromSample=d['fromSample'], toSample=d['toSample'], padSamplesEachSide=d['padSamplesEachSide']))
progress = dict(recordedAt=datetime.now(timezone.utc).isoformat(),
    currentMixedAudioSha256=data['mixSha256'], currentAacSha256=data['aacSha256'], planSha256=data['planSha256'],
    windows=rows, directlyRead=a.through, total=52, all52WindowsDirectlyCompared=a.through == 52,
    technicallyApproved=False, finalMixedAsrApproved=False,
    unresolvedContentQuestions=[] if a.through==52 else ['Finish current independent mixed comparison; separate lexical pronunciation alternatives from confirmed sentence-level omissions'],
    humanWholeListening='pending', humanPronunciation='pending', endingHeuristicUsedForApproval=False,
    allFinalPixels=False, qa=False, collected=False, private=False, imagesGitAdded=0)
(W / 'mixed-asr-direct-progress.json').write_text(json.dumps(progress, ensure_ascii=False, indent=2) + '\n', 'utf-8')
print(json.dumps(dict(directlyCompared=a.through, total=52, finalMixedAsrApproved=False)))
