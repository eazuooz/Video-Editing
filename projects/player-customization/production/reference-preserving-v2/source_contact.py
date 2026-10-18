"""Bounded D21 source-pixel inspection boards; no work runs on import.

    python source_contact.py <source> <safe-name> --start 0 --end 30 --step 6

No download or recognition occurs. Sources stay untouched. Output is confined
to this revision's ignored local inspection directory. Existing boards may be
reused only for the same source bytes, range and sampling settings. Boards are
inspection material, never a whole moving-footage review or FHD source proof.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import argparse
import json
import math
import re
import subprocess

from audio_pipeline import ROOT, LOCAL, artifact, repo_path, require_authorized, sha, tool


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('source')
    parser.add_argument('name')
    parser.add_argument('--step', type=float, default=6)
    parser.add_argument('--start', type=float, default=0)
    parser.add_argument('--end', type=float, required=True)
    args = parser.parse_args()
    require_authorized('source-contact')
    if not re.fullmatch(r'[A-Za-z0-9_-]+', args.name):
        parser.error('name must contain only letters, numbers, underscore or hyphen')
    if not all(math.isfinite(v) for v in (args.start, args.end, args.step)) or not (0 <= args.start < args.end and args.step > 0):
        parser.error('Require finite 0 <= start < end and step > 0')
    sample_count = math.ceil((args.end - args.start) / args.step)
    if sample_count > 240:
        parser.error('Use a bounded interval with at most 240 inspection samples')
    source = repo_path(args.source)
    if not source.is_file():
        raise FileNotFoundError(source)
    output = LOCAL / 'inspection' / args.name
    settings = {'source': artifact(source), 'start': args.start, 'end': args.end,
                'step': args.step, 'previewSize': [640, 360], 'codeSha256': sha(Path(__file__))}
    index = output / 'index.json'
    if index.exists():
        previous = json.loads(index.read_text(encoding='utf-8-sig'))
        if previous.get('inputs') != settings:
            raise ValueError('Preserve the existing inspection set; use a different safe name for changed source/settings')
        if all((ROOT / item['path']).is_file() and sha(ROOT / item['path']) == item['sha256']
               for item in previous.get('outputs', [])) and previous.get('outputs'):
            print('Reusing identical source inspection boards; no extraction repeated')
            return
        raise ValueError('An existing inspection output is missing or changed; recover or use a different safe name')
    if output.exists() and any(output.iterdir()):
        raise FileExistsError('Preserve unregistered inspection images; use another safe name')
    output.mkdir(parents=True, exist_ok=True)
    font = ImageFont.truetype('C:/Windows/Fonts/malgun.ttf', 23)
    rows, outputs = [], []
    for i in range(sample_count):
        t = args.start + i * args.step
        image = output / f'{t:09.3f}.jpg'
        subprocess.run([tool('ffmpeg'), '-nostdin', '-n', '-v', 'error', '-threads', '2',
            '-ss', str(t), '-i', str(source), '-frames:v', '1', '-vf',
            'scale=640:360:force_original_aspect_ratio=decrease,pad=640:360:(ow-iw)/2:(oh-ih)/2',
            '-q:v', '3', str(image)], check=True, cwd=ROOT)
        record = artifact(image)
        outputs.append(record)
        rows.append({'seconds': t, **record})
    for first in range(0, len(rows), 12):
        group = rows[first:first + 12]
        board = Image.new('RGB', (1920, 1600), '#141714')
        draw = ImageDraw.Draw(board)
        for j, row in enumerate(group):
            x, y = (j % 3) * 640, (j // 3) * 400
            with Image.open(ROOT / row['path']) as frame:
                board.paste(frame, (x, y))
            draw.text((x + 14, y + 365), f'{args.name}  {row["seconds"]:.3f}s', font=font, fill='white')
        destination = output / f'board-{first // 12 + 1:02}.jpg'
        board.save(destination, quality=92)
        outputs.append(artifact(destination))
    index.write_text(json.dumps({'inputs': settings, 'samples': rows, 'outputs': outputs,
        'directReview': 'pending', 'continuousMovingReview': 'not performed',
        'researchContactBoardsAreNotProductionSources': True}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Prepared', len(rows), 'source samples;', math.ceil(len(rows) / 12), 'boards for direct review')


if __name__ == '__main__':
    main()
