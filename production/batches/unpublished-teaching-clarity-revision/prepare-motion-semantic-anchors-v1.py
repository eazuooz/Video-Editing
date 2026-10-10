"""Editable screen-space observations; source samples retained, no source encode."""
import os
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']: os.environ[k]='2'
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, math, importlib.util, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.signal import fftconvolve

ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'projects/motion-sickness-games/production/revision-teaching-clarity-v1'
OUT=ROOT/'shared/output/unpublished-teaching-clarity-revision/motion/semantic-anchor-preparation-v2'
spec=importlib.util.spec_from_file_location('draw',Path(__file__).with_name('render-motion-opening-overlay-pilot-v1.py'))
draw=importlib.util.module_from_spec(spec);spec.loader.exec_module(draw)
read=draw.read;sha=draw.sha;save=draw.save
pre=read(R/'retained-annotation-preflight-execution-v1.json')
assert pre['allSelectedSamplesDirectlyRead'] if 'allSelectedSamplesDirectlyRead' in pre else all(w['allSelectedSamplesDirectlyRead'] for w in pre['windows'])
RECOVERY='--recover-prepared-images' in sys.argv
if RECOVERY: assert OUT.exists()
else: assert not OUT.exists();OUT.mkdir(parents=True)

def white(im):
    a=np.asarray(im.resize((960,540)),dtype=np.float32)
    return ((a.min(2)>140)&((a.max(2)-a.min(2))<110)).astype(np.float32)
base=Image.open(ROOT/pre['windows'][0]['samples'][0]['path']).convert('RGB')
template=white(base)[204:285,609:647]
assert template.sum()>20
guides03=[(0,881,769),(15,942,714),(30,945,660),(45,942,663),(60,935,638),(75,996,642),(90,1305,675),(105,1425,655),(120,1329,657),(135,1248,630),(150,1545,638),(165,1539,690),(180,1518,697),(195,1488,660),(210,1443,690),(225,1407,643),(240,1368,664),(255,1359,618),(270,1389,643),(285,1386,643),(299,1386,643)]

def reticle(im,sid,f,previous=None):
    if sid in ['05','09','11']: return [960,540],1.0,'observed fixed centre in these selected windows'
    mask=white(im)
    # Reticle template contains two thin arcs and a centre dot, not a filled circle.
    if sid=='03':
        gx=np.interp(f,[p[0] for p in guides03],[p[1] for p in guides03]);gy=np.interp(f,[p[0] for p in guides03],[p[2] for p in guides03])
        x0=max(0,int((gx-100)/2));x1=min(960,int((gx+100)/2));y0=max(85,int((gy-100)/2));y1=min(440,int((gy+100)/2))
    else:
        x0,x1,y0,y1=250,900,160,450
    corr=fftconvolve(mask,template[::-1,::-1],mode='same')/float(template.sum())
    candidate=corr[y0:y1,x0:x1]
    yy,xx=np.unravel_index(np.argmax(candidate),candidate.shape)
    x=int(2*(x0+xx));y=int(2*(y0+yy)+1)
    score=float(candidate[yy,xx])
    return [x,y],score,'white-arc/dot template inside observed semantic search region; direct pixel review required'

# Short lines follow a specific background feature. Screen units are pixels,
# never measured world angles or clinical comfort values.
blue01=[(0,440,300,407,575),(210,440,300,407,575),(225,433,290,400,560),(240,406,266,375,546),(255,388,245,358,525),(270,380,241,350,521),(299,380,241,350,521)]
blue03=[(0,399,275,389,535),(299,399,275,389,535)]
# Different near/far objects are explicitly labelled; rapid yaw is hidden.
near05=[(0,652,425),(15,312,425),(30,350,425),(45,346,425),(60,324,425),(75,318,425),(90,338,425)]
far05=[(0,28,605,185,600),(15,1470,514,1610,511),(30,1515,514,1655,511),(45,1480,514,1620,511),(60,1455,514,1595,511),(75,1450,514,1590,511),(90,1450,514,1590,511)]
# Red marker identifies the actual red beam where visible; remove it when its
# endpoint goes off screen. Its pixel inclination is not a game gravity vector.
beam07=[(0,1040,520),(15,1190,440),(30,1305,440),(45,1355,510),(60,1425,590),(75,1520,670),(90,1500,590),(105,1590,575),(120,1630,525),(135,1625,465),(150,1690,410),(165,1835,420),(180,1785,415),(195,1840,385),(210,1990,260)]
door07=[(0,353,480),(15,565,635),(30,590,744),(45,660,835),(60,716,928),(75,786,1020),(90,825,999),(105,834,940),(120,851,910),(135,855,855),(150,862,768),(165,922,674),(180,950,588),(195,1035,540),(210,1100,494),(225,1075,410),(240,1125,347),(251,1110,330)]
cross11=[(0,34,324,635,428),(15,34,185,590,290),(30,33,180,565,281),(45,28,180,553,295),(60,95,245,751,360),(75,1050,290,1670,470),(90,37,174,680,346),(105,100,304,720,435),(120,275,570,910,625),(135,864,747,1555,758),(150,1080,714,1720,654),(165,1083,555,1720,475),(180,1090,493,1700,347),(195,1080,514,1700,369),(210,1090,476,1710,337),(225,1090,408,1710,270),(240,1090,306,1710,205),(255,1090,291,1710,197),(270,1090,384,1710,272),(285,1090,429,1710,304),(299,1090,424,1710,296)]

def interp(g,f):
    return [float(np.interp(f,[x[0] for x in g],[x[i] for x in g])) for i in range(1,len(g[0]))]

def draw_marks(im,sid,f,point):
    layer=Image.new('RGBA',im.size);d=ImageDraw.Draw(layer)
    # Source credit already exists in the retained encoded action.
    if sid in ['01','03']:
        x,y=point['aim'];d.ellipse((x-42,y-31,x+42,y+31),outline=draw.RED,width=4)
        draw.label(d,(min(1500,max(520,x-120)),max(180,y-158)),'조준 위치',draw.RED,30)
        g=blue01 if sid=='01' else blue03;a=interp(g,f)
        draw.line(d,tuple(a[:2]),tuple(a[2:]),draw.BLUE,5)
        draw.label(d,(520,216),'배경 기둥',draw.BLUE,30)
        draw.line(d,(520,251),tuple(a[:2]),draw.BLUE,3)
        draw.label(d,(550,843),'조준 위치와 배경의 이동을 따로 봅니다','#ffffff',27)
    elif sid=='05':
        if f<=90:
            a=interp(near05,f);draw.line(d,(a[0],a[1]-64),(a[0],a[1]+64),draw.RED,5)
            draw.label(d,(620,160),'가까운 기둥',draw.RED,30);draw.line(d,(660,205),tuple(a),draw.RED,3)
            b=interp(far05,f);draw.line(d,tuple(b[:2]),tuple(b[2:]),draw.BLUE,5)
            draw.label(d,(1320,360),'먼 울타리',draw.BLUE,30);draw.line(d,(1420,405),tuple(b[:2]),draw.BLUE,3)
        draw.label(d,(610,843),'위치를 옮기면 가까운 것과 먼 것의 배치도 달라집니다','#ffffff',27)
    elif sid=='07':
        a=interp(beam07,f)
        if f<205 and a[0]<1880:
            draw.label(d,(min(1500,max(1020,a[0]-330)),max(155,min(620,a[1]-140))),'게임의 레이저',draw.RED,28)
            draw.arrow(d,(a[0]-110,a[1]-100),tuple(a),draw.RED,4)
        b=interp(door07,f)
        if b[1]<870:
            draw.line(d,(b[0],b[1]-70),(b[0],min(865,b[1]+70)),draw.BLUE,5)
            draw.label(d,(560,180),'벽의 문틀',draw.BLUE,28);draw.line(d,(670,225),tuple(b),draw.BLUE,3)
        draw.label(d,(480,840),'서로 다른 발췌 장면 · 바뀐 뒤에도 방향을 읽을 단서','#ffffff',27)
    elif sid=='09':
        x,y=point['aim'];d.ellipse((x-42,y-31,x+42,y+31),outline=draw.RED,width=4)
        draw.label(d,(1180,530),'물줄기' if f>=338 else '조준 위치',draw.RED,30)
        draw.line(d,(1180,565),(x+42,y),draw.RED,3)
        draw.label(d,(570,842),'어느 면을 향하는지 먼저 찾습니다','#ffffff',27)
    elif sid=='11':
        x,y=point['aim'];d.ellipse((x-44,y-34,x+44,y+34),outline=draw.RED,width=4)
        draw.label(d,(700,695),'물줄기' if f>=180 else '조준 위치',draw.RED,28)
        draw.line(d,(820,695),(x-44,y+34),draw.RED,3)
        a=interp(cross11,f)
        if not 65<=f<=170:
            draw.line(d,tuple(a[:2]),tuple(a[2:]),draw.BLUE,5)
            draw.label(d,(min(1450,max(580,a[0]+80)),max(165,min(605,a[1]-80))),'가로대',draw.BLUE,28)
        draw.label(d,(590,842),'보는 방향의 변화와 도구의 움직임을 구분합니다','#ffffff',27)
    assert layer.getbbox()[3]<=910
    return Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB')

state=dict(schemaVersion=1,recordedAt=datetime.now(timezone.utc).isoformat(),stage='sample-anchor-preparation-direct-review-pending',
 worldCoordinatesMeasured=False,clinicalComfortApproved=False,allIntermediateFramesApproved=False,
 finalCaptionedPixelsApproved=False,sourceOrPcmModified=0,newGitImages=0,windows=[])
for w in pre['windows']:
    folder=OUT/f"scene{w['scene']}";folder.mkdir(exist_ok=RECOVERY);rows=[];pts=[]
    for row in w['samples']:
        src=ROOT/row['path'];assert sha(src)==row['sha256']
        im=Image.open(src).convert('RGB');f=row['frame']
        aim,score,method=reticle(im,w['scene'],f)
        point=dict(frame=f,aim=aim,aimTemplateScore=round(score,5),method=method)
        if w['scene'] in ['01','03']: assert score>.40,(w['scene'],f,score)
        out=draw_marks(im,w['scene'],f,point);p=folder/f'anchor-{f:04d}.png'
        if RECOVERY: assert Image.open(p).convert('RGB').tobytes()==out.tobytes()
        else: out.save(p)
        rows.append(dict(frame=f,path=p.relative_to(ROOT).as_posix(),sha256=sha(p)))
        pts.append(point)
    boards=[];font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',21)
    for i in range(0,len(rows),6):
        im=Image.new('RGB',(1920,780),'#181818');d=ImageDraw.Draw(im)
        for j,row in enumerate(rows[i:i+6]):
            x=j%3*640;y=j//3*390
            im.paste(Image.open(ROOT/row['path']).resize((640,360)),(x,y+30))
            d.text((x+5,y+4),f"scene{w['scene']} f{row['frame']} aim{pts[i+j]['aim']} score{pts[i+j]['aimTemplateScore']}",font=font,fill='white')
        p=folder/f'board-{i//6+1:02d}.png'
        if RECOVERY:
            # Retain the already generated board. Its informational header used
            # numpy scalar repr before the serialization repair; sample pixels
            # above are compared exactly and do not depend on that header.
            assert Image.open(p).size==im.size
        else: im.save(p)
        boards.append(dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)))
    state['windows'].append(dict(scene=w['scene'],source=w['source'],sourceSha256=w['sourceSha256'],
      frames=w['frames'],sceneLocalStart=w['sceneLocalStart'],points=pts,samples=rows,boards=boards,
      manualAnchorGuidesAreApproval=False,allAnchorsDirectlyReviewed=False))
state['preparationFailureHistory']={'v1':'Template minimum40 sparse white pixels failed before any sample output; empty directory preserved. Half-resolution antialiasing required a broader brightness mask. No encode or source alteration.'}
state['preparationFailureHistory']['v2']='All127 images/24 boards generated, then numpy int64 JSON serialization failed. Recovery verifies all individual sample pixels exactly in memory and board dimensions, retaining original board headers with numpy scalar repr. Writes only corrected JSON; existing images preserved.'
state['preparationFailureHistory']['metadataRecovery1']='First recovery compared regenerated informational board headers after int conversion and failed before writing JSON. Source/sample/board files were preserved; board hashes now refer to the original files.'
state['recoveredPreparedImages']=RECOVERY
save(R/'retained-semantic-anchor-preparation-v2.json',state)
print(json.dumps({'windows':len(state['windows']),'samples':sum(len(w['samples']) for w in state['windows']),'boards':sum(len(w['boards']) for w in state['windows'])}))
print(json.dumps({w['scene']:[(p['frame'],p['aim'],p['aimTemplateScore']) for p in w['points']] for w in state['windows'] if w['scene'] in ['01','03']}))
