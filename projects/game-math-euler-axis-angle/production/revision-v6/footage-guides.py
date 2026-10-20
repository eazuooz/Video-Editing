"""CPU-only editorial guides from already inspected native-source tracking keys.

No video decoding, renderer, detector or inferred internal game values are used.
ASS times are clip-relative. The source image and every guide share one affine
placement; root applies this ASS after scaling/padding the native finite clip.
"""
from pathlib import Path
import argparse
import bisect
import hashlib
import json
import math
import shutil
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[4]
PROJECT = ROOT / 'projects/game-math-euler-axis-angle'
HERE = Path(__file__).parent
OUT = PROJECT / 'production/local/revision-v6/edit'
PLAN = HERE / 'footage-plan.json'
LEGACY = PROJECT / 'sources/annotation-plan-v3.json'
FONT_FILE = Path('C:/Windows/Fonts/malgunbd.ttf')
FONT = ImageFont.truetype(str(FONT_FILE), 40)
X, Y, WIDTH, HEIGHT = 224, 32, 1472, 828
SCALE = WIDTH / 1920
GREEN, BLACK, WHITE = '#6cce8e', '#080b0d', '#f5f5f5'
LABELS = {'mk-body-up': '차체', 'zelda-log-position': '옮기는 통나무',
          'mario-middle-poses': '마리오의 자세', 'zelda-mast-orientation': '돛대의 긴 방향'}
HEADER = '''[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Guide,Malgun Gothic,40,&H00F5F5F5,&H00F5F5F5,&H000D0B08,&H000D0B08,-1,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def rel(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def point(p):
    return (X + p[0] * SCALE, Y + p[1] * SCALE)


def timekey(key):
    return round(float(key['sourceTime']) * 60)


def tracking_keys(clip, old):
    window = next(w for w in old['windows'] if w['id'] == clip['annotation']['sourceWindow'])
    lower = round(clip['sourceIn'] * 60)
    upper = round(clip['sourceOutExclusive'] * 60)
    # Current verified keys override old keys at the same actual source frame.
    merged = {timekey(k): k for k in window.get('keyframes', []) if lower <= timekey(k) < upper}
    merged.update({timekey(k): k for k in clip['annotation']['sourceKeyframes']})
    return sorted(merged.items())


def state_at(clip, keys, source_frame):
    frames = [f for f, _ in keys]
    # Do not extrapolate before the first observation, or after its last frame.
    if source_frame < frames[0] or source_frame > frames[-1]:
        return None
    i = bisect.bisect_right(frames, source_frame) - 1
    left_frame, left = keys[i]
    if not left.get('visible', True):
        return None
    for a, b in clip['annotation'].get('visibleSourceRanges', [[clip['sourceIn'], clip['sourceOutExclusive']]]):
        if round(a * 60) <= source_frame < round(b * 60):
            break
    else:
        return None
    if i + 1 == len(keys) or source_frame == left_frame:
        return left
    right_frame, right = keys[i + 1]
    if not right.get('visible', True):
        # A hide key is a visibility change, never a shrinking box to (0,0).
        return left
    fraction = (source_frame - left_frame) / (right_frame - left_frame)
    shape = 'points' if 'points' in left else 'bbox'
    assert shape in right, (clip['id'], source_frame, 'incompatible verified shapes')

    def mix(a, b):
        if isinstance(a, list):
            assert len(a) == len(b)
            return [mix(x, y) for x, y in zip(a, b)]
        return a + (b - a) * fraction

    return {'visible': True, shape: mix(left[shape], right[shape])}


def offset_polyline(points, amount):
    result = []
    for i, p in enumerate(points):
        a, b = points[max(0, i - 1)], points[min(len(points) - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        length = math.hypot(dx, dy)
        assert length > 0
        result.append((p[0] - dy / length * amount, p[1] + dx / length * amount))
    return result


def direction_pointer_geometry(clip, source_frame, relative_frame):
    spec = clip['annotation']['directionPointers']
    keys = spec['sourceKeyframes']
    fs = [round(k['sourceTime'] * 60) for k in keys]
    if not fs[0] <= source_frame <= fs[-1]:
        return None
    i = bisect.bisect_right(fs, source_frame) - 1
    j = min(i + 1, len(keys) - 1)
    t = 0 if fs[i] == fs[j] else (source_frame - fs[i]) / (fs[j] - fs[i])
    active = ['front'] if relative_frame < 80 else ['up'] if relative_frame < 140 else ['front', 'up']
    marks = []
    for role in active:
        target = point([keys[i][role][n] + (keys[j][role][n] - keys[i][role][n]) * t for n in range(2)])
        label = spec['roles'][role]['label']
        lx, ly = spec['roles'][role]['labelPosition']
        w = math.ceil(FONT.getlength(label)) + 30
        rect = (lx, ly, lx + w, ly + 62)
        origin = (rect[2] + 16, ly + 31)
        dx, dy = target[0] - origin[0], target[1] - origin[1]
        size = math.hypot(dx, dy); ux, uy = dx / size, dy / size
        back = (target[0] - ux * 20, target[1] - uy * 20)
        head = [(back[0] - uy * 11, back[1] + ux * 11), target,
                (back[0] + uy * 11, back[1] - ux * 11)]
        marks.append(dict(label=label, labelRect=rect, paths=[[origin, target], head],
                          color=spec['roles'][role]['color'], role=role, target=target))
    return dict(mode='observed-direction-pointers', marks=marks,
                note='화면 관찰 · 방향 안내', noteRect=(300, 190, 850, 246), width=6)


def guide_geometry(clip, state, source_frame=None, relative_frame=None):
    if state is None:
        return None
    if clip['id'] == 'mk-body-up' and 'directionPointers' in clip['annotation']:
        return direction_pointer_geometry(clip, source_frame, relative_frame)
    if 'points' in state:
        source_points = state['points']
        assert all(0 <= p[0] <= 1920 and 0 <= p[1] <= 1080 for p in source_points)
        centerline = [point(p) for p in source_points]
        # Parallel open contours protect the visible shaft and native arc.
        # They stop at the verified in-picture endpoints; no unseen sail box.
        paths = [offset_polyline(centerline, sign * 14) for sign in [-1, 1]]
        anchor = centerline[len(centerline) // 2]
        label_x, label_y = anchor[0] + 44, anchor[1] - 29
        leader = [anchor, (label_x - 9, label_y + 29)]
    else:
        x, y, w, h = state['bbox']
        assert w > 0 and h > 0
        x, y = point((x, y))
        w, h = w * SCALE, h * SCALE
        edge = max(22, min(45, w * .16, h * .16))
        paths = [[(x + edge, y), (x, y), (x, y + edge)],
                 [(x + w - edge, y), (x + w, y), (x + w, y + edge)],
                 [(x, y + h - edge), (x, y + h), (x + edge, y + h)],
                 [(x + w - edge, y + h), (x + w, y + h), (x + w, y + h - edge)]]
        label_x, label_y = x, y - 66
        leader = [(x + 14, y - 5), (x + 14, y - 12)]
    label = LABELS[clip['id']]
    ink = FONT.getbbox(label)
    label_w = math.ceil(FONT.getlength(label)) + 24
    label_h = 58
    label_x = max(X + 12, min(X + WIDTH - label_w - 12, label_x))
    label_y = max(Y + 12, min(Y + HEIGHT - label_h - 12, label_y))
    if 'points' in state:
        leader[-1] = (label_x - 9, label_y + 29)
    rect = (label_x, label_y, label_x + label_w, label_y + label_h)
    return {'paths': paths, 'leader': leader, 'label': label, 'labelRect': rect,
            'inkOffset': [-ink[0], -ink[1]], 'width': 6}


def polygon_segment(a, b, width):
    dx, dy = b[0] - a[0], b[1] - a[1]
    length = math.hypot(dx, dy)
    if length < 1e-9:
        return []
    nx, ny = -dy / length * width / 2, dx / length * width / 2
    return [(a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny),
            (b[0] - nx, b[1] - ny), (a[0] - nx, a[1] - ny)]


def ass_path(paths, width):
    polygons = [polygon_segment(a, b, width) for path in paths for a, b in zip(path, path[1:])]
    return ' '.join('m ' + ' l '.join(f'{x:.2f} {y:.2f}' for x, y in poly) for poly in polygons if poly)


def clock(frame):
    # floor boundaries between decoded frame samples: every f/60 sample sees
    # its own state despite ASS's centisecond timestamp resolution.
    centis = (frame * 100) // 60
    hour, centis = divmod(centis, 360000)
    minute, centis = divmod(centis, 6000)
    second, centis = divmod(centis, 100)
    return f'{hour}:{minute:02d}:{second:02d}.{centis:02d}'


def event(frame, layer, text):
    return f'Dialogue: {layer},{clock(frame)},{clock(frame + 1)},Guide,,0,0,0,,{text}\n'


def ass_events(frame, geom):
    if geom is None:
        return ''
    if geom.get('mode') == 'observed-direction-pointers':
        out = ''
        for mark in geom['marks']:
            rgb = mark['color'].lstrip('#');color = rgb[4:6] + rgb[2:4] + rgb[:2]
            out += event(frame, 1, rf'{{\an7\pos(0,0)\p1\c&H00{color}&\bord2\3c&H000D0B08&\shad0\clip(224,32,1696,860)}}' + ass_path(mark['paths'],6) + r'{\p0}')
        for mark in [dict(label=geom['note'],labelRect=geom['noteRect']),*geom['marks']]:
            left,top,right,bottom=mark['labelRect'];box=f'm {left} {top} l {right} {top} {right} {bottom} {left} {bottom}'
            out += event(frame,2,r'{\an7\pos(0,0)\p1\c&H000D0B08&\alpha&H10&\bord0\shad0}'+box+r'{\p0}')
            size=34 if mark['label']==geom['note'] else 40
            out += event(frame,3,rf'{{\an7\pos({left+15},{top+7})\fs{size}\b1\c&H00F5F5F5&\bord0\shad0}}'+mark['label'])
        return out
    paths = ass_path(geom['paths'], 6)
    leader = ass_path([geom['leader']], 3)
    left, top, right, bottom = geom['labelRect']
    box = f'm {left:.2f} {top:.2f} l {right:.2f} {top:.2f} {right:.2f} {bottom:.2f} {left:.2f} {bottom:.2f}'
    output = event(frame, 1, r'{\an7\pos(0,0)\p1\c&H008ECE6C&\bord1.5\3c&H000D0B08&\shad0\clip(224,32,1696,860)}' + paths + r'{\p0}')
    output += event(frame, 1, r'{\an7\pos(0,0)\p1\c&H008ECE6C&\bord1\3c&H000D0B08&\shad0\clip(224,32,1696,860)}' + leader + r'{\p0}')
    output += event(frame, 2, r'{\an7\pos(0,0)\p1\c&H000D0B08&\alpha&H18&\bord0\shad0}' + box + r'{\p0}')
    output += event(frame, 3, rf'{{\an7\pos({left+12:.2f},{top:.2f})\fs40\b1\c&H00F5F5F5&\bord0\shad0}}' + geom['label'])
    return output


def still(clip, which, geom):
    source = clip[which + 'Frame']
    path = ROOT / source['path']
    assert sha(path) == source['sha256'], ('Inspected source still changed', path)
    image = Image.open(path).convert('RGB')
    assert image.size == (1920, 1080)
    canvas = Image.new('RGB', (1920, 1080), BLACK)
    canvas.paste(image.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS), (X, Y))
    if geom is not None and geom.get('mode') == 'observed-direction-pointers':
        draw = ImageDraw.Draw(canvas)
        for mark in geom['marks']:
            for path in mark['paths']:
                draw.line(path,fill=BLACK,width=10,joint='curve')
                draw.line(path,fill=mark['color'],width=6,joint='curve')
        for mark in [dict(label=geom['note'],labelRect=geom['noteRect']),*geom['marks']]:
            x0,y0,x1,y1=mark['labelRect'];draw.rectangle((x0,y0,x1,y1),fill=BLACK)
            font=ImageFont.truetype(str(FONT_FILE),34) if mark['label']==geom['note'] else FONT
            ink=font.getbbox(mark['label']);height=ink[3]-ink[1]
            draw.text((x0+15-ink[0],y0+((y1-y0)-height)/2-ink[1]),mark['label'],font=font,fill=WHITE)
    elif geom is not None:
        draw = ImageDraw.Draw(canvas)
        for lines, width in [(geom['paths'], 6), ([geom['leader']], 3)]:
            for line in lines:
                draw.line(line, fill=BLACK, width=width + 3, joint='curve')
                draw.line(line, fill=GREEN, width=width, joint='curve')
        x0, y0, x1, y1 = geom['labelRect']
        draw.rectangle((x0, y0, x1, y1), fill=BLACK)
        offset_x, offset_y = geom['inkOffset']
        ink = FONT.getbbox(geom['label'])
        height = ink[3] - ink[1]
        draw.text((x0 + 12 + offset_x, y0 + (58-height)/2 + offset_y), geom['label'], font=FONT, fill=WHITE)
    output = OUT / f'{clip["beatId"]}.{which}-display.png'
    canvas.save(output)
    mobile = output.with_name(output.stem + '.375.png')
    canvas.resize((375, 211), Image.Resampling.LANCZOS).save(mobile)
    return {'path': rel(output), 'sha256': sha(output), 'source': source['path'], 'sourceSha256': source['sha256'],
            'sourceSeconds': source['sourceSeconds'], 'guideVisible': geom is not None,
            'mobile': rel(mobile), 'mobileSha256': sha(mobile)}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--clip',choices=list(LABELS));args=parser.parse_args()
    control = read(ROOT / 'shared/publishing/video-production-control.json')
    assert control['selectedVideo'] == PROJECT.name
    assert control['newProductionAuthorization']['fullProductionAuthorized']
    plan, old = read(PLAN), read(LEGACY)
    OUT.mkdir(parents=True, exist_ok=True)
    rows, bounds, total_visible = [], [], 0
    previous=read(OUT/'guide-outputs.json') if args.clip else None
    previous_rows={r['id']:r for r in previous['clips']} if previous else {}
    previous_bounds=read(OUT/'guide-label-bounds.json')['rows'] if previous else []
    if previous:
        backup=OUT/('before-'+args.clip+'-direction-pointers');backup.mkdir(exist_ok=True)
        owned=previous_rows[args.clip]
        for file in [OUT/'guide-outputs.json',OUT/'guide-label-bounds.json',ROOT/owned['assFile'],ROOT/owned['firstDisplay'],ROOT/owned['lastDisplay']]:
            dest=backup/file.name
            if not dest.exists():shutil.copy2(file,dest)
    for clip in plan['clips']:
        if args.clip and clip['id'] != args.clip:
            row=previous_rows[clip['id']]
            assert sha(ROOT/row['assFile'])==row['assSha256']
            for endpoint in row['stills'].values():
                assert sha(ROOT/endpoint['path'])==endpoint['sha256'] and sha(ROOT/endpoint['mobile'])==endpoint['mobileSha256']
            rows.append(row);bounds += [b for b in previous_bounds if b['clip']==clip['id']]
            total_visible += row['visibleFrames'];continue
        keys = tracking_keys(clip, old)
        count = clip['frames']
        assert count == clip['sourceFrames'] == round((clip['sourceOutExclusive'] - clip['sourceIn']) * 60)
        start = round(clip['sourceIn'] * 60)
        geometries = [guide_geometry(clip, state_at(clip, keys, start + frame),start+frame,frame) for frame in range(count)]
        ass = HEADER
        visible = []
        for frame, geom in enumerate(geometries):
            ass += ass_events(frame, geom)
            if geom is None:
                continue
            visible.append(frame)
            if geom.get('mode') == 'observed-direction-pointers':
                for mark in [dict(labelRect=geom['noteRect'],paths=[]),*geom['marks']]:
                    box=mark['labelRect'];assert X<=box[0]<box[2]<=X+WIDTH and Y<=box[1]<box[3]<880
                    assert all(X<=px<=X+WIDTH and Y<=py<=Y+HEIGHT for path in mark['paths'] for px,py in path)
                    bounds.append({'clip':clip['id'],'frame':frame,'labelRect':list(box),'mode':'observed-direction-pointer'})
                continue
            box = geom['labelRect']
            assert box[0] >= X and box[2] <= X + WIDTH and box[1] >= Y and box[3] < 880
            # Geometry is source-bound and clipped to the same content rectangle.
            allpoints = [p for path in geom['paths'] for p in path]
            allpoints += geom['leader']
            assert all(X <= px <= X + WIDTH and Y <= py <= Y + HEIGHT for px, py in allpoints), (clip['id'], frame)
            bounds.append({'clip': clip['id'], 'frame': frame, 'labelRect': [round(v, 2) for v in box]})
        path = OUT / f'{clip["beatId"]}.guide.ass'
        path.write_text(ass, encoding='utf-8-sig')
        first, last = still(clip, 'first', geometries[0]), still(clip, 'last', geometries[-1])
        total_visible += len(visible)
        rows.append({'id': clip['id'], 'beatId': clip['beatId'], 'frames': count,
                     'sourceIn': clip['sourceIn'], 'sourceOutExclusive': clip['sourceOutExclusive'],
                     'verifiedKeyCount': len(keys), 'firstVerifiedSourceFrame': keys[0][0], 'lastVerifiedSourceFrame': keys[-1][0],
                     'assFile': rel(path), 'assSha256': sha(path), 'visibleFrames': len(visible),
                     'firstVisibleRelativeFrame': visible[0] if visible else None, 'lastVisibleRelativeFrame': visible[-1] if visible else None,
                     'firstDisplay': first['path'], 'lastDisplay': last['path'], 'stills': {'first': first, 'last': last},
                     'label': '앞쪽 · 조종부 / 위쪽 · 머리 쪽' if clip['id']=='mk-body-up' and 'directionPointers' in clip['annotation'] else LABELS[clip['id']], 'clearAtSourceCut': True})
    # Explicit regression guard for the verified Zelda attachment hide.
    zelda = next(row for row in rows if row['id'] == 'zelda-log-position')
    assert (zelda['firstVisibleRelativeFrame'], zelda['lastVisibleRelativeFrame']) == (15, 266)
    assert not zelda['stills']['first']['guideVisible'] and not zelda['stills']['last']['guideVisible']
    output = {'schemaVersion': 1, 'scope': 'CPU ASS plus existing-source first/last PNG annotation only',
              'inputs': {'footagePlan': rel(PLAN), 'footagePlanSha256': sha(PLAN),
                         'annotationPlan': rel(LEGACY), 'annotationPlanSha256': sha(LEGACY),
                         'helperSha256': sha(Path(__file__)), 'fontSha256': sha(FONT_FILE)},
              'layout': {'source': [1920, 1080], 'contentRect': [X, Y, WIDTH, HEIGHT],
                         'uniformScale': SCALE, 'guideGreen': GREEN, 'strokePx': 6, 'labelPx': 40,
                         'font': 'Malgun Gothic Bold', 'captionReserveMinY': 880},
              'tracking': {'method': 'Reuse dense inspected sourceWindow keys, override exact frame with current final verified keys; linear interpolation only between visible observations',
                           'beforeFirstKey': 'hidden', 'afterLastKey': 'hidden', 'falseKey': 'hide immediately; never interpolate to zero bbox',
                           'assFrameTiming': 'floor centisecond event boundaries preserve exact per-frame state at native 60fps sample times',
                           'measurements': 'Editorial image-space brackets/parallel shaft contours/observable-part direction pointers only; no internal axes, angle, detector or world-distance claim',
                           'sourceCut': 'Separate beat-local ASS; no event outside its own finite clip'},
              'clips': rows, 'checks': {'clips': len(rows), 'totalFrames': sum(r['frames'] for r in rows),
                                      'visibleFrameGeometryAndLabelBoundsChecked': total_visible,
                                      'zelda994_2HidePassed': True, 'noAddedCreatorCredits': True,
                                      'newVideoDecodeOrGpuJobs': 0},
              'review': {'nativeAnd375StillDirectReview': 'pending', 'actualEncodedAssFontAndMovingGuideReview': 'pending root composition',
                         'actualFinalCaptionReview': 'pending root composition'}}
    save(OUT / 'guide-outputs.json', output)
    save(OUT / 'guide-label-bounds.json', {'inputs': output['inputs'], 'rows': bounds})
    print(json.dumps({'clips': len(rows), 'frames': sum(r['frames'] for r in rows), 'visible': total_visible,
                      'output': rel(OUT / 'guide-outputs.json'), 'sha256': sha(OUT / 'guide-outputs.json')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
