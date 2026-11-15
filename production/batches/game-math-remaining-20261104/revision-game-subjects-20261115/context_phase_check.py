"""Check early/late original formula states before revised context encodes."""
from frame_tests import *

def main(ids):
 rows=[];out=HERE/'local/context-phases';out.mkdir(parents=True,exist_ok=True)
 for eid,sids,*rest in CONTEXTS:
  if eid not in ids:continue
  e=EPISODES[eid]
  for sid in sids:
   s=next(x for x in e['scenes'] if x['scene']==sid)
   for frac in (.15,.85):
    # Offset prevents reuse of the old midpoint-only authoring cache.
    t=s['start']+(s['end']-s['start'])*frac+.001
    f=render(eid,sid,t);rows.append(dict(episode=eid,scene=sid,fraction=frac,time=t,file=str(f)))
    print(eid,sid,frac,str(f),flush=True)
 boards=[]
 for first in range(0,len(rows),12):
  group=rows[first:first+12];im=Image.new('RGB',(1440,294*math.ceil(len(group)/3)),'black');d=ImageDraw.Draw(im)
  for j,row in enumerate(group):
   x=j%3*480;y=j//3*294;im.paste(Image.open(row['file']).resize((480,270)),(x,y));d.text((x+5,y+274),f'{row["episode"]}/{row["scene"]} {row["fraction"]:.0%} @ {row["time"]:.2f}',fill='white')
  target=out/f'{"-".join(ids)}-{first//12+1:02}.jpg';im.save(target,quality=95);boards.append(str(target))
 save(out/f'{"-".join(ids)}.json',dict(rows=rows,boards=boards,actuallyInspected=False,humanReviewed=False))
if __name__=='__main__':main(sys.argv[1:])
