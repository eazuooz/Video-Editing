"""Remove only duplicate intermediates belonging to this checked revision."""
from pathlib import Path
import json,hashlib,sys
R=Path(__file__).resolve().parents[4];V=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
for ep in sys.argv[1:]:
 planpath=V/(ep+'-plan.json');p=read(planpath);H=R/'projects'/p['slug']/'production'/p['revision'];O=(H.parent/'local'/p['revision']).resolve()
 assert p['revision']=='gameplay-motion-v4' and O.is_relative_to(R.resolve())
 out=read(H/'outputs.json');qa=read(H/'technical-qa.json');assert out['planSha256']==sha(planpath)
 assert {x['path']:x['sha256'] for x in qa['checks']}=={x['path']:x['sha256'] for x in out['outputs']}
 for x in out['outputs']:assert sha(R/x['path'])==x['sha256']
 removed=[]
 for f in [O/'clean-video.mp4',O/'captioned-video.mp4',*O.glob('game-*.wav')]:
  assert f.resolve().parent==O
  if f.exists():removed.append(dict(path=f.relative_to(R).as_posix(),bytes=f.stat().st_size));f.unlink()
 (H/'intermediate-cleanup.json').write_text(json.dumps(dict(verifiedFinalHashes=True,oldDeliveriesPreserved=True,removed=removed),indent=2)+'\n',encoding='utf8')
 print(ep,'reclaimed',round(sum(x['bytes'] for x in removed)/1024**3,2),'GiB',flush=True)
