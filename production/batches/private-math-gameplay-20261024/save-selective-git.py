"""Prepare a private index containing only this revision; never rewrite shared staging."""
from pathlib import Path
import os,subprocess,json,hashlib,sys,shutil
B=Path(__file__).resolve().parent;R=B.parents[2]
def git(*args,input=None,env=None):return subprocess.check_output(['git',*args],cwd=R,input=input,env=env)
def rd(p):return json.loads(p.read_text('utf-8-sig'))
head=git('rev-parse','HEAD').decode().strip();ref=git('symbolic-ref','HEAD').decode().strip()
gd=Path(git('rev-parse','--absolute-git-dir').decode().strip());shared=gd/'index'
before=hashlib.sha256(shared.read_bytes()).hexdigest()
shared_entries=git('ls-files','--stage','-z').split(b'\0')
shutil.copy2(shared,gd/'index.before-private-math-gameplay-20261024')
env=dict(os.environ,GIT_INDEX_FILE=str(gd/'index-private-math-gameplay-20261024'))
git('read-tree',head,env=env);paths=[]
def stage(path,data):
 sha=git('hash-object','-w','--path',path,'--stdin',input=data).decode().strip()
 git('update-index','--add','--cacheinfo','100644',sha,path,env=env);paths.append(path)
def stage_json(path,value):stage(path,(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode())
def original(path):return git('show',head+':'+path).decode('utf8')
c=rd(B/'checkpoint.json');assert c['ready']==18
for folder in [B]+[R/'projects'/e['slug']/'production/gameplay-v3' for e in c['entries']]:
 for p in sorted(folder.iterdir()):
  if p.is_file() and p.suffix in {'.py','.json','.md','.html'} and not p.name.startswith('git-'):
   stage(p.relative_to(R).as_posix(),p.read_bytes())
for e in c['entries']:
 p=R/'projects'/e['slug']/'rebuild.json';stage(p.relative_to(R).as_posix(),p.read_bytes())
path='shared/publishing/video-production-control.json';d=json.loads(original(path));current=rd(R/path)
d.setdefault('scopedBatchAuthorizations',{})[B.name]=current['scopedBatchAuthorizations'][B.name];stage_json(path,d)
path='shared/publishing/video-worklist.json';d=json.loads(original(path));current=rd(R/path)
d.setdefault('privateMathPolish',{})['gameplayTimingRevision']=current['privateMathPolish']['gameplayTimingRevision'];stage_json(path,d)
path='docs/GAME_MATH_PRIVATE_POLISH.md';old=original(path);now=(R/path).read_text('utf-8-sig');start='<!-- GAMEPLAY-20261024-START -->';end='<!-- GAMEPLAY-20261024-END -->'
block=start+now.split(start,1)[1].split(end,1)[0]+end
if start in old:old=old.split(start,1)[0]+block+old.split(end,1)[1]
else:old+='\n\n'+block+'\n'
stage(path,old.encode())
path='docs/VIDEO_WORKLIST.md';old=original(path);now=(R/path).read_text('utf-8-sig');block=now.split('## 최신 게임수학 게임 장면·표식 수정',1)[1].split('\n---\n',1)[0]
old=old.split('\n',1)[0]+'\n\n## 최신 게임수학 게임 장면·표식 수정'+block+'\n---\n'+old.split('\n',1)[1];stage(path,old.encode())
path='scripts/render-video-worklist.py';old=original(path);now=(R/path).read_text('utf-8-sig');needle="(R/'docs/VIDEO_WORKLIST.md').write_text"
block=now.split("gameplay=(polish or {}).get('gameplayTimingRevision')",1)[1].split(needle,1)[0]
old=old.replace(needle,"gameplay=(polish or {}).get('gameplayTimingRevision')"+block+needle);stage(path,old.encode())
git('diff','--cached','--check',env=env)
receipt=dict(baseHead=head,ref=ref,index=str(env['GIT_INDEX_FILE']),sharedIndexBefore=before,paths=paths)
(B/'git-selection.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(git('diff','--cached','--stat',env=env).decode('utf8'))
if '--commit' in sys.argv:
 assert git('rev-parse','HEAD').decode().strip()==head,'Another commit landed; prepare again against it.'
 tree=git('write-tree',env=env).decode().strip()
 commit=git('commit-tree',tree,'-p',head,input=b'Polish Game Math gameplay examples, guides and local review deliveries\n').decode().strip()
 git('update-ref',ref,commit,head)
 # Only newly owned revision records are synchronized. Shared documents and
 # pre-existing manifests may contain another task's staged edits/deletions.
 owned=[p for p in paths if p.startswith(B.relative_to(R).as_posix()+'/') or '/production/gameplay-v3/' in p]
 existing={x.split(b'\t',1)[1].decode() for x in shared_entries if b'\t' in x}
 owned=[p for p in owned if p not in existing]
 for path in owned:
  blob=git('rev-parse',commit+':'+path).decode().strip();git('update-index','--add','--cacheinfo','100644',blob,path)
 def outside(rows):return sorted(x for x in rows if x and x.split(b'\t',1)[1].decode() not in owned)
 unchanged=outside(shared_entries)==outside(git('ls-files','--stage','-z').split(b'\0'))
 assert unchanged,'Non-owned staging changed concurrently; inspect without restoring over it.'
 receipt.update(commit=commit,sharedIndexAfter=hashlib.sha256(shared.read_bytes()).hexdigest(),newOwnedPathsSynchronized=owned,nonOwnedStagingPreserved=unchanged)
 (B/'git-commit.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print('Committed',commit,'unrelated staging preserved:',unchanged)
