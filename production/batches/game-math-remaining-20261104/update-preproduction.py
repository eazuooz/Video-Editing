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
    if item['id']=='M21':stage='대본·게임 연결 확정 · Qwen 음성 생성·발화 큐 준비'
    if item['id']=='M22':stage='게임 연결·통합 대본·관절/법선 계산 모듈 완료 · Unity 실행 검수 전'
    if item['id']=='M23':stage='게임 연결·통합 대본·파이프라인 계산 모듈 완료 · Unity 실행 검수 전'
    if item['id'] in {'M24','M25','M26'}:stage='게임 3역할 연결·통합 대본·물리 계산 모듈 준비 · Unity 실행 검수 전'
    if item['id'] in {f'M{i}' for i in range(27,31)}:stage='원문·게임 연결·한영 통합 대본 완료 · 힘/충돌 씬 제작 전'
    if item['id'] in {'M27','M28'}:stage='통합 대본·힘/마찰/감쇠 계산 검사 완료 · 설명 씬 구현 중'
    if item['id'] in {f'M{i}' for i in range(31,34)}:stage='원문·게임 연결·한영 통합 대본 완료 · 곡선 애니메이션 제작 중'
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
                         'M21 v4 grid/vertex/mixed directly inspected; approved voice production and cue preparation',
                         'All 13 integrated bilingual scripts and gameplay bindings exist; M22/M23/M24–26 CPU modules ready; M27/M28 math invariants and staged renderer compile pass; M29–33 visual implementation incomplete']
checkpoint['localReviewReady']=[]
preflight=ROOT/'projects/game-math-shading-lights/production/unity-staging/local-preflight-v4/progress.json'
if preflight.exists():
    actual=load(preflight)
    checkpoint['finitePreflightJob']={**actual,'progress':preflight.relative_to(ROOT).as_posix(),'scope':'3 M21 targeted image preflights only','automationCreated':False}
    checkpoint['runningCostlyJobs']=[actual.get('current')] if actual['status']=='running-preflight' else []
    checkpoint['resourceGate']={'status':actual['status'],'reason':actual.get('reason')}
voice=ROOT/'projects/game-math-shading-lights/production/local/audio-v1/finite-worker.json'
if voice.exists():
    actual=load(voice);checkpoint['voiceWorker']=actual
    checkpoint['runningCostlyJobs']=['M21 approved voice'] if actual['status']=='synthesizing' else []
    checkpoint['resourceGate']={'status':actual['status'],'lastCheckedAt':actual.get('checkedAt')}
checkpoint['nextAction']='Complete M21 voice and actual word alignment, then final visual/audio rendering and QA; continue exact M21–M33 scope.'
checkpoint['lastPlanningCommit']='01f08cc92f3ea5ba6e2234e4c99377edbf9021c6'
checkpoint['lastProductionCommit']='11edef44f0e9424fba839254b9e23f66bb0ce9c9'
save(BATCH/'checkpoint.json',checkpoint)
subprocess.run(['python','-X','utf8',str(BATCH/'progress.py')],cwd=ROOT,check=True)
