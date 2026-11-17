"""Finish current voice alignment/ASR independently of the pending furniture files."""
from pathlib import Path
import json,hashlib,subprocess
H=Path(__file__).resolve().parent;R=H.parents[2];P=H.parent;L=H/'local/full-video-v5';PY=R/'qwen3-tts/.venv/Scripts/python.exe'
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def run(args):subprocess.run(list(map(str,args)),cwd=R,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
assert (L/'narration/ai-3d-lofi-gaming-room.timing.json').exists()
run([PY,'-X','utf8','-u',H/'build-film-audio.py'])
Q=L/'qa';Q.mkdir(exist_ok=True)
for key,source in [('narration',L/'narration-aligned.wav'),('mix',L/'final-mix.m4a')]:
 out=Q/(key+'.txt');record=out.with_suffix('.timestamps.json')
 if not record.exists() or json.loads(record.read_text('utf-8'))['audio_sha256']!=sha(source):run([PY,'-X','utf8','-u',R/'qwen3-tts/transcribe_reference.py',source,'--output',out,'--device','cuda','--timestamps','word'])
run([PY,'-X','utf8','-u',H/'build-film-captions.py'])
print('Current v5 narration, mix ASR and both caption timings prepared',flush=True)
