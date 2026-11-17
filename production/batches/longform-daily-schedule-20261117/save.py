"""Commit this date-only correction while preserving all unrelated staging."""
import argparse
import copy
import json
import os
from pathlib import Path
import runpy
import subprocess
import tempfile
from finish import ROOT, HERE, UPLOAD, KEY, START, END


def git(*args, data=None, env=None):
    return subprocess.check_output(['git', '-c', 'core.safecrlf=false', *args], cwd=ROOT, input=data, env=env)


def projection(path, base, current):
    a, b = base.decode('utf-8-sig'), current.decode('utf-8-sig')
    if path.endswith('.md'):
        start, end = (('<!-- SEPARATE-FORMAT-SCHEDULE-20261117-START -->',
                       '<!-- SEPARATE-FORMAT-SCHEDULE-20261117-END -->')
                      if path.endswith('YOUTUBE_PUBLISHING.md') else (START, END))
        part = b[b.index(start):b.index(end) + len(end)]
        return (a[:a.index(start)] + part + a[a.index(end) + len(end):]
                if start in a else a.rstrip() + '\n\n' + part + '\n').encode('utf8')
    a, b = json.loads(a), json.loads(b)
    if path.endswith('video-production-control.json'):
        a.setdefault('scopedPublishingAuthorizations', {})[KEY] = copy.deepcopy(b['scopedPublishingAuthorizations'][KEY])
        a['separateFormatSchedulePolicy20261117'] = copy.deepcopy(b['separateFormatSchedulePolicy20261117'])
        target = a['scopedPublishingAuthorizations']['mathPublishing20261117']
        source = b['scopedPublishingAuthorizations']['mathPublishing20261117']
        for k in ('firstKst', 'lastKst', 'existingAnchorKst', 'currentScheduleSummary'):
            target[k] = copy.deepcopy(source[k])
    else:
        a[KEY] = copy.deepcopy(b[KEY])
        updated = {r['id']:r for r in b['rows'] if 'longformSchedule20261117' in r}
        for row in a['rows']:
            if row['id'] in updated:
                src = updated[row['id']]
                row['longformSchedule20261117'] = copy.deepcopy(src['longformSchedule20261117'])
                if src.get('publishing20261117'):
                    row['publishing20261117']['scheduledKst'] = src['publishing20261117']['scheduledKst']
        for k in ('firstKst', 'lastKst', 'existingAnchorKst', 'currentScheduleSummary'):
            a['mathPublishing20261117'][k] = copy.deepcopy(b['mathPublishing20261117'][k])
    return (json.dumps(a, ensure_ascii=False, indent=2) + '\n').encode('utf8')


def main(push):
    publish = runpy.run_path(str(ROOT / 'projects/buckshot-roulette-reverse-engineering/production/save-selective-git.py'))['publish_index_and_ref']
    head = git('rev-parse', 'HEAD').decode().strip()
    ref = git('symbolic-ref', 'HEAD').decode().strip()
    index = Path(git('rev-parse', '--path-format=absolute', '--git-path', 'index').decode().strip())
    original = index.read_bytes()
    direct = [p for p in HERE.iterdir() if p.is_file() and p.suffix in {'.json','.md','.html','.py'}]
    direct += [UPLOAD / name for name in ('batch.json', 'summary.json', 'platform-progress.json', 'prepare.py', 'finish.py', 'review.html')]
    direct.append(UPLOAD / 'thumbnail-revision-v2/review.html')
    direct += [UPLOAD / f'M{i}' / name for i in range(21,34) for name in ('package.json','youtube-upload.json')]
    shared = ['shared/publishing/video-production-control.json','shared/publishing/video-worklist.json',
              'docs/VIDEO_WORKLIST.md','docs/GAME_MATH_PRIVATE_POLISH.md','docs/YOUTUBE_PUBLISHING.md','docs/VIDEO_WORKFLOW.md']
    with tempfile.TemporaryDirectory() as temp:
        commit_env = dict(os.environ, GIT_INDEX_FILE=str(Path(temp) / 'commit.index'))
        reconcile_env = dict(os.environ, GIT_INDEX_FILE=str(Path(temp) / 'reconcile.index'))
        git('read-tree', head, env=commit_env)
        Path(reconcile_env['GIT_INDEX_FILE']).write_bytes(original)
        buffers = {e['GIT_INDEX_FILE']:bytearray() for e in (commit_env, reconcile_env)}

        def stage(path, data, env):
            data = data.replace(b'\r\n', b'\n')
            oid = git('hash-object', '-w', '--stdin', data=data).decode().strip()
            buffers[env['GIT_INDEX_FILE']].extend(f'100644 {oid}\t{path}\0'.encode('utf8'))

        for p in direct:
            data = p.read_bytes()
            if p.suffix == '.json':
                json.loads(data.decode('utf-8-sig'))
            if p.suffix == '.py':
                compile(data, str(p), 'exec')
            for env in (commit_env, reconcile_env):
                stage(p.relative_to(ROOT).as_posix(), data, env)
        for path in shared:
            for env, revision in ((commit_env, head + ':' + path), (reconcile_env, ':' + path)):
                stage(path, projection(path, git('show', revision), (ROOT / path).read_bytes()), env)
        for env in (commit_env, reconcile_env):
            git('update-index', '-z', '--index-info', data=bytes(buffers[env['GIT_INDEX_FILE']]), env=env)
        git('diff', '--cached', '--check', env=commit_env)
        subprocess.run(['node','scripts/media-policy.cjs'], cwd=ROOT, env=commit_env, check=True)
        changed = git('diff','--cached','--name-only',head,env=commit_env).decode().splitlines()
        if not changed:
            print('No schedule changes to commit')
            return
        tree = git('write-tree', env=commit_env).decode().strip()
        commit = git('commit-tree', tree, '-p', head, data=b'Separate Shorts and long-form queues; reschedule 43 videos daily from today\n').decode().strip()
        publish(index, Path(reconcile_env['GIT_INDEX_FILE']).read_bytes(), original, ref, head, commit)
        print(commit, len(changed), 'schedule files; unrelated staging preserved')
    if push:
        subprocess.run(['git','push','origin',ref], cwd=ROOT, check=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--push', action='store_true')
    main(parser.parse_args().push)
