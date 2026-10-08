"""Propose current-word/PCM boundaries after full guide text review.

Every output remains unapproved until its exact word pairs and PCM measurements
are read. This does not run ASR, regenerate audio or approve final timing.
"""
from pathlib import Path
from datetime import datetime, timezone
import array, difflib, hashlib, json, math, re, wave

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
DEST = BASE/'observation-guide-boundary-candidates-v1.json'

def read(p): return json.loads(p.read_text('utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def norm(s): return ''.join(re.findall(r'[a-zA-Z0-9가-힣]', s)).lower()

assert not DEST.exists(), 'Read the existing candidate measurement; do not repeat.'
execution = read(BASE/'observation-guide-whole-asr-execution-v1.json')
assert execution['exitCode'] == 0 and execution['actualExitObserved']
review_path = BASE/'observation-guide-whole-asr-direct-review-v1.json'
review = read(review_path)
assert review['allWholeTextsDirectlyCompared']
script_path = ROOT/'projects/player-customization/script/observation-guides.ko.v1.json'
script = read(script_path)
whole_path = BASE/'observation-guide-whole-asr-v1/asr.json'
whole = read(whole_path)
assert whole['complete'] and len(whole['results']) == len(script['scenes']) == 8
rows, contexts = [], []
for scene, result in zip(script['scenes'], whole['results']):
    assert result['id'] == scene['id'] and result['expectedKo'] == scene['lines']
    source = ROOT/result['sourcePath']
    assert sha(source) == result['sourceSha256']
    with wave.open(str(source), 'rb') as wav:
        rate, count = wav.getframerate(), wav.getnframes()
        assert rate == 24000 and wav.getnchannels() == 1 and wav.getsampwidth() == 2
        pcm = array.array('h', wav.readframes(count))
    expected = ''.join(norm(s) for s in scene['lines'])
    actual, indices = '', []
    for index, word in enumerate(result['words']):
        token = norm(word['text']); actual += token; indices.extend([index]*len(token))
    matches = difflib.SequenceMatcher(None, expected, actual, autojunk=False).get_matching_blocks()
    boundaries, starts = [], [0]
    for paragraph in range(3):
        edge = sum(len(norm(s)) for s in scene['lines'][:paragraph+1])-1
        match = next((m for m in matches if m.a <= edge < m.a+m.size), None)
        assert match, f'{scene["id"]} paragraph{paragraph+1} requires direct mapping'
        index = indices[match.b+edge-match.a]
        previous, following = result['words'][index:index+2]
        a, b = previous['timestamp'][1], following['timestamp'][0]
        assert a is not None and b is not None and b >= a, (scene['id'], previous, following)
        lo, hi, span = round((a+.05)*rate), round((b-.05)*rate), round(.01*rate)
        candidates = []
        for center in range(lo, hi+1, 60):
            values = pcm[center-span//2:center+span//2]
            if len(values) == span:
                rms = math.sqrt(sum(v*v for v in values)/span)/32768
                candidates.append((rms, abs(center-(a+b)*rate/2), center))
        assert candidates, f'{scene["id"]} paragraph{paragraph+1} has no protected quiet gap'
        rms, _, split = min(candidates)
        boundaries.append(dict(afterParagraph=paragraph+1, previousWordIndex=index,
            previousWord=previous, nextWord=following, selectedSplitSample=split,
            selectedSplitSeconds=split/rate, normalizedRms=rms,
            minimumWordEdgeMarginSeconds=.05, pcmWindowSeconds=.01,
            directWordAndPcmReview=False))
        starts.append(split)
    starts.append(count)
    assert all(a < b for a, b in zip(starts, starts[1:]))
    rows.append(dict(id=scene['id'], sourcePath=result['sourcePath'],
        sourceSha256=result['sourceSha256'], sampleRate=rate, samples=count,
        seconds=count/rate, boundaries=boundaries, proposedParagraphStartSamples=starts[:-1],
        proposedParagraphStarts=[s/rate for s in starts[:-1]], allOriginalSamplesRetained=True,
        directBoundaryReview=False, measuredTimingApproved=False))
    split = starts[2]
    for name, start, end, lines in [('first-half', 0, split, scene['lines'][:2]),
            ('last-half', split, count, scene['lines'][2:])]:
        contexts.append(dict(id=scene['id']+'-'+name, sceneId=scene['id'],
            sourcePath=result['sourcePath'], sourceSha256=result['sourceSha256'],
            startSample=start, endSample=end, seconds=(end-start)/rate,
            expectedKo=lines, containsCompleteParagraphs=True, independentFromWholeRecognition=True))
record = dict(schemaVersion=1, recordedAt=datetime.now(timezone.utc).isoformat(),
    slug='player-customization', wholeReview=review_path.relative_to(ROOT).as_posix(),
    wholeReviewSha256=sha(review_path), koSha256=sha(script_path), wholeAsrSha256=sha(whole_path),
    scenes=rows, proposedContexts=contexts, boundariesDirectlyComparedWithCurrentWordsAndPCM=False,
    measuredTimingApproved=False, allFinalPixelsReviewed=False, humanListening='pending')
DEST.write_text(json.dumps(record, ensure_ascii=False, indent=2)+'\n', 'utf-8')
print(json.dumps(dict(scenes=[dict(id=r['id'], boundaries=r['boundaries']) for r in rows],
    contexts=len(contexts), automaticallyApproved=False), ensure_ascii=False))
