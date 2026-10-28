"""Prepare/commit only the selected publishing-record JSON changes.

Usage:
  python commit-own-publishing-records.py --bundle <record-merge-bundle>
  python commit-own-publishing-records.py --bundle <record-merge-bundle> --commit

The default prepares a C:-local review only. --commit creates an isolated commit
and reconciles only these changes into the real index, preserving foreign index
entries and flags. No push, working-tree edit, platform action or media staging.
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
REPO = Path('D:/Github/VideoEditing').resolve()
WORKLIST = 'shared/publishing/shorts-worklist.json'
NEW_PREFIX = 'production/batches/shorts-title-readability-20261028/'
TEXT_SUFFIXES = {'.json', '.md', '.txt', '.py', '.js', '.cjs'}
MISSING = object()


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def encode(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def run_git(*args, env=None, data=None, required=True):
    p = subprocess.run(['git', '-c', 'gc.auto=0', '-c', 'maintenance.auto=false', *args], cwd=REPO, env=env, input=data, capture_output=True)
    if required and p.returncode:
        raise RuntimeError((p.stdout + p.stderr).decode('utf-8', errors='replace'))
    return p


def git(*args, **kwargs):
    return run_git(*args, **kwargs).stdout


def unescape(token):
    return token.replace('~1', '/').replace('~0', '~')


def remap_pointer(op_path, document, change):
    assert op_path.startswith('/'), 'Root document replacement is forbidden'
    parts = [unescape(x) for x in op_path[1:].split('/')]
    if change['file'] == WORKLIST:
        # The worklist root and foreign rows may have changed since planning.
        assert len(parts) >= 3 and parts[0] == 'rows', f'Worklist operation outside selected rows: {op_path}'
        slug = change['rowAnchors'][parts[1]]
        matches = [i for i, row in enumerate(document['rows']) if row.get('slug') == slug]
        assert len(matches) == 1, f'{slug}: cannot resolve worklist row'
        parts[1] = str(matches[0])
    return parts


def apply_operations(base, change):
    value = copy.deepcopy(base)
    for op in change['operations']:
        parts = remap_pointer(op['path'], value, change)
        parent = value
        for part in parts[:-1]:
            parent = parent[int(part)] if isinstance(parent, list) else parent[part]
        key = int(parts[-1]) if isinstance(parent, list) else parts[-1]
        current = parent[key] if isinstance(parent, list) else parent.get(key, MISSING)
        kind = op['op']
        if kind == 'add':
            if current is not MISSING:
                assert current == op['value'], f"Conflicting existing value {change['file']}{op['path']}"
            else:
                parent[key] = copy.deepcopy(op['value'])
        elif kind == 'replace':
            assert current == op['before'] or current == op['value'], f"Concurrent/base conflict {change['file']}{op['path']}"
            parent[key] = copy.deepcopy(op['value'])
        elif kind == 'remove':
            if current is not MISSING:
                assert current == op['before'], f"Concurrent removal conflict {change['file']}{op['path']}"
                del parent[key]
        else:
            raise AssertionError(f'Unsupported JSON operation: {kind}')
    return value


def index_entries(env=None):
    entries = {}
    for line in git('ls-files', '--stage', '-z', env=env).split(b'\0'):
        if not line:
            continue
        meta, path = line.split(b'\t', 1)
        mode, obj, stage = meta.split()
        entries[(path.decode('utf-8'), int(stage))] = (mode.decode(), obj.decode())
    return entries


def index_flags(env=None):
    # -v includes assume-unchanged/skip-worktree state; preserved foreign bytes
    # are compared separately from mode/blob/stage entries.
    result = {}
    for line in git('ls-files', '-v', '-z', env=env).split(b'\0'):
        if line:
            result[line[2:].decode('utf-8')] = line[:1].decode()
    return result


def blob_at(spec):
    p = run_git('show', spec, required=False)
    return p.stdout if p.returncode == 0 else None


def safe_temp_remove(path, git_dir):
    assert path.parent.resolve() == git_dir and path.name.startswith('index.shorts-readability-20261028-')
    if path.exists():
        path.unlink()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--bundle', type=Path, required=True)
    ap.add_argument('--commit', action='store_true')
    ap.add_argument('--message', default='Improve fourteen Shorts titles and thumbnail readability')
    args = ap.parse_args()
    bundle = args.bundle.resolve()
    assert bundle.is_relative_to(TASK / 'record-merge-bundles'), 'Unexpected review bundle location'
    manifest = read_json(bundle / 'manifest.json')
    changes = read_json(bundle / 'own-changes.json')
    audit = read_json(TASK / 'assets-audit.json')
    selected = {f"projects/{x['slug']}/publishing/youtube-upload.json" for x in audit['items']} | {WORKLIST}
    assert len(selected) == 15 and {x['file'] for x in changes} == selected
    assert len(changes) == 15
    entries_by_path = {x['path']: x for x in manifest['files']}
    assert set(entries_by_path) == selected
    head = git('rev-parse', 'HEAD').decode().strip()
    branch = git('symbolic-ref', '-q', 'HEAD').decode().strip()
    assert branch.startswith('refs/heads/'), 'Detached HEAD requires explicit handling'
    index_path = Path(git('rev-parse', '--git-path', 'index').decode().strip())
    if not index_path.is_absolute():
        index_path = (REPO / index_path).resolve()
    git_dir = index_path.parent.resolve()
    assert git_dir == (REPO / '.git').resolve(), 'Unexpected Git index directory'
    assert not index_path.with_name('index.lock').exists(), 'Existing index.lock must be left untouched'
    original_index = index_path.read_bytes()
    before_entries = index_entries()
    before_flags = index_flags()
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    review = TASK / 'commit-review-bundles' / stamp
    review.mkdir(parents=True)
    (review / 'index-before.bin').write_bytes(original_index)
    merged_head, merged_index, expected_work = {}, {}, {}
    modes = {}
    for change in changes:
        rel = change['file']
        working = (REPO / rel).read_bytes()
        assert sha(working) == entries_by_path[rel]['afterSHA256'], f'Working file changed since record merge: {rel}'
        expected_work[rel] = working
        head_bytes = blob_at(f'{head}:{rel}')
        assert head_bytes is not None, f'Selected tracked file missing from HEAD: {rel}'
        assert (rel, 0) in before_entries and not any(p == rel and stage != 0 for p, stage in before_entries), f'Unmerged/missing selected index entry: {rel}'
        mode, oid = before_entries[(rel, 0)]
        modes[rel] = mode
        idx_bytes = git('cat-file', 'blob', oid)
        merged_head[rel] = encode(apply_operations(json.loads(head_bytes.decode('utf-8-sig')), change))
        merged_index[rel] = encode(apply_operations(json.loads(idx_bytes.decode('utf-8-sig')), change))

    # New record files are explicitly limited to the new batch folder.
    new_root = REPO / NEW_PREFIX
    assert new_root.is_dir(), f'Root must copy selected text records into {NEW_PREFIX} first'
    new_paths = sorted(p for p in new_root.rglob('*') if p.is_file())
    assert new_paths, 'No new batch records found'
    for path in new_paths:
        assert not path.is_symlink() and path.resolve().is_relative_to(new_root.resolve())
        rel = path.relative_to(REPO).as_posix()
        assert path.suffix.lower() in TEXT_SUFFIXES and '/local/' not in rel, f'Media or unexpected file forbidden: {rel}'
        data = path.read_bytes()
        assert len(data) < 2_000_000, f'Oversized record: {rel}'
        data.decode('utf-8-sig')  # Reject binary masquerading as text.
        assert blob_at(f'{head}:{rel}') is None, f'Batch path already tracked: {rel}'
        if (rel, 0) in before_entries:
            assert git('cat-file', 'blob', before_entries[(rel, 0)][1]) == data, f'Foreign staged new-record conflict: {rel}'
        assert not any(p == rel and stage != 0 for p, stage in before_entries)
        merged_head[rel] = merged_index[rel] = expected_work[rel] = data
        modes[rel] = '100644'
    allowed = set(merged_head)
    for label, files in [('head-after', merged_head), ('index-after', merged_index)]:
        for rel, data in files.items():
            out = review / label / rel
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(data)
    review_manifest = {'preparedAt': datetime.now(timezone.utc).isoformat(), 'mode': 'commit' if args.commit else 'prepare-only', 'head': head, 'branch': branch, 'allowedPaths': sorted(allowed), 'selectedJsonCount': 15, 'newRecordCount': len(new_paths), 'foreignIndexEntryCount': sum(p not in allowed for p, _ in before_entries), 'worktreeWritten': False, 'platformChanged': False, 'push': 'not-attempted'}
    (review / 'manifest.json').write_bytes(encode(review_manifest))
    if not args.commit:
        print(json.dumps({'mode': 'prepare-only', 'review': str(review), 'pathCount': len(allowed), 'gitMutated': False}))
        return

    head_index = git_dir / f'index.shorts-readability-20261028-head-{stamp}'
    reconcile_index = git_dir / f'index.shorts-readability-20261028-reconcile-{stamp}'
    lock_path = index_path.with_name('index.lock')
    owns_lock = False
    head_updated = False
    commit_oid = None
    try:
        assert not head_index.exists() and not reconcile_index.exists()
        env_head = os.environ.copy()
        env_head['GIT_INDEX_FILE'] = str(head_index)
        env_idx = os.environ.copy()
        env_idx['GIT_INDEX_FILE'] = str(reconcile_index)
        git('read-tree', head, env=env_head)
        reconcile_index.write_bytes(original_index)
        for files, env in [(merged_head, env_head), (merged_index, env_idx)]:
            rows = []
            for rel, data in files.items():
                oid = git('hash-object', '-w', '--stdin', data=data).decode().strip()
                rows.append(f'{modes[rel]} {oid} 0\t{rel}'.encode('utf-8'))
            git('update-index', '-z', '--index-info', data=b'\0'.join(rows) + b'\0', env=env)
        staged = {x.decode('utf-8') for x in git('diff', '--cached', '--name-only', '-z', head, env=env_head).split(b'\0') if x}
        assert staged and staged <= allowed, 'Unexpected isolated staged paths'
        git('diff', '--cached', '--check', env=env_head)
        (review / 'selected.patch').write_bytes(git('diff', '--cached', head, env=env_head))
        policy = subprocess.run(['node', 'scripts/media-policy.cjs'], cwd=REPO, env=env_head, capture_output=True)
        (review / 'media-policy.txt').write_bytes(policy.stdout + policy.stderr)
        assert policy.returncode == 0, 'Media policy failed; see saved output'
        after_entries = index_entries(env_idx)
        after_flags = index_flags(env_idx)
        foreign_before = {key: val for key, val in before_entries.items() if key[0] not in allowed}
        foreign_after = {key: val for key, val in after_entries.items() if key[0] not in allowed}
        assert foreign_before == foreign_after, 'Foreign semantic index entries changed'
        assert {p: f for p, f in before_flags.items() if p not in allowed} == {p: f for p, f in after_flags.items() if p not in allowed}, 'Foreign index flags changed'
        # All working files stay as the human/root merged them; a concurrent
        # update aborts without touching HEAD or the real index.
        for rel, expected in expected_work.items():
            assert (REPO / rel).read_bytes() == expected, f'Concurrent worktree change: {rel}'
        assert index_path.read_bytes() == original_index, 'Concurrent real-index change'
        assert git('rev-parse', 'HEAD').decode().strip() == head, 'Concurrent HEAD change'
        assert git('symbolic-ref', '-q', 'HEAD').decode().strip() == branch, 'Concurrent checkout change'
        tree = git('write-tree', env=env_head).decode().strip()
        commit_oid = git('commit-tree', tree, '-p', head, '-m', args.message).decode().strip()
        reconciled_bytes = reconcile_index.read_bytes()
        # The ordinary Git lock is obtained exclusively. This never removes or
        # overwrites a preexisting lock. It protects real-index replacement.
        fd = os.open(lock_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o666)
        owns_lock = True
        with os.fdopen(fd, 'wb') as handle:
            handle.write(reconciled_bytes)
            handle.flush()
            os.fsync(handle.fileno())
        assert index_path.read_bytes() == original_index, 'Concurrent real-index change before commit'
        assert git('rev-parse', 'HEAD').decode().strip() == head, 'Concurrent HEAD change before commit'
        assert git('symbolic-ref', '-q', 'HEAD').decode().strip() == branch, 'Concurrent checkout change before commit'
        for rel, expected in expected_work.items():
            assert (REPO / rel).read_bytes() == expected, f'Concurrent worktree change before commit: {rel}'
        git('update-ref', 'HEAD', commit_oid, head)  # compare-and-swap
        head_updated = True
        os.replace(lock_path, index_path)
        owns_lock = False
        final_entries, final_flags = index_entries(), index_flags()
        assert {k: v for k, v in final_entries.items() if k[0] not in allowed} == foreign_before
        assert {p: f for p, f in final_flags.items() if p not in allowed} == {p: f for p, f in before_flags.items() if p not in allowed}
        assert git('rev-parse', 'HEAD').decode().strip() == commit_oid
        for rel, expected in expected_work.items():
            assert (REPO / rel).read_bytes() == expected, f'Working file unexpectedly changed: {rel}'
        result = {**review_manifest, 'commit': commit_oid, 'parent': head, 'foreignIndexEntriesPreserved': len(foreign_before), 'foreignIndexFlagsPreserved': True, 'mediaPolicy': 'pass', 'diffCheck': 'pass', 'reviewBundle': str(review)}
        (review / 'commit-result.json').write_bytes(encode(result))
        (TASK / 'commit-result.json').write_bytes(encode(result))
        print(json.dumps(result, ensure_ascii=False))
    except BaseException as exc:
        (review / 'failure.json').write_bytes(encode({'error': str(exc), 'headUpdated': head_updated, 'newCommit': commit_oid, 'ownsIndexLock': owns_lock, 'indexBackup': str(review / 'index-before.bin'), 'reconciledIndex': str(reconcile_index), 'instructions': 'If HEAD was updated but index replacement failed, preserve the prepared lock/reconciled index and inspect before recovery. Do not reset or overwrite foreign staging.'}))
        if owns_lock and not head_updated:
            lock_path.unlink()  # This lock was created exclusively by us.
            owns_lock = False
        raise
    finally:
        # Preserve the recovery index when HEAD changed but real-index replacement
        # failed. Otherwise remove only our exact temporary index files.
        if not owns_lock:
            safe_temp_remove(head_index, git_dir)
            safe_temp_remove(reconcile_index, git_dir)


if __name__ == '__main__':
    main()
