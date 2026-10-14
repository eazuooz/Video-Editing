"""Seal all directly compared mixed contexts after actual180-worker closure."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json
ROOT=Path(__file__).resolve().parents[3];O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ap=argparse.ArgumentParser();ap.add_argument('--last-ten-read-evidence',required=True);a=ap.parse_args()
out=O/'current34-mixed-complete-direct-review-v1.json';assert not out.exists()
s=read(O/'current34-mixed-contexts-asr-execution-v1.json')
assert s['actualOuterExitCode']==0 and s['workerDead'] and s['completed']==s['total']==180
wholep=O/'current34-mixed-whole-direct-review-v1.json';whole=read(wholep)
assert whole['all34WholeTextsDirectlyCompared'] and whole['mixAacSha256']==s['mixAacSha256']
priorp=O/'current34-mixed-context-partial-direct-review-v3.json';prior=read(priorp);assert prior['reviewedCount']==130
rows=list(prior['rows'])
for r in rows:assert sha(ROOT/r['resultPath'])==r['resultSha256']
def evidence(i):
    if i<=144:return '55d1c9'
    if i<=152:return 'afec5e'
    if i<=154:return 'c6d2c6'
    if i<=159:return '8f8927'
    if i<=163:return 'b287ca'
    if i<=170:return 'a52119'
    return a.last_ten_read_evidence
for i,r in enumerate(s['results'][130:],131):
    p=O/'current34-mixed-contexts-asr-v1'/(r['id']+'.json');assert read(p)==r
    assert r['sourceSha256']==s['decodedAacSha256'] and r['exactSourceStereoPcmBytesMatched'] and not r['expectedWasRecognizerPrompt']
    rows.append(dict(index=i,id=r['id'],expectedKo=r['expectedKo'],currentText=r['text'],resultPath=p.relative_to(ROOT).as_posix(),resultSha256=sha(p),fullExpectedAndCurrentDirectlyRead=True,firstThreeAndLastThreeWordsDirectlyRead=True,readEvidence=evidence(i)))
assert len(rows)==180
mix=read(O/'current34-mix-execution-v2.json')
assert mix['all34RawPcmPlacementsExact'] and mix['all24BaselineDistributedPcmExact'] and mix['actualOuterExitCode']==0
proof=read(O/'narration-07b-guide-repair-execution-v1.json')
for x in proof['protectedInputs']+proof['results']:assert sha(ROOT/x['path'])==x['sha256']
notes={**prior['recognitionNotes'],
    '18-p01':'행렬의/생렬의 initial term alternative; remaining benefit statement and ending complete.',
    '19-p01':'투/to recognized2; both local-to-world and world-to-local contracts intact.',
    '19-p03':'공간의/공간에 particle alternatives.',
    '19-p05':'수학표기/수확표기 alternative; row-major storage versus row-vector convention distinction intact.',
    '20-p04':'변수에/변수의 particle alternative.',
    '21-p01':'처음 prefix unrecovered in independent AAC, as in whole review. Original approved PCM and exact placement preserved; not every word recognized or human pronunciation approved.',
    '21-p05':'보간/보관 alternative; averaging matrix components does not guarantee valid rotations statement retained.',
    '21-p06':'보간/보관 alternative in upcoming lesson reference.',
    '22-p01':'앞의/앞에 particle alternative;90degree and(1,0,0) problem intact.',
    '22-p03':'물체 원점/물체의 원점 recognizer addition; values(4,5,0),(3,3,0) and90degrees intact.',
    '22-p04':'변위/변이 recognizer alternative; displacement(1,2,0) recovered.'}
data=dict(recordedAt=datetime.now(timezone.utc).isoformat(),wholeReview=wholep.relative_to(ROOT).as_posix(),wholeReviewSha256=sha(wholep),
    partialReview=priorp.relative_to(ROOT).as_posix(),partialReviewSha256=sha(priorp),rows=rows,recognitionNotes=notes,
    actualContextsSession=s['actualSession'],actualContextsOuterExit=s['actualOuterExitCode'],actualContextsCompletion=s['completionChunk'],
    all180ContextsDirectlyCompared=True,all34WholeTextsDirectlyCompared=True,currentMixedPlacementAndContentReviewPassed=True,
    reviewBasis='All expected/current whole texts and180 independent complete paragraph diagnostics read; exact approved34 PCM/24 distributed placements verified. Recognizer substitutions/unrecovered prefixes remain disclosed, not exact human pronunciation approval.',
    allExpectedWordsRecognized=False,currentMixedAudioApproved=False,humanListeningApproved=False,humanPronunciationApproved=False,publicRightsApproved=False,
    mixAacSha256=s['mixAacSha256'],decodedAacSha256=s['decodedAacSha256'],all34RawPcmPlacementsExact=True,
    all24BaselineDistributedPcmExact=True,all79ProtectedInputsUnchanged=True,repairCandidateUnchanged=True,
    timingLimit=prior['timingLimit'],newTts=0,finalCuePixelsApproved=False)
out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(whole=34,contexts=180,placementAndContentReview=True,allExpectedWordsRecognized=False,humanPending=True)))
