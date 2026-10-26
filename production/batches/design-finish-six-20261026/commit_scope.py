"""Commit only this finite batch while preserving unrelated index/shared edits."""
from pathlib import Path
import argparse, ast, copy, json, os, subprocess, uuid

R=Path(__file__).resolve().parents[3]
B='production/batches/design-finish-six-20261026/'
SLUGS=['limited-color-world','computer-controlled-players','in-game-cutscenes','start-with-climax','kind-to-beginners','respect-player-time']
IDS=['D25','D26','D27','D28','D29','D30']
C='shared/publishing/video-production-control.json';W='shared/publishing/video-worklist.json';D='docs/VIDEO_WORKLIST.md';G='.gitignore'
CONFIG='motion-canvas/vite.design-finish-six.config.ts'
PREFIXES=[B]+['projects/'+s+'/' for s in SLUGS]+['motion-canvas/src/projects/'+s+'/batch-v1/' for s in SLUGS]
OWNIGNORE=['/projects/'+s+'/production/local/' for s in SLUGS]
ap=argparse.ArgumentParser();ap.add_argument('--paths',required=True);ap.add_argument('--message',required=True);args=ap.parse_args()
paths=json.loads(Path(args.paths).read_text('utf-8-sig'))
assert len(paths)==len(set(paths)) and all(any(p.startswith(x) for x in PREFIXES) or p in [C,W,D,G,CONFIG] for p in paths)
assert not any('/production/local/' in p or Path(p).suffix.lower() in ['.mp4','.wav','.mp3','.webm','.zip','.png','.jpg'] for p in paths)
helper=ast.parse((R/'unity/VideoEditing/Library/YamyamAssetLibrary/finalize-steam-thumbnail-schedule.py').read_text('utf-8-sig'))
ns={'json':json,'copy':copy};exec(compile(ast.Module(body=[n for n in helper.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in ['N','parse','mutate_json','upsert_list','jload']],type_ignores=[]),'<scoped-json>','exec'),ns)
patch=ns['mutate_json'];upsert=ns['upsert_list']

def git(*a,env=None,data=None):
 q=subprocess.run(['git',*a],cwd=R,env=env,input=data,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 if q.returncode:raise RuntimeError((q.stdout+q.stderr).decode('utf8','replace')[:6000])
 return q.stdout
def load(b):return json.loads(b.decode('utf-8-sig'))
base=git('rev-parse','HEAD').strip().decode();branch=git('symbolic-ref','--quiet','HEAD').strip().decode()
assert branch.startswith('refs/heads/codex/')
work={p:(R/p).read_bytes() for p in paths};head={};idx={}
for p in paths:
 if p in [C,W,D,G]:head[p]=git('show',base+':'+p);idx[p]=git('show',':'+p)
source=load((R/C).read_bytes())

def overlay(p,b):
 if p==G:
  for line in OWNIGNORE:
   if line in work[G].decode('utf8').splitlines() and line not in b.decode('utf8').splitlines():b+=(b'' if b.endswith(b'\n') else b'\n')+line.encode()+b'\n'
  return b
 if p==C:
  for field in ['finiteBatchAuthorizations','scopedProductionAuthorizations']:
   if field not in load(b):b=patch(b,[field],{})
  b=patch(b,['finiteBatchAuthorizations','design-finish-six-20261026'],source['finiteBatchAuthorizations']['design-finish-six-20261026'])
  for s in SLUGS:b=patch(b,['scopedProductionAuthorizations',s],source['scopedProductionAuthorizations'][s])
  return b
 if p==W:
  for episode in IDS:b=upsert(b,'rows',lambda x:x.get('id')==episode,next(x for x in load(work[W])['rows'] if x['id']==episode))
  return b
 if p==D:
  new=work[D].decode('utf-8-sig').splitlines();out=[]
  for line in b.decode('utf-8-sig').splitlines(keepends=True):
   own=next((e for e in IDS if line.startswith('| '+e+' ') or '| 게임디자인 | '+e+' ' in line),None)
   if own:
    candidates=[x for x in new if x.startswith('| '+own+' ') and (x.startswith('| '+own+' |')==line.startswith('| '+own+' |'))] if line.startswith('| '+own+' ') else [x for x in new if '| 게임디자인 | '+own+' ' in x]
    if len(candidates)!=1:raise ValueError('Ambiguous rendered row '+own)
    line=candidates[0]+('\r\n' if line.endswith('\r\n') else '\n')
   out.append(line)
  return ''.join(out).encode('utf8')
 return work[p]

committed={p:overlay(p,head[p]) if p in head else work[p] for p in paths}
synced={p:overlay(p,idx[p]) if p in idx else work[p] for p in paths}
for values in [committed,synced]:
 for p in paths:
  if p not in [C,W,D,G]:
   cleaned=git('hash-object','-w','--path='+p,'--stdin',data=values[p]).strip().decode();values[p]=git('cat-file','blob',cleaned)
run=Path('C:/Users/1/.codex/video-production/design-finish-six-20261026/git')/uuid.uuid4().hex;run.mkdir(parents=True)
env=os.environ.copy();env['GIT_INDEX_FILE']=str(run/'commit-index');env['GIT_OPTIONAL_LOCKS']='0';git('read-tree',base,env=env)
def stage(p,b,e):
 h=git('hash-object','-w','--stdin',data=b).strip().decode();git('update-index','--add','--cacheinfo','100644',h,p,env=e)
for p,b in committed.items():stage(p,b,env)
git('-c','core.whitespace=trailing-space,space-before-tab,cr-at-eol','diff','--cached','--check',base,env=env)
subprocess.run(['node','scripts/media-policy.cjs'],cwd=R,env=env,check=True)
changed=git('diff','--cached','--name-only',base,env=env).decode().splitlines();assert changed and set(changed)<=set(paths)
tree=git('write-tree',env=env).strip().decode();commit=git('commit-tree',tree,'-p',base,data=(args.message+'\n').encode()).strip().decode()
index=Path(git('rev-parse','--git-path','index').strip().decode());index=index if index.is_absolute() else R/index
original=index.read_bytes();(run/'index-before.backup').write_bytes(original)
se=os.environ.copy();se['GIT_INDEX_FILE']=str(run/'sync-index');se['GIT_OPTIONAL_LOCKS']='0';(run/'sync-index').write_bytes(original)
for p,b in synced.items():stage(p,b,se)
ownset={p.encode() for p in paths}
def foreign(e=None):return {flag:b'\0'.join(x for x in git('ls-files',flag,'-z',env=e).split(b'\0') if x and (x.split(b'\t',1)[-1] if flag=='--stage' else x[2:]) not in ownset) for flag in ['--stage','-v']}
before=foreign();assert foreign(se)==before
lock=Path(str(index)+'.lock');fd=os.open(lock,os.O_WRONLY|os.O_CREAT|os.O_EXCL|getattr(os,'O_BINARY',0),0o666);moved=False
try:
 assert index.read_bytes()==original and git('rev-parse','HEAD').strip().decode()==base
 assert all((R/p).read_bytes()==b for p,b in work.items()),'Concurrent owned-path edit; ref not changed'
 payload=(run/'sync-index').read_bytes()
 with os.fdopen(fd,'wb') as f:fd=None;assert f.write(payload)==len(payload);f.flush();os.fsync(f.fileno())
 git('update-ref','-m','commit: finite D25-D30 production',branch,commit,base);moved=True;os.replace(lock,index)
except Exception:
 if fd is not None:os.close(fd)
 if lock.exists():lock.unlink()
 (run/'interrupted.json').write_text(json.dumps({'commit':commit,'refUpdated':moved}),encoding='utf8');raise
assert foreign()==before
for p,b in committed.items():assert git('show',commit+':'+p)==b
subprocess.run(['git','push','origin',commit+':'+branch],cwd=R,check=True)
remote=git('ls-remote','--heads','origin',branch).decode().split()[0];git('merge-base','--is-ancestor',commit,remote)
receipt={'status':'committed-and-pushed','base':base,'commit':commit,'remoteSha':remote,'paths':changed,'foreignIndexPreserved':True,'unrelatedSharedFieldsPreserved':True}
(run/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8');print(json.dumps(receipt))
