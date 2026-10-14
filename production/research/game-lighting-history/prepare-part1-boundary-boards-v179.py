from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw
root=Path(__file__).resolve().parents[3];folder=root/'projects/game-lighting-history-04/production/local/part1-boundaries-v178'
state=json.loads((folder/'execution.json').read_text('utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=folder/'boards-v179.json'
if out.exists():raise RuntimeError('Preserve boards')
groups=[['wheel-112','wheel-112-5','wheel-113','wheel-185-8'],['man-37','man-37-5','man-38','fan-32','fan-32-5','fan-33'],['mobile-263','mobile-264','mobile-265','mobile-266']]
records=[]
for i,names in enumerate(groups):
 board=Image.new('RGB',(1920,((len(names)+1)//2)*566),'#101010');draw=ImageDraw.Draw(board);refs=[]
 for j,n in enumerate(names):
  r=next(x for x in state['results'] if x['id']==n);p=root/r['path']
  if sha(p)!=r['sha256']:raise RuntimeError('Changed sample')
  im=Image.open(p).convert('RGB');x=(j%2)*960;y=(j//2)*566;draw.text((x+8,y+5),n+' native seconds',fill='white');board.paste(im,(x,y+26));refs.append({k:r[k] for k in ['id','path','sha256','seconds']})
 p=folder/('board-v179-'+str(i+1)+'.png');board.save(p);records.append(dict(path=p.relative_to(root).as_posix(),sha256=sha(p),samples=refs,directlyRead=False,localOnly=True))
out.write_text(json.dumps(dict(extraction=dict(path=(folder/'execution.json').relative_to(root).as_posix(),sha256=sha(folder/'execution.json')),boards=records,allDirectlyRead=False,allFinalPixelsReviewed=False),ensure_ascii=False,indent=2)+'\n','utf-8')
print('3 local-only source boards; original samples and extraction untouched.')
