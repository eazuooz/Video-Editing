"""Record direct full-text/word comparison and plan exact independent PCM contexts."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, time, wave

ROOT=Path(__file__).resolve().parents[3]; BASE=Path(__file__).resolve().parent
PROOF=ROOT/'production/batches/sakurai-planning-game-design/proof-familiar-game-rules'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
now=lambda:datetime.now(timezone.utc).isoformat()
def save(p,d):
    tmp=p.with_name(p.name+f'.{os.getpid()}.writing')
    tmp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for n in range(40):
        try:os.replace(tmp,p);return
        except OSError:
            if n==39:raise
            time.sleep(.15)

dest=BASE/'observation-guides-whole-direct-review-v1.json'
planpath=BASE/'observation-guides-independent-context-plan-v1.json'
assert not dest.exists() and not planpath.exists()
statepath=BASE/'observation-guides-whole-asr-execution-v2.json'
state=read(statepath);assert state['completed']==8 and state['exitCode']==0
sessionpath=BASE/'observation-guides-whole-asr-session-v2.json'
session=read(sessionpath);assert session['pid']==35308 and session['sessionId']==16005
session.update(alive=False,exitObserved=True,exitCode=0,exitObservedAt=now(),
    observedBy='Actual exec session16005 returned exit0; actual35308/proxy49140 absent in CIM at direct review')
save(sessionpath,session)
asrpath=BASE/'observation-guides-whole-asr-v2/asr.json';asr=read(asrpath)
assert asr['complete'] and len(asr['results'])==8
notes={
 '12':'All three sentences and all words read; 앞의 recognized 앞에. Complete 보세요 ending present; particle/phonetic uncertainty retained for independent first-sentence context and human listening.',
 '13':'All three sentences and words read, including 새 발차기 and complete 나누어 보세요 ending. High tailRatio0.2562 is preserved as a heuristic observation, not a truncation finding or approval. Independent complete final sentence still required.',
 '14':'All three sentences and words present, punctuation only. Whole actual last-sentence onset8.60s supports testing a new explanatory comparison; not yet an approved visual timing.',
 '15':'All three sentences and words present, punctuation only; 별도 구간 and complete 점검합니다 ending retained.',
 '16':'All three sentences and words read; 위의 recognized 위에. 따라가 보세요 recognized without a space. Particle/articulation uncertainty retained; full first-two-sentence context and final sentence required.',
 '17':'All three sentences and words present. Complete design-implication sentence begins7.46s in whole recognition; a prepared comparison remains unrendered/unapproved.',
 '18':'All three sentences and words present, including downward gun, lower target and complete 보세요 ending. No omitted sentence/repetition/greeting observed in this whole result.',
 '19':'All three sentences and words present, including roof-to-carriage transition and complete 점검합니다 ending. No omitted sentence/repetition/greeting observed in this whole result.'
}
rows=[]
for d in asr['results']:
    assert sha(ROOT/d['audioPath'])==d['audioSha256']
    prev=0
    for w in d['words']:
        a,b=w['timestamp'];assert a is not None and b is not None and 0<=a<=b and a>=prev and b<=d['seconds']+.04
        prev=b
    rows.append(dict(id=d['id'],expectedKo=d['expectedKo'],expectedEn=d['expectedEn'],recognizedText=d['text'],
        wordCount=len(d['words']),allExpectedSentencesAndActualWordsDirectlyRead=True,wordTimesMonotonic=True,
        audioSha256=d['audioSha256'],resultSha256=sha(BASE/'observation-guides-whole-asr-v2'/(d['id']+'.json')),
        observation=notes[d['id']],phoneticApproval=False))
review=dict(schemaVersion=1,slug='familiar-game-rules',reviewedAt=now(),wholeCount=8,rows=rows,
    allExpectedKoEnAndRecognizedWordsDirectlyRead=True,allCurrentAudioHashesMatched=True,
    wholeAsrSha256=sha(asrpath),noFullSentenceOmissionRepetitionOrGreetingObserved=True,
    wholeDirectReview=True,independentContextReview=False,structuralContentReviewComplete=False,
    technicalAsrApproved=False,asrApproved=False,narrationApproved=False,endingHeuristicWasApproval=False,
    pendingIssues=['12: 앞의/앞에','16: 위의/위에','13: high tail ratio requires complete independent ending context; no auditory truncation claim'],
    humanWholeListening='pending',pronunciation='pending',newGitImages=0)
save(dest,review)
contexts=[]
starts={'12':5.5,'13':5.3,'14':8.2,'15':6.85,'16':7.0,'17':7.22,'18':6.18,'19':5.92}
for d in asr['results']:
    expected=d['expectedKo'].split('. ')[-1]
    with wave.open(str(ROOT/d['audioPath']),'rb') as w:
        assert w.getframerate()==24000 and w.getnchannels()==1 and w.getsampwidth()==2
        count=w.getnframes()
    contexts.append(dict(id=d['id']+'-complete-ending',scene=d['id'],sourcePath=d['audioPath'],sourceSha256=d['audioSha256'],
        startSample=round(starts[d['id']]*24000),endSample=count,startSeconds=starts[d['id']],endSeconds=count/24000,
        expectedKo=expected,reason='Complete final sentence plus natural pre-onset context; inspect actual ending without heuristic approval.'))
for id,end,expected in [('12',2.45,'분홍색 문 앞의 대상을 겨눕니다.'),
    ('16',7.10,'이번에는 다른 기차 구간입니다. 객차 안을 지나면서 바닥 쪽 상대를 겨누다가 상자 위의 상대를 향하죠.')]:
    d=next(x for x in asr['results'] if x['id']==id)
    contexts.append(dict(id=id+'-particle-context',scene=id,sourcePath=d['audioPath'],sourceSha256=d['audioSha256'],
        startSample=0,endSample=round(end*24000),startSeconds=0,endSeconds=end,expectedKo=expected,
        reason='Full sentence context around 의/에 recognition discrepancy; retain pronunciation uncertainty.'))
plan=dict(schemaVersion=1,slug='familiar-game-rules',createdAt=now(),contextCount=10,contexts=contexts,
    wholeReview=rel(dest),wholeReviewSha256=sha(dest),wholeAsr=rel(asrpath),wholeAsrSha256=sha(asrpath),
    expectedWasRecognizerPrompt=False,original11WholeAnd16IndependentRepeated=False,automaticApproval=False,
    allContextsCompleteSentences=True,humanWholeListening='pending',pronunciation='pending')
save(planpath,plan)
state.update(alive=False,actualExitObserved=True,exitObservedAt=now(),wholeDirectReview=True,directReviewPath=rel(dest))
save(statepath,state)
qpath=PROOF.parent/'queue.json';q=read(qpath);item=next(x for x in q['items'] if x['slug']=='familiar-game-rules')
assert item['execution']['pid']==35308
item['execution'].update(alive=False,exitCode=0,actualExitObserved=True,exitObserved=True,activeTasks=[])
item.update(stage='8newguide-whole-direct-read-10complete-contexts-prepared',updatedAt=now(),
    guideWholeDirectReview=rel(dest),guideIndependentContextPlan=rel(planpath),
    nextAction='Run only10new exact complete guide contexts with existing working ASR wrapper, then directly compare all results/currentPCM. Preserve original11/46PCM296.72s and six white147.2s; phonetic approval and final timing/pixels remain pending.')
q.update(updatedAt=now(),lastProgressAt=now());save(qpath,q)
for p in [BASE/'latest-checkpoint.json',PROOF/'latest-checkpoint.json']:
    d=read(p)
    for k in ['stage','updatedAt','execution','nextAction','guideWholeDirectReview','guideIndependentContextPlan']:d[k]=item[k]
    save(p,d)
print(json.dumps(dict(wholeCount=8,allWordsDirectlyRead=True,independentCompleteContexts=10,technicalAsrApproved=False),ensure_ascii=False))
