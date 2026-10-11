"""Deliver verified L7 permanent deletion, preserving other work and real index."""
from pathlib import Path
import json,hashlib,os,subprocess,copy,argparse
parser=argparse.ArgumentParser();parser.add_argument('--commit',action='store_true');args=parser.parse_args()
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent;E=ROOT/'shared/publishing/polygons-four-game-schedule-20261011';W=ROOT/'shared/output/polygons-git-delivery-v4';W.mkdir(exist_ok=True)
env=dict(os.environ,GIT_INDEX_FILE=str(W/'deletion.index'))
def git(*a,data=None,isolated=True):
 return subprocess.run(['git',*a],cwd=ROOT,env=env if isolated else os.environ,input=data,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True).stdout
read=lambda p:json.loads(p.read_text(encoding='utf8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
base=git('rev-parse','HEAD',isolated=False).decode().strip();branch=git('symbolic-ref','HEAD',isolated=False).decode().strip();index=Path(git('rev-parse','--git-path','index',isolated=False).decode().strip())
if not index.is_absolute():index=ROOT/index
before=sha(index);git('read-tree',base)
deletion=read(E/'L7SXFwn4i2k-permanent-deletion.json')
assert deletion['videoId']=='L7SXFwn4i2k' and deletion['userAnswer']=='기존 L7SXFwn4i2k 영구 삭제 확인'
assert deletion['evidenceSha256']==sha(ROOT/deletion['evidence']) and '업로더가 삭제한 동영상입니다.' in (ROOT/deletion['evidence']).read_text(encoding='utf8')
receipt=read(ROOT/'projects/game-math-polygons-triangulation/publishing/youtube-upload.json');assert receipt['currentVisibility']=='permanently-deleted' and receipt['scheduledAt'] is None
files=['projects/game-math-polygons-triangulation/publishing/youtube-upload.json','projects/game-math-polygons-triangulation/rebuild.json',*(p.relative_to(ROOT).as_posix() for p in E.iterdir() if p.name in ['L7SXFwn4i2k-deleted.txt','L7SXFwn4i2k-deleted-watch.txt','L7SXFwn4i2k-permanent-deletion.json']),Path(__file__).relative_to(ROOT).as_posix()]
git('add','--pathspec-from-file=-','--pathspec-file-nul',data=('\0'.join(files)+'\0').encode())
def base_json(path):return json.loads(git('show',base+':'+path,isolated=False))
def stage_json(path,value):
 blob=git('hash-object','-w','--stdin',data=(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode()).decode().strip()
 git('update-index','--add','--cacheinfo','100644,'+blob+','+path);files.append(path)
qpath=B.relative_to(ROOT).as_posix()+'/queue.json';q=base_json(qpath);working=read(B/'queue.json')
old=next(i for i in q['items'] if i['slug']=='game-math-polygons-triangulation');new=next(i for i in working['items'] if i['slug']==old['slug'])
for k in ['status','baseline']:old[k]=copy.deepcopy(new[k])
old['revision']['baselineDeletionComplete']=True;stage_json(qpath,q)
progresspath=B.relative_to(ROOT).as_posix()+'/cross-game-review-20261011/polygons-v4-current-progress.json';v=base_json(progresspath);v.update(baselineStatus='permanently deleted with current user confirmation',baselineDeletion=deletion);stage_json(progresspath,v)
ledgerpath='shared/publishing/daily-alternating-schedule.json';ledger=base_json(ledgerpath)
def update(v):
 if isinstance(v,dict):
  if v.get('videoId')=='L7SXFwn4i2k':v.update(currentStatus=deletion['status'],deletedAt=deletion['verifiedAt'],deletionEvidence='shared/publishing/polygons-four-game-schedule-20261011/L7SXFwn4i2k-permanent-deletion.json')
  for child in v.values():update(child)
 elif isinstance(v,list):
  for child in v:update(child)
update(ledger);stage_json(ledgerpath,ledger)
subprocess.run(['node','scripts/media-policy.cjs'],cwd=ROOT,env=env,check=True)
tree=git('write-tree').decode().strip();summary=git('diff','--cached','--stat',base).decode('utf8')
record=dict(base=base,tree=tree,paths=files,realIndexBeforeSha256=before,realIndexPreserved=True,unrelatedWorkingQueueLedgerFieldsExcluded=True,videoId=deletion['videoId'],committed=False,summary=summary)
target=W/'deletion-delivery.json'
if args.commit:
 assert git('rev-parse','HEAD',isolated=False).decode().strip()==base
 commit=git('commit-tree',tree,'-p',base,data=b'Record confirmed permanent deletion of replaced polygon lecture\n').decode().strip();git('update-ref',branch,commit,base)
 record.update(committed=True,commit=commit);target.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 git('push','origin',branch);remote=git('ls-remote','origin',branch).decode().split()[0];assert remote==commit;record.update(pushed=True,remoteSha=remote)
record['realIndexAfterSha256']=sha(index);assert record['realIndexAfterSha256']==before
target.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(summary);print(json.dumps({k:record.get(k) for k in ['committed','commit','pushed','remoteSha','realIndexPreserved']},ensure_ascii=False))
