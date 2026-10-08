"""Sample every narrated explanation beat from the current captioned delivery.

Contact sheet creation is pending review, never an automatic pixel approval.
"""
from pathlib import Path
import sys, json, hashlib, subprocess
from PIL import Image, ImageDraw, ImageFont
from production_control import require_current_authorization

ROOT = Path(__file__).resolve().parents[3]
slug = sys.argv[1]
require_current_authorization(slug, 'final explanation beat inspection')
base = ROOT / 'projects' / slug
manifest = json.loads((base / 'project.json').read_text(encoding='utf-8'))
timeline = json.loads((base / 'production/timeline.json').read_text(encoding='utf-8'))
lesson = json.loads((Path(__file__).parent / 'lessons' / (slug + '.json')).read_text(encoding='utf-8'))
video = ROOT / manifest['paths']['videoBurnedCaptions']
output = ROOT / 'shared/output' / slug / 'qa/final-beats'
output.mkdir(parents=True, exist_ok=True)
font = ImageFont.truetype('C:/Windows/Fonts/malgun.ttf', 20)
records = []
for scene in lesson['scenes']:
    if scene['kind'] != 'explanation':
        continue
    slot = next(s for s in timeline['scenes'] if s['id'] == scene['id'])
    assert len(slot['lineStarts']) == len(scene['beats'])
    times = []
    rows = (len(scene['beats']) + 1) // 2
    sheet = Image.new('RGB', (1920, 570 * rows), '#e9ecee')
    draw = ImageDraw.Draw(sheet)
    for i, (start, beat) in enumerate(zip(slot['lineStarts'], scene['beats'])):
        end = slot['lineStarts'][i+1] if i+1 < len(slot['lineStarts']) else slot['voiceSeconds']
        local = start + min(1.5, max(.08, (end-start)*.6))
        t = min(slot['start'] + local, slot['start'] + slot['seconds'] - .1)
        target = output / f'scene{scene["id"]}-beat{i+1:02}.jpg'
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', str(t), '-i', str(video),
                        '-frames:v', '1', '-q:v', '2', str(target)], check=True)
        x, y = (i % 2)*960, (i // 2)*570
        sheet.paste(Image.open(target).resize((960, 540)), (x, y+30))
        draw.text((x+8, y+3), f'{scene["id"]} / beat{i+1} / {t:.2f}s', font=font, fill='#202020')
        times.append(dict(beat=i+1, time=t, expected=beat))
    path = output / f'scene{scene["id"]}-all-beats.jpg'
    sheet.save(path, quality=95)
    records.append(dict(scene=scene['id'], path=path.relative_to(ROOT).as_posix(),
                        sha256=hashlib.sha256(path.read_bytes()).hexdigest(), samples=times,
                        directPixelReview='pending'))
    print('Generated final beat sheet', scene['id'], flush=True)
proof = dict(video=manifest['paths']['videoBurnedCaptions'],
             videoSha256=hashlib.sha256(video.read_bytes()).hexdigest(), records=records,
             status='generated-pending-direct-review')
(output / 'generated-samples.json').write_text(json.dumps(proof, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
