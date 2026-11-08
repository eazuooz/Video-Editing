"""Sample the actual encoded master around revised word-aligned visual changes."""
from pathlib import Path
import json, re, subprocess
from PIL import Image, ImageDraw

P = Path(__file__).resolve().parents[1]
L = P / 'production/local'
Q = L / 'qa'
timeline = json.loads((L / 'timeline.json').read_text('utf-8'))
words = json.loads((Q / 'narration.timestamps.json').read_text('utf-8'))['chunks']
master = L / 'final' / f'{P.name}.captioned.mp4'

def word_time(scene_id, phrase):
    scene = next(s for s in timeline['scenes'] if s['id'] == scene_id)
    norm = lambda s: re.sub(r'[^\w]', '', s.lower(), flags=re.UNICODE)
    text, anchors = '', []
    for word in words:
        a, b = word['timestamp']
        if a is None or b is None or b <= scene['start'] or a >= scene['speechEnd']:
            continue
        part = norm(word['text'])
        text += part
        anchors += [a] * len(part)
    index = text.index(norm(phrase))
    return anchors[index]

spec = []
for sid, phrase, offsets in [
    ('15', '바깥 영역을', [-.5, 1.5, 3.4]),
    ('15', '배경 레이어에서는', [-.4, .5]),
    ('27', '포인트', [-.4, .4]),
    ('27', '픽셀 퍼 유닛', [.5, 2.5]),
    ('27', '피벗', [.4]),
    ('28', '프레임을', [-.6, .1, .6, 1.1, 11.6, 12.1]),
]:
    at = word_time(sid, phrase)
    for offset in offsets:
        spec.append({'scene': sid, 'phrase': phrase, 'wordTime': at, 'offset': offset, 'sampleTime': at + offset})

for i, row in enumerate(spec):
    target = Q / f'cue-{i:02}-{row["scene"]}.jpg'
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-ss', str(row['sampleTime']), '-i', str(master), '-frames:v', '1', str(target)], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
    row['file'] = str(target.relative_to(P)).replace('\\', '/')
    Image.open(target).resize((375, 211)).save(target.with_suffix('.mobile.png'))

for start in range(0, len(spec), 6):
    sheet = Image.new('RGB', (1440, 900), '#151515')
    draw = ImageDraw.Draw(sheet)
    for i, row in enumerate(spec[start:start+6]):
        x, y = (i % 2) * 720, (i // 2) * 300
        sheet.paste(Image.open(P / row['file']).resize((533, 300)), (x, y))
        draw.text((x+540, y+30), f"{start+i:02} / {row['scene']}\n{row['sampleTime']:.3f}s\noffset {row['offset']:+.1f}", fill='white')
    sheet.save(Q / f'cue-contact-{start//6}.jpg')
(P / 'production/encoded-cue-samples.json').write_text(json.dumps({'master': str(master.relative_to(P)).replace('\\', '/'), 'samples': spec}, ensure_ascii=False, indent=2)+'\n', 'utf-8')
print(f'Saved {len(spec)} encoded cue samples')
