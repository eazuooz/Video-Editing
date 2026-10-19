"""Commit just owned policy transformations against HEAD, not foreign dirty hunks."""
from pathlib import Path
import importlib.util,os,json,subprocess,datetime
H=Path(__file__).parent;R=H.parents[3]
s=importlib.util.spec_from_file_location('policy',H/'update-audio-policy.py');p=importlib.util.module_from_spec(s);s.loader.exec_module(p)
O=R/'shared/output/game-math-euler-axis-angle/git-v4-audio-policy';O.mkdir(exist_ok=True)
extra=['projects/game-math-euler-axis-angle/production/revision-v4/'+n for n in ['update-audio-policy.py','commit-rules.py','remix.py','verify.py']]+['projects/game-math-euler-axis-angle/production/revision-v3/review-final-audio.py','projects/game-math-euler-axis-angle/production/checkpoint.json']
owned=p.FILES+extra
def git(*args,env=None,input=None):
 r=subprocess.run(['git',*args],cwd=R,env=env,input=input,capture_output=True)
 if r.returncode:raise RuntimeError(r.stderr.decode(errors='replace'))
 return r.stdout
def foreign():return [r for r in git('ls-files','--stage','-z').split(b'\0') if r and r.split(b'\t',1)[1].decode() not in owned]
before=foreign();base=git('rev-parse','HEAD').decode().strip()
for name in p.FILES:
 assert git('rev-parse',':'+name)==git('rev-parse','HEAD:'+name),('Foreign staged change in shared path',name)
index=O/'isolated.index';assert not index.exists();env=dict(os.environ,GIT_INDEX_FILE=str(index));git('read-tree',base,env=env)
for name in p.FILES:
 original=git('show',base+':'+name).decode('utf8');transformed=p.transform(name,original).encode('utf8')
 blob=git('hash-object','-w','--stdin',input=transformed).decode().strip();git('update-index','--add','--cacheinfo','100644',blob,name,env=env)
git('add','--',*extra,env=env);git('diff','--cached','--check',env=env)
subprocess.run(['node','scripts/media-policy.cjs'],cwd=R,env=env,check=True)
git('commit','-m','Restore normal game audio for lectures and remove only added BGM',env=env)
commit=git('rev-parse','HEAD').decode().strip();git('reset','-q','HEAD','--',*owned);assert foreign()==before
branch=git('branch','--show-current').decode().strip();git('push','origin','HEAD:refs/heads/'+branch);remote=git('ls-remote','origin','refs/heads/'+branch).decode().split()[0];assert remote==commit
receipt=dict(commit=commit,remoteSha=remote,paths=owned,unrelatedWorktreeHunksPreserved=True,foreignIndexPreserved=True,at=datetime.datetime.now(datetime.timezone.utc).isoformat())
(O/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8');print(json.dumps(receipt))
