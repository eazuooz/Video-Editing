from pathlib import Path
from datetime import datetime, timezone
import hashlib,json
ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'projects/motion-sickness-games/production/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
d=read(ROOT/'projects/motion-sickness-games/production/delivery-output.json')
assert d['cueCounts']=={'ko':179,'en':179} and len(d['files'])==4
rows=[]
for v in d['files']:
 src=ROOT/v['source'];dst=ROOT/d['directory']/v['name']
 assert sha(src)==sha(dst)==v['sha256']
 rows.append(dict(**v,output=dst.relative_to(ROOT).as_posix(),sourceAndOutputHashEqual=True))
assert next(v for v in rows if v['name'].endswith('captioned.mp4'))['sha256']=='575b01decc8b65c8e1f04cc3694ce6246d66ecd78d2820431a4558a00bc8399d'
p=R/'collection-private-preflight-v2.json';assert not p.exists()
p.write_text(json.dumps(dict(verifiedAt=datetime.now(timezone.utc).isoformat(),actualCollectSessionId=56267,actualCollectExitCode=0,actualExitObservedChunk='37028a',sourceAndOutputAllFourHashesEqual=True,files=rows,actualId=None,uploaded=False,humanListeningApproved=False,publicRightsApproved=False),ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(sourceAndOutputAllFourHashesEqual=True,files=4,actualCollectExitCode=0)))
