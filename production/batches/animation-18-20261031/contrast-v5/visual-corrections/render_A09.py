"""Align the pink slime's landing with the A09 S017 narration."""
import json
import os
from pathlib import Path
import subprocess

from PIL import Image, ImageDraw, ImageFont

from render_A07 import H, R, ENCODE, digest, read, rel, run, sample

O = H / 'local/visual-corrections/A09'
SOURCE = 'slime-bounce'
FIRST, LAST = 1340, 1470
NATIVE, STILL = 130, 59
BG, YELLOW, WHITE, TEAL = '#080d0a', '#f2d787', '#f3f5ef', '#81cfc5'
FONT = 'C:/Windows/Fonts/malgunbd.ttf'


def text(draw, xy, value, size, color):
    draw.text(xy, value, font=ImageFont.truetype(FONT, size), fill=color, anchor='lt')


def compare(source, out):
    frames = [(1448, '착지 직전', YELLOW), (1453, '바닥에 닿은 뒤', TEAL)]
    image = Image.new('RGB', (1920, 1080), BG)
    draw = ImageDraw.Draw(image)
    text(draw, (52, 17), 'Slime Rancher 2', 42, YELLOW)
    text(draw, (1510, 24), '정지 분석', 32, YELLOW)
    text(draw, (60, 100), '착지하며 달라지는 높이와 폭', 56, YELLOW)
    for (frame, label, color), x in zip(frames, (63, 987)):
        raw = O / f'slime-source-frame-{frame}.png'
        run('-threads', '1', '-ss', '24', '-i', str(source), '-an', '-filter_threads', '1',
            '-vf', f'select=eq(n\\,{frame - 1440})', '-frames:v', '1', '-threads', '1', '-y', str(raw))
        with Image.open(raw) as shot:
            assert shot.size == (1920, 1080)
            enlarged = shot.crop((387, 337, 755, 613)).resize((760, 570), Image.Resampling.LANCZOS)
            image.paste(enlarged, (x + 54, 226))
            image.paste(shot.resize((240, 135), Image.Resampling.LANCZOS), (x + 565, 245))
        draw.rectangle((x + 564, 244, x + 805, 380), outline=color, width=3)
        text(draw, (x + 54, 164), label, 42, color)
        text(draw, (x + 54, 813), f'관찰 시점 {frame / 60:.2f}초', 32, WHITE)
    image.save(out)
    return [frame / 60 for frame, *_ in frames]


def main():
    control = read(R / 'shared/publishing/video-production-control.json')['animationContrastRevision20261108']
    assert 'A09' in control['episodes'] and control['renderAuthorized'] and control['fullLocalProductionAuthorized']
    assert all(p['episode'] != 'A09' for p in read(H / 'footage/audio-technical-windows.json')['nativePlateProposals'])
    coverage = H / 'footage/game-coverage-team-a.json'
    source = next(row for row in read(coverage)['sources'] if row['key'] == SOURCE)
    assert source['cleanSourceAccepted'] and source['decodedFhd'] and not source['publicationReady']
    assert any(a <= FIRST / 60 < LAST / 60 <= b for a, b in source['actionWindows'])
    video = Path(source['file'])
    assert digest(video) == source['sha256'] and LAST - FIRST == NATIVE

    O.mkdir(parents=True, exist_ok=True)
    chip = O / 'slime-native-header.png'
    image = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 1919, 79), fill=BG)
    text(draw, (52, 17), 'Slime Rancher 2', 42, YELLOW)
    text(draw, (1480, 24), '실제 게임 · 1×', 29, WHITE)
    image.save(chip)
    native = O / 'A09-correction-008493-008623-slime-native.mp4'
    run('-threads', '1', '-ss', '22', '-i', str(video),
        '-threads', '1', '-loop', '1', '-framerate', '60', '-i', str(chip),
        '-filter_complex_threads', '1', '-filter_complex',
        "[0:v]select='between(n,20,149)',setpts=N/(60*TB),scale=1422:800,pad=1920:1080:249:80:0x080d0a,setsar=1[bg];"
        '[bg][1:v]overlay=0:0:shortest=1[v]', '-map', '[v]', '-an', '-frames:v', str(NATIVE),
        *ENCODE, '-y', str(native))
    comparison = O / 'slime-landing-comparison.png'
    frame_times = compare(video, comparison)
    still = O / 'A09-correction-008623-008682-slime-comparison.mp4'
    run('-threads', '1', '-loop', '1', '-framerate', '60', '-i', str(comparison), '-an',
        '-frames:v', str(STILL), *ENCODE, '-y', str(still))
    rows, samples = [], []
    for movie, old_start, count, media_kind, local_in, local_out, times in (
        (native, 8493, NATIVE, 'native-gameplay', FIRST / 60, LAST / 60, None),
        (still, 8623, STILL, 'still-analysis', *frame_times, frame_times),
    ):
        stream, = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_streams', '-of', 'json', str(movie)]))['streams']
        assert tuple(stream[k] for k in ('width', 'height', 'avg_frame_rate', 'nb_frames')) == (1920, 1080, '60/1', str(count))
        game = media_kind == 'native-gameplay'
        rows.append({
            'id': movie.stem, 'kind': 'independent-gameplay' if game else 'authored-explanation',
            'startFrame': old_start, 'endFrame': old_start + count, 'newFrames': count,
            'picture': rel(movie), 'pictureSha256': digest(movie), 'sourceStartFrame': 0, 'sourceVerified': True,
            'expectedUnderlyingExplanationIds': [], 'sourceClassification': 'game' if game else 'analysis',
            'nativeFrames': count if game else 0, 'analysisFrames': count if not game else 0,
            'mediaSegments': [{
                'kind': media_kind, 'offsetFrame': 0, 'frames': count, 'sourceKey': SOURCE,
                'sourceLocalIn': local_in, 'sourceLocalOut': local_out,
                'sourceSha256': source['sha256'], 'sourceFrameTimes': times,
            }],
            'sourceUrl': source['sourceUrl'], 'sourceEvidence': rel(coverage),
            'sourceRightsEvidence': source['sourceRightsEvidence'],
            'reason': 'The native bounce begins on the named game clause and hands off to the actual before/after landing frames.',
            'newAudio': False, 'newTts': False,
        })
        full = O / f'{movie.stem}-encoded.png'
        sample(movie, count // 2, full)
        mobile = full.with_name(f'{full.stem}-375.png')
        with Image.open(full) as frame:
            frame.resize((375, 211), Image.Resampling.LANCZOS).save(mobile)
        samples.append({'file': rel(full), 'mobile': rel(mobile)})
    manifest = {
        'schemaVersion': 1, 'episode': 'A09', 'clock': 'relations-v4', 'readyForAssembly': False,
        'sourceCode': rel(Path(__file__)), 'sourceCodeSha256': digest(Path(__file__)),
        'supportCode': rel(Path(__file__).with_name('render_A07.py')),
        'supportCodeSha256': digest(Path(__file__).with_name('render_A07.py')),
        'pictureEdits': rows, 'preservedCueBoundary': {'oldFrame': 8493, 'finalFrame': 8614, 'captionStartsSeconds': 143.559},
        'patchQa': {'samples': samples, 'modelInspected': False, 'currentIntegratedMasterInspectionPending': True},
        'humanFullWatch': False, 'publicationRightsApproved': False,
    }
    output = H / 'visual-corrections/A09.json'
    pending = output.with_suffix('.pending')
    pending.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', 'utf-8')
    os.replace(pending, output)


if __name__ == '__main__':
    main()
