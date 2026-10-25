"""Commit only this finite math batch, preserving all other staged work."""
from pathlib import Path
import subprocess,os,json,hashlib,shutil,sys,datetime
R=Path('D:/Github/VideoEditing');B=Path(__file__).resolve().parent
def git(*args,input=None,env=None):return subprocess.check_output(['git',*args],cwd=R,input=input,env=env)
def read(p):return json.loads(p.read_text('utf-8-sig'))
head=git('rev-parse','HEAD').decode().strip();ref=git('symbolic-ref','HEAD').decode().strip();gd=Path(git('rev-parse','--absolute-git-dir').decode().strip());env=dict(os.environ,GIT_INDEX_FILE=str(gd/'index-private-math-abstracts-20261025'));before=git('ls-files','--stage','-z');git('read-tree',head,env=env);paths=[]
def original(p):return git('show',head+':'+p).decode('utf8')
def stage(p,data):
 blob=git('hash-object','-w','--path',p,'--stdin',input=data).decode().strip();git('update-index','--add','--cacheinfo','100644',blob,p,env=env);paths.append(p)
def stagejson(p,d):stage(p,(json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode())
cp=read(B/'checkpoint.json')
for folder in [B]+[R/'projects'/e['slug']/'production/actual-abstract-v6' for e in cp['entries'] if e['id']!='M14']:
 for f in sorted(folder.rglob('*')):
  if f.is_file() and f.suffix in ['.py','.json'] and not f.name.startswith('git-') and '__pycache__' not in f.parts:stage(f.relative_to(R).as_posix(),f.read_bytes())
p='shared/publishing/video-production-control.json';d=json.loads(original(p));c=read(R/p);d.setdefault('scopedBatchAuthorizations',{})[B.name]=c['scopedBatchAuthorizations'][B.name];d['actualGameAbstractPolicy']['scope']=c['actualGameAbstractPolicy']['scope'];stagejson(p,d)
p='shared/publishing/video-worklist.json';d=json.loads(original(p));c=read(R/p);d['privateMathPolish']['abstractRevision']=c['privateMathPolish']['abstractRevision']
for e in c['privateMathPolish']['gameplayTimingRevision']['entries']:
 if e['id']=='M14':continue
 target=next(x for x in d['privateMathPolish']['gameplayTimingRevision']['entries'] if x['id']==e['id'])
 for k in ['preAbstractOutput','preAbstractMasterSha256','newOutput','masterSha256','abstractRevision','abstractSeconds','humanReview']:
  if k in e:target[k]=e[k]
stagejson(p,d)
for p,start,end in [('docs/GAME_MATH_PRIVATE_POLISH.md','<!-- GAMEPLAY-20261024-START -->','<!-- GAMEPLAY-20261024-END -->'),('docs/VIDEO_WORKLIST.md','<!-- GAMEPLAY-PRESENCE-AUDIT-20261024-START -->','<!-- GAMEPLAY-PRESENCE-AUDIT-20261024-END -->')]:
 old=original(p);current=(R/p).read_text('utf8');block=start+current.split(start,1)[1].split(end,1)[0]+end;stage(p,(old.split(start,1)[0]+block+old.split(end,1)[1]).encode())
p='docs/VIDEO_WORKFLOW.md';old=original(p);current=(R/p).read_text('utf8');start='### 실제 게임으로 여는 Abstract';end='다음 표를 채운 설계가 제작의 입력이다.';assert start in old;section=current.split(start,1)[1].split(end,1)[0];stage(p,(old.split(start,1)[0]+start+section+end+old.split(end,1)[1]).encode())
p='AGENTS.md';old=original(p);current=(R/p).read_text('utf8');line=next(x for x in current.splitlines() if 'actual-game-thesis-abstract-v1' in x);lines=old.splitlines(keepends=True);count=0
for i,s in enumerate(lines):
 if 'actual-game-thesis-abstract-v1' in s:lines[i]=line+'\n';count+=1
assert count==1;stage(p,''.join(lines).encode())
git('diff','--cached','--check',env=env)
subprocess.run(['node','scripts/media-policy.cjs'],cwd=R,env=env,check=True)
receipt=dict(baseHead=head,paths=paths,index=env['GIT_INDEX_FILE'],beforeIndexSha256=hashlib.sha256(before).hexdigest());(B/'git-selection.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Selected',len(paths),'owned files; other staging untouched.',flush=True)
if '--commit' in sys.argv:
 assert cp['ready']==18 and cp['status']=='local-human-review-pending'
 assert git('rev-parse','HEAD').decode().strip()==head
 backup=gd/('index-before-math-abstracts-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));shutil.copy2(gd/'index',backup)
 tree=git('write-tree',env=env).decode().strip();commit=git('commit-tree',tree,'-p',head,input=b'Add actual-game thesis openings to all 18 math review videos\n').decode().strip();git('update-ref',ref,commit,head)
 def imap(data):return {x.split(b'\t',1)[1].decode():x.split(b'\t',1)[0] for x in data.split(b'\0') if b'\t' in x}
 bm=imap(before);cm=imap(git('ls-files','--stage','-z'));owned=[];records=[]
 for p in paths:
  tr=git('ls-tree',head,'--',p).strip();allowed=False
  if not tr:allowed=p not in bm and p not in cm
  else:
   f=tr.split(b'\t',1)[0].split();expected=f[0]+b' '+f[2]+b' 0';allowed=bm.get(p)==expected and cm.get(p)==expected
  if allowed:
   owned.append(p);blob=git('rev-parse',commit+':'+p).decode().strip();records.append(('100644 '+blob+' 0\t'+p).encode()+b'\0')
 git('update-index','-z','--index-info',input=b''.join(records))
 am=imap(git('ls-files','--stage','-z'));same={p:v for p,v in cm.items() if p not in owned}=={p:v for p,v in am.items() if p not in owned};assert same
 receipt.update(commit=commit,backup=str(backup),synchronized=owned,nonOwnedStagingPreserved=same);(B/'git-commit.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(commit,flush=True)
