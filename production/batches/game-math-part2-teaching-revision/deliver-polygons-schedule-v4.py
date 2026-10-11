"""Push reviewed owned PART2 scheduling metadata through a separate Git index.

The shared ledger blob copies only this batch's lecture entries into HEAD;
other owners' uncommitted ledger fields and the real index are preserved.
Usage: python deliver-polygons-schedule-v4.py [--commit]
"""
import copy
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BATCH = ROOT/'production/batches/game-math-part2-teaching-revision'
EVIDENCE = ROOT/'shared/publishing/polygons-four-game-schedule-20261011'
WORK = ROOT/'shared/output/polygons-git-delivery-v4'
env = dict(os.environ,GIT_INDEX_FILE=str((WORK/'schedule.index').resolve()))

def git(*args,data=None,isolated=True):
    return subprocess.run(['git',*args],cwd=ROOT,env=env if isolated else os.environ,
        input=data,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True).stdout

def read(path):
    return json.loads(path.read_text(encoding='utf-8'))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

queue = read(BATCH/'queue.json')
owned = {item['slug'] for item in queue['items']}
for item in queue['items']:
    owned.update(item.get('revision',{}).get('episodeSlugs',[]))
working_ledger = read(ROOT/'shared/publishing/daily-alternating-schedule.json')
current = [entry for entry in working_ledger['actualSchedules'] if entry['slug'] in owned]
assert len(current)==16
verification = read(EVIDENCE/'actual-verified-schedule.json')
assert verification['actualNoDoubleBooking'] and verification['allTwoDaysApart'] and verification['all09KST']
base = git('rev-parse','HEAD',isolated=False).decode().strip()
branch = git('symbolic-ref','HEAD',isolated=False).decode().strip()
real_index = Path(git('rev-parse','--git-path','index',isolated=False).decode().strip())
if not real_index.is_absolute(): real_index = ROOT/real_index
real_before = sha(real_index)
git('read-tree',base)
paths = [entry['slug'] for entry in current]+['game-math-polygons-triangulation']
files = [f'projects/{slug}/{suffix}' for slug in paths for suffix in ['publishing/youtube-upload.json','rebuild.json']]
files += ['projects/game-math-polygon-centers-v2/project.json','projects/game-math-polygon-partition-v2/project.json']
files += [p.relative_to(ROOT).as_posix() for p in EVIDENCE.iterdir() if p.suffix in {'.txt','.json'}]
files += [str(p.relative_to(ROOT)).replace('\\','/') for p in [
    BATCH/'queue.json',BATCH/'record-polygons-schedule-v4.py',BATCH/'deliver-polygons-schedule-v4.py',
    BATCH/'rebuild-polygons-scoped-v4.cjs',BATCH/'cross-game-review-20261011/polygons-v4-current-progress.json']]
files += ['shared/publishing/schedule-replacement-20261011/two-day-final-audit.json']
files += ['scripts/build-rebuild-manifests.cjs']
for slug in [entry['slug'] for entry in current]:
    receipt = read(ROOT/'projects'/slug/'publishing/youtube-upload.json')
    row = next(e for e in current if e['slug']==slug)
    assert receipt['videoId'] == row['videoId'] and receipt['scheduledAt'] == row['publishAt']
git('add','--pathspec-from-file=-','--pathspec-file-nul',data=('\0'.join(files)+'\0').encode('utf-8'))

ledger = json.loads(git('show',base+':shared/publishing/daily-alternating-schedule.json',isolated=False))
unrelated_before = [e for e in ledger['actualSchedules'] if e['slug'] not in owned]
ledger['actualSchedules'] = sorted(copy.deepcopy(unrelated_before)+copy.deepcopy(current),key=lambda e:(e['date'],e.get('time','09:00')))
assert len({(e['date'],e.get('time','09:00')) for e in ledger['actualSchedules']})==len(ledger['actualSchedules'])
assert [e for e in ledger['actualSchedules'] if e['slug'] not in owned] == sorted(unrelated_before,key=lambda e:(e['date'],e.get('time','09:00')))
ledger['updatedAt'] = verification['verifiedAt']
ledger['latestPart2RevisionScheduleEvidence'] = 'shared/publishing/polygons-four-game-schedule-20261011/actual-verified-schedule.json'
ledger['polygonsFourGameReplacement'] = verification
blob = git('hash-object','-w','--stdin',data=(json.dumps(ledger,ensure_ascii=False,indent=2)+'\n').encode('utf-8')).decode().strip()
git('update-index','--add','--cacheinfo','100644,'+blob+',shared/publishing/daily-alternating-schedule.json')
files.append('shared/publishing/daily-alternating-schedule.json')
subprocess.run(['node','scripts/media-policy.cjs'],cwd=ROOT,env=env,check=True)
tree = git('write-tree').decode().strip()
summary = git('diff','--cached','--stat',base).decode('utf-8')
record = dict(base=base,tree=tree,paths=sorted(files),realIndexBeforeSha256=real_before,
    schedulesVerified=16,polygonActualVideoIds=['YgcN8vs0gNo','pfagaQK-xfI'],
    unrelatedWorkingLedgerFieldsExcluded=True,committed=False,stagedSummary=summary)
target = WORK/'schedule-delivery.json'
if '--commit' in sys.argv:
    assert git('rev-parse','HEAD',isolated=False).decode().strip()==base
    commit = git('commit-tree',tree,'-p',base,data=b'Record verified two-day PART2 schedules and four-game polygon replacement\n').decode().strip()
    git('update-ref',branch,commit,base)
    record.update(committed=True,commit=commit)
    target.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    git('push','origin',branch)
    remote = git('ls-remote','origin',branch).decode().split()[0]
    assert remote==commit
    record.update(pushed=True,remoteSha=remote)
record['realIndexAfterSha256'] = sha(real_index)
assert record['realIndexAfterSha256']==real_before
target.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({key:record.get(key) for key in ['committed','commit','pushed','remoteSha','schedulesVerified']},ensure_ascii=False))
print(summary)
