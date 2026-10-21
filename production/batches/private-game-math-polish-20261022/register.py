"""Record the explicit finite overnight exception without changing other work."""
import json, hashlib
from pathlib import Path
from datetime import datetime, timezone
R=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
now=datetime.now(timezone.utc).isoformat()
evidence='좋아 잘됐어~ 나 자는동안 나머지 목록도 다 진행해주고 검수대기로 만들어줘~'
w=read(R/'shared/publishing/video-worklist.json');rows=[x for x in w['rows'] if x['id'].startswith('M') and 5<=int(x['id'][1:])<=20]
auth=dict(id='private-math-overnight-polish-20261022',recordedAt=now,userEvidence=evidence,ids=[x['id'] for x in rows],slugs=[x['slug'] for x in rows],status='active',fullProductionAuthorized=True,newTtsAuthorized=False,scriptRewriteAuthorized=False,uploadAuthorized=False,deleteAuthorized=False,automaticAdvanceWithinThisList=True,advanceBeyondThisList=False,stopAt='all sixteen internally checked and ready for local human review',automationId='16')
z=read(R/'shared/publishing/video-production-control.json');z['scopedBatchAuthorizations']=z.get('scopedBatchAuthorizations',{});z['scopedBatchAuthorizations'][auth['id']]=auth;z['updatedAt']=now
master=read(R/'projects/game-math-euler-axis-angle/production/private-polish-v1/outputs.json')['localReview']['captionedMasterSha256']
approved=dict(status='accepted',recordedAt=now,userEvidence=evidence,captionedMasterSha256=master,wholeListeningExplicitlyConfirmed=False,uploadAuthorized=False)
a=z['scopedProductionAuthorizations']['game-math-euler-axis-angle'];a['humanFinalReview']='accepted';a['actualHumanReview']=approved;a['status']='accepted-local-visual-polish';a['localReview']['humanFinalReview']='accepted'
save(R/'shared/publishing/video-production-control.json',z)
first=next(x for x in w['rows'] if x['id']=='M04');first['privatePolish'].update(status='시각 보강본 사용자 검수 완료',humanReview='사용자 승인 완료',actualHumanReview=approved);first['reviewStatus']='사용자 승인 완료';first['humanApproval']=evidence
w['privateMathPolish'].update(updatedAt=now,selected='M05',batchAuthorization=auth,automaticNextVideo=True,automaticNextVideoScope='M05–M20 only; no uploads or further videos')
entries=[]
for row in rows:
 p=R/'projects'/row['slug'];t=read(p/'production/timeline.json')
 entry=dict(id=row['id'],slug=row['slug'],videoId=row['videoId'],title=row['title'],seconds=t['seconds'],scenes=len(t['scenes']),originalTimelineSha256=sha(p/'production/timeline.json'),stage='restore-inputs',status='queued-authorized',humanReview='pending',newTts=False,platformMutation=False)
 row['privatePolish'].update(status='야간 보강 승인 · 원본 복구 대기',humanReview='수정본 검수 전',batchAuthorization=auth['id'])
 entries.append(entry)
w['updatedAt']=now;save(R/'shared/publishing/video-worklist.json',w)
save(B/'queue.json',dict(schemaVersion=1,authorization=auth,createdAt=now,entries=entries))
save(B/'checkpoint.json',dict(updatedAt=now,stage='input-restoration',active='M05',ready=[],blocked=[],nextAction='Recover existing uploaded audio through Studio download; restore original code/FHD footage; preserve lesson, speech and timeline. Complete each internally and advance only within approved sixteen.',automationId='16'))
save(B/'authorization.json',auth)
for rel in ['project.json','production/checkpoint.json','production/review-ledger.json','production/private-polish-v1/outputs.json','planning/production-plan.json']:
 p=R/'projects/game-math-euler-axis-angle'/rel;d=read(p)
 if rel=='project.json':d['activeVisualPolish']['humanFinalReview']=approved
 elif rel=='production/checkpoint.json':d['finalUserReview']='accepted';d['actualHumanReview']=approved
 elif rel=='production/review-ledger.json':d['activeVisualPolishReview']['actualHumanReview']=approved;d['activeVisualPolishReview']['localReview']['humanFinalReview']='accepted'
 elif rel=='production/private-polish-v1/outputs.json':d['localReview']['humanFinalReview']='accepted';d['localReview']['actualHumanReview']=approved
 else:d['baselineVisualPolish']['actualHumanReview']=approved
 save(p,d)
p=R/'docs/VIDEO_WORKFLOW.md';s=p.read_text(encoding='utf8');prefix='2026-10-22 사용자 선택';line=next(x for x in s.splitlines() if x.startswith(prefix))
add=' 이후 같은 날 사용자 야간 요청으로 **기존 비공개 게임수학 본편 M05–M20의 남은16편에 한정한 일괄 보강 예외**를 승인했다. 이 목록은 개별 사용자 검수 전에도 다음 편으로 진행하여 각 편을 내부 검사 완료·로컬 검수 대기로 모은다. M04는 전달한 해시의 사용자 검수 완료로 기록한다. 기존 대본·녹음·순서·예시·길이를 보존하며, 새 TTS·업로드·삭제·공개·예약이나 목록 밖 자동 진행은 허용하지 않는다. 이번 전용 자동 이어가기는16편 완료 시 중지하며 다른 작업/자동화는 바꾸지 않는다.'
if add not in line:p.write_text(s.replace(line,line+add,1),encoding='utf8')
print('Registered sixteen-video exception and exact-master M04 acceptance.')
