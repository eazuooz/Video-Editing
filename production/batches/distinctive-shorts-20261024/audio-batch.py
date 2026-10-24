"""Finite CPU-only narration jobs. Stop at failed stage, preserve completed takes."""
from pathlib import Path
import subprocess,json,time,sys
R=Path(__file__).resolve().parents[3];B=Path(__file__).parent;L=B/'local';L.mkdir(exist_ok=True)
py=R/'qwen3-tts/.venv/Scripts/python.exe'; results=[]
for row in json.loads((B/'batch.json').read_text(encoding='utf8'))['projects']:
 slug=row['slug'];p=R/'projects'/slug;log=p/'production/local/voice-job.log'
 if (p/'production/local/audio-v1/voice/narration.wav').exists():continue
 print('VOICE_START',slug,flush=True)
 with log.open('w',encoding='utf8') as f:
  r=subprocess.run([str(py),'-X','utf8',str(p/'production/render-voice.py'),'--cpu'],cwd=R,stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
 results.append({'slug':slug,'exit':r.returncode,'finishedAt':time.time()});(L/'audio-batch-status.json').write_text(json.dumps(results,indent=2),encoding='utf8')
 print('VOICE_DONE',slug,r.returncode,flush=True)
print('BATCH_VOICE_FINISHED',flush=True)
