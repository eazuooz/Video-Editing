"""Repair only05/07; reuse the reviewed v4 samples of the other four windows."""
from pathlib import Path
import importlib.util, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
spec=importlib.util.spec_from_file_location('anchors_v4',Path(__file__).with_name('prepare-motion-semantic-anchors-v4.py'))
v4=importlib.util.module_from_spec(spec);spec.loader.exec_module(v4)
ROOT,R,draw=v4.ROOT,v4.R,v4.draw
OUT=ROOT/'shared/output/unpublished-teaching-clarity-revision/motion/semantic-anchor-preparation-v5'
NEAR=[(0,652,425),(15,168,425),(30,88,425),(45,165,425),(60,247,425),(75,205,425),(90,205,425)]

def door(im,f):
    gx,gy=v4.interp(v4.DOOR07,f)
    if gy>=870: return dict(visible=False,reason='Boundary below the caption-safe field')
    x0=max(0,int(gx-200));x1=min(1920,int(gx+70));y0=max(100,int(gy-40));y1=min(890,int(gy+41))
    a=np.asarray(im,dtype=np.int16)[y0:y1,x0:x1]
    mask=(a[:,:,2]-a[:,:,0]>45)&(a[:,:,2]-a[:,:,1]>12)&(a[:,:,2]>110)
    counts=mask.sum(0);xs=np.flatnonzero(counts>=20)
    if not len(xs):return dict(visible=False,reason='No visible blue door boundary in the reviewed neighbourhood')
    # Choose the cyan edge closest to the observed door guide, not a bright sky.
    xx=int(min(xs,key=lambda x:abs(x+x0-gx)))+x0
    return dict(visible=True,xy=[xx,gy],reason='Visible cyan boundary; screen coordinates, not world measurement')

def point(im,sid,f):
    if sid=='07':return dict(aim=None,visible=False,door=door(im,f),method='Visible door boundary and game laser only')
    return v4.point(im,sid,f)

def annotate(im,sid,f,p):
    if sid not in ['05','07']:return v4.annotate(im,sid,f,p)
    layer=Image.new('RGBA',im.size);d=ImageDraw.Draw(layer)
    if sid=='05':
        # The fast pan between0 and15 is deliberately unmarked.
        if f==0 or 15<=f<=90:
            a=v4.interp(NEAR,f);draw.line(d,(a[0],a[1]-64),(a[0],a[1]+64),draw.RED,5)
            draw.label(d,(620,160),'가까운 기둥',draw.RED,30);draw.line(d,(660,205),tuple(a),draw.RED,3)
            b=v4.interp(v4.FAR05,f);draw.line(d,tuple(b[:2]),tuple(b[2:]),draw.BLUE,5)
            draw.label(d,(1320,360),'먼 울타리',draw.BLUE,30);draw.line(d,(1420,405),tuple(b[:2]),draw.BLUE,3)
        draw.label(d,(610,843),'위치를 옮기면 가까운 것과 먼 것의 배치도 달라집니다','#ffffff',27)
    else:
        a=v4.interp(v4.BEAM07,f)
        if f<205 and a[0]<1880:
            draw.label(d,(min(1500,max(1020,a[0]-330)),max(155,min(620,a[1]-140))),'게임의 레이저',draw.RED,28)
            draw.arrow(d,(a[0]-110,a[1]-100),tuple(a),draw.RED,4)
        t=p['door']
        if t['visible']:
            x,y=t['xy'];d.ellipse((x-16,y-25,x+16,y+25),outline=draw.BLUE,width=4)
            draw.label(d,(560,180),'문틀의 파란 경계',draw.BLUE,28);draw.line(d,(670,225),(x,y),draw.BLUE,3)
        draw.label(d,(480,840),'서로 다른 발췌 장면 · 바뀐 뒤에도 방향을 읽을 단서','#ffffff',27)
    assert layer.getbbox()[3]<=910
    return Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB')

def main():
    assert not OUT.exists();OUT.mkdir(parents=True)
    old=draw.read(R/'retained-semantic-anchor-preparation-v4.json')
    state=dict(schemaVersion=1,recordedAt=draw.now(),stage='two-window-sample-repair-awaiting-direct-review',
      v4Preserved=True,sourceOrPcmModified=0,newGitImages=0,worldCoordinatesMeasured=False,
      allIntermediateFramesApproved=False,finalCaptionedPixelsApproved=False,windows=[])
    font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',21)
    for w in v4.pre['windows']:
        if w['scene'] not in ['05','07']:
            row=next(x for x in old['windows'] if x['scene']==w['scene']);state['windows'].append(dict(row,reusedFromV4=True));continue
        folder=OUT/f"scene{w['scene']}";folder.mkdir();rows=[];points=[]
        for row in w['samples']:
            src=ROOT/row['path'];assert draw.sha(src)==row['sha256']
            im=Image.open(src).convert('RGB');f=row['frame'];p=point(im,w['scene'],f);p['frame']=f
            dest=folder/f'anchor-{f:04d}.png';annotate(im,w['scene'],f,p).save(dest)
            rows.append(dict(frame=f,path=draw.rel(dest),sha256=draw.sha(dest)));points.append(p)
        boards=[]
        for i in range(0,len(rows),6):
            im=Image.new('RGB',(1920,780),'#181818');d=ImageDraw.Draw(im)
            for j,row in enumerate(rows[i:i+6]):
                x=j%3*640;y=j//3*390;im.paste(Image.open(ROOT/row['path']).resize((640,360)),(x,y+30))
                t=points[i+j].get('door',{});d.text((x+5,y+4),f"scene{w['scene']} f{row['frame']} door{t.get('xy')} visible{t.get('visible')}",font=font,fill='white')
            dest=folder/f'board-{i//6+1:02d}.png';im.save(dest);boards.append(dict(path=draw.rel(dest),sha256=draw.sha(dest)))
        state['windows'].append(dict(scene=w['scene'],source=w['source'],sourceSha256=w['sourceSha256'],frames=w['frames'],
          sceneLocalStart=w['sceneLocalStart'],samples=rows,points=points,boards=boards,allAnchorsDirectlyReviewed=False,reusedFromV4=False))
    draw.save(R/'retained-semantic-anchor-preparation-v5.json',state)
    print(json.dumps(dict(newSamples=39,newBoards=7,reusedSamples=88,reusedBoards=17)))
if __name__=='__main__':main()
