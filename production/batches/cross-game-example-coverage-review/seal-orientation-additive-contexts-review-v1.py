"""Seal full direct text comparison of six current PCM and 22 independent contexts."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json
ROOT=Path(__file__).resolve().parents[3]
O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=O/'additions-whole-and-independent-direct-review-v1.json'
assert not out.exists()
wholepath=O/'additions-whole-asr-execution-v1.json'
contextpath=O/'additions-contexts-asr-execution-v1.json'
whole,contexts=read(wholepath),read(contextpath)
assert contexts['actualExitObserved'] and contexts['actualOuterExitCode']==0
assert contexts['actualOuterSession']==59706 and contexts['completed']==22
assert whole['actualExitObserved'] and whole['actualOuterExitCode']==0 and whole['completed']==6
notes={
 '06a-p02':'Independent 資料-like 자료를 replaces 자로; current whole recognizes the full intended ruler reading. Retain that whole/context alternative and human pronunciation pending.',
 '06a-p03':'Independent full context recovers 방의 기준에서. 세자가 is the same spoken 세 자가; spacing does not prove human pronunciation.',
 '13a-p03':'Independent full context recovers 축 길이, repairing the whole recognizer alternative 축끼리 without PCM modification.',
 '16a-p02':'Written 일로 and recognized 1로 are the same spoken number one.',
 '21a-p01':'Both current whole and padded independent full-source context omit expected initial 시작. Hold this first original paragraph for one scoped repair candidate; no acoustic failure or human listening claim.'}
rows=[]
for row in contexts['results']:
    assert sha(ROOT/row['sourcePath'])==row['sourceSha256']
    assert sha(ROOT/row['contextPath'])==row['contextSha256']
    assert row['exactSourceSampleBytesMatched'] and not row['expectedWasRecognizerPrompt']
    rows.append(dict(id=row['id'],sceneId=row['sceneId'],expectedCompleteText=row['expectedKo'],
        recognizedCompleteText=row['text'],sourcePath=row['sourcePath'],sourceSha256=row['sourceSha256'],
        contextPath=row['contextPath'],contextSha256=row['contextSha256'],
        sourceSampleRange=[row['startSample'],row['endSample']],currentWords=row['words'],
        allExpectedRecognizedWordsAndEndpointsDirectlyCompared=True,
        note=notes.get(row['id'],'Complete intended sentence recovered, with punctuation/spacing alternatives only; no omission or repetition observed in this recognized context.'),
        currentContentApproved=row['id']!='21a-p01',humanPronunciationApproved=False))
data=dict(reviewedAt=datetime.now(timezone.utc).isoformat(),wholeExecution=wholepath.relative_to(ROOT).as_posix(),
    wholeExecutionSha256=sha(wholepath),contextsExecution=contextpath.relative_to(ROOT).as_posix(),
    contextsExecutionSha256=sha(contextpath),actualSession=59706,actualOuterExitCode=0,actualCompletion='31c477',
    allWhole6AndIndependent22FullTextsDirectlyCompared=True,rows=rows,
    scope='Current unmixed recognized completeness and exact-source padded independent boundaries only.',
    heldOriginalParagraphs=['21a-p01'],currentAll6ContentApproved=False,
    humanListeningApproved=False,humanPronunciationApproved=False,currentMixedAsrApproved=False,
    finalCaptionTimingApproved=False,baseline24PcmRegenerated=0,additive6PcmRegenerated=0,
    next='Preserve all six original PCM. Inspect native game candidates. Prepare one original first-paragraph repair of 21a; assess candidate before adoption.')
out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf-8')
cp=read(O/'latest-checkpoint.json')
cp.update(additionsCurrentDirectReview=out.relative_to(ROOT).as_posix(),currentUnmixedAsrApproved=False,
    currentAsrHeldParagraphs=['21a-p01'],activeOwnedWorkers=0,
    next=data['next'],recordedAt=data['reviewedAt'])
(O/'latest-checkpoint.json').write_text(json.dumps(cp,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(whole=6,contexts=22,directlyCompared=True,held=['21a-p01'],pcmChanged=0)))
