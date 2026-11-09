"""Correct the two A02 normal-speed header chips on the relations-v4 clock."""
import hashlib
import json
import os
from pathlib import Path
import subprocess

from PIL import Image, ImageDraw, ImageFont

H = Path(__file__).resolve().parents[1]
R = H.parents[3]
O = H / 'local/visual-corrections/A02'
HEADER = (1600, 44, 320, 62)
COUNTER = (1500, 856, 420, 52)


def read(path):
    return json.loads(path.read_text('utf-8-sig'))


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def rel(path):
    return path.relative_to(R).as_posix()


def sample(source, frame, output):
    subprocess.run([
        'ffmpeg', '-nostdin', '-v', 'error', '-threads', '1', '-i', str(source),
        '-an', '-filter_threads', '1', '-vf', f'select=eq(n\\,{frame})',
        '-frames:v', '1', '-threads', '1', '-y', str(output),
    ], check=True)


def main():
    control = read(R / 'shared/publishing/video-production-control.json')['animationContrastRevision20261108']
    assert 'A02' in control['episodes'] and control['renderAuthorized'] and control['fullLocalProductionAuthorized']
    integration = read(H / 'renderer/integration-caption-safe.json')
    episode = next(episode for episode in integration['episodes'] if episode['id'] == 'A02')
    rows = [row for row in episode['rows'] if row['mode'] == 'native' and row.get('screenSize')]
    assert [(row['relationFrameStart'], row['relationFrameEnd']) for row in rows] == [(8822, 8990), (8990, 9158)]
    inputs = [R / row['output'] for row in rows]
    assert all(row['sha256'] == digest(source) for row, source in zip(rows, inputs))
    O.mkdir(parents=True, exist_ok=True)
    x, y, width, height = HEADER
    before = O / 'header-before.png'
    sample(inputs[0], 103, before)
    count_x, count_y, count_width, count_height = COUNTER
    with Image.open(before) as image:
        background = image.getpixel((x, y))
        counter_background = image.getpixel((count_x, count_y))
    header = Image.new('RGB', (width, height), background)
    font = ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf', 32)
    ImageDraw.Draw(header).text((1620 - x, 58 - y), '1× 관찰', font=font, fill='#f3f5ef', anchor='lt')
    chip = O / 'native-header.png'
    header.save(chip)
    counter_font = ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf', 29)
    counters = []
    for index in (1, 2):
        counter = Image.new('RGB', (count_width, count_height), counter_background)
        ImageDraw.Draw(counter).text(
            (1530 - count_x, 873 - count_y), f'기본 속도 {index}/2',
            font=counter_font, fill='#abb9af', anchor='lt',
        )
        counter_path = O / f'native-counter-{index}.png'
        counter.save(counter_path)
        counters.append(counter_path)
    movie = O / 'A02-correction-008822-009158-native-header.mp4'
    temporary = movie.with_suffix('.partial.mp4')
    frames = sum(row['newFrames'] for row in rows)
    subprocess.run([
        'ffmpeg', '-nostdin', '-v', 'error',
        '-threads', '1', '-i', str(inputs[0]), '-threads', '1', '-i', str(inputs[1]),
        '-threads', '1', '-i', str(chip), '-threads', '1', '-i', str(counters[0]),
        '-threads', '1', '-i', str(counters[1]), '-filter_complex_threads', '1',
        '-filter_complex',
        f'[0:v][3:v]overlay={count_x}:{count_y}:format=yuv420:repeatlast=1[first];'
        f'[1:v][4:v]overlay={count_x}:{count_y}:format=yuv420:repeatlast=1[second];'
        '[first][second]concat=n=2:v=1:a=0,setpts=N/(60*TB)[native];'
        f'[native][2:v]overlay={x}:{y}:format=yuv420:repeatlast=1[v]',
        '-map', '[v]', '-an', '-frames:v', str(frames), '-threads', '1', '-c:v', 'libx264',
        '-preset', 'ultrafast', '-qp', '0', '-bf', '0', '-pix_fmt', 'yuv420p', '-r', '60',
        '-video_track_timescale', '60000', '-color_primaries', 'bt709', '-color_trc', 'bt709',
        '-colorspace', 'bt709', '-movflags', '+faststart', '-y', str(temporary),
    ], check=True)
    streams = json.loads(subprocess.check_output([
        'ffprobe', '-v', 'error', '-show_streams', '-of', 'json', str(temporary),
    ]))['streams']
    assert len(streams) == 1
    assert tuple(streams[0][key] for key in ('width', 'height', 'avg_frame_rate', 'nb_frames')) == (1920, 1080, '60/1', str(frames))
    os.replace(temporary, movie)
    samples = []
    for frame in (103, 271):
        full = O / f'header-after-{frame}.png'
        sample(movie, frame, full)
        original = O / f'header-source-{frame}.png'
        sample(inputs[frame // 168], frame % 168, original)
        with Image.open(full) as after, Image.open(original) as before_image:
            outside = [
                (0, 0, 1920, y), (0, y, x, y + height), (0, y + height, 1920, count_y),
                (0, count_y, count_x, count_y + count_height), (0, count_y + count_height, 1920, 1080),
            ]
            assert all(after.crop(area).tobytes() == before_image.crop(area).tobytes() for area in outside)
            mobile = full.with_name(f'{full.stem}-375.png')
            after.resize((375, 211), Image.Resampling.LANCZOS).save(mobile)
        samples.append({'patchFrame': frame, 'full': rel(full), 'mobile': rel(mobile), 'outsideChipsPixelIdentical': True})
    timing = H / 'baseline-sentence-timing.json'
    result = {
        'schemaVersion': 1, 'episode': 'A02', 'clock': 'relations-v4', 'readyForAssembly': False,
        'sourceCode': rel(Path(__file__)), 'sourceCodeSha256': digest(Path(__file__)),
        'pictureEdits': [{
            'id': movie.stem, 'kind': 'authored-explanation',
            'startFrame': 8822, 'endFrame': 9158, 'newFrames': frames,
            'picture': rel(movie), 'pictureSha256': digest(movie), 'sourceStartFrame': 0, 'sourceVerified': True,
            'expectedUnderlyingExplanationIds': [row['id'] for row in rows],
            'narrationEvidence': {'path': rel(timing), 'sha256': digest(timing), 'sentenceIds': ['029']},
            'visualEvidence': {
                'sourcePlates': [{'path': row['output'], 'sha256': row['sha256'], 'frames': row['newFrames']} for row in rows],
                'sourceRunsUnaltered': True, 'headerBoxXYWH': list(HEADER), 'beforeHeader': '느린 분석',
                'afterHeader': '1× 관찰', 'counterBoxXYWH': list(COUNTER),
                'passCounters': ['기본 속도 1/2', '기본 속도 2/2'],
                'narrationContext': 'Revised S028 sets up the size comparison without specifying a count. Two complete screen-size passes follow before the rotation-only explanation. Old S029 starts at 9157.8f and intersects the final frame. The later amplitude sequence is outside these edits.',
            },
            'reason': 'Mark native speed and the exact count while retaining both 168-frame passes and the exact audio clock.',
            'newAudio': False, 'newTts': False,
        }],
        'patchQa': {'samples': samples, 'modelInspected': False, 'currentIntegratedMasterInspectionPending': True},
        'humanFullWatch': False,
    }
    output = H / 'visual-corrections/A02.json'
    pending = output.with_suffix('.pending')
    pending.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', 'utf-8')
    os.replace(pending, output)


if __name__ == '__main__':
    main()
