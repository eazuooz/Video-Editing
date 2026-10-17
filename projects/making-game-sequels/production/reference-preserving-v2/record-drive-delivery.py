"""Link the actual Drive revision to the collected master and current worklist."""
from pathlib import Path
import json,datetime
R=Path(__file__).resolve().parents[4];P=R/'projects/making-game-sequels'
def read(p): return json.loads(p.read_text(encoding='utf8'))
def write(p,x): p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
control=read(R/'shared/publishing/video-production-control.json');assert control['selectedVideo']==P.name
receiptPath='projects/making-game-sequels/publishing/reference-preserving-v2/drive-final-review.json';d=read(R/receiptPath);out=read(P/'production/delivery-output.json')
assert d['sourceSha256']==out['files'][0]['sha256'] and d['bytes']==out['files'][0]['bytes'] and d['playback']['status']=='passed-reopened-and-played'
assert d['humanReview'].startswith('pending') and not d['youtubeUploadAuthorized']
now=datetime.datetime.now(datetime.timezone.utc).isoformat();p=P/'project.json';m=read(p)
m['currentDelivery'].update(driveUploaded=True,driveId=d['fileId'],driveUrl=d['url'],driveRevisionId=d['driveRevisionId'],masterSha256=d['sourceSha256'],receipt=receiptPath,userReview=d['humanReview'])
m['currentRevision'].update(status='awaiting-user-drive-final-review',deliveryStatus='complete-four-outputs-and-drive',productionComplete=True)
m['finalProduction'].update(collected=True,driveUploaded=True,driveReceipt=receiptPath,privateUploaded=False,humanWholeListening='pending',humanPronunciation='pending',publishReady=False)
m['status']='awaiting-user-drive-final-review';write(p,m)
p=P/'production/review-ledger.json';l=read(p);l.update(updatedAt=now,driveFinalReview={'upload':'complete','playback':'passed1080p','receipt':receiptPath,'driveId':d['fileId'],'driveRevisionId':d['driveRevisionId'],'sourceSha256':d['sourceSha256'],'humanReview':'pending'})
l['audioQA']['finalAmbiguityContexts']='production/local/reference-preserving-v2/edit/final-contexts-asr.json';l['audioQA']['humanListeningFocus']=[{'seconds':272.9,'reason':'Source ASR reads 기대에서; final ASR reads 기대해서. Full sentence retained; human pronunciation check remains pending.'}];write(p,l)
p=P/'production/latest-checkpoint.json';c=read(p);c.update(updatedAt=now,stage='awaiting-user-drive-final-review',nextAction='Wait for human review of this exact Drive version; no D19 YouTube upload or next video without user scope',newRevisionRendered=True,newRevisionHumanReviewed=False,automaticNextVideo=False,currentDriveDelivery=receiptPath,currentFourOutputs='projects/making-game-sequels/production/delivery-output.json')
if 'latestVerifiedUnitCommit' in c: c['lastVerifiedCommitBeforeDelivery']=c.pop('latestVerifiedUnitCommit')
c['finalGitReceipt']='shared/output/making-game-sequels/git-final-review/receipt.json';c['masterRenderExecution']['status']='complete; all source cuts, new masters and encoded mix checked';write(p,c)
p=R/'shared/publishing/video-worklist.json';w=read(p);row=next(x for x in w['rows'] if x['slug']==P.name)
row.update(title=m['titles']['ko'],productionComplete=True,productionStatus='개정본 제작·4파일·Drive 검수본 완료',reviewStatus='화면·자막·전체 음성 대조·기술 검사 완료 / 사용자 최종 청취·발음 검수 대기',humanApproval='현재 Drive 버전 사용자 검수 필요',platformStatus='기존 YouTube 비공개본 보존 / 개정본 Drive 검수 대기',executionStatus='완성본 전달 완료 · 사용자 검수 대기',localMasterAvailable=True,notes='1080p60·6분55초·실제60:설명40. 기존2-IyuwcP_vQ 보존. 이번 개정본은 Drive에서 최종 검수 후 YouTube 업로드. 다음 편 자동 착수 없음.')
row['currentRevision'].update(productionComplete=True,technicalQaComplete=True,humanReview='pending',driveUrl=d['url'],driveId=d['fileId'],driveRevisionId=d['driveRevisionId'],masterSha256=d['sourceSha256'],youtubeUploadAuthorized=False)
for e in [receiptPath,'projects/making-game-sequels/production/review-ledger.json','projects/making-game-sequels/production/delivery-output.json']:
 if e not in row['evidence']:row['evidence'].append(e)
w['updatedAt']=now;write(p,w)
control.update(updatedAt=now,runningWorkBoundary='making-game-sequels completed through Drive final review; wait for human review. D18 private upload complete; baselines preserved; no automatic next video.')
control['selectedDelivery']={'slug':P.name,'stage':'awaiting-user-drive-final-review','receipt':receiptPath,'driveUrl':d['url'],'sourceSha256':d['sourceSha256'],'userReview':'pending','youtubeUploadAuthorized':False};write(R/'shared/publishing/video-production-control.json',control)
print(d['url'])
