"""Resumable, fingerprinted full-page TTS. Does not imply publication approval.

Run with qwen3-tts/.venv/Scripts/python.exe. Writes progress after every page.
Excerpts from the approved preview are never substituted for full-page speech.
The generic provisional SRT is not published: ASR alignment is a separate step.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import sys
import subprocess
import time
import traceback

ROOT = Path(__file__).resolve().parents[3]
PROJECT = ROOT / 'projects/renderformer-explained'
sys.path.insert(0, str(ROOT / 'qwen3-tts'))
import render_narration as tts


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    temporary.replace(path)


def main():
    manifest = json.loads((PROJECT/'project.json').read_text(encoding='utf-8'))
    if not manifest['approvals']['voice'].startswith('approved-'):
        raise RuntimeError('Full synthesis requires approved voice.')
    tts.configure_project('renderformer-explained')
    jobs = tts.load_jobs()
    items = tts.build_render_items(jobs)
    assert len(items) == 88
    tts.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    lock = tts.OUTPUT_DIR/'production.lock'
    # An existing lock must be checked against the OS before manual removal.
    with lock.open('x', encoding='utf-8') as f:
        f.write(str(os.getpid()))
    progress_file = tts.OUTPUT_DIR/'production-progress.json'
    progress = {'status':'synthesizing', 'pid':os.getpid(), 'totalPages':88,
                'completedPages':0, 'asrStatus':'pending', 'publishReady':False,
                'startedAt':datetime.now(timezone.utc).isoformat(), 'pages':[]}
    try:
        # Refuse stale cache even if the old audio happens to have a clean tail.
        identity = {'script':hashlib.sha256(tts.SCRIPT_PATH.read_bytes()).hexdigest(),
                    'reference':hashlib.sha256(tts.REFERENCE.read_bytes()).hexdigest(),
                    'referenceText':hashlib.sha256(tts.REFERENCE_TEXT_PATH.read_bytes()).hexdigest(),
                    'model':str(tts.MODEL_DIR), 'maxNewTokens':tts.MAX_NEW_TOKENS}
        cache = tts.OUTPUT_DIR/'synthesis-inputs.json'
        if cache.exists() and json.loads(cache.read_text(encoding='utf-8')) != identity:
            raise RuntimeError('Inputs changed. Use a new output version; do not reuse stale chunks.')
        write(cache, identity)
        write(progress_file, progress)
        while True:
            free = int(subprocess.check_output(['nvidia-smi', '--query-gpu=memory.free',
                       '--format=csv,noheader,nounits'], text=True).splitlines()[0])
            if free >= 9000:
                break
            progress.update(status='waiting-for-gpu', freeGpuMiB=free)
            write(progress_file, progress)
            print(f'Waiting for GPU memory: {free} MiB free; preserving other running jobs.', flush=True)
            time.sleep(15)
        progress.update(status='synthesizing')
        write(progress_file, progress)
        tts.load_tts_dependencies()
        # Limit CPU oversubscription while GPU synthesis and slide production run.
        tts.torch.set_num_threads(4)
        original_write = tts.sf.write
        def tracked_write(path, data, sr, *args, **kwargs):
            result = original_write(path, data, sr, *args, **kwargs)
            complete = []
            for item in items:
                if tts.valid_wav(item.path):
                    info = tts.sf.info(item.path)
                    complete.append({'id':item.key.split('-')[0], 'seconds':info.duration})
            progress.update(completedPages=len(complete), pages=complete,
                            updatedAt=datetime.now(timezone.utc).isoformat())
            write(progress_file, progress)
            return result
        tts.sf.write = tracked_write
        tts.render_chunks(items, 1)
        tts.sf.write = original_write
        progress.update(status='synthesis-complete-awaiting-asr', completedPages=88,
                        finishedAt=datetime.now(timezone.utc).isoformat())
        write(progress_file, progress)
        print('88 full-page WAVs ready; ASR, mastering and final video QA remain.', flush=True)
    except BaseException as exc:
        progress.update(status='failed', error=str(exc), traceback=traceback.format_exc())
        write(progress_file, progress)
        raise
    finally:
        lock.unlink(missing_ok=True)


if __name__ == '__main__':
    main()
