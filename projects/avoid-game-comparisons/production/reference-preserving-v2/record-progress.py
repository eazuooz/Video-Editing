"""Update only the selected revision; retain prior deliveries as evidence."""
from pathlib import Path
import json,datetime,argparse
R=Path(__file__).resolve().parents[4];P=R/'projects/avoid-game-comparisons';V=P/'production/reference-preserving-v2'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
ap=argparse.ArgumentParser();ap.add_argument('stage',choices=['voice-reviewed','rendering','local-review']);args=ap.parse_args();stage=args.stage;now=datetime.datetime.now(datetime.timezone.utc).isoformat()
cp=P/'production/latest-checkpoint.json';checkpoint=read(cp);rev=checkpoint['currentRevision'];rev.update(status=stage,updatedAt=now,ttsComplete=True,fullNarrationAsrComplete=True,fullNarrationTextReviewed=True,scriptComplete=True)
edit=read(V/'edit-plan.json');rev.update(bodyFrames=edit['bodyFrames'],actualFrames=edit['actualFrames'],explanationFrames=edit['explanationFrames'],totalFrames=edit['totalFrames'],editPlan='projects/avoid-game-comparisons/production/reference-preserving-v2/edit-plan.json',fullRenderStarted=stage!='voice-reviewed')
if stage=='local-review':
 delivery=read(P/'production/delivery-output.json');rev.update(productionComplete=True,finalOutputs=delivery['files'],internalQA='projects/avoid-game-comparisons/production/reference-preserving-v2/review-ledger.json',humanReview='pending current complete local captioned master',youtubeUploadAuthorized=False,baselinePreserved=True)
write(cp,checkpoint)
p=P/'planning/chapter-plan.json';plan=read(p);plan['currentRevision'].update(status=stage,ttsComplete=True,editPlan=rev['editPlan'],timingAndAudio={'actualFrames':edit['actualFrames'],'explanationFrames':edit['explanationFrames'],'bodyFrames':edit['bodyFrames'],'ratioErrorFrames':edit['ratioErrorFrames'],'audioReview':'projects/avoid-game-comparisons/production/reference-preserving-v2/review-ledger.json','humanListening':'pending current local review'},nextAction={'voice-reviewed':'Render completed source/timing/diagram plan','rendering':'Finish pair encode and current whole-output QA','local-review':'User reviews completed local captioned1080p60 master; no automatic upload/next episode'}[stage]);write(p,plan)
p=R/'shared/publishing/video-production-control.json';control=read(p);assert control['selectedVideo']==P.name
# Some older summary fields still described the previous selected reward video.
# Archive those explicit fields once before replacing the active pointer.
old=control.get('selectedVideoRevision',{})
if old.get('baselineVideoId') not in [None,'cQE7_ygx_XM']:
 control.setdefault('selectedVideoHistory',[]).append({'archivedAt':now,'reason':'Active pointers moved to selected D18; earlier reward delivery remains unchanged','selectedVideoRevision':old,'selectedVideoFinalReview':control.get('selectedVideoFinalReview')})
control['selectedVideoRevision']={'video':P.name,'id':rev['id'],'status':stage,'design':'projects/avoid-game-comparisons/planning/chapter-plan.json#currentRevision','baselineVideoId':'cQE7_ygx_XM','baselinePreserved':True,'actualShare':.6,'explanationShare':.4,'ratioPolicy':'actual-footage-60-explanation-40-v2','youtubeAuthorized':False,'productionComplete':stage=='local-review'}
control['selectedVideoFinalReview']={'video':P.name,'version':rev['id'],'status':'pending-user-local-review' if stage=='local-review' else 'production-in-progress','driveRequired':False,'reason':'User explicitly waived Drive for this request; preserve earlier platform copies','userReview':None,'youtubeUploadAuthorized':False}
control['updatedAt']=now;write(p,control)
p=R/'shared/publishing/video-worklist.json';work=read(p);row=next(r for r in work['rows'] if r.get('slug')==P.name);row['currentRevision'].update(productionComplete=stage=='local-review',ttsComplete=True,renderStarted=stage!='voice-reviewed',localReviewPending=stage=='local-review');row.update(productionStatus={'voice-reviewed':'수정본 대본·전체 음성 검증 완료 / 렌더 준비','rendering':'수정본1080p60 렌더·자막·전체 검수 중','local-review':'수정본1080p60·네 가지 결과물 완성'}[stage],executionStatus={'voice-reviewed':'선택됨 · 실제60·설명40 프레임 편집 확정','rendering':'선택됨 · 최종 렌더와 검수 진행','local-review':'현재 완성본 사용자 검수 대기'}[stage],localMasterAvailable=stage=='local-review',reviewStatus='전체 음성·화면·한영 자막 내부 검수 완료 / 사용자 최종 청취 대기' if stage=='local-review' else '전체 음성 대조 완료 / 최종 화면·자막·믹스 검수 진행',notes='D18만 진행. 실제60·설명40, 독립1080p 자료. 기존 비공개본 cQE7_ygx_XM 보존. Drive 생략 요청 유지; 새 완성본 검수 전 YouTube 교체·다음 편 시작 없음.');work['updatedAt']=now;write(p,work)
if stage=='local-review':
 row['reviewStatus']='화면·자막 검수 및 전체 음성 전사·인코딩 검사 완료 / 발음·국소 음량과 전체 청취 최종 확인 대기'
 row['currentRevision']['humanListeningComplete']=False
 write(p,work)
print(stage,edit['totalFrames']/60,'seconds; baseline unchanged')
