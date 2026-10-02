"""Assemble current, technically reviewed scene audio and bilingual word-aligned cues."""
from pathlib import Path
import json,hashlib,math,re,difflib
import numpy as np,soundfile as sf
ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'projects/blank-project-coding';WORK=BASE/'production/final-v1';WORK.mkdir(exist_ok=True)
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
m=read(BASE/'project.json');out=ROOT/m['tts']['outputDir'];approval=read(BASE/'production/voice-approval.json')
assert approval['allCurrentScenesTechnicallyReviewed'] and len(approval['scenes'])==34
scripts={lang:read(ROOT/m['paths']['script' if lang=='ko' else 'scriptEn']) for lang in ['ko','en']}
board={s['id']:s for s in read(BASE/'planning/storyboard.json')['scenes']}
approved={s['id']:s for s in approval['scenes']};scenes=[]
for script in scripts['ko']['scenes']:
    sid=script['id'];wav=out/'chunks'/f'{sid}-scene.wav';digest=hashlib.sha256(wav.read_bytes()).hexdigest();assert digest==approved[sid]['audioSha256']
    pcm,rate=sf.read(wav,dtype='int16');assert rate==24000 and pcm.ndim==1
    asr=read(out/'asr'/f'{sid}.json');assert asr['audio_sha256']==digest
    scenes.append({'id':sid,'classification':'explanation' if board[sid]['classification']=='explanation' else 'actual','actionClassification':board[sid]['classification'],'title':script['title'],'voiceSeconds':len(pcm)/rate,'voiceFrames':math.ceil(len(pcm)/rate*60-1e-7),'frames':math.ceil(len(pcm)/rate*60-1e-7)+43,'voice':wav.relative_to(ROOT).as_posix(),'audioSha256':digest,'asr':(out/'asr'/f'{sid}.json').relative_to(ROOT).as_posix()})
A=sum(s['frames'] for s in scenes if s['classification']!='explanation');P0=sum(s['frames'] for s in scenes if s['classification']=='explanation');P=round(A/1.5)
assert P>=P0,'Add related narrated actual content; preserve explanation duration.'
extra=P-P0;expl=[s for s in scenes if s['classification']=='explanation']
for i,s in enumerate(expl):s['explanationReadFramesAdded']=extra//len(expl)+(i<extra%len(expl));s['frames']+=s['explanationReadFramesAdded']
def norm(t):
    t=re.sub('[^a-z0-9가-힣]','',t.lower().replace('ai','에이아이').replace('api','에이피아이').replace('node','노드'))
    for a,b in [('사십이','42'),('이십일','21'),('삼십','30'),('이십','20'),('십오','15'),('십칠','17'),('십','10')]:t=t.replace(a,b)
    return t
def sentences(t):return [v.strip() for v in re.findall(r'.+?(?:[.!?](?=\s|$)|$)',t) if v.strip()]
def split_balanced(t,n):
    left=t.split();n=min(n,len(left));result=[]
    for i in range(n-1):
        goal=len(' '.join(left))/(n-i);_,j=min((abs(len(' '.join(left[:j]))-goal),j) for j in range(1,len(left)-(n-i-1)+1));result.append(' '.join(left[:j]));left=left[j:]
    return result+[' '.join(left)]
position=120;pieces=[];entries=[];paragraphs=[]
for scene in scenes:
    sid=scene['id'];scene.update(startFrame=position,start=position/60,seconds=scene['frames']/60);position+=scene['frames']
    pcm,rate=sf.read(ROOT/scene['voice'],dtype='int16');pad=scene['frames']*400-len(pcm);assert pad>=0;pieces.append(np.concatenate([pcm,np.zeros(pad,dtype=np.int16)]))
    ko=next(s['lines'] for s in scripts['ko']['scenes'] if s['id']==sid);en=next(s['lines'] for s in scripts['en']['scenes'] if s['id']==sid);assert len(ko)==len(en)
    words=read(ROOT/scene['asr'])['words'];expected=norm(''.join(ko));recognized='';times=[]
    for wi,w in enumerate(words):
        a,b=w['timestamp'];a=float(a if a is not None else (times[-1][1] if times else 0));b=float(b if b is not None else next((v['timestamp'][0] for v in words[wi+1:] if v['timestamp'][0] is not None),scene['voiceSeconds']));b=min(max(a,b),scene['voiceSeconds']);chars=norm(w['text'])
        for j,ch in enumerate(chars):recognized+=ch;times.append((a+(b-a)*j/max(len(chars),1),a+(b-a)*(j+1)/max(len(chars),1)))
    match=difflib.SequenceMatcher(None,expected,recognized,autojunk=False);assert match.ratio()>.93,(sid,match.ratio())
    mapping={block.a+j:block.b+j for block in match.get_matching_blocks() for j in range(block.size)}
    mapkeys=sorted(mapping)
    def mapped(i):
        if i in mapping:return mapping[i]
        return int(round(float(np.interp(i,mapkeys,[mapping[k] for k in mapkeys]))))
    char_pos=0;scene_rows=[]
    for pi,(k,e) in enumerate(zip(ko,en)):
        ksent=sentences(k);esent=sentences(e)
        if len(ksent)!=len(esent):ksent=[k];esent=[e]
        pairs=[]
        for ks,es in zip(ksent,esent):
            n=min(max(math.ceil(len(ks)/32),math.ceil(len(es)/110),1),len(ks.split()),len(es.split()));pairs+=list(zip(split_balanced(ks,n),split_balanced(es,n)))
        pa=times[mapped(char_pos)][0]
        for kc,ec in pairs:
            n=len(norm(kc));a=times[mapped(char_pos)][0];b=times[mapped(char_pos+n-1)][1];char_pos+=n
            display=kc.replace('에이아이','AI').replace('링크드 리스트','Linked List').replace('레코그니션','Recognition').replace('리콜','Recall')
            row={'scene':sid,'paragraph':pi+1,'start':scene['start']+a,'end':min(scene['start']+b+.07,scene['start']+scene['voiceSeconds']),'ko':display,'en':ec};scene_rows.append(row)
        paragraphs.append({'scene':sid,'paragraph':pi+1,'start':scene['start']+pa,'end':scene_rows[-1]['end'],'ko':k,'en':e})
    assert char_pos==len(expected)
    for i,c in enumerate(scene_rows):
        if i<len(scene_rows)-1:c['end']=min(c['end'],scene_rows[i+1]['start']-.015)
        assert c['end']>c['start'],(sid,c)
    entries+=scene_rows;scene['wordMatch']=match.ratio()
bodyFrames=position-120;totalFrames=position+600
plan={'revision':'final-v1','fps':60,'introFrames':120,'introSeconds':2,'outroFrames':600,'bodyFrames':bodyFrames,'bodySeconds':bodyFrames/60,'bodyEnd':position/60,'seconds':totalFrames/60,'totalFrames':totalFrames,'actualFrames':A,'explanationFrames':P,'gameplaySeconds':A/60,'explanationSeconds':P/60,'gameplayShare':A/bodyFrames,'ratioErrorFrames':abs(A-.6*bodyFrames),'retainedExplanationMinimumFrames':P0,'additionalExplanationReadFrames':extra,'scenes':scenes,'paragraphs':paragraphs,'cuts':[],'humanListening':'pending','sourceRights':'owned-examples; original-library-music-verification-pending'}
assert plan['ratioErrorFrames']<=1
write(WORK/'plan.json',plan);write(WORK/'caption-alignment.json',{'entries':entries,'cues':len(entries),'kind':'Current-hash Whisper words aligned to original Korean and faithful English paragraphs','humanListening':'pending'})
bodyWav=out/'blank-project-coding-final-body.wav';sf.write(bodyWav,np.concatenate(pieces),24000,subtype='PCM_16');assert len(np.concatenate(pieces))==bodyFrames*400
def stamp(t):
    n=round(t*1000);return f'{n//3600000:02}:{n//60000%60:02}:{n//1000%60:02},{n%1000:03}'
for lang in ['ko','en']:
    (WORK/f'captions.{lang}.srt').write_text('\n\n'.join(f'{i+1}\n{stamp(c["start"])} --> {stamp(c["end"])}\n'+ ('\n'.join(split_balanced(c[lang],2)) if lang=='en' and len(c[lang])>80 else c[lang]) for i,c in enumerate(entries))+'\n',encoding='utf-8')
m['paths'].update(narration=bodyWav.relative_to(ROOT).as_posix(),captionsKo='projects/blank-project-coding/production/final-v1/captions.ko.srt',captionsEn='projects/blank-project-coding/production/final-v1/captions.en.srt')
m['editing'].update(actualGameplaySeconds=plan['gameplaySeconds'],actualExplanationSeconds=plan['explanationSeconds'],actualGameplayShare=plan['gameplayShare'],actualCommercialGameplaySeconds=0,actualDevelopmentFootageSeconds=plan['gameplaySeconds'],timingStatus='reviewed-voice-measured; final-actual-capture-and-render-pending',scenePlan='projects/blank-project-coding/production/final-v1/plan.json')
m['video']['durationSeconds']=plan['seconds'];write(BASE/'project.json',m)
print(json.dumps({'seconds':plan['seconds'],'actual':plan['gameplaySeconds'],'explanation':plan['explanationSeconds'],'cues':len(entries),'ratioErrorFrames':plan['ratioErrorFrames']},ensure_ascii=False))
