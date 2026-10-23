"""Commit owned revision files with a private index; leave foreign staging/lock intact."""
from common import *
import shutil,time,sys
unit=sys.argv[1];config=read(B/(unit+'-commit.json'));paths=config['paths']
def git(*args,env=None,inp=None):
 p=subprocess.run(['git',*args],cwd=R,env=env,input=inp,capture_output=True)
 if p.returncode:raise RuntimeError((p.stdout+p.stderr).decode(errors='replace')[-2500:])
 return p.stdout
base=git('rev-parse','HEAD').decode().strip();work=R/'shared/output/private-math-concept-fit-20261023'/f'git-{unit}-{time.time_ns()}';work.mkdir(parents=True)
index=R/'.git/index';shutil.copy2(index,work/'index-before.bin');before=git('ls-files','--stage','-z')
staged=set(git('diff','--cached','--name-only').decode().splitlines());shared=set(config.get('sharedPaths',[]))
# An earlier private-index commit intentionally left the locked real index alone.
# Accept its resulting reverse diff only when the exact saved index entry is unchanged.
def entries(data):return {x.split(b'\t',1)[1].decode():x for x in data.split(b'\0') if x}
current_entries=entries(before);pending_owned=set()
for old_receipt in work.parent.glob('*-git-receipt.json'):
 receipt=read(old_receipt);backup=R/receipt.get('privateIndexWork','')/'index-before.bin'
 if not backup.is_file() or not receipt.get('syncWhenUnlocked'):continue
 if subprocess.run(['git','merge-base','--is-ancestor',receipt['commit'],base],cwd=R,capture_output=True).returncode:continue
 old_env=dict(os.environ,GIT_INDEX_FILE=str(backup));saved_entries=entries(git('ls-files','--stage','-z',env=old_env))
 for path in receipt['syncWhenUnlocked']:
  if current_entries.get(path)==saved_entries.get(path):pending_owned.add(path)
# Explicitly inspected staging may remain untouched while our working-file changes
# are committed through the private index. Reject any intervening index changes.
preserved=set(config.get('preservedStaging',{}))
for path,expected in config.get('preservedStaging',{}).items():
 actual=current_entries.get(path)
 assert (actual.decode() if actual is not None else None)==expected,'Reviewed staging changed: '+path
assert not(staged&set(paths)-shared-pending_owned-preserved),'Independent staging on owned path'
env=dict(os.environ,GIT_INDEX_FILE=str(work/'index'));git('read-tree',base,env=env);git('add','--',*paths,env=env)
def head(p):return git('show',base+':'+p).decode('utf-8-sig')
def blob(p,s):
 h=git('hash-object','-w','--stdin',inp=s.encode('utf8')).decode().strip();git('update-index','--cacheinfo','100644,'+h+','+p,env=env)
for p in shared:
 current=read(R/p) if p.endswith('.json') else (R/p).read_text(encoding='utf8')
 if p=='shared/publishing/video-production-control.json':
  d=json.loads(head(p));d.setdefault('scopedBatchAuthorizations',{})[KEY]=current['scopedBatchAuthorizations'][KEY];blob(p,json.dumps(d,ensure_ascii=False,indent=2)+'\n')
 elif p=='shared/publishing/video-worklist.json':
  d=json.loads(head(p));d.setdefault('privateMathPolish',{})['conceptFitRevision']=current['privateMathPolish']['conceptFitRevision'];blob(p,json.dumps(d,ensure_ascii=False,indent=2)+'\n')
 elif p=='docs/VIDEO_WORKFLOW.md':
  old=head(p);line=next(x for x in current.splitlines() if x.startswith('2026-10-23 사용자 지시 `narration-matched-gameplay-v1`'))
  prior=next((x for x in old.splitlines() if x.startswith('2026-10-23 사용자 지시 `narration-matched-gameplay-v1`')),None)
  if prior:old=old.replace(prior,line)
  else:
   marker=next(x for x in old.splitlines() if x.startswith('## 3.'));old=old.replace(marker,marker+'\n\n'+line,1)
  blob(p,old)
 elif p=='docs/GAME_MATH_PRIVATE_POLISH.md':
  # This generated table is wholly owned by the selected math revision.
  blob(p,current)
 elif p=='docs/VIDEO_WORKLIST.md':
  marker='## 이번 게임수학 게임 장면 적합성 수정 (18편)'
  old=head(p);assert marker in current
  section=marker+current.split(marker,1)[1]
  if marker in old:old=old.split(marker,1)[0].rstrip()+'\n\n'+section
  else:old=old.rstrip()+'\n\n'+section
  blob(p,old)
 elif p.endswith('/project.json'):
  d=json.loads(head(p));d['activeConceptFitRevision']=current['activeConceptFitRevision'];blob(p,json.dumps(d,ensure_ascii=False,indent=2)+'\n')
 else:raise RuntimeError('No scoped merger for '+p)
changed=set(git('diff','--cached','--name-only','-z',env=env).decode().split('\0'))-{''};assert changed and changed<=set(paths)
git('diff','--cached','--check',env=env)
subprocess.run(['node','scripts/media-policy.cjs'],cwd=R,env=env,check=True)
save(work/'planned-blobs.json',dict(base=base,paths=sorted(changed),stagedEntries=git('ls-files','--stage',env=env).decode().splitlines(),originalIndexSha256=sha(work/'index-before.bin')))
assert git('rev-parse','HEAD').decode().strip()==base
git('commit','-m',config['message'],env=env);commit=git('rev-parse','HEAD').decode().strip()
sync=[p for p in paths if p not in staged];sync_done=[]
if sync and not (R/'.git/index.lock').exists():git('reset','-q','HEAD','--',*sync);sync_done=sync
def foreign(data):return [x for x in data.split(b'\0') if x and x.split(b'\t',1)[1].decode() not in sync_done]
assert foreign(before)==foreign(git('ls-files','--stage','-z'))
receipt=dict(commit=commit,paths=sorted(changed),privateIndexWork=rel(work),foreignIndexPreserved=True,realIndexSync='complete' if sync==sync_done else 'pending: existing index.lock preserved',syncWhenUnlocked=[p for p in sync if p not in sync_done],push='pending')
save(work.parent/(unit+'-git-receipt.json'),receipt)
branch=git('branch','--show-current').decode().strip();git('push','origin','HEAD:refs/heads/'+branch)
remote=git('ls-remote','origin','refs/heads/'+branch).decode().split()[0];assert remote==commit
receipt.update(remote=remote,push='verified');save(work.parent/(unit+'-git-receipt.json'),receipt)
print(json.dumps(dict(commit=commit,remote=remote,files=len(changed),foreignIndexPreserved=True)))
