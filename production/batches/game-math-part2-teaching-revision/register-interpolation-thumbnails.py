"""Only the two explicitly reviewed delivery thumbnails become essential."""
from pathlib import Path
import json,hashlib,datetime
ROOT=Path(__file__).resolve().parents[3];file=ROOT/'shared/git-essential-images.json'
r=json.loads(file.read_text(encoding='utf8'));ignore=ROOT/'.gitignore';text=ignore.read_text(encoding='utf8')
for slug in ['game-math-interpolation-paths-v2','game-math-rotation-conversions-v2']:
 path=f'projects/{slug}/publishing/thumbnail-v2.png';p=ROOT/path
 proof=json.loads((p.with_suffix('.json')).read_text(encoding='utf8'))
 assert proof['originalPixelReview'] and proof['mobilePixelReview']
 digest=hashlib.sha256(p.read_bytes()).hexdigest();assert digest==proof['sha256']
 row={'path':path,'purpose':'delivery-thumbnail','reason':'Individually reviewed ImageGen illustration and480px mobile preview; concept-specific Korean headline and natural channel cat; no footage inset.','sha256':digest,'reviewedAt':datetime.datetime.now().astimezone().isoformat(),'project':slug}
 r['entries']=[x for x in r['entries'] if x['path']!=path]+[row]
 exception='!/'+path
 if exception not in text.splitlines():text+='\n'+exception+'\n'
file.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8');ignore.write_text(text,encoding='utf8')
print('Registered only two reviewed delivery thumbnails; QA/source images remain local')
