"""Record actual closed read-only observation and completed content review."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os

ROOT = Path(__file__).resolve().parents[3]
B = Path(__file__).resolve().parent
R = ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
now = lambda: datetime.now(timezone.utc).isoformat()
def save(p, obj):
    tmp=p.with_name(p.name+f'.{os.getpid()}.writing')
    tmp.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n','utf-8')
    os.replace(tmp,p)

dest=R/'resource-and-annotation-handoff-v13.json'
assert not dest.exists(), 'Inspect already recorded result rather than repeating.'
resource_path=R/'voice-retry-resource-verification-v12.json'
resource=read(resource_path)
review_path=R/'duplicate-content-and-studio-direct-review-v8.json'
review=read(review_path)
assert resource['all68ProtectedHashesMatched'] and resource['processOrPauseOrLeaseMutations']==0
assert not resource['voiceRequestEligible'] and not resource['stableGpuIdle20SecondsVerified']
assert review['verdict']=='distinct' and review['allChangedContentsReviewed']
assert review['currentWholeStudioReviewComplete'] and review['inventoryInputCount']==499
for row in review['changedInputs']+resource['protectedInputs']:
    assert sha(ROOT/row['path'])==row['sha256'],row['path']
request=read(R/'narration-tts-request-v1.json')
assert not any((ROOT/row['path']).exists() for row in request['scenes'])
check=dict(schemaVersion=1,recordedAt=now(),review=review_path.relative_to(ROOT).as_posix(),
    reviewSha256=sha(review_path),inventoryDigest=review['inventoryDigest'],
    actualDecisionChunk='020bc1',actualCheckChunks=['11b471'],
    actualCheckExitCode=0,actualCheckOutput='motion-sickness-games: current pre-production content and Studio duplicate review passed.',
    appliesToRecordedInventoryOnly=True,futureChangedInputsRequireFullReview=True)
check_path=R/'duplicate-current-check-verification-v8.json'
assert not check_path.exists()
save(check_path,check)
next_step=('ObserverV12 completed65366/exit0 with29samples/56seconds and stable20s=false; no voice request. '
    'Do not run preparedV6 against falseV11; no request using currentfalseV12 or repeat completed observers/pilots. At a later real resource opportunity '
    'follow exact restoration lineage and make one fresh read-only observation referencingV12. Require currentidentity/noforeignlease/stable20s/68SHA; '
    'recheck currentduplicate immediately before one new-version wrapper request with exact resource reference. '
    'Preserve coordinator20s/600s guard and verify actual success/failure originalcommandcwd resume. '
    'Then whole3/independent15 currentPCM ASR, exact60:40, narrated annotations/mix/currentQA/4files/private/settings/Git/same09schedule before matchingobsolete deletion.')
handoff=dict(schemaVersion=1,recordedAt=now(),observer=dict(sessionId=65366,actualOuterExitCode=0,
    actualCompletionChunk='3444de',path=resource_path.name,sha256=sha(resource_path),observedAt=resource['observedAt'],
    samples=len(resource['gpuObservations']),stableGpuIdle20SecondsVerified=False,voiceRequestEligible=False),
    currentOriginalResearchAtObservation=resource['currentOriginalResearch'],
    currentOriginalResearchStatusAtObservation=resource['currentResearchStatus'],
    restorationScope=resource['restorationScope'],subsequentForeignRestorationLinks=len(resource['subsequentForeignRestorationLineage']),
    currentForeignLeaseAtObservation=resource['currentForeignLease'],
    duplicateReview=review_path.name,duplicateReviewSha256=sha(review_path),currentDuplicateCheckPassed=True,
    duplicateCheckVerification=check_path.name,inventoryDigest=review['inventoryDigest'],projects=87,inputs=499,
    all68ProtectedInputsMatched=True,preparedVoiceVersion=6,preparedVoiceRequestStarted=False,
    sourceOrPilotOrQaReexecutions=0,newRequestOrModelOrPcmOrMedia=0,
    foreignProcessOrPauseOrLeaseOrPlatformMutations=0,gitActions=0,allFinalApprovals=False,next=next_step)
save(dest,handoff)
cp_path=R/'latest-checkpoint.json';cp_raw=cp_path.read_text('utf-8-sig');cp=json.loads(cp_raw)
cp.update(recordedAt=now(),stage='content-and-studio-distinct-passed-resource-idle-not-stable',
    currentHandoff=dest.name,currentDuplicateReview=review_path.name,currentDuplicateCheckPassed=True,
    currentDuplicateReviewPending=None,currentDuplicateCheckVerification=check_path.name,
    currentResourceVerification=resource_path.name,stableGpuIdle20SecondsVerified=False,
    voiceRequestEligibleAtObservation=False,preparedVoiceVersion=6,preparedVoiceRequestStarted=False,
    currentForeignHandoff=resource['currentForeignLease'],currentOriginalResearchPid=resource['currentOriginalResearch']['pid'],
    currentOriginalResearchCreateTime=resource['currentOriginalResearch']['createTime'],
    currentOriginalResearchAlive=resource['currentOriginalQueueAlive'],currentOriginalResearchObservationAt=resource['observedAt'],next=next_step)
assert cp_path.read_text('utf-8-sig')==cp_raw
save(cp_path,cp)
queue_path=B/'queue.json';queue_raw=queue_path.read_text('utf-8-sig');queue=json.loads(queue_raw)
queue['updatedAt']=now()
queue['currentMotionReview'].update(status=cp['stage'],stage=cp['stage'],next=next_step,
    currentHandoff=dest.relative_to(ROOT).as_posix(),currentDuplicateReview=review_path.relative_to(ROOT).as_posix(),
    currentDuplicateReviewPending=None,currentDuplicateCheckPassed=True,
    currentDuplicateCheckVerification=check_path.relative_to(ROOT).as_posix(),
    currentResourceVerification=resource_path.relative_to(ROOT).as_posix(),
    currentForeignHandoff=resource['currentForeignLease'],preparedVoiceVersion=6,newTts=False,newVideoId=None,deleted=False)
assert queue_path.read_text('utf-8-sig')==queue_raw
save(queue_path,queue)
print('ActualV12exit0/stablefalse; fivechangedcontents/twoNewwholeStudio/currentduplicatecheck0 recorded. No newTTS/PCM/platform/Git mutation.')
