"""Commit only this publishing package; preserve foreign staging exactly."""
from pathlib import Path
import subprocess,hashlib,json,sys
ROOT=Path('D:/Github/VideoEditing');HERE=Path(__file__).parent
PREFIX=HERE.relative_to(ROOT).as_posix()+'/'
def git(*args):
 p=subprocess.run(['git',*args],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 if p.returncode:raise RuntimeError((p.stdout+p.stderr).decode('utf-8','replace'))
 return p.stdout
def foreign_index():
 return b'\0'.join(x for x in git('ls-files','--stage','-z').split(b'\0') if x and not x.split(b'\t',1)[1].decode('utf-8').startswith(PREFIX))
if __name__=='__main__':
 paths=sorted(p.relative_to(ROOT).as_posix() for p in HERE.rglob('*') if p.is_file() and 'local' not in p.relative_to(HERE).parts and '__pycache__' not in p.parts and (p.suffix in {'.py','.json','.txt','.md'} or p.name=='.gitignore'))
 assert paths and all(p.startswith(PREFIX) for p in paths)
 before=foreign_index();git('add','--',*paths)
 staged=git('diff','--cached','--name-only','--',*paths).strip()
 if staged:
  git('commit','--only','-m','Record approved animation uploads and publishing progress','--',*paths)
 assert foreign_index()==before,'Foreign index changed'
 head=git('rev-parse','HEAD').decode().strip()
 if '--push' in sys.argv:print(git('push').decode('utf-8','replace').strip())
 print(json.dumps({'commit':head,'ownedFiles':len(paths),'foreignStagingPreserved':True}))
