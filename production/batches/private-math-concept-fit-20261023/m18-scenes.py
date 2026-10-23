"""Depth, surface patterns and landmarks in one editable projected3D stage."""
from pathlib import Path
import importlib.util,json,os
import numpy as np
from manim import *
spec=importlib.util.spec_from_file_location('architecture',Path(__file__).with_name('m16-scenes.py'));v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
text=v.text;BG=v.BG;FG=v.FG;BLUE=v.BLUE;GREEN=v.GREEN;YELLOW=v.YELLOW;SECOND=v.SECOND
TITLES={'03':'같은 화면 위치 · 다른 앞뒤 깊이','06':'무늬는 화면이 아니라 표면에 붙습니다','09':'한 기준점으로 변환 단계 확인'}
PHRASES={
'03':['새 앞벽과 기존 뒤쪽 난간','가로·세로만으로 앞뒤를 정할 수 없음','관찰 높이만 바꾸어 가림 비교','저장 깊이 ≠ 실제 거리','이 예제: near 0 / far 1','게임의 깊이 형식은 미확인','같은 카메라·투영에서 비교','배치 → 경계 → 깊이 검사'],
'06':['지붕 표면에 붙은 반복 무늬','기울어진 면 / 달라지는 화면 간격','앞의 계산: u = 0.2','게임 셰이더를 추정한 그림이 아님','다음: 표면 위치에 UV 좌표 연결'],
'09':['같은 테라스의 모서리 A 유지','다른 건물에 가려진 상태 구분','새 블록은 물체 구조의 변화','난간과 나무를 함께 기준으로 사용','local → world → view','clip의 네 성분과 w를 유지','출력 창의 시작과 크기도 기록','접근 가능한 프로젝트 값으로 확인','앞뒤 가림 / 표면 보간까지 연결','처음 달라진 변환부터 찾기']}
def cuboid(cx,cy,w,d,h,col):
 x0=cx-w/2;x1=cx+w/2;y0=cy-d/2;y1=cy+d/2
 return [(np.array(pts,float),c) for pts,c in [([[x0,y0,0],[x1,y0,0],[x1,y0,h],[x0,y0,h]],col),([[x1,y0,0],[x1,y1,0],[x1,y1,h],[x1,y0,h]],'#8398AC'),([[x1,y1,0],[x0,y1,0],[x0,y1,h],[x1,y1,h]],'#A8B8C7'),([[x0,y1,0],[x0,y0,0],[x0,y0,h],[x0,y1,h]],'#657E96'),([[x0,y0,h],[x1,y0,h],[x1,y1,h],[x0,y1,h]],'#A8D6BD')]]
class Replacement(Scene):
 sid=''
 def construct(self):
  slot=next(s for s in json.loads(Path(os.environ['MATH_RENDER_TIMING']).read_text(encoding='utf8'))['scenes'] if s['id']==self.sid)
  self.camera.background_color=BG;self.add(v.v.base.fit(text(TITLES[self.sid],34,YELLOW),11.2).to_corner(UL,buff=.45),text('우리 구현',19,SECOND).to_corner(UR,buff=.45))
  az=ValueTracker(-68*DEGREES);elev=ValueTracker(32*DEGREES);height=ValueTracker(.8);active=None;metric=None;showpoint=[self.sid=='09']
  def drawing():
   target=np.array([0,.4,.8]);eye=target+9*np.array([np.cos(elev.get_value())*np.cos(az.get_value()),np.cos(elev.get_value())*np.sin(az.get_value()),np.sin(elev.get_value())]);f=target-eye;f/=np.linalg.norm(f);r=np.cross(f,[0,0,1]);r/=np.linalg.norm(r);u=np.cross(r,f);center=np.array([-3.65,.2,0])
   def project(p):q=np.array(p)-eye;z=np.dot(q,f);return center+np.array([np.dot(q,r),np.dot(q,u),0])*6.2/z,z
   g=VGroup()
   for j in np.linspace(-2.5,2.5,6):
    for a,b in [([-2.5,j,0],[2.5,j,0]),([j,-2.5,0],[j,2.5,0])]:g.add(Line(project(a)[0],project(b)[0],color=v.v.RULE,stroke_width=1))
   if self.sid=='06':
    fs=cuboid(0,0,3,2,.55,'#C4CFD8');n=8
    # Planar roof grid in world coordinates, then perspective-project each tile.
    for ix in range(n):
     for iy in range(n):
      x0=-1.6+3.2*ix/n;x1=-1.6+3.2*(ix+1)/n;y0=-1.25+2.5*iy/n;y1=-1.25+2.5*(iy+1)/n
      fs.append((np.array([[x0,y0,1.0+.45*y0],[x1,y0,1.0+.45*y0],[x1,y1,1.0+.45*y1],[x0,y1,1.0+.45*y1]]),BLUE if (ix+iy)%2 else '#DCE6EC'))
   elif self.sid=='09':
    fs=cuboid(0,0,2.7,2.2,height.get_value(),BLUE)+cuboid(.9,1.4,1.2,1.2,2.3,'#A8B8C7')
    for cx,cy in [(-1.25,0),(.1,-1.0),(1.25,0)]:fs+=cuboid(cx,cy,.12,.12,height.get_value()+.45,GREEN)
   else:fs=v.architecture()
   shapes=[]
   for points,col in fs:
    pp=[project(p) for p in points];shapes.append((np.mean([z for p,z in pp]),Polygon(*[p for p,z in pp],fill_color=col,fill_opacity=1,stroke_color=BG,stroke_width=1)))
   for _,poly in sorted(shapes,key=lambda x:x[0],reverse=True):g.add(poly)
   if showpoint[0]:
    p=project([-1.35,-1.1,height.get_value()])[0];g.add(Dot(p,radius=.055,color=YELLOW),text('A',24,YELLOW).move_to(p+[.15,.25,0]))
   return g
  model=always_redraw(drawing);self.add(model)
  def note(s,c=BLUE):
   nonlocal metric
   if metric:self.remove(metric)
   metric=v.v.base.fit(text(s,25,c),5.7).move_to([3.25,.05,0]);self.add(metric)
  def move(*args):self.play(*args,run_time=1.8)
  for i,tm in enumerate(slot['lineStarts']):
   if tm>self.renderer.time:self.wait(tm-self.renderer.time)
   if active:self.remove(active)
   active=v.v.base.fit(text(PHRASES[self.sid][i],27),5.7).move_to([3.25,1.65,0]);self.add(active)
   if self.sid=='03':
    if i==0:move(az.animate.set_value(-135*DEGREES),elev.animate.set_value(12*DEGREES));note('앞쪽 지붕이 뒤쪽 면을 가림',GREEN)
    elif i==1:note('같은 픽셀에 여러 표면이 겹칠 수 있음',YELLOW)
    elif i==2:move(elev.animate.set_value(58*DEGREES));move(elev.animate.set_value(12*DEGREES));note('물체 배치는 고정 · 관찰 높이만 변경')
    elif i==3:note('0.825는 거리 단위가 아님',YELLOW)
    elif i==4:note('우리 예제의 규약: 가까움 0 / 멂 1',GREEN)
    elif i==5:note('게임 내부 버퍼를 읽은 결과 아님',SECOND)
    elif i==6:note('다른 카메라의 깊이를 바로 비교하지 않기')
    else:note('처음 달라진 단계부터 점검',YELLOW)
   elif self.sid=='06':
    if i==0:note('표면의 같은 무늬를 유지',GREEN)
    elif i==1:move(az.animate.set_value(-20*DEGREES),elev.animate.set_value(15*DEGREES));note('세계의 격자는 일정 / 화면 간격은 변화')
    elif i==2:note('(0.125) / (0.625) = 0.2',YELLOW)
    elif i==3:note('표면 관계의 모형 · 내부 셰이더 추정 아님',SECOND)
    else:move(elev.animate.set_value(55*DEGREES));note('UV는 표면의 위치와 무늬를 연결',GREEN)
   else:
    if i==0:move(az.animate.set_value(-35*DEGREES));note('같은 A와 주변 기준물을 함께 보기',GREEN)
    elif i==1:showpoint[0]=False;move(az.animate.set_value(45*DEGREES),elev.animate.set_value(10*DEGREES));note('뒤로 숨은 기준점은 표시도 숨김',GREEN)
    elif i==2:move(az.animate.set_value(-68*DEGREES),elev.animate.set_value(35*DEGREES));showpoint[0]=True;move(height.animate.set_value(1.7));note('높이를 바꾸면 물체 자체가 변함',YELLOW)
    elif i==3:note('모서리와 가장자리 기둥을 함께 유지')
    elif i==4:note('같은 점의 이름과 local 위치부터 기록')
    elif i==5:note('(x, y, z, w) · 나누기 전의 네 숫자',YELLOW)
    elif i==6:note('viewport = 시작 위치 + 너비 + 높이',GREEN)
    elif i==7:note('게임 영상만으로 중간 수치 추정 금지',SECOND)
    elif i==8:note('깊이와 보간도 같은 변환 흐름에 연결')
    else:note('다음: 메시와 표면의 UV',YELLOW)
   model.update(0)
  if self.renderer.time<slot['seconds']:self.wait(slot['seconds']-self.renderer.time)
for sid in TITLES:globals()['Scene'+sid]=type('Scene'+sid,(Replacement,),{'sid':sid,'__module__':__name__})
