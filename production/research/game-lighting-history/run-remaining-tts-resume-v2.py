"""Resume only episodes3/4 in one cooperative lease, preserving completed1/2.

Preflight changes require a fresh direct content review. Verification runs before
this worker exits, so no Python wait helper blocks the restored research queue.
"""
from pathlib import Path
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import wave
import psutil

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'production/research/game-lighting-history'
LEASE = ROOT / 'shared/output/GPU_HANDOFF.json'
READY = BASE / 'remaining-tts-input-review-v2.json'
STATE = BASE / 'remaining-tts-execution-v2.json'
BATCH = 'game-lighting-history-remaining-tts-resume-v2'
SLUGS = ['game-lighting-history-03', 'game-lighting-history-04']
EXPECTED = {'game-lighting-history-02': (106, 17), SLUGS[0]: (84, 14), SLUGS[1]: (87, 14)}
NO_WINDOW = subprocess.CREATE_NO_WINDOW


def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))


def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda: f.read(1048576), b''):
            h.update(block)
    return h.hexdigest()


def write(p, obj):
    temp = p.with_name(p.name + '.tmp-' + str(os.getpid()))
    temp.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    os.replace(temp, p)


def relative(p):
    return p.relative_to(ROOT).as_posix()


def check_inputs(review):
    for rel, digest in review['inputHashes'].items():
        if sha(ROOT / rel) != digest:
            raise RuntimeError('Frozen reviewed input changed: ' + rel)


def verify_audio(done):
    slug = done['slug']
    manifest = read(ROOT / 'projects' / slug / 'project.json')
    ko, en = [read(ROOT / manifest['paths'][key]) for key in ('script', 'scriptEn')]
    pairs, scenes = EXPECTED[slug]
    assert len(ko['scenes']) == len(en['scenes']) == scenes
    assert [s['id'] for s in ko['scenes']] == [s['id'] for s in en['scenes']]
    assert [len(s['lines']) for s in ko['scenes']] == [len(s['lines']) for s in en['scenes']]
    flattened = [(s['id'], line) for s in ko['scenes'] for line in s['lines']]
    assert len(flattened) == pairs
    for item in done['files'].values():
        assert sha(ROOT / item['path']) == item['sha256']
    wav_path = ROOT / done['files']['.wav']['path']
    timing = read(ROOT / done['files']['.timing.json']['path'])
    assert len(timing['entries']) == pairs
    with wave.open(str(wav_path), 'rb') as wav:
        samples, rate = wav.getnframes(), wav.getframerate()
        assert (rate, wav.getnchannels(), wav.getsampwidth()) == (24000, 1, 2)
        byte_count = 0
        while block := wav.readframes(rate * 20):
            byte_count += len(block)
        assert byte_count == samples * 2
    duration = samples / rate
    assert abs(duration - timing['duration_seconds']) <= 1 / rate
    previous_end = 0
    for (scene_id, text), entry in zip(flattened, timing['entries']):
        assert entry['scene_id'] == scene_id and entry['text'] == text
        assert entry['start'] >= previous_end - 1 / rate
        assert entry['end'] > entry['start'] and entry['end'] <= duration + 1 / rate
        previous_end = entry['end']
    ffmpeg = shutil.which('ffmpeg')
    if not ffmpeg:
        raise RuntimeError('Installed FFmpeg required for whole WAV decode.')
    cmd = [ffmpeg, '-v', 'error', '-threads', '2', '-i', str(wav_path), '-map', '0:a:0', '-f', 'null', '-']
    decode = subprocess.run(cmd, capture_output=True, text=True, creationflags=NO_WINDOW)
    if decode.returncode:
        raise RuntimeError('Whole WAV decode failed: ' + decode.stderr)
    en_cmd = [sys.executable, '-X', 'utf8', str(ROOT / 'qwen3-tts/build_translated_srt.py'),
              '--project', slug, '--language', 'en']
    translated = subprocess.run(en_cmd, cwd=ROOT, capture_output=True, text=True,
                                encoding='utf-8', creationflags=NO_WINDOW)
    if translated.returncode:
        raise RuntimeError('Provisional English captions failed: ' + translated.stderr)
    chunks = sorted((wav_path.parent / 'chunks').glob('*-scene.wav'))
    assert len(chunks) == scenes
    captions = {}
    for language, key in [('ko', 'captionsKo'), ('en', 'captionsEn')]:
        p = ROOT / manifest['paths'][key]
        captions[language] = dict(path=relative(p), sha256=sha(p),
                                  cueCount=len(re.findall(r'(?m)^\d+\s*$', p.read_text(encoding='utf-8-sig'))))
    return dict(slug=slug, samples=samples, sampleRate=rate, durationSeconds=duration,
                sceneCount=scenes, paragraphPairs=pairs, audioSha256=sha(wav_path),
                rawSceneHashes={p.name: sha(p) for p in chunks}, captions=captions,
                wholeWavDecode=dict(exitCode=0, command=cmd),
                captionTimingMode='provisional-character-weighted; word alignment and pixels pending',
                generatedNarrationComplete=True, currentNarrationApproved=False,
                humanWholeListeningApproved=False, finalMixedAsrApproved=False, finalVideoProduced=False)


def wait_current_review(slug, state, review):
    command = ['node', 'scripts/review-video-duplicates.cjs', slug, '--candidate-file',
               f'production/research/game-lighting-history/candidate-{slug[-2:]}.json', '--check']
    deadline = time.monotonic() + 1800
    while True:
        check_inputs(review)
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True,
                                encoding='utf-8', creationflags=NO_WINDOW)
        if result.returncode == 0:
            return
        state.update(status='awaiting-fresh-direct-inventory-review', current=slug,
                     preflightError=result.stderr, cudaAllocationStartedForCurrentEpisode=False)
        write(STATE, state)
        if 'Existing project evidence changed' not in result.stderr:
            raise RuntimeError(result.stderr)
        if time.monotonic() > deadline:
            raise TimeoutError('Fresh direct inventory review needed; preserve audio and restore research.')
        time.sleep(10)


def main():
    lease = read(LEASE)
    owner, token = lease['coordinator'], lease['token']
    if not any(p.pid == owner['pid'] and abs(p.create_time() - owner['createTime']) < .01
               for p in [psutil.Process(), *psutil.Process().parents()]):
        raise RuntimeError('Live cooperative coordinator ancestry required.')
    if lease['project'] != BATCH or lease['state'] != 'tts_running' or STATE.exists():
        raise RuntimeError('Unexpected lease scope or existing resume state.')
    review = read(READY)
    if review.get('allKoEnTextDirectlyReviewed') is not True or review['episodesToGenerate'] != SLUGS:
        raise RuntimeError('Full reviewed inputs required before CUDA.')
    check_inputs(review)
    old = read(BASE / 'remaining-tts-execution-v1.json')
    reused = old['completed'][0]
    if reused['slug'] != 'game-lighting-history-02' or reused['exitCode'] != 0:
        raise RuntimeError('Actual successful episode2 evidence required.')
    q = Path(lease['queueDir'])
    previous = read(BASE / 'research-preservation-before-remaining-tts-v1.json')
    assert all(sha(q / 'done' / p) == digest for p, digest in previous['beforeTtsCompleteMarkers'].items())
    pins = {name: sha(q / name) for name in previous['queueConfigHashes']}
    sources = {}
    queue_entry = next(arg for arg in lease['queueOwner']['command'][1:] if arg.endswith('.py'))
    for p in [Path(queue_entry),
              Path('C:/Users/eazuo/renderformer/lora_experiment/analysis/placement_focus/gpu_queue.py'),
              Path('C:/Users/eazuo/renderformer/lora_experiment/analysis/ladder_followup/gpu_queue.py')]:
        sources[str(p)] = sha(p)
    preservation = dict(token=token, boundaryStatus=lease['boundaryStatus'],
                        originalQueue=lease['queueOwner'], queueConfigHashes=pins,
                        queueSourceHashes=sources,
                        beforeTtsCompleteMarkers={p.name: sha(p) for p in sorted((q / 'done').glob('*.json'))},
                        previous348MarkersByteIdentical=True)
    write(BASE / 'research-preservation-before-remaining-tts-v2.json', preservation)
    state = dict(schemaVersion=2, token=token, pid=os.getpid(), createTime=psutil.Process().create_time(),
                 status='verifying-preserved-episode2', startedAt=time.time(), current=None,
                 episodesToGenerate=SLUGS, reusedCompletedEpisodes=['game-lighting-history-01','game-lighting-history-02'],
                 completed=[], verification=[], userEvidence=review['userEvidence'],
                 humanWholeListeningApproved=False, finalVideoProduced=False)
    write(STATE, state)
    try:
        state['verification'].append(verify_audio(reused))
        state['completed'].append({**reused, 'reusedWithoutSynthesis': True})
        write(STATE, state)
        for slug in SLUGS:
            wait_current_review(slug, state, review)
            current = read(LEASE)
            if current['token'] != token or current['coordinator'] != owner:
                raise RuntimeError('Lease changed; preserve foreign owner.')
            current.update(project=slug, batchProject=BATCH, currentEpisode=slug,
                           reviewedBatchInput=relative(READY), updatedAt=time.time())
            write(LEASE, current)
            write(ROOT / 'shared/output/gpu-handoff' / (token + '.json'), current)
            log_path = BASE / 'local' / (slug + '-tts-v2.log')
            command = [sys.executable, '-X', 'utf8', '-u', str(BASE / 'render-reviewed-episode-v1.py'),
                       '--project', slug, '--device', 'cuda:0', '--batch-size', '1']
            with log_path.open('x', encoding='utf-8') as log:
                child = subprocess.Popen(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
                                         creationflags=NO_WINDOW)
                p = psutil.Process(child.pid)
                state.update(status='synthesizing', current=slug, log=relative(log_path),
                             child=dict(pid=p.pid, createTime=p.create_time(), command=p.cmdline()),
                             modelAllocationStatus='see-current-child-log-and-resource-observation')
                write(STATE, state)
                code = child.wait()
            if code:
                raise RuntimeError(f'{slug} exited{code}; preserve chunks and inspect log.')
            manifest = read(ROOT / 'projects' / slug / 'project.json')
            out = ROOT / manifest['tts']['outputDir']
            stem = manifest['tts']['filenameStem']
            files = {ext: dict(path=relative(out / (stem + ext)), sha256=sha(out / (stem + ext)))
                     for ext in ['.wav', '.srt', '.timing.json']}
            done = dict(slug=slug, exitCode=0, files=files, finishedAt=time.time(),
                        reusedWithoutSynthesis=False, humanListeningApproved=False, finalVideoProduced=False)
            state.update(status='verifying-generated-audio', child=None)
            write(STATE, state)
            state['verification'].append(verify_audio(done))
            state['completed'].append(done)
            write(STATE, state)
        check_inputs(review)
        assert all(sha(q / 'done' / name) == digest for name, digest in preservation['beforeTtsCompleteMarkers'].items())
        assert all(sha(q / name) == digest for name, digest in pins.items())
        assert all(sha(Path(name)) == digest for name, digest in sources.items())
        state.update(status='all-remaining-tts-produced-and-decoded', exitCode=0,
                     current=None, finishedAt=time.time(), researchPreservationVerified=True)
        write(STATE, state)
        print(json.dumps(dict(status=state['status'], episodes=state['verification']), ensure_ascii=False), flush=True)
    except BaseException as exc:
        state.update(status='failed-preserve-chunks-and-restore-research', error=str(exc), exitCode=1)
        write(STATE, state)
        raise


if __name__ == '__main__':
    main()
