"""Seal directly compared whole text and complete-context boundary evidence."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, wave
ROOT = Path(__file__).resolve().parents[3]
O = ROOT / 'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
reviewpath = O / 'additions-whole-direct-review-v1.json'
planpath = O / 'additions-independent-context-plan-v1.json'
assert not reviewpath.exists() and not planpath.exists()
wholepath = O / 'additions-whole-asr-execution-v1.json'
proposalpath = O / 'additions-independent-context-proposal-v1.json'
whole,proposal = read(wholepath),read(proposalpath)
assert whole['actualExitObserved'] and whole['actualOuterSession'] == 43092
assert whole['actualOuterExitCode'] == 0 and whole['completed'] == 6
assert proposal['wholeExecutionSha256'] == sha(wholepath)
notes = {
    '02a': 'All four complete sentences and screen-observation disclaimer recovered. Sentence 1/2 timestamp gaps are zero width; retain 150ms context overlap at both boundaries rather than claim exact silence.',
    '06a': 'Sentences 1 and 2 recovered. Sentence 3 has 방의 기준에서 versus 방에 기준해서; independent complete sentence required before content approval.',
    '09a': 'All four complete sentences, dot-product reading and transpose operation recovered without omission/repetition.',
    '13a': 'Three sentences recovered; sentence 3 축 길이 versus 축끼리 is a meaningful alternative requiring independent comparison.',
    '16a': 'All four complete sentences recovered; written 일로/recognized 1로 represents the same spoken one, with the parallel/vanished-axis condition retained.',
    '21a': 'Sentence 1 recognizes 자세와 and omits expected initial 시작. Keep the entire source from sample0 and add quiet context padding for an independent reading; no acoustic failure claim.'}
rows = []
for row in whole['results']:
    assert sha(ROOT/row['sourcePath']) == row['sourceSha256']
    rows.append(dict(id=row['id'],sourcePath=row['sourcePath'],sourceSha256=row['sourceSha256'],
        expectedWholeText=' '.join(row['expectedKo']),recognizedWholeText=row['text'],
        expectedParagraphCount=len(row['expectedKo']),wholeTextAndAllWordsDirectlyRead=True,
        note=notes[row['id']],currentContentApproved=False))
review = dict(reviewedAt=datetime.now(timezone.utc).isoformat(),
    execution=wholepath.relative_to(ROOT).as_posix(),executionSha256=sha(wholepath),
    actualOuterExitCode=0,actualOuterSession=43092,actualCompletionChunk='87a92b',
    allWholeTextsDirectlyCompared=True,allCurrentWordLandmarksDirectlyCompared=True,
    rows=rows,wholeContentApprovalHeldForIndependentContexts=True,
    humanListeningApproved=False,humanPronunciationApproved=False,
    currentMixedAsrApproved=False,baseline24PcmRegenerated=0,additive6PcmRegenerated=0)
reviewpath.write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n','utf-8')
contexts = []
for row in proposal['contexts']:
    source = ROOT / row['sourcePath']
    assert sha(source) == row['sourceSha256']
    with wave.open(str(source),'rb') as wav:
        frames = wav.getnframes()
        pcm = wav.readframes(frames)
    r = dict(row)
    if r['sceneId'] == '02a':
        # Only the two zero-width word boundaries need overlapping complete contexts.
        if r['paragraphIndex'] in [1,2]: r['startSample'] = max(0,r['startSample']-3600)
        if r['paragraphIndex'] in [0,1]: r['endSample'] = min(frames,r['endSample']+3600)
        r['boundaryContextOverlapSamples'] = 3600
    a,b = r['startSample'],r['endSample']
    r.update(startSeconds=a/24000,endSeconds=b/24000,
        exactContextPcmSha256=hashlib.sha256(pcm[a*2:b*2]).hexdigest(),
        boundaryScope='Current whole word ends/starts and disclosed exact-PCM energy evidence; padded independent diagnostic, not final caption timing.')
    contexts.append(r)
plan = dict(createdAt=datetime.now(timezone.utc).isoformat(),
    proposal=proposalpath.relative_to(ROOT).as_posix(),proposalSha256=sha(proposalpath),
    wholeReview=reviewpath.relative_to(ROOT).as_posix(),wholeReviewSha256=sha(reviewpath),
    contexts=contexts,boundariesDirectlyComparedWithCurrentWordsAndPCM=True,
    contextCount=22,zeroPaddingSamplesEachSide=7200,expectedWasRecognizerPrompt=False,
    acousticOrHumanListeningApproval=False,finalCueTimingApproved=False,
    modelExecuted=False,baseline24AndAdditive6PcmPreserved=True)
planpath.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(review=reviewpath.relative_to(ROOT).as_posix(),plan=planpath.relative_to(ROOT).as_posix(),
    whole6DirectlyCompared=True,contexts=22,heldAlternatives=['06a-p03','13a-p03','21a-p01'])))
