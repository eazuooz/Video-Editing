"""Preserve only explicit generated current files before a selected repair."""
from pathlib import Path
import json,hashlib,sys
P=Path(__file__).resolve().parents[1];L=(P/'production/local').resolve();name=sys.argv[1]
assert name=='v1-before-minus-and-peak-fix'
H=(L/'history'/name).resolve();assert H.is_relative_to(L) and not H.exists()
names=['audio-build.json','visual-build.json','pair-build.json','portrait-visual.mp4',P.name+'.clean.mp4',P.name+'.captioned.mp4','retained-voice-24k.wav','voice-input-stereo.wav','narration-stem.wav','music-input.wav','music-stem.wav','mix-before-peak-protection.wav','final-mix.wav','final-mix.m4a','visual-render.log','encoded-audio-16k.wav','final-mix-asr.json','ending-context.wav','ending-context-asr.json','qa']
records=[]
for n in names:
 s=(L/n).resolve();d=(H/n).resolve();assert s.is_relative_to(L) and d.is_relative_to(H) and s.exists(),n
 records.append(dict(original=str(s),archived=str(d),kind='directory' if s.is_dir() else 'file',sha256=hashlib.sha256(s.read_bytes()).hexdigest() if s.is_file() else None))
H.mkdir(parents=True)
for r in records:Path(r['original']).rename(Path(r['archived']))
(H/'archive-map.json').write_text(json.dumps(dict(reason='Fix missing minus glyph and reduce excessive source-to-stem peak attenuation; original source and approved raw narration remain untouched',files=records),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Preserved',len(records),'explicit generated files/directories under',H)
