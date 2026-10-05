"""Expose raw read-back differences; never auto-approve narration meaning."""
from pathlib import Path
import sys,json,hashlib,difflib,importlib.util
import soundfile as sf
R=Path(__file__).resolve().parents[3];slug=sys.argv[1]
m=json.loads((R/f'projects/{slug}/project.json').read_text(encoding='utf8'));script=json.loads((R/m['paths']['script']).read_text(encoding='utf8'));out=R/m['tts']['outputDir']
spec=importlib.util.spec_from_file_location('math_align',Path(__file__).parent/'align.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
for s in script['scenes']:
 p=out/'asr'/f'{s["id"]}.json';wav=out/'chunks'/f'{s["id"]}-scene.wav'
 if not p.exists() or not wav.exists():continue
 raw=json.loads(p.read_text(encoding='utf8'));digest=hashlib.sha256(wav.read_bytes()).hexdigest()
 if digest!=raw['audio_sha256']:print(s['id'],'STALE ASR');continue
 audio,sr=sf.read(wav);expected=' '.join(s['lines']);recognized=raw['text']
 try:_,_,coverage=a.a.align_characters(expected,raw['words'],len(audio)/sr);gate=round(coverage,5)
 except ValueError as e:gate=str(e)
 x,y=a.normalized(expected),a.normalized(recognized);matcher=difflib.SequenceMatcher(None,x,y,autojunk=False)
 changes=[{'expected':x[i:j],'recognized':y[k:l]} for tag,i,j,k,l in matcher.get_opcodes() if tag!='equal']
 print(json.dumps({'scene':s['id'],'coverageGate':gate,'rawRecognized':recognized,'normalizedDifferences':changes},ensure_ascii=False))
