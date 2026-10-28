"""Save only this cleanup's audit, leaving unrelated staging byte-for-byte equivalent."""
from pathlib import Path
import subprocess,os,json,hashlib,shutil,datetime
R=Path('D:/Github/VideoEditing');B=Path(__file__).resolve().parent
def git(*args,input=None,env=None):return subprocess.check_output(['git',*args],cwd=R,input=input,env=env)
v=json.loads((B/'verification.json').read_text());assert not v['errors'] and v['deletedFiles']>0
head=git('rev-parse','HEAD').decode().strip();ref=git('symbolic-ref','HEAD').decode().strip()
gd=Path(git('rev-parse','--absolute-git-dir').decode().strip());env=dict(os.environ,GIT_INDEX_FILE=str(gd/'index-media-cleanup-20261028'))
before=git('ls-files','--stage','-z');git('read-tree',head,env=env);paths=[]
for f in sorted(B.iterdir()):
    if not f.is_file() or f.suffix not in {'.py','.ps1','.json','.jsonl','.md'} or f.name.startswith('git-'):continue
    p=f.relative_to(R).as_posix();blob=git('hash-object','-w','--path',p,'--stdin',input=f.read_bytes()).decode().strip()
    git('update-index','--add','--cacheinfo','100644',blob,p,env=env);paths.append(p)
git('diff','--cached','--check',env=env)
subprocess.run(['node','scripts/media-policy.cjs'],cwd=R,env=env,check=True)
assert git('rev-parse','HEAD').decode().strip()==head
backup=gd/('index-before-cleanup-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));shutil.copy2(gd/'index',backup)
tree=git('write-tree',env=env).decode().strip()
commit=git('commit-tree',tree,'-p',head,input=b'Record verified published media cleanup and preserved source files\n').decode().strip()
git('update-ref',ref,commit,head)
def imap(data):return {x.split(b'\t',1)[1].decode():x.split(b'\t',1)[0] for x in data.split(b'\0') if b'\t' in x}
bm=imap(before);cm=imap(git('ls-files','--stage','-z'));owned=[];records=[]
for p in paths:
    # This is a new audit directory; do not overwrite preexisting staging if any.
    if p not in bm and p not in cm:
        owned.append(p);blob=git('rev-parse',commit+':'+p).decode().strip()
        records.append(('100644 '+blob+' 0\t'+p).encode()+b'\0')
git('update-index','-z','--index-info',input=b''.join(records))
am=imap(git('ls-files','--stage','-z'));same={p:v for p,v in cm.items() if p not in owned}=={p:v for p,v in am.items() if p not in owned};assert same
receipt={'baseHead':head,'commit':commit,'paths':paths,'nonOwnedStagingPreserved':same,'backup':str(backup),'indexBeforeSha256':hashlib.sha256(before).hexdigest()}
(B/'git-commit.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8');print(json.dumps(receipt),flush=True)
