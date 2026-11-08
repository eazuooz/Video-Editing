"""Record only the user's two new production selections; preserve other work."""
from pathlib import Path
import sys, json
from datetime import datetime, timezone, timedelta
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'production/batches/design-25-30-review-actions-20261029'))
from scoped_json import load,patch
now=datetime.now(timezone(timedelta(hours=9))).isoformat()
c=ROOT/'shared/publishing/video-production-control.json'; raw=c.read_bytes(); data=load(raw)
batch=data['animationContrastRevision20261108']
batch.update(status='approved-roster-production-in-progress',candidateUserApproval={'at':now,'text':'이 목록으로 진행','candidate':'production/batches/animation-18-20261031/contrast-v5/candidate-review.json'},fullLocalProductionAuthorized=True,renderAuthorized=True,currentAuthorizedStage='Secure and view independent concept-matched FHD sources, preserve reference teaching logic, revise 17 topic-specific comparison/stage demos and corresponding game passages; finish combined local review. Preserve A03 and old masters. No upload or scheduling.',updatedAt=now)
raw=patch(raw,['animationContrastRevision20261108'],batch)
old=data['ai2dUpload20261108'];old.update(status='superseded-private-draft-rebuild-required',videoId='t7Li-IzqJyk',studioUrl='https://studio.youtube.com/video/t7Li-IzqJyk/edit',updatedAt=now)
raw=patch(raw,['ai2dUpload20261108'],old)
revision={'selectedAt':now,'userEvidence':'ai 픽셀영상 다시 만들어야해 게임 바뀐걸로 한거야 ?','status':'latest-game-v6-video-revision-in-progress','baselineRevision':'room-v3','baselineMasterSha256':'8e5fc1902c8c1ade2637769a496c613a5bb45d45758ca14eb94c7b345c6a3d1c','siteVersion':6,'siteCommit':'0c294d8509dacfee2057f6b47b4dda414c2222b3','publicGameUrl':'https://yamyam-cartographers-room.eazuooz.chatgpt.site/','scope':'Replace outdated room/game demonstrations and align production explanations with the actual v6 game; preserve tool demonstrations and useful approved PCM; add needed current-feature narration; deliver new FHD60 local review and 4 outputs. Do not present v3 as latest.','fullLocalProductionAuthorized':True,'renderAuthorized':True,'youtubeUploadAfterSameVersionReview':True,'sameVersionUserReview':False,'youtubeAuthorizedNow':False,'publicPublicationAuthorized':False,'schedulingAuthorized':False,'deletionAuthorized':False,'obsoleteDraftVideoId':'t7Li-IzqJyk','preserveOldMasters':True,'checkpoint':'projects/ai-2d-game-assets/production/room-v4-video/checkpoint.json'}
raw=patch(raw,['ai2dLatestGameVideo20261108'],revision); c.write_bytes(raw)
b=ROOT/'production/batches/animation-18-20261031/contrast-v5';(b/'batch.json').write_text(json.dumps(batch,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
cp=load((b/'checkpoint.json').read_bytes());cp.update(stage=batch['status'],candidateUserApproval=batch['candidateUserApproval'],productionStarted=True,next='Source acquisition and topic-specific comparison/stage revision; no platform mutation');(b/'checkpoint.json').write_text(json.dumps(cp,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
r=ROOT/'projects/ai-2d-game-assets/production/room-v4-video';r.mkdir(parents=True,exist_ok=True);(r/'authorization.json').write_text(json.dumps(revision,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
p=ROOT/'projects/ai-2d-game-assets/publishing/room-v3-upload-20261108/youtube-upload.json';receipt=load(p.read_bytes());receipt.update(status='superseded-private-draft-rebuild-required',privacy='private',captionedMasterSha256=receipt['masterSha256'],observedAt=now,watchUrl='https://www.youtube.com/watch?v=t7Li-IzqJyk',userRequestedRevision=True,uploadedVersionIsLatestGame=False,completedSettings=['title-ko','thumbnail','playlist','video-language-ko','manual-ko-srt-published','manual-en-srt-published','english-title-description-published'],unfinishedSettings=['ko-description','tags','card','end-screen','ad-suitability-user','finish-upload-wizard'],newRenderReviewRequired=True,publicPublication=False,scheduled=False);p.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'animation':batch['status'],'ai2d':revision['status'],'oldUpload':receipt['status']},ensure_ascii=False))
