"""11.05 callable CPU frame compositor; importing/default CLI renders nothing.

Uses the first-film approved caption/font/cat methods read-only. A guarded future
film router supplies actual frames/timed clauses; this helper starts no decoder,
encoder, renderer process, model or resource worker and saves no media itself.
"""
from __future__ import annotations
import copy, hashlib, importlib.util, json, math, sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DATA = HERE / 'solution-path-composition-data-v1.py'
FIRST = ROOT / 'projects/shorts-leveldesign-03-02'
STYLE_SHA = '0c97916ddb76c84155325c253bedf703b5a51b603b33c2f6027dde498ef559ad'
LAYOUT_SHA = '145022f82d9ed7d369170a9145b87fa0592dd900181309eeedad2accf63911ad'
SIZE = (1080, 1920)
COLORS = dict(text='#f5f5f5', muted='#b8b8b8', term='#73c7c2', result='#a4c6a0', problem='#ef8585', title='#e8cf83')


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


data = module('solution_frame_data_v1', DATA)


def prepared_style():
    from PIL import Image
    helper, layout = FIRST / 'production/composite-native-frame.py', FIRST / 'visual-layout-v1.json'
    data.need(data.sha(helper) == STYLE_SHA and data.sha(layout) == LAYOUT_SHA, 'Approved style source changed')
    library = module('solution_approved_style_v1', helper)
    style = library.NativeFrameComposer.__new__(library.NativeFrameComposer)
    style.spec = copy.deepcopy(data.read(layout))
    style.spec['caption']['nativeCenter'] = [488, 1600]
    style.tokens = style.spec['tokens']['scene']
    style.caption_tokens = style.spec['tokens']['caption']
    style.font_cache, style.cat_images = {}, {}
    for row in style.spec['fontMeasurement']['fontFiles']:
        data.checked(row)
    for row in style.spec['cat']['poses']:
        path = ROOT / row['path']
        data.need(data.sha(path) == row['sha256'], 'Approved cat asset changed')
        with Image.open(path) as image:
            style.cat_images[row['pose']] = image.convert('RGBA')
    return style


def caption_emphasis(cue):
    spans = cue.get('emphasis', []) if cue else []
    if not spans:
        return None
    row = spans[0]
    return row['line'], row['start'], row['end'], row['role']


def source_kind_label(layout, mode, camera, index):
    if layout.startswith('ab-'):
        names = {'construction': '생성 과정', 'branches-a': '주변 연결', 'branches-b': '주변 연결',
                 'templates-a': '방 내부', 'templates-b': '방 내부', 'threats-a': '적 위치',
                 'threats-b': '적 위치', 'broken-link': '의도한 입력 경로'}
        return ('A · ' if index == 0 else 'B · ') + names[mode] + ' · 자체 구현'
    if mode == 'broken-link' and camera == 'observer':
        return '의도한 입력 경로 · 닫힌 통로 · 자체 구현'
    return '플레이어 시점 · 자체 구현' if camera == 'player' else '연결 구조 · 자체 구현'


def command_contract(command):
    data.need(command.get('kind') == 'point-label' and command.get('role') in ('term', 'result', 'problem'), 'Supported semantic point label required')
    data.need(isinstance(command.get('label'), str) and bool(command['label'].strip()), 'Nonempty object label required')
    for name in ('point', 'labelCenter'):
        data.need(len(command[name]) == 2 and all(type(v) in (int, float) and math.isfinite(v) for v in command[name]), 'Finite source-attached point/label required')
    data.need(48 <= command['point'][0] < data.RAIL and 350 <= command['point'][1] < data.CAPTION_TOP, 'Target outside protected picture area')


class FrameComposer:
    def __init__(self):
        self.style = None  # Do not decode brand assets or load fonts at import/default.

    def compose(self, packet, decoded_images, *, headline, caption=None, hold_reason=None):
        from PIL import Image, ImageDraw
        data.packet_contract(packet)
        data.need(getattr(decoded_images, 'packetFingerprint', None) == packet['fingerprint']
                  and getattr(decoded_images, 'sourcePins', None) == {v['key']: v['sourceImage']['sha256'] for v in packet['panels']},
                  'Decoded sources are not bound to this exact frame/panel packet')
        data.validate_selection(packet['layout'], packet['modes'], packet['nativeFrame'], packet['purpose'], packet['catPose'], packet['term'])
        data.caption_contract(caption)
        data.need(1 <= len(headline) <= 2 and all(isinstance(v, str) and v.strip() for v in headline), 'Fixed one/two-line headline required')
        if self.style is None:
            self.style = prepared_style()
        style = self.style
        canvas = Image.new('RGB', SIZE, '#000000')
        for panel in packet['panels']:
            source = decoded_images[panel['key']]
            data.need(source.mode == 'RGB' and source.size == (1920, 1080), 'Already-decoded actual FHD RGB image required')
            transform = panel['transform']
            crop = transform['crop']
            x, y, w, h = transform['rect']
            scale = transform['scale']
            # Apply the exact same fractional translation/uniform scale used by
            # projected guides. No square-to-16:9 stretch or rounded-origin drift.
            left, top = math.floor(x), math.floor(y)
            right, bottom = math.ceil(x + w), math.ceil(y + h)
            image = source.transform((right - left, bottom - top), Image.Transform.AFFINE,
                                     (1 / scale, 0, crop[0] + (left - x) / scale,
                                      0, 1 / scale, crop[1] + (top - y) / scale),
                                     resample=Image.Resampling.BICUBIC)
            canvas.paste(image, (left, top))
        draw = ImageDraw.Draw(canvas)
        font = lambda size, weight=700: style.font(size, weight, True)
        for index, line in enumerate(headline):
            data.need(font(62).getlength(line) <= 800, 'Headline must fit the fixed rail; do not shrink')
            draw.text((488, (166, 254)[index]), line, font=font(62), fill=COLORS['title'] if index == 0 else COLORS['text'], anchor='mm')
        # Source-kind labels help distinguish HD/Classic/our model; never credits.
        for index, panel in enumerate(packet['panels']):
            label = source_kind_label(packet['layout'], panel['mode'], panel['camera'], index)
            data.need(font(36).getlength(label) <= 800, 'Source-kind label must fit the fixed width')
            draw.text((488, 376 if index == 0 else 958), label, font=font(36), fill=COLORS['muted'], anchor='mm')
        term = packet['term']
        if term:
            data.need(term.get('presentation') in ('definition', 'chip'), 'Explicit definition/chip presentation required')
            if term['presentation'] == 'definition':
                canvas = canvas.point(lambda value: round(value * .28))
                draw = ImageDraw.Draw(canvas)
                rows = data.definition_rows(term)
                for i, line in enumerate(rows):
                    row_font = font(48, 700 if i == 0 else 500)
                    data.need(row_font.getlength(line) <= 800, 'Definition line exceeds fixed content width; author a semantic break, never shrink')
                    draw.text((488, 1060 + i * 82), line, font=row_font, fill=COLORS['title'] if i == 0 else COLORS['text'], anchor='mm')
            else:
                label = term['english'] + ' (' + term['korean'] + ')'
                data.need(font(40).getlength(label) <= 800, 'Term chip too wide')
                draw.text((488, 338), label, font=font(40), fill=COLORS['title'], anchor='mm')
        for command in packet['commands']:
            command_contract(command)
            color = COLORS[command['role']]
            px, py = command['point']
            lx, ly = command['labelCenter']
            label_font = font(46)
            width = label_font.getlength(command['label']) + 24
            data.need(48 <= lx - width / 2 and lx + width / 2 < data.RAIL and 350 <= ly - 34 and ly + 34 < data.CAPTION_TOP, 'Label would enter rail/caption/header')
            draw.line((px, py, lx, ly), fill=color, width=7)
            draw.ellipse((px - 19, py - 19, px + 19, py + 19), outline=color, width=9)
            draw.rectangle((lx - width / 2, ly - 34, lx + width / 2, ly + 34), fill='#000000', outline=color, width=3)
            draw.text((lx, ly), command['label'], font=label_font, fill=color, anchor='mm')
        if packet['catPose'] is not None:
            style._cat(canvas, packet['catPose'])
        if hold_reason:
            data.need(isinstance(hold_reason, str) and bool(hold_reason.strip()), 'Purposeful hold requires its explanation')
            # Same left safe position as the corrected third-film note; no cat overlap.
            draw.text((220, 1497), '설명을 위한 정지 화면', font=font(26), fill=COLORS['muted'], anchor='mm')
        clean = canvas
        captioned = clean.copy()
        if caption:
            style._captions(captioned, tuple(caption['lines']), caption_emphasis(caption))
        return clean, captioned, dict(packetFingerprint=packet['fingerprint'], nativeFrame=packet['nativeFrame'],
                                      actualSpeechTimingVerified=False, actualPixelQaPassed=False, savedMedia=False)


if __name__ == '__main__':
    print(json.dumps(dict(readyForFinalFilm=False, callableFrameComposerPrepared=True,
                          actualSpeechTimingVerified=False, imageDecoded=False, rendered=False, jobLaunched=False)))
