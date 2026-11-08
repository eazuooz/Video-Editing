"""Render finalized takes on CPU while the next authorized paragraph synthesizes."""
from pathlib import Path
import time,subprocess,json
from build_audio import timeline
P=Path(__file__).resolve().parents[1];L=P/'production/local'
for i in range(1,31):
 key=f'{i:02}';nextfile=L/'narration/chunks'/f'{i+1:02}-scene.wav'
 complete=L/'narration/ai-2d-game-assets.timing.json'
 while not (nextfile.exists() or complete.exists()):time.sleep(5)
 t=timeline(False)
 assert any(r['id']==key for r in t['scenes'])
 result=subprocess.run(['node',str(P/'production/render-scenes.cjs'),'render',key],cwd=P.parents[1],creationflags=subprocess.CREATE_NO_WINDOW)
 if result.returncode:raise SystemExit(result.returncode)
 print('Finished visual',key,flush=True)
print('All30visuals complete',flush=True)
