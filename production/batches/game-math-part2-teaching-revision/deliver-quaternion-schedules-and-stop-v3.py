"""Deliver actual quaternion schedules and the user stopping boundary selectively."""
from pathlib import Path
import argparse,copy,hashlib,json,os,subprocess
parser=argparse.ArgumentParser();parser.add_argument('--commit',action='store_true');args=parser.parse_args()
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
Q=B/'cross-game-review-20261011/quaternion-four-game-v3'
W=ROOT/'shared/output/quaternion-git-delivery-v3';W.mkdir(exist_ok=True)
env=dict(os.environ,GIT_INDEX_FILE=str(W/'publishing-and-stop.index'))
def git(*a,data=None,isolated=True):
    p=subprocess.run(['git',*a],cwd=ROOT,env=env if isolated else os.environ,input=data,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if p.returncode:raise RuntimeError(p.stderr.decode('utf8',errors='replace'))
    return p.stdout
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
base=git('rev-parse','HEAD',isolated=False).decode().strip();branch=git('symbolic-ref','HEAD',isolated=False).decode().strip()
index=Path(git('rev-parse','--git-path','index',isolated=False).decode().strip())
if not index.is_absolute():index=ROOT/index
before=sha(index);git('read-tree',base)
files=[]
def include(p):
    assert p.is_file() and p.suffix in {'.py','.cjs','.json','.md','.txt'}
    files.append(p.relative_to(ROOT).as_posix())
for name in ['foundations','calculations']:
    schedule=read(Q/f'{name}-v3-actual-schedule.json')
    assert schedule['actualSavedReopened'] and schedule['baselinePrivateSavedReopened']
    for version in ['v2','v3']:
        folder=ROOT/'projects'/f'game-math-quaternion-{name}-{version}'
        for rel in ['publishing/youtube-upload.json','rebuild.json']:
            include(folder/rel)
        if version=='v3':include(folder/'project.json')
    for suffix in ['korean-reopened.json','english-reopened.json','platform-status.json',
                   'youtube-caption-pixel-review.json','old-schedule-before-replacement.txt',
                   'old-private-reopened.txt','v3-schedule-reopened.txt','v3-actual-schedule.json']:
        include(Q/f'{name}-{suffix}')
for name in ['current-private-progress.json','actual-schedule-replacements.json',
             'foundations-copyright-pending.txt','foundations-schedule-copyright-pending-notice.txt',
             'calculations-platform-checks-complete.txt']:
    include(Q/name)
for name in ['record-quaternion-schedules-v3.py','refresh-quaternion-publishing-rebuilds-v3.cjs',
             'record-stop-after-3d-graphics-20261012.py','stop-after-3d-graphics-20261012.json']:
    include(B/name)
include(Path(__file__))
git('add','--pathspec-from-file=-','--pathspec-file-nul',data=('\0'.join(files)+'\0').encode())
def head_json(path):return json.loads(git('show',base+':'+path,isolated=False))
def stage_text(path,value):
    blob=git('hash-object','-w','--stdin',data=value.encode()).decode().strip()
    git('update-index','--add','--cacheinfo','100644,'+blob+','+path);files.append(path)
def stage_json(path,value):stage_text(path,json.dumps(value,ensure_ascii=False,indent=2)+'\n')

# Preserve unrelated in-flight changes to this shared rule file.
head_agents=git('show',base+':AGENTS.md',isolated=False).decode('utf8')
own_rule=next(line for line in (ROOT/'AGENTS.md').read_text(encoding='utf-8-sig').splitlines() if line.startswith('- Part 2 stopping boundary, user-directed 2026-10-12:'))
if own_rule not in head_agents:
    head_agents=head_agents.replace('# Video production defaults\n\n','# Video production defaults\n\n'+own_rule+'\n\n',1)
stage_text('AGENTS.md',head_agents)

qpath=B.relative_to(ROOT).as_posix()+'/queue.json';queue=head_json(qpath);working=read(B/'queue.json')
old=next(i for i in queue['items'] if i['slug']=='game-math-quaternion-operations')
new=next(i for i in working['items'] if i['slug']==old['slug'])
for key in ['status','fourGameRevision']:old[key]=copy.deepcopy(new[key])
for key in ['stage','lastProgressAt','currentQuaternionReview','stopAfterSlug','stopAfterScope',
            'stopAfterCompletionRecord','stopAtBoundaryRequested','startSubsequentLectures',
            'startRemainingSakuraiSix','resumeAfterBoundaryRequiresExplicitUserInstruction']:
    queue['execution'][key]=copy.deepcopy(working['execution'][key])
queue['authorization']['nextBatchAfterPart2']=working['authorization']['nextBatchAfterPart2']
assert queue['execution']['stopAfterSlug']==queue['items'][-1]['slug']=='game-math-normal-transform-uv'
stage_json(qpath,queue)

ledgerpath='shared/publishing/daily-alternating-schedule.json';ledger=head_json(ledgerpath);live=read(ROOT/ledgerpath)
old_ids={'HdJw7bgKlbM','SPq_41LyOG0'};new_ids={'wreXZkEtLqA','Rck2eL8VtqM'}
for name in ['foundations','calculations']:
    s=read(Q/f'{name}-v3-actual-schedule.json')
    actual=next(a for a in live['actualSchedules'] if a['videoId']==s['videoId'])
    targets=[i for i,a in enumerate(ledger['actualSchedules']) if a['videoId'] in {s['videoId'],s['replacedVideoId']}]
    assert len(targets)==1
    ledger['actualSchedules'][targets[0]]=copy.deepcopy(actual)
for history in live.get('replacementHistory',[]):
    if history.get('oldSchedule',{}).get('videoId') not in old_ids:continue
    assert history['newSchedule']['videoId'] in new_ids
    items=ledger.setdefault('replacementHistory',[])
    target=next((i for i,h in enumerate(items) if h.get('oldSchedule',{}).get('videoId')==history['oldSchedule']['videoId'] and h.get('newSchedule',{}).get('videoId')==history['newSchedule']['videoId']),None)
    if target is None:items.append(copy.deepcopy(history))
    else:items[target]=copy.deepcopy(history)
ledger['updatedAt']=live['updatedAt'];stage_json(ledgerpath,ledger)
subprocess.run(['node','scripts/media-policy.cjs'],cwd=ROOT,env=env,check=True)
for episode in ['foundations','calculations']:
    for version in ['v2','v3']:
        subprocess.run(['node','scripts/build-rebuild-manifests.cjs',f'game-math-quaternion-{episode}-{version}','--check'],cwd=ROOT,env=env,check=True)
tree=git('write-tree').decode().strip();summary=git('diff','--cached','--stat',base).decode('utf8')
record=dict(base=base,tree=tree,paths=sorted(set(files)),realIndexBeforeSha256=before,
    realIndexPreserved=True,unrelatedWorkingFieldsExcluded=True,committed=False,
    originalProductionGitReceiptsPreserved=True,foundationCopyrightCheckStillPending=True,
    stopAfterSlug='game-math-normal-transform-uv',summary=summary)
target=W/'publishing-and-stop-delivery.json'
if args.commit:
    assert git('rev-parse','HEAD',isolated=False).decode().strip()==base
    commit=git('commit-tree',tree,'-p',base,data=b'Record quaternion schedule replacements and stop after Part 2 graphics\n').decode().strip()
    git('update-ref',branch,commit,base);record.update(committed=True,commit=commit)
    target.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    git('push','origin',branch);remote=git('ls-remote','origin',branch).decode().split()[0];assert remote==commit
    record.update(pushed=True,remoteSha=remote)
record['realIndexAfterSha256']=sha(index);assert record['realIndexAfterSha256']==before
target.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(summary);print(json.dumps({k:record.get(k) for k in ['committed','commit','pushed','remoteSha','realIndexPreserved','stopAfterSlug']}))
