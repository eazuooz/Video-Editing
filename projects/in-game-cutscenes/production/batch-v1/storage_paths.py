"""Only this selected episode's verified C-backed local route."""
from pathlib import Path
import json, os
ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
PROJECT=HERE.parents[1]
SLUG=PROJECT.name
LOCAL=PROJECT/'production/local/batch-v1'
PHYSICAL=Path('C:/Users/1/.codex/video-production/design-finish-six-20261026')/SLUG/'batch-v1'
def absolute(v):
 p=Path(v);return Path(os.path.abspath(p if p.is_absolute() else ROOT/p))
def route():
 d=json.loads((HERE/'storage-routing.json').read_text('utf-8-sig'))
 if d['slug']!=SLUG or absolute(d['logicalRoot'])!=absolute(LOCAL) or absolute(d['physicalRoot'])!=absolute(PHYSICAL):raise ValueError('Wrong scoped storage record')
 if not LOCAL.is_dir() or LOCAL.resolve()!=absolute(PHYSICAL) or PHYSICAL.resolve()!=absolute(PHYSICAL):raise ValueError('Exact local junction must exist')
def logical_path(v):
 p=absolute(v)
 if p.is_relative_to(absolute(PHYSICAL)):
  route();logical=LOCAL/p.relative_to(absolute(PHYSICAL))
 elif p.is_relative_to(absolute(ROOT)):logical=p
 else:raise ValueError('Outside repository and exact media route')
 if logical.is_relative_to(LOCAL):
  route()
  if not p.resolve().is_relative_to(absolute(PHYSICAL)):raise ValueError('Nested local path escapes selected C root')
 elif not p.resolve().is_relative_to(ROOT.resolve()):raise ValueError('Foreign junction not authorized')
 return logical
def repo_path(v):
 logical=logical_path(v)
 return logical.resolve()
def relative(v):return logical_path(v).relative_to(ROOT).as_posix()
def local_output(v):
 logical=logical_path(v)
 if not logical.is_relative_to(LOCAL):raise ValueError('Media output outside current local root')
 return repo_path(logical)
def write_path(v):return repo_path(v)
def same_logical_tree(v,a):return logical_path(v).is_relative_to(logical_path(a))
