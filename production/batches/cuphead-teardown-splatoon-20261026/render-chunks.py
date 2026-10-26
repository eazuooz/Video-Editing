"""Serial, exact-range MC rendering for the four explicitly authorized Shorts.

Does not start servers, alter selection, kill processes or overwrite attempts.
Each existing project wrapper creates a fresh browser. Run --check for code/input
inspection only; real rendering and media validation require an explicit --run.
"""
from pathlib import Path
import argparse
import datetime
import hashlib
import importlib
import inspect
import json
import os
import re
import subprocess
import sys
import urllib.request
from fractions import Fraction

R = Path(__file__).resolve().parents[3]
B = Path(__file__).resolve().parent
MEDIA = Path('C:/Users/1/Videos/YamyamProduction/cuphead-teardown-splatoon-20261026')
PROJECTS = {
    'shorts-cuphead-animation-tick': ('animation-tick-v1', 9275, 'vite.cuphead.config.ts'),
    'shorts-teardown-spray-palette': ('spray-palette-v1', 9277, 'vite.teardown.config.ts'),
    'shorts-splatoon-ink-readability': ('ink-readability-v1', 9278, 'vite.ink-readability.config.ts'),
    'shorts-splatoon-surface-ink': ('surface-ink-v1', 9276, 'vite.surface-ink.config.ts'),
}


def read(p):
    return json.loads(Path(p).read_text(encoding='utf8'))


def sha(p):
    with Path(p).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def write_new(p, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('x', encoding='utf8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')


def run(command, timeout=1800):
    return subprocess.check_output(command, cwd=R, text=True, encoding='utf8',
        errors='replace', timeout=timeout, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))


def media_proof(file, frames):
    """Decode/count frame timestamps, not just trust the container duration."""
    data = json.loads(run(['ffprobe', '-v', 'error', '-show_streams', '-show_frames',
        '-show_data_hash', 'sha256', '-show_entries',
        'stream=codec_type,codec_name,codec_tag_string,profile,width,height,pix_fmt,r_frame_rate,avg_frame_rate,time_base,extradata_hash:frame=best_effort_timestamp_time',
        '-of', 'json', str(file)], timeout=300))
    streams = data.get('streams', [])
    if len(streams) != 1 or streams[0].get('codec_type') != 'video':
        raise RuntimeError('Expected one silent video stream: ' + str(file))
    v = streams[0]
    if ((v.get('width'), v.get('height')) != (1080, 1920)
            or Fraction(v.get('avg_frame_rate', '0/1')) != 60
            or Fraction(v.get('r_frame_rate', '0/1')) != 60):
        raise RuntimeError('Expected native portrait 1080x1920 at 60fps: ' + str(file))
    pts = [float(f['best_effort_timestamp_time']) for f in data.get('frames', [])]
    if len(pts) != frames or any(abs(t-i/60) > .000002 for i, t in enumerate(pts)):
        raise RuntimeError('Wrong decoded frame count / nonzero origin / irregular PTS: ' + str(file))
    # The finalizer performs its complete decode/audio QA separately as well.
    return {'sha256': sha(file), 'frames': frames, 'stream': v,
        'firstPts': pts[0], 'lastPts': pts[-1], 'frameStepSeconds': 1/60,
        'decodedTimestampCount': len(pts), 'audioStreams': 0}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--slug', choices=list(PROJECTS), required=True)
    ap.add_argument('--name', required=True, help='Unique final visual filename stem.')
    ap.add_argument('--chunk-frames', type=int, default=480)
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument('--check', action='store_true')
    mode.add_argument('--run', action='store_true')
    a = ap.parse_args()
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]{1,80}', a.name):
        raise RuntimeError('Use a safe unique output name (at most 81 characters).')
    if not 360 <= a.chunk_frames <= 600:
        raise RuntimeError('Use bounded chunks of 360..600 frames.')
    revision, port, vite = PROJECTS[a.slug]
    P = R/'projects'/a.slug/'production'
    L = MEDIA/a.slug/'local'
    if (P/'local').resolve() != L.resolve():
        raise RuntimeError('The project local directory must resolve to its exact C: media root.')
    sys.path.insert(0, str(P))
    ar = importlib.import_module('audio_revision')
    if 'require_current_selection' in inspect.signature(ar.guard).parameters:
        ar.guard(require_current_selection=not a.check)
    else:
        # Older completed Cuphead has a selected-only guard; keep its contract.
        ar.guard()
    timing, config = read(P/'visual-timing.json'), read(P/'visual-config.json')
    captions = read(P.parent/'script/captions.json')
    if (timing != read(L/'visual-timing.json') or timing.get('revision') != revision
            or timing.get('previewOnly') is not False or timing.get('fps') != 60
            or timing.get('frames') != captions.get('frames')
            or timing.get('timingInputs', {}).get('voiceSha256') != sha(ar.VOICE)):
        raise RuntimeError('Current complete actual-PCM timeline and captions must match.')
    frames = int(timing['frames'])
    inputs = [P/'visual-timing.json', P/'visual-config.json', P/'render-visual.cjs',
        P/'audio_revision.py', P.parent/'script/captions.json', ar.VOICE,
        R/'motion-canvas/render-worker.html', R/'motion-canvas'/vite,
        R/'motion-canvas/src/styles/research-dark.ts', Path(__file__)]
    inputs += sorted((R/'motion-canvas/src/projects'/a.slug).glob('*.ts*'))
    for filename in ['video-source-inputs.json', 'visual_revision.py', 'audio-source-inputs.json']:
        if (P/filename).is_file(): inputs.append(P/filename)
    fingerprints = {str(p.resolve()): sha(p) for p in inputs}
    spec = {'slug': a.slug, 'revision': revision, 'name': a.name, 'frames': frames,
        'fps': 60, 'width': 1080, 'height': 1920, 'chunkFrames': a.chunk_frames,
        'inputHashes': fingerprints}
    digest = hashlib.sha256(json.dumps(spec, sort_keys=True).encode()).hexdigest()
    ranges = [(start, min(a.chunk_frames, frames-start)) for start in range(0, frames, a.chunk_frames)]
    if a.check:
        print(json.dumps({'mode': 'read-only-check', 'inputFingerprint': digest,
            'ranges': ranges, 'serverPort': port, 'jobsStarted': 0, **spec}, ensure_ascii=False))
        return

    def guard():
        ar.guard()
        ar.assert_no_game_apps()
        if ar.LEASE.exists():
            raise RuntimeError('Foreign GPU/costly lease preserved; wait for the serial owner.')
        if any(sha(Path(p)) != h for p, h in fingerprints.items()):
            raise RuntimeError('Production inputs changed; preserve the old attempt and select a new version.')

    guard()
    with urllib.request.urlopen(f'http://127.0.0.1:{port}/__yamyam_production_scope', timeout=10) as response:
        scope = json.load(response)
    output_root = L/'motion-canvas-output'
    if (scope.get('slug') != a.slug or scope.get('revision') != revision
            or Path(scope.get('output', '')).resolve() != output_root.resolve()
            or (a.slug != 'shorts-cuphead-animation-tick' and
                (scope.get('productionWatch') != 'disabled' or scope.get('encoderWebSocket') is not True))):
        raise RuntimeError('Wrong/unrestarted production server. Root must restart its own frozen-watch server.')
    folder = L/'chunk-renders'/a.name
    plan = folder/'plan.json'
    plan_value = {'schemaVersion': 1, 'inputFingerprint': digest, 'spec': spec, 'ranges': ranges}
    if plan.exists():
        old = read(plan)
        if old['inputFingerprint'] != digest or old['spec'] != spec:
            raise RuntimeError('This chunk name belongs to different inputs. Preserve it and use another name.')
    else:
        write_new(plan, plan_value)
    # Does not replace the existing GPU lease; wrappers require that lease absent.
    # This lock prevents two members of this finite batch from encoding together.
    lock = MEDIA/'serial-mc-render.lock'
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        raise RuntimeError('Another finite-batch render lock exists. Preserve it; do not steal or auto-delete it.')
    lock_data = json.dumps({'pid': os.getpid(), 'slug': a.slug, 'name': a.name,
        'inputFingerprint': digest, 'startedAt': datetime.datetime.now(datetime.timezone.utc).isoformat()}).encode()
    os.write(fd, lock_data); os.close(fd)
    try:
        chunks = []
        signature = None
        for index, (first, count) in enumerate(ranges):
            guard()
            verified = folder/f'part-{index:03d}-verified.json'
            if verified.exists():
                item = read(verified)
                if (item['inputFingerprint'] != digest or item['firstFrame'] != first
                        or item['frames'] != count or sha(item['receipt']) != item['receiptSha256']):
                    raise RuntimeError('Existing verified chunk evidence changed.')
                proof = media_proof(Path(item['output']), count)
                if proof != item['mediaProof']:
                    raise RuntimeError('Existing verified chunk media changed.')
                print(f'Reused verified chunk {index+1}/{len(ranges)}: {first}..{first+count-1}', flush=True)
            else:
                attempt = 1
                while True:
                    stem = f'{a.name}-part-{index:03d}-a{attempt:03d}'
                    outfile, receipt = output_root/(stem+'.mp4'), L/(stem+'-render.json')
                    log, request = folder/(stem+'.log'), folder/(stem+'-request.json')
                    if not any(p.exists() for p in [outfile, receipt, log, request]): break
                    attempt += 1
                write_new(request, {'inputFingerprint': digest, 'firstFrame': first, 'frames': count,
                    'command': ['node', str(P/'render-visual.cjs'), stem, str(first), str(count)]})
                print(f'Rendering chunk {index+1}/{len(ranges)}: {first}..{first+count-1}', flush=True)
                with log.open('x', encoding='utf8') as handle:
                    result = subprocess.run(['node', str(P/'render-visual.cjs'), stem, str(first), str(count)],
                        cwd=R, stdout=handle, stderr=subprocess.STDOUT,
                        creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
                if result.returncode:
                    raise RuntimeError(f'Chunk failed; partial output/log preserved: {log}. Root checks orphan jobs before rerun.')
                guard()
                rendered = read(receipt)
                if (rendered.get('slug') != a.slug or rendered.get('revision') != revision
                        or rendered.get('done') is not True or rendered.get('result') != 0
                        or rendered.get('errors') or rendered.get('firstFrame') != first
                        or rendered.get('frames') != count or Path(rendered.get('output', '')).resolve() != outfile.resolve()):
                    raise RuntimeError('The project renderer did not attest this exact successful chunk.')
                proof = media_proof(outfile, count)
                if rendered.get('outputSha256') and rendered['outputSha256'] != proof['sha256']:
                    raise RuntimeError('Chunk hash differs from its renderer receipt.')
                item = {'inputFingerprint': digest, 'firstFrame': first, 'frames': count,
                    'output': str(outfile), 'receipt': str(receipt), 'receiptSha256': sha(receipt), 'mediaProof': proof}
                write_new(verified, item)
            stream = item['mediaProof']['stream']
            if signature is not None and stream != signature:
                raise RuntimeError('Chunk codec/pixel format/time base/extradata differ; unsafe to concatenate-copy.')
            signature = stream
            chunks.append(item)

        guard()
        target, receipt = output_root/(a.name+'.mp4'), L/(a.name+'-render.json')
        if receipt.exists():
            prior = read(receipt)
            if (prior.get('inputFingerprint') == digest and prior.get('done') is True
                    and prior.get('outputSha256') == sha(target) and prior.get('frames') == frames):
                media_proof(target, frames)
                print(json.dumps({'alreadyComplete': True, 'output': str(target), 'receipt': str(receipt)}))
                return
            raise RuntimeError('Preserve the existing final receipt; do not overwrite it.')
        if target.exists():
            raise RuntimeError('Partial final MP4 exists without a receipt; preserve it and use a new final name.')
        concat = folder/'concat.ffconcat'
        text = 'ffconcat version 1.0\n'
        for item in chunks:
            filename = Path(item['output']).as_posix()
            if "'" in filename or '\n' in filename: raise RuntimeError('Unsafe concat path.')
            text += f"file '{filename}'\nduration {item['frames']/60:.12f}\n"
        if concat.exists():
            if concat.read_text(encoding='utf8') != text: raise RuntimeError('Concat manifest changed.')
        else:
            with concat.open('x', encoding='utf8') as f: f.write(text)
        run(['ffmpeg', '-nostdin', '-v', 'error', '-n', '-f', 'concat', '-safe', '0', '-i', str(concat),
            '-map', '0:v:0', '-an', '-c:v', 'copy', '-video_track_timescale', '60000',
            '-movflags', '+faststart', str(target)], timeout=300)
        proof = media_proof(target, frames)
        guard()
        record = {'schemaVersion': 1, 'slug': a.slug, 'revision': revision, 'done': True, 'result': 0,
            'errors': [], 'frame': frames-1, 'firstFrame': 0, 'frames': frames, 'fps': 60,
            'output': str(target), 'outputSha256': proof['sha256'], 'fullCurrentTimeline': True,
            'timingSha256': sha(P/'visual-timing.json'), 'configSha256': sha(P/'visual-config.json'),
            'inputHashes': config.get('inputs'), 'inputFingerprint': digest,
            'method': 'serial-fresh-browser-exact-ranges-then-lossless-concat-copy',
            'chunkPlan': str(plan), 'chunks': chunks, 'mediaProof': proof,
            'fullListening': 'pending', 'movingVisualReview': 'pending'}
        write_new(receipt, record)
        print(json.dumps({'output': str(target), 'receipt': str(receipt), 'sha256': proof['sha256']}))
    finally:
        # Only remove the lock created by this invocation and only if unchanged.
        if lock.is_file() and lock.read_bytes() == lock_data:
            lock.unlink()


if __name__ == '__main__':
    main()
