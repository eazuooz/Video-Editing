"""Narrated, projected prerequisites using retained floor/point/triangle inputs.

White is the recorded theme of this already-started lecture. Each class is an
independent editable scene. All numbers are defined examples, not game measures.
"""
from pathlib import Path
import sys,json,os
import numpy as np
from manim import *
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'manim/projects/game-math-part2-full-series'))
from lesson import txt,fit,P,arrow,basis,INK,MUTED,RULE,RED,GREEN,BLUE,GOLD
from quaternion import screen_point
B=ROOT/'production/batches/game-math-part2-teaching-revision'
O=ROOT/'shared/output/game-math-part2-teaching-revision/planes'
CONTENT={s['id']:s for s in json.loads((B/'planes-flow-draft.json').read_text(encoding='utf8'))['additions']}
for current_slug in ['game-math-plane-distances-v2','game-math-triangle-addresses-v2']:
 current_lesson=ROOT/f'projects/{current_slug}/production/lesson.json'
 if current_lesson.exists():
  CONTENT.update({s['id']:s for s in json.loads(current_lesson.read_text(encoding='utf8'))['scenes'] if s['id'] in CONTENT})

class PlaneAddition(ThreeDScene):
 sid='PF01'
 def construct(self):
  self.camera.background_color=WHITE
  self.set_camera_orientation(phi=64*DEGREES,theta=-48*DEGREES,zoom=.85)
  record=CONTENT[self.sid];slot=json.loads((O/'combined-addition-timing.json').read_text(encoding='utf8'))[self.sid]
  if os.environ.get('REVISION_FINAL_TIMING')=='1':
   found=[]
   for slug in ['game-math-plane-distances-v2','game-math-triangle-addresses-v2']:
    f=ROOT/f'projects/{slug}/production/timeline.json'
    if f.exists():found.extend(s for s in json.loads(f.read_text(encoding='utf8'))['scenes'] if s['id']==self.sid)
   assert len(found)==1 and found[0]['voiceSha256']==slot['voiceSha256'];slot=found[0]
  total=slot['seconds'];starts=slot['lineStarts'];origin=screen_point(-3.2,-.15)
  self.add_fixed_in_frame_mobjects(fit(txt(record['title'],36),12.4).to_corner(UL,buff=.6),txt('같은 입력 → 계산 → 결과 / 숫자는 정의한 예제',19,MUTED).move_to([0,2.67,0]))
  texts={}
  def fixed(text,where,color=INK,size=27,width=6.05,height=1.3):
   g=VGroup(*[fit(txt(r,size,color),width) for r in text.split(' / ')]).arrange(DOWN,aligned_edge=LEFT,buff=.16)
   if g.height>height:g.scale(height/g.height)
   g.move_to(where);self.add_fixed_in_frame_mobjects(g);return g
  def note(text,color=INK):
   if 'note' in texts:self.remove(texts['note'])
   texts['note']=fixed(text,[3.2,-1.75,0],color)
  def equation(text,color=GOLD):
   if 'formula' in texts:self.remove(texts['formula'])
   texts['formula']=fixed(text,[3.2,.35,0],color,29)
  def caption(text):
   if 'caption' in texts:self.remove(texts['caption'])
   texts['caption']=fixed(text,[-3.2,-2.22,0],MUTED,21,5.5,.65)
  def wait_to(t):
   if t>self.renderer.time:self.wait(t-self.renderer.time,frozen_frame=True)
  def line(i):wait_to(starts[i])
  def sentence(fragment):
   cues=[c for c in slot.get('sentenceCues',[]) if fragment in c['text']]
   assert len(cues)==1,(self.sid,fragment,[c['text'] for c in cues]);wait_to(cues[0]['start'])
  def dot(q,color=GOLD):return Dot3D(q,radius=.085,color=color,resolution=(8,8))
  def floormap(q):return origin+.62*P@(np.array(q,dtype=float)-np.array([4,2,-3]))
  def floor():
   face=Polygon(*[floormap([x,2,z]) for x,z in [(1,-5),(7,-5),(7,-1),(1,-1)]],fill_color=BLUE,fill_opacity=.12,stroke_color=BLUE,stroke_width=2)
   rim=face.copy().shift(-.12*P[:,1]).set_fill(BLUE,.04)
   sides=VGroup(*[Polygon(face.get_vertices()[i],face.get_vertices()[(i+1)%4],rim.get_vertices()[(i+1)%4],rim.get_vertices()[i],fill_color=BLUE,fill_opacity=.07,stroke_color=RULE,stroke_width=.8) for i in range(4)])
   self.add(rim,sides,face);return VGroup(rim,sides,face)
  def trimap(q):return origin+.62*P@(np.array(q,dtype=float)-np.array([3,2,0]))
  def triangle():
   v=[trimap(q) for q in [[0,0,0],[6,0,0],[0,4,0]]]
   face=Polygon(*v,fill_color=BLUE,fill_opacity=.12,stroke_color=BLUE,stroke_width=2.5)
   depth=face.copy().shift(-.13*P[:,2]).set_fill(BLUE,.04)
   sides=VGroup(*[Polygon(v[i],v[(i+1)%3],v[(i+1)%3]-.13*P[:,2],v[i]-.13*P[:,2],fill_color=BLUE,fill_opacity=.07,stroke_color=RULE,stroke_width=.8) for i in range(3)])
   markers=VGroup(*[dot(q,c) for q,c in zip(v,[RED,GREEN,BLUE])]);self.add(depth,sides,face,markers)
   return VGroup(depth,sides,face,markers),v
  if self.sid=='PF01':
   ground=floor();q=dot(floormap([4,5,-3]));self.add(q)
   bound=Cube(side_length=1,fill_color=GREEN,fill_opacity=.045,stroke_color=GREEN,stroke_width=1.4).apply_matrix(P).move_to(q);self.add(bound)
   equation('앞 편: 연결선·경계 상자 / 겹침 → 검사할 후보');note('남은 질문 / 실제 표면에 닿았는가?',GREEN)
   line(1);self.play(FadeOut(bound),Create(Line3D(q.get_center(),floormap([4,2,-3]),color=RED,thickness=.025)),run_time=.8)
   equation('① 방향·거리·최근접점 / ② 유한한 삼각형의 주소·색');note('같은 점을 / 두 편의 질문으로 연결');caption('바닥 y=2 / 점(4,5,−3)을 계속 사용')
  elif self.sid=='PB01':
   floor();q=dot(floormap([4,5,-3]));self.add(q)
   tangent=arrow(floormap([4,2,-3]),floormap([6,2,-3]),GREEN);self.add(tangent)
   equation('따라가는 방향 / 면에서 떨어지는 방향');note('평면: 끝없이 이어지는 평평한 면',GREEN)
   sentence('법선은 그 면에');normal=arrow(floormap([4,2,-3]),floormap([4,3.5,-3]),RED);self.play(Create(normal),run_time=.7);equation('법선 n: 면에 수직 / 길이와 바닥 높이는 별개')
   line(1);equation('바닥 y=2 / 위 방향 n=(0,1,0)');note('같은 점·바닥 / 방향을 숫자로 정함')
   sentence('내적은');equation('n·p=0x+1y+0z / 같은 성분 곱하기 → 더하기');self.play(Indicate(q),run_time=.6)
   sentence('이 법선과');equation('n·p=y / 평면 위 조건 n·p=d=2');caption('빨강: 법선 / 초록: 면을 따라가는 방향')
  elif self.sid=='PB02':
   floor();q=dot(floormap([4,5,-3]));r=dot(floormap([4,2,-3]),BLUE);self.add(q,r)
   gap=Line3D(q.get_center(),r.get_center(),color=RED,thickness=.025);self.add(gap)
   equation('같은 바닥 y=2 / 같은 점의 y=5');note('수직 거리5−2=3',GREEN)
   sentence('방정식의 양쪽');equation('y=2 ↔ 2y=4 / 둘 다 같은 평면');self.play(Indicate(gap),run_time=.7)
   line(1);equation('잔차:5−2=3 / 2×5−4=6');note('식의 눈금만 두 배 / 물리적 간격은 그대로',RED)
   sentence('실제 수직 거리를');equation('n=(0,2,0), d=4 / ‖n‖=2 / 거리=(n·p−d)/‖n‖=6/2=3');self.play(Indicate(r),run_time=.7);caption('식의 잔차와 길이를 구분 / n과 d를 함께 배율 변경')
  elif self.sid=='PB03':
   floor();q=dot(floormap([4,5,-3]));end=dot(floormap([4,2,-3]),BLUE);self.add(q,end)
   equation('거리3을 알았음 / 남은 질문: 어디로 옮길까?');note('같은 점 p=(4,5,−3)',GREEN)
   line(1);diagonal=Line3D(q.get_center(),floormap([6,2,-3]),color=GREEN,thickness=.019);perp=Line3D(q.get_center(),end.get_center(),color=RED,thickness=.027);self.play(Create(diagonal),Create(perp),run_time=.85);equation('비스듬히: 옆으로도 이동 / 수직: 가장 짧은 길')
   sentence('같은 바닥의 높이');self.play(q.animate.move_to(end.get_center()),run_time=1);equation('(4,5,−3) → (4,2,−3) / x·z 유지 / y만2');note('기울어진 면에서도 / 단위 법선 방향으로 이동');caption('앞에서 구한 거리 → 실제 최근접 위치')
  elif self.sid=='PB04':
   tri,v=triangle();self.add(arrow(v[0],v[1],GREEN),arrow(v[0],v[2],BLUE))
   equation('이제 꼭짓점에서 면 방향 만들기 / 같은 시작점의 두 변');note('예제 전환 / xy면·수직 방향 z',GREEN);caption('y=2 바닥 → z=0 삼각형 / 전환을 먼저 설명')
   line(1);rectangle=Polygon(trimap([0,0,0]),trimap([6,0,0]),trimap([6,4,0]),trimap([0,4,0]),fill_color=GREEN,fill_opacity=.065,stroke_color=GREEN,stroke_width=2);self.play(Create(rectangle),run_time=.75);equation('두 변:6과4 / 평행사변형 넓이6×4=24')
   sentence('외적은');normal=arrow(trimap([2,1,0]),trimap([2,1,2.1]),RED);self.play(Create(normal),run_time=.75);equation('e₁×e₂=(0,0,24) / 방향:두 변에 수직 / 길이:평행사변형 넓이24')
   sentence('삼각형은');self.play(Indicate(tri),run_time=.7);equation('삼각형 넓이24/2=12 / 단위 법선(0,0,1)');note('방향의 순서 / 넓이의 크기를 구분')
  elif self.sid=='PC09':
   tri,v=triangle();equation('세 점 → 삼각형의 면 방향');note('더 큰 표면은 / 꼭짓점이 여러 개',GREEN)
   points=[trimap(q) for q in [[0,0,0],[3,0,0],[6,0,0],[6,4,0],[0,4,0]]]
   polygon=Polygon(*points,fill_color=BLUE,fill_opacity=.09,stroke_color=BLUE,stroke_width=2.5)
   self.play(FadeOut(tri),Create(polygon),run_time=.8);bad=VGroup(*[dot(q,RED) for q in points[:3]]);self.add(bad)
   sentence('거의 한 줄');equation('한 줄에 가까운 세 점 / 방향을 안정적으로 정하기 어려움');self.play(Indicate(bad),run_time=.65)
   line(1);self.remove(bad);walk=dot(points[0],GOLD);self.add(walk);equation('Newell:정렬된 경계의 이웃 기여 / 둘레 순서를 유지')
   for i in range(len(points)):
    edge=Line3D(points[i],points[(i+1)%len(points)],color=RED,thickness=.025);self.play(Create(edge),walk.animate.move_to(points[(i+1)%len(points)]),run_time=.4)
   note('마지막 → 첫 점으로 닫기 / 임의 순서의 점군 계산과 다름');caption('같은 평면 위의 경계 / 방향과 순서를 함께 확인')
  elif self.sid in ['PF02','PF03']:
   tri,v=triangle();q=dot(trimap([1.8,2,0] if self.sid=='PF02' else [4.2,2,0]));self.add(q)
   equation('방향 → 거리 → 최근접점 / 평면 자체에는 끝이 없음');note('유한한 발판의 경계는 / 별도 질문',GREEN)
   if self.sid=='PF02':
    line(1);self.play(q.animate.move_to(trimap([4.2,2,0])),run_time=1);equation('면 거리0 / 삼각형 경계는 넘음');note('다음 편 / 같은 평면에서 세 숫자로 위치 읽기');caption('평면 위 ≠ 실제 발판 안')
   else:
    line(1);self.play(Indicate(tri),run_time=.7);equation('① 길이·넓이 / ② 세 꼭짓점의 비율 / ③ 공면성·내부 검사·속성');note('앞 편의 바깥 점을 유지 / 안쪽 주소 예제와 이어서 비교');caption('6×4 삼각형 / 앞 편의 경계 밖 점(4.2,2,0)')
  elif self.sid=='PB05':
   tri,v=triangle();q=dot(trimap([1.8,2,0]));self.add(q)
   equation('변 길이 → 넓이 / 부분이 차지하는 비율');note('같은 삼각형 안의 / 점 주소를 준비',GREEN)
   line(1);small=Polygon(trimap([0,0,0]),trimap([4,0,0]),trimap([0,3,0]),fill_color=GREEN,fill_opacity=.10,stroke_color=GREEN,stroke_width=3);self.play(tri.animate.set_opacity(.2),FadeOut(q),Create(small),run_time=.8)
   equation('보존한 예:6×4, 넓이12 / 별도 비교 예:4×3, 넓이6');note('세 넓이 공식 비교 후 / 6×4 가중치 예로 복귀');caption('다른 삼각형으로 바뀐 이유와 복귀 지점을 명시')
  elif self.sid=='PB06':
   tri,v=triangle();q=dot((v[0]+v[1])/2);self.add(q)
   equation('두 점:½A+½B / 중간점');note('같은 생각을 / 세 꼭짓점으로 늘림',GREEN);caption('원래6×4 예제 / A·B·C 역할 유지')
   line(1);weights=[.2,.3,.5];end=trimap([1.8,2,0]);self.play(q.animate.move_to(end),run_time=1);equation('.2+.3+.5=1 / p=.2A+.3B+.5C / p=(1.8,2,0)');note('위치:길이 / 가중치:단위 없는 비율')
   sentence('이 비율이');caption('무게중심 좌표 / 실제 질량을 반드시 재는 뜻 아님')
  elif self.sid=='PB07':
   tri,v=triangle();q=trimap([1.8,2,0]);self.add(dot(q));equation('앞:비율 → p=(1.8,2,0) / 이번:같은 p → 비율');note('입력과 출력을 뒤집기 / 삼각형·점은 유지',GREEN)
   line(1);equation('전체 넓이6×4/2=12');parts=[]
   for i,color in enumerate([RED,GREEN,BLUE]):
    part=Polygon(q,v[(i+1)%3],v[(i+2)%3],fill_color=color,fill_opacity=.11,stroke_color=color,stroke_width=2);parts.append(part)
   sentence('점을 꼭짓점들과');self.play(*[Create(part) for part in parts],run_time=.9);equation('A 반대 부분2.4 / B 반대 부분3.6 / C 반대 부분6')
   sentence('십이로 나누면');equation('2.4/12=.2 / 3.6/12=.3 / 6/12=.5');note('원래 넣은 같은 비율을 되찾음',GREEN);caption('밖의 점도 표현하려면 부호 있는 넓이 유지')
  elif self.sid=='PB08':
   # Looking along the perpendicular first makes the true off-plane point
   # and its projection coincide. Orbit around the retained triangle centre
   # to expose the gap, rather than moving a supposedly stationary query.
   self.set_camera_orientation(phi=90*DEGREES,theta=-90*DEGREES)
   # Parallel projection preserves x/y coincidence for different depths.
   # Cairo's default perspective would rescale an off-plane point even
   # while looking along the normal, defeating this specific comparison.
   self.camera.set_focal_distance(1e6)
   origin=np.array([-3.2/.85,0,-.15/.85])
   tri,v=triangle();q=trimap([1.8,2,0]);a=dot(q,BLUE);off=trimap([1.8,2,7]);b=dot(off,GOLD);self.add(a,b)
   equation('같은 정면 위치로 보임 / 실제로 같은 표면 점인가?');note('투영된 위치 / 원래 위치는 별개',GREEN)
   line(1);self.move_camera(phi=72*DEGREES,theta=-62*DEGREES,run_time=1.2);gap=Line3D(q,off,color=RED,thickness=.022);self.play(Create(gap),run_time=.7);equation('p=(1.8,2,0) / q=(1.8,2,7) / xy 같음 / 면 거리0 대7');note('먼저 면 거리 / 그다음 투영 가중치 검사');caption('그림자 비유:위치 겹침만 / 실제 조명 계산 아님')
  elif self.sid=='PB09':
   tri,v=triangle();q=trimap([1.8,2,0]);marker=dot(q,GOLD);self.add(marker)
   equation('평면 위·삼각형 안 확인 / 같은 주소(.2,.3,.5)');note('다음 질문 / 이 위치에 어떤 값이 있을까?',GREEN)
   line(1);colors=[RED,GREEN,BLUE]
   for i,c in enumerate(colors):self.play(Indicate(tri[-1][i],color=c),run_time=.35)
   equation('정의한 선형 RGB / .2(1,0,0)+.3(0,1,0)+.5(0,0,1) / =(.2,.3,.5)');self.play(marker.animate.set_color(ManimColor((.2,.3,.5))),run_time=.65);note('위치 대신 저장 값 / 같은 비율로 보간');caption('게임 내부 구현·모든 화면 색의 계산 방식으로 단정하지 않음')
  else:raise RuntimeError(self.sid)
  assert self.renderer.time<=total+.05,(self.sid,self.renderer.time,total)
  wait_to(total)

for ident in CONTENT:globals()[ident]=type(ident,(PlaneAddition,),{'sid':ident,'__module__':__name__})
