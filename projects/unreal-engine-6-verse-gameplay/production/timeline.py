"""Align editorial bilingual clauses to actual speech, then put all assets on a single clock."""
from pathlib import Path
import json, re, hashlib, math, difflib, textwrap
import numpy as np
import soundfile as sf
from PIL import ImageFont
from edition import BASE, EXTENDED, LOCAL, SCRIPT, voice_dir, sealed_voice_batch
P=Path(__file__).resolve().parents[1]
R=P.parents[1]
L=LOCAL
pairs=[[(lambda parts:(parts[0].strip(),parts[1].strip()))(line.split(' | ')) for line in block.splitlines()] for block in (SCRIPT/'caption-pairs.txt').read_text(encoding='utf-8').strip().split('\n\n')]
scenes=json.loads((SCRIPT/'narration.ko.json').read_text(encoding='utf-8'))['scenes']
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',48)
def normalized(text):
    text=re.sub(r'\s+','',text.lower())
    aliases={'씨플러스플러스':'cpp','c++':'cpp','씨뿔뿔':'cpp','얼리얼':'언리얼','언리얼엔진식스':'언리얼엔진6','엔진식스':'엔진6','엔진파이브':'엔진5','버전식스':'버전6','유이에프엔':'uefn','유이애프엔':'uefn','유엔프엔':'uefn','유이엔에프':'uefn','버스':'verse','벌스':'verse','엠씨피':'mcp','엠시피':'mcp','에이아이':'ai','오점구':'5점9','5.9':'5점9','5.구':'5점9','한배반':'1점5배','1.5배':'1점5배','네배':'4배','이천이십육년':'2026년','이천이십칠년':'2027년','십일월':'11월','삼일':'3일','유월':'6월','백개':'100개','폰':'pawn','액터':'actor','엑터':'actor','프리팹':'prefab','프리펩':'prefab'}
    if EXTENDED:
        # Normalize readings only while aligning. Both visible language files keep
        # their authored names, currency and thousands separators.
        aliases.update({'지디스크립트':'gdscript','gd스크립트':'gdscript','엠아이티':'mit',
            '씨샵':'csharp','시샵':'csharp','c#':'csharp','피씨':'pc','피시':'pc',
            '십이개월':'12개월','백이십만':'120만','이십만':'20만','백만':'100만',
            '이천삼백십':'2310','사천육백이십':'4620','오퍼센트':'5퍼센트','5%':'5퍼센트',
            '일만달러':'1만달러','영원':'0원','영달러':'0달러','일년':'1년'})
    for a,b in aliases.items():text=text.replace(a,b)
    return re.sub(r'[^가-힣a-z0-9]','',text)
def stamp(s,ass=False):
    b=100 if ass else 1000
    h,m=divmod(round(s*b),3600*b);m,ss=divmod(m,60*b);ss,f=divmod(ss,b)
    return f'{h}:{m:02}:{ss:02}.{f:02}' if ass else f'{h:02}:{m:02}:{ss:02},{f:03}'
def wrap(text):
    if font.getlength(text)<=1530:return text
    w=text.split()
    j=min(range(1,len(w)),key=lambda i:abs(font.getlength(' '.join(w[:i]))-font.getlength(' '.join(w[i:]))))
    lines=[' '.join(w[:j]),' '.join(w[j:])];assert max(map(font.getlength,lines))<=1570
    return '\n'.join(lines)
def save(path,value):
    temporary=path.with_name(path.name+'.tmp')
    temporary.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    temporary.replace(path)
def align(cues,asr,duration):
    tokens=[normalized(t) for t,_ in cues]
    ref=''.join(tokens)
    hyp='';beg=[];end=[]
    for w in asr['words']:
        z=normalized(w['text']);a,b=w['timestamp']
        if not z:continue
        a=max(0,a if a is not None else (end[-1] if end else 0));b=min(duration,b if b is not None else duration)
        hyp+=z;edge=np.linspace(a,max(a,b),len(z)+1);beg.extend(edge[:-1]);end.extend(edge[1:])
    blocks=difflib.SequenceMatcher(None,ref,hyp,autojunk=False).get_matching_blocks()
    ii=[];aa=[];bb=[]
    for block in blocks:
        for j in range(block.size):ii.append(block.a+j);aa.append(beg[block.b+j]);bb.append(end[block.b+j])
    coverage=len(ii)/len(ref)
    if coverage<.84:raise ValueError(f'Speech deviates from script: {coverage:.1%}, {asr["text"]}')
    begin=np.maximum.accumulate(np.interp(np.arange(len(ref)),ii,aa))
    finish=np.maximum.accumulate(np.interp(np.arange(len(ref)),ii,bb))
    begin[1:]=np.maximum(begin[1:],finish[:-1])
    cuts=[];cursor=0
    for text,en in cues:
        n=len(normalized(text));cuts.append(dict(start=round(float(begin[cursor]),3),end=round(float(finish[cursor+n-1]),3),text=text,en=en));cursor+=n
    if cuts[0]['start']>0.60:cuts[0]['start']=0.08
    return cuts,round(coverage,4)
def build():
    rows=[];captions=[];all_ready=True;origin=0.;previous_end=0.
    assert len(scenes)==len(pairs)
    if EXTENDED:
        baseline=json.loads((BASE/'timeline.json').read_text(encoding='utf-8'))
        assert [s['id'] for s in scenes]==[str(i) for i in range(13,18)]
        assert len(baseline['scenes'])==12 and baseline['bodyFrames']==17724
        rows=baseline['scenes'].copy()
        captions=json.loads((BASE/'cue-review.json').read_text(encoding='utf-8'))
        origin=baseline['bodyFrames']/60
        previous_end=captions[-1]['end']
    L.mkdir(parents=True,exist_ok=True)
    for i,(scene,segments) in enumerate(zip(scenes,pairs)):
        sid=scene['id'];assert ' '.join(x for x,_ in segments)==scene['lines'][0],sid
        V=voice_dir(sid)
        lead=.28 if EXTENDED and i==0 else 0.
        p=V/'chunks'/f'{sid}-scene.wav';q=V/'asr'/f'{sid}.json'
        if not(p.exists() and q.exists()):
            all_ready=False;break
        info=sf.info(p);duration=info.frames/info.samplerate
        asr=json.loads(q.read_text(encoding='utf-8'))
        if asr['audio_sha256']!=hashlib.sha256(p.read_bytes()).hexdigest():
            all_ready=False;break
        cues,coverage=align(segments,asr,duration);sentences=[];clause=[]
        for c in cues:
            c['start']=round(c['start']+lead,3);c['end']=round(c['end']+lead,3)
        for c in cues:
            clause.append(c)
            if c['text'].endswith(('.','?','!')):
                sentences.append(dict(start=clause[0]['start'],end=c['end'],text=' '.join(q['text'] for q in clause)));clause=[]
            global_start=round(2+origin+c['start'],3);global_end=round(2+origin+c['end'],3)
            global_start=max(previous_end,global_start);assert global_end>global_start,(sid,c)
            captions.append(dict(start=global_start,end=global_end,ko=wrap(c['text']),en='\n'.join(textwrap.wrap(c['en'],54)),scene=sid))
            previous_end=global_end
        assert not clause
        next_origin=origin+lead+duration+(.28 if i<len(scenes)-1 else 0)
        f0=round(origin*60);f1=math.ceil(next_origin*60) if i==len(scenes)-1 else round(next_origin*60)
        rows.append(dict(id=sid,title=scene['title'],startFrame=f0,frames=f1-f0,voiceStart=origin+lead,duration=duration,sentences=sentences,clauses=cues,coverage=coverage))
        origin=next_origin
    if not rows:return
    frames=rows[-1]['startFrame']+rows[-1]['frames']
    plan=dict(fps=60,width=1920,height=1080,bodyFrames=frames,totalFrames=frames+720,scenes=rows)
    if EXTENDED:
        plan['edition']='engine-comparison-v2'
        plan['baseBodyFrames']=baseline['bodyFrames']
        plan['extraBodyFrames']=frames-baseline['bodyFrames']
        assert rows[:12]==baseline['scenes']
    if all_ready:
        seal=sealed_voice_batch(voice_dir(scenes[0]['id']),'comparison' if EXTENDED else 'narration',[s['id'] for s in scenes])
        if not seal:
            raise RuntimeError('Final Qwen join, actual take lengths and ASR fingerprints must match before publishing a final timeline.')
        plan['sealedPrimaryTakes']=seal
    if not all_ready:
        save(L/'partial-timeline.json',plan)
        print('Preview scenes ready:',len(rows));return
    for lang in ['ko','en']:
        (L/f'captions.{lang}.srt').write_text('\n\n'.join(f'{i}\n{stamp(c["start"])} --> {stamp(c["end"])}\n{c[lang]}' for i,c in enumerate(captions,1))+'\n',encoding='utf-8')
    header=(R/'projects/game-reward-planning/production/local/reference-preserving-v2/edit/captions.ko.ass').read_text(encoding='utf-8').split('[Events]')[0]
    lines=[header+'[Events]','Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text']
    for c in captions:
        label=c['ko'];parts=label.splitlines();w=math.ceil(max(map(font.getlength,parts)))+44;h=len(parts)*62+22
        x=960-w//2;y=970-h//2
        assert y>=892 and y+h+14<=1060
        start,end=stamp(c['start'],True),stamp(c['end'],True)
        for layer,offset,fill,border in [(0,14,'323C07',0),(1,0,'FFFFFF',3)]:
            lines.append(f'Dialogue: {layer},{start},{end},Default,,0,0,0,,{{\\an7\\pos({x+offset},{y+offset})\\p1\\bord{border}\\shad0\\1c&H{fill}&\\3c&H181B16&}}m 0 0 l {w} 0 {w} {h} 0 {h}')
        for key in ['게임플레이 프레임워크','씬 그래프','블루프린트','얼리 액세스','엔티티','Verse','1.5배','2027년','UEFN','C++','0달러','4,620달러','1만 달러','GDScript','MIT 라이선스','C#','2,310달러']:
            if key in label:
                label=label.replace(key,'{\\c&H666B0B&\\b1}'+key+'{\\c&H090B08&\\b0}',1);break
        lines.append(f'Dialogue: 2,{start},{end},Default,,0,0,0,,{{\\an5\\pos(960,970)\\bord0\\shad0}}'+label.replace('\n',r'\N'))
    (L/'captions.ko.ass').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    save(L/'cue-review.json',captions)
    save(L/'timeline.json',plan)
    print('Final timeline:',frames,'body frames,',len(captions),'bilingual cues')
if __name__=='__main__':build()
