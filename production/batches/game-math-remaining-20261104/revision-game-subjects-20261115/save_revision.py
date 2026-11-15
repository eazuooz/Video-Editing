"""Isolated index; only this revision's code and exact shared leaves."""
import argparse,copy,json,os,runpy,subprocess,tempfile
from pathlib import Path
from subject_revision import HERE,ROOT,EPISODES
def git(*args,data=None,env=None):return subprocess.check_output(['git','-c','core.safecrlf=false',*args],cwd=ROOT,input=data,env=env)
def project(path,base,current):
 a=base.decode('utf-8-sig');b=current.decode('utf-8-sig')
 if path.endswith('.md'):
  key='GAME-SUBJECT-CONTINUITY-20261115' if path.endswith('VIDEO_WORKFLOW.md') else 'MATH-GAME-SUBJECTS-20261115';start='<!-- '+key+' -->';end='<!-- '+key+'-END -->';block=b[b.index(start):b.index(end)+len(end)]
  return (a[:a.index(start)]+block+a[a.index(end)+len(end):] if start in a else a.rstrip()+'\n\n'+block+'\n').encode('utf8')
 a=json.loads(a);b=json.loads(b)
 if path.endswith('review-ledger.json'):a['gameSubjectRevision20261115']=copy.deepcopy(b['gameSubjectRevision20261115'])
 elif path.endswith('video-production-control.json'):a['explicitMathRemainingBatch20261104']['gameSubjectRevision20261115']=copy.deepcopy(b['explicitMathRemainingBatch20261104']['gameSubjectRevision20261115'])
 else:
  a['mathGameSubjects20261115']=copy.deepcopy(b['mathGameSubjects20261115'])
  rows={r['id']:r['gameSubjects20261115'] for r in b['rows'] if 'gameSubjects20261115' in r}
  for r in a['rows']:
   if r['id'] in rows:r['gameSubjects20261115']=copy.deepcopy(rows[r['id']])
 return (json.dumps(a,ensure_ascii=False,indent=2)+'\n').encode('utf8')
def main(message,push):
 helper=runpy.run_path(str(ROOT/'projects/buckshot-roulette-reverse-engineering/production/save-selective-git.py'));publish=helper['publish_index_and_ref']
 head=git('rev-parse','HEAD').decode().strip();ref=git('symbolic-ref','HEAD').decode().strip();index=Path(git('rev-parse','--path-format=absolute','--git-path','index').decode().strip());original=index.read_bytes()
 direct=[p for p in HERE.iterdir() if p.suffix in ('.py','.json','.md')]
 shared=['shared/publishing/video-production-control.json','shared/publishing/video-worklist.json','docs/VIDEO_WORKFLOW.md','docs/VIDEO_WORKLIST.md']
 for e in EPISODES.values():
  path='projects/'+e['slug']+'/production/review-ledger.json'
  if 'gameSubjectRevision20261115' in json.loads((ROOT/path).read_text(encoding='utf-8-sig')):shared.append(path)
 with tempfile.TemporaryDirectory() as temp:
  ce=dict(os.environ,GIT_INDEX_FILE=str(Path(temp)/'commit.index'));re=dict(os.environ,GIT_INDEX_FILE=str(Path(temp)/'reconcile.index'));git('read-tree',head,env=ce);Path(re['GIT_INDEX_FILE']).write_bytes(original);buffers={x['GIT_INDEX_FILE']:bytearray() for x in (ce,re)}
  def stage(path,data,env):
   data=data.replace(b'\r\n',b'\n');oid=git('hash-object','-w','--stdin',data=data).decode().strip();buffers[env['GIT_INDEX_FILE']].extend(f'100644 {oid}\t{path}\0'.encode('utf8'))
  for p in direct:
   data=p.read_bytes();rel=p.relative_to(ROOT).as_posix()
   if p.suffix=='.json':json.loads(data.decode('utf-8-sig'))
   if p.suffix=='.py':compile(data,str(p),'exec')
   for env in (ce,re):stage(rel,data,env)
  for path in shared:
   current=(ROOT/path).read_bytes()
   for env,revision in ((ce,head+':'+path),(re,':'+path)):stage(path,project(path,git('show',revision),current),env)
  for env in (ce,re):git('update-index','-z','--index-info',env=env,data=bytes(buffers[env['GIT_INDEX_FILE']]))
  git('diff','--cached','--check',env=ce);subprocess.run(['node','scripts/media-policy.cjs'],cwd=ROOT,env=ce,check=True)
  changed=git('diff','--cached','--name-only',head,env=ce).decode().splitlines()
  if not changed:print('No scoped changes');return
  tree=git('write-tree',env=ce).decode().strip();commit=git('commit-tree',tree,'-p',head,data=(message+'\n').encode('utf8')).decode().strip();publish(index,Path(re['GIT_INDEX_FILE']).read_bytes(),original,ref,head,commit);print(commit,len(changed),'scoped files; unrelated staging preserved')
 if push:subprocess.run(['git','push','origin',ref],cwd=ROOT,check=True)
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--message',required=True);ap.add_argument('--push',action='store_true');a=ap.parse_args();main(a.message,a.push)
