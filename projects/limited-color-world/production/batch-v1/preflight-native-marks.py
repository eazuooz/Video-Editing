"""Two lightweight source/layout boards; never a final encoded-pixel approval."""
from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont
import video_pipeline as video
import caption_pipeline as caption

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
LOCAL = PROJECT / 'production/local/batch-v1'
plan = json.loads((HERE / 'edit-plan.json').read_text('utf-8'))
layout = json.loads((LOCAL / 'edit/caption-layout.json').read_text('utf-8'))
cut = next(c for c in plan['cuts'] if c.get('source') == 'wonder-block-cc')
destination = LOCAL / 'edit/preflight-native-marks'
destination.mkdir(exist_ok=True)
caption_font = caption.measured_font(Path(layout['fontFile']), 500)
mark_font = ImageFont.truetype('C:/Windows/Fonts/malgun.ttf', 48)
boards = []
for native_second in (7, 8):
    clock = native_second - cut['sourceStart']
    global_time = cut['startFrame'] / 60 + clock
    source = Image.open(LOCAL / f'sources/wonder-block-inspect/{native_second}.jpg')
    canvas = Image.new('RGB', (1920, 1080), 'black')
    canvas.paste(source.resize((1408, 792), Image.Resampling.LANCZOS), (256, 80))
    draw = ImageDraw.Draw(canvas)
    for mark in cut['marks']:
        if not mark['t0'] <= clock < mark['t1']:
            continue
        geometry = video.interpolate(mark['keyframes'], clock, mark['shape'])
        box = [geometry['x'], geometry['y'], geometry['x'] + geometry['w'], geometry['y'] + geometry['h']]
        color = '#000000' if mark['color'] == '#000000' else '#a4c6a0'
        draw.ellipse(box, outline=color, width=mark['thickness'])
        draw.text(tuple(mark['labelPosition']), mark['label'], font=mark_font,
                  fill='#a4c6a0', stroke_width=3, stroke_fill='black')
    active = next((r for r in layout['rows'] if r['start'] <= global_time < r['end']), None)
    if active:
        x, y, width, height = (active[k] for k in ('x', 'y', 'width', 'height'))
        draw.rectangle([x + 14, y + 14, x + width + 14, y + height + 14], fill='#123C31')
        draw.rectangle([x, y, x + width, y + height], fill='white', outline='#123C31', width=3)
        for i, line in enumerate(active['lines']):
            length = caption_font.getlength(line)
            draw.text((960 - length / 2, y + 8 + i * 60), line, font=caption_font, fill='#123C31')
    canvas.save(destination / f'native-{native_second}-1920.png')
    small = canvas.resize((375, 211), Image.Resampling.LANCZOS)
    small.save(destination / f'native-{native_second}-375.png')
    boards.append(small)
board = Image.new('RGB', (375, 422), 'black')
for i, image in enumerate(boards):
    board.paste(image, (0, i * 211))
board.save(destination / 'mobile-board.png')
print(destination / 'mobile-board.png')
