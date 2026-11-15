"""Gameplay-first studies. All rig, timing and collision graphics are editorial models."""
from common import *
from studies import SOURCES,catalog,KOREAN,FOCUS
from functools import lru_cache
import math
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageEnhance,ImageOps

BG='#080c0a';WHITE='#f3f5ef';YELLOW='#f2d787';TEAL='#81cfc5';RED='#f18b81';GREEN='#a4d987';MUTED='#abb9af';LINE='#425247'

@lru_cache(None)
def font(n):return ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf',n)
def text(d,xy,s,size=37,color=WHITE,width=1780,anchor='lt'):
 while d.textlength(s,font=font(size))>width and size>26:size-=1
 d.text(xy,s,font=font(size),fill=color,anchor=anchor)
def arrow(d,a,b,color=YELLOW,width=7):
 d.line([a,b],fill=color,width=width);t=math.atan2(b[1]-a[1],b[0]-a[0]);l=19
 d.polygon([b,(b[0]-l*math.cos(t-.5),b[1]-l*math.sin(t-.5)),(b[0]-l*math.cos(t+.5),b[1]-l*math.sin(t+.5))],fill=color)
def chain(d,ps,color=TEAL):
 d.line(ps,fill=color,width=10,joint='curve')
 for x,y in ps:d.ellipse((x-11,y-11,x+11,y+11),fill=BG,outline=color,width=5)
def fit(im,pic,box):
 x,y,w,h=box;r=min(w/pic.width,h/pic.height);ww,hh=round(pic.width*r),round(pic.height*r)
 at=(x+(w-ww)//2,y+(h-hh)//2)
 source=pic.info.get('yamyamFitSource');expected=(1920,1080) if source and source[2] is None else (source[2][2]-source[2][0],source[2][3]-source[2][1]) if source else None
 resized=scaled_picture(*source,ww,hh) if source and pic.size==expected else pic.resize((ww,hh),Image.Resampling.LANCZOS)
 im.paste(resized,at)
 return (*at,ww,hh)

def prepare_banks():
 cat=catalog();rows=[]
 used={s['bank'] for e in read(HERE/'plan.json')['episodes'] for s in e.get('studyDefinitions',{}).values()}|{'maelle','bottle-body','dee-left'}
 for bank,(key,a,b,phases,crop) in SOURCES.items():
  if bank not in used:continue
  p=Path(cat[key]['file']);folder=WORK/'banks-v2'/bank;folder.mkdir(parents=True,exist_ok=True)
  meta=folder/'bank.json';sig=dict(sourceSha256=sha(p),inSeconds=a,outSeconds=b,fps=60,crop=crop,canvas=[1920,1080])
  if meta.exists() and read(meta).get('signature')==sig and len(list(folder.glob('*.jpg')))>=round((b-a)*60)-1:
   rows.append(read(meta));continue
  info=__import__('json').loads(run(['ffprobe','-v','error','-select_streams','v:0','-show_streams','-of','json',p],True))['streams'][0]
  assert info['width']>=1920 and info['height']>=1080,(bank,'not genuine FHD')
  n=round((b-a)*60)
  assert folder.resolve().is_relative_to((WORK/'banks-v2').resolve())
  for old in folder.glob('*.jpg'):old.unlink() # only our disposable bank frames, never sources/deliveries
  ff('-threads',2,'-ss',a,'-i',p,'-vf','fps=60,scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2',
     '-frames:v',n,'-q:v',2,'-start_number',0,folder/'%05d.jpg')
  assert len(list(folder.glob('*.jpg')))==n,(bank,n)
  r=dict(bank=bank,signature=sig,frames=n,width=info['width'],height=info['height'],nativeFps=info['avg_frame_rate'],
    game=cat[key].get('game',key),url=cat[key].get('sourceUrl',cat[key].get('url')),opticalFlow=False,phaseFrames=[round(x*60) for x in phases])
  save(meta,r);rows.append(r);print('Bank',bank,n,'frames',flush=True)
 save(WORK/'banks.json',dict(banks=rows,sourceFhdChecked=True))

@lru_cache(24)
def picture(bank,n):
 a,b=SOURCES[bank][1:3];n=min(round((b-a)*60)-1,max(0,round(n)))
 p=WORK/'banks-v2'/bank/f'{n:05d}.jpg'
 if not p.exists():
  p.parent.mkdir(parents=True,exist_ok=True);cat=catalog();key=SOURCES[bank][0]
  ff('-threads',1,'-ss',SOURCES[bank][1]+n/60,'-i',cat[key]['file'],'-frames:v',1,'-q:v',2,p)
 with Image.open(p) as im:pic=im.convert('RGB')
 if pic.size!=(1920,1080):pic=ImageOps.pad(pic,(1920,1080),color=BG,method=Image.Resampling.LANCZOS)
 if bank=='lune':pic=ImageEnhance.Brightness(pic).enhance(1.65)
 pic.info['yamyamFitSource']=(bank,n,None)
 return pic
def detail(bank,n):
 p=picture(bank,n);crop=SOURCES[bank][4]
 if not crop:return p
 out=p.crop(crop);out.info['yamyamFitSource']=(bank,p.info['yamyamFitSource'][1],crop);return out

@lru_cache(384)
def scaled_picture(bank,n,crop,width,height):
 # Bounded CPU-memory cache: reuse the exact same LANCZOS pixels for repeated
 # observation passes. No frame interpolation, GPU allocation or quality change.
 p=picture(bank,n)
 if crop:p=p.crop(crop)
 return p.resize((width,height),Image.Resampling.LANCZOS)

def phase_frames(bank):return [round(x*60) for x in SOURCES[bank][3]]
@lru_cache(None)
def game_label(bank):return catalog()[SOURCES[bank][0]].get('game',SOURCES[bank][0]).split(' (')[0]


@lru_cache(90)
def backdrop(ep,key,title,bank,grammar):
 im=Image.new('RGB',(1920,1080),BG);d=ImageDraw.Draw(im)
 text(d,(55,27),title.split('|')[0].strip(),51,YELLOW,width=1500)
 text(d,(55,103),FOCUS.get((ep,key),KOREAN[ep][0]),33,TEAL,width=1510)
 text(d,(1860,49),'실제 게임 · 관찰 / 원리 도식',29,MUTED,width=580,anchor='rt')
 d.line((55,151,1865,151),fill=LINE,width=2)
 text(d,(1860,106),game_label(bank),26,MUTED,width=650,anchor='rt')
 return im

def timeline(d,x,y,w,u,labels):
 colors=[TEAL,YELLOW,RED,GREEN]
 for i,label in enumerate(labels):
  xx=x+w*i/4;d.line((xx,y,xx+w/4-10,y),fill=colors[i],width=11)
  text(d,(xx,y+20),label,31,colors[i],width=w/4-12)
 xx=x+w*min(1,max(0,u));d.polygon([(xx,y-19),(xx-12,y-37),(xx+12,y-37)],fill=WHITE)

def phase_grid(im,bank,labels):
 d=ImageDraw.Draw(im)
 for i,f in enumerate(phase_frames(bank)):
  x=55+i*465;text(d,(x,185),labels[i],36,(TEAL,YELLOW,RED,GREEN)[i],430)
  fit(im,detail(bank,f),(x,247,425,500));d.line((x,785,x+425,785),fill=(TEAL,YELLOW,RED,GREEN)[i],width=7)
 text(d,(58,816),'같은 실제 동작의 순간들을 나란히 놓고 비교합니다',30,MUTED)

def observation(im,bank,n,grammar,ep,key,labels,u):
 d=ImageDraw.Draw(im)
 if grammar=='size':
  text(d,(65,180),'크게 보기',38,TEAL);text(d,(1090,180),'같은 시각 · 작게 보기',38,RED,770)
  fit(im,detail(bank,n),(70,238,925,568))
  small=detail(bank,n);r=min(300/small.width,220/small.height);small=small.resize((round(small.width*r),round(small.height*r)),Image.Resampling.LANCZOS)
  d.rectangle((1110,250,1830,800),outline=LINE,width=2)
  # A deliberately small image remains small; fit() above must not enlarge it.
  im.paste(small,(1470-small.width//2,530-small.height//2))
  text(d,(1095,819),'크기를 바꾼 편집 비교 · 원본 동작은 동일',29,MUTED,780)
  return
 if grammar=='face':
  text(d,(65,181),'표정 전체',38,TEAL);text(d,(1030,181),'같은 순간 · 얼굴 확대',38,RED,820)
  fit(im,picture(bank,n),(65,250,855,500));box=fit(im,detail(bank,n),(1030,240,820,540))
  # The crop is the observed face; no generated expression or facial deformation.
  x,y,w,h=box;d.rectangle((x,y,x+w,y+h),outline=RED,width=6)
  text(d,(1030,812),'동일한 시각의 확대 · 0.5배 관찰',29,MUTED,820)
  return
 if grammar=='direction':
  text(d,(65,184),'실제 오른쪽 보기',37,TEAL);text(d,(1030,184),'실제 왼쪽 보기',37,RED)
  fit(im,detail('dee-right',n%42),(65,245,850,535));fit(im,detail('dee-left',n%42),(1030,245,850,535))
  arrow(d,(150,812),(650,812),TEAL);arrow(d,(1760,812),(1260,812),RED)
  return
 if grammar=='pose':
  text(d,(65,184),'처음 자세 · 정지',37,TEAL);text(d,(1030,184),'동작 분석 · 0.5배',37,RED,820)
  first=phase_frames(bank)[0];last=n
  fit(im,detail(bank,first),(65,245,850,540));fit(im,detail(bank,last),(1030,245,850,540))
  # Keep lines away from the character. They identify a region, not a guessed rig.
  d.line((65,813,915,813),fill=TEAL,width=7);d.line((1030,813,1880,813),fill=RED,width=7)
  return
 # One large moving detail plus complete original context, never a reconstructed rig.
 fit(im,detail(bank,n),(55,195,1280,635));fit(im,picture(bank,n),(1360,245,500,282))
 text(d,(1360,197),'원래 화면 · 전체 맥락',30,MUTED,500)
 text(d,(1360,562),'실제 장면에서 보이는',30,TEAL,500);text(d,(1360,606),'시작 → 행동 → 결과',34,YELLOW,500)
 timeline(d,90,787,1160,u,labels)

def timing(im,bank,u,key,ep):
 d=ImageDraw.Draw(im);frames=phase_frames(bank);N=12 if ep=='A04' else 8
 f=min(N,int(u*(N+1)));progress=f/N
 # Same endpoints and elapsed display time. Only sampling/holds differ.
 left=progress;right=(.16*progress/.58 if progress<.58 else .16+(progress-.58)*.84/.42)
 if ep=='A04':
  prep=(frames[1]-frames[0])/max(1,frames[2]-frames[0]);right=0 if f==0 else prep if f<=8 else prep+(progress-8/12)*(1-prep)/(1-8/12)
 for side,amount in enumerate([left,right]):
  x=55+side*930;text(d,(x,183),'고른 간격' if not side else '첫 변화 크게 · 준비 자세 유지' if ep=='A04' else '준비를 남기고 빠르게 타격',36,TEAL if not side else RED,865)
  fi=frames[2] if f==N else min(frames[2]-1,round(frames[0]+(frames[2]-frames[0])*amount))
  # This is a held-key-pose editing experiment, not resimulation of the retail game.
  fit(im,detail(bank,fi),(x,242,875,500))
  for k in range(N+1):
   xx=x+35+k*800/N;d.line((xx,775,xx,790),fill=MUTED,width=2)
  arrow(d,(x+35,765),(x+35+800*progress,765),TEAL if not side else RED,5)
  text(d,(x+35,811),f'진행 {f}/{N}F · 같은 주요 자세와 도착 시각',28,MUTED,805)
 text(d,(65,868),f'기록된 자세의 시간 배분 실험 · {N}프레임 시간표를 느리게 펼쳐 관찰',27,MUTED,1700)

def startup_board(im,u):
 d=ImageDraw.Draw(im)
 text(d,(70,198),'Zero Suit Samus · Jab 1 (첫 잽)',43,TEAL,1700)
 # A character-identification still, never mislabeled as a recorded Jab1.
 portrait=picture('jab',0).crop((820,75,1310,620));fit(im,portrait,(70,290,430,480))
 text(d,(75,800),'캐릭터 식별용 정지 화면',27,MUTED,460)
 text(d,(590,285),'Startup: 1F',74,YELLOW,1200)
 text(d,(595,395),'첫 번째 프레임부터 공격 판정',42,WHITE,1200)
 for i in range(8):
  x=600+i*145;c=RED if i==0 else LINE
  d.rectangle((x,525,x+115,665),outline=c,width=6)
  text(d,(x+57,585),'공격' if i==0 else '—',35,c if i==0 else MUTED,110,anchor='mm')
  text(d,(x+57,705),f'{i+1}F',31,WHITE,110,anchor='mm')
 text(d,(595,760),'이후의 활성·복귀 구간은 별도의 기술 데이터',31,MUTED,1220)
 text(d,(595,817),'기술 데이터: Ultimate Frame Data · Zero Suit Samus / Jab 1',27,MUTED,1240)

def fist_board(im,u):
 d=ImageDraw.Draw(im);text(d,(65,200),'Scale (부위 크기 변화)',42,TEAL,1700)
 for side,cx in enumerate([490,1420]):
  s=1 if not side else 1+.8*math.sin(math.pi*u/2);cy=535
  d.line((cx-220,cy+30,cx,cy+30),fill=WHITE,width=29)
  points=[(cx+xx*s,cy+yy*s) for xx,yy in [(-80,-95),(65,-95),(100,-45),(95,80),(-65,95),(-100,20)]]
  d.polygon(points,fill=BG,outline=TEAL if not side else RED,width=9)
  for j in range(3):d.line((cx+(-45+j*40)*s,cy-90*s,cx+(-45+j*40)*s,cy-25*s),fill=WHITE,width=4)
  text(d,(cx,320),'기본 크기' if not side else '주먹 부분만 확대',40,TEAL if not side else RED,800,anchor='mm')
  text(d,(cx,790),'손의 도착 위치는 유지',32,MUTED,800,anchor='mm')
  d.ellipse((cx-15,cy-15,cx+15,cy+15),outline=GREEN,width=5)
 text(d,(65,850),'눌리며 부피를 유지하는 변형과, 공격 부위를 키우는 과장은 목적이 다릅니다',31,YELLOW,1790)

def principle_header(im,subtitle):
 d=ImageDraw.Draw(im);d.rectangle((1200,18,1880,145),fill=BG)
 text(d,(1860,49),'직접 구성한 원리 도식',29,MUTED,650,anchor='rt')
 text(d,(1860,106),subtitle,26,MUTED,650,anchor='rt')

def hand(im,bank,n,u,key):
 d=ImageDraw.Draw(im)
 if key=='grip':
  text(d,(65,184),'병의 목을 쥔 손',38,TEAL);text(d,(1030,184),'병의 몸통을 쥔 손',38,RED)
  fit(im,detail('bottle-neck',min(n,83)),(65,244,850,545));fit(im,detail('bottle-body',min(n,53)),(1030,244,850,545))
  text(d,(65,818),'서로 다른 실제 장면 · 물체를 쥐는 위치와 손 모양 비교',28,MUTED)
  return
 fit(im,detail(bank,n),(55,245,980,550));text(d,(55,184),'실제 연속 손동작',38,TEAL)
 text(d,(1130,184),'미리 준비한 손 모양',38,RED,710)
 # A labeled hand-shape selector, not a procedural humanoid demonstration.
 for i,(label,closed) in enumerate([('펴기',0),('굽히기',.5),('쥐기',1)]):
  x=1170+i*215;y=440;selected=i==min(2,int(u*3));c=YELLOW if selected else MUTED
  d.rounded_rectangle((x-50,y,x+60,y+120),radius=24,outline=c,width=5)
  for j in range(4):
   xx=x-35+j*27;tip=(xx+closed*24,y-115+closed*135)
   d.line([(xx,y+12),(xx,y-45+closed*70),tip],fill=c,width=7,joint='curve')
  text(d,(x,y+165),label,31,c,180,anchor='mt')
 text(d,(1100,766),'손 모양을 고르는 원리 도식',30,MUTED,760)

def graph_panel(im,kind,u,key,full=False):
 d=ImageDraw.Draw(im);x=1045;y=260;w=790;h=545
 d.rectangle((55 if full else 1015,210,1880,835),fill=BG)
 if not full:text(d,(1045,216),'직접 구성한 원리 모형',29,MUTED,790)
 if not full and kind=='fkik':
  d.rectangle((1020,210,1860,295),fill=BG)
  text(d,(1045,216),'Forward Kinematics (순운동학)',28,TEAL,790)
  text(d,(1045,255),'Inverse Kinematics (역운동학)',28,RED,790)
 elif kind in ('blend','weights'):
  d.rectangle((1020,210,1860,260),fill=BG)
  text(d,(1045,216),'Animation Blending (애니메이션 블렌딩)' if kind=='blend' else 'Blend Weight (혼합 가중치)',28,YELLOW,790)
 elif kind in ('collision','active'):
  d.rectangle((1020,210,1860,260),fill=BG)
  text(d,(1045,216),'Hitbox (공격 영역) / Hurtbox (피격 영역)',28,YELLOW,790)
 if kind in ('collision','active','space','prop','displacement','return','squash'):
  if kind=='space':
   text(d,(1050,278),'위에서 보는 기준 평면',35,YELLOW,780)
   for yy in [420,520,620,720]:d.line((1080,yy,1820,yy),fill=LINE,width=2)
   for xx in [1100,1280,1460,1640,1820]:d.line((xx,390,xx,750),fill=LINE,width=2)
   d.ellipse((1125,515,1205,595),outline=TEAL,width=7);d.ellipse((1620,490,1740,610),outline=RED,width=7)
   arrow(d,(1205,555),(1620,555),YELLOW);text(d,(1080,775),'화면의 겹침과 깊이를 구분',32,WHITE,750)
  elif kind in ('collision','active'):
   text(d,(1050,278),'같은 검 경로 · 한 조건만 변경',34,YELLOW,780)
   for side,cy in enumerate([430,665]):
    v=min(1,u/.70);start=(1130,cy);tip=(1390+220*v,cy);r=(65 if side==0 else 125) if kind=='collision' else 88
    active=(.15<v<.35) if side==0 else (.67<v<=1)
    if kind=='collision':active=True
    target=(1740 if kind=='collision' else 1640,cy);hit=active and abs(tip[0]-target[0])<r+35
    d.line((1100,cy,1780,cy),fill=LINE,width=3);d.line((1100,cy,tip[0],cy),fill=WHITE,width=8)
    c=RED if active else MUTED;d.ellipse((tip[0]-r,cy-r,tip[0]+r,cy+r),outline=c,width=6)
    d.rectangle((target[0]-30,cy-70,target[0]+30,cy+70),outline=GREEN if hit else WHITE,width=6)
    text(d,(1055,cy-110),('좁은 범위' if side==0 else '넓은 범위') if kind=='collision' else ('앞쪽 활성 구간' if side==0 else '뒤쪽 활성 구간'),31,c,760)
    text(d,(1740,cy+83),'명중' if hit else '비접촉',29,GREEN if hit else MUTED,150,anchor='mm')
   text(d,(1080,817),'경로 · 범위 · 시간은 서로 다른 조건',28,MUTED,760)
  elif kind=='prop':
   text(d,(1050,280),'몸 반전 + 손과 소품의 대응',34,YELLOW,780)
   for side,cx in enumerate([1225,1640]):
    c=TEAL if not side else RED;d.ellipse((cx-35,360,cx+35,430),outline=c,width=6);d.line((cx,430,cx,650),fill=c,width=8)
    hand=(cx+(100 if side==0 else -100),500);chain(d,[(cx,465),hand],c);d.rectangle((hand[0]-20,450,hand[0]+25,610),outline=YELLOW,width=6)
    text(d,(cx,730),'오른손' if not side else '왼손',34,c,270,anchor='mm')
   arrow(d,(1390,525),(1475,525),GREEN)
  elif kind=='return':
   text(d,(1050,280),'공격 경로와 복귀 경로',35,YELLOW,780)
   a=(1130,540);b=(1740,540);arrow(d,a,b,RED)
   curve=[(1740-610*t,540+150*math.sin(math.pi*t)) for t in np.linspace(0,1,70)];d.line(curve,fill=TEAL,width=7,joint='curve')
   text(d,(1110,775),'같은 직선을 역재생 / 다른 곡선으로 복귀',29,MUTED,750)
  elif kind=='displacement':
   text(d,(1050,280),'자세 변화와 전체 이동을 분리',35,YELLOW,780)
   d.line((1080,720,1810,720),fill=GREEN,width=6)
   for i,cx in enumerate([1210,1570]):
    offset=130*u if i else 0;hip=(cx+offset,520);chain(d,[(cx+offset-65,720),hip,(cx+offset+70,720)],TEAL if not i else RED)
    arrow(d,hip,(hip[0]-80*u,380),YELLOW)
    text(d,(cx,780),'자세만' if not i else '자세 + 전체 이동',31,WHITE,350,anchor='mm')
  else:
   text(d,(1050,280),'이동 경로는 그대로 · 주먹만 확대',33,YELLOW,780)
   for side,cx in enumerate([1210,1640]):
    size=1 if not side else 1+.8*math.sin(math.pi*u/2)
    d.line((cx-110,570,cx+10,570),fill=WHITE,width=20)
    fist=[(-55,-65),(45,-65),(70,-30),(65,55),(-45,65),(-70,15)]
    points=[(cx+xx*size,535+yy*size) for xx,yy in fist]
    d.polygon(points,fill=BG,outline=TEAL if not side else RED,width=7)
    for j in range(3):d.line((cx+(-30+j*27)*size,535-60*size,cx+(-30+j*27)*size,535-16*size),fill=WHITE,width=3)
    text(d,(cx,750),'기본 크기' if not side else '손 부분만 확대',30,WHITE,370,anchor='mm')
   text(d,(1070,810),'부피 유지 변형과 공격 강조를 구분하는 도식',28,MUTED,790)
 elif kind in ('blend','weights','slope','weightbase'):
  if kind=='weightbase':
   text(d,(1050,275),'발의 배치 → 몸을 받치는 관계',34,YELLOW,790)
   for cx,cy,theta,label,c in [(1240,665,-.25,'뒤쪽 발',TEAL),(1630,460,.25,'앞쪽 발',RED)]:
    ps=[(cx+xx*math.cos(theta)-yy*math.sin(theta),cy+xx*math.sin(theta)+yy*math.cos(theta)) for xx,yy in [(-55,-95),(55,-95),(55,95),(-55,95)]]
    d.polygon(ps,outline=c,width=6);text(d,(cx,cy+132),label,32,c,300,anchor='mm')
   hip=(1370+170*u,390+150*u);d.ellipse((hip[0]-18,hip[1]-18,hip[0]+18,hip[1]+18),outline=YELLOW,width=6)
   arrow(d,hip,(hip[0],620),YELLOW,5)
   text(d,(1055,810),'자세를 읽는 안내 · 질량 중심 측정이 아닙니다',27,MUTED,800)
  elif kind=='weights':
   c=(1440,490);r=145;theta=u*math.pi*2
   d.ellipse((c[0]-r,c[1]-r,c[0]+r,c[1]+r),outline=LINE,width=5);arrow(d,c,(c[0]+r*.8*math.cos(theta),c[1]+r*.8*math.sin(theta)),GREEN)
   for i,(label,value,c) in enumerate([('기본 자세',1-u,YELLOW),('방향 자세',u,TEAL)]):
    yy=720+i*70;text(d,(1050,yy-17),label,29,c,200);d.line((1270,yy,1800,yy),fill=LINE,width=15);d.line((1270,yy,1270+530*value,yy),fill=c,width=15)
  elif kind=='slope':
   for side,cx in enumerate([1150,1570]):
    ground=lambda x:725-(x-cx)*.32
    d.line((cx-70,ground(cx-70),cx+260,ground(cx+260)),fill=GREEN,width=7)
    hip=(cx+60,430);feet=[(cx-30,725 if not side else ground(cx-30)),(cx+210,725 if not side else ground(cx+210))]
    for foot in feet:
     delta=np.array(foot)-np.array(hip);distance=np.linalg.norm(delta);direction=delta/distance
     along=(180**2-190**2+distance**2)/(2*distance);normal=np.array([-direction[1],direction[0]])
     mid=tuple(np.array(hip)+direction*along+normal*math.sqrt(max(0,180**2-along**2)))
     chain(d,[hip,mid,foot],TEAL if not side else RED)
    text(d,(cx-50,785),'평지 자세' if not side else '지면에 맞춘 발',29,WHITE,340)
  else:
   for side,cx in enumerate([1230,1640]):
    v=(0 if u<.5 else 1) if not side else u
    hip=(cx,630);shoulder=(cx-90*(1-v),440);hand=(cx+130*v,450+110*(1-v));gait=65*math.sin(2*math.pi*u)
    chain(d,[(cx-100+v*gait,750),hip,(cx+100-v*gait,750)],WHITE);chain(d,[hip,shoulder,hand],TEAL if not side else RED)
    text(d,(cx,330),'즉시 교체' if not side else '잠깐 혼합',31,TEAL if not side else RED,350,anchor='mm')
   text(d,(1070,810),'위치 예시: 이전 위치 × (1−w) + 다음 위치 × w',27,YELLOW,760)
 elif kind=='spline':
  text(d,(1045,277),'같은 끝점 · 중간 제어점 추가',34,YELLOW,790)
  for side,cy in enumerate([440,685]):
   a=(1090,cy);b=(1800,cy);amplitude=80*math.sin(math.pi*u)
   if not side:ps=[a,(1435,cy-45),b]
   else:ps=[(a[0]+(b[0]-a[0])*t,cy-amplitude*math.sin(2*math.pi*t)-60*math.sin(math.pi*t)) for t in np.linspace(0,1,61)]
   d.line(ps,fill=TEAL if not side else RED,width=9,joint='curve')
   for pt in ps[::max(1,len(ps)//6)]:d.ellipse((pt[0]-8,pt[1]-8,pt[0]+8,pt[1]+8),outline=YELLOW,width=4)
   for xx,yy in [a,b]:d.ellipse((xx-13,yy-13,xx+13,yy+13),outline=GREEN,width=5)
  text(d,(1080,805),'끝 위치와 중간 윤곽을 각각 제어',31,MUTED,760)
 elif kind in ('fkik','fkik-leg','hint'):
  # A two-link IK solution. Both lengths remain fixed, and hints really change the elbow.
  leg=kind=='fkik-leg'
  for side,cx in enumerate([500,1400] if full else [1150,1570]):
   a=np.array([float(cx),350. if leg else 625.]);delta=np.array([235.,-130. if kind=='hint' else -60-120*u]);delta=np.array([-delta[1],delta[0]]) if leg else delta
   target=a+delta;l1=170.;l2=180.
   if kind in ('fkik','fkik-leg'):
    t=-.25-.8*u;ed=l1*np.array([math.cos(t),math.sin(t)]);hd=ed+l2*np.array([math.cos(t+.65),math.sin(t+.65)])
    if leg:ed=np.array([-ed[1],ed[0]]);hd=np.array([-hd[1],hd[0]])
    target=a+hd
   if kind in ('fkik','fkik-leg') and not side:
    e=a+ed;hand=a+hd
   else:
    delta=target-a;dist=np.linalg.norm(delta);direction=delta/dist;along=(l1*l1-l2*l2+dist*dist)/(2*dist);height=math.sqrt(max(0,l1*l1-along*along))
    sign=(-1 if not side else 1) if kind=='hint' else -1;e=a+direction*along+np.array([-direction[1],direction[0]])*height*sign;hand=target
   c=TEAL if not side else RED;chain(d,[tuple(a),tuple(e),tuple(hand)],c);d.ellipse((hand[0]-18,hand[1]-18,hand[0]+18,hand[1]+18),outline=GREEN,width=5)
   if kind in ('fkik','fkik-leg'):
    text(d,(cx-250 if full else cx-80,275 if leg else 310),('Forward Kinematics (순운동학)' if not side else 'Inverse Kinematics (역운동학)') if full else ('FK · 관절부터' if not side else 'IK · 손 목표부터'),29,c,800 if full else 360)
    arrow(d,tuple(a+np.array([0.,-27.])),tuple(e+np.array([0.,-27.])),c,4) if not side else arrow(d,tuple(hand+np.array([20.,15.])),tuple(e+np.array([20.,15.])),GREEN,4)
    p=a if not side else hand;d.ellipse((p[0]-23,p[1]-23,p[0]+23,p[1]+23),outline=YELLOW if not side else GREEN,width=8)
   else:text(d,(cx-80,310),'팔꿈치 아래쪽' if not side else '팔꿈치 위쪽',30,c,360)
  text(d,(180 if full else 1060,790),'발의 목표를 먼저 정하고 다리 관절을 맞추기' if leg else '같은 끝점 · 다른 입력 방식' if kind=='fkik' else '손 목표와 굽힘 방향을 각각 제어',34 if full else 29,YELLOW,1540 if full else 790)
 elif kind in ('rotation','rotation-three','curves','gaze','wrist','wrist-bend'):
  for side,cx in enumerate([360,960,1560] if kind=='rotation-three' else [500,1400] if full else [1235,1650]):
   v=u if kind!='curves' or not side else max(0,(u-.18)/.82)
   yaw=math.radians(60*v if not(kind=='gaze' and side) else 40*v)
   pitch=math.radians(10*math.sin(math.pi*u)*(1 if side else 0)) if (kind=='rotation-three' and side==1) or (kind!='rotation-three' and key!='tilt' and kind!='gaze') else 0
   roll=math.radians(10*math.sin(math.pi*u)*(1 if side else 0)) if (kind=='rotation-three' and side==2) or (kind!='rotation-three' and key=='tilt') else 0
   if kind=='wrist-bend':yaw=0;pitch=0;roll=math.radians(25*math.sin(math.pi*u)*side)
   cy=475 if full else 510;c=[TEAL,RED,GREEN][side] if kind=='rotation-three' else TEAL if not side else RED
   # Project a neutral ellipsoid and nose using the same rotation as the plotted curves.
   def proj(p):
    x,y,z=p;wrist=kind.startswith('wrist');y=y-85 if wrist else y
    yy=y*math.cos(pitch)-z*math.sin(pitch);zz=y*math.sin(pitch)+z*math.cos(pitch)
    xx=x*math.cos(yaw)+zz*math.sin(yaw);zz=-x*math.sin(yaw)+zz*math.cos(yaw)
    xr=xx*math.cos(roll)-yy*math.sin(roll);yr=xx*math.sin(roll)+yy*math.cos(roll)
    scale=1.3 if full else 1
    return (cx+scale*(xr+.18*zz),cy+scale*(yr-.12*zz+(85 if wrist else 0)))
   if kind.startswith('wrist'):
    outline=[(-65,85,0),(-65,-40,0),(-45,-130,0),(-25,-135,0),(-15,-45,0),(-5,-150,0),(15,-150,0),(25,-45,0),(40,-135,0),(58,-130,0),(60,-35,0),(90,-75,0),(110,-60,0),(65,45,0),(55,85,0)]
    ps=[proj(p) for p in outline];d.polygon(ps,fill=BG,outline=c,width=5)
    size=1.3 if full else 1
    for sign in [-1,1]:d.line(((cx+sign*40*size,cy+85*size),(cx+sign*40*size,cy+210*size)),fill=WHITE,width=7)
    d.ellipse((cx-10,cy+85*size-10,cx+10,cy+85*size+10),fill=YELLOW)
    label=('곧게 편 손목' if not side else '조금 굽힌 손목') if kind=='wrist-bend' else ('한 축 회전' if not side else '기울이며 회전')
    text(d,(cx,235 if full else 285),label,34 if full else 29,c,700 if full else 370,anchor='mm')
   else:
    d.ellipse((cx-110,cy-140,cx+110,cy+140),outline=MUTED,width=4)
    for lat in [-.6,0,.6]:
     pts=[proj((105*math.sqrt(1-lat*lat)*math.sin(t),135*lat,105*math.sqrt(1-lat*lat)*math.cos(t))) for t in np.linspace(-math.pi/2,math.pi/2,55)]
     d.line(pts,fill=LINE,width=2)
   nose=proj((0,0,145))
   if kind=='wrist-bend':arrow(d,proj((0,85,0)),proj((0,-80,0)),c)
   else:arrow(d,proj((0,0,0)),nose,c)
   eye=proj((32,-40,95))
   if not kind.startswith('wrist'):
    for p in [(32,-40,95),(-32,-40,95)]:
     ex,ey=proj(p);d.ellipse((ex-7,ey-7,ex+7,ey+7),fill=WHITE)
    d.line([proj((-28,50,105)),proj((28,50,105))],fill=WHITE,width=4)
   if kind=='gaze':arrow(d,eye,(eye[0]+110*math.sin(math.radians(60*u)),eye[1]-30),GREEN,5)
   if kind=='rotation-three':text(d,(cx,235),['좌우 회전만','숙임을 함께','옆 기울임을 함께'][side],34,[TEAL,RED,GREEN][side],550,anchor='mm')
   elif not kind.startswith('wrist'):text(d,(cx,305),'한 축' if not side else '기울임도 함께' if kind!='gaze' else '머리 + 눈',30,c,360,anchor='mm')
   if kind=='curves':
    for j,color in enumerate([YELLOW,TEAL]):
     yy=735+j*65;ps=[];text(d,(cx-160,yy-60),'Yaw (좌우)' if j==0 else 'Pitch (숙임)',25,color,330)
     for q in range(61):
      t=q/60;value=(t if not side else max(0,(t-.18)/.82)) if j==0 else math.sin(math.pi*t)*(1 if side else 0)
      ps.append((cx-160+320*t,yy-38*value))
     d.line((cx-160,yy,cx+160,yy),fill=LINE,width=2);d.line(ps,fill=color,width=4);xx=cx-160+320*u;d.line((xx,yy-43,xx,yy+4),fill=WHITE,width=2)
   elif kind=='gaze':
    xx=cx-165;yy=755;head=(1 if not side else 2/3)*u;eyes=(0 if not side else 1/3)*u
    d.line((xx,yy,xx+330,yy),fill=LINE,width=16);d.line((xx,yy,xx+330*head,yy),fill=c,width=16)
    if eyes:d.line((xx+330*head,yy,xx+330*(head+eyes),yy),fill=GREEN,width=16)
    text(d,(cx,810),'같은 축 · 머리 방향 + 눈 방향',26,MUTED,390,anchor='mm')
   else:
    if kind=='rotation-three':
     text(d,(cx,670),'최종 Yaw: 60° · 동일',31,WHITE,550,anchor='mm')
     text(d,(cx,715),['추가 축 없음','중간 Pitch: 10°','중간 Roll: 10°'][side],30,c,550,anchor='mm')
    ps=[(cx-150+300*t,(825 if full else 750)-(65*math.sin(math.pi*t) if side else 0)) for t in np.linspace(0,1,61)]
    d.line(ps,fill=c,width=5,joint='curve');cursor=ps[round(u*60)];d.ellipse((cursor[0]-8,cursor[1]-8,cursor[0]+8,cursor[1]+8),fill=WHITE)
    text(d,(cx,865 if full else 805),'추가 축의 각도 변화 · 세로 확대',26,MUTED,600 if full else 385,anchor='mm')

def draw(ep,row,span,local_frame,absolute_frame):
 key=span['key'];s=row['studyDefinitions'][key];bank=s['bank'];grammar=s['grammar']
 clock=span.get('newFrame',absolute_frame)/60
 context=' '.join(c['text'] for c in row.get('renderNarrationCues',row['bodyNarrationCues']) if c['start']<=clock<c['end']+.5)
 if 'nativeLeadBank' in span:bank=span['nativeLeadBank']
 elif ep=='A08' and any(w in context for w in ['옷감','목도리','외투','치마','마엘']):bank='maelle'
 if ep=='A17' and key=='hint' and absolute_frame>=275*60:grammar='spline'
 if ep=='A17' and key=='fkik' and any(w in context for w in ['발이','다리','발의']):grammar='fkik-leg'
 if ep=='A08' and '손목' in context:grammar='wrist-bend'
 if ep=='A18' and key in ('head','tilt') and 136*60<=absolute_frame<173.2*60:grammar='rotation-three'
 if ep=='A07' and key=='gesture' and 220*60<=absolute_frame<247.5*60:bank='luigi-head'
 if ep=='A18' and key=='wrist' and absolute_frame<202.27*60:
  grammar='phases';s=dict(s,phaseLabels=['처음 자세','움직이는 중','몸이 따라옴','다음 자세'])
 im=backdrop(ep,key,row['title'],bank,grammar).copy();d=ImageDraw.Draw(im)
 if grammar in ('wrist-bend','fkik-leg'):
  d.rectangle((55,93,1195,145),fill=BG)
  text(d,(55,103),'팔에서 손끝으로 이어지는 방향' if grammar=='wrist-bend' else '같은 제어 원리를 발 목표에도 적용',33,TEAL,1140)
 if grammar in ('startup','squash','wrist','wrist-bend','fkik-leg','rotation-three'):
  principle_header(im,{'startup':'Startup (발동 프레임) · 기술 데이터','squash':'부위 크기 변화 · 설명 모형','wrist':'손목 회전 · 같은 끝 방향','wrist-bend':'팔뚝에서 손끝까지 이어지는 방향','fkik-leg':'발 목표 · 관절 제어','rotation-three':'같은 최종 좌우 방향 · 다른 중간 회전'}[grammar])
  u=(local_frame%240)/239
  if grammar=='startup':startup_board(im,u)
  elif grammar=='squash':fist_board(im,u)
  else:graph_panel(im,grammar,u,key,full=True)
  return im
 native=(span['mode']=='native' and not span.get('nativeLeadCompleted')) or 'nativeLeadFrame' in span
 length=round((SOURCES[bank][2]-SOURCES[bank][1])*60)
 native_frame=span.get('nativeLeadFrame',local_frame)
 if native and native_frame>=3*length:
  native=False;local_frame=native_frame-3*length
 n=min(native_frame,3*length-1)%length if native else min(length-1,int(local_frame*.5)%length)
 u=n/max(1,length-1)
 if native:
  fit(im,detail(bank,n),(65,185,1310,642));fit(im,picture(bank,n),(1390,245,475,267))
  text(d,(1390,197),'원래 화면',30,MUTED,470);text(d,(1390,570),'1.0배 · 실제 속도',32,TEAL,470)
  text(d,(1390,625),f'반복 관찰 {min(3,native_frame//length+1)}/3' if 'nativeLeadFrame' in span else '동작 전체를 다시 관찰',32,YELLOW,470)
  return im
 if ep=='A12' and key=='expression' and any(w in context for w in ['그림','그려','수정 방향','스케치']):
  text(d,(65,184),'실제 표정의 움직임',36,TEAL,900);text(d,(1030,184),'선택한 프레임 · 수정 방향 제안',34,RED,820)
  fit(im,picture('lune',n),(65,250,855,500));x,y,w,h=fit(im,detail('lune',90),(1030,245,820,540))
  d.rectangle((x,y,x+w,y+h),outline=RED,width=6)
  for px,py in [(220,220),(350,215)]:
   at=(x+px*w/610,y+py*h/640);arrow(d,at,(at[0],at[1]-50),YELLOW,6)
  text(d,(1030,816),'선택한 정지 화면 위에 표시한 눈썹 수정 방향',27,MUTED,825)
  return im
 if ep=='A05' and key=='impact' and '윤곽' in context:n=phase_frames(bank)[2]
 if ep=='A03' and any(w in context for w in ['프레임','제어','초당','조작','캔슬','시간','판정']):
  fit(im,detail(bank,n),(55,240,930,535));text(d,(60,183),'실제 공격 동작',36,TEAL,930)
  text(d,(1070,210),'설명용 시간표 · 직접 설정한 값',29,MUTED,760)
  for i,label in enumerate(['동작 전체','다음 행동 입력','공격 판정']):
   yy=370+i*180;text(d,(1070,yy-65),label,34,(YELLOW,GREEN,RED)[i],760)
   d.line((1080,yy,1830,yy),fill=LINE,width=22)
   if i==0:d.line((1080,yy,1830,yy),fill=YELLOW,width=22)
   if i==1:d.line((1080+750*36/48,yy,1830,yy),fill=GREEN,width=22)
   if i==2:d.line((1080+750*.55,yy,1080+750*.68,yy),fill=RED,width=22)
   xx=1080+750*u;d.line((xx,yy-28,xx,yy+28),fill=WHITE,width=4)
  text(d,(1080,830),'0F                 36F · 제어 가능      48F',28,WHITE,760)
 elif grammar=='timing':timing(im,bank,(local_frame%240)/239,key,ep)
 elif grammar=='hand':hand(im,bank,n,u,key)
 elif grammar in ('blend','weights','slope','weightbase','collision','active','fkik','hint','spline','rotation','curves','gaze','wrist','space','prop','displacement','return','squash'):
  observed=picture(bank,n).crop((0,50,530,1040)) if grammar=='weightbase' else detail(bank,n)
  fit(im,observed,(55,250,930,535));text(d,(60,184),'게임 속 전사 자세' if grammar=='weightbase' else '실제 게임의 보이는 동작',35,TEAL,930)
  graph_panel(im,grammar,(local_frame%240)/239,key)
 elif grammar=='phases':
  if local_frame<length*2:
   observation(im,bank,n,grammar,ep,key,s['phaseLabels'],u);text(d,(1360,700),'0.5배 · 동작 분석',31,YELLOW,500)
  else:phase_grid(im,bank,s['phaseLabels'])
 else:observation(im,bank,n,grammar,ep,key,s['phaseLabels'],u)
 return im

if __name__=='__main__':prepare_banks()
