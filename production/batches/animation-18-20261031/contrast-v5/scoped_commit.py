"""Candidate selection only: 17 episode rows and one authorization key."""
from pathlib import Path, PurePosixPath
import importlib.util, json, sys, re
sys.dont_write_bytecode=True
H=Path(__file__).resolve().parent; ROOT=H.parents[3]
sp=importlib.util.spec_from_file_location('scope',ROOT/'projects/kind-to-beginners/publishing/botw-v4/scoped-publishing-commit.py')
mod=importlib.util.module_from_spec(sp);sp.loader.exec_module(mod)
C='shared/publishing/video-production-control.json';W='shared/publishing/video-worklist.json';D='docs/VIDEO_WORKLIST.md'
IDS={f'A{i:02}' for i in range(1,19) if i!=3}
def overlay(name,raw,s):
 if name==C:return mod.patch(raw,['animationContrastRevision20261108'],s['control'])
 if name==W:
  for entry in s['worklist']:
   assert entry['id'] in IDS
   rows=mod.load(raw)['rows'];matches=[i for i,v in enumerate(rows) if v['id']==entry['id']];assert len(matches)==1
   i=matches[0]
   for k,v in entry['set'].items():
    assert k in {'executionStatus','contrastRevision','updatedAt'}
    raw=mod.patch(raw,['rows',i,k],v)
  return raw
 if name==D:
  text=raw.decode('utf-8-sig');bom=b'\xef\xbb\xbf' if raw.startswith(b'\xef\xbb\xbf') else b''
  for identity in sorted(IDS):
   pattern=r'^\| '+identity+r' \| .*?$';matches=re.findall(pattern,text,re.M);assert len(matches)==1
   old=matches[0];parts=old.rstrip('\r').rsplit('|',2);assert len(parts)==3
   new=parts[0]+'| 기존 완성본 보존 · 게임·캐릭터 후보 검수 대기 |'+('\r' if old.endswith('\r') else '')
   text=text.replace(old,new)
  return bom+text.encode('utf-8')
 raise AssertionError(name)
def validate(s):
 assert s['scope']=='animation-17-candidate-review-20261108'
 assert set(s['control']['episodes'])==IDS and not s['control']['renderAuthorized']
 assert {v['id'] for v in s['worklist']}==IDS
 assert s['candidateUserApproval'] is None
 paths=s['ownedPaths'];assert len(paths)==len(set(paths))
 for name in paths:
  p=PurePosixPath(name);assert not p.is_absolute() and '..' not in p.parts
  assert name.startswith('production/batches/animation-18-20261031/contrast-v5/') and '/local/' not in name
  assert p.suffix in {'.json','.md','.py','.txt'} or p.name=='.gitignore'
  assert (ROOT/name).is_file()
 return sorted(paths)+sorted(mod.SHARED)
mod.SHARED={C,W,D};mod.overlay=overlay;mod.validate=validate
if __name__=='__main__':
 if '--spec' not in sys.argv:sys.argv[1:1]=['--spec',str(H/'commit-spec.json')]
 mod.main()
