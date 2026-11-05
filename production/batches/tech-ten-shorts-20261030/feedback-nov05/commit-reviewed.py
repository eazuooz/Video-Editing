"""Commit the updated ten rows only, without committing another task's worklist edits or staged files."""
from adopt import *
import os,tempfile
def git(*args,env=None,data=None):return sp.check_output(['git','-c','gc.auto=0','-c','maintenance.auto=false',*args],cwd=ROOT,input=data,env=env)
def main():
    wl='shared/publishing/shorts-worklist.json'
    area=HERE.relative_to(ROOT).as_posix()
    owned=read(WORK/'git-include.json')+[area]
    # All these records must be unstaged in the main index. Leave unrelated paths alone.
    assert not git('diff','--cached','--name-only','--',*owned,wl).strip()
    with tempfile.TemporaryDirectory(prefix='yamyam-tech-ten-index-') as td:
        env=dict(os.environ,GIT_INDEX_FILE=str(Path(td)/'index'))
        branch=git('symbolic-ref','HEAD').strip().decode();base=git('rev-parse',branch).strip().decode()
        git('read-tree',base,env=env);git('add','--',*owned,env=env)
        old=json.loads(git('show',base+':'+wl));new=worklist(old)
        data=(json.dumps(new,ensure_ascii=False,indent=2)+'\n').encode()
        blob=git('hash-object','-w','--stdin',data=data).strip().decode()
        git('update-index','--add','--cacheinfo','100644',blob,wl,env=env)
        changes=git('diff','--cached','--name-only',base,'--',env=env).decode('utf8').splitlines()
        assert changes and all(c==wl or c in owned or c.startswith(area+'/') for c in changes)
        tree=git('write-tree',env=env).strip().decode();msg='Deliver ten revised Shorts with verified script-review playback'
        commit=git('commit-tree',tree,'-p',base,'-m',msg).strip().decode()
        git('update-ref','-m','commit: '+msg,branch,commit,base)
        git('reset','-q',commit,'--',*owned,wl)
        save(WORK/'commit-reviewed.json',dict(commit=commit,parent=base,files=changes));print(commit)
if __name__=='__main__':main()
