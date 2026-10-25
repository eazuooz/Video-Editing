"""Own M14 changes only; preserve unrelated staged cleanup and shared edits."""
from pathlib import Path
import os,subprocess,json,hashlib,sys,shutil
from datetime import datetime
B=Path(__file__).resolve().parent;R=B.parents[3];H=R/'projects/game-math-polygon-partition-v2/production/gameplay-abstract-v5'
def git(*a,input=None,env=None):return subprocess.check_output(['git',*a],cwd=R,input=input,env=env)
def read(p):return json.loads(p.read_text('utf-8-sig'))
head=git('rev-parse','HEAD').decode().strip();ref=git('symbolic-ref','HEAD').decode().strip();gd=Path(git('rev-parse','--absolute-git-dir').decode().strip());env=dict(os.environ,GIT_INDEX_FILE=str(gd/'index-m14-gameplay-abstract-v5'))
before=git('ls-files','--stage','-z');git('read-tree',head,env=env);paths=[]
def original(p):return git('show',head+':'+p).decode('utf8')
def stage(p,data):
 blob=git('hash-object','-w','--path',p,'--stdin',input=data).decode().strip();git('update-index','--add','--cacheinfo','100644',blob,p,env=env);paths.append(p)
def stagejson(p,d):stage(p,(json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode())
for folder in [B,H]:
 for f in sorted(folder.glob('*')):
  if f.is_file() and f.suffix in {'.py','.json','.txt'} and not f.name.startswith('git-'):stage(f.relative_to(R).as_posix(),f.read_bytes())
stage((B.parent/'checkpoint.json').relative_to(R).as_posix(),(B.parent/'checkpoint.json').read_bytes())
p='shared/publishing/video-production-control.json';d=json.loads(original(p));c=read(R/p)
d['actualGameAbstractPolicy']=c['actualGameAbstractPolicy'];d.setdefault('scopedBatchAuthorizations',{})['m14-gameplay-abstract-v5']=c['scopedBatchAuthorizations']['m14-gameplay-abstract-v5']
for k in ['status','reviewReady','rendered','checkpoint','m14Revision']:d['scopedBatchAuthorizations']['private-math-gameplay-20261024']['latestRevision'][k]=c['scopedBatchAuthorizations']['private-math-gameplay-20261024']['latestRevision'][k]
stagejson(p,d)
p='shared/publishing/video-worklist.json';d=json.loads(original(p));c=read(R/p);d['privateMathPolish']['gameplayTimingRevision']=c['privateMathPolish']['gameplayTimingRevision'];stagejson(p,d)
for p,start,end in [('docs/GAME_MATH_PRIVATE_POLISH.md','<!-- GAMEPLAY-20261024-START -->','<!-- GAMEPLAY-20261024-END -->'),('docs/VIDEO_WORKLIST.md','<!-- GAMEPLAY-PRESENCE-AUDIT-20261024-START -->','<!-- GAMEPLAY-PRESENCE-AUDIT-20261024-END -->')]:
 old=original(p);current=(R/p).read_text('utf8');block=start+current.split(start,1)[1].split(end,1)[0]+end;assert start in old and end in old;stage(p,(old.split(start,1)[0]+block+old.split(end,1)[1]).encode())
p='docs/VIDEO_WORKFLOW.md';old=original(p);current=(R/p).read_text('utf8');start='### 실제 게임으로 여는 Abstract';end='다음 표를 채운 설계가 제작의 입력이다.';section=current.split(start,1)[1].split(end,1)[0].rstrip();assert start not in old;old=old.replace(end,start+section+'\n\n'+end,1);stage(p,old.encode())
p='AGENTS.md';old=original(p);current=(R/p).read_text('utf8');needle='- After the original 2-second branding';line=next(s for s in current.splitlines() if 'actual-game-thesis-abstract-v1' in s and 'After the original 2-second branding' in s);lines=old.splitlines(keepends=True);n=0
for i,s in enumerate(lines):
 if s.startswith(needle):lines[i]=line+'\n';n+=1
assert n==1;stage(p,''.join(lines).encode())
git('diff','--cached','--check',env=env)
assert read(B/'checkpoint.json')['status']=='local-human-review-pending'
receipt=dict(baseHead=head,paths=paths,index=env['GIT_INDEX_FILE'],beforeIndexSha256=hashlib.sha256(before).hexdigest());(B/'git-selection.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(git('diff','--cached','--stat',env=env).decode('utf8'),flush=True)
if '--commit' in sys.argv:
 assert git('rev-parse','HEAD').decode().strip()==head
 backup=gd/('index-before-m14-abstract-'+datetime.now().strftime('%Y%m%d-%H%M%S'));shutil.copy2(gd/'index',backup)
 tree=git('write-tree',env=env).decode().strip();commit=git('commit-tree',tree,'-p',head,input=b'Finish M14 square-cut gameplay and add real-game thesis abstract\n').decode().strip();git('update-ref',ref,commit,head)
 def indexmap(data):return {x.split(b'\t',1)[1].decode():x.split(b'\t',1)[0] for x in data.split(b'\0') if b'\t' in x}
 bm=indexmap(before);cm=indexmap(git('ls-files','--stage','-z'));owned=[]
 for p in paths:
  tr=git('ls-tree',head,'--',p).strip()
  if not tr:
   if p not in bm and p not in cm:owned.append(p)
  else:
   f=tr.split(b'\t',1)[0].split();expected=f[0]+b' '+f[2]+b' 0'
   if bm.get(p)==expected and cm.get(p)==expected:owned.append(p)
 for p in owned:git('update-index','--add','--cacheinfo','100644',git('rev-parse',commit+':'+p).decode().strip(),p)
 after=git('ls-files','--stage','-z');am=indexmap(after);nonownedSame={p:v for p,v in bm.items() if p not in owned}=={p:v for p,v in am.items() if p not in owned}
 receipt.update(commit=commit,backup=str(backup),synchronized=owned,nonOwnedStagingPreserved=nonownedSame,afterIndexSha256=hashlib.sha256(after).hexdigest());(B/'git-commit.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(commit,'non-owned staging preserved',nonownedSame,flush=True)
