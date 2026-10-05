"""Independent original lecture diagrams. Geometry is explanation, not gameplay.

Semantic vectors are right-handed, column-vector, y-up. P is a proper rotation
of those logical coordinates into Manim's z-up drawing coordinates (det P=+1).
The camera projection is presentation only and never changes the math contract.
"""
from pathlib import Path
import os,json,math
import numpy as np
from manim import *
ROOT=Path(__file__).resolve().parents[3]
INK='#202020';MUTED='#70757c';RULE='#cbd0d6';RED='#b7443f';GREEN='#52704c';BLUE='#2f5faa';GOLD='#a27319';PALE='#e7eef4'
P=np.array([[1,0,0],[0,0,-1],[0,1,0]],dtype=float)
def txt(s,size=28,color=INK,font='Malgun Gothic'):
 return Text(s,font=font,font_size=size,color=color)
def fit(m,width):
 if m.width>width:m.scale(width/m.width)
 return m
def card(s,width=6,size=29,color=BLUE):
 words=fit(txt(s,size,color),width-.4)
 face=Rectangle(width=width,height=max(.84,words.height+.3),stroke_color=RULE,stroke_width=1,fill_color=WHITE,fill_opacity=1)
 shadow=face.copy().set_stroke(width=0).set_fill(PALE,opacity=.9).shift(.085*RIGHT+.085*DOWN)
 return VGroup(shadow,face,words)
def rz(a):
 c,s=np.cos(a),np.sin(a);return np.array([[c,-s,0],[s,c,0],[0,0,1]])
def ry(a):
 c,s=np.cos(a),np.sin(a);return np.array([[c,0,s],[0,1,0],[-s,0,c]])
def rx(a):
 c,s=np.cos(a),np.sin(a);return np.array([[1,0,0],[0,c,-s],[0,s,c]])
def arrow(start,end,color,width=4):
 if np.linalg.norm(end-start)<1e-5:return Dot3D(start,radius=.035,color=color,resolution=(4,4))
 return Line(start,end,color=color,stroke_width=width).add_tip(tip_length=.15)
def logical_box(dim,center,color):
 b=Cube(side_length=1,fill_opacity=.75,fill_color=color,stroke_color=RULE,stroke_width=.6)
 for i,d in enumerate(dim):b.stretch(d,i)
 return b.shift(center)
def body(R,origin,scale=1.2):
 obj=VGroup(logical_box([.22,.15,1.55],[0,0,0],BLUE),logical_box([1.65,.09,.34],[0,0,.08],PALE),logical_box([.65,.08,.23],[0,0,-.55],GREEN))
 obj.apply_matrix(P@R);obj.scale(scale,about_point=ORIGIN);obj.shift(origin);return obj
def basis(R,origin,scale=2.05,with_body=True):
 axes=VGroup(*[arrow(origin,origin+scale*(P@R[:,i]),c) for i,c in enumerate([RED,GREEN,BLUE])])
 return VGroup(body(R,origin,1.25),axes) if with_body else axes
def numeric_matrix(values,width=4.6):
 cells=VGroup();cols=[VGroup(),VGroup(),VGroup()]
 decimal_cells=any(isinstance(v,(float,np.floating)) and not float(v).is_integer() for row in values for v in row)
 spacing=max(.92,max(txt(str(v),36,font='Consolas').width for row in values for v in row)+.3) if decimal_cells else .92
 for i,row in enumerate(values):
  for j,value in enumerate(row):
   v=txt(str(value),36,[RED,GREEN,BLUE][j],font='Consolas').move_to([j*spacing,-i*.67,0]);cells.add(v);cols[j].add(v)
 cells.move_to(ORIGIN)
 left=Line(cells.get_corner(UL)+[-.24,.15,0],cells.get_corner(DL)+[-.24,-.15,0],color=INK)
 right=left.copy().move_to(cells.get_right()+[.28,0,0])
 return VGroup(left,cells,right),cols
def timing(slug,data):
 if os.environ.get('MATH_RENDER_TIMING'):return json.loads(Path(os.environ['MATH_RENDER_TIMING']).read_text(encoding='utf8'))
 if os.environ.get('MATH_PREVIEW')=='1':return {'scenes':[{'id':s['id'],'seconds':len(s['ko'])*2.2+1,'voiceSeconds':len(s['ko'])*2.2,'lineStarts':[i*2.2 for i in range(len(s['ko']))]} for s in data['scenes']]}
 return json.loads((ROOT/f'projects/{slug}/production/timeline.json').read_text(encoding='utf8'))

class LectureScene(ThreeDScene):
 slug='';sid=''
 def fixed(self,*m):self.add_fixed_in_frame_mobjects(*m)
 def replace_fixed(self,old,new):
  self.fixed(new)
  if old:self.play(FadeOut(old),FadeIn(new,shift=.07*UP),run_time=.35);self.remove(old)
  else:self.play(FadeIn(new,shift=.07*UP),run_time=.35)
  return new
 def construct(self):
  self.camera.background_color=WHITE
  data=json.loads((ROOT/f'production/batches/game-math-part2-full-series/lessons/{self.slug}.json').read_text(encoding='utf8'))
  s=next(s for s in data['scenes'] if s['id']==self.sid);slot=next(x for x in timing(self.slug,data)['scenes'] if x['id']==self.sid);mode=s['mode']
  title=fit(txt(s['title'],40),12.65).to_corner(UL,buff=.6)
  sub=fit(txt(f'게임수학 Part 2 / 3D 회전 {data["part"]}편  ·  오른손 / 열벡터 / R: 로컬 → 월드',20,MUTED),12.65).next_to(title,DOWN,aligned_edge=LEFT,buff=.14)
  self.fixed(title,sub,Line([-6.5,2.63,0],[6.5,2.63,0],color=RULE,stroke_width=1))
  self.set_camera_orientation(phi=64*DEGREES,theta=-48*DEGREES,zoom=.85)
  origin=np.array([-2.45,-2.45,-.28]);R=rz(PI/2) if mode in ['contract','dcm','inverse','practice'] else np.eye(3)
  obj=None;matrix=None;matrix_cols=[];special=None;active=None;note=None
  flat=mode in ['overview','storage','code','composition','summary']
  if not flat:
   world=VGroup(*[DashedLine(origin-2.1*P[:,i],origin+2.25*P[:,i],color=RULE,stroke_width=1.5) for i in range(3)])
   obj=basis(R,origin);self.add(world,obj)
   legend=VGroup(txt('x',23,RED),txt('y ↑',23,GREEN),txt('z 앞',23,BLUE)).arrange(RIGHT,buff=.55).move_to([-3.35,-2.15,0]);self.fixed(legend)
  if 'matrix' in s:
   matrix,matrix_cols=numeric_matrix(s['matrix']);matrix.move_to([3.12,-.1,0]);self.fixed(matrix)
  if mode=='overview':
   labels=['방향과 자세','세 축과 행렬','좌표 변환','검사와 실습'];flow=VGroup(*[card(v,width=2.9,size=28,color=GREEN if i==3 else BLUE) for i,v in enumerate(labels)]).arrange(RIGHT,buff=.25).move_to([0,.05,0]);self.fixed(flow)
   arrows=VGroup(*[Arrow(flow[i].get_right(),flow[i+1].get_left(),buff=.03,color=MUTED,stroke_width=2) for i in range(3)]);self.fixed(arrows);special=flow
  elif mode=='storage':
   a=VGroup(*[card(v,width=3.75,size=31,color=c) for v,c in [('Matrix / 36 B',BLUE),('Euler / 12 B',GREEN),('Quaternion / 16 B',GOLD)]]).arrange(RIGHT,buff=.4).move_to([0,.25,0]);self.fixed(a);special=a
   self.fixed(txt('float32 성분만 계산 · 정렬과 메타데이터 제외',25,MUTED).move_to([0,-1.0,0]))
  elif mode=='code':
   code=VGroup(*[Text(line,font='Consolas',font_size=24,color=INK,t2c={'return':GREEN,'Vec3':BLUE,'transpose':GOLD,'position':RED}) for line in s['code']]).arrange(DOWN,aligned_edge=LEFT,buff=.3);fit(code,12.2);code.move_to([0,-.45,0]);self.fixed(code);special=code
  elif mode=='composition':
   panels=VGroup(*[card(v,width=3.7,size=28) for v in ['자식 공간','부모 공간','월드 공간']]).arrange(RIGHT,buff=.52).move_to([0,.3,0]);self.fixed(panels)
   arrows=VGroup(Arrow(panels[0].get_right(),panels[1].get_left(),buff=.02,color=GREEN),Arrow(panels[1].get_right(),panels[2].get_left(),buff=.02,color=BLUE));self.fixed(arrows)
   labels=VGroup(txt('B',30,GREEN).next_to(arrows[0],UP),txt('A',30,BLUE).next_to(arrows[1],UP));self.fixed(labels);special=panels
  elif mode=='summary':
   special=VGroup(*[card(v,width=10.3,size=31,color=GREEN) for v in ['방향과 전체 자세를 구분','세 로컬 축을 같은 월드 기준으로 기록','공간·벡터 약속·정규직교·행렬식 확인']]).arrange(DOWN,buff=.28).move_to([0,-.4,0]);self.fixed(special)
  elif mode in ['valid','invalid','creep','lerp']:
   values={'valid':[[1,0,0],[0,1,0],[0,0,1]],'invalid':[[2,0,0],[0,1,0],[0,0,1]],'creep':[[1.07,.08,0],[0,.98,.05],[0,0,1]],'lerp':[[1,0,0],[0,1,0],[0,0,1]]}[mode]
   matrix,matrix_cols=numeric_matrix(values);matrix.move_to([3.12,-.1,0]);self.fixed(matrix)
   if mode=='creep':
    self.remove(obj);obj=basis(np.array(values),origin);self.add(obj)
    self.fixed(txt('오차를 크게 그린 개념도',20,MUTED).move_to([-3.35,-2.55,0]))
  elif mode=='dcm':
   self.fixed(txt('Rᵢⱼ = 월드 축ᵢ · 로컬 축ⱼ',25,MUTED).move_to([3.12,-1.6,0]))
  elif mode=='inverse':
   v=np.array([-1,2,0.]);special=arrow(origin,origin+.75*P@v,GOLD,5);self.add(special)
  initial_time=self.renderer.time
  for i,beat in enumerate(s['beats']):
   ts=slot['lineStarts'][min(i,len(slot['lineStarts'])-1)]
   if ts>self.renderer.time+1/60:self.wait(ts-self.renderer.time,frozen_frame=True)
   pos=[0,1.65,0] if flat else [3.12,1.58,0]
   active=self.replace_fixed(active,card(beat,width=12.0 if flat else 6.0,size=28,color=GREEN if i==len(s['beats'])-1 else BLUE).move_to(pos))
   if mode=='overview':self.play(Indicate(special[min(i,3)],color=GREEN),run_time=.55)
   elif mode=='direction':
    if i in [0,1]:self.play(Rotate(obj,angle=PI/3,axis=P[:,2],about_point=origin),run_time=1.05)
    if i==2:self.play(Indicate(obj[1][2],color=GOLD),run_time=.7)
    if i==3:
     other=basis(rz(PI/2),origin+[0,0,1.7],scale=1.1);self.play(FadeIn(other),run_time=.65)
   elif mode=='basis':
    if i==1:self.play(Rotate(obj,angle=PI/5,axis=P[:,1],about_point=origin),run_time=.8)
    if i==2:self.play(Indicate(obj[1],color=GOLD),run_time=.7)
    if i==3:self.play(Rotate(obj,angle=PI/4,axis=P[:,2],about_point=origin),run_time=.9)
   elif mode=='contract' and i==2:self.play(*[Indicate(col,color=c) for col,c in zip(matrix_cols,[RED,GREEN,BLUE])],run_time=.8)
   elif mode=='matrix':
    if i==0:self.play(Rotate(obj,angle=PI/2,axis=P[:,2],about_point=origin),run_time=1.4)
    if i in [1,2,3]:self.play(Indicate(matrix_cols[i-1],color=GOLD),run_time=.65)
    if i==4:
     a=origin+P@np.array([0,1.5,0]);b=origin+P@np.array([-.75,1.5,0]);self.play(Create(arrow(origin,a,RED,5)),Create(arrow(a,b,GREEN,5)),run_time=.9)
    if i==5:self.play(Create(arrow(origin,origin+.75*P@np.array([-1,2,0.]),GOLD,5)),run_time=.8)
   elif mode=='inverse':
    if i==2:self.play(Indicate(matrix,color=GREEN),run_time=.65)
    if i==3:
     note=self.replace_fixed(note,txt('(-1,2,0) → (2,1,0)',26,GOLD).move_to([3.12,-1.95,0]))
    if i==5:note=self.replace_fixed(note,txt('점과 방향벡터: 이동 처리 구분',24,GREEN).move_to([3.12,-1.95,0]))
   elif mode=='dcm':
    if i==2:self.play(Indicate(matrix_cols[0],color=GOLD),run_time=.65)
    if i==4:self.play(Indicate(obj[1][0],color=GOLD),Indicate(matrix_cols[0],color=GOLD),run_time=.75)
   elif mode=='composition':
    if i in [0,1,2]:self.play(Indicate(special[i],color=GREEN),run_time=.6)
    if i==3:note=self.replace_fixed(note,txt('A B v = A(Bv)    ·    오른쪽부터 적용',29,GREEN).move_to([0,-1.3,0]))
   elif mode=='valid':
    if i==1:self.play(Indicate(obj[1],color=GOLD),run_time=.7)
    if i==2:note=self.replace_fixed(note,txt('RᵀR = I',30,GREEN).move_to([3.12,-1.95,0]))
    if i==3:note=self.replace_fixed(note,txt('RᵀR = I   +   det(R) = +1',27,GREEN).move_to([3.12,-1.95,0]))
   elif mode=='invalid':
    values=[[2,0,0],[0,1,0],[0,0,1]] if i==0 else [[-1,0,0],[0,1,0],[0,0,1]] if i<4 else [[-1,0,0],[0,-1,0],[0,0,1]]
    if i in [0,1,4]:
     target=basis(np.array(values),origin);self.play(Transform(obj,target),run_time=.9)
     new,_=numeric_matrix(values);new.move_to(matrix);matrix=self.replace_fixed(matrix,new)
    if i in [3,4]:note=self.replace_fixed(note,txt('det = -1: 반사' if i==3 else 'det = +1: z축 180°',27,RED if i==3 else GREEN).move_to([3.12,-1.95,0]))
   elif mode=='creep':
    if i==2:self.play(Indicate(obj[1],color=GOLD),run_time=.7)
    if i==4:
     self.play(Transform(obj,basis(np.eye(3),origin)),run_time=1)
     new,_=numeric_matrix([[1,0,0],[0,1,0],[0,0,1]]);new.move_to(matrix);matrix=self.replace_fixed(matrix,new)
   elif mode=='storage':
    if i in [2,3]:self.play(Indicate(special[1 if i==2 else 2],color=GREEN),run_time=.65)
   elif mode=='code':
    if note:self.remove(note)
    note=None
    if i<4:
     rows=[special[1]] if i<2 else [special[2]] if i==2 else [special[j] for j in range(1,5)]
     highlight=SurroundingRectangle(VGroup(*rows),buff=.1,color=GREEN,stroke_width=2)
     self.fixed(highlight);self.play(Create(highlight),run_time=.4);note=highlight
   elif mode=='lerp':
    values=np.diag([-1,-1,1]) if i==1 else np.diag([0,0,1]) if i==2 else None
    if values is not None:
     self.play(Transform(obj,basis(values,origin)),run_time=1)
     new,_=numeric_matrix(values.astype(int).tolist());new.move_to(matrix);matrix=self.replace_fixed(matrix,new)
    if i==3:note=self.replace_fixed(note,txt('det = 0  ·  회전 아님',28,RED).move_to([3.12,-1.95,0]))
   elif mode=='practice':
    if i==1:self.play(Indicate(obj[1][0],color=GOLD),run_time=.7)
    if i>=3:note=self.replace_fixed(note,fit(txt(s['beats'][i],26,GOLD),5.7).move_to([3.12,-1.95,0]))
   elif mode=='summary' and i<3:self.play(Indicate(special[i],color=GREEN),run_time=.65)
  remaining=slot['seconds']-self.renderer.time
  if remaining>1/60:self.wait(remaining,frozen_frame=True)

def make_scenes(slug,module):
 data=json.loads((ROOT/f'production/batches/game-math-part2-full-series/lessons/{slug}.json').read_text(encoding='utf8'))
 return {'Scene'+s['id']:type('Scene'+s['id'],(LectureScene,),{'slug':slug,'sid':s['id'],'__module__':module}) for s in data['scenes'] if s['kind']=='explanation'}
