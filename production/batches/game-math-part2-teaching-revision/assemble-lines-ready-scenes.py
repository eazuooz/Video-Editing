"""Expose only stable, acoustically passing complete scenes for concurrent CPU ASR.

Uses the exact final renderer assembly method. No synthesis/GPU use, original
audio changes, relaxed gates or approval. Final provenance is still sealed by
the guarded renderer after all lines pass, and ASR remains current-hash evidence.
"""
from pathlib import Path
import sys,json,hashlib,time,os
import numpy as np,soundfile as sf
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
slug='game-math-lines-bounds-teaching-additions-v2'
sys.path.insert(0,str(ROOT/'qwen3-tts'));import render_narration as r
r.np=np;r.sf=sf;r.configure_project(slug)
scenes=json.loads((ROOT/f'projects/{slug}/script/narration.ko.json').read_text(encoding='utf8'))['scenes']
seen={};completed=set();deadline=time.monotonic()+7200
while time.monotonic()<deadline:
 for scene in scenes:
  source=[r.CHUNK_DIR/f'{scene["id"]}-{i:02}.wav' for i in range(1,len(scene['lines'])+1)]
  if not all(p.exists() and p.stat().st_size>44 for p in source):continue
  signatures=[(p.stat().st_size,p.stat().st_mtime_ns) for p in source]
  if seen.get(scene['id'])!=signatures:seen[scene['id']]=signatures;continue
  pieces=[];passing=True
  try:
   for i,p in enumerate(source):
    a,sr=sf.read(p,dtype='float32');assert sr==24000 and a.ndim==1
    if not r._passes_quality(r._tail_ratio(a,sr),r._tail_decay_ms(a,sr)):passing=False;break
    pieces.append(r._apply_edge_fades(a,sr))
    if i+1<len(source):pieces.append(np.zeros(round(.28*sr),dtype='float32'))
  except (RuntimeError,AssertionError):continue
  if not passing:continue
  target=r.CHUNK_DIR/f'{scene["id"]}-scene.wav';temporary=r.CHUNK_DIR/f'{scene["id"]}-scene.ready.tmp.wav'
  sf.write(temporary,np.concatenate(pieces),24000)
  if not target.exists() or hashlib.sha256(target.read_bytes()).digest()!=hashlib.sha256(temporary.read_bytes()).digest():os.replace(temporary,target);print('Stable passing scene available for CPU ASR:',scene['id'],flush=True)
  else:temporary.unlink()
  completed.add(scene['id'])
 if len(completed)==len(scenes):break
 time.sleep(15)
assert len(completed)==len(scenes),'Ready-scene assembly timed out; preserve chunks and final GPU handoff'
print('All20 new-only passing scenes exposed; final guarded provenance and review still required.',flush=True)
