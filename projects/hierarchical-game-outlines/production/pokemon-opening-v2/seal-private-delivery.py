"""Record already-observed private settings and the explicit main transition."""
from pathlib import Path
import json,hashlib,datetime,re
P=Path(__file__).resolve().parent;R=P.parents[3];H=P.parents[1];pub=P/'publishing'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(R).as_posix()
def write(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert not (pub/'main-private-transition-v1.json').exists()
review=read(pub/'private-settings-direct-review-v1.json');upload=read(pub/'youtube-upload-v1.json');video=upload['videoId']
assert re.fullmatch(r'[-_A-Za-z0-9]{11}',video) and video not in ['JoHXz7YtEPw','jBRt3xatdPk'] and review['videoId']==video
assert review['privateSavedAndReopened'] and review['fullAvailableSettingsVerified'] and not review['scheduled'] and not review['baselineMutated']
final=read(P/'final-direct-review-v1.json');collection=read(P/'collection-verification-v2.json');assert collection['exitCode']==0 and len(collection['files'])==4 and final['captionedSha256']==upload['sha256']
assert upload['fileSelectionCount']==1
promotion=read(P/'main-promotion-v1.json');main=H/'project.json';assert sha(main)==promotion['current']['sha256'] and sha(R/promotion['baseline']['path'])==promotion['baseline']['sha256']
backup=P/'pre-private-main-local.json';assert not backup.exists();backup.write_bytes(main.read_bytes());at=datetime.datetime.now(datetime.timezone.utc).isoformat()
upload.update(status='private-saved-settings-verified-user-review-pending',privateSaved=True,fullSettingsComplete=True,sdHdProcessed=review['sdHdProcessed'],automaticCopyrightCheckPassed=review['automaticCopyrightCheckPassed'],automaticAdCheckPassed=review['automaticAdCheckPassed'],verifiedAt=at,studioUrl=f'https://studio.youtube.com/video/{video}/edit',videoUrl=f'https://youtu.be/{video}',settingsReview='private-settings-direct-review-v1.json',pinnedCommentStatus='prepared-private-unavailable')
write(pub/'youtube-upload-v1.json',upload)
j=read(main);j['status']='private-delivered-awaiting-user-review';j['publishing'].update(uploaded=True,actualVideoId=video,videoUrl=upload['videoUrl'],studioUrl=upload['studioUrl'],fullSettingsVerified=True,verification=rel(pub/'private-settings-direct-review-v1.json'),automaticAdCheckPassed=review['automaticAdCheckPassed'],scheduled=False)
j['userReview']=dict(status='pending',humanFullListening=False,pronunciationApproved=False,publicRightsApproved=False,nextVideoAuthorized=False,notes=review['pending']);j['finalRender']['openItems']=review['pending'];write(main,j)
write(pub/'main-private-transition-v1.json',dict(at=at,purpose='New private revision only; JoHXz7YtEPw and scheduled jBRt3xatdPk preserved',before=dict(path=rel(backup),sha256=sha(backup)),current=dict(path=rel(main),sha256=sha(main)),originalBaselineBackupUnchanged=True,baselineMutated=False,scheduled=False))
lp=H/'production/review-ledger.json';ledger=read(lp);ledger['entries'].append(dict(check='pokemon-opening-private-settings',status='pass-for-private-editorial-review',scopeVersion='pokemon-opening-v2',evidence=rel(pub/'private-settings-direct-review-v1.json'),sha256=sha(pub/'private-settings-direct-review-v1.json'),videoId=video,humanFullListening=False,publicRightsApproved=False));ledger.update(updatedAt=at,privateUploadComplete=True,availablePublishingSettingsComplete=True,userReviewPending=True,automaticNextVideo=False);write(lp,ledger)
cp=read(P/'latest-checkpoint.json');cp.update(updatedAt=at,stage='private-complete-ready-selective-git',worker=None,finalPair=True,finalDelivery=True,actualVideoId=video,privateUpload=True,fullSettingsComplete=True,next='Selective Git delivery once, then stop for the user to review this video.',gitVerification='publishing/production-git-verification-v1.json',gitDelivered=False);write(P/'latest-checkpoint.json',cp)
print(json.dumps(dict(videoId=video,privateSettings=True,mainSha256=sha(main),gitPending=True)))
