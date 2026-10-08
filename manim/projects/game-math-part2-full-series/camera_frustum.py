"""Original narration-timed spatial camera diagrams for the complete10.2 lesson.

Semantic camera axes:+x right,+y up,+z forward. The oblique drawing projection
only illustrates depth and never represents a game's projection matrix.
"""
import json,math,textwrap
import numpy as np
from manim import *
from lesson import ROOT,txt,fit,card,timing,INK,MUTED,RULE,RED,GREEN,BLUE,GOLD,PALE

VIEW=np.array([1.3,.85,-1.])
MODE_ALIASES={'aspect-fov':'aspect','orthographic':'ortho'}
def point(p):
 x,y,z=np.asarray(p,dtype=float);return np.array([x+1.3*z,y+.85*z,0.])
def edge(a,b,color=RULE,width=2,dashed=False):
 return (DashedLine if dashed else Line)(point(a),point(b),color=color,stroke_width=width)
def face(points,color=PALE,opacity=.7):
 return Polygon(*[point(p) for p in points],stroke_color=RULE,stroke_width=1.1,fill_color=color,fill_opacity=opacity)
def label(p,value,color=INK,size=25,shift=(0,0,0)):
 return txt(value,size,color).move_to(point(p)+np.array(shift)).add_background_rectangle(color=WHITE,opacity=.92,buff=.035)
def box(center,size,color=PALE,R=None):
 c=np.asarray(center);h=np.asarray(size)/2;faces=[]
 R=np.eye(3) if R is None else R
 for axis in range(3):
  for sign in [-1,1]:
   n=R[:,axis]*sign
   if np.dot(n,VIEW)<=0:continue
   other=[j for j in range(3) if j!=axis];pts=[]
   for u,v in [(-1,-1),(1,-1),(1,1),(-1,1)]:
    p=np.zeros(3);p[axis]=sign*h[axis];p[other[0]]=u*h[other[0]];p[other[1]]=v*h[other[1]];pts.append(c+R@p)
   shade=interpolate_color(ManimColor(color),ManimColor('#8d99a5'),.25 if axis!=2 else .05)
   faces.append((np.dot(np.mean(pts,axis=0),VIEW),face(pts,shade,1)))
 return VGroup(*[f for _,f in sorted(faces,key=lambda t:t[0])])
def positioned(obj,width=6.15,height=3.2,center=(-3.28,-.35,0)):
 # The scene wrapper fits the union of all states once. Refitting each state
 # would move a supposedly fixed camera when changing only FOV or zoom.
 return obj
def cam(z=0):
 return VGroup(box([0,0,z],[.5,.4,.45],BLUE),box([0,0,z+.3],[.3,.26,.24],GOLD))
def corners(z,hfov=90,aspect=16/9,ortho=False,ortho_width=4):
 x=ortho_width/2 if ortho else z*math.tan(math.radians(hfov/2));y=x/aspect
 return np.array([[-x,-y,z],[x,-y,z],[x,y,z],[-x,y,z]])
def frustum(hfov=90,near=1,far=4,aspect=16/9,ortho=False,highlight=None,ortho_width=4,show_labels=True):
 a,b=corners(near,hfov,aspect,ortho,ortho_width),corners(far,hfov,aspect,ortho,ortho_width)
 planes=[a,b,*[np.array([a[i],a[(i+1)%4],b[(i+1)%4],b[i]]) for i in range(4)]]
 fills=[]
 for i,p in enumerate(planes):
   colors=['#d8e6d4','#dce5ef','#eadfce','#d3e1e9','#e2e8d4','#d4dee8']
   fills.append((float(np.dot(p.mean(axis=0),VIEW)),face(p,GREEN if i==highlight else colors[i],.40 if i==highlight else .27)))
 obj=VGroup(*[f for _,f in sorted(fills,key=lambda t:t[0])],cam())
 for i in range(4):
  obj.add(edge(a[i],a[(i+1)%4],GREEN,2.1),edge(b[i],b[(i+1)%4],BLUE,2.1),edge(a[i],b[i],RULE,1.6))
  if not ortho:obj.add(edge([0,0,0],a[i],GOLD,1.2,dashed=True))
  else:obj.add(edge(a[i]-.6*np.array([0,0,1]),b[i],GOLD,1.4,dashed=True))
 obj.add(edge([0,0,0],[0,0,far+.5],MUTED,dashed=True))
 if show_labels:obj.add(label([0,0,0],'카메라',BLUE,25,(-.85,-.75,0)),label([0,0,near],'near',GREEN,24,(.15,.18,0)),label([0,0,far],'far',BLUE,24,(.6,-.2,0)))
 return obj
def screen(split=False,stretch=1,highlight=None,split_labels=True):
 w,h=6,3.375
 obj=VGroup(box([0,0,-.13],[w,h,.26],PALE))
 if split:
  obj.add(face([[-3,-h/2,0],[0,-h/2,0],[0,h/2,0],[-3,h/2,0]],'#dce8db',.95),face([[0,-h/2,0],[3,-h/2,0],[3,h/2,0],[0,h/2,0]],'#dce5ef',.95),edge([0,-h/2,.01],[0,h/2,.01],RED,3))
  if split_labels:obj.add(label([-1.5,0,.01],'왼쪽 960×1080',GREEN,27),label([1.5,0,.01],'오른쪽 960×1080',BLUE,27))
 else:
  cell=VGroup(*[edge([x,-h/2,.01],[x,h/2,.01],RULE,1) for x in np.linspace(-3,3,9)],*[edge([-3,y,.01],[3,y,.01],RULE,1) for y in np.linspace(-h/2,h/2,6)])
  ring=Circle(radius=1,color=GREEN,stroke_width=4).stretch(stretch,0);obj.add(cell,ring)
 obj.add(label([-3,h/2,0],'(0,0)',RED,24,(-.2,.32,0)),label([0,-h/2,0],'가로1920 / 세로1080',INK,25,(0,-.35,0)))
 if highlight=='pixel':obj.add(box([-1.55,.85,.2],[.68*stretch,.68,.2],GOLD),label([-1.55,.85,.4],'1칸',INK,23))
 return obj
def fov_diagram(theta=90,depth=3):
 half=depth*math.tan(math.radians(theta/2));obj=frustum(theta,1,depth)
 obj.add(edge([-half,0,depth],[half,0,depth],RED,3),label([0,1.0,depth],f'폭 {2*half:.2f}',RED,25),label([0,0,0],f'θx={theta:.2f}°',GOLD,25,(-1.1,.55,0)))
 return obj
def plates(perspective=True,dolly=False,zoom=1,turned=False,depths=None,camera_z=None):
 # Left is spatial placement; right small windows give independently calculated widths.
 original_depths=depths if depths is not None else ([4,8] if perspective else [2,10])
 camera_z=(2 if dolly else 0) if camera_z is None else camera_z
 z=[depth-camera_z for depth in original_depths];obj=VGroup(cam(.4*camera_z))
 for i,(depth,color) in enumerate(zip(z,[GREEN,RED])):
  original=original_depths[i]
  a=PI/3 if turned and i==1 else 0;R=np.array([[math.cos(a),0,math.sin(a)],[0,1,0],[-math.sin(a),0,math.cos(a)]])
  # Compress the illustrative depth axis equally for every state, so the
  # calculated image rectangles remain readable. The semantic z values and
  # projection factors below are exact and independent of this drawing view.
  obj.add(box([(-.7 if i==0 else .7),0,.4*original],[1.3,1,.18],color,R),label([(-.7 if i==0 else .7),.8,.4*original],f'z={depth}',color,26))
  factor=zoom/depth if perspective else zoom/4
  slab=Rectangle(width=factor*6,height=factor*4,color=color,fill_color=color,fill_opacity=.75).move_to([(-1.6 if i==0 else 1.6),-1.55,0])
  if turned and i==1:slab.stretch(.5,0)
  obj.add(slab)
 obj.add(edge([0,0,0],[0,0,.4*(max(original_depths)+.8)],BLUE,dashed=True),label([0,-2.9,0],'계산한 화면 크기',BLUE,25))
 return obj
def lens(sensor=36,focal=18):
 # Millimetres use a common drawing scale; rays meet the defined focal point.
 scale=.12;s=sensor*scale;f=focal*scale
 obj=VGroup(box([0,0,0],[s,1.7,.16],GREEN),box([0,0,f],[.38,.65,.45],GOLD),edge([-s/2,0,0],[0,0,f],BLUE,3),edge([s/2,0,0],[0,0,f],BLUE,3),edge([0,0,0],[0,0,f],RULE,1.4,dashed=True),label([0,1.2,0],f'센서 {sensor} mm',GREEN,27),label([0,0,f/2],f'f={focal} mm',GOLD,27,(.7,0,0)))
 return obj
def diagram(mode,i):
 mode=MODE_ALIASES.get(mode,mode)
 if mode=='overview':return positioned(VGroup(frustum(53.13 if i==2 else 75,1,3,ortho=i==3),screen(True).scale(.45).shift([5.8,-.2,0])),width=11.8,height=1.95,center=(0,-.2,0))
 if mode=='output':
  obj=screen(split=i>=2)
  if i==0:obj.add(box([3.5,0,1],[1.1,1.3,.3],BLUE),label([3.5,1,1],'텍스처',BLUE,25))
  if i==4:obj.add(edge([-.08,-1.7,.12],[-.08,1.7,.12],RED,4))
  if i==5:obj.add(cam().scale(.6).shift([-1.5,2.1,0]),cam().scale(.6).shift([1.5,2.1,0]))
  return positioned(obj)
 if mode=='pixel-aspect':return positioned(screen(stretch=4/3 if i in [3,4] else 1,highlight='pixel'))
 if mode=='frustum':
  obj=frustum(60 if i==3 else 90)
  if i==0:
   c=corners(4,90)
   obj=VGroup(cam(),face(c,BLUE,.18),*[edge([0,0,0],p,GOLD,2.2) for p in c],*[edge(c[j],c[(j+1)%4],BLUE,2) for j in range(4)],label([0,0,0],'카메라',BLUE,25,(-.85,-.75,0)))
  if i==2:obj.add(box([0,0,2],[1.4,1.2,.2],RED),Dot(point([0,0,3]),color=GREEN))
  if i==3:obj.rotate(.12,about_point=point([0,0,0]))
  if i==4:obj.add(screen().scale(.25).shift([4.9,-.6,0]))
  return positioned(obj)
 if mode=='planes':
  obj=frustum(90,.4,4.4,highlight=[2,3,0,0,3,0,1,1][i])
  if i>=3:
   # Presentation depth is scaled; the labels retain the defined semantic z values.
   for p,t,c,shift in [([0,0,.2],'0.5',RED,(.3,-.6,0)),([0,0,2.4],'6',GREEN,(.25,.45,0)),([0,0,4.8],'12',RED,(.4,.5,0))]:obj.add(Dot(point(p),color=c,radius=.10),label(p,t,c,27,shift))
  if i==4:obj.add(Dot(point([3.4,0,2.4]),color=RED),label([3.4,0,2.4],'옆면 밖',RED,25,(0,.4,0)))
  if i==5:
   obj=VGroup(face([[-1,.5,2],[1,.5,2],[0,-.6,.5]],'#e4c9c7',.55),face([[-1,.5,2],[1,.5,2],[1/3,-7/30,1],[-1/3,-7/30,1]],'#dce8db',.95),face([[-2,-1,1],[2,-1,1],[2,1,1],[-2,1,1]],BLUE,.14),label([0,1.4,1],'near=1',BLUE,28))
  return positioned(obj)
 if mode in ['fov','zoom']:return positioned(fov_diagram(53.130102354 if (mode=='zoom' and i>=2) or (mode=='fov' and i==4) else 90,6 if mode=='fov' and i==3 else 3))
 if mode=='aspect':
  obj=frustum(90,1,3,aspect=1 if i==2 else 16/9)
  obj.add(screen(stretch=16/9 if i==2 else 1).scale(.28).shift([4.4,-.3,0]))
  return positioned(obj)
 if mode=='dolly':return positioned(plates(dolly=i in [2,3,4],zoom=2 if i==1 else 1))
 if mode=='physical':return positioned(lens(sensor=18 if i==4 else 36,focal=36 if i==3 else 18))
 if mode=='ortho':
  if i in [1,2,3]:return positioned(plates(perspective=False,turned=i==2,depths=[2,10],camera_z=1 if i==3 else 0))
  return positioned(frustum(90,1,4,ortho=i>=1))
 if mode=='ortho-size':
  obj=frustum(90,1,4,ortho=True,ortho_width=2 if i in [2,3,5] else 4,aspect=8/9 if i==5 else 16/9)
  obj.add(screen(stretch=2 if i==5 else 1).scale(.28).shift([4.3,-.3,0]))
  return positioned(obj)
 if mode=='exercise':
  obj=screen(split=i>=1,split_labels=i<2)
  if i>=2:
   for x,color in [(-1.5,GREEN),(1.5,BLUE)]:
    theta=90 if i==4 else 53.130102354
    angles='θx90° / θy96.73°' if i==4 else 'θx53.13° / θy58.72°'
    mini=frustum(theta,1,3,aspect=8/9,show_labels=False)
    mini.scale(min(2.45/mini.width,2.0/mini.height)).move_to([x,-.1,0])
    obj.add(mini,label([x,1.35,0],'960×1080 / 8:9',color,22),label([x,-1.35,0],angles,color,19))
  if i==5:obj=VGroup(frustum(90,1,4,ortho=True),label([0,-1.8,0],'8×4.5 → 4×2.25',GREEN,30))
  return positioned(obj)
 if mode=='summary':return positioned(VGroup(frustum(75,1,3),frustum(90,1,3,ortho=True).scale(.62).shift([4.3,-.6,0])))
 raise ValueError('Unimplemented camera scene '+mode)

raw_diagram=diagram
LAYOUT={}
def diagram(mode,i):
 mode=MODE_ALIASES.get(mode,mode)
 if mode=='planes' and i==5:
  # A separate magnified clipping case, rather than a FOV comparison. Keep
  # fixed-camera comparisons at their common scale; enlarge this detail so the
  # retained polygon and intersection vertices can actually be inspected.
  obj=raw_diagram(mode,i)
  obj.scale(min(5.8/obj.width,2.7/obj.height)).move_to([-3.28,-.3,0])
  obj.add(fit(txt('삼각형 클리핑 확대',23,MUTED),5.8).move_to([-3.28,1.5,0]))
  return obj
 if mode not in LAYOUT:
  all_states=VGroup(*[raw_diagram(mode,j) for j in range(len(FORMULAS[mode]))])
  width,height,center=(11.8,1.95,np.array([0,-.15,0])) if mode=='overview' else (6.15,3.1,np.array([-3.28,-.3,0]))
  scale=min(width/all_states.width,height/all_states.height)
  LAYOUT[mode]=(scale,center-all_states.get_center()*scale)
 scale,shift=LAYOUT[mode]
 return raw_diagram(mode,i).scale(scale,about_point=ORIGIN).shift(shift)

FORMULAS={
 'overview':['카메라 위치 / 줌 / 창은 어떻게 다를까?','출력 영역 → 픽셀 비율','시야각 → 줌 → 이동','직교 상자 → 두 문제'],
 'output':['렌더 타깃 = 결과 저장소','viewport = 위치 + 크기','1920×1080 → 두 창','(0,0;960,1080) / (960,0;960,1080)','0…959 / 경계960','한 카메라→두 창 / 두 카메라→각 창','화면 밖 텍스처도 결과 저장'],
 'pixel-aspect':['이미지16:9 ≠ 픽셀16:9','(16/9)×(1080/1920)=1','픽셀비 = 표시비 × 해상도높이/너비','(16/9)×(3/4)=4/3','원 → 가로로 늘어난 타원','창 비율과 픽셀 비율을 구별','저장 비율 / 최종 표시 비율','1152/720=16/10'],
 'frustum':['카메라 → 네 모서리 광선','near / far로 잘린 피라미드','시야 안이어도 가릴 수 있음','이동 / 회전 / 벌어지는 각도','창의 위치 ≠ 카메라 위치','여섯 평면의 안쪽'],
 'planes':['left,right,top,bottom,near,far','여섯 반공간의 교집합','예제: +z / near1 / far11','0.5 밖 / 6 사이 / 12 밖','깊이 조건 + 옆면 조건','밖의 꼭짓점 ≠ 전체 삼각형 제거','near·far + 깊이 형식·정밀도','다음: 클립 → 나눗셈 → 픽셀'],
 'fov':['두 끝 사이 전체 θx','90°의 반각은45°','반폭=3tan45°=3','z3 폭6 / z6 폭12','작은 시야각 → 좁은 범위','수평 θx / 수직 θy'],
 'zoom':['zoom = 1/tan(θ/2)','θ90° → zoom1','zoom2 → tan(θ/2)=0.5','θ=2atan0.5≈53.13°','위치 고정 / 화면 중심에서2배','계산 함수: radians 확인','원근 zoom과 직교 zoom의 단위'],
 'aspect':['zx1 / zy16/9','θy=2atan(9/16)≈58.72°','θx=θy90° → 가로 늘어남','zy/zx = 물리적 창 너비/높이','정사각형 픽셀 가정 확인','엔진 FOV는 어느 축인가?','창 변경 시 유지할 축 선언'],
 'dolly':['같은 판 / 깊이4와8','zoom2: 두 판 모두2배','앞으로2 → 깊이2와6','4/2=2 / 8/6=4/3','앞 판 같아도 뒤 판은 다름','분모는 앞쪽 z / 직선 거리 아님','서로 다른 깊이의 기준물 비교'],
 'physical':['초점 거리 + 센서 크기','θx=2atan(sensor/(2f))','sensor36 / f18 →90°','sensor36 / f36 →53.13°','sensor18 / f18 →53.13°','임의 투영 평면 ≠ 물리 렌즈','센서 / 초점 거리 / 창 맞춤'],
 'ortho':['원근: 한 점 / 직교: 평행','깊이2와10 / 같은 크기','회전하면 보이는 폭은 달라짐','앞뒤 이동 / 클립·가림은 별도','직교 시야 = 상자','일정 축척 / 게임 내부는 추측하지 않음'],
 'ortho-size':['world8×4.5 / screen1920×1080','1920/8 = 1080/4.5 = 240','world4×2.25 →480 pixels/unit','zoom8=0.25 / zoom4=0.5','원근은 비율 / 직교는 길이⁻¹','두 축 축척이 다르면 원→타원','직교에도 near와far 필요'],
 'exercise':['전체16:9 / zx1 / zy16/9','창960×1080 / 8:9','세로 유지 / zy 고정','zx=(16/9)/(8/9)=2','가로 유지라면 다른 결과','8×4.5 →4×2.25 / 240→480','창 크기 / 투영 크기 / 위치'],
 'summary':['위치·방향 / 투영 / 출력','픽셀1:1 / 화면16:9','줌2와 앞으로2는 다름','직교 상자 / 가림·클립·축척','약속 기록 → 한 조건 변경 → 비교','다음: 한3D점 → 화면 픽셀']}

class CameraFrustumScene(Scene):
 slug='';sid=''
 def replace(self,old,new):
  if old:self.play(FadeOut(old),run_time=.10);self.remove(old)
  self.play(FadeIn(new,shift=.04*UP),run_time=.20);return new
 def construct(self):
  self.camera.background_color=WHITE
  d=json.loads((ROOT/f'production/batches/game-math-part2-full-series/lessons/{self.slug}.json').read_text(encoding='utf8'))
  s=next(x for x in d['scenes'] if x['id']==self.sid);slot=next(x for x in timing(self.slug,d)['scenes'] if x['id']==self.sid);mode=MODE_ALIASES.get(s['mode'],s['mode'])
  title=fit(txt(s['title'],39),12.5).to_corner(UL,buff=.58)
  subtitle=txt('게임수학 Part 2 / 렌더링 2편 · 위치·시야각·출력 / 정의한+z 예제',20,MUTED).next_to(title,DOWN,aligned_edge=LEFT,buff=.14)
  self.add(title,subtitle,Line([-6.5,2.32,0],[6.5,2.32,0],color=RULE,stroke_width=1))
  obj=diagram(mode,0);self.add(obj);active=equation=footer=None
  for i,beat in enumerate(s['beats']):
   start=slot['lineStarts'][i]
   if start>self.renderer.time+1/60:self.wait(start-self.renderer.time,frozen_frame=True)
   target=diagram(mode,i)
   if i:self.play(Transform(obj,target),run_time=.65)
   else:self.play(Indicate(obj,color=GOLD,scale_factor=1.015),run_time=.55)
   # Wrap long Korean labels; preserve semantic colors and the caption-safe band.
   wrapped='\n'.join(textwrap.wrap(beat,width=26,break_long_words=False,break_on_hyphens=False))
   active=self.replace(active,card(wrapped,width=6.15,size=25,color=GREEN if i==len(s['beats'])-1 else BLUE).move_to([3.12,1.63,0] if mode!='overview' else [0,1.65,0]))
   value=FORMULAS[mode][i];wrapped_formula='\n'.join(textwrap.wrap(value,width=31,break_long_words=False,break_on_hyphens=False))
   equation=self.replace(equation,fit(txt(wrapped_formula,28,RED if mode=='dolly' and i==3 else BLUE),5.8 if mode!='overview' else 12).move_to([3.12,-.48,0] if mode!='overview' else [0,-1.7,0]))
   footer=self.replace(footer,fit(txt('실제 게임의 내부 숫자는 단정하지 않음 / 도식은 명시한 약속의 계산',22,MUTED),12.3).move_to([0,-2.2,0]))
  if slot['seconds']>self.renderer.time:self.wait(slot['seconds']-self.renderer.time,frozen_frame=True)

def make_scenes(slug,module):
 d=json.loads((ROOT/f'production/batches/game-math-part2-full-series/lessons/{slug}.json').read_text(encoding='utf8'))
 return {'Scene'+s['id']:type('Scene'+s['id'],(CameraFrustumScene,),{'slug':slug,'sid':s['id'],'__module__':module}) for s in d['scenes'] if s['kind']=='explanation'}
