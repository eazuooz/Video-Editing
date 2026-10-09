"""Adopt only directly reviewed current31 inputs; preserved baseline is untouched."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,subprocess
ROOT=Path(__file__).resolve().parents[3];P=Path(__file__).parent;B=P/'revision-balatro60-v2';F=B/'final-v3'
read=lambda p:json.loads(p.read_text('utf-8-sig'));rel=lambda p:p.relative_to(ROOT).as_posix()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
now=lambda:datetime.now(timezone.utc).isoformat()
def save(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
assert not (F/'plan.json').exists()
subprocess.run(['C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe','scripts/review-video-duplicates.cjs','presenting-game-scores','--check'],cwd=ROOT,check=True)
pfp=B/'selected-input-preflight-v4.json';pf=read(pfp);progressp=B/'selected-input-direct-progress-v4.json';progress=read(progressp)
assert progress['directlyReadBoardNumbers']==list(range(1,len(pf['boards'])+1))
assert progress['directlyReadSampleCount']==len(pf['samples']) and not progress['unresolvedIssues']
assert progress['sourceSha256']==sha(pfp)
assert progress['equalityCorrectionDirectlyReviewed']
correctionp=B/'source-equality-correction-v1.json';correction=read(correctionp)
assert correction['oldAnnotationDisproved'] and correction['replacement']['sourceStartFrame']==2050 and correction['replacement']['sourceEndFrameExclusive']==2525
for x in correction['directlyReadEvidence']:assert x['directlyRead'] and sha(ROOT/x['path'])==x['sha256']
assert pf['allBodyPtsVerified'] and pf['allSamplePtsVerified'] and pf['wholeBodyDecodeExitCode']==pf['extractionExitCode']==0
for x in [*pf['boards'],*pf['samples'],*pf['segments']]:assert sha(ROOT/x['path'])==x['sha256']
assert sha(ROOT/pf['bodyPath'])==pf['bodySha256']
planp=ROOT/pf['plan'];capp=ROOT/pf['captionCandidate'];plan=read(planp);cap=read(capp)
assert sha(planp)==pf['planSha256'] and sha(capp)==pf['captionCandidateSha256']
vp=ROOT/plan['voiceSelection'];voice=read(vp);assert sha(vp)==plan['voiceSelectionSha256'] and voice['currentCompleteVoiceApproved']
assert (plan['actualFrames'],plan['explanationFrames'],plan['balatroFrames'],plan['tetrisFrames'],plan['bodyFrames'],plan['finalFrames'])==(11561,7707,6936,4625,19268,19988)
assert abs(plan['bodyRatioFrameError'])<=1 and abs(plan['gameRatioFrameError'])<=1
assert cap['allCurrentCueTextsDirectlyRead'] and cap['allLiteralKoEn39ParagraphsPreserved']
assert len(cap['ko'])==175 and len(cap['en'])==70 and len(cap['chunks'])==42
assert sum(p['samples'] for p in plan['voicePlacements'])==6691203
assert all(not x['removedSamples'] and not x['repeatedSamples'] for x in plan['exactPcmCoverage'])
reviewp=B/'selected-input-direct-review-v4.json'
review=dict(schemaVersion=4,reviewedAt=now(),preflight=rel(pfp),preflightSha256=sha(pfp),progress=rel(progressp),progressSha256=sha(progressp),
 sourceEqualityCorrection=rel(correctionp),sourceEqualityCorrectionSha256=sha(correctionp),equalityCorrectionDirectlyReviewed=True,
 planSha256=sha(planp),captionCandidateSha256=sha(capp),bodySha256=pf['bodySha256'],boards=pf['boards'],sampleCount=len(pf['samples']),
 allBoardsDirectlyRead=True,allInputCaptionPixelsReviewed=True,sourceAllocationApproved=True,allCurrentCueTextsDirectlyRead=True,
 cuts=31,blackMotionSegments=13,koCueCount=175,enCueCount=70,logicalParagraphs=39,semanticChunks=42,
 observations=progress['observations'],unresolvedDefects=[],
 scope='All planned current cue/cut/complete-clause/spatial-motion pixels and outside-game recorder credit directly read. Not every native continuous frame or final pair/human pronunciation.',
 allFinalPixels=False,finalMixedAsrApproved=False,humanListening='pending',humanPronunciation='pending',publicRights='pending',localOnlyImages=True,imagesGitAdded=0)
save(reviewp,review);F.mkdir()
plan.update(schemaVersion=4,adoptedAt=now(),candidatePlan=rel(planp),candidatePlanSha256=sha(planp),selectedInputReview=rel(reviewp),selectedInputReviewSha256=sha(reviewp),
 sourceEqualityCorrection=rel(correctionp),sourceEqualityCorrectionSha256=sha(correctionp),equalityCorrectionDirectlyReviewed=True,
 selectedInputPreflight=rel(pfp),selectedInputPreflightSha256=sha(pfp),bodySilent=pf['bodyPath'],bodySilentSha256=pf['bodySha256'],selectedInputSegments=pf['segments'],
 captionCandidate=rel(capp),captionCandidateSha256=sha(capp),captions=rel(F/'captions.json'),narrationSamples=6691203,
 body60_40ErrorFrames=abs(plan['bodyRatioFrameError']),bodyRatioApproved=True,gameMixRatioApproved=True,finalTimingApproved=True,
 allInputSegmentCaptionPixelsReviewed=True,finalPlanAdopted=True,preparedOnly=False,membershipStartFrame=19388,style='research-black-v1')
save(F/'plan.json',plan)
cap.update(adoptedAt=now(),candidatePath=rel(capp),candidateSha256=sha(capp),allCurrentCueTextsDirectlyRead=True,allInputCuePixelsReviewed=True,
 inputReview=rel(reviewp),finalTimingApproved=True,allCuePixelsReviewed=False,allFinalPixels=False)
save(F/'captions.json',cap)
for lang in ['ko','en']:(F/f'presenting-game-scores.{lang}.srt').write_bytes(capp.with_name(f'candidate.{lang}.srt').read_bytes())
mp=P.parent/'project.json';m=read(mp)
m['currentRevision'].update(finalPlan=rel(F/'plan.json'),finalPlanSha256=sha(F/'plan.json'),inputPixelReview=rel(reviewp),
 currentVoiceApproved=True,finalTimingApproved=True,gameMixRatioApproved=True,bodyRatioApproved=True,finalMixedAsrApproved=False,allFinalPixels=False,
 actualFrames=11561,explanationFrames=7707,balatroFrames=6936,tetrisFrames=4625,bodyFrames=19268,finalFrames=19988,durationSeconds=19988/60)
m['currentRevision']['checkpoints'].update(additionalSources=True,currentDuplicateReview=True,
 revisedScript=True,voice=True,voiceAsr=True,measuredTiming=True,gameMixRatio=True,bodyRatio=True)
save(mp,m)
cp=read(P/'latest-checkpoint.json');cp.update(recordedAt=now(),stage='revision-reviewed-inputs-Nimbus-mix-pending',revisionFinalPlan=rel(F/'plan.json'),
 finalTimingApproved=True,allInputSegmentCaptionPixelsReviewed=True,finalMixedAsrApproved=False,pairRendered=False,allFinalPixels=False,qa=False,collected=False,
 nextAction='SingleCPU2 current exactPCM/Nimbus mix, then10 whole and42 independent complete mixed contexts. Guarded pair/all pixels/QA/collection/new private/Git/schedule afterward.')
cp['revisionCheckpoints'].update(voice=True,voiceAsr=True,measuredTiming=True,gameMixRatio=True,bodyRatio=True)
save(P/'latest-checkpoint.json',cp)
print(json.dumps(dict(inputsAdopted=True,frames=19988,seconds=19988/60,finalMixedAsrApproved=False)))
