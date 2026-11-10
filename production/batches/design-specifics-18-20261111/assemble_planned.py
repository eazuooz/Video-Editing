"""Assemble a selected episode from cue-sized, inspected gameplay and authored studies."""

import argparse
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / 'DS01'))
import assemble_review as common


FPS = common.FPS


def plan_cuts(timing, plan):
    starts = [round(entry['start'] * FPS) for entry in timing['entries']]
    body = round(timing['duration_seconds'] * FPS)
    durations = dict(zip([entry['scene_id'] for entry in timing['entries']],
                         [b - a for a, b in zip(starts, starts[1:] + [body])], strict=True))
    scenes = plan['scenes']
    assert list(scenes) == list(durations), 'Plan and spoken scene order must match'
    bounds = {}
    game = {}
    for scene, frames in durations.items():
        row = scenes[scene]
        windows = row.get('game', [])
        minimum = round(row.get('minGameSeconds', 0) * FPS) if 'diagram' in row else frames
        max_game = sum(round((end - start) * FPS) for _, start, end in windows)
        max_explanation = frames - round(row.get('minDiagramSeconds', 4) * FPS) if 'diagram' in row else frames
        maximum = min(max_game, max_explanation)
        assert 0 <= minimum <= maximum, (scene, minimum, maximum, frames)
        bounds[scene] = minimum, maximum
        preferred = round(row.get('preferredGameSeconds', minimum / FPS) * FPS)
        game[scene] = max(minimum, min(maximum, preferred))
    target = round(body * plan['gameplayShare'])
    adjustment = target - sum(game.values())
    for scene in plan.get('adjustableScenes', scenes):
        minimum, maximum = bounds[scene]
        change = max(minimum - game[scene], min(maximum - game[scene], adjustment))
        game[scene] += change
        adjustment -= change
    assert adjustment == 0, (adjustment, target, game, durations, bounds)

    rows = [common.row('brand', 'brand', 120)]
    for scene, frames in durations.items():
        row = scenes[scene]
        remaining = game[scene]
        shots = []
        for source, start, end in row.get('game', []):
            count = min(remaining, round((end - start) * FPS))
            if count:
                shots.append(common.row(scene, 'game', count, source=source, offset=start))
            remaining -= count
        assert not remaining
        if len(shots) > 1:
            # A remainder from a measured voice duration should still be a readable cut.
            previous, last = shots[-2:]
            minimum_shot = round(2.4 * FPS)
            last_source, last_start, last_end = row['game'][len(shots) - 1]
            assert (last_source, last_start) == (last['source'], last['offset'])
            transfer = min(minimum_shot - last['frames'], previous['frames'] - minimum_shot,
                           round((last_end - last_start) * FPS) - last['frames'])
            if transfer > 0:
                previous['frames'] -= transfer
                last['frames'] += transfer
        explanation = frames - game[scene]
        studies = [common.row(scene, 'explanation', explanation)] if explanation else []
        rows.extend(studies + shots if row.get('diagramFirst') else shots + studies)
    rows.append(common.row('member', 'member', 600))
    assert sum(row['frames'] for row in rows) == body + 720
    assert sum(row['frames'] for row in rows if row['kind'] == 'game') == target
    return rows, body


def verify_sources(rows, sources):
    for source in {part['source'] for part in rows if part['kind'] == 'game'}:
        receipt = sources[source]
        assert receipt['classification'] in {'independent-gameplay', 'publisher-gameplay-excerpts'}
        assert receipt['rights'] and common.sha(receipt['file']) == receipt['sha256']
        streams = common.probe(receipt['file'])['streams']
        video = next(stream for stream in streams if stream['codec_type'] == 'video')
        assert min(video['width'], video['height']) >= 1080, source
    for part in rows:
        if part['kind'] == 'game':
            start = part['offset']
            end = start + part['frames'] / FPS
            assert any(a <= start and end <= b + .001
                       for a, b, *_ in sources[part['source']]['verifiedWindows']), part


def draw_diagram(part, study, destination):
    source, start, end = study
    frames = part['frames']
    assert 0 <= start < end
    filters = (f'trim=start_frame={start}:end_frame={end},setpts={frames / (end - start):.12f}*(PTS-STARTPTS),'
               'fps=60,tpad=stop_mode=clone:stop_duration=0.08,setsar=1')
    common.ff('-threads', 2, '-filter_threads', 2, '-i', common.ROOT / source, '-an', '-vf', filters,
              '-frames:v', frames, *common.VENC, destination)
    common.check_picture(destination, frames)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('episode')
    parser.add_argument('--plan-only', action='store_true')
    args = parser.parse_args()
    episode = args.episode
    selection = common.load(common.ROOT / 'shared/publishing/video-production-control.json')[
        'designSpecifics18Selected20261111']
    assert episode in selection['episodes'] and not selection['youtubeAuthorized']
    base, local = HERE / episode, HERE / 'local' / episode
    plan, sources = (common.load(base / name) for name in ('production-plan.json', 'source-review.json'))
    stem = common.load(local / 'tts-manifest.json')['tts']['filenameStem']
    voice = local / 'voice' / f'{stem}.wav'
    rows, body = plan_cuts(common.load(voice.with_suffix('.timing.json')), plan)
    verify_sources(rows, sources)
    captions = local / 'captions'
    common.save(local / 'render-plan.json', {'bodyFrames': body, 'segments': rows,
                'voiceSha256': common.sha(voice), 'captionAssSha256': common.sha(captions / 'captions.ko.ass')})
    if args.plan_only:
        print(rows, flush=True)
        return

    parts = common.MEDIA / f'{episode}-assembly'
    output = common.OUTPUT.parent / episode
    for directory in (parts, output):
        directory.mkdir(parents=True, exist_ok=True)
    prior = common.load(common.ROOT / 'production/batches/animation-18-20261031/contrast-v5/review-manifest.json')[
        'records'][0]
    brand = next(file for file in prior['files'] if file['kind'] == 'clean.mp4')
    assert common.sha(brand['path']) == brand['sha256']
    files = []
    for index, part in enumerate(rows):
        kind, scene, frames = part['kind'], part['scene'], part['frames']
        destination = parts / f'{index:02d}-{scene}-{kind}.mp4'
        if kind == 'game':
            source = sources[part['source']]
            marks = common.gameplay_marks(part, plan['scenes'][scene].get('marks', []))
            common.picture(source['file'], frames, part['offset'], destination, kind,
                           common.game_badge(source['label'], left=source.get('badgeLeft', False)) + marks)
        elif kind == 'explanation':
            draw_diagram(part, plan['scenes'][scene]['diagram'], destination)
        else:
            offset = 0 if kind == 'brand' else (prior['frames'] - 600) / FPS
            common.picture(brand['path'], frames, offset, destination, kind)
        files.append(destination)
        print(index, scene, kind, frames, flush=True)
    mix = parts / 'final-mix.m4a'
    common.mix_audio(rows, sources, body, parts, mix, voice)
    common.write_delivery(episode, rows, body, parts, files, mix, captions, output)


if __name__ == '__main__':
    main()
