"""Scene decisions and actual encoded picture evidence, distinct from user review."""
import sys,io,json,math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE));import render
def direction_audit():
 records=[];samples=[]
 for eid,e in render.base.EPISODES.items():
  ts=render.base.tracks(e);by={}
  for t in ts:by.setdefault(t['scene'],[]).append(t)
  for s in e['scenes']:
   rr=dict(episode=eid,scene=s['scene'],start=s['start'],end=s['end'],decision='Retain verified native game / necessary abstract diagram; no image-facing motion assertion',scope='scene inventory and model semantics, not a claim of full human playback')
   tt=by.get(s['scene'],[])
   if tt:
    t=tt[0];rr.update(asset=t['asset'],mode=t['mode'])
    if t['mode']=='motion':
     kind=t['lesson']['motion']['parameters'].get('kind');down=t['lesson']['motion'].get('positiveYIsDown',False)
     if t['asset']=='forza':policy='Actual high-angle car, nose-up calibration; rotate nose to projected velocity tangent'
     elif t['asset']=='mario':policy='Actual upright side profile; horizontal facing follows nonzero horizontal velocity, hold facing at a stop; descent does not invert body'
     elif down:policy='Actual side-profile kart remains upright during vertical throw/fall; +y is down; no reversing interpretation of vertical velocity'
     else:policy='Actual side-profile kart; body forward +x; negative horizontal velocity may mean reversing, not forced body rotation'
     rr.update(decision=policy,modelKind=kind,positiveYDown=down)
     tested=0;directions=set();fitting=render.base.motion.fit(t['lesson'])
     for sec in __import__('numpy').linspace(max(t['start'],s['start']),min(t['end'],s['end'])-.00001,121):
      q=render.base.anchor(dict(t,sceneStart=s['start']),float(sec),fitting);v=render.base.motion.raw(q['model'],q['velocity']);angle=math.atan2(-v[1],v[0]);facing=angle if t['asset']=='forza' else 0 if v[0]>=0 else math.pi
      if t['asset']=='forza' and __import__('numpy').linalg.norm(v[:2])>1e-8:
       m=q['model'];dt=1e-4
       before=render.base.motion.state(m['parameters'],q['t']-dt)[0];after=render.base.motion.state(m['parameters'],q['t']+dt)[0]
       displacement=render.base.motion.raw(m,after-before)
       # Independently differentiate the position path; catch projected-axis /
       # rotation-sign mistakes instead of comparing an angle with itself.
       dot=math.cos(facing)*displacement[0]+math.sin(facing)*(-displacement[1]);assert dot/__import__('numpy').linalg.norm(displacement[:2])>1-1e-7
      directions.add('left' if v[0]<-1e-8 else 'right' if v[0]>1e-8 else 'zero-x');tested+=1
     rr.update(modelSamples=tested,horizontalVelocitySigns=sorted(directions),encodedMotionReview='pending')
    elif t['asset']=='beamng':rr.update(decision='Genuine side-profile car; body facing fixed during spring oscillation / vertical jump; force and velocity arrows independent')
    else:rr.update(decision='Keep actual game image as reference context; do not infer facing from independent diagram arrows')
   records.append(rr)
 render.save(HERE/'scene-direction-audit.json',dict(rows=records,allScenesClassified=True,humanReviewed=False))
 return records
def frame(path,t):
 raw=render.ff(['-threads','2','-ss',t,'-i',path,'-frames:v','1','-f','image2pipe','-vcodec','png','-'],capture=True)
 return Image.open(io.BytesIO(raw)).convert('RGB')
def collect(eid=None):
 plan=render.read(HERE/'plan.json');out=HERE/'local/encoded-review';out.mkdir(exist_ok=True);manifest=[]
 for row in plan['episodes']:
  if eid and eid!=row['id']:continue
  receipt=HERE/'deliveries'/f'{row["id"]}.json'
  if not receipt.exists():continue
  delivery=render.read(receipt);f=delivery['files']['captioned']['path'];points=[('overview',min(row['end']-.3,row['roadmap']+2)),('recap',min(row['recapEnd']-.4,row['recap'][-1]['at']+1.5))]
  e=render.base.EPISODES[row['id']]
  for a,z in render.direction_ranges(e):
   if a<=row['start'] and z>=row['end']:continue
   if a>=row['recapStart']:continue
   points.extend((f'direction-{a:.3f}-{part}',a+(z-a)*u) for part,u in [('a',.15),('b',.5),('c',.85)])
  pages=[];board=None
  for i,(label,t) in enumerate(points):
   if i%12==0:
    if board is not None:board.save(out/f'{row["id"]}-{len(pages):02}.jpg',quality=94);pages.append(str(out/f'{row["id"]}-{len(pages):02}.jpg'))
    board=Image.new('RGB',(3*640,4*385),'#171717');d=ImageDraw.Draw(board)
   im=frame(f,t);thumb=im.resize((640,360),Image.Resampling.LANCZOS);x=i%3*640;y=(i%12)//3*385;board.paste(thumb,(x,y));d.text((x+8,y+363),f'{row["id"]} {label}  {t:.3f}s',fill='white')
   if label in ('overview','recap'):
    im.save(out/f'{row["id"]}-{label}.png');im.resize((375,211),Image.Resampling.LANCZOS).save(out/f'{row["id"]}-{label}-mobile.png')
   manifest.append(dict(episode=row['id'],label=label,seconds=t,source=f))
  if board is not None:board.save(out/f'{row["id"]}-{len(pages):02}.jpg',quality=94)
 render.save(out/('sampling-'+(eid or 'all')+'.json'),dict(samples=manifest,reviewStatus='Encoded samples collected; actual image inspection pending',humanReviewed=False))
 return manifest
if __name__=='__main__':
 direction_audit();collect(sys.argv[1] if len(sys.argv)>1 else None)
