"""Wait for a foreign TTS lease to end; then request our normal job boundary.

Never remove another owner's controls, steal its GPU or bypass its guard.
The GPU handoff itself restores the original research command on every exit.
"""
from pathlib import Path
import time,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent;lease=ROOT/'shared/output/GPU_HANDOFF.json'
deadline=time.monotonic()+10800;last=None
while lease.exists():
 r=json.loads(lease.read_text(encoding='utf-8-sig'));key=(r.get('project'),r.get('state'))
 if key!=last:print('Preserving current GPU lease:',key,flush=True);last=key
 if time.monotonic()>deadline:raise TimeoutError('Foreign GPU lease still active; no controls changed')
 time.sleep(15)
command=['C:/Users/eazuo/anaconda3/envs/renderformer/python.exe','-u','-X','utf8',str(ROOT/'production/batches/game-math-part2-full-series/gpu-handoff.py'),'--project','game-math-lines-narration-retakes-v3','--queue-dir','C:/Users/eazuo/renderformer/tmp/placement_focus_20261008','--gpu-idle-timeout','600','--',str(ROOT/'qwen3-tts/.venv/Scripts/python.exe'),'-X','utf8',str(B/'render-lines-retakes-v3.py'),'--project','game-math-lines-narration-retakes-v3','--device','cuda:0','--batch-size','1']
print('Foreign lease ended; requesting normal research job boundary for three retakes.',flush=True)
raise SystemExit(subprocess.call(command,cwd=ROOT,creationflags=subprocess.CREATE_NO_WINDOW))
