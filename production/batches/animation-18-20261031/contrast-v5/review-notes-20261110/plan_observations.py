"""Place short explanations in verified gaps within repeated observation footage."""
from collections import Counter
import json
import math
from pathlib import Path
import re


HERE = Path(__file__).resolve().parent
BATCH = HERE.parent
ROOT = BATCH.parents[3]
WORK = BATCH / 'local/review-notes-20261110'
OUTPUT = Path('C:/Users/1/Videos/YamyamCoding/animation-review-notes-20261110')
TIMECODE = r'\d\d:\d\d:\d\d,\d+'
PRIORITY = ('A06', 'A08', 'A11')


def read(path):
    return Path(path).read_text('utf-8-sig')


def load(path):
    return json.loads(read(path))


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf8')


def relative(path):
    return path.relative_to(ROOT).as_posix()


def seconds(value):
    hours, minutes, secs = value.replace(',', '.').split(':')
    return int(hours) * 3600 + int(minutes) * 60 + float(secs)


def authored_and_game_passes(integration, game):
    rows = []
    for row in integration['rows']:
        if row['mode'] == 'native':
            rows.append((row['relationFrameStart'], row['relationFrameEnd'], 'demo-' + row['key'], None))
    for row in game['pictureEdits']:
        media = row.get('mediaSegments', [])
        if len(media) == 1 and media[0]['kind'] == 'native-gameplay':
            rows.append((row['startFrame'], row['endFrame'], media[0]['sourceKey'],
                         round(media[0]['sourceLocalIn'], 3)))
    groups = []
    for start, end, key, source_in in sorted(rows):
        identity = (key, source_in)
        if groups and identity == groups[-1]['identity'] and abs(groups[-1]['end'] - start) <= 3:
            groups[-1]['end'] = end
            groups[-1]['passStarts'].append(start)
        else:
            groups.append({'start': start, 'end': end, 'identity': identity, 'passStarts': [start]})
    return [group for group in groups if len(group['passStarts']) > 1]


def final_frame(edl, frame):
    row = next(row for row in edl['pictureEdl'] if row['oldStartFrame'] <= frame < row['oldEndFrame'])
    return row['outputStartFrame'] + min(frame - row['oldStartFrame'], row['frames'] - 1)


def free_windows(start, end, captions):
    cursor = start
    for left, right in captions:
        if right <= cursor:
            continue
        if left >= end:
            break
        if left > cursor:
            yield cursor, min(end, left)
        cursor = max(cursor, right)
    if cursor < end:
        yield cursor, end


def main():
    prior = load(BATCH / 'review-manifest.json')
    scope = load(ROOT / 'shared/publishing/video-production-control.json')['animationContrastRevision20261108']
    assert prior['scope'] == scope['episodes'] and scope['renderAuthorized']
    choices = load(HERE / 'observation-cues.json')
    output_plan = HERE / 'observation-plan.json'
    existing = load(output_plan)['episodes'] if output_plan.exists() else {}
    integration = {row['id']: row for row in load(BATCH / 'renderer/integration-caption-safe.json')['episodes']}
    game = {row['id']: row for row in load(BATCH / 'game-plates-caption-safe.json')['episodes']}
    episodes = {}
    scenes = []
    for record in sorted(prior['records'], key=lambda row: (row['id'] not in PRIORITY, row['id'])):
        ep = record['id']
        edl = load(BATCH / 'local/explanation-assembly' / ep / 'edl.json')
        ko = next(row for row in record['files'] if row['kind'] == 'ko.srt')
        en = next(row for row in record['files'] if row['kind'] == 'en.srt')
        cues = set(re.findall(f'({TIMECODE}) --> ({TIMECODE})', read(ko['path']) + '\n' + read(en['path'])))
        occupied = sorted((math.floor(seconds(a) * 60), math.ceil(seconds(b) * 60)) for a, b in cues)
        counts = Counter()
        rows = []
        old_ids = {(r['study'], *r['range']): r['id'] for r in existing.get(ep, [])}
        next_id = max((int(value[-2:]) for value in old_ids.values()), default=0) + 1
        windows_to_check = []
        for group in authored_and_game_passes(integration[ep], game[ep]):
            key, source_in = group['identity']
            start = final_frame(edl, group['start'])
            end = final_frame(edl, group['end'] - 1) + 1
            starts = [final_frame(edl, x) for x in group['passStarts']]
            windows_to_check.append((start, end, key, source_in, starts))
        for row in edl['pictureEdl']:
            if row['id'] == 'A15-keys-three-complete-native-passes':
                start, end = row['outputStartFrame'], row['outputEndFrame']
                assert ep == 'A15' and (end - start) % 3 == 0
                windows_to_check.append((start, end, 'demo-keys', None,
                                         [start + (end - start) * i // 3 for i in range(3)]))
        for start, end, key, source_in, starts in sorted(windows_to_check):
            windows = [w for w in free_windows(start, end, occupied) if w[1] - w[0] >= 132]
            if not windows:
                continue
            a, b = max(windows, key=lambda w: w[1] - w[0])
            counts[key] += 1
            suffix = f'#{counts[key]}' if counts[key] > 1 else ''
            ko_text, en_text = choices[ep][key + suffix]
            scene_id = old_ids.get((key, start, end))
            if scene_id is None:
                scene_id = f'{ep}OBS{next_id:02d}'
                next_id += 1
            rows.append({'id': scene_id, 'study': key, 'sourceLocalIn': source_in,
                         'range': [start, end], 'available': [a + 14, b - 11],
                         'passStarts': starts,
                         'ko': ko_text, 'en': en_text})
            scenes.append({'id': scene_id, 'title': f'{ep} 반복 관찰', 'lines': [ko_text]})
        episodes[ep] = rows
    assert all(episodes.values())
    save(output_plan, {'clock': 'contrast-v5 final 60 fps', 'episodes': episodes})
    script = WORK / 'observations.ko.json'
    manifest = load(BATCH / 'narration/released-tts-manifest.json')
    manifest.update(slug='animation-observation-notes', revision='review-notes-20261110')
    manifest['paths']['script'] = relative(script)
    manifest['tts'].update(outputDir=relative(WORK / 'voice'), filenameStem='observation-notes')
    save(script, {'scenes': scenes})
    save(WORK / 'tts-manifest.json', manifest)
    print(f'{len(scenes)} observation cues across {len(episodes)} episodes')


if __name__ == '__main__':
    main()
