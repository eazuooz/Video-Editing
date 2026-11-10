"""Build the selected local 1080p60 episode after speech and source checks."""

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

from scene_visuals import RENDERERS, ROOT

HERE = Path(__file__).resolve().parent
LOCAL = HERE.parent / 'local/DS01'
MEDIA = Path('C:/Users/1/Videos/YamyamProduction/design-specifics-18-20261111')
OUTPUT = Path('C:/Users/1/Videos/YamyamCoding/design-specifics-18-review/DS01')
VOICE = LOCAL / 'voice/ds01-game-feel.wav'
EFFECT_COMPARISON = ROOT / 'shared/output/motion-canvas/ds01-effect-comparison-review.mp4'
FPS, RATE = 60, 48000
VENC = ['-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-threads', '4', '-bf', '0',
        '-g', '120', '-sc_threshold', '0', '-pix_fmt', 'yuv420p', '-r', '60',
        '-video_track_timescale', '60000', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709']
# Windows and rectangles are observed in the decoded native cut, then projected to the fitted picture.
FOCUS = {'01': (106.26, 106.48, 1185, 485, 188, 209),
         '02': (13.71, 13.94, 170, 552, 425, 264),
         '04': (101.38, 101.64, 1232, 277, 345, 397)}


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def save(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def ff(*args):
    subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-xerror', '-y', *map(str, args)],
                   check=True, creationflags=subprocess.CREATE_NO_WINDOW)


def probe(path):
    return json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_streams', '-of', 'json', str(path)]))


def check_picture(path, frames):
    picture = next(s for s in probe(path)['streams'] if s['codec_type'] == 'video')
    assert (picture['width'], picture['height'], picture['avg_frame_rate'], int(picture['nb_frames'])) == (
        1920, 1080, '60/1', frames), (path, picture)


def row(key, kind, frames, **values):
    assert frames > 0
    return {'scene': key, 'kind': kind, 'frames': frames, **values}


def cut_list(timing, cues):
    entries = timing['entries']
    starts = [round(item['start'] * FPS) for item in entries]
    end = round(timing['duration_seconds'] * FPS)
    durations = dict(zip([item['scene_id'] for item in entries],
                         [b - a for a, b in zip(starts, starts[1:] + [end])], strict=True))
    first = {key: next(cue for cue in cues if cue['scene'] == key) for key in ('01', '06', '08')}
    opening_offset = 106.85 - (first['01']['end'] - 2)
    opening_frames = round((109.82 - opening_offset) * FPS)
    keys = ('02', '04', '05', '09')
    supplemental = round(end * .6) - sum(durations[key] for key in keys) - opening_frames
    context06 = round(first['06']['end'] * FPS) - 120 - starts[5]
    context08 = round(first['08']['end'] * FPS) - 120 - starts[7]
    native06 = min(context06, supplemental)
    native08 = supplemental - native06
    assert 0 < native06 and 0 <= native08 <= context08 + 24, (supplemental, context06, context08)
    placements = {'02': ('sf6', 8), '04': ('fantasy', 111 - durations['04'] / FPS), '05': ('fantasy', 70),
                  '09': ('smash', 346.3 - durations['09'] / FPS)}
    rows = [row('brand', 'brand', 120)]
    for key, frames in durations.items():
        if key == '01':
            rows.append(row(key, 'game', opening_frames, source='smash', offset=opening_offset))
            rows.append(row(key, 'explanation', frames - opening_frames))
        elif key in placements:
            source, offset = placements[key]
            rows.append(row(key, 'game', frames, source=source, offset=offset))
        elif key == '06':
            rows.append(row(key, 'game', native06, source='fantasy', offset=12))
            rows.append(row(key, 'explanation', frames - native06))
        elif key == '08' and native08:
            rows.append(row(key, 'game', native08, source='smash', offset=254.25))
            rows.append(row(key, 'explanation', frames - native08))
        else:
            rows.append(row(key, 'explanation', frames))
    rows.append(row('member', 'member', 600))
    assert sum(part['frames'] for part in rows if part['kind'] == 'game') == round(end * .6)
    assert sum(part['frames'] for part in rows) == end + 720
    return rows, end


def picture(source, frames, offset, destination, kind, suffix=''):
    filter_chain = 'fps=60,setsar=1'
    if kind == 'game':
        filter_chain += ',scale=1920:880:force_original_aspect_ratio=decrease:force_divisible_by=2,pad=1920:1080:(ow-iw)/2:12:color=0x0a110d'
    ff('-threads', 2, '-filter_threads', 2, '-ss', f'{offset:.7f}', '-i', source,
       '-an', '-vf', filter_chain + suffix, '-frames:v', frames, *VENC, destination)
    check_picture(destination, frames)


def gameplay_focus(part):
    focus = FOCUS.get(part['scene'])
    if focus is None:
        return ''
    start, end, x, y, width, height = focus
    scale = 880 / 900
    x, y = round(960 + (x - 960) * scale), round(12 + (y - 12) * scale)
    width, height = round(width * scale), round(height * scale)
    start -= part['offset']
    end -= part['offset']
    enable = f"enable='between(t,{start:.6f},{end:.6f})'"
    return (f',drawbox=x={x}:y={y}:w={width}:h={height}:color=0x101713:t=12:{enable}'
            f',drawbox=x={x + 2}:y={y + 2}:w={width - 4}:h={height - 4}:color=0xf2d786:t=7:{enable}')


def explanation(key, frames, destination):
    if key == '07':
        # This authored diagram uses the same time scale in all four conditions.
        ff('-threads', 2, '-filter_threads', 2, '-i', EFFECT_COMPARISON, '-an', '-vf',
           f'setpts={frames / 480:.12f}*PTS,fps=60,tpad=stop_mode=clone:stop_duration=0.08',
           '-frames:v', frames, *VENC, destination)
    else:
        render = RENDERERS[key]
        proc = subprocess.Popen(['ffmpeg', '-nostdin', '-v', 'error', '-xerror', '-y', '-f', 'rawvideo',
                                 '-pix_fmt', 'rgb24', '-s', '1920x1080', '-r', '60', '-i', '-',
                                 '-an', *VENC, str(destination)], stdin=subprocess.PIPE,
                                creationflags=subprocess.CREATE_NO_WINDOW)
        try:
            for index in range(frames):
                proc.stdin.write(render(index / FPS, frames / FPS).tobytes())
        finally:
            proc.stdin.close()
        assert proc.wait() == 0, key
    check_picture(destination, frames)


def mix_audio(rows, sources, body_frames, parts, destination):
    music = ROOT / 'shared/assets/music/youtube-audio-library/Nimbus-Eveningland.mp3'
    assert music.is_file() and music.with_suffix('.LICENSE.md').is_file()
    games = []
    for index, part in enumerate(rows):
        if part['kind'] in ('brand', 'member'):
            continue
        duration = part['frames'] / FPS
        wav = parts / f'{index:02d}-ambient.wav'
        if part['kind'] == 'game':
            source = sources[part['source']]['file']
            ff('-ss', f'{part["offset"]:.8f}', '-i', source, '-map', '0:a:0', '-af',
               f'loudnorm=I=-30:TP=-4:LRA=10,aresample=48000,apad,atrim=duration={duration:.8f}',
               '-ac', 2, '-c:a', 'pcm_s16le', wav)
        else:
            ff('-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo', '-t', f'{duration:.8f}', '-c:a', 'pcm_s16le', wav)
        games.append(wav)
    listing = parts / 'game-audio.txt'
    listing.write_text(''.join(f"file '{p.as_posix()}'\n" for p in games), encoding='utf-8')
    body = body_frames / FPS
    total = body + 12
    graph = (
        '[0:a]loudnorm=I=-16:TP=-2:LRA=8,aresample=48000,pan=stereo|c0=c0|c1=c0,adelay=2000:all=1,'
        f'apad,atrim=duration={total:.8f},asplit=2[voice][side];'
        f'[1:a]loudnorm=I=-28:TP=-8:LRA=9,aresample=48000,atrim=duration={total:.8f},'
        f'afade=t=in:d=0.6,afade=t=out:st={total-2:.8f}:d=2[music];'
        '[music][side]sidechaincompress=threshold=0.045:ratio=3.2:attack=14:release=250[under];'
        f'[2:a]adelay=2000:all=1,apad,atrim=duration={total:.8f}[games];'
        '[voice][under][games]amix=inputs=3:normalize=0,alimiter=limit=0.89:level=false[mix]'
    )
    ff('-i', VOICE, '-stream_loop', '-1', '-i', music, '-f', 'concat', '-safe', '0', '-i', listing,
       '-filter_complex', graph, '-map', '[mix]', '-t', f'{total:.8f}', '-c:a', 'aac', '-b:a', '256k',
       '-ar', RATE, '-ac', 2, destination)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--plan-only', action='store_true')
    args = parser.parse_args()
    control = load(ROOT / 'shared/publishing/video-production-control.json')['designSpecifics18Selected20261111']
    assert 'DS01' in control['episodes'] and not control['youtubeAuthorized']
    sources = load(HERE / 'source-review.json')
    prior = load(ROOT / 'production/batches/animation-18-20261031/contrast-v5/review-manifest.json')['records'][0]
    brand = next(file for file in prior['files'] if file['kind'] == 'clean.mp4')
    assert sha(brand['path']) == brand['sha256']
    timing = load(VOICE.with_suffix('.timing.json'))
    cues = load(LOCAL / 'captions/captions.json')['cues']
    rows, body = cut_list(timing, cues)
    for part in rows:
        if part['kind'] != 'game':
            continue
        source = sources[part['source']]
        assert source['classification'] == 'independent-gameplay' and sha(source['file']) == source['sha256']
        assert any(a <= part['offset'] and part['offset'] + part['frames'] / FPS <= b + .001
                   for a, b, _ in source['clipWindows']), part
    save(LOCAL / 'render-plan.json', {'bodyFrames': body, 'segments': rows, 'voiceSha256': sha(VOICE),
                                     'captionAssSha256': sha(LOCAL / 'captions/captions.ko.ass')})
    if args.plan_only:
        print(json.dumps(rows, ensure_ascii=False, indent=2), flush=True)
        return
    OUTPUT.mkdir(parents=True, exist_ok=True)
    parts = MEDIA / 'DS01-assembly'
    parts.mkdir(parents=True, exist_ok=True)
    for i, t in enumerate((106.35, 107.12, 108.50)):
        ff('-ss', t, '-i', sources['smash']['file'], '-an', '-frames:v', 1, '-c:v', 'png',
           '-threads', 1, parts / f'finish-still-{i}.png')
    files = []
    for index, part in enumerate(rows):
        key, kind, frames = part['scene'], part['kind'], part['frames']
        destination = parts / f'{index:02d}-{key}-{kind}.mp4'
        if kind == 'game':
            picture(sources[part['source']]['file'], frames, part['offset'], destination, kind, gameplay_focus(part))
        elif kind == 'explanation':
            explanation(key, frames, destination)
        else:
            offset = 0 if kind == 'brand' else (prior['frames'] - 600) / FPS
            picture(brand['path'], frames, offset, destination, kind)
        files.append(destination)
        print(index, key, kind, frames, flush=True)
    listing = parts / 'picture.txt'
    listing.write_text(''.join(f"file '{p.as_posix()}'\n" for p in files), encoding='utf-8')
    mix = parts / 'final-mix.m4a'
    mix_audio(rows, sources, body, parts, mix)
    clean, captioned = OUTPUT / 'DS01.clean.mp4', OUTPUT / 'DS01.captioned.mp4'
    ff('-f', 'concat', '-safe', '0', '-i', listing, '-i', mix, '-map', '0:v:0', '-map', '1:a:0',
       '-c', 'copy', '-movflags', '+faststart', clean)
    ass = (LOCAL / 'captions/captions.ko.ass').resolve().as_posix().replace(':', '\\:')
    ff('-threads', 2, '-filter_threads', 2, '-i', clean, '-vf', f"ass='{ass}'", *VENC,
       '-c:a', 'copy', '-movflags', '+faststart', captioned)
    proof = []
    for file in (clean, captioned):
        check_picture(file, body + 720)
        ff('-threads', 2, '-i', file, '-f', 'null', '-')
        proof.append({'path': str(file), 'sha256': sha(file), 'fullDecode': 'passed'})
    for lang in ('ko', 'en'):
        path = OUTPUT / f'DS01.{lang}.srt'
        shutil.copyfile(LOCAL / f'captions/captions.{lang}.srt', path)
        proof.append({'path': str(path), 'sha256': sha(path)})
    save(OUTPUT / 'delivery.json', {'episode': 'DS01', 'stage': 'encoded-sample-review-pending',
         'technicalQa': True, 'humanReviewed': False, 'platformChanged': False, 'bodyFrames': body,
         'gameFrames': sum(part['frames'] for part in rows if part['kind'] == 'game'), 'files': proof})
    print('Four output files encoded and decoded', OUTPUT, flush=True)


if __name__ == '__main__':
    main()
