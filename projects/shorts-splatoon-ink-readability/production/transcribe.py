"""Cache complete voice/mix ASR using the existing offline Whisper snapshot.

No model import/job on import or --check. No expected-text prompt is given to
the recognizer. CUDA verification owns a serial lease; no foreign apps are closed.
"""
from contextlib import nullcontext
from pathlib import Path
import argparse
import difflib
import hashlib
import json
import os
import shutil
import subprocess
import time
import wave

from audio_revision import (
    P, R, L, VOICE, REVISION, LEASE, read, sha, normalize_speech,
    guard as revision_guard, assert_no_game_apps, assert_media_junction,
    gpu_lease, assert_owned_lease,
)

ASR_SNAPSHOT = Path('C:/Users/1/.cache/huggingface/hub/models--openai--whisper-large-v3-turbo/snapshots/41f01f3fe87f28c78e2fbf8b568835947dd65ed9')
ASR_CONFIG_SHA256 = 'c5b526b3e3cd64cd8940dabb45e8ba726629e22d8ed389c29b552f9140daf04a'


def normalized(text):
    return normalize_speech(text, read(P / 'production/clauses.json').get('pronunciationAliases', {}))


def repository_path(value):
    path = Path(value)
    return path if path.is_absolute() else R / path


def relative(path):
    try:
        return Path(path).resolve().relative_to(R.resolve()).as_posix()
    except ValueError:
        return str(Path(path).resolve())


def narration_input(project):
    source = repository_path(read(P / 'production/tts-manifest.json')['paths']['script'])
    document = read(source)
    lines = [line for scene in document['scenes'] for line in scene['lines']]
    if not lines or any(not isinstance(line, str) or not line.strip() for line in lines):
        raise RuntimeError('Narration must contain nonempty scene lines.')
    expected = ' '.join(lines)
    raw = (P / 'production/narration.ko.txt').read_text(encoding='utf8').strip()
    if normalized(raw) != normalized(expected):
        raise RuntimeError('Narration JSON and narration.ko.txt differ.')
    return source, raw


def resolve_existing_asr_model():
    manifest = read(P / 'production/tts-manifest.json').get('asr', {})
    configured = Path(manifest.get('modelPath', ''))
    if (configured != ASR_SNAPSHOT or manifest.get('configSha256') != ASR_CONFIG_SHA256
            or manifest.get('downloadAllowed') is not False
            or manifest.get('localFilesOnly') is not True):
        raise RuntimeError('ASR must use the existing hash-locked offline snapshot, with no download.')
    for name in ('config.json', 'model.safetensors', 'preprocessor_config.json', 'tokenizer.json'):
        if not (configured / name).is_file():
            raise RuntimeError('Existing cached ASR file unavailable; do not download: ' + name)
    if sha(configured / 'config.json') != ASR_CONFIG_SHA256:
        raise RuntimeError('Existing ASR configuration changed.')
    return configured


def ffmpeg_path():
    configured = os.environ.get('YAMYAM_FFMPEG')
    candidate = Path(configured) if configured else Path(
        'C:/Users/1/AppData/Local/Microsoft/WinGet/Packages/'
        'Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/'
        'ffmpeg-9.0-full_build/bin/ffmpeg.exe'
    )
    if candidate.is_file():
        return candidate
    found = shutil.which('ffmpeg')
    if not found:
        raise RuntimeError('FFmpeg not found; set YAMYAM_FFMPEG to its executable.')
    return Path(found)


def recognize_complete(wav, model_path, device, lease):
    """Heavy work lives only here, called after every live execution guard."""
    revision_guard()
    assert_no_game_apps()
    if lease is not None:
        assert_owned_lease(lease)
    elif LEASE.exists():
        raise RuntimeError('Foreign costly/GPU work remains active; defer complete CPU verification.')
    import torch
    from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

    torch.set_num_threads(3)
    torch.set_num_interop_threads(1)
    if device == 'cuda' and not torch.cuda.is_available():
        raise RuntimeError('Explicit CUDA ASR unavailable; do not substitute another device/model.')
    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        str(model_path), dtype=torch.float32, attn_implementation='eager', local_files_only=True,
    ).to(device)
    processor = AutoProcessor.from_pretrained(str(model_path), local_files_only=True)
    recognize = pipeline(
        'automatic-speech-recognition', model=model, tokenizer=processor.tokenizer,
        feature_extractor=processor.feature_extractor, dtype=torch.float32, device=device,
    )
    revision_guard()
    assert_no_game_apps()
    if lease is not None:
        assert_owned_lease(lease)
    elif LEASE.exists():
        raise RuntimeError('A foreign GPU lease appeared; defer CPU recognition.')
    return recognize(str(wav), generate_kwargs={'language': 'korean', 'task': 'transcribe'},
                     return_timestamps='word')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('role', choices=['voice', 'mix'])
    parser.add_argument('--check', action='store_true', help='Input/cache metadata only; no model or ASR.')
    args = parser.parse_args(argv)
    revision_guard(require_current_selection=not args.check)
    model_path = resolve_existing_asr_model()
    script_path, expected = narration_input(read(P / 'project.json'))
    source = VOICE if args.role == 'voice' else L / 'final-mix.m4a'
    device = os.environ.get('YAMYAM_ASR_DEVICE', 'cpu')
    if device not in ('cpu', 'cuda'):
        raise RuntimeError('Unsupported ASR verification device.')
    if args.check:
        print(json.dumps({'revision': REVISION, 'inputGuard': 'passed', 'role': args.role,
                          'sourcePresent': source.is_file(), 'modelPath': str(model_path),
                          'deviceOnFutureRun': device, 'modelLoaded': False,
                          'asrStarted': False, 'gpuWorkStarted': False}, ensure_ascii=False))
        return
    digest = sha(source)
    output = L / f'asr-{args.role}-{digest[:12]}.json'
    if output.exists():
        prior = read(output)
        if (prior.get('sha256') != digest or prior.get('role') != args.role
                or not prior.get('fullInput') or not prior.get('chunks')
                or prior.get('rawRecognitionUnmodified') is not True):
            raise RuntimeError('Existing ASR cache is incomplete or belongs to another input.')
        print(json.dumps({'output': relative(output), 'cached': True,
                          'rawAsrPreserved': True,
                          'currentExpectedNormalizedMatch': normalized(expected) == normalized(prior['text'])},
                         ensure_ascii=False))
        return
    assert_no_game_apps()
    if LEASE.exists():
        raise RuntimeError('Foreign GPU lease preserved; defer this verification job.')
    report_temporary = output.with_suffix('.partial.json')
    if report_temporary.exists():
        raise RuntimeError('Prior incomplete ASR report needs inspection before another full run.')
    os.environ['HF_HUB_OFFLINE'] = '1'
    os.environ['TRANSFORMERS_OFFLINE'] = '1'
    os.environ['OMP_NUM_THREADS'] = '3'
    os.environ['MKL_NUM_THREADS'] = '3'
    ffmpeg = ffmpeg_path()
    os.environ['PATH'] = str(ffmpeg.parent) + os.pathsep + os.environ.get('PATH', '')
    L.mkdir(parents=True, exist_ok=True)
    wav = L / f'asr-{args.role}-{digest[:12]}-16k.wav'
    if not wav.exists():
        temporary = wav.with_name(wav.stem + '.partial.wav')
        if temporary.exists():
            raise RuntimeError('Incomplete ASR conversion exists; inspect it before retrying.')
        subprocess.run([str(ffmpeg), '-v', 'error', '-n', '-threads', '2', '-i', str(source),
                        '-ac', '1', '-ar', '16000', '-c:a', 'pcm_s16le', str(temporary)], check=True)
        revision_guard()
        temporary.rename(wav)
    with wave.open(str(wav), 'rb') as audio:
        if audio.getframerate() != 16000 or audio.getnchannels() != 1:
            raise RuntimeError('ASR conversion must be mono16k PCM.')
        measured_seconds = audio.getnframes() / audio.getframerate()
        if measured_seconds <= 0:
            raise RuntimeError('ASR conversion contains no samples.')
    started = time.monotonic()
    scope = gpu_lease('splatoon-complete-' + args.role + '-asr') if device == 'cuda' else nullcontext(None)
    with scope as lease:
        recognized = recognize_complete(wav, model_path, device, lease)
    if not recognized.get('text') or not recognized.get('chunks'):
        raise RuntimeError('Complete ASR returned no usable text/word timestamps.')
    report = {
        'schemaVersion': 1, 'revision': REVISION, 'role': args.role, 'input': relative(source),
        'sha256': digest, 'fullInput': True, 'inputDurationSeconds': measured_seconds,
        'model': str(model_path), 'modelConfigSha256': ASR_CONFIG_SHA256,
        'device': device, 'cpuThreads': 3, 'modelDownloadAttempted': False,
        'expectedTextPromptUsed': False, 'rawRecognitionUnmodified': True,
        'normalizationAliases': read(P / 'production/clauses.json').get('pronunciationAliases', {}),
        'text': recognized['text'], 'chunks': recognized['chunks'],
        'expected': expected, 'expectedSource': relative(script_path),
        'expectedSourceSha256': sha(script_path),
        'normalizedMatch': normalized(expected) == normalized(recognized['text']),
        'similarity': difflib.SequenceMatcher(None, normalized(expected), normalized(recognized['text']),
                                             autojunk=False).ratio(),
        'elapsedSeconds': round(time.monotonic() - started, 3), 'humanListening': 'pending',
    }
    revision_guard()
    assert_media_junction()
    if sha(source) != digest:
        raise RuntimeError('Source changed during ASR; cannot assign recognition to the earlier hash.')
    with report_temporary.open('x', encoding='utf8') as stream:
        stream.write(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    report_temporary.rename(output)
    print(json.dumps({'output': relative(output), 'text': report['text'],
                      'similarity': report['similarity'], 'humanListening': 'pending'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
