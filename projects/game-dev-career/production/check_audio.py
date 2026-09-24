"""Read-only layer, bilingual timing and pronunciation-review checks."""
import json, math, re
from pathlib import Path
import numpy as np
import soundfile as sf
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
cfg=json.loads((BASE.parent/'project.json').read_text(encoding='utf-8'))
mc=ROOT/'motion-canvas/src/projects/game-dev-career'
timing=json.loads((mc/'timing.generated.json').read_text(encoding='utf-8'))
suffix='-v'+str(cfg['production']['revision']) if cfg['production'].get('revision',1)>1 else ''
background,sr=sf.read(BASE/('audio'+suffix)/'background.wav',dtype='float32')
narration,nr=sf.read(mc/'assets/narration.wav',dtype='float32')
mix,mr=sf.read(ROOT/cfg['paths']['editorAudioMix'],dtype='float32')
assert sr==mr==48000 and nr==24000
def db(x):return float(20*np.log10(max(1e-8,np.sqrt(np.mean(x*x)))))
rows=[]
for s in timing['scenes']:
    start=s['firstFrame']/60;example=cfg['editing'].get('exampleSecondsByScene',{}).get(s['id'],cfg['editing']['exampleSeconds'])
    def sample(w,rate,a,b):return db(w[round((start+a)*rate):round((start+b)*rate)])
    row={'scene':s['id'],'exampleBackgroundDbfs':sample(background,sr,1,example-1),'explanationBackgroundDbfs':sample(background,sr,example+1,s['duration']-1),'narrationDbfs':sample(narration,nr,.25,s['duration']-.7)}
    assert min(row[k] for k in row if k!='scene')>-70
    rows.append(row)
ko=(ROOT/cfg['paths']['captionsKo']).read_text(encoding='utf-8');en=(ROOT/cfg['paths']['captionsEn']).read_text(encoding='utf-8')
rx=r'^\d\d:\d\d:\d\d,\d{3} --> \d\d:\d\d:\d\d,\d{3}$'
assert re.findall(rx,ko,re.M)==re.findall(rx,en,re.M)
assert len(re.findall(rx,ko,re.M))==len(timing['captions'])
for a,b in zip(timing['captions'],timing['captions'][1:]):assert a['start']<a['end']<=b['start']
report={'duration':len(mix)/mr,'sameDurationAsVideo':abs(len(mix)/mr-timing['duration'])<.0001,'koEnIdenticalTimings':True,'captionCount':len(timing['captions']),'sceneLayers':rows,'humanListeningApproval':False}
(BASE/f'audio-layer-check{suffix}.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
