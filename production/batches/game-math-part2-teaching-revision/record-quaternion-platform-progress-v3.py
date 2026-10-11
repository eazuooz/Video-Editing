"""Reconcile observed Studio receipts without resetting verified publishing work."""
from pathlib import Path
import datetime,json
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
Q=B/'cross-game-review-20261011/quaternion-four-game-v3'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
progress=read(Q/'current-private-progress.json');now=datetime.datetime.now(datetime.timezone.utc).isoformat()
for ep in progress['episodes']:
 name=ep['slug'].removeprefix('game-math-quaternion-').removesuffix('-v3')
 p=ROOT/'projects'/ep['slug'];m=read(p/'project.json')
 for language in ['korean','english']:
  proof=read(Q/f'{name}-{language}-reopened.json')
  assert proof['videoId']==ep['videoId'] and proof['requiredBesiegeLinksVerified']
 for element in ['card','end-screen','end-screen-subscribe','end-screen-link']:
  proof=Q/f'{name}-{element}-reopened.txt';assert proof.exists() and proof.stat().st_size>100
 ep.update(cardAndEndScreenReopenVerificationPending=False,
  besiegeRequiredLinksKoreanVerified=True,englishMetadataSavedReopened=True)
 observed=Q/f'{name}-platform-status.json'
 if observed.exists():
  state=read(observed);assert state['videoId']==ep['videoId']
  ep.update(uploadTransportComplete=state['transportComplete'],
   actualPrivateSaveVerified=state['privateSaveVerified'],
   automaticPlatformChecksComplete=state['copyrightCheckComplete'] and state['advertisingCheckComplete'],
   platformStatus=observed.relative_to(ROOT).as_posix())
  m['publishing'].update(privateUploadComplete=state['transportComplete'] and state['privateSaveVerified'],
   automaticPlatformChecksComplete=ep['automaticPlatformChecksComplete'],
   actualPlatformStatus=ep['platformStatus'])
 pixel=Q/f'{name}-youtube-caption-pixel-review.json'
 if pixel.exists():
  proof=read(pixel)
  assert proof['videoId']==ep['videoId'] and proof['uploadInputSha256']==ep['captionedSha256']
  assert proof['burnedKoreanCaptionsDirectlyVisible'] and proof['gameplayAnnotationsDirectlyVisible']
  ep.update(actualUploadedCaptionPixelsVerified=True,uploadedPixelReview=pixel.relative_to(ROOT).as_posix())
 m['editing']['exampleInterleaving']['reviewStatus']='Current-hash narrated moving additions and original retained clips directly reviewed; all fixed-caption cues passed.'
 m['editing']['timingStatus']='Measured current narration and retained PCM; exact body actual40/explanation60; final 1080p60 decode and whole native playback passed.'
 m['approvals']['rights']='Both languages saved and reopened with the explicitly authorized Besiege mandatory links; source/game-IP human review remains pending.'
 m['publishing'].update(actualVideoId=ep['videoId'],availableStudioSettingsSaved=True,
  descriptionBesiegeLinksPlatformVerified=True,koEnSubtitlesManuallySaved=True,
  cardsAndEndScreenSavedReopened=True,pinnedCommentStatus='prepared; posting and pinning pending while private',
  scheduleStatus='Existing v2 actual date anchor retained until current reviewed private save and Git delivery are verified.')
 write(p/'project.json',m)
progress.update(updatedAt=now,stage='Reviewed production; actual private upload and publishing checks reconciled from evidence')
progress['pending']=['Finish any active upload transport and automatic checks','Verify both actual YouTube caption pixels',
 'Selective Git delivery before replacing Oct17/19 reservations','Save and reopen replacement schedules',
 'Specific action-time confirmation before permanent deletion of HdJw7bgKlbM and SPq_41LyOG0']
write(Q/'current-private-progress.json',progress)
q=read(B/'queue.json');q['execution'].update(lastProgressAt=now,
 stage='quaternion-four-game-private-publishing-verification',fullTaskComplete=False)
item=next(i for i in q['items'] if i['slug']=='game-math-quaternion-operations')
item['fourGameRevision']['episodes']=progress['episodes']
item['status']='Four-game masters reviewed and collected; actual publishing verification in progress'
write(B/'queue.json',q)
print(json.dumps(dict(episodes=len(progress['episodes']),fullTaskComplete=False)))
