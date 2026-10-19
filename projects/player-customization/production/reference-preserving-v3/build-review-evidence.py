"""Export D21 caption/cut/annotation review evidence in one video decode.

Example (run only after the current captioned master exists)::

  python build-review-evidence.py --plan .../edit-plan.json \
    --caption-layout .../caption-layout.json \
    --caption-alignment .../caption-alignment.json --video .../captioned.mp4

One FFmpeg invocation decodes video and selects deduplicated native frames.
Pillow creates375px-wide copies and6-or9-image contact boards FROM those PNGs.
All artifacts stay below this revision's ignored local/inspection directory.
Existing successful, hash-identical evidence is reused without another decode.
No media job runs on import or --help. Sampling supplies evidence for direct
review; it never certifies continuous playback, listening, or every-frame QA.
"""
from __future__ import annotations

import argparse
import bisect
import datetime
from fractions import Fraction
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
LOCAL = ROOT / 'projects/player-customization/production/local/reference-preserving-v3'
INSPECTION = LOCAL / 'inspection'
DEFAULT_OUT = INSPECTION / 'final-evidence'
FF_DIR = Path('C:/Users/1/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0-full_build/bin')
FPS, WIDTH, HEIGHT = 60, 1920, 1080


class EvidenceError(RuntimeError):
    pass


def require(test, message):
    if not test:
        raise EvidenceError(message)


def scoped(value, owner=ROOT):
    path = Path(value)
    path = (path if path.is_absolute() else ROOT / path).resolve()
    require(path.is_relative_to(owner.resolve()), f'Path escapes required scope: {path}')
    return path


def rel(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def write(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def sha(path):
    result = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            result.update(chunk)
    return result.hexdigest()


def tool(name, override=None):
    value = override or os.environ.get(name.upper()) or shutil.which(name)
    candidate = Path(value) if value else FF_DIR / (name + '.exe')
    require(candidate.is_file(), f'{name} executable not found; supply --{name}.')
    return str(candidate.resolve())


def guard():
    auth_path = HERE / 'authorization.json'
    control_path = ROOT / 'shared/publishing/video-production-control.json'
    auth, control = read(auth_path), read(control_path)
    require(auth.get('slug') == 'player-customization' and auth.get('revision') == 'reference-preserving-v3'
            and auth.get('fullProductionAuthorized') is True,
            'Current selected-D21 full-production authorization is required.')
    require(auth.get('automaticNextVideo') is False, 'This tool cannot authorize automatic next-video work.')
    return {'authorization': {'path': rel(auth_path), 'sha256': sha(auth_path)},
            'control': {'path': rel(control_path), 'sha256': sha(control_path)},
            'globalSelectedVideoPreserved': control.get('selectedVideo'),
            'globalOrForeignJobsModified': False}


def finite(value):
    result = float(value)
    require(math.isfinite(result), 'Non-finite timeline time is invalid.')
    return result


def seconds_frame(seconds):
    return round(finite(seconds) * FPS)


def visible(mark, seconds):
    if not finite(mark['t0']) <= seconds < finite(mark['t1']):
        return False
    if any(finite(a) <= seconds < finite(b) for a, b in mark.get('hiddenIntervals', [])):
        return False
    intervals = mark.get('visibleIntervals')
    return intervals is None or any(finite(a) <= seconds < finite(b) for a, b in intervals)


def make_samples(plan, layout, alignment):
    require(plan.get('slug') == 'player-customization' and plan.get('revision') == 'reference-preserving-v3',
            'Expected current D21 edit-plan.')
    require((plan.get('fps'), plan.get('width'), plan.get('height')) == (FPS, WIDTH, HEIGHT),
            'Expected native1920x1080/60fps timeline.')
    total = int(plan['totalFrames'])
    require(total > 720, 'Invalid selected-video totalFrames.')
    require(layout.get('fixedCenter') == [960, 970] and layout.get('fontSize') == 48
            and layout.get('maxLines') == 2, 'Expected fixed960,970/48px/max2line caption contract.')
    cues = layout['rows']
    require(cues and len({row['cue'] for row in cues}) == len(cues), 'Caption cues must be nonempty and unique.')
    require(alignment.get('bilingualCueCount') == len(cues), 'Alignment and layout cue counts differ.')
    aligned_ids = [cid for p in alignment['paragraphs'] for cid in p['cues']]
    require(len(aligned_ids) == len(cues) and set(aligned_ids) == {r['cue'] for r in cues},
            'Alignment paragraph mapping does not cover every layout cue exactly once.')
    points = {}

    def add(frame, kind, **context):
        frame = max(0, min(total - 1, int(frame)))
        reason = {'kind': kind, **context}
        rows = points.setdefault(frame, [])
        if reason not in rows:
            rows.append(reason)

    def boundary(frame, kind, **context):
        for delta in (-1, 0, 1):
            add(frame + delta, kind, offsetFrames=delta, **context)

    add(0, 'first-frame')
    add(total - 1, 'last-frame')
    for row in cues:
        start, end = int(row['startFrame']), int(row['endFrameExclusive'])
        require(0 <= start < end <= total, f'Cue{row["cue"]} has no valid visible-frame interval.')
        add((start + end - 1) // 2, 'ko-caption-midpoint', cue=row['cue'], paragraph=row['paragraph'], scene=row['scene'])

    cuts = sorted(plan['cuts'], key=lambda cut: int(cut['startFrame']))
    require(cuts and len({c['id'] for c in cuts}) == len(cuts), 'Cuts must be nonempty and uniquely identified.')
    previous = int(plan.get('brandingFrames', 120))
    for cut in cuts:
        start, end = int(cut['startFrame']), int(cut['endFrame'])
        require(start == previous and start < end <= total, f'Non-contiguous cut timeline at{cut["id"]}.')
        require(end - start == int(cut['frames']), f'Cut frame span differs at{cut["id"]}.')
        previous = end
        boundary(start, 'cut-start', cutId=cut['id'], scene=cut['scene'])
        boundary(end, 'cut-end', cutId=cut['id'], scene=cut['scene'])
        add((start + end - 1) // 2, 'cut-midpoint', cutId=cut['id'], scene=cut['scene'])
        duration = (end - start) / FPS
        for index, mark in enumerate(cut.get('marks', [])):
            mid = mark.get('id', f'{cut["id"]}-mark{index}')
            lo, hi = finite(mark['t0']), finite(mark['t1'])
            require(0 <= lo < hi <= duration + 1e-7, f'Mark{mid} is outside its cut.')
            base = {'cutId': cut['id'], 'markId': mid, 'label': mark.get('label', '')}
            boundary(start + seconds_frame(lo), 'annotation-start', **base)
            boundary(start + seconds_frame(hi), 'annotation-end', **base)
            add(start + seconds_frame((lo + hi) / 2), 'annotation-midpoint', **base)
            reveal_end = min(hi, lo + finite(mark.get('revealSeconds', .25)))
            add(start + seconds_frame((lo + reveal_end) / 2), 'annotation-reveal-midpoint', **base)
            add(start + seconds_frame(reveal_end), 'annotation-reveal-complete', **base)
            times = [finite(k['t']) for k in mark.get('keyframes', [])]
            require(times == sorted(times), f'Unsorted tracking keyframes:{mid}')
            for i, t in enumerate(times):
                require(0 <= t <= duration + 1e-7, f'Tracking keyframe outside cut:{mid}')
                add(start + seconds_frame(t), 'annotation-keyframe', keyframe=i, **base)
            for a, b in zip(times, times[1:]):
                if b > a:
                    add(start + seconds_frame((a + b) / 2), 'annotation-between-keyframes', **base)
            for name in ('hiddenIntervals', 'visibleIntervals'):
                for i, pair in enumerate(mark.get(name, [])):
                    for edge, value in zip(('start', 'end'), pair):
                        boundary(start + seconds_frame(value), 'annotation-visibility-boundary', intervalKind=name,
                                 interval=i, edge=edge, **base)
    require(previous == total - int(plan.get('outroFrames', 600)), 'Cut end does not meet the preserved member ending.')

    scenes = sorted(plan['scenes'], key=lambda scene: int(scene.get('visualStartFrame', scene['startFrame'])))
    require(len(scenes) == 8 and len({s['id'] for s in scenes}) == 8, 'Expected8 D21 scenes and7 chapter joins.')
    for before, after in zip(scenes, scenes[1:]):
        frame = int(after.get('visualStartFrame', after['startFrame']))
        for delta in (-30, -1, 0, 1, 30):
            add(frame + delta, 'chapter-join', fromScene=before['id'], toScene=after['id'], offsetFrames=delta)

    starts = [int(c['startFrame']) for c in cuts]
    cue_starts = [int(c['startFrame']) for c in cues]
    require(cue_starts == sorted(cue_starts), 'Caption rows are not timeline sorted.')
    result = []
    for frame in sorted(points):
        cut_index = bisect.bisect_right(starts, frame) - 1
        cut = cuts[cut_index] if cut_index >= 0 and frame < int(cuts[cut_index]['endFrame']) else None
        cue_index = bisect.bisect_right(cue_starts, frame) - 1
        cue = cues[cue_index] if cue_index >= 0 and frame < int(cues[cue_index]['endFrameExclusive']) else None
        ct = (frame - int(cut['startFrame'])) / FPS if cut else None
        active_marks = [{'id': m.get('id', f'{cut["id"]}-mark{i}'), 'label': m.get('label', '')}
                        for i, m in enumerate(cut.get('marks', [])) if visible(m, ct)] if cut else []
        source_time = finite(cut['sourceStart']) + ct if cut and cut.get('sourceStart') is not None else None
        result.append({'frame': frame, 'timeSeconds': frame / FPS, 'reasons': points[frame],
                       'cutId': cut['id'] if cut else ('branding' if frame < int(plan.get('brandingFrames', 120)) else 'membership'),
                       'scene': cut['scene'] if cut else None, 'cutKind': cut['kind'] if cut else 'preserved-branding-or-membership',
                       'sourceLocalSeconds': source_time, 'sourceSha256': cut.get('sourceSha256') if cut else None,
                       'captionCue': cue['cue'] if cue else None, 'paragraph': cue.get('paragraph') if cue else None,
                       'koCaption': cue.get('ko') if cue else None, 'enCaptionReference': cue.get('en') if cue else None,
                       'activeEditorialMarks': active_marks, 'actualDirectReview': 'pending',
                       'native': None, 'mobile375': None})
    return result


def probe_video(video, executable, total):
    completed = subprocess.run([executable, '-v', 'error', '-select_streams', 'v:0', '-show_entries',
        'stream=width,height,avg_frame_rate,nb_frames:format=duration,start_time', '-of', 'json', str(video)],
        capture_output=True, text=True, encoding='utf-8', errors='replace')
    require(completed.returncode == 0, 'Could not read captioned-master header with ffprobe.')
    info = json.loads(completed.stdout)
    stream = info['streams'][0]
    require((int(stream['width']), int(stream['height'])) == (WIDTH, HEIGHT), 'Master is not native1920x1080.')
    require(Fraction(stream['avg_frame_rate']) == FPS, 'Master is not60fps.')
    if stream.get('nb_frames') not in (None, 'N/A'):
        require(int(stream['nb_frames']) == total, 'Header frame count differs from current edit-plan.')
    return info


def export_once(video, samples, folder, ffmpeg, threads):
    native = folder / 'native'
    native.mkdir()
    # A left-nested sum of hundreds of terms exceeds FFmpeg's expression
    # parser depth. A balanced tree retains every requested index at log depth.
    terms = [f'eq(n,{s["frame"]})' for s in samples]
    while len(terms)>1:
        terms = ['('+terms[i]+'+'+terms[i+1]+')' if i+1<len(terms) else terms[i]
                 for i in range(0,len(terms),2)]
    expression = terms[0]
    script = folder / 'select.filter.txt'
    script.write_text(f"setpts=PTS-STARTPTS,select='{expression}',showinfo\n", encoding='ascii')
    log = folder / 'ffmpeg-selected-frames.log'
    command = [ffmpeg, '-hide_banner', '-nostdin', '-n', '-loglevel', 'info', '-threads', str(threads),
               '-filter_threads', '1', '-i', str(video), '-map', '0:v:0', '-an', '-sn', '-dn',
               '-vf', script.read_text(encoding='ascii').strip(), '-fps_mode', 'passthrough', '-c:v', 'png',
               '-compression_level', '2', '-threads', str(threads), str(native / 'sample-%06d.png')]
    with log.open('wb') as stream:
        completed = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=stream)
    require(completed.returncode == 0, f'One-pass frame export failed; inspect{rel(log)}. No automatic retry.')
    text = log.read_text(encoding='utf-8', errors='replace')
    decoded = re.findall(r'\bn:\s*(\d+)\s+pts:\s*(-?\d+)\s+pts_time:([-+\d.eE]+).*?\bs:(\d+)x(\d+)', text)
    images = sorted(native.glob('sample-*.png'))
    require(len(images) == len(samples) == len(decoded), 'Selected PNG/PTS count differs; do not infer missing-frame approval.')
    for index, (sample, png, observed) in enumerate(zip(samples, images, decoded)):
        n, pts, seconds, width, height = observed
        require(int(n) == index and (int(width), int(height)) == (WIDTH, HEIGHT), 'Unexpected selected-frame sequence/dimensions.')
        require(abs(float(seconds) - sample['timeSeconds']) <= .51 / FPS,
                f'Selected-frame timestamp differs at frame{sample["frame"]}.')
        dest = native / f'frame-{sample["frame"]:08d}.png'
        png.rename(dest)
        sample['observedPts'] = int(pts)
        sample['observedNormalizedPtsSeconds'] = float(seconds)
        sample['native'] = {'path': rel(dest), 'sha256': sha(dest), 'dimensions': [WIDTH, HEIGHT]}
    return {'ffmpegVideoDecodeInvocations': 1, 'audioDecodedOrListened': False,
            'filterScript': rel(script), 'log': rel(log), 'selectedFrameCount': len(samples),
            'ptsNormalizedToFirstFrame': True,
            'limits': 'This exports selected pixels and checks their timestamps. It does not certify continuous viewing, all-frame pixel review, human listening or replace the final-output integrity report.'}


def font(size):
    from PIL import ImageFont
    for name in ('C:/Windows/Fonts/malgun.ttf', 'C:/Windows/Fonts/arial.ttf'):
        if Path(name).exists():
            return ImageFont.truetype(name, size)
    return ImageFont.load_default()


def shortened(draw, value, chosen_font, width):
    value = str(value).replace('\n', ' ')
    while value and draw.textlength(value, font=chosen_font) > width:
        value = value[:-1]
    return value


def derivatives(samples, folder, per_board):
    from PIL import Image, ImageDraw
    mobile, boards = folder / 'mobile375', folder / 'boards'
    mobile.mkdir(); boards.mkdir()
    for sample in samples:
        path = ROOT / sample['native']['path']
        with Image.open(path) as image:
            require(image.size == (WIDTH, HEIGHT), 'Extracted PNG unexpectedly lost native dimensions.')
            dest = mobile / path.name
            image.convert('RGB').resize((375, 211), Image.Resampling.LANCZOS).save(dest)
        sample['mobile375'] = {'path': rel(dest), 'sha256': sha(dest), 'dimensions': [375, 211],
                               'derivedFromNativeSha256': sample['native']['sha256'], 'actualDirectReview': 'pending'}
    cols = 2 if per_board == 6 else 3
    rows = per_board // cols
    output = []
    for variant in ('native', 'mobile375'):
        thumb_w = 1920 // cols if variant == 'native' else 375
        thumb_h = round(thumb_w * HEIGHT / WIDTH)
        footer = 72 if variant == 'native' else 58
        chosen = font(23 if variant == 'native' else 17)
        for offset in range(0, len(samples), per_board):
            page = samples[offset:offset + per_board]
            board = Image.new('RGB', (cols * thumb_w, rows * (thumb_h + footer)), '#111111')
            draw = ImageDraw.Draw(board)
            for index, sample in enumerate(page):
                x, y = index % cols * thumb_w, index // cols * (thumb_h + footer)
                with Image.open(ROOT / sample[variant]['path']) as image:
                    board.paste(image.convert('RGB').resize((thumb_w, thumb_h), Image.Resampling.LANCZOS), (x, y))
                f = sample['frame']
                stamp = f'{f//(FPS*3600):02}:{f//(FPS*60)%60:02}:{f//FPS%60:02}:{f%FPS:02}'
                line1 = f'{stamp} / f{f} / {sample["cutId"]} / cue{sample["captionCue"] or "-"}'
                note = sample['koCaption'] or ', '.join(r['kind'] for r in sample['reasons'])
                draw.text((x+8, y+thumb_h+5), shortened(draw, line1, chosen, thumb_w-16), font=chosen, fill='white')
                draw.text((x+8, y+thumb_h+footer/2), shortened(draw, note, chosen, thumb_w-16), font=chosen, fill='#e8cf83')
            dest = boards / f'{variant}-board-{offset//per_board+1:03d}.jpg'
            board.save(dest, quality=93, subsampling=0)
            output.append({'path': rel(dest), 'sha256': sha(dest), 'variant': variant,
                           'sampleFrames': [s['frame'] for s in page], 'imagesPerBoardLimit': per_board,
                           'dimensions': list(board.size), 'actualDirectReview': 'pending'})
    return output


def reuse_if_complete(folder, signature):
    manifest = folder / 'manifest.json'
    if not manifest.exists():
        require(not folder.exists(), f'Incomplete export directory already exists:{rel(folder)}. Inspect its log before a deliberate new run; nothing is overwritten.')
        return None
    old = read(manifest)
    require(old.get('exportStatus') == 'complete' and old.get('inputSignature') == signature,
            'Existing evidence signature/status differs; nothing is overwritten.')
    assets = [s[k] for s in old['samples'] for k in ('native', 'mobile375')] + old['boards']
    require(all((ROOT/a['path']).exists() and sha(ROOT/a['path']) == a['sha256'] for a in assets),
            'Existing evidence file is missing/changed; inspect it before re-exporting.')
    return old


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--plan', required=True, help='Current D21 edit-plan.json')
    parser.add_argument('--caption-layout', required=True, help='Current caption-layout.json with everyKO cue')
    parser.add_argument('--caption-alignment', required=True, help='Current complete paragraph/cue alignment JSON')
    parser.add_argument('--video', required=True, help='Current captioned1920x1080/60fps MP4; never the clean or mobile review copy')
    parser.add_argument('--output-dir', default=rel(DEFAULT_OUT), help='Base directory inside this revision ignored local/inspection; a hash-named run folder is created')
    parser.add_argument('--per-board', type=int, choices=(6, 9), default=6)
    parser.add_argument('--threads', type=int, choices=(1, 2, 3, 4), default=2)
    parser.add_argument('--ffmpeg', help='Optional executable path')
    parser.add_argument('--ffprobe', help='Optional executable path')
    args = parser.parse_args()
    authorization = guard()
    paths = {'editPlan': scoped(args.plan), 'captionLayout': scoped(args.caption_layout),
             'captionAlignment': scoped(args.caption_alignment), 'captionedVideo': scoped(args.video)}
    require(all(p.is_file() for p in paths.values()), 'All current inputs, including the final captioned master, must exist.')
    require(paths['editPlan'].is_relative_to(HERE), 'Edit-plan must belong to this D21 revision.')
    require(paths['captionedVideo'].suffix.lower() == '.mp4', 'Expected the current captioned MP4.')
    plan, layout, alignment = (read(paths[k]) for k in ('editPlan', 'captionLayout', 'captionAlignment'))
    samples = make_samples(plan, layout, alignment)
    inputs = {name: {'path': rel(p), 'sha256': sha(p), 'bytes': p.stat().st_size} for name, p in paths.items()}
    code = {'path': rel(Path(__file__)), 'sha256': sha(Path(__file__))}
    fingerprint = {'inputs': inputs, 'code': code, 'frames': [s['frame'] for s in samples],
                   'mobileWidth': 375, 'perBoard': args.per_board}
    signature = hashlib.sha256(json.dumps(fingerprint, sort_keys=True).encode('utf-8')).hexdigest()
    base = scoped(args.output_dir, INSPECTION)
    folder = base / ('v-' + signature[:16])
    old = reuse_if_complete(folder, signature)
    if old is not None:
        print(json.dumps({'manifest': rel(folder/'manifest.json'), 'reused': True, 'samples': len(old['samples']),
                          'decodeInvocationsThisRun': 0, 'actualDirectReview': old['actualDirectReview']}, ensure_ascii=False))
        return
    ffmpeg, ffprobe = tool('ffmpeg', args.ffmpeg), tool('ffprobe', args.ffprobe)
    metadata = probe_video(paths['captionedVideo'], ffprobe, int(plan['totalFrames']))
    # Check authorization immediately before the costly decode; preserve all
    # foreign jobs/selection. Inputs are immutable evidence for this one run.
    latest = guard()
    require(latest['authorization']['sha256'] == authorization['authorization']['sha256'], 'D21 authorization changed before decode.')
    require(all(sha(p) == inputs[name]['sha256'] for name, p in paths.items()), 'An input changed while planning evidence; no export started.')
    folder.mkdir(parents=True)
    write(folder/'sample-plan.json', {'inputSignature': signature, 'inputs': inputs, 'samples': samples,
                                    'actualDirectReview': 'pending', 'exportsStarted': False})
    execution = export_once(paths['captionedVideo'], samples, folder, ffmpeg, args.threads)
    boards = derivatives(samples, folder, args.per_board)
    require(all(sha(p) == inputs[name]['sha256'] for name, p in paths.items()), 'Input changed during export; artifacts are not a valid current-input export.')
    manifest = {'schemaVersion': 1, 'slug': 'player-customization', 'revision': 'reference-preserving-v3',
                'createdAt': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'exportStatus': 'complete',
                'inputSignature': signature, 'inputs': inputs, 'helper': code, 'authorization': authorization,
                'videoHeader': metadata, 'fps': FPS, 'nativeDimensions': [WIDTH, HEIGHT], 'mobileDimensions': [375, 211],
                'captionContract': {'anchor': [960,970], 'fontPx':48, 'maxLines':2, 'source':'current captioned-master pixels; not redrawn'},
                'samplePolicy': 'EveryKO cue midpoint; each cut midpoint and cut pre/first/next frames; annotation reveal, endpoints, tracking keys and between-key points, visibility boundaries;5frames around each of7chapterjoins. Frame indices deduplicated, every reason retained.',
                'execution': execution, 'samples': samples, 'boards': boards,
                'coverage': {'koCaptionCues': len(layout['rows']), 'uniqueSamples':len(samples),
                             'cuts':len(plan['cuts']), 'chapterJoins':7,
                             'annotationMarks':sum(len(c.get('marks',[])) for c in plan['cuts'])},
                'actualDirectReview': 'pending', 'continuousPlaybackReview':'not performed by exporter',
                'humanListening':'not performed; audio is not decoded', 'allFrameVisualReview':'not performed',
                'wholeVideoApproval':False, 'productionMediaOrSourceInputsModified':False,
                'mediaMustRemainIgnored':True, 'scope':'D21 ignored local/inspection only; no Git/platform/GPU/foreign-job mutations'}
    write(folder/'manifest.json', manifest)
    print(json.dumps({'manifest':rel(folder/'manifest.json'), 'reused':False, 'samples':len(samples),
                      'boards':len(boards), 'decodeInvocationsThisRun':1, 'actualDirectReview':'pending'}, ensure_ascii=False))


if __name__ == '__main__':
    try:
        main()
    except (EvidenceError, FileNotFoundError, KeyError, ValueError, OSError) as exc:
        raise SystemExit(f'D21 review evidence not approved: {exc}') from exc
