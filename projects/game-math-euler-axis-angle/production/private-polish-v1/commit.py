"""Selective private-index delivery; preserve independently staged shared files."""
from pathlib import Path
import copy,json,os,shutil,subprocess,sys,time
import common as c
def git(*args,env=None,inp=None):
 r=subprocess.run(['git',*args],cwd=c.R,env=env,input=inp,capture_output=True)
 if r.returncode:raise RuntimeError((r.stdout+r.stderr).decode(errors='replace')[-3000:])
 return r.stdout
unit=sys.argv[1];paths=c.read(c.O/(unit+'-commit.json'))['paths']
assert all('/local/' not in p and not p.startswith('output/') for p in paths)
base=git('rev-parse','HEAD').decode().strip();work=c.O/f'git-{unit}-{time.time_ns()}';work.mkdir()
real=Path(git('rev-parse','--git-path','index').decode().strip());real=real if real.is_absolute() else c.R/real
shutil.copy2(real,work/'index-before.bin');before=git('ls-files','--stage','-z')
staged=set(git('diff','--cached','--name-only').decode().splitlines())
allowed_shared={'shared/publishing/video-worklist.json','shared/publishing/video-production-control.json','docs/VIDEO_WORKLIST.md'}
assert not (staged & set(paths) - allowed_shared),'Independent staging on a non-shared owned path'
env=dict(os.environ,GIT_INDEX_FILE=str(work/'index'));git('read-tree',base,env=env)
git('add','--',*paths,env=env)
def head(path):return git('show',base+':'+path).decode('utf8')
def blob(path,content):
 h=git('hash-object','-w','--stdin',inp=content.encode('utf8')).decode().strip()
 git('update-index','--cacheinfo','100644,'+h+','+path,env=env)
worklist=None
for path in paths:
 if path=='shared/publishing/video-production-control.json':
  data=json.loads(head(path));current=c.read(c.R/path)
  data['scopedProductionAuthorizations'][c.P.name]=current['scopedProductionAuthorizations'][c.P.name]
  data['updatedAt']=current['updatedAt'];blob(path,json.dumps(data,ensure_ascii=False,indent=2)+'\n')
 elif path=='shared/publishing/video-worklist.json':
  data=json.loads(head(path));current=c.read(c.R/path)
  data['privateMathPolish']=current['privateMathPolish'];data['updatedAt']=current['updatedAt']
  cur={r['id']:r for r in current['rows']}
  for row in data['rows']:
   if 'privatePolish' in cur[row['id']]:
    for k in ['privatePolish','platformStatus','platformEvidence']:row[k]=cur[row['id']][k]
   if row['id']=='M04':
    for k in ['title','executionStatus','reviewStatus','latestRulesPassed']:row[k]=cur[row['id']][k]
  worklist=data;blob(path,json.dumps(data,ensure_ascii=False,indent=2)+'\n')
 elif path=='projects/game-math-euler-axis-angle/project.json':
  data=json.loads(head(path));current=c.read(c.R/path);data['activeVisualPolish']=current['activeVisualPolish'];data['updatedAt']=current['updatedAt']
  blob(path,json.dumps(data,ensure_ascii=False,indent=2)+'\n')
 elif path=='projects/game-math-euler-axis-angle/planning/production-plan.json':
  data=json.loads(head(path));data['baselineVisualPolish']=c.read(c.R/path)['baselineVisualPolish'];blob(path,json.dumps(data,ensure_ascii=False,indent=2)+'\n')
 elif path=='projects/game-math-euler-axis-angle/production/review-ledger.json':
  data=json.loads(head(path));data['activeVisualPolishReview']=c.read(c.R/path)['activeVisualPolishReview'];blob(path,json.dumps(data,ensure_ascii=False,indent=2)+'\n')
 elif path=='docs/VIDEO_WORKFLOW.md':
  previous=head(path);paragraph=next(x for x in (c.R/path).read_text(encoding='utf8').splitlines() if x.startswith('2026-10-22 사용자 선택 `baseline-preserving-visual-polish-v1`'))
  old=next((x for x in previous.splitlines() if x.startswith('2026-10-22 사용자 선택 `baseline-preserving-visual-polish-v1`')),None)
  if old:previous=previous.replace(old,paragraph,1)
  elif paragraph not in previous:previous=previous.replace('## 8. 게시·Git·종료',paragraph+'\n\n## 8. 게시·Git·종료')
  blob(path,previous)
if worklist is not None:
 root=work/'render';(root/'scripts').mkdir(parents=True);(root/'docs').mkdir();(root/'shared/publishing').mkdir(parents=True)
 c.save(root/'shared/publishing/video-worklist.json',worklist)
 shutil.copy2(c.R/'scripts/render-video-worklist.py',root/'scripts/render-video-worklist.py')
 subprocess.run([sys.executable,root/'scripts/render-video-worklist.py'],check=True,capture_output=True)
 for path in ['docs/VIDEO_WORKLIST.md','docs/GAME_MATH_PRIVATE_POLISH.md']:
  if path in paths:blob(path,(root/path).read_text(encoding='utf8'))
changed=set(git('diff','--cached','--name-only','-z',env=env).decode().split('\0'))-{''};assert changed<=set(paths) and changed
git('diff','--cached','--check',env=env)
subprocess.run(['node','scripts/media-policy.cjs'],cwd=c.R,env=env,check=True)
assert git('rev-parse','HEAD').decode().strip()==base,'Concurrent commit; rerun with latest HEAD'
git('commit','-m',c.read(c.O/(unit+'-commit.json'))['message'],env=env)
commit=git('rev-parse','HEAD').decode().strip()
# Leave the existing staged shared entries intact. Sync only unstaged owned entries.
sync=[p for p in paths if p not in staged]
if sync:git('reset','-q','HEAD','--',*sync)
def foreign(data):return [x for x in data.split(b'\0') if x and x.split(b'\t',1)[1].decode() not in sync]
assert foreign(before)==foreign(git('ls-files','--stage','-z'))
branch=git('branch','--show-current').decode().strip();git('push','origin','HEAD:refs/heads/'+branch)
remote=git('ls-remote','origin','refs/heads/'+branch).decode().split()[0];assert remote==commit
c.save(c.O/(unit+'-git-receipt.json'),dict(commit=commit,remote=remote,paths=sorted(changed),foreignIndexPreserved=True))
print(json.dumps({'commit':commit,'remote':remote,'files':len(changed),'foreignIndexPreserved':True}))
