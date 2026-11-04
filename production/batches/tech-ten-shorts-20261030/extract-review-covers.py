"""Extract unmodified actual-game frames from verified selected review masters.

These are local thumbnail candidates, not uploaded or applied platform covers.
Each frame keeps the encoded title, native aspect ratio, and original marks.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('ten_review', HERE / 'build-review-overview.py')
REVIEW = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REVIEW)
TIMES = {
    'shorts-alyx-liquid-shader': 4.5,
    'shorts-batman-origins-snow-below-camera': 2.5,
    'shorts-sea-of-thieves-water-masking': 2.5,
    'shorts-uncharted3-fixed-plane-scrolling-desert': 2.5,
    'shorts-uncharted4-taut-rope-fallback': 2.5,
    'shorts-starcraft-worker-mineral-walk': 3.0,
    'shorts-starcraft-diagonal-bridge-square-path-grid': 2.5,
    'shorts-starcraft-eud-compatibility-emulator': 1.5,
    'shorts-starcraft2-marine-random-firing-delay': 2.5,
    'shorts-starcraft2-replay-input-resimulation': 3.0,
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--require-all', action='store_true')
    args = parser.parse_args()
    media, record = REVIEW.collect()
    if args.require_all and record['completeCount'] != 10:
        raise RuntimeError('All ten current review masters are required.')
    ffmpeg = shutil.which('ffmpeg')
    if not ffmpeg:
        raise RuntimeError('ffmpeg is not available.')
    entries = []
    for row in record['projects']:
        if not row['generated']:
            continue
        time = TIMES[row['slug']]
        timing = REVIEW.read(REVIEW.ROOT / 'projects' / row['slug'] / 'production/visual-timing.json')
        section = next(s for s in timing['sections'] if s['startFrame'] <= round(time * 60) < s['endFrame'])
        if section['kind'] != 'game' or not section.get('source'):
            raise RuntimeError(f'{row["slug"]}: cover must use an actual-game section.')
        target = media / 'delivery/covers' / row['slug'] / row['masterSha256'] / f'frame-{round(time * 60):06d}'
        target.mkdir(parents=True, exist_ok=True)
        cover = target / 'actual-game-frame.png'
        receipt = target / 'cover.json'
        if receipt.exists():
            previous = REVIEW.read(receipt)
            if previous['frameSeconds'] != time or previous['sha256'] != REVIEW.sha(cover):
                raise RuntimeError('Existing cover receipt differs; preserve it before revising.')
        else:
            subprocess.run([ffmpeg, '-hide_banner', '-loglevel', 'error', '-threads', '1',
                            '-ss', str(time), '-i', str(Path(row['finalDirectory']) / 'captioned.mp4'),
                            '-frames:v', '1', '-threads', '1', '-n', str(cover)], check=True)
            previous = dict(slug=row['slug'], masterSha256=row['masterSha256'],
                            frameSeconds=time, frameIndex=round(time * 60),
                            sourceSection=section['id'], sourceId=section['source'],
                            sourceSeconds=section['sourceStart'] + time - section['startFrame'] / 60,
                            path=str(cover), sha256=REVIEW.sha(cover),
                            method='Unmodified decoded frame; no crop, retouch, text addition, or watermark removal.',
                            visualReview='pending', platformCoverApplied=False)
            receipt.write_text(json.dumps(previous, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
        entries.append(previous)
    index = dict(batchId=record['batchId'], currentCoverCount=len(entries),
                 platformActionsPerformed=False, covers=entries)
    data = json.dumps(index, ensure_ascii=False, indent=2) + '\n'
    path = media / 'delivery/covers'
    path.mkdir(parents=True, exist_ok=True)
    snapshot = path / ('covers-' + hashlib.sha256(data.encode()).hexdigest()[:12] + '.json')
    snapshot.write_text(data, encoding='utf8')
    (path / 'covers.json').write_text(data, encoding='utf8')
    print(json.dumps(dict(count=len(entries), index=str(path / 'covers.json')), ensure_ascii=False))


if __name__ == '__main__':
    main()
