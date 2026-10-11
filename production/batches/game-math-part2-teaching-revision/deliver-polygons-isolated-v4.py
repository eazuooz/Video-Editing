"""Selective per-video Git delivery; never consume another task's real index.

Usage: python deliver-polygons-isolated-v4.py <owned-slug> [--commit]
The default prepares and checks a separate index and records its exact path list.
--commit uses an expected-HEAD compare-and-swap and a normal, non-force push.
"""
import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BATCH = ROOT / 'production/batches/game-math-part2-teaching-revision'
parser = argparse.ArgumentParser()
parser.add_argument('slug', choices=['game-math-polygon-centers-v2','game-math-polygon-partition-v2'])
parser.add_argument('--commit', action='store_true')
args = parser.parse_args()
WORK = ROOT / 'shared/output/polygons-git-delivery-v4'
WORK.mkdir(parents=True, exist_ok=True)
index = WORK / (args.slug + '.index')
assert index.resolve().is_relative_to(ROOT)
env = dict(os.environ, GIT_INDEX_FILE=str(index.resolve()))

def git(*argv, data=None, isolated=True):
    return subprocess.run(['git', *argv], cwd=ROOT,
        env=env if isolated else os.environ, input=data, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, check=True).stdout

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None

base = git('rev-parse','HEAD',isolated=False).decode().strip()
branch = git('symbolic-ref','HEAD',isolated=False).decode().strip()
assert branch.startswith('refs/heads/')
real_index_name = git('rev-parse','--git-path','index',isolated=False).decode().strip()
real_index = Path(real_index_name)
if not real_index.is_absolute():
    real_index = ROOT / real_index
index_before = sha(real_index)
git('read-tree',base)
receipt = json.loads((ROOT / 'projects' / args.slug / 'publishing/youtube-upload.json').read_text(encoding='utf-8'))
assert receipt['uploadComplete'] and receipt['fullPublishingSettingsComplete']
assert json.loads((ROOT / 'projects' / args.slug / 'production/current-pixel-review.json').read_text(encoding='utf-8'))['sha256'] == receipt['video']['sha256']
allowed = {'.json','.md','.py','.cjs','.js','.ts','.ps1','.txt','.srt','.ass','.html','.css'}
def owned_batch_path(path):
    relative = path.relative_to(BATCH)
    if relative.parts[0] == 'baselines':
        return len(relative.parts) > 1 and relative.parts[1] == 'game-math-polygons-triangulation'
    if relative.parts[0] == 'cross-game-review-20261011':
        return True
    return 'polygon' in path.name.lower() or 'polygons-tracks' in relative.parts or relative.as_posix() in {
        'queue.json', 'gpu-handoff.py', 'serve-review.cjs',
        'audit-cross-game-inventory.py', 'record-four-game-retain-review.py'}

files = sorted({path.relative_to(ROOT).as_posix()
    for parent in [ROOT/'projects'/args.slug, BATCH]
    for path in parent.rglob('*') if path.is_file() and path.suffix.lower() in allowed
    and '__pycache__' not in path.parts
    and (not path.is_relative_to(BATCH) or owned_batch_path(path))})
files += ['docs/VIDEO_EXAMPLE_TRANSFER_REVIEW.md', 'shared/publishing/game-example-coverage-policy.json']
thumbnail = receipt['thumbnail']['path']
assert sha(ROOT / thumbnail) == receipt['thumbnail']['sha256']
files.append(thumbnail)
git('add','--pathspec-from-file=-','--pathspec-file-nul',
    data=('\0'.join(files)+'\0').encode('utf-8'))

def head_text(path):
    return git('show',base+':'+path,isolated=False).decode('utf-8').replace('\r\n','\n')

def stage_text(path,text):
    blob = git('hash-object','-w','--stdin',data=text.encode('utf-8')).decode().strip()
    git('update-index','--add','--cacheinfo','100644,'+blob+','+path)
    if path not in files:
        files.append(path)

# Copy just this task's new policy sections into HEAD versions. Do not commit
# unrelated working-copy policy changes or another task's image registrations.
agents = (ROOT/'AGENTS.md').read_text(encoding='utf-8')
paragraph = next(line for line in agents.splitlines() if line.startswith('- Cross-game teaching coverage,'))
agents_base = head_text('AGENTS.md')
if paragraph not in agents_base:
    assert '- Cross-game teaching coverage,' not in agents_base
    agents_base = agents_base.replace('# Video production defaults\n\n', '# Video production defaults\n\n'+paragraph+'\n\n',1)
stage_text('AGENTS.md',agents_base)
workflow = (ROOT/'docs/VIDEO_WORKFLOW.md').read_text(encoding='utf-8')
section = workflow.split('\n\n',1)[1].split('\n## ',1)[0].strip()+'\n\n'
workflow_base = head_text('docs/VIDEO_WORKFLOW.md')
if '## 여러 게임으로 개념을 일반화하기' not in workflow_base:
    title, body = workflow_base.split('\n\n',1)
    workflow_base = title+'\n\n'+section+body
stage_text('docs/VIDEO_WORKFLOW.md',workflow_base)
footage = (ROOT/'docs/VIDEO_GAME_FOOTAGE_POLICY.md').read_text(encoding='utf-8')
paragraph = next(line for line in footage.splitlines() if line.startswith('2026-10-11 최신 사용자 지시:'))
footage_base = head_text('docs/VIDEO_GAME_FOOTAGE_POLICY.md')
if paragraph not in footage_base:
    title, body = footage_base.split('\n\n',1)
    footage_base = title+'\n\n'+paragraph+'\n\n'+body
stage_text('docs/VIDEO_GAME_FOOTAGE_POLICY.md',footage_base)
ignore = head_text('.gitignore')
exception = '!'+thumbnail
if exception not in ignore.splitlines():
    ignore = ignore.rstrip()+'\n\n# Reviewed lecture delivery thumbnail\n'+exception+'\n'
stage_text('.gitignore',ignore)
registry = json.loads(head_text('shared/git-essential-images.json'))
working_registry = json.loads((ROOT/'shared/git-essential-images.json').read_text(encoding='utf-8'))
entry = next(e for e in working_registry['entries'] if e['path'] == thumbnail)
assert entry['sha256'] == receipt['thumbnail']['sha256']
registry['entries'] = [e for e in registry['entries'] if e['path'] != thumbnail]+[entry]
stage_text('shared/git-essential-images.json',json.dumps(registry,ensure_ascii=False,indent=2)+'\n')

subprocess.run(['node','scripts/media-policy.cjs'],cwd=ROOT,env=env,check=True)
tree = git('write-tree').decode().strip()
summary = git('diff','--cached','--stat',base).decode('utf-8')
record = dict(slug=args.slug, base=base, branch=branch, isolatedIndex=str(index),
              actualVideoId=receipt['videoId'], paths=sorted(files), tree=tree,
              realIndexBeforeSha256=index_before, stagedSummary=summary,
              humanListening='pending', gameIPHumanApproval='pending', committed=False)
record_path = WORK / (args.slug+'.json')
if args.commit:
    assert git('rev-parse','HEAD',isolated=False).decode().strip() == base, 'Concurrent HEAD changed; rerun from fresh HEAD.'
    subject = 'Deliver four-game '+('polygon centers' if 'centers' in args.slug else 'polygon partition')+' lecture with verified private upload'
    commit = git('commit-tree',tree,'-p',base,data=(subject+'\n').encode('utf-8')).decode().strip()
    git('update-ref',branch,commit,base)
    record.update(committed=True,commit=commit)
    # Save the local commit evidence even if a non-force push is rejected.
    record_path.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    git('push','origin',branch)
    remote = git('ls-remote','origin',branch).decode().split()[0]
    assert remote == commit, 'Actual remote SHA differs.'
    record.update(pushed=True,remoteSha=remote)
record['realIndexAfterSha256'] = sha(real_index)
assert record['realIndexAfterSha256'] == index_before, 'Real index changed; inspect concurrent ownership before proceeding.'
record_path.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:record[k] for k in ['slug','base','tree','committed']},ensure_ascii=False))
print(summary)
