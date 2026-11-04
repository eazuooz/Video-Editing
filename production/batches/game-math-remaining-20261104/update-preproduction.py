"""Update only this authorized batch using reported, persisted evidence."""
from pathlib import Path
from datetime import datetime, timezone
import json
import subprocess

ROOT=Path(__file__).resolve().parents[3]
BATCH=Path(__file__).parent
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
batch=load(BATCH/'batch.json')
work=load(ROOT/'shared/publishing/video-worklist.json')
rows={r['id']:r for r in work['rows']}
# Completion here means source audit and bilingual draft, never rendered media.
reported_complete={f'M{i}' for i in range(21,34)}
currently_writing=set()
for item in batch['items']:
    project=ROOT/'projects'/item['slug']
    row=rows[item['id']]
    if item['localReviewReady']:continue
    stage='원문 확보 · 순차 대본 준비'
    if item['id'] in currently_writing:stage='원문 검수 · 한영 대본 작성 중'
    if item['id'] in reported_complete:
        assert all((project/p).exists() for p in ('planning/source-audit.json','script/draft-narration.ko.json','script/draft-narration.en.json'))
        stage='원문 검수·한영 초안 완료 · 장면 제작 전'
        item['status']='source-audit-bilingual-draft-ready'
    if item['id']=='M21':stage='Unity 1차 렌더 8종 완료 · 화면 배치 수정·2차 검수 중'
    if item['id']=='M22':stage='게임 예시 연결·한영 통합 대본 완료 · Unity 관절/법선 씬 제작 중'
    if item['id']=='M23':stage='게임 예시 연결·한영 통합 대본 완료 · 파이프라인 씬 준비'
    if item['id'] in {'M24','M25','M26'}:stage='한영 초안·Unity 물리 계산 모듈 준비 · 실제 게임 검수 중'
    if item['id'] in {f'M{i}' for i in range(27,34)}:stage='원문·한영 초안 완료 · 개념에 맞는 실제 게임 확보·검수 중'
    row['productionStatus']=stage
    row['productionComplete']=False
    row['reviewStatus']='완성 영상 대기 · 실제 음성/합성 검수 전'
    row['notes']='2026-11-04 승인된 M21–M33 로컬 제작 범위. '+stage+'. 업로드·예약 미승인.'
    item['evidence']={'sourceAudit':str(project/'planning/source-audit.json') if (project/'planning/source-audit.json').exists() else None,
                      'footageAudit':str(project/'planning/footage-audit.json') if (project/'planning/footage-audit.json').exists() else None}
batch['updatedAt']=datetime.now(timezone.utc).isoformat()
save(BATCH/'batch.json',batch);save(ROOT/'shared/publishing/video-worklist.json',work)
checkpoint=load(BATCH/'checkpoint.json')
checkpoint['updatedAt']=batch['updatedAt']
checkpoint['currentWork']=['Complete source audit and bilingual draft: '+', '.join(sorted(reported_complete)),
                         'M21 eight GPU image preflights completed, including actual baked/mixed lighting; overlap and color fixes are in the second finite preview queue',
                         'M22–M23 integrated narration ready; M22 rig module and M24–M33 independent footage in progress']
checkpoint['localReviewReady']=[]
preflight=ROOT/'projects/game-math-shading-lights/production/unity-staging/local-preflight-v2/progress.json'
if preflight.exists():
    actual=load(preflight)
    checkpoint['finitePreflightJob']={**actual,'progress':preflight.relative_to(ROOT).as_posix(),'scope':'12 M21 image preflights only; no TTS or next episode','automationCreated':False}
    checkpoint['runningCostlyJobs']=[actual.get('current')] if actual['status']=='running-preflight' else []
    checkpoint['resourceGate']={'status':actual['status'],'reason':actual.get('reason'),'gameProcessNotObservedAtLatestCheck':True}
checkpoint['lastPlanningCommit']='01f08cc92f3ea5ba6e2234e4c99377edbf9021c6'
checkpoint['lastProductionCommit']='7dbbf3a9796b0b59595b1050084ae57330af8a13'
save(BATCH/'checkpoint.json',checkpoint)
subprocess.run(['python','-X','utf8',str(BATCH/'progress.py')],cwd=ROOT,check=True)
