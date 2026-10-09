"""Seal directly compared independent results and prepare a PCM-exact join.
The old13 voices remain immutable. No final-mix or human-listening approval.
"""
from pathlib import Path
from datetime import datetime, timezone
import array, difflib, hashlib, json, math, os, psutil, re, wave
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return p.relative_to(ROOT).as_posix()
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8')
def pcm(p):
    with wave.open(str(p),'rb') as w:
        params=w.getparams();assert (params.framerate,params.nchannels,params.sampwidth)==(24000,1,2)
        return params,w.readframes(w.getnframes())
def wav(p,params,data):
    assert not p.exists();p.parent.mkdir(parents=True,exist_ok=True)
    with wave.open(str(p),'wb') as w:w.setparams(params);w.writeframes(data)
    assert pcm(p)[1]==data
stamp=datetime.now(timezone.utc).isoformat()
statepath=BASE/'guides-contexts-asr-v3-execution.json';state=read(statepath)
assert state['exitCode']==0 and state['completed']==state['total']==9
if psutil.pid_exists(state['pid']):assert abs(psutil.Process(state['pid']).create_time()-state['createTime'])>.01
if (BASE/'guides-contexts-asr-direct-review-v3.json').exists():
    previous=read(BASE/'guides-contexts-asr-direct-review-v3.json')
    assert previous['independentAsrSha256']==sha(BASE/'guides-contexts-asr-v3/asr.json')
    assert not (BASE/'current-mining-pcm-join-prepared-v1.json').exists(), 'Read completed preparation.'
state.update(actualExitObserved=True,actualExitCodeObserved=0,processIdentityAbsentVerifiedAt=stamp);save(statepath,state)
session=read(BASE/'guides-contexts-asr-v3.session.json');session.update(status='closed-exit0-directly-observed',actualExitObserved=True,exitCode=0,observedAt=stamp);save(BASE/'guides-contexts-asr-v3.session.json',session)
whole=read(BASE/'guides-whole-asr-v3/asr.json');indep=read(BASE/'guides-contexts-asr-v3/asr.json');assert indep['complete']
notes={
 '14-corridor-pursuit':'Complete independent context has no added 자. Same full PCM sample0 retained; whole extra onset is recognition variance. 사이의/사이에 remains pronunciation/particle review pending.',
 '15-corridor-to-open':'Both complete paragraphs and terminal 보겠습니다 are present.',
 '16-effects-and-position':'Both complete paragraphs and terminal 쉽습니다 are present.',
 '17-rock-and-route':'Both complete paragraphs including full 있습니다 are present in whole and independent context; ending heuristic does not decide approval.',
 '18-target-and-effects':'Both complete paragraphs and terminal 봅시다 are present.',
 '19-visible-destination':'귀환/귀한 remains the same phonetic recognition discrepancy in two contexts. Return-section visual meaning is independently observed; human pronunciation is pending.',
 '20-moving-relationships':'회피/회피의 remains the same short particle recognition discrepancy. Every surrounding complete clause and terminal 달라집니다 are present; human pronunciation is pending.',
 '21-read-before-ranking':'Independent context explicitly contains initial 적. Same sample0 full PCM retained; whole omission is recognition variance, not a deleted syllable.',
 '22-mining-opening-repair':'Both whole and independent complete candidate contain 딥록 갤럭틱 서바이버의 and every expected sentence/terminal 장면입니다. Join with original26.18s remainder is prepared next, not yet approved.'}
rows=[]
for a,b in zip(whole['results'],indep['results']):
    assert b['sceneId']==a['id'] and a['expectedKo']==b['expectedKo'] and b['exactSourceSampleBytesMatched']
    assert sha(ROOT/a['sourcePath'])==a['sourceSha256'];assert sha(ROOT/b['contextPath'])==b['contextSha256']
    rows.append(dict(id=a['id'],expectedKo=a['expectedKo'],wholeText=a['text'],independentText=b['text'],
         independentWords=b['words'],sourcePath=a['sourcePath'],sourceSha256=a['sourceSha256'],
         independentPath=b['contextPath'],independentSha256=b['contextSha256'],
         fullExpectedActualTextsAndWordsDirectlyRead=True,fullPcmByteMatched=True,review=notes[a['id']]))
save(BASE/'guides-contexts-asr-direct-review-v3.json',dict(schemaVersion=1,reviewedAt=stamp,sessionId=19013,
     wholeAsrSha256=sha(BASE/'guides-whole-asr-v3/asr.json'),independentAsrSha256=sha(BASE/'guides-contexts-asr-v3/asr.json'),
     allNineCompleteContextsDirectlyCompared=True,results=rows,allCurrentSamplesRetained=True,
     structuralOmissionsRepetitionsOrUnscriptedGreetingConfirmed=False,automatedTextIntegrityReviewPassed=True,
     unresolvedHumanPronunciation=['14 사이의/사이에','19 귀환/귀한','20 회피/회피의'],
     candidate22CompleteTextApprovedForPcmJoin=True,original04JoinApproved=False,
     finalMixedAsrApproved=False,humanListening='pending',humanPronunciation='pending'))
# Current whole timestamps provide a candidate quiet split between the two
# already-read complete paragraphs. This measurement needs its own direct review.
guideMeasures=[]
for a in whole['results'][:8]:
    params,data=pcm(ROOT/a['sourcePath']);values=array.array('h',data)
    norm=lambda s: ''.join(re.findall(r'[가-힣A-Za-z0-9]',s))
    expected=''.join(norm(s) for s in a['expectedKo']);actual='';indices=[]
    for i,w in enumerate(a['words']):
        token=norm(w['text']);actual+=token;indices.extend([i]*len(token))
    pos=len(norm(a['expectedKo'][0]))-1
    match=next(m for m in difflib.SequenceMatcher(None,expected,actual,autojunk=False).get_matching_blocks() if m.a<=pos<m.a+m.size)
    firstEnd=indices[match.b+pos-match.a]
    prev,nxt=a['words'][firstEnd],a['words'][firstEnd+1]
    assert prev['text'].strip().rstrip('.') in ['보세요','있습니다','않겠습니다']
    lo=round(prev['timestamp'][1]*24000);hi=round(nxt['timestamp'][0]*24000);assert hi>=lo
    span=240;options=[]
    for center in range(lo+480,hi-480+1,60):
        rms=math.sqrt(sum(v*v for v in values[center-span//2:center+span//2])/span)/32768
        options.append((rms,abs(center-(lo+hi)/2),center))
    if options:rms,_,cut=min(options)
    else:
        cut=round((lo+hi)/2);rms=math.sqrt(sum(v*v for v in values[cut-span//2:cut+span//2])/span)/32768
    guideMeasures.append(dict(id=a['id'],path=a['sourcePath'],sha256=a['sourceSha256'],samples=len(values),
         boundary=dict(afterParagraph=1,previousWord=prev,nextWord=nxt,splitSample=cut,splitSeconds=cut/24000,normalizedRms=rms),
         paragraphs=[dict(paragraph=1,sourceInSample=0,sourceOutSample=cut,seconds=cut/24000),
                     dict(paragraph=2,sourceInSample=cut,sourceOutSample=len(values),seconds=(len(values)-cut)/24000)],
         entirePcmRetained=True))
save(BASE/'guides-paragraph-timing-candidate-v3.json',dict(schemaVersion=1,measuredAt=stamp,scenes=guideMeasures,
     allEightBoundaryWordPairsDirectlyRead=False,finalTimelineApproved=False,bodyRatioApproved=False))
repair=read(BASE/'localized-mining-first-paragraph-repair-plan-v1.json')
old=ROOT/repair['sourcePath'];new=ROOT/whole['results'][-1]['sourcePath']
assert sha(old)==repair['sourceSha256'];assert whole['results'][-1]['id']=='22-mining-opening-repair'
params,oldbytes=pcm(old);_,newbytes=pcm(new);start=repair['preservedOriginalRemainderStartSample']
remainder=oldbytes[start*2:];assert len(remainder)//2==628320
joined=ROOT/'shared/output/narration/similar-game-design/current-mining-pcm-join-v1/04-mining-route-scene.wav'
wav(joined,params,newbytes+remainder)
originalArchive=joined.parent/'archived-original-first-paragraph.wav';wav(originalArchive,params,oldbytes[:start*2])
assert sha(old)==repair['sourceSha256'] and pcm(joined)[1][len(newbytes):]==remainder
expected=read(ROOT/'projects/similar-game-design/script/narration.ko.json')['scenes'][3]['lines']
assert expected[0]==whole['results'][-1]['expectedKo'][0]
newSamples=len(newbytes)//2;headEnd=446400-start+newSamples;total=(len(newbytes)+len(remainder))//2
windows=[dict(id='04-mining-route-whole',startSample=0,endSample=total,zeroPaddingSamplesEachSide=0,expectedKo=expected),
         dict(id='04-mining-route-complete-join',startSample=0,endSample=headEnd,zeroPaddingSamplesEachSide=9600,expectedKo=expected[:2]),
         dict(id='04-mining-route-complete-tail',startSample=headEnd,endSample=total,zeroPaddingSamplesEachSide=9600,expectedKo=expected[2:])]
for r in windows:r.update(sourcePath=rel(joined),sourceSha256=sha(joined))
save(BASE/'current-mining-pcm-join-prepared-v1.json',dict(schemaVersion=1,preparedAt=stamp,sourcePath=rel(joined),sourceSha256=sha(joined),
     sourceSamples=total,seconds=total/24000,replacementSamples=newSamples,replacementPath=rel(new),replacementSha256=sha(new),
     originalPath=rel(old),originalSha256=sha(old),preservedOriginalRemainderStartSample=start,preservedRemainderSamples=628320,
     preservedRemainderSha256=hashlib.sha256(remainder).hexdigest(),allRemainderBytesIdentical=True,
     originalFirstParagraphArchive=rel(originalArchive),originalFirstParagraphArchiveSha256=sha(originalArchive),
     allOriginal13WavsUnchanged=True,wholeCandidateAndIndependentTextApproved=True,windows=windows,
     currentJoinedVoiceApproved=False,finalMixApproved=False,humanListening='pending',humanPronunciation='pending'))
print(json.dumps(dict(independentFullDirectlyCompared=9,joinSeconds=total/24000,originalRemainderSeconds=628320/24000,
                     original13Modified=False,guideBoundaries=guideMeasures),ensure_ascii=False))
