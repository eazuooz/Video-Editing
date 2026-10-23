"""Editable pinhole-camera models: actual projected 3D architecture, not game telemetry.

Reuse the established Manim mathematical stage. Geometry, camera orbit/distance,
focal scale and output viewport are independent variables in this implementation.
"""
from pathlib import Path
import importlib.util,json,os
import numpy as np
from manim import *
spec=importlib.util.spec_from_file_location('camera_style',Path(__file__).with_name('m03-scenes.py'));v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
text=v.text;BG=v.BG;FG=v.FG;YELLOW=v.YELLOW;GREEN=v.Y;BLUE=v.Z;RED=v.X;SECOND=v.SECOND
TITLES={'02':'카메라와 출력 영역은 서로 다른 조건','05':'건물 편집 / 관찰 방향 변경','08':'건물 고정 · 카메라 방향 변경','11':'캐릭터 크기만으로 시야각을 알 수 있을까?','13':'앞뒤 지붕을 함께 비교','16':'같은 기준점 · 다른 관찰 조건','19':'원하는 면과 범위를 먼저 정하기','21':'물체 · 카메라 · 출력 창 구분'}
PHRASES={
'02':['두 플레이어 / 서로 다른 카메라','각 시점에서 다른 면과 가림','카메라: 무엇을 보는가','출력 창: 어디에 놓는가'],
'05':['건물 자체의 형태가 달라짐','물체의 모양 ≠ 픽셀의 종횡비','건물 고정 / 관찰 방향만 변경','같은 지붕을 계속 추적','게임의 내부 투영값은 미확정','한 조건씩 바꾸는 통제 예제','다음: 카메라가 담는 부피'],
'08':['낮은 시점 → 높은 시점','위쪽 지붕과 안쪽 면이 드러남','같은 배치 / 다른 겹침','확대 정도와 보이는 면을 구분','화면 밖 ≠ 물체 삭제','near / far 숫자는 게임에서 미측정','다음: 카메라 고정, FOV 변경'],
'11':['몸 크기와 주변 공간을 함께 보기','거리 · 시야각 · 방향이 모두 영향','통제 예제에서 한 변수씩 변경'],
'13':['같은 지붕의 모서리 A를 추적','가까운 화면 / 줄어든 주변 공간','뒤쪽 지붕 B도 함께 비교','다음: 줌과 이동을 나눠 계산'],
'16':['앞벽 A / 뒤쪽 지붕 B','가까운 화면 / 넓은 화면','방향이 달라지면 보이는 면도 변경','오른쪽 모형의 A와 B를 유지','두 깊이의 기준점을 함께 추적','게임의 함수·배율을 추정하지 않음','관찰 결과와 계산 조건을 연결','다음: 거리에 따른 축소를 없애기'],
'19':['가까운 성 → 주변 탑까지','방향을 바꾸면 숨은 면이 드러남','직교 투영: 거리 축소 없는 축척','관찰 방향 → 투영 → 출력 영역'],
'21':['시점 변경 / 넓게 보기','건물 추가는 물체의 변화','대상 · 방향 · 범위 · 출력 창','한 조건씩 바꿔 기준점 비교']}

def architecture(scale=1,extra=False):
 # z is up. Each entry is a real planar face with world-space vertices.
 faces=[]
 def face(points,c):faces.append((np.array(points,float),c))
 def house(cx,cy,w,d,h,roof):
  x0=cx-w/2;x1=cx+w/2;y0=cy-d/2;y1=cy+d/2
  face([[x0,y0,0],[x1,y0,0],[x1,y0,h],[x0,y0,h]],'#C4CFD8')
  face([[x1,y0,0],[x1,y1,0],[x1,y1,h],[x1,y0,h]],'#8398AC')
  face([[x1,y1,0],[x0,y1,0],[x0,y1,h],[x1,y1,h]],'#A8B8C7')
  face([[x0,y1,0],[x0,y0,0],[x0,y0,h],[x0,y1,h]],'#657E96')
  face([[x0,y0,h],[cx,y0,h+.65],[cx,y1,h+.65],[x0,y1,h]],roof)
  face([[cx,y0,h+.65],[x1,y0,h],[x1,y1,h],[cx,y1,h+.65]],roof)
  face([[x0,y0,h],[x1,y0,h],[cx,y0,h+.65]],'#CFDBE4')
  face([[x1,y1,h],[x0,y1,h],[cx,y1,h+.65]],'#9AAAB9')
  for xx in [cx-w*.24,cx+w*.24]:
   face([[xx-.11,y0-.008,h*.45],[xx+.11,y0-.008,h*.45],[xx+.11,y0-.008,h*.74],[xx-.11,y0-.008,h*.74]],'#233346')
  face([[cx-.15,y0-.012,0],[cx+.15,y0-.012,0],[cx+.15,y0-.012,h*.40],[cx-.15,y0-.012,h*.40]],'#385245')
 house(-.9,-.4,1.6,1.4,1.7*scale,BLUE)
 house(.9,1.4,1.45,1.4,2.0,GREEN)
 if extra:house(-1.7,1.8,.9,1.0,1.3,YELLOW)
 return faces

class Replacement(Scene):
 sid=''
 def construct(self):
  slot=next(s for s in json.loads(Path(os.environ['MATH_RENDER_TIMING']).read_text(encoding='utf8'))['scenes'] if s['id']==self.sid)
  self.camera.background_color=BG
  self.add(v.base.fit(text(TITLES[self.sid],34,YELLOW),11.2).to_corner(UL,buff=.45),text('우리 구현',19,SECOND).to_corner(UR,buff=.45))
  az=ValueTracker(-68*DEGREES);elev=ValueTracker(24*DEGREES);dist=ValueTracker(9);focal=ValueTracker(6.3);height=ValueTracker(1);centerx=ValueTracker(-3.7)
  scene_extra=[False];marks=[False];dual=[self.sid in ['02','11']];metric=None;active=None
  def view(angle,center,width=5.55,ht=3.75):
   target=np.array([0,.5,.9]);eye=target+dist.get_value()*np.array([np.cos(elev.get_value())*np.cos(angle),np.cos(elev.get_value())*np.sin(angle),np.sin(elev.get_value())]);forward=target-eye;forward/=np.linalg.norm(forward);right=np.cross(forward,[0,0,1]);right/=np.linalg.norm(right);up=np.cross(right,forward)
   def project(p):
    q=p-eye;dep=np.dot(q,forward);return np.array([np.dot(q,right),np.dot(q,up),0])*focal.get_value()/dep+center,dep
   g=VGroup()
   for j in np.linspace(-2.5,2.5,6):
    for p,q in [([-2.5,j,0],[2.5,j,0]),([j,-2.5,0],[j,2.5,0])]:
     a,_=project(p);b,_=project(q);g.add(Line(a,b,color=v.RULE,stroke_width=1))
   fs=[]
   for vertices,col in architecture(height.get_value(),scene_extra[0]):
    pts=[];depth=[]
    for p in vertices:a,z=project(p);pts.append(a);depth.append(z)
    fs.append((np.mean(depth),Polygon(*pts,fill_color=col,fill_opacity=1,stroke_color=BG,stroke_width=1.5)))
   for _,poly in sorted(fs,key=lambda x:x[0],reverse=True):g.add(poly)
   if marks[0]:
    for name,p,c in [('A',[-.9,-1.1,1.7*height.get_value()+.65],BLUE),('B',[.9,.7,2.65],GREEN)]:
     a,_=project(p);g.add(Dot(a,radius=.055,color=c),text(name,23,c).move_to(a+[.16,.24,0]))
   # All mesh remains within the diagram pane by design; no fake game numbers.
   return g
  def drawing():
   center=np.array([centerx.get_value(),.20,0])
   if dual[0]:
    return VGroup(view(az.get_value(),center+[-1.5,0,0]).scale(.60,about_point=center+[-1.5,0,0]),view(az.get_value()+60*DEGREES,center+[1.5,0,0]).scale(.60,about_point=center+[1.5,0,0]),Line(center+[0,-1.9,0],center+[0,1.9,0],color=SECOND,stroke_width=2))
   return view(az.get_value(),center)
  model=always_redraw(drawing);self.add(model)
  footer=text('자체 좌표로 계산한 투영 · 게임 내부 수치 아님',19,SECOND).move_to([-2,-2.65,0]);self.add(footer)
  def note(s,c=BLUE):
   nonlocal metric
   if metric:self.remove(metric)
   side=-3.2 if centerx.get_value()>0 else 3.25
   metric=v.base.fit(text(s,25,c),5.7).move_to([side,.05,0]);self.add(metric)
  def motion(*anims,seconds=1.8):self.play(*anims,run_time=seconds)
  for i,tm in enumerate(slot['lineStarts']):
   if tm>self.renderer.time:self.wait(tm-self.renderer.time)
   if self.sid=='16' and i==3:
    # Narration explicitly says right-hand model. Swap the model and prose here.
    centerx.set_value(3.3);marks[0]=True
    # A frozen Wait otherwise retains the previous pixels until the next play.
    model.update(0)
   if active:self.remove(active)
   side=-3.2 if centerx.get_value()>0 else 3.25
   active=v.base.fit(text(PHRASES[self.sid][min(i,len(PHRASES[self.sid])-1)],27),5.7).move_to([side,1.65,0]);self.add(active)
   if self.sid=='02':
    if i==0:note('같은 건물 · 두 관찰 방향',YELLOW)
    if i==1:motion(az.animate.set_value(-110*DEGREES));note('각 카메라에서 겹침을 따로 계산')
    if i==2:note('관찰 위치 + 방향 + 투영',GREEN)
    if i==3:note('두 결과를 서로 다른 출력 영역에 배치',YELLOW)
   elif self.sid=='05':
    if i==0:motion(height.animate.set_value(1.4));note('건물 높이 변경',YELLOW)
    if i==1:note('픽셀은 그대로 · 3D 기하가 변경',GREEN)
    if i==2:motion(az.animate.set_value(-22*DEGREES));note('물체 고정 · 카메라 위치/방향 변경',BLUE)
    if i==3:marks[0]=True;motion(az.animate.set_value(-5*DEGREES));note('같은 지붕 A / 다른 겹침',BLUE)
    if i==4:note('카메라 함수·행렬은 게임에서 미확인',SECOND)
    if i==5:note('위치 / FOV / 출력 창을 각각 제어',GREEN)
    if i==6:note('다음: 절두체, near와 far',YELLOW)
   elif self.sid=='08':
    if i==0:motion(elev.animate.set_value(52*DEGREES));note('카메라 높이 변경',BLUE)
    if i==1:marks[0]=True;note('위쪽 면이 더 잘 보임',GREEN)
    if i==2:motion(az.animate.set_value(-18*DEGREES));note('세계의 배치는 그대로',BLUE)
    if i==3:motion(dist.animate.set_value(11));motion(dist.animate.set_value(7.5));note('모형: 카메라 거리 변경',YELLOW)
    if i==4:note('보이는 범위와 물체 존재는 다름',GREEN)
    if i==5:note('게임의 near/far 값을 읽어낸 것이 아님',SECOND)
    if i==6:note('다음 계산: 시야각만 바꾸기',YELLOW)
   elif self.sid=='11':
    if i==0:note('모형: 서로 다른 관찰 방향',BLUE)
    if i==1:motion(dist.animate.set_value(7.5));note('크기에 영향을 주는 조건은 여러 개',YELLOW)
    if i==2:note('거리 고정 → FOV 변경 / FOV 고정 → 이동',GREEN)
   elif self.sid=='13':
    if i==0:marks[0]=True;motion(focal.animate.set_value(7.5));note('기준점 A와 B',BLUE)
    if i==1:motion(focal.animate.set_value(8.2));note('모형: 관찰 위치 고정, 초점 배율 변경')
    if i==2:note('앞뒤 두 대상의 변화 함께 확인',GREEN)
    if i==3:note('다음: 두 깊이에서 줌 / 이동 비교',YELLOW)
   elif self.sid=='16':
    if i==0:marks[0]=True;motion(focal.animate.set_value(7.5));note('모형의 기준점 A / B',BLUE)
    if i==1:motion(focal.animate.set_value(5.5));note('넓은 범위로 관찰',GREEN)
    if i==2:motion(az.animate.set_value(-30*DEGREES));note('같은 면도 방향에 따라 다르게 보임',YELLOW)
    if i==3:note('A: 앞쪽 벽의 지붕 / B: 뒤쪽 지붕',GREEN)
    if i==4:motion(focal.animate.set_value(5));motion(focal.animate.set_value(7.5));note('두 기준점을 남긴 채 넓게 → 가까이',BLUE)
    if i==5:note('2배 / 4⁄3배는 앞의 통제 예제 값',SECOND)
    if i==6:note('결과 보기 + 원인이 되는 조건 확인',GREEN)
    if i==7:note('다음: 직교 투영 Orthographic Projection',YELLOW)
   elif self.sid=='19':
    if i==0:scene_extra[0]=True;dist.set_value(7);motion(dist.animate.set_value(11));note('모형: 카메라 후퇴',BLUE)
    if i==1:motion(az.animate.set_value(-15*DEGREES));note('크기뿐 아니라 방향도 선택',GREEN)
    if i==2:note('현재 모형은 원근 투영 · 앞 계산과 구분',SECOND)
    if i==3:note('관찰 방향 / 원근감 / 담을 범위',YELLOW)
   elif self.sid=='21':
    if i==0:motion(elev.animate.set_value(46*DEGREES),dist.animate.set_value(10.5));note('관찰 조건 변경',BLUE)
    if i==1:scene_extra[0]=True;note('새 건물이 생김: 물체 변화',GREEN)
    if i==2:note('대상 → 방향 → 범위 → 출력 창',YELLOW)
    if i==3:marks[0]=True;motion(az.animate.set_value(-35*DEGREES));note('물체 고정 · 관찰 방향만 변경',BLUE)
  if self.renderer.time<slot['seconds']:self.wait(slot['seconds']-self.renderer.time)
for sid in TITLES:globals()['Scene'+sid]=type('Scene'+sid,(Replacement,),{'sid':sid,'__module__':__name__})
