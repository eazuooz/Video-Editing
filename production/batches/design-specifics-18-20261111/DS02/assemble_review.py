"""Apply the reviewed game clips and response diagrams to DS02's actual narration."""

import argparse
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'DS01'))
import assemble_review as common


LOCAL = HERE.parent / 'local/DS02'
VOICE = LOCAL / 'voice/ds02-button-weight.wav'
OUTPUT = common.OUTPUT.parent / 'DS02'
MOTION = common.ROOT / 'shared/output/motion-canvas'
RESPONSES = MOTION / 'ds02-button-response-preview.mp4'
CONTROLS = MOTION / 'ds02-control-studies-review.mp4'
FPS = common.FPS


def cut_list(timing):
    entries = timing['entries']
    starts = [round(item['start'] * FPS) for item in entries]
    body = round(timing['duration_seconds'] * FPS)
    durations = dict(zip([item['scene_id'] for item in entries],
                         [b - a for a, b in zip(starts, starts[1:] + [body])], strict=True))
    game = {'01': ('sonic', 3.70), '02': ('sonic', 23.65),
            '04': ('celeste', .3), '07': ('smash', 193.0)}
    context = round(body * .60) - sum(durations[key] for key in game)
    assert 180 <= context <= min(durations['06'] - 120, round(12.5 * FPS)), (context, durations)
    rows = [common.row('brand', 'brand', 120)]
    for key, frames in durations.items():
        if key in game:
            source, offset = game[key]
            rows.append(common.row(key, 'game', frames, source=source, offset=offset))
        elif key == '06':
            rows.append(common.row(key, 'game', context, source='celeste', offset=52.5))
            rows.append(common.row(key, 'explanation', frames - context))
        else:
            rows.append(common.row(key, 'explanation', frames))
    rows.append(common.row('member', 'member', 600))
    assert sum(row['frames'] for row in rows) == body + 720
    assert sum(row['frames'] for row in rows if row['kind'] == 'game') == round(body * .6)
    return rows, body


def cue_box(part):
    # Brief boxes anchor to an observed source event, then clear before the character moves away.
    boxes = {'01': (3.73, 3.86, 580, 602, 116, 149),
             '04': (6.05, 6.22, 1136, 447, 118, 136),
             '07': (197.71, 197.87, 939, 528, 201, 214)}
    item = boxes.get(part['scene'])
    if not item:
        return ''
    start, end, x, y, w, h = item
    a, b = start - part['offset'], end - part['offset']
    return f",drawbox=x={x}:y={y}:w={w}:h={h}:color=0xf2d786:t=7:enable='between(t,{a:.4f},{b:.4f})'"


def diagram(part, destination):
    clips = {'03': (RESPONSES, 0, 720), '05': (RESPONSES, 720, 1080),
             '06': (CONTROLS, 0, 420), '08': (CONTROLS, 420, 960)}
    source, start, end = clips[part['scene']]
    frames = part['frames']
    chain = (f'trim=start_frame={start}:end_frame={end},setpts={frames / (end - start):.12f}*(PTS-STARTPTS),'
             'fps=60,tpad=stop_mode=clone:stop_duration=0.08,setsar=1')
    common.ff('-threads', 2, '-filter_threads', 2, '-i', source, '-an', '-vf', chain,
              '-frames:v', frames, *common.VENC, destination)
    common.check_picture(destination, frames)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--plan-only', action='store_true')
    args = parser.parse_args()
    selected = common.load(common.ROOT / 'shared/publishing/video-production-control.json')[
        'designSpecifics18Selected20261111']
    assert 'DS02' in selected['episodes'] and selected['youtubeAuthorized'] is False
    sources = common.load(HERE / 'source-review.json')
    rows, body = cut_list(common.load(VOICE.with_suffix('.timing.json')))
    for source in sources.values():
        assert source['classification'] == 'independent-gameplay' and common.sha(source['file']) == source['sha256']
    for part in rows:
        if part['kind'] == 'game':
            assert any(a <= part['offset'] and part['offset'] + part['frames'] / FPS <= b + .001
                       for a, b, _ in sources[part['source']]['clipWindows']), part
    captions = LOCAL / 'captions'
    common.save(LOCAL / 'render-plan.json', {'bodyFrames': body, 'segments': rows, 'voiceSha256': common.sha(VOICE),
                'captionAssSha256': common.sha(captions / 'captions.ko.ass')})
    if args.plan_only:
        print(rows, flush=True)
        return
    OUTPUT.mkdir(parents=True, exist_ok=True)
    parts = common.MEDIA / 'DS02-assembly'
    parts.mkdir(parents=True, exist_ok=True)
    prior = common.load(common.ROOT / 'production/batches/animation-18-20261031/contrast-v5/review-manifest.json')[
        'records'][0]
    brand = next(file for file in prior['files'] if file['kind'] == 'clean.mp4')
    assert common.sha(brand['path']) == brand['sha256']
    files = []
    for index, part in enumerate(rows):
        kind, frames = part['kind'], part['frames']
        destination = parts / f'{index:02d}-{part["scene"]}-{kind}.mp4'
        if kind == 'game':
            common.picture(sources[part['source']]['file'], frames, part['offset'], destination, kind, cue_box(part))
        elif kind == 'explanation':
            diagram(part, destination)
        else:
            offset = 0 if kind == 'brand' else (prior['frames'] - 600) / FPS
            common.picture(brand['path'], frames, offset, destination, kind)
        files.append(destination)
        print(index, part['scene'], kind, frames, flush=True)
    mix = parts / 'final-mix.m4a'
    common.mix_audio(rows, sources, body, parts, mix, VOICE)
    common.write_delivery('DS02', rows, body, parts, files, mix, captions, OUTPUT)


if __name__ == '__main__':
    main()
