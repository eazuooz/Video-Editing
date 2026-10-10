"""Adopt only the current directly reviewed measured inputs; later gates stay false."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,subprocess
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent;FINAL=BASE/'final-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rel=lambda p:p.relative_to(ROOT).as_posix();now=lambda:datetime.now(timezone.utc).isoformat()
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf-8')
assert not (FINAL/'plan.json').exists(),'Continue actual checkpoint without repeating adoption'
subprocess.run(['C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe','scripts/review-video-duplicates.cjs','character-parameters','--check'],cwd=ROOT,check=True)
RP=BASE/'selected-input-direct-review-v4.json';review=read(RP);PF=BASE/'selected-input-preflight-v4.json';pre=read(PF);execution=read(BASE/'selected-input-repair-execution-v4.json')
assert execution['exitCode']==execution['outerExitCode']==0 and execution['outerExitDirectlyObserved'] and execution['sessionClosed']
assert review['allBoardsDirectlyRead'] and review['allInputCaptionPixelsReviewed'] and not review['unresolvedDefects'] and review['sourceAllocationApproved'] and review['preflightSha256']==sha(PF)
assert pre['allBodyPtsVerified'] and pre['allSamplePtsVerified'] and pre['wholeBodyDecodeExitCode']==pre['extractionExitCode']==0
for item in [*pre['segments'],*pre['samples'],*pre['boards']]:assert sha(ROOT/item['path'])==item['sha256'],item['path']
assert sha(ROOT/pre['bodyPath'])==pre['bodySha256']
PP=ROOT/pre['plan'];CP=ROOT/pre['captionCandidate'];plan=read(PP);cap=read(CP)
assert sha(PP)==pre['planSha256'] and sha(CP)==pre['captionCandidateSha256']
assert (plan['actualFrames'],plan['explanationFrames'],plan['bodyFrames'],plan['finalFrames'])==(13606,9071,22677,23397) and abs(plan['bodyRatioFrameError'])<=1
assert cap['allCurrent37KoEnParagraphsRetained'] and cap['all35UnchangedParagraphsPreserved'] and (len(cap['ko']),len(cap['en']))==(201,95)
voice=read(ROOT/plan['currentVoiceSelection']);assert sha(ROOT/plan['currentVoiceSelection'])==plan['currentVoiceSelectionSha256'] and voice['currentCompleteVoiceReadyForMeasuredPlanning']
for v in voice['scenes']:assert sha(ROOT/v['path'])==v['sha256']
samples=sum(v['samples']for v in voice['scenes']);assert samples==8430001 and sum(v['samples']for v in plan['voicePlacements'])==samples and len(plan['voicePlacements'])==17
assert all(v['exactCoverage'] and v['removedSamples']==v['repeatedSamples']==0 for v in plan['exactPcmCoverage'])
FINAL.mkdir(exist_ok=True)
plan.update(schemaVersion=1,adoptedAt=now(),candidatePlan=rel(PP),candidatePlanSha256=sha(PP),selectedInputReview=rel(RP),selectedInputReviewSha256=sha(RP),selectedInputPreflight=rel(PF),selectedInputPreflightSha256=sha(PF),bodySilent=pre['bodyPath'],bodySilentSha256=pre['bodySha256'],selectedInputSegments=pre['segments'],captionCandidate=rel(CP),captionCandidateSha256=sha(CP),captions=rel(FINAL/'captions.json'),narrationSamples=samples,membershipStartFrame=22797,body60_40ErrorFrames=abs(plan['bodyRatioFrameError']),bodyRatioApproved=True,finalTimingApproved=True,allInputSegmentCaptionPixelsReviewed=True,finalPlanAdopted=True,preparedOnly=False,style='research-black-v1')
save(FINAL/'plan.json',plan)
cap.update(adoptedAt=now(),candidatePath=rel(CP),candidateSha256=sha(CP),allCurrentCueTextsDirectlyRead=True,allInputCuePixelsReviewed=True,inputReview=rel(RP),finalTimingApproved=True,timingApprovalScope='Current literal full37 KOEN paragraphs and measured word/PCM timing; all planned input pixels. Human pronunciation/listening pending.',allCuePixelsReviewed=False,allFinalPixels=False)
save(FINAL/'captions.json',cap)
for src,dst in [('candidate.ko.srt','character-parameters.ko.srt'),('candidate.en.srt','character-parameters.en.srt')]: (FINAL/dst).write_bytes((CP.parent/src).read_bytes())
mp=BASE.parent/'project.json';m=read(mp);m['status']='reviewed-inputs-final-mix-pending';m['video']['durationSeconds']=plan['durationSeconds']
m['editing'].update(timingStatus='measured-final-inputs-adopted',actualGameplaySeconds=13606/60,actualExplanationSeconds=9071/60,actualGameplayShare=13606/22677,actualCommercialGameplaySeconds=13606/60,finalPlan=rel(FINAL/'plan.json'),finalPlanSha256=sha(FINAL/'plan.json'),actualFrames=13606,explanationFrames=9071,bodyFrames=22677,finalFrames=23397,bodyRatioFrameError=plan['bodyRatioFrameError'],currentScriptParagraphs=37,originalScriptParagraphsPreserved=35,inputPixelReview=rel(RP))
music=ROOT/'shared/assets/music/youtube-audio-library/Nimbus-Eveningland-restored.m4a';assert sha(music)=='36a0c40b73e7dc656470c242cce0047bd987abc595f28b013265d947a10d98ef'
m['audio'].update(mixStatus='current37-PCM-final-mix-pending',currentNarrationSamples=samples,currentNarrationSeconds=samples/24000)
m['audio']['backgroundMusic'].update(approvalStatus='approved-continuous-Nimbus-by-user-production-defaults',file=rel(music),sha256=sha(music),originalLibraryFileApproval='pending',missingOriginalMp3ReferencePreserved='shared/assets/music/youtube-audio-library/Nimbus-Eveningland.mp3')
m['paths'].update(narration=rel(FINAL/'narration-timed.wav'),audioMix=rel(FINAL/'final-mix.m4a'),captionsKo=rel(FINAL/'character-parameters.ko.srt'),captionsEn=rel(FINAL/'character-parameters.en.srt'),videoClean=rel(FINAL/'character-parameters.clean.mp4'),videoBurnedCaptions=rel(FINAL/'character-parameters.captioned.mp4'))
m.setdefault('approvals',{}).update(finalTiming=True,bodyRatio=True,inputCaptionPixels=True,finalMixedAsr=False,allFinalPixels=False,humanListening=False,publicRights=False);save(mp,m)
cp=read(BASE/'latest-checkpoint.json');job=dict(status='closed-repaired-input-review-approved',pid=execution['pid'],createTime=execution['createTime'],sessionId=execution['sessionId'],state=rel(BASE/'selected-input-repair-execution-v4.json'),exitCode=0,outerExitDirectlyObserved=True,workerExpectedRunning=False,cpuThreads=2,gpu=0)
cp.update(recordedAt=now(),stage='reviewed-final-inputs-Nimbus-mix-pending',ownedJob=job,finalTimingApproved=True,allInputSegmentCaptionPixelsReviewed=True,finalPlan=rel(FINAL/'plan.json'),selectedInputReview=rel(RP),scenes=12,paragraphs=37,nextAction='SingleCPU2 exact current PCM/Nimbus mix; current12 whole and independent complete mixed contexts, then guarded pair/final pixels/QA/collection/private/Git/schedule.');save(BASE/'latest-checkpoint.json',cp)
qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qp);i=next(x for x in q['items']if x['slug']=='character-parameters');i.update(stage=cp['stage'],currentExecution=job,finalPlan=rel(FINAL/'plan.json'),selectedInputReview=rel(RP),nextAction=cp['nextAction']);i['checkpoints'].update(narration=True,footage=True,scenes=True,mix=False,render=False,qa=False,collected=False);q['updatedAt']=now();save(qp,q)
save(BASE/'final-input-adoption-v1.json',dict(adoptedAt=now(),plan=rel(FINAL/'plan.json'),planSha256=sha(FINAL/'plan.json'),review=rel(RP),reviewSha256=sha(RP),captionsSha256=sha(FINAL/'captions.json'),frames=23397,seconds=389.95,koCues=201,enCues=95,allInputPixelsReviewed=True,finalMixedAsrApproved=False,allFinalPixels=False,qa=False,collected=False,private=False,actualId=None,newMedia=0,newImagesGitAdded=0,newTts=0,researchControlChanges=0))
print(json.dumps(dict(frames=23397,seconds=389.95,narrationSamples=samples,finalMixedAsrApproved=False)))
