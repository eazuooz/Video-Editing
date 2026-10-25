"""Selective commit and push, preserving unrelated staging and working changes."""
import json,os,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[3];B=Path(__file__).parent;tag=sys.argv[1];L=B/'local'/('git-'+tag);L.mkdir(parents=True,exist_ok=False)
def git(*args,env=None,data=None):
 p=subprocess.run(['git',*args],cwd=R,env=env,input=data,capture_output=True)
 if p.returncode:raise RuntimeError(p.stderr.decode('utf8','replace'))
 return p.stdout
def enc(x):return (json.dumps(x,ensure_ascii=False,indent=2)+'\n').encode()
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
slugs=['shorts-portal-seamless-traversal'];CP='shared/publishing/video-production-control.json';WP='shared/publishing/shorts-worklist.json';work={p:(R/p).read_bytes() for p in [CP,WP]}
owned={k:json.loads(work[CP])[k] for k in ['portalTraversalShortsAuthorization']};current=read(R/WP);rows={r['slug']:r for r in current['rows'] if r.get('slug') in slugs};assert len(rows)==1
def transform(path,raw):
 d=json.loads(raw)
 if path==CP:d.update(owned)
 else:
  found=set()
  for i,row in enumerate(d['rows']):
   if row.get('slug') in rows:d['rows'][i]=rows[row['slug']];found.add(row['slug'])
  d['rows'] += [rows[s] for s in slugs if s not in found];d['updatedAt']=current['updatedAt']
 return enc(d)
base=git('rev-parse','HEAD').decode().strip();index=Path(git('rev-parse','--path-format=absolute','--git-path','index').decode().strip());before=index.read_bytes();entries=git('ls-files','--stage','-z');(L/'original-index.bin').write_bytes(before)
env=os.environ.copy();env['GIT_INDEX_FILE']=str(L/'selected.index');git('read-tree',base,env=env);sync={}
for path in [CP,WP]:
 head=transform(path,git('show',base+':'+path));sync[path]=transform(path,git('show',':'+path));blob=git('hash-object','-w','--stdin',data=head).decode().strip();git('update-index','--add','--cacheinfo','100644',blob,path,env=env)
unity='unity/VideoEditing/Assets/VideoScenes/portal-traversal-shorts-20261025'
roots=[f'projects/{s}' for s in slugs]+['motion-canvas/src/projects/portal-traversal-shorts-20261025/composite.tsx','motion-canvas/src/projects/portal-traversal-shorts-20261025/7']
roots += [unity+'/'+p for p in ['CameraGuide.cs','CameraGuide.cs.meta','PortalDemo.cs','Editor/Capture.cs','Scenes/traversal/camera.unity','Scenes/traversal/screen.unity']]
roots += [p.relative_to(R).as_posix() for p in (R/unity/'Materials').glob('*camera*')]
roots=[p for p in roots if (R/p).exists()];git('add','--',*roots,env=env);paths=git('diff','--cached','--name-only','-z',env=env).decode().strip('\0').split('\0')
assert all(p in [CP,WP,*roots] or any(p.startswith(r+'/') for r in roots) for p in paths)
assert not any('/local/' in p or '/__pycache__/' in p for p in paths)
git('diff','--cached','--check',env=env);(L/'review.patch').write_bytes(git('diff','--cached',env=env))
q=subprocess.run(['node','scripts/media-policy.cjs'],cwd=R,env=env,capture_output=True);assert q.returncode==0,q.stderr.decode()
assert index.read_bytes()==before and git('rev-parse','HEAD').decode().strip()==base
assert all((R/p).read_bytes()==b for p,b in work.items())
git('-c','gc.auto=0','-c','maintenance.auto=false','commit','-m',sys.argv[2],env=env);commit=git('rev-parse','HEAD').decode().strip();assert index.read_bytes()==before
records=[]
for p in paths:
 if p in sync:blob=git('hash-object','-w','--stdin',data=sync[p]).decode().strip();records.append(f'100644 {blob}\t{p}\0'.encode())
 else:records.append(git('ls-files','--stage','-z','--',p,env=env))
git('update-index','-z','--index-info',data=b''.join(records))
def foreign(raw):return [e for e in raw.split(b'\0') if e and e.split(b'\t',1)[1].decode() not in paths]
assert foreign(entries)==foreign(git('ls-files','--stage','-z'));assert all((R/p).read_bytes()==b for p,b in work.items())
branch=git('branch','--show-current').decode().strip();git('push','origin','HEAD:refs/heads/'+branch);remote=git('ls-remote','origin','refs/heads/'+branch).decode().split()[0];assert remote==commit
result={'commit':commit,'remoteMatches':True,'foreignStagingPreserved':True,'changedPaths':len(paths)};(L/'result.json').write_bytes(enc(result));print(json.dumps(result))
