"""Read verified existing inputs; write only D25 clarity-v3 source/media trees."""
from pathlib import Path
import os
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent;PROJECT=HERE.parents[1]
LOCAL=PROJECT/'production/local/clarity-v3'
PHYSICAL=Path('C:/Users/1/.codex/video-production/design-25-30-review-actions-20261029/limited-color-world/clarity-v3')
READ_ROUTES={LOCAL:PHYSICAL,
 PROJECT/'production/local/batch-v1':Path('C:/Users/1/.codex/video-production/design-finish-six-20261026/limited-color-world/batch-v1'),
 PROJECT/'production/local/unity-visual-v2':Path('C:/Users/1/.codex/video-production/design-25-30-unity-v2-20261028/limited-color-world')}
def absolute(v):
 p=Path(v);return Path(os.path.abspath(p if p.is_absolute() else ROOT/p))
def logical_path(v):
 p=absolute(v)
 for logical,physical in READ_ROUTES.items():
  if p.is_relative_to(physical):p=logical/p.relative_to(physical);break
 if not p.is_relative_to(ROOT):raise ValueError('Input outside repository/selected media roots')
 for logical,physical in READ_ROUTES.items():
  if p.is_relative_to(logical):
   if not logical.is_dir() or logical.resolve()!=physical.resolve():raise ValueError('Unexpected media junction')
   if not p.resolve().is_relative_to(physical.resolve()):raise ValueError('Nested media escape')
   return p
 if not p.resolve().is_relative_to(ROOT.resolve()):raise ValueError('Unregistered media junction')
 return p
def repo_path(v):return logical_path(v).resolve()
def relative(v):return logical_path(v).relative_to(ROOT).as_posix()
def local_output(v):
 p=logical_path(v)
 if not p.is_relative_to(LOCAL):raise ValueError('Output outside new clarity-v3 media root')
 return p.resolve()
def write_path(v):
 p=logical_path(v)
 if not (p.is_relative_to(LOCAL) or p.is_relative_to(HERE)):raise ValueError('Write outside owned revision')
 return p.resolve()
def same_logical_tree(v,a):return logical_path(v).is_relative_to(logical_path(a))
