"""Editable cross-section light models; actual game footage supplies the observed surfaces."""
from pathlib import Path
import importlib.util,json,os
import numpy as np
from manim import *
spec=importlib.util.spec_from_file_location('light_style',Path(__file__).with_name('m03-scenes.py'));v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
text=v.text;BG=v.BG;YELLOW=v.YELLOW;GREEN=v.Y;BLUE=v.Z;RED=v.X;SECOND=v.SECOND
TITLES={'02':'먼저 보이는 표면 고르기','05':'빈 구멍과 반투명 표면','08':'표면색과 조명 조건','11':'표시한 색과 빛의 스펙트럼','14':'굽은 표면마다 다른 법선','17':'빛을 내는 조명 / 빛을 받는 벽','19':'가려진 한 방향과 남은 입사광','21':'앞뒤 순서와 밝기는 다른 질문'}
PHRASES={
'02':['벽과 뒤쪽 물체의 겹침','시선이 바뀌면 보이는 부분도 변경','불투명: 가장 먼저 만나는 표면','가시성 / 셰이딩 구분','밝게 해도 앞벽은 그대로','다음: 광선과 래스터 방식'],
'05':['구멍에는 앞벽 표면이 없음','빈 구멍 ≠ 흐린 벽','상자 표면 + 뒤의 물체','투과 · 필요하면 굴절도 고려','기법은 화면만으로 확정하지 않음'],
'08':['밝은 벽 / 어두운 표면','재질과 빛이 함께 만든 결과','건설 도구로 문틀 설치','픽셀에서 광원·BRDF를 단정하지 않음','다음: 조건을 정한 반사 분포'],
'11':['같은 빨간 표면의 명암','RGB: 색을 기록하는 좌표','빛이 세 파장뿐이라는 뜻 아님','재질 · 빛 · 시선 · 표시 변환','다음: 에너지와 단위를 구별'],
'14':['밝은 부분과 어두운 부분','위치마다 다른 표면 방향','거리·가림·재질·물속 효과도 존재','다음: 빛 고정 / 판 방향만 변경','실제 게임의 각도 측정값 아님'],
'17':['같은 표면 / 달라진 입사광','방출과 반사는 다른 역할','미리 보기 → 설치된 조명','설치 후 벽이 밝아진 결과','내부 간접 조명 구현은 미확정'],
'19':['그늘에도 보이는 표면','한 광원 방향의 가림','다른 방향의 기여가 남을 수 있음','방향별 기여를 합하는 문제','다음: 표본 수와 정규화'],
'21':['가까운 표면이 뒤를 가림','어느 면인가 / 얼마나 밝은가','입사광과 관찰 방향을 연결','표면 선택 → 단위 → 반사 합','다음: 조건을 정한 확산면']}

class Replacement(Scene):
 sid=''
 def construct(self):
  slot=next(s for s in json.loads(Path(os.environ['MATH_RENDER_TIMING']).read_text(encoding='utf8'))['scenes'] if s['id']==self.sid)
  self.camera.background_color=BG
  self.add(v.base.fit(text(TITLES[self.sid],34,YELLOW),11).to_corner(UL,buff=.5),text('직접 정의한 원리 모형',19,SECOND).to_corner(UR,buff=.5))
  active=None;metric=None;model=VGroup();anchor=np.array([-4.2,-.05,0])
  def p(x,y):return anchor+np.array([x,y,0])
  def label(s,x,y,c=WHITE,size=23):return text(s,size,c).move_to(p(x,y))
  def beat(s):
   nonlocal active
   if active:self.remove(active)
   active=v.base.fit(text(s,27),5.7).move_to([3.3,1.6,0]);self.add(active)
  def note(s,c=BLUE):
   nonlocal metric
   if metric:self.remove(metric)
   metric=v.base.fit(text(s,25,c),5.7).move_to([3.3,.05,0]);self.add(metric)
  def replace(m):
   nonlocal model
   self.remove(*model.get_family());model=m;self.add(model)
  def arrow(a,b,c=YELLOW):return Arrow(p(*a),p(*b),buff=.06,color=c,stroke_width=4)
  def person(x,y,c=BLUE):
   return VGroup(Circle(.22,fill_opacity=1,fill_color=c,color=c).move_to(p(x,y+.7)),Line(p(x,y+.5),p(x,y-.25),color=c,stroke_width=13),Line(p(x-.4,y+.3),p(x+.4,y+.3),color=c,stroke_width=9),Line(p(x,y-.2),p(x-.3,y-.8),color=c,stroke_width=9),Line(p(x,y-.2),p(x+.3,y-.8),color=c,stroke_width=9))
  def opaque():
   obj=person(1,0);wall=Rectangle(width=.35,height=2.0,color=YELLOW,fill_color=YELLOW,fill_opacity=1).move_to(p(-.15,0));cam=Circle(.2,color=WHITE).move_to(p(-2,0))
   return VGroup(obj,Line(p(-2,0),p(1,0),color=BLUE,stroke_opacity=.35),wall,cam,arrow((-1.7,0),(-.4,0)),label('눈',-2,-.6),label('앞벽',-.15,1.7,YELLOW),label('뒤 물체',1,-1.3,BLUE))
  def room(on=False):
   c=WHITE if on else SECOND;floor=VMobject().set_points_as_corners([p(-2,1.3),p(2,1.3),p(2,-1.5),p(-2,-1.5)]).set_stroke(c,6)
   lamp=Rectangle(width=.7,height=.18,color=YELLOW,fill_color=YELLOW,fill_opacity=1 if on else 0).move_to(p(0,1.25));m=VGroup(floor,lamp,label('빛을 내는 면',0,1.9,YELLOW),label('빛을 받는 벽',1.3,-1.9,c))
   if on:m.add(arrow((0,1.1),(1.8,-.6)),arrow((0,1.1),(-1.8,-.4)),arrow((1.75,-.55),(.5,-.5),GREEN))
   return m
  self.add(text('원리 설명용 단면·색 모형 · 게임 내부 측정값 아님',20,SECOND).move_to([-2,-2.68,0]))
  if self.sid in ['02','21']:replace(opaque())
  elif self.sid=='05':replace(VGroup(Rectangle(width=.35,height=.8,color=YELLOW,fill_opacity=1).move_to(p(0,1)),Rectangle(width=.35,height=.8,color=YELLOW,fill_opacity=1).move_to(p(0,-1)),Circle(.5,color=GREEN,fill_opacity=.5).move_to(p(1.4,0)),arrow((-2,0),(1,0)),label('빈 통로',0,1.8,YELLOW)))
  elif self.sid=='08':replace(VGroup(Square(1.5,color=WHITE,fill_color='#DCE6E4',fill_opacity=1).move_to(p(-1,0)),Square(1.5,color=SECOND,fill_color='#30383F',fill_opacity=1).move_to(p(1,0)),label('밝은 표면',-1,-1.3),label('어두운 표면',1,-1.3,SECOND)))
  elif self.sid=='11':replace(VGroup(*[Square(1.15,color=c,fill_color=c,fill_opacity=1).move_to(p(-1.4+i*1.4,0)) for i,c in enumerate(['#E4646F','#9B3542','#4C1F2A'])],label('같은 빨강 계열 / 다른 명암',0,-1.1,RED)))
  elif self.sid=='14':
   curve=Arc(radius=1.5,start_angle=PI*.12,angle=PI*.76,arc_center=p(0,-.6),color=SECOND,stroke_width=8);replace(VGroup(curve,label('굴곡진 표면 단면',0,-1.4)))
  elif self.sid=='17':replace(room(False))
  elif self.sid=='19':replace(VGroup(Line(p(-2,-1),p(2,-1),color=GREEN,stroke_width=7),Rectangle(width=.5,height=1.4,color=SECOND,fill_color=SECOND,fill_opacity=1).move_to(p(-.6,.35)),arrow((-2,1.8),(-.9,.8)),label('가려진 광원 방향',-.7,2.1,YELLOW),label('그늘의 표면',.6,-1.4,GREEN)))
  starts=slot.get('lineStarts',[x['start'] for x in slot['cues']])
  for i,tm in enumerate(starts):
   if tm>self.renderer.time:self.wait(tm-self.renderer.time)
   beat(PHRASES[self.sid][min(i,len(PHRASES[self.sid])-1)])
   if self.sid=='02':
    if i==0:note('가까운 벽 / 뒤쪽 캐릭터')
    if i==1:
     m=opaque();replace(m);self.remove(m[1],m[4]);self.play(m[3].animate.shift(UP*2),m[5].animate.shift(UP*2),run_time=1.3);ray=arrow((-2,2),(1,.7),BLUE);self.add(ray);m.add(ray);note('시선 위치 변경 / 벽과 물체는 그대로')
    if i==2:replace(opaque());note('불투명한 앞면에서 시선이 멈춤',YELLOW)
    if i==3:note('가시성: 대상 선택 / 셰이딩: 색 계산',GREEN)
    if i==4:self.play(model[2].animate.set_fill(WHITE),run_time=.7);note('벽이 밝아져도 가림은 유지',YELLOW)
    if i==5:note('광선 또는 투영된 삼각형에서 시작',BLUE)
   elif self.sid=='05':
    if i==0:note('없는 앞면을 통과해 뒤를 봄',GREEN)
    if i==1:note('구멍: 표면이 없음 / 투명: 표면이 있음',YELLOW)
    if i==2:
     replace(VGroup(Circle(.55,color=RED,fill_color=RED,fill_opacity=1).move_to(p(.7,0)),Rectangle(width=2.2,height=2,color=BLUE,fill_color=BLUE,fill_opacity=.25).move_to(p(.3,0)),label('표면과 뒤 물체가 함께 보임',0,-1.5,BLUE)));note('반투명 표면',BLUE)
    if i==3:
     beam=arrow((-2,0),(1.3,0),GREEN);self.play(Create(beam),run_time=1.4);model.add(beam);note('뒤에서 오는 빛의 기여도 필요',GREEN)
    if i==4:note('표시는 설명 모형 · 기법의 실측 아님',SECOND)
   elif self.sid=='08':
    if i==0:note('밝기만으로 재질을 결정할 수 없음',YELLOW)
    if i==1:note('재질 색 × 조명 조건 × 관찰 조건',GREEN)
    if i==2:
     outline=Rectangle(width=2.8,height=2.1,color=GREEN,fill_opacity=.1).move_to(p(0,0));self.play(Create(outline),run_time=1);model.add(outline);note('문틀과 주변 벽의 밝기 비교',GREEN)
    if i==3:note('영상만으로 BRDF·광원 값을 역산하지 않음',SECOND)
    if i==4:note('다음은 직접 정한 조건의 계산',BLUE)
   elif self.sid=='11':
    if i==0:note('관찰한 픽셀색과 명암',RED)
    if i==1:
     replace(VGroup(*[Rectangle(width=.8,height=1.5,color=c,fill_color=c,fill_opacity=.7).move_to(p(-1.4+j*1.4,0)) for j,c in enumerate([RED,GREEN,BLUE])],*[label(k,-1.4+j*1.4,-1.2,c) for j,(k,c) in enumerate(zip(['R','G','B'],[RED,GREEN,BLUE]))]));note('표시색의 세 좌표 · 수치는 미측정',BLUE)
    if i==2:note('서로 다른 스펙트럼 → 같은 표시색 가능',YELLOW)
    if i==3:note('어두워짐 ≠ 재질 변경의 증거',SECOND)
    if i==4:note('색 표현과 에너지 단위를 따로 확인',GREEN)
   elif self.sid=='14':
    if i==0:note('실제 장면에는 여러 조건이 함께 변함',YELLOW)
    if i==1:
     for a in [PI/4,PI/2,3*PI/4]:
      start=np.array([np.cos(a),np.sin(a)])*1.5+np.array([0,-.6]);end=start+np.array([np.cos(a),np.sin(a)])*.8;ar=arrow(start,end,BLUE);self.play(Create(ar),run_time=.35);model.add(ar)
     note('법선: 각 위치에서 표면 바깥 방향',BLUE)
    if i==2:note('각도 하나만의 통제 실험은 아님',SECOND)
    if i==3:replace(VGroup(Line(p(-1.5,0),p(1.5,0),color=GREEN,stroke_width=9),arrow((0,0),(0,1.5),BLUE),*[arrow((x,1.8),(x,.25)) for x in [-1,0,1]],label('다음: 빛 고정, 판만 회전',0,-1.3)));note('다른 조건을 고정한 모형 비교',GREEN)
    if i==4:note('0°와 60°는 다음에 직접 정한 예제',YELLOW)
   elif self.sid=='17':
    if i==0:note('표면은 같아도 들어오는 빛은 달라질 수 있음',BLUE)
    if i==1:note('방출 Lₑ / 반사된 빛',YELLOW)
    if i==2:
     note('미리 보기 → 설치 → 조명 켜짐',GREEN)
     self.wait(2.0)
     replace(room(True));note('광원 → 벽 → 관찰자',GREEN)
    if i==3:note('밝아진 벽 ≠ 모두 발광 재질',YELLOW)
    if i==4:note('다음: 직접 조명과 간접 조명의 경로',BLUE)
   elif self.sid=='19':
    if i==0:note('그늘에서도 다른 빛을 받을 수 있음',BLUE)
    if i==1:note('특정 광원의 길이 막힘',YELLOW)
    if i==2:
     a=arrow((1.8,1.9),(.6,-.8),BLUE);b=arrow((2,-.4),(.8,-.9),GREEN);self.play(Create(a),Create(b),run_time=1.5);model.add(a,b);note('하늘·주변 표면에서 오는 다른 방향',GREEN)
    if i==3:note('내부 그림자 기법을 특정하지 않음',SECOND)
    if i==4:note('더 많은 표본 ≠ 밝기를 그대로 더하기',YELLOW)
   elif self.sid=='21':
    if i==0:note('어느 표면이 먼저 보이는가?',YELLOW)
    if i==1:note('선택한 표면에서 나가는 빛은 얼마인가?',GREEN)
    if i==2:
     replace(VGroup(Line(p(-1.5,0),p(1.5,0),color=GREEN,stroke_width=8),arrow((-1,1.8),(0,.1),YELLOW),arrow((0,.1),(1.5,1.5),BLUE),arrow((0,.1),(0,1.5),GREEN),label('입사광',-1.4,1.9,YELLOW),label('눈 쪽 반사',1.3,1.9,BLUE)));note('입사 방향 · 법선 · 나가는 방향')
    if i==3:note('표면 선택 → 단위 구분 → 방향별 합',YELLOW)
    if i==4:note('다음: 반사율0.6, 복사조도10',GREEN)
  if self.renderer.time<slot['seconds']:self.wait(slot['seconds']-self.renderer.time)
for sid in TITLES:globals()['Scene'+sid]=type('Scene'+sid,(Replacement,),{'sid':sid,'__module__':__name__})
