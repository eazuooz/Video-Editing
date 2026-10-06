"""Record full original-guide-original readback and exact component bytes."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,time,wave
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
PROOF=ROOT/'production/batches/sakurai-planning-game-design/proof-familiar-game-rules'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
now=lambda:datetime.now(timezone.utc).isoformat()
def save(p,d):
    t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for n in range(40):
        try:os.replace(t,p);return
        except OSError:
            if n==39:raise
            time.sleep(.15)
def pcm(p):
    with wave.open(str(p),'rb') as w:return w.readframes(w.getnframes())
dest=BASE/'guide-joins-direct-review-v1.json';assert not dest.exists()
statepath=BASE/'guide-joins-asr-execution-v1.json';st=read(statepath);assert st['completed']==8 and st['exitCode']==0
sessionpath=BASE/'guide-joins-asr-execution-v1.session.json';s=read(sessionpath);assert s['pid']==50708 and s['sessionId']==7459
s.update(alive=False,exitObserved=True,exitCode=0,exitObservedAt=now(),observedBy='Actual exec session7459 returned exit0; matched50708/proxy45204 absent in CIM');save(sessionpath,s)
plan=read(BASE/'guide-join-context-plan-v1.json');assert sha(BASE/'guide-join-context-plan-v1.json')==st['planSha256']
audit=read(ROOT/plan['insertionAudit']);assert sha(ROOT/plan['insertionAudit'])==plan['insertionAuditSha256']
for id in [f'{i:02d}' for i in range(1,12)]:
    fragments=[x for x in audit['originalFragments'] if x['scene']==id]
    source=ROOT/fragments[0]['sourcePath'];assert sha(source)==fragments[0]['sourceSha256']
    parts=[]
    for f in fragments:assert sha(ROOT/f['path'])==f['sha256'];parts.append(pcm(ROOT/f['path']))
    assert b''.join(parts)==pcm(source)
asrpath=BASE/'guide-joins-asr-v1/asr.json';a=read(asrpath);assert a['complete'] and len(a['results'])==8
notes={
 '12':'All seven complete sentences read. Original 조준에/조준의 and new 앞의/앞에 discrepancies persist; no sentence loss or repetition at either insertion boundary.',
 '13':'Original complete paragraph → all three guide sentences → original complete next paragraph present. Original 둘지뿐/둘짓뿐 remains; new final 보세요 fully recognized before 새 기획에서는. High tail heuristic was not used for approval.',
 '14':'Original tool introduction → all three city/wire guide sentences → original air/upward-target paragraph complete. 건브렐라/검브렐라 and 맡는/맞는 issues persist as before; no sentence loss/repetition.',
 '15':'Original complete action paragraph → three rail/market/swamp/container guide sentences → complete input-evidence caveat present. 맡는/맞는 retained; no loss/repetition/greeting.',
 '16':'Original first paragraph, three train-guide sentences and complete barrel/hanging paragraph all present. 페드로 is recognized here whereas another original independent context used 패드로; do not infer corrected pronunciation. 위의/위에 persists.',
 '17':'Both original direction-selection sentences → all three opposite-gun/design guide sentences → complete input/device-evidence caution present. Every word monotonic; no loss/repetition/greeting.',
 '18':'Both original movement-preservation sentences, all three roof/downward-aim guide sentences and full next design-check sentence present. Some word boundary timestamps touch despite exact120ms separators; no timing-based auditory conclusion.',
 '19':'Complete original design-check sentence → three rotation/roof/carriage guide sentences → complete original new-route conclusion present. Monotonic0..23.50s, original whole26.18→26.04 reversal not copied into this join. No loss/repetition/greeting.'
}
rows=[]
for r in a['results']:
    assert sha(ROOT/r['sourcePath'])==r['sourceSha256'] and sha(ROOT/r['contextPath'])==r['contextSha256']
    raw=pcm(ROOT/r['sourcePath']);assert raw==pcm(ROOT/r['contextPath'])
    for c in r['sourceComponents']:
        data=raw[2*c['startSample']:2*c['endSample']]
        assert hashlib.sha256(data).hexdigest()==c['pcmSha256']
        if c['sourcePath']:
            original=pcm(ROOT/c['sourcePath']);assert data==original[2*c['sourceStartSample']:2*c['sourceEndSample']]
        else:assert set(data)=={0}
    previous=0
    for w in r['words']:
        x,y=w['timestamp'];assert x is not None and y is not None and 0<=x<=y and x>=previous;previous=y
    rows.append(dict(id=r['id'],parentScene=r['parentScene'],expectedKo=r['expectedKo'],recognizedText=r['text'],
        allExpectedSentencesAndActualWordsDirectlyRead=True,wordCount=len(r['words']),wordTimesMonotonic=True,
        sourceSha256=r['sourceSha256'],contextSha256=r['contextSha256'],allComponentPcmBytesMatched=True,
        resultSha256=sha(BASE/'guide-joins-asr-v1'/(r['id']+'.json')),observation=notes[r['scene']],phoneticApproval=False))
review=dict(schemaVersion=1,slug='familiar-game-rules',reviewedAt=now(),joinCount=8,rows=rows,
    asrSha256=sha(asrpath),insertionAuditSha256=plan['insertionAuditSha256'],allOriginal11PcmRecombinedExactly=True,
    allJoinComponentBytesMatched=True,allExpectedAndRecognizedWordsDirectlyRead=True,structuralContentReviewComplete=True,
    noFullSentenceOmissionRepetitionOrGreetingObserved=True,endingHeuristicWasApproval=False,
    asrApproved=False,narrationApproved=False,finalMixedAsrApproved=False,finalTimelineAdopted=False,finalTimingApproved=False,
    pendingIssues=['Original proper-name/articulation issues remain','12 앞의/앞에','16 위의/위에','13 end release requires human listening'],
    humanWholeListening='pending',pronunciation='pending',newGitImages=0)
save(dest,review)
st.update(alive=False,actualExitObserved=True,exitObservedAt=now(),directReview=True,directReviewPath=rel(dest),structuralContentReviewComplete=True);save(statepath,st)
qp=PROOF.parent/'queue.json';q=read(qp);item=next(x for x in q['items'] if x['slug']=='familiar-game-rules');assert item['execution']['pid']==50708
item['execution'].update(alive=False,exitCode=0,actualExitObserved=True,activeTasks=[])
item.update(stage='all-original-new-guide-joins-direct-reviewed-final-timeline-and-caption-framing-pending',updatedAt=now(),
    guideJoinsDirectReview=rel(dest),byteExactInsertionAudit=plan['insertionAudit'],guideJoinStructuralReviewComplete=True,
    nextAction='Preserve original11/46PCM296.72s, new8PCM77.2000417s, originalsixwhite147.2s and24.32s overview. Test targeted literal cues/static crops; then adopt measured word/action alignment, every source/caption pixel and60:40. Final mix/ASR/render/QA/collection/private false; human listening/pronunciation pending.')
q.update(updatedAt=now(),lastProgressAt=now());save(qp,q)
for p in [BASE/'latest-checkpoint.json',PROOF/'latest-checkpoint.json']:
    d=read(p)
    for k in ['stage','updatedAt','execution','nextAction','guideJoinsDirectReview','byteExactInsertionAudit','guideJoinStructuralReviewComplete']:d[k]=item[k]
    save(p,d)
print(json.dumps(dict(joinContexts=8,allWordsRead=True,allOriginalPcmBytesPreserved=True,finalApproval=False)))
