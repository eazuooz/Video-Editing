"""Replace the unrelated head/eye footer in A18's existing wrist plates."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import qa_final_episode_frames as qa


EPISODE = 'A18'
OUT = Path('C:/Users/1/Videos/YamyamProduction/animation-contrast-v5-work/visual-corrections/A18')
FOOTER = '같은 손잡이에서 손목 방향과 팔의 움직임 비교'
WRIST_RANGES = {
    'A18-gp-011191-011351-own': (11191, 11303),
    'A18-wrist-pass-1': (11850, 11970),
    'A18-wrist-pass-2': (11970, 12090),
    'A18-wrist-pass-3': (12090, 12210),
    'A18-cut-026': (12210, 12383),
    'A18-cut-029': (12919, 13386),
    'A18-gp-013808-014105-own': (13808, 14016),
    'A18-cut-032': (14105, 14463),
}


def episode(path):
    return next(row for row in qa.read(path)['episodes'] if row['id'] == EPISODE)


def verify_video(path, frames):
    probe = json.loads(subprocess.check_output([
        'ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
        'stream=width,height,avg_frame_rate,nb_frames', '-of', 'json', str(path),
    ]))['streams'][0]
    assert (probe['width'], probe['height'], probe['avg_frame_rate'], int(probe['nb_frames'])) == (1920, 1080, '60/1', frames)


def render_patch(row, start, end):
    source = qa.path(row['source'])
    source_start = row['sourceStartFrame'] + start - row['oldStartFrame']
    frames = end - start
    edit_id = f'A18-wrist-footer-{start:06d}-{end:06d}'
    picture = OUT / f'{edit_id}.mp4'
    pending = picture.with_stem(picture.stem + '.pending')
    seek = max(0, source_start // 60 - 2)
    offset = source_start - seek * 60
    vf = (
        f'trim=start_frame={offset},setpts=PTS-STARTPTS,'
        'drawbox=x=70:y=812:w=960:h=64:color=0x080c0a:t=fill,'
        "drawtext=fontfile='C\\:/Windows/Fonts/malgunbd.ttf':"
        f"text='{FOOTER}':x=80:y=825:fontsize=40:fontcolor=0xf3f5ef"
    )
    subprocess.run([
        'ffmpeg', '-nostdin', '-v', 'error', '-y', '-threads', '1', '-ss', str(seek),
        '-i', str(source), '-an', '-filter_threads', '1', '-vf', vf,
        '-frames:v', str(frames), '-c:v', 'libx264', '-preset', 'veryfast',
        '-crf', '18', '-threads', '1', '-bf', '0', '-pix_fmt', 'yuv420p',
        '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709',
        '-movflags', '+faststart', str(pending),
    ], check=True)
    verify_video(pending, frames)
    pending.replace(picture)
    return {
        'id': edit_id, 'kind': 'authored-explanation', 'sourceClassification': 'own',
        'startFrame': start, 'endFrame': end, 'newFrames': frames, 'picture': picture.as_posix(),
        'pictureSha256': qa.sha(picture), 'sourceStartFrame': 0, 'sourceVerified': True,
        'original': {'id': row['id'], 'file': source.as_posix(), 'sha256': qa.sha(source), 'sourceStartFrame': source_start},
        'reason': 'Use a wrist-specific observation prompt in the existing wrist shot.',
        'captionSafeBottomY': 876, 'newAudio': False, 'newTts': False,
    }


def join_observation_beat(patches):
    # Keep the silent observation passes and the immediate narrated analysis
    # together, including their separate replay counters and exact edit points.
    ids = {'A18-wrist-pass-1', 'A18-wrist-pass-2', 'A18-wrist-pass-3', 'A18-cut-026'}
    beat = [patch for patch in patches if patch['original']['id'] in ids]
    assert len(beat) == len(ids)
    assert all(left['endFrame'] == right['startFrame'] for left, right in zip(beat, beat[1:]))
    for patch in beat:
        assert qa.sha(patch['picture']) == patch['pictureSha256']
    concat = OUT / 'wrist-observation-beat.concat'
    concat.write_text(''.join(f"file '{patch['picture']}'\n" for patch in beat), encoding='utf-8')
    picture = OUT / 'A18-wrist-footer-011850-012383-observation.mp4'
    pending = picture.with_stem(picture.stem + '.pending')
    subprocess.run([
        'ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 'concat', '-safe', '0',
        '-i', str(concat), '-map', '0:v:0', '-an', '-c:v', 'copy', '-movflags', '+faststart', str(pending),
    ], check=True)
    frames = sum(patch['newFrames'] for patch in beat)
    verify_video(pending, frames)
    pending.replace(picture)
    joined = dict(beat[0])
    del joined['original']
    joined.update(
        id=picture.stem, endFrame=beat[-1]['endFrame'], newFrames=frames,
        picture=picture.as_posix(), pictureSha256=qa.sha(picture),
        components=beat, reason='Keep three corrected observation passes and the following narrated analysis in one teaching beat.',
    )
    return sorted([patch for patch in patches if patch not in beat] + [joined], key=lambda patch: patch['startFrame'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--render', action='store_true')
    args = parser.parse_args()
    assert args.render
    control = qa.read(qa.R / 'shared/publishing/video-production-control.json')['animationContrastRevision20261108']
    assert EPISODE in control['episodes'] and control['renderAuthorized'] and control['fullLocalProductionAuthorized']
    builder = qa.module('a18_wrist_extensions', qa.H / 'build_final_extensions.py')
    game = episode(qa.H / 'game-plates-caption-safe.json')
    integration = episode(builder.assembly.INTEGRATION)
    baseline = next(row for row in qa.read(qa.H / 'baseline-review-manifest.json')['records'] if row['id'] == EPISODE)
    expected = {row['id']: row['sha256'] for row in integration['rows'] if row['key'] == 'wrist'}
    expected.update({row['id']: row['pictureSha256'] for row in game['pictureEdits'] if row['id'] in WRIST_RANGES})
    rows = {row['id']: row for row in builder.visual_timeline(game, integration, baseline) if row['id'] in WRIST_RANGES}
    assert set(rows) == set(expected) == set(WRIST_RANGES)
    OUT.mkdir(parents=True, exist_ok=True)
    patches = []
    for edit_id, (start, end) in WRIST_RANGES.items():
        row = rows[edit_id]
        assert row['oldStartFrame'] == start and end <= row['oldEndFrame']
        assert qa.sha(row['source']) == expected[edit_id]
        patches.append(render_patch(row, start, end))
    manifest = {
        'schemaVersion': 1, 'episode': EPISODE, 'clock': 'relations-v4', 'readyForAssembly': False,
        'pictureEdits': join_observation_beat(patches), 'sourceCode': Path(__file__).resolve().relative_to(qa.R).as_posix(),
        'sourceCodeSha256': qa.sha(__file__), 'revisedFooter': FOOTER, 'preservesStageFrames': True,
        'preservesSourceFrameOrder': True, 'preservesAudioAndTiming': True,
        'humanFullWatch': False, 'modelVisualReview': 'Pending corrected encoded source-frame previews.',
    }
    qa.save(qa.H / 'visual-corrections/A18.json', manifest)
    print(json.dumps({'episode': EPISODE, 'sourcePatches': len(patches), 'affectedFrames': sum(row['newFrames'] for row in patches)}))


if __name__ == '__main__':
    main()
