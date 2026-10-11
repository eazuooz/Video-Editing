"""Independent additive comparisons; defined right-handed model, white palette.

Model axes are drawing x/y/z directly (z up). These are expressly not measured
game axes. Only the additions use this model; all80 approved clips stay intact.
"""
from pathlib import Path
import json,os,sys,numpy as np
from manim import *
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'manim/projects/game-math-part2-full-series'))
from lesson import txt,fit,INK,MUTED,RULE,RED,BLUE,GOLD
from quaternion import screen_point,qmatrix,qaxis,qmul,qinverse,qrotate
TEAL='#327d7d';R=ROOT/'production/batches/game-math-part2-teaching-revision/cross-game-review-20261011/quaternion-four-game-v3'
CONTENT={s['id']:s for s in json.loads((R/'additions.json').read_text(encoding='utf8'))['scenes']}

def vec_arrow(origin,v,color=RED,scale=2.6):
 end=origin+np.asarray(v)*scale;direction=(end-origin)/np.linalg.norm(end-origin)
 shaft=Line3D(origin,end-.17*direction,color=color,thickness=.035,resolution=(3,8))
 tip=Cone(direction=direction,base_radius=.065,height=.17,resolution=(3,8),fill_color=color,fill_opacity=1,stroke_width=0).shift(end)
 return VGroup(shaft,tip)

def plane(origin,Rm=np.eye(3),scale=1):
 # Projected solid faces and crossing wing/fuselage provide actual depth.
 def box(dim,center,color):
  b=Cube(side_length=1,fill_color=color,fill_opacity=.78,stroke_color=RULE,stroke_width=.7)
  for i,size in enumerate(dim):b.stretch(size,i)
  return b.shift(center)
 g=VGroup(box([2.5,.24,.26],[0,0,0],GOLD),box([.43,2.5,.13],[.15,0,.28],BLUE),box([.38,.95,.10],[-.98,0,.16],BLUE),box([.38,.12,.6],[-.98,0,.44],TEAL))
 g.add(vec_arrow(ORIGIN,[1.7,0,0],RED,.9),vec_arrow(ORIGIN,[0,1.55,0],BLUE,.9),vec_arrow(ORIGIN,[0,0,1.35],TEAL,.9))
 return g.apply_matrix(Rm).scale(scale,about_point=ORIGIN).shift(origin)

def comparison_object(kind,origin):
 """Recognizable explanation models, never classified as actual game footage."""
 def block(dim,center,color):
  b=Cube(side_length=1,fill_color=color,fill_opacity=.86,stroke_color=RULE,stroke_width=.7)
  for i,size in enumerate(dim):b.stretch(size,i)
  return b.shift(center)
 if kind=='ski':
  g=VGroup(block([2.6,.22,.10],[0,-.26,0],BLUE),block([2.6,.22,.10],[0,.26,0],BLUE),
           block([.3,.62,.65],[0,0,.4],GOLD),block([.42,.48,.65],[0,0,1.02],TEAL),
           Sphere(radius=.25,resolution=(5,8),fill_color=GOLD,stroke_width=0).shift([0,0,1.65]))
 elif kind=='aircraft':return plane(origin,scale=.8)
 elif kind=='component':
  g=VGroup(block([.42,.42,2.25],[0,0,.65],TEAL),block([1.25,1,.26],[0,0,-.6],BLUE),
           block([.8,.7,.4],[0,0,1.62],GOLD))
 elif kind=='cannon':
  barrel=Cylinder(radius=.20,height=1.7,resolution=(5,12),fill_color=GOLD,fill_opacity=.86,stroke_color=RULE,stroke_width=.7)
  barrel.rotate(PI/2,axis=UP).shift([.45,0,.6])
  g=VGroup(block([1.65,.9,.33],[0,0,0],BLUE),block([.4,.6,.6],[-.25,0,.4],TEAL),barrel)
 else:raise ValueError(kind)
 g.add(vec_arrow(ORIGIN,[1.6,0,0],RED,.9))
 return g.scale(.82,about_point=ORIGIN).shift(origin)

class CrossGameQuaternion(ThreeDScene):
 sid='QF00'
 def construct(self):
  self.camera.background_color=WHITE;self.set_camera_orientation(phi=64*DEGREES,theta=-48*DEGREES,zoom=.85)
  s=CONTENT[self.sid];slug=f'game-math-quaternion-{s["episode"]}-v3'
  path=Path(os.environ.get('QUATERNION_COMPARISON_TIMING',str(ROOT/f'projects/{slug}/production/timeline.json')))
  preview=os.environ.get('QUATERNION_COMPARISON_PREVIEW')=='1'
  if preview:
   slot=dict(seconds=18,lineStarts=[0,8],sentenceCues=[])
  else:slot=next(x for x in json.loads(path.read_text(encoding='utf8'))['scenes'] if x['id']==self.sid)
  title=fit(txt(s['title'],34),12.5).to_corner(UL,buff=.6)
  note=fit(txt('정의한 설명 모형 · 오른손 / 열벡터 / wxyz · 게임 좌표계·각도 실측 아님',18,MUTED),12.5).move_to([0,2.7,0])
  self.add_fixed_in_frame_mobjects(title,note)
  labels={};cue_index=0
  def label(key,value,where=(3.15,.15,0),color=INK,size=28,width=6):
   if key in labels:self.remove(labels[key])
   alignment=ORIGIN if self.sid=='QC11' and key=='result' else LEFT
   obj=VGroup(*[fit(txt(part,size,color),width) for part in value.split(' / ')]).arrange(DOWN,aligned_edge=alignment,buff=.19).move_to(where)
   labels[key]=obj;self.add_fixed_in_frame_mobjects(obj);return obj
  def wait_to(t):
   if t>self.renderer.time:self.wait(t-self.renderer.time,frozen_frame=True)
  def sentence(fragment):
   nonlocal cue_index
   if preview:cue_index+=1;wait_to(min(14,2.5*cue_index));return
   if fragment in slot.get('fragmentCues',{}):wait_to(slot['fragmentCues'][fragment]);return
   cues=[c for c in slot['sentenceCues'] if fragment in c['text']]
   assert len(cues)==1,(self.sid,fragment,cues);wait_to(cues[0]['start'])
  def line(n):wait_to(slot['lineStarts'][n])
  def axes(origin,extent=2.65):
   g=VGroup(*[DashedLine(origin-extent*np.eye(3)[i],origin+extent*np.eye(3)[i],color=RULE,stroke_width=1.3) for i in range(3)])
   self.add(g)
   for i,(name,color) in enumerate([('x',RED),('y',BLUE),('z',TEAL)]):
    self.add_fixed_orientation_mobjects(txt(name,25,color).move_to(origin+(extent+.18)*np.eye(3)[i]))
   return g
  origin=screen_point(-3.2,-.1)
  if self.sid in ['QF00','QC00']:
   names=['라이더스 리퍼블릭','트레일메이커스','스페이스 엔지니어스','비시지']
   objects=VGroup(*[comparison_object(kind,screen_point(x,.25)) for kind,x in zip(['ski','aircraft','component','cannon'],[-4.9,-1.65,1.65,4.9])])
   self.add(objects)
   self.add_fixed_in_frame_mobjects(*[fit(txt(name,22,BLUE),3).move_to([x,-1.45,0]) for name,x in zip(names,[-4.9,-1.65,1.65,4.9])])
   label('step','처음 방향 → 적용할 회전 → 결과 방향',(0,-2.25,0),GOLD,29,12)
   sentence('비행기와 조립');self.play(*[Rotate(obj,PI/4,axis=RIGHT,about_point=obj.get_center()) for obj in objects],run_time=1.4)
   sentence('달라지고' if self.sid=='QF00' else '현재 방향');label('step','게임이 달라도 / 무엇을 바꿨는지 같은 질문으로 비교',(0,-2.1,0),GOLD,27,12)
  elif self.sid=='QF11':
   axes(origin);obj=plane(origin,scale=1.65);self.add(obj)
   label('main','x: 앞 / y: 한쪽 날개 / z: 위',color=GOLD)
   sentence('실제 게임');label('below','이 모형에서 정한 축',(3.15,-1.8,0),MUTED,24)
   line(1);self.play(Rotate(obj,PI/2,axis=RIGHT,about_point=origin),run_time=1.4)
   label('main','앞 x는 그대로 / 날개 y → 위 z',color=BLUE)
   sentence('네 성분');label('main','qₓ(90°) = (√2/2, √2/2, 0, 0) / 성분 순서: w, x, y, z',size=25)
   sentence('제트축 회전');label('below','각도가 같아도 / 회전축의 성분은 다름',(3.15,-1.75,0),GOLD,24)
  elif self.sid=='QF21':
   axes(origin);v=vec_arrow(origin,[1,0,0]);self.add(v)
   label('main','세워진 모습 / 전체 자세가 같은지는 별도 확인',color=GOLD,size=26)
   sentence('처음 방향');label('main','처음 방향 (1, 0, 0)',color=RED)
   sentence('제트축으로');self.play(Rotate(v,PI/2,axis=OUT,about_point=origin),run_time=1.2);label('main','+90° → (0, 1, 0)',color=BLUE)
   sentence('반대 구십');self.play(Rotate(v,-PI/2,axis=OUT,about_point=origin),run_time=1.2);label('main','−90° → (1, 0, 0)',color=RED)
   line(1);label('below','q⁻¹ q = 1 / 방향 연산을 정확히 되돌림',(3.15,-1.65,0),GOLD,26)
   sentence('부품을 놓은');label('main','방향의 역회전 / 배치 위치나 이동 기록을 지우지 않음',color=BLUE,size=25)
  elif self.sid=='QF31':
   axes(origin);a=vec_arrow(origin,[0,1,0],BLUE);b=vec_arrow(origin,[0,0,1],TEAL);g=VGroup(a,b);self.add(g)
   label('main','y · z = 0 / 서로 직각인 두 방향',color=BLUE)
   sentence('같은 구십');self.play(Rotate(g,PI/2,axis=RIGHT,about_point=origin),run_time=1.3)
   label('main','y → z / z → −y / 두 방향의 직각 유지',color=TEAL)
   sentence('방향마다 다른');label('below','한 회전을 함께 적용',(3.15,-1.85,0),GOLD,25)
   line(1);label('main','물체 모양보다 / 처음 방향과 회전 결과를 연결',color=GOLD)
   sentence('한 번 더');label('below','이제 같은 회전을 한 번 더 / 기존 q² 계산으로 연결',(3.15,-1.85,0),BLUE,24)
  elif self.sid=='QC11':
   a0=screen_point(-3.3,.05);b0=screen_point(3.3,.05)
   axes(a0,2.4);axes(b0,2.4);a=vec_arrow(a0,[0,0,1],RED);b=vec_arrow(b0,[0,0,1],RED);self.add(a,b)
   label('left','x축 90° → y축 90°',(-3.3,1.9,0),BLUE,25,5.9)
   label('right','y축 90° → x축 90°',(3.3,1.9,0),BLUE,25,5.9)
   label('result','같은 시작 (0, 0, 1) / 공간의 축은 고정',(0,-1.95,0),GOLD,26,12)
   sentence('공간의 엑스축');self.play(Rotate(a,PI/2,axis=RIGHT,about_point=a0),run_time=1)
   sentence('와이축으로')
   self.play(Rotate(a,PI/2,axis=UP,about_point=a0),run_time=1)
   label('left-result','(0, −1, 0)',(-3.3,-1.6,0),RED,29,5.9)
   line(1);self.play(Rotate(b,PI/2,axis=UP,about_point=b0),run_time=1)
   self.play(Rotate(b,PI/2,axis=RIGHT,about_point=b0),run_time=1)
   label('right-result','(1, 0, 0)',(3.3,-1.6,0),RED,29,5.9)
   sentence('마지막 방향');label('result','qᵧ qₓ ≠ qₓ qᵧ / 적용 순서를 바꾸면 결과도 달라짐',(0,-2,0),GOLD,26,12)
  elif self.sid=='QC21':
   axes(origin);a=vec_arrow(origin,[np.cos(PI/6),np.sin(PI/6),0],RED);target=vec_arrow(origin,[0,1,0],TEAL)
   target.set_opacity(.3);self.add(a,target)
   label('main','현재 A: z축 30° / 목표 B: z축 90°',color=GOLD)
   sentence('남은 회전');self.play(Rotate(a,PI/3,axis=OUT,about_point=origin),run_time=1.3);label('main','남은 D: z축 60° / 30° + 60° = 90°',color=BLUE)
   sentence('다시 더하는');label('below','목표 90°를 현재에 더하지 않음',(3.15,-1.8,0),RED,24)
   line(1);label('main','D A = B / D = B A⁻¹',color=BLUE,size=32)
   sentence('다른 축');label('below','각도 뺄셈은 이 같은 축 예시에 한함',(3.15,-1.8,0),GOLD,23)
  elif self.sid=='QC31':
   axes(origin);v=vec_arrow(origin,[1,0,1],RED);self.add(v)
   # Constant z plane and its projected rim make the retained height visible.
   square=Polygon(origin+[0,0,2.6],origin+[2.8,0,2.6],origin+[2.8,2.8,2.6],origin+[0,2.8,2.6],fill_color=TEAL,fill_opacity=.07,stroke_color=TEAL,stroke_width=1)
   self.add(square);label('main','처음 (1, 0, 1) / z 높이 성분은 1',color=RED)
   sentence('돌린 결과');self.play(Rotate(v,PI/2,axis=OUT,about_point=origin),run_time=1.4);label('main','z축 90° → (0, 1, 1) / 위쪽 성분 1은 그대로',color=BLUE)
   line(1);label('below','길이 √(1² + 1²) = √2 / 회전 전후 길이 보존',(3.15,-1.75,0),GOLD,25)
   sentence('내부 구현');label('main','q [0, v] q⁻¹ / 앞의 계산을 방향 변화로 읽기',color=BLUE,size=27)
  else:raise ValueError(self.sid)
  wait_to(slot['seconds'])

class QF00(CrossGameQuaternion):sid='QF00'
class QF11(CrossGameQuaternion):sid='QF11'
class QF21(CrossGameQuaternion):sid='QF21'
class QF31(CrossGameQuaternion):sid='QF31'
class QC00(CrossGameQuaternion):sid='QC00'
class QC11(CrossGameQuaternion):sid='QC11'
class QC21(CrossGameQuaternion):sid='QC21'
class QC31(CrossGameQuaternion):sid='QC31'
