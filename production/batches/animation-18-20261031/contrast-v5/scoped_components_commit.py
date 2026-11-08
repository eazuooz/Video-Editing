"""Commit selected17 component sources without foreign staging or local media."""
from pathlib import Path,PurePosixPath
import importlib.util,sys,hashlib
sys.dont_write_bytecode=True
H=Path(__file__).resolve().parent;R=H.parents[3]
sp=importlib.util.spec_from_file_location('active_scope',H/'scoped_active_commit.py');a=importlib.util.module_from_spec(sp);sp.loader.exec_module(a);m=a.mod
def validate(s):
 assert s['scope']=='animation-17-approved-roster-production-20261108'
 assert set(s['control']['episodes'])==a.IDS and not s['control']['youtubeAuthorized']
 assert {r['id'] for r in s['worklist']}==a.IDS
 paths=s['ownedPaths'];assert len(paths)==len(set(paths))
 manifest=m.load((H/'renderer/owned-files.json').read_bytes());asset={x['path']:x for x in manifest['files'] if Path(x['path']).suffix in {'.uasset','.umap'}}
 allowedProjects={f"projects/{r['slug']}/production/contrast-v5/final.{lang}.json" for r in m.load((H/'baseline-review-manifest.json').read_bytes())['records'] if r['id'] in a.IDS for lang in ['ko','en']}
 for name in paths:
  p=PurePosixPath(name);assert not p.is_absolute() and '..' not in p.parts and '/local/' not in name and '__pycache__' not in name
  assert name.startswith('production/batches/animation-18-20261031/contrast-v5/') or name in allowedProjects
  assert (R/name).is_file()
  if name in asset:assert hashlib.sha256((R/name).read_bytes()).hexdigest()==asset[name]['sha256']
  else:assert p.suffix in {'.json','.md','.py','.txt','.cjs'}
 return sorted(paths)+sorted(m.SHARED)
m.validate=validate
if __name__=='__main__':
 if '--spec' not in sys.argv:sys.argv[1:1]=['--spec',str(H/'components-commit-spec.json')]
 m.main()
