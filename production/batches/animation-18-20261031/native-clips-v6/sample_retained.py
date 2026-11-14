"""Inspect encoded native-motion examples before allowing retained-body assembly."""
import argparse
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from prepare import HERE, ROOT, WORK, read, save
from finish_episode import sha


def sample(ep):
    audit = read(WORK / ep / 'native-source-audit.json')
    movie = audit['pictures']['captioned.mp4']['path']
    if ep == 'A03':
        rows = read(ROOT / 'projects/animation-breaking-down-attack-animations/production/contrast-v5/edit-plan.json')['rows']
        moments = [r['start'] / 60 + min(1, r['frames'] / 120) for r in rows if r['frames'] >= 120]
    else:
        rows = next(r['intervals'] for r in read(HERE / 'motion-audit.json')['episodes'] if r['id'] == ep)
        moments = []
        for key in dict.fromkeys(r['reference']['key'] for r in rows):
            group = [r for r in rows if r['reference']['key'] == key]
            r = max(group, key=lambda r: r['end'] - r['start'])
            moments.extend([r['start'] / 60 + (r['end'] - r['start']) / 60 * t for t in (.2, .55, .85)])
    if len(moments) > 12:
        moments = moments[:12]
    folder = WORK / ep / 'retained-native-sampling'
    folder.mkdir(parents=True, exist_ok=True)
    font = ImageFont.truetype('C:/Windows/Fonts/malgun.ttf', 20)
    grid = Image.new('RGB', (1500, 264 * ((len(moments) + 2) // 3)), '#080c0a')
    d = ImageDraw.Draw(grid)
    records = []
    for i, at in enumerate(moments):
        path = folder / f'{i:02}.png'
        subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-ss', str(at), '-threads', '2',
                        '-i', movie, '-frames:v', '1', '-vf', 'scale=480:270', str(path)], check=True)
        with Image.open(path) as im:
            grid.paste(im.resize((450, 253)), (i % 3 * 500, i // 3 * 264))
        records.append({'seconds': at, 'image': str(path), 'sha256': sha(path)})
    grid.save(folder / 'contact.jpg')
    save(folder / 'samples.json', {'episode': ep, 'sourceSha256': audit['pictures']['captioned.mp4']['sha256'],
                                 'samples': records, 'visualReviewPending': True})
    print(folder / 'contact.jpg')


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('episodes', nargs='+')
    for ep in p.parse_args().episodes:
        sample(ep)
