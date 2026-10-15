"""Inventory current actual-footage nodes and inspect native motion before annotation."""
from pathlib import Path
import json, av
from fractions import Fraction
from PIL import Image, ImageDraw, ImageFont
R=Path(__file__).resolve().parents[4]
H=Path(__file__).parent
O=H.parent/'local/review-v4'
B=H.parent/'local/review-v3'
def rd(p): return json.loads(p.read_text('utf8'))
def wr(p,d): p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf8')
def frame(c, f):
 s=c.streams.video[0]; c.seek(int(Fraction(f,60)/s.time_base),stream=s,backward=True)
 for v in c.decode(s):
  if v.pts*s.time_base>=Fraction(f,60): return v.to_image()
 raise ValueError(f)
def main():
 O.mkdir(exist_ok=True,parents=True);q=O/'survey';q.mkdir(exist_ok=True)
 plan=rd(B/'plan.json');caps=rd(B/'captions.json')['cues']['ko']
 groups=[]
 for g in plan['nativeGroups']:
  ns=[n for n in plan['nodes'] if n.get('packetIndex')==g['packetIndex'] and n['role']=='actual']
  n=max(ns,key=lambda n:n['frames'])
  points=[n['startFrame']+min(60,n['frames']//5),n['startFrame']+n['frames']//2,n['endFrame']-min(60,n['frames']//5)]
  groups.append(dict(group=g['packetIndex'],nodes=[{k:n.get(k) for k in ['id','startFrame','endFrame','focusKo','sourceId']} for n in ns],representative=n['id'],points=points,cues=[c for c in caps if c['endSeconds']*60>min(n['startFrame'] for n in ns) and c['startSeconds']*60<max(n['endFrame'] for n in ns)]))
 font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',18)
 with av.open(str(B/'pair/captioned.mp4')) as c:
  c.streams.video[0].thread_type='AUTO'
  for i,g in enumerate(groups):
   if i%4==0: board=Image.new('RGB',(1440,4*310),'#151515');draw=ImageDraw.Draw(board)
   y=(i%4)*310
   draw.text((6,y+2),f"G{g['group']:02} {g['representative']} · "+g['nodes'][0]['focusKo'],font=font,fill='white')
   for j,f in enumerate(g['points']):
    im=frame(c,f);im.save(q/f'g{g["group"]:02}-{j}.jpg',quality=92)
    board.paste(im.resize((480,270)),(480*j,y+30))
    draw.text((480*j+4,y+33),f'{f/60:.2f}s / f{f}',font=font,fill='#ffff00',stroke_width=2,stroke_fill='black')
   if i%4==3 or i==len(groups)-1:board.save(q/f'board-{i//4:02}.jpg',quality=93);print('board',i//4,flush=True)
 wr(O/'inventory.json',dict(baseline=str(B.relative_to(R)),groups=groups))
if __name__=='__main__':main()
