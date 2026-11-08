"""Apply verified official Korean spelling; keep the running83-job snapshot intact."""
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;B=H.parent;R=B.parents[3]
def read(p):return json.loads(p.read_text('utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
source=H/'source-verified-revisions.json';data=read(source);ep=next(e for e in data['episodes']if e['id']=='A12');c=next(c for c in ep['changes']if c['id']=='038')
assert '뤼네'in c['ko']or'루네'in c['ko'];previous=c['ko'];c['ko']=c['ko'].replace('뤼네','루네');c['spokenKo']=c['ko']
evidence=B/'footage/canonical-name-lune.json';assert read(evidence)['canonicalDisplay']['ko']=='루네'
actual='production/batches/animation-18-20261031/contrast-v5/footage/team-b/lune-clean-camp.json';c['evidence']=actual
c['evidenceFiles']=[x for x in c['evidenceFiles']if x['path']==actual]
if not any(x['path']==evidence.relative_to(R).as_posix()for x in c['evidenceFiles']):c['evidenceFiles'].append({'path':evidence.relative_to(R).as_posix(),'sha256':sha(evidence)})
c['canonicalNameCorrection']={'before':'뤼네','after':'루네','basis':'Official publisher Korean Steam news + game achievements','englishPreserved':'Lune','applyToNextContentAddressedTtsPass':True}
data['rootCanonicalCorrections']=[{'episode':'A12','sentence':'038','before':previous,'after':c['ko'],'evidence':evidence.relative_to(R).as_posix()}]
source.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf8')
print(c['ko'])
