"""Candidate paragraph timing from sealed current ASR/contexts and exact PCM.
All original samples remain. This does not approve the unrepaired04 name,
final timeline, visual-content roles, listening, captions or the body ratio.
"""
from pathlib import Path
from datetime import datetime,timezone
import array,difflib,hashlib,json,math,re,wave
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
DEST=BASE/'current-original-paragraph-timing-v1.json';assert not DEST.exists(),'Read the existing measurement.'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def norm(s):return ''.join(re.findall(r'[a-zA-Z0-9가-힣]',s)).lower()
ko=read(ROOT/'projects/similar-game-design/script/narration.ko.json')
whole=read(BASE/'current-whole-asr-v1/asr.json');contexts=read(BASE/'current-contexts-asr-v1/asr.json')
review=read(BASE/'current-contexts-asr-direct-review-v1.json');assert review['allCompleteContextsTextCompared']
plan=read(BASE/'current-independent-context-plan-v1.json')
roles=[['explanation']*3,['actual','actual','explanation','explanation'],['actual','actual','explanation','explanation'],
 ['actual','actual','explanation','actual'],['actual','actual','explanation','explanation'],['actual']*4,
 ['actual','actual','explanation','explanation'],['actual','actual','explanation','explanation'],
 ['actual','actual','actual','explanation'],['actual','actual','explanation','explanation'],
 ['explanation','explanation','actual','explanation'],['explanation','actual','actual','explanation'],
 ['actual','explanation','explanation','explanation']]
def mapped_gap(lines,words,after):
    expected=''.join(norm(x) for x in lines);actual='';indices=[]
    for i,w in enumerate(words):token=norm(w['text']);actual+=token;indices.extend([i]*len(token))
    pos=sum(len(norm(x)) for x in lines[:after])-1
    block=next((m for m in difflib.SequenceMatcher(None,expected,actual,autojunk=False).get_matching_blocks() if m.a<=pos<m.a+m.size),None)
    assert block,'Unmapped complete boundary'
    i=indices[block.b+pos-block.a];assert i+1<len(words)
    return words[i],words[i+1]
rows=[]
for scene,asr,sroles in zip(ko['scenes'],whole['results'],roles):
    assert scene['id']==asr['id'] and scene['lines']==asr['expectedKo']
    source=ROOT/asr['sourcePath'];assert sha(source)==asr['sourceSha256']
    with wave.open(str(source),'rb') as w:
        rate=w.getframerate();samples=w.getnframes();pcm=array.array('h',w.readframes(samples))
    sealed=next(x for x in plan['boundaries'] if x['sceneId']==scene['id'])
    tail=next(x for x in contexts['results'] if x['id']==scene['id']+'-complete-tail')
    cuts=[0];boundaries=[]
    for after in range(1,len(scene['lines'])):
        if after==sealed['afterParagraph']:
            cut=sealed['selectedSplitSample'];energy=sealed['selectedNormalizedRms'];prev,nxt=sealed['previousWord'],sealed['nextWord'];offset=0
            method='sealed direct complete-context PCM boundary'
        else:
            if after>sealed['afterParagraph']:
                localafter=after-sealed['afterParagraph'];prev,nxt=mapped_gap(tail['expectedKo'],tail['words'],localafter);offset=tail['startSample']
                method='complete independent tail words + quiet PCM gap'
            else:
                # Ignore long-chunk backtracking tail repetitions when measuring p1/p2.
                words=[x for x in asr['words'] if x['timestamp'][0] is not None and x['timestamp'][1] is not None and x['timestamp'][1]<=sealed['selectedSplitSeconds']]
                prev,nxt=mapped_gap(scene['lines'][:sealed['afterParagraph']],words,after);offset=0
                method='current complete head words + quiet PCM gap'
            a,b=prev['timestamp'][1],nxt['timestamp'][0];assert a is not None and b is not None and b>=a,(scene['id'],after,prev,nxt)
            lo,hi=round(a*rate)+offset,round(b*rate)+offset;options=[];span=240
            for center in range(lo+960,hi-960+1,60):
                window=pcm[center-span//2:center+span//2];energy=math.sqrt(sum(v*v for v in window)/span)/32768
                options.append((energy,abs(center-(lo+hi)/2),center))
            if options:energy,_,cut=min(options)
            else:cut=round((lo+hi)/2);window=pcm[cut-span//2:cut+span//2];energy=math.sqrt(sum(v*v for v in window)/span)/32768;method+=' (short-gap midpoint)'
        boundaries.append(dict(afterParagraph=after,previousWord=prev,nextWord=nxt,wordSourceOffsetSample=offset,
                               splitSample=cut,splitSeconds=cut/rate,normalizedRms=energy,method=method));cuts.append(cut)
    cuts.append(samples);assert all(a<b for a,b in zip(cuts,cuts[1:]))
    paras=[dict(paragraph=i+1,expectedKo=line,roleCandidate=sroles[i],sourceInSample=cuts[i],sourceOutSample=cuts[i+1],seconds=(cuts[i+1]-cuts[i])/rate) for i,line in enumerate(scene['lines'])]
    rows.append(dict(id=scene['id'],path=asr['sourcePath'],sha256=asr['sourceSha256'],sampleRate=rate,totalSamples=samples,seconds=samples/rate,boundaries=boundaries,paragraphs=paras,allOriginalSamplesRetained=True))
totals={r:sum(p['seconds'] for s in rows for p in s['paragraphs'] if p['roleCandidate']==r) for r in ['actual','explanation']}
record=dict(schemaVersion=1,recordedAt=datetime.now(timezone.utc).isoformat(),slug='similar-game-design',scenes=rows,
 koSha256=sha(ROOT/'projects/similar-game-design/script/narration.ko.json'),wholeAsrSha256=sha(BASE/'current-whole-asr-v1/asr.json'),contextAsrSha256=sha(BASE/'current-contexts-asr-v1/asr.json'),
 preservedOriginalSeconds=sum(x['seconds'] for x in rows),provisionalPcmRoleSeconds=totals,directBoundaryTextReview=False,
 continuousSelectedActionReview=False,localized04CandidateApplied=False,currentOriginalVoiceTextIntegrityApproved=False,
 finalTimelineApproved=False,bodyRatioApproved=False,humanListening='pending',humanPronunciation='pending')
DEST.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(scenes=[dict(id=x['id'],boundaries=x['boundaries']) for x in rows],provisional=totals),ensure_ascii=False))
