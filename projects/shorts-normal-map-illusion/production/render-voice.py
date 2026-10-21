"""One finite batch1 paragraph GPU job; same approved voice, no foreign-job mutation."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import time
import uuid

import psutil

from audio_revision import P, R, L, VOICE, REVISION, read, guard

LEASE = R / 'shared/output/GPU_HANDOFF.json'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def wait_for_gpu(seconds):
    deadline = time.monotonic() + seconds
    announced = None
    while True:
        guard()
        if LEASE.exists():
            state = read(LEASE)
            owner = state.get('coordinator', {})
            if owner.get('pid'):
                try:
                    live = abs(psutil.Process(owner['pid']).create_time() - owner.get('createTime', 0)) < .01
                except psutil.NoSuchProcess:
                    live = False
                if not live:
                    raise RuntimeError('Foreign GPU owner exited unexpectedly; preserve its lease for inspection.')
            marker = (state.get('token'), state.get('state'))
            if marker != announced:
                print(json.dumps({'waitingForExistingLease': state.get('project'), 'state': state.get('state'),
                                  'foreignWorkPreserved': True}, ensure_ascii=False), flush=True)
                announced = marker
        else:
            raw = subprocess.check_output(['nvidia-smi', '--query-gpu=memory.free,utilization.gpu',
                                           '--format=csv,noheader,nounits'], text=True)
            free, utilization = [int(value.strip()) for value in raw.splitlines()[0].split(',')]
            clients = subprocess.check_output(['nvidia-smi', '--query-compute-apps=pid,process_name',
                                               '--format=csv,noheader'], text=True)
            if free >= 7500 and utilization < 20 and not any('python' in line.lower() for line in clients.splitlines()):
                print(json.dumps({'gpuSlotAvailable': True, 'freeMiB': free, 'utilization': utilization}), flush=True)
                return
            marker = ('capacity', free // 512, utilization // 20)
            if marker != announced:
                print(json.dumps({'waitingForGpuCapacity': True, 'freeMiB': free, 'utilization': utilization}), flush=True)
                announced = marker
        if time.monotonic() >= deadline:
            raise RuntimeError('Finite GPU wait expired; foreign work and selected audio inputs preserved.')
        time.sleep(min(15, max(0, deadline - time.monotonic())))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--release-script-sha256', required=True,
                        help='Root releases this exact full display script after inspecting actual game source.')
    parser.add_argument('--wait-for-gpu-seconds', type=int, default=0)
    args = parser.parse_args()
    control = guard()
    manifest = read(P / 'production/tts-manifest.json')
    manifest_sha = sha(P / 'production/tts-manifest.json')
    assert manifest['revision'] == REVISION and manifest['tts']['renderMode'] == 'line'
    assert sha(P / 'script/narration.ko.json') == args.release_script_sha256
    assert read(P / 'planning/production-plan.json')['status'] == 'ready-for-narration'
    if args.wait_for_gpu_seconds:
        assert 0 < args.wait_for_gpu_seconds <= 7200
        wait_for_gpu(args.wait_for_gpu_seconds)
        control = guard()
        assert sha(P / 'script/narration.ko.json') == args.release_script_sha256
        assert sha(P / 'production/tts-manifest.json') == manifest_sha, 'Manifest changed during wait; restart with reviewed current settings.'
    assert not LEASE.exists(), 'An existing GPU lease is preserved.'
    assert not VOICE.exists(), 'Reuse existing successful v2 PCM rather than synthesizing again.'
    assert not (L / 'tts-execution.json').exists(), 'Inspect/version the previous finite execution before retry.'
    prepared = read(R / manifest['paths']['script'])
    assert prepared['derivation']['displayScriptSha256'] == args.release_script_sha256
    assert prepared['derivation']['clausesSha256'] == sha(P / 'script/clauses.json')
    raw = subprocess.check_output(['nvidia-smi', '--query-gpu=memory.free,memory.total,utilization.gpu',
                                   '--format=csv,noheader,nounits'], text=True)
    free, total, utilization = [int(x.strip()) for x in raw.splitlines()[0].split(',')]
    assert utilization < 20, ('Existing GPU activity preserved', utilization)
    assert free >= 7500, ('Insufficient GPU capacity; no foreign applications stopped', free)
    clients = subprocess.check_output(['nvidia-smi', '--query-compute-apps=pid,process_name', '--format=csv,noheader'], text=True)
    assert not any('python' in line.lower() for line in clients.splitlines()), 'Another GPU Python job is preserved.'
    paths = {'script': manifest['paths']['script'], 'displayScript': f'projects/{P.name}/script/narration.ko.json',
             'clauses': f'projects/{P.name}/script/clauses.json', 'manifest': f'projects/{P.name}/production/tts-manifest.json',
             'reference': manifest['tts']['reference'], 'referenceText': manifest['tts']['referenceText']}
    me = psutil.Process()
    token = str(uuid.uuid4())
    record = {'schemaVersion': 2, 'project': P.name, 'revision': REVISION, 'token': token,
              'state': 'gpu_granted_to_tts', 'requestedAt': time.time(),
              'coordinator': {'pid': me.pid, 'createTime': me.create_time()},
              'gpuBefore': {'freeMiB': free, 'totalMiB': total, 'utilization': utilization},
              'allocatorLimitMiB': 6144, 'foreignProcessesPaused': [],
              'userEvidence': control['shortsDirectSelection'].get('latestUserEvidence', control['shortsDirectSelection']['userEvidence']),
              'inputs': {key: sha(R / value) for key, value in paths.items()},
              'launcherSha256': sha(__file__), 'assemblyScriptSha256': sha(P / 'production/assemble-paragraphs.py'),
              'renderMode': 'meaningful-paragraph-line; sequential-batch1; one-model-load', 'speechSpeed': 1}
    L.mkdir(parents=True, exist_ok=True)
    with LEASE.open('x', encoding='utf8') as handle:
        json.dump(record, handle, ensure_ascii=False, indent=2)
    code = 1
    try:
        import torch
        torch.set_num_threads(4)
        torch.set_num_interop_threads(2)
        torch.cuda.set_per_process_memory_fraction(6144 * 1048576 / torch.cuda.get_device_properties(0).total_memory, 0)
        sys.path.insert(0, str(R / 'qwen3-tts'))
        import render_narration as worker
        # The shared generic reduced-memory configuration validates scene mode only.
        # This local explicit finite profile uses the same model with sequential batch1
        # paragraph takes and the same measured allocator cap; no shared entrypoint changes.
        tts = manifest['tts']
        worker.SCRIPT_PATH = R / manifest['paths']['script']
        worker.REFERENCE = R / tts['reference']
        worker.REFERENCE_TEXT_PATH = R / tts['referenceText']
        worker.MODEL_DIR = R / tts['model']
        worker.OUTPUT_DIR = R / tts['outputDir']
        worker.CHUNK_DIR = worker.OUTPUT_DIR / 'chunks'
        worker.LANGUAGE = tts['language']
        worker.RENDER_MODE = 'line'
        worker.INFERENCE_DEVICE = 'cuda:0'
        worker.LINE_GAP_SECONDS = float(tts['lineGapSeconds'])
        worker.SCENE_GAP_SECONDS = 0
        worker.EXAMPLE_SECONDS = 0
        worker.NARRATION_PLACEMENT = manifest['editing']['narrationPlacement']
        worker.TAIL_RATIO_THRESHOLD = float(tts['tailRatioThreshold'])
        worker.DECAY_MS_THRESHOLD = float(tts['tailDecayMsThreshold'])
        worker.MAX_RENDER_ATTEMPTS = int(tts['maxRenderAttempts'])
        worker.MAX_NEW_TOKENS = int(tts['maxNewTokens'])
        worker.FADE_SECONDS = float(tts['edgeFadeSeconds'])
        worker.GPU_MINIMUM_FREE_MIB = 7500
        worker.load_tts_dependencies()
        items = worker.build_render_items(worker.load_jobs())
        assert len(items) == sum(len(scene['lines']) for scene in prepared['scenes'])
        worker.render_chunks(items, 1)
        record['takes'] = []
        for item in items:
            samples, rate = worker._read_mono(item.path)
            tail, decay = worker._tail_ratio(samples, rate), worker._tail_decay_ms(samples, rate)
            record['takes'].append({'key': item.key, 'path': item.path.relative_to(R).as_posix(),
                                    'sha256': sha(item.path), 'durationSeconds': len(samples) / rate,
                                    'tailRatio': tail, 'tailDecayMs': decay if decay != float('inf') else None,
                                    'endingHeuristicPassed': worker._passes_quality(tail, decay),
                                    'fullAsrAndListening': 'pending'})
        assert all(sha(R / value) == record['inputs'][key] for key, value in paths.items()), 'Audio inputs changed during generation.'
        guard()
        spec = importlib.util.spec_from_file_location('assemble_paragraphs', P / 'production/assemble-paragraphs.py')
        assembler = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(assembler)
        assembler.main()
        record['voiceSha256'] = sha(VOICE)
        code = 0
    except BaseException as error:
        record['failure'] = {'type': type(error).__name__, 'message': str(error),
                             'automaticRetry': False, 'rawOutputsPreserved': True}
        raise
    finally:
        if 'torch' in locals() and torch.cuda.is_initialized():
            record.update(peakAllocatedMiB=torch.cuda.max_memory_allocated() / 1048576,
                          peakReservedMiB=torch.cuda.max_memory_reserved() / 1048576)
        record.update(state='finished' if code == 0 else 'failed', finishedAt=time.time(), exitCode=code)
        (L / 'tts-execution.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
        if LEASE.exists() and read(LEASE).get('token') == token:
            LEASE.unlink()


if __name__ == '__main__':
    main()
