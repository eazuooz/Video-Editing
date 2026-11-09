"""Show Luigi's visible corridor escape on the existing A07 narration clock."""
import hashlib
import json
import os
from pathlib import Path
import subprocess

from PIL import Image, ImageDraw, ImageFont

H = Path(__file__).resolve().parents[1]
R = H.parents[3]
O = H / 'local/visual-corrections/A07'
SOURCE = 'luigi-run'
IN_FRAME = 1036
NATIVE_FRAMES = 75
STILL_FRAMES = 44
VIEW = (249, 80, 1422, 800)
TRACK = [
    (0, (468, 750, 703, 1049)),
    (15, (299, 649, 571, 964)),
    (30, (369, 677, 609, 1004)),
    (45, (434, 656, 603, 981)),
    (60, (424, 685, 691, 996)),
    (74, (393, 693, 635, 1002)),
]
ENCODE = [
    '-threads', '1', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18',
    '-bf', '0', '-g', '120', '-sc_threshold', '0', '-pix_fmt', 'yuv420p', '-r', '60',
    '-video_track_timescale', '60000', '-color_primaries', 'bt709', '-color_trc', 'bt709',
    '-colorspace', 'bt709',
]


def read(path):
    return json.loads(path.read_text('utf-8-sig'))


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def rel(path):
    return path.relative_to(R).as_posix()


def run(*args):
    subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', *args], check=True)


def timestamp(frame):
    centiseconds = round(frame * 100 / 60)
    return f'0:00:{centiseconds // 100:02}.{centiseconds % 100:02}'


def caption_chip(path, still=False):
    image = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 1919, 79), fill='#080d0a')
    family = 'C:/Windows/Fonts/malgunbd.ttf'
    draw.text((52, 17), "Luigi's Mansion 3", font=ImageFont.truetype(family, 42), fill='#f2d787', anchor='lt')
    draw.text(
        (1510 if still else 1480, 24), '정지 분석' if still else '실제 게임 · 1×',
        font=ImageFont.truetype(family, 32 if still else 29),
        fill='#f2d787' if still else '#f3f5ef', anchor='lt',
    )
    image.save(path)


def track_file(path):
    lines = [
        '[Script Info]', 'ScriptType: v4.00+', 'PlayResX: 1920', 'PlayResY: 1080', 'ScaledBorderAndShadow: yes',
        '[V4+ Styles]',
        'Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding',
        'Style: Focus,Malgun Gothic,33,&H00C5CF81,&H00C5CF81,&H000A0D08,&H00000000,-1,0,0,0,100,100,0,0,1,2,0,7,0,0,0,1',
        '[Events]', 'Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text',
    ]
    x0, y0, width, height = VIEW
    for frame in range(NATIVE_FRAMES):
        left, right = next((left, right) for left, right in zip(TRACK, TRACK[1:]) if left[0] <= frame <= right[0])
        weight = (frame - left[0]) / (right[0] - left[0])
        box = [a + weight * (b - a) for a, b in zip(left[1], right[1])]
        x, y, x2, y2 = [round(v) for v in (
            x0 + box[0] * width / 1920, y0 + box[1] * height / 1080,
            x0 + box[2] * width / 1920, y0 + box[3] * height / 1080,
        )]
        drawing = f'm {x} {y} l {x2} {y} {x2} {y2} {x} {y2} {x} {y}'
        start, end = timestamp(frame), timestamp(frame + 1)
        for layer, border, color in ((0, 8, '0A0D08'), (1, 5, 'C5CF81')):
            style = f'{{\\an7\\pos(0,0)\\p1\\bord{border}\\1a&HFF&\\3c&H{color}&\\shad0}}'
            lines.append(f'Dialogue: {layer},{start},{end},Focus,,0,0,0,,{style}{drawing}')
        lines.append(f'Dialogue: 2,{start},{end},Focus,,0,0,0,,{{\\an7\\pos({x},{y-39})}}루이지')
    path.write_text('\n'.join(lines) + '\n', 'utf-8')


def sample(source, frame, out):
    run(
        '-threads', '1', '-i', str(source), '-an', '-filter_threads', '1', '-vf', f'select=eq(n\\,{frame})',
        '-frames:v', '1', '-threads', '1', '-y', str(out),
    )


def main():
    control = read(R / 'shared/publishing/video-production-control.json')['animationContrastRevision20261108']
    assert 'A07' in control['episodes'] and control['renderAuthorized'] and control['fullLocalProductionAuthorized']
    coverage = H / 'footage/game-coverage-team-a.json'
    source = next(row for row in read(coverage)['sources'] if row['key'] == SOURCE)
    assert source['cleanSourceAccepted'] and source['decodedFhd'] and not source['publicationReady']
    start, end = IN_FRAME / 60, (IN_FRAME + NATIVE_FRAMES) / 60
    last = (IN_FRAME + NATIVE_FRAMES - 1) / 60
    assert any(a <= start < end <= b for a, b in source['actionWindows'])
    video = Path(source['file'])
    assert digest(video) == source['sha256']
    audio_adoption = read(H / 'footage/audio-technical-windows.json')
    assert all(proposal['episode'] != 'A07' for proposal in audio_adoption['nativePlateProposals'])

    O.mkdir(parents=True, exist_ok=True)
    native_chip, still_chip, track = (O / name for name in ('native.png', 'still.png', 'luigi-target.ass'))
    caption_chip(native_chip)
    caption_chip(still_chip, still=True)
    track_file(track)
    native = O / 'A07-correction-013484-013559-corridor-native.mp4'
    still = O / 'A07-correction-013559-013603-corridor-still.mp4'
    track_arg = rel(track)
    run(
        '-threads', '1', '-ss', '17', '-i', str(video), '-threads', '1', '-loop', '1', '-framerate', '60',
        '-i', str(native_chip), '-filter_complex_threads', '1',
        '-filter_complex',
        "[0:v]select='between(n,16,90)',setpts=N/(60*TB),scale=1422:800,pad=1920:1080:249:80:0x080d0a,setsar=1[bg];"
        f"[bg][1:v]overlay=0:0:shortest=1,ass='{track_arg}'[v]",
        '-map', '[v]', '-an', '-frames:v', str(NATIVE_FRAMES), *ENCODE, '-y', str(native),
    )
    last_native = O / 'luigi-native-74.png'
    sample(native, NATIVE_FRAMES - 1, last_native)
    run(
        '-threads', '1', '-loop', '1', '-framerate', '60', '-i', str(last_native),
        '-threads', '1', '-loop', '1', '-framerate', '60', '-i', str(still_chip),
        '-filter_complex_threads', '1', '-filter_complex', '[0:v][1:v]overlay=0:0:shortest=1[v]',
        '-map', '[v]', '-an', '-frames:v', str(STILL_FRAMES), *ENCODE, '-y', str(still),
    )
    rows = []
    for movie, old_start, count, kind, role in (
        (native, 13484, NATIVE_FRAMES, 'independent-gameplay', 'native-gameplay'),
        (still, 13559, STILL_FRAMES, 'authored-explanation', 'still-analysis'),
    ):
        stream, = json.loads(subprocess.check_output([
            'ffprobe', '-v', 'error', '-show_streams', '-of', 'json', str(movie),
        ]))['streams']
        assert tuple(stream[key] for key in ('width', 'height', 'avg_frame_rate', 'nb_frames')) == (1920, 1080, '60/1', str(count))
        rows.append({
            'id': movie.stem, 'kind': kind, 'startFrame': old_start, 'endFrame': old_start + count,
            'newFrames': count, 'picture': rel(movie), 'pictureSha256': digest(movie),
            'sourceStartFrame': 0, 'sourceVerified': True, 'expectedUnderlyingExplanationIds': [],
            'sourceClassification': 'game' if role == 'native-gameplay' else 'analysis',
            'nativeFrames': count if role == 'native-gameplay' else 0,
            'analysisFrames': count if role == 'still-analysis' else 0,
            'mediaSegments': [{
                'kind': role, 'offsetFrame': 0, 'frames': count, 'sourceKey': SOURCE,
                'sourceLocalIn': start if role == 'native-gameplay' else last,
                'sourceLocalOut': end if role == 'native-gameplay' else last,
                'sourceSha256': source['sha256'], 'sourceFrameTimes': None if role == 'native-gameplay' else [last],
            }],
            'sourceEvidence': rel(coverage), 'sourceUrl': source['sourceUrl'], 'sourceRightsEvidence': source['sourceRightsEvidence'],
            'reason': 'The close facial view precedes full-body corridor running; the labelled hold retains the last visible running pose.',
            'newAudio': False, 'newTts': False,
        })
    samples = []
    for movie, frame in [(native, 0), (native, 15), (native, 45), (native, 74), (still, 20)]:
        full = O / f'{movie.stem}-{frame}.png'
        sample(movie, frame, full)
        small = full.with_name(f'{full.stem}-375.png')
        with Image.open(full) as image:
            image.resize((375, 211), Image.Resampling.LANCZOS).save(small)
        samples.append({'plate': movie.stem, 'frame': frame, 'full': rel(full), 'mobile': rel(small)})
    result = {
        'schemaVersion': 1, 'episode': 'A07', 'clock': 'relations-v4', 'readyForAssembly': False,
        'sourceCode': rel(Path(__file__)), 'sourceCodeSha256': digest(Path(__file__)), 'pictureEdits': rows,
        'editorialTrack': {'file': rel(track), 'sha256': digest(track), 'keyframesSourcePixels': TRACK, 'bboxIsEditorial': True},
        'patchQa': {'samples': samples, 'modelInspected': False, 'currentIntegratedMasterInspectionPending': True},
        'humanFullWatch': False, 'publicationRightsApproved': False,
    }
    output = H / 'visual-corrections/A07.json'
    pending = output.with_suffix('.pending')
    pending.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', 'utf-8')
    os.replace(pending, output)


if __name__ == '__main__':
    main()
