"""Seal the directly read whole paired editorial, then prepare a guarded voice request."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json,os
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent;P=BASE.parent
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8')
now=lambda:datetime.now(timezone.utc).isoformat()
en=read(P/'script/narration.en.json')
en['scenes'][5]['lines'][1]='When both line counts show 27, the displayed scores differ by 2920. In a later shot, the player with fewer cleared lines leads by 141 points.'
save(P/'script/narration.en.json',en)
contract=read(BASE/'visual-contract-v1.json');contract['palette']=read(ROOT/'shared/publishing/explanation-style-policy.json')['palette'];save(BASE/'visual-contract-v1.json',contract)
ko=read(P/'script/narration.ko.json')
assert [(s['id'],len(s['lines'])) for s in ko['scenes']]==[(s['id'],len(s['lines'])) for s in en['scenes']]
assert len(ko['scenes'])==10 and sum(len(s['lines']) for s in ko['scenes'])==30
report=ROOT/'production/batches/sakurai-planning-game-design/preflight/presenting-game-scores.json'
review=dict(schemaVersion=1,slug='presenting-game-scores',reviewedAt=now(),wholeKoAndEnDirectlyRead=True,
 scenes=10,paragraphs=30,pairedWholeTextReview=True,contentReadyForApprovedVoiceMeasurement=True,
 overviewPromiseReview=dict(passed=True,scene='01-overview',naturalSentences=3,targetSeconds=[20,30],
  measuredSeconds=None,centralQuestion=True,viewerOutcome=True,actualOrderedExamples=['Tetris quantity/evaluation','Opponent comparison','Balatro calculation feedback'],firstExample='02-score-and-lines',
  promisesFulfilledBy=['02/03/04/05','06/07','08/09/10']),
 sourceBeforeNarration=True,sourceBank='production/batches/sakurai-planning-game-design/proof-presenting-game-scores/source-action-bank-v4.json',
 observations=[dict(scene=s['id'],koSha256=hashlib.sha256('\n'.join(s['lines']).encode()).hexdigest(),
  enSha256=hashlib.sha256('\n'.join(t['lines']).encode()).hexdigest(),allWholeParagraphsDirectlyCompared=True) for s,t in zip(ko['scenes'],en['scenes'])],
 numericObservation=dict(scene='06-relative-gap',equalLines=27,scoreDifference=2920,laterLead=141,
  evidenceFrames=[dict(source='modern',frame=2915,left=14096,right=17016),dict(source='modern',frame=3455,leftLines=29,rightLines=32,left=19919,right=19778)],
  separateShots=True,finalWinnerNotInferred=True),
 scopeCaveats=['Exact proprietary scoring weights are not inferred from notices.','Illustrative recovered-item tray is an explanation, not adopted gameplay.',
  'Balatro press montage is two short observed shots, not an asserted full continuous calculation or final round total.',
  'Score-reading emphasis does not repeat the existing reward-economy topic.'],
 fullOriginalLectureResearchRead=True,sourceTranscriptCopiedOrTranslatedAsWhole=False,
 duplicateReportSha256=sha(report),duplicateInputsDigest=read(report)['inputsDigest'],
 scriptKoSha256=sha(P/'script/narration.ko.json'),scriptEnSha256=sha(P/'script/narration.en.json'),
 finalNarrationApproval=False,wholeAsrDirectReview=False,finalMixedAsrApproved=False,finalPixelsApproved=False,
 humanListening='pending',humanPronunciation='pending',publicRights='pending',heuristicIsApproval=False)
save(BASE/'paired-script-direct-review-v1.json',review)
m=read(P/'project.json');m['status']='script-reviewed-awaiting-serialized-approved-voice';m['approvals']['wholeScriptReview']='content-ready-for-approved-voice-measurement'
m['editing']['openingOverview']['reviewedBeforeTts']=True
m['tts']['maxNewTokens']=1024
save(P/'project.json',m)
reference=ROOT/m['tts']['reference'];referenceText=ROOT/m['tts']['referenceText']
assert sha(reference)=='2ce15a7e3656f47dc026d780766275de42d8eff99a433b61ec9cccf08e274530'
assert sha(referenceText)=='a258d6f475b673391f0a48bcad2b92800d3adbb33a6aa15f53315b71f46efc17'
paths=['projects/presenting-game-scores/project.json','projects/presenting-game-scores/script/narration.ko.json',
 'projects/presenting-game-scores/script/narration.en.json','projects/presenting-game-scores/planning/outline.md',
 'projects/presenting-game-scores/sources/game-candidates.json','projects/presenting-game-scores/production/paired-script-direct-review-v1.json',
 'projects/presenting-game-scores/production/visual-contract-v1.json',m['tts']['reference'],m['tts']['referenceText']]
request=dict(schemaVersion=1,slug='presenting-game-scores',preparedAt=now(),pairedWholeTextReview=True,overviewPromiseReview=True,
 scriptReview='projects/presenting-game-scores/production/paired-script-direct-review-v1.json',
 queueDir='C:/Users/eazuo/renderformer/tmp/placement_focus_20261008',device='cuda:0',cpuThreads=2,batchSize=1,total=10,
 model=m['tts']['model'],voiceApproval='Existing user-approved Qwen1.7B and exact reference; no new speaker requested',
 protectedInputs=[dict(path=x,sha256=sha(ROOT/x)) for x in paths],scenes=[],
 expectedGpuPolicy='Wait foreign owned lease; finish current research checkpoint/validation/done; own cooperative boundary request; one TTS; restore original queue on success/failure and verify actual resumed state',
 finalVoiceAsrApproved=False,finalMixedAsrApproved=False,measuredTimingApproved=False)
for s in ko['scenes']:
 request['scenes'].append(dict(id=s['id'],title=s['title'],paragraphs=len(s['lines']),text=' '.join(s['lines']),
  path=m['tts']['outputDir']+'/chunks/'+s['id']+'-scene.wav'))
save(BASE/'narration-tts-request-v1.json',request)
c=read(BASE/'latest-checkpoint.json');c.update(recordedAt=now(),stage='whole-paired-script-reviewed-serialized-GPU-request-prepared',
 scriptReviewedForVoice=True,overviewPromiseReviewed=True,ttsStarted=False,
 scriptKoSha256=sha(P/'script/narration.ko.json'),scriptEnSha256=sha(P/'script/narration.en.json'),
 nextAction='Launch single guarded request behind current foreign GPU lease; no model while waiting. Build independent black projected scene code while narration waits/measures.');save(BASE/'latest-checkpoint.json',c)
print(json.dumps(dict(preparedScenes=10,wholePairedReview=True,modelLoaded=False,protectedInputs=len(paths))))
