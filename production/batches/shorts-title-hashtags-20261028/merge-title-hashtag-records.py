"""Validate saved UI receipts; prepare/apply title-only records for fourteen Shorts.

Default writes C:-local snapshots/JSON operations only. --apply writes exactly
fourteen upload records and their selected worklist rows. No platform or Git
mutation. Thumbnail, schedule, privacy, rights, video and human review stay intact.
"""
from __future__ import annotations
import argparse
import copy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

TASK = Path(__file__).resolve().parent
REPO = Path('D:/Github/VideoEditing')
OW = 'QlIwFupj9Dk'
EXCLUDED = 'iZm0krfqQ_4'
CHANGE_ID = 'shorts-title-hashtags-20261028'
WORKLIST = 'shared/publishing/shorts-worklist.json'

def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def sha(data):
    return hashlib.sha256(data).hexdigest()

def fsha(path):
    return sha(Path(path).read_bytes())

def output_bytes(value, original=b''):
    newline = '\r\n' if b'\r\n' in original else '\n'
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').replace('\n', newline).encode('utf-8')

def git(*args):
    p = subprocess.run(['git', '-c', 'gc.auto=0', '-c', 'maintenance.auto=false', *args], cwd=REPO, capture_output=True)
    return p.returncode, p.stdout, p.stderr

def pointer(path):
    return '/' + '/'.join(str(x).replace('~', '~0').replace('/', '~1') for x in path)

def difference(before, after, path=()):
    if before == after:
        return []
    if isinstance(before, dict) and isinstance(after, dict):
        result = []
        for key in before:
            if key not in after:
                result.append({'op': 'remove', 'path': pointer((*path, key)), 'before': before[key]})
        for key, value in after.items():
            if key not in before:
                result.append({'op': 'add', 'path': pointer((*path, key)), 'value': value})
            else:
                result.extend(difference(before[key], value, (*path, key)))
        return result
    if isinstance(before, list) and isinstance(after, list) and len(before) == len(after):
        result = []
        for i, (a, b) in enumerate(zip(before, after)):
            result.extend(difference(a, b, (*path, i)))
        return result
    return [{'op': 'replace', 'path': pointer(path), 'before': before, 'value': after}]

def list_by_id(items, label):
    indexed = {x['videoId']: x for x in items}
    assert len(indexed) == len(items), f'{label}: duplicate videoId'
    return indexed

def preserve_except(before, after, allowed, label):
    assert {k: v for k, v in before.items() if k not in allowed} == {k: v for k, v in after.items() if k not in allowed}, f'{label}: protected fields changed'

def verify(receipt, proposed, schedule, baseline):
    vid = receipt['videoId']
    assert receipt.get('slug') == proposed['slug'], f'{vid}: slug differs'
    assert receipt.get('verifiedAfterReload') is True and receipt.get('observedAt'), f'{vid}: reload observation missing'
    assert receipt.get('proof') and Path(receipt['proof']).is_file(), f'{vid}: screenshot missing'
    assert receipt.get('thumbnailUnchanged') is True, f'{vid}: thumbnail preservation not observed'
    assert receipt['title'] == proposed['title'], f'{vid}: saved title differs'
    assert receipt['previousTitle'] == proposed['previousTitle'] == baseline['title'], f'{vid}: before title differs'
    assert receipt['hashtags'] == proposed['hashtags'], f'{vid}: hashtags differ'
    hashtags = proposed['hashtags']
    assert 2 <= len(hashtags) <= 3 and len(set(hashtags)) == len(hashtags)
    assert all(re.fullmatch(r'#[^\s#]+', s) for s in hashtags)
    assert '#게임개발' in hashtags and len(proposed['title']) <= 100
    assert proposed['title'] == proposed['previousTitle'] + ' ' + ' '.join(hashtags)
    if vid == OW:
        assert receipt['status'] in ('private', 'uploaded-private-rights-hold'), 'Outer Wilds must remain private'
        assert not receipt.get('dateKst') and not receipt.get('timeKst'), 'Outer Wilds must have no release schedule'
    else:
        assert receipt['status'] == 'scheduled', f'{vid}: scheduled state lost'
        assert receipt['dateKst'] == schedule['dateKst'] and receipt['timeKst'] == schedule['timeKst'], f'{vid}: schedule changed'
        assert receipt['zone'] == 'GMT+0900', f'{vid}: timezone unverified'

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()
    plan = load(TASK / 'plan.json')
    plans = list_by_id(plan['items'], 'plan')
    assets = list_by_id(load(TASK / 'assets-audit.json')['items'], 'assets')
    schedules = list_by_id(load(TASK / 'schedule-plan.json')['items'], 'prior schedules')
    receipts = list_by_id(load(TASK / 'platform-receipts.json'), 'UI receipts')
    baseline_doc = load(TASK / 'studio-before.json')
    baselines = list_by_id(baseline_doc['rows'], 'live UI baseline')
    assert len(assets) == len(plans) == len(receipts) == 14
    assert set(assets) == set(plans) == set(receipts)
    assert len(schedules) == 13 and set(schedules) == set(assets) - {OW}
    assert set(assets) <= set(baselines) and EXCLUDED not in assets
    now = datetime.now(timezone.utc).isoformat()
    auth = {'id': CHANGE_ID, 'dateKst': '2026-10-28', 'userEvidence': plan['request'],
            'scope': 'Append relevant hashtags to Korean titles of the same recent fourteen existing Shorts. Base wording, thumbnails, descriptions, English metadata, schedules, privacy, rights holds and master bytes are preserved.',
            'actualHumanViewingOrListeningInferred': False, 'masterBytesChanged': False,
            'publicationAuthorizationChanged': False, 'scheduleChanged': False, 'thumbnailChanged': False}
    changes, versions = [], {}
    for vid, asset in assets.items():
        r, p, b = receipts[vid], plans[vid], baselines[vid]
        verify(r, p, schedules.get(vid), b)
        path = Path(asset['receiptPath'])
        rel = path.relative_to(REPO).as_posix()
        original = path.read_bytes()
        old = json.loads(original.decode('utf-8-sig'))
        assert old['videoId'] == vid and old['slug'] == p['slug']
        old_title = old.get('title') or old.get('metadata', {}).get('title')
        assert old_title == p['previousTitle'], f'{vid}: current record title differs'
        master = old.get('masterSha256') or old.get('captionedSha256') or old.get('uploadedFile', {}).get('sha256')
        assert master == p['masterSHA256'] == asset['masterSHA256'], f'{vid}: video master changed'
        assert old['thumbnail']['sha256'] == p['thumbnailSHA256'] == fsha(old['thumbnail']['path']), f'{vid}: thumbnail bytes changed'
        new = copy.deepcopy(old)
        proof = {'path': r['proof'], 'sha256': fsha(r['proof'])}
        baseline = {'observedAt': baseline_doc['observedAt'], 'status': b['cells'][3],
                    'dateLabel': b['cells'][4], 'views': b['cells'][5],
                    'interpretation': 'Not public at baseline; low private test counts do not measure audience response.'}
        history = new.setdefault('platformChangeHistory', [])
        assert not any(x.get('id') == CHANGE_ID for x in history), f'{vid}: already merged'
        history.append({'id': CHANGE_ID, 'observedAt': r['observedAt'],
                        'source': 'Actual YouTube Studio UI; title and unchanged visibility re-opened',
                        'before': {'title': old_title, 'metadataRefresh': old.get('metadataRefresh'),
                                   'metadataRefreshAuthorization': old.get('metadataRefreshAuthorization'), 'baseline': baseline},
                        'after': {'title': r['title'], 'hashtags': r['hashtags'], 'status': r['status'],
                                  'dateKst': r.get('dateKst'), 'timeKst': r.get('timeKst'), 'zone': r.get('zone')},
                        'thumbnailUnchanged': True, 'changeDesign': 'Title hashtag suffix only; no controlled ranking or performance experiment.',
                        'performanceImprovementClaimed': False, 'proof': proof})
        if 'title' in new:
            new['title'] = r['title']
        if isinstance(new.get('metadata'), dict) and 'title' in new['metadata']:
            new['metadata']['title'] = r['title']
        new['metadataRefreshAuthorization'] = {**auth, 'videoId': vid, 'masterSHA256': master}
        new['metadataRefresh'] = {'id': CHANGE_ID, 'title': r['title'], 'hashtags': r['hashtags'],
                                  'titleVerifiedAfterReload': True, 'observedAt': r['observedAt'], 'proof': proof,
                                  'baseTitleChanged': False, 'thumbnailChanged': False, 'descriptionChanged': False,
                                  'englishMetadataChanged': False, 'fullPlaybackOrListeningPerformed': False,
                                  'baseline': baseline, 'performanceImprovementClaimed': False}
        new['updatedAt'] = r['observedAt']
        preserve_except(old, new, {'title', 'metadata', 'platformChangeHistory', 'metadataRefreshAuthorization', 'metadataRefresh', 'updatedAt'}, vid)
        if 'metadata' in old:
            preserve_except(old['metadata'], new['metadata'], {'title'}, vid + '/metadata')
        versions[rel] = (original, output_bytes(new, original))
        changes.append({'file': rel, 'videoId': vid, 'slug': p['slug'], 'operations': difference(old, new)})
    before_bytes = (REPO / WORKLIST).read_bytes()
    old_work = json.loads(before_bytes.decode('utf-8-sig'))
    new_work = copy.deepcopy(old_work)
    for vid, p in plans.items():
        matches = [(i, row) for i, row in enumerate(new_work['rows']) if row.get('slug') == p['slug']]
        assert len(matches) == 1
        _, row = matches[0]
        assert (row.get('youtubeId') or row.get('videoId')) in (None, vid)
        old_row = copy.deepcopy(row)
        r = receipts[vid]
        if 'title' in row:
            assert row['title'] == p['previousTitle'], f'{vid}: worklist title differs'
            row['title'] = p['title']
        row['metadataRefresh'] = {'id': CHANGE_ID, 'title': r['title'], 'hashtags': r['hashtags'],
                                  'observedAt': r['observedAt'], 'verifiedAfterReload': True,
                                  'baseTitleChanged': False, 'thumbnailChanged': False,
                                  'combinedTitleThumbnailRevision': False, 'performanceImprovementClaimed': False}
        row['updatedAt'] = r['observedAt']
        preserve_except(old_row, row, {'title', 'metadataRefresh', 'updatedAt'}, vid + '/worklist')
    versions[WORKLIST] = (before_bytes, output_bytes(new_work, before_bytes))
    changes.append({'file': WORKLIST, 'rowAnchors': {str(i): r.get('slug') for i, r in enumerate(old_work['rows'])}, 'operations': difference(old_work, new_work)})
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    bundle = TASK / 'record-merge-bundles' / stamp
    bundle.mkdir(parents=True)
    code, head, _ = git('rev-parse', 'HEAD')
    assert code == 0
    manifest = {'changeId': CHANGE_ID, 'preparedAt': now, 'mode': 'apply' if args.apply else 'dry-run',
                'head': head.decode().strip(), 'files': [], 'humanReviewFlagsUnchanged': True,
                'thumbnailSchedulePrivacyAndRightsUnchanged': True, 'noPlatformActions': True,
                'noGitMutation': True, 'outerWildsHeldPrivate': True, 'oldBloomExcluded': True}
    for rel, (before, after) in versions.items():
        for label, data in [('before', before), ('after', after)]:
            dest = bundle / label / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
        entry = {'path': rel, 'beforeSHA256': sha(before), 'afterSHA256': sha(after)}
        for label, spec in [('head', f'HEAD:{rel}'), ('index', f':{rel}')]:
            code, data, _ = git('show', spec)
            entry[label + 'Exists'] = code == 0
            if code == 0:
                dest = bundle / label / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(data)
                entry[label + 'SHA256'] = sha(data)
        code, index, _ = git('ls-files', '--stage', '--', rel)
        assert code == 0
        entry['semanticIndexEntry'] = index.decode('utf-8').strip()
        manifest['files'].append(entry)
    (bundle / 'manifest.json').write_bytes(output_bytes(manifest))
    (bundle / 'own-changes.json').write_bytes(output_bytes(changes))
    if args.apply:
        for rel, (before, _) in versions.items():
            assert (REPO / rel).read_bytes() == before, f'Concurrent modification: {rel}'
        for rel, (_, after) in versions.items():
            path = REPO / rel
            temp = path.with_name(path.name + '.hashtags-20261028.tmp')
            assert not temp.exists()
            temp.write_bytes(after)
            os.replace(temp, path)
    print(json.dumps({'mode': manifest['mode'], 'bundle': str(bundle), 'selectedReceiptCount': 14,
                      'schedulesPreserved': 13, 'heldPrivate': OW, 'thumbnailsPreserved': 14,
                      'changedFileCount': len(versions), 'repoWritten': args.apply}, ensure_ascii=False))

if __name__ == '__main__':
    main()
