"""Use completed audio/word timestamps to record individual examples early.
This partial plan makes no claim about global timing, total duration or ratio.
"""
from pathlib import Path
import json,re,difflib,hashlib,math
import soundfile as sf,numpy as np
ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'projects/blank-project-coding';WORK=BASE/'production/final-v1';WORK.mkdir(exist_ok=True)
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
m=read(BASE/'project.json');out=ROOT/m['tts']['outputDir'];script=read(ROOT/m['paths']['script']);board={s['id']:s for s in read(BASE/'planning/storyboard.json')['scenes']}
finished_logs='\n'.join(p.read_text(encoding='utf-8',errors='replace') for p in (BASE/'production').glob('voice-actual-*.log'))
def norm(t):
    t=re.sub('[^a-z0-9가-힣]','',t.lower().replace('ai','에이아이').replace('node','노드'))
    for a,b in [('사십이','42'),('이십일','21'),('삼십','30'),('이십','20'),('십오','15'),('십칠','17'),('십','10')]:t=t.replace(a,b)
    return t
scenes=[];paragraphs=[];pending=[]
for s in script['scenes']:
    sid=s['id'];wav=out/'chunks'/f'{sid}-scene.wav';asrp=out/'asr'/f'{sid}.json'
    if board[sid]['classification']=='explanation':continue
    if f'Rendered {sid}-scene' not in finished_logs:pending.append(sid);continue
    if not wav.exists() or not asrp.exists():pending.append(sid);continue
    a=read(asrp);digest=hashlib.sha256(wav.read_bytes()).hexdigest()
    if digest!=a['audio_sha256']:pending.append(sid);continue
    pcm,rate=sf.read(wav);duration=len(pcm)/rate;frames=math.ceil(duration*60-1e-7)+43;expected=norm(''.join(s['lines']));recognized='';times=[]
    for w in a['words']:
        x,y=w['timestamp'];x=float(x if x is not None else (times[-1] if times else 0));y=float(y if y is not None else duration);chars=norm(w['text'])
        for i,c in enumerate(chars):recognized+=c;times.append(x+(y-x)*i/max(1,len(chars)))
    match=difflib.SequenceMatcher(None,expected,recognized,autojunk=False)
    if match.ratio()<.95:pending.append(sid);continue
    mapping={b.a+j:b.b+j for b in match.get_matching_blocks() for j in range(b.size)}
    keys=sorted(mapping)
    def time_at(i):
        if i not in mapping:
            return times[int(round(float(np.interp(i,keys,[mapping[k] for k in keys]))))]
        return times[mapping[i]]
    offset=0
    for i,line in enumerate(s['lines']):paragraphs.append({'scene':sid,'paragraph':i+1,'start':time_at(offset),'ko':line});offset+=len(norm(line))
    scenes.append({'id':sid,'title':s['title'],'classification':'actual','audioSha256':digest,'voiceSeconds':duration,'frames':frames,'seconds':frames/60,'start':0,'scope':'isolated-scene-timing-only','asrWordSimilarity':match.ratio()})
p={'scope':'isolated capture timing; not global edit or ratio','scenes':scenes,'paragraphs':paragraphs,'cuts':[],'pending':pending}
(WORK/'capture-available-plan.json').write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'available':[s['id'] for s in scenes],'pending':pending}))
