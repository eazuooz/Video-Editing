"""Register one directly reviewed essential thumbnail; never include QA frames."""
from pathlib import Path
import sys,json,hashlib,datetime
R=Path(__file__).resolve().parents[3];slug=sys.argv[1];rel=f'projects/{slug}/publish/assets/thumbnail.png';p=R/rel
assert p.exists();digest=hashlib.sha256(p.read_bytes()).hexdigest()
record=p.parent/'thumbnail-generation.json';g=json.loads(record.read_text(encoding='utf8'));assert g['directVisualReview']['status']=='passed'
registry=R/'shared/git-essential-images.json';d=json.loads(registry.read_text(encoding='utf8'));existing=next((e for e in d['entries'] if e['path']==rel),None)
manifest=json.loads((R/f'projects/{slug}/project.json').read_text(encoding='utf8'))
entry={'path':rel,'purpose':'delivery-thumbnail','reason':'Directly reviewed final thumbnail for '+manifest['titles']['en']+'; retains approved yellow strip, large Korean text and original channel-cat reference. Only the selected final is essential; generated variants and all QA frames stay local.','sha256':digest,'reviewedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'project':slug}
if existing:assert existing['sha256']==digest,'Replaced essential image requires a fresh explicit review.'
else:d['entries'].append(entry);registry.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
ignore=R/'.gitignore';text=ignore.read_text(encoding='utf8');exception='!'+rel
if exception not in text.splitlines():ignore.write_text(text.rstrip()+'\n'+exception+'\n',encoding='utf8')
g['sha256']=digest;record.write_text(json.dumps(g,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Registered exact essential image:',rel,digest)
