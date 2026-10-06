"""Preserve every original PCM byte, insert new guides at measured quiet boundaries."""
from pathlib import Path
from datetime import datetime,timezone
import array,hashlib,json,math,os,wave
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
now=lambda:datetime.now(timezone.utc).isoformat()
def save(p,d):
    assert not p.exists(),f'Preserve existing artifact: {p}'
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def pcm(p):
    with wave.open(str(p),'rb') as w:
        assert w.getframerate()==24000 and w.getnchannels()==1 and w.getsampwidth()==2
        return w.readframes(w.getnframes())
def wav(p,raw):
    assert not p.exists()
    with wave.open(str(p),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000);w.writeframes(raw)
    assert pcm(p)==raw

assert read(BASE/'observation-guides-independent-direct-review-v1.json')['structuralContentReviewComplete']
request=read(BASE/'observation-guide-tts-request-v1.json')
for x in request['protectedInputs']:assert sha(ROOT/x['path'])==x['sha256'],x['path']
whole=read(BASE/'current-whole-asr-v1/asr.json')
orig=read(BASE.parent/'script/narration.ko.json')['scenes']
new=read(BASE/'observation-guide-tts-execution-v1.json')['results']
root=ROOT/'shared/output/narration/familiar-game-rules/byte-exact-insertions-v1'
assert not root.exists();(root/'original-fragments').mkdir(parents=True);(root/'join-contexts').mkdir()
# Last boundary uses the already reviewed monotonic independent10 context, not backward whole timestamps.
boundaries=[('02','12',2,10.82,11.06),('04','13',2,11.70,12.22),('06','14',1,5.40,5.64),('06','15',2,12.42,12.72),
    ('08','16',1,6.12,6.40),('08','17',3,20.20,20.46),('10','18',3,19.48,19.72),('10','19',4,25.98,26.32)]
cuts=[]
for scene,guide,paragraph,a,b in boundaries:
    source=ROOT/f'shared/output/narration/familiar-game-rules/qwen3-1.7b-balanced-v1/chunks/{scene}-scene.wav'
    raw=pcm(source);samples=array.array('h',raw);options=[]
    for c in range(round((a+.025)*24000),round((b-.025)*24000),60):
        window=samples[c-480:c+480];rms=math.sqrt(sum(v*v for v in window)/len(window));db=20*math.log10(max(rms,1e-9)/32768)
        peak=max(abs(v) for v in window)
        if db<=-50 and peak<=500:options.append((abs(c/24000-(a+b)/2),c,db,peak))
    assert options,'No safe low-amplitude boundary; inspect actual PCM before cutting'
    _,c,db,peak=min(options)
    z=min(range(c-60,c+61),key=lambda x:(abs(samples[x])+abs(samples[x-1]),abs(x-c)))
    cuts.append(dict(scene=scene,guide=guide,afterOriginalParagraph=paragraph,sourcePath=rel(source),sourceSha256=sha(source),
        splitSample=z,splitSeconds=z/24000,asrGap=[a,b],rms40msDbfs=db,peak40ms=peak,
        boundarySamples=[samples[z-1],samples[z]],originalSilenceKept=True,noCrossfadeOrSamplesRemoved=True,
        timingBasis='independent10 complete context + originalPCM' if guide=='19' else 'directly read whole word boundary + originalPCM'))
fragments=[];preservation=[]
for scene in orig:
    id=scene['id'];source=ROOT/f'shared/output/narration/familiar-game-rules/qwen3-1.7b-balanced-v1/chunks/{id}-scene.wav'
    raw=pcm(source);edges=[0]+[x['splitSample'] for x in cuts if x['scene']==id]+[len(raw)//2]
    parts=[]
    for i,(a,b) in enumerate(zip(edges,edges[1:])):
        part=raw[2*a:2*b];out=root/'original-fragments'/f'{id}-{i+1:02d}.wav';wav(out,part);parts.append(part)
        fragments.append(dict(scene=id,part=i+1,path=rel(out),sha256=sha(out),sourcePath=rel(source),sourceSha256=sha(source),
            startSample=a,endSample=b,samples=b-a,seconds=(b-a)/24000,pcmSha256=hashlib.sha256(part).hexdigest()))
    assert b''.join(parts)==raw
    preservation.append(dict(scene=id,sourceSha256=sha(source),samples=len(raw)//2,originalPcmSha256=hashlib.sha256(raw).hexdigest(),
        recombinedPcmSha256=hashlib.sha256(b''.join(parts)).hexdigest(),allOriginalSamplesInOrderExactlyOnce=True))
# Complete preceding/following sentences; each test includes a whole new guide, avoiding clipped phonemes.
context_bounds={'12':(5.20,17.20),'13':(5.98,18.56),'14':(0,12.568208333333333),'15':(5.521458333333333,18.24),
    '16':(0,12.92),'17':(12.92,25.70),'18':(12.55,26.151125),'19':(19.601458333333333,33.20)}
rows=[];silence=b'\0\0'*2880
for cut in cuts:
    id=cut['guide'];original=pcm(ROOT/cut['sourcePath']);guide=next(x for x in new if x['id']==id)
    assert sha(ROOT/guide['path'])==guide['sha256'];gpcm=pcm(ROOT/guide['path'])
    start,end=context_bounds[id];a=round(start*24000);b=round(end*24000);z=cut['splitSample']
    left=original[2*a:2*z];right=original[2*z:2*b];joined=left+silence+gpcm+silence+right
    out=root/'join-contexts'/f'{id}-join.wav';wav(out,joined)
    parent=next(x for x in orig if x['id']==cut['scene']);para=cut['afterOriginalParagraph']
    following=parent['lines'][para]
    if id=='17':following=following.split('. ')[0]+'.'
    expected=parent['lines'][para-1]+' '+guide['text']+' '+following
    components=[];offset=0
    for label,data,source,sa,sb in [('original-before',left,cut['sourcePath'],a,z),('new-silence-before',silence,None,None,None),
        ('new-guide',gpcm,guide['path'],0,len(gpcm)//2),('new-silence-after',silence,None,None,None),('original-after',right,cut['sourcePath'],z,b)]:
        components.append(dict(role=label,sourcePath=source,sourceStartSample=sa,sourceEndSample=sb,
            startSample=offset,endSample=offset+len(data)//2,pcmSha256=hashlib.sha256(data).hexdigest()))
        offset+=len(data)//2
    assert len(joined)/48000<30
    rows.append(dict(id=id+'-complete-join',scene=id,parentScene=cut['scene'],sourcePath=rel(out),sourceSha256=sha(out),
        startSample=0,endSample=len(joined)//2,startSeconds=0,endSeconds=len(joined)/48000,expectedKo=expected,
        sourceComponents=components,allNonSilentSourceBytesMatched=True,addedSilenceSeconds=.24,
        reason='Complete original paragraph/sentence → whole new guide → complete next original paragraph/sentence, exact PCM with120ms new separator on each side.'))
audit=dict(schemaVersion=1,slug='familiar-game-rules',preparedAt=now(),originalSceneCount=11,originalParagraphCount=46,
    originalSpeechSeconds=296.72,originalSixWhiteSeconds=147.2,originalOverviewSeconds=24.32,
    originalScriptKoSha256=sha(BASE.parent/'script/narration.ko.json'),originalScriptEnSha256=sha(BASE.parent/'script/narration.en.json'),
    cuts=cuts,originalFragments=fragments,preservation=preservation,allOriginalPcmBytesRecombinedExactly=True,
    originalSamplesDiscarded=0,originalSamplesRepeated=0,newGuides=8,sourceAudioUsed=False,
    newGuidePcmSeconds=sum(x['seconds'] for x in new),newSeparatorSeconds=1.92,
    finalTimelineAdopted=False,finalRatioApproved=False,finalWordActionAlignment=False,finalMixedAsrApproved=False,
    allFinalCaptionPixelsReviewed=False,humanWholeListening='pending',pronunciation='pending',newGitImages=0)
save(BASE/'byte-exact-original-guide-insertion-audit-v1.json',audit)
plan=dict(schemaVersion=1,slug='familiar-game-rules',createdAt=now(),contextCount=8,contexts=rows,
    wholeReview=rel(BASE/'observation-guides-whole-direct-review-v1.json'),wholeReviewSha256=sha(BASE/'observation-guides-whole-direct-review-v1.json'),
    independentReview=rel(BASE/'observation-guides-independent-direct-review-v1.json'),independentReviewSha256=sha(BASE/'observation-guides-independent-direct-review-v1.json'),
    insertionAudit=rel(BASE/'byte-exact-original-guide-insertion-audit-v1.json'),insertionAuditSha256=sha(BASE/'byte-exact-original-guide-insertion-audit-v1.json'),
    expectedWasRecognizerPrompt=False,allContextsCompleteSentences=True,finalTimelineAdopted=False)
save(BASE/'guide-join-context-plan-v1.json',plan)
print(json.dumps(dict(originalFragments=len(fragments),originalPcmRecombined=True,joinContexts=8,
    joinSeconds=[round(x['endSeconds'],4) for x in rows],finalTimelineAdopted=False)))
