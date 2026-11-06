"""Deterministic CPU-only frame composer for the existing 03.02 native capture.

Import NativeFrameComposer, then call compose(mode, frame_index, ...). Both
cameras and all geometry guides use that exact trace row. 270 frames at60fps
cover [0,4.5s); there is no looping, freezing, retiming or engine invocation.

Example (one sample only, never a whole-film render):
  python composite-native-frame.py --mode narrow --frame 70 --layout dual \
    --caption "같은 입력이어도" --caption "여기서 막힙니다." --write-sample

No import-time writes. The caller owns actual speech timing and editorial cuts.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
from fractions import Fraction
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
PROJECT = Path(__file__).resolve().parents[1]
FPS = 60
FRAME_COUNT = 270


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def frame_at_seconds(seconds) -> int:
    """Presentation time, end exclusive. Invalid/outside times never wrap."""
    if isinstance(seconds, bool):
        raise ValueError('A boolean is not a clip time')
    try:
        time = Fraction(str(seconds))
    except (ValueError, ZeroDivisionError) as error:
        raise ValueError('Finite clip time required') from error
    if time < 0 or time >= Fraction(FRAME_COUNT, FPS):
        raise ValueError('Native clip time must be in [0,4.5), without loops/holds')
    return int(time * FPS)


class ComposedFrame:
    def __init__(self, image: Image.Image, evidence: dict):
        self.image = image
        self.evidence = evidence


class NativeFrameComposer:
    def __init__(self, project=PROJECT):
        self.project = Path(project).resolve()
        if self.project != PROJECT.resolve():
            raise ValueError('This helper is scoped to the selected 03.02 project')
        self.layout_path = self.project / 'visual-layout-v1.json'
        self.spec = read(self.layout_path)
        if self.spec['topicId'] != '03.02':
            raise ValueError('Wrong topic layout')
        self.layout_sha = sha(self.layout_path)
        native = self.spec['nativeCropMaps']
        self.native_root = Path(native['artifactRoot']).resolve()
        self.evidence_path = ROOT / native['evidence']['path']
        self.native_evidence = read(self.evidence_path)
        if sha(self.evidence_path) != native['evidence']['sha256']:
            raise ValueError('Native evidence changed; review it before composing')
        self.evidence_sha = sha(self.evidence_path)
        if Path(self.native_evidence['output']).resolve() != self.native_root:
            raise ValueError('Evidence points to another attempt')
        self.fingerprint = native['evidence']['fingerprint']
        if self.native_evidence['fingerprint'] != self.fingerprint:
            raise ValueError('Native fingerprint mismatch')
        if self.fingerprint not in (self.native_root / 'capture-complete.txt').read_text():
            raise ValueError('Missing matching native completion marker')
        self.trace = {}
        self.trace_sha = {}
        for mode in ('narrow', 'wide'):
            marker = read(self.native_root / mode / 'mode-complete.json')
            if (marker['fingerprint'], marker['frames'], marker['fps'], marker['width'], marker['height']) != (
                    self.fingerprint, FRAME_COUNT, FPS, 1920, 1080):
                raise ValueError('Incomplete or different native mode: ' + mode)
            path = self.native_root / mode / 'trace.csv'
            self.trace_sha[mode] = sha(path)
            if self.trace_sha[mode] != self.native_evidence['traceSHA256'][mode]:
                raise ValueError('Trace changed: ' + mode)
            with path.open(encoding='utf8', newline='') as handle:
                rows = list(csv.DictReader(handle))
            if len(rows) != FRAME_COUNT:
                raise ValueError('Exactly270 native trace rows required')
            self.trace[mode] = rows
            for index, row in enumerate(rows):
                if int(row['frame']) != index or row['blocked'] not in ('0', '1'):
                    raise ValueError('Noncontiguous trace or invalid state')
                if not all(math.isfinite(float(row[key])) for key in (
                        'width', 'playerDiameter', 'playerX', 'playerZ', 'commandX', 'commandZ')):
                    raise ValueError('Nonfinite trace coordinate')
        for a, b in zip(self.trace['narrow'], self.trace['wide']):
            if any(a[key] != b[key] for key in ('frame', 'commandX', 'commandZ', 'playerDiameter')):
                raise ValueError('Narrow/wide input clock mismatch')
        self.sample_pins = {
            Path(item['path']).resolve(): item['sha256']
            for sample in native['sampledFrames'] for item in sample['sourceFiles']
        }
        self.tokens = self.spec['tokens']['scene']
        self.caption_tokens = self.spec['tokens']['caption']
        self.font_paths = {item['path']: item['sha256'] for item in self.spec['fontMeasurement']['fontFiles']}
        for path, digest in self.font_paths.items():
            if sha(Path(path)) != digest:
                raise ValueError('Measured font changed: ' + path)
        self.font_cache = {}
        self.cat_images = {}
        for pose in self.spec['cat']['poses']:
            path = ROOT / pose['path']
            if sha(path) != pose['sha256']:
                raise ValueError('Original brand pose changed')
            with Image.open(path) as image:
                self.cat_images[pose['pose']] = image.convert('RGBA')
        self._check_geometry_containment()

    def _check_geometry_containment(self):
        """Read all actual trace rows, without claiming actual moving review."""
        top = self.spec['nativeCropMaps']['top']
        if top['cropRotatedXYWH'] != [0, 700, 1080, 540]:
            raise ValueError('Unexpected top crop; needs a new containment review')
        if self.spec['nativeCropMaps']['observer']['cropSourceXYWH'] != [480, 180, 1440, 900]:
            raise ValueError('Unexpected observer crop; needs a new containment review')
        camera = self.spec['nativeCropMaps']['editorialPostOverlay']['topCamera']
        if camera['rotationEuler'] != [90, 0, 0]:
            raise ValueError('Projection only supports the verified top camera')
        pixel_per_world = 1080 / (2 * camera['orthographicSize'])
        for rows in self.trace.values():
            for row in rows:
                u, v = self._world_to_top(float(row['playerX']), float(row['playerZ']))
                radius = float(row['playerDiameter']) * .5 * pixel_per_world
                if not (700 <= u-radius and u+radius <= 1240 and 0 <= v-radius and v+radius <= 1080):
                    raise ValueError('Crop loses an actual projected collision footprint')

    def _unchanged(self):
        if sha(self.layout_path) != self.layout_sha or sha(self.evidence_path) != self.evidence_sha:
            raise ValueError('Layout/evidence changed after composer initialization')
        for mode, digest in self.trace_sha.items():
            if sha(self.native_root / mode / 'trace.csv') != digest:
                raise ValueError('Native trace changed during composition')

    def font(self, size, weight=700, caption=False):
        key = (size, weight, caption)
        if key not in self.font_cache:
            path = ('C:/Windows/Fonts/NotoSansKR-VF.ttf' if caption
                    else 'C:/Windows/Fonts/malgunbd.ttf')
            font = ImageFont.truetype(path, size)
            if caption:
                font.set_variation_by_axes([weight])
            self.font_cache[key] = font
        return self.font_cache[key]

    def text(self, draw, text, xy, size, color, weight=700):
        draw.text(xy, text, font=self.font(size, weight), fill=color, anchor='mm')

    def _world_to_top(self, x, z):
        camera = self.spec['nativeCropMaps']['editorialPostOverlay']['topCamera']
        px, _, pz = camera['position']
        scale = 1080 / (2 * camera['orthographicSize'])
        return 960 + (x-px)*scale, 540 - (z-pz)*scale

    def _top_point(self, x, z, upper=False):
        u, v = self._world_to_top(x, z)
        dest = self.spec['nativeCropMaps']['top']['destinationInUpper' if upper else 'destinationInLower']
        crop = self.spec['nativeCropMaps']['top']['cropRotatedXYWH']
        scale = self.spec['nativeCropMaps']['top']['uniformScale']
        return dest[0] + (1079-v-crop[0])*scale, dest[1] + (u-crop[1])*scale

    def _picture(self, canvas, mode, frame, view, upper):
        path = self.native_root / mode / view / f'{frame:04d}.jpg'
        data = path.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        if path.resolve() in self.sample_pins and digest != self.sample_pins[path.resolve()]:
            raise ValueError('A visually reviewed sample changed: ' + str(path))
        with Image.open(io.BytesIO(data)) as image:
            if image.size != (1920, 1080):
                raise ValueError('Unexpected native image dimensions')
            image = image.convert('RGB')
        mapping = self.spec['nativeCropMaps'][view]
        if view == 'top':
            image = image.transpose(Image.Transpose.ROTATE_270)
            x, y, w, h = mapping['cropRotatedXYWH']
        else:
            x, y, w, h = mapping['cropSourceXYWH']
        image = image.crop((x, y, x+w, y+h))
        dest = mapping['destinationInUpper' if upper else 'destinationInLower']
        dx, dy, dw, dh = dest
        if abs(dw / w - dh / h) > 1e-9:
            raise ValueError('Nonuniform native image scaling prohibited')
        canvas.paste(image.resize((dw, dh), Image.Resampling.LANCZOS), (dx, dy))
        return dict(path=path.as_posix(), sha256=digest, view=view, frame=frame,
                    crop=[x, y, w, h], rotation=90 if view == 'top' else 0, destination=dest)

    def _guides(self, canvas, row, upper):
        draw = ImageDraw.Draw(canvas)
        x, z = float(row['playerX']), float(row['playerZ'])
        radius = float(row['playerDiameter']) / 2
        cart_half_length = next(t for t in self.spec['overlayTargets'] if t['id'] == 'cart-footprint')['size'][2] / 2
        blocked, passed = row['blocked'] == '1', z-radius > cart_half_length
        role = 'problem' if blocked else 'result' if passed else 'relationship'
        color = self.tokens[role]
        points = [self._top_point(x + radius*math.cos(i*math.pi/48),
                                 z + radius*math.sin(i*math.pi/48), upper) for i in range(97)]
        overlay = self.spec['nativeCropMaps']['editorialPostOverlay']
        draw.line(points, fill=color, width=overlay['strokeNativeCompositePx'], joint='curve')
        sample_z = overlay['clearanceSampleWorldZ']
        cart_half_width = next(t for t in self.spec['overlayTargets'] if t['id'] == 'cart-footprint')['size'][0] / 2
        a = self._top_point(cart_half_width, sample_z, upper)
        b = self._top_point(float(row['width']) / 2, sample_z, upper)
        draw.line([a, b], fill=self.tokens['title'], width=overlay['strokeNativeCompositePx'])
        tick = overlay['endpointTickPx'] / 2
        for p in (a, b):
            draw.line([(p[0]-tick, p[1]), (p[0]+tick, p[1])], fill=self.tokens['title'], width=8)
        center = self._top_point(x, z, upper)
        input_label = None
        if not upper:
            # Same layout as the root-reviewed375px prototype. Keep all labels
            # inside the lower image reservation, above the fixed captions.
            self.text(draw, '사람이 지날 틈', (700, 1133), 40, self.tokens['title'])
            mid = ((a[0]+b[0])/2, (a[1]+b[1])/2)
            draw.line([(610, 1158), (mid[0]+16, mid[1])], fill=self.tokens['title'], width=4)
            label_x = 720 if center[0] > 650 else 210
            self.text(draw, '충돌 영역', (label_x, 1408), 40, color)
            draw.line([(label_x, 1380), (center[0], center[1]+31)], fill=color, width=4)
            if blocked:
                # UpdateGuides() draws the native green forward-intent arrow
                # from player z+.45 to z+1.11. Mark its shaft, not a measured
                # velocity: the attempted input persists while movement stops.
                arrow_target = self._top_point(x, z+.78, upper)
                self.text(draw, '이동 입력', (720, 1408), 40, self.tokens['relationship'])
                draw.line([(640, 1380), (arrow_target[0], arrow_target[1]+14)],
                          fill=self.tokens['relationship'], width=4)
                input_label = dict(text='이동 입력', target=list(arrow_target),
                    meaning='native forward-intent cue, not actual displacement',
                    geometrySource='TunnelExperiment.UpdateGuides: shaft z+.45 to z+1.11')
        return dict(kind='editorial post-overlay reconstructed from own native geometry',
                    nativeThickGuide=False, depthTested=False, noTF2Measurement=True,
                    role=role, blocked=blocked, footprintClearsCart=passed,
                    capsuleCenter=list(center), radiusWorld=radius,
                    clearanceEndpoints=[list(a), list(b)], inputArrowLabel=input_label)

    def _cat(self, canvas, pose):
        if pose not in self.cat_images:
            raise ValueError('Unknown original brand pose')
        layout = self.spec['cat']['layout']
        image = self.cat_images[pose].resize(tuple(layout['spriteSize']), Image.Resampling.LANCZOS)
        layer = Image.new('RGBA', canvas.size)
        layer.alpha_composite(image, tuple(layout['poseTopLeft'][pose]))
        mask = Image.new('L', canvas.size)
        x, y, w, h = layout['visibleClipRect']
        ImageDraw.Draw(mask).rectangle((x, y, x+w-1, y+h-1), fill=255)
        layer.putalpha(ImageChops.multiply(layer.getchannel('A'), mask))
        canvas.paste(layer, (0, 0), layer)

    def _captions(self, canvas, lines, emphasis=None):
        """Optional single (line,start,end,role) emphasis; plain SRT stays external."""
        if not lines:
            if emphasis is not None:
                raise ValueError('Cannot emphasize an absent caption')
            return None
        cfg = self.spec['caption']
        if len(lines) > cfg['maxLines'] or any(not isinstance(t, str) or not t.strip() for t in lines):
            raise ValueError('Caption requires one/two nonempty spoken-clause lines')
        if emphasis is not None:
            line, start, end, role = emphasis
            if role not in ('term', 'result', 'problem') or not (0 <= line < len(lines) and 0 <= start < end <= len(lines[line])):
                raise ValueError('One valid caption emphasis span required')
        runs = []
        for i, text in enumerate(lines):
            if emphasis is not None and i == emphasis[0]:
                _, start, end, role = emphasis
                parts = [(text[:start], 500, 'text'), (text[start:end], 700, role), (text[end:], 500, 'text')]
            else:
                parts = [(text, 500, 'text')]
            runs.append([(t, self.font(cfg['fontPx'], weight, True), self.caption_tokens[role]) for t, weight, role in parts if t])
        widths = [sum(font.getlength(text) for text, font, color in row) for row in runs]
        if max(widths) > cfg['textMaxWidthPx']:
            raise ValueError('Caption too wide; split an actual spoken clause, never shrink')
        width = math.ceil(max(widths)) + cfg['paddingX'] * 2
        height = len(lines) * cfg['lineHeightPx'] + cfg['paddingY'] * 2
        cx, cy = cfg['nativeCenter']; x, y = cx-width/2, cy-height/2
        dx, dy = cfg['hardShadowOffset']; draw = ImageDraw.Draw(canvas)
        draw.rectangle((x+dx, y+dy, x+width+dx, y+height+dy), fill=self.caption_tokens['shadow'])
        draw.rectangle((x, y, x+width, y+height), fill=self.caption_tokens['background'],
                       outline=self.caption_tokens['border'], width=cfg['borderPx'])
        for i, row in enumerate(runs):
            cursor = cx-widths[i]/2
            baseline = cy + (i-(len(lines)-1)/2) * cfg['lineHeightPx'] - 1
            for text, font, color in row:
                w = font.getlength(text)
                draw.text((cursor+w/2, baseline), text, font=font, fill=color, anchor='mm')
                cursor += w
        return dict(center=cfg['nativeCenter'], bounds=[x, y, width, height],
                    lines=list(lines), emphasis=emphasis, actualSpeechTimingVerified=False)

    def compose(self, mode, frame_index, *, layout='dual', caption_lines=(),
                caption_emphasis=None, cat_pose=None, editorial_guides=True):
        """Return a1080x1920 image and evidence; no files, models or apps started."""
        if mode not in self.trace or type(frame_index) is not int or not 0 <= frame_index < FRAME_COUNT:
            raise ValueError('Use narrow/wide and exact native frame0..269; never repeat the clip')
        if layout not in ('dual', 'single-observer', 'single-top'):
            raise ValueError('Unsupported reviewed layout')
        if layout == 'dual' and cat_pose:
            raise ValueError('Cat must remain hidden during the dual-camera comparison')
        self._unchanged()
        row = self.trace[mode][frame_index]
        canvas = Image.new('RGB', (1080, 1920), self.tokens['background'])
        draw = ImageDraw.Draw(canvas)
        title = self.spec['title']
        for text, y, size, role in zip(title['headerLines'], title['lineCentersY'], title['fontPx'], title['lineColors']):
            self.text(draw, text, (title['centerX'], y), size, self.tokens[role])
        state = '원래 폭 · 같은 입력' if mode == 'narrow' else '벽만 넓힘 · 같은 입력'
        self.text(draw, state, (492, 350), 36, self.tokens['muted'])
        pictures, guides = [], None
        if layout == 'dual':
            self.text(draw, '직접 만든 Unity 시연 · 사선', (492, 397), 40, self.tokens['ink'])
            pictures.append(self._picture(canvas, mode, frame_index, 'observer', True))
            self.text(draw, '위에서 본 같은 순간 · 가로 회전', (492, 946), 40, self.tokens['relationship'])
            pictures.append(self._picture(canvas, mode, frame_index, 'top', False))
            if editorial_guides:
                guides = self._guides(canvas, row, False)
        else:
            view = layout.removeprefix('single-')
            self.text(draw, '직접 만든 Unity 시연 · 해설용', (492, 397), 40, self.tokens['relationship'])
            pictures.append(self._picture(canvas, mode, frame_index, view, True))
            if view == 'top' and editorial_guides:
                guides = self._guides(canvas, row, True)
            if cat_pose:
                self._cat(canvas, cat_pose)
        caption = self._captions(canvas, tuple(caption_lines), caption_emphasis)
        return ComposedFrame(canvas, dict(topicId='03.02', mode=mode, frame=frame_index,
            presentationPtsSeconds=frame_index/FPS,
            simulationElapsedAfterStepSeconds=(frame_index+1)/FPS,
            clipDurationSeconds=FRAME_COUNT/FPS, endExclusive=True, noLoopOrHold=True,
            layout=layout, layoutSHA256=self.layout_sha, nativeFingerprint=self.fingerprint,
            nativeEvidenceSHA256=self.evidence_sha, traceSHA256=self.trace_sha[mode],
            traceState=row, pictures=pictures, editorialGuides=guides,
            catPose=cat_pose, caption=caption, sourceAudioOrMusicProcessed=False,
            QA='Single deterministic CPU composite; no moving/encoded/audio/human-review approval'))


def png_bytes(image):
    target = io.BytesIO()
    image.save(target, format='PNG', compress_level=6)
    return target.getvalue()


def save_once(path, data):
    if path.exists():
        if path.read_bytes() != data:
            raise FileExistsError('Preserve differing existing sample: ' + str(path))
        return
    with path.open('xb') as handle:
        handle.write(data)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=['narrow', 'wide'], default='narrow')
    parser.add_argument('--frame', type=int, default=70)
    parser.add_argument('--layout', choices=['dual', 'single-observer', 'single-top'], default='dual')
    parser.add_argument('--cat', choices=['puzzled', 'realize', 'relief'])
    parser.add_argument('--caption', action='append', default=[])
    parser.add_argument('--write-sample', action='store_true', help='Only one master PNG/mobile PNG/receipt; no video renderer')
    args = parser.parse_args()
    composer = NativeFrameComposer()
    result = composer.compose(args.mode, args.frame, layout=args.layout, cat_pose=args.cat, caption_lines=args.caption)
    # Determinism is independent of call order. This does not advance a clock.
    composer.compose('wide', 269, layout='single-top', cat_pose='realize')
    repeated = composer.compose(args.mode, args.frame, layout=args.layout, cat_pose=args.cat, caption_lines=args.caption)
    if result.image.tobytes() != repeated.image.tobytes():
        raise AssertionError('Frame composition depends on prior calls')
    for value in (-1, 4.5, 'NaN'):
        try:
            frame_at_seconds(value)
        except ValueError:
            pass
        else:
            raise AssertionError('Invalid clip time accepted')
    assert frame_at_seconds(0) == 0 and frame_at_seconds('4.499') == 269
    if args.write_sample:
        output_root = Path(composer.native_evidence['output']).parents[2] / 'compositor-prep-v1'
        # Dedicated output root, outside immutable native attempts/source paths.
        expected = Path('C:/Users/1/Videos/YamyamProduction/architectural-111-20261106/compositor-prep-v1')
        if output_root.resolve() != expected.resolve():
            raise ValueError('Unexpected sample output location')
        # A code revision gets its own deterministic receipt directory; never
        # overwrite an earlier sample/receipt just because pixels look alike.
        output = output_root / sha(Path(__file__))[:12]
        output.mkdir(parents=True, exist_ok=True)
        stem = f'{args.mode}-f{args.frame:03d}-{args.layout}'
        master, mobile = output/(stem+'.1080x1920.png'), output/(stem+'.375px.png')
        save_once(master, png_bytes(result.image))
        save_once(mobile, png_bytes(result.image.resize((375, 667), Image.Resampling.LANCZOS)))
        result.evidence.update(helperSHA256=sha(Path(__file__)), deterministicCallOrderCheck=True,
            sourceFilesUnchangedAfterCompose=all(sha(Path(p['path'])) == p['sha256'] for p in result.evidence['pictures']),
            outputFiles=[dict(path=p.as_posix(), sha256=sha(p)) for p in (master, mobile)])
        receipt = output/(stem+'.receipt.json')
        save_once(receipt, (json.dumps(result.evidence, ensure_ascii=False, indent=2)+'\n').encode('utf8'))
    print(json.dumps(result.evidence, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
