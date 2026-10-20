"""One whole-PCM ASR of the finished scene batch, then script-aligned KO/EN cues.
Takes the GPU lease only after the owned TTS batch has finished."""
from pathlib import Path
import json, subprocess, sys, time, uuid, psutil
R = Path(__file__).resolve().parents[3]; P = R / 'projects/steam-next-fest-ai-flood'; L = P / 'production/local/edit'
LEASE = R / 'shared/output/GPU_HANDOFF.json'; receipt = L / 'tts-gpu-coordination.json'; out = L / 'voice-review-execution.json'
PY = R / 'qwen3-tts/.venv/Scripts/python.exe'
def read(p): return json.loads(p.read_text(encoding='utf8'))
def save(status, **more): out.write_text(json.dumps({'status': status, 'at': time.time(), **more}, indent=2) + '\n')
state = read(receipt)
assert state['state'] == 'finished', state['state']
assert not LEASE.exists(), 'Preserve foreign GPU lease'
free = int(subprocess.check_output(['nvidia-smi', '--query-gpu=memory.free', '--format=csv,noheader,nounits'], text=True).splitlines()[0]); assert free >= 5000, free
me = psutil.Process(); token = str(uuid.uuid4())
with LEASE.open('x', encoding='utf8') as f: json.dump({'token': token, 'project': P.name, 'state': 'asr_running', 'coordinator': {'pid': me.pid, 'createTime': me.create_time()}, 'foreignProcessesPaused': []}, f)
code = 1
try:
    save('whole-current-PCM-ASR-running', device='cuda')
    with (L / 'whole-voice-asr.log').open('w', encoding='utf8') as log:
        code = subprocess.call([str(PY), '-u', '-X', 'utf8', 'qwen3-tts/review_project_narration.py', '--project', P.name, '--device', 'cuda'], cwd=R, stdout=log, stderr=subprocess.STDOUT)
finally:
    if LEASE.exists() and read(LEASE).get('token') == token: LEASE.unlink()
if code == 0:
    L.mkdir(parents=True, exist_ok=True)
    with (L / 'align.log').open('w', encoding='utf8') as log:
        code = subprocess.call([str(PY), '-X', 'utf8', 'qwen3-tts/align_project_subtitles.py', '--project', P.name], cwd=R, stdout=log, stderr=subprocess.STDOUT)
save('ASR-and-alignment-ready-for-direct-full-text-review' if code == 0 else 'ASR-or-alignment-failed', exitCode=code)
sys.exit(code)
