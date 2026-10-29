"""Checkpointed CPU-only final AAC transcript review, without word alignment.

The source already has full word ASR and reviewed caption timing. This fallback
examines all 19 final spoken paragraphs using short overlapping contexts and
segment timestamps. Decoded trailing digital silence is measured separately.
Each completed paragraph is bound to the actual master and decoded WAV hashes.
"""
import os
os.environ.update(CUDA_VISIBLE_DEVICES='', OMP_NUM_THREADS='2', MKL_NUM_THREADS='2', OPENBLAS_NUM_THREADS='2', NUMEXPR_NUM_THREADS='2', HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1')

import argparse
from datetime import datetime, timezone
import gc
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
PROJECT = Path(__file__).resolve().parents[1]
SOURCE = PROJECT / 'production/local/audio-v4'
QA = PROJECT / 'production/local/final-qa-v4'
FOLDER = QA / 'segment-asr'
DECODED = QA / 'final-encoded-v4.wav'
MONO = FOLDER / 'final-encoded-16k.wav'
MASTER = ROOT / 'output/buckshot-roulette-reverse-engineering-v4' / (PROJECT.name + '.captioned.mp4')
FFMPEG = Path('C:/Users/1/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0-full_build/bin/ffmpeg.exe')


def read(path): return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def now(): return datetime.now(timezone.utc).isoformat()
def save(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(8 * 1024 * 1024), b''): h.update(block)
    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true')
    args = parser.parse_args()
    import numpy as np
    import psutil
    import soundfile as sf
    auth = read(ROOT / 'shared/publishing/video-production-control.json')['scopedSetupAuthorizations'][PROJECT.name]
    assert auth['productionAllowedNow'] is True
    final_qa = read(PROJECT / 'production/local/documentary-v4/technical-qa.json')
    master_hash = digest(MASTER)
    assert final_qa['technicalDecodePassed'] and final_qa['pairedAudioIdentical'] and final_qa['outputs']['captioned']['sha256'] == master_hash
    receipt = read(QA / 'final-aac-decode-v4.json')
    decoded_hash = digest(DECODED)
    assert receipt['masterSha256'] == master_hash and receipt['decodedAudioSha256'] == decoded_hash
    timing = read(SOURCE / 'narration.timing.json')
    original = sf.info(DECODED)
    body_end = original.duration - 10
    entries = timing['entries']
    assert len(entries) == 19
    segments = []
    for index, entry in enumerate(entries):
        core_start = 0.0 if index == 0 else float(entry['start']) + 2
        core_end = float(entries[index + 1]['start']) + 2 if index + 1 < len(entries) else body_end
        segments.append({'id': f'{entry["scene_id"]}-{entry["paragraph"]:02}', 'mode': entry['mode'],
                         'expected': entry['text'], 'coreStart': core_start, 'coreEnd': core_end,
                         'windowStart': max(0, core_start - .2), 'windowEnd': min(original.duration, core_end + .2)})
    assert segments[0]['coreStart'] == 0 and segments[-1]['coreEnd'] == body_end
    assert all(a['coreEnd'] == b['coreStart'] for a, b in zip(segments, segments[1:]))
    print(json.dumps({'status': 'cpu-segment-plan', 'paragraphs': 19, 'speechCoreCoverage': [0, body_end],
                      'digitalTailCoverage': [body_end, original.duration], 'masterSha256': master_hash, 'gpuLeaseCreated': False}), flush=True)
    if not args.run: return
    memory = psutil.virtual_memory()
    assert memory.available >= 8 * 2**30, 'Insufficient free host memory; preserve other applications.'
    FOLDER.mkdir(parents=True, exist_ok=True)
    for name in ['mix-asr-execution.json', 'mix-full-asr.log']:
        old = SOURCE / 'review' / name
        preserved = FOLDER / ('failed-cpu-longform-' + name)
        if old.exists() and not preserved.exists(): shutil.copy2(old, preserved)
    mono_receipt = FOLDER / 'resample-receipt.json'
    if MONO.exists():
        prior = read(mono_receipt)
        assert prior['decodedAudioSha256'] == decoded_hash and prior['monoSha256'] == digest(MONO)
    else:
        command = [str(FFMPEG), '-hide_banner', '-nostdin', '-v', 'warning', '-threads', '2', '-i', str(DECODED), '-vn', '-ac', '1', '-ar', '16000', '-c:a', 'pcm_f32le', '-n', str(MONO)]
        with (FOLDER / 'resample.log').open('w', encoding='utf-8') as log:
            result = subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        assert result.returncode == 0
        save(mono_receipt, {'masterSha256': master_hash, 'decodedAudioSha256': decoded_hash, 'monoSha256': digest(MONO), 'command': command})
    data, rate = sf.read(MONO, dtype='float32')
    assert rate == 16000 and abs(len(data) / rate - original.duration) < .001
    state = {'schemaVersion': 1, 'startedAt': now(), 'status': 'running', 'device': 'cpu', 'dtype': 'float32',
             'torchIntraopThreads': 2, 'torchInteropThreads': 1, 'ompThreads': 2, 'cudaVisibleDevices': '',
             'gpuLeaseCreated': False, 'foreignProcessesChanged': False, 'availableMemoryGiB': memory.available / 2**30,
             'masterSha256': master_hash, 'decodedAudioSha256': decoded_hash, 'segments': segments,
             'decision': 'Short final AAC paragraph checks after a native failure in CPU long-form word ASR. Source word timestamps and caption timing remain unchanged.'}
    save(FOLDER / 'execution.json', state)
    completed, pending = [], []
    for row in segments:
        path = FOLDER / (row['id'] + '.json')
        if path.exists():
            value = read(path)
            assert value['masterSha256'] == master_hash and value['decodedAudioSha256'] == decoded_hash and value['segment'] == row
            completed.append(value)
        else: pending.append(row)
    try:
        if pending:
            import torch
            from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
            torch.set_num_threads(2); torch.set_num_interop_threads(1)
            assert not torch.cuda.is_initialized()
            model_path = Path('C:/Users/1/.cache/huggingface/hub/models--openai--whisper-large-v3-turbo/snapshots/41f01f3fe87f28c78e2fbf8b568835947dd65ed9')
            assert (model_path / 'model.safetensors').exists()
            model = AutoModelForSpeechSeq2Seq.from_pretrained(str(model_path), dtype=torch.float32, low_cpu_mem_usage=True, use_safetensors=True, attn_implementation='sdpa').to('cpu').eval()
            processor = AutoProcessor.from_pretrained(str(model_path))
            transcriber = pipeline('automatic-speech-recognition', model=model, tokenizer=processor.tokenizer,
                                   feature_extractor=processor.feature_extractor, dtype=torch.float32, device='cpu')
            print('Same local Whisper model loaded once on CPU; segment timestamps, inference mode, no CUDA context.', flush=True)
            for row in pending:
                samples = data[round(row['windowStart'] * rate):round(row['windowEnd'] * rate)].copy()
                assert 0 < len(samples) / rate < 36
                with torch.inference_mode():
                    result = transcriber({'array': samples, 'sampling_rate': rate}, generate_kwargs={'language': 'korean', 'task': 'transcribe'}, return_timestamps=True)
                chunks, selected = [], []
                for chunk in result.get('chunks', []):
                    a, b = chunk['timestamp']
                    a = 0 if a is None else float(a)
                    b = len(samples) / rate if b is None else float(b)
                    start, end = row['windowStart'] + a, row['windowStart'] + b
                    chunks.append({'text': chunk['text'], 'timestamp': [start, end]})
                    if row['coreStart'] <= (start + end) / 2 < row['coreEnd']: selected.append(chunk['text'])
                value = {'schemaVersion': 1, 'completedAt': now(), 'masterSha256': master_hash, 'decodedAudioSha256': decoded_hash,
                         'segment': row, 'language': 'korean', 'timestampMode': 'segment', 'rawText': str(result['text']).strip(),
                         'coreText': ' '.join(selected).strip() or str(result['text']).strip(), 'chunks': chunks,
                         'device': 'cpu', 'humanListening': False}
                save(FOLDER / (row['id'] + '.json'), value)
                completed.append(value)
                print(json.dumps({'completedParagraph': row['id'], 'completed': len(completed), 'total': 19, 'rawText': value['rawText']}, ensure_ascii=False), flush=True)
                del samples, result
                gc.collect()
                assert not torch.cuda.is_initialized()
        by_id = {r['segment']['id']: r for r in completed}
        ordered = [by_id[r['id']] for r in segments]
        with sf.SoundFile(DECODED) as original_audio:
            original_audio.seek(round(body_end * original_audio.samplerate))
            tail = original_audio.read(dtype='float32', always_2d=True)
        # AAC filter/codec tails can cross the nominal bookend by a few samples.
        # The last overlapping ASR window already covers that boundary: verify
        # the truly untranscribed tail, rather than asserting a guessed cut is 0.
        tail_start_frame = round(body_end * original.samplerate)
        last_window_end_frame = round(segments[-1]['windowEnd'] * original.samplerate)
        uncovered = tail[max(0, last_window_end_frame - tail_start_frame):]
        nonzero = np.flatnonzero(np.any(tail != 0, axis=1))
        last_nonzero = int(tail_start_frame + nonzero[-1]) if len(nonzero) else None
        tail_report = {'start': body_end, 'end': original.duration, 'frames': len(tail),
                       'allSamplesExactlyZero': bool(np.all(tail == 0)), 'maxAbsoluteAmplitude': float(np.abs(tail).max()),
                       'nonzeroFrames': len(nonzero), 'lastNonzeroAbsoluteFrame': last_nonzero,
                       'exactDigitalSilenceStartsAtFrame': last_nonzero + 1 if last_nonzero is not None else tail_start_frame,
                       'lastAsrWindowEndFrame': last_window_end_frame,
                       'untranscribedTailFrames': len(uncovered),
                       'allUntranscribedSamplesExactlyZero': bool(np.all(uncovered == 0)),
                       'method': 'Actual decoded AAC samples. All nonzero samples are within the already transcribed final overlapping window; the remaining tail is checked for exact digital silence.'}
        assert tail_report['allUntranscribedSamplesExactlyZero'], 'Non-silent uncovered ending needs explicit content inspection.'
        aggregate = {'schemaVersion': 1, 'completedAt': now(), 'masterSha256': master_hash, 'audio_sha256': decoded_hash,
                     'audio': str(DECODED), 'language': 'korean', 'timestampMode': 'segment', 'device': 'cpu',
                     'text': ' '.join(r['coreText'] for r in ordered), 'paragraphCount': 19, 'paragraphs': ordered,
                     'continuousSpeechCoreCoverage': [0, body_end], 'endingSilence': tail_report,
                     'fullDecodedRangeAccountedFor': True, 'humanListening': False,
                     'reviewStatus': 'Complete current mix segmentation; direct text comparison still required.'}
        save(SOURCE / 'review/mix-segment-asr.json', aggregate)
        state.update(status='finished', finishedAt=now(), completedParagraphs=19, cudaInitialized=False)
    except BaseException as error:
        state.update(status='failed', failedAt=now(), error=repr(error), completedParagraphs=len(completed))
        raise
    finally:
        save(FOLDER / 'execution.json', state)
    print(json.dumps({'status': 'all-19-final-AAC-paragraphs-transcribed-on-CPU', 'masterSha256': master_hash, 'gpuUsed': False}), flush=True)


if __name__ == '__main__': main()
