"""CPU-only contact sheets for editorial review; never modifies source media."""
from pathlib import Path
import io, json, subprocess
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[5]
DEST = Path(__file__).resolve().parent
FFMPEG = 'ffmpeg'
sources = [
    ('gm-tutorial', ROOT / 'shared/assets/game-writing/raw/gm-tutorial.mp4', range(15, 1905, 30)),
    ('gameplay-overview', ROOT / 'shared/assets/game-writing/raw/gameplay-overview.mp4', range(3, 207, 9)),
]
inventory = []
for name, source, timestamps in sources:
    frames = []
    for seconds in timestamps:
        data = subprocess.check_output([
            FFMPEG, '-v', 'error', '-threads', '2', '-ss', str(seconds),
            '-i', str(source), '-frames:v', '1', '-vf', 'scale=384:216',
            '-f', 'image2pipe', '-vcodec', 'png', '-threads', '2', '-'])
        frames.append((seconds, Image.open(io.BytesIO(data)).convert('RGB')))
    for offset in range(0, len(frames), 16):
        group = frames[offset:offset+16]
        sheet = Image.new('RGB', (1536, 960), 'white')
        draw = ImageDraw.Draw(sheet)
        for index, (seconds, frame) in enumerate(group):
            x, y = (index % 4) * 384, (index // 4) * 240
            sheet.paste(frame, (x, y))
            draw.text((x+8, y+220), f'{name} {seconds//60:02d}:{seconds%60:02d}', fill='black')
        target = DEST / f'{name}-coarse-{offset//16+1:02d}.jpg'
        sheet.save(target, quality=94)
        inventory.append({'source': source.relative_to(ROOT).as_posix(),
                          'sampleSeconds': [s for s,_ in group],
                          'contactSheet': target.relative_to(ROOT).as_posix()})
        print(target.name, flush=True)
(DEST / 'source-sampling.json').write_text(json.dumps(inventory, indent=2), encoding='utf-8')
