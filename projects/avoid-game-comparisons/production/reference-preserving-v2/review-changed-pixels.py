"""Only changed cuts and their joins;22 retained cuts reuse identical evidence."""
from pathlib import Path
import subprocess,json,math,hashlib,sys
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[4];V=Path(__file__).resolve().parent;O=R/'projects/avoid-game-comparisons/production/local/reference-preserving-v2/edit';Q=O/'qa';plan=json.loads((V/'edit-plan.json').read_text(encoding='utf8'));prior=json.loads((O/'first-pass/qa/pixel-sample-index.json').read_text(encoding='utf8'));proof=json.loads((O/'retained-range-proof.json').read_text())
changed=[c for c in plan['cuts'] if c['id']+'.mp4' in proof['changedCuts'] and ('--conclusion-only' not in sys.argv or c['id']=='cut25')];samples={}
for c in changed:
 for r in prior:
  if c['startFrame']-30<=r['frame']<=c['endFrame']+30:samples.setdefault(r['frame'],[]).extend(r['labels'])
 step=6 if c['id']=='cut12' else 60 if c['id'] in ['cut00','cut17'] else 120
 for f in range(c['startFrame']+3,c['endFrame'],step):samples.setdefault(f,[]).append(c['id']+' motion')
 for f in [c['startFrame']-1,c['startFrame'],c['endFrame']-1,c['endFrame']]:samples.setdefault(f,[]).append(c['id']+' join')
rows=[{'frame':f,'time':f/60,'labels':labels} for f,labels in sorted(samples.items())];(Q/'changed-pixel-index.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def balanced(terms):
 if len(terms)==1:return terms[0]
 mid=len(terms)//2;return '('+balanced(terms[:mid])+'+'+balanced(terms[mid:])+')'
seek=math.floor(rows[0]['time']) if '--conclusion-only' in sys.argv else 0
selection=balanced(['eq(n,'+str(r['frame']-seek*60)+')' for r in rows]);vf="select='"+selection+"',scale=480:270:flags=lanczos"
with (Q/'changed-extract.log').open('w') as f:r=subprocess.run(['ffmpeg','-v','error','-ss',str(seek),'-i',str(O/'avoid-game-comparisons-v2-captioned.mp4'),'-an','-vf',vf,'-fps_mode','vfr','-c:v','mjpeg','-threads','1','-q:v','3','-y',str(Q/'changed-%04d.jpg')],stdout=f,stderr=subprocess.STDOUT)
assert r.returncode==0
for page in range(math.ceil(len(rows)/12)):
 chunk=rows[page*12:(page+1)*12];sheet=Image.new('RGB',(1440,310*math.ceil(len(chunk)/3)),(22,22,22));draw=ImageDraw.Draw(sheet)
 for k,row in enumerate(chunk):
  im=Image.open(Q/f'changed-{page*12+k+1:04}.jpg');x=k%3*480;y=k//3*310;sheet.paste(im,(x,y));draw.text((x+5,y+274),f"{row['time']:.2f}s | "+' / '.join(row['labels'])[:65],fill='white')
 sheet.save(Q/f'changed-contact-{page:02}.jpg')
report={'currentCaptionedSha256':hashlib.sha256((O/'avoid-game-comparisons-v2-captioned.mp4').read_bytes()).hexdigest(),'changedCuts':[c['id'] for c in changed],'sampleCount':len(rows),'sheets':math.ceil(len(rows)/12),'retainedCutCount':len(plan['cuts'])-len(changed),'proof':'retained-range-proof.json','status':'awaiting direct images review'};(Q/'changed-pixels.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
