"""Semantic sample repair. Existing v2 samples/boards stay as held history.

The small centre dot is matched inside reviewed neighbourhoods. No numerical
match or manual guide constitutes pixel approval. Water spray can obscure the
dot, so those windows use a separately labelled, observed contact guide.
"""
import os
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']: os.environ[k]='2'
from pathlib import Path
import json, importlib.util, math
import numpy as np
from scipy.ndimage import uniform_filter
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'projects/motion-sickness-games/production/revision-teaching-clarity-v1'
OUT=ROOT/'shared/output/unpublished-teaching-clarity-revision/motion/semantic-anchor-preparation-v3'
spec=importlib.util.spec_from_file_location('draw',Path(__file__).with_name('render-motion-opening-overlay-pilot-v1.py'))
draw=importlib.util.module_from_spec(spec);spec.loader.exec_module(draw)
read,save,sha=draw.read,draw.save,draw.sha
pre=read(R/'retained-annotation-preflight-execution-v1.json')
old=read(R/'retained-semantic-anchor-preparation-v2.json')
GUIDES={w['scene']:[(p['frame'],*p['aim']) for p in w['points']] for w in old['windows']}
GUIDES['01']=[(f,*({15:[1034,569],90:[1060,629],165:[1053,601]}.get(f,[x,y]))) for f,x,y in GUIDES['01']]
GUIDES['09']=[(0,960,540),(300,960,540),(315,928,367),(330,903,291),(345,903,291),(359,903,291)]
GUIDES['11']=[(0,960,540),(180,960,540),(195,960,540),(210,960,540),(225,960,540),
 (240,1070,535),(255,1300,548),(270,1395,560),(285,1258,560),(299,1055,557)]
BLUE01=[(0,440,300,407,575),(210,440,300,407,575),(225,350,290,317,565),
 (240,370,270,337,548),(255,268,245,236,525),(270,256,241,224,521),(299,218,241,186,521)]
BLUE03=[(0,399,275,389,535),(299,399,275,389,535)]
# Same left/front tower timber at y400. Hide during the rapid look-around.
NEAR05=[(0,652,425),(15,168,425),(30,88,425),(45,79,425),(60,64,425),(75,70,425),(90,68,425)]
FAR05=[(0,28,605,185,600),(15,1470,514,1610,511),(30,1515,514,1655,511),
 (45,1480,514,1620,511),(60,1455,514,1595,511),(75,1450,514,1590,511),(90,1450,514,1590,511)]
BEAM07=[(0,1040,520),(15,1190,440),(30,1305,440),(45,1355,510),(60,1425,590),
 (75,1520,670),(90,1500,590),(105,1590,575),(120,1630,525),(135,1625,465),
 (150,1690,410),(165,1835,420),(180,1785,415),(195,1840,385),(210,1990,260)]
DOOR07=[(0,353,480),(15,565,635),(30,590,744),(45,660,835),(60,716,928),
 (75,786,1020),(90,825,999),(105,834,940),(120,851,910),(135,855,855),
 (150,862,768),(165,922,674),(180,950,588),(195,1035,540),(210,1100,494),
 (225,1075,410),(240,1125,347),(251,1110,330)]
CROSS11=[(0,34,324,635,428),(15,34,185,590,290),(30,33,180,565,281),
 (45,28,180,553,295),(60,95,245,751,360),(180,1090,493,1700,347),
 (195,1080,514,1700,369),(210,1090,476,1710,337)]
def interp(g,f):return [float(np.interp(f,[x[0] for x in g],[x[i] for x in g])) for i in range(1,len(g[0]))]

def point(im,sid,f):
    guided=interp(GUIDES[sid],f)
    if sid not in ['01','03']:
        return dict(aim=guided,visible=sid=='09' or (sid=='11' and f>=180),
          guide=guided,method='Observed reticle/spray neighbourhood; directly review the actual frame',score=None)
    # A broad arc correlation previously matched an unrelated white feature.
    # The centre dot is a compact bright patch; search only its observed region.
    x0=max(0,int(guided[0]-125));x1=min(1920,int(guided[0]+125))
    y0=max(100,int(guided[1]-125));y1=min(900,int(guided[1]+125))
    a=np.asarray(im,dtype=np.float32)[y0:y1,x0:x1].min(2)
    contrast=uniform_filter(a,3)-uniform_filter(a,11)
    yy,xx=np.unravel_index(np.argmax(contrast),contrast.shape)
    score=float(contrast[yy,xx]);found=[int(x0+xx),int(y0+yy)]
    return dict(aim=found,visible=score>45 and math.dist(found,guided)<120,
      guide=guided,score=round(score,3),method='Compact centre-dot contrast inside observed region; no automatic approval')

def annotate(im,sid,f,p):
    layer=Image.new('RGBA',im.size);d=ImageDraw.Draw(layer)
    if sid in ['01','03']:
        if p['visible']:
            x,y=p['aim'];d.ellipse((x-42,y-31,x+42,y+31),outline=draw.RED,width=4)
            draw.label(d,(min(1500,max(520,x-120)),max(180,y-130)),'조준 위치',draw.RED,30)
        a=interp(BLUE01 if sid=='01' else BLUE03,f)
        draw.line(d,tuple(a[:2]),tuple(a[2:]),draw.BLUE,5)
        draw.label(d,(520,216),'배경 기둥',draw.BLUE,30);draw.line(d,(520,251),tuple(a[:2]),draw.BLUE,3)
        draw.label(d,(550,843),'조준 위치와 배경의 이동을 따로 봅니다','#ffffff',27)
    elif sid=='05':
        if f<=90:
            a=interp(NEAR05,f);draw.line(d,(a[0],a[1]-64),(a[0],a[1]+64),draw.RED,5)
            draw.label(d,(620,160),'가까운 기둥',draw.RED,30);draw.line(d,(660,205),tuple(a),draw.RED,3)
            b=interp(FAR05,f);draw.line(d,tuple(b[:2]),tuple(b[2:]),draw.BLUE,5)
            draw.label(d,(1320,360),'먼 울타리',draw.BLUE,30);draw.line(d,(1420,405),tuple(b[:2]),draw.BLUE,3)
        draw.label(d,(610,843),'위치를 옮기면 가까운 것과 먼 것의 배치도 달라집니다','#ffffff',27)
    elif sid=='07':
        a=interp(BEAM07,f)
        if f<205 and a[0]<1880:
            draw.label(d,(min(1500,max(1020,a[0]-330)),max(155,min(620,a[1]-140))),'게임의 레이저',draw.RED,28)
            draw.arrow(d,(a[0]-110,a[1]-100),tuple(a),draw.RED,4)
        b=interp(DOOR07,f)
        if b[1]<870:
            draw.line(d,(b[0],b[1]-70),(b[0],min(865,b[1]+70)),draw.BLUE,5)
            draw.label(d,(560,180),'벽의 문틀',draw.BLUE,28);draw.line(d,(670,225),tuple(b),draw.BLUE,3)
        draw.label(d,(480,840),'서로 다른 발췌 장면 · 바뀐 뒤에도 방향을 읽을 단서','#ffffff',27)
    elif sid=='09':
        x,y=p['aim'];d.ellipse((x-42,y-31,x+42,y+31),outline=draw.RED,width=4)
        draw.label(d,(1180,530),'물줄기' if f>=338 else '조준 위치',draw.RED,30)
        draw.line(d,(1180,565),(x+42,y),draw.RED,3)
        draw.label(d,(570,842),'어느 면을 향하는지 먼저 찾습니다','#ffffff',27)
    elif sid=='11':
        if p['visible']:
            x,y=p['aim'];d.ellipse((x-44,y-34,x+44,y+34),outline=draw.RED,width=4)
            draw.label(d,(700,695),'물줄기',draw.RED,28);draw.line(d,(820,695),(x-44,y+34),draw.RED,3)
        if f<=60 or 180<=f<=210:
            a=interp(CROSS11,f);draw.line(d,tuple(a[:2]),tuple(a[2:]),draw.BLUE,5)
            draw.label(d,(min(1450,max(580,a[0]+80)),max(165,min(605,a[1]-80))),'가로대',draw.BLUE,28)
        draw.label(d,(590,842),'보는 방향의 변화와 도구의 움직임을 구분합니다','#ffffff',27)
    assert layer.getbbox()[3]<=910
    return Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB')

def main():
    assert not OUT.exists();OUT.mkdir(parents=True)
    state=dict(schemaVersion=1,recordedAt=draw.now(),stage='semantic-sample-repair-direct-review-pending',
      v2Preserved=True,v2SampleReviewCompleted=True,v2Approved=False,
      v2Findings=['01 f15/90/165 arc correlation marks a false centre',
      '09 f315 onward and11 early/late reticle is not fixed centre',
      '01 background post moves after225;05 near-post guide misses actual timber',
      '11 crossbar guide after225 lies in sky; suppress unverified interval'],
      sourceOrPcmModified=0,newGitImages=0,worldCoordinatesMeasured=False,
      allIntermediateFramesApproved=False,finalCaptionedPixelsApproved=False,windows=[])
    font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',21)
    for w in pre['windows']:
        folder=OUT/f"scene{w['scene']}";folder.mkdir();rows=[];points=[]
        for row in w['samples']:
            src=ROOT/row['path'];assert sha(src)==row['sha256']
            im=Image.open(src).convert('RGB');f=row['frame']
            p=point(im,w['scene'],f) if w['scene']!='07' else dict(aim=None,visible=False,method='Game beam and door semantic guides only')
            p['frame']=f;out=annotate(im,w['scene'],f,p);dest=folder/f'anchor-{f:04d}.png';out.save(dest)
            rows.append(dict(frame=f,path=draw.rel(dest),sha256=sha(dest)));points.append(p)
        boards=[]
        for i in range(0,len(rows),6):
            im=Image.new('RGB',(1920,780),'#181818');d=ImageDraw.Draw(im)
            for j,row in enumerate(rows[i:i+6]):
                x=j%3*640;y=j//3*390;im.paste(Image.open(ROOT/row['path']).resize((640,360)),(x,y+30))
                p=points[i+j];d.text((x+5,y+4),f"scene{w['scene']} f{row['frame']} aim{p['aim']} visible{p['visible']}",font=font,fill='white')
            dest=folder/f'board-{i//6+1:02d}.png';im.save(dest);boards.append(dict(path=draw.rel(dest),sha256=sha(dest)))
        state['windows'].append(dict(scene=w['scene'],source=w['source'],sourceSha256=w['sourceSha256'],frames=w['frames'],
          sceneLocalStart=w['sceneLocalStart'],samples=rows,points=points,boards=boards,allAnchorsDirectlyReviewed=False))
    save(R/'retained-semantic-anchor-preparation-v3.json',state)
    print(json.dumps({w['scene']:[(p['frame'],p['aim'],p['visible'],p.get('score')) for p in w['points']] for w in state['windows']}))
if __name__=='__main__':main()
