from pathlib import Path
import json,time,subprocess
R=Path(__file__).resolve().parents[3];B=Path(__file__).parent
for slug in json.loads((B/'batch.json').read_text(encoding='utf8'))['authorization']['slugs'][2:]:
 p=R/'projects'/slug;deadline=time.monotonic()+3600
 while not (p/'production/local/audio-v1/voice/narration.wav').exists():
  assert time.monotonic()<deadline;time.sleep(10)
 print('ASR_START',slug,flush=True)
 with (p/'production/local/asr-job.log').open('w',encoding='utf8') as log:
  subprocess.run([str(R/'qwen3-tts/.venv/Scripts/python.exe'),'-X','utf8',str(p/'production/transcribe.py'),'voice'],cwd=R,stdout=log,stderr=subprocess.STDOUT,check=True)
 print('ASR_DONE',slug,flush=True)
