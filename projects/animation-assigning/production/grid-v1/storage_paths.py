"""A01 reads workspace sources; writes only this revision's code or local outputs."""
from pathlib import Path
import os
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
PROJECT=HERE.parents[1]
LOCAL=PROJECT/'production/local/grid-v1'
EXTERNAL_BASE=Path('C:/Users/1/.codex/video-production').resolve()

def absolute(value):
 p=Path(value);return Path(os.path.abspath(p if p.is_absolute() else ROOT/p))
def logical_path(value):
 p=absolute(value)
 if not p.is_relative_to(ROOT):raise ValueError('Input outside workspace')
 resolved=p.resolve()
 if not resolved.is_relative_to(ROOT.resolve()) and not resolved.is_relative_to(EXTERNAL_BASE):
  raise ValueError('Unrecognized external source junction')
 return p
def repo_path(value):return logical_path(value)
def relative(value):return logical_path(value).relative_to(ROOT).as_posix()
def local_output(value):
 p=logical_path(value)
 if not p.is_relative_to(LOCAL) or not p.resolve().is_relative_to(LOCAL.absolute()):
  raise ValueError('Output outside isolated A01 revision')
 return p.resolve()
def write_path(value):
 p=logical_path(value)
 if p.is_relative_to(LOCAL):return local_output(p)
 if not p.is_relative_to(HERE):raise ValueError('Metadata outside isolated A01 revision')
 return p.resolve()
def same_logical_tree(value,anchor):return logical_path(value).is_relative_to(logical_path(anchor))
