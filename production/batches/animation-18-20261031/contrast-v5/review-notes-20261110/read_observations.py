"""Read back only the new lines with the local CPU Whisper model."""
import argparse
import hashlib
import os
from pathlib import Path
import re
import time

from plan_observations import HERE, PRIORITY, ROOT, WORK, load, save


def norm(text):
    return re.sub(r'[^\w가-힣]', '', text).casefold()


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def initialize():
    import torch
    from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
    torch.set_num_threads(2)
    torch.set_num_interop_threads(1)
    model_path = ROOT / 'qwen3-tts/models/whisper-large-v3-turbo'
    if not model_path.exists():
        from huggingface_hub import snapshot_download
        model_path = Path(snapshot_download('openai/whisper-large-v3-turbo', local_files_only=True))
    model = AutoModelForSpeechSeq2Seq.from_pretrained(str(model_path), dtype=torch.float32,
               low_cpu_mem_usage=True, use_safetensors=True, attn_implementation='eager', local_files_only=True).to('cpu')
    processor = AutoProcessor.from_pretrained(str(model_path), local_files_only=True)
    return pipeline('automatic-speech-recognition', model=model, tokenizer=processor.tokenizer,
                    feature_extractor=processor.feature_extractor, dtype=torch.float32, device='cpu')


def main(once=False):
    from finish_review import RATE, load_take, voice_window
    plan_path = HERE / 'observation-plan.json'
    recognize = None
    deadline = time.monotonic() + 4 * 3600
    while time.monotonic() < deadline:
        episodes = load(plan_path)['episodes']
        targets = [row for ep in sorted(episodes, key=lambda ep: (ep not in PRIORITY, ep)) for row in episodes[ep]]
        retake_path = WORK / 'retakes-pending.json'
        retakes = load(retake_path) if retake_path.exists() else {}
        read = {}
        for row in targets:
            path = next((WORK / 'voice').rglob(row['id'] + '-scene.wav'), None)
            if not path or time.time() - path.stat().st_mtime < 2:
                continue
            digest = sha(path)
            if retakes.get(row['id']) == digest:
                continue
            report = WORK / 'readback' / f'{row["id"]}.json'
            existing = load(report) if report.exists() else {}
            if existing.get('sha256') == digest and existing.get('expected') == row['ko']:
                read[row['id']] = existing
                continue
            try:
                samples, _, _ = load_take(path)
            except (AssertionError, RuntimeError):
                continue
            if recognize is None:
                print('Loading the local CPU readback model', flush=True)
                recognize = initialize()
            result = recognize(str(path), generate_kwargs={'language': 'korean', 'task': 'transcribe'},
                               return_timestamps='word', batch_size=1)
            if sha(path) != digest:
                print(row['id'], 'take changed during readback; retrying the current bytes', flush=True)
                continue
            available = (row['available'][1] - row['available'][0]) / 60
            a, b = voice_window(row, len(samples))
            proof = {'id': row['id'], 'sha256': digest, 'expected': row['ko'],
                     'recognized': result['text'].strip(), 'words': result.get('chunks', []),
                     'semanticMatch': norm(row['ko']) == norm(result['text']), 'humanListened': False,
                     'durationSeconds': round(len(samples) / RATE, 4), 'availableSeconds': available,
                     'fitsCaptionFreeWindow': len(samples) <= b - a}
            pending = report.with_suffix('.pending')
            save(pending, proof)
            os.replace(pending, report)
            read[row['id']] = proof
            print(row['id'], proof['durationSeconds'], 'fit', proof['durationSeconds'] <= available,
                  proof['recognized'], flush=True)
        complete = len(read) == len(targets)
        save(WORK / 'readback-status.json', {'complete': complete, 'checked': len(read), 'total': len(targets),
             'tooLong': [q for q in read.values() if not q.get('fitsCaptionFreeWindow',
                         q['durationSeconds'] <= q['availableSeconds'] + 13 / 60)],
             'different': [q for q in read.values() if not q['semanticMatch']]})
        if complete or once:
            return
        time.sleep(15)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--once', action='store_true')
    main(parser.parse_args().once)
