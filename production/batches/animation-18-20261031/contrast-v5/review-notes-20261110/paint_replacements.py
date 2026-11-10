"""Repaint only affected final-clock picture ranges with verified sources."""
import argparse
from functools import lru_cache
import hashlib
import math
from pathlib import Path
import re
import subprocess
import sys

from plan_observations import BATCH, HERE, ROOT, load, save

sys.path.insert(0, str(BATCH / 'renderer'))
import compose
import render_rows
import sources
from PIL import Image, ImageDraw
import numpy as np
from scipy.ndimage import gaussian_filter1d


WORK = Path('C:/Users/1/Videos/YamyamProduction/animation-review-notes-20261110')
EPISODES = {'A06': {'ending', 'timing'}, 'A08': {'flow', 'edge', 'stance', 'overview', 'warrior'}, 'A11': {'kick'}}
ENCODE = ['-threads', '4', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-bf', '0',
          '-g', '120', '-sc_threshold', '0', '-pix_fmt', 'yuv420p', '-r', '60',
          '-video_track_timescale', '60000', '-color_primaries', 'bt709', '-color_trc', 'bt709',
          '-colorspace', 'bt709', '-movflags', '+faststart']


def run(args, **options):
    return subprocess.run(args, check=True, creationflags=subprocess.CREATE_NO_WINDOW, **options)


def file_path(value):
    return (ROOT / value).resolve()


def picture_span(start, end, reference, offset):
    return {'start': start, 'end': end, 'reference': reference, 'offset': offset}


def source_registry(ep):
    group = next(row for row in load(BATCH / 'renderer/integration-caption-safe.json')['episodes'] if row['id'] == ep)
    for row in group['rows']:
        if ep == 'A08' and row['id'].startswith('A08-relocated-flow-'):
            row['key'] = 'warrior'
    real = {row['id']: row for row in group['rows']}
    games = next(row for row in load(BATCH / 'game-plates-caption-safe.json')['episodes'] if row['id'] == ep)
    names = {Path(row['output']).stem: row for row in group['rows']}
    by_path = {str(file_path(row['output'])): row for row in group['rows']}
    for row in games['pictureEdits']:
        media = row.get('mediaSegments', [])
        if len(media) != 1 or not media[0]['sourceKey'].startswith('authored:'):
            continue
        key = media[0]['sourceKey'].split('/')[-1]
        if key not in EPISODES[ep]:
            continue
        source = row.get('captionSafePatch', {}).get('sourcePlate', '')
        template = names.get(Path(source).stem)
        if not template:
            alternatives = [q for q in group['rows'] if q['key'] == key and q['mode'] == 'analysis']
            template = min(alternatives, key=lambda q: abs(q['relationFrameStart'] - row['startFrame']))
        real[row['id']] = {'id': row['id'], 'key': key, 'mode': 'retimed', 'frames': row['newFrames'],
                           'template': template, 'oldPictureSha256': row['pictureSha256']}
        by_path[str(file_path(row['picture']))] = real[row['id']]
    return real, by_path


def classify(ep, edl):
    ids, paths = source_registry(ep)
    comps = {str(file_path(q['picture'])): q['mediaComposition']
             for q in edl['pictureEdits'] if 'mediaComposition' in q}
    spans = []

    def lookup(source, name):
        return paths.get(str(file_path(source))) or ids.get(re.sub(r'(?:-visual|-fragment\d+)+$', '', name))

    def add(start, end, template, offset, hold=False):
        if template and template['key'] in EPISODES[ep] and start < end:
            spans.append(dict(picture_span(start, end, template, offset), hold=hold))

    for row in edl['pictureEdl']:
        src = str(file_path(row['source']))
        start, end = row['outputStartFrame'], row['outputEndFrame']
        offset = row['sourceStartFrame']
        if src not in comps:
            add(start, end, lookup(src, row['id']), offset)
            continue
        composition = comps[src]
        cursor = 0
        limit = composition['originalUnscaledFrames']
        for i, clip in enumerate(composition['clips']):
            amount = min(clip['frames'], max(0, limit - cursor))
            a, b = max(offset, cursor), min(offset + end - start, cursor + amount)
            template = lookup(clip['source'], clip['id'])
            add(start + a - offset, start + b - offset, template, clip['sourceStartFrame'] + a - cursor)
            if i == composition['heldClipIndex'] and amount:
                a = max(offset, limit)
                add(start + a - offset, end, template, clip['sourceStartFrame'] + amount - 1, hold=True)
            cursor += amount
    return sorted(spans, key=lambda q: q['start'])


def adopt_game_inserts(edl, spans):
    entries = load(HERE / 'A06-game-beats.json')['inserts']
    coverage = load(BATCH / 'footage/team-b/game-coverage.json')['sources']
    for entry in entries:
        start, end = entry['start'], entry['end']
        covered = [r for r in edl['pictureEdl'] if r['outputStartFrame'] < end and r['outputEndFrame'] > start]
        assert all(r['kind'] == 'authored-explanation' for r in covered), (entry, covered)
        source = coverage[entry['source']]
        assert source['decodedFhd'] and sources.sha(source['file']) == source['sha256']
        assert any(window['localIn'] <= entry['in'] and entry['in'] + (end - start) / 60 <= window['localOut']
                   for window in source['observedRanges'])
        replaced = []
        for r in spans:
            if r['end'] <= start or r['start'] >= end:
                replaced.append(r)
                continue
            if r['start'] < start:
                replaced.append(dict(r, end=start))
            if r['end'] > end:
                replaced.append(dict(r, start=end, offset=r['offset'] + end - r['start']))
        spans = replaced + [{'start': start, 'end': end, 'game': entry, 'gameSource': source}]
    return sorted(spans, key=lambda q: q['start'])


ORIGINAL_SOURCE = sources.source
ORIGINAL_GUIDE = compose.guide_plate
ORIGINAL_CONTRACT = compose.contract
ORIGINAL_STRIP = compose.contextual_strip
ORIGINAL_BOUNDS = compose.bounds


@lru_cache(None)
def study_source(ep, key):
    if ep not in ('A08', 'A11') or key not in EPISODES[ep]:
        return ORIGINAL_SOURCE(ep, key)
    local = WORK / ('A08-motion' if (ep, key) == ('A08', 'warrior') else ep)
    receipt = load(local / 'capture-receipt.json')
    path = local / 'poses' / f'{key}.json'
    assert receipt['definitions'][key] == sources.sha(path)
    files = tuple(sorted((local / 'frames' / key).glob('*.png')))
    assert len(files) == 180
    return {'episode': ep, 'key': key, 'definition': load(path), 'metadata': path, 'files': files,
            'movie': None, 'kind': 'actual-UE-authored-demonstration', 'importedMotion': False}


@lru_cache(None)
def study_bounds(ep, key):
    if ep not in ('A08', 'A11') or key not in EPISODES[ep]:
        return ORIGINAL_BOUNDS(ep, key)
    study = study_source(ep, key)
    offset = sources.panel_offset(ep, key, 1)
    bounds = []
    for filename in study['files']:
        with Image.open(filename) as plate:
            rgb = np.asarray(plate.convert('RGB'), dtype=np.int16)
        orange = (rgb[:, :, 0] > rgb[:, :, 1] + 17) & (rgb[:, :, 1] > rgb[:, :, 2] + 10)
        for side in (0, 1):
            y, x = np.nonzero(orange[:, 960 * side:960 * (side + 1)])
            # Ignore the thin red floor line and use the orange rig's visible geometry.
            keep = y < 846
            if keep.sum() > 500:
                x = x[keep] + side * (960 - offset)
                y = y[keep]
                bounds.append((x.min(), y.min(), x.max(), y.max()))
    all_bounds = np.asarray(bounds)
    return (max(0, int(all_bounds[:, 0].min()) - 28), max(0, int(all_bounds[:, 1].min()) - 30),
            min(951, int(all_bounds[:, 2].max()) + 28), max(885, int(all_bounds[:, 3].max()) + 30))


@lru_cache(256)
def wrist_path(ep, key, n, side):
    d = study_source(ep, key)['definition']
    points = []
    for frame in range(max(0, n - 23), n + 1):
        p = sources.points(ep, key, frame, side).get('hand_r')
        if p is not None:
            points.append(sources.projected(d, p, side))
    if len(points) < 2:
        return ()
    smooth = gaussian_filter1d(np.asarray(points), 1.45, axis=0, mode='nearest')
    smooth[-1] = points[-1]
    return tuple(map(tuple, smooth))


def guide(ep, key, n, side, enabled=True):
    if ep != 'A06':
        return ORIGINAL_GUIDE(ep, key, n, side, enabled)
    plate, _ = compose.raw(ep, key, n, side)
    points = wrist_path(ep, key, n, side) if enabled else ()
    if points and math.dist(points[0], points[-1]) > 6:
        pen = ImageDraw.Draw(plate)
        color = '#078076' if side == 0 else '#9b3d2b'
        pen.line(points, fill='#f9f4e2', width=11, joint='curve')
        pen.line(points, fill=color, width=6, joint='curve')
        x, y = points[-1]
        pen.ellipse((x - 9, y - 9, x + 9, y + 9), fill='#fff9eb', outline=color, width=4)
    return plate


def contract(ep, key):
    if (ep, key) == ('A08', 'warrior'):
        return dict(heading='전사 자세에서 몸통 기울이기', labels=['시작 자세 유지', '기울였다가 돌아오기'],
                    samples=[12, 100, 179], phases=['시작', '몸통 기울임', '복귀'],
                    guide='none', comparisonKind='pose timing')
    c = ORIGINAL_CONTRACT(ep, key)
    if (ep, key) == ('A11', 'kick'):
        c = dict(c, heading='같은 회전 발차기, 다른 시간 배분', samples=[61, 67, 69],
                 phases=['몸을 돌려 준비', '다리를 펼치는 중', '같은 도달 자세'], guide='none')
    return c


def strip(image, ep, key, frame, c):
    if (ep, key) == ('A08', 'warrior'):
        compose.txt(ImageDraw.Draw(image), (80, 821), '두 손은 머리 위 · 두 발은 바닥에 고정', 40, compose.WHITE)
        return
    if (ep, key) != ('A11', 'kick'):
        return ORIGINAL_STRIP(image, ep, key, frame, c)
    pen = ImageDraw.Draw(image)
    for x, color, text, first in ((80, '#81cfc5', '8프레임에 고르게 이동', 0),
                                  (1010, '#f18b81', '준비 5프레임 · 이동 3프레임', 5)):
        compose.txt(pen, (x, 784), text, 34, color)
        pen.line((x, 849, x + 760, 849), fill='#58645d', width=13)
        if first:
            pen.line((x, 849, x + 95 * first, 849), fill='#d8b467', width=13)
        pen.line((x + 95 * first, 849, x + 760, 849), fill=color, width=13)
        if 61 <= frame <= 69:
            now = x + (frame - 61) * 95
            pen.line((now, 829, now, 868), fill=compose.WHITE, width=5)


def state(ep, row, offset):
    if row['mode'] == 'retimed':
        ref = row['template']
        return state(ep, ref, min(ref['frames'] - 1, round(offset * (ref['frames'] - 1) / max(1, row['frames'] - 1))))
    if ep == 'A11' and row['mode'] == 'native':
        counter = int(row['id'].rsplit('-', 1)[1]) - 1
        return min(179, counter * 60 + offset), 'native', None
    if row['mode'] == 'native':
        n, mode = render_rows.state(ep, row, offset)
        return n, mode, row.get('passIndex')
    f = offset + row.get('cutOffset', 0)
    total = row['originalCutFrames']
    lead = row.get('nativeLeadFrames', 0)
    if f < lead and ep != 'A11':
        return min(179, f), 'native', None
    if ep == 'A08' and row['key'] == 'overview':
        chapter = str(row.get('chapter')).zfill(2)
        if chapter in ('02', '08'):
            return 171, 'compare', None
        if chapter == '07' or f >= round(total * .7):
            return 171, 'stages', None
        return round(171 * np.clip(f / max(1, round(total * .7) - 1), 0, 1)), 'compare', None
    if ep == 'A11':
        limit = round(total * .70) if row.get('phaseModeAtTail') else total
        if row.get('phaseModeAtTail') and f >= limit:
            return 69, 'stages', None
        return round(61 + 8 * np.clip(f / max(1, limit - 1), 0, 1)), 'compare', None
    n, mode = render_rows.state(ep, row, offset)
    return n, mode, None


@lru_cache(28)
def frame_pixels(ep, key, n, mode, counter, hold):
    image = compose.frame(ep, key, n, mode, pass_index=counter, legend=False)
    if ep in ('A08', 'A11') or hold:
        draw = ImageDraw.Draw(image)
        if ep in ('A08', 'A11'):
            draw.rectangle((62, 105, 835, 151), fill=compose.BG)
            label = '링 피트 전사 자세 I 참고 · 자체 시연' if ep == 'A08' else 'ACCAD 회전 발차기 모션 캡처 · UE 시연'
            compose.txt(draw, (64, 112), label, 31, compose.MUTED)
        if hold:
            draw.rectangle((1610, 0, 1920, 112), fill=compose.BG)
            compose.txt(draw, (1630, 57), '정지 분석', 32, compose.YELLOW)
    return image.tobytes()


def render_span(ep, span, output):
    frames = span['end'] - span['start']
    if 'game' in span:
        game = span['game']
        plate = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0))
        pen = ImageDraw.Draw(plate)
        compose.txt(pen, (240, 27), game['label'], 37, compose.YELLOW)
        compose.txt(pen, (1460, 35), '실제 게임 · 1×', 30, compose.WHITE)
        logo = output.with_suffix('.png')
        plate.save(logo)
        run(['ffmpeg', '-v', 'error', '-nostdin', '-y', '-ss', str(game['in']), '-threads', '2',
             '-i', span['gameSource']['file'], '-i', str(logo), '-filter_complex_threads', '1',
             '-filter_complex', '[0:v]fps=60,scale=1440:810:flags=lanczos,pad=1920:1080:240:85:color=0x080c0a[v];[v][1:v]overlay=0:0',
             '-frames:v', str(frames), '-an', *ENCODE, str(output)])
    else:
        row = span['reference']
        with output.with_suffix('.log').open('wb') as log:
            process = subprocess.Popen(['ffmpeg', '-v', 'error', '-nostdin', '-y', '-f', 'rawvideo', '-pix_fmt',
                                        'rgb24', '-s', '1920x1080', '-r', '60', '-i', 'pipe:0', '-an',
                                        *ENCODE, str(output)], stdin=subprocess.PIPE, stderr=log,
                                       creationflags=subprocess.CREATE_NO_WINDOW)
            try:
                for i in range(frames):
                    n, mode, counter = state(ep, row, span['offset'] + (0 if span['hold'] else i))
                    process.stdin.write(frame_pixels(ep, row['key'], n, mode, counter, span['hold']))
            finally:
                process.stdin.close()
                assert process.wait() == 0, output
    probe = subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v:0',
                                    '-show_entries', 'stream=width,height,nb_frames,avg_frame_rate',
                                    '-of', 'csv=p=0', str(output)], text=True)
    assert probe.strip().split(',') == ['1920', '1080', '60/1', str(frames)], (output, probe)


def main(ep):
    edl = load(BATCH / 'local/explanation-assembly' / ep / 'edl.json')
    spans = classify(ep, edl)
    if ep == 'A06':
        spans = adopt_game_inserts(edl, spans)
    assert spans and all(a['end'] <= b['start'] for a, b in zip(spans, spans[1:]))
    assert spans[0]['start'] >= 120 and spans[-1]['end'] <= edl['frames'] - 600
    folder = WORK / ep / 'new-pictures'
    folder.mkdir(parents=True, exist_ok=True)
    captures = [WORK / ep / 'capture-receipt.json']
    if ep == 'A08':
        captures.append(WORK / 'A08-motion/capture-receipt.json')
    code = hashlib.sha256(Path(__file__).read_bytes() +
                         b''.join(p.read_bytes() for p in captures if p.exists())).hexdigest()
    for i, span in enumerate(spans):
        dest = folder / f'{i:03d}-{span["start"]:06d}-{span["end"]:06d}.mp4'
        sidecar = dest.with_suffix('.json')
        cached = load(sidecar) if sidecar.exists() else {}
        if not dest.exists() or cached.get('span') != span or cached.get('code') != code or cached.get('sha256') != sources.sha(dest):
            render_span(ep, span, dest)
            save(sidecar, {'span': span, 'code': code, 'sha256': sources.sha(dest)})
        span['file'] = str(dest)
        span['sha256'] = sources.sha(dest)
        print(ep, i + 1, len(spans), span['start'], span['end'], flush=True)
    save(folder / 'manifest.json', {'episode': ep, 'priorFrameCount': edl['frames'], 'spans': spans})


if __name__ == '__main__':
    sources.source = compose.source = render_rows.source = study_source
    compose.guide_plate = guide
    compose.contract = contract
    compose.contextual_strip = strip
    compose.bounds = study_bounds
    parser = argparse.ArgumentParser()
    parser.add_argument('episode', choices=tuple(EPISODES))
    main(parser.parse_args().episode)
