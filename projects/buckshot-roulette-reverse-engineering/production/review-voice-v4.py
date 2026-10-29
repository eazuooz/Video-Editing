"""Readiness check or coordinator-authorized whole-v4 Korean ASR review.

Default does not load a model or acquire a GPU. --run uses the installed local
Whisper pipeline and the reviewed v4 resource guard; it preserves foreign apps.
Evidence is additive under audio-v4/review. No narration or old QA is changed.
ASR comparison is evidence, not a claim of human listening or verified delivery.
"""
from __future__ import annotations

import argparse
import difflib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[3]
PROJECT = Path(__file__).resolve().parents[1]
OUT = PROJECT / 'production/local/audio-v4'
REVIEW = OUT / 'review'
SCRIPT = PROJECT / 'script/revision-v4/narration.ko.json'
LEASE = ROOT / 'shared/output/GPU_HANDOFF.json'
CREATE_NO_WINDOW = getattr(subprocess, 'CREATE_NO_WINDOW', 0)
PYTHON = ROOT / 'qwen3-tts/.venv/Scripts/python.exe'
TRANSCRIBER = ROOT / 'qwen3-tts/transcribe_reference.py'
FFMPEG = Path('C:/Users/1/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0-full_build/bin/ffmpeg.exe')


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


captions = load('buckshot_v4_captions_for_review', PROJECT / 'production/build-subtitles-v4.py')
read, save, digest = captions.read, captions.save, captions.digest
LOCAL_MODEL = captions.base.review.LOCAL_MODEL


def current_authorization():
    control = read(ROOT / 'shared/publishing/video-production-control.json')
    auth = control['scopedSetupAuthorizations'][PROJECT.name]
    assert auth['productionAllowedNow'] is True, 'Selected project production is not authorized.'
    assert auth['projectPath'] == PROJECT.relative_to(ROOT).as_posix()
    return auth


def ensure_local_audio(audio):
    audio = audio.resolve()
    audio.relative_to(PROJECT.resolve())
    assert audio.suffix.lower() == '.wav', 'Review the actual local PCM WAV.'
    assert audio.is_file(), audio
    return audio


def run_asr(audio, output, allow_idle_editors, device):
    import psutil
    if device == 'cpu':
        memory = psutil.virtual_memory()
        assert memory.available >= 8 * 2**30, 'CPU ASR needs at least 8 GiB of actual free memory; preserve other work.'
        resources = {'device': 'cpu', 'availableMemoryGiB': memory.available / 2**30,
                     'totalMemoryGiB': memory.total / 2**30, 'minimumFreeGiB': 8,
                     'torchIntraopThreads': 2, 'torchInteropThreads': 1, 'ompThreads': 2,
                     'cudaVisibleDevices': '', 'dtype': 'float32', 'gpuLeaseCreated': False,
                     'decision': 'Coordinator-selected CPU-only final ASR to preserve a foreground GPU application. No foreign process is changed.'}
    else:
        guard = load('buckshot_v4_resource_guard_for_asr', PROJECT / 'production/render-voice-v4.py')
        assert not LEASE.exists(), 'Preserve the current GPU lease; wait for its owner.'
        resources = guard.resource_guard(allow_idle_editors)
    current_authorization()
    token = str(uuid.uuid4())
    process = psutil.Process()
    state = {'schemaVersion': 1, 'token': token, 'project': PROJECT.name, 'state': 'asr_running',
             'purpose': 'One current v4 whole recording Korean ASR',
             'coordinator': {'pid': process.pid, 'createTime': process.create_time()},
             'startedAt': time.time(), 'resources': resources, 'foreignProcessesPaused': [],
             'rootExplicitInvocation': f'review-voice-v4.py --run --device {device}', 'audioSha256': digest(audio), 'device': device}
    if device == 'cuda':
        LEASE.parent.mkdir(parents=True, exist_ok=True)
        with LEASE.open('x', encoding='utf-8') as stream:
            json.dump(state, stream, ensure_ascii=False, indent=2)
    receipt = output.with_name(output.stem.replace('-full-asr', '-asr-execution') + '.json')
    save(receipt, state)
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        env = os.environ.copy()
        env.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1')
        transcriber = TRANSCRIBER
        if device == 'cpu':
            env.update(CUDA_VISIBLE_DEVICES='', OMP_NUM_THREADS='2', MKL_NUM_THREADS='2', OPENBLAS_NUM_THREADS='2', NUMEXPR_NUM_THREADS='2')
            transcriber = PROJECT / 'production/transcribe-cpu-v4.py'
        assert FFMPEG.is_file(), 'Expected existing FFmpeg installation; do not install implicitly.'
        env['PATH'] = str(FFMPEG.parent) + os.pathsep + env.get('PATH', '')
        command = [str(PYTHON), '-X', 'utf8', str(transcriber), str(audio), '--output', str(output),
                   '--model', str(LOCAL_MODEL), '--language', 'korean', '--device', device, '--timestamps', 'word']
        state['command'] = command
        save(receipt, state)
        with output.with_suffix('.log').open('w', encoding='utf-8') as log:
            result = subprocess.run(command, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT, creationflags=CREATE_NO_WINDOW)
        if result.returncode:
            raise RuntimeError(f'ASR exited {result.returncode}; inspect {output.with_suffix(".log")}')
        state.update(state='finished', exitCode=0, finishedAt=time.time())
    except BaseException as error:
        state.update(state='failed', error=repr(error), finishedAt=time.time())
        raise
    finally:
        save(receipt, state)
        # The synchronous model child has exited before releasing this lease.
        if device == 'cuda' and LEASE.exists() and read(LEASE).get('token') == token:
            LEASE.unlink()
    print(json.dumps({'status': 'ASR-child-exited-GPU-released' if device == 'cuda' else 'CPU-only-ASR-child-exited-no-GPU-lease', 'audioSha256': state['audioSha256']}), flush=True)


def compare(expected, recognized):
    left, right = captions.normalized(expected), captions.normalized(recognized)
    matcher = difflib.SequenceMatcher(None, left, right, autojunk=False)
    differences = [{'kind': kind, 'expected': left[a:b], 'recognized': right[c:d],
                    'expectedCharacterRange': [a, b], 'recognizedCharacterRange': [c, d]}
                   for kind, a, b, c, d in matcher.get_opcodes() if kind != 'equal']
    return matcher.ratio(), differences


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true', help='Only after coordinator confirms the TTS/render GPU job is finished')
    parser.add_argument('--kind', choices=['source', 'mix'], default='source')
    parser.add_argument('--audio', type=Path, help='Required for mix; actual decoded encoded-AAC WAV under this project')
    parser.add_argument('--master', type=Path, help='Optional actual encoded MP4 binding for later mix review')
    parser.add_argument('--offset', type=float, default=None, help='Narration start in reviewed audio: source 0, mix default 2 seconds')
    parser.add_argument('--allow-idle-editors', action='store_true')
    parser.add_argument('--device', choices=['cuda', 'cpu'], default='cuda', help='CPU fallback uses fp32, two intraop threads, one interop thread, and creates no GPU lease')
    parser.add_argument('--build-captions', action='store_true', help='After source ASR, run CPU-only v4 clause caption builder')
    args = parser.parse_args()
    if args.kind == 'mix' and args.audio is None:
        parser.error('--kind mix requires --audio')
    if args.build_captions and args.kind != 'source':
        parser.error('--build-captions is for source review only')
    assert (LOCAL_MODEL / 'model.safetensors').is_file(), 'Local model is missing; no automatic download.'
    audio = (args.audio if args.audio else OUT / 'narration.wav').resolve()
    audio.relative_to(PROJECT.resolve())
    offset = args.offset if args.offset is not None else (2.0 if args.kind == 'mix' else 0.0)
    current_authorization()
    output = REVIEW / f'{args.kind}-full-asr.txt'
    cache = output.with_suffix('.timestamps.json')
    if not args.run:
        print(json.dumps({'status': 'preflight-only', 'audio': str(audio), 'audioExists': audio.is_file(),
                          'scriptExists': SCRIPT.is_file(), 'localModel': str(LOCAL_MODEL), 'output': str(cache),
                          'language': 'korean', 'timestamps': 'word', 'gpuLoaded': False, 'gpuLeaseCreated': False,
                          'willBuildCaptionsAfterRun': args.build_captions, 'humanListening': False}, ensure_ascii=False))
        return
    audio = ensure_local_audio(audio)
    audio_hash = digest(audio)
    valid_cache = cache.is_file() and read(cache).get('audio_sha256') == audio_hash and read(cache).get('language') == 'korean' and read(cache).get('timestampMode') == 'word'
    if not valid_cache:
        if cache.exists():
            # Preserve old evidence in this revision; never silently reuse a
            # transcript bound to a different audio file.
            suffix = time.strftime('%Y%m%dT%H%M%SZ', time.gmtime()) + '-' + uuid.uuid4().hex[:6]
            for path in [output, cache, output.with_suffix('.log')]:
                if path.exists():
                    path.rename(path.with_name(f'{path.stem}-previous-{suffix}{path.suffix}'))
        run_asr(audio, output, args.allow_idle_editors, args.device)
    actual = read(cache)
    assert actual['audio_sha256'] == audio_hash and actual['timestampMode'] == 'word' and actual['language'] == 'korean'
    rows = captions.planned_rows()
    timing = read(OUT / 'narration.timing.json')
    assert len(timing['entries']) == len(rows)
    expected = ' '.join(row['ko'] for row in rows)
    similarity, differences = compare(expected, actual['text'])
    paragraph_reports = []
    for row, entry in zip(rows, timing['entries']):
        assert captions.key(entry['scene_id'], entry['paragraph']) == row['id'] and entry['text'] == row['ko']
        start, end = entry['start'] + offset, entry['end'] + offset
        words = [w for w in actual['chunks'] if None not in w['timestamp'] and start <= sum(w['timestamp']) / 2 < end]
        transcript = ' '.join(w['text'] for w in words)
        ratio, edits = compare(row['ko'], transcript)
        paragraph_reports.append({'id': row['id'], 'mode': row['mode'], 'start': start, 'end': end,
                                  'expected': row['ko'], 'recognized': transcript, 'similarity': ratio, 'differences': edits,
                                  'wordTimestampRange': [words[0]['timestamp'][0], words[-1]['timestamp'][1]] if words else None,
                                  'priority': 'new speech: inspect missing/repeated clauses and names' if row['mode'] != 'reuse' else 'unchanged body: reuse baseline content review only with exact PCM proof',
                                  'reviewStatus': 'pending direct transcript comparison; ASR substitutions are candidates, not proven speech faults'})
    report = {'schemaVersion': 1, 'revision': 'v4', 'kind': args.kind, 'audioSha256': audio_hash,
              'scriptSha256': digest(SCRIPT), 'sourceAsrSha256': digest(cache), 'wholeCurrentAudioAsr': True,
              'cacheReused': valid_cache, 'language': 'korean', 'expected': expected, 'recognized': actual['text'],
              'similarity': similarity, 'differences': differences, 'narrationOffsetSeconds': offset,
              'paragraphs': paragraph_reports, 'humanListening': False, 'paceVerified': False,
              'reviewStatus': 'pending direct full transcript review; technical pass is not inferred from ASR similarity'}
    if args.master is not None:
        master = args.master.resolve()
        master.relative_to(ROOT.resolve())
        assert master.is_file() and master.suffix.lower() == '.mp4'
        report.update(masterPath=str(master), masterSha256=digest(master), decodedAudioProvenance='Caller-supplied decoded file; verify the decode receipt separately.')
    save(REVIEW / f'{args.kind}-text-comparison.json', report)
    if args.build_captions:
        command = [str(PYTHON), '-X', 'utf8', str(PROJECT / 'production/build-subtitles-v4.py'), '--asr', str(cache)]
        subprocess.run(command, cwd=ROOT, check=True, creationflags=CREATE_NO_WINDOW)
    print(json.dumps({'status': 'current-v4-whole-ASR-ready-for-direct-review', 'kind': args.kind,
                      'similarity': similarity, 'differences': len(differences),
                      'newParagraphDifferences': {r['id']: len(r['differences']) for r in paragraph_reports if r['mode'] != 'reuse'},
                      'audioSha256': audio_hash, 'humanListening': False}, ensure_ascii=False))


if __name__ == '__main__':
    main()
