"""Capture six approved native clips serially. Resume completed hash-pinned cuts."""
from pathlib import Path
import json, subprocess, sys, hashlib
H=Path(__file__).resolve().parent;L=H.parents[1]/'local/fighters-v4-kula-lili/unreal'
for cid in ['A02-E005','A02-E004','A02-E011','A02-E013','A02-E014','A02-E015']:
    record=L/f'{cid}-capture.json';movie=L/f'{cid}.mp4'
    if record.is_file() and movie.is_file():
        with movie.open('rb') as f:s=hashlib.file_digest(f,'sha256').hexdigest()
        if s==json.loads(record.read_text())['movieSha256']:continue
    subprocess.run([sys.executable,'-u','-X','utf8',str(H/'render_unreal.py'),cid],check=True)
    subprocess.run([sys.executable,'-u','-X','utf8',str(H/'compose.py'),cid],check=True)
