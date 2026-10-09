"""Deliver only this scheduling change with an isolated index and real SHA proof."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, subprocess, tomllib, uuid

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
NODE = Path('C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe')

def sha(data):
    return hashlib.sha256(data).hexdigest()

def run(args, env=None, data=None):
    p = subprocess.run(args, cwd=ROOT, env=env, input=data, capture_output=True)
    if p.returncode:
        raise RuntimeError(p.stderr.decode('utf-8', 'replace') + p.stdout.decode('utf-8', 'replace'))
    return p.stdout

def git(args, env=None, data=None):
    return run(['git', *args], env, data)

def save(p, value):
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

result = json.loads((BASE/'result.json').read_text('utf-8'))
assert result['actualScheduledCount'] == 23 and result['allDatesTimesTimezonesReopened']
assert result['allRowsReverifiedAfterReload'] and result['rasterGitAdditions'] == 0
automation = tomllib.loads(Path('C:/Users/eazuo/.codex/automations/24/automation.toml').read_text('utf-8'))
assert automation['status'] == 'ACTIVE' and automation['kind'] == 'heartbeat'
assert automation['prompt'].startswith('최신 사용자 예약 지시(2026-10-09)')
save(BASE/'automation-verification.json', dict(
    verifiedAt=datetime.now(timezone.utc).isoformat(), id=automation['id'],
    status=automation['status'], name=automation['name'], kind=automation['kind'],
    targetThreadId=automation['target_thread_id'], recurrence=automation['rrule'],
    actualPromptSha256=sha(automation['prompt'].encode('utf-8')),
    latestSchedulingOverridePresent=True, preservedOriginalProductionInstructions=True,
    schedulingUnfinishedTargetsClaimed=False))

explicit = [
    'AGENTS.md', 'docs/YOUTUBE_PUBLISHING.md',
    'shared/publishing/youtube-defaults.json',
    'shared/publishing/daily-alternating-schedule.json',
    'shared/publishing/schedule-20261009/prepare-plan.cjs',
    'shared/publishing/schedule-20261009/record-verification.cjs',
    'shared/publishing/schedule-20261009/deliver-records.py',
    'shared/publishing/schedule-20261009/studio-before-rows.json',
    'shared/publishing/schedule-20261009/plan.json',
    'shared/publishing/schedule-20261009/execution.json',
    'shared/publishing/schedule-20261009/result.json',
    'shared/publishing/schedule-20261009/calendar.md',
    'shared/publishing/schedule-20261009/automation-verification.json',
]
explicit += [item['evidence'] for item in result['items']]
assert len(explicit) == len(set(explicit)) == 36
assert all((ROOT/p).is_file() for p in explicit)
assert not any(Path(p).suffix.lower() in ['.png', '.jpg', '.mp4', '.wav', '.aac'] for p in explicit)
parent = git(['rev-parse', 'HEAD']).decode().strip()
index_name = git(['rev-parse', '--git-path', 'index']).decode().strip()
external_index = Path(index_name)
if not external_index.is_absolute():
    external_index = ROOT/external_index
external_index_hash = sha(external_index.read_bytes()) if external_index.exists() else None
external_entries = git(['ls-files', '--stage', '-z'])
temp_index = ROOT/'shared/output'/('schedule-index-' + str(uuid.uuid4()) + '.tmp')
env = dict(os.environ, GIT_INDEX_FILE=str(temp_index))
git(['read-tree', parent], env)
normal_paths = [p for p in explicit if p != 'AGENTS.md']
git(['add', '--', *normal_paths], env)

# Only the newly authored scheduling paragraph enters this shared-file blob.
# Preserve the working copy's foreign palette/series/hold changes untouched.
working_agents = (ROOT/'AGENTS.md').read_bytes()
text = working_agents.decode('utf-8-sig').replace('\r\n', '\n')
own = next(line for line in text.splitlines() if line.startswith('- Daily alternating publication, user-directed 2026-10-09:'))
head_agents = git(['show', parent + ':AGENTS.md']).decode('utf-8-sig').replace('\r\n', '\n')
assert own not in head_agents and head_agents.startswith('# Video production defaults\n\n')
approved_agents = head_agents.replace('# Video production defaults\n\n', '# Video production defaults\n\n' + own + '\n\n', 1).encode('utf-8')
agents_blob = git(['hash-object', '-w', '--stdin'], data=approved_agents).decode().strip()
git(['update-index', '--add', '--cacheinfo', '100644', agents_blob, 'AGENTS.md'], env)
changed = git(['diff', '--cached', '--name-only', '-z'], env).decode().split('\0')
assert set(filter(None, changed)) == set(explicit)
git(['diff', '--cached', '--check'], env)
media_check = run([str(NODE), 'scripts/media-policy.cjs'], env).decode().strip()
expected_blobs = {p: git(['rev-parse', ':'+p], env).decode().strip() for p in explicit}
assert (ROOT/'AGENTS.md').read_bytes() == working_agents
assert git(['rev-parse', 'HEAD']).decode().strip() == parent
assert (sha(external_index.read_bytes()) if external_index.exists() else None) == external_index_hash
assert git(['ls-files', '--stage', '-z']) == external_entries
before = dict(
    checkedAt=datetime.now(timezone.utc).isoformat(), parent=parent, explicitPaths=explicit,
    approvedBlobs=expected_blobs, mediaCheck=media_check, whitespacePassed=True,
    newRasterOrMediaCount=0, scope='Scheduling records and policy only; no production media/code changes; rebuild/TTS/render checks not rerun',
    temporaryIndex=str(temp_index), externalIndexBeforeSha256=external_index_hash,
    foreignAgentsWorkingBytesPreserved=True, foreignSharedFileChangesExcluded=True)
save(BASE/'git-pre-delivery-verification.json', before)
commit_output = git(['commit', '-m', 'Schedule completed design and lecture videos on alternating mornings'], env).decode('utf-8', 'replace')
commit = git(['rev-parse', 'HEAD']).decode().strip()
assert git(['rev-parse', commit+'^']).decode().strip() == parent
assert set(filter(None, git(['diff-tree', '--no-commit-id', '--name-only', '-r', '-z', commit]).decode().split('\0'))) == set(explicit)
for p, blob in expected_blobs.items():
    assert git(['rev-parse', commit+':'+p]).decode().strip() == blob, p
assert (ROOT/'AGENTS.md').read_bytes() == working_agents
assert (sha(external_index.read_bytes()) if external_index.exists() else None) == external_index_hash
assert git(['ls-files', '--stage', '-z']) == external_entries
proof = dict(before, commit=commit, actualCommitOutput=commit_output, pushed=False, remoteCommit=None,
             exactLocalRemoteMatch=False, allCommittedBlobsVerified=True, externalIndexUnchanged=True)
save(BASE/'git-delivery-verification.json', proof)
push_output = git(['push', 'origin', 'HEAD:main']).decode('utf-8', 'replace')
remote = git(['ls-remote', '--heads', 'origin', 'main']).decode().split()[0]
local = git(['rev-parse', 'HEAD']).decode().strip()
assert remote == local == commit
for p, blob in expected_blobs.items():
    assert git(['rev-parse', remote+':'+p]).decode().strip() == blob, p
assert (ROOT/'AGENTS.md').read_bytes() == working_agents
assert (sha(external_index.read_bytes()) if external_index.exists() else None) == external_index_hash
assert git(['ls-files', '--stage', '-z']) == external_entries
proof.update(verifiedAt=datetime.now(timezone.utc).isoformat(), pushed=True, normalPush=True,
             actualPushOutput=push_output, remoteCommit=remote, actualLocalHead=local,
             exactLocalRemoteMatch=True, allRemoteBlobsVerified=True,
             externalIndexAfterSha256=external_index_hash, unrelatedIndexEntriesPreserved=True)
save(BASE/'git-delivery-verification.json', proof)
print(json.dumps(dict(commit=commit, remote=remote, exactLocalRemoteMatch=True,
                      explicitPaths=len(explicit), newImagesAndMedia=0,
                      externalIndexUnchanged=True, allRemoteBlobsVerified=True)))
