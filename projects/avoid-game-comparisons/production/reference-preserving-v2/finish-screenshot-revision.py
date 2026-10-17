"""Register reviewed screenshot masters and keep the previous review version intact."""
from pathlib import Path
import json,datetime,hashlib,argparse
R=Path(__file__).resolve().parents[4];V=Path(__file__).parent;P=V.parent.parent
O=P/'production/local/reference-preserving-v2/screenshots-v1';B=O.parent/'edit';Q=O/'qa'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def rel(p):return p.relative_to(R).as_posix()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
ap=argparse.ArgumentParser();ap.add_argument('stage',choices=['reviewed','collected']);args=ap.parse_args()
now=datetime.datetime.now(datetime.timezone.utc).isoformat();plan=read(V/'edit-plan.json');cp=read(P/'production/latest-checkpoint.json');design=read(P/'planning/chapter-plan.json');m=read(P/'project.json');ledger=read(V/'review-ledger.json')
if args.stage=='reviewed':
 qa=read(Q/'integrity.json');direct=read(Q/'direct-review.json')
 assert direct['status']=='passed' and direct['captionedSha256']==qa['outputs'][1]['sha256']
 assert all(x['fullDecodePassed'] and x['ptsMonotonicAndUniform'] and x['aacSha256']=='0686ba6400fcc2f4898f0de2fae3aea69cb07a91bb211b726c644eddb0a9906d' for x in qa['outputs'])
 qa['pixelReview']='passed-direct-review';write(Q/'integrity.json',qa)
 rev=design['currentRevision']['visualRevision'];rev.update(status='complete-local-review-pending',directReview=rel(Q/'direct-review.json'),integrity=rel(Q/'integrity.json'),audioUnchanged=True,completedAt=now,sourceStillsDirectlyReviewed=True)
 rev['userStyleApproval']={'message':'너무좋다. 설명에 그림 넣기 이거 규칙에 추가해줘~','date':'2026-10-17','scope':'Screenshot-supported explanation style and future rule; not a separate instruction to upload or replace the platform video'}
 for c in plan['cuts']:
  if c['kind']!='explanation':continue
  c.update(visualRevision='screenshots-v1',renderedOverride=rel(O/(c['id']+'.mp4')),implementationKind='independent explanation with inspected screenshots from separate gameplay recordings',screenshotAssets=rel(V/'screenshot-assets.json'))
  c.pop('holdAfterFrames',None);c.pop('holdReason',None)
 for c in rev['cuts']:c['sourceReview']='Decoded source stills and final1080p60/mobile captioned scene directly inspected'
 plan['visualRevision']='screenshots-v1';plan['annotations']['finalMovingOutputReviewed']=True;plan['currentFinalReview']='pending-user-local-review';write(V/'edit-plan.json',plan)
 ledger.setdefault('visualRevisionHistory',[])
 if not any(r.get('revision')=='before-screenshots-v1' for r in ledger['visualRevisionHistory']):ledger['visualRevisionHistory'].append({'revision':'before-screenshots-v1','visualQA':ledger.get('visualQA'),'outputs':read(P/'production/delivery-output.json')['files'],'preservedMasterDirectory':rel(B)})
 ledger['visualQA']={'revision':'screenshots-v1','earlyCaptioned1080And375Preflight':'passed after moving credits clear of two-line captions','completeFinalPixels':'passed-direct-review','changedCutIds':[c['id'] for c in plan['cuts'] if c['kind']=='explanation'],'changedSamplesDirectlyReviewed':direct['samples'],'changedContactSheets':direct['contactSheets'],'changedIndex':rel(Q/'pixel-index.json'),'directReview':rel(Q/'direct-review.json'),'mobile375':'passed-direct-review','movingArrowsAndImageChanges':'passed in sequential decoded frames at reveal starts/middles/completion, every changed caption and scene join','retainedCutFiles':22,'retainedRangeProof':rel(O/'retained-inputs.json'),'unchangedFootageAnnotationEvidence':rel(O/'before-review-ledger.json')}
 ledger['currentIntegrity']=rel(Q/'integrity.json');ledger['audioReuse']={'aacSha256':qa['outputs'][0]['aacSha256'],'exactEncodedStreamIdentical':True,'narrationAndMixAsrRerun':False,'existingAudioReviewAndOpenListeningItemsRetained':True};ledger['currentVisualRevision']='screenshots-v1';ledger['updatedAt']=now
 ledger['delivery'].update(outputs=qa['outputs'],integrityReport=rel(Q/'integrity.json'),currentUserReview='pending complete screenshot-supported local captioned master',visualRevision='screenshots-v1');write(V/'review-ledger.json',ledger)
 m.setdefault('preservedDeliveryManifests',[])
 if not any(r.get('id')=='before-screenshots-v1' for r in m['preservedDeliveryManifests']):m['preservedDeliveryManifests'].append({'id':'before-screenshots-v1','paths':dict(m['paths']),'editing':dict(m['editing']),'finalRender':dict(m['finalRender']),'preserved':True})
 for kind,key in [('clean','videoClean'),('captioned','videoBurnedCaptions')]:m['paths'][key]=rel(O/f'avoid-game-comparisons-screenshots-v1-{kind}.mp4');m['finalRender'][key]=m['paths'][key]
 m['paths']['motionCanvasProject']=rev['motionCanvasProject'];m['finalRender'].update(status='complete-local-user-review-pending',technicalQa=rel(Q/'integrity.json'),allFinalPixelsReviewed=True,visualRevision='screenshots-v1',humanListening='pending',technicalApproved=False)
 # These active manifest summaries were left over from the preserved v1 edit.
 # The complete old object is retained above; update only the active revision.
 e=m['editing'];e.update(timingStatus='exact26080-frames-zero-ratio-error; 115 fixed-caption cues; six screenshot scenes reviewed',explanationStyle='research-black-v1; actual gameplay screenshots linked to progressive labels and arrows',sourceActionBank='projects/avoid-game-comparisons/planning/chapter-plan.json#currentRevision',plannedCandidateActualSeconds=plan['actualFrames']/60,scriptSourceReview='projects/avoid-game-comparisons/planning/chapter-plan.json#currentRevision',measuredEditCandidate={'path':rel(V/'edit-plan.json'),'actualFrames':plan['actualFrames'],'explanationFrames':plan['explanationFrames'],'bodyFrames':plan['bodyFrames'],'finalFrames':plan['totalFrames'],'finalSeconds':plan['totalFrames']/60,'ratioErrorFrames':0,'cuts':26,'narrationAndAacPreserved':True,'allCaptionPixelsReviewed':True})
 e['openingOverview']={'script':m['paths']['script'],'scene':'01','question':'마리오 같은 게임이라고 설명하면 듣는 사람도 같은 장면을 떠올릴까?','orderedSteps':['마리오의 서로 다른 플레이 비교','목표·행동·조건으로 설명 바꾸기','상대의 말로 돌아온 행동 확인'],'firstCaseBridge':'익숙한 이름이 불러오는 횡스크롤 플레이','narrationUnchanged':True}
 e['footageClassification']['explanation']='Diagrams, screenshot-supported explanations, text slides and self-authored demonstrations; screenshot slides remain explanation40%'
 m['currentDelivery'].update(visualRevision='screenshots-v1',builtAt=now);m['status']='awaiting-local-final-review';m['publishReady']=False;write(P/'project.json',m)
 design['currentRevision'].update(status='local-review',nextAction='User reviews screenshot-supported complete local captioned master; no automatic upload or next video');write(P/'planning/chapter-plan.json',design)
 cp['currentRevision'].update(status='local-review',productionComplete=True,visualRevision={'id':rev['id'],'status':rev['status'],'plan':'projects/avoid-game-comparisons/planning/chapter-plan.json#currentRevision.visualRevision','integrity':rev['integrity'],'directReview':rev['directReview']},humanReview='pending current screenshot-supported complete local master',updatedAt=now);write(P/'production/latest-checkpoint.json',cp)
else:
 delivery=read(P/'production/delivery-output.json');qa=read(Q/'integrity.json')
 assert delivery['files'][0]['sha256']==qa['outputs'][1]['sha256']
 assert delivery['files'][1]['sha256']==qa['outputs'][0]['sha256']
 assert delivery['files'][2]['sha256']=='a3d9d21da4ec2c1c1a2112a4b8497a927ccee8c16c0b3b017d9e6a53e8c056c4'
 assert delivery['files'][3]['sha256']=='4e11ff3b012a191b61a9853e03551934080ab77177226467890128d36dabcedc'
 design_git=read(R/'shared/output/avoid-game-comparisons/git-screenshots-design/receipt.json')
 cp['currentRevision'].update(finalOutputs=delivery['files'],humanReview='pending screenshot-supported1080p60 master',productionComplete=True,latestGit={'commit':design_git['commit'],'remoteSha':design_git['remoteSha'],'verified':True,'scope':'Screenshot design unit; final delivery receipt records the subsequent actual commit','foreignIndexPreserved':True},finalGitReceipt='shared/output/avoid-game-comparisons/git-screenshots-delivery/receipt.json');write(P/'production/latest-checkpoint.json',cp)
 ledger['currentOutputs']=delivery['files'];write(V/'review-ledger.json',ledger)
 control=read(R/'shared/publishing/video-production-control.json');assert control['selectedVideo']==P.name
 control['selectedVideoRevision'].update(status='local-review',productionComplete=True,visualRevision='screenshots-v1')
 control['selectedVideoFinalReview'].update(status='pending-user-local-review',version='reference-preserving-v2/screenshots-v1',userReview=None,captionedSha256=delivery['files'][0]['sha256'],path='output/avoid-game-comparisons/avoid-game-comparisons.captioned.mp4',youtubeUploadAuthorized=False)
 control['updatedAt']=now;write(R/'shared/publishing/video-production-control.json',control)
 work=read(R/'shared/publishing/video-worklist.json');row=next(r for r in work['rows'] if r.get('slug')==P.name)
 row.update(productionStatus='수정본1080p60·설명6구간 스크린샷 반영 완료',executionStatus='스크린샷 보강 완성본 사용자 검수 대기',reviewStatus='변경 화면·자막·전환 및 인코딩 검사 완료 / 기존 발음·국소 음량·전체 청취 확인 대기',localMasterAvailable=True)
 row['currentRevision'].update(productionComplete=True,visualRevision='screenshots-v1',localReviewPending=True,humanListeningComplete=False);work['updatedAt']=now;write(R/'shared/publishing/video-worklist.json',work)
 print('Collected hashes verified; selected-video state updated')
