"""Seal directly verified second-episode delivery, preserving pending reviews."""
from pathlib import Path
import json,hashlib,datetime,shutil
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
S=ROOT/'shared/output/game-math-part2-teaching-revision/interpolation'
slug='game-math-rotation-conversions-v2';P=ROOT/'projects'/slug
read=lambda p:json.loads(p.read_text(encoding='utf8'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(8388608),b''):h.update(block)
 return h.hexdigest()
now=datetime.datetime.now().astimezone().isoformat();d=read(P/'publishing/youtube-upload.json');t=read(P/'production/timeline.json');m=read(P/'project.json')
assert d['videoId']=='n-k7zwaSum0'
assert sha(ROOT/d['video']['path'])==d['video']['sha256']==read(P/'production/current-pixel-review.json')['sha256']
details=(S/'second-processed-details-ax.txt').read_text(encoding='utf8')
ads=(S/'second-ads-verified-ax.txt').read_text(encoding='utf8');claims=(S/'second-claims-verified-ax.txt').read_text(encoding='utf8')
assert all(x in details for x in ['n-k7zwaSum0','고화질 완료','비공개','captioned.mp4'])
assert 'text 사용' in ads and '미드롤 광고 게재, Value: 1' in ads
assert '동영상에서 소유권 주장이 발견되지 않았습니다' in claims
language=(S/'second-language-save-ax.txt').read_text(encoding='utf8')
assert '영어(미국)' in language and '1개 게시됨' in language and '게시됨' in language
end=(S/'second-endscreen-reopened-ax.txt').read_text(encoding='utf8');card=(S/'second-card-reopened-ax.txt').read_text(encoding='utf8')
assert all(x in end for x in ['13:51:05','14:01:04','구독:','재생목록:','링크: https://www.yamyamcoding.com/1430b1ff-a61e-8040-a542-d672d5d25328'])
assert '티저 시작 시간: 0분 0초 0프레임' in card and 'Value: 프로그래밍 과외' in card
player=read(S/'second-uploaded-cc-off.json');v=player['observation']['video'][0]
assert player['videoId']==d['videoId'] and v['width']==1920 and v['height']==1080 and abs(v['duration']-t['seconds'])<.1
assert player['observation']['cc'] and all(c.get('pressed') in [None,'false'] and c.get('checked') in [None,'false'] for c in player['observation']['cc'])
proof=P/'publishing/proof';proof.mkdir(exist_ok=True)
for name in ['processed-details-ax.txt','ads-verified-ax.txt','claims-verified-ax.txt','language-save-ax.txt','endscreen-reopened-ax.txt','card-reopened-ax.txt','uploaded-cc-off.json','platform-caption-proof.png']:
 shutil.copy2(S/('second-'+name),proof/name)
image=proof/'platform-caption-proof.png';rel=image.relative_to(ROOT).as_posix()
registry=read(ROOT/'shared/git-essential-images.json');registry['entries']=[e for e in registry['entries'] if e['path']!=rel]+[{'path':rel,'purpose':'minimal-publishing-proof','reason':'Actual private YouTube1080p player directly viewed with CC off; burned Korean bottom captions and tracked gameplay math visible.','sha256':sha(image),'reviewedAt':now,'project':slug}]
write(ROOT/'shared/git-essential-images.json',registry)
ignore=ROOT/'.gitignore';text=ignore.read_text(encoding='utf8');exception='!/'+rel
if exception not in text.splitlines():ignore.write_text(text.rstrip()+'\n'+exception+'\n',encoding='utf8')
d.update(status='reviewed Korean-captioned revision uploaded privately; HD and available Studio settings verified',privateUploadComplete=True,fullPublishingSettingsComplete=True,transferAndProcessing='complete; SD/HD badges,1920x1080 uploaded player, CC-off burned caption pixels verified',completedAt=now)
d['englishMetadata']['status']='saved-published-in-English-language-row'
for s in d['subtitles']:s['status']='manual-timed-file-published-in-Studio'
d['thumbnail']['status']='uploaded-saved-and-reopened-in-Studio'
d['coachingCard']['status']='saved-and-reopened-in-Studio';d['coachingEndingLink']['status']='saved-and-reopened-in-Studio'
d['endScreen'].update(status='saved-and-reopened-in-Studio',observedStart='13:51:05',observedEnd='14:01:04',platformTimebase='60fps display; end rounded one frame',memberProfilesNamesBadgesClear=True,originalThankYouTitleClear=True,printedCoachingUrlClear=True)
d['burnedCaptionVerification'].update(status='verified-in-actual-uploaded-player',proof=rel,playerObservation='publishing/proof/uploaded-cc-off.json',playerCaptionsOff=True)
d['studioSettingsObserved']={'processing':'SD and HD complete','privacy':'private','playlist':'게임 수학(Game Math) PART2','language':'Korean','category':'Education','paidPromotion':False,'aiUsed':True,'ads':'enabled; midroll checked; reopened actual saved state','automaticAdAndRightsChecks':'Actual claims UI:none found, no revenue effect; ads enabled. Platform checks do not complete human listening or game-IP review.','proof':'publishing/proof'}
d['humanListening']='pending';d['rightsReview']='Recording reuse statements retained; game-IP/human review pending';write(P/'publishing/youtube-upload.json',d)
m['status']='reviewed-private-revision-delivered; schedule-and-git-pending';m['publishing'].update(actualVideoId=d['videoId'],availableStudioSettingsSaved=True,privateUploadComplete=True,fullPublishingSettingsComplete=True)
m['publishReady']=False;m['finalRender']['openItems']=['Human whole listening and game-IP review pending.','Actual schedule replacement and selective Git delivery pending.','Native Motion Canvas editor playback unverified.'];write(P/'project.json',m)
pixel=read(P/'production/current-pixel-review.json');pixel['uploadedPlayerCaptionProof']='publishing/proof/uploaded-cc-off.json';pixel['platformComplete']=True;write(P/'production/current-pixel-review.json',pixel)
q=read(B/'queue.json');item=next(i for i in q['items'] if i['slug']=='game-math-rotation-interpolation');item['revision'].update(flowReviewPassed=True,annotationMotionReviewPassed=True,narrationComplete=True,renderComplete=True,localOutputsCollected=True,videoIds=['_SzbJR4R6OI','n-k7zwaSum0'],privateUploadComplete=False,privateEpisodeCompletions={'game-math-rotation-conversions-v2':True,'game-math-interpolation-paths-v2':False})
item['status']='two-reviewed-local-episodes; second-private-delivered; first-transfer-in-progress';q['execution']['stage']='Interpolation both local moving/caption/native reviews complete; second private settings verified; first private transfer in progress; lines/bounds native gameplay comparison and additive planning active.';q['updatedAt']=now;write(B/'queue.json',q)
write(B/'interpolation-second-private-completion.json',{'observedAt':now,'slug':slug,'videoId':d['videoId'],'sha256':d['video']['sha256'],'privateUploadComplete':True,'availableStudioSettingsComplete':True,'humanListening':'pending','gameIPHumanRights':'pending','scheduled':False,'gitDelivery':'pending','firstEpisodeTransfer':'in progress','fullBatchCompleted':False})
print('Second interpolation episode private delivery verified; first transfer and remaining batch preserved.')
