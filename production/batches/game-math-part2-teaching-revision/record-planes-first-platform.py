"""Record the first plane lecture's actually saved and reopened private settings."""
from pathlib import Path
import json, hashlib, datetime
ROOT=Path(__file__).resolve().parents[3]; B=Path(__file__).parent
SLUG='game-math-plane-distances-v2'; P=ROOT/'projects'/SLUG
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
r=read(P/'publishing/youtube-upload.json')
assert r['videoId']=='Rzrt47-u4G0'
assert r['video']['sha256']=='64ff63e99f6e004eada6d6726fefbf618c4796f17102cc640544fae2b13bd181'
assert read(P/'production/current-pixel-review.json')['sha256']==r['video']['sha256']
proof=P/'publishing/private-caption-proof.png'; assert proof.exists()
observed=read(P/'publishing/uploaded-player-observed.json'); v=observed['video'][0]
assert v['width']==1920 and v['height']==1080 and abs(v['duration']-r['video']['seconds'])<1/30
assert observed['cc'][0]['pressed']=='false'
now=datetime.datetime.now().astimezone().isoformat()
write(P/'publishing/uploaded-cc-off.json',dict(videoId=r['videoId'],watchUrl=r['url'],observedAt=now,
 **v,ccLabel=observed['cc'][0]['label'],ccPressed='false',playerCaptionsOff=True,
 burnedCaptionPixelsDirectlyViewed=True,proof=proof.relative_to(ROOT).as_posix()))
r.update(watchUrl=r['url'],status='reviewed-captioned-private-upload; full available settings saved and reopened',
 privateUploadComplete=True,availableStudioSettingsComplete=True,fullPublishingSettingsComplete=True,
 completedAt=now,transferAndProcessing='SD and HD complete; actual1920x1080 CC-off burned captions viewed',scheduled=False)
r['englishMetadata'].update(language='en',status='separate title and description published and reopened in Studio')
for s in r['subtitles']:s['status']='manually-uploaded-with-timing and published in Studio'
r['thumbnail']['status']='saved actual reviewed V2 thumbnail in Studio'
r['burnedCaptionVerification'].update(status='verified-in-actual-uploaded-player',proof=proof.relative_to(ROOT).as_posix(),playerObservation='publishing/uploaded-cc-off.json')
r['coachingCard'].update(status='saved-and-reopened-in-Studio',title='프로그래밍 과외',
 teaser='프로그래밍 과외',callToAction='과외 안내 보기',observedTime='00:00:00',image='shared/assets/branding/yamyamcoding-cats-original.png')
r['endScreen'].update(status='saved-and-reopened-in-Studio',observedStart='11:51:55',observedEnd='12:01:55',
 platformTimebase='60fps display; final10seconds',memberProfilesNamesBadgesClear=True,
 directPixelProof='shared/output/game-math-plane-distances-v2/endscreen-upload-proof.png')
r['coachingEndingLink']['status']='saved-and-reopened-in-Studio'
r['platformObserved'].update(transportComplete=True,processingComplete=True,copyrightAndAdChecksComplete=True,
 uploadedCaptionPixelsVerified=True,midrollEnabled=False,automaticClaims='none found; no revenue effect')
r['studioSettingsObserved']={'processing':'SD and HD complete','privacy':'private','playlist':'게임 수학(Game Math) PART 2',
 'language':'Korean','category':'Education','paidPromotion':False,'aiUsed':True,'madeForKids':False,
 'ads':'enabled; actual midroll checkbox unchecked and Save disabled after reopening',
 'automaticAdSuitability':'edit page alert cleared to em dash after review; monetization remains enabled',
 'automaticClaims':'none found; no revenue effect'}
write(P/'publishing/youtube-upload.json',r)
m=read(P/'project.json');m['status']='reviewed-private-upload; schedule-transition-pending'
m['publishing'].update(videoId=r['videoId'],privateUploadComplete=True,fullPublishingSettingsComplete=True)
m['finalRender']['openItems']=['Human whole listening and game-IP review pending.','Native Motion Canvas editor playback unverified.','Schedule transition pending.']
write(P/'project.json',m)
registry=read(ROOT/'shared/git-essential-images.json');path=proof.relative_to(ROOT).as_posix()
entry={'path':path,'purpose':'minimal-publishing-proof','sha256':hashlib.sha256(proof.read_bytes()).hexdigest(),
 'reviewedAt':now,'reason':'Actual private uploaded1080p player; burned Korean caption visible while CC is off.','project':SLUG}
registry['entries']=[e for e in registry['entries'] if e['path']!=path]+[entry];write(ROOT/'shared/git-essential-images.json',registry)
ignore=ROOT/'.gitignore';text=ignore.read_text(encoding='utf8');exception='!/'+path
if exception not in text.splitlines():ignore.write_text(text.rstrip()+'\n'+exception+'\n',encoding='utf8')
q=read(B/'queue.json');item=next(i for i in q['items'] if i['slug']=='game-math-planes-barycentric')
item['status']='both-local-episodes-reviewed; first-private-settings-complete; second-upload-pending'
item['revision'].update(flowReviewPassed=True,annotationMotionReviewPassed=True,narrationComplete=True,
 renderComplete=True,localOutputsCollected=True,localPixelReviewComplete=True,wholeNativePlaybackComplete=True,
 firstEpisodePrivateUploadComplete=True,firstEpisodeFullPublishingSettingsComplete=True,videoIds=[r['videoId']])
q['execution']['stage']='Both plane lectures locally reviewed and collected; first actual private upload/settings complete; first selective Git and second upload pending; polygon source comparison active'
q['updatedAt']=now;write(B/'queue.json',q)
print('Recorded actual first plane private upload and full available settings:',r['videoId'])
