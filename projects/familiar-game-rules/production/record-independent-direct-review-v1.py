"""Record human-agent direct comparison of every completed context; no phonetic claim."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, time, wave

ROOT=Path(__file__).resolve().parents[3]
BASE=Path(__file__).resolve().parent
PROOF=ROOT/'production/batches/sakurai-planning-game-design/proof-familiar-game-rules'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
stamp=datetime.now(timezone.utc).isoformat()
def write(p,d):
    tmp=p.with_name(p.name+f'.{os.getpid()}.writing')
    tmp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for n in range(40):
        try:os.replace(tmp,p);return
        except OSError:
            if n==39:raise
            time.sleep(.15)

dest=BASE/'current-independent-direct-review-v1.json'
assert not dest.exists(), 'Read completed review; do not repeat or overwrite'
state=read(BASE/'current-independent-asr-execution-v1.json')
assert state['completed']==16 and state['exitCode']==0
plan=read(BASE/'current-independent-context-plan-v1.json')
assert sha(BASE/'current-independent-context-plan-v1.json')==state['planSha256']
whole=read(BASE/'current-whole-asr-v1/asr.json')
asr=read(BASE/'current-independent-asr-v1/asr.json')
assert asr['complete'] and len(asr['results'])==16
notes={
 '01-role-tail':'Both complete sentences and bridge directly read. 맡는 remains recognized 맞는; preserve orthography/phonetic uncertainty. No missing/repeated sentence or greeting observed.',
 '01-game-names':'Full ordered three-game statement present. 앵거 풋 recognized 앵거푸트, 건브렐라 recognized 검브렐라; 페드로 present in this independent context. Proper-name pronunciation remains pending.',
 '02-addition':'Both sentences present. 조준에 remains 조준의; preserve unresolved particle/phonetic discrepancy, not repaired audio.',
 '02-tail':'Complete final paragraph and 있습니다 ending present. 일인칭/1인칭 numeric orthography differs only.',
 '03-tail':'Complete new-user caveat and 합니다 ending present; no omission/repetition/greeting observed.',
 '04-complete-tail':'Both complete paragraphs present, including montage/continuous-action caution and 않습니다 ending. 둘지뿐 remains 둘짓뿐; preserve pronunciation/particle review.',
 '05-tail':'Complete simultaneous-action and remapped-guidance instruction present; no omission/repetition/greeting observed.',
 '06-name-role':'Both complete first paragraphs present. 건브렐라/검브렐라 and 맡는/맞는 differences persist. No device-binding or universal-blocking claim inferred.',
 '06-complete-tail':'Full two-sentence final paragraph recognized with monotonic word times0..7.42s. Current source samples24.72..32.16s match exactly; whole-result29.12→28.94 timestamp reversal is not repeated speech evidence. Complete 확인합니다 ending present.',
 '07-tail':'Full final selection/range/continuous-change instruction and 보세요 ending present; spacing only.',
 '08-name':'Full first paragraph present; 페드로 remains 패드로 and 겨눕니다 becomes 견눕니다 in this context. Preserve proper-name and articulation uncertainty.',
 '08-complete-tail':'Both complete final paragraphs recognized with monotonic times0..14.82s, source samples20.20..35.04s exact. Whole-result28.44→28.04 reversal not present here; device-evidence caution and 합니다 ending complete.',
 '09-tail':'Complete decision-preservation instruction and 대조하세요 ending present; 지키는 데/지키는데 spacing only.',
 '10-complete-tail':'Both complete final paragraphs present with monotonic times0..13.32s, source19.48..33.20s exact. Whole26.18→26.04 reversal not present here. No repeated sentence or arbitrary goodbye observed.',
 '11-role':'Full input-role/additional-action instruction present; 맡는 remains 맞는. Orthographic/phonetic issue retained.',
 '11-tail':'Full other-path conclusion and 있습니다 ending present. No arbitrary goodbye/omission/repeated sentence observed.'
}
rows=[]
for r in asr['results']:
    c=next(x for x in plan['contexts'] if x['id']==r['id'])
    assert sha(ROOT/r['sourcePath'])==r['sourceSha256']==c['sourceSha256']
    assert sha(ROOT/r['contextPath'])==r['contextSha256']
    with wave.open(str(ROOT/r['sourcePath']),'rb') as w:
        w.setpos(c['startSample']);pcm=w.readframes(c['endSample']-c['startSample'])
    with wave.open(str(ROOT/r['contextPath']),'rb') as w:
        assert w.readframes(w.getnframes())==pcm
    assert hashlib.sha256(pcm).hexdigest()==r['pcmSha256']
    previous=0
    for word in r['words']:
        a,b=word['timestamp'];assert a is not None and b is not None and 0<=a<=b and a>=previous
        previous=b
    whole_row=next(x for x in whole['results'] if x['scene']==r['scene'])
    rows.append(dict(id=r['id'],scene=r['scene'],expectedKo=r['expectedKo'],recognizedText=r['text'],
        wordCount=len(r['words']),allWordsAndExpectedSentencesDirectlyRead=True,
        wholeTextDirectlyCompared=whole_row['text'],sourceSha256=r['sourceSha256'],contextSha256=r['contextSha256'],
        resultSha256=sha(BASE/'current-independent-asr-v1'/(r['id']+'.json')),
        exactCurrentPcmSourceSampleBytesMatched=True,independentWordTimesMonotonic=True,
        observation=notes[r['id']],structuralContentReviewed=True,phoneticApproval=False))
review=dict(schemaVersion=1,slug='familiar-game-rules',reviewedAt=stamp,contextCount=16,wholeSceneCount=11,
    currentExpectedParagraphCount=46,allExpectedAndRecognizedWordsDirectlyRead=True,
    allCurrentPcmSlicesBytesMatched=True,rows=rows,wholeAsrSha256=sha(BASE/'current-whole-asr-v1/asr.json'),
    independentAsrSha256=sha(BASE/'current-independent-asr-v1/asr.json'),
    noFullSentenceOmissionRepetitionOrGreetingObserved=True,endingHeuristicWasApproval=False,
    structuralContentReviewComplete=True,asrApproved=False,narrationApproved=False,automaticApproval=False,
    pendingIssues=['Game-name pronunciations: 앵거 풋/앵거푸트, 건브렐라/검브렐라, 페드로/패드로',
        'Particle/articulation: 조준에/조준의, 둘지뿐/둘짓뿐, 겨눕니다/견눕니다; 맡는/맞는 orthography'],
    humanWholeListening='pending',pronunciation='pending',finalMixedAsrApproved=False,
    approvalScope='Structural full-text/ending comparison only. No direct auditory or phoneme approval claimed.')
write(dest,review)
sp=BASE/'current-independent-asr-execution-v1.session.json';session=read(sp)
assert session['pid']==17412 and session['sessionId']==66281
session.update(alive=False,exitObserved=True,exitCode=0,exitObservedAt=stamp,
    observedBy='Actual exec session66281 returned exit0; matched actualPython17412/proxy60348 absent in CIM')
write(sp,session)
state.update(alive=False,actualExitObserved=True,exitObservedAt=stamp,directReview=True,
    directReviewPath=rel(dest),structuralContentReviewComplete=True)
write(BASE/'current-independent-asr-execution-v1.json',state)
qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qp)
item=next(x for x in q['items'] if x['slug']=='familiar-game-rules')
assert item['execution']['pid']==17412
item['execution'].update(alive=False,exitCode=0,exitObserved=True,actualExitObserved=True,activeTasks=[])
item.update(stage='current11-plus16-direct-reviewed-source-expansion-pending-pronunciation',updatedAt=stamp,
    independentNarrationDirectReview=rel(dest),narrationStructuralReviewComplete=True,
    nextAction='Preserve all11currentPCM and147.2s white explanation. Secure distinct additional actual action; precise edges/cross-source review before guide writing and measured60:40. Audio phonetic/particle review still pending; no final mix/render/QA/upload approval.')
write(qp,q)
for p in [BASE/'latest-checkpoint.json',PROOF/'latest-checkpoint.json']:
    d=read(p)
    for k in ['stage','updatedAt','execution','nextAction','independentNarrationDirectReview','narrationStructuralReviewComplete']:d[k]=item[k]
    d.update(asrApproved=False,narrationApproved=False,finalRatioApproved=False);write(p,d)
print(json.dumps(dict(wholeScenes=11,independentContexts=16,allWordsDirectlyRead=True,pcmBytesMatched=True,asrApproved=False,pronunciation='pending')))
