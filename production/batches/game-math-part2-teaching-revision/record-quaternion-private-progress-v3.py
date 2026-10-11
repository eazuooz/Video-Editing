"""Checkpoint reviewed four-game masters without equating uploads in progress with delivery."""
from pathlib import Path
import datetime,hashlib,json
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
Q=B/'cross-game-review-20261011/quaternion-four-game-v3'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
episodes=[]
for episode,video,date in [('foundations','wreXZkEtLqA','2026-10-17'),('calculations','Rck2eL8VtqM','2026-10-19')]:
 slug='game-math-quaternion-'+episode+'-v3';p=ROOT/'projects'/slug
 qa=read(p/'production/qa.json');review=read(p/'production/current-pixel-review.json')
 started=read(p/'publishing/upload-started.json');english=read(Q/(episode+'-english-reopened.json'))
 assert started.get('videoId',started.get('actualVideoId'))==english['videoId']==video
 assert review['directMovingPixelsPassed'] and review['wholeNativePlayback']['ended']
 assert english['preparedTextMatchAfterLineEndingNormalization'] and english['requiredBesiegeLinksVerified']
 assert (ROOT/'output'/slug/(slug+'.captioned.mp4')).exists()
 episodes.append(dict(slug=slug,videoId=video,url='https://youtu.be/'+video,
  captionedSha256=qa['videos']['videoBurnedCaptions']['sha256'],seconds=qa['seconds'],cues=qa['captionCount'],
  bodyRatio=dict(actual=.4,explanation=.6,roundingErrorFrames=0),
  localTechnicalReviewComplete=True,localOutputsCollected=True,
  distinctGames=review['distinctGames'],koSrtUploaded=True,enSrtManualPublished=True,
  englishMetadataSavedReopened=True,besiegeRequiredLinksEnglishVerified=True,
  initialPrivateSaveRequested=True,uploadTransportComplete=False,
  currentPixelReview=(p/'production/current-pixel-review.json').relative_to(ROOT).as_posix(),
  targetSchedule=dict(date=date,time='09:00',timezone='Asia/Seoul',actualStudioReservation=False),
  baselineSchedulePreservedUntilReviewedPrivateReplacement=True,
  actualUploadedCaptionPixelsVerified=False,automaticPlatformChecksComplete=False,
  cardAndEndScreenSavedInUploadWizard=True,cardAndEndScreenReopenVerificationPending=True,
  humanListeningComplete=False,rightsHumanReviewComplete=False,gitDelivered=False))
record=dict(schemaVersion=1,updatedAt=now,stage='reviewed-collected; private upload transport and actual publishing verification pending',
 episodes=episodes,originalScenesPreserved=80,newNarratedScenes=14,allCaptionCuesDirectlyReviewed=523,
 backgroundMusic=False,sourceAudioUsed=False,
 originalExplanationOrderAndPcmAudit=Q.relative_to(ROOT).as_posix()+'/final-preservation-audit.json',
 currentAudioMeaningReview=Q.relative_to(ROOT).as_posix()+'/final-aac-meaning-comparison.json',
 pending=['Finish existing uploads; never duplicate','Actual 1080p60 caption pixels with player CC off',
 'Reopen metadata, cards, end screens and platform checks','Replace actual Oct17/19 reservations only after verified private saves',
 'Specific action-time confirmation before permanent deletion of HdJw7bgKlbM and SPq_41LyOG0','Selective Git delivery'],
 fullTaskComplete=False)
write(Q/'current-private-progress.json',record)
q=read(B/'queue.json');q['execution'].update(stage='quaternion-four-game-reviewed-collected-private-uploads-in-progress',lastProgressAt=now,
 currentQuaternionReview=(Q/'current-private-progress.json').relative_to(ROOT).as_posix(),fullTaskComplete=False)
item=next(i for i in q['items'] if i['slug']=='game-math-quaternion-operations')
item['status']='four-game-revisions-reviewed-collected; private uploads in progress; existing schedules preserved'
item['fourGameRevision']=dict(progress=(Q/'current-private-progress.json').relative_to(ROOT).as_posix(),episodes=episodes,
 historicalTwoEpisodeDeliveryPreservedInRevision=True)
write(B/'queue.json',q)
print(json.dumps(dict(episodes=len(episodes),reviewed=True,uploadsComplete=False,schedulesChanged=False)))
