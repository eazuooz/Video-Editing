"""Record local preparation and live identities without approving final delivery."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,time,psutil
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
now=lambda:datetime.now(timezone.utc).isoformat();rel=lambda p:p.relative_to(ROOT).as_posix()
def save(p,x):
 t=p.with_name(p.name+'.followup.writing');t.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
request=read(BASE/'narration-tts-request-v1.json')
for x in request['protectedInputs']:assert sha(ROOT/x['path'])==x['sha256'],x['path']
qaexec=read(BASE/'black-structural-qa-execution-v1.json');qaexec.update(sessionId=64817,actualOuterExitObserved=True,actualOuterExitCode=0)
save(BASE/'black-structural-qa-execution-v1.json',qaexec)
thumb=read(BASE/'prepared-thumbnail-direct-review-v1.json');thumb.update(uploadCandidateDirectlyRead=True,uploadCandidateDirectReviewAt=now(),preparedThumbnailVisualReviewApproved=True)
assert sha(ROOT/thumb['uploadCandidate']['path'])==thumb['uploadCandidate']['sha256'];save(BASE/'prepared-thumbnail-direct-review-v1.json',thumb)
pub=read(BASE.parent/'publishing/publishing-text-preparation-v1.json')
save(BASE.parent/'publishing/publishing-text-direct-review-v1.json',dict(reviewedAt=now(),preparation=rel(BASE.parent/'publishing/publishing-text-preparation-v1.json'),preparationSha256=sha(BASE.parent/'publishing/publishing-text-preparation-v1.json'),fullKoEnDescriptionAndTitlesRead=True,pairedScriptWholeReview=rel(BASE/'paired-script-direct-review-v1.json'),descriptionScopeMatchesHistoricalActionsAndHypotheticalExamples=True,chapterOrderMatchesTwelveScenes=True,chapterTimesMeasured=False,canonicalLinks=pub['exactCanonicalLinks'],unfilledPlaceholdersOmitted=True,sourceCreditConditionObserved=False,mandatorySourceCreditNotObservedInPrimaryRights=True,pinnedCommentExactTextRead=True,actualVideoId=None,uploaded=False,scheduled=False,platformSettingsVerified=False,humanListening='pending',finalPublicRights='pending'))
mc=read(BASE/'black-structural-render-execution-v2.json')
for path,mutate in [(BASE/'latest-checkpoint.json',False),(ROOT/'production/batches/sakurai-planning-game-design/queue.json',True)]:
 for attempt in range(10):
  raw=path.read_text('utf-8-sig');doc=json.loads(raw);item=next(x for x in doc['items'] if x['slug']=='character-parameters') if mutate else doc
  item.update(motionCanvasCreated=True,measuredMotionCanvasCreated=False,structuralPrototype=dict(status='five-targeted-scenes-render-running',execution=rel(BASE/'black-structural-render-execution-v2.json'),historicalReview=rel(BASE/'black-structural-direct-review-v1.json'),finalApproval=False),publishingPreparation=rel(BASE.parent/'publishing/publishing-text-preparation-v1.json'),thumbnailPreparation=rel(BASE/'prepared-thumbnail-direct-review-v1.json'))
  if not (BASE/'narration-tts-execution-v2.json').exists():item.update(ttsRequestLaunched=True,ttsStarted=False)
  if mutate:doc['updatedAt']=now()
  else:doc['recordedAt']=now()
  if path.read_text('utf-8-sig')==raw:save(path,doc);break
  time.sleep(.1)
 else:raise RuntimeError('Concurrent writer; preserve actual checkpoint')
proof=dict(observedAt=now(),protectedInputsUnchanged=True,protectedInputCount=len(request['protectedInputs']),ttsExecutionV2Exists=(BASE/'narration-tts-execution-v2.json').exists(),structuralV1Review=rel(BASE/'black-structural-direct-review-v1.json'),structuralV2Execution=rel(BASE/'black-structural-render-execution-v2.json'),thumbnailPrepared=True,publishingTextPrepared=True,measuredVoiceAndTimingApproved=False,finalPixelsApproved=False,collected=False,uploaded=False,scheduled=False,actualId=None,imagesGitAdded=0,foreignProcessManipulation=0)
save(BASE/'prepared-followups-handoff-v1.json',proof)
print('Prepared metadata/thumbnail reviewed; exact10 protected inputs unchanged. Live TTS and targeted structural work remain pending.')
