"""Seal the manually read whole17 and all81 complete current-AAC text pairs.

This is a bounded transcript/completeness review. Human pronunciation/listening
and final video/caption review are separate, unfinished approvals.
"""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=R/'current17-mixed-complete-direct-review-v2.json';assert not out.exists()
state=read(R/'current17-mixed-contexts-asr-execution-v3.json');session=read(R/'current17-mixed-contexts-asr-execution-v3.session.json')
assert state['exitCode']==session['actualOuterExitCode']==0 and not session['workerCurrentlyAlive'] and state['completed']==state['total']==81
whole=R/'current17-mixed-whole-direct-review-v2.json';wv=read(whole);assert wv['all17WholeTextsDirectlyCompared']
mix=read(R/'current-mix-execution-v2.json');assert mix['decodedAacSha256']==state['decodedAacSha256']==sha(ROOT/mix['decodedAac'])
for p in mix['protectedInputs']:assert sha(ROOT/p['path'])==p['sha256']
notes={
 '00a-p03':'관찰의/관찰을 alternative; current whole00a recovers expected 관찰을. Human pronunciation pending.',
 '01-p03':'Independent 에임모드 recovers whole A 모드 spelling alternative.',
 '01-p04':'Independent 조종/조준 alternative, whole01 recovers 조준. Independent 이동이 recovers whole 이동에.',
 '01-p05':'2022 is the numeric spelling of 이천이십이 년.',
 '03-p04':'배경에/배경의 alternative; whole03 recovers 배경의.',
 '04-p04':'뜻밖의/뜻밖에 alternative; whole04 recovers 뜻밖에.',
 '05-p06':'Independent 아니므로 recovers whole 아님으로 alternative.',
 '06-p03':'도식의 appears as 도시계 in both current transcripts; human pronunciation remains pending. Independent 설계 제안 recovers whole 설계 제한. Full distinction between actual game menu and our proposed diagram remains present. 앞에/앞의 is a genitive alternative. No PCM rewritten.',
 '07-p01':'2 is the numeric spelling of 투.',
 '07-p03':'컷임으로/컷이므로 and 잊지는/읽지는 alternatives persist in both current transcripts. The complete three sentences are present; do not claim exact pronunciation or recovered spelling. Human listening/pronunciation pending; retained approved PCM remains unchanged.',
 '07-p05':'앞에/앞의 genitive alternative; full shared-question comparison present.',
 '07b-p01':'Both current transcripts have initial 스퍼즐 instead of 퍼즐. Current source bytes exactly match the repaired PCM; the separately reviewed spliced source whole/seam recovered 퍼즐. This is an unresolved mixed-recognition prefix alternative, not claimed human pronunciation approval. Both full sentences remain present.',
 '07b-p02':'Current independent text recovers complete 먼저 and 방의 단서; whole 방해 alternative is recovered here. Physical 먼저 onset placement was repaired at the measured zero 8.21 source boundary.',
 '07b-p03':'앞에/앞의 genitive alternative; full cube/Aim Mode comparison present.',
 '07b-p04':'Both separate intervals and blue-to-yellow result are present; word timestamps sweep long observation gaps and must be clamped to exact placement windows before captions.',
 '08-p01':'더욱/더 spelling alternative; individual-comfort limitation remains complete.',
 '10-p04':'다름으로/다르므로 recognition alternative, human pronunciation pending; full safety/feedback limitation retained.',
 '11-p02':'Independent 조주는/조준은 alternative; whole11 recovers 조준은. Whole 뒤에/뒤의 is recovered by independent 뒤의.',
 '11-p04':'Independent 에임모드 recovers English aim mode spelling in whole11.',
 '11b-p01':'Independent 내/네 alternative, whole11b recovers 네; 화면에/화면의 genitive alternative persists. All three questions are complete; human pronunciation pending.',
 '12-p01':'Comma after 시점 is recognition punctuation; no omitted 이동.',
 '12-p04':'마지막에/마지막의 genitive alternative; full coaching request and link ending retained.'
}
rows=[]
for v in state['results']:
 p=R/f'current17-mixed-contexts-asr-v3/{v["id"]}.json';stored=read(p);assert stored==v
 assert v['exactSourceStereoPcmBytesMatched'] and v['sourceSha256']==state['decodedAacSha256'] and sha(ROOT/v['contextPath'])==v['contextSha256']
 assert v['words'] and all(w['timestamp'][0] is not None and w['timestamp'][1] is not None for w in v['words'])
 rows.append(dict(id=v['id'],resultPath=p.relative_to(ROOT).as_posix(),resultSha256=sha(p),expectedKo=v['expectedKo'],recognizedKo=v['text'],fullExpectedAndRecognizedTextsDirectlyCompared=True,completeSentenceBeginningAndEndingDirectlyCompared=True,noMissingOrRepeatedCompleteSentenceObserved=True,firstWord=v['words'][0],lastWord=v['words'][-1],wordTimesAreApproximate=True,reviewNote=notes.get(v['id'],'Full expected/recognized sentence(s) agree apart from punctuation or spacing.'),humanPronunciationApproved=False))
obj=dict(schemaVersion=1,reviewedAt=datetime.now(timezone.utc).isoformat(),wholeReview=whole.relative_to(ROOT).as_posix(),wholeReviewSha256=sha(whole),independentActualSession=22131,independentActualCompletion='085ff5',independentActualOuterExitCode=0,all17WholeAnd81IndependentContextsDirectlyCompared=True,all81CompleteTextBeginningsAndEndingsDirectlyCompared=True,currentMixedContentReviewPassed=True,reviewScope='Current mixed transcript completeness and exact source-boundary comparison for editing; not human acoustic/pronunciation approval or a claim that every recognized spelling matches.',allExpectedWordsRecognizedExactly=False,unresolvedRecognitionAlternativesRemainPendingHumanReview=True,rows=rows,mixAacSha256=state['mixAacSha256'],decodedAacSha256=state['decodedAacSha256'],all71ProtectedInputsUnchanged=True,all17RawPcmPlacementsExact=True,original14ApprovedPcmPreserved=True,firstVoicedOnsetPhysicalPlacementRepaired=True,captionLongObservationGapTimingReviewPending=True,allFinalPixelsApproved=False,humanListeningApproved=False,humanPronunciationApproved=False,publicRightsApproved=False,actualVideoId=None)
out.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n','utf-8')
cp=read(R/'latest-checkpoint.json');cp.update(recordedAt=obj['reviewedAt'],currentMixedDirectReview=out.name,currentMixedAudioApproved=True,currentMixedHumanListeningApproved=False,activeOwnedWorkers=0,next='Run prepared captionBuilderV4; directly read all41 new cue timing rows including exact observation-gap corrections. Then freshresource/currentdup and one pairV2; final pixels/4files/private/settings/Git/actualschedule and corresponding obsolete handling remain pending.')
t=R/'latest-checkpoint.json.writing';t.write_text(json.dumps(cp,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,R/'latest-checkpoint.json')
print(json.dumps(dict(wholeDirectRead=17,independentDirectRead=81,contentCompletenessReview=True,exactEveryRecognizedWord=False,humanListening=False,finalPixels=False)))
