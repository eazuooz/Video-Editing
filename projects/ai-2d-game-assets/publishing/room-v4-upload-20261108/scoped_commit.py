"""Exact AI2D metadata + final thumbnail commit without foreign staging."""
from pathlib import Path,PurePosixPath
import importlib.util,sys,re,hashlib
sys.dont_write_bytecode=True
H=Path(__file__).resolve().parent;R=H.parents[3]
sp=importlib.util.spec_from_file_location('scope',R/'projects/kind-to-beginners/publishing/botw-v4/scoped-publishing-commit.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
C='shared/publishing/video-production-control.json';W='shared/publishing/video-worklist.json';D='docs/VIDEO_WORKLIST.md';I='shared/git-essential-images.json';G='.gitignore'
def overlay(name,raw,s):
 if name==C:return m.patch(raw,['ai2dLatestGameVideo20261108'],s['control'])
 if name==W:
  rows=m.load(raw)['rows'];ind=[i for i,r in enumerate(rows) if r['id']=='S-AI2D'];assert len(ind)==1
  for k,v in s['worklistUpdate'].items():raw=m.patch(raw,['rows',ind[0],k],v)
  return raw
 if name==I:return m.upsert(raw,'entries','path',s['essentialImage'])
 if name==G:
  exception='!/'+s['essentialImage']['path'];nl=b'\r\n' if b'\r\n' in raw else b'\n'
  if exception not in raw.decode('utf-8-sig').splitlines():raw+=(b'' if raw.endswith(b'\n') else nl)+exception.encode()+nl
  return raw
 if name==D:
  bom=b'\xef\xbb\xbf' if raw.startswith(b'\xef\xbb\xbf') else b'';t=raw.decode('utf-8-sig');rows=re.findall(r'^\| S-AI2D \| .*?$',t,re.M);assert len(rows)==1
  cols=rows[0].rstrip('\r').split('|');assert len(cols)==7;cols[4]=' 같은 SHA256 사용자 확인 완료 ';cols[5]=s['tablePlatform']
  return bom+t.replace(rows[0],'|'.join(cols)+ ('\r' if rows[0].endswith('\r') else '')).encode('utf8')
 raise AssertionError(name)
def validate(s):
 assert s['scope']=='ai2d-room-v4-reviewed-upload-packaging-v2'
 receipt=m.load((H/'youtube-upload.json').read_bytes());assert receipt['videoId']=='e7hxBpIetq4' and receipt['sameVersionUserReview']
 assert s['control']['videoId']==receipt['videoId'] and not s['control']['schedulingAuthorized']
 paths=s['ownedPaths'];assert len(paths)==len(set(paths))
 for name in paths:
  p=PurePosixPath(name);assert not p.is_absolute() and '..' not in p.parts and '/local/' not in name
  assert name.startswith('projects/ai-2d-game-assets/') and (R/name).is_file()
  assert p.suffix in {'.json','.py','.cjs','.txt'} or name==s['essentialImage']['path']
 assert hashlib.sha256((R/s['essentialImage']['path']).read_bytes()).hexdigest()==s['essentialImage']['sha256']
 return sorted(paths)+sorted(m.SHARED)
m.SHARED={C,W,D,I,G};m.overlay=overlay;m.validate=validate
if __name__=='__main__':
 if '--spec' not in sys.argv:sys.argv[1:1]=['--spec',str(H/'commit-spec.json')]
 m.main()
