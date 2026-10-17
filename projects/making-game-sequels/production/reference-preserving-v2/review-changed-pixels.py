"""Inspect only changed cut/caption pixels and joins; retain unchanged evidence."""
from pathlib import Path
import json,subprocess,math,hashlib
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[4];P=R/'projects/making-game-sequels';O=P/'production/local/reference-preserving-v2/edit'
plan=json.loads((P/'production/reference-preserving-v2/edit-plan.json').read_text());repair=json.loads((O/'active-inpoint-repair.json').read_text());assert repair['status']=='repaired-masters-ready-for-QA'
Q=O/('qa/changed-final' if repair.get('repairGeneration',1)>1 else 'qa/changed');Q.mkdir(exist_ok=True)
for name,digest in repair['retainedInputs'].items():assert hashlib.sha256((O/name).read_bytes()).hexdigest()==digest
for cid,digest in repair['unchangedCutHashes'].items():assert hashlib.sha256((O/(cid+'.mp4')).read_bytes()).hexdigest()==digest
for cid,digest in repair.get('retainedFromPreviousRepair',{}).items():assert hashlib.sha256((O/(cid+'.mp4')).read_bytes()).hexdigest()==digest
cuts=[c for c in plan['cuts'] if c['id'] in repair.get('rerenderedCuts',repair['changedCuts'])];prior=json.loads((O/'first-pass/qa/pixel-sample-index.json').read_text());samples={x['frame']:x['labels'] for x in prior if any(c['startFrame']-15<=x['frame']<=c['endFrame']+15 for c in cuts)}
for c in cuts:
 for f in [c['startFrame']-2,c['startFrame']+2,c['endFrame']-2,c['endFrame']+2]:samples.setdefault(f,[]).append(c['id']+' join')
for f,label in [(48,'Original branding'),(round((plan['totalFrames']/60-5)*60),'Exact membership end card')]:samples[f]=[label]
rows=[{'frame':f,'time':f/60,'labels':v} for f,v in sorted(samples.items())]
(Q/'index.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def expr(xs):
 if len(xs)==1:return xs[0]
 n=len(xs)//2;return '('+expr(xs[:n])+'+'+expr(xs[n:])+')'
vf="select='"+expr(['eq(n,'+str(x['frame'])+')' for x in rows])+"',scale=480:270:flags=lanczos"
subprocess.run(['ffmpeg','-v','error','-i',str(O/'making-game-sequels-v2-captioned.mp4'),'-an','-vf',vf,'-fps_mode','vfr','-c:v','mjpeg','-threads','1','-q:v','3','-y',str(Q/'frame-%04d.jpg')],check=True)
for n in range(math.ceil(len(rows)/12)):
 chunk=rows[n*12:(n+1)*12];im=Image.new('RGB',(1440,math.ceil(len(chunk)/3)*310),'#161616');d=ImageDraw.Draw(im)
 for i,row in enumerate(chunk):
  x=i%3*480;y=i//3*310;im.paste(Image.open(Q/f'frame-{n*12+i+1:04}.jpg'),(x,y));d.text((x+5,y+276),f"{row['time']:.2f}s | "+' / '.join(row['labels'])[:65],fill='white')
 im.save(Q/f'contact-{n:02}.jpg')
print(json.dumps({'changedSamples':len(rows),'sheets':math.ceil(len(rows)/12),'unchangedCutInputsVerified':len(repair['unchangedCutHashes']),'directReview':'pending'}))
