"""Seal the completed four texts after their entire direct comparison."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
FOLDER=BASE/'voice-clarity-v2'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
state_path=FOLDER/'asr-execution.json';state=read(state_path)
assert state['exitCode']==0 and state['actualExitObserved'] and state['actualOuterExitCode']==0
assert state['sessionId']==71144 and len(state['results'])==4 and state['all25ProtectedInputsUnchanged']
notes=[
 'Complete three-paragraph text and all word clocks read. New fixed base-capability sentence is fully recognized. Unchanged p2 retains 맞힌/마친, 장면이므로/장면임으로 and 읽지는/익지는 uncertainty. The original independent context resolved 장면이므로. Whole-ASR 있습니다/이때 clock overlap27.06–27.22 is resolved by the complete independent paragraph; it is not evidence of overlapping PCM.',
 'Complete three-paragraph text and all word clocks read. Two/six digit spellings preserve meaning. Entire program-behavior sentence and final 있습니다 recognized. Whole-ASR 설계 starts19.22 while actual replacement bytes begin19.29; preserve the actual PCM clock and independent context, never place speech earlier from that estimate.',
 'Entire new p3 expected/actual and all words read. Only spacing/punctuation differs. Fixed capability wording is intact; no complete sentence omission/repetition or lexically missing ending.',
 'Entire new p3 expected/actual and all words read. Only spacing/punctuation differs. 실제 프로그램의 동작과 is intact; no complete sentence omission/repetition or lexically missing ending.'
]
rows=[]
for row,note in zip(state['results'],notes):
 p=FOLDER/'asr'/f"{row['id']}.json"
 assert sha(ROOT/row['path'])==row['sha256']
 rows.append(dict(id=row['id'],kind=row['kind'],resultPath=p.relative_to(ROOT).as_posix(),
   resultSha256=sha(p),audioPath=row['path'],audioSha256=row['sha256'],
   expectedKo=row['expectedKo'],actualFullText=row['text'],
   entireExpectedActualAndAllWordTimestampsRead=True,
   wholeSentenceOmission=False,wholeSentenceRepetition=False,observation=note,
   humanListening='pending',humanPronunciation='pending'))
out=FOLDER/'current-direct-review.json';assert not out.exists()
review=dict(schemaVersion=2,reviewedAt=datetime.now(timezone.utc).isoformat(),
 actualOuterSession=71144,actualOuterExitCode=0,executionSha256=sha(state_path),
 allFourCompleteTextsDirectlyCompared=True,rows=rows,
 changedVoiceReadyForMeasuredPlanning=True,currentCompleteScenes=12,
 unchanged10OriginalScenePcmReused=True,originalTwelvePcmPreserved=True,
 originalWholeReview='projects/character-parameters/production/current-whole-direct-review-v1.json',
 originalIndependentReview='projects/character-parameters/production/current-context-direct-review-v1.json',
 exactOriginalPrefixesAndWholeReplacementBytesMatched=True,
 joinedPrefix08Samples=476640,joinedPrefix09Samples=460560,zeroGapSamplesEach=2400,
 currentParagraphStart08=19.96,currentParagraphStart09=19.29,
 endingObservation='All complete expected endings recognized in whole and independent texts.08 whole recognizer warned about its final timestamp; this is retained as timestamp uncertainty, not diagnosed as an audio truncation. Exact whole new PCM retained without phone removal or retiming.',
 independentPaddingObservation='6000 zero samples each side are retained; word clocks extending into those pads are estimates and not a sample boundary.',
 expectedUsedAsRecognizerPrompt=False,automaticApproval=False,auditoryListeningClaimed=False,
 humanListening='pending',humanPronunciation='pending',
 finalMixedAsrApproved=False,finalTimingApproved=False,allFinalPixelsApproved=False,
 candidateAdopted=False,rasterGitAdditions=0,mediaGitAdditions=0)
out.write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n','utf-8')
print('All four current complete texts and joins directly compared; changed voice ready for measured planning. Human auditory/mixed/final review remain pending.')
