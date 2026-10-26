"""Extract each current caption, cut boundary and authored mark in one decode pass."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from audio_pipeline import require_authorized
from storage_paths import repo_path, relative


def sha(file):
    return hashlib.sha256(file.read_bytes()).hexdigest()


def main():
    require_authorized('current encoded pixels review extraction')
    plan = json.loads((HERE / 'edit-plan.json').read_text('utf-8-sig'))
    local = repo_path(plan['outputDir'])
    master = local / (plan['outputStem'] + '-captioned.mp4')
    caption_file = local / 'captions.json'
    captions = json.loads(caption_file.read_text('utf-8-sig'))['cues']
    qa = local / 'qa/final-v2'
    qa.mkdir(parents=True, exist_ok=True)
    receipt = qa / 'frame-index.json'
    inputs = {'captionedSha256': sha(master), 'planSha256': sha(HERE / 'edit-plan.json'),
              'captionSha256': sha(caption_file)}
    if receipt.exists():
        previous = json.loads(receipt.read_text('utf-8-sig'))
        if previous['inputs'] != inputs:
            raise ValueError('Preserve existing pixel evidence for different inputs; choose a new QA version')
        print('Unchanged complete frame evidence reused')
        return
    points = {}
    groups = {'captions': [], 'boundaries': [], 'marks': [], 'ends': []}

    def add(t, group, label, data=None):
        frame = max(0, min(plan['totalFrames'] - 1, round(t * 60)))
        record = {'group': group, 'label': label, 'frame': frame, 'time': frame / 60, **(data or {})}
        groups[group].append(record)
        points.setdefault(frame, []).append(record)

    for cue in captions:
        add((cue['start'] + cue['end']) / 2, 'captions', f"Cue{cue['cue']:03d}",
            {'cue': cue['cue'], 'ko': cue['ko'], 'en': cue['en'], 'scene': cue['scene']})
    for cut in plan['cuts']:
        add((cut['startFrame'] + min(8, cut['frames'] // 3)) / 60, 'boundaries', cut['id'] + ' beginning', {'cut': cut['id']})
        add((cut['endFrame'] - min(8, cut['frames'] // 3)) / 60, 'boundaries', cut['id'] + ' ending', {'cut': cut['id']})
        for mark in cut.get('marks', []):
            for tag, t in [('early', mark['t0'] + .15), ('middle', (mark['t0'] + mark['t1']) / 2), ('late', mark['t1'] - .10)]:
                if mark['t0'] <= t < mark['t1']:
                    add(cut['startFrame'] / 60 + t, 'marks', mark['id'] + ' ' + tag, {'cut': cut['id'], 'mark': mark['id']})
    for t in [.5, 1.5, plan['totalFrames'] / 60 - 9, plan['totalFrames'] / 60 - 5, plan['totalFrames'] / 60 - .5]:
        add(t, 'ends', f'Brand/member {t:.2f}')
    ordered = sorted(points)
    frames = qa / 'frames'
    frames.mkdir(exist_ok=True)
    def balanced_sum(terms):
        if len(terms) == 1:
            return terms[0]
        middle = len(terms) // 2
        return '(' + balanced_sum(terms[:middle]) + '+' + balanced_sum(terms[middle:]) + ')'

    # FFmpeg's expression parser has a bounded recursion depth. A balanced tree
    # preserves the exact requested frames without a215-term left-deep sum.
    expression = balanced_sum([f'eq(n,{n})' for n in ordered])
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-threads', '2',
                    '-i', str(master), '-vf', "select='" + expression + "'", '-fps_mode', 'vfr',
                    '-frames:v', str(len(ordered)), '-compression_level', '1', '-threads', '2',
                    '-n', str(frames / '%04d.png')], check=True)
    mapping = {n: frames / f'{i+1:04d}.png' for i, n in enumerate(ordered)}
    assert len(list(frames.glob('*.png'))) == len(ordered)
    for group, records in groups.items():
        for width in [640, 375]:
            height = round(width * 9 / 16)
            for page in range((len(records) + 7) // 8):
                batch = records[page*8:(page+1)*8]
                board = Image.new('RGB', (width * 2, (height + 26) * 4), '#151515')
                draw = ImageDraw.Draw(board)
                for j, row in enumerate(batch):
                    x, y = (j % 2) * width, (j // 2) * (height + 26)
                    image = Image.open(mapping[row['frame']]).convert('RGB').resize((width, height), Image.Resampling.LANCZOS)
                    board.paste(image, (x, y))
                    draw.text((x + 5, y + height + 5), f"{row['label']} | {row['time']:.3f}s", fill='white')
                board.save(qa / f'{group}-{width}-{page+1:02d}.jpg', quality=93)
    output = {'inputs': inputs, 'status': 'extracted-awaiting-direct-pixel-review',
              'master': relative(master), 'nativeWidth': 1920, 'nativeHeight': 1080, 'mobileBoardWidthPerFrame': 375,
              'groups': groups, 'frames': [{'frame': n, 'time': n / 60, 'file': relative(mapping[n]), 'sha256': sha(mapping[n])} for n in ordered],
              'wholeListening': False}
    receipt.write_bytes((json.dumps(output, ensure_ascii=False, indent=2) + '\n').encode())
    print(json.dumps({'uniqueFrames': len(ordered), 'captions': len(captions), 'groups': {key: len(rows) for key, rows in groups.items()}, 'directory': relative(qa)}))


if __name__ == '__main__':
    main()
