"""Draft current-voice timeline and bilingual cues; actual cuts and every cue remain unapproved. No audio/MC/manifest mutation."""
from pathlib import Path
import json,hashlib,math,re,difflib
import numpy as np,soundfile as sf
ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'projects/hierarchical-game-outlines';WORK=BASE/'production/final-v1'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def norm(t):return re.sub('[^a-z0-9가-힣]','',t.lower())
def sentences(t):return [v.strip() for v in re.findall(r'.+?(?:[.!?](?=\s|$)|$)',t) if v.strip()]
def split_balanced(t,n):
    words=t.split();assert len(words)>=n;result=[];left=words[:]
    for i in range(n-1):
        goal=len(' '.join(left))/(n-i);_,j=min((abs(len(' '.join(left[:j]))-goal),j) for j in range(1,len(left)-(n-i-1)+1));result.append(' '.join(left[:j]));left=left[j:]
    return result+[' '.join(left)]
m=read(BASE/'project.json');approval=read(BASE/'production/voice-approval-v2.json');assert approval['allCurrentScenesTechnicallyReviewed'] and len(approval['scenes'])==12
assert approval['all60ParagraphsDirectlyCompared'] and approval['unchangedPcmVerified'],'Current full composite and retained PCM review required.'
scripts={lang:read(BASE/f'script/narration.{lang}.json') for lang in ['ko','en']};approved={s['scene']:s for s in approval['scenes']};scenes=[];chunks=[]
for s in scripts['ko']['scenes']:
    sid=s['id'];a=approved[sid];wav=ROOT/a['audio'];assert sha(wav)==a['audio_sha256'];pcm,rate=sf.read(wav,dtype='int16');assert rate==24000 and pcm.ndim==1
    asr=read(ROOT/a['asr']);assert asr['audio_sha256']==sha(wav)
    scene={'id':sid,'title':s['title'],'classification':'explanation' if int(sid)%2==0 else 'actual','voiceSeconds':len(pcm)/rate,'voiceFrames':math.ceil(len(pcm)/400),'frames':math.ceil(len(pcm)/400)+43,'voice':a['audio'],'audioSha256':a['audio_sha256'],'asr':a['asr'],'originalExplanationPcmPreserved':int(sid)%2==0};scenes.append(scene);chunks.append(pcm)
P0=sum(s['frames'] for s in scenes if s['classification']=='explanation');A0=sum(s['frames'] for s in scenes if s['classification']=='actual');P=max(P0,math.ceil(A0/1.5));A=round(P*1.5)
extraP=P-P0;explanations=[s for s in scenes if s['classification']=='explanation']
for i,s in enumerate(explanations):s['explanationReadFramesAdded']=extraP//6+(i<extraP%6);s['frames']+=s['explanationReadFramesAdded']
extra=A-A0;assert extra>=0
observationIds=['01','03','05','07','09','11'];context={c['id']:c for c in read(BASE/'planning/action-map.json')['chapters']}
for i,sid in enumerate(observationIds):
    s=next(s for s in scenes if s['id']==sid);n=extra//len(observationIds)+(i<extra%len(observationIds));s['frames']+=n;s['observationFramesAdded']=n;s['observationPurpose']=context[sid]['focus'];s['observationPolicy']='New normal-speed action continues under the last instruction to inspect it; no replay, freeze or unrelated waiting.'
position=120;pieces=[];entries=[];paragraphs=[];units=[]
for scene,pcm in zip(scenes,chunks):
    sid=scene['id'];scene.update(startFrame=position,start=position/60,seconds=scene['frames']/60);position+=scene['frames'];pieces.append(np.concatenate([pcm,np.zeros(scene['frames']*400-len(pcm),dtype=np.int16)]))
    ko=next(s['lines'] for s in scripts['ko']['scenes'] if s['id']==sid);en=next(s['lines'] for s in scripts['en']['scenes'] if s['id']==sid);assert len(ko)==len(en)
    words=read(ROOT/scene['asr'])['words'];excluded=next((v for v in approval.get('timestampAlignmentExclusions',[]) if v['scene']==sid),None);words=words[:excluded['fromWordIndex']] if excluded else words;expected=norm(''.join(ko));recognized='';times=[]
    for wi,w in enumerate(words):
        a,b=w['timestamp'];a=float(a if a is not None else (times[-1][1] if times else 0));b=float(b if b is not None else next((v['timestamp'][0] for v in words[wi+1:] if v['timestamp'][0] is not None),scene['voiceSeconds']));b=min(max(a,b),scene['voiceSeconds']);chars=norm(w['text'])
        for j,ch in enumerate(chars):recognized+=ch;times.append((a+(b-a)*j/max(len(chars),1),a+(b-a)*(j+1)/max(len(chars),1)))
    match=difflib.SequenceMatcher(None,expected,recognized,autojunk=False);assert match.ratio()>.94,(sid,match.ratio());mapping={block.a+j:block.b+j for block in match.get_matching_blocks() for j in range(block.size)}
    def mapped(i):
        if i in mapping:return mapping[i]
        k=min(mapping,key=lambda k:abs(k-i));return max(0,min(len(times)-1,mapping[k]+i-k))
    char_pos=0;rows=[];local=[]
    for pi,(k,e) in enumerate(zip(ko,en)):
        ksent=sentences(k);esent=sentences(e)
        if len(ksent)!=len(esent):ksent=[k];esent=[e]
        pairs=[]
        for ks,es in zip(ksent,esent):
            n=max(1,math.ceil(len(ks)/(36 if scene['classification']=='actual' else 62)),math.ceil(len(es)/150));pairs+=list(zip(split_balanced(ks,n) if n>1 else [ks],split_balanced(es,n) if n>1 else [es]))
        pa=times[mapped(char_pos)][0]
        for kc,ec in pairs:
            n=len(norm(kc));a=times[mapped(char_pos)][0];b=times[mapped(char_pos+n-1)][1];char_pos+=n
            row={'scene':sid,'paragraph':pi+1,'start':scene['start']+a,'end':min(scene['start']+b+.07,scene['start']+scene['voiceSeconds']),'ko':kc,'en':ec};rows.append(row);units.append([sid,pi+1,kc,ec])
        paragraphs.append({'scene':sid,'paragraph':pi+1,'start':scene['start']+pa,'end':rows[-1]['end'],'localStart':pa,'localEnd':rows[-1]['end']-scene['start'],'ko':k,'en':e});local.append({'paragraph':pi+1,'start':pa,'end':rows[-1]['end']-scene['start']})
    assert char_pos==len(expected)
    # A sparse full ASR can anticipate speech at splice joins. The exact
    # candidate PCM start is a hard lower bound, independent of ASR spelling.
    splice=next(p for p in read(BASE/'production/repair1/v2-composite-proof.json')['scenes'] if p['scene']==sid)
    edits=read(BASE/'production/repair1/request.json')['edits']
    for replacement in splice.get('replacements',[]):
        pi=next(e['paragraph'] for e in edits if e['id']==replacement['candidateId'])
        first=next(c for c in rows if c['paragraph']==pi)
        first['start']=max(first['start'],scene['start']+replacement['compositeFromSample']/24000)
    for i,c in enumerate(rows):
        if i<len(rows)-1 and c['end']>=rows[i+1]['start']:
            boundary=(c['end']+rows[i+1]['start'])/2
            c['end']=boundary-.008;rows[i+1]['start']=boundary+.008
        assert c['end']>c['start']
    local=[]
    for pi in range(1,len(ko)+1):
        group=[r for r in rows if r['paragraph']==pi]
        local.append({'paragraph':pi,'start':group[0]['start']-scene['start'],'end':group[-1]['end']-scene['start']})
        paragraph=next(r for r in paragraphs if r['scene']==sid and r['paragraph']==pi)
        paragraph.update(start=group[0]['start'],end=group[-1]['end'],localStart=local[-1]['start'],localEnd=local[-1]['end'])
    entries+=rows;scene['paragraphs']=local;scene['wordMatch']=match.ratio()
bodyFrames=position-120;totalFrames=position+600
plan={'revision':'final-v1','fps':60,'introFrames':120,'introSeconds':2,'outroFrames':600,'bodyFrames':bodyFrames,'bodySeconds':bodyFrames/60,'bodyEnd':position/60,'seconds':totalFrames/60,'totalFrames':totalFrames,'actualFrames':A,'explanationFrames':P,'gameplaySeconds':A/60,'explanationSeconds':P/60,'gameplayShare':A/bodyFrames,'ratioErrorFrames':abs(A-.6*bodyFrames),'retainedExplanationMinimumFrames':P0,'additionalExplanationReadFrames':extraP,'additionalMeaningfulActionObservationFrames':extra,'scenes':scenes,'paragraphs':paragraphs,'cuts':[],'sourcePlan':'projects/hierarchical-game-outlines/planning/action-map.json','timingStatus':'draft-measured-voice-and-provisional-footage-targets; not final60:40 evidence','captionReviewComplete':False,'actualFootageMeasuredAndApproved':False,'humanListening':'pending','sourceRights':'pending','finalSourceTimingApproved':False};assert plan['ratioErrorFrames']<=1
assert not (WORK/'plan.json').exists(),'Inspect existing draft rather than overwrite it'
write(WORK/'plan.json',plan);write(WORK/'caption-alignment.json',{'entries':entries,'cues':len(entries),'kind':'Current-hash directly reviewed ASR words matched to exact Korean; bilingual cues share timing.','humanListening':'pending'});write(BASE/'script/caption-units.json',units)
def stamp(t):
    n=round(t*1000);return f'{n//3600000:02}:{n//60000%60:02}:{n//1000%60:02},{n%1000:03}'
for lang in ['ko','en']:
    (WORK/f'captions.{lang}.srt').write_text('\n\n'.join(f'{i+1}\n{stamp(c["start"])} --> {stamp(c["end"])}\n'+('\n'.join(split_balanced(c[lang],2)) if lang=='en' and len(c[lang])>80 else c[lang]) for i,c in enumerate(entries))+'\n',encoding='utf-8')
print(json.dumps({'seconds':plan['seconds'],'actual':plan['gameplaySeconds'],'explanation':plan['explanationSeconds'],'cues':len(entries),'ratioErrorFrames':plan['ratioErrorFrames'],'explanationNotCut':True},ensure_ascii=False))
