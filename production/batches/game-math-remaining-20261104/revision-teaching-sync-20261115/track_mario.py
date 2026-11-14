"""Pixel-derived editorial guide; hide it when Mario is behind the wall.

Red-cap/clothing pixels in this inspected snow scene locate a visible point,
not game coordinates or an alleged runtime detector/confidence measurement.
"""
import io
import json
from pathlib import Path
import subprocess

import numpy as np
from scipy import ndimage
from PIL import Image,ImageDraw
from inventory import HERE,ROOT,read,save,sha
from render_revision import FF,CREATE


def main():
    plan=read(HERE/'game-additions.json')
    game=next(g for g in plan['additions'] if g['episode']=='M24' and g['scene']=='004')
    source=ROOT/game['source']['file'];w,h=960,540
    data=subprocess.check_output([str(FF),'-v','error','-nostdin','-threads','1','-ss',str(game['sourceIn']),
        '-i',str(source),'-t',str(game['duration']),'-vf','fps=20,scale=960:540','-threads','1','-pix_fmt','rgb24','-f','rawvideo','-'],creationflags=CREATE)
    frames=np.frombuffer(data,np.uint8).reshape(-1,h,w,3);keys=[];hidden=[];review=[]
    for i,frame in enumerate(frames):
        r,g,b=np.moveaxis(frame.astype(np.float32),-1,0)
        mask=(r>145)&(g<115)&(b<130)&(r>g*1.8)&(r>b*1.4)
        blue=(b>65)&(b>r*1.4)&(b>g*1.2)
        mask[:55,:]=False;mask[460:,:]=False;mask[:,:290]=False;mask[:,650:]=False
        labels,total=ndimage.label(mask);objects=ndimage.find_objects(labels)
        choices=[]
        for n,slices in enumerate(objects,1):
            if slices is None:continue
            yy,xx=np.where(labels[slices]==n);area=len(xx)
            if area<5:continue
            x=xx.mean()+slices[1].start;y=yy.mean()+slices[0].start
            support=int(blue[max(0,int(y)-45):min(h,int(y)+65),max(0,int(x)-40):min(w,int(x)+40)].sum())
            if support<10:continue
            choices.append((area,x,y))
        if choices:
            area,x,y=max(choices)
            keys.append([i/20,float(x/w),float(y/h)])
        else:
            hidden.append(i/20)
            keys.append([i/20,keys[-1][1] if keys else .5,keys[-1][2] if keys else .5])
        if i%5==0:
            im=Image.fromarray(frame).resize((480,270));draw=ImageDraw.Draw(im)
            if choices:
                cx,cy=keys[-1][1]*480,keys[-1][2]*270;draw.ellipse((cx-14,cy-14,cx+14,cy+14),outline='#73c7c2',width=2)
            draw.text((6,6),f'{i/20:.2f}s'+(' hidden' if not choices else ''),fill='black');review.append(im)
    hide=[]
    for t in hidden:
        if hide and t-hide[-1][1]<.051:hide[-1][1]=t+.05
        else:hide.append([t,t+.05])
    marks=game['marks'];marks.update(keys=keys,hideIntervals=hide,hideAfter=game['duration'],
        label='화면에서 추적하는 점',basis='20 Hz red cap/clothing pixels in the inspected independent recording; guide hidden while no visible target pixels remain')
    save(HERE/'mario-track-correction.json',dict(sourceSha256=sha(source),sourceIn=game['sourceIn'],
        samplingHz=20,keys=keys,hideIntervals=hide,marks=marks,actualVisualReview=False))
    board=Image.new('RGB',(480*4,270*((len(review)+3)//4)))
    for i,im in enumerate(review):board.paste(im,(i%4*480,i//4*270))
    board.save(HERE/'mario-track-contact.jpg',quality=95)
    print('prepared',len(keys),'observations, hidden',hide)


if __name__=='__main__':main()
