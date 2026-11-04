"""Update only this authorized batch using reported, persisted evidence."""
from pathlib import Path
from datetime import datetime, timezone
import json
import subprocess
import re

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
    if item['id']=='M21':
        audio=project/'production/local/audio-v1';worker=load(audio/'finite-worker.json') if (audio/'finite-worker.json').exists() else {}
        log=(audio/'finite-synthesis.stdout.log').read_text(encoding='utf-8',errors='replace') if (audio/'finite-synthesis.stdout.log').exists() else ''
        finished=set(re.findall(r'^Rendered (\d{3})-',log,re.M))
        stage=f'게임·대본 확정 · Qwen 음성 {len(finished)}/79구간 생성 · 화면 검수 중'
        if worker.get('status')=='voice-generated-review-pending':
            stage='79구간 음성 생성 완료 · 실제 발화·자막 시각 검수 중'
            word=load(audio/'finite-word-review.json') if (audio/'finite-word-review.json').exists() else {}
            if word.get('status')=='waiting-for-current-voice':stage='79구간 음성 완료 · 다른 GPU 작업 종료 대기 후 발화 시각 분석'
            if word.get('status')=='transcribing-word-timestamps':stage='79구간 음성 완료 · 단어별 발화 시각 분석 중'
            if word.get('status')=='failed-or-blocked':stage='79구간 음성 완료 · 발화 시각 분석 오류 복구 중'
            if word.get('status')=='word-evidence-ready-content-review-pending':stage='음성·한영 자막 준비 · 첫 본편 장면 1080p60 인코딩 완료·합성 검사 중'
            capture=project/'production/local/render-v2/progress.json'
            if capture.exists():
                current=load(capture);stage=f'음성·자막 준비 · 설명 장면 {len(current.get("completed",[]))}/78 렌더 · 전체 합성/검수 전'
                if current['status']=='body-captures-complete-compositing-and-QA-pending':stage='78개 설명 장면 렌더 완료 · 본편 합성/검수 중'
                if current['status']=='failed-or-blocked':stage=f'설명 장면 {len(current.get("completed",[]))}/78 · 작업 오류 확인/복구 중'
            composite=project/'production/local/render-v2/composite/progress.json'
            if composite.exists():
                c=load(composite)
                if c['status']=='compositing':stage=f'본편 합성 {c["completedCuts"]}/{c["totalCuts"]}컷 · 전체 검수 전'
                if c['status']=='encoded-internal-QA-pending':stage='1080p60·한영 자막 4파일 생성 · 최종 내부 검수 중'
    if item['id']=='M22':stage='게임 연결·통합 대본·관절/법선 계산 모듈 완료 · Unity 실행 검수 전'
    if item['id']=='M23':stage='게임 연결·통합 대본·파이프라인 계산 모듈 완료 · Unity 실행 검수 전'
    if item['id'] in {'M22','M23'}:
        preview=project/'production/unity-staging/local-preflight-v1/progress.json'
        if preview.exists():
            run=load(preview);done=len(run.get('completed',[]))
            if run['status']=='waiting':stage=f'설명 씬 준비 · GPU 순차 작업 대기 · 실행 샘플 {done}개 완료'
            elif run['status']=='running-preflight':stage=f'Unity 설명 씬 실행 검사 중 · 샘플 {done}개 완료'
            elif run['status']=='images-ready-for-internal-visual-QA':stage=f'Unity 실행 샘플 {done}개 생성 · 화면 검수 중'
            else:stage=f'Unity 실행 검사 확인 필요 · 샘플 {done}개 완료'
    if item['id'] in {'M24','M25','M26'}:stage='게임 3역할 연결·통합 대본·물리 계산 모듈 준비 · Unity 실행 검수 전'
    shotNames={'M24':'derivative-shots.json','M25':'integration-shots.json','M26':'circular-shots.json'}
    if item['id'] in shotNames:
        shots=project/'production/unity-staging'/shotNames[item['id']]
        if shots.exists():
            n=len(load(shots)['shots']);stage=f'원문 순서 {n}개 설명 장면·계산 단계 작성 · Unity 실행 검사 대기'
            preview=project/'production/unity-staging/local-preflight-v1/progress.json'
            if preview.exists():
                run=load(preview);done=len(run.get('completed',[]));stage+=f' · 실행 샘플 {done}개 생성'
                if run['status']=='failed-or-blocked':stage+=' · 실행 오류 확인 중'
    if item['id'] in {f'M{i}' for i in range(27,31)}:stage='원문·게임 연결·한영 통합 대본 완료 · 힘/충돌 씬 제작 전'
    if item['id'] in {'M27','M28'}:stage='통합 대본·힘/마찰/감쇠 계산 검사 완료 · 설명 씬 구현 중'
    if item['id'] in {'M29','M30'}:stage='통합 대본·충돌/관성 수치 검사 완료 · 설명 씬 구현 중'
    if item['id'] in {f'M{i}' for i in range(31,34)}:stage='통합 대본·곡선 계산 검사 완료 · 애니메이션 실행 검수 전'
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
                         'M21 narration complete (79 paragraphs, 1917.9200833333307 seconds); original PCM preserved. Full ASR aligned, 715 KO / 606 EN cues, zero alignment flags. Final media and integrated QA pending.',
                         'All 13 integrated bilingual scripts and gameplay bindings exist; M22–M33 staged math/renderer modules compile; M29/M30 numeric model passes 2261 invariants, 10 visual modes implemented but remaining source-beat coverage/runtime QA are pending',
                         'M21 seven annotation layouts directly inspected at 1080p / 375px; M22/M23 isolated capture transport and finite preflight runner prepared, actual runtime QA pending']
checkpoint['localReviewReady']=[]
preflights=list((ROOT/'projects/game-math-shading-lights/production/unity-staging').glob('local-preflight-v*/progress.json'))
preflight=max(preflights,key=lambda p:p.stat().st_mtime) if preflights else ROOT/'missing-preflight'
if preflight.exists():
    actual=load(preflight)
    checkpoint['finitePreflightJob']={**actual,'progress':preflight.relative_to(ROOT).as_posix(),'scope':'M21 targeted image preflights only','automationCreated':False}
    checkpoint['runningCostlyJobs']=[actual.get('current')] if actual['status']=='running-preflight' else []
    checkpoint['resourceGate']={'status':actual['status'],'reason':actual.get('reason')}
voice=ROOT/'projects/game-math-shading-lights/production/local/audio-v1/finite-worker.json'
if voice.exists():
    actual=load(voice);checkpoint['voiceWorker']=actual
    checkpoint['runningCostlyJobs']=['M21 approved voice'] if actual['status']=='synthesizing' else []
    checkpoint['resourceGate']={'status':actual['status'],'lastCheckedAt':actual.get('checkedAt')}
word=ROOT/'projects/game-math-shading-lights/production/local/audio-v1/finite-word-review.json'
if word.exists():
    actual=load(word);checkpoint['wordReviewWorker']=actual
    checkpoint['runningCostlyJobs']=['M21 word timestamps'] if actual['status']=='transcribing-word-timestamps' else []
    checkpoint['resourceGate']={'status':actual['status'],'reason':actual.get('reason'),'lastCheckedAt':actual.get('checkedAt')}
checkpoint['nextAction']='Finish the measured M21 captures and finite compositor, then inspect complete media. M22–M26 scoped Unity runtime samples share the GPU lease. M27–M33 complete source-beat visuals remain in progress. No platform mutation.'
if preflight.exists() and load(preflight)['status'] in {'running-preflight','waiting-for-idle-resources'}:
    actual=load(preflight)
    checkpoint['runningCostlyJobs']=[actual.get('current','M21 font regression')] if actual['status']=='running-preflight' else []
    checkpoint['resourceGate']={'status':actual['status'],'reason':actual.get('reason'),'lastCheckedAt':actual.get('checkedAt')}
    checkpoint['nextAction']='Inspect single-sample capture regression and final-caption/encoder sample, then capture the measured M21 timeline. Font-only experiments did not fix lost 3D/UI regions. Original narration unchanged; remaining authorized lectures continue after scoped resource checks.'
caption_sample=ROOT/'projects/game-math-shading-lights/production/local/encoder-sample-v1/caption-sample-progress.json'
if caption_sample.exists():
    checkpoint['encoderCaptionSample']=load(caption_sample)
    if checkpoint['encoderCaptionSample']['status']=='waiting-for-scoped-resources':
        checkpoint['resourceGate']=checkpoint['encoderCaptionSample'];checkpoint['runningCostlyJobs']=[]
capture=ROOT/'projects/game-math-shading-lights/production/local/render-v2/progress.json'
if capture.exists():
    checkpoint['productionCapture']=load(capture)
    checkpoint['runningCostlyJobs']=[checkpoint['productionCapture'].get('current')] if checkpoint['productionCapture']['status']=='capturing' else []
    checkpoint['resourceGate']={'status':checkpoint['productionCapture']['status'],'reason':checkpoint['productionCapture'].get('reason')}
checkpoint['modulePreflights']={}
for slug in ['game-math-skinning-normal-map','game-math-pipeline-shaders','game-math-velocity-derivatives','game-math-acceleration-integration','game-math-circular-motion']:
    path=ROOT/'projects'/slug/'production/unity-staging/local-preflight-v1/progress.json'
    if path.exists():checkpoint['modulePreflights'][slug]=load(path)
compositor=ROOT/'projects/game-math-shading-lights/production/local/render-v2/composite/worker.json'
if compositor.exists():checkpoint['compositorWorker']=load(compositor)
checkpoint['lastPlanningCommit']='01f08cc92f3ea5ba6e2234e4c99377edbf9021c6'
checkpoint['lastProductionCommit']='a8c50f3f0af82747af340b53fb610ac79575bcf0'
save(BATCH/'checkpoint.json',checkpoint)
subprocess.run(['python','-X','utf8',str(BATCH/'progress.py')],cwd=ROOT,check=True)
