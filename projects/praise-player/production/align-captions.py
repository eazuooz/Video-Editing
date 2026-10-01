"""Align original bilingual short cues to reviewed per-scene Whisper words."""
from pathlib import Path
import json,re,difflib
ROOT=Path(__file__).resolve().parents[3]
BASE=Path(__file__).parent.parent;WORK=Path(__file__).parent/'final-v1'
m=json.loads((BASE/'project.json').read_text(encoding='utf-8'))
script=json.loads((ROOT/m['paths']['script']).read_text(encoding='utf-8'))
units=json.loads((BASE/'script/caption-units.json').read_text(encoding='utf-8'))
out=ROOT/m['tts']['outputDir'];timing=json.loads((out/(m['tts']['filenameStem']+'.timing.json')).read_text(encoding='utf-8'))
plan=json.loads((WORK/'plan.json').read_text(encoding='utf-8'))
norm=lambda s:re.sub('[^a-z0-9가-힣]','',s.lower())
captions=[];evidence=[]
for scene in script['scenes']:
    sid=scene['id'];expected=norm(''.join(scene['lines']));shorts=units[sid]
    assert norm(''.join(v[0] for v in shorts))==expected, f'Subtitle text changed in {sid}'
    words=json.loads((out/'asr'/f'{sid}.json').read_text(encoding='utf-8'))['words']
    recognized='';char_times=[]
    for word in words:
        text=norm(word['text']);a,b=word['timestamp'];a=float(a or 0);b=float(b or a)
        for j,char in enumerate(text):recognized+=char;char_times.append((a+(b-a)*j/max(len(text),1),a+(b-a)*(j+1)/max(len(text),1)))
    match=difflib.SequenceMatcher(None,expected,recognized,autojunk=False);mapping={}
    for block in match.get_matching_blocks():
        for j in range(block.size):mapping[block.a+j]=block.b+j
    assert match.ratio()>.93,(sid,match.ratio())
    def mapped(index):
        if index in mapping:return mapping[index]
        near=min(mapping,key=lambda k:abs(k-index));return max(0,min(len(char_times)-1,mapping[near]+index-near))
    start=next(e['start'] for e in timing['entries'] if e['scene_id']==sid)+plan['introSeconds'];pos=0
    row=[]
    for ko,en in shorts:
        n=len(norm(ko));a=char_times[mapped(pos)][0];b=char_times[mapped(pos+n-1)][1];pos+=n
        row.append({'scene':sid,'start':start+a,'end':start+b+.07,'ko':ko,'en':en})
    for i,c in enumerate(row):
        if i<len(row)-1:c['end']=min(c['end'],row[i+1]['start']-.015)
        assert c['end']>c['start'],(sid,i,c)
    captions+=row;evidence.append({'scene':sid,'wordMatch':match.ratio(),'cues':len(row),'timing':'measured words with matched original characters'})
for i,c in enumerate(captions):
    if i:c['start']=max(c['start'],captions[i-1]['end'])
    assert c['end']>c['start'] and c['end']<=plan['bodyEnd']+.03,c
def stamp(t):
    n=round(t*1000);return f'{n//3600000:02}:{n//60000%60:02}:{n//1000%60:02},{n%1000:03}'
def english_wrap(text):
    if len(text)<=68:return text
    words=text.split();pairs=[(' '.join(words[:i]),' '.join(words[i:])) for i in range(1,len(words))]
    a,b=min(pairs,key=lambda p:abs(len(p[0])-len(p[1])))
    return a+'\n'+b
for lang in ['ko','en']:
    file=WORK/f'captions.{lang}.srt'
    file.write_text('\n\n'.join(f'{i+1}\n{stamp(c["start"])} --> {stamp(c["end"])}\n{english_wrap(c[lang]) if lang=="en" else c[lang]}' for i,c in enumerate(captions))+'\n',encoding='utf-8')
(WORK/'caption-alignment.json').write_text(json.dumps({'kind':'word-aligned bilingual captions','cues':len(captions),'scenes':evidence,'entries':captions},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'{len(captions)} KO/EN cues; identical timing, all original spoken text preserved.')
