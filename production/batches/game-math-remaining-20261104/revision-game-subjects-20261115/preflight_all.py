"""Check every changed scene before costly masters; board review is still human."""
import json,sys,time
from PIL import Image,ImageDraw
import frame_tests as frames
from subject_revision import *
def main():
 out=HERE/'local/authoring';out.mkdir(exist_ok=True);rows=[]
 selected=sys.argv[1:] or list(EPISODES)
 for eid,e in EPISODES.items():
  if eid not in selected:continue
  if eid=='M21':continue
  ids=set(t['scene'] for t in tracks(e))
  ids.update(sid for key,sids,*_ in CONTEXTS if key==eid for sid in sids)
  if eid=='M33':ids.add('029')
  ep=[]
  for sid in sorted(ids):
   p=frames.render(eid,sid);ep.append(dict(episode=eid,scene=sid,picture=str(p),status='actual-picture-review-pending'))
  for i in range(0,len(ep),16):
   group=ep[i:i+16];board=Image.new('RGB',(1600,250*((len(group)+3)//4)),'black');d=ImageDraw.Draw(board)
   for k,row in enumerate(group):
    im=Image.open(row['picture']).convert('RGB');im.thumbnail((400,225));x=k%4*400;y=k//4*250;board.paste(im,(x,y));d.text((x+5,y+229),eid+'/'+row['scene'],fill='white')
   board.save(out/f'{eid}-{i//16+1:02}.jpg',quality=95)
  rows.extend(ep);print(eid,len(ep),'changed scenes prepared',flush=True)
 priorrows=read(HERE/'authoring-review.json')['rows'] if (HERE/'authoring-review.json').exists() else []
 rows=[r for r in priorrows if r['episode'] not in selected]+rows
 save(HERE/'authoring-review.json',dict(rows=rows,status='pending-human-picture-review',checks='Changed scene midpoint only; motion/joins/captions receive separate encoded QA.',humanReviewed=False))
if __name__=='__main__':main()
