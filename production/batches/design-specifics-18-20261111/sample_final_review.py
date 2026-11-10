"""Collect proof from the encoded review; visual approval is recorded separately."""

import argparse
import re
import subprocess

from PIL import Image, ImageDraw

from assemble_planned import HERE, FPS, common


def collect(episode, extra_times):
    control = common.load(common.ROOT / 'shared/publishing/video-production-control.json')
    assert episode in control['designSpecifics18Selected20261111']['episodes']
    local = HERE / 'local' / episode
    output = common.OUTPUT.parent / episode
    qa = common.MEDIA / f'{episode}-assembly' / 'qa'
    qa.mkdir(parents=True, exist_ok=True)
    delivery = common.load(output / 'delivery.json')
    assert delivery['stage'] == 'encoded-sample-review-pending'
    plan = common.load(local / 'render-plan.json')
    alignment = common.load(local / 'captions/caption-alignment.json')['paragraphs']
    files = {part['path'].split('.')[-2]: part['path'] for part in delivery['files']}
    total = (delivery['bodyFrames'] + 720) / FPS
    hashes = [subprocess.check_output(['ffmpeg', '-nostdin', '-v', 'error', '-i', files[kind], '-map', '0:a:0',
                                      '-c', 'copy', '-f', 'hash', '-hash', 'sha256', '-'], text=True).strip()
              for kind in ('clean', 'captioned')]
    assert len(set(hashes)) == 1
    levels = subprocess.run(['ffmpeg', '-hide_banner', '-nostdin', '-i', files['captioned'], '-vn', '-af',
                             'volumedetect', '-f', 'null', 'NUL'], check=True, capture_output=True, text=True)
    volume = dict(re.findall(r'(mean|max)_volume: (-?[\d.]+) dB', levels.stderr))
    assert -2.5 < float(volume['max']) < 0

    marks, at = [], 0
    for row in plan['segments']:
        seconds = row['frames'] / FPS
        marks.append((at + seconds / 2, f"{row['scene']} {row.get('source', row['kind'])}"))
        at += seconds
    marks.extend((t, 'cue') for t in extra_times if 0 <= t < total)
    marks.sort()
    columns, width, height = 4, 375, 211
    board = Image.new('RGB', (width * columns, (height + 24) * ((len(marks) + columns - 1) // columns)), '#202020')
    draw = ImageDraw.Draw(board)
    for index, (seconds, title) in enumerate(marks):
        full = qa / f'encoded-{index:02d}.png'
        common.ff('-ss', f'{seconds:.6f}', '-i', files['captioned'], '-frames:v', 1, '-threads', 1, full)
        with Image.open(full) as decoded:
            assert decoded.size == (1920, 1080), full
            mobile = decoded.resize((width, height), Image.Resampling.LANCZOS)
        x, y = index % columns * width, index // columns * (height + 24)
        board.paste(mobile, (x, y))
        draw.text((x + 6, y + height + 3), f'{seconds:.2f}s {title}', fill='white')
    grid = qa / 'final-mobile-375.jpg'
    board.save(grid, quality=91)
    proof = {'stage': 'sample-evidence-visual-check-pending', 'captionPairs': sum(len(x['cues']) for x in alignment),
             'asrCharacterCoverage': {x['scene']: x['matchingCharacterCoverage'] for x in alignment},
             'aacPayloadSha256': hashes[0].split('=')[1], 'meanDbfs': float(volume['mean']),
             'peakDbfs': float(volume['max']), 'durationSeconds': total, 'finalFrameGrid': str(grid),
             'sampleTimes': [time for time, _ in marks], 'humanFullListening': False}
    common.save(qa / 'sample-proof.json', proof)
    print(grid)
    print(proof)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('episode')
    parser.add_argument('--time', type=float, action='append', default=[])
    args = parser.parse_args()
    collect(args.episode, args.time)
