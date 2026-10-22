"""Reuse all original M03 mathematical beats and timing with readable dark tokens.

No mathematical contract is changed: right handed, column vectors, R local→world.
Actual game clips are composed separately and never used as measured engine data.
"""
from pathlib import Path
import sys,os,json,re
import numpy as np
R=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(R/'manim/projects/game-math-part2-full-series'))
import lesson as base
from manim import *
BG='#090D12';FG='#F5F5EF';SECOND='#A7B0BC';RULE='#424D5A';X='#FF7785';Y='#80D3A2';Z='#78B7FF';YELLOW='#FFD773'
old_txt=base.txt
def text(s,size=28,color=None,font='Malgun Gothic'):
 s=s.replace('비행 관찰 → 방향과 자세','물체 조립 → 방향과 자세')
 colors={'#202020':FG,'#70757c':SECOND,'#2f5faa':Z,'#52704c':Y,'#a27319':YELLOW,'#b7443f':X}
 color=colors.get(str(color),color) if color is not None else FG
 if size==40:color=YELLOW
 return Text(s,font=font,font_size=size,color=color)
def card(s,width=6,size=29,color=None):
 words=base.fit(text(s,size,color),width-.35)
 face=Rectangle(width=width,height=max(.84,words.height+.3),stroke_color=RULE,stroke_width=1,fill_color=BG,fill_opacity=1)
 return VGroup(face,words)
def aircraft(matrix,origin,scale=1.2):
 # Own illustrative aircraft: pointed nose, broad swept wings, tail and upright fin.
 # A neutral recognizable shape rather than game geometry or an asserted game asset.
 hull=Sphere(radius=1,resolution=(8,12),fill_color='#D7DFEA',checkerboard_colors=['#D7DFEA','#D7DFEA'],fill_opacity=1,stroke_width=0).stretch(.15,0).stretch(.13,1).stretch(.83,2)
 wings=Polygon([-.95,0,-.18],[-.17,0,.35],[.17,0,.35],[.95,0,-.18],[.95,0,-.37],[-.95,0,-.37],fill_color='#9DB5CE',fill_opacity=1,stroke_color=FG,stroke_width=1)
 tail=Polygon([-.36,0,-.57],[0,0,-.40],[.36,0,-.57],[.36,0,-.72],[-.36,0,-.72],fill_color=Y,fill_opacity=1,stroke_width=.7)
 fin=Polygon([0,0,-.48],[0,.43,-.70],[0,0,-.78],fill_color=YELLOW,fill_opacity=1,stroke_width=1)
 cockpit=Sphere(radius=1,resolution=(6,8),fill_color='#36536E',checkerboard_colors=['#36536E','#36536E'],fill_opacity=1,stroke_width=0).stretch(.12,0).stretch(.08,1).stretch(.25,2).shift([0,.105,.28])
 obj=VGroup(hull,wings,tail,fin,cockpit);obj.apply_matrix(base.P@matrix);obj.scale(scale,about_point=ORIGIN);obj.shift(origin);return obj
base.INK=FG;base.MUTED=SECOND;base.RULE=RULE;base.RED=X;base.GREEN=Y;base.BLUE=Z;base.GOLD=YELLOW;base.PALE='#293A4A';base.WHITE=BG
base.txt=text;base.card=card;base.body=aircraft
def syntax_text(s,**kwargs):
 if kwargs.get('font')=='Consolas':
  colors={}
  for pattern,color in [(r'\breturn\b','#D9A8FA'),(r'\bVec3\b',Z),(r'\b(?:localToWorld|worldToLocal|pointToWorld|pointToLocal|transpose)\b',YELLOW),(r'\b(?:R|v|p|position)\b','#B5DBD8')]:
   for m in re.finditer(pattern,s):colors[f'[{m.start()}:{m.end()}]']=color
  if s.startswith('//'):kwargs['color']=SECOND;colors={}
  kwargs['t2c']=colors
 return Text(s,**kwargs)
base.Text=syntax_text
original_fixed=base.LectureScene.fixed
def fixed(self,*objects):
 for m in objects:
  if isinstance(m,Line) and m.width>12 and abs(m.get_center()[1]-2.63)<.01:m.shift(.4*DOWN)
 original_fixed(self,*objects)
base.LectureScene.fixed=fixed
globals().update(base.make_scenes('game-math-orientation-matrices',__name__))

def sail(matrix,origin):
 mast=Line3D([0,-1,0],[0,1.25,0],thickness=.055,color='#B8A183')
 cloth=Polygon([-.02,1.13,0],[1.12,-.55,0],[-.02,-.55,0],fill_color='#C9D7DE',fill_opacity=1,stroke_color=FG,stroke_width=1)
 boom=Line3D([0,-.6,0],[1.17,-.6,0],thickness=.045,color='#B8A183')
 obj=VGroup(mast,cloth,boom);obj.apply_matrix(base.P@matrix);obj.shift(origin);return obj
def hook(matrix,origin):
 # Opening is +logical Z, matching the explicitly chosen front direction.
 points=[np.array([0,.65*np.sin(a)+.35,.65*np.cos(a)]) for a in np.linspace(-.1*PI,1.15*PI,22)]
 points+=[np.array([0,-1.0,points[-1][2]]),np.array([0,-1.0,.05])]
 obj=VGroup(*[Line3D(a,b,thickness=.10,color='#C9D7DE') for a,b in zip(points,points[1:])]);obj.apply_matrix(base.P@matrix);obj.shift(origin);return obj
def assembly(matrix,origin):
 obj=VGroup()
 for x in [-.56,0,.56]:
  barrel=Cylinder(radius=.23,height=.9,direction=np.array([0,1,0]),resolution=(8,12),fill_color='#B58A5A',checkerboard_colors=['#B58A5A','#B58A5A'],fill_opacity=1,stroke_width=.5).shift([x,0,0]);obj.add(barrel)
 baseboard=Cube(side_length=1,fill_color='#778B9E',fill_opacity=1,stroke_width=.5).stretch(1.75,0).stretch(.12,1).stretch(.62,2).shift([0,-.53,0]);obj.add(baseboard)
 obj.apply_matrix(base.P@matrix);obj.shift(origin);return obj
def rig(matrix,origin,kind='aircraft'):
 obj={'sail':sail,'hook':hook,'assembly':assembly,'aircraft':aircraft}[kind](matrix,origin)
 axes=VGroup(*[base.arrow(origin,origin+2.05*base.P@matrix[:,i],c,5) for i,c in enumerate([X,Y,Z])])
 return VGroup(obj,axes)

class Demonstration(ThreeDScene):
 sid=''
 def construct(self):
  self.camera.background_color=BG
  timeline=json.loads(Path(os.environ['MATH_RENDER_TIMING']).read_text(encoding='utf8'))
  slot=next(x for x in timeline['scenes'] if x['id']==self.sid)
  # Exact Korean terms are fixed to the screen, axes are projected 3D geometry.
  titles={'02':'위치와 자세는 서로 다른 정보','05':'물체에 붙인 위쪽과 고정된 위쪽','08':'로컬의 앞을 월드에서 표현하기','11':'물체 고정 · 카메라만 이동','14':'투영된 폭 ≠ 실제 길이','17':'모습과 수학 조건을 함께 검사','20':'같은 입력 · 다른 기준','23':'위치 + 앞쪽 + 위쪽'}
  beats={
   '02':['잡기 → 들어 올리기 → 세우기 → 붙이기','위치: 어디에 놓았는가','자세: 어느 쪽으로 놓였는가','한 방향을 고정해도 비틀 수 있다','앞쪽만 같아도 위쪽은 다르다','이 차이를 세 축으로 기록'],
   '05':['선택 부품만 회전','물체의 축은 물체와 함께 회전','로컬 y: 물체에 붙인 위쪽','월드 y: 고정된 기준','R: 로컬 축 → 월드 성분','게임 내부 값이 아닌 설명용 좌표'],
   '08':['고리를 세워 붙이는 실제 동작','설명에서는 열린 쪽을 앞이라고 정함','월드 기준은 고정','로컬 앞 / 월드 앞 비교','v_world = R v_local','역방향: v_local = Rᵀ v_world'],
   '11':['물체 고정 · 시점만 변경','정면과 위에서 본 같은 물체','월드 자세와 카메라 상대 자세','관찰 위치가 바뀌면 투영도 변경','입력 공간 → 출력 공간','여러 변환은 행렬 곱으로 연결'],
   '14':['같은 돛을 다른 각도에서 관찰','보이는 폭 변화는 크기 변환의 증거가 아님','거리·원근도 화면 크기에 영향','3D 길이 / 화면의 픽셀 길이','||R v|| = ||v||','투영 길이는 회전 행렬의 축 길이가 아님'],
   '17':['부드러운 회전만으로 수학 조건은 알 수 없음','화면의 모습 / 계산된 수치','세 축 길이 = 1','서로 다른 축의 내적 = 0','실제 계산값을 오른쪽에서 확인','이제 저장과 코드로 연결'],
   '20':['조립 부품의 로컬 왼쪽','화면 왼쪽과 같은가?','같은 물체 · 두 기준 비교','변수에 좌표 공간을 명시','localLeft → R localLeft','다음: 행렬 성분을 섞으면?'],
   '23':['조립 물체의 상태를 기록','위치 / 앞쪽 / 위쪽','카메라 기준도 따로 구분','세 축을 열에 기록','설명용 계산과 실제 게임을 구별','다음: 오일러 각과 회전 순서']}
  title=text(titles[self.sid],38,YELLOW).to_corner(UL,buff=.5)
  kind=text('우리 구현 · 오른손 / 열벡터',20,SECOND).to_corner(UR,buff=.5)
  self.add_fixed_in_frame_mobjects(title,kind)
  self.set_camera_orientation(phi=64*DEGREES,theta=-48*DEGREES,zoom=.85)
  origin=np.array([-2.2,-2.2,-.2]);matrix=np.eye(3)
  shape='sail' if self.sid in ['02','14','23'] else 'hook' if self.sid=='08' else 'assembly'
  obj=rig(matrix,origin,shape)
  world=VGroup(*[DashedLine(origin-2.4*base.P[:,i],origin+2.7*base.P[:,i],color=RULE,stroke_width=2) for i in range(3)])
  self.add(world,obj)
  legend=VGroup(text('X',27,X),text('Y ↑',27,Y),text('Z 앞',27,Z)).arrange(RIGHT,buff=.4).move_to([-3.3,-2.3,0]);self.add_fixed_in_frame_mobjects(legend)
  active=None;metric=None
  for i,ts in enumerate(slot['lineStarts']):
   if ts>self.renderer.time+1/60:self.wait(ts-self.renderer.time)
   phrase=beats[self.sid][min(i,5)]
   if active:self.remove(active)
   active=base.fit(text(phrase,29,FG),6.5).move_to([3.0,1.5,0]);self.add_fixed_in_frame_mobjects(active)
   if self.sid=='02':
    if i==0:self.play(obj.animate.shift(.8*UP),run_time=1.5)
    if i==1:self.play(obj.animate.shift(.8*DOWN),run_time=1.5)
    if i in [2,3,4]:self.play(Rotate(obj,angle=(-1 if i==3 else 1)*PI/4,axis=base.P[:,2],about_point=origin),run_time=1.3)
   elif self.sid in ['05','08','23']:
    rotate=(self.sid=='05' and i in [1,3]) or (self.sid=='08' and i==1) or (self.sid=='23' and i==2)
    if rotate:self.play(Rotate(obj,angle=-PI/6 if self.sid=='08' else PI/6,axis=base.P[:,2 if self.sid=='05' else 1],about_point=origin),run_time=1.3)
    if i==4:
     if metric:self.remove(metric)
     metric=base.fit(text('R = [ x_world  y_world  z_world ]',27,Z,font='Consolas'),6.4).move_to([3,-.2,0]);self.add_fixed_in_frame_mobjects(metric)
   elif self.sid=='11':
    if i==1:self.move_camera(phi=20*DEGREES,theta=-48*DEGREES,run_time=2)
    if i==3:self.move_camera(phi=64*DEGREES,theta=-10*DEGREES,run_time=2)
   elif self.sid=='14':
    if i in [0,1,3]:self.play(Rotate(obj,angle=PI/6,axis=base.P[:,1],about_point=origin),run_time=2)
    if i==2:self.move_camera(zoom=.65,run_time=1.5)
    if i==4:
     metric=text('단위 X축 길이: 1.00 → 1.00',28,Y).move_to([3,0,0]);self.add_fixed_in_frame_mobjects(metric)
   elif self.sid=='17':
    # A rigid rotation must not linearly morph vertex coordinates or shorten axes.
    a=(i+1)*PI/7;matrix=base.rz(a)@base.ry(.3)
    if i==0:self.play(Rotate(obj,angle=.3,axis=base.P[:,1],about_point=origin),run_time=.4)
    self.play(Rotate(obj,angle=PI/7,axis=base.P[:,2],about_point=origin),run_time=.7 if i==0 else 1.1)
    if metric:self.remove(metric)
    vals=np.linalg.norm(matrix,axis=0);dot=matrix[:,0]@matrix[:,1]
    if abs(dot)<.0000005:dot=0.
    metric=VGroup(text('자체 구현의 실제 계산값',23,SECOND),text('축 길이  '+ ' / '.join(f'{x:.2f}' for x in vals),27,Y),text(f'x · y = {dot:+.6f}',27,Z,font='Consolas')).arrange(DOWN,aligned_edge=LEFT,buff=.35).move_to([3,-.1,0]);self.add_fixed_in_frame_mobjects(metric)
   elif self.sid=='20':
    if i==0:self.play(Rotate(obj,angle=PI/2,axis=base.P[:,1],about_point=origin),run_time=1.5)
    if i==2:
     vector=base.arrow(origin,origin+base.P@np.array([-2.,0,0]),YELLOW,6);local=base.arrow(origin,origin+base.P@np.array([0,0,2.]),Z,6);self.play(Create(vector),Create(local),run_time=1.5)
    if i==3:
     metric=VGroup(text('worldLeft = (-1,0,0)',25,YELLOW,font='Consolas'),text('R localLeft = (0,0,1)',25,Z,font='Consolas')).arrange(DOWN,buff=.4).move_to([3,-.3,0]);self.add_fixed_in_frame_mobjects(metric)
  if slot['seconds']>self.renderer.time:self.wait(slot['seconds']-self.renderer.time)

for sid in ['02','05','08','11','14','17','20','23']:
 globals()['Scene'+sid]=type('Scene'+sid,(Demonstration,),{'sid':sid,'__module__':__name__})

class SynchronizedDemonstration(ThreeDScene):
 """The visible action has its own cue; paragraph boundaries are not action cues."""
 sid=''
 def construct(self):
  self.camera.background_color=BG
  slot=next(x for x in json.loads(Path(os.environ['MATH_RENDER_TIMING']).read_text(encoding='utf8'))['scenes'] if x['id']==self.sid)
  self.set_camera_orientation(phi=64*DEGREES,theta=-48*DEGREES,zoom=.85)
  titles={'02':'위치와 자세는 서로 다른 정보','05':'물체에 붙인 위쪽과 고정된 위쪽','08':'로컬의 앞을 월드에서 표현하기','11':'물체 고정 · 카메라만 이동'}
  phrases={
   '02':['물체를 잡고 → 돌리고 → 배치','위치: 어디에 놓았는가','자세: 어느 쪽으로 놓였는가','앞 방향이 같아도 비틀림은 다르다','방향 하나 < 물체 전체의 자세','세 축으로 자세를 기록'],
   '05':['선택한 부품과 고정된 주변','실선: 물체의 축 / 점선: 고정 기준','물체의 위쪽도 함께 회전','월드 위쪽은 고정된 기준','R: 로컬 축 → 월드 성분','자체 설명용 모형과 좌표'],
   '08':['고리를 세워 붙이는 실제 동작','열린 쪽 = 이 모형에서 정한 앞','월드 기준은 고정','물체의 앞 / 월드의 앞','v_world = R v_local','v_local = Rᵀ v_world'],
   '11':['물체 고정 · 시점만 변경','앞과 위에서 본 같은 물체','월드 자세 / 카메라 상대 자세','같은 물체도 투영된 모습은 변화','입력 공간 → 출력 공간','여러 변환은 행렬 곱으로 연결']}
  self.add_fixed_in_frame_mobjects(text(titles[self.sid],38,YELLOW).to_corner(UL,buff=.5),text('우리 구현 · 오른손 / 열벡터',20,SECOND).to_corner(UR,buff=.5))
  origin=np.array([-2.2,-2.2,-.2]);shape={'02':'sail','05':'assembly','08':'hook','11':'assembly'}[self.sid]
  initial=base.rx(PI/2) if self.sid in ['02','08'] else np.eye(3)
  obj=rig(initial,origin,shape)
  world=VGroup(*[DashedLine(origin-2.4*base.P[:,i],origin+2.7*base.P[:,i],color=RULE,stroke_width=2) for i in range(3)])
  self.add(world,obj)
  self.add_fixed_in_frame_mobjects(VGroup(text('X',27,X),text('Y ↑',27,Y),text('Z 앞',27,Z)).arrange(RIGHT,buff=.4).move_to([-3.3,-2.3,0]))
  active=None;metric=None
  events=[(t,'text',i) for i,t in enumerate(slot['lineStarts'])]
  # Times were read from the native footage. The diagram is an analogy, not tracked engine telemetry.
  actions={
   '02':[(6.5,'lift',.8),(9.5,'upright',1.3),(13.5,'place',.8),(16.0,'twist',1.3),(21.0,'untwist',1.3)],
   '05':[(4.8,'tilt',1.3),(8.7,'tilt',1.1)],
   '08':[(2.5,'upright',1.3),(4.8,'heading',1.2)],
   '11':[(2.0,'view-top',1.0),(14.0,'view-side',1.4)]}
  events += [(t,action,d) for t,action,d in actions[self.sid]]
  for t,kind,value in sorted(events,key=lambda e:e[0]):
   if t>self.renderer.time:self.wait(t-self.renderer.time)
   if kind=='text':
    if active:self.remove(active)
    active=base.fit(text(phrases[self.sid][value],29,FG),6.5).move_to([3,1.5,0]);self.add_fixed_in_frame_mobjects(active)
    if value==4 and self.sid in ['05','08']:
     metric=base.fit(text('R = [ x_world  y_world  z_world ]',27,Z,font='Consolas'),6.4).move_to([3,-.2,0]);self.add_fixed_in_frame_mobjects(metric)
   elif kind=='lift':self.play(obj.animate.shift(.5*base.P[:,1]),run_time=value)
   elif kind=='upright':
    pivot=origin+.5*base.P[:,1] if self.sid=='02' else origin
    self.play(Rotate(obj,angle=-PI/2,axis=base.P[:,0],about_point=pivot),run_time=value,rate_func=smooth)
   elif kind=='place':self.play(obj.animate.shift(-.5*base.P[:,1]),run_time=value)
   elif kind in ['twist','untwist']:self.play(Rotate(obj,angle=(1 if kind=='twist' else -1)*PI/4,axis=base.P[:,2],about_point=origin),run_time=value)
   elif kind=='tilt':self.play(Rotate(obj,angle=PI/6,axis=base.P[:,2],about_point=origin),run_time=value)
   elif kind=='heading':self.play(Rotate(obj,angle=-PI/6,axis=base.P[:,1],about_point=origin),run_time=value)
   elif kind=='view-top':self.move_camera(phi=20*DEGREES,theta=-48*DEGREES,run_time=value)
   elif kind=='view-side':self.move_camera(phi=64*DEGREES,theta=-10*DEGREES,run_time=value)
  if slot['seconds']>self.renderer.time:self.wait(slot['seconds']-self.renderer.time)

for sid in ['02','05','08','11']:
 globals()['Scene'+sid]=type('Scene'+sid,(SynchronizedDemonstration,),{'sid':sid,'__module__':__name__})
