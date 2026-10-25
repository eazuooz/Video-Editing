"""Commit only observed publishing records, preserving all unrelated staging."""
from pathlib import Path
import subprocess, os, json, hashlib, shutil, sys, datetime
R=Path('D:/Github/VideoEditing'); B=Path(__file__).resolve().parent
def git(*args,input=None,env=None):
    return subprocess.check_output(['git',*args],cwd=R,input=input,env=env)
def read(p): return json.loads(p.read_text('utf-8-sig'))
head=git('rev-parse','HEAD').decode().strip(); ref=git('symbolic-ref','HEAD').decode().strip()
gd=Path(git('rev-parse','--absolute-git-dir').decode().strip())
env=dict(os.environ,GIT_INDEX_FILE=str(gd/'index-private-math-publishing-20261026'))
before=git('ls-files','--stage','-z'); git('read-tree',head,env=env); paths=[]
def original(p): return git('show',head+':'+p).decode('utf8')
def stage(p,data):
    blob=git('hash-object','-w','--path',p,'--stdin',input=data).decode().strip()
    git('update-index','--add','--cacheinfo','100644',blob,p,env=env); paths.append(p)
def stagejson(p,d): stage(p,(json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode())
cp=read(B/'checkpoint.json')
assert cp['scheduled']==18 and cp['status']=='scheduled-duplicate-deletion-confirmation-pending'
for f in sorted(B.rglob('*')):
    if f.is_file() and f.suffix in ['.py','.json','.txt','.md'] and not f.name.startswith('git-') and '__pycache__' not in f.parts:
        stage(f.relative_to(R).as_posix(),f.read_bytes())
p='shared/publishing/video-production-control.json'; d=json.loads(original(p)); c=read(R/p)
d.setdefault('scopedPublishingAuthorizations',{})[B.name]=c['scopedPublishingAuthorizations'][B.name]; stagejson(p,d)
p='shared/publishing/video-worklist.json'; d=json.loads(original(p)); c=read(R/p)
d['privateMathPolish']['publishingRevision']=c['privateMathPolish']['publishingRevision']; stagejson(p,d)
start='<!-- MATH-PUBLISHING-20261026-START -->'; end='<!-- MATH-PUBLISHING-20261026-END -->'
for name in ['GAME_MATH_PRIVATE_POLISH.md','VIDEO_WORKLIST.md']:
    p='docs/'+name; old=original(p); current=(R/p).read_text('utf8')
    block=start+current.split(start,1)[1].split(end,1)[0]+end+'\n\n'
    if start in old: projected=old.split(start,1)[0]+block+old.split(end,1)[1].lstrip('\n')
    else: projected=block+old
    stage(p,projected.encode())
git('diff','--cached','--check',env=env)
subprocess.run(['node','scripts/media-policy.cjs'],cwd=R,env=env,check=True)
receipt=dict(baseHead=head,paths=paths,index=env['GIT_INDEX_FILE'],beforeIndexSha256=hashlib.sha256(before).hexdigest())
(B/'git-selection.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Selected',len(paths),'owned files; other staging untouched.',flush=True)
if '--commit' in sys.argv:
    assert git('rev-parse','HEAD').decode().strip()==head
    backup=gd/('index-before-math-publishing-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S')); shutil.copy2(gd/'index',backup)
    tree=git('write-tree',env=env).decode().strip()
    commit=git('commit-tree',tree,'-p',head,input=b'Record 18 scheduled math uploads and exact duplicate removal queue\n').decode().strip()
    git('update-ref',ref,commit,head)
    def imap(data): return {x.split(b'\t',1)[1].decode():x.split(b'\t',1)[0] for x in data.split(b'\0') if b'\t' in x}
    bm=imap(before); cm=imap(git('ls-files','--stage','-z')); owned=[]; records=[]
    for p in paths:
        tr=git('ls-tree',head,'--',p).strip()
        if not tr: allowed=p not in bm and p not in cm
        else:
            f=tr.split(b'\t',1)[0].split(); expected=f[0]+b' '+f[2]+b' 0'
            allowed=bm.get(p)==expected and cm.get(p)==expected
        if allowed:
            owned.append(p); blob=git('rev-parse',commit+':'+p).decode().strip()
            records.append(('100644 '+blob+' 0\t'+p).encode()+b'\0')
    git('update-index','-z','--index-info',input=b''.join(records))
    am=imap(git('ls-files','--stage','-z'))
    same={p:v for p,v in cm.items() if p not in owned}=={p:v for p,v in am.items() if p not in owned}; assert same
    receipt.update(commit=commit,backup=str(backup),synchronized=owned,nonOwnedStagingPreserved=same)
    (B/'git-commit.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(commit,flush=True)
