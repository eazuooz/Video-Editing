"""Save the directly observed first lines episode's actual private settings."""
from pathlib import Path
import json, hashlib, datetime
ROOT=Path(__file__).resolve().parents[3]; B=Path(__file__).parent
P=ROOT/'projects/game-math-lines-circles-v2'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
r=read(P/'publishing/youtube-upload.json')
assert r['videoId']=='cOcuxWKHN5g'
assert r['video']['sha256']=='05a1282c5ead9afb880a7218904f00f9563f7866d807eb15747d3c3c98a1d471'
assert read(P/'production/current-pixel-review.json')['sha256']==r['video']['sha256']
proof=P/'publishing/private-caption-proof.png';assert proof.exists()
now=datetime.datetime.now().astimezone().isoformat()
observation={'videoId':r['videoId'],'watchUrl':r['watchUrl'],'observedAt':now,
 'currentTime':37.554968,'duration':667.941,'width':1920,'height':1080,
 'ccLabel':'자막 사용 불가','ccPressed':'false','playerCaptionsOff':True,
 'burnedCaptionPixelsDirectlyViewed':True,'proof':proof.relative_to(ROOT).as_posix()}
write(P/'publishing/uploaded-cc-off.json',observation)
r.update(status='reviewed-captioned-private-upload; full available settings saved and reopened',
 privateUploadComplete=True,availableStudioSettingsComplete=True,fullPublishingSettingsComplete=True,
 completedAt=now,transferAndProcessing='SD and HD complete; actual 1920x1080 CC-off burned captions viewed',scheduled=False)
r['englishMetadata'].update(language='en',status='separate title and description published in Studio')
for s in r['subtitles']:s['status']='manually-uploaded-with-timing and saved/published in Studio'
r['thumbnail']['status']='saved actual reviewed V2 thumbnail in Studio'
r['burnedCaptionVerification'].update(status='verified-in-actual-uploaded-player',proof=proof.relative_to(ROOT).as_posix(),playerObservation='publishing/uploaded-cc-off.json')
r['coachingCard'].update(status='saved-and-reopened-in-Studio',title='프로그래밍 코칭 (프로그래밍 과외, 멘토링)',
 teaser='프로그래밍 코칭 · 과외 안내',callToAction='프로그래밍 과외',observedTime='00:00:00',
 image='shared/assets/branding/yamyamcoding-cats-original.png')
r['endScreen'].update(status='saved-and-reopened-in-Studio',observedStart='10:57:55',observedEnd='11:07:54',
 platformTimebase='60fps display; final endpoint within one frame',memberProfilesNamesBadgesClear=True)
r['coachingEndingLink']['status']='saved-and-reopened-in-Studio'
r['platformObserved'].update(processingComplete=True,midrollEnabled=True,automaticClaims='none found; no revenue effect')
r['studioSettingsObserved']={'processing':'SD and HD complete','privacy':'private','playlist':'게임 수학(Game Math) PART 2',
 'language':'Korean','category':'Education','paidPromotion':False,'aiUsed':True,
 'ads':'enabled; actual midroll checkbox checked and Save disabled after reopening',
 'automaticAdSuitability':'enabled after completed checks','automaticClaims':'none found; no revenue effect'}
write(P/'publishing/youtube-upload.json',r)
m=read(P/'project.json');m['status']='reviewed-private-upload; schedule-transition-pending'
m['publishing'].update(videoId=r['videoId'],privateUploadComplete=True,fullPublishingSettingsComplete=True)
m['finalRender']['openItems']=['Human whole listening and game-IP review pending.','Native Motion Canvas editor playback unverified.','Schedule transition pending.']
write(P/'project.json',m)
registry=read(ROOT/'shared/git-essential-images.json');path=proof.relative_to(ROOT).as_posix()
entry={'path':path,'purpose':'minimal-publishing-proof','sha256':hashlib.sha256(proof.read_bytes()).hexdigest(),
 'reviewedAt':now,'reason':'Actual private uploaded 1080p player; burned Korean caption visible while CC is off.',
 'project':'game-math-lines-circles-v2'}
registry['entries']=[e for e in registry['entries'] if e['path']!=path]+[entry];write(ROOT/'shared/git-essential-images.json',registry)
ignore=ROOT/'.gitignore';text=ignore.read_text(encoding='utf8');exception='!/'+path
if exception not in text.splitlines():ignore.write_text(text.rstrip()+'\n'+exception+'\n',encoding='utf8')
print('Recorded actual private first lines upload and full available settings:',r['videoId'])
