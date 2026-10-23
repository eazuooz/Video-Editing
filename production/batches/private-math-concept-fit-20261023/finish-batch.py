"""Validate the delivered files and close only the authorized 18-lecture revision."""
from common import *
from html.parser import HTMLParser
from urllib.parse import urlparse, unquote

class Links(HTMLParser):
 def __init__(self):super().__init__();self.links=[]
 def handle_starttag(self,tag,attrs):
  if tag in ('a','video','source','track'):
   self.links.extend(v for k,v in attrs if k in ('href','src') and v)

def local_links(page):
 parser=Links();parser.feed(page.read_text(encoding='utf8'));count=0
 for target in parser.links:
  u=urlparse(target)
  if u.scheme or not u.path:continue
  p=(page.parent/unquote(u.path)).resolve()
  assert p.is_relative_to(R.resolve()) and p.is_file(),(rel(page),target)
  count+=1
 return count

c=read(B/'checkpoint.json');control_path=R/'shared/publishing/video-production-control.json'
control=read(control_path);authorization=control['scopedBatchAuthorizations'][KEY]
assert len(c['entries'])==18 and set(c['ready'])==set(authorization['ids'])
assert not authorization['uploadAuthorized'] and not authorization['heartbeatEnabled']
entries=[];total_bytes=0;verified_links=0
for e in c['entries']:
 h=R/'projects'/e['slug']/'production/concept-fit-v2';ledger=read(h/'review-ledger.json')
 out=read(h/'outputs.json');qa=read(R/ledger['technicalQa']);cap=read(R/ledger['captionCoverage']);play=read(R/ledger['nativePlayback'])
 assert ledger['status']=='local-review-ready-with-listening-notes'
 assert ledger['outputs']==out['outputs'] and len(out['outputs'])==4
 assert ledger['humanReview']=='pending-for-this-hash' and not ledger['audio']['actualListening']
 files=[]
 for f in out['outputs']:
  p=R/f['path'];assert p.is_file() and p.stat().st_size==f['bytes']
  assert sha(p)==f['sha256'],f['path'];total_bytes+=f['bytes'];files.append(f['path'])
 master=next(f for f in out['outputs'] if f['path'].endswith('.captioned.mp4'))
 assert master['sha256']==ledger['masterSha256']==cap['masterSha256']==play['masterSha256']
 assert len(qa['technical'])==2
 for v in qa['technical']:
  assert v['decodeErrors']==0 and v['sha256']==next(f['sha256'] for f in out['outputs'] if f['path']==v['path'])
  meta=probe(R/v['path']);video=next(s for s in meta['streams'] if s['codec_type']=='video')
  assert (video['width'],video['height'],video['avg_frame_rate'])==(1920,1080,'60/1')
  assert int(video['nb_frames'])==out['frames']
 segments=play['segments'];assert segments and all(s['rate']==1 and s['end']>s['start'] for s in segments)
 full=any(s['start']==0 and s.get('ended') and abs(s['end']-out['seconds'])<.05 for s in segments)
 page=R/e['outputFolder']/'index.html';verified_links+=local_links(page)
 entries.append(dict(id=e['id'],title=e['title'],seconds=out['seconds'],frames=out['frames'],masterSha256=master['sha256'],outputs=files,reviewPage=rel(page),reviewLedger=rel(h/'review-ledger.json'),nativePlayback='full-file' if full else 'targeted-final-intervals-with-prior-evidence',humanReview='pending',actualListening=False))
 verified_links+=local_links(R/'output/private-game-math-polish/index.html') if len(entries)==18 else 0
 print(e['id'],'four outputs, hash, FHD60 and links verified',flush=True)
result=dict(checkedAt=now(),status='local-review-ready-with-listening-notes',episodes=len(entries),files=sum(len(e['outputs']) for e in entries),totalBytes=total_bytes,totalSeconds=sum(e['seconds'] for e in entries),verifiedLocalLinks=verified_links,sha256Verified=True,decodeEvidenceReused=True,nativeFullFilePlayback=sum(e['nativePlayback']=='full-file' for e in entries),entries=entries,actualListening=False,humanReview='pending',uploadAuthorized=False)
save(B/'final-batch-check.json',result)
authorization.update(status='completed-local-review-ready',completedAt=now(),fullProductionAuthorized=False,renderAuthorized=False,limitedNarrationRepairAuthorized=False,automaticAdvanceWithinThisList=False,completionEvidence=rel(B/'final-batch-check.json'),deliveredIds=[e['id'] for e in entries],humanReview='pending',actualListening=False)
save(control_path,control)
print('18 lectures /72 files verified. Scoped production closed; actual listening and human review pending.')
