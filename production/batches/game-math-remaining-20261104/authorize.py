"""Record the user's finite M21–M33 local-production request without changing other work."""
from pathlib import Path
from datetime import datetime, timezone
import json

ROOT = Path(__file__).resolve().parents[3]
BATCH = Path(__file__).parent
KEY = 'explicitMathRemainingBatch20261104'

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def main():
    now = datetime.now(timezone.utc).isoformat()
    control_path = ROOT/'shared/publishing/video-production-control.json'
    worklist_path = ROOT/'shared/publishing/video-worklist.json'
    control, worklist = read(control_path), read(worklist_path)
    rows = [r for r in worklist['rows'] if r['id'] in {f'M{i:02d}' for i in range(21,34)}]
    assert len(rows)==13 and all(not r['productionComplete'] for r in rows)
    queue = {x['slug']:x for x in read(ROOT/'production/batches/game-math-part2-full-series/queue.json')['items']}
    auth = {
        'batchId':BATCH.name, 'authorizedAt':now,
        'userRequest':'좋아 그럼 M21 빛과 셰이딩부터 우리 최신 영상 규칙 적용해서 한번에 전부 제작해줘~',
        'scopeConfirmation':'M21~M33 남은 13편 전부',
        'itemIds':[r['id'] for r in rows], 'projectSlugs':[r['slug'] for r in rows],
        'productionAllowedNow':True, 'advanceWithinExactBatch':True,
        'boundary':'13 local final-review deliveries with clean/captioned 1080p60, KO/EN SRT, actual internal QA and selective Git',
        'humanReview':'pending for every new master; technical QA is not user viewing/listening',
        'upload':False, 'publish':False, 'schedule':False, 'deleteOrReplace':False,
        'drive':False, 'automationOrHeartbeat':False, 'advanceBeyondM33':False,
        'preserveOtherJobs':True, 'costlyJobs':'serialized; no duplicate launches or forced termination',
        'batchPlan':str(BATCH.relative_to(ROOT)).replace('\\','/')+'/batch.json'
    }
    if KEY in control:
        raise SystemExit('Batch already registered; inspect checkpoint instead of resetting it.')
    control[KEY]=auth
    items=[]
    for row in rows:
        q=queue[row['slug']]
        state='source-and-footage-review' if row['id']=='M21' else 'authorized-queued'
        item=dict(id=row['id'],slug=row['slug'],title=row['title'],sections=q['sections'],sourceNotion=q['sourceNotion'],status=state,localReviewReady=False,humanReviewed=False,outputFiles={},blockers=[])
        items.append(item)
        row.update(productionStatus='원문·게임 예시 확인 중' if row['id']=='M21' else '제작 승인 · 대기',reviewStatus='새 완성본 제작 후 로컬 검수',executionStatus='2026-11-04 M21~M33 명시 일괄 제작 승인',notes='사용자 범위 답변: M21~M33 남은 13편 전부. 로컬 검수본까지 제작; 업로드·예약·삭제 미포함.')
        row['evidence']=list(dict.fromkeys([*row.get('evidence',[]),auth['batchPlan']]))
    worklist['mathRemainingBatch20261104']={'batchPlan':auth['batchPlan'],'scope':auth['itemIds'],'localReviewReady':0,'humanReviewed':0}
    batch={'schemaVersion':1,'createdAt':now,'authorization':auth,'rules':{'sourceOrderAndDepth':'full selected current article, independently phrased, corrections evidenced','gameplay':'concept-matched independently sourced FHD, observed before/action/result, native motion; meaningful core examples','intro':'2s branding then real-game thesis abstract','lectureRatio':None,'lectureMusic':'no added BGM; original game audio with standard voice ducking','explanations':'Unity for spatial/math; MC/Manim as appropriate; persistent teaching objects','narration':'approved Qwen voice, speech overlaps relevant motion, no forced observation holds','delivery':'1920x1080 60fps clean/captioned KO/EN SRT','review':'actual visual/audio evidence, no fabricated human approval'},'items':items}
    save(BATCH/'batch.json',batch)
    save(BATCH/'checkpoint.json',{'updatedAt':now,'status':'active-preproduction','currentEpisode':'M21','localReviewReady':[],'runningCostlyJobs':[],'currentWork':['M21 full current source audit and Korean/English draft','M21 independent FHD gameplay review','M21 isolated Unity staging; preserve other live Unity project'],'nextAction':'Bind inspected gameplay and complete source-faithful narration/scene plan before TTS.'})
    save(control_path,control)
    save(worklist_path,worklist)
    project=ROOT/'projects/game-math-shading-lights'
    save(project/'project.json',{'schemaVersion':1,'slug':'game-math-shading-lights','status':'preproduction','titles':{'ko':'빛과 셰이딩'},'batch':BATCH.name,'startGate':{'productionAllowedNow':True,'authorizationKey':KEY},'video':{'width':1920,'height':1080,'fps':60},'paths':{'narration':'projects/game-math-shading-lights/script/narration.ko.json','narrationEnglish':'projects/game-math-shading-lights/script/narration.en.json'},'tts':{'engine':'qwen3-tts','language':'Korean','reference':'shared/voice-reference/reference-15-35s.wav','referenceText':'shared/voice-reference/reference-15-35s.ko.txt','model':'qwen3-tts/models/Qwen3-TTS-12Hz-1.7B-Base','outputDir':'shared/output/narration/game-math-shading-lights/qwen3-1.7b-balanced-v1','filenameStem':'game-math-shading-lights-qwen3-1.7b-balanced-v1','renderMode':'scene','sceneGapSeconds':0.28,'tailRatioThreshold':0.07,'tailDecayMsThreshold':70,'maxRenderAttempts':3,'maxNewTokens':1536,'edgeFadeSeconds':0.006},'audio':{'addedBackgroundMusic':False,'gameAudio':'preserve cleared original audio and duck only game bed under speech'},'publishing':{'allowedNow':False,'localFinalReviewRequired':True},'lecture':{'sections':['10.6','10.7'],'fixedRuntime':None,'fixedGameplayShare':None}})
    save(project/'planning/production-plan.json',{'schemaVersion':1,'batch':auth['batchPlan'],'episode':'M21','sourceAudit':'planning/source-audit.json','footageAudit':'planning/footage-audit.json','unityPlan':'planning/unity-plan.json','stage':'source-footage-script-preproduction','sourceFinal':False,'narrationFinal':False,'sceneBindingsFinal':False,'choices':[{'choice':'Complete all13 as one finite local-review batch','reason':'Explicit user scope confirmation; no per-episode approval gate.'},{'choice':'No fixed length or footage ratio','reason':'Full article teaching logic and concept-sized game examples take priority.'},{'choice':'Stage Unity outside shared live project','reason':'Other task currently owns Unity project; avoid changing its imports/scenes.'}],'learningSteps':[],'teachingBeats':[],'boundaryLinks':[],'terminology':[]})
    save(project/'production/checkpoint.json',{'updatedAt':now,'stage':'source-and-footage-review','runningCostlyJobs':[],'nextAction':'Finalize source and observed gameplay mapping before narration generation.'})
    save(project/'production/review-ledger.json',{'schemaVersion':1,'project':'game-math-shading-lights','checks':[],'localReviewReady':False,'humanReview':{'status':'not-requested-no-master'}})
    print('Registered finite M21–M33 batch; unrelated control selections and platform records preserved.')

if __name__=='__main__':
    main()
