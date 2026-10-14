"""Prepare only three additive bridge chunks; protect the completed eight."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,copy,subprocess
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
def new(p,d):
 assert not p.exists(),p
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf-8')
node='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
subprocess.run([node,'scripts/review-video-duplicates.cjs','limited-color-world','--check'],cwd=ROOT,check=True)
originalRequest=read(BASE/'narration-tts-request-v1.json')
for x in originalRequest['protectedInputs']:assert sha(ROOT/x['path'])==x['sha256']
voice=read(BASE/'narration-tts-execution-v1.json')
assert voice['actualOuterExitCode']==0 and voice['researchResumeVerified'] and voice['generationComplete']
asr=read(BASE/'current-independent-voice-direct-review-v1.json')
assert asr['boundedCurrent8VoiceTextReviewComplete']
plan=read(ROOT/'projects/limited-color-world/planning/causal-chain-additions-v1.json')
paired=read(BASE/'causal-bridge-paired-direct-review-v1.json')
assert paired['all3PairedBridgeParagraphsDirectlyRead'] and paired['original24ParagraphsAndOrderPreserved']
bankPath=ROOT/'production/batches/sakurai-planning-game-design/proof-limited-color-world/source-action-bank-v2.json'
bank=read(bankPath);assert len(bank['windows'])==31 and bank['maximumUniqueSeconds']==141.25 and bank['sourceAdoptionApproved']
stamp=datetime.now(timezone.utc).isoformat(); ids=[x['id'] for x in plan['preparedAdditions']]
koPath=ROOT/'projects/limited-color-world/script/causal-bridges.v1.ko.json';enPath=ROOT/'projects/limited-color-world/script/causal-bridges.v1.en.json'
titles=['윤곽에서 상태 변화로','경계에서 밝기 차이로','단서에서 실제 확인으로']
for language,p in [('ko',koPath),('en',enPath)]:
 new(p,dict(title='색이 달라도 읽히는 화면: 추가 연결 해설',language=language,additiveOnly=True,
 scenes=[dict(id=x['id'],title=titles[i],lines=x[language]) for i,x in enumerate(plan['preparedAdditions'])]))
manifest=copy.deepcopy(read(ROOT/'projects/limited-color-world/project.json'))
outDir='shared/output/narration/limited-color-world/qwen3-1.7b-causal-bridges-v1'
manifest['paths']['script']=rel(koPath);manifest['paths']['scriptEn']=rel(enPath)
manifest['tts'].update(outputDir=outDir,filenameStem='limited-color-world-qwen3-1.7b-causal-bridges-v1',sceneGapSeconds=.72)
manifest.update(status='additive-three-bridge-voice-measurement-only',original8PcmProtected=True,standaloneUploadAllowed=False)
manifestPath=BASE/'causal-bridge-tts-manifest-v1.json';new(manifestPath,manifest)
readyPath=BASE/'causal-bridge-voice-ready-review-v1.json'
new(readyPath,dict(schemaVersion=1,reviewedAt=stamp,all3PairedBridgeParagraphsDirectlyRead=True,original24ParagraphsAndOrderPreserved=True,
 original8PcmAnd32AsrPreserved=True,originalOwnHandoffVerified=True,contentReadyForApprovedVoiceMeasurement=True,
 priorPairedReview=rel(BASE/'causal-bridge-paired-direct-review-v1.json'),priorPairedReviewSha256=sha(BASE/'causal-bridge-paired-direct-review-v1.json'),
 sourceBank=rel(bankPath),sourceBankSha256=sha(bankPath),sourceBoundedPlanningScope=True,finalMeasuredRatioApproved=False,finalContinuousFlowApproved=False,publicRightsApproved=False))
request=copy.deepcopy(originalRequest)
request.update(preparedAt=stamp,total=3,paragraphs=3,scriptReview=rel(readyPath),manifestOverride=rel(manifestPath),additiveOnly=True,
 retainedOriginalVoiceSeconds=voice['totalRawSceneSeconds'],original8NotRegenerated=True,sourceBankMaximumUniqueSeconds=141.25,
 measuredAllocationPending=True,overviewPromiseReview=True,
 scenes=[dict(id=x['id'],title=titles[i],paragraphs=1,text=' '.join(x['ko']),path=f"{outDir}/chunks/{x['id']}-scene.wav") for i,x in enumerate(plan['preparedAdditions'])])
more=[ROOT/'projects/limited-color-world/planning/causal-chain-additions-v1.json',BASE/'causal-bridge-paired-direct-review-v1.json',bankPath,
 ROOT/'projects/limited-color-world/sources/game-candidates-v2.json',koPath,enPath,manifestPath,readyPath,BASE/'current-independent-voice-direct-review-v1.json',BASE/'research-handoff-verification-v1.json']
more += [ROOT/x['path'] for x in voice['results']]
for x in more:request['protectedInputs'].append(dict(path=rel(x),sha256=sha(x)))
requestPath=BASE/'causal-bridge-tts-request-v1.json';new(requestPath,request)
source=(BASE/'render-voice-v1.py').read_text('utf-8')
replacements={
 "narration-tts-execution-v1.json":"causal-bridge-tts-execution-v1.json",
 "narration-tts-request-v1.json":"causal-bridge-tts-request-v1.json",
 "narration-tts-session-v1.json":"causal-bridge-tts-session-v1.json",
 "narration-tts-waiting-v1.json":"causal-bridge-tts-waiting-v1.json",
 "request['total']==8 and request['paragraphs']==24":"request['total']==3 and request['paragraphs']==3",
 "rn.configure_project('limited-color-world')":"rn.configure_project('limited-color-world',request['manifestOverride'])",
 "Prepared8 scenes/24 paragraphs":"Prepared3 additive bridge scenes/3 paragraphs",
 "total=8":"total=3",
 "ttsStarted=True":"bridgeTtsStarted=True",
 "eight-scenes-measured-awaiting-full-ASR":"three-additive-bridges-measured-awaiting-full-ASR",
 "single-GPU-approved-voice-measurement":"single-GPU-additive3bridge-voice-measurement",
 "Observe exact own lease/PID/log. After TTS exit verify original research resume, then whole current-hash ASR plus independent contexts and measured source allocation.":"Observe the additive3bridge lease/PID/log. After actual exit verify original research resume, then review only new3 current-hash whole/context ASR and measured31window allocation. Original8PCM/32ASR remain preserved."
 }
for a,b in replacements.items():assert a in source,a;source=source.replace(a,b)
worker=BASE/'render-causal-bridge-voice-v1.py';assert not worker.exists();worker.write_text(source,'utf-8')
verify=(BASE/'verify-own-voice-research-resume-v1.py').read_text('utf-8')
for a,b in {'narration-tts-session-v1.json':'causal-bridge-tts-session-v1.json','narration-tts-execution-v1.json':'causal-bridge-tts-execution-v1.json','research-handoff-verification-v1.json':'causal-bridge-research-handoff-verification-v1.json',"state['total']==8":"state['total']==3",'allEightCurrentPcmHashesMatched':'allThreeCurrentPcmHashesMatched','eight-scene':'three-bridge'}.items():
 assert a in verify,a;verify=verify.replace(a,b)
verifier=BASE/'verify-causal-bridge-research-resume-v1.py';assert not verifier.exists();verifier.write_text(verify,'utf-8')
print(json.dumps(dict(request=rel(requestPath),sha256=sha(requestPath),worker=rel(worker),workerSha256=sha(worker),scenes=3,original8Preserved=True,modelOrStateCreated=0)))
