"""Record only observed upload/packaging facts, preserving unrelated shared JSON bytes."""
from pathlib import Path
import json, importlib.util, sys
from datetime import datetime
from zoneinfo import ZoneInfo
sys.dont_write_bytecode=True
H=Path(__file__).resolve().parent; R=H.parents[3]; P=R/'projects/ai-2d-game-assets'; V=P/'production/room-v4-video'
sp=importlib.util.spec_from_file_location('scope',R/'projects/kind-to-beginners/publishing/botw-v4/scoped-publishing-commit.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
def read(p):return json.loads(p.read_text('utf-8-sig'))
def save(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
now=datetime.now(ZoneInfo('Asia/Seoul')).isoformat(); pkg=read(H/'packaging-v2.json');thumb=read(H/'thumbnail-v2.provenance.json')
receipt=read(H/'youtube-upload.json');receipt.update(updatedAt=now,status='private-draft-ad-review-and-final-settings-pending',titleKo=pkg['selectedTitleKo'],thumbnail=str(H/'thumbnail-v2.png'),thumbnailSHA256=thumb['finalSHA256'],metadataVerified=True,completeSettings=False)
receipt['completedSettings']=['title-ko-saved-reopened','description-ko-saved-reopened','thumbnail-v2-actual-game-saved-reopened','playlist','video-language-ko','education-category','targeted-tags','manual-ko-srt-published','manual-en-srt-published','english-title-description-v1-published-reopened','00:00-coaching-card-saved']
receipt['unfinishedSettings']=['english-title-v2-sync','end-screen','ad-suitability-user','finish-upload-wizard']
receipt['browserIssue']='After title/thumbnail save, original tab stopped responding. Fresh tab reopened and visibly verified saved Korean title/thumbnail. Language controls on recovered tab did not open; newer English title remains local only.'
receipt['proof']='projects/ai-2d-game-assets/production/local/room-v4-video/upload-proof/title-thumbnail-v2-saved.jpg'
receipt['platformEvidence']='Fresh Studio edit page visibly showed new Korean title and actual-game thumbnail; save disabled, duration20:55, SD/HD complete. Draft still present; no advertising submission inferred from title-request reply.'
save(H/'youtube-upload.json',receipt)
delivery=read(V/'delivery.json');delivery['youtubeUploaded']=True;delivery['youtubeVideoId']=receipt['videoId'];delivery['youtubeCompleteSettings']=False;save(V/'delivery.json',delivery)
cp=read(V/'checkpoint.json');cp.update(updatedAt=now,stage=receipt['status'],delivery=delivery,youtubeVideoId=receipt['videoId'],publishingReceipt=str(H/'youtube-upload.json'),next='User ad-suitability submission; finish remaining settings in same video, no duplicate upload.');save(V/'checkpoint.json',cp)
project=read(P/'project.json');project['status']=receipt['status'];project['titles']['ko']=pkg['selectedTitleKo'];project['currentRevision'].update(humanReview='approved-same-sha256',youtubeUploaded=True,youtubeVideoId=receipt['videoId'],completeSettings=False);save(P/'project.json',project)
ledger=read(P/'production/review-ledger.json');ledger['stage']=receipt['status'];ledger['platform'].update(youtubeUploaded=True,uploadAuthorizedNow=True,videoId=receipt['videoId'],status=receipt['status'],completeSettings=False,receipt=str(H/'youtube-upload.json'));save(P/'production/review-ledger.json',ledger)
C='shared/publishing/video-production-control.json';W='shared/publishing/video-worklist.json';D='docs/VIDEO_WORKLIST.md';I='shared/git-essential-images.json'
control=read(R/C)['ai2dLatestGameVideo20261108'];control.update(status=receipt['status'],updatedAt=now,videoId=receipt['videoId'],uploadReceipt=str(H/'youtube-upload.json'),titleThumbnailRevision='actual-game-v2',completeSettings=False)
row=next(x for x in read(R/W)['rows'] if x['id']=='S-AI2D')
update={'title':pkg['selectedTitleKo'],'videoId':receipt['videoId'],'url':receipt['url'],'reviewStatus':'같은 SHA256 새 검수본 사용자 확인 완료','humanApproval':'새 검수본 확인했어. 이 버전 업로드','platformStatus':'새 영상 업로드·HD 완료, 실제 게임 썸네일 적용 · 비공개 초안 · 광고 평가/마지막 설정 대기','executionStatus':receipt['status'],'updatedAt':now,'latestRevision':project['currentRevision']}
evidence=list(row.get('evidence',[]))
for x in ['projects/ai-2d-game-assets/publishing/room-v4-upload-20261108/youtube-upload.json','projects/ai-2d-game-assets/publishing/room-v4-upload-20261108/packaging-v2.json']:
 if x not in evidence:evidence.append(x)
update['evidence']=evidence
essential={'path':'projects/ai-2d-game-assets/publishing/room-v4-upload-20261108/thumbnail-v2.png','purpose':'delivery-thumbnail','reason':'User-requested actual latest game capture and AI pixel-tool-to-game headline; 1280x720 and375px reviewed; actually saved in Studio.','sha256':thumb['finalSHA256'],'reviewedAt':now,'project':'ai-2d-game-assets'}
owned=[str(p.relative_to(R)).replace('\\','/') for p in H.iterdir() if p.is_file() and (p.suffix in {'.json','.py','.cjs','.txt'} or p.name=='thumbnail-v2.png') and p.name!='commit-spec.json']
owned += [str(p.relative_to(R)).replace('\\','/') for p in [P/'project.json',P/'production/review-ledger.json',V/'checkpoint.json',V/'delivery.json',V/'final-review.json']]
spec={'scope':'ai2d-room-v4-reviewed-upload-packaging-v2','ownedPaths':sorted(set(owned)),'control':control,'worklistUpdate':update,'essentialImage':essential,'tableReview':' 同一SHA256 사용자 확인 완료 ','tablePlatform':' 새 영상 비공개 초안·광고평가 대기·제목/실제게임 썸네일 적용 '}
save(H/'commit-spec.json',spec)
