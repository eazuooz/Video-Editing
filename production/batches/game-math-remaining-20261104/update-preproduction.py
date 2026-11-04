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
def latest_revision(base,pattern,filename):
    candidates=list(base.glob(pattern+'/'+filename))
    return max(candidates,key=lambda p:int(re.search(r'-v(\d+)$',p.parent.name)[1])) if candidates else base/'missing'/filename

def latest_preview(project):return latest_revision(project/'production/unity-staging','local-preflight-v*','progress.json')
def latest_render(project):return latest_revision(project/'production/local','render-v*','queue.json').parent
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
            capture=latest_render(project)/'progress.json'
            if capture.exists():
                current=load(capture);stage=f'음성·자막 준비 · 설명 장면 {len(current.get("completed",[]))}/78 렌더 · 전체 합성/검수 전'
                if current['status']=='body-captures-complete-compositing-and-QA-pending':stage='78개 설명 장면 렌더 완료 · 본편 합성/검수 중'
                if current['status']=='failed-or-blocked':stage=f'설명 장면 {len(current.get("completed",[]))}/78 · 작업 오류 확인/복구 중'
            composite=latest_render(project)/'composite/progress.json'
            if composite.exists():
                c=load(composite)
                if c['status']=='compositing':stage=f'본편 합성 {c["completedCuts"]}/{c["totalCuts"]}컷 · 전체 검수 전'
                if c['status']=='encoded-internal-QA-pending':stage='1080p60·한영 자막 4파일 생성 · 최종 내부 검수 중'
    if item['id']=='M22':stage='게임 연결·통합 대본·관절/법선 계산 모듈 완료 · Unity 실행 검수 전'
    if item['id']=='M23':stage='게임 연결·통합 대본·파이프라인 계산 모듈 완료 · Unity 실행 검수 전'
    if item['id'] in {'M22','M23'}:
        preview=latest_preview(project)
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
            preview=latest_preview(project)
            if preview.exists():
                run=load(preview);done=len(run.get('completed',[]));stage+=f' · 실행 샘플 {done}개 생성'
                if run['status']=='failed-or-blocked':stage+=' · 실행 오류 확인 중'
    if item['id'] in {f'M{i}' for i in range(27,31)}:stage='원문·게임 연결·한영 통합 대본 완료 · 힘/충돌 씬 제작 전'
    if item['id'] in {'M27','M28'}:stage='통합 대본·힘/마찰/감쇠 계산 검사 완료 · 설명 씬 구현 중'
    if item['id']=='M27':
        shots=project/'production/unity-staging/force-shots.json'
        if shots.exists():stage=f'원문 순서 {len(load(shots)["shots"])}개 힘·마찰 설명 씬 작성 · 실행 검수 중'
        preview=latest_preview(project)
        if preview.exists():
            run=load(preview);stage+=f' · 실행 샘플 {len(run.get("completed",[]))}개 생성'
            if run['status']=='failed-or-blocked':stage+=' · 실행 오류 복구 중'
    if item['id']=='M28':
        shots=project/'production/unity-staging/spring-shots.json'
        if shots.exists():stage=f'원문 순서 {len(load(shots)["shots"])}개 용수철·감쇠 장면 작성 · 실행 검수 대기'
    if item['id']=='M22' and load(project/'planning/production-plan.json').get('narrationFinal'):
        stage='36문단·게임 3예시·장면 연결 확정 · 표식 수정 검수 중'
        vf=project/'production/local/audio-v1/finite-worker.json'
        if vf.exists():
            v=load(vf);stage+=' · '+{'synthesizing':'Qwen 음성 생성 중','voice-generated-review-pending':'음성 생성 완료·청취 검수 전'}.get(v['status'],'음성 생성 대기')
    if item['id']=='M23' and load(project/'planning/production-plan.json').get('narrationFinal'):
        stage='68문단·게임 4구간·발화 전환 100개 연결 · 수정 화면·음성 제작 대기'
    if item['id'] in {'M29','M30'}:
        name='dynamics-shots.json' if item['id']=='M29' else 'rigid-shots.json'
        shots=project/'production/unity-staging'/name
        stage=f'원문 순서 {len(load(shots)["shots"])}개 설명 장면 작성 · 실행 검수 전' if shots.exists() else '통합 대본·충돌/관성 수치 검사 완료 · 설명 씬 구현 중'
    if item['id'] in {f'M{i}' for i in range(31,34)}:
        path=project/'production/unity-staging/curve-shots.json'
        stage=f'원문 순서 {len(load(path)["shots"])}개 곡선 설명 장면 작성 · 실행 검수 전' if path.exists() else '통합 대본·곡선 계산 검사 완료 · 애니메이션 실행 검수 전'
    row['productionStatus']=stage
    row['productionComplete']=False
    row['reviewStatus']='완성 영상 대기 · 실제 음성/합성 검수 전'
    row['notes']='2026-11-04 승인된 M21–M33 로컬 제작 범위. '+stage+'. 업로드·예약 미승인.'
    item['evidence']={'sourceAudit':str(project/'planning/source-audit.json') if (project/'planning/source-audit.json').exists() else None,
                      'footageAudit':str(project/'planning/footage-audit.json') if (project/'planning/footage-audit.json').exists() else None}
    # Project-level checkpoints must not remain at an obsolete source-pending
    # stage while the batch ledger reports authored scenes and active media jobs.
    cp=project/'production/checkpoint.json';existing=load(cp) if cp.exists() else {}
    binding=project/'planning/scene-bindings.json';source_bindings=load(binding) if binding.exists() else None
    existing.update(updatedAt=datetime.now(timezone.utc).isoformat(),stage=stage,batch='production/batches/game-math-remaining-20261104/batch.json',localReviewReady=False,humanReview=False,outputsReady=False)
    existing['evidence']=dict(item['evidence'],sceneBindings=str(binding) if source_bindings else None)
    existing['nextAction']='Finish actual speech, source-matched runtime checks, integrated edit and internal audiovisual/mobile QA; only then deliver four local files.'
    if source_bindings:existing['boundSourceParagraphs']=len(source_bindings['scenes'])
    vf=project/'production/local/audio-v1/finite-worker.json'
    existing['voiceWorker']=load(vf) if vf.exists() else None
    existing['runningCostlyJobs']=[]
    if existing['voiceWorker'] and existing['voiceWorker']['status']=='synthesizing':existing['runningCostlyJobs'].append('approved Qwen narration')
    save(cp,existing)
batch['updatedAt']=datetime.now(timezone.utc).isoformat()
save(BATCH/'batch.json',batch);save(ROOT/'shared/publishing/video-worklist.json',work)
checkpoint=load(BATCH/'checkpoint.json')
checkpoint['updatedAt']=batch['updatedAt']
checkpoint['currentWork']=['Complete source audit and bilingual draft: '+', '.join(sorted(reported_complete)),
                         'M21 narration complete (79 paragraphs, 1917.9200833333307 seconds); original PCM preserved. Full ASR aligned, 715 KO / 606 EN cues, zero alignment flags. Final media and integrated QA pending.',
                         'All 13 integrated bilingual scripts and gameplay bindings exist; M22–M33 staged math/renderer modules compile; M29/M30 shared numerical model passes 2261 invariants; 37/60 source-ordered scene configurations prepared; visual/runtime QA pending',
                         'M21 original raster crops disprove apparent UI/render corruption in tool previews; labels match pixel-for-pixel across V15/V16/V17. V15 17 material/volume/grid repairs are image-approved; production recaptures and integrated final QA pending. All seven gameplay annotation layouts inspected at 1080p/375px; final integrated review pending.',
                         'M22 36 unchanged bilingual paragraphs and35 Unity modes bound; nine V2 runtime samples inspected, eight targeted V3 checks prepared. Voice design frozen, final speech and media QA pending.',
                         'M24–M26 runtime samples inspected; repaired explicit override serialization, hidden motion guides, formula/object overlap and reverse-motion graph ranges. V3 runtime queues prepared.',
                         'M31/M32/M33 now have 36/29/42 source-ordered configurations with 130 checked speech anchors; 1387 curve-model assertions pass. Runtime/visual/speech QA pending.',
                         'M27 31 source-ordered force/friction scenes; M28 24 source-ordered spring/damping scenes. Corrected capture camera interface and out-of-range graph clipping; revised runtime checks pending.']
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
checkpoint['nextAction']='Inspect M21 targeted repair samples, reuse verified captures and render only changed scenes, then compose and review full media. Finish M22–M27 scoped runtime repairs and complete M28–M33 source-beat coverage. No platform mutation.'
if preflight.exists() and load(preflight)['status'] in {'running-preflight','waiting-for-idle-resources'}:
    actual=load(preflight)
    checkpoint['runningCostlyJobs']=[actual.get('current','M21 font regression')] if actual['status']=='running-preflight' else []
    checkpoint['resourceGate']={'status':actual['status'],'reason':actual.get('reason'),'lastCheckedAt':actual.get('checkedAt')}
    checkpoint['nextAction']='Inspect current targeted M21 specular/grid samples; prepare a scoped capture revision reusing verified unchanged scenes. Original narration unchanged. Continue authorized source-beat work during resource waits.'
caption_sample=ROOT/'projects/game-math-shading-lights/production/local/encoder-sample-v1/caption-sample-progress.json'
if caption_sample.exists():
    checkpoint['encoderCaptionSample']=load(caption_sample)
    if checkpoint['encoderCaptionSample']['status']=='waiting-for-scoped-resources':
        checkpoint['resourceGate']=checkpoint['encoderCaptionSample'];checkpoint['runningCostlyJobs']=[]
capture=latest_render(ROOT/'projects/game-math-shading-lights')/'progress.json'
if capture.exists():
    checkpoint['productionCapture']=load(capture)
    checkpoint['runningCostlyJobs']=[checkpoint['productionCapture'].get('current')] if checkpoint['productionCapture']['status']=='capturing' else []
    checkpoint['resourceGate']={'status':checkpoint['productionCapture']['status'],'reason':checkpoint['productionCapture'].get('reason')}
checkpoint['modulePreflights']={}
for item in batch['items'][1:]:
    slug=item['slug'];path=latest_preview(ROOT/'projects'/slug)
    if path.exists():checkpoint['modulePreflights'][slug]={**load(path),'progressPath':path.relative_to(ROOT).as_posix()}
compositor=latest_render(ROOT/'projects/game-math-shading-lights')/'composite/worker.json'
if compositor.exists():checkpoint['compositorWorker']=load(compositor)
checkpoint['lastPlanningCommit']='01f08cc92f3ea5ba6e2234e4c99377edbf9021c6'
checkpoint['lastProductionCommit']=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
# Derive running state from live owned workers; historical failures must not erase it.
import psutil
active=[];checkpoint['episodeVoiceWorkers']={}
for item in batch['items']:
    project=ROOT/'projects'/item['slug']
    paths=[project/'production/local/audio-v1/finite-worker.json',project/'production/local/audio-v1/finite-word-review.json',latest_preview(project),latest_render(project)/'progress.json',latest_render(project)/'composite/worker.json']
    for path in paths:
        if not path.is_file():continue
        state=load(path)
        if path.name=='finite-worker.json':checkpoint['episodeVoiceWorkers'][item['id']]=state
        try:alive=abs(psutil.Process(state['pid']).create_time()-state['createTime'])<.1
        except (KeyError,psutil.NoSuchProcess):alive=False
        if alive and state['status'] in {'synthesizing','running-preflight','capturing','transcribing-word-timestamps','compositing'}:active.append({'episode':item['id'],'status':state['status'],'pid':state['pid'],'evidence':path.relative_to(ROOT).as_posix()})
checkpoint['runningCostlyJobs']=active
if active:checkpoint['resourceGate']={'status':'active-owned-work','jobs':active}
checkpoint['nextAction']='Complete M22 approved-voice generation; recapture 17 image-approved M21 repairs with 61 structurally verified captures reused, then final compose/QA and source-matched module runtime QA. No final video is marked ready before integrated review.'
save(BATCH/'checkpoint.json',checkpoint)
subprocess.run(['python','-X','utf8',str(BATCH/'progress.py')],cwd=ROOT,check=True)
