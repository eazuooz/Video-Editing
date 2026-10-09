"""Record the actual tool exit and native-pixel correction; no media mutation."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json
ROOT = Path(__file__).resolve().parents[3]
W = Path(__file__).resolve().parent / 'final-v1'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
now = datetime.now(timezone.utc).isoformat()
e = read(W / 'encoded-caption-qa-execution.json')
assert e['exitCode'] == 0 and e['sampleCount'] == 1810 and e['boardCount'] == 302 and e['allActualPtsMatched']
out = dict(observedAt=now, sessionId=77618, pid=56164, actualToolExitCode=0,
    executionExitCode=e['exitCode'], sourceSha256=e['sourceSha256'], actualSampleCount=1810,
    actualBoardCount=302, allActualPtsMatched=True, allFinalPixels=False,
    qaApproved=False, collected=False, uploaded=False, repeatedExtraction=False, newGitImages=0)
(W / 'encoded-caption-qa-tool-exit-observation-v1.json').write_text(json.dumps(out, ensure_ascii=False, indent=2)+'\n', 'utf-8')
samples = []
for i in [22,23,24]:
    row = next(x for x in e['samples'] if x['index'] == i)
    assert hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256']
    samples.append(dict(row, nativeImageDirectlyRead=True, directlyObservedCaption='none' if i < 24 else '이번 영상에서는'))
gap = dict(observedAt=now, sourceSha256=e['sourceSha256'], samples=samples,
    initialSuspicion='Possible cue4 residue in board4 gap',
    actualObservation='Native samples22/frame444 and23/frame445 have empty caption regions; sample24/frame446 starts cue5 correctly.',
    disposition='Operator reading error corrected by direct native-pixel inspection; no actual residue confirmed.',
    mediaChanged=False, newExtraction=False, allFinalPixels=False, qaApproved=False)
(W / 'caption-gap-native-direct-review-v1.json').write_text(json.dumps(gap, ensure_ascii=False, indent=2)+'\n', 'utf-8')
print(json.dumps(dict(actualExitCode=0, nativeGapImagesDirectlyRead=3, actualResidueObserved=False, allFinalPixels=False)))
