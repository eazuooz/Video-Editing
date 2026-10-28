"""Validate saved UI receipts and prepare/apply only 14 title/cover record changes.

Default creates a C:-local diff/snapshot bundle; --apply additionally writes the
14 upload receipts and their worklist rows. No platform action or Git mutation.
Schedules, privacy, rights holds, master hashes and human review are preserved.
"""
from __future__ import annotations

import argparse
import copy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess

TASK = Path(__file__).resolve().parent
REPO = Path('D:/Github/VideoEditing')
OW = 'QlIwFupj9Dk'
EXCLUDED = 'iZm0krfqQ_4'
QUOTE = '썸네일 글씨 잘보이게해줘~ 사람들이 잘 안봐 조회수가 제목도 조회수잘나오게~'
CHANGE_ID = 'shorts-title-thumbnail-readability-20261028'
WORKLIST = 'shared/publishing/shorts-worklist.json'


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def sha(data):
    return hashlib.sha256(data).hexdigest()


def fsha(path):
    return sha(Path(path).read_bytes())


def output_bytes(data, original=b''):
    newline = '\r\n' if b'\r\n' in original else '\n'
    return (json.dumps(data, ensure_ascii=False, indent=2) + '\n').replace('\n', newline).encode('utf-8')


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
    result = {x['videoId']: x for x in items}
    assert len(result) == len(items), f'{label}: duplicate videoId'
    return result


def verify(r, p, c, plan, baseline):
    vid = r['videoId']
    assert r.get('slug') == p['slug'] == c['slug'], f'{vid}: slug differs'
    assert r.get('verifiedAfterReload') is True, f'{vid}: persistence not verified'
    assert r.get('observedAt'), f'{vid}: missing UI observation time'
    assert r.get('proof') and Path(r['proof']).is_file(), f'{vid}: missing saved screenshot'
    assert r.get('title') == p['proposedTitle'], f'{vid}: saved title differs from final proposal'
    assert r.get('previousTitle') == baseline['title'], f'{vid}: before title differs from UI baseline'
    assert p['currentTitle'] == baseline['title'], f'{vid}: proposal uses stale title baseline'
    assert c.get('proposedTitle') == p['proposedTitle'], f'{vid}: cover title record differs'
    assert c['headline'] == p['thumbnailLines'], f'{vid}: cover wording differs from final proposal'
    assert r.get('thumbnailSHA256') == c['jpgSHA256'] == fsha(c['jpgPath']), f'{vid}: cover SHA mismatch'
    assert c['dimensions'] == [1080, 1920], f'{vid}: expected portrait cover'
    assert c['sourceFrameSHA256'] == fsha(c['sourceFramePath']), f'{vid}: source bitmap changed'
    if vid == OW:
        assert r.get('status') in ('private', 'thumbnail-only-private', 'uploaded-private-rights-hold'), 'Outer Wilds must remain private'
        assert not r.get('dateKst') and not r.get('timeKst'), 'Outer Wilds must have no release schedule'
    else:
        assert r.get('status') == 'scheduled', f'{vid}: schedule lost'
        assert r.get('dateKst') == plan['dateKst'] and r.get('timeKst') == plan['timeKst'], f'{vid}: schedule changed'
        assert r.get('zone') == 'GMT+0900', f'{vid}: zone not verified'


def protected_equal(before, after, fields, label):
    for field in fields:
        assert before.get(field) == after.get(field), f'{label}: protected field changed: {field}'


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()
    assets = list_by_id(load(TASK / 'assets-audit.json')['items'], 'assets')
    plans = list_by_id(load(TASK / 'schedule-plan.json')['items'], 'prior schedules')
    covers = list_by_id(load(TASK / 'covermap.json')['covers'], 'covers')
    proposals = list_by_id(load(TASK / 'title-proposals.json')['items'], 'title proposals')
    receipts = list_by_id(load(TASK / 'platform-receipts.json'), 'UI receipts')
    baseline_doc = load(TASK / 'studio-before.json')
    baselines = list_by_id(baseline_doc['rows'], 'UI baseline')
    assert len(assets) == 14 and len(plans) == 13 and OW in assets and OW not in plans
    assert set(receipts) == set(assets) == set(covers) == set(proposals)
    assert set(plans) == set(assets) - {OW} and EXCLUDED not in assets
    assert set(assets) <= set(baselines), 'Missing live Studio baseline'
    now = datetime.now(timezone.utc).isoformat()
    auth = {
        'id': CHANGE_ID, 'dateKst': '2026-10-28', 'userEvidence': QUOTE,
        'scope': 'Improve Korean titles and thumbnails of the same recent fourteen existing uploaded Shorts. Preserve all schedules, privacy, rights holds, descriptions, translated metadata and video bytes.',
        'actualHumanViewingOrListeningInferred': False, 'masterBytesChanged': False,
        'publicationAuthorizationChanged': False, 'scheduleChanged': False,
    }
    own_changes, file_versions = [], {}
    for vid, item in assets.items():
        r, c, p, b = receipts[vid], covers[vid], proposals[vid], baselines[vid]
        verify(r, p, c, plans.get(vid), b)
        path = Path(item['receiptPath'])
        rel = path.relative_to(REPO).as_posix()
        original = path.read_bytes()
        old = json.loads(original.decode('utf-8-sig'))
        assert old['videoId'] == vid and old['slug'] == item['slug']
        master = old.get('masterSha256') or old.get('captionedSha256') or old.get('uploadedFile', {}).get('sha256')
        assert master == item['masterSHA256'] == c['masterSHA256'], f'{vid}: master hash differs'
        old_title = old.get('title') or old.get('metadata', {}).get('title')
        assert old_title == b['title'], f'{vid}: local title differs from baseline; inspect before merge'
        new = copy.deepcopy(old)
        proof = {'path': r['proof'], 'sha256': fsha(r['proof'])}
        baseline = {
            'observedAt': baseline_doc['observedAt'], 'status': b['cells'][3],
            'dateLabel': b['cells'][4], 'views': b['cells'][5],
            'interpretation': 'Not public at baseline; these small counts are not public-audience performance evidence.',
        }
        change = {
            'id': CHANGE_ID, 'observedAt': r['observedAt'],
            'source': 'Actual YouTube Studio UI; title, thumbnail and unchanged visibility verified after reload',
            'before': {'title': old_title, 'thumbnail': copy.deepcopy(old['thumbnail']), 'baseline': baseline},
            'after': {'title': r['title'], 'thumbnailSHA256': c['jpgSHA256'], 'studioStatus': r['status'], 'dateKst': r.get('dateKst'), 'timeKst': r.get('timeKst'), 'zone': r.get('zone')},
            'changeDesign': 'Combined title and thumbnail revision; not a controlled single-variable A/B test.',
            'performanceImprovementClaimed': False, 'proof': proof,
        }
        history = new.setdefault('platformChangeHistory', [])
        assert not any(x.get('id') == CHANGE_ID for x in history), f'{vid}: merge already applied'
        history.append(change)
        if 'title' in new:
            new['title'] = r['title']
        if isinstance(new.get('metadata'), dict) and 'title' in new['metadata']:
            new['metadata']['title'] = r['title']
        new['metadataRefreshAuthorization'] = {**auth, 'videoId': vid, 'masterSHA256': master}
        new['metadataRefresh'] = {'id': CHANGE_ID, 'title': r['title'], 'titleVerifiedAfterReload': True, 'observedAt': r['observedAt'], 'proof': proof, 'descriptionChanged': False, 'englishMetadataChanged': False, 'fullPlaybackOrListeningPerformed': False, 'baseline': baseline, 'performanceImprovementClaimed': False}
        new['thumbnail'] = {
            'path': c['jpgPath'], 'sha256': c['jpgSHA256'], 'customFileUploaded': True,
            'status': 'applied-and-reopened',
            'sourceKind': 'actual-game-frame-with-independent-vector-typography-and-editorial-focus-mark',
            'sourceFramePath': c['sourceFramePath'], 'sourceFrameSHA256': c['sourceFrameSHA256'],
            'dimensions': c['dimensions'], 'headline': c['headline'], 'typography': c.get('typography'),
            'observedAt': r['observedAt'], 'evidence': proof, 'performanceImprovementClaimed': False,
        }
        new['updatedAt'] = r['observedAt']
        protected_equal(old, new, ('publicationAuthorization', 'schedule', 'publication', 'privacy', 'status', 'public', 'scheduled', 'publicMonetizedUseClearance', 'masterSha256', 'captionedSha256', 'uploadedFile', 'video', 'userAcceptance', 'authorization', 'humanFullListeningExplicitlyConfirmed', 'actualNewVersionHumanView', 'fullHumanListening', 'fullContinuousPlayback', 'englishMetadata', 'english', 'titleEn', 'savedMetadataReadback', 'englishMetadataReadback', 'subtitles', 'captions'), vid)
        if 'metadata' in old:
            protected_equal(old['metadata'], new['metadata'], set(old['metadata']) - {'title'}, vid + '/metadata')
        file_versions[rel] = (original, output_bytes(new, original))
        own_changes.append({'file': rel, 'videoId': vid, 'slug': item['slug'], 'operations': difference(old, new)})

    before_bytes = (REPO / WORKLIST).read_bytes()
    old_work = json.loads(before_bytes.decode('utf-8-sig'))
    new_work = copy.deepcopy(old_work)
    for vid, item in assets.items():
        matches = [(i, x) for i, x in enumerate(new_work['rows']) if x.get('slug') == item['slug']]
        assert len(matches) == 1, f"{item['slug']}: ambiguous worklist row"
        index, row = matches[0]
        assert (row.get('youtubeId') or row.get('videoId')) in (None, vid)
        old_row = copy.deepcopy(row)
        r, c = receipts[vid], covers[vid]
        if 'title' in row:
            assert row['title'] == baselines[vid]['title'], f'{vid}: worklist title differs from baseline'
            row['title'] = r['title']
        row['metadataRefresh'] = {'id': CHANGE_ID, 'title': r['title'], 'thumbnailSHA256': c['jpgSHA256'], 'thumbnailPath': c['jpgPath'], 'observedAt': r['observedAt'], 'verifiedAfterReload': True, 'combinedTitleThumbnailRevision': True, 'performanceImprovementClaimed': False}
        row['thumbnailRefresh'] = {'id': CHANGE_ID, 'status': 'applied-and-reopened', 'sha256': c['jpgSHA256'], 'path': c['jpgPath'], 'observedAt': r['observedAt']}
        row['updatedAt'] = r['observedAt']
        protected_equal(old_row, row, set(old_row) - {'title', 'updatedAt', 'metadataRefresh', 'thumbnailRefresh'}, vid + '/worklist')
    file_versions[WORKLIST] = (before_bytes, output_bytes(new_work, before_bytes))
    own_changes.append({'file': WORKLIST, 'rowAnchors': {str(i): r.get('slug') for i, r in enumerate(old_work['rows'])}, 'operations': difference(old_work, new_work)})

    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    bundle = TASK / 'record-merge-bundles' / stamp
    bundle.mkdir(parents=True)
    head_code, head_data, _ = git('rev-parse', 'HEAD')
    assert head_code == 0
    manifest = {'changeId': CHANGE_ID, 'preparedAt': now, 'mode': 'apply' if args.apply else 'dry-run', 'head': head_data.decode().strip(), 'files': [], 'humanReviewFlagsUnchanged': True, 'schedulePrivacyAndRightsUnchanged': True, 'noPlatformActions': True, 'noGitMutation': True, 'outerWildsHeldPrivate': True, 'oldBloomExcluded': True}
    for rel, (before, after) in file_versions.items():
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
        code, idx, _ = git('ls-files', '--stage', '--', rel)
        assert code == 0
        entry['semanticIndexEntry'] = idx.decode('utf-8').strip()
        manifest['files'].append(entry)
    (bundle / 'own-changes.json').write_bytes(output_bytes(own_changes))
    (bundle / 'manifest.json').write_bytes(output_bytes(manifest))
    if args.apply:
        for rel, (before, _) in file_versions.items():
            assert (REPO / rel).read_bytes() == before, f'Concurrent modification: {rel}'
        for rel, (_, after) in file_versions.items():
            path = REPO / rel
            temporary = path.with_name(path.name + '.readability-20261028.tmp')
            assert not temporary.exists(), f'Temporary file exists: {temporary}'
            temporary.write_bytes(after)
            os.replace(temporary, path)
    print(json.dumps({'mode': manifest['mode'], 'bundle': str(bundle), 'selectedReceiptCount': 14, 'schedulesPreserved': 13, 'heldPrivate': OW, 'changedFileCount': len(file_versions), 'repoWritten': args.apply}, ensure_ascii=False))


if __name__ == '__main__':
    main()
