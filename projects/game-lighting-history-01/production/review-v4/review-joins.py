"""Inspect changed-GOP joins and every caption overlapping reencoded ranges."""
from probe import *
import numpy as np,math

def main():
 state=rd(O/'pair/visual-execution.json');cues=rd(B/'captions.json')['cues']['ko'];q=O/'qa';items=[]
 for i,(a,b) in enumerate(state['windows']):
  frames={a:'patch-start',b-1:'patch-end'}
  for c in cues:
   lo=max(a,round(c['startSeconds']*60));hi=min(b,round(c['endSeconds']*60))
   if hi>lo:frames[(lo+hi)//2]='caption-'+str(c['index'])
  with av.open(str(O/f'pair/patch-{i}-captioned.mp4')) as new,av.open(str(B/'pair/captioned.mp4')) as old:
   for f,why in sorted(frames.items()):
    im=frame(new,f-a);base=frame(old,f)
    x=np.asarray(im.crop((0,880,1920,1080)),dtype=float);y=np.asarray(base.crop((0,880,1920,1080)),dtype=float)
    rmse=float(np.sqrt(np.mean((x-y)**2)))
    items.append(dict(frame=f,patch=i,reason=why,captionRegionRmse=rmse))
    im.resize((480,270)).save(q/f'join-{len(items)-1}.jpg',quality=94)
 font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',16)
 for page in range(math.ceil(len(items)/12)):
  board=Image.new('RGB',(1440,1200),'#111');dr=ImageDraw.Draw(board)
  for j,it in enumerate(items[page*12:(page+1)*12]):
   k=page*12+j;x=j%3*480;y=j//3*300;board.paste(Image.open(q/f'join-{k}.jpg'),(x,y+26));dr.text((x+3,y+3),f'{it["reason"]} {it["frame"]/60:.2f}s',font=font,fill='white')
  board.save(q/f'joins-{page}.jpg',quality=94)
 wr(q/'joins.json',dict(items=items,boards=math.ceil(len(items)/12),maxCaptionRegionRmse=max(x['captionRegionRmse'] for x in items),method='Every changed GOP first/last frame and every overlapping caption cue; direct encoded pixels plus caption ROI comparison.'))
 print('Caption/join checks',len(items),'boards',math.ceil(len(items)/12),flush=True)
if __name__=='__main__':main()
