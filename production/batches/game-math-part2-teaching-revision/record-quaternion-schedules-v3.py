"""Record saved/reopened replacements; pending platform checks stay pending."""
from pathlib import Path
import copy,datetime,hashlib,json,os
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
Q=B/'cross-game-review-20261011/quaternion-four-game-v3'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):
 p.parent.mkdir(parents=True,exist_ok=True)
 tmp=p.with_name(p.name+'.tmp-'+str(os.getpid()))
 tmp.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8');os.replace(tmp,p)
now=datetime.datetime.now(datetime.timezone.utc).isoformat();progress=read(Q/'current-private-progress.json')
ledger_path=ROOT/'shared/publishing/daily-alternating-schedule.json';ledger_sha=sha(ledger_path);ledger=read(ledger_path)
replacements=[]
for name,date in [('foundations','2026-10-17'),('calculations','2026-10-19')]:
 schedule=read(Q/f'{name}-v3-actual-schedule.json');slug=schedule['slug'];p=ROOT/'projects'/slug
 assert schedule['actualSavedReopened'] and schedule['baselinePrivateSavedReopened'] and schedule['date']==date
 evidence=ROOT/schedule['evidence'];text=evidence.read_text(encoding='utf8')
 assert f'2026. 10. {date[-2:]}.' in text and '오전 9:00' in text and 'GMT+0900' in text
 assert '"완료" [disabled]' in text and schedule['videoId'] in text
 oldtext=(ROOT/schedule['baselinePrivateEvidence']).read_text(encoding='utf8')
 assert 'radio "비공개" [checked]' in oldtext and '"완료" [disabled]' in oldtext
 qa=read(p/'production/qa.json');review=read(p/'production/current-pixel-review.json')
 platform=read(Q/f'{name}-platform-status.json');pixel=read(Q/f'{name}-youtube-caption-pixel-review.json')
 assert platform['transportComplete'] and platform['privateSaveVerified'] and platform['hdComplete']
 assert pixel['uploadInputSha256']==qa['videos']['videoBurnedCaptions']['sha256']
 delivery=read(ROOT/f'shared/output/quaternion-git-delivery-v3/{name}-delivery.json')
 assert delivery['pushed'] and delivery['remoteSha']==delivery['commit']==schedule['reviewedProductionGitCommit']
 for language in ['korean','english']:
  proof=read(Q/f'{name}-{language}-reopened.json')
  assert proof['requiredBesiegeLinksVerified'] and proof['preparedTextMatchAfterLineEndingNormalization']
 full_checks=platform['copyrightCheckComplete'] and platform['advertisingCheckComplete']
 receipt=dict(schemaVersion=1,slug=slug,videoId=schedule['videoId'],url='https://youtu.be/'+schedule['videoId'],
  status='reviewed four-game lecture; actual schedule saved/reopened'+('' if full_checks else '; copyright check pending'),
  uploadInput=dict(path=f'output/{slug}/{slug}.captioned.mp4',sha256=pixel['uploadInputSha256']),
  privateUploadComplete=True,transferAndProcessing=dict(transportComplete=True,sdComplete=True,hdComplete=True),
  currentVisibility='scheduled',scheduled=True,scheduledAt=schedule['publishAt'],scheduleVerification=schedule,
  bodyRatio=review['bodyRatio'],distinctGames=review['distinctGames'],
  currentLocalPixelReview=f'projects/{slug}/production/current-pixel-review.json',
  uploadedPlayerCaptionProof=Q.relative_to(ROOT).as_posix()+f'/{name}-youtube-caption-pixel-review.json',
  metadataSavedReopened=True,requiredBesiegeLinksSavedReopenedBothLanguages=True,
  subtitles=dict(ko='manual SRT published',en='manual SRT published',englishTitleDescriptionPublishedReopened=True),
  thumbnail=dict(uploadedSavedReopened=True,source=read(p/'project.json')['publishing']['thumbnailPath']),
  coachingCard=dict(savedReopened=True,time='00:00',url='https://www.yamyamcoding.com/1430b1ff-a61e-8040-a542-d672d5d25328'),
  endScreen=dict(savedReopened=True,scope='original final10seconds only',elements=['PART2 playlist','own-channel subscribe','coaching link'],
   originalMemberIdentityClear=True,evidence=Q.relative_to(ROOT).as_posix()+f'/{name}-end-screen-reopened.txt'),
  platformChecks=platform,availableStudioSettingsSavedReopened=True,fullPublishingSettingsComplete=full_checks,
  humanListening=dict(status='pending',nativePlaybackAndAsrDoNotReplaceHumanReview=True),
  rightsReview=dict(status='pending',descriptionExceptionUserAuthorized=True,sourceAndGameIpNotAutomaticallyApproved=True),
  pinnedComment=dict(prepared=True,posted=False,pinned=False,reason='Private video; comments not available'),
  productionGit=dict(commit=delivery['commit'],remoteVerifiedSha=delivery['remoteSha']),
  replacementBaseline=dict(videoId=schedule['replacedVideoId'],currentVisibility='private',permanentlyDeleted=False),
  verifiedAt=now)
 write(p/'publishing/youtube-upload.json',receipt)
 m=read(p/'project.json');m['publishing'].update(privateUploadComplete=True,actualVideoId=schedule['videoId'],
  fullPublishingSettingsComplete=full_checks,scheduleStatus='actual saved and reopened',
  scheduledAt=schedule['publishAt'],actualSchedule=schedule,
  replacementBaselineCurrentVisibility='private; old reservation removed; permanent deletion pending',
  availableStudioSettingsSaved=True,automaticPlatformChecksComplete=full_checks)
 write(p/'project.json',m)
 old_slug=slug[:-1]+'2';old=ROOT/'projects'/old_slug/'publishing/youtube-upload.json';oldreceipt=read(old)
 assert oldreceipt['videoId']==schedule['replacedVideoId']
 if oldreceipt.get('currentVisibility')!='private':oldreceipt['previousScheduleBeforeFourGameRevision']=copy.deepcopy(oldreceipt.get('scheduleVerification'))
 oldreceipt.update(currentVisibility='private',scheduled=False,scheduledAt=None,
  status='Superseded by reviewed four-game revision; private baseline retained until specific permanent-deletion confirmation',
  supersededBy=dict(videoId=schedule['videoId'],slug=slug,verifiedAt=now),
  currentPrivacyEvidence=schedule['baselinePrivateEvidence'])
 write(old,oldreceipt)
 ep=next(e for e in progress['episodes'] if e['slug']==slug)
 ep.update(uploadTransportComplete=True,actualPrivateSaveVerified=True,actualUploadedCaptionPixelsVerified=True,
  automaticPlatformChecksComplete=full_checks,availableStudioSettingsSavedReopened=True,fullPublishingSettingsComplete=full_checks,
  gitDelivered=True,gitCommit=delivery['commit'],actualSchedule=schedule,
  targetSchedule=dict(date=date,time='09:00',timezone='Asia/Seoul',actualStudioReservation=True),
  baselineSchedulePreservedUntilReviewedPrivateReplacement=False,baselineCurrentVisibility='private; not deleted')
 current=next((e for e in ledger['actualSchedules'] if e['videoId']==schedule['replacedVideoId']),None)
 if current is not None:
  historical=copy.deepcopy(current);new=copy.deepcopy(current)
  new.update(slug=slug,videoId=schedule['videoId'],title=m['titles']['ko'],verifiedAt=schedule['verifiedAt'],
   evidence=schedule['evidence'],evidenceSha256=sha(evidence),status='actual-saved-reopened',
   copyrightCheckPending=not platform['copyrightCheckComplete'],advertisingCheckPassed=platform['advertisingCheckComplete'])
  ledger['actualSchedules'][ledger['actualSchedules'].index(current)]=new
  history=dict(replacedAt=now,oldSchedule=historical,newSchedule=new,
   oldVideoCurrentVisibility='private',oldVideoPermanentlyDeleted=False,
   evidence=schedule['baselinePrivateEvidence'])
  ledger.setdefault('replacementHistory',[]).append(history)
 else:
  new=next(e for e in ledger['actualSchedules'] if e['videoId']==schedule['videoId'])
  assert new['date']==date and new['time']=='09:00'
 replacements.append(dict(oldVideoId=schedule['replacedVideoId'],newVideoId=schedule['videoId'],
  slug=slug,actualSchedule=schedule,oldVideoCurrentVisibility='private',oldVideoPermanentlyDeleted=False))
ledger['updatedAt']=now
assert sha(ledger_path)==ledger_sha,'Concurrent ledger changed; rerun against fresh evidence'
write(ledger_path,ledger)
progress.update(updatedAt=now,stage='Both actual schedules saved/reopened; foundation copyright pending; obsolete baselines private',
 pending=['Foundation copyright check result before Oct17','Specific action-time permanent-deletion confirmation for corresponding obsolete baselines',
 'Save final publishing/schedule Git evidence','Continue remaining owned four-game teaching revisions in date order'],fullTaskComplete=False)
write(Q/'current-private-progress.json',progress)
q=read(B/'queue.json');item=next(i for i in q['items'] if i['slug']=='game-math-quaternion-operations')
item['fourGameRevision'].update(episodes=progress['episodes'],scheduleReplacementComplete=True,
 baselineDeletionsComplete=False,foundationCopyrightCheckPending=True)
item['status']='Four-game replacements reviewed, privately saved, Git delivered and scheduled; old baselines private; foundation copyright check and permanent deletion pending'
q['execution'].update(stage='quaternion-four-game-schedules-verified-platform-followup',lastProgressAt=now,fullTaskComplete=False)
write(B/'queue.json',q);write(Q/'actual-schedule-replacements.json',dict(verifiedAt=now,replacements=replacements,fullTaskComplete=False))
print(json.dumps(dict(actualSchedules=2,oldReservationsRemoved=2,oldVideosDeleted=False,foundationCopyrightCheckPending=True)))
