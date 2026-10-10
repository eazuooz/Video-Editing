"""Verify the complete TTS batch and the actual research handoff, without CUDA.

This never launches research or changes pause controls. Partial synthesis is
refused; WAV structure and decoding are distinct from spoken-content approval.
"""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import time
import wave

import psutil

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'production/research/game-lighting-history'
TOKEN = '967d4ad1-fe14-4940-a548-67133be275de'
SLUGS = [f'game-lighting-history-0{n}' for n in (2, 3, 4)]
EXPECTED = {'game-lighting-history-02': (106, 17),
            'game-lighting-history-03': (84, 14),
            'game-lighting-history-04': (87, 14)}
NO_WINDOW = subprocess.CREATE_NO_WINDOW


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def write(path, record):
    temporary = path.with_name(path.name + '.tmp-' + str(os.getpid()))
    temporary.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    os.replace(temporary, path)


def live_identity(identity):
    try:
        p = psutil.Process(identity['pid'])
        return p if abs(p.create_time() - identity['createTime']) < .01 else None
    except psutil.NoSuchProcess:
        return None


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--wait', action='store_true')
    args = ap.parse_args()
    state_path = BASE / 'remaining-tts-execution-v1.json'
    deadline = time.monotonic() + 43200
    while True:
        state = read(state_path)
        if state.get('status') == 'all-requested-tts-produced-awaiting-asr':
            break
        if state.get('status') in ('child-failed', 'input-preparation-timeout'):
            raise RuntimeError('Producer failed. Preserve all chunks and inspect the actual log.')
        if not args.wait:
            raise RuntimeError('All requested episodes must finish before verification.')
        if time.monotonic() > deadline:
            raise TimeoutError('Complete-batch verification wait exceeded12hours.')
        time.sleep(10)
    if state.get('token') != TOKEN or [x['slug'] for x in state['completed']] != SLUGS or state.get('exitCode') != 0:
        raise RuntimeError('Unexpected batch identity or completion evidence.')
    review = read(BASE / 'remaining-tts-input-review-v1.json')
    for relative, expected_sha in review['inputHashes'].items():
        if sha(ROOT / relative) != expected_sha:
            raise RuntimeError('Reviewed TTS input changed: ' + relative)
    ffmpeg = shutil.which('ffmpeg')
    if not ffmpeg:
        raise RuntimeError('Whole WAV decode needs the installed ffmpeg.')
    episodes = []
    for done in state['completed']:
        slug = done['slug']
        manifest = read(ROOT / 'projects' / slug / 'project.json')
        ko = read(ROOT / manifest['paths']['script'])
        en = read(ROOT / manifest['paths']['scriptEn'])
        expected_lines, expected_scenes = EXPECTED[slug]
        assert len(ko['scenes']) == len(en['scenes']) == expected_scenes
        flattened = [(scene['id'], line) for scene in ko['scenes'] for line in scene['lines']]
        assert len(flattened) == expected_lines
        assert [s['id'] for s in ko['scenes']] == [s['id'] for s in en['scenes']]
        assert [len(s['lines']) for s in ko['scenes']] == [len(s['lines']) for s in en['scenes']]
        for info in done['files'].values():
            assert sha(ROOT / info['path']) == info['sha256']
        wav_path = ROOT / done['files']['.wav']['path']
        timing = read(ROOT / done['files']['.timing.json']['path'])
        assert len(timing['entries']) == expected_lines
        with wave.open(str(wav_path), 'rb') as wav:
            samples, sr, channels, width = wav.getnframes(), wav.getframerate(), wav.getnchannels(), wav.getsampwidth()
            assert (sr, channels, width) == (24000, 1, 2)
            actual_bytes = 0
            while block := wav.readframes(sr * 20):
                actual_bytes += len(block)
            assert actual_bytes == samples * channels * width
        duration = samples / sr
        assert abs(duration - timing['duration_seconds']) <= 1 / sr
        previous_end = 0
        for (scene_id, text), entry in zip(flattened, timing['entries']):
            assert entry['scene_id'] == scene_id and entry['text'] == text
            assert entry['start'] >= previous_end - 1 / sr
            assert entry['end'] > entry['start'] and entry['end'] <= duration + 1 / sr
            previous_end = entry['end']
        command = [ffmpeg, '-v', 'error', '-threads', '2', '-i', str(wav_path), '-map', '0:a:0', '-f', 'null', '-']
        decode = subprocess.run(command, capture_output=True, text=True, creationflags=NO_WINDOW)
        if decode.returncode:
            raise RuntimeError('Whole narration decode failed: ' + slug + ' ' + decode.stderr)
        en_command = [str(ROOT / 'qwen3-tts/.venv/Scripts/python.exe'), '-X', 'utf8',
                      str(ROOT / 'qwen3-tts/build_translated_srt.py'), '--project', slug, '--language', 'en']
        en_result = subprocess.run(en_command, cwd=ROOT, capture_output=True, text=True, encoding='utf-8', creationflags=NO_WINDOW)
        if en_result.returncode:
            raise RuntimeError('English provisional captions failed: ' + en_result.stderr)
        en_path = ROOT / manifest['paths']['captionsEn']
        ko_path = ROOT / manifest['paths']['captionsKo']
        chunk_dir = wav_path.parent / 'chunks'
        chunks = sorted(chunk_dir.glob('*-scene.wav'))
        assert len(chunks) == expected_scenes
        episodes.append(dict(slug=slug, sampleRate=sr, samples=samples, durationSeconds=duration,
                             paragraphPairs=expected_lines, sceneCount=expected_scenes,
                             audioSha256=sha(wav_path), files=done['files'],
                             wholeWavDecode=dict(exitCode=decode.returncode, command=command),
                             rawSceneHashes={p.name: sha(p) for p in chunks},
                             captionsKo=dict(path=ko_path.relative_to(ROOT).as_posix(), sha256=sha(ko_path),
                                             cueCount=len(re.findall(r'(?m)^\d+\s*$', ko_path.read_text(encoding='utf-8-sig')))),
                             captionsEn=dict(path=en_path.relative_to(ROOT).as_posix(), sha256=sha(en_path),
                                             cueCount=len(re.findall(r'(?m)^\d+\s*$', en_path.read_text(encoding='utf-8-sig')))),
                             captionTimingMode='provisional-character-weighted-paragraphs; not reviewed word alignment',
                             generatedNarrationComplete=True, currentNarrationApproved=False,
                             humanWholeListeningApproved=False, finalMixedAsrApproved=False,
                             finalVideoProduced=False))
        print(f'VERIFIED {slug}: {duration:.6f}s / {expected_lines} paragraphs / decode0', flush=True)
    history_path = ROOT / 'shared/output/gpu-handoff' / (TOKEN + '.json')
    deadline = time.monotonic() + 180
    while True:
        handoff = read(history_path)
        if handoff.get('state') in ('research_resume_verified', 'resume_pending_foreign_stop', 'research_already_complete_or_failed'):
            break
        if time.monotonic() > deadline:
            raise TimeoutError('Research coordinator completion not yet observed; do not claim resume.')
        time.sleep(5)
    preservation = read(BASE / 'research-preservation-before-remaining-tts-v1.json')
    q = Path(handoff['queueDir'])
    marker_failures = [name for name, digest in preservation['beforeTtsCompleteMarkers'].items()
                       if not (q / 'done' / name).exists() or sha(q / 'done' / name) != digest]
    configs = {name: sha(q / name) == digest for name, digest in preservation['queueConfigHashes'].items()}
    queue_script = Path(handoff['queueOwner']['command'][-1])
    source_preserved = sha(queue_script) == preservation['queueSourceSha256']
    if marker_failures or not all(configs.values()) or not source_preserved:
        raise RuntimeError('Research preservation mismatch; preserve evidence and inspect.')
    status = read(q / 'status.json')
    resumed = handoff.get('resumedQueue')
    queue_proc = live_identity(resumed) if resumed else None
    child = None
    if queue_proc and status.get('owner_pid') == queue_proc.pid and status.get('status') == 'running':
        try:
            p = psutil.Process(status['child_pid'])
            child = dict(pid=p.pid, createTime=p.create_time(), command=p.cmdline(), cwd=p.cwd())
        except psutil.NoSuchProcess:
            pass
    active_lease = ROOT / 'shared/output/GPU_HANDOFF.json'
    controls = {path: dict(exists=Path(path).exists(), token=read(Path(path)).get('token') if Path(path).exists() else None)
                for path in handoff['ownedFiles']}
    assert not any(info['exists'] and info['token'] == TOKEN for info in controls.values())
    record = dict(schemaVersion=1, observedAt=now(), allRequestedTtsProduced=True, ttsExitCode=0,
                  handoffToken=TOKEN, episodes=episodes, researchHandoffHistory=history_path.relative_to(ROOT).as_posix(),
                  researchHandoffState=handoff['state'], preservedDoneMarkers=len(preservation['beforeTtsCompleteMarkers']),
                  allPreservedDoneMarkersByteIdentical=True, queueConfigHashesPreserved=configs,
                  queueSourcePreserved=source_preserved, pauseControls=controls,
                  ownedLeaseRemoved=not active_lease.exists() or read(active_lease).get('token') != TOKEN,
                  actualResearchStatus=status, liveResumedQueue=bool(queue_proc), actualResearchChild=child,
                  researchGpuProgressVerified=False,
                  researchResumeMeaning='Original queue continues uncompleted jobs; no optimizer/RNG resume is claimed from adapter-only weights.',
                  currentNarrationApproved=False, humanWholeListeningApproved=False,
                  finalMixedAsrApproved=False, finalVideoProduced=False)
    write(BASE / 'remaining-tts-completion-verification-v1.json', record)
    print(json.dumps(dict(allRequestedTtsProduced=True, researchState=handoff['state'],
                          liveResumedQueue=bool(queue_proc), actualResearchChild=child), ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
