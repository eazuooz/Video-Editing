"""Preserve current PCM; derive reviewable paragraph boundaries from full actual words.

This is a measurement plan, never final ratio, listening or render approval.
"""
from pathlib import Path
from datetime import datetime, timezone
import array, difflib, hashlib, json, math, re, wave
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
DEST=BASE/'current-original-paragraph-timing-v1.json'
assert not DEST.exists(),'Existing measured checkpoint; read it.'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def norm(s):return ''.join(re.findall(r'[a-zA-Z0-9가-힣]',s)).lower()
ko=read(ROOT/'projects/player-customization/script/narration.ko.json')
whole=read(BASE/'current-whole-asr-v1/asr.json')
review=read(BASE/'current-contexts-asr-direct-review-v1.json')
assert review['allCompleteContextsTextCompared'] and review['currentOriginalVoiceTextIntegrityApproved']
context=read(BASE/'current-independent-context-plan-v1.json')
# Visible-content roles, menus and cosmetic previews are explanation.
roles=[['explanation']*4,['actual','actual','explanation','explanation'],
 ['actual','actual','explanation','explanation'],['actual','actual','explanation','explanation'],
 ['explanation']*4,['actual','explanation','explanation','explanation'],
 ['explanation']*4,['explanation']*4]
rows=[]
for scene,asr,scene_roles in zip(ko['scenes'],whole['results'],roles):
    assert scene['id']==asr['id'] and scene['lines']==asr['expectedKo']
    source=ROOT/asr['sourcePath'];assert sha(source)==asr['sourceSha256']
    with wave.open(str(source),'rb') as w:
        rate=w.getframerate();samples=w.getnframes();pcm=array.array('h',w.readframes(samples))
    expected=''.join(norm(x) for x in scene['lines'])
    actual='';indices=[]
    for i,word in enumerate(asr['words']):
        token=norm(word['text']);actual+=token;indices.extend([i]*len(token))
    matches=difflib.SequenceMatcher(None,expected,actual,autojunk=False).get_matching_blocks()
    boundaries=[];split_samples=[0]
    for p in range(3):
        target_pos=sum(len(norm(x)) for x in scene['lines'][:p+1])-1
        block=next((m for m in matches if m.a<=target_pos<m.a+m.size),None)
        assert block, f'{scene["id"]} p{p+1} needs direct mapping'
        index=indices[block.b+target_pos-block.a]
        before=asr['words'][index];after=asr['words'][index+1]
        a=before['timestamp'][1];b=after['timestamp'][0]
        assert a is not None and b is not None
        if p==1:
            old=next(x for x in context['boundaries'] if x['sceneId']==scene['id'])
            split=old['selectedSplitSample'];energy=old['selectedNormalizedRms'];method='reviewed complete half-context boundary'
        else:
            assert b>=a, f'{scene["id"]} overlapping boundary words'
            lo=round(a*rate);hi=round(b*rate);span=round(.01*rate)
            options=[]
            for center in range(lo+round(.05*rate),hi-round(.05*rate)+1,60):
                values=pcm[center-span//2:center+span//2]
                options.append((math.sqrt(sum(v*v for v in values)/span)/32768,abs(center-(lo+hi)/2),center))
            if options:energy,_,split=min(options);method='quiet10ms PCM valley between matched full-ASR words'
            else:split=round((a+b)/2*rate);energy=None;method='word-gap midpoint; no10ms valley available'
        boundaries.append({'afterParagraph':p+1,'previousWord':before,'nextWord':after,
            'splitSample':split,'splitSeconds':split/rate,'normalizedRms':energy,'method':method})
        split_samples.append(split)
    split_samples.append(samples)
    assert all(a<b for a,b in zip(split_samples,split_samples[1:]))
    paragraphs=[{'paragraph':i+1,'expectedKo':line,'roleCandidate':scene_roles[i],
        'sourceInSample':split_samples[i],'sourceOutSample':split_samples[i+1],
        'startSeconds':split_samples[i]/rate,'seconds':(split_samples[i+1]-split_samples[i])/rate}
        for i,line in enumerate(scene['lines'])]
    rows.append({'id':scene['id'],'path':asr['sourcePath'],'sha256':asr['sourceSha256'],
        'sampleRate':rate,'totalSamples':samples,'seconds':samples/rate,
        'boundaries':boundaries,'paragraphs':paragraphs,'allOriginalSamplesRetained':True})
totals={r:sum(p['seconds'] for row in rows for p in row['paragraphs'] if p['roleCandidate']==r) for r in ['actual','explanation']}
plan={'schemaVersion':1,'recordedAt':datetime.now(timezone.utc).isoformat(),'slug':'player-customization',
 'koSha256':sha(ROOT/'projects/player-customization/script/narration.ko.json'),
 'wholeAsrSha256':sha(BASE/'current-whole-asr-v1/asr.json'),
 'contextReviewSha256':sha(BASE/'current-contexts-asr-direct-review-v1.json'),'scenes':rows,
 'provisionalPcmRoleSeconds':totals,'preservedOriginalSeconds':sum(row['seconds'] for row in rows),
 'directBoundaryTextReview':False,'continuousSelectedActionReview':False,
 'finalTimelineApproved':False,'bodyRatioApproved':False,'humanListening':'pending',
 'note':'PCM roles are proposed visible-content assignments only. Exact native cut timing, observation guides, source camera/caption review and final60:40 are pending. No original PCM shortened.'}
DEST.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps({'scenes':[{'id':row['id'],'seconds':row['seconds'],'boundaries':row['boundaries']} for row in rows],'provisional':totals},ensure_ascii=False))
