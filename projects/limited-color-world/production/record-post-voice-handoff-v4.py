"""Record actual exit/restoration and the current single CPU ASR; no approval."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,psutil
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
PROOF=ROOT/'production/batches/sakurai-planning-game-design/proof-limited-color-world'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
req=read(BASE/'narration-tts-request-v1.json')
assert all(sha(ROOT/r['path'])==r['sha256'] for r in req['protectedInputs'])
tts=read(BASE/'narration-tts-execution-v1.json');restore=read(BASE/'research-handoff-verification-v1.json')
assert tts['actualOuterSession']==91184 and tts['actualOuterExitCode']==0 and tts['actualExitObserved']
assert restore['restorationVerified'] and restore['ownedCoordinatorClosed']
assert all(sha(ROOT/r['path'])==r['sha256'] for r in tts['results'])
asr=read(BASE/'current-whole-asr-execution-v1.json');session=read(BASE/'current-whole-asr-execution-v1.session.json')
p=psutil.Process(asr['pid']);assert abs(p.create_time()-asr['createTime'])<.01
assert session['sessionId']==62160 and session['pid']==p.pid
source=read(PROOF/'additional-action-editorial-review-v3.json')
assert sum(r['candidateSeconds'] for r in source['candidates'])==source['totalPotentialSeconds']==32
bank=PROOF/'source-action-bank-v1.json';assert sha(bank)==source['protectedOriginalBankSha256']
ax=PROOF/'chicory-trimmed-v3-after-resource-change.ax.txt';assert ax.exists()
limitation=dict(schemaVersion=4,recordedAt=datetime.now(timezone.utc).isoformat(),
    currentBrowser='3',nativeTab='40',helper='http://127.0.0.1:9250/limited-chicory-trimmed-framing-v3.html',
    priorLimitation=rel(PROOF/'chicory-trimmed-playback-limitation-v3.json'),
    afterMemoryFreedCaptureAttempt='Page.captureScreenshot timed out; no screenshot returned or saved.',
    documentedSemanticPlayAttempt='Input.dispatchMouseEvent timed out; fresh AX remained outline-room at155 seconds paused.',
    subsequentAx=rel(ax),subsequentAxSha256=sha(ax),
    observedNewStartEvents=0,observedNewEndEvents=0,continuousTrimmedPlaybackApproved=False,
    allIntermediateFramesReviewed=False,finalCueApproval=False,helperRebuilt=False,serverRestarted=False,
    sourceMediaChanged=False,repeatInputWithoutStateChange=False,
    nextAction='Use supported CUA state/recovery when the actual browser state changes; preserve completed sample/native scope and do not claim the failed input ran playback.')
lp=PROOF/'chicory-trimmed-playback-limitation-v4.json';assert not lp.exists()
lp.write_text(json.dumps(limitation,ensure_ascii=False,indent=2)+'\n','utf-8')
snapshot=dict(schemaVersion=4,recordedAt=datetime.now(timezone.utc).isoformat(),
    actualOuterSession=91184,actualOuterExitCode=0,toolExitObservation='dbaff5',
    currentTtsExecution=rel(BASE/'narration-tts-execution-v1.json'),currentTtsExecutionSha256=sha(BASE/'narration-tts-execution-v1.json'),
    measured8PcmSeconds=sum(r['seconds'] for r in tts['results']),all8PcmHashesMatched=True,
    overviewMeasuredSeconds=tts['results'][0]['seconds'],heuristicIsApproval=False,wholeNarrationDirectReview=False,
    restoration=rel(BASE/'research-handoff-verification-v1.json'),restorationSha256=sha(BASE/'research-handoff-verification-v1.json'),
    restorationVerifierExitCode=0,restorationVerifierToolObservation='b76560',
    resumedResearch=restore['observedResumedIdentity'],observedResumedStatus=restore['currentResumedStatus'],
    completedTrainingJobEvidence=restore['completedResearchJobEvidence'],foreignRestorationNotClaimedAsOwn=True,
    originalFailedSession1912Preserved=True,firstFailureBeforeModelOrPcm=True,
    protected10InputsAllMatched=True,ownAsr=dict(sessionId=62160,pid=p.pid,createTime=p.create_time(),command=p.cmdline(),cwd=p.cwd(),
        mode='whole',cpuThreads=2,gpuJobs=0,state=rel(BASE/'current-whole-asr-execution-v1.json'),log=rel(BASE/'current-whole-asr-v1.log'),
        completedAtSnapshot=asr['completed'],total=8,actualExitObserved=False),
    currentDuplicateInputsDigest='176082991351a51cef66607e137ab02342f865315e10ba627406f021721a9411',
    duplicateCheckExitCode=0,duplicateCheckToolObservation='66bf63',
    preparedOriginalScenes=8,preparedCausalBridgeScenes=3,scopedTypescriptExitCode=0,scopedTypescriptToolObservation='7309d4',
    bridgePcmCreated=False,prototypePixelApproval=False,continuousNarrationMotionApproval=False,
    sourceBankSha256=sha(bank),sourceBankUniqueSeconds=101.5,sourceApprovalScope='Previously reviewed native selected samples and framing; not all continuous/final cue pixels or public rights.',
    additionalActionReview=rel(PROOF/'additional-action-editorial-review-v3.json'),additionalActionReviewSha256=sha(PROOF/'additional-action-editorial-review-v3.json'),
    additionalPotentialSeconds=32,additionalAdoption=False,
    priorManual49Point5CorrectedToActualPlan49AndEditorial32=True,measuredRatioApproved=False,
    browserPlaybackLimitation=rel(lp),thumbnailPrepared=True,platformThumbnailSaved=False,actualId=None,
    finalTiming=False,mixedAsr=False,allFinalPixels=False,qa=False,collected=False,uploaded=False,gitDelivered=False,scheduled=False,
    nextAction='Observe62160 actual exit and read every full recognized text vs current8PCM/24paragraphs. Prepare whole-sentence independent currentPCM contexts and one additive3bridge request only after direct original voice review. Secure enough useful unique normal-speed action through native before/action/after and fixed-caption checks, then measured60:40, narration-timed black2.5D, mix/fullmixedASR/finalpixels/QA/collection/private/settings/selectiveGit/09KSTschedule.')
out=BASE/'prepared-handoff-resource-verification-v4.json';assert not out.exists()
out.write_text(json.dumps(snapshot,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(actualTtsExit=0,session=91184,measuredSeconds=snapshot['measured8PcmSeconds'],restoration=True,
    asrSession=62160,actualAsrPid=p.pid,additionalPotentialSeconds=32,additionalAdoption=False,protected10=True)))
