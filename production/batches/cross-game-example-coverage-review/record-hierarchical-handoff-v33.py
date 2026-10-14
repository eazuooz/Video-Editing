"""Record closed source/native research and the single live additive voice batch."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,subprocess,psutil
ROOT=Path(__file__).resolve().parents[3]
V=ROOT/'projects/hierarchical-game-outlines/revision-teaching-clarity-v1'
R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
B=ROOT/'production/batches/cross-game-example-coverage-review'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for c in iter(lambda:f.read(8*1024*1024),b''):h.update(c)
 return h.hexdigest()
def save(p,x):
 t=p.with_name(p.name+'.'+str(os.getpid())+'.writing')
 t.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf8');os.replace(t,p)
def live(x):
 try:
  p=psutil.Process(x['pid'])
  if abs(p.create_time()-x['createTime'])<.02:return dict(pid=p.pid,createTime=p.create_time(),command=p.cmdline(),cwd=p.cwd())
 except psutil.NoSuchProcess:pass
 return None
out=R/'resource-and-annotation-handoff-v33.json';assert not out.exists()
prior_path=R/'resource-and-annotation-handoff-v32.json';prior=read(prior_path)
source=read(V/'source-acquisition-execution-v2.session.json')
native=read(V/'native-candidate-extraction-execution-v2.session.json')
assert source['actualOuterExitCode']==native['actualOuterExitCode']==0
assert source['exactWorkerDead'] and native['exactWorkerDead'] and native['exactChildrenDead']
direct=read(V/'native-candidate-direct-review-v4.json')
assert direct['totalNewDirectlyReadBoards']==87 and direct['totalCandidateResearchPoints']==870
session=read(V/'narration-additions-session-v1.json');assert session['sessionId']==69732
voice=read(V/'narration-additions-execution-v1.json');assert voice['actualPid']==session['pid']
assert voice['requestSha256']==sha(V/'narration-additions-request-v1.json')
current_worker=live(session)
resource=read(V/'resource-before-additions-voice-v1.json');assert resource['voiceEligibleAtObservation']
for item in resource['protectedInputs']:assert sha(ROOT/item['path'])==item['sha256'],item['path']
main_sha=sha(ROOT/'projects/game-math-orientation-matrices/project.json')
assert main_sha==read(O/'current34-main-schedule-update-v1.json')['afterSha256']
index=ROOT/'.git/index';before=sha(index)
git='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/git/cmd/git.exe'
entries=subprocess.check_output([git,'ls-files','--stage','-z'],cwd=ROOT)
helper=psutil.Process(27140)
assert abs(helper.create_time()-1791509666.8377817)<.02 and helper.cwd()==str(ROOT)
research=Path(resource['research']['statusPath'])
assert sha(research)==resource['research']['statusSha256']=='bbeac85c5f493baec614eeb5fae13f15d8b9b913f58631dce2d2ee211f07b0b8'
confirmation_path=O/'publishing/obsolete-deletion-action-time-confirmation-v1.json';confirmation=read(confirmation_path)
assert confirmation['questionCount']==1 and confirmation['userAnswer'] is None and not confirmation['permanentDeletionExecuted']
lease_path=ROOT/'shared/output/GPU_HANDOFF.json';lease=read(lease_path) if lease_path.exists() else None
if lease and lease['token']==voice['leaseToken']:assert lease['project']=='hierarchical-game-outlines'
cim=subprocess.check_output(['powershell.exe','-NoProfile','-Command',"Get-CimInstance Win32_Process | Where-Object { $_.Name -in @('python.exe','ffmpeg.exe','node.exe') } | Select-Object ProcessId,ParentProcessId,CreationDate,CommandLine | ConvertTo-Json -Depth 3 -Compress"],encoding='utf8',errors='replace')
(V/'handoff-resource-v33.cim.json').write_text(cim,'utf8')
voice=read(V/'narration-additions-execution-v1.json');stamp=datetime.now(timezone.utc).isoformat()
next_text='Reuse single H voice69732 actualPID81000/create1791851762.8460844/state/lease; no duplicateTTS. After actual outerexit verify exactdead/ownedidleleaseclosure/research1088status/129current-transition-safe protected hashes, then whole4 and18complete independent currentPCM ASR once. Source36150/64cb66/a80ebb and native23194/c54402/771c79 are already exit0closed; never wait or rerun them. All870nativepoints151boards are read, with499new/87boards and371exactprior; no repeated extraction/views/sourceplayback. Preserve original12PCM/60KOEN/14pieces/sixEX/white/Nimbus/cat/member. Add editable tracked annotations to evidenced original Museum gaps, measure current timing and unique meaningful ACT60:EX40 allocation without idle/loop/slowdown/shortened good explanation. Then new pixels/audioQA/fouroutputs/singlecaptionedprivateupload/settings/selectGit/currentOct14saved-reopened schedule replacement and corresponding action-time deletion confirmation. Old Motion/Orientation questions already once pending/noanswer; do not repeat/delete. Continue through normal-transform-UV then pause owned continuation; no new lecture/Sakurai6.'
record=dict(schemaVersion=2,recordedAt=stamp,stage='hierarchical-source-research-closed;single-additive-voice-running',
 previousHandoff=dict(path=prior_path.relative_to(ROOT).as_posix(),sha256=sha(prior_path)),
 completedOrientation=dict(prior['completedOrientation'],currentMainSha256=main_sha,mediaUploadPlaybackGitRepeated=0),
 hierarchy=dict(baselineVideoId='jBRt3xatdPk',actualScheduledAt='2026-10-14T09:00:00+09:00',baselineReservationChanged=False,
  baseline49InputsPreserved=True,original12PcmPreserved=True,original60KoEnPreserved=True,original14PiecesPreserved=True,
  originalSixExplanationScenesPreserved=True,whitePalettePreserved=True,continuousNimbusPreserved=True,
  sourceV1ActualSession=92565,sourceV1Exit=0,sourceV2ActualSession=36150,sourceV2ActualCompletion='64cb66',sourceV2Closure='a80ebb exit0',
  sourceV2WorkerDead=True,nativeV1ActualSession=79458,nativeV1Exit=0,nativeV2ActualSession=23194,
  nativeV2ActualCompletion='c54402',nativeV2Closure='771c79 exit0',nativeV2WorkerDead=True,
  nativeCandidateReview='native-candidate-direct-review-v4.json',nativeReviewActual='23e9fe exit0',
  newNativePoints=499,newBoards=87,exactPriorNativePoints=371,exactPriorBoards=64,allCandidatePoints=870,allCandidateBoards=151,
  completedSourceNativeWholeDecodeViewsRepeated=0,timberShortHeld=True,
  newKoEnParagraphs=18,newVoiceItems=4,voiceActualSession=69732,voiceInitial='475ac0',voiceRegistration='8fb098 exit0',
  voiceStatePath='narration-additions-execution-v1.json',voiceState=voice['stage'],voiceCurrentWorker=current_worker,
  voiceCurrentResults=voice['results'],voiceActualOuterExitNotYetObserved=True,
  ownIdleLeaseToken=voice['leaseToken'],ownIdleLease=voice['idleGpu'],newVoiceRequestDuplicated=False,
  fresh129InputsIncludeOrientation78OthersCandidateAndCurrent08bcMain=True,all129ProtectedShaMatched=True,
  originalAnnotationGapAudit='retained-gameplay-annotation-gap-audit-v1.json',newSevenBoundedOriginalRepresentativesReviewed=True,
  originalAnnotationFinalApproval=False,newProductionRenderStarted=False,finalVoiceRatioOrFourGameTeachingApproved=False,
  newActualVideoId=None,newGitDelivery=False,newScheduleReplacement=False),
 activeOwnedMediaWorkers=int(current_worker is not None),currentOwnedGpuJobs=voice['gpuJobs'],
 freshObservedCpuPercent=psutil.cpu_percent(interval=.3),freshAvailableRamBytes=psutil.virtual_memory().available,
 helper9250=dict(pid=helper.pid,createTime=helper.create_time(),command=helper.cmdline(),newServerStarted=False),
 completedResearchStatusSha256=sha(research),researchCompleted=1088,researchWorkerAlive=False,
 foreignResearchPart2LightingLeaseControlsChanged=False,
 currentExternalIndexSha256=before,currentExternalIndexEntriesSha256=hashlib.sha256(entries).hexdigest(),
 oldMotionDelete=prior['oldMotionDelete'],oldOrientationDelete=dict(prior['oldOrientationDelete'],currentConfirmationSha256=sha(confirmation_path)),
 humanWholeListeningApproved=False,humanPronunciationApproved=False,publicRightsApproved=False,
 optionalCcPropagationPending=True,automaticDubbingHumanReviewPending=True,newGitImages=0,newGitMedia=0,next=next_text)
record['boundHierarchyRecords']=[dict(path=(V/n).relative_to(ROOT).as_posix(),sha256=sha(V/n)) for n in [
 'native-candidate-direct-review-v4.json','source-acquisition-execution-v2.session.json','native-candidate-extraction-execution-v2.session.json',
 'retained-gameplay-annotation-gap-audit-v1.json','source-action-planning-direct-review-v1.json',
 'causal-paired-script-direct-review-v1.json','tts-additions-manifest-v1.json','narration-additions-request-v1.json',
 'narration-additions-session-v1.json','resource-before-additions-voice-v1.json']]
assert sha(index)==before and subprocess.check_output([git,'ls-files','--stage','-z'],cwd=ROOT)==entries
record['externalIndexBytesAndEntriesPreserved']=True;save(out,record)
for p in [V/'latest-checkpoint.json',R/'latest-checkpoint.json']:
 raw=p.read_bytes();cp=read(p);cp.update(recordedAt=stamp,latestHandoff=out.relative_to(ROOT).as_posix())
 if p.parent==R:cp.update(activeContinuationSlug='hierarchical-game-outlines',activeContinuationOwnedWorkers=record['activeOwnedMediaWorkers'],next=next_text)
 assert p.read_bytes()==raw;save(p,cp)
qp=B/'queue.json';raw=qp.read_bytes();q=read(qp)
q['currentHierarchicalReview'].update(latestHandoff=out.relative_to(ROOT).as_posix(),additionalSourceWorkerDead=True,
 additionalNativeWorkerDead=True,additionalNativePointsReviewed=499,additionalNativeBoardsReviewed=87,
 causalScriptReview=(V/'causal-paired-script-direct-review-v1.json').relative_to(ROOT).as_posix(),
 currentProtectedInputCount=129,activeOwnedWorkers=record['activeOwnedMediaWorkers'])
q.update(updatedAt=stamp,currentResourceHandoff=out.relative_to(ROOT).as_posix(),next=next_text)
assert qp.read_bytes()==raw;save(qp,q)
print(json.dumps(dict(handoff=out.relative_to(ROOT).as_posix(),voiceSession=69732,currentWorker=current_worker,
 sourceNativeWorkersClosed=True,all870CandidatePointsReviewed=True,all129ProtectedShaMatched=True,indexPreserved=True)))
