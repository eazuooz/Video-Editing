"""Combine DS04's eight controlled comparisons with inspected native gameplay."""

import argparse
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'DS01'))
import assemble_review as common


LOCAL = HERE.parent / 'local/DS04'
VOICE = LOCAL / 'voice/ds04-hit-stop.wav'
OUTPUT = common.OUTPUT.parent / 'DS04'
PARTS = common.MEDIA / 'DS04-assembly'
STUDIES = common.ROOT / 'shared/output/motion-canvas/ds04-eight-hit-stop-studies.mp4'
FPS = common.FPS


def cut_list(timing, plan):
    starts = [round(item['start'] * FPS) for item in timing['entries']]
    body = round(timing['duration_seconds'] * FPS)
    durations = dict(zip([item['scene_id'] for item in timing['entries']],
                         [b - a for a, b in zip(starts, starts[1:] + [body])], strict=True))
    targets = plan['targets']
    primary = {'01': ((9.2, 19.4), (38.0, 45.5)), '10': ((71.7, 83.0), (47.0, 56.0))}
    mixed = [key for key in durations if key not in primary]
    budget = round(body * .60) - sum(durations[key] for key in primary)
    maximum = {key: min(round((targets[key]['window'][1] - targets[key]['window'][0]) * FPS),
                        durations[key] - 240) for key in mixed}
    native = {key: min(maximum[key], max(240, round(durations[key] * .48))) for key in mixed}
    remainder = budget - sum(native.values())
    for key in ('04', '07', '02', '09', '03', '05', '06', '08'):
        delta = max(240 - native[key], min(maximum[key] - native[key], remainder))
        native[key] += delta
        remainder -= delta
    assert not remainder and min(native.values()) >= 240, (durations, budget, native)
    rows = [common.row('brand', 'brand', 120)]
    for key, frames in durations.items():
        source = targets[key]['source']
        if key in primary:
            for start, end in primary[key]:
                take = min(frames, round((end - start) * FPS))
                if take:
                    rows.append(common.row(key, 'game', take, source=source, offset=start))
                frames -= take
            assert frames == 0, (key, frames)
        else:
            start, _ = targets[key]['window']
            a = common.row(key, 'game', native[key], source=source, offset=start)
            b = common.row(key, 'explanation', frames - native[key])
            rows.extend([b, a] if targets[key].get('afterDiagram') else [a, b])
    rows.append(common.row('member', 'member', 600))
    assert sum(row['frames'] for row in rows) == body + 720
    assert sum(row['frames'] for row in rows if row['kind'] == 'game') == round(body * .6)
    return rows, body


def diagram(part, index, destination):
    start, frames = index * 420, part['frames']
    filters = (f'trim=start_frame={start}:end_frame={start+420},setpts={frames/420:.12f}*(PTS-STARTPTS),'
               'fps=60,tpad=stop_mode=clone:stop_duration=0.08,setsar=1')
    common.ff('-threads', 2, '-filter_threads', 2, '-i', STUDIES, '-an', '-vf', filters,
              '-frames:v', frames, *common.VENC, destination)
    common.check_picture(destination, frames)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--plan-only', action='store_true')
    args = parser.parse_args()
    selected = common.load(common.ROOT / 'shared/publishing/video-production-control.json')[
        'designSpecifics18Selected20261111']
    assert 'DS04' in selected['episodes'] and not selected['youtubeAuthorized']
    sources = common.load(HERE / 'source-review.json')
    plan = common.load(HERE / 'production-plan.json')
    rows, body = cut_list(common.load(VOICE.with_suffix('.timing.json')), plan)
    for key in {part['source'] for part in rows if part['kind'] == 'game'}:
        source = sources[key]
        assert source['classification'] == 'independent-gameplay' and common.sha(source['file']) == source['sha256']
    for part in rows:
        if part['kind'] == 'game':
            assert any(a <= part['offset'] and part['offset'] + part['frames'] / FPS <= b + .001
                       for a, b, _ in sources[part['source']]['verifiedWindows']), part
    captions = LOCAL / 'captions'
    common.save(LOCAL / 'render-plan.json', {'bodyFrames': body, 'segments': rows, 'voiceSha256': common.sha(VOICE),
                'captionAssSha256': common.sha(captions / 'captions.ko.ass')})
    if args.plan_only:
        print(rows, flush=True)
        return
    common.check_picture(STUDIES, 3360)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    PARTS.mkdir(parents=True, exist_ok=True)
    prior = common.load(common.ROOT / 'production/batches/animation-18-20261031/contrast-v5/review-manifest.json')[
        'records'][0]
    brand = next(file for file in prior['files'] if file['kind'] == 'clean.mp4')
    assert common.sha(brand['path']) == brand['sha256']
    files = []
    for index, part in enumerate(rows):
        kind, key, frames = part['kind'], part['scene'], part['frames']
        destination = PARTS / f'{index:02d}-{key}-{kind}.mp4'
        if kind == 'game':
            labels = {'finalFight': '파이널 파이트 원', 'armsHelix': 'ARMS', 'armsRibbon': 'ARMS',
                      'iceborne': '몬스터 헌터 월드 아이스본 · 태도'}
            marks = common.gameplay_marks(part, plan['targets'][key].get('marks', []))
            common.picture(sources[part['source']]['file'], frames, part['offset'], destination, kind,
                           common.game_badge(labels[part['source']]) + marks)
        elif kind == 'explanation':
            diagram(part, plan['targets'][key]['study'], destination)
        else:
            offset = 0 if kind == 'brand' else (prior['frames'] - 600) / FPS
            common.picture(brand['path'], frames, offset, destination, kind)
        files.append(destination)
        print(index, key, kind, frames, flush=True)
    mix = PARTS / 'final-mix.m4a'
    common.mix_audio(rows, sources, body, PARTS, mix, VOICE)
    common.write_delivery('DS04', rows, body, PARTS, files, mix, captions, OUTPUT)


if __name__ == '__main__':
    main()
