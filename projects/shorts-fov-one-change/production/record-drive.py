"""Bind the actual uploaded revision, access and playback to this exact Short."""
from pathlib import Path
import json,hashlib,datetime,sys
R=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parents[1];ready='--playback-ready' in sys.argv
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def save(p,j):Path(p).write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
now=datetime.datetime.now(datetime.timezone.utc).isoformat();file=R/'output'/P.name/(P.name+'.captioned.mp4');digest=hashlib.sha256(file.read_bytes()).hexdigest()
assert digest=='ab40288ad2e6376c5176b1895c7c0bc7abaa055f467e2ebbb80b2b785a213d86' and file.stat().st_size==1988822
d=dict(schemaVersion=1,revision='v1-fov-complete-30s',fileId='1lBQbzBFIvTVrVKvlSMmWNYaDSKSxvrAb',url='https://drive.google.com/file/d/1lBQbzBFIvTVrVKvlSMmWNYaDSKSxvrAb/view',fileName='얌얌코딩_쇼츠01_FOV를_넓혔더니_30초_v1_1080x1920_60fps.mp4',driveRevisionId='0B__JCPwFbAsxd2hJdnBuR2ppdkVpeko3ZFYraEJEUnY5akpBPQ',revisionModifiedAt='2026-10-18T13:39:59.796Z',localUploadedMaster=str(file.relative_to(R)).replace('\\','/'),localUploadedMasterSha256=digest,bytes=1988822,remoteMetadataBytes=1988822,remoteChecksumReturned=False,uploadToolAcceptedExactFile=True,sourceFormat=dict(width=1080,height=1920,fps=60,frames=1800,seconds=30),permission=dict(ownerOnly=True,source='Actual Drive metadata shows owner only; no public/link permission added'),viewerAccess='verified signed-in owner' if ready else 'metadata owner access; actual viewer loading/processing',playback='verified actual Drive player' if ready else 'processing; actual player confirmation pending',humanFinalReview='pending exact version',youtubeUploaded=False,scheduledAt=None,publicationTime='19:00 Asia/Seoul after exact-version approval',priorRejectedDraftPreserved=True,verifiedAt=now)
if ready:
 d['playbackProof']='projects/shorts-fov-one-change/production/local/drive-final-review.png'
 assert (R/d['playbackProof']).is_file(),'Save real Drive player screenshot first.'
 d['observedPlayerQuality']='1080p available/selected'
 d['observedPlayback']='Actual Drive player advanced with the current car comparison and captions, duration0:30.'
save(P/'publishing/drive-review.json',d)
project=read(P/'project.json');project['status']='awaiting-user-Drive-final-review' if ready else 'Drive-uploaded-processing';project['publishing'].update(driveReview='publishing/drive-review.json',driveId=d['fileId'],userReview='pending exact version',youtubeId=None,scheduleSaved=False);save(P/'project.json',project)
checkpoint=read(P/'production/checkpoint.json');checkpoint.update(stage='awaiting-final-user-review' if ready else 'Drive-uploaded-processing',next='Stop for exact-version user final review. No YouTube upload/scheduling or next draft before approval.',driveId=d['fileId'],drivePlayback=d['playback'],humanFinalReview='pending',youtubeUploaded=False,scheduleSaved=False);save(P/'production/checkpoint.json',checkpoint)
ledger=read(P/'production/review-ledger.json');ledger['driveReview']=d;ledger['pending']=['현재 Drive 버전의 최종 사용자 검수·전체 청취/발음','승인 후 같은 파일 YouTube 게시·실제 Shorts UI 확인']+([] if ready else ['Drive 스트리밍 재생 완료 확인']);save(P/'production/review-ledger.json',ledger)
worklist=read(R/'shared/publishing/shorts-worklist.json');row=next(x for x in worklist['rows'] if x['slug']==P.name);row.update(productionStatus='30초·FHD60·4파일 수집·Drive 업로드 완료',reviewStatus='최종 사용자 검수 대기' if ready else 'Drive 재생 처리 확인 중',driveId=d['fileId'],driveRevisionId=d['driveRevisionId'],captionedSha256=digest,userApproval='pending-exact-version',youtubeId=None,scheduledAt=None);worklist['updatedAt']=now;save(R/'shared/publishing/shorts-worklist.json',worklist)
print(d['url'],d['playback'])
