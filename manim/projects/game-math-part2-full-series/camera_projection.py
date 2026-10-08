"""Original narrated10.3 diagrams; oblique drawing never changes semantic math.

Semantic main contract: LH row,+z forward,clip[0,w],top-left screen.
All spatial objects have projected faces and consistent common comparison scales.
"""
import json,math,textwrap
import numpy as np
from manim import *
from lesson import ROOT,txt,fit,card,timing,INK,MUTED,RULE,RED,GREEN,BLUE,GOLD,PALE
from camera_frustum import point,edge,face,label,box,cam,frustum

P_WORLD=np.array([4.,2.,5.]);C_WORLD=np.array([2.,1.,1.]);P_VIEW=P_WORLD-C_WORLD
A=np.array([0.,-.6,.5]);B=np.array([-1.,.5,2.]);C=np.array([1.,.5,2.])
I1=B+(A-B)*2/3;I2=C+(A-C)*2/3

def dot(p,color=RED,radius=.075):return Dot(point(p),radius=radius,color=color)
def axes(origin=(0,0,0),length=1.5,names=('x','y','z')):
 o=np.array(origin,dtype=float);g=VGroup()
 for j,color in enumerate([RED,GREEN,BLUE]):
  v=np.eye(3)[j]*length;g.add(edge(o,o+v,color,2.3).add_tip(tip_length=.11),label(o+v,names[j],color,23,(.12,.12,0)))
 return g

def grid(z=0):
 return VGroup(*[edge([a,0,z],[a,0,z+3],RULE,1) for a in np.arange(0,3.1,.5)],*[edge([0,0,z+a],[3,0,z+a],RULE,1) for a in np.arange(0,3.1,.5)])

def pipeline(active=0):
 names=['로컬','월드','뷰','클립','NDC','화면'];g=VGroup()
 for j,name in enumerate(names):
  x=j*1.7;tile=box([x,0,j*.08],[1.38,.95,.25],GREEN if j==active else PALE)
  g.add(tile,label([x,0,j*.08+.15],name,INK,26))
  if j:g.add(edge([(j-1)*1.7+.8,0,(j-1)*.08],[x-.8,0,j*.08],GOLD,2).add_tip(tip_length=.09))
 return g

def compact_pipeline(active=0):
 # A spatial two-row path leaves room to read the six distinct spaces.
 names=['로컬','월드','뷰','클립','NDC','화면'];g=VGroup()
 positions=[[-2,1,0],[0,1,0],[2,1,0],[2,-1,0],[0,-1,0],[-2,-1,0]]
 for j,(name,p) in enumerate(zip(names,positions)):
  color=GREEN if j==active else PALE
  g.add(box(p,[1.55,.85,.3],color),label(np.array(p)+[0,0,.18],name,INK,27))
  if j:
   a=np.array(positions[j-1]);b=np.array(p);unit=(b-a)/np.linalg.norm(b-a)
   g.add(edge(a+unit*.85,b-unit*.85,GOLD,2.6).add_tip(tip_length=.10))
 return g

def model(i):
 s=.5;origin=np.array([3.,2.,5.])*s if i>=1 else np.zeros(3);center=origin+np.array([.25,.25,.25])
 p=P_WORLD*s if i>=1 else np.array([1.,0,0])*s
 localaxes=VGroup(*[edge(origin,origin+np.eye(3)[j]*.65,[RED,GREEN,BLUE][j],2.3).add_tip(tip_length=.10) for j in range(3)])
 g=VGroup(grid(),axes(length=1.2),box(center,[.5,.5,.5],GREEN),localaxes)
 g.add(dot(p),label(p,'P (4,2,5)' if i>=1 else 'P (1,0,0)',RED,28,(-.7,.9,0)))
 if i>=1:g.add(edge([0,0,0],origin,GOLD,3,dashed=True),label(origin,'모델 원점',GOLD,25,(.1,-.65,0)))
 if i==4:
  g.add(edge(origin,origin+np.array([.5,0,0]),BLUE,4).add_tip(tip_length=.12),label(origin+np.array([1.25,.3,0]),'방향 w=0',BLUE,27))
 return g

def view(i):
 s=.5;c=C_WORLD*s;p=P_WORLD*s
 g=VGroup(grid(),axes(length=1.4),cam().scale(.48).shift(point(c)),axes(c,1.3,('오른쪽','위','앞쪽')),dot(p),edge(c,p,GOLD,3,dashed=True),label(p,'P_world (4,2,5)',RED,24,(-.6,.65,0)),label(c,'Camera (2,1,1)',BLUE,24,(-.6,-.6,0)))
 if i>=1:g.add(label((c+p)/2,'뷰 변위 (2,1,4)',GREEN,27,(-.7,.35,0)))
 if i>=3:g.add(dot(c,GREEN),label(c+[-.8,.7,0],'카메라 → 뷰 원점',GREEN,24))
 return g

def homogeneous(i):
 plane=box([0,0,.65],[5.2,3.0,.12],PALE).set_fill(opacity=.2)
 g=VGroup(plane,cam(),axes(length=1.0));p=np.array([2.,1.,4.])*.65
 g.add(dot(p),edge([0,0,0],p,GOLD,2,dashed=True),label(p,'view (2,1,4)',RED,25,(-.7,.65,0)))
 q=p/4 if i!=4 else np.array([2.,1.,.65])
 g.add(dot(q,GREEN),label(q,'나눈 위치' if i!=4 else '직교: 평행',GREEN,24,(.3,-.55,0)))
 if i==4:
  g.add(edge(p,q,BLUE,3,dashed=True))
 if i==5:g.add(box([1.4,0,.65],[2.0,2.2,.12],GREEN),label([1.4,1.5,.65],'비대칭 창',GREEN,24))
 return g

def projection(i):
 # Every coordinate here shares a0.35 illustration scale.
 s=.35;g=frustum(90,1*s,11*s,16/9,show_labels=False)
 p=P_VIEW*s;g.add(dot(p),label(p,'P_view (2,1,4)',RED,26,(-.5,.6,0)),label([0,0,1*s],'near1',GREEN,25,(-.5,-.5,0)),label([0,0,11*s],'far11',BLUE,25,(.55,.1,0)))
 if i>=3:g.add(edge([0,0,0],p,GOLD,3,dashed=True))
 return g

def clip(i):
 # Homogeneous slice at w4: first three clip coordinates, not physical world.
 s=.35
 g=VGroup(box([0,0,2*s],[8*s,8*s,4*s],PALE).set_fill(opacity=.24),axes([-4*s,-4*s,0],.7),label([-4*s,4*s,0],'−w=−4',GREEN,25,(-.3,.3,0)),label([4*s,4*s,4*s],'+w=4',BLUE,25,(.3,.2,0)),label([0,-4*s,0],'z_clip0',GREEN,25,(0,-.35,0)),label([0,-4*s,4*s],'z_clip4',BLUE,25,(0,-.35,0)))
 p=np.array([5,0,2] if i==3 else [2,16/9,3.3])*s
 if i==3:
  g.add(face([[4*s,-4*s,0],[4*s,4*s,0],[4*s,4*s,4*s],[4*s,-4*s,4*s]],BLUE,.15),dot([4*s,0,2*s],GREEN,.09),edge([4*s,0,2*s],p,RED,4).add_tip(tip_length=.09),label([4*s,0,2*s],'경계 x4',GREEN,25,(-.3,-.55,0)))
 g.add(dot(p,RED,.12),label(p,'밖 x5>w4' if i==3 else 'P_clip',RED,26,(-.3,.4,0)))
 return g

def near(i):
 # The original mathematical triangle and near intersection are explicit.
 plane=face([[-1.25,-1,1],[1.25,-1,1],[1.25,1.1,1],[-1.25,1.1,1]],PALE,.45)
 g=VGroup(plane,cam().scale(.33),label([-1.25,1.1,1],'near1',GREEN,25,(-.2,.3,0)))
 poly=[A,B,C] if i<4 else [I1,B,C,I2]
 g.add(face(poly,RED if i<4 else GREEN,.7))
 for name,p in [('A',A),('B',B),('C',C)]:g.add(dot(p),label(p,name+' z'+str(p[2]),RED,25,(-.65,-.32,0) if name=='A' else (-.4,.4,0)))
 if i>=1:
  for p in [I1,I2]:g.add(dot(p,GOLD),label(p,'I₁ −1/3' if p[0]<0 else 'I₂ +1/3',GOLD,23,(-.65,-.48,0) if p[0]<0 else (.65,-.48,0)))
 if i==6:g.add(label([0,-2.1,1],'작은 w → 큰1/w',RED,27))
 return g

def depth_chart(orthographic=False,point_z=4):
 axes2=Axes(x_range=[1,11,2],y_range=[0,1,.25],x_length=5,y_length=1.7,axis_config={'color':INK,'include_tip':False},tips=False).shift([0,.7,0])
 f=(lambda z:(z-1)/10) if orthographic else (lambda z:1.1-1.1/z)
 curve=axes2.plot(f,x_range=[1,11,.15],color=GREEN if orthographic else BLUE)
 g=VGroup(axes2,curve,txt('뷰 깊이 z',24).next_to(axes2.x_axis,DOWN),txt('저장 깊이 d',24).next_to(axes2.y_axis,UP))
 # Keep the numeric graph true while connecting its samples to view-space
 # objects below it. Only the active sample has a label near the curve.
 for z in [1,2,4,6,11]:
  p=axes2.c2p(z,f(z));g.add(Dot(p,color=RED if z==point_z else MUTED,radius=.07))
  if z in [1,11]:g.add(txt(f'{z}→{f(z):.0f}',23,MUTED).next_to(p,LEFT if z==1 else RIGHT,buff=.15))
 active=axes2.c2p(point_z,f(point_z))
 g.add(txt(f'z{point_z} → d{f(point_z):.4g}',27,RED).next_to(active,UP,buff=.2))
 ruler=VGroup(cam().scale(.2).shift([-2.9,-1.4,0]))
 def rp(z):return np.array([-2.3+(z-1)*.4,-1.35,(z-1)*.06])
 for z in [2,4,6]:
  pos=rp(z);ruler.add(box(pos,[.38,.42,.26],RED if z==point_z else PALE),label(pos,f'z{z}',INK,23,(0,-.48,0)))
 ruler.add(edge(rp(1),rp(11),BLUE,2,dashed=True),txt('카메라',20,BLUE).move_to([-2.9,-1.85,0]))
 g.add(ruler)
 return g

def alternate(i):
 if i>=6:return VGroup(depth_chart(True,6),txt('직교[0,1] / w1',25,GREEN).shift([0,2.4,0]))
 g=VGroup(box([-1.7,0,0],[1.4,3.0,.2],GREEN),box([1.7,0,0],[1.4,3.0,.2],BLUE),txt('[-1,1]',27,GREEN).move_to([-1.7,2,0]),txt('[0,1]',27,BLUE).move_to([1.7,2,0]))
 for x,minv,maxv,d in [(-1.7,-1,1,.65),(1.7,0,1,.825)]:
  y=-1.5+3*(d-minv)/(maxv-minv);g.add(Dot([x,y+.08,0],color=GOLD if i in [0,1,2] and x<0 or i>=3 and x>0 else WHITE,radius=.12),txt(str(d),27,INK).next_to([x,y+.08,0],RIGHT,buff=.65))
 g.add(Arrow([-1.,.3,0],[1.,.3,0],color=GOLD,buff=0))
 if i>=4:g.add(txt('RH 열벡터 / 앞쪽−z / w=−z',23).move_to([0,-2.2,0]))
 return g

def viewport(i,exercise=False):
 # Actual pixel mapping laid out on a projected screen with depth-bearing rim.
 g=VGroup(box([0,0,-.16],[6.6,3.71,.32],PALE))
 rect=np.array([[-2.4,-1.1,0],[1.6,-1.1,0],[1.6,1.15,0],[-2.4,1.15,0]])
 g.add(face(rect,GREEN,.45),label([-2.4,1.15,0],'(100,50)',BLUE,23,(-.18,.4,0)),label([1.6,-1.1,0],'800×450',BLUE,24,(0,-.35,0)))
 x700=0.6;y175=.525
 if exercise and i in [0,1,2,3]:x700=.1
 if exercise and i==4:g=VGroup(box([0,0,-.16],[6.6,3.71,.32],PALE),face(rect,GREEN,.45),label([-2.4,1.15,0],'origin(0,0)',BLUE,23,(0,.45,0)))
 if exercise and i==5:
  g=VGroup(box([0,0,-.16],[6.6,3.71,.32],PALE),txt('전체1920×1080',26).move_to([0,2.3,0]));x700=1.65;y175=.825
 g.add(Dot(point([x700,y175,.07]),color=RED,radius=.1))
 value='(600,175)' if exercise and i<=3 else '(600,125)' if exercise and i==4 else '(1440,300)' if exercise and i==5 else '(700,175)'
 g.add(label([x700,y175,.08],value,RED,26,(.5,.4,0)),edge([x700,-1.1,.02],[x700,y175,.02],RED,1.5,dashed=True),edge([-2.4,y175,.02],[x700,y175,.02],RED,1.5,dashed=True))
 if i<2 and not exercise:g.add(txt('NDC (0.5,4/9)',24,BLUE).move_to([0,-2.0,0]))
 if not exercise or i<5:g.add(txt('출력 창 확대',23,MUTED).move_to([0,2.4,0]))
 return g

def interpolation(i):
 # Equal screen weights correspond to t0.2 on the defined perspective edge.
 a=np.array([0.,0.,1.]);b=np.array([4.,0.,4.]);p=a+.2*(b-a)
 s=.4;a=a*s;b=b*s;p=p*s
 g=VGroup(face([[-.12,-.22,.4],[.52,-.22,.4],[.52,.22,.4],[-.12,.22,.4]],PALE,.3),cam().scale(.28),edge(a,b,BLUE,4),dot(a,GREEN),dot(b,RED),label(a,'w1 / u0',GREEN,27,(-.2,.6,0)),label(b,'w4 / u1',RED,27,(.2,.6,0)))
 q=np.array([.2,0,.4]);g.add(dot(q,GOLD),label(q,'화면50%',GOLD,26,(-.1,-.65,0)))
 if i>=2:g.add(dot(p,RED),edge([0,0,0],p,GOLD,2,dashed=True),label(p,'공간20% / u0.2',RED,27,(.45,.9,0)))
 if i>=3:g.add(edge([0,0,0],b,RULE,1,dashed=True),edge([0,0,0],a,RULE,1,dashed=True))
 return g

def plane_scale(i):
 # Explicit constant shape: both ray intersection and film bounds scale.
 g=VGroup(cam(),edge([0,0,0],[1.8,0,3.6],GOLD,3,dashed=True))
 for d,c in [(1,GREEN),(2,BLUE)]:
  if d==2 and i==0:continue
  g.add(box([0,0,d],[2*d,1.125*d,.06],c).set_fill(opacity=.18),dot([.5*d,0,d],RED),label([0,1.0*d,d],f'd{d} / 폭{2*d}',c,26))
 g.add(label([0,-1.1,2],'점과 창이 함께 커짐',BLUE,24))
 return g

def light_tangent(i):
 if i<5:return compact_pipeline(min(5,i+3))
 if i==5:
  g=frustum(80,.8,3.4,show_labels=False);g.add(box([.4,.2,2],[1.1,.9,.7],GREEN),label([0,0,0],'광원',GOLD,28,(-.55,-.5,0)),label([0,0,3.4],'광원 기준 보기',BLUE,25,(.5,.4,0)));return g
 # Surface lies in xz, so its normal points in the +y direction.
 g=VGroup(face([[-1.5,0,-1],[1.5,0,-1],[1.5,0,1],[-1.5,0,1]],GREEN,.7),axes([0,.04,0],1.5,('T 접선','N 법선','B 종접선')))
 return g

def raw_diagram(mode,i):
 if mode=='overview':return pipeline([0,2,4,5][min(i,3)])
 if mode=='conventions':
  g=VGroup(cam(),axes(length=1.8),box([2.8,0,1.8],[2.6,1.55,.2],PALE),label([2.8,-1.1,1.8],'화면은 아래+y',BLUE,25))
  if i==0:g.add(edge([0,0,0],[0,0,1.8],GOLD,4).add_tip(tip_length=.12))
  if i==3:g.add(edge([2.8,.6,1.95],[2.8,-.6,1.95],RED,4).add_tip(tip_length=.12))
  if i in [1,2,4,5]:g.add(label([1.3,2,0],['','p × M','0 ≤ z_clip ≤ w','','약속을 각각 기록','한 점을 끝까지 추적'][i],BLUE,26))
  return g
 if mode=='model':return model(i)
 if mode=='view':return view(i)
 if mode=='homogeneous':return homogeneous(i)
 if mode=='projection':return projection(i)
 if mode=='clip':return clip(i)
 if mode=='near':return near(i)
 if mode=='alternate':return alternate(i)
 if mode=='viewport':return viewport(i)
 if mode=='depth':return depth_chart(i==4,6 if i in [3,4] else 4)
 if mode=='interpolation':return interpolation(i)
 if mode=='plane-scale':return plane_scale(i)
 if mode=='pipeline':return light_tangent(i)
 if mode=='exercise':return viewport(i,True)
 if mode=='summary':return pipeline([2,3,5,4,0][min(i,4)])
 raise ValueError(mode)

LAYOUT={}
def diagram(mode,i,count):
 phase=0 if mode!='pipeline' or i<5 else i
 key=(mode,count,phase)
 if key not in LAYOUT:
  indices=range(count) if mode!='pipeline' else range(5) if phase==0 else [i]
  group=VGroup(*[raw_diagram(mode,j) for j in indices])
  width,height,center=(12,2.5,np.array([0,-.2,0])) if mode in ['overview','summary'] else (6.1,3.3,np.array([-3.28,-.28,0]))
  scale=min(width/group.width,height/group.height);LAYOUT[key]=(scale,center-group.get_center()*scale)
 scale,shift=LAYOUT[key]
 return raw_diagram(mode,i).scale(scale,about_point=ORIGIN).shift(shift)

def matrix4(values):
 cells=VGroup()
 for y,row in enumerate(values):
  for x,v in enumerate(row):cells.add(txt(str(v),25,[RED,GREEN,BLUE,GOLD][x],font='Consolas').move_to([x*.9,-y*.52,0]))
 cells.move_to(ORIGIN);left=Line(cells.get_corner(UL)+[-.18,.15,0],cells.get_corner(DL)+[-.18,-.15,0],color=INK);right=left.copy().move_to(cells.get_right()+[.23,0,0])
 return VGroup(left,cells,right)

def right_panel(scene,i):
 text=scene['formulas'][i];mode=scene['mode']
 values=None;caption=None
 if mode=='model' and i==3:values=[[1,0,0,0],[0,1,0,0],[0,0,1,0],[3,2,5,1]];caption='모델 이동 M / 행벡터'
 if mode=='projection' and i in [2,5]:values=[[1,0,0,0],[0,'16/9',0,0],[0,0,1.1,1],[0,0,-1.1,0]];caption='원근 P / n1,f11 / [0,1]'
 if mode=='alternate' and i==5:values=[[1,0,0,0],[0,'16/9',0,0],[0,0,-1.2,-2.2],[0,0,-1,0]];caption='RH 열벡터 / −z 앞 / [-1,1]'
 if values is not None:
  g=matrix4(values).move_to([3.12,-.2,0]);g.add(fit(txt(caption,23,MUTED),5.7).move_to([3.12,-1.62,0]));return g
 lines=textwrap.wrap(text,width=31,break_long_words=False,break_on_hyphens=False) or ['']
 return fit(txt('\n'.join(lines),28,BLUE),5.8 if mode not in ['overview','summary'] else 12).move_to([3.12,-.35,0] if mode not in ['overview','summary'] else [0,-1.8,0])

class CameraProjectionScene(Scene):
 slug='';sid=''
 def replace(self,old,new):
  if old:self.play(FadeOut(old),run_time=.10);self.remove(old)
  self.play(FadeIn(new,shift=.04*UP),run_time=.20);return new
 def construct(self):
  self.camera.background_color=WHITE
  d=json.loads((ROOT/f'production/batches/game-math-part2-full-series/lessons/{self.slug}.json').read_text(encoding='utf8'));s=next(x for x in d['scenes'] if x['id']==self.sid);slot=next(x for x in timing(self.slug,d)['scenes'] if x['id']==self.sid);mode=s['mode']
  episode=d.get('episodeSubtitle','렌더링3편').split(' · ')[0]
  title=fit(txt(s['title'],39),12.5).to_corner(UL,buff=.58);sub=fit(txt(f'게임수학 Part 2 / {episode} · LH 행벡터 / 앞+z / 깊이[0,1] / 화면 왼쪽 위',20,MUTED),12.5).next_to(title,DOWN,aligned_edge=LEFT,buff=.14)
  self.add(title,sub,Line([-6.5,2.32,0],[6.5,2.32,0],color=RULE,stroke_width=1))
  obj=diagram(mode,0,len(s['beats']));self.add(obj);active=formula=None
  footer=fit(txt('그림의 비스듬한 시점은 설명용 / 실제 게임의 내부 값은 추정하지 않음',21,MUTED),12.3).move_to([0,-2.25,0]);self.add(footer)
  for i,beat in enumerate(s['beats']):
   start=slot['lineStarts'][i]
   if start>self.renderer.time+1/60:self.wait(start-self.renderer.time,frozen_frame=True)
   target=diagram(mode,i,len(s['beats']))
   if i:self.play(Transform(obj,target),run_time=.65)
   else:self.play(Indicate(obj,color=GOLD,scale_factor=1.015),run_time=.55)
   wrapped='\n'.join(textwrap.wrap(beat,width=26,break_long_words=False,break_on_hyphens=False))
   active=self.replace(active,card(wrapped,width=6.15,size=25,color=GREEN if i==len(s['beats'])-1 else BLUE).move_to([3.12,1.65,0] if mode not in ['overview','summary'] else [0,1.65,0]))
   formula=self.replace(formula,right_panel(s,i))
  if slot['seconds']>self.renderer.time:self.wait(slot['seconds']-self.renderer.time,frozen_frame=True)

def make_scenes(slug,module):
 d=json.loads((ROOT/f'production/batches/game-math-part2-full-series/lessons/{slug}.json').read_text(encoding='utf8'))
 return {'Scene'+s['id']:type('Scene'+s['id'],(CameraProjectionScene,),{'slug':slug,'sid':s['id'],'__module__':module}) for s in d['scenes'] if s['kind']=='explanation'}
