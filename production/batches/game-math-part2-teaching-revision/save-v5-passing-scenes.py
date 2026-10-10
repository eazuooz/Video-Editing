"""CPU checkpoint of four complete, gate-passing new scenes after V5 failed."""
from pathlib import Path
import json,sys,hashlib
import numpy as np,soundfile as sf
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
sys.path.insert(0,str(ROOT/'qwen3-tts'));import render_narration as r
r.np=np;r.sf=sf;r.configure_project('game-math-quaternion-teaching-additions-v5')
scenes=json.loads(r.SCRIPT_PATH.read_text(encoding='utf8'))['scenes'];saved=[];failed=[]
for scene in scenes:
 pieces=[];sources=[];passing=True
 for n,text in enumerate(scene['lines'],1):
  p=r.CHUNK_DIR/f'{scene["id"]}-{n:02}.wav';a,sr=sf.read(p,dtype='float32');assert sr==24000
  gate=r._passes_quality(r._tail_ratio(a,sr),r._tail_decay_ms(a,sr));passing&=gate
  sources.append({'text':text,'file':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'endingGatePassed':gate})
  pieces.append(r._apply_edge_fades(a,sr))
  if n<len(scene['lines']):pieces.append(np.zeros(round(.28*sr),dtype='float32'))
 if passing:
  target=r.CHUNK_DIR/f'{scene["id"]}-scene.wav';sf.write(target,np.concatenate(pieces),sr);saved.append({'scene':scene['id'],'lines':sources,'sceneSha256':hashlib.sha256(target.read_bytes()).hexdigest()})
 else:failed.append({'scene':scene['id'],'lines':sources,'sceneAssemblyApproved':False})
(B/'quaternion-v5-passing-scene-checkpoint.json').write_text(json.dumps({'saved':saved,'failed':failed,'originalAudioChanged':False,'currentHashAsrAndHumanListening':'pending'},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'savedScenes':[s['scene'] for s in saved],'failedScenes':[s['scene'] for s in failed]}))
