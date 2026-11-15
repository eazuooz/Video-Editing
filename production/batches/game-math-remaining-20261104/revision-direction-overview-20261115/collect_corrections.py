"""Actual final encoded glyph/axis samples; first-pass sheets remain preserved."""
import sys,io
from pathlib import Path
from PIL import Image,ImageDraw
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE));import render
def main():
 out=HERE/'local/correction-review';out.mkdir(exist_ok=True);records=[]
 for row in render.read(HERE/'plan.json')['episodes']:
  eid=row['id']
  if eid not in ('M25','M26','M28') or (len(sys.argv)>1 and eid not in sys.argv[1:]):continue
  f=HERE/'deliveries'/f'{eid}.json'
  if not f.exists():continue
  delivery=render.read(f)
  if not delivery.get('correctionsComplete'):continue
  source=delivery['files']['captioned'];e=render.base.EPISODES[eid];points=[]
  if eid=='M25':
   points.append(('overview-glyph',row['roadmap']+2))
   for t in render.base.tracks(e):
    if t['mode']=='motion' and t['lesson']['motion'].get('positiveYIsDown'):points.append((t['scene']+'-vertical-v',min(t['end']-.3,t['start']+1.5)))
  if eid=='M26':
   for t in render.base.tracks(e):
    if t['mode']=='motion' and t['asset']=='kart' and t['lesson']['motion']['parameters'].get('kind')==2:points.append((t['scene']+'-projectile-v',(t['start']+t['end'])/2))
  if eid=='M28':points=[('recap-glyph',row['recap'][-1]['at']+1.5)]
  board=Image.new('RGB',(1920,385*((len(points)+2)//3)),'#151515');d=ImageDraw.Draw(board)
  for i,(label,t) in enumerate(points):
   raw=render.ff(['-threads','2','-ss',t,'-i',source['path'],'-frames:v','1','-f','image2pipe','-vcodec','png','-'],capture=True);im=Image.open(io.BytesIO(raw)).convert('RGB');im.save(out/f'{eid}-{label}.png');im.resize((375,211),Image.Resampling.LANCZOS).save(out/f'{eid}-{label}-mobile.png');x=i%3*640;y=i//3*385;board.paste(im.resize((640,360),Image.Resampling.LANCZOS),(x,y));d.text((x+8,y+362),f'{eid} {label} {t:.3f}s',fill='white');records.append(dict(episode=eid,label=label,seconds=t,source=source,picture=str(out/f'{eid}-{label}.png')))
  board.save(out/f'{eid}-final-correction.jpg',quality=95)
 previous=render.read(out/'manifest.json')['records'] if (out/'manifest.json').exists() else []
 replaced={r['episode'] for r in records};records=[r for r in previous if r['episode'] not in replaced]+records
 render.save(out/'manifest.json',dict(records=records,actualImageInspection='pending',humanReviewed=False))
if __name__=='__main__':main()
