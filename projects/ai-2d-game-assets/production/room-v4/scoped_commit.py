"""Exact-file room website + selected A03 metadata commit. Default: read-only plan."""
from pathlib import Path,PurePosixPath
import importlib.util,json,sys,re,hashlib
sys.dont_write_bytecode=True
H=Path(__file__).resolve().parent;ROOT=H.parents[3]
helper=ROOT/'projects/kind-to-beginners/publishing/botw-v4/scoped-publishing-commit.py'
spec=importlib.util.spec_from_file_location('publishing_scope',helper);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
W='shared/publishing/video-worklist.json';D='docs/VIDEO_WORKLIST.md';C='shared/publishing/video-production-control.json'
M='production/batches/animation-18-20261031/relations-v4/review-manifest.json'
B='production/batches/animation-18-20261031/relations-v4/review.html'
CONTROL_PATHS={('ai2dRoomRevision20261108','latestWebsiteRevision'),('a03ContrastRevision20261108',)}
ROW_KEYS={'productionComplete','productionStatus','reviewStatus','humanApproval','platformStatus','executionStatus','localMasterAvailable','updatedAt','reviewUrl','captionedMasterSha256','deliveryLedger','websiteRevision','contrastRevision','notes'}

def overlay(name,raw,s):
 if name==M:
  if not s.get('a03Record'):return raw
  assert s['a03Record']['id']=='A03'
  return mod.upsert(raw,'records','id',s['a03Record'])
 if name==B:
  if not s.get('a03HtmlRow'):return raw
  replacement=s['a03HtmlRow'];assert replacement.startswith('<tr><td>A03</td>') and replacement.endswith('</tr>')
  pattern=rb'<tr><td>A03</td>.*?</tr>';assert len(re.findall(pattern,raw,flags=re.S))==1
  return re.sub(pattern,lambda _:replacement.encode('utf8'),raw,flags=re.S)
 if name==C:
  for change in s['controlPatches']:
   assert tuple(change['path']) in CONTROL_PATHS
   raw=mod.patch(raw,change['path'],change['value'])
  return raw
 if name==W:
  for update in s['worklistUpdates']:
   assert update['id'] in {'S-AI2D','A03'}
   data=mod.load(raw);indices=[i for i,r in enumerate(data['rows']) if r['id']==update['id']];assert len(indices)==1;i=indices[0]
   for key,value in update['set'].items():
    assert key in ROW_KEYS
    raw=mod.patch(raw,['rows',i,key],value)
   evidence=list(mod.load(raw)['rows'][i].get('evidence',[]))
   for value in update.get('appendEvidence',[]):
    if value not in evidence:evidence.append(value)
   raw=mod.patch(raw,['rows',i,'evidence'],evidence)
  return raw
 if name==D:
  bom=b'\xef\xbb\xbf' if raw.startswith(b'\xef\xbb\xbf') else b'';text=raw.decode('utf-8-sig');nl='\r\n' if '\r\n' in text else '\n'
  start='<!-- AI2D-WEBSITE-20261108 -->';end='<!-- AI2D-WEBSITE-20261108-END -->'
  addition=nl.join(s['websiteMarkdown'].splitlines())
  if start in text:
   assert text.count(start)==text.count(end)==1
   text=re.sub(re.escape(start)+r'.*?'+re.escape(end),lambda _:addition,text,flags=re.S)
  else:
   anchor='<!-- AI2D-20261108-END -->';assert text.count(anchor)==1
   text=text.replace(anchor,addition+nl+anchor)
  for value in s.get('a03MarkdownRows',[]):
   assert value.startswith('| A03 |') and '\n' not in value and '\r' not in value
   matches=[line for line in text.splitlines() if line.startswith('| A03 |')];assert len(matches)==1
   text=text.replace(matches[0],value)
  return bom+text.encode('utf8')
 raise AssertionError(name)

def validate(s):
 assert s['scope']=='room-v4-website-and-selected-a03-contrast-v5'
 assert hashlib.sha256((H/'site-deployment.json').read_bytes()).hexdigest()==s['websiteReceiptSha256'],'Website receipt changed; run prepare_metadata.py again.'
 if '--execute' in sys.argv:assert s['readyForCommit'] is True,'Root is still finalizing website and A03. Do not commit yet.'
 paths=s['ownedPaths'];assert paths and len(paths)==len(set(paths))
 approved=set(s.get('a03ApprovedPaths',[]))
 for name in paths:
  pure=PurePosixPath(name);assert not pure.is_absolute() and '..' not in pure.parts and '\\' not in name
  assert not name.startswith('sites/') and ('/local/' not in name)
  assert name.startswith('projects/ai-2d-game-assets/production/room-v4/') or name in approved
  if name in approved:assert name.startswith('projects/animation-breaking-down-attack-animations/')
  p=ROOT/name;assert p.is_file() and p.resolve().is_relative_to(ROOT.resolve())
  assert p.suffix in {'.py','.cjs','.json','.txt','.md','.html'} or p.name=='.gitignore'
 assert {tuple(v['path']) for v in s['controlPatches']}<=CONTROL_PATHS
 assert all(v['id'] in {'S-AI2D','A03'} for v in s['worklistUpdates'])
 return sorted(paths)+sorted(mod.SHARED)

mod.SHARED={W,D,C,M,B};mod.overlay=overlay;mod.validate=validate
if __name__=='__main__':
 if '--spec' not in sys.argv:sys.argv[1:1]=['--spec',str(H/'commit-spec.json')]
 mod.main()
