"""Editable spatial examples beside preserved original matrix calculations.
Actual 3D face projection and independent object/camera controls; no game telemetry.
"""
from pathlib import Path
import importlib.util,json,os
import numpy as np
from manim import *
spec=importlib.util.spec_from_file_location('camera_architecture',Path(__file__).with_name('m16-scenes.py'));v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
text=v.text;BG=v.BG;FG=v.FG;BLUE=v.BLUE;GREEN=v.GREEN;YELLOW=v.YELLOW;RED=v.RED;SECOND=v.SECOND
TITLES={'02':'고정된 기둥 · 달라지는 화면 위치','05':'같은 지붕의 점을 계속 따라가기','08':'기존 점과 새로 생긴 구조 구분','11':'큐브 이동과 카메라 이동 분리','14':'가림과 시야 경계의 차이'}
PHRASES={
'02':['기둥 고정 · 관찰 위치 변경','앞 기둥과 뒤 장치의 가림','세계 좌표 → 카메라 좌표'],
'05':['지붕의 기준점 A를 고정','새 굴뚝의 점은 다른 점','카메라만 돌려 화면 위치 비교','건물 좌표 / 카메라 좌표','물체의 같은 점 → 세계 좌표','관찰 기준으로 바꾸기','계산 예제와 게임 관측을 구분','구조 편집 / 관찰 변화'],
'08':['낮은 발판 추가 / 탑은 그대로','점의 이동과 시점 변경 구분','기존 지붕의 점 A를 유지','카메라 좌표 / 투영 매개변수','변환 → 클리핑 → 나눗셈 → 화면','세계의 위 / 카메라의 위 / 화면의 아래','관찰한 결과 → 통제된 수치 예제'],
'11':['방의 기둥과 큐브를 함께 비교','큐브를 놓는 위치와 화면 위치','화면 크기만으로 깊이를 알 수 없음','큐브와 기둥이라는 기준점','큐브 이동 → 카메라 이동','한 조건씩 고정해서 비교'],
'14':['새 지붕과 뒤쪽 건물','앞 지붕이 뒤 건물을 가림','높은 시점에서 숨은 부분 확인','시야 범위 / 앞뒤 가림 구분','건물 편집 ≠ near 평면 클리핑','게임 내부 near 값은 미확인','처음 선택한 같은 기준점 유지','다음: 남은 점을 픽셀 좌표로']}

def box(center,size,color):
 c=np.array(center,float);s=np.array(size,float)/2
 verts=[c+s*np.array(x) for x in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
 return [(np.array([verts[j] for j in idx]),col) for idx,col in [([0,1,5,4],color),([1,2,6,5],'#96A7B5'),([2,3,7,6],'#718799'),([3,0,4,7],'#536A7D'),([4,5,6,7],color)]]

class Replacement(Scene):
 sid=''
 def construct(self):
  slot=next(s for s in json.loads(Path(os.environ['MATH_RENDER_TIMING']).read_text(encoding='utf8'))['scenes'] if s['id']==self.sid)
  self.camera.background_color=BG
  self.add(v.v.base.fit(text(TITLES[self.sid],34,YELLOW),11.2).to_corner(UL,buff=.45),text('우리 구현',19,SECOND).to_corner(UR,buff=.45))
  az=ValueTracker(-68*DEGREES);elev=ValueTracker(24*DEGREES);distance=ValueTracker(9);cube_x=ValueTracker(-1.1)
  chimney=[False];terrace=[False];showpoint=[True];metric=None;active=None
  def drawing():
   target=np.array([0,.5,.9]);eye=target+distance.get_value()*np.array([np.cos(elev.get_value())*np.cos(az.get_value()),np.cos(elev.get_value())*np.sin(az.get_value()),np.sin(elev.get_value())]);forward=target-eye;forward/=np.linalg.norm(forward);right=np.cross(forward,[0,0,1]);right/=np.linalg.norm(right);up=np.cross(right,forward);center=np.array([-3.65,.20,0])
   def project(p):
    q=np.array(p)-eye;z=np.dot(q,forward);return np.array([np.dot(q,right),np.dot(q,up),0])*6.1/z+center,z
   g=VGroup()
   for j in np.linspace(-2.5,2.5,6):
    for a,b in [([-2.5,j,0],[2.5,j,0]),([j,-2.5,0],[j,2.5,0])]:g.add(Line(project(a)[0],project(b)[0],color=v.v.RULE,stroke_width=1))
   if self.sid in ['02','11']:
    faces=box([.5,1.3,1.35],[.8,.8,2.7],'#C4CFD8')+box([cube_x.get_value(),-.7,.5],[1,1,1],BLUE)
    point=[cube_x.get_value(),-1.2,1] if self.sid=='11' else [.1,.9,2.7]
   else:
    faces=v.architecture();point=[-.9,-1.1,2.35]
    if chimney[0]:faces+=box([-.5,-.2,2.45],[.3,.35,.7],YELLOW)
    if terrace[0]:faces+=box([0,-1.2,.15],[2.8,1.4,.3],GREEN)
   projected=[]
   for vertices,col in faces:
    pts=[project(p) for p in vertices];projected.append((np.mean([z for p,z in pts]),Polygon(*[p for p,z in pts],fill_color=col,fill_opacity=1,stroke_color=BG,stroke_width=1.4)))
   for dep,p in sorted(projected,key=lambda x:x[0],reverse=True):g.add(p)
   # Mark a directly visible front roof/cube point; hidden points are omitted in14.
   if showpoint[0]:
    p=project(point)[0];g.add(Dot(p,radius=.055,color=YELLOW),text('A',24,YELLOW).move_to(p+[.15,.25,0]))
   return g
  model=always_redraw(drawing);self.add(model)
  def note(s,c=BLUE):
   nonlocal metric
   if metric:self.remove(metric)
   metric=v.v.base.fit(text(s,25,c),5.65).move_to([3.25,.05,0]);self.add(metric)
  def move(*args):self.play(*args,run_time=1.8)
  for i,tm in enumerate(slot['lineStarts']):
   if tm>self.renderer.time:self.wait(tm-self.renderer.time)
   if active:self.remove(active)
   active=v.v.base.fit(text(PHRASES[self.sid][min(i,len(PHRASES[self.sid])-1)],27),5.65).move_to([3.25,1.65,0]);self.add(active)
   if self.sid=='02':
    if i==0:move(az.animate.set_value(-32*DEGREES));note('기둥의 세계 배치는 그대로')
    elif i==1:move(az.animate.set_value(-12*DEGREES));note('관찰 방향에 따라 겹치는 면 변경',GREEN)
    else:note('같은 점 · 서로 다른 기준',YELLOW)
   elif self.sid=='05':
    if i==0:chimney[0]=True;note('A는 기존 지붕 · 굴뚝은 새 구조',YELLOW)
    elif i==1:note('기준점을 바꿔 잡지 않기',GREEN)
    elif i==2:move(az.animate.set_value(-22*DEGREES));note('건물 고정 · 카메라만 회전')
    elif i==3:note('세계 좌표는 그대로 / 관찰 기준 변경',GREEN)
    elif i==4:note('물체 점 → 모델 변환 → 세계의 점')
    elif i==5:move(elev.animate.set_value(42*DEGREES));note('세계의 배치를 다시 쓰지 않음',GREEN)
    elif i==6:note('(1,0,0) + (3,2,5): 앞의 계산 예제',SECOND)
    else:note('새 점 / 같은 점의 다른 관찰',YELLOW)
   elif self.sid=='08':
    if i==0:terrace[0]=True;move(elev.animate.set_value(15*DEGREES));note('발판 추가 + 관찰 높이 변화',GREEN)
    elif i==1:move(az.animate.set_value(-25*DEGREES));note('같은 A가 화면에서 다른 위치에 보임')
    elif i==2:note('새 발판 대신 기존 지붕 A를 계속 추적',GREEN)
    elif i==3:move(distance.animate.set_value(11));note('카메라 거리와 투영 조건을 따로 기록')
    elif i==4:note('행렬 곱 뒤에도 처리 단계가 남음',YELLOW)
    elif i==5:note('축의 방향은 공간마다 다를 수 있음',GREEN)
    else:note('게임의 숨은 좌표를 측정한 것이 아님',SECOND)
   elif self.sid=='11':
    if i==0:move(cube_x.animate.set_value(.6));note('큐브 이동 / 기둥 고정',GREEN)
    elif i==1:note('물체의 세계 위치와 화면 위치는 다름',YELLOW)
    elif i==2:move(distance.animate.set_value(11));note('거리를 바꾸어도 화면 크기가 변함')
    elif i==3:note('포털 내부 렌더링의 분석은 아님',SECOND)
    elif i==4:move(cube_x.animate.set_value(-1.1));move(az.animate.set_value(-20*DEGREES));note('먼저 큐브만 이동 → 그다음 카메라만 이동',GREEN)
    else:note('세계 배치 / 카메라 / 투영을 각각 제어',YELLOW)
   elif self.sid=='14':
    if i==0:note('앞 건물과 뒤 건물의 관계',YELLOW)
    elif i==1:showpoint[0]=False;move(az.animate.set_value(-135*DEGREES),elev.animate.set_value(10*DEGREES));note('앞 건물이 뒤쪽 면을 가림',GREEN)
    elif i==2:move(elev.animate.set_value(55*DEGREES));note('높아진 관찰 위치 → 뒤쪽 면이 드러남')
    elif i==3:note('범위 밖 / 다른 물체 뒤는 다른 원인',YELLOW)
    elif i==4:note('기하 편집 · 가림 · 클리핑을 구분',GREEN)
    elif i==5:note('near 수치는 앞의 명시적 계산 예제',SECOND)
    elif i==6:showpoint[0]=True;move(az.animate.set_value(-68*DEGREES));note('같은 기준점 A로 돌아와 비교')
    else:note('다음: 남은 점을 출력 창에 배치',YELLOW)
   model.update(0)
  if self.renderer.time<slot['seconds']:self.wait(slot['seconds']-self.renderer.time)
for sid in TITLES:globals()['Scene'+sid]=type('Scene'+sid,(Replacement,),{'sid':sid,'__module__':__name__})
