"""Update picture timing only when a new, hash-bound comparison readback is ready."""
import json
import os
import time
import hashlib
import subprocess
import sys
import psutil

os.environ['UE6_EDITION']='engine-comparison-v2'
from edition import LOCAL, PROJECT, sealed_voice_batch
import timeline

control = PROJECT.parents[1] / 'shared/publishing/video-production-control.json'
def main():
    for item,clauses in zip(timeline.scenes, timeline.pairs, strict=True):
        assert ' '.join(k for k,_ in clauses)==item['lines'][0], item['id']
    previous=()
    deadline=time.monotonic()+7200
    while time.monotonic()<deadline:
        ready=[]
        stale=[]
        for n in range(13,18):
            cache=LOCAL/f'voice/asr/{n}.json';pcm=LOCAL/f'voice/chunks/{n}-scene.wav'
            if not cache.is_file() or not pcm.is_file():break
            with pcm.open('rb') as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
            if json.loads(cache.read_text(encoding='utf-8'))['audio_sha256']!=sha:
                stale.append(n);break
            ready.append(sha)
        joined=LOCAL/'voice/comparison.timing.json'
        all_ids=[str(n) for n in range(13,18)]
        if joined.exists() and stale:
            # Scene-mode retries may replace a WAV after the --watch transcriber
            # first read it. Wait for its process to release the cache, then
            # refresh only stale scenes against the completed assembly.
            alive=False
            for proc in psutil.process_iter(['cmdline','name']):
                argv=proc.info['cmdline'] or []
                if (proc.info['name'] or '').lower() in ('python.exe','python') and any('review_project_narration.py' in a for a in argv) and any('engine-comparison-v2-voice.json' in a for a in argv):
                    alive=True;break
            if not alive:
                root=PROJECT.parents[1]
                subprocess.run([sys.executable,'-u','-X','utf8','qwen3-tts/review_project_narration.py',
                    '--project',PROJECT.name,'--manifest',str((PROJECT/'production/engine-comparison-v2-voice.json').relative_to(root)),
                    '--device','cpu','--scenes',','.join(str(n) for n in stale)],cwd=root,check=True)
            time.sleep(5);continue
        if len(ready)==5 and not sealed_voice_batch(LOCAL/'voice','comparison',all_ids):
            time.sleep(5);continue
        if ready and tuple(ready)!=previous:
            grant=json.loads(control.read_text(encoding='utf-8-sig'))['scopedProductionAuthorizations'][PROJECT.name]
            assert grant['renderAuthorized'] and grant['revision']=='engine-comparison-v2'
            timeline.build()
            print('Comparison scenes with aligned cues:',len(ready),flush=True)
            previous=tuple(ready)
        if len(ready)==5:return
        time.sleep(5)
    raise TimeoutError('Comparison voice batch did not finish within two hours')

if __name__=='__main__':main()
