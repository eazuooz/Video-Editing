"""Promote the reviewed current17 delivery without overwriting its historical baseline."""
from pathlib import Path
from datetime import datetime,timezone
import copy,hashlib,json,os
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def atomic(p,v):
 t=p.with_name(p.name+'.writing');t.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
now=datetime.now(timezone.utc).isoformat();rp='projects/motion-sickness-games/production/revision-cross-game-four-v1/'
main=ROOT/'projects/motion-sickness-games/project.json';before=main.read_bytes();beforeSha=hashlib.sha256(before).hexdigest()
assert beforeSha=='48dd15d50cb48e655f0312c644ef9a5c8349676a3ab17620b68769955210b749'
assert not (R/'current17-main-promotion-v1.json').exists()
review=read(R/'current17-final-encoded-pixel-direct-review-v1.json');assert review['technicalQaPassed'] and review['all238BoardsDirectlyRead']
flow=read(R/'current17-final-normal-playback-direct-review-v1.json');assert flow['wholeNormalSpeedStartToEndObserved']
mix=read(R/'current-mix-execution-v2.json');protected=mix['protectedInputs']
for x in protected:assert sha(ROOT/x['path'])==x['sha256']
others=[x for x in protected if (ROOT/x['path']).resolve()!=main.resolve()];assert len(others)==70
backup=R/'baseline-main-before-current17-promotion-v1.json';assert not backup.exists();backup.write_bytes(before);assert sha(backup)==beforeSha
v=json.loads(before.decode('utf-8-sig'));plan=read(R/'measured-current17-plan-v2.json');pair=read(R/'current17-final-pair-execution-v2.json')
v['status']='cross-game-four-current17-local-reviewed; private-upload-settings-Git-schedule-pending'
e=v['editing'];e.update(actualGameplaySeconds=plan['actualFrames']/60,actualExplanationSeconds=plan['explanationFrames']/60,actualGameplayShare=plan['actualFrames']/plan['bodyFrames'],actualCommercialGameplaySeconds=plan['actualFrames']/60,plannedGameplaySeconds=plan['actualFrames']/60,plannedExplanationSeconds=plan['explanationFrames']/60,plannedGameplayShare=.6,scenePlan=rp+'measured-current17-plan-v2.json',finalBodyFrames=dict(total=plan['bodyFrames'],actual=plan['actualFrames'],explanation=plan['explanationFrames'],ratioErrorFrames=plan['ratioErrorFrames']),timingStatus='Current17 measured PCM placements,220 KOEN cues,18 chapters and original600f member ending retimed together; all planned encoded samples reviewed.')
e['exampleInterleaving']['reviewStatus']='Four distinct existing games, connected controls/retained task cues; all1425 encoded samples/238boards across220cue/37cut/29PCM placements directly read; normal1x muted start/end. Bounded sample review; human hearing pending.'
e['openingOverview']['currentFinalFlow']=rp+'current17-final-normal-playback-direct-review-v1.json'
e['crossGameRevision']=dict(version='cross-game-four-v1',baselineVideoId='mBDd9VzSTkA',original14PcmPreserved=True,original20SilentPiecesPreserved=True,sceneCount=17,paragraphCount=81,retainedCaptionCount=179,newCaptionCount=41,distinctGames=['PowerWash Simulator','The Talos Principle 2','Portal 2','Half-Life: Alyx'],concept='Separate necessary control/view/locomotion from optional presentation while retaining readable task feedback.',finalPixels=rp+'current17-final-encoded-pixel-direct-review-v1.json',currentMixedAudio=rp+'current17-mixed-complete-direct-review-v2.json',claimScope='Visible screen roles and task results; no measured game-world geometry or individual comfort guarantee.')
v['video']['durationSeconds']=plan['seconds'];v['audio']['mixStatus']='Current17 decodedAAC whole17+independent81 complete text directly compared; human hearing/pronunciation pending.'
p=v['paths'];p.update(script=rp+'script/narration.ko.json',scriptEn=rp+'script/narration.en.json',audioReport=rp+'current-mix-execution-v2.json',audioMix=mix['mixAac'],editorAudioMix=mix['mixWav'],narration=mix['files'][0]['path'],captionsKo=rp+'captions.ko.srt',captionsEn=rp+'captions.en.srt',captionsAss=rp+'captions.ko.ass',videoClean=pair['pair'][0]['path'],videoBurnedCaptions=pair['pair'][1]['path'],renderReport=rp+'current17-final-encoded-pixel-direct-review-v1.json',currentAssemblyBuilder='production/batches/cross-game-example-coverage-review/assemble-motion-current17-pair-v2.py',currentMeasuredScenePlan=rp+'measured-current17-plan-v2.json',timeline=rp+'measured-current17-plan-v2.json',currentTeachingRevision=rp+'current17-main-promotion-v1.json',publishingKo=rp+'publishing/upload-description.ko.txt',publishingEn=rp+'publishing/upload-description.en.txt')
old=copy.deepcopy(v['publishing']);v['publishingHistory'].append(dict(reason='Preserve prior completed teaching upload; latest actual Studio observed PRIVATE. Historical schedule is not current reservation proof.',publishing=old,currentObservedPrivacy='private',currentScheduleVerified=False))
pub=v['publishing'];pub.update(privacyStatus='private',scheduledPublishAt=None,videoId=None,videoUrl=None,receipt=rp+'publishing/youtube-upload-v1.json',status='reviewed-local-current17-awaiting-single-private-upload',uploaded=False,actualVideoId=None,scheduled=False,fullSettingsVerified=False,ccOffPixelVerification=None,baselineVideoId='mBDd9VzSTkA',baselinePreserved=True,baselineScheduleChanged=False,productionGitEvidence=None,scheduleEvidence=None)
v['approvals'].update(script='Original14scene66paragraph content and order retained; three15paragraph bilingual insertions directly compared across four distinct games.',final='Current17 whole+81independent decodedAAC texts and all1425 planned final samples directly read; normal1x muted start/end; human hearing/pronunciation and public rights remain pending.')
v['publishReady']=False;v['finalRender'].update(revision='cross-game-four-v1',qa=rp+'current17-final-pair-execution-v2.json',durationSeconds=plan['seconds'],frames=plan['totalFrames'],status='reviewed-current17-local-pair',videoClean=p['videoClean'],videoBurnedCaptions=p['videoBurnedCaptions'],pixelReview=p['renderReport'],technicalQa=rp+'current17-final-pair-execution-v2.json',allFinalPixelsReviewed=True,pixelReviewScope='All planned1425 samples/238boards; not every continuous frame.')
atomic(main,v)
for x in others:assert sha(ROOT/x['path'])==x['sha256']
proof=dict(schemaVersion=1,promotedAt=now,baselineMain=dict(path=str(backup.relative_to(ROOT)).replace('\\','/'),sha256=beforeSha,exactOriginalBytesPreserved=True),currentMain=dict(path='projects/motion-sickness-games/project.json',sha256=sha(main)),intentionalProtectedMainTransition=True,other70ProtectedInputsUnchanged=True,otherProtectedInputs=others,sourceReview=rp+'current17-final-encoded-pixel-direct-review-v1.json',sourceReviewSha256=sha(R/'current17-final-encoded-pixel-direct-review-v1.json'),newActualVideoId=None,baselinePlatformModified=False,humanListeningApproved=False,publicRightsApproved=False)
atomic(R/'current17-main-promotion-v1.json',proof)
cp=read(R/'latest-checkpoint.json');cp.update(recordedAt=now,stage='current17-main-promoted-awaiting-four-output-collection',mainPromotion='current17-main-promotion-v1.json',mainPromoted=True,next='Collect explicit current root four outputs and compare hashes; one private captioned upload; full possible settings/reopen/Git before actualschedule replacement.')
atomic(R/'latest-checkpoint.json',cp)
bp=ROOT/'production/batches/cross-game-example-coverage-review/queue.json';b=read(bp);b.update(updatedAt=now,status='active-current17-local-reviewed-delivery-pending',next=cp['next']);b['currentMotionReview'].update(finalPixelReview=cp['currentFinalPixelReview'],allFinalPixelsApproved=True,finalRatioApproved=True,measuredTimingApproved=True,qaApproved=True,mainPromoted=True,mainPromotion=rp+'current17-main-promotion-v1.json',activeOwnedWorkers=0);atomic(bp,b)
print(json.dumps(dict(mainPromoted=True,currentMainSha256=sha(main),otherProtected=70,oldMainBackupSha256=sha(backup),fourOutputsCollected=False)))
