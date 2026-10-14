"""Seal explicit whole-text and mapping review; independent recognition remains pending."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,wave,numpy as np
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
mix=read(R/'current-mix-execution-v2.json');plan=read(R/'measured-current17-plan-v2.json');whole=read(R/'current17-mixed-whole-asr-execution-v3.json');session=read(R/'current17-mixed-whole-asr-execution-v3.session.json')
assert whole['exitCode']==session['actualOuterExitCode']==0 and not session['workerCurrentlyAlive'] and whole['completed']==whole['total']==17
for v in mix['protectedInputs']:assert sha(ROOT/v['path'])==v['sha256']
notes={
'00a':'All four overview sentences retained; spacing differences only.',
'01':'All six paragraphs retained. Recognition A mode versus 에임 모드, 이동에 versus 이동이, and digits2022 versus spokenyear are recorded alternatives; independent context and human pronunciation pending.',
'02':'All four paragraphs retained; no missing or repeated whole argument observed.',
'03':'All six paragraphs retained; no missing or repeated whole argument observed.',
'04':'All four paragraphs retained; no missing or repeated whole argument observed.',
'05':'All six paragraphs retained; 아님으로 versus 아니므로 recognition alternative pending independent context.',
'06':'All four paragraphs retained. 도시계/도식의, 설계 제한/설계 제안, 앞에/앞의 remain recognition alternatives; do not assert pronunciation or change approved source from this result.',
'06b':'Both bridging sentences retained.',
'07':'All six paragraphs retained. digits2/투, 컷임으로/컷이므로, 잊지는/읽지는, 앞에/앞의 recorded for independent recovery.',
'07b':'All six paragraphs retained; extra initial 스, 방해/방의 and 앞에/앞의 remain recognition alternatives. Current 먼저 word16.72–16.98 with300ms padding is after the corrected16.4s placed onset. Source junction8.21 is exactly zero, unlike held8.32. Whole 다른 timestamp39.7–54.12 crosses a long quiet observation gap and is unusable for precise cue alignment; use independent current words.',
'08':'All four paragraphs retained; no missing or repeated whole argument observed.',
'08b':'All five paragraphs retained; destination, arrival, board action and common question intact.',
'09':'All six paragraphs retained. Recognizer emitted an ending-timestamp warning but stored word pairs are nonnull; this does not prove a truncated source word.',
'10':'All four paragraphs retained; 다름으로/다르므로 recognition alternative.',
'11':'All six paragraphs retained; aim mode English transcription and 뒤에/뒤의 alternative.',
'11b':'All four paragraphs retained. 네, 게임/네 게임 and 화면에/화면의 alternatives; all four game roles and three questions present.',
'12':'All four conclusion paragraphs retained. 시점, 이동 punctuation and 마지막에/마지막의 alternatives; coaching sentence present.'}
assert set(notes)==set(s['id'] for s in plan['scenes'])
rows=[]
for s in plan['scenes']:
 p=R/f'current17-mixed-whole-asr-v3/{s["id"]}.json';v=read(p);assert v['sourceSha256']==mix['decodedAacSha256'] and v['exactSourceStereoPcmBytesMatched']
 rows.append(dict(id=s['id'],path=p.relative_to(ROOT).as_posix(),sha256=sha(p),expectedWholeKo=v['expectedKo'],recognizedWholeKo=v['text'],allExpectedAndRecognizedTextDirectlyCompared=True,directObservation=notes[s['id']],expectedWasRecognizerPrompt=False,allWordTimestampsNonNull=all(None not in w['timestamp'] for w in v['words']),humanListeningApproved=False,humanPronunciationApproved=False))
out=R/'current17-mixed-whole-direct-review-v2.json';assert not out.exists()
review=dict(recordedAt=datetime.now(timezone.utc).isoformat(),actualSession=16265,actualOuterExitCode=0,actualCompletion='c92d6e',actualExitRecorder='a94198',wholeExecutionSha256=sha(R/'current17-mixed-whole-asr-execution-v3.json'),mixAacSha256=mix['mixAacSha256'],decodedAacSha256=mix['decodedAacSha256'],all17WholeTextsDirectlyCompared=True,noMissingWholeParagraphObserved=True,all17WholeAnd81IndependentContextsDirectlyCompared=False,currentMixedContentReviewPassed=False,independentContextsRun=False,results=rows,firstOnsetPhysicalPlacementRepaired=True,wordTimestampsAreApproximate=True,all71ProtectedInputsUnchanged=True,humanListeningApproved=False,humanPronunciationApproved=False,publicRightsApproved=False)
out.write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n','utf-8')
proposal=R/'current17-mixed-independent-context-plan-proposed-v4.json';v=read(proposal)
assert v['wholeExecutionSha256']==sha(R/'current17-mixed-whole-asr-execution-v3.json') and len(v['contexts'])==81 and len(v['boundaries'])==64
assert v['sourceSha256']==mix['decodedAacSha256']
with wave.open(str(ROOT/mix['decodedAac']),'rb') as w:
 assert w.getframerate()==48000 and w.getnchannels()==2
 for b in v['boundaries']:
  n=b['currentAacBoundarySample'];w.setpos(n-192);data=np.frombuffer(w.readframes(384),dtype='<i2').astype(float)
  b.update(directlyReviewed=True,currentMixed8msRms=float(np.sqrt(np.mean(data**2))),review='Read previous/following complete expected text, current whole neighboring words, source PCM quiet junction and exact source/destination mappings. Word times approximate; independent context still required.')
for sid in [s['id'] for s in plan['scenes']]:
 scene=next(s for s in plan['scenes'] if s['id']==sid);ctx=[x for x in v['contexts'] if x['scene']==sid]
 assert ctx and all(x['sourceSha256']==mix['decodedAacSha256'] for x in ctx)
 assert all(a['endSample']==b['startSample'] for a,b in zip(ctx,ctx[1:]))
 assert all(scene['startFrame']*800<=x['startSample']<x['endSample']<=scene['endFrame']*800 for x in ctx)
v.update(reviewedAt=datetime.now(timezone.utc).isoformat(),proposalSha256=sha(proposal),wholeReview=out.relative_to(ROOT).as_posix(),wholeReviewSha256=sha(out),all17WholeTextsDirectlyCompared=True,currentWholeWordsAndPcmBoundariesDirectlyCompared=True,all64BoundaryRowsDirectlyRead=True,boundaryReviewOutputs=['1c6f37','9685fd'],currentMixedContentReviewPassed=False,contextModelRun=False)
p=R/'current17-mixed-independent-context-plan-v2.json';assert not p.exists();p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(whole17DirectlyCompared=True,boundaries64DirectlyCompared=True,contexts81Prepared=True,currentMixedContentApproved=False,independentModelRun=False,all71Protected=True)))
