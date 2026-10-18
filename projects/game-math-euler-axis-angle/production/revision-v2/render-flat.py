"""Render the six authored M04 Manim explanations, explicitly and sequentially.

The default invocation is a CPU-only plan. --render is for the parent's completed
TTS/GPU handoff; an active exclusive voice lease blocks every media stage. This
wrapper never edits narration, lesson/timeline inputs, actual footage or policy.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import uuid

ROOT = Path(__file__).resolve().parents[4]
SLUG = 'game-math-euler-axis-angle'
PROJECT = ROOT / 'projects' / SLUG
HERE = PROJECT / 'production/revision-v2'
LOCAL = PROJECT / 'production/local/revision-v2'
OUT = LOCAL / 'flat'
WORK = OUT / 'work'
TIMELINE = HERE / 'timeline.json'
LESSON = HERE / 'lesson.json'
VISUALS = HERE / 'math_visuals.py'
MANIM_PYTHON = ROOT / 'manim/.venv/Scripts/python.exe'
CONTROL = ROOT / 'shared/publishing/video-production-control.json'
LEASE = ROOT / 'shared/output/GPU_HANDOFF.json'
SCENE_IDS = ('01', '13', '15', '24', '25', '26')
FPS = 60
WIDTH, HEIGHT = 1920, 1080
FONTS = (Path('C:/Windows/Fonts/malgun.ttf'), Path('C:/Windows/Fonts/consola.ttf'))
ENCODING = dict(codec='libx264', threads=4, preset='fast', crf=17,
                pixelFormat='yuv420p', colorRange='tv', colorSpace='bt709',
                timeBase='1/60', trackTimescale=60000, audio=False)
CREATE_FLAGS = (subprocess.CREATE_NO_WINDOW | subprocess.BELOW_NORMAL_PRIORITY_CLASS) if os.name == 'nt' else 0


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as source:
        for block in iter(lambda: source.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def canonical_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(',', ':')).encode('utf8')).hexdigest()


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    staging = path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp')
    staging.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    os.replace(staging, path)


def now():
    return datetime.now(timezone.utc).isoformat()


def check_selected():
    if read(CONTROL).get('selectedVideo') != SLUG:
        raise RuntimeError('M04 is not the selected video; no media job started.')


def check_handoff():
    check_selected()
    if LEASE.exists():
        raise RuntimeError('An exclusive GPU/voice lease is active. Wait for the parent handoff; no media job started.')


@contextmanager
def own_lock():
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / 'render-flat.lock.json'
    token = uuid.uuid4().hex
    try:
        with path.open('x', encoding='utf8') as handle:
            json.dump(dict(pid=os.getpid(), token=token, createdAt=now(), script=str(Path(__file__).resolve())), handle)
    except FileExistsError as exc:
        raise RuntimeError(f'Another flat render owns {path}. Inspect it; this wrapper will not remove a foreign lock.') from exc
    try:
        yield
    finally:
        if path.exists() and read(path).get('token') == token:
            path.unlink()


def output(command, **kwargs):
    return subprocess.check_output(command, creationflags=CREATE_FLAGS, **kwargs)


def dependencies():
    if not MANIM_PYTHON.is_file():
        raise FileNotFoundError(MANIM_PYTHON)
    ffmpeg, ffprobe = shutil.which('ffmpeg'), shutil.which('ffprobe')
    if not ffmpeg or not ffprobe:
        raise RuntimeError('Existing ffmpeg and ffprobe executables are required; no software is installed.')
    for path in FONTS:
        if not path.is_file():
            raise FileNotFoundError(path)
    runtime = json.loads(output([str(MANIM_PYTHON), '-c',
        'import importlib.metadata,json,sys;print(json.dumps(dict(python=sys.version,manim=importlib.metadata.version("manim"))))'],
        text=True, encoding='utf8'))
    return dict(manimPython=str(MANIM_PYTHON), **runtime,
                ffmpeg=ffmpeg, ffprobe=ffprobe,
                ffmpegVersion=output([ffmpeg, '-version'], text=True, encoding='utf8').splitlines()[0],
                ffprobeVersion=output([ffprobe, '-version'], text=True, encoding='utf8').splitlines()[0],
                fonts={str(path): sha(path) for path in FONTS})


def load_inputs(timeline_path, requested):
    check_selected()
    # An alternate file must not silently replace the measured production plan.
    if timeline_path.resolve() != TIMELINE.resolve():
        raise ValueError(f'Use the canonical timeline: {TIMELINE}')
    plan, lesson = read(timeline_path), read(LESSON)
    if plan.get('fps') != FPS or plan.get('slug') != SLUG:
        raise ValueError('The measured timeline must name M04 and use 60fps.')
    lesson_by_id = {str(s['id']).zfill(2): s for s in lesson['scenes']}
    scene_by_id = {str(s['id']).zfill(2): s for s in plan['scenes']}
    chosen = [sid for sid in SCENE_IDS if not requested or sid in requested]
    scenes = []
    for sid in chosen:
        scene, authored = scene_by_id[sid], lesson_by_id[sid]
        if scene.get('kind') != 'explanation':
            raise ValueError(f'{sid}: this wrapper only accepts explanation scenes, never actual footage.')
        frames, seconds = scene['frames'], scene['seconds']
        if type(frames) is not int or frames <= 0 or not math.isfinite(seconds):
            raise ValueError(f'{sid}: invalid exact duration.')
        if abs(seconds - frames / FPS) > 1e-8:
            raise ValueError(f'{sid}: seconds disagree with integer frames.')
        starts = scene['lineStarts']
        if len(starts) != len(authored['ko']) or len(authored['beats']) != len(starts):
            raise ValueError(f'{sid}: every narration line needs an aligned visual beat.')
        if not starts or any(not math.isfinite(t) or t < 0 or t >= seconds for t in starts):
            raise ValueError(f'{sid}: lineStarts lie outside the scene.')
        if any(a > b for a, b in zip(starts, starts[1:])):
            raise ValueError(f'{sid}: lineStarts must be monotonic.')
        scenes.append((sid, scene, authored))
    hashes = {str(path): sha(path) for path in (timeline_path, LESSON, VISUALS, Path(__file__).resolve())}
    return scenes, hashes


def unchanged_inputs(hashes):
    for path, expected in hashes.items():
        if sha(path) != expected:
            raise RuntimeError(f'An active render input changed: {path}. Stop and rebuild from the current measured plan.')


def probe(path, ffprobe, exact_frames=None, normalized=False):
    report = json.loads(output([ffprobe, '-v', 'error', '-show_streams', '-of', 'json', str(path)],
                               text=True, encoding='utf8'))
    streams = report['streams']
    if len(streams) != 1 or streams[0].get('codec_type') != 'video':
        raise ValueError(f'{path}: exactly one video stream and no audio are required.')
    video = streams[0]
    if (video['width'], video['height']) != (WIDTH, HEIGHT):
        raise ValueError(f'{path}: expected native FHD, found {video["width"]}x{video["height"]}.')
    for key in ('r_frame_rate', 'avg_frame_rate'):
        if Fraction(video[key]) != FPS:
            raise ValueError(f'{path}: {key} is not 60fps.')
    if not str(video.get('nb_frames', '')).isdigit():
        raise ValueError(f'{path}: exact encoded frame count is unavailable.')
    frames = int(video['nb_frames'])
    if exact_frames is not None and frames != exact_frames:
        raise ValueError(f'{path}: {frames} frames != measured {exact_frames}.')
    if normalized:
        for key, expected in dict(pix_fmt='yuv420p', color_range='tv', color_space='bt709',
                                  color_primaries='bt709', color_transfer='bt709', sample_aspect_ratio='1:1').items():
            if video.get(key) != expected:
                raise ValueError(f'{path}: {key}={video.get(key)!r}, expected {expected!r}.')
        duration = Fraction(int(video['duration_ts'])) * Fraction(video['time_base'])
        if duration != Fraction(frames, FPS):
            raise ValueError(f'{path}: stream duration {duration} differs from {frames}/60.')
    return video


def static_tail(path, frames, ffmpeg):
    """Prove the last three decoded frames are identical before <=2-frame repair."""
    count = min(3, frames)
    if count < 3:
        raise ValueError('A short explanation cannot supply the required static-tail evidence.')
    command = [ffmpeg, '-hide_banner', '-loglevel', 'error', '-threads', '2',
               '-ss', f'{(frames - count) / FPS:.12f}', '-i', str(path), '-map', '0:v:0',
               '-an', '-sn', '-dn', '-frames:v', str(count), '-fps_mode', 'passthrough',
               '-pix_fmt', 'rgb24', '-f', 'rawvideo', 'pipe:1']
    data = output(command)
    size = WIDTH * HEIGHT * 3
    if len(data) != count * size:
        raise ValueError('Static-tail verification could not decode exactly three final frames.')
    hashes = [hashlib.sha256(data[i * size:(i + 1) * size]).hexdigest() for i in range(count)]
    if len(set(hashes)) != 1:
        raise ValueError('Frame repair refused: the final explanation state is moving.')
    return dict(method='identical decoded RGB24 frames', lastFrameIndices=list(range(frames-count, frames)),
                sha256=hashes, static=True, command=command)


def run_media(command, log_path, hashes, env=None):
    check_handoff()
    unchanged_inputs(hashes)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open('w', encoding='utf8') as log:
        result = subprocess.run(command, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT,
                                creationflags=CREATE_FLAGS)
    if result.returncode:
        raise RuntimeError(f'Media stage failed ({result.returncode}); see {log_path}')
    unchanged_inputs(hashes)


def preserve_previous(target, receipt):
    if not target.exists() and not receipt.exists():
        return
    destination = OUT / 'history' / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S') + '-' + uuid.uuid4().hex[:8])
    destination.mkdir(parents=True, exist_ok=False)
    for path in (target, receipt):
        if path.exists():
            path.rename(destination / path.name)


def render_one(sid, scene, authored, hashes, runtime, args):
    timing = dict(id=sid, kind=scene['kind'], frames=scene['frames'], seconds=scene['seconds'], lineStarts=scene['lineStarts'])
    signature_data = dict(timing=timing, lesson=authored, visualsSha256=hashes[str(VISUALS)],
                          wrapperSha256=hashes[str(Path(__file__).resolve())], runtime=runtime, encoding=ENCODING,
                          frameRepair='explanation-static-tail-only; at most two frames')
    signature = canonical_hash(signature_data)
    target, receipt = OUT / f'{sid}.mp4', OUT / f'{sid}.json'
    if target.exists() and receipt.exists() and not args.force:
        prior = read(receipt)
        if prior.get('signature') == signature and prior.get('outputSha256') == sha(target):
            print(json.dumps(dict(scene=sid, status='cached', frames=scene['frames'], output=str(target))), flush=True)
            return prior

    work = WORK / sid / signature
    work.mkdir(parents=True, exist_ok=True)
    raw_receipt = work / 'manim.json'
    raw = None
    if raw_receipt.exists() and not args.force:
        previous = read(raw_receipt)
        candidate = Path(previous['output'])
        if previous.get('signature') == signature and candidate.exists() and previous.get('sha256') == sha(candidate):
            raw = candidate
    manim_command = [str(MANIM_PYTHON), '-m', 'manim', '--renderer', 'cairo', '--format', 'mp4',
                     '-r', '1920,1080', '--fps', '60', '--media_dir', str(work / 'manim'),
                     '-o', f'{sid}-manim', str(VISUALS), f'Scene{sid}']
    if raw is None:
        env = os.environ.copy()
        env.update(MATH_RENDER_TIMING=str(TIMELINE.resolve()), PYTHONUTF8='1', PYTHONIOENCODING='utf-8',
                   OMP_NUM_THREADS='4', MKL_NUM_THREADS='4', OPENBLAS_NUM_THREADS='4')
        save(work / 'manim-command.json', dict(command=manim_command, MATH_RENDER_TIMING=env['MATH_RENDER_TIMING']))
        run_media(manim_command, work / 'manim.log', hashes, env)
        candidates = list((work / 'manim').rglob(f'{sid}-manim.mp4'))
        if len(candidates) != 1:
            raise RuntimeError(f'{sid}: expected one Manim final movie, found {len(candidates)}.')
        raw = candidates[0]
        raw_probe = probe(raw, runtime['ffprobe'])
        save(raw_receipt, dict(signature=signature, output=str(raw), sha256=sha(raw), probe=raw_probe, command=manim_command))
    else:
        raw_probe = probe(raw, runtime['ffprobe'])
    raw_frames = int(raw_probe['nb_frames'])
    difference = scene['frames'] - raw_frames
    tail = None
    if difference:
        if abs(difference) > 2:
            raise ValueError(f'{sid}: Manim has {raw_frames} frames, target {scene["frames"]}. Refuse an adjustment beyond two frames.')
        check_handoff()
        unchanged_inputs(hashes)
        tail = static_tail(raw, raw_frames, runtime['ffmpeg'])
    filters = ['scale=in_range=auto:out_range=tv:out_color_matrix=bt709', 'format=yuv420p',
               'setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709', 'setsar=1']
    if difference > 0:
        filters.append(f'tpad=stop_mode=clone:stop={difference}')
    filters += [f'trim=end_frame={scene["frames"]}', 'settb=expr=1/60', 'setpts=N']
    staging = work / f'{sid}-{uuid.uuid4().hex}.mp4'
    command = [runtime['ffmpeg'], '-hide_banner', '-loglevel', 'warning', '-y', '-i', str(raw),
               '-map', '0:v:0', '-an', '-sn', '-dn', '-vf', ','.join(filters), '-frames:v', str(scene['frames']),
               '-c:v', 'libx264', '-threads', '4', '-preset', 'fast', '-crf', '17', '-pix_fmt', 'yuv420p',
               '-r', '60', '-fps_mode', 'cfr', '-enc_time_base', '1:60', '-color_range', 'tv',
               '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709',
               '-video_track_timescale', '60000', '-movflags', '+faststart', str(staging)]
    save(work / 'normalize-command.json', command)
    run_media(command, work / 'normalize.log', hashes)
    final_probe = probe(staging, runtime['ffprobe'], exact_frames=scene['frames'], normalized=True)
    digest = sha(staging)
    unchanged_inputs(hashes)
    preserve_previous(target, receipt)
    os.replace(staging, target)
    report = dict(schemaVersion=1, scene=sid, renderedAt=now(), signature=signature, signatureInputs=signature_data,
                  inputHashes=hashes, output=str(target), outputSha256=digest,
                  frames=scene['frames'], seconds=scene['frames']/FPS, stream=final_probe,
                  renderer='Manim 0.20.1 Cairo; editable authored mathematical diagrams',
                  timingEnvironment=dict(MATH_RENDER_TIMING=str(TIMELINE.resolve())),
                  originalManim=dict(path=str(raw), sha256=sha(raw), stream=raw_probe, command=manim_command),
                  frameAdjustment=dict(frames=difference, action='none' if not difference else ('clone static last frame' if difference>0 else 'trim static last frames'),
                                       staticTailEvidence=tail, maximumFrames=2, actualFootageModified=False),
                  normalizeCommand=command, colorRange='tv', audioStreams=0,
                  captionReserve='Existing white palette; content above y=880; fixed final captions centered at 960,970.',
                  visualReview='Representative layout proof exists; current six-scene moving and caption review pending parent QA.',
                  fullDecode='Pending parent current-output decode/PTS/audio-integrity QA; not repeatedly decoded here.')
    save(receipt, report)
    print(json.dumps(dict(scene=sid, status='rendered', frames=scene['frames'], output=str(target))), flush=True)
    return report


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--timeline', type=Path, default=TIMELINE, help='Canonical measured timeline (alternate paths are rejected).')
    ap.add_argument('--scene', action='append', choices=SCENE_IDS, help='Select a scene; repeat as needed. Default: all six.')
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument('--render', action='store_true', help='Start sequential media jobs only after the parent TTS/GPU handoff.')
    mode.add_argument('--check-inputs', action='store_true', help='Validate current timeline and dependencies without starting a media job.')
    ap.add_argument('--force', action='store_true', help='Ignore completed scene/raw hash caches during --render.')
    args = ap.parse_args()
    if args.force and not args.render:
        ap.error('--force requires --render.')
    check_selected()
    if not args.timeline.exists():
        if args.render or args.check_inputs:
            raise FileNotFoundError(f'The measured canonical timeline is not ready: {args.timeline}')
        print(json.dumps(dict(status='awaiting-measured-timeline', timeline=str(TIMELINE),
                              scenes=list(SCENE_IDS), mediaJobsStarted=False, renderRequires='--render after parent handoff')))
        return
    scenes, hashes = load_inputs(args.timeline, args.scene)
    runtime = dependencies()
    if not args.render:
        print(json.dumps(dict(status='inputs-validated', mediaJobsStarted=False, exclusiveLeaseActive=LEASE.exists(),
                              timeline=str(TIMELINE), inputHashes=hashes, runtime=runtime,
                              scenes=[dict(id=sid, frames=s['frames'], seconds=s['seconds'], output=str(OUT/f'{sid}.mp4')) for sid,s,_ in scenes],
                              renderRequires='--render after parent handoff'), ensure_ascii=False))
        return
    check_handoff()
    with own_lock():
        reports = []
        for sid, scene, authored in scenes:
            check_handoff()
            unchanged_inputs(hashes)
            reports.append(render_one(sid, scene, authored, hashes, runtime, args))
        save(OUT / 'flat-render-report.json', dict(schemaVersion=1, completedAt=now(), selectedVideo=SLUG,
                                                 timeline=str(TIMELINE), inputHashes=hashes, reports=reports))


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, ValueError, FileNotFoundError, subprocess.CalledProcessError) as error:
        print(f'ERROR: {error}', file=sys.stderr)
        sys.exit(2)
