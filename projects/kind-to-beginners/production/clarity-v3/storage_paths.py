"""Read pinned baseline media; only write the isolated D29 clarity revision."""
from pathlib import Path
import json,os
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent;PROJECT=HERE.parents[1];SLUG=PROJECT.name
LOCAL=PROJECT/'production/local/clarity-v3'
PHYSICAL=Path('C:/Users/1/.codex/video-production/design-25-30-review-actions-20261029')/SLUG/'clarity-v3'
READ_ROUTES={
 LOCAL:PHYSICAL,
 PROJECT/'production/local/batch-v1':Path('C:/Users/1/.codex/video-production/design-finish-six-20261026')/SLUG/'batch-v1',
 PROJECT/'production/local/unity-visual-v2':Path('C:/Users/1/.codex/video-production/design-25-30-unity-v2-20261028')/SLUG,
}
def absolute(v):
 p=Path(v);return Path(os.path.abspath(p if p.is_absolute()else ROOT/p))
def route():
 d=json.loads((HERE/'storage-routing.json').read_text('utf-8-sig'))
 if d['slug']!=SLUG or absolute(d['logicalRoot'])!=absolute(LOCAL)or absolute(d['physicalRoot'])!=absolute(PHYSICAL):raise ValueError('Wrong scoped storage record')
 if LOCAL.resolve()!=absolute(PHYSICAL)or PHYSICAL.resolve()!=absolute(PHYSICAL):raise ValueError('Exact selected junction required')
def logical_path(v):
 p=absolute(v)
 for logical,physical in READ_ROUTES.items():
  if p.is_relative_to(absolute(physical)):p=logical/p.relative_to(absolute(physical));break
 if not p.is_relative_to(absolute(ROOT)):raise ValueError('Outside repository and selected read routes')
 for logical,physical in READ_ROUTES.items():
  if p.is_relative_to(logical):
   if logical.resolve()!=absolute(physical)or not p.resolve().is_relative_to(absolute(physical)):raise ValueError('Foreign junction or escape')
   return p
 if not p.resolve().is_relative_to(ROOT.resolve()):raise ValueError('Unlisted external route')
 return p
def repo_path(v):return logical_path(v).resolve()
def relative(v):return logical_path(v).relative_to(ROOT).as_posix()
def local_output(v):
 p=logical_path(v);route()
 if not p.is_relative_to(LOCAL):raise ValueError('Output outside isolated D29 revision')
 return p.resolve()
def write_path(v):
 p=logical_path(v)
 if p.is_relative_to(LOCAL):return local_output(p)
 if not p.is_relative_to(HERE):raise ValueError('Metadata output outside isolated D29 revision')
 return p.resolve()
def same_logical_tree(v,a):return logical_path(v).is_relative_to(logical_path(a))
