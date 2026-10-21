"""Record actual selected delivery; no platform action or other worklist mutation."""
from pathlib import Path
import importlib.util,datetime,copy
H=Path(__file__).parent
sp=importlib.util.spec_from_file_location('v8_state_common',H/'common.py');c=importlib.util.module_from_spec(sp);sp.loader.exec_module(c)
def preserve(d,key,value,identity):
 if value and not any((x.get(identity)==value.get(identity) if value.get(identity) else x==value) for x in d.setdefault(key,[])):d[key].append(copy.deepcopy(value))
def main():
 c.authorized();delivery=c.read(H/'local-delivery.json');qa=c.read(c.O/'qa/quality-review.json');timeline=c.read(H/'timeline.json');now=datetime.datetime.now(datetime.timezone.utc).isoformat()
 assert qa['technicalStatus']=='passed' and qa['masterSha256']==delivery['masterSha256']
 assert delivery['humanFinalReview']=='pending' and not delivery['platformMutation']
 files={x['kind']:x for x in delivery['files']}
 assert delivery['masterSha256']==files['captioned']['sha256']
 for x in files.values():assert c.sha(c.R/x['file'])==x['sha256']
 review=dict(policyId='local-final-review-before-youtube-v1',provider='local-filesystem',directory=delivery['directory'],captioned=files['captioned']['file'],index=delivery['index'],version='orientation-matrix-v8',sha256=delivery['masterSha256'],status='ready-for-local-user-review',filesCollectedAndHashVerified=True,linksReady=True,humanReview='pending',userReviewMessage=None,reviewedAt=None,deliveredAt=None,driveUploadRequired=False)
 active=dict(revision='orientation-matrix-v8',stage='complete-local-final-review-pending',authorization=c.rel(H/'authorization.json'),approvedScriptSha256=c.sha(c.S/'narration.ko.json'),deliveryProject='game-math-orientation-matrix',durationSeconds=timeline['duration'],frames=timeline['totalFrames'],masterSha256=delivery['masterSha256'],localReview=review,qualityReview=c.rel(c.O/'qa/quality-review.json'),humanFinalReview='pending',platformMutation=False,completedAt=now)
 pfile=c.P/'project.json';p=c.read(pfile)
 preserve(p,'completedRevisionHistory',p.get('finalRender'),'captionedSha256')
 p.update(status='complete-v8-local-final-review-pending',revision='orientation-matrix-v8',publishReady=False,selectedDeliveryProject='game-math-orientation-matrix',selectedProductionPart=None,updatedAt=now,activeProductionV8=active)
 p['activeScriptWork'].update(status='produced-to-local-final-review',newTts='complete-current-76-paragraph-takes',newVideo='complete-current-FHD60-clean-and-captioned',runtimeSeconds=timeline['duration'],actualHumanWholeListening='pending')
 p['titles'].update(ko=delivery['title'],en='How Does a Game Remember an Object’s Tilt? — Orientation and Rotation Matrices')
 p['finalRender']=dict(active,width=1920,height=1080,fps=60,captionedSha256=files['captioned']['sha256'],cleanSha256=files['clean']['sha256'],knownIssues=[],openItems=['사용자 최종 검수·전체 청취 대기'])
 p['paths'].update(videoClean=files['clean']['file'],videoBurnedCaptions=files['captioned']['file'],captionsKo=files['ko']['file'],captionsEn=files['en']['file'],timeline=c.rel(H/'timeline.json'))
 p['delivery'].update(directory=delivery['directory'],review=review);c.save(pfile,p)
 cpfile=c.P/'production/checkpoint.json';cp=c.read(cpfile)
 preserve(cp,'previousMasters',cp.get('currentMaster'),'sha256')
 cp.update(updatedAt=now,revision='orientation-matrix-v8',revisionUnderWork=None,stage='complete-local-final-review-pending',runningJob=None,blockers=[],nextAction='Wait for actual user review of this exact full captioned master. No upload/next video.',activeProductionV8=active,activeProduction=active,currentMaster=dict(file=files['captioned']['file'],sha256=files['captioned']['sha256'],revision='orientation-matrix-v8'),localReview=review,delivery=delivery,latestUserRequest='대본 좋은거같아 제작해줘~',automaticNextVideo=False)
 c.save(cpfile,cp);c.save(H/'production-checkpoint.json',dict(active,nextAction=cp['nextAction'],runningJobs=[],humanReview='pending',fullVideoExists=True))
 ledgerfile=c.P/'production/review-ledger.json';ledger=c.read(ledgerfile)
 preserve(ledger,'previousOutputs',ledger.get('currentOutput'),'sha256')
 ledger.update(revision='orientation-matrix-v8',updatedAt=now,currentOutput=dict(file=files['captioned']['file'],sha256=files['captioned']['sha256'],revision='orientation-matrix-v8'),currentLocalReview=review,reviewProvider='local-filesystem',activeProduction=active,humanWholeListening=dict(status='pending',actualHumanReview=None,technicalReviewNotHumanApproval=True))
 ledger['checks']=[x for x in ledger['checks'] if x.get('id')!='v8CurrentMaster'];ledger['checks'].append(dict(id='v8CurrentMaster',file=c.rel(c.O/'qa/quality-review.json'),sha256=c.sha(c.O/'qa/quality-review.json'),status='passed-internal-technical-review',humanReview='pending'));c.save(ledgerfile,ledger)
 wf=c.R/'shared/publishing/video-worklist.json';w=c.read(wf);row=next(x for x in w['rows']if x['id']=='M04')
 row.update(title='자세와 회전행렬 — 3차원 회전',productionComplete=True,currentRevisionProductionComplete=True,productionStatus='V8 완료 · 자세와 회전행렬 8.1–8.2.5 · FHD60',reviewStatus='V8 기술 검수 완료 · 사용자 최종 영상 검수 대기',humanApproval='V8 대본 승인 · 완성 영상 검수 대기',platformStatus='V8 로컬 완성 · 새 업로드 없음 · 기존 Drive·비공개 YouTube 보존',latestRulesPassed=True,executionStatus='V8 로컬 검수 대기 · 자동 진행 안 함',localMasterAvailable=True,currentRevision='orientation-matrix-v8',localReview=review,notes='승인된 8.1–8.2.5 전체 학습 흐름으로 V8 제작 완료. 실제 게임/모형 동시 설명, 행렬 계산, 새 문단 음성. 최종 영상 사용자 검수 대기; 업로드·다음 편 없음.')
 for f in [c.rel(H/'local-delivery.json'),c.rel(c.O/'qa/quality-review.json')]:
  if f not in row['evidence']:row['evidence'].append(f)
 w['updatedAt']=now;c.save(wf,w)
 docs=c.R/'docs/VIDEO_WORKLIST.md';lines=docs.read_text(encoding='utf8').splitlines()
 for i,line in enumerate(lines):
  if line.startswith('| 5 | 게임수학 | M04 '):lines[i]='| 5 | 게임수학 | M04 [자세와 회전행렬](../output/game-math-orientation-matrix/index.html) | V8 완료 · 로컬 검수 대기 | ☐ 최종 영상 사용자 검수 대기 |'
  elif line.startswith('| M04 |'):lines[i]='| M04 | [자세와 회전행렬](../output/game-math-orientation-matrix/index.html) | ☑ V8 완료 · 8.1–8.2.5 · 1080p60 | ☐ 기술 검수 완료 · 사용자 최종 검수 대기 | 새 업로드 없음 · 기존 Drive·비공개 YouTube 보존 |'
  elif line.startswith('| M04 3D 회전'):lines[i]='| M04 자세와 회전행렬 | '+row['notes']+' |'
 docs.write_text('\n'.join(lines)+'\n',encoding='utf8')
 controlfile=c.R/'shared/publishing/video-production-control.json';control=c.read(controlfile);scope=control['scopedProductionAuthorizations'][c.P.name]
 assert scope['revision']=='orientation-matrix-v8'
 scope.update(status='complete-local-final-review-pending',fullProductionAuthorized=False,newTtsAuthorized=False,renderAuthorized=False,humanFinalReview='pending',actualHumanReview=None,captionedMasterSha256=delivery['masterSha256'],localReviewDirectory=str(c.R/delivery['directory']),completedAt=now)
 c.save(controlfile,control);print('Recorded current V8 only; exact-master human review pending. Existing platforms preserved.')
if __name__=='__main__':main()
