"""Read the existing editor selection pixels for an editorial per-frame anchor."""
from probe import *
import numpy as np
from scipy.ndimage import label as components
def main():
 d=rd(H/'annotations.json');w=next(x for x in d['windows'] if x['id']=='character');keys=[];stats=[]
 with av.open(str(B/'pair/captioned.mp4')) as c:
  s=c.streams.video[0];s.thread_type='AUTO';c.seek(int(Fraction(w['startFrame'],60)/s.time_base),stream=s,backward=True)
  for v in c.decode(s):
   f=round(float(v.pts*s.time_base)*60)
   if f<w['startFrame']:continue
   if f>=w['endFrame']:break
   im=np.array(v.to_image().resize((480,270))).astype(float);r,g,b=im[:,:,0],im[:,:,1],im[:,:,2]
   mask=(r>g*1.03)&(g>b*1.35)&(r>90);mask[:50]=False;mask[214:]=False;mask[:,:100]=False;mask[:,325:]=False
   lab,n=components(mask);sizes=np.bincount(lab.ravel());sizes[0]=0;k=sizes.argmax();assert sizes[k]>100,(f,int(sizes[k]))
   y,x=np.where(lab==k);x1,x2,y1,y2=x.min(),x.max(),y.min(),y.max();cx=(x1+x2)/2;cy=(y1+y2)/2
   rx=(x2-x1)/2*1.35+4;ry=(y2-y1)/2*1.12+3
   pts=[[round(cx-rx,2),round(cy-ry,2)],[round(cx+rx,2),min(217,round(cy+ry,2))]]
   keys.append(dict(frame=f,points=pts));stats.append(dict(frame=f,selectedPixels=int(sizes[k]),observedBox=[int(x1),int(y1),int(x2),int(y2)]))
 assert len(keys)==w['endFrame']-w['startFrame']
 wr(O/'character-observed-anchors.json',dict(keys=keys,frames=stats,method='Existing yellow editor selection pixels; largest connected body component inside reviewed region; not simulated motion/normal/depth measurement'))
 w.update(keyframes=keys,labelAt=[15,38],tracking='per-frame anchor from visible editor body-selection pixels; direct motion QA pending')
 wr(H/'annotations.json',d)
if __name__=='__main__':main()
