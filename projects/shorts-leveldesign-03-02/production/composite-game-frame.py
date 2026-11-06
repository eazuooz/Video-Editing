"""CPU-only composition of an already decoded selected TF2 RGB frame.

GameFrameComposer().compose(frame, source_id=..., local_pts=...) shares the
native helper's title, caption and original-cat implementation. It never
decodes a video or starts ffmpeg. Pass the frame's actual source presentation
PTS, even when the caller repeats that30fps frame in a60fps output.

Only the checked26–29s opening has object marks. Exact checked RGB/PTS pins
must match; otherwise annotations are withheld rather than extrapolated.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw

PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT.parents[1]
TRACKING = PROJECT / 'opening-cart-tracking-v1.json'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


class GameFrameComposer:
    def __init__(self, tracking_path=None):
        default_v2 = PROJECT / 'opening-cart-tracking-v2.json'
        self.tracking_path = Path(tracking_path) if tracking_path else (default_v2 if default_v2.is_file() else TRACKING)
        if self.tracking_path.resolve() not in (TRACKING.resolve(), default_v2.resolve()):
            raise ValueError('Tracking must remain in this selected project')
        self.tracking = read(self.tracking_path)
        self.tracking_sha = sha(self.tracking_path)
        self.style_path = ROOT / self.tracking['nativeStyleHelperPath']
        if sha(self.style_path) != self.tracking['nativeStyleHelperSHA256']:
            raise ValueError('Native shared styles changed; review the companion before use')
        loader = importlib.util.spec_from_file_location('leveldesign03_native_style', self.style_path)
        native = importlib.util.module_from_spec(loader)
        loader.loader.exec_module(native)
        self.style_module = native
        self.style = native.NativeFrameComposer()
        if self.style.layout_sha != self.tracking['layoutSHA256']:
            raise ValueError('Gameplay layout changed after tracking review')
        self.source_record_path = ROOT / self.tracking['sourceRecordPath']
        if sha(self.source_record_path) != self.tracking['sourceRecordSHA256']:
            raise ValueError('Selected source record changed; review new inputs')
        self.sources = {}
        self.source_stats = {}
        for item in read(self.source_record_path)['sources']:
            if not item.get('selectedForCut'):
                continue
            path = Path(item['path'])
            if sha(path) != item['sha256'] or (item['width'], item['height']) != (1920, 1080):
                raise ValueError('Selected footage hash or dimensions differ')
            self.sources[item['id']] = item
            self.source_stats[item['id']] = (path.stat().st_size, path.stat().st_mtime_ns)
        self.checked_frames = self.tracking['frames']
        self.viewport = self.style.spec['pictureModes']['actualGameplay']['viewport']
        if abs(self.viewport[2] / 1920 - self.viewport[3] / 1080) > 1e-12:
            raise ValueError('Full original16:9 must use one uniform scale')

    def _unchanged(self, source_id):
        self.style._unchanged()
        if sha(self.tracking_path) != self.tracking_sha or sha(self.style_path) != self.tracking['nativeStyleHelperSHA256']:
            raise ValueError('Tracking/shared compositor changed during composition')
        if sha(self.source_record_path) != self.tracking['sourceRecordSHA256']:
            raise ValueError('Source selection changed during composition')
        path = Path(self.sources[source_id]['path'])
        if (path.stat().st_size, path.stat().st_mtime_ns) != self.source_stats[source_id]:
            raise ValueError('Bound source changed after its SHA256 verification')

    def annotations_for(self, source_id, local_pts, decoded_rgb_sha256=None):
        """No nearest-frame lookup, prediction, cut bridging or out-of-window marks."""
        if source_id != self.tracking['sourceId']:
            return [], 'no-verified-track-for-source'
        start = self.tracking['inspection'].get('annotationWindowStartInclusive', 26)
        if not start <= local_pts < self.tracking['inspection']['annotationWindowEndExclusive']:
            return [], 'outside-verified-opening-window'
        matches = [f for f in self.checked_frames if abs(f['localPtsSeconds']-local_pts) <= .000001]
        if len(matches) != 1:
            return [], 'not-an-exact-checked-source-pts'
        frame = matches[0]
        if decoded_rgb_sha256 != frame['decodedRGBSHA256']:
            return [], 'incoming-rgb-does-not-match-checked-source-frame'
        return frame['marks'], 'exact-source-rgb-and-pts-match' if frame['marks'] else 'target-hidden-in-checked-frame'

    def _map_point(self, x, y):
        dx, dy, width, _ = self.viewport
        scale = width / 1920
        return dx + x*scale, dy + y*scale

    def _marks(self, canvas, marks):
        # All text is outside the source. Thin leaders and thick hollow regions
        # are editorial guides, never a game's collider or detector output.
        layer = Image.new('RGBA', canvas.size)
        draw = ImageDraw.Draw(layer)
        cfg = self.tracking['drawing']
        for mark in marks:
            color = self.style.tokens[mark['role']]
            x1, y1, x2, y2 = mark['sourceBBoxXYXY']
            if not (0 < x1 < x2 < 1920 and 0 < y1 < y2 < 1080):
                raise ValueError('Never extend a verified region beyond the source')
            a, b = self._map_point(x1, y1), self._map_point(x2, y2)
            draw.ellipse((*a, *b), outline=color, width=cfg['strokePortraitPx'])
            lx, ly = mark['labelCenter']
            draw.line([(lx, ly+22), ((a[0]+b[0])/2, a[1])], fill=color,
                      width=cfg['leaderPortraitPx'])
            self.style.text(draw, mark['labelKo'], (lx, ly), cfg['labelFontPx'], color)
        # Preserve the original timer, kill feed, weapon UI, healer label,
        # watermark and bottom HUD. No annotation paints through those areas.
        for rect in cfg['hudProtectedSourceRectsXYXY']:
            a, b = self._map_point(*rect[:2]), self._map_point(*rect[2:])
            draw.rectangle((*a, *b), fill=(0, 0, 0, 0))
        canvas.paste(layer, (0, 0), layer)

    def compose(self, frame, *, source_id, local_pts, caption_lines=(),
                caption_emphasis=None, cat_pose=None, annotations=True):
        if not isinstance(frame, Image.Image) or frame.mode != 'RGB' or frame.size != (1920, 1080):
            raise ValueError('Pass an already decoded1920x1080 RGB PIL image')
        if source_id not in self.sources:
            raise ValueError('Only selected, bound independent gameplay is accepted')
        if isinstance(local_pts, bool):
            raise ValueError('Source PTS must be finite local seconds')
        try:
            pts = float(local_pts)
        except (ValueError, TypeError) as error:
            raise ValueError('Source PTS must be finite local seconds') from error
        if not math.isfinite(pts) or not 0 <= pts < float(self.sources[source_id]['duration']):
            raise ValueError('Source PTS lies outside the selected source file')
        self._unchanged(source_id)
        rgb_sha = hashlib.sha256(frame.tobytes()).hexdigest()
        marks, state = self.annotations_for(source_id, pts, rgb_sha)
        if not annotations:
            marks, state = [], 'editorially-disabled'
        canvas = Image.new('RGB', (1080, 1920), self.style.tokens['background'])
        draw = ImageDraw.Draw(canvas)
        title = self.style.spec['title']
        for text, y, size, role in zip(title['headerLines'], title['lineCentersY'], title['fontPx'], title['lineColors']):
            self.style.text(draw, text, (title['centerX'], y), size, self.style.tokens[role])
        self.style.text(draw, 'TEAM FORTRESS 2 · 실제 게임 화면', (492, 350), 36, self.style.tokens['muted'])
        dx, dy, width, height = self.viewport
        scale = width / 1920
        # Continuous affine mapping retains the exact888x499.5 rectangle.
        # Rounding it to888x500 and stretching would alter the source aspect.
        picture = frame.convert('RGBA').transform(canvas.size, Image.Transform.AFFINE,
            (1/scale, 0, -dx/scale, 0, 1/scale, -dy/scale), Image.Resampling.BICUBIC,
            fillcolor=(0, 0, 0, 0))
        canvas.paste(picture, (0, 0), picture)
        self._marks(canvas, marks)
        if cat_pose:
            self.style._cat(canvas, cat_pose)
        caption = self.style._captions(canvas, tuple(caption_lines), caption_emphasis)
        return self.style_module.ComposedFrame(canvas, dict(topicId='03.02',
            sourceId=source_id, sourcePath=self.sources[source_id]['path'],
            sourceSHA256=self.sources[source_id]['sha256'], sourceLocalPtsSeconds=pts,
            sourceNativeFps=self.sources[source_id]['fps'], sourceSpeed=1,
            sourceFpsNotOutputFps=True, sourceRGBSHA256=rgb_sha,
            inputBinding='Incoming RGB/PTS checked against reviewed pins for annotations; other frame origin is supplied by the caller-bound decoder',
            viewport=self.viewport, uniformScale=scale, sourceCrop=None,
            fullOriginalHUDRetained=True, temporalFrameInterpolation=False, loop=False,
            trackingSHA256=self.tracking_sha, layoutSHA256=self.style.layout_sha,
            sharedNativeStyleSHA256=self.tracking['nativeStyleHelperSHA256'],
            annotationState=state, annotations=marks, catPose=cat_pose, caption=caption,
            QA='Single CPU composition; not encoded-motion, speech-timing, audio or human-final approval'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-sample', action='store_true')
    args = parser.parse_args()
    composer = GameFrameComposer()
    media = Path(composer.tracking['inspection']['decodeManifest']).parent
    with Image.open(media / 'first-frame-rgb.png') as original:
        image = original.convert('RGB')
    source_id = composer.tracking['sourceId']
    # One meaningful boundary check: the same image cannot carry a stale mark
    # before/at/after the reviewed window, or on a different selected clip.
    window_start = composer.tracking['inspection'].get('annotationWindowStartInclusive', 26)
    window_end = composer.tracking['inspection']['annotationWindowEndExclusive']
    for pts in (window_start-.000001, window_end, window_end+.000001):
        assert composer.compose(image, source_id=source_id, local_pts=pts).evidence['annotations'] == []
    assert composer.annotations_for('tf2-black-knight-2138-2226', 26, 'anything')[0] == []
    assert composer.annotations_for(source_id, 26.016667, 'anything')[0] == []
    assert composer.annotations_for(source_id, 26, 'wrong-pixels')[0] == []
    lines = ('이 수레 옆에서 싸우는', '사람들을 보세요.')
    result = composer.compose(image, source_id=source_id, local_pts=26,
        caption_lines=lines, cat_pose='puzzled')
    assert len(result.evidence['annotations']) == 2
    result.evidence.update(helperSHA256=sha(Path(__file__)), trackingHideOutsideWindowCheck=True)
    if args.write_sample:
        output = media/'compositor-samples'/(sha(Path(__file__))[:12]+'-'+composer.tracking_sha[:12])
        output.mkdir(parents=True, exist_ok=True)
        paths = [output/'opening26.1080x1920.png', output/'opening26.375px.png']
        composer.style_module.save_once(paths[0], composer.style_module.png_bytes(result.image))
        composer.style_module.save_once(paths[1], composer.style_module.png_bytes(result.image.resize((375,667),Image.Resampling.LANCZOS)))
        result.evidence['outputFiles'] = [dict(path=p.as_posix(),sha256=sha(p)) for p in paths]
        composer.style_module.save_once(output/'opening26.receipt.json',
            (json.dumps(result.evidence,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
    print(json.dumps(result.evidence,ensure_ascii=False,indent=2))


if __name__ == '__main__':
    main()
