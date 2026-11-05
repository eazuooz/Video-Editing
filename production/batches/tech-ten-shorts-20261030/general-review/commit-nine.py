"""Commit only the nine review updates, preserving concurrent index and worktree changes."""
import importlib.util
import json
import os
import subprocess
import tempfile
from pathlib import Path
from render import HERE,WORK,editor

loader=importlib.util.spec_from_file_location('adoption',HERE/'adopt-nine.py')
adoption=importlib.util.module_from_spec(loader)
loader.loader.exec_module(adoption)
ROOT=editor.ROOT
def git(*arguments,env=None,data=None):
    return subprocess.check_output(['git','-c','gc.auto=0','-c','maintenance.auto=false',*arguments],cwd=ROOT,input=data,env=env)
def blob(transform,contents):
    obj=transform(json.loads(contents))
    return git('hash-object','-w','--stdin',data=(json.dumps(obj,ensure_ascii=False,indent=2)+'\n').encode()).strip().decode()
if __name__=='__main__':
    owned=editor.read(WORK/'git-include.json')+[HERE.relative_to(ROOT).as_posix()]
    shared={'shared/publishing/video-production-control.json':adoption.set_control,
            'shared/publishing/shorts-worklist.json':adoption.set_worklist}
    if git('diff','--cached','--name-only','--',*owned).strip():
        raise RuntimeError('A selected file was staged separately; preserve it before committing.')
    with tempfile.TemporaryDirectory(prefix='nine-shorts-review-') as tmp:
        alt=dict(os.environ,GIT_INDEX_FILE=str(Path(tmp)/'index'))
        branch=git('symbolic-ref','HEAD').decode().strip()
        head=git('rev-parse',branch).decode().strip()
        git('read-tree',head,env=alt);git('add','--',*owned,env=alt)
        for path,transform in shared.items():
            sha=blob(transform,git('show',f'{head}:{path}'))
            git('update-index','--add','--cacheinfo','100644',sha,path,env=alt)
        diff=git('diff','--cached','--name-only',head,env=alt).decode('utf8').splitlines()
        assert all(p in shared or p in owned or p.startswith(owned[-1]+'/') for p in diff)
        tree=git('write-tree',env=alt).decode().strip()
        title='Deliver nine retitled Shorts with rope contact and replay seed experiments'
        commit=git('commit-tree',tree,'-p',head,'-m',title).decode().strip()
        git('update-ref','-m','commit: '+title,branch,commit,head)
        git('reset','-q',commit,'--',*owned)
        # Apply only our two scoped JSON transformations to the real currently staged blobs.
        for path,transform in shared.items():
            sha=blob(transform,git('show',':'+path))
            git('update-index','--add','--cacheinfo','100644',sha,path)
        editor.save(WORK/'commit.json',dict(commit=commit,parent=head,files=diff));print(commit)
