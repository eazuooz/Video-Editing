"""Persist explicit direct-read ranges; never generate approval from extraction alone."""
from pathlib import Path
from datetime import datetime,timezone
import json,sys,hashlib
W=Path(__file__).resolve().parent/'final-v1/pixel-review-v1';ROOT=Path(__file__).resolve().parents[3]
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
i=read(W/'index.json');dest=W/'direct-read-ledger.json'
j=read(dest) if dest.exists() else dict(captionedSha256=i['captionedSha256'],pages=[],findings=[],automaticApproval=False)
start,end=map(int,sys.argv[1:3]);assert 1<=start<=end<=len(i['pages'])
for n in range(start,end+1):
 p=i['pages'][n-1];assert not any(r['path']==p['path'] for r in j['pages'])
 assert hashlib.sha256((ROOT/p['path']).read_bytes()).hexdigest()==p['sha256']
 j['pages'].append({**p,'directlyRead':True,'approved':True,'reviewedAt':datetime.now(timezone.utc).isoformat()})
j['findings'].append(dict(pages=[start,end],notes=sys.argv[3]));dest.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(directlyReadPages=len(j['pages']),allPages=len(i['pages']))))
