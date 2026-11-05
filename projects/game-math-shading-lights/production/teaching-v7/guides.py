"""Surface-space guides, projected with the same WARP mesh, light, viewing direction and timeline."""
import functools,math,subprocess
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from common import BASE,WORK,sha,read,write
from samples import DEMOS
W,H=852,480
NCLR='#99e29f';LCLR='#ffd076';VCLR='#77d7ee';RCLR='#ff958b';HCLR='#d0aff4';PCLR='#faf8ee';BG='#101619'
STILLS={22,23,41,46,48,54,57,72}
def unit(a):
    v=np.asarray(a,dtype=float);return v/max(1e-12,np.linalg.norm(v))
view=unit([-.45,.28,.85])
def vec(s,u):
    theta=(.1+(1.95-.1)*u) if s in (20,21,30) else (-.9+1.8*u) if s==42 else .52
    return unit([math.sin(theta),.22,math.cos(theta)])
def triangle(s):
    rings,segs=(12,18) if s in (41,42) else (40,64)
    j=round(rings*.60);i=round(segs*.20)
    def pos(j,i):
        lat=-math.pi/2+math.pi*j/rings;lon=math.tau*i/segs+.14
        return np.array([math.cos(lat)*math.cos(lon),math.sin(lat),math.cos(lat)*math.sin(lon)])
    return np.array([pos(j,i),pos(j,i+1),pos(j+1,i)])
def project(s,p,side=0):
    split=s in (30,42);scale=W*(.216 if split else .235)
    center=np.array([W*((.268,.732)[side] if split else .5),H*.455])
    return center+scale*np.array([p[0],-p[1]])
def xy(p):return tuple(map(float,p))
@functools.lru_cache(None)
def face(size):return ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf',size)
def dot(d,p,r,color):
    x,y=p;d.ellipse((x-r,y-r,x+r,y+r),fill=color,outline=BG,width=1)
def stroke(d,a,b,fill,width=4,broken=False):
    delta=np.array(b)-a;length=np.linalg.norm(delta)
    if length<.5:return
    v=delta/length
    if not broken:
        d.line([xy(a),xy(b)],fill=BG,width=width+3);d.line([xy(a),xy(b)],fill=fill,width=width);return
    for k in range(0,int(length),14):
        d.line([xy(a+v*k),xy(a+v*min(k+8,length))],fill=fill,width=width)
def arrow(d,p,vec3,scale,col,dash=False):
    q=p+scale*np.array([vec3[0],-vec3[1]]);delta=q-p;length=np.linalg.norm(delta)
    if length<9:
        x,y=p;d.ellipse((x-8,y-8,x+8,y+8),outline=col,width=3)
        if vec3[2]>=0:dot(d,p,3,col)
        else:d.line((x-4,y-4,x+4,y+4),fill=col,width=2);d.line((x-4,y+4,x+4,y-4),fill=col,width=2)
    else:
        v=delta/length;normal=np.array([-v[1],v[0]]);h=min(15,length*.4)
        stroke(d,p,q-v*h*.68,col,7,dash);d.polygon([xy(q),xy(q-v*h+normal*h*.47),xy(q-v*h-normal*h*.47)],fill=col)
    return q
def label(d,p,word,color,offset,boxes,size=25):
    f=face(size);ww=d.textlength(word,font=f)+12;hh=size+9
    for dx,dy in [offset,(offset[0],offset[1]-27),(offset[0]+19,offset[1]+23),(-offset[0],-offset[1]),(32,-37),(-33,41)]:
        cx=max(ww/2+3,min(W-ww/2-3,p[0]+dx));cy=max(hh/2+4,min(H-45-hh/2,p[1]+dy))
        box=(cx-ww/2,cy-hh/2,cx+ww/2,cy+hh/2)
        if all(box[2]+2<o[0] or o[2]+2<box[0] or box[3]+2<o[1] or o[3]+2<box[1] for o in boxes):break
    boxes.append(box);d.rounded_rectangle(box,radius=4,fill=BG)
    d.text((cx,cy-1),word,font=f,fill=color,anchor='mm')
def bracket(d,p,q,col):
    delta=np.asarray(q)-p;v=unit(delta);perp=np.array([-v[1],v[0]])*6
    stroke(d,p,q,col,3)
    for e in [p,q]:d.line([xy(e-perp),xy(e+perp)],fill=col,width=3)
def texture_triangle(d,u,boxes):
    vertices=np.array([[.16,.69],[.82,.64],[.41,.12]])*np.array([W,H])
    weights=(1-u)*np.array([.64,.13,.23])+u*np.array([.11,.77,.12]);p=weights@vertices
    for i,(v,w) in enumerate(zip(vertices,weights)):
        others=[vertices[(i+1)%3],vertices[(i+2)%3]]
        colors=[(125,185,245),(255,203,110),(150,223,176)]
        # The subtriangle opposite a vertex has area fraction lambda_i.
        d.polygon([xy(p),xy(others[0]),xy(others[1])],fill=(*colors[i],42))
        stroke(d,p,v,'#ece7d2',2,True)
    for i,v in enumerate(vertices):
        dot(d,v,4,PCLR);label(d,v,['C₀','C₁','C₂'][i],PCLR,[(-5,19),(7,22),(3,-18)][i],boxes,21)
    dot(d,p,6,LCLR);label(d,p,'P',LCLR,(16,-19),boxes,22)
    label(d,(p+vertices[0]+vertices[2])/3,'λ₁',LCLR,(0,0),boxes,19)
def draw(s,u):
    layer=Image.new('RGBA',(W,H));d=ImageDraw.Draw(layer);boxes=[]
    if s==39:texture_triangle(d,u,boxes);return layer
    tri=triangle(s);probe=tri.mean(axis=0);n=unit(probe);light=vec(s,u)
    side=1 if s in (30,42) else 0;p=project(s,probe,side)
    r=2*np.dot(n,light)*n-light
    def rays(keys,scale=175):
        colors={'N':NCLR,'L':LCLR,'V':VCLR,'R':RCLR,'H':HCLR}
        dirs={'N':n,'L':light,'V':view,'R':r,'H':unit(view+light)}
        shifts={'N':(-14,-16),'L':(16,-12),'V':(-16,7),'R':(16,14),'H':(15,-14)}
        tips={key:arrow(d,p,dirs[key],scale,colors[key],key in ('V','H')) for key in keys}
        lanes=({'N':(610,28),'L':(786,66),'V':(458,123),'R':(792,204)} if side else
               {'N':(424,28),'L':(695,85),'V':(174,108),'R':(670,213)})
        if len(keys)>1:
            for key in keys:
                at=np.array(lanes[key]);delta=at-tips[key]
                if np.linalg.norm(delta)>24:stroke(d,tips[key]+unit(delta)*5,at-unit(delta)*16,colors[key],2,key=='V')
            for key in keys:label(d,np.array(lanes[key]),key,colors[key],(0,0),boxes,38)
        else:
            for key in keys:label(d,tips[key],key,colors[key],shifts[key],boxes,34)
        dot(d,p,7,PCLR);label(d,p,'P',PCLR,(-14,25),boxes,23)
    if s in (12,42):
        if s==42:
            left=[project(s,vertex,0) for vertex in tri];poly=[xy(x) for x in left]
            d.line(poly+[poly[0]],fill=MUSTARD,width=3)
            for v in left:dot(d,v,4,LCLR)
            pleft=project(s,probe,0);dot(d,pleft,5,PCLR);label(d,pleft,'P',PCLR,(-13,21),boxes,19)
        rays(('N','L','V','R'),208 if s==12 else 166)
    elif s in (20,21,30,23,46,72):
        if s==30:
            dot(d,project(s,probe,0),5,PCLR)
        rays(('N','L'))
        if s in (20,21,23,72):
            # Project the true direction arc into the observer view; theta is the 3D angle, not its apparent 2D size.
            pts=[p+57*np.array([v[0],-v[1]]) for f in np.linspace(0,1,25) for v in [unit(n*(1-f)+light*f)]]
            d.line([xy(x) for x in pts],fill='#f5efc7',width=3)
            label(d,pts[len(pts)//2],'θ',PCLR,(3,16),boxes,18)
        if s in (23,72):
            # L_i refers to radiance arriving from the sampled direction wi, not the unit vector.
            q=p+180*np.array([light[0],-light[1]])
            label(d,q,'ω · 입사 방향',LCLR,(37,-27),boxes,18)
    elif s in (48,57,58):
        delta=(.8+1.8*u if s==58 else 2.1)*112*np.array([light[0],-light[1]]);q=p+delta
        bracket(d,p,q,LCLR);dot(d,q,10,LCLR);dot(d,p,6,PCLR)
        label(d,q,'Q · 광원',LCLR,(45,-12),boxes,21);label(d,p,'P',PCLR,(-17,16),boxes,20)
        label(d,(p+q)/2,'d',PCLR,(2,19),boxes,22)
        if s==48:rays(('L',),84)
    elif s==41:
        projected=[project(s,v) for v in tri];d.line([*map(xy,projected),xy(projected[0])],fill=LCLR,width=3)
        for v,at in zip(tri,projected):arrow(d,at,unit(v),76,'#7baf83')
        rays(('N',),165)
        label(d,p,'픽셀 법선',NCLR,(72,38),boxes,18)
    elif s in (54,22):
        tangent=unit(np.cross(n,[0,1,0]));bitangent=np.cross(n,tangent)
        patch=[project(s,unit(n+.12*(tangent*math.cos(t)+bitangent*math.sin(t)))) for t in np.linspace(0,math.tau,48)]
        d.line([xy(x) for x in patch],fill=NCLR,width=4)
        start=p+165*np.array([light[0],-light[1]]);arrow(d,start,-light,165,LCLR)
        label(d,start,'입사 Φ',LCLR,(15,-22),boxes,20)
        label(d,p,'dA' if s==54 else 'ρ · 반사율',NCLR,(0,30),boxes,21)
        if s==22:
            for delta in [(-65,-76),(0,-91),(71,-66)]:
                arrow(d,p,unit([delta[0],-delta[1],0]),math.hypot(*delta),RCLR)
            label(d,p,'반사 반구',RCLR,(-72,-103),boxes,18)
    elif s==6:
        dot(d,p,6,PCLR);end=p+np.array([-92.,-68.]);stroke(d,p,end,MINT,3)
        label(d,end,'C · 표면색',MINT,(-30,-14),boxes,22)
        ox,oy=55,350
        for i,(value,col) in enumerate([(.85,'#f89a8e'),(.08+.92*u,'#9cdeaa'),(.85,'#89bfe9')]):
            d.rectangle((ox+i*92,oy,ox+i*92+56,oy+8),fill='#293432')
            d.rectangle((ox+i*92,oy,ox+i*92+56*value,oy+8),fill=col)
        label(d,np.array([170,oy]),'광원 RGB',PCLR,(0,26),boxes,18)
    return layer
MUSTARD='#ffc66d';MINT='#83dcca'
def static(s):
    folder=WORK/'symbol-stills';folder.mkdir(exist_ok=True);path=folder/f'{s:03}.png';shader=BASE/'surface.hlsl'
    sig=sha(shader)+sha(BASE/'guides.py')+sha(WORK/'surface.exe');stamp=path.with_suffix('.json')
    if path.exists() and stamp.exists() and read(stamp).get('source')==sig:return path
    rgba=subprocess.check_output([str(WORK/'surface.exe'),str(shader),str(s),'1','0','1'],stderr=subprocess.PIPE)
    base=Image.frombytes('RGBA',(W,H),rgba,'raw','BGRA')
    base=Image.alpha_composite(base,draw(s,0));base.save(path)
    write(stamp,dict(source=sig,scene=s));return path
def animate(s):
    raw=WORK/'demos'/f'{s:03}.mp4';data=read(raw.with_suffix('.json'))
    dst=raw.with_name(f'{s:03}-guided.mp4');receipt=dst.with_suffix('.json')
    stamp=data['stamp']+[sha(BASE/'guides.py')]
    if receipt.exists() and read(receipt).get('stamp')==stamp and dst.exists():return
    n=data['frames'];lo,hi=data['linearRampFrames']
    tmp=dst.with_suffix('.pending.mp4');cmd=['ffmpeg','-nostdin','-y','-v','error','-threads','2','-i',str(raw),'-f','rawvideo','-pix_fmt','rgba','-s','852x480','-r','60','-i','pipe:0','-filter_complex_threads','2','-filter_complex','[0:v][1:v]overlay=shortest=1','-an','-frames:v',str(n),'-c:v','libx264','-threads','2','-preset','veryfast','-crf','13','-bf','0','-pix_fmt','yuv420p',str(tmp)]
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE,creationflags=subprocess.CREATE_NO_WINDOW);prev=None;pixels=None
    try:
        for frame in range(n):
            u=max(0,min(1,(frame-lo)/(hi-lo)))
            if u!=prev:pixels=draw(s,u).tobytes();prev=u
            p.stdin.write(pixels)
    finally:p.stdin.close()
    if p.wait()!=0:raise RuntimeError(s)
    tmp.replace(dst);write(receipt,dict(stamp=stamp,frames=n,linearRampFrames=[lo,hi],sourceView='orthographic observer, independent V=(-.45,.28,.85) normalized',probeTriangle=triangle(s).tolist() if s!=39 else None))
if __name__=='__main__':
    from samples import render
    for s in [42,12,20,21,30,39,58,6]:
        render(s);animate(s);print('Attached',s,flush=True)
    for s in sorted(STILLS):static(s)
