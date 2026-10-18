"""Commit only this Short and its scoped rules; preserve mixed foreign control."""
from pathlib import Path
import subprocess,os,json,hashlib,shutil,datetime,sys
R=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parents[1]
unit=sys.argv[1];message=sys.argv[2];O=R/'shared/output/shorts-commits'/unit;O.mkdir(parents=True,exist_ok=True)
assert not (O/'receipt.json').exists(),'Inspect prior actual receipt; do not duplicate a commit.'
def git(*args,env=None,data=None):
 r=subprocess.run(['git',*args],cwd=R,env=env,input=data,capture_output=True)
 if r.returncode:raise RuntimeError((r.stdout+r.stderr).decode(errors='replace')[-4000:])
 return r.stdout
def rel(p):return p.relative_to(R).as_posix()
control='shared/publishing/video-production-control.json';field='shortsRecurringAuthorization'
paths=sorted(rel(p) for p in P.rglob('*') if p.is_file() and '/local/' not in rel(p) and '__pycache__' not in rel(p) and p.suffix in ['.py','.json','.md','.txt','.srt','.ass','.cjs'])
paths+=['docs/VIDEO_WORKFLOW.md','shared/publishing/shorts-worklist.json'];owned=set(paths)
def foreign():return [x for x in git('ls-files','--stage','-z').split(b'\0') if x and x.split(b'\t',1)[1].decode() not in owned|{control}]
before=foreign();base=git('rev-parse','HEAD').decode().strip();ref=git('symbolic-ref','HEAD').decode().strip()
index=R/'.git/index';shutil.copy2(index,O/'index-before.bin')
previous_control=json.loads(git('show',':'+control));working_control=json.loads((R/control).read_text(encoding='utf8'));scoped=working_control[field]
head_control=json.loads(git('show',base+':'+control));head_control[field]=scoped
isolated=O/'commit.index';assert not isolated.exists();env=dict(os.environ,GIT_INDEX_FILE=str(isolated))
git('read-tree',base,env=env);git('add','--',*paths,env=env)
def blob(value):return git('hash-object','-w','--stdin',data=(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode()).decode().strip()
git('update-index','--add','--cacheinfo','100644',blob(head_control),control,env=env)
git('diff','--cached','--check',env=env)
subprocess.run(['node','scripts/media-policy.cjs'],cwd=R,env=env,check=True)
changed=git('diff','--cached','--name-only','-z',env=env).decode().split('\0');changed=[x for x in changed if x];assert changed and set(changed)<=owned|{control}
tree=git('write-tree',env=env).decode().strip();assert git('rev-parse','HEAD').decode().strip()==base,'Another task committed; rebuild this isolated unit from the new HEAD.'
commit=git('commit-tree',tree,'-p',base,'-m',message).decode().strip();git('update-ref',ref,commit,base)
receipt=dict(commit=commit,parent=base,paths=changed,remoteSha=None,indexSynchronized=False,mixedControlFieldOnly=field,foreignControlChangesIncluded=False,at=datetime.datetime.now(datetime.timezone.utc).isoformat())
(O/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8')
git('reset','-q','HEAD','--',*paths)
# Add only our now-committed field to the previously staged control version.
# Its foreign staged content remains staged rather than being reset to HEAD.
next_control=dict(previous_control);next_control[field]=scoped;git('update-index','--add','--cacheinfo','100644',blob(next_control),control)
assert before==foreign();check=json.loads(git('show',':'+control));check.pop(field,None);prior=dict(previous_control);prior.pop(field,None);assert check==prior
receipt['indexSynchronized']=True;receipt['foreignIndexPreserved']=True
(O/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8')
branch=ref.removeprefix('refs/heads/');git('push','origin','HEAD:'+ref);remote=git('ls-remote','origin',ref).decode().split()[0];assert remote==commit
receipt['remoteSha']=remote;(O/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8');print(json.dumps(receipt))
