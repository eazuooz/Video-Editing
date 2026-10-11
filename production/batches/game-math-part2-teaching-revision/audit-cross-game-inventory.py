"""Audit adopted lecture cuts, never approve teaching from source counts."""
import json
import hashlib
import re
from pathlib import Path
from datetime import datetime, timezone, timedelta

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).parent / 'cross-game-review-20261011'

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def walk(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    names = {}
    source_files = list((ROOT / 'projects').glob('*/sources/gameplay-cuts.json'))
    source_files += list((ROOT / 'projects').glob('*/production/footage-sources.json'))
    for path in source_files:
        for obj in walk(read(path)):
            if obj.get('id') and obj.get('game'):
                aliases = {'Forza Horizon4': 'Forza Horizon 4', 'Portal2': 'Portal 2',
                           'Serious Sam2': 'Serious Sam 2', 'Subnautica2': 'Subnautica 2'}
                game = aliases.get(obj['game'], obj['game'])
                names.setdefault(obj['id'], set()).add(game)
            elif obj.get('id') and str(obj.get('name', '')).startswith('Portal 2 '):
                names.setdefault(obj['id'], set()).add('Portal 2')
            elif obj.get('id') and str(obj.get('name', '')).startswith('Tiny Glade '):
                names.setdefault(obj['id'], set()).add('Tiny Glade')
            elif obj.get('id') and '/app/2162800/' in str(obj.get('sourceUrl', '')):
                names.setdefault(obj['id'], set()).add('shapez 2')
    # Both recordings describe the same game, not two independent games.
    names.setdefault('_dw9jjRpanA', set()).add('Riders Republic')
    skate_record = read(Path(__file__).parent / 'interpolation-skate-source.json')
    assert skate_record['videoId'] == 'TPkvx2W8CV8' and skate_record['title'].startswith('SKATE 3 |')
    names.setdefault(skate_record['videoId'], set()).add('Skate 3')
    ledger = read(ROOT / 'shared/publishing/daily-alternating-schedule.json')
    targets = [row for row in ledger['actualSchedules']
               if str(row.get('slug', '')).startswith('game-math-')]
    if not any(row['slug'] == 'game-math-polar-2d' for row in targets):
        targets.append({'slug': 'game-math-polar-2d', 'videoId': 'PcxaKEvbzjg',
                        'date': '2026-10-08', 'historicalPublic': True})
    for slug in ['game-math-polygon-centers-v2', 'game-math-polygon-partition-v2']:
        targets.append({'slug': slug, 'videoId': None, 'date': None, 'notUploaded': True})
    results = []
    for row in targets:
        directory = ROOT / 'projects' / row['slug']
        manifest_path = directory / 'project.json'
        manifest = read(manifest_path)
        paths = manifest['paths']
        timeline_path = ROOT / paths['timeline']
        timeline = read(timeline_path)
        cuts_path = ROOT / paths['footageCuts']
        cuts = read(cuts_path)
        cut_by_scene = {str(c.get('scene')): c for c in cuts.get('cuts', [])}
        games, unresolved, actions = set(), set(), []
        for scene in timeline['scenes']:
            if scene.get('classification') != 'actual':
                continue
            cut = scene.get('cut') or scene.get('footage') or cut_by_scene.get(str(scene['id']), {})
            source_ids = sorted({str(o['sourceId']) for o in walk(cut) if o.get('sourceId')})
            if not source_ids and cuts.get('source', {}).get('id'):
                source_ids = [cuts['source']['id']]
            scene_games = set()
            for source_id in source_ids:
                matches = names.get(source_id, set())
                if len(matches) == 1:
                    scene_games.update(matches)
                else:
                    unresolved.add(source_id)
            games.update(scene_games)
            actions.append({'sceneId': scene['id'], 'title': scene.get('title'),
                            'sourceIds': source_ids, 'games': sorted(scene_games),
                            'seconds': scene.get('seconds'),
                            'nativeSegments': cut.get('sourceSegments', cut.get('segments', [])),
                            'sceneHasNarration': bool(scene.get('captions') or scene.get('cues'))})
        games = sorted(games)
        missing = max(0, 4 - len(games))
        studio_rows = []
        for page in ['studio-page1.json', 'studio-page2.json']:
            if (OUT / page).exists():
                studio_rows.extend(read(OUT / page))
        studio = next((s for s in studio_rows if s['videoId'] == row['videoId']), None)
        results.append({
            'slug': row['slug'], 'videoId': row['videoId'], 'recordedDate': row.get('date'),
            'studioStatus': studio['visibility'] if studio else 'not-uploaded' if row.get('notUploaded') else 'not-refreshed-in-this-inventory',
            'studioDateText': studio['date'] if studio else None,
            'currentStudioDirectlyObserved': studio is not None,
            'selectedDistinctGames': games, 'distinctGameCount': len(games),
            'minimumDistinctGames': 4, 'additionalDistinctGamesNeeded': missing,
            'unresolvedAdoptedSourceIds': sorted(unresolved),
            'revisionNeededByCount': bool(missing) if not unresolved else None,
            'status': 'evidenced-count-gap-content-review-pending' if missing and not unresolved
                      else 'current-content-and-source-mapping-review-required',
            'coverageApproved': False, 'wholeCurrentScriptsDirectlyRead': False,
            'currentFinalMovingPixelsReviewed': False, 'currentMixedAudioReviewed': False,
            'contracts': {'actualShare': manifest['editing']['targetGameplayShare'],
                          'explanationShare': manifest['editing']['targetExplanationShare'],
                          'palette': manifest.get('visualStyle'),
                          'backgroundMusic': manifest.get('audio', {}).get('backgroundMusic', {}).get('enabled'),
                          'sourceAudioPolicy': manifest.get('audio', {}).get('sourceAudioPolicy')},
            'preserveOriginalExplanationsAndPcm': True,
            'evidence': [{'path': p.relative_to(ROOT).as_posix(), 'sha256': sha(p)}
                         for p in [manifest_path, timeline_path, cuts_path, ROOT / paths['script']]],
            'adoptedActualScenes': actions,
        })
    report = {'schemaVersion': 1,
              'recordedAt': datetime.now(timezone(timedelta(hours=9))).isoformat(),
              'userEvidence': '미게시(예약 포함)와 기존 업로드를 검수하고 필요한 영상에 최소4종 게임 사례와 비교 해설을 적용',
              'policy': 'shared/publishing/game-example-coverage-policy.json',
              'scope': 'Current PART2 lecture ledger plus published polar2D; deleted historical IDs excluded.',
              'inventoryOnly': True, 'sourceNamesDoNotApproveTeaching': True,
              'platformSettingsChanged': False, 'newTtsOrRenderStarted': False,
              'projects': results}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'adopted-game-inventory.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps([{'slug': r['slug'], 'games': r['selectedDistinctGames'],
                       'needed': r['additionalDistinctGamesNeeded'], 'unresolved': r['unresolvedAdoptedSourceIds']}
                      for r in results], ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
