"""Restore official public TTS/ASR weights without the stalled Xet transport.

Usage: qwen3-tts/.venv/Scripts/python.exe -X utf8 projects/one-button-game-design/production/restore-models.py
Large weights stay local under the gitignored qwen3-tts/models directory.
"""
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
from pathlib import Path
import json
import requests

ROOT = Path(__file__).resolve().parents[3]
MODELS = [
    ('Qwen/Qwen3-TTS-12Hz-1.7B-Base', 'Qwen3-TTS-12Hz-1.7B-Base'),
    ('openai/whisper-large-v3-turbo', 'whisper-large-v3-turbo'),
]

def restore(model):
    repo, name = model
    response = requests.get(f'https://huggingface.co/api/models/{repo}', timeout=30)
    response.raise_for_status()
    info = response.json()
    dest = ROOT / 'qwen3-tts/models' / name
    files = [x['rfilename'] for x in info['siblings'] if x['rfilename'].endswith(('.json', '.safetensors', '.txt'))]
    records = []
    for filename in files:
        target = dest / filename
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and target.stat().st_size:
            continue
        url = f'https://huggingface.co/{repo}/resolve/{info["sha"]}/{filename}'
        with requests.get(url, stream=True, timeout=(30, 90)) as stream:
            stream.raise_for_status()
            expected = int(stream.headers.get('content-length', 0))
            partial = target.with_name(target.name + '.direct-download')
            count = 0
            digest = sha256()
            with partial.open('wb') as output:
                for block in stream.iter_content(4 * 1024 * 1024):
                    output.write(block)
                    digest.update(block)
                    count += len(block)
                    if count % (256 * 1024 * 1024) < len(block):
                        print(f'{name}/{filename}: {count / 1024**2:.0f} MiB', flush=True)
            if expected and count != expected:
                raise RuntimeError(f'Truncated {filename}: {count}/{expected}')
            partial.replace(target)
            records.append({'file': filename, 'bytes': count, 'sha256': digest.hexdigest()})
            print(f'Restored {name}/{filename}: {count} bytes', flush=True)
    (dest / 'restoration.json').write_text(json.dumps({'repo':repo, 'revision':info['sha'], 'downloaded':records}, indent=2), encoding='utf-8')

if __name__ == '__main__':
    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(restore, MODELS))
