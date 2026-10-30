"""Prepare a selective D25/D29 publishing commit, preserving foreign staging.

Default: read-only Git plan. --apply-shared applies only explicit spec overlays
to four shared working files (no Git). --execute commits via isolated indices;
--push is separately required. Never use directory-wide git add or reset.
The exact-path spec must be refreshed if platform facts change before execution.
"""
from pathlib import Path, PurePosixPath
import argparse, copy, hashlib, json, os, re, struct, subprocess, sys, uuid

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'production/batches/design-25-30-review-actions-20261029'))
from scoped_json import load, patch, upsert

HOME = 'projects/kind-to-beginners/publishing/botw-v4/'
W = 'shared/publishing/video-worklist.json'
D = 'docs/VIDEO_WORKLIST.md'
I = 'shared/git-essential-images.json'
G = '.gitignore'
SHARED = {W, D, I, G}
ROOTS = ('projects/limited-color-world/publishing/clarity-v3/', HOME,
         'projects/limited-color-world/publishing/upload-20261030/',
         'projects/kind-to-beginners/publishing/upload-20261030/')
SLUGS = {'D25': 'limited-color-world', 'D29': 'kind-to-beginners'}
THUMBS = {f'projects/{slug}/publishing/upload-20261030/thumbnail-v1.png' for slug in SLUGS.values()}
ROW_FIELDS = {'reviewStatus', 'humanApproval', 'platformStatus', 'videoId', 'url',
              'executionStatus', 'updatedAt', 'revisionInProduction', 'youtubeUpload'}

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
    assert any(name.startswith(prefix) for prefix in ROOTS), ('Outside publishing scope', name)
    assert len(pure.parts) == 5, ('Only exact top-level publishing artifacts allowed', name)
    assert name in THUMBS or pure.suffix in {'.json', '.txt', '.py'}
    file = ROOT / name
    assert file.is_file() and file.resolve().is_relative_to(ROOT.resolve())

def at(value, path):
    for key in path:
        if not isinstance(value, dict) or key not in value:
            return False, None
        value = value[key]
    return True, value

def markdown_rows(raw):
    found = {}
    for line in raw.decode('utf-8-sig').splitlines(keepends=True):
        for identity in SLUGS:
            kind = ('series' if line.startswith('| ' + identity + ' | ') else
                    'order' if re.match(r'^\| \d+ \| 게임디자인 \| ' + identity + r' ', line) else None)
            if kind:
                assert (identity, kind) not in found
                found[identity, kind] = line
    assert len(found) == 4, ('Expected two table rows per selected video', len(found))
    return found

def overlay(name, raw, spec):
    if name == W:
        for item in spec['rows']:
            identity = item['id']; assert identity in SLUGS
            rows = load(raw)['rows']
            indices = [n for n, row in enumerate(rows) if row['id'] == identity]
            assert len(indices) == 1
            n = indices[0]; assert rows[n]['slug'] == SLUGS[identity]
            for change in item['changes']:
                path = change['path']
                assert path and path[0] in ROW_FIELDS
                assert path[0] != 'revisionInProduction' or path[1:] in [
                    ['privateUploadAuthorized'], ['status'], ['updatedAt']]
                exists, current = at(load(raw)['rows'][n], path)
                assert (exists == change['expectedExists'] and current == change['expected']) or (
                    exists and current == change['value']), ('Concurrent row edit', identity, path)
                raw = patch(raw, ['rows', n, *path], copy.deepcopy(change['value']))
            evidence = load(raw)['rows'][n].get('evidence', [])
            for link in item.get('appendEvidence', []):
                assert link == f"projects/{SLUGS[identity]}/publishing/{item['revision']}/youtube-upload.json"
                if link not in evidence:
                    evidence.append(link)
            raw = patch(raw, ['rows', n, 'evidence'], evidence)
        return raw
    if name == D:
        rows = markdown_rows(raw); replacement = {}
        for item in spec['markdownCells']:
            key = item['id'], item['kind']; line = rows[key]
            assert key[0] in SLUGS
            cols = replacement.get(line, line).rstrip('\r\n').split('|')
            index = item['column']
            assert index in ([4, 5] if key[1] == 'order' else [4, 5])
            assert cols[index] in [item['expected'], item['value']], ('Concurrent markdown edit', key, index)
            cols[index] = item['value']
            replacement[line] = '|'.join(cols) + ('\r\n' if line.endswith('\r\n') else '\n' if line.endswith('\n') else '')
        text = ''.join(replacement.get(line, line) for line in raw.decode('utf-8-sig').splitlines(keepends=True))
        return (b'\xef\xbb\xbf' if raw.startswith(b'\xef\xbb\xbf') else b'') + text.encode('utf-8')
    if name == I:
        for entry in spec['essentialImages']:
            assert entry['path'] in THUMBS and entry['purpose'] == 'delivery-thumbnail'
            existing = [x for x in load(raw)['entries'] if x['path'] == entry['path']]
            assert not existing or existing == [entry], 'Conflicting thumbnail registry entry'
            raw = upsert(raw, 'entries', 'path', entry)
        return raw
    if name == G:
        newline = b'\r\n' if b'\r\n' in raw else b'\n'
        for name in sorted(THUMBS):
            lines = raw.decode('utf-8-sig').splitlines()
            if '!' + name not in lines and '!/' + name not in lines:
                raw += (b'' if raw.endswith(b'\n') else newline) + ('!/' + name).encode() + newline
        return raw
    raise AssertionError(name)

def validate(spec):
    assert spec['scope'] == 'D25-D29-upload-20261030'
    assert {x['id'] for x in spec['rows']} == set(SLUGS)
    assert {x['path'] for x in spec['essentialImages']} == THUMBS
    paths = spec['ownedPaths']
    assert paths and len(paths) == len(set(paths)) and THUMBS <= set(paths)
    for name in paths:
        owned_path(name)
    for entry in spec['essentialImages']:
        name = entry['path']; pixels = (ROOT / name).read_bytes()
        review = load((ROOT / Path(name).parent / 'thumbnail-review.json').read_bytes())
        assert pixels[:8] == b'\x89PNG\r\n\x1a\n' and struct.unpack('>II', pixels[16:24]) == (1280, 720)
        assert len(pixels) < 2 * 1024 * 1024
        assert sha(pixels) == entry['sha256'] == review['finalSha256']
        assert review['visualReview']['result'] == 'pass' and review['visualReview']['mobile375ActuallyViewed']
    for item in spec['rows']:
        receipt = load((ROOT / f"projects/{SLUGS[item['id']]}/publishing/{item['revision']}/youtube-upload.json").read_bytes())
        changes = {tuple(x['path']): x['value'] for x in item['changes']}
        assert receipt['videoId'] == changes[('videoId',)]
        assert receipt['status'] == changes[('youtubeUpload',)]['status'], 'Refresh spec after platform facts change'
    return sorted(paths) + sorted(SHARED)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--spec', default=str(ROOT / HOME / 'publishing-commit-spec.json'))
    parser.add_argument('--apply-shared', action='store_true', help='Only explicit working-tree shared overlays; no Git')
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--push', action='store_true')
    parser.add_argument('--message', default='Record D25 and D29 YouTube uploads and reviewed thumbnails')
    args = parser.parse_args()
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
            'paths': paths, 'indexSha256': sha(original_index), 'sharedScope': 'Two explicit rows/four table rows; two thumbnail entries/exceptions',
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
        git('update-ref', '-m', 'commit: D25 D29 publishing', branch, commit, base); moved = True
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
