"""Extract current encoded cut boundaries for direct visual review; no approval is inferred."""
from pathlib import Path
import hashlib, json, subprocess
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
WORK = ROOT / 'projects/hierarchical-game-outlines/production/final-v1'
OUT = WORK / 'encoded-boundary-review-v1'
FF = 'C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
media = read(WORK / 'actual-media-review.json')
assert not OUT.exists(), 'Review existing frames rather than overwrite them.'
OUT.mkdir()
font = ImageFont.truetype('C:/Windows/Fonts/malgun.ttf', 18)
rows = []
for cut in media['cuts']:
    f = ROOT / cut['file']
    assert sha(f) == cut['sha256']
    tag = f.stem
    frames = [0, cut['frames'] // 2, cut['frames'] - 1]
    pattern = OUT / f'{tag}-%02d.png'
    command = [FF, '-v', 'error', '-threads', '2', '-i', str(f), '-vf',
               'select=' + '+'.join(f'eq(n\\,{n})' for n in frames),
               '-vsync', '0', '-frames:v', '3', str(pattern)]
    result = subprocess.run(command, capture_output=True)
    assert result.returncode == 0 and not result.stderr, (tag, result.stderr)
    for i, n in enumerate(frames, 1):
        image = OUT / f'{tag}-{i:02}.png'
        assert image.exists()
        rows.append({'cut': tag, 'frame': n, 'file': image.relative_to(ROOT).as_posix(),
                     'encodedSha256': cut['sha256'], 'imageSha256': sha(image)})
    print(tag, flush=True)
pages = []
for first in range(0, len(rows), 12):
    sheet = Image.new('RGB', (1920, 876), 'white')
    d = ImageDraw.Draw(sheet)
    for j, row in enumerate(rows[first:first + 12]):
        x, y = (j % 4) * 480, (j // 4) * 292
        im = Image.open(ROOT / row['file']).convert('RGB').resize((480, 270))
        sheet.paste(im, (x, y))
        d.text((x + 5, y + 270), f"{row['cut']} encoded frame {row['frame']}", font=font, fill='black')
    p = OUT / f'page-{first // 12 + 1:02}.jpg'
    sheet.save(p, quality=95)
    pages.append(p.relative_to(ROOT).as_posix())
(OUT / 'index.json').write_text(json.dumps({'views': rows, 'pages': pages,
    'wholeDecodePreviouslyPassed': True, 'directPixelReview': 'pending',
    'finalCaptionsApproved': False}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
