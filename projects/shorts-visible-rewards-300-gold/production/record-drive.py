"""Bind actual uploaded Drive version to the collected approved-review master."""
from pathlib import Path
import json,hashlib,datetime,sys
R=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parents[1];now=datetime.datetime.now(datetime.timezone.utc).isoformat();ready='--playback-ready' in sys.argv
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def save(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
master=R/'output'/P.name/(P.name+'.captioned.mp4');digest=hashlib.sha256(master.read_bytes()).hexdigest();assert digest=='eac6511b5f63cab8ffd6ba58e3db7bbba0a542345ce7c62b389e5346881ba21c' and master.stat().st_size==5853598
d=dict(schemaVersion=1,revision='v2-minus-and-peak-fix',fileId='1D0hzamkdeOZTy-o__uq_TrPmi_2eW_w6',url='https://drive.google.com/file/d/1D0hzamkdeOZTy-o__uq_TrPmi_2eW_w6/view',fileName='얌얌코딩_쇼츠01_300골드가_부족하다면_v2_1080x1920_60fps.mp4',driveRevisionId='0B__JCPwFbAsxQlc4aXU5dlV1OUMrYURVcDNPMjJiZ1VYNDkwPQ',revisionModifiedAt='2026-10-18T13:04:15.176Z',uploadedLocalMaster=str(master.relative_to(R)).replace('\\','/'),localUploadedMasterSha256=digest,bytes=5853598,remoteMetadataBytes=5853598,sourceFormat=dict(width=1080,height=1920,fps=60,frames=1812,seconds=30.2),uploadToolAcceptedExactFile=True,remoteChecksumReturned=False,remoteRawFileStreamAvailable=True,permission=dict(ownerOnly=True,observedFrom=['Drive metadata owner permission','Drive viewer shows 나에게만 공개'],publicSharingAdded=False),viewerAccess='verified signed-in owner',playback='verified actual Drive player' if ready else 'processing observed; recheck before final delivery',humanFinalReview='pending exact version',youtubeUploaded=False,scheduledAt=None,approvedPublicTime='19:00 Asia/Seoul after exact-version human approval',createdAt='2026-10-18T13:04:15.176Z',verifiedAt=now)
if ready:
 d['playbackProof']='shared/output/shorts-inventory/drive-short01-v2-playback.png'
 assert (R/d['playbackProof']).is_file(),'Save actual Drive player proof before recording playback ready.'
 d['observedPlayerQuality']='1080p selected; 720p and 360p also available'
 d['observedPlayback']='Actual player advanced from 0:05 to 0:30/end; sought back to 0:20 and verified the diagram and captions.'
save(P/'publishing/drive-review.json',d)
p=read(P/'project.json');p['status']='awaiting-user-Drive-final-review' if ready else 'Drive-uploaded-processing';p['publishing']=dict(driveReview='publishing/drive-review.json',driveId=d['fileId'],userReview='pending',youtubeId=None,scheduleSaved=False,publicationTime='19:00 Asia/Seoul');save(P/'project.json',p)
c=read(P/'production/checkpoint.json');c.update(stage='awaiting-final-user-review' if ready else 'Drive-uploaded-processing',next='Stop for final user review. Publish the same approved version in the next available19:00 slot only after approval; do not start another pending draft.',driveId=d['fileId'],drivePlayback=d['playback'],humanFinalReview='pending',youtubeUploaded=False,scheduleSaved=False);save(P/'production/checkpoint.json',c)
w=read(R/'shared/publishing/shorts-worklist.json');w['rows'][0].update(productionStatus='v2 완성·4파일 수집·Drive 업로드 완료',reviewStatus='최종 사용자 검수 대기' if ready else 'Drive 재생 처리 확인 중',driveId=d['fileId'],driveRevisionId=d['driveRevisionId'],captionedSha256=digest,userApproval='pending-exact-version',youtubeId=None,scheduledAt=None);w['updatedAt']=now;save(R/'shared/publishing/shorts-worklist.json',w)
l=read(P/'production/review-ledger.json');l['driveReview']=d;l['pending']=['최종 사용자 검수 및 전체 청취/발음','승인 후 같은 파일 YouTube 업로드 및 다음19시 예약·실제 Shorts UI 확인']+([] if ready else ['Drive 재생 처리 완료 확인']);save(P/'production/review-ledger.json',l)
print(d['url'],d['playback'])
