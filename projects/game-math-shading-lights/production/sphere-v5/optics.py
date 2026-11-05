"""Observer view of one material sphere. The drawn camera is the shading camera, not the observer.
Per-pixel GGX/Schlick/Smith studio preview; teaching cases use named Phong/Blinn laws separately."""
import math,io,subprocess,functools
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from native import P,W,read,HERO
BG='#080b0e';WHITE='#eef0ec';MUT='#aeb8b7';GOLD='#ffcf70';GREEN='#9ce2a4';CYAN='#76daec';RED='#ff9989';VIO='#d1adf2'
CX,CY,rad=685,692,222; tilt=math.radians(26);pt=np.array([CX,CY-rad*math.cos(tilt)])
norm=lambda a: a/max(float(np.linalg.norm(a)),1e-9)
def vec(deg):return np.array([math.sin(math.radians(deg)),math.cos(math.radians(deg)),0.])
def project(v,k):return pt+k*np.array([v[0],-v[1]*math.cos(tilt)+v[2]*math.sin(tilt)])
def ease(t,a,b):
 u=max(0,min(1,(t-a)/(b-a)));return u*u*(3-2*u)
def lerp(x,y,u):return x+(y-x)*u
@functools.lru_cache(None)
def font(sz,b=False):return ImageFont.truetype('C:/Windows/Fonts/'+('malgunbd.ttf' if b else 'malgun.ttf'),sz)
def text(d,xy,t,sz=43,c=WHITE,b=False,anchor='lt'):
 import re
 f=font(sz,b);mf=ImageFont.truetype('C:/Windows/Fonts/segoeui'+('b' if b else '')+'.ttf',sz)
 if not re.search('[−ⁿ]',t):d.text(tuple(xy),t,font=f,fill=c,anchor=anchor,stroke_width=1,stroke_fill=BG);return
 runs=[(p,mf if re.fullmatch('[−ⁿ]+',p) else f) for p in re.split('([−ⁿ]+)',t) if p]
 x,y=xy;width=sum(d.textlength(p,font=ft) for p,ft in runs);x-=width if anchor[0]=='r' else width/2 if anchor[0]=='m' else 0
 for p,ft in runs:d.text((x,y+sz*.91),p,font=ft,fill=c,anchor='ls');x+=d.textlength(p,font=ft)
def label(d,xy,t,c):
 box=d.textbbox(tuple(xy),t,font=font(41,True),anchor='mm');d.rounded_rectangle((box[0]-6,box[1]-4,box[2]+6,box[3]+5),8,fill=BG);text(d,xy,t,41,c,True,'mm')
def xy(p):return tuple(float(v) for v in p)
def dot(d,p,r,c):x,y=p;d.ellipse((x-r,y-r,x+r,y+r),fill=c)
def arrow(d,a,b,u,c,w=9,dash=False):
 if u<=0:return
 a=np.array(a);b=np.array(b);v=b-a;tip=a+u*v;unit=norm(v);tang=np.array([-unit[1],unit[0]]);ht=min(23,np.linalg.norm(tip-a)*.45)
 if dash:
  for k in range(0,max(0,int(np.linalg.norm(tip-a)-ht)),22):d.line([xy(a+unit*k),xy(a+unit*min(k+12,np.linalg.norm(tip-a)-ht))],fill=c,width=w)
 else:
  d.line([xy(a),xy(tip-unit*ht*.78)],fill=BG,width=w+4);d.line([xy(a),xy(tip-unit*ht*.78)],fill=c,width=w)
 d.polygon([xy(tip),xy(tip-unit*ht+tang*ht*.47),xy(tip-unit*ht-tang*ht*.47)],fill=c)
def sun(d,p):
 x,y=p
 for i in range(12):
  a=i*math.pi/6;v=np.array([math.cos(a),math.sin(a)]);d.line([xy(p+v*29),xy(p+v*44)],fill=GOLD,width=6)
 dot(d,p,21,GOLD);dot(d,p-np.array([5,6]),9,'#ffe5a1')
def camera(d,p,target):
 axis=norm(target-p);up=np.array([axis[1],-axis[0]])
 def poly(ps,fill,edge):pts=[xy(p+axis*a+up*b) for a,b in ps];d.polygon(pts,fill);d.line(pts+[pts[0]],fill=edge,width=4)
 poly([(-66,-25),(-23,-25),(-23,22),(-32,22),(-39,31),(-56,31),(-57,22),(-66,22)],'#22343c',CYAN)
 poly([(-23,-16),(-10,-16),(0,-20),(0,20),(-10,16),(-23,16)],'#37535e',CYAN);d.line([xy(p-up*13),xy(p+up*13)],fill='#d7f5ed',width=5)
@functools.lru_cache(4)
def grid(r):
 y,x=np.mgrid[-r:r+1,-r:r+1].astype('float32')/r;rr=x*x+y*y;z=np.sqrt(np.maximum(0,1-rr));ny=-y*np.cos(tilt)+z*np.sin(tilt);nz=y*np.sin(tilt)+z*np.cos(tilt)
 return np.stack((x,ny,nz),-1),np.clip((1-np.sqrt(rr))*r+.55,0,1)[...,None]
@functools.lru_cache(26)
def sphere(r,mode,ldeg,vdeg,metal,rough,lit):
 n,mask=grid(r);l=vec(ldeg).astype('f');v=vec(vdeg).astype('f');obs=np.array([0,np.sin(tilt),np.cos(tilt)],dtype='f');rgb=np.array([.24,.40,.43],dtype='f')
 if mode in ('pbr','brdf'):
  # Softboxes are finite angular patches approximated by 3x3 incoming directions.
  v=obs if mode=='pbr' else v;nv=np.clip(n@v,.001,1);alpha=max(.055,rough)**2;f0=.04*(1-metal)+rgb*metal
  col=.024*rgb*(.5+.5*n[:,:,1,None])+.003
  lights=[(norm(l+np.array([0,0,.65])),(1,.9,.72),.18,3.4),(norm(np.array([-1.,.45,.45])),(.6,.83,1),.21,1.4),(norm(np.array([.5,.7,-.75])),(.8,1,1),.08,2.8)] if mode=='pbr' else [(l,(1,.95,.85),0.,3.2)]
  for direction,tint,size,power in lights:
   a=norm(np.cross(direction,[0,1,0]));b=np.cross(direction,a)
   for i in [-1,0,1]:
    for j in [-1,0,1]:
     wi=norm(direction+a*i*size+b*j*size*.32).astype('f');h=norm(wi+v);nl=np.maximum(0,n@wi);nh=np.maximum(0,n@h)
     dist=alpha**2/(math.pi*(nh**2*(alpha**2-1)+1)**2)
     k=(rough+1)**2/8;geo=nl/(nl*(1-k)+k)*nv/(nv*(1-k)+k)
     fr=f0+(1-f0)*(1-max(0,float(h@v)))**5
     col=col+((1-fr)*(1-metal)*rgb/math.pi+(dist*geo/np.maximum(4*nl*nv,.0001))[...,None]*fr)*nl[...,None]*np.array(tint)*power/9
 else:
  nl=n@l; nv=n@v;rr=2*nl*nv-float(l@v);h=norm(l+v);sp=np.maximum(0,n@h)**36 if mode=='blinn' else np.maximum(0,rr)**20
  direct=(np.maximum(0,nl)[...,None]*rgb*.82+sp[...,None]*np.array([1,.92,.78])*(0 if mode=='lambert' else .72))*(nl>0)[...,None]
  col=rgb*.065+direct*lit
 # OETF and gentle highlight rolloff. The dot product readout below uses un-tonemapped unit vectors.
 col=np.clip(col,0,None);col=col/(1+.5*col);col=np.where(col<.0031308,col*12.92,1.055*col**(1/2.4)-.055)
 back=np.array([8,11,14])/255;res=np.clip((col*mask+back*(1-mask))*255,0,255).astype('uint8');return Image.fromarray(res)
TIT={1:('재질에 빛을 비추면','재질 미리보기'),2:('빛이 들어오고 나가는 방향','양방향 반사 분포 함수  ·  BRDF'),3:('빛 한 줄기를 따라가면','직접광  ·  Direct lighting'),4:('빛을 보내는 것과 보이는 것','광원  ·  Light source'),7:('카메라만 옮겨 볼까요?','정반사  ·  Specular reflection'),8:('표면의 한 점에서 방향 정하기','단위 벡터  ·  Unit vectors'),9:('법선을 기준으로 튕겨 나가는 빛','반사 벡터  ·  Reflection vector'),10:('반사 방향을 숫자로 확인하기','반사 벡터  ·  Worked example'),11:('반사 방향에 카메라가 가까워지면','퐁 반사 모델  ·  Phong reflection'),16:('두 방향의 가운데는 어디일까?','하프웨이 벡터  ·  Halfway vector'),17:('가운데 방향과 법선을 비교하면','블린–퐁  ·  Blinn–Phong'),51:('멀리 있는 해에서 오는 평행광','방향성 광원  ·  Directional light')}
def info(d,h,lines,col=WHITE):
 text(d,(1190,295),h,36,GOLD,True)
 for i,line in enumerate(lines):text(d,(1190,369+i*72),line,48,col if i==0 else WHITE, i==0)
def paint(s,t):
 if s in (20,55):return distance_or_cosine(s,t)
 im=Image.new('RGB',(1920,1080),BG);d=ImageDraw.Draw(im)
 text(d,(92,53),TIT[s][1],31,MUT);text(d,(90,108),TIT[s][0],58,GOLD,True)
 text(d,(1825,62),'재질 구  /  자체 구현',31,MUT,False,'rt')
 Ldeg=36.8698976458; vd=-67.;inc=0; nr=lr=rr=vr=hr=0.; mode='phong';sc=1.;rough=.31;met=.08;plot='';msg=('한 점의 빛',[]);showSun=True;showCamera=True;sunShift=0
 if s==1:
  mode='pbr';met=ease(t,15.98,20.13);rough=.33;showCamera=False;showSun=False
  msg=('스튜디오 조명 · GGX',['재질만 바꾸기','기본색과 조명은 고정',f'금속성   {met:.2f}',f'거칠기   {rough:.2f}'])
 elif s==2:
  mode='brdf';rough=.44;inc=ease(t,5.2,6.3);vr=ease(t,7.5,8.6);msg=('들어오는 빛과 나가는 빛',['입사 방향 → 표면','표면 → 관찰 방향','각 방향 쌍마다','반사량이 달라져요.'])
 elif s==3:
  vd=-Ldeg;inc=ease(t,7.65,8.9);rr=ease(t,10.95,12.85);vr=ease(t,12.9,14.25);nr=ease(t,9,10);msg=('직접광의 경로',['①  해 → 표면']+(['②  법선을 기준으로 반사'] if t>=9 else [])+(['③  반사광 → 카메라'] if t>=11 else []))
 elif s==4:
  inc=ease(t,4.6,6);showSun=not(3.3<t<10.8);showCamera=False;msg=('광원과 메시',['아이콘을 숨겨도','조명 계산은 계속돼요.','광원의 위치와 방향이','입력값입니다.'])
 elif s==7:
  inc=nr=rr=vr=1;vd=lerp(-70,-Ldeg,ease(t,18.8,21.5))+lerp(0,25,ease(t,22,25));msg=('구와 해는 그대로',['카메라만 이동','R과 V가 가까울수록','이 점의 반짝임이','더 강해집니다.'])
 elif s==8:
  nr=ease(t,.05,1.4);vr=ease(t,3.4,4.7);lr=ease(t,5.95,7.25)
  if 12.75<t<17.4:lr=0;inc=ease(t,12.75,14.1)
  elif t>=17.4:lr=ease(t,17.4,18.65)
  msg=('세 벡터의 출발점은 표면',['N   표면에 수직','V   카메라 쪽','L   광원 쪽'] if t>6 else (['N   표면에 수직','V   카메라 쪽'] if t>3.4 else ['N   표면에 수직']))
  if t>12.75:msg=('서로 반대인 두 방향',['−L   해 → 표면','L     표면 → 해'])
 elif s in (9,10):
  inc=ease(t,0,.85);nr=ease(t,.7,1.7);lr=ease(t,1.75,2.7);rr=ease(t,12.55,14.05);plot='construct';showCamera=False
  if s==9:msg=('법선 위에 쌓아 보기',['p = (N·L)N']+(['2p'] if t>9.8 else [])+(['R = 2p − L'] if t>12.55 else []))
  else:msg=('좌표로 확인하기',['N = (0, 1, 0)','L = (0.6, 0.8, 0)']+(['N·L = 0.8'] if t>6.7 else [])+(['R = (−0.6, 0.8, 0)'] if t>12.55 else [])+(['reflect(−L, N)'] if t>20.1 else []))
 elif s==11:
  inc=ease(t,0,.7);nr=ease(t,.6,1.3);rr=ease(t,1.2,2.2);vr=ease(t,2,3.1);vd=lerp(-70,-Ldeg,ease(t,3.55,6.7))+lerp(0,-37,ease(t,8.2,10.8));msg=('퐁 모델의 정반사',['R · V = '+f'{max(0,float(vec(-Ldeg)@vec(vd))):.2f}','완전히 겹치면 1','정반사 ∝ max(0, R·V)ⁿ'])
 elif s in (16,17):
  mode='blinn';lr=ease(t,3.85 if s==16 else .1,4.8 if s==16 else 1);vr=ease(t,4.65 if s==16 else .9,5.65 if s==16 else 1.85)
  hr=ease(t,6.25 if s==16 else 1.85,8.7 if s==16 else 2.8);nr=ease(t,12.8 if s==16 else 2.95,14 if s==16 else 3.85)
  if s==16:vd=lerp(-76,-Ldeg,ease(t,12.8,15.1))+lerp(0,-30,ease(t,16.8,19.1))
  msg=('두 단위 벡터를 더해서',['H = normalize(L + V)','N과 H가 가까우면','반짝임이 강해집니다.'] if s==16 else ['max(0, N·H)ⁿ','L + V = 0 이면','정규화할 수 없어요.'])
 elif s==51:
  showCamera=False;sunShift=125*ease(t,12.4,14.35);Ldeg-=28*ease(t,14.85,16.85);inc=ease(t,.2,2);msg=('방향성 광원',['위치 이동 → 그대로','회전 → 명암 변화','같은 방향의 평행광']);plot='parallel'
 if mode=='pbr':sd=round(met*32)/32
 else:sd=0
 # Scene 001 shows base color first, then actual shaded material at locked framing.
 if s==3:sc=.19+.81*ease(t,8.85,9.25)
 ball=sphere(rad,mode,round(Ldeg,1),round(vd,1),sd,rough,round(sc,2))
 if s==1 and t<3.9:
  flat=Image.new('RGB',ball.size,BG);ImageDraw.Draw(flat).ellipse((0,0,2*rad,2*rad),fill='#88a8af');ball=Image.blend(flat,ball,ease(t,1.65,3.85))
 im.paste(ball,(CX-rad,CY-rad));d=ImageDraw.Draw(im)
 info(d,*msg)
 if s==1:return im
 ln=vec(Ldeg);rn=vec(-Ldeg);vn=vec(vd);hn=norm(ln+vn)
 source=project(ln,319 if s==51 else 348);cam=project(vn,338 if s==3 else 401);ne=project(vec(0),275);le=project(ln,239);re=cam if s==3 else project(rn,275);ve=project(vn,320 if s==3 else 383);he=project(hn,209)
 if s in (7,11,16):
  # Keep the orbit at a constant diagram radius, with clearance above the lens even near the normal.
  cam=project(vn,265);ve=project(vn,249);re=project(rn,204)
 if s==8:
  ne=project(vec(0),250);le=project(ln,250);ve=project(vn,250)
  if vr>.95:arrow(d,ve,cam,.98,'#477780',3,True)
 if showSun:sun(d,source+np.array([sunShift,0]));text(d,source+np.array([sunShift+56,-7]),'광원',36,GOLD,True)
 if showCamera:
  camera(d,cam,pt)
  if s in (7,11,16):text(d,cam+[-80,-12],'카메라',33,CYAN,True,'rt')
  else:text(d,cam+[-73,42],'카메라',33,CYAN,True,'mt')
 if plot=='parallel':
  # Parallel incident rays intersect the actual sphere silhouette/surface in this cross-section.
  for a in (-21,17):
   ang=math.radians(a);hit=pt+np.array([rad*math.sin(ang),rad*(1-math.cos(ang))*math.cos(tilt)]);offset=project(ln,369)-pt;arrow(d,hit+offset,hit,inc,GOLD,6)
 if inc:
  begin=source-norm(source-pt)*49;arrow(d,begin,pt,inc,GOLD,8)
  if inc<1 or (s==8 and 12.75<t<17.4):dot(d,begin+(pt-begin)*inc,8,'#fff7da')
 if nr:arrow(d,pt,ne,nr,GREEN);
 if lr:arrow(d,pt,le,lr,GOLD,8,dash=inc>0)
 if rr:
  arrow(d,pt,re,rr,RED,11)
  if s==3 and rr<1:dot(d,pt+(re-pt)*rr,9,'#fff5d9')
 if vr:arrow(d,pt,ve,vr,CYAN,6,dash=rr>0)
 if hr:arrow(d,pt,he,hr,VIO,7,dash=True)
 if s==3 and t>15:
  for ang,on in [(-27,15.1),(77,16.5)]:
   add=project(vec(ang),268);dot(d,add,9,GOLD);arrow(d,add,pt,ease(t,on,on+1),GOLD,4,True)
 if plot=='construct':
  k=155;p1=project(vec(0),.8*k);p2=project(vec(0),1.6*k);l1=project(ln,k);r1=project(rn,k)
  arrow(d,l1,p1,ease(t,2.7,4.5),'#abc0be',4,True)
  arrow(d,pt,p1,ease(t,5.1,7.5),VIO,6)
  arrow(d,p1,p2,ease(t,9.1,10.7),VIO,6)
  arrow(d,p2,r1,ease(t,10.8,12.55),VIO,6,True)
 if nr>.92:label(d,ne+[-12,-27],'N',GREEN)
 if lr>.92:label(d,le+[39,13],'L',GOLD)
 if rr>.92:label(d,re+([33,-24] if s==3 else [23,-22] if s in (7,11) else [-18,-27]),'R',RED)
 if vr>.92:label(d,ve+([-23,36] if s in (7,11,16) else [0,35]),'V',CYAN)
 if hr>.92:label(d,he+[43,9],'H',VIO)
 dot(d,pt,10,BG);dot(d,pt,6,'#ffffff')
 if s in (3,8,9,10,11):text(d,(CX+36,pt[1]+22),'표면점 P',30,WHITE,True)
 return im
def distance_or_cosine(s,t):
 im=Image.new('RGB',(1920,1080),BG);d=ImageDraw.Draw(im)
 text(d,(92,53),'램버트 난반사 · Lambertian diffuse' if s==20 else '복사휘도 · Radiance',32,MUT)
 text(d,(90,108),'한 표면에서 빛을 얼마나 받을까?' if s==20 else '카메라가 멀어지면 무엇이 달라질까?',55,GOLD,True)
 if s==55:
  u=ease(t,4.85,7.22);r=round(215-80*u);p0=np.array([391.,384.]);eye=p0+(1+.65*u)*np.array([384.,-62.])
  im.paste(sphere(55,'lambert',29.,-65.,0,.4,1),(290,346));d=ImageDraw.Draw(im)
  text(d,(287,280),'옆에서 본 배치',31,MUT)
  camera(d,eye,p0);text(d,eye+[-60,-83],'카메라',37,CYAN,True)
  arrow(d,p0,eye,.98,CYAN,6,True);dot(d,p0,8,WHITE);text(d,p0+[-80,26],'표면점',35,WHITE)
  ball=sphere(r,'lambert',29.,-65.,0,.4,1);im.paste(ball,(652-r,690-r));d=ImageDraw.Draw(im);text(d,(282,564),'카메라 화면',33,MUT)
  info(d,'카메라만 뒤로 이동',['화면에서는 작아짐','조명과 재질은 고정','같은 표면점의','복사휘도는 그대로']);return im
 angle=60*ease(t,4.9,5.95)+30*ease(t,7.05,7.95)+28*ease(t,16.6,17.9);a=math.radians(angle)
 r=201;cy=627;im.paste(sphere(r,'lambert',0.,-65.,0,.4,1),(CX-r,cy-r));d=ImageDraw.Draw(im)
 n=np.array([.78*math.sin(a),-math.cos(a)*math.cos(tilt)+math.sqrt(1-.78**2)*math.sin(a)*math.sin(tilt)]);l=np.array([0.,-math.cos(tilt)])
 p0=np.array([CX,cy])+r*n;src=np.array([CX,230.]);sun(d,src);text(d,src+[58,-10],'평행광',32,GOLD)
 arrow(d,np.array([p0[0],292.]),p0,ease(t,0,.9),GOLD,6,True)
 arrow(d,p0,p0+192*n,ease(t,.85,1.8),GREEN,9);arrow(d,p0,p0+152*l,ease(t,1.9,2.7),GOLD,5,True)
 label(d,p0+192*n+[28,0],'N',GREEN);label(d,p0+152*l+[-32,0],'L',GOLD);dot(d,p0,8,WHITE)
 value=max(0,math.cos(a));info(d,'구의 표면을 따라 이동',[f'사이각   {angle:.0f}°',f'max(0, N·L) = {value:.2f}','법선이 빛에서','멀어질수록 어두워요.']);return im
if __name__=='__main__':
 for s,t in [(1,19),(3,15),(8,10),(9,14),(10,23),(11,6.8),(16,16)]:
  f=W/f'optical-{s:02}.jpg';paint(s,t).save(f,quality=94)
