"""Record verified private upload; preserve a still-running ad suitability check."""
from pathlib import Path
import json,hashlib,datetime,shutil
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
S=ROOT/'shared/output/game-math-part2-teaching-revision/interpolation'
slug='game-math-interpolation-paths-v2';P=ROOT/'projects'/slug
read=lambda p:json.loads(p.read_text(encoding='utf8'))
def write(p,d):p.parent.mkdir(exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(8388608),b''):h.update(block)
 return h.hexdigest()
now=datetime.datetime.now().astimezone().isoformat();d=read(P/'publishing/youtube-upload.json');t=read(P/'production/timeline.json');m=read(P/'project.json')
assert d['videoId']=='_SzbJR4R6OI'
assert sha(ROOT/d['video']['path'])==d['video']['sha256']==read(P/'production/current-pixel-review.json')['sha256']
details=(S/'first-processed-details-ax.txt').read_text(encoding='utf8')
assert all(x in details for x in ['_SzbJR4R6OI','고화질 완료','비공개','captioned.mp4','button 교육','동영상 언어','한국어'])
ads=(S/'first-ads-verified-ax.txt').read_text(encoding='utf8');selected=(S/'first-ads-selected-ax.txt').read_text(encoding='utf8');claims=(S/'first-claims-verified-ax.txt').read_text(encoding='utf8')
assert 'radio button 사용, Value: 1' in selected and '미드롤 광고 게재, Value: 1' in ads
assert '동영상에서 소유권 주장이 발견되지 않았습니다' in claims
ad_check_pending='text 검사 중' in ads
assert ad_check_pending or 'text 사용' in ads,'Preserve and inspect a different automatic ad result'
language=(S/'first-language-save-ax.txt').read_text(encoding='utf8')
assert all(x in language for x in ['영어(미국)','1개 게시됨','게시됨'])
end=(S/'first-endscreen-reopened-ax.txt').read_text(encoding='utf8');card=(S/'first-card-reopened-ax.txt').read_text(encoding='utf8')
assert all(x in end for x in ['15:07:20','15:17:19','구독:','재생목록:','링크: https://www.yamyamcoding.com/1430b1ff-a61e-8040-a542-d672d5d25328'])
assert '티저 시작 시간: 0분 0초 0프레임' in card and 'Value: 프로그래밍 과외' in card
player=read(S/'first-uploaded-cc-off.json');v=player['observation']['video'][0]
assert player['videoId']==d['videoId'] and (v['width'],v['height'])==(1920,1080) and abs(v['duration']-t['seconds'])<.1
assert player['observation']['cc'] and all(c.get('pressed') in [None,'false'] and c.get('checked') in [None,'false'] for c in player['observation']['cc'])
proof=P/'publishing/proof';proof.mkdir(exist_ok=True)
for name in ['processed-details-ax.txt','ads-selected-ax.txt','ads-verified-ax.txt','claims-verified-ax.txt','language-save-ax.txt','endscreen-reopened-ax.txt','card-reopened-ax.txt','uploaded-cc-off.json','platform-caption-proof.png']:
 shutil.copy2(S/('first-'+name),proof/name)
image=proof/'platform-caption-proof.png';rel=image.relative_to(ROOT).as_posix()
registry=read(ROOT/'shared/git-essential-images.json');registry['entries']=[e for e in registry['entries'] if e['path']!=rel]+[{'path':rel,'purpose':'minimal-publishing-proof','reason':'Actual private YouTube1080p player directly viewed with CC off; burned bottom Korean captions and tracked red body direction visible.','sha256':sha(image),'reviewedAt':now,'project':slug}];write(ROOT/'shared/git-essential-images.json',registry)
ignore=ROOT/'.gitignore';text=ignore.read_text(encoding='utf8');exception='!/'+rel
if exception not in text.splitlines():ignore.write_text(text.rstrip()+'\n'+exception+'\n',encoding='utf8')
d.update(status='reviewed captioned private upload; available settings verified'+('; automatic ad suitability still checking' if ad_check_pending else ''),privateUploadComplete=True,fullPublishingSettingsComplete=not ad_check_pending,availableStudioSettingsComplete=True,transferAndProcessing='complete; HD1920x1080 and CC-off burned caption pixels verified',completedAt=now)
d['englishMetadata']['status']='saved-published-in-English-language-row'
for s in d['subtitles']:s['status']='manual-timed-file-published-in-Studio'
d['thumbnail']['status']='uploaded-saved-and-reopened-in-Studio'
d['coachingCard']['status']='saved-and-reopened-in-Studio';d['coachingEndingLink']['status']='saved-and-reopened-in-Studio'
d['endScreen'].update(status='saved-and-reopened-in-Studio',observedStart='15:07:20',observedEnd='15:17:19',platformTimebase='60fps display; final endpoint within one frame',memberProfilesNamesBadgesClear=True,originalThankYouTitleClear=True,printedCoachingUrlClear=True)
d['burnedCaptionVerification'].update(status='verified-in-actual-uploaded-player',proof=rel,playerObservation='publishing/proof/uploaded-cc-off.json',playerCaptionsOff=True)
d['studioSettingsObserved']={'processing':'SD and HD complete','privacy':'private','playlist':'게임 수학(Game Math) PART2','language':'Korean','category':'Education','paidPromotion':False,'aiUsed':True,'ads':'saved enabled; midroll checked','automaticAdSuitability':'checking; not approved' if ad_check_pending else 'enabled after actual completed check','automaticClaims':'none found; no revenue effect','proof':'publishing/proof'}
d['humanListening']='pending';d['rightsReview']='Recording reuse statements retained; game-IP/human review pending';write(P/'publishing/youtube-upload.json',d)
m['status']='reviewed-private-revision-delivered'+('; automatic-ad-check-pending' if ad_check_pending else '; schedule-and-git-pending');m['publishReady']=False
m['publishing'].update(actualVideoId=d['videoId'],availableStudioSettingsSaved=True,privateUploadComplete=True,fullPublishingSettingsComplete=not ad_check_pending)
m['finalRender']['openItems']=['Human whole listening and game-IP review pending.','Actual schedule replacement and selective Git delivery pending.','Native Motion Canvas editor playback unverified.']+(['Automatic ad suitability still checking.'] if ad_check_pending else []);write(P/'project.json',m)
pixel=read(P/'production/current-pixel-review.json');pixel['uploadedPlayerCaptionProof']='publishing/proof/uploaded-cc-off.json';pixel['platformComplete']=not ad_check_pending;write(P/'production/current-pixel-review.json',pixel)
q=read(B/'queue.json');item=next(i for i in q['items'] if i['slug']=='game-math-rotation-interpolation');item['revision'].update(flowReviewPassed=True,annotationMotionReviewPassed=True,narrationComplete=True,renderComplete=True,localOutputsCollected=True,videoIds=['_SzbJR4R6OI','n-k7zwaSum0'],privateUploadComplete=True,fullPublishingSettingsComplete=not ad_check_pending,privateEpisodeCompletions={'game-math-rotation-conversions-v2':True,'game-math-interpolation-paths-v2':True})
item['status']='two-reviewed-private-episodes; '+('first-automatic-ad-check-pending' if ad_check_pending else 'selective-git-and-schedule-pending');q['execution']['stage']='Interpolation pair privately saved; '+('first ad suitability still checking; ' if ad_check_pending else '')+'lines/bounds new TTS and CPU explanation/tracking preparation active.';q['updatedAt']=now;write(B/'queue.json',q)
write(B/'interpolation-first-private-completion.json',{'observedAt':now,'slug':slug,'videoId':d['videoId'],'sha256':d['video']['sha256'],'privateUploadComplete':True,'availableStudioSettingsComplete':True,'fullPublishingSettingsComplete':not ad_check_pending,'automaticAdSuitabilityPending':ad_check_pending,'humanListening':'pending','gameIPHumanRights':'pending','scheduled':False,'gitDelivery':'pending','fullBatchCompleted':False})
print(json.dumps({'privateUploadComplete':True,'availableSettingsVerified':True,'automaticAdSuitabilityPending':ad_check_pending,'scheduleAndGitComplete':False}))
