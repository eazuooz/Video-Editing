"""Reconcile current output evidence into the existing review ledger/checkpoint."""
from pathlib import Path
import datetime,json
ROOT=Path(__file__).resolve().parents[2]
SLUG='ai-game-development-human-craft'
P=ROOT/'projects'/SLUG
O=ROOT/'shared/output'/SLUG
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
integrity=read(O/'encoded-integrity.json');motion=read(O/'encoded-motion-review/review.json')
captions=read(O/'caption-pixel-qa/report.json');ratio=read(O/'screen-role-measurement.json')
audio=read(O/'audio/level-continuity.json');files=read(O/'four-file-verification.json')
assert captions['status']==files['status']==ratio['status']=='pass'
assert motion['movieSha256']==integrity['outputs'][1]['sha256']
assert motion['status']=='pass-agent-scoped-visual-review'
ledger=read(P/'production/review-ledger.json')
def check(id,**fields):
    row=next((x for x in ledger['checks'] if x['id']==id),None)
    if row is None:row={'id':id};ledger['checks'].append(row)
    row.update(reviewedAt=now,**fields)
base=f'shared/output/{SLUG}'
check('whole-video-delivery',status='pass-local-four-files; drive-review-pending',scope='Current complete24:38.867 clean/captioned masters and340cue KO/EN; human review and YouTube upload pending.',evidence=f'projects/{SLUG}/production/delivery-output.json',files=files['files'])
check('full-narration-production',status='complete-human-listening-pending',scope='All28 scenes complete; targeted repairs bounded to3 attempts; unchanged approved PCM retained. No GPU lease/research pause remains.',sourceSha256=audio['sourceSha256'],evidence=f'{base}/audio/final-asr/complete-readback.json')
check('production-source-acquisition',status='pass-selected-production-ranges',scope='52 unique native-speed independent development,craft/history/automation and game cuts selected; licensed asset/source records retained.',evidence=[f'projects/{SLUG}/sources/source-manifest.json',f'projects/{SLUG}/planning/actual-footage-plan.json'])
check('independent-source-rights',status='selected-visual-ranges-cleared-with-notices',scope='Mix and Jam,Jammo,Nyhver,Unreal,Unity AI third-party demo,Godot,Krita,wood carving,robot and1906history; attribution/license notices retained. Research-only lessons excluded.',evidence=f'projects/{SLUG}/sources/source-manifest.json')
check('full-composite-visual-qa',status=motion['status'],scope=motion['method'],evidence=f'{base}/encoded-motion-review/review.json',movieSha256=motion['movieSha256'],frames=motion['frames'],currentDirectlyReviewedFrames=motion['directlyReviewedCurrentFrames'],retainedCompressionEquivalentFrames=motion.get('withinCompressionToleranceFrames'),exactIdenticalFrames=motion.get('exactIdenticalFrames'),allFrameCompressionComparison=motion.get('allFrameCompressionComparison'),humanFullPlayback='pending',findings=motion['findings'])
check('final-caption-pixels',status='pass',scope='All340 cues,2124 encoded cue-start/end and actual-cut/scene-neighbor samples;0 failures. Fixed48px,max2lines,960/970.',evidence=f'{base}/caption-pixel-qa/report.json',movieSha256=motion['movieSha256'],captionStateRepair=f'{base}/caption-state-repair.json')
check('final-encoded-integrity',status='pass',scope='Both complete88732-frame1920x1080p60 masters: full video/audio decode,monotonic60fps PTS,duration and identical AAC packet hash.',evidence=f'{base}/encoded-integrity.json',outputs=integrity['outputs'],captions=integrity['captions'])
check('narration-level-continuity',status='pass-measured-processing; source-prosody-listening-pending',scope='13742speech-active400ms/100ms windows across source/stem/AAC;185paragraph medians and184joins; progressive source decay corrected. All53source-prosody flags retained for human listening.',evidence=f'{base}/audio/level-continuity.json',sourceSha256=audio['sourceSha256'],stemSha256=audio['stemSha256'],finalSha256=audio['finalSha256'],voiceTransferMedianDb=audio['voiceTransferMedianDb'],processingAttenuationStatus=audio['processingAttenuationStatus'],humanListening='pending')
check('actual-footage-60-v2',status='pass-measured-current-output',scope='52807/88012 body frames actual footage;60% within one frame. Self-authored Unity remains explanation.52unique native-speed ranges; no loops,padding or slowdown.',evidence=f'{base}/screen-role-measurement.json',actualShare=ratio['actualShare'],motionReview=motion['status'])
check('first-word-listening-followup',status='pending-human-listening',scope='01:43.2,scene03: expected 지금까지는; full-mix and independent-context ASR recognized 까지는. Do not turn text inference into a listening pass;3targeted TTS attempts already exhausted.',evidence=f'{base}/audio/current-ambiguity/result.json')
for row in ledger['checks']:
    if row['id']=='chapter-continuity-revision3':row['renderedJoinReview']='agent-scoped-state/cut review complete; human continuous listening pending'
    if row['id']=='unity-capture-completion':row['visualReview']=f'Current action/cut evidence in {base}/encoded-motion-review/review.json'
ledger['updatedAt']=now
checkpoint=read(P/'production/checkpoint.json')
checkpoint.update(updatedAt=now,stage='local-complete-drive-upload',activeJobs=[],pending=['Google Drive upload/readback','Human complete-version review and listening before YouTube','Selective Git delivery'],nextAction='Finish Drive upload/readback and selective Git; then stop for review of this complete version.')
for item in ['Caption-state and member-join repair complete; all340cues/2124samples pass','Current clean/captioned88732-frame full decode/PTS/AAC pass; current changed visual frames inspected','Four-file collector complete; output hashes match validated masters']:
    if item not in checkpoint['completed']:checkpoint['completed'].append(item)
checkpoint['latestVerifiedSourceCommit']={'sha':'abe536af640cb7f667ae5ee659c04e7cffac18db','remote':'origin/codex/ai-game-development-human-craft-20261014','push':'verified','scope':'Prior completed actual-footage acquisition/cut implementation; final delivery commit recorded separately after creation'}
checkpoint['finalGitReceipt']=f'{base}/git-final-delivery/committed.json'
plan=read(P/'planning/production-plan.json');plan.update(status='local-complete-drive-upload',nextAction=checkpoint['nextAction'])
plan['narrativeContinuity']['renderedJoinReview']='agent-scoped-state/cut review complete; human continuous listening pending'
plan['selectedFootageSteering']['sourceSelection']='selected/licensed; current encoded agent-scoped state/cut review complete'
manifest=read(P/'project.json')
manifest['editing']['exampleInterleaving']['reviewStatus']=motion['status']
manifest['audio']['backgroundMusic']['approvalStatus']='existing approved track and license reused; current mix measured; human listening pending'
manifest['audio']['lectureDefaults']['comparisonSampleStatus']='technical current-mix review complete; human comparison/listening pending'
control=read(ROOT/'shared/publishing/video-production-control.json')
assert control['selectedVideo']==SLUG
deliveryPath=O/'drive-final-v1-delivery.json'
if deliveryPath.exists():
    delivery=read(deliveryPath)
    assert delivery['localSha256']==motion['movieSha256'] and delivery['sizeBytes']==integrity['outputs'][1]['bytes']
    assert delivery['fileId'] and delivery['accessStatus']=='verified-owner-only'
    for obj,key in [(ledger,'finalDriveReview'),(checkpoint,'finalReviewDelivery'),(plan,'finalReviewDelivery'),(control,'finalReviewDelivery')]:obj.setdefault(key,{}).update(delivery)
    checkpoint.update(stage='drive-review-delivered-awaiting-user',nextAction='User reviews this complete Drive version; revise selected issues or upload this exact approved SHA to private YouTube only after review.',pending=['Human complete-version review and listening before YouTube'])
    checkpoint['gitDelivery']={'status':'consult-final-operation-receipt','receipt':checkpoint['finalGitReceipt'],'rule':'Only the actual commit/remote SHA in this receipt confirms Git completion; no future self-SHA is embedded in this commit.'}
    checkpoint['driveDestinationReadback']['finalFileId']=delivery['fileId']
    item='Complete captioned MP4 uploaded to private Drive; actual ID,size and permissions read back'
    if item not in checkpoint['completed']:checkpoint['completed'].append(item)
    plan.update(status='drive-review-delivered-awaiting-user',nextAction=checkpoint['nextAction'])
    plan['approvals']['finalDriveUserReview'].update(status='pending-user-review',fileId=delivery['fileId'],version=delivery['version'],sha256=delivery['localSha256'])
    check('whole-video-delivery',status='pass-delivered-for-user-review',scope='Complete local clean/captioned/KO/EN and private Drive captioned v1 delivered; human listening/review pending; no YouTube upload.',drive=delivery)
    manifest['delivery']['driveReview']=delivery
    control['updatedAt']=now
    write(ROOT/'shared/publishing/video-production-control.json',control)
elif (O/'drive-transfer-block.json').exists():
    block=read(O/'drive-transfer-block.json')
    assert block['finalLocalSha256']==motion['movieSha256']
    delivery={'status':'blocked-transfer','fileId':None,'url':None,'version':None,'localSha256':motion['movieSha256'],'sizeBytes':integrity['outputs'][1]['bytes'],'accessStatus':'no-final-file-created','processingAndPlaybackStatus':'not-uploaded','userReviewMessage':None,'reviewedAt':None,'block':block}
    for obj,key in [(ledger,'finalDriveReview'),(checkpoint,'finalReviewDelivery'),(plan,'finalReviewDelivery'),(control,'finalReviewDelivery')]:obj.setdefault(key,{}).update(delivery)
    checkpoint.update(stage='local-complete-drive-transfer-blocked',nextAction='Upload the complete reviewed captioned MP4 through a working Google Drive transfer path; read back actual ID/access/playback, then user reviews that version before YouTube.',pending=['Working Google Drive transfer for the completed captioned MP4','Human complete-version review and listening before YouTube'])
    checkpoint['gitDelivery']={'status':'consult-final-operation-receipt','receipt':checkpoint['finalGitReceipt'],'rule':'Only actual commit/remote SHA in the receipt confirms Git completion.'}
    plan.update(status=checkpoint['stage'],nextAction=checkpoint['nextAction'])
    plan['approvals']['finalDriveUserReview']['status']='pending-final-file; transfer-blocked'
    manifest['status']='local-review-complete-drive-transfer-blocked'
    manifest['delivery']['driveReview']=delivery
    check('whole-video-delivery',status='pass-local-four-files; drive-transfer-blocked',scope='Complete current high-bitrate clean/captioned/KO/EN saved and reviewed. Original940MB fails connector512MiB preflight; reviewed527MB copy reaches transfer service but fails413; browser transfer did not progress. No final Drive ID or YouTube upload.',drive=delivery)
    control['updatedAt']=now
    write(ROOT/'shared/publishing/video-production-control.json',control)
write(P/'project.json',manifest);write(P/'production/review-ledger.json',ledger);write(P/'production/checkpoint.json',checkpoint);write(P/'planning/production-plan.json',plan)
print(json.dumps({'stage':checkpoint['stage'],'checks':len(ledger['checks']),'publishReady':False}))
