"""Direct complete-context comparison; no claim of human auditory approval."""
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
dest=BASE/'observation-guides-independent-direct-review-v1.json';assert not dest.exists()
sp=BASE/'observation-guides-independent-asr-execution-v1.session.json';s=read(sp)
assert s['pid']==18980 and s['sessionId']==31916
s.update(alive=False,exitObserved=True,exitCode=0,exitObservedAt=now(),
    observedBy='Actual exec session31916 returned exit0; matched18980/proxy60804 absent in CIM')
save(sp,s)
stp=BASE/'observation-guides-independent-asr-execution-v1.json';st=read(stp)
assert st['completed']==10 and st['exitCode']==0
plan=read(BASE/'observation-guides-independent-context-plan-v1.json')
assert sha(BASE/'observation-guides-independent-context-plan-v1.json')==st['planSha256']
asrp=BASE/'observation-guides-independent-asr-v1/asr.json';a=read(asrp)
whole=read(BASE/'observation-guides-whole-asr-v2/asr.json')
assert a['complete'] and len(a['results'])==10
rows=[]
for r in a['results']:
    assert sha(ROOT/r['sourcePath'])==r['sourceSha256'] and sha(ROOT/r['contextPath'])==r['contextSha256']
    with wave.open(str(ROOT/r['sourcePath']),'rb') as w:
        w.setpos(r['startSample']);raw=w.readframes(r['endSample']-r['startSample'])
    with wave.open(str(ROOT/r['contextPath']),'rb') as w:assert raw==w.readframes(w.getnframes())
    assert hashlib.sha256(raw).hexdigest()==r['pcmSha256']
    prev=0
    for word in r['words']:
        x,y=word['timestamp'];assert x is not None and y is not None and 0<=x<=y and x>=prev
        prev=y
    note='Complete expected final sentence and every recognized word directly read; no missing/repeated sentence or arbitrary greeting observed. Punctuation/spacing only.'
    if r['id']=='13-complete-ending':note='Complete 새 발차기와 방향 잡기의 연결을 나누어 보세요 present with monotonic0..2.92s words. Exact source5.30..8.2400417s PCM bytes matched. High tailRatio0.2562 retained; neither truncation nor phonetic approval inferred from it.'
    if r['id']=='12-particle-context':note='Complete first sentence present; 앞의 remains recognized 앞에 independently. Preserve particle/phonetic uncertainty for human listening; no audio correction claimed.'
    if r['id']=='16-particle-context':note='Complete first two sentences present; 위의 remains recognized 위에 independently. Preserve particle/phonetic uncertainty; no auditory correction claimed.'
    w=next(x for x in whole['results'] if x['id']==r['scene'])
    rows.append(dict(id=r['id'],scene=r['scene'],expectedKo=r['expectedKo'],recognizedText=r['text'],wholeRecognizedText=w['text'],
        allExpectedSentencesAndRecognizedWordsDirectlyRead=True,wordCount=len(r['words']),wordTimesMonotonic=True,
        sourceSha256=r['sourceSha256'],contextSha256=r['contextSha256'],exactCurrentPcmSourceSampleBytesMatched=True,
        resultSha256=sha(BASE/'observation-guides-independent-asr-v1'/(r['id']+'.json')),observation=note,phoneticApproval=False))
review=dict(schemaVersion=1,slug='familiar-game-rules',reviewedAt=now(),wholeGuideCount=8,independentContextCount=10,rows=rows,
    allExpectedAndRecognizedWordsDirectlyRead=True,allCurrentPcmSlicesBytesMatched=True,
    independentAsrSha256=sha(asrp),wholeAsrSha256=sha(BASE/'observation-guides-whole-asr-v2/asr.json'),
    noFullSentenceOmissionRepetitionOrGreetingObserved=True,structuralContentReviewComplete=True,
    technicalStructuralReadbackComplete=True,asrApproved=False,narrationApproved=False,finalMixedAsrApproved=False,
    endingHeuristicWasApproval=False,pendingIssues=['12 앞의/앞에','16 위의/위에','13 ending release/articulation requires human listening'],
    humanWholeListening='pending',pronunciation='pending',approvalScope='Structural full-text/end comparison, not auditory/phoneme approval.',newGitImages=0)
save(dest,review)
st.update(alive=False,actualExitObserved=True,exitObservedAt=now(),directReview=True,directReviewPath=rel(dest),structuralContentReviewComplete=True);save(stp,st)
qp=PROOF.parent/'queue.json';q=read(qp);item=next(x for x in q['items'] if x['slug']=='familiar-game-rules')
assert item['execution']['pid']==18980
item['execution'].update(alive=False,exitCode=0,actualExitObserved=True,activeTasks=[])
item.update(stage='new8whole-plus10contexts-direct-reviewed-join-and-framing-pending',updatedAt=now(),
    guideIndependentDirectReview=rel(dest),guideStructuralContentReviewComplete=True,
    nextAction='Preserve original11/46PCM296.72s and sixwhite147.2s. Find true quiet paragraph boundaries, assemble byte-exact8joins and directly read their ASR. Then adopt word/action timeline, meaningful added comparisons and every fixed-caption pixel. Human listening/pronunciation still pending; no final render/upload yet.')
q.update(updatedAt=now(),lastProgressAt=now());save(qp,q)
for p in [BASE/'latest-checkpoint.json',PROOF/'latest-checkpoint.json']:
    d=read(p)
    for k in ['stage','updatedAt','execution','nextAction','guideIndependentDirectReview','guideStructuralContentReviewComplete']:d[k]=item[k]
    save(p,d)
print(json.dumps(dict(wholeGuides=8,independentContexts=10,allWordsDirectlyRead=True,pcmBytesMatched=True,phoneticApproval=False)))
