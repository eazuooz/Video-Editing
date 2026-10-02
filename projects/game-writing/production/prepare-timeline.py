"""Assemble approved scene PCM, preserve explanations, add actual observations."""
from pathlib import Path
import json,hashlib,math,re,difflib,shutil
import numpy as np,soundfile as sf
ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'projects/game-writing';WORK=BASE/'production/final-v1';WORK.mkdir(exist_ok=True)
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
m=read(BASE/'project.json');approval=read(BASE/'production/voice-approval.json')
assert approval['allCurrentScenesTechnicallyReviewed'] and len(approval['scenes'])==16
if not (WORK/'base-manifest.json').exists():write(WORK/'base-manifest.json',m)
base=read(WORK/'base-manifest.json')
scripts={lang:read(ROOT/base['paths']['script' if lang=='ko' else 'scriptEn']) for lang in ['ko','en']}
added={lang:read(BASE/f'script/observations.{lang}.json') for lang in ['ko','en']}
order=['01','13','02','03','04','05','14','06','07','15','08','09','16','10','11','12']
out=ROOT/'shared/output/narration/game-writing/qwen3-preserved-final-v1';(out/'chunks').mkdir(parents=True,exist_ok=True);(out/'asr').mkdir(exist_ok=True)
final={lang:{'title':scripts[lang]['title'],'authorship':'Independent channel script with concept-matched narrated insertions; original twelve scene explanations retained.','scenes':[]} for lang in ['ko','en']}
for lang in ['ko','en']:
    catalog={s['id']:s for s in scripts[lang]['scenes']+added[lang]['scenes']};final[lang]['scenes']=[catalog[sid] for sid in order];write(BASE/f'script/final-v1.{lang}.json',final[lang])
scenes=[];approved={s['id']:s for s in approval['scenes']}
for sid in order:
    a=approved[sid];source=ROOT/a['wav'];digest=hashlib.sha256(source.read_bytes()).hexdigest();assert digest==a['audioSha256']
    pcm,rate=sf.read(source,dtype='int16');assert rate==24000 and pcm.ndim==1
    dest=out/'chunks'/f'{sid}-scene.wav';shutil.copy2(source,dest);assert hashlib.sha256(dest.read_bytes()).hexdigest()==digest
    asr=read(ROOT/a['approvedAsr']);shutil.copy2(ROOT/a['approvedAsr'],out/'asr'/f'{sid}.json')
    script=next(s for s in final['ko']['scenes'] if s['id']==sid)
    scenes.append({'id':sid,'classification':script['classification'],'title':script['title'],'voiceSeconds':len(pcm)/rate,'voiceFrames':math.ceil(len(pcm)/rate*60-1e-7),'frames':math.ceil(len(pcm)/rate*60-1e-7)+43,'voice':dest.relative_to(ROOT).as_posix(),'audioSha256':digest,'asr':(out/'asr'/f'{sid}.json').relative_to(ROOT).as_posix(),'baseRetained':int(sid)<=12})
A=sum(s['frames'] for s in scenes if s['classification']=='actual');P0=sum(s['frames'] for s in scenes if s['classification']=='explanation');P=round(A/1.5);assert P>=P0, 'Add meaningful narrated actual footage; never cut existing explanations.'
extra=P-P0;explanations=[s for s in scenes if s['classification']=='explanation']
for i,s in enumerate(explanations):s['explanationReadFramesAdded']=extra//6+(i<extra%6);s['frames']+=s['explanationReadFramesAdded']
position=120;pieces=[];entries=[];units=[];paragraphs=[]
def norm(t):return re.sub('[^a-z0-9가-힣]','',t.lower()).replace('신2','신투')
def sentences(t):return [v.strip() for v in re.findall(r'.+?(?:[.!?](?=\s|$)|$)',t) if v.strip()]
def split_balanced(t,n):
    words=t.split();assert len(words)>=n
    result=[];left=words[:]
    for i in range(n-1):
        goal=len(' '.join(left))/(n-i);candidates=[(abs(len(' '.join(left[:j]))-goal),j) for j in range(1,len(left)-(n-i-1)+1)];_,j=min(candidates);result.append(' '.join(left[:j]));left=left[j:]
    return result+[' '.join(left)]
for scene in scenes:
    sid=scene['id'];scene['startFrame']=position;scene['start']=position/60;scene['seconds']=scene['frames']/60
    pcm,rate=sf.read(ROOT/scene['voice'],dtype='int16');pad=scene['frames']*400-len(pcm);assert pad>=0;pieces.append(np.concatenate([pcm,np.zeros(pad,dtype=np.int16)]));position+=scene['frames']
    ko=next(s['lines'] for s in final['ko']['scenes'] if s['id']==sid);en=next(s['lines'] for s in final['en']['scenes'] if s['id']==sid);assert len(ko)==len(en)
    words=read(ROOT/scene['asr'])['words'];expected=norm(''.join(ko));recognized='';times=[]
    for wi,w in enumerate(words):
        a,b=w['timestamp'];a=float(a if a is not None else (times[-1][1] if times else 0));b=float(b if b is not None else next((v['timestamp'][0] for v in words[wi+1:] if v['timestamp'][0] is not None),scene['voiceSeconds']));b=min(max(a,b),scene['voiceSeconds']);chars=norm(w['text'])
        for j,ch in enumerate(chars):recognized+=ch;times.append((a+(b-a)*j/max(len(chars),1),a+(b-a)*(j+1)/max(len(chars),1)))
    match=difflib.SequenceMatcher(None,expected,recognized,autojunk=False);assert match.ratio()>.93,(sid,match.ratio())
    mapping={block.a+j:block.b+j for block in match.get_matching_blocks() for j in range(block.size)}
    def mapped(i):
        if i in mapping:return mapping[i]
        k=min(mapping,key=lambda k:abs(k-i));return max(0,min(len(times)-1,mapping[k]+i-k))
    char_pos=0;scene_rows=[]
    for pi,(k,e) in enumerate(zip(ko,en)):
        ksent=sentences(k);esent=sentences(e)
        if len(ksent)!=len(esent):ksent=[k];esent=[e]
        pairs=[]
        for ks,es in zip(ksent,esent):
            n=max(math.ceil(len(ks)/62),math.ceil(len(es)/150));n=max(1,n)
            pairs+=list(zip(split_balanced(ks,n) if n>1 else [ks],split_balanced(es,n) if n>1 else [es]))
        pa=times[mapped(char_pos)][0]
        for kc,ec in pairs:
            n=len(norm(kc));a=times[mapped(char_pos)][0];b=times[mapped(char_pos+n-1)][1];char_pos+=n
            row={'scene':sid,'paragraph':pi+1,'start':scene['start']+a,'end':min(scene['start']+b+.07,scene['start']+scene['voiceSeconds']),'ko':kc,'en':ec};scene_rows.append(row);units.append([sid,pi+1,kc,ec])
        paragraphs.append({'scene':sid,'paragraph':pi+1,'start':scene['start']+pa,'end':scene_rows[-1]['end'],'ko':k,'en':e})
    assert char_pos==len(expected)
    for i,c in enumerate(scene_rows):
        if i<len(scene_rows)-1:c['end']=min(c['end'],scene_rows[i+1]['start']-.015)
        assert c['end']>c['start']
    entries+=scene_rows;scene['wordMatch']=match.ratio()
bodyFrames=position-120;totalFrames=position+600
plan={'revision':'final-v1','fps':60,'introFrames':120,'introSeconds':2,'outroFrames':600,'bodyFrames':bodyFrames,'bodySeconds':bodyFrames/60,'bodyEnd':position/60,'seconds':totalFrames/60,'totalFrames':totalFrames,'actualFrames':A,'explanationFrames':P,'gameplaySeconds':A/60,'explanationSeconds':P/60,'gameplayShare':A/bodyFrames,'ratioErrorFrames':abs(A-.6*bodyFrames),'retainedExplanationMinimumFrames':P0,'additionalExplanationReadFrames':extra,'scenes':scenes,'paragraphs':paragraphs,'cuts':[],'humanListening':'pending','sourceRights':'pending'}
assert plan['ratioErrorFrames']<=1
write(WORK/'plan.json',plan);write(WORK/'caption-alignment.json',{'entries':entries,'cues':len(entries),'kind':'current-hash reviewed Whisper words matched to original Korean; faithful original English preserved','humanListening':'pending'})
write(BASE/'script/caption-units.json',units)
bodyWav=out/'game-writing-preserved-final-v1.wav';sf.write(bodyWav,np.concatenate(pieces),24000,subtype='PCM_16');assert len(np.concatenate(pieces))==bodyFrames*400
def stamp(t):
    n=round(t*1000);return f'{n//3600000:02}:{n//60000%60:02}:{n//1000%60:02},{n%1000:03}'
def wrap_en(t):return '\n'.join(split_balanced(t,2)) if len(t)>80 else t
for lang in ['ko','en']:
    (WORK/f'captions.{lang}.srt').write_text('\n\n'.join(f'{i+1}\n{stamp(c["start"])} --> {stamp(c["end"])}\n{wrap_en(c[lang]) if lang=="en" else c[lang]}' for i,c in enumerate(entries))+'\n',encoding='utf-8')
m['paths'].update({'script':'projects/game-writing/script/final-v1.ko.json','scriptEn':'projects/game-writing/script/final-v1.en.json','narration':bodyWav.relative_to(ROOT).as_posix(),'captionsKo':'projects/game-writing/production/final-v1/captions.ko.srt','captionsEn':'projects/game-writing/production/final-v1/captions.en.srt','editorAudioMix':'motion-canvas/src/projects/game-writing/assets/final-mix.wav'})
m['tts'].update({'outputDir':out.relative_to(ROOT).as_posix(),'filenameStem':'game-writing-preserved-final-v1','editorialAssembly':'projects/game-writing/production/prepare-timeline.py'})
m['editing'].update({'actualGameplaySeconds':plan['gameplaySeconds'],'actualExplanationSeconds':plan['explanationSeconds'],'actualGameplayShare':plan['gameplayShare'],'timingStatus':'current-reviewed-voice-measured; actual-cuts-and-final-render-pending','scenePlan':'projects/game-writing/production/final-v1/plan.json'})
m['status']='measured-awaiting-actual-cuts-and-final-render';m['video']['durationSeconds']=plan['seconds'];write(BASE/'project.json',m)
print(json.dumps({'seconds':plan['seconds'],'actual':plan['gameplaySeconds'],'explanation':plan['explanationSeconds'],'cues':len(entries),'ratioErrorFrames':plan['ratioErrorFrames'],'baseExplanationNotCut':True},ensure_ascii=False))
