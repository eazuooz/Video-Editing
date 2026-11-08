"""AI2D room-v3 publishing-only commit adapter.

Draft prepared without running Git or applying shared changes.
--print-schema is read-only. Default invocation prints an isolated-index plan.
--apply-shared applies only the explicit reviewed overlays, without Git.
--execute commits through isolated indices; --push must be separately selected.
The receipt and spec must be refreshed after actual browser-observed facts.
"""
from pathlib import Path, PurePosixPath
import argparse, copy, hashlib, json, os, re, struct, subprocess, sys, uuid

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'production/batches/design-25-30-review-actions-20261029'))
from scoped_json import load, patch, upsert

HOME = 'projects/ai-2d-game-assets/publishing/room-v3-upload-20261108/'
P = 'projects/ai-2d-game-assets/project.json'
K = 'projects/ai-2d-game-assets/production/room-v3/checkpoint.json'
C = 'shared/publishing/video-production-control.json'
W = 'shared/publishing/video-worklist.json'
D = 'docs/VIDEO_WORKLIST.md'
I = 'shared/git-essential-images.json'
G = '.gitignore'
SHARED = {P, K, C, W, D, I, G}
THUMB = HOME + 'thumbnail-v1.png'
AUTHORIZATION = HOME + 'authorization.json'
RECEIPT = HOME + 'youtube-upload.json'
CONTROL_KEY = 'ai2dUpload20261108'
SLUG = 'ai-2d-game-assets'
ROW_ID = 'S-AI2D'
MASTER_SHA = '8e5fc1902c8c1ade2637769a496c613a5bb45d45758ca14eb94c7b345c6a3d1c'
DURATION = 1231.4
ROW_FIELDS = {'reviewStatus', 'humanApproval', 'platformStatus', 'videoId', 'url',
              'executionStatus', 'updatedAt', 'youtubeUpload'}
CHECKPOINT_PATHS = {
    ('updatedAt',), ('stage',), ('humanReview',), ('youtubeAuthorized',),
    ('next',), ('youtubeUpload',), ('delivery', 'userReview'),
    ('delivery', 'youtubeUploaded'), ('delivery', 'youtubeUpload')
}
CONTROL_EXTRA_FIELDS = {'videoId', 'url', 'watchUrl', 'studioUrl', 'receipt',
                        'uploadedAt', 'updatedAt', 'youtubeUpload', 'privateSaved',
                        'checks', 'settings', 'uploadFacts'}

# Explicit expected states permit the same bounded overlay against HEAD, the
# current index, and the working tree when the initial authorization is not yet
# committed. Each state must be captured exactly; no wildcard exists.
SPEC_SCHEMA = {
    '$schema': 'https://json-schema.org/draft/2020-12/schema',
    'title': 'AI2D room-v3 observed-private-upload selective commit',
    'type': 'object',
    'additionalProperties': False,
    'required': ['schemaVersion', 'scope', 'ownedPaths', 'receiptSha256',
                 'uploadFacts', 'projectDurationChange', 'checkpointChanges',
                 'controlRecord', 'rowChanges', 'appendEvidence',
                 'markdownCells', 'essentialImage'],
    'properties': {
        'schemaVersion': {'const': 1},
        'scope': {'const': 'ai2d-room-v3-upload-20261108'},
        'ownedPaths': {'type': 'array', 'minItems': 1, 'uniqueItems': True,
                       'items': {'type': 'string'},
                       'description': 'Exact existing top-level files under this publishing folder. No directories, source media, other projects or local QA.'},
        'receiptSha256': {'type': 'string', 'pattern': '^[a-f0-9]{64}$'},
        'uploadFacts': {
            'type': 'object', 'additionalProperties': False,
            'required': ['videoId', 'status', 'privacy', 'captionedMasterSha256',
                         'observedAt', 'studioUrl', 'watchUrl'],
            'properties': {
                'videoId': {'type': 'string', 'pattern': '^[A-Za-z0-9_-]{11}$'},
                'status': {'type': 'string', 'minLength': 1},
                'privacy': {'const': 'private'},
                'captionedMasterSha256': {'const': MASTER_SHA},
                'observedAt': {'type': 'string', 'minLength': 1},
                'studioUrl': {'type': 'string'},
                'watchUrl': {'type': 'string'}
            },
            'description': 'Must equal same-named fields in actual youtube-upload.json. Observed upload/processing/settings incompleteness must remain explicit.'
        },
        'projectDurationChange': {'$ref': '#/$defs/change',
                                  'description': 'Only path [video,durationSeconds], value 1231.4. Do not edit currentRevision, branding or outro duration.'},
        'checkpointChanges': {'type': 'array', 'items': {'$ref': '#/$defs/change'}},
        'controlRecord': {'$ref': '#/$defs/change',
                          'description': 'Whole ai2dUpload20261108 record only; all authorization.json fields except status must be retained exactly, and only upload-result fields may be added.'},
        'rowChanges': {'type': 'array', 'items': {'$ref': '#/$defs/change'},
                       'description': 'Paths relative to the S-AI2D row. Only publishing-status fields are allowed.'},
        'appendEvidence': {'type': 'array', 'uniqueItems': True,
                           'items': {'const': RECEIPT}},
        'markdownCells': {'type': 'array', 'items': {
            'type': 'object', 'additionalProperties': False,
            'required': ['column', 'expected', 'value'],
            'properties': {'column': {'enum': [4, 5]},
                           'expected': {'type': 'string'}, 'value': {'type': 'string'}}
        }, 'description': 'Only review and platform cells of | S-AI2D |. Exact cell strings include their spaces.'},
        'essentialImage': {'type': 'object',
                           'required': ['path', 'purpose', 'reason', 'sha256', 'reviewedAt', 'project'],
                           'properties': {'path': {'const': THUMB},
                                          'purpose': {'const': 'delivery-thumbnail'},
                                          'reason': {'type': 'string'},
                                          'sha256': {'type': 'string', 'pattern': '^[a-f0-9]{64}$'},
                                          'reviewedAt': {'type': 'string'},
                                          'project': {'const': SLUG}},
                           'additionalProperties': False}
    },
    '$defs': {
        'change': {'type': 'object', 'additionalProperties': False,
                   'required': ['path', 'expectedStates', 'value'],
                   'properties': {
                       'path': {'type': 'array', 'minItems': 1,
                                'items': {'type': 'string'}},
                       'expectedStates': {'type': 'array', 'minItems': 1, 'maxItems': 3,
                                          'items': {'type': 'object',
                                                    'required': ['exists', 'value'],
                                                    'properties': {'exists': {'type': 'boolean'}, 'value': {}},
                                                    'additionalProperties': False}},
                       'value': {}
                   }}
    }
}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def git(*args, env=None, data=None, optional=False):
    merged = os.environ.copy()
    merged['GIT_OPTIONAL_LOCKS'] = '0'
    if env:
        merged.update(env)
    result = subprocess.run(['git', *args], cwd=ROOT, env=merged, input=data,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode:
        if optional:
            return None
        raise RuntimeError((result.stdout + result.stderr).decode('utf-8', 'replace')[:6000])
    return result.stdout


def owned_path(name):
    assert isinstance(name, str) and not any(c in name for c in '\\\x00\n\r')
    pure = PurePosixPath(name)
    assert not pure.is_absolute() and '..' not in pure.parts and str(pure) == name
    assert name.startswith(HOME) and len(pure.parts) == 5, ('Outside publishing scope', name)
    assert name == THUMB or pure.suffix in {'.json', '.txt', '.py', '.md'}
    file = ROOT / name
    assert file.is_file() and file.resolve().is_relative_to(ROOT.resolve())


def at(value, path):
    for key in path:
        if not isinstance(value, dict) or key not in value:
            return False, None
        value = value[key]
    return True, value


def validate_change(change):
    assert set(change) == {'path', 'expectedStates', 'value'}
    assert change['path'] and all(isinstance(x, str) for x in change['path'])
    assert 1 <= len(change['expectedStates']) <= 3
    for state in change['expectedStates']:
        assert set(state) == {'exists', 'value'} and isinstance(state['exists'], bool)
        assert state['exists'] or state['value'] is None


def changed(raw, path, change):
    exists, current = at(load(raw), path)
    if exists and current == change['value']:
        return raw
    assert {'exists': exists, 'value': current} in change['expectedStates'], (
        'Concurrent scoped value edit; refresh exact HEAD/index/work expected states', path)
    return patch(raw, path, copy.deepcopy(change['value']))


def markdown_row(raw):
    rows = [line for line in raw.decode('utf-8-sig').splitlines(keepends=True)
            if line.startswith('| ' + ROW_ID + ' | ')]
    assert len(rows) == 1, ('Expected one AI2D table row', len(rows))
    assert len(rows[0].rstrip('\r\n').split('|')) == 7
    return rows[0]


def overlay(name, raw, spec):
    if name == P:
        ch = spec['projectDurationChange']
        return changed(raw, ch['path'], ch)
    if name == K:
        for ch in spec['checkpointChanges']:
            raw = changed(raw, ch['path'], ch)
        return raw
    if name == C:
        ch = spec['controlRecord']
        return changed(raw, [CONTROL_KEY], ch)
    if name == W:
        rows = load(raw)['rows']
        indices = [n for n, row in enumerate(rows)
                   if row.get('id') == ROW_ID and row.get('slug') == SLUG]
        assert len(indices) == 1
        n = indices[0]
        for ch in spec['rowChanges']:
            raw = changed(raw, ['rows', n, *ch['path']], ch)
        if spec['appendEvidence']:
            evidence = load(raw)['rows'][n].get('evidence', [])
            assert isinstance(evidence, list)
            for link in spec['appendEvidence']:
                if link not in evidence:
                    evidence.append(link)
            raw = patch(raw, ['rows', n, 'evidence'], evidence)
        return raw
    if name == D:
        line = markdown_row(raw)
        cols = line.rstrip('\r\n').split('|')
        for item in spec['markdownCells']:
            index = item['column']
            assert cols[index] in [item['expected'], item['value']], (
                'Concurrent AI2D markdown status edit', index)
            assert not any(c in item['value'] for c in '|\n\r')
            cols[index] = item['value']
        replacement = '|'.join(cols) + (
            '\r\n' if line.endswith('\r\n') else '\n' if line.endswith('\n') else '')
        text = raw.decode('utf-8-sig')
        assert text.count(line) == 1
        return (b'\xef\xbb\xbf' if raw.startswith(b'\xef\xbb\xbf') else b'') + text.replace(
            line, replacement, 1).encode('utf-8')
    if name == I:
        entry = spec['essentialImage']
        existing = [x for x in load(raw)['entries'] if x['path'] == THUMB]
        assert not existing or existing == [entry], 'Conflicting thumbnail registry entry'
        return upsert(raw, 'entries', 'path', entry)
    if name == G:
        lines = raw.decode('utf-8-sig').splitlines()
        if '!' + THUMB in lines or '!/' + THUMB in lines:
            return raw
        newline = b'\r\n' if b'\r\n' in raw else b'\n'
        return raw + (b'' if raw.endswith(b'\n') else newline) + (
            '!/' + THUMB).encode('utf-8') + newline
    raise AssertionError(name)


def validate(spec):
    assert set(spec) == set(SPEC_SCHEMA['required'])
    assert spec['schemaVersion'] == 1 and spec['scope'] == 'ai2d-room-v3-upload-20261108'
    auth = load((ROOT / AUTHORIZATION).read_bytes())
    assert auth['youtubeAuthorized'] is True and auth['privacy'] == 'private'
    for key in ['publicPublicationAuthorized', 'schedulingAuthorized',
                'deletePreviousUploads', 'newVideoRenderAuthorized']:
        assert auth[key] is False
    assert auth['captionedMasterSha256'] == MASTER_SHA
    paths = spec['ownedPaths']
    assert paths and len(paths) == len(set(paths))
    assert {THUMB, AUTHORIZATION, RECEIPT, HOME + 'scoped_commit.py'} <= set(paths)
    for name in paths:
        owned_path(name)
    receipt_raw = (ROOT / RECEIPT).read_bytes()
    assert sha(receipt_raw) == spec['receiptSha256'], 'Refresh spec after platform facts change'
    receipt = load(receipt_raw)
    facts = spec['uploadFacts']
    assert set(facts) == set(SPEC_SCHEMA['properties']['uploadFacts']['required'])
    assert all(receipt.get(key) == value for key, value in facts.items())
    assert re.fullmatch(r'[A-Za-z0-9_-]{11}', facts['videoId'])
    assert facts['privacy'] == 'private' and facts['captionedMasterSha256'] == MASTER_SHA
    assert facts['studioUrl'] == 'https://studio.youtube.com/video/' + facts['videoId'] + '/edit'
    assert facts['watchUrl'] == 'https://www.youtube.com/watch?v=' + facts['videoId']
    assert facts['observedAt'] and facts['status'] and 'TBD' not in facts['status']
    assert receipt.get('publicPublication') in [None, False]
    assert receipt.get('scheduled') in [None, False]
    duration = spec['projectDurationChange']
    validate_change(duration)
    assert duration['path'] == ['video', 'durationSeconds'] and duration['value'] == DURATION
    checkpoint = load((ROOT / K).read_bytes())
    assert checkpoint['masterSha256'] == MASTER_SHA
    assert abs(checkpoint['delivery']['duration'] - DURATION) < 0.001
    for ch in spec['checkpointChanges']:
        validate_change(ch)
        assert tuple(ch['path']) in CHECKPOINT_PATHS, ('Non-upload checkpoint change', ch['path'])
    record = spec['controlRecord']
    validate_change(record)
    assert record['path'] == [CONTROL_KEY] and isinstance(record['value'], dict)
    assert all(record['value'].get(key) == value for key, value in auth.items() if key != 'status')
    assert set(record['value']) - set(auth) <= CONTROL_EXTRA_FIELDS
    assert record['value'].get('videoId') == facts['videoId']
    assert record['value'].get('status') == facts['status']
    assert spec['rowChanges'] and len({tuple(x['path']) for x in spec['rowChanges']}) == len(spec['rowChanges'])
    for ch in spec['rowChanges']:
        validate_change(ch)
        assert len(ch['path']) == 1 and ch['path'][0] in ROW_FIELDS
    row_values = {tuple(ch['path']): ch['value'] for ch in spec['rowChanges']}
    assert row_values.get(('videoId',)) == facts['videoId']
    assert row_values.get(('url',)) == facts['watchUrl']
    if ('youtubeUpload',) in row_values:
        upload = row_values['youtubeUpload',]
        assert isinstance(upload, dict) and upload.get('videoId') == facts['videoId']
        assert upload.get('status') == facts['status']
    assert set(spec['appendEvidence']) <= {RECEIPT}
    assert 1 <= len(spec['markdownCells']) <= 2
    assert len({x['column'] for x in spec['markdownCells']}) == len(spec['markdownCells'])
    for item in spec['markdownCells']:
        assert set(item) == {'column', 'expected', 'value'} and item['column'] in [4, 5]
        assert isinstance(item['expected'], str) and isinstance(item['value'], str)
    entry = spec['essentialImage']
    assert set(entry) == set(SPEC_SCHEMA['properties']['essentialImage']['required'])
    assert entry['path'] == THUMB and entry['purpose'] == 'delivery-thumbnail' and entry['project'] == SLUG
    pixels = (ROOT / THUMB).read_bytes()
    review = load((ROOT / HOME / 'thumbnail-v1.qa.json').read_bytes())
    assert pixels[:8] == b'\x89PNG\r\n\x1a\n' and struct.unpack('>II', pixels[16:24]) == (1280, 720)
    assert len(pixels) < 2 * 1024 * 1024
    assert sha(pixels) == entry['sha256'] == review['finalSha256']
    assert review['status'] == 'ready-for-parent-upload' and review['textChecks']['readableAt375'] is True
    return sorted(paths) + sorted(SHARED)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--print-schema', action='store_true', help='Print JSON schema only; no files or Git are changed')
    parser.add_argument('--spec', default=str(ROOT / HOME / 'publishing-commit-spec.json'))
    parser.add_argument('--apply-shared', action='store_true', help='Only bounded publishing overlays in seven working-tree files; no Git')
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--push', action='store_true')
    parser.add_argument('--message', default='Record AI2D room-v3 private upload and reviewed thumbnail')
    args = parser.parse_args()
    if args.print_schema:
        assert not (args.apply_shared or args.execute or args.push)
        print(json.dumps(SPEC_SCHEMA, ensure_ascii=False, indent=2))
        return
    assert not args.push or args.execute
    assert not (args.apply_shared and (args.execute or args.push))
    spec_path = Path(args.spec); spec_raw = spec_path.read_bytes(); spec = load(spec_raw)
    paths = validate(spec)
    work = {name: (ROOT / name).read_bytes() for name in paths}
    proposed_shared = {name: overlay(name, work[name], spec) for name in SHARED}
    if args.apply_shared:
        # Checks for all files precede any write. This mode never touches Git.
        assert spec_path.read_bytes() == spec_raw
        assert all((ROOT / name).read_bytes() == raw for name, raw in work.items())
        for name, raw in proposed_shared.items():
            if raw != work[name]:
                assert (ROOT / name).read_bytes() == work[name]
                (ROOT / name).write_bytes(raw)
        print(json.dumps({'status': 'explicit-shared-overlays-applied', 'gitTouched': False}, ensure_ascii=False))
        return
    base = git('rev-parse', 'HEAD').strip().decode()
    branch = git('symbolic-ref', '--quiet', 'HEAD').strip().decode()
    assert branch.startswith('refs/heads/codex/')
    index = Path(git('rev-parse', '--git-path', 'index').strip().decode())
    if not index.is_absolute(): index = ROOT / index
    original_index = index.read_bytes()
    heads = {name: git('show', base + ':' + name) for name in SHARED}
    indexed = {name: git('show', ':' + name) for name in SHARED}
    assert index.read_bytes() == original_index
    committed = {name: overlay(name, heads[name], spec) if name in SHARED else work[name] for name in paths}
    synced = {name: overlay(name, indexed[name], spec) if name in SHARED else work[name] for name in paths}
    plan = {'mode': 'execute' if args.execute else 'read-only-plan', 'base': base, 'branch': branch,
            'paths': paths, 'indexSha256': sha(original_index), 'sharedScope': 'Only video.durationSeconds=1231.4, room-v3 upload facts, ai2dUpload20261108, S-AI2D publishing cells, and one thumbnail registry/ignore entry',
            'unrelatedStagingPreserved': True, 'workingSourcesRewrittenByCommit': False, 'pushRequested': args.push}
    if not args.execute:
        print(json.dumps(plan, ensure_ascii=False, indent=2)); return
    assert all(work[name] == proposed_shared[name] for name in SHARED), 'Apply the reviewed shared overlays first with --apply-shared'
    git_dir = Path(git('rev-parse', '--absolute-git-dir').strip().decode())
    run = git_dir / 'scoped-publishing' / uuid.uuid4().hex
    run.mkdir(parents=True)
    (run / 'index-before.backup').write_bytes(original_index)
    (run / 'plan.json').write_text(json.dumps(plan, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    commit_env = {'GIT_INDEX_FILE': str(run / 'commit-index')}
    sync_env = {'GIT_INDEX_FILE': str(run / 'sync-index')}
    old_env = {'GIT_INDEX_FILE': str(run / 'index-before.backup')}
    git('read-tree', base, env=commit_env)
    (run / 'sync-index').write_bytes(original_index)
    owned = {name.encode() for name in paths}
    def foreign(env):
        return {flag: b'\0'.join(x for x in git('ls-files', flag, '-z', env=env).split(b'\0') if x and
                (x.split(b'\t', 1)[-1] if flag == '--stage' else x[2:]) not in owned)
                for flag in ['--stage', '-v']}
    foreign_before = foreign(old_env)
    # Non-shared text respects repository clean filters; shared lexical bytes are
    # deliberately kept exact so unrelated staged edits retain their content.
    objects = {}
    for name in paths:
        for values in (committed, synced):
            args_hash = ['hash-object', '-w'] + ([] if name in SHARED else ['--path=' + name]) + ['--stdin']
            object_id = git(*args_hash, data=values[name]).strip().decode()
            values[name] = git('cat-file', 'blob', object_id)
            objects[name, sha(values[name])] = object_id
    head_modes = {x.split(b'\t', 1)[1].decode(): x.split()[0].decode() for x in git('ls-tree', '-r', '-z', base).split(b'\0') if x}
    staged_entries = [x for x in git('ls-files', '--stage', '-z', env=old_env).split(b'\0') if x]
    for item in staged_entries:
        if item.split(b'\t', 1)[1] in owned: assert item.split(b'\t', 1)[0].split()[2] == b'0', 'Owned merge conflict'
    index_modes = {x.split(b'\t', 1)[1].decode(): x.split()[0].decode() for x in staged_entries}
    for values, env, modes in ((committed, commit_env, head_modes), (synced, sync_env, index_modes)):
        payload = b''.join((modes.get(name, '100644') + ' ' + objects[name, sha(raw)] + '\t' + name).encode() + b'\0' for name, raw in values.items())
        git('update-index', '-z', '--index-info', env=env, data=payload)
    assert foreign(sync_env) == foreign_before
    git('-c', 'core.whitespace=trailing-space,space-before-tab,cr-at-eol', 'diff', '--cached', '--check', base, env=commit_env)
    policy_env = os.environ.copy(); policy_env.update(commit_env); policy_env['GIT_OPTIONAL_LOCKS'] = '0'
    subprocess.run(['node', 'scripts/media-policy.cjs'], cwd=ROOT, env=policy_env, check=True)
    changed = git('diff', '--cached', '--name-only', base, env=commit_env).decode().splitlines()
    assert changed and set(changed) <= set(paths)
    def stable():
        assert index.read_bytes() == original_index and git('rev-parse', 'HEAD').strip().decode() == base
        assert git('symbolic-ref', '--quiet', 'HEAD').strip().decode() == branch
        assert spec_path.read_bytes() == spec_raw
        assert all((ROOT / name).read_bytes() == raw for name, raw in work.items()), 'Concurrent source/shared edits'
    stable()
    tree = git('write-tree', env=commit_env).strip().decode()
    commit = git('commit-tree', tree, '-p', base, data=(args.message + '\n').encode()).strip().decode()
    lock = Path(str(index) + '.lock'); fd = None; lock_owned = False; moved = False
    try:
        fd = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, 'O_BINARY', 0), 0o666)
        lock_owned = True; stable()
        payload = (run / 'sync-index').read_bytes()
        with os.fdopen(fd, 'wb') as stream:
            fd = None; assert stream.write(payload) == len(payload); stream.flush(); os.fsync(stream.fileno())
        git('update-ref', '-m', 'commit: AI2D room-v3 private publishing', branch, commit, base); moved = True
        os.replace(lock, index)
    except Exception:
        if fd is not None: os.close(fd)
        if lock_owned and lock.exists(): lock.unlink()
        (run / 'interrupted.json').write_text(json.dumps({'commit': commit, 'refUpdated': moved, 'indexBackup': str(run / 'index-before.backup')}), encoding='utf-8')
        raise
    assert foreign(None) == foreign_before
    assert all((ROOT / name).read_bytes() == raw for name, raw in work.items())
    for name in SHARED: assert git('show', ':' + name) == synced[name]
    receipt = {'status': 'committed-not-pushed', 'base': base, 'commit': commit, 'paths': changed,
               'foreignIndexPreserved': True, 'unrelatedSharedBytesPreserved': True, 'workingSourcesUnchanged': True,
               'backupDirectory': str(run)}
    if args.push:
        git('push', 'origin', commit + ':' + branch)
        remote = git('ls-remote', '--heads', 'origin', branch).decode().split()[0]
        git('merge-base', '--is-ancestor', commit, remote)
        receipt.update(status='committed-and-pushed', remoteSha=remote)
    (run / 'receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(receipt, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
