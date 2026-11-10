"""Index official research-only visuals and burned-in English captions."""

from difflib import SequenceMatcher
from hashlib import file_digest
from pathlib import Path
import json
import subprocess
import sys
import time

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
OCR_DEPS = HERE.parent / 'animation-18-20261031/research/A10/ocr-deps'
sys.path.insert(0, str(OCR_DEPS))
import cv2
from rapidocr_onnxruntime import RapidOCR


def save(path, data):
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temp.replace(path)


def inspect(source, episode, folder, ocr):
    target = folder / episode['id']
    target.mkdir(exist_ok=True)
    with source.open('rb') as stream:
        digest = file_digest(stream, 'sha256').hexdigest()
    receipt = target / 'reference-review-input.json'
    if receipt.exists() and json.loads(receipt.read_text(encoding='utf-8'))['sourceSha256'] == digest:
        return
    decoder = subprocess.Popen(['ffmpeg', '-v', 'error', '-threads', '2', '-i', str(source),
                                '-an', '-vf', 'fps=2,scale=854:480', '-pix_fmt', 'bgr24', '-f',
                                'rawvideo', '-threads', '1', '-'], stdout=subprocess.PIPE)
    width, height = 854, 480
    previous, previous_text, last_stored_text = None, '', ''
    cues, stills = [], []
    tick = 0
    while data := decoder.stdout.read(width * height * 3):
        if len(data) != width * height * 3:
            raise ValueError(f'Truncated reference at {tick / 2:.1f}s: {source}')
        frame = np.frombuffer(data, dtype=np.uint8).reshape(height, width, 3)
        crop = frame[407:478, 4:850]
        same = previous is not None and np.mean(cv2.absdiff(crop, previous)) < .18
        if same:
            text = previous_text
        else:
            found, _ = ocr(cv2.resize(crop, None, fx=1.5, fy=1.5))
            found = sorted(found or [], key=lambda x: (min(p[1] for p in x[0]) // 18, min(p[0] for p in x[0])))
            text = ' '.join(x[1] for x in found)
        if text and SequenceMatcher(None, last_stored_text, text).ratio() < .96:
            cues.append({'seconds': tick / 2, 'text': text})
            last_stored_text = text
        if tick % 14 == 0:
            im = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)).resize((384, 216))
            stills.append((tick / 2, im))
        previous, previous_text = crop, text
        tick += 1
    decoder.stdout.close()
    if decoder.wait() or tick < 2 * (episode['referenceDurationSeconds'] - 2):
        raise ValueError(f'Decode did not cover the full reference: {source}')
    for begin in range(0, len(stills), 24):
        cells = stills[begin:begin + 24]
        sheet = Image.new('RGB', (1536, 240 * ((len(cells) + 3) // 4)), '#161816')
        draw = ImageDraw.Draw(sheet)
        for index, (second, im) in enumerate(cells):
            x, y = 384 * (index % 4), 240 * (index // 4)
            sheet.paste(im, (x, y))
            draw.text((x + 10, y + 220), f'{episode["id"]}  {int(second)//60:02}:{int(second)%60:02}', fill='white')
        sheet.save(target / f'visuals-{begin // 24 + 1:02}.jpg', quality=89)
    (target / 'caption-readback.txt').write_text('\n'.join(f'{r["seconds"]:06.1f} {r["text"]}' for r in cues),
                                                encoding='utf-8')
    save(receipt, {'source': str(source), 'sourceSha256': digest, 'sourceClass': 'research-reference-only',
                   'episode': episode['id'], 'captionCues': len(cues), 'decodedHalfSeconds': tick,
                   'method': 'Full-range local OCR of official burned-in captions with sampled visual contacts',
                   'fullAudioListened': False, 'sourceUsageInProduction': False})
    print(episode['id'], f'{tick / 2:.1f}s / {len(cues)} caption changes', flush=True)


def main():
    batch = json.loads((HERE / 'batch.json').read_text(encoding='utf-8'))
    folder = Path(batch['mediaRoot']) / 'research-reference-only'
    ocr = RapidOCR(intra_op_num_threads=2, inter_op_num_threads=1, use_cls=False,
                   det_limit_type='max', det_limit_side_len=1600)
    cv2.setNumThreads(1)
    requested = set(sys.argv[1:])
    pending = [row for row in batch['episodes'] if not requested or row['id'] in requested]
    deadline = time.monotonic() + 1200
    while pending and time.monotonic() < deadline:
        for row in list(pending):
            source = folder / (row['referenceId'] + '.mp4')
            if not source.is_file() or time.time() - source.stat().st_mtime < 4:
                continue
            inspect(source, row, folder, ocr)
            pending.remove(row)
        if pending:
            time.sleep(8)
    if pending:
        raise FileNotFoundError(', '.join(row['id'] for row in pending))


if __name__ == '__main__':
    main()
