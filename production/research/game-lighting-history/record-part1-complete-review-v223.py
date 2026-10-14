"""Seal directly read replacements; retain unchanged recognition and failed pixels."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, os, psutil

ROOT = Path(__file__).resolve().parents[3]
B = ROOT / 'projects/game-lighting-history-04/production'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
ref = lambda p: dict(path=p.relative_to(ROOT).as_posix(), sha256=sha(p))
write = lambda p, d: p.write_text(json.dumps(d, ensure_ascii=False, indent=2)+'\n', 'utf-8')
prior = read(B/'part1-current-asr-direct-review-v201.json')
old = read(B/'part1-selected-actions-asr-execution-v182.json')
newpath = B/'part1-literal-onset-asr-execution-v220.json'
new = read(newpath)
selectedpath = B/'part1-selected-current-tts-execution-v219.json'
selected = read(selectedpath)
assert new['exitCode'] == 0 and new['endedAt'] and len(new['completed']) == 5
identity = new['actualIdentity']
if psutil.pid_exists(identity['pid']):
    p = psutil.Process(identity['pid'])
    if abs(p.create_time()-identity['createTime']) < .1 and p.cmdline() == identity['command']:
        raise RuntimeError('Worker still alive')
notes = {
 'whole-runtime-texture-size': 'All four literal statements once. 이번 자산 창에서는 at0-.24/.24-.62/.62-1.10; final 합니다21.24-21.58. No diagnostic preface retained.',
 'context-runtime-texture-size': 'All six consumer statements and four size statements once. Size starts24.84; 합니다46.08-46.42. 보입니다28.90-29.44/주소로29.30-30.16 overlap is recognizer timing, not repeated PCM. 앞의/앞에 and 텍셀이/택셀이 remain pronunciation review.',
 'context-ordinary-streaming-budget': 'All four size and four ordinary-budget statements once. Next paragraph starts22.0; final 적어두겠습니다39.8-40.9. Adjacent28.54-29.36/29.18-29.88 boundaries overlap; preserve actual times. 물리 풀과 한 joined spelling is ASR spacing.',
 'whole-geometry-car-material': 'Both literal statements once. 자동차0-.40 and final 읽어보세요5.64-6.36. Current PCM begins with complete automobile word; no preface or additional filler.',
 'context-geometry-car-material': 'All nine programmable-material statements and both car statements once. 자동차42.42-42.84 precedes exact PCM paragraph start42.44 by20ms: recognizer timing discrepancy. 분기/붕기18.08-18.48 and 뒤의/뒤에23.84-24.08 preserved. 됩니다27.02-27.52/여기서는27.26-28.20 overlap is recognizer timing. Final 읽어보세요48.08-48.84.'
}
replacements = {}
for done in new['completed']:
    p = ROOT/done['result']; assert sha(p) == done['sha256']
    r = read(p)
    for source in r['job']['sources']:
        assert sha(ROOT/source['path']) == source['sha256']
        take = next((t for t in selected['results'] if t['id'] == source['id']), None)
        if take:
            assert take['sha256'] == source['sha256']
    replacements[done['label']] = dict(label=done['label'], result=ref(p),
        directFullExpectedAndActualTextCompared=True,
        expectedFullTexts=[dict(id=s['id'], ko=s['ko'], pcm=dict(path=s['path'], sha256=s['sha256'], sampleRange=s['sampleRange'])) for s in r['job']['sources']],
        actualFullText=r['text'], endingWords=r['chunks'][-3:], notes=notes[done['label']],
        recognizerExpectedPrompt=False, observedClauseCoverageAccepted=True,
        allSpokenWordsConfirmed=None, allWordTimestampsDirectlyCompared=True,
        actualPronunciationApproved=False, humanListening='pending', endingHeuristicOnlyApproval=False)
rows = [replacements.get(row['label'], row) for row in prior['rows']]
assert len(rows) == 74 and len({r['label'] for r in rows}) == 74
for row in rows:
    assert row['directFullExpectedAndActualTextCompared'] and row['allWordTimestampsDirectlyCompared']
    assert sha(ROOT/row['result']['path']) == row['result']['sha256']
combined = dict(old)
changed = {r['label']: r for r in new['completed']}
combined['completed'] = [changed.get(r['label'], r) for r in old['completed']]
combined.update(status='74-selected-results-from-closed-workers-directly-reviewed',
    actualExecutions=[ref(B/'part1-selected-actions-asr-execution-v182.json'), ref(newpath)],
    selectionOnly=True, recognizerRerun=False, unchangedResultsReused=69,
    actualIdentity=identity, endedAt=new['endedAt'], exitCode=0)
combinedpath = B/'part1-current-asr-results-v223.json'
out = B/'part1-current-asr-direct-review-v223.json'
assert not combinedpath.exists() and not out.exists()
write(combinedpath, combined)
record = dict(prior)
record.update(reviewedAt=datetime.now(timezone.utc).isoformat(), prior=ref(B/'part1-current-asr-direct-review-v201.json'),
    selectedTakes=ref(selectedpath), sourceExecution=ref(combinedpath), rows=rows,
    replacementExecution=ref(newpath), actualWorker=identity, session=26428,
    sessionObservedClosedExitCode=0, actualExecutionEndedAt=new['endedAt'],
    onsetRepairIds=[], affectedReplacementWindows=list(notes), retainedCurrentTakes=35,
    twoUnresolvedOnsetsApproved=True, literalOnsetClauseCoverageAccepted=True,
    wholeAndIndependentContextApproval=True, currentMixAsrApproved=False,
    next='Bind current37 captions, fix source label collisions, then review actual final mix and every final cue/cut.')
write(out, record)
qapath = ROOT/'production/research/game-lighting-history/local/part1-spatial-bank-v206/qa-v222/execution.json'
qa = read(qapath)
assert qa['exitCode'] == 0 and len(qa['boards']) == 53
for board in qa['boards']:
    assert sha(ROOT/board['path']) == board['sha256']
findings = [
 dict(id='horizon-comparison-before', issue='Bag boxes occlude CNN/SR and Transformer/SR labels.', repair='Raise labels above maximum object extent.'),
 dict(id='cyber-comparison-before', issue='Surface label sits too close to output object extent.', repair='Separate plane labels above geometry.'),
 dict(id='fortnite-comparison-before', issue='Three material objects occlude left condition label.', repair='Raise plane label above all three objects.'),
 dict(id='tsr-silhouette-history', issue='Gold projected object occludes past/current surface names.', repair='Raise names above object and motion path.'),
 dict(id='tsr-rotation-vectors', issue='Orange boundary path crosses surface-name letters.', repair='Raise names outside motion extent.'),
 dict(id='cyber-light-reconstruction', issue='Small light samples touch right input-name letters.', repair='Raise input names above sample extent.'),
 dict(id='mobile-compiler-availability', issue='Orange hollow outline/vertical edges cross confirm and unavailable-data names.', repair='Place both names above maximum hollow-outline extent.')
]
write(B/'part1-spatial-source-direct-review-v223.json', dict(reviewedAt=record['reviewedAt'], extraction=ref(qapath),
    source=qa['source'], all53BoardsDirectlyViewed=True, extractedFrames=211,
    boards=[dict(x, directlyViewed=True) for x in qa['boards']], findings=findings,
    unchangedSceneIds=['outer-comparison-before','four-game-transfer-conclusion','shadow-wheel-change'],
    projectedFacesAndDepthObserved=True, orderedStagesObserved=True,
    actualBrowserPlaybackObserved=False, allMovingPixelsReviewed=False,
    currentSourcePixelApproval=False, allFinalCaptionPixelsReviewed=False,
    imagesLocalOnly=True, newGitImages=0, uploaded=False))
cp = ROOT/'production/research/game-lighting-history/checkpoint.json'
c = read(cp); c.update(updatedAt=record['reviewedAt'], ownedActiveWork=None,
    status='episode04-physical01-current37-ASR-complete-scoped-spatial-label-repair',
    episode04Part1CompleteAsrV223=dict(review=ref(out), completed=74, unchangedReused=69, replacements=5, session=26428, sessionExit=0, humanListening='pending', finalMixApproved=False),
    episode04Part1SpatialSourceReviewV223=ref(B/'part1-spatial-source-direct-review-v223.json'))
tmp=cp.with_name(cp.name+'.223-'+str(os.getpid()));write(tmp,c);os.replace(tmp,cp)
print(json.dumps(dict(currentWindows=74, replacements=5, unchangedReused=69, wholeContextCompared=True, sessionClosed=0, sourceBoardsRead=53, repairScenes=7, finalMixApproved=False)))
