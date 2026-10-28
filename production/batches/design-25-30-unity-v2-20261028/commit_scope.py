"""Commit only this finite batch while preserving unrelated index/shared edits."""
from pathlib import Path
import argparse, ast, copy, json, os, re, subprocess, uuid

R=Path(__file__).resolve().parents[3]
B='production/batches/design-25-30-unity-v2-20261028/'
SLUGS=['limited-color-world','computer-controlled-players','in-game-cutscenes','start-with-climax','kind-to-beginners','respect-player-time']
IDS=['D25','D26','D27','D28','D29','D30']
C='shared/publishing/video-production-control.json';W='shared/publishing/video-worklist.json';D='docs/VIDEO_WORKLIST.md';G='.gitignore'
CONFIG='motion-canvas/vite.design-finish-six.config.ts'
PREFIXES=[B,'unity/VideoEditing/Assets/VideoScenes/design-25-30-unity-v2']+['projects/'+s+'/' for s in SLUGS]+['unity/VideoEditing/Assets/VideoScenes/'+s+'/unity-visual-v2' for s in SLUGS]
PARENT_METAS=['unity/VideoEditing/Assets/VideoScenes/'+s+'.meta' for s in SLUGS]
OWNIGNORE=['/projects/'+s+'/production/local/' for s in SLUGS]
ap=argparse.ArgumentParser();ap.add_argument('--paths',required=True);ap.add_argument('--message',required=True);args=ap.parse_args()
paths=json.loads(Path(args.paths).read_text('utf-8-sig'))
assert len(paths)==len(set(paths)) and all(any(p.startswith(x) for x in PREFIXES) or p in [C,W,D,G,CONFIG]+PARENT_METAS for p in paths)
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

OWN_ROW_FIELDS=['productionComplete','productionStatus','reviewStatus','humanApproval','executionStatus','localMasterAvailable','activeRevision','selectedBatch','internalQaStatus','localReview']
OWN_NOTE='이전 이야기/순서 호평을 반영해 설명만 Unity로 보완. 기존 완성본 보존. 새 파일 사용자 전체 검수 대기; 플랫폼 변경 없음.'
def overlay_row(target, current):
 out=copy.deepcopy(target)
 previous=out.get('localReview')
 if previous and previous.get('captionedSha256')!=current['localReview']['captionedSha256']:
  history=out.setdefault('localReviewHistory',[])
  if not any(h.get('captionedSha256')==previous.get('captionedSha256') for h in history):history.append(previous)
 for key in OWN_ROW_FIELDS:out[key]=copy.deepcopy(current[key])
 evidence='projects/'+SLUGS[IDS.index(current['id'])]+'/production/unity-visual-v2/review-status.json'
 if evidence not in out.setdefault('evidence',[]):out['evidence'].append(evidence)
 if OWN_NOTE not in out.get('notes',''):out['notes']=(out.get('notes','').rstrip()+' '+OWN_NOTE).strip()
 return out

def overlay(p,b):
 if p==G:
  for line in OWNIGNORE:
   if line in work[G].decode('utf8').splitlines() and line not in b.decode('utf8').splitlines():b+=(b'' if b.endswith(b'\n') else b'\n')+line.encode()+b'\n'
  return b
 if p==C:
  for field in ['finiteBatchAuthorizations']:
   if field not in load(b):b=patch(b,[field],{})
  b=patch(b,['finiteBatchAuthorizations','design-25-30-unity-v2-20261028'],source['finiteBatchAuthorizations']['design-25-30-unity-v2-20261028'])
  # Only this new finite visual-revision authorization is owned here.
  return b
 if p==W:
  for episode in IDS:
   existing=next(x for x in load(b)['rows'] if x['id']==episode)
   current=next(x for x in load(work[W])['rows'] if x['id']==episode)
   b=upsert(b,'rows',lambda x:x.get('id')==episode,overlay_row(existing,current))
  return b
 if p==D:
  new=work[D].decode('utf-8-sig').splitlines();out=[]
  for line in b.decode('utf-8-sig').splitlines(keepends=True):
   own=next((e for e in IDS if line.startswith('| '+e+' ') or '| 게임디자인 | '+e+' ' in line),None)
   if own:
    candidates=[x for x in new if x.startswith('| '+own+' ') and (x.startswith('| '+own+' |')==line.startswith('| '+own+' |'))] if line.startswith('| '+own+' ') else [x for x in new if '| 게임디자인 | '+own+' ' in x]
    if len(candidates)!=1:raise ValueError('Ambiguous rendered row '+own)
    oldcells=line.rstrip('\r\n').split('|');newcells=candidates[0].split('|')
    if line.startswith('| '+own+' |'):
     for column in [3,4]:oldcells[column]=newcells[column]
    elif '| 게임디자인 | '+own+' ' in line:
     for column in [4,5]:oldcells[column]=newcells[column]
    elif OWN_NOTE not in oldcells[2]:oldcells[2]=' '+(oldcells[2].strip()+' '+OWN_NOTE).strip()+' '
    line='|'.join(oldcells)+('\r\n' if line.endswith('\r\n') else '\n')
   out.append(line)
  return ''.join(out).encode('utf8')
 return work[p]

committed={p:overlay(p,head[p]) if p in head else work[p] for p in paths}
synced={p:overlay(p,idx[p]) if p in idx else work[p] for p in paths}
clean_cache={};oid_cache={}
for values in [committed,synced]:
 for p in paths:
  if p not in [C,W,D,G]:
   key=(p,values[p])
   if key not in clean_cache:
    cleaned=git('hash-object','-w','--path='+p,'--stdin',data=values[p]).strip().decode();data=git('cat-file','blob',cleaned)
    clean_cache[key]=data;oid_cache[data]=cleaned
   values[p]=clean_cache[key]
run=Path('C:/Users/1/.codex/video-production/design-25-30-unity-v2-20261028/git')/uuid.uuid4().hex;run.mkdir(parents=True)
env=os.environ.copy();env['GIT_INDEX_FILE']=str(run/'commit-index');env['GIT_OPTIONAL_LOCKS']='0';git('read-tree',base,env=env)
def oid(b):
 if b not in oid_cache:oid_cache[b]=git('hash-object','-w','--stdin',data=b).strip().decode()
 return oid_cache[b]
def stage_all(values,e):
 payload=b''.join(('100644 '+oid(b)+'\t'+p).encode()+b'\0' for p,b in values.items())
 git('update-index','-z','--index-info',env=e,data=payload)
stage_all(committed,env)
# Unity emits a space after empty YAML values. Preserve the exact captured scene
# bytes and hashes; allow only those generated empty-value lines, not arbitrary
# whitespace defects. Hand-authored code/documents retain the normal diff check.
generated_suffixes=['.unity','.meta','.mat','.asset']
for p in paths:
 if p.startswith('unity/VideoEditing/Assets/VideoScenes/') and Path(p).suffix in generated_suffixes:
  for n,line in enumerate(committed[p].decode('utf-8-sig').splitlines(),1):
   assert not re.search(r' +\t',line),f'Space before tab: {p}:{n}'
   if line.rstrip(' \t')!=line:assert re.fullmatch(r'\s*(?:-\s+)?[^\s:]+:[ \t]+',line),f'Unexpected generated whitespace: {p}:{n}'
exclusions=[':(exclude,glob)unity/VideoEditing/Assets/VideoScenes/**/*'+suffix for suffix in generated_suffixes]
git('-c','core.whitespace=trailing-space,space-before-tab,cr-at-eol','diff','--cached','--check',base,'--','.',*exclusions,env=env)
subprocess.run(['node','scripts/media-policy.cjs'],cwd=R,env=env,check=True)
changed=git('diff','--cached','--name-only',base,env=env).decode().splitlines();assert changed and set(changed)<=set(paths)
tree=git('write-tree',env=env).strip().decode();commit=git('commit-tree',tree,'-p',base,data=(args.message+'\n').encode()).strip().decode()
index=Path(git('rev-parse','--git-path','index').strip().decode());index=index if index.is_absolute() else R/index
original=index.read_bytes();(run/'index-before.backup').write_bytes(original)
se=os.environ.copy();se['GIT_INDEX_FILE']=str(run/'sync-index');se['GIT_OPTIONAL_LOCKS']='0';(run/'sync-index').write_bytes(original)
stage_all(synced,se)
ownset={p.encode() for p in paths}
def foreign(e=None):return {flag:b'\0'.join(x for x in git('ls-files',flag,'-z',env=e).split(b'\0') if x and (x.split(b'\t',1)[-1] if flag=='--stage' else x[2:]) not in ownset) for flag in ['--stage','-v']}
before=foreign();assert foreign(se)==before
lock=Path(str(index)+'.lock');fd=os.open(lock,os.O_WRONLY|os.O_CREAT|os.O_EXCL|getattr(os,'O_BINARY',0),0o666);moved=False
try:
 assert index.read_bytes()==original and git('rev-parse','HEAD').strip().decode()==base
 assert all((R/p).read_bytes()==b for p,b in work.items()),'Concurrent owned-path edit; ref not changed'
 payload=(run/'sync-index').read_bytes()
 with os.fdopen(fd,'wb') as f:fd=None;assert f.write(payload)==len(payload);f.flush();os.fsync(f.fileno())
 git('update-ref','-m','commit: D25-D30 Unity explanation revision',branch,commit,base);moved=True;os.replace(lock,index)
except Exception:
 if fd is not None:os.close(fd)
 if lock.exists():lock.unlink()
 (run/'interrupted.json').write_text(json.dumps({'commit':commit,'refUpdated':moved}),encoding='utf8');raise
assert foreign()==before
tree_blobs={item.split(b'\t',1)[1].decode():item.split(b'\t',1)[0].split()[2].decode() for item in git('ls-tree','-r','-z',commit).split(b'\0') if item}
for p,b in committed.items():assert tree_blobs[p]==oid(b)
subprocess.run(['git','push','origin',commit+':'+branch],cwd=R,check=True)
remote=git('ls-remote','--heads','origin',branch).decode().split()[0];git('merge-base','--is-ancestor',commit,remote)
receipt={'status':'committed-and-pushed','base':base,'commit':commit,'remoteSha':remote,'paths':changed,'foreignIndexPreserved':True,'unrelatedSharedFieldsPreserved':True}
(run/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8');print(json.dumps(receipt))
