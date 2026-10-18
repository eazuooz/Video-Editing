"""Selective Shorts commit with a separate index; retain foreign staging."""
from pathlib import Path
import subprocess,os,json,shutil,datetime,sys
R=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parents[1]
unit,message=sys.argv[1:3];O=R/'shared/output/shorts-commits'/unit;O.mkdir(parents=True,exist_ok=True)
assert not (O/'receipt.json').exists(),'Inspect prior receipt before retrying.'
def git(*args,env=None,data=None):
 r=subprocess.run(['git',*args],cwd=R,env=env,input=data,capture_output=True)
 if r.returncode:raise RuntimeError((r.stdout+r.stderr).decode(errors='replace')[-4000:])
 return r.stdout
def rel(p):return p.relative_to(R).as_posix()
control='shared/publishing/video-production-control.json';field='shortsRecurringAuthorization'
paths=[rel(p) for p in P.rglob('*') if p.is_file() and '/local/' not in rel(p) and '__pycache__' not in rel(p) and p.suffix in ['.py','.json','.md','.txt','.srt','.ass','.cjs']]
u=R/'unity/VideoEditing/Assets/VideoScenes'/P.name
if u.exists():paths += [rel(p) for p in u.rglob('*') if p.is_file() and p.suffix in ['.cs','.meta','.unity','.mat','.asset','.asmdef']]
if Path(str(u)+'.meta').exists():paths.append(rel(Path(str(u)+'.meta')))
paths += ['docs/VIDEO_WORKFLOW.md','shared/publishing/shorts-worklist.json']
paths += ['projects/shorts-visible-rewards-300-gold/'+x for x in ['project.json','production/checkpoint.json','production/review-ledger.json','publishing/drive-review.json']]
paths=sorted(set(paths));owned=set(paths)
def foreign():return [x for x in git('ls-files','--stage','-z').split(b'\0') if x and x.split(b'\t',1)[1].decode() not in owned|{control}]
before=foreign();base=git('rev-parse','HEAD').decode().strip();ref=git('symbolic-ref','HEAD').decode().strip()
shutil.copy2(R/'.git/index',O/'index-before.bin')
previous=json.loads(git('show',':'+control));working=json.loads((R/control).read_text(encoding='utf8'));scoped=working[field]
head=json.loads(git('show',base+':'+control));head[field]=scoped
isolated=O/'commit.index';assert not isolated.exists();env=dict(os.environ,GIT_INDEX_FILE=str(isolated))
git('read-tree',base,env=env);git('add','--',*paths,env=env)
def blob(v):return git('hash-object','-w','--stdin',data=(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode()).decode().strip()
git('update-index','--add','--cacheinfo','100644',blob(head),control,env=env)
git('diff','--cached','--check',env=env);subprocess.run(['node','scripts/media-policy.cjs'],cwd=R,env=env,check=True)
changed=[x for x in git('diff','--cached','--name-only','-z',env=env).decode().split('\0') if x];assert changed and set(changed)<=owned|{control}
tree=git('write-tree',env=env).decode().strip();assert git('rev-parse','HEAD').decode().strip()==base,'HEAD changed; rebuild isolated unit from current HEAD.'
commit=git('commit-tree',tree,'-p',base,'-m',message).decode().strip();git('update-ref',ref,commit,base)
receipt=dict(commit=commit,parent=base,paths=changed,remoteSha=None,indexSynchronized=False,mixedControlFieldOnly=field,foreignControlChangesIncluded=False,at=datetime.datetime.now(datetime.timezone.utc).isoformat())
def record():(O/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8')
record();git('reset','-q','HEAD','--',*paths)
previous[field]=scoped;git('update-index','--add','--cacheinfo','100644',blob(previous),control)
assert before==foreign();check=json.loads(git('show',':'+control));check.pop(field,None);previous.pop(field,None);assert check==previous
receipt.update(indexSynchronized=True,foreignIndexPreserved=True);record()
git('push','origin','HEAD:'+ref);remote=git('ls-remote','origin',ref).decode().split()[0];assert remote==commit
receipt['remoteSha']=remote;record();print(json.dumps(receipt))
