"""Edit DS03's observed gameplay and mathematical studies at the spoken cues."""

import argparse
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'DS01'))
import assemble_review as common


LOCAL = HERE.parent / 'local/DS03'
VOICE = LOCAL / 'voice/ds03-jump-physics.wav'
OUTPUT = common.OUTPUT.parent / 'DS03'
PARTS = common.MEDIA / 'DS03-assembly'
MANIM = PARTS / 'manim/videos/jump_studies/1080p60'
FPS = common.FPS


def cuts(timing, plan):
    entries = timing['entries']
    starts = [round(item['start'] * FPS) for item in entries]
    body = round(timing['duration_seconds'] * FPS)
    durations = dict(zip([item['scene_id'] for item in entries],
                         [b - a for a, b in zip(starts, starts[1:] + [body])], strict=True))
    fixed, mixed = plan['fullGameplay'], plan['mixedGameplay']
    native = {key: round(window['preferred'] * FPS) for key, window in mixed.items()}
    remaining = round(body * .6) - sum(durations[key] for key in fixed) - sum(native.values())
    for key in ('09', '10', '04', '02', '07', '08'):
        window = mixed[key]
        floor = round(window['minimum'] * FPS)
        ceiling = min(round(window['maximum'] * FPS), durations[key] - 150)
        assert floor <= native[key] <= ceiling, (key, durations[key])
        change = max(floor - native[key], min(ceiling - native[key], remaining))
        native[key] += change
        remaining -= change
    assert remaining == 0, (remaining, durations, native)
    rows = [common.row('brand', 'brand', 120)]
    for key, frames in durations.items():
        if key in fixed:
            source, start, end = fixed[key]
            assert start + frames / FPS <= end, (key, start, frames, end)
            rows.append(common.row(key, 'game', frames, source=source, offset=start))
        elif key in mixed:
            window = mixed[key]
            footage = common.row(key, 'game', native[key], source=window['source'], offset=window['start'])
            explanation = common.row(key, 'explanation', frames - native[key])
            rows.extend([explanation, footage] if window.get('afterDiagram') else [footage, explanation])
        else:
            rows.append(common.row(key, 'explanation', frames))
    rows.append(common.row('member', 'member', 600))
    assert sum(row['frames'] for row in rows) == body + 720
    assert sum(row['frames'] for row in rows if row['kind'] == 'game') == round(body * .6)
    return rows, body


def gameplay_overlay(part):
    labels = {'metroid': '메트로이드 드레드 · 크레이드', 'ghosts': '돌아온 마계촌',
              'zangief': '스트리트 파이터 6 · 훈련 화면', 'celeste': '셀레스트 · 공중 조향'}
    label = labels.get(part['source'])
    filters = common.game_badge(label) if label else ''
    # Native anchors checked in the decoded gameplay, in the final 880px picture region.
    focus = {'05': (28.53, 28.69, 778, 463, 139, 133),
             '06': (17.63, 18.52, 203, 432, 153, 155),
             '07': (31.54, 31.69, 879, 252, 203, 168)}
    item = focus.get(part['scene'])
    if item:
        start, end, x, y, w, h = item
        a, b = start - part['offset'], end - part['offset']
        filters += f",drawbox=x={x}:y={y}:w={w}:h={h}:color=0xf2d786:t=7:enable='between(t,{a:.4f},{b:.4f})'"
    return filters


def diagram(part, definition, destination):
    source, start, end, _ = definition
    frames = part['frames']
    picture = MANIM / f'{source}.mp4'
    common.check_picture(picture, 600)
    chain = (f'trim=start_frame={start}:end_frame={end},setpts={frames / (end - start):.12f}*(PTS-STARTPTS),'
             'fps=60,tpad=stop_mode=clone:stop_duration=0.08,setsar=1')
    common.ff('-threads', 2, '-filter_threads', 2, '-i', picture, '-an', '-vf', chain,
              '-frames:v', frames, *common.VENC, destination)
    common.check_picture(destination, frames)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--plan-only', action='store_true')
    args = parser.parse_args()
    selected = common.load(common.ROOT / 'shared/publishing/video-production-control.json')[
        'designSpecifics18Selected20261111']
    assert 'DS03' in selected['episodes'] and not selected['youtubeAuthorized']
    sources = common.load(HERE / 'source-review.json')
    plan = common.load(HERE / 'production-plan.json')
    rows, body = cuts(common.load(VOICE.with_suffix('.timing.json')), plan)
    for key in {part['source'] for part in rows if part['kind'] == 'game'}:
        source = sources[key]
        assert source['classification'] in {'independent-gameplay', 'publisher-gameplay-excerpts'}
        assert common.sha(source['file']) == source['sha256']
    captions = LOCAL / 'captions'
    common.save(LOCAL / 'render-plan.json', {'bodyFrames': body, 'segments': rows,
                'voiceSha256': common.sha(VOICE), 'captionAssSha256': common.sha(captions / 'captions.ko.ass')})
    if args.plan_only:
        print(rows, flush=True)
        return
    OUTPUT.mkdir(parents=True, exist_ok=True)
    prior = common.load(common.ROOT / 'production/batches/animation-18-20261031/contrast-v5/review-manifest.json')[
        'records'][0]
    brand = next(file for file in prior['files'] if file['kind'] == 'clean.mp4')
    assert common.sha(brand['path']) == brand['sha256']
    files = []
    for index, part in enumerate(rows):
        kind, key, frames = part['kind'], part['scene'], part['frames']
        destination = PARTS / f'{index:02d}-{key}-{kind}.mp4'
        if kind == 'game':
            common.picture(sources[part['source']]['file'], frames, part['offset'], destination, kind,
                           gameplay_overlay(part))
        elif kind == 'explanation':
            diagram(part, plan['diagrams'][key], destination)
        else:
            offset = 0 if kind == 'brand' else (prior['frames'] - 600) / FPS
            common.picture(brand['path'], frames, offset, destination, kind)
        files.append(destination)
        print(index, key, kind, frames, flush=True)
    mix = PARTS / 'final-mix.m4a'
    common.mix_audio(rows, sources, body, PARTS, mix, VOICE)
    common.write_delivery('DS03', rows, body, PARTS, files, mix, captions, OUTPUT)


if __name__ == '__main__':
    main()
