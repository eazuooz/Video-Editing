"""Commit only native-motion revision records through a separate Git index."""
from pathlib import Path
import os,subprocess,json,hashlib,sys,shutil
from datetime import datetime
V=Path(__file__).resolve().parent;B=V.parent;R=V.parents[3]
def git(*args,input=None,env=None):return subprocess.check_output(['git',*args],cwd=R,input=input,env=env)
def read(p):return json.loads(p.read_text('utf-8-sig'))
head=git('rev-parse','HEAD').decode().strip();ref=git('symbolic-ref','HEAD').decode().strip()
gd=Path(git('rev-parse','--absolute-git-dir').decode().strip())
env=dict(os.environ,GIT_INDEX_FILE=str(gd/'index-private-math-gameplay-motion-v4'))
before=git('ls-files','--stage','-z');existing={x.split(b'\t',1)[1].decode() for x in before.split(b'\0') if b'\t' in x}
git('read-tree',head,env=env);paths=[]
def stage(path,data):
 blob=git('hash-object','-w','--path',path,'--stdin',input=data).decode().strip()
 git('update-index','--add','--cacheinfo','100644',blob,path,env=env);paths.append(path)
def stage_json(path,d):stage(path,(json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode())
def original(path):return git('show',head+':'+path).decode('utf8')
cp=read(V/'checkpoint.json')
for folder in [V]+[R/'projects'/e['slug']/'production/gameplay-motion-v4' for e in cp['entries']]:
 for f in sorted(folder.glob('*')):
  if f.is_file() and f.suffix in {'.py','.json','.md'} and not f.name.startswith('git-'):
   stage(f.relative_to(R).as_posix(),f.read_bytes())
for f in [B/'assemble-gameplay.py',B/'checkpoint.json']:
 stage(f.relative_to(R).as_posix(),f.read_bytes())
path='shared/publishing/video-production-control.json';d=json.loads(original(path));current=read(R/path)
d.setdefault('scopedBatchAuthorizations',{})[B.name]=current['scopedBatchAuthorizations'][B.name];stage_json(path,d)
path='shared/publishing/video-worklist.json';d=json.loads(original(path));current=read(R/path)
d.setdefault('privateMathPolish',{})['gameplayTimingRevision']=current['privateMathPolish']['gameplayTimingRevision'];stage_json(path,d)
for path,start,end in [
 ('docs/GAME_MATH_PRIVATE_POLISH.md','<!-- GAMEPLAY-20261024-START -->','<!-- GAMEPLAY-20261024-END -->'),
 ('docs/VIDEO_WORKLIST.md','<!-- GAMEPLAY-PRESENCE-AUDIT-20261024-START -->','<!-- GAMEPLAY-PRESENCE-AUDIT-20261024-END -->')]:
 old=original(path);now=(R/path).read_text('utf-8-sig');block=start+now.split(start,1)[1].split(end,1)[0]+end
 if path=='docs/GAME_MATH_PRIVATE_POLISH.md':
  if start in old:old=old.split(start,1)[0]+old.split(end,1)[1]
  old=block+'\n\n'+old.lstrip()
 elif start in old:old=old.split(start,1)[0]+block+old.split(end,1)[1]
 else:old+='\n\n'+block+'\n'
 stage(path,(old.rstrip()+'\n').encode())
git('diff','--cached','--check',env=env)
receipt=dict(baseHead=head,index=env['GIT_INDEX_FILE'],paths=paths,sharedStagingBeforeSha256=hashlib.sha256(before).hexdigest(),rendered=cp['rendered'],changedFramesChecked=cp['ready'])
(V/'git-selection.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Selected',len(paths),'revision files; unrelated staging untouched',flush=True)
if '--commit' in sys.argv:
 assert cp['rendered']==18,'Finish each authorized render or record a separate explicit stopping condition first.'
 assert cp['ready']==18 or all(e['newReviewReady'] or e.get('blockers') for e in cp['entries'])
 assert git('rev-parse','HEAD').decode().strip()==head,'Concurrent commit: rerun preparation.'
 index_backup=gd/('index-before-private-math-motion-v4-'+datetime.now().strftime('%Y%m%d-%H%M%S'))
 shutil.copy2(gd/'index',index_backup)
 receipt['sharedIndexBackup']=str(index_backup)
 tree=git('write-tree',env=env).decode().strip()
 commit=git('commit-tree',tree,'-p',head,input=b'Preserve Game Math lessons and restore source-native gameplay motion\n').decode().strip()
 git('update-ref',ref,commit,head)
 # Synchronize our new records and entries that were exactly the old HEAD.
 # Never replace an actual staged edit/deletion from another task. Leaving
 # untouched old-HEAD entries would otherwise stage an inverse of our commit.
 before_map={x.split(b'\t',1)[1].decode():x.split(b'\t',1)[0] for x in before.split(b'\0') if b'\t' in x}
 current_map={x.split(b'\t',1)[1].decode():x.split(b'\t',1)[0] for x in git('ls-files','--stage','-z').split(b'\0') if b'\t' in x}
 owned=[]
 for path in paths:
  if path not in existing:
   if path not in current_map and (path.startswith(V.relative_to(R).as_posix()+'/') or '/production/gameplay-motion-v4/' in path):owned.append(path)
   continue
  tree_row=git('ls-tree',head,'--',path).strip()
  if not tree_row:continue
  fields=tree_row.split(b'\t',1)[0].split();old_index=fields[0]+b' '+fields[2]+b' 0'
  if before_map.get(path)==old_index and current_map.get(path)==old_index:owned.append(path)
 for path in owned:
  blob=git('rev-parse',commit+':'+path).decode().strip();git('update-index','--add','--cacheinfo','100644',blob,path)
 def other(data):return sorted(x for x in data.split(b'\0') if x and x.split(b'\t',1)[1].decode() not in owned)
 after=git('ls-files','--stage','-z');unchanged=other(before)==other(after)
 receipt.update(commit=commit,newOrPreviouslyUnstagedPathsSynchronized=owned,nonOwnedStagingPreserved=unchanged,sharedStagingAfterSha256=hashlib.sha256(after).hexdigest())
 (V/'git-commit.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print('Committed',commit,'non-owned staging preserved:',unchanged,flush=True)
