"""Wait for this project's synthesis, then ASR-align/master/render a review copy.
Does not mark the episode complete, publish it, or fabricate a missing outro.
"""
from pathlib import Path
import json
import os
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[3]
PROJECT=ROOT/'projects/renderformer-explained'
progress=ROOT/'shared/output/narration/renderformer-explained/qwen3-1.7b-balanced-v1/production-progress.json'
lock=PROJECT/'production/finish-body.lock'

def main():
    with lock.open('x',encoding='utf-8') as f:f.write(str(os.getpid()))
    try:
        while True:
            state=json.loads(progress.read_text(encoding='utf-8')) if progress.exists() else {}
            if state.get('status')=='failed':raise RuntimeError(state.get('error'))
            if state.get('status')=='synthesis-complete-awaiting-asr':break
            print(f"Waiting: {state.get('completedPages',0)}/88 full-page voice files",flush=True)
            time.sleep(30)
        while True:
            free=int(subprocess.check_output(['nvidia-smi','--query-gpu=memory.free','--format=csv,noheader,nounits'],text=True).splitlines()[0])
            if free>6500:break
            time.sleep(15)
        subprocess.run([sys.executable,'-X','utf8','-u',str(PROJECT/'production/prepare_full.py')],cwd=ROOT,check=True)
        subprocess.run(['node','motion-canvas/scripts/render-renderformer-body.cjs'],cwd=ROOT,check=True)
        print('Body review rendered. English, listening checks and original-image outro remain.',flush=True)
    finally:lock.unlink(missing_ok=True)

if __name__=='__main__':main()
