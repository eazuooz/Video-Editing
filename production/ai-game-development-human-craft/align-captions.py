"""Reuse the single complete narration ASR for scene-local caption alignment.

No inference runs here. A missing/stale complete transcript is an error.
The canonical script is unchanged; aliases affect matching only.
"""
from pathlib import Path
import sys, json, hashlib, re, difflib
import soundfile as sf
ROOT=Path(__file__).resolve().parents[2]
SLUG='ai-game-development-human-craft'
sys.path.insert(0,str(ROOT/'qwen3-tts'))
import align_project_subtitles as aligner

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))

m=read(ROOT/f'projects/{SLUG}/project.json')
out=ROOT/m['tts']['outputDir'];stem=m['tts']['filenameStem']
wav=out/(stem+'.wav');source=out/(stem+'.asr-review.timestamps.json')
asr=read(source)
assert asr['audio_sha256']==sha(wav),'Complete ASR is stale'
assert asr['timestampMode']=='word'
timing=read(out/(stem+'.timing.json'))
script=read(ROOT/m['paths']['script'])
cache=out/'asr';cache.mkdir(exist_ok=True)
review=[];assigned=set()
for scene in script['scenes']:
    sid=scene['id'];chunk=out/'chunks'/f'{sid}-scene.wav'
    info=sf.info(chunk);duration=info.duration
    origin=next(e['start'] for e in timing['entries'] if e['scene_id']==sid)
    words=[]
    for i,w in enumerate(asr['chunks']):
        a,b=w['timestamp']
        assert a is not None and b is not None, f'Inspect incomplete ASR timestamp {i}'
        if origin<=(a+b)/2<origin+duration:
            words.append({'text':w['text'],'timestamp':[max(0,a-origin),min(duration,b-origin)]})
            assigned.add(i)
    assert words, sid
    record={'scene':sid,'audio_sha256':sha(chunk),'text':''.join(w['text'] for w in words),
            'words':words,'provenance':'partitioned-from-one-complete-narration-ASR',
            'completeAsrSha256':sha(source),'origin':origin,'duration':duration}
    (cache/f'{sid}.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    review.append({'scene':sid,'expected':' '.join(scene['lines']),'recognized':record['text'],
                   'origin':origin,'duration':duration})
unassigned=[dict(index=i,**w) for i,w in enumerate(asr['chunks']) if i not in assigned]
(out/'complete-asr-scene-review.json').write_text(json.dumps({'scenes':review,'gapWords':unassigned},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert not unassigned,'ASR words occur outside scene audio; review gapWords before aligning'

aliases={'wild ox studios':'와일드옥스스튜디오','unity spark':'유니티스파크','ue6':'언리얼엔진식스',
         'mcp':'엠씨피','uv':'유브이','udk':'유디케이','nft':'엔에프티','verse':'벌스',
         'api':'에이피아이','ai':'에이아이'}
def normalized(text):
    text=text.lower()
    for a,b in aliases.items(): text=text.replace(a,b)
    return re.sub(r'[^가-힣a-z0-9]','',text)
aligner.normalized=normalized
for r in review:
    a,b=normalized(r['expected']),normalized(r['recognized'])
    matcher=difflib.SequenceMatcher(None,a,b,autojunk=False)
    r['differences']=[{'expected':a[i:j],'recognized':b[k:l]} for tag,i,j,k,l in matcher.get_opcodes() if tag!='equal']
(out/'complete-asr-scene-review.json').write_text(json.dumps({'scenes':review,'gapWords':unassigned},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if '--cache-only' in sys.argv:
    print('Cached complete scene read-back for direct text review; no alignment or inference performed.')
    raise SystemExit(0)
sys.argv=['align_project_subtitles.py','--project',SLUG]
aligner.main()
print('Aligned cached words. Complete text and pronunciation still require review.')
