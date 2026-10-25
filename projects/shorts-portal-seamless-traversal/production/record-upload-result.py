"""Record observed Studio settings for only the approved seventh video."""
import datetime,json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[1];R=P.parents[1]
def read(p):return json.loads(p.read_text(encoding='utf8'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
d=read(P/'production/delivery.json');a=read(P/'publishing/upload-approval.json');master=d['files']['captioned'];assert master['sha256']==a['masterSha256']
assert hashlib.sha256(Path(master['path']).read_bytes()).hexdigest()==master['sha256']
receipt=read(P/'publishing/youtube-upload.json')
receipt.update(status='uploaded-private',privacy='private',updatedAt=now,platformStateVerified=True,
 masterVersion=d['masterVersion'],userAcceptance=a,video=master,
 metadata={'title':(P/'publishing/title.ko.txt').read_text(encoding='utf8').strip(),'description':(P/'publishing/description.ko.txt').read_text(encoding='utf8'),'language':'ko','category':'교육','madeForKids':False,'paidPromotion':False,'alteredContent':False,
 'alteredContentBasis':'Game recording, explicitly illustrated Unity demonstration and narration; no fabricated real-person actions, real event/location, photoreal event or generated musical focus in this video.',
 'tags':['게임개발','포털','Portal','좌표 변환','게임프로그래밍','클리핑','Portal Traversal','Unity']},
 englishMetadata={'title':(P/'publishing/title.en.txt').read_text(encoding='utf8').strip(),'description':(P/'publishing/description.en.txt').read_text(encoding='utf8'),'status':'published-and-reopened-in-studio'},
 subtitles={'ko':{'file':d['files']['ko'],'status':'manual-upload-published-in-studio'},'en':{'file':d['files']['en'],'status':'manual-upload-published-and-reopened-in-studio'},'watchPlayerPropagation':'not-yet-available-in-initial-watch-player-check'},
 playlist={'title':'도움이 되는 게임 개발 이야기','status':'saved-and-reopened'},
 thumbnail={'status':'generated-frame-retained','customFileUploaded':False},
 checks={'copyright':'no-issues-observed','advertiserSuitability':'in-progress-at-last-observation','selfRating':'none-of-the-listed-categories; educational nonviolent portal traversal','hdProcessing':'complete'},
 platformPlayback={'qualityMenu':'1080p60 HD','burnedCaptionsVisibleWithCcOff':True,'revisedTwoCameraSceneObservedAtSeconds':16,'evidence':'production/local/upload-v5-evidence/youtube-1080p60.png','wholePlaybackListeningClaimed':False},
 shortsUnavailableElements=['External card and long-form end-screen controls not offered in observed Shorts upload flow'],
 pinnedComment={'status':'pending-video-publication','draft':'publishing/pinned-comment.ko.txt','reason':'Watch page states comments unavailable for private videos.'},
 fullSettings=False,remainingPlatformChecks=['YouTube automatic advertiser-suitability check','Selectable CC propagation in watch player','Unreviewed automatic dubbed-audio drafts left unchanged','Public release/schedule not inferred for a new seventh upload without an existing baseline'])
save(P/'publishing/youtube-upload.json',receipt)
d.update(youtube=receipt['url'],youtubeState='private',youtubeUploadReceipt='projects/'+P.name+'/publishing/youtube-upload.json',humanReview='accepted-for-upload',remainingReview=['No additional human-review gate added; upload accepted by the user. Whole listening was not explicitly confirmed.']);save(P/'production/delivery.json',d)
cp=read(P/'production/checkpoint.json');cp.update(status='uploaded-private',youtubeUpload=True,youtubeVideoId=receipt['videoId'],youtubeUrl=receipt['url'],youtubeState='private',youtubeReceipt='projects/'+P.name+'/publishing/youtube-upload.json',updatedAt=now,next='Selected upload completed; advertiser check and player CC propagation remain platform processing. No automatic next video or public schedule.');save(P/'production/checkpoint.json',cp)
project=read(P/'project.json');project.update(status='uploaded-private',youtubeVideoId=receipt['videoId'],youtubeUrl=receipt['url']);save(P/'project.json',project)
review=read(P/'production/review-ledger.json');review['youtubeUploadResult']={'receipt':'publishing/youtube-upload.json','videoId':receipt['videoId'],'privacy':'private','captionedSha256':master['sha256'],'humanAcceptance':a};save(P/'production/review-ledger.json',review)
meta=read(P/'publishing/metadata-draft.json');meta.update(status='uploaded-private',humanReview='accepted-for-upload',youtubeVideoId=receipt['videoId']);save(P/'publishing/metadata-draft.json',meta)
wpath=R/'shared/publishing/shorts-worklist.json';w=read(wpath);row=next(x for x in w['rows'] if x['slug']==P.name);row.update(status='uploaded-private',review='accepted-for-upload',youtube=receipt['url'],youtubeState='private',publishingReceipt='projects/'+P.name+'/publishing/youtube-upload.json',updatedAt=now);w['updatedAt']=now;save(wpath,w)
cpath=R/'shared/publishing/video-production-control.json';c=read(cpath);auth=c['portalTraversalShortsAuthorization'];auth['currentRevision'].update(status='uploaded-private',uploadResult={'videoId':receipt['videoId'],'privacy':'private','sha256':master['sha256'],'receipt':'projects/'+P.name+'/publishing/youtube-upload.json','baselineDeleted':False})
for x in auth['deliveries']:
 if x['slug']==P.name:x.update(humanReview='accepted-for-upload',youtube=receipt['url'],youtubeState='private')
save(cpath,c)
print(json.dumps({'url':receipt['url'],'privacy':'private','sha256':master['sha256'],'deletedVideoIds':[]},ensure_ascii=False))
