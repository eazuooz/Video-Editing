"""Independent plane/triangle lessons; right-handed semantic coordinates."""
from geometry import screen_point,axes3
from lesson import *

def tri_flat(v,C,scale=.65,color=BLUE):
 return Polygon(*[C+scale*np.array([x,y,0.]) for x,y in v],color=color,stroke_width=3,fill_color=PALE,fill_opacity=.35)
def dot_flat(p,C,scale=.65,color=GOLD):
 return Dot(C+scale*np.array([p[0],p[1],0.]),color=color,radius=.08)
def linear_display(v):
 v=np.clip(np.array(v,float),0,1)
 return rgb_to_color(np.where(v<=.0031308,12.92*v,1.055*v**(1/2.4)-.055))

class PlaneTriangleScene(ThreeDScene):
 slug='';sid='';fixed=LectureScene.fixed;replace_fixed=LectureScene.replace_fixed
 def construct(self):
  self.camera.background_color=WHITE;self.set_camera_orientation(phi=64*DEGREES,theta=-48*DEGREES,zoom=.85)
  data=json.loads((ROOT/f'production/batches/game-math-part2-full-series/lessons/{self.slug}.json').read_text(encoding='utf8'))
  s=next(x for x in data['scenes'] if x['id']==self.sid);slot=next(x for x in timing(self.slug,data)['scenes'] if x['id']==self.sid);mode=s['mode']
  title=fit(txt(s['title'],40),12.65).to_corner(UL,buff=.6)
  sub=fit(txt('게임수학 Part 2 / 기하 2편 · 오른손 / 같은 좌표계 / 평면과 표면 경계 구분',20,MUTED),12.65).next_to(title,DOWN,aligned_edge=LEFT,buff=.14)
  self.fixed(title,sub,Line([-6.5,2.63,0],[6.5,2.63,0],color=RULE,stroke_width=1))
  full=mode=='overview';active=eq=note=None;obj=[];labels=[];dots=[];special=None
  C=np.array([-5.5,-1.3,0.]);V=np.array([[0,0],[6,0],[0,4]],float);O=screen_point(-3.35,-.1)
  def equation(v,color=GOLD):
   nonlocal eq
   eq=self.replace_fixed(eq,fit(txt(v,27,color),11.8 if full else 5.9).move_to([0 if full else 3.15,-.65,0]))
  def foot(v,color=GREEN):
   nonlocal note
   note=self.replace_fixed(note,fit(txt(v,22,color),11.8 if full else 5.9).move_to([0 if full else 3.15,-2.13,0]))
  def flat_triangle(v=V,scale=.65):
   poly=tri_flat(v,C,scale);self.fixed(poly)
   for j,(p,color) in enumerate(zip(v,[RED,GREEN,BLUE])):
    d=dot_flat(p,C,scale,color);label=txt(f'v{j+1}',23,color).next_to(d,DOWN if j<2 else UP,buff=.12);self.fixed(d,label);dots.append(d);labels.append(label)
   return poly
  if full:
   special=VGroup(*[card(v,width=3.8,size=27) for v in ['법선·거리·투영','삼각형·넓이','가중치·공면성·속성']]).arrange(RIGHT,buff=.35).move_to([0,-.05,0]);self.fixed(special)
   self.fixed(VGroup(*[Arrow(special[j].get_right(),special[j+1].get_left(),buff=.04,color=MUTED) for j in range(2)]))
  elif mode in ['affine-plane','plane-distance','plane-projection','planes-practice']:
   scale=.47;origin=O-scale*P@np.array([2.5,2,0.]);pos=lambda p:origin+scale*P@np.array(p,float)
   surface=lambda y,color:Polygon(*[pos(p) for p in [(-1,y,-4),(6,y,-4),(6,y,3),(-1,y,3)]],color=color,stroke_width=2,fill_opacity=.20,fill_color=color)
   plane=surface(2,BLUE);self.add(plane)
   normal=arrow(pos([1,2,0]),pos([1,4.4,0]),GREEN,4);self.add(normal)
   ax=axes3(pos([0,0,0]),1.0);self.add(ax);legend=txt('x / y↑ / z · 논리 좌표',20,MUTED).move_to([-3.35,-2.13,0]);self.fixed(legend)
   if mode=='affine-plane':
    old=surface(0,RULE);self.add(old);obj=[old,plane,normal,pos]
   else:
    p=Dot3D(pos([4,5,-3]),radius=.08,color=GOLD,resolution=(8,8));p0=Dot3D(pos([4,2,-3]),radius=.08,color=GREEN,resolution=(8,8))
    measure=DashedLine(p0.get_center(),p.get_center(),color=GOLD,stroke_width=3);self.add(p,p0,measure);obj=[p,p0,measure,normal,pos]
  elif mode=='plane-three-points':
   scale=.56;origin=O-scale*P@np.array([2,1.2,0.]);pos=lambda p:origin+scale*P@np.array(p,float)
   vs=np.array([[0,0,0],[6,0,0],[0,4,0]],float);poly=Polygon(*[pos(p) for p in vs],color=BLUE,fill_color=PALE,fill_opacity=.45,stroke_width=2);self.add(poly)
   edges=VGroup(arrow(pos(vs[0]),pos(vs[1]),RED),arrow(pos(vs[0]),pos(vs[2]),GREEN));self.add(edges)
   normal=arrow(pos(vs[0]),pos(vs[0]+[0,0,2.5]),BLUE);obj=[poly,edges,normal,pos,vs]
   self.fixed(txt('원점에서 같은 시작점의 두 변',20,MUTED).move_to([-3.35,-2.13,0]))
  elif mode=='newell-ordered':
   vs=np.array([[0,0],[4,0],[4,2],[2,3],[0,2]],float);poly=tri_flat(vs,C,.75);self.fixed(poly);obj=[poly,vs]
   special=VGroup(*[Arrow(C+.75*np.r_[p,0],C+.75*np.r_[q,0],buff=.12,color=[RED,GREEN,BLUE,GOLD,MUTED][j],stroke_width=3) for j,(p,q) in enumerate(zip(vs,np.roll(vs,-1,axis=0)))])
   self.fixed(*[txt(str(j),22,col).move_to(C+.75*np.r_[p,0]+(.22*LEFT if p[0]==0 else .22*RIGHT)) for j,(p,col) in enumerate(zip(vs,[RED,GREEN,BLUE,GOLD,MUTED]))])
  elif mode in ['triangle-laws','triangle-area']:
   V=np.array([[0,0],[4,0],[0,3]],float);poly=flat_triangle(V,.95);obj=[poly]
   self.fixed(txt('4',25,RED).move_to(C+[1.9,-.45,0]),txt('3',25,GREEN).move_to(C+[-.45,1.43,0]),txt('5',25,BLUE).move_to(C+[2.12,1.63,0]))
   right=Square(side_length=.25,color=MUTED,stroke_width=2).move_to(C+[.125,.125,0]);self.fixed(right)
  elif mode in ['barycentric-basis','barycentric-worked','barycentric-areas','barycentric-attributes']:
   poly=flat_triangle();p=dot_flat([0,0],C,color=GOLD);self.fixed(p);obj=[poly,p]
   self.fixed(txt('XY 삼각형 / z=0',20,MUTED).move_to([-3.35,-2.13,0]))
   if mode=='barycentric-attributes':
    # Show linear attributes through an sRGB display transfer, rather than
    # claiming raw display bytes are physically linear light values.
    patches=VGroup();N=16
    def at(i,j):return C+.65*np.array([6*i/N,4*j/N,0.])
    for i in range(N):
     for j in range(N-i):
      pts=[(i,j),(i+1,j),(i,j+1)];w=np.mean([[1-(x+y)/N,x/N,y/N] for x,y in pts],axis=0)
      patches.add(Polygon(*[at(x,y) for x,y in pts],fill_color=linear_display(w),fill_opacity=1,stroke_width=0))
      if i+j<N-1:
       pts=[(i+1,j),(i+1,j+1),(i,j+1)];w=np.mean([[1-(x+y)/N,x/N,y/N] for x,y in pts],axis=0)
       patches.add(Polygon(*[at(x,y) for x,y in pts],fill_color=linear_display(w),fill_opacity=1,stroke_width=0))
    obj.append(patches)
  elif mode=='barycentric-coplanarity':
   origin=screen_point(-3.35,.45)-.29*P@np.array([2,1.5,0.]);pos=lambda p:origin+.29*P@np.array(p,float)
   poly=Polygon(*[pos(p) for p in [[0,0,0],[6,0,0],[0,4,0]]],color=BLUE,fill_color=PALE,fill_opacity=.5);self.add(poly)
   p=Dot3D(pos([1.8,2,0]),color=GREEN,radius=.07,resolution=(8,8));q=Dot3D(pos([1.8,2,7]),color=RED,radius=.07,resolution=(8,8));line=DashedLine(p.get_center(),q.get_center(),color=GOLD,stroke_width=3);self.add(p);obj=[poly,p,q,line]
   mini=np.array([-4.15,-1.62,0.]);self.fixed(tri_flat(V,mini,.30),dot_flat([1.8,2],mini,.30,GOLD),txt('동일 XY 투영',20,MUTED).move_to([-3.35,-2.13,0]))
  else:raise ValueError('Unimplemented independent plane/triangle mode: '+mode)
  for i,beat in enumerate(s['beats']):
   ts=slot['lineStarts'][min(i,len(slot['lineStarts'])-1)]
   if ts>self.renderer.time+1/60:self.wait(ts-self.renderer.time,frozen_frame=True)
   active=self.replace_fixed(active,card(beat,width=12 if full else 6,size=25,color=GREEN if i==len(s['beats'])-1 else BLUE).move_to([0 if full else 3.15,1.66,0]))
   if full:self.play(Indicate(special[max(0,min(i-1,2))],color=GREEN),run_time=.55)
   elif mode=='affine-plane':
    vals=['법선 n: 표면에 수직','n·p=d','n=(0,1,0), d=2','y=0 / y=2: 원점 포함 여부','n·(p-q)=0','(n,d) ↔ (-n,-d)'];equation(vals[i])
    if i==3:self.play(Indicate(obj[0],color=GOLD),Indicate(obj[1],color=BLUE),run_time=.65)
    if i==5:
     pos=obj[3];target=arrow(pos([1,2,0]),pos([1,-.4,0]),RED,4);self.play(Transform(obj[2],target),run_time=.8);foot('평면은 유지 / 앞·뒤 방향만 반전')
   elif mode=='plane-distance':
    vals=['F(p)=n·p-d','n=(0,2,0), d=4, ‖n‖=2','F(4,5,-3)=10-4=6','signedDistance=6/2=3','n̂=(0,1,0), d̂=2','‖n‖=0이면 정규화 거절'];equation(vals[i],RED if i==5 else GOLD)
    if i==3:self.play(Indicate(obj[2],color=GOLD),run_time=.7)
    if i==4:foot('법선과 d를 함께 나누기')
   elif mode=='plane-projection':
    vals=['거리 +3 / n̂=(0,1,0)','p₀=(4,2,-3)','p₀=p-signedDistance·n̂','p₀=p-[(n·p-d)/(n·n)]n','거리 -2: 뒤에서 평면으로','투영 후 유한 표면 경계 검사'];equation(vals[i])
    if i==1:self.play(obj[0].animate.move_to(obj[1].get_center()).set_color(GREEN),run_time=1.0)
    if i==4:
     pos=obj[4];self.play(obj[0].animate.move_to(pos([4,0,-3])).set_color(RED),run_time=.65);self.play(obj[0].animate.move_to(obj[1].get_center()).set_color(GREEN),run_time=.9)
    if i==5:foot('무한 평면의 최근접점 / 삼각형 최근접점과 구분')
   elif mode=='plane-three-points':
    vals=['e₁=v₂-v₁ / e₂=v₃-v₁','(6,0,0) × (0,4,0)','외적=(0,0,24), n̂=(0,0,1)','e₂×e₁ = -(e₁×e₂)','d=n·v₁=0','‖e₁×e₂‖≈0: 퇴화·오차 검사'];equation(vals[i])
    if i==2:self.play(Create(obj[2]),run_time=.8)
    if i==3:
     pos=obj[3];self.play(Transform(obj[2],arrow(pos([0,0,0]),pos([0,0,-2.5]),RED)),run_time=.8)
    if i==5:foot('외적이 유효할 때만 나누기',RED)
   elif mode=='newell-ordered':
    vals=['세 점 선택의 공선·오목 오류','닫힌 둘레: i → i+1, 마지막 → 0','n_z=Σ(xᵢ-xᵢ₊₁)(yᵢ+yᵢ₊₁)','둘레 순서 반전 → n 부호 반전','d=n·평균(vᵢ)','일반 점군의 최소제곱과 구분'];equation(vals[i])
    if i==1:self.fixed(special);self.play(LaggedStart(*[Create(x) for x in special],lag_ratio=.12),run_time=1.0)
    if i==2:self.play(Indicate(special[0],color=GOLD),run_time=.6);foot('x,y,z 성분을 순환해서 각각 누적')
    if i==3:self.play(Indicate(special,color=RED),run_time=.6)
    if i==5:foot('유효한 순서·점 개수·비영 면적 확인')
   elif mode=='triangle-laws':
    vals=['aᵢ: vᵢ 맞은편 변의 길이','P=3+4+5=12 / s=6','a₁/sinθ₁=a₂/sinθ₂=a₃/sinθ₃','a₁²=a₂²+a₃²-2a₂a₃cosθ₁','3²+4²=5²','길이>0 / 삼각부등식 / 각도 단위'];equation(vals[i])
    if i==0:foot('a₁=5, a₂=3, a₃=4 / θ₁=90°')
    if i==4:self.play(Indicate(obj[0],color=GREEN),run_time=.6);foot('이 예제의 θ₁=90° / cosθ₁=0')
   elif mode=='triangle-area':
    vals=['A=4×3/2=6','A=√[s(s-a)(s-b)(s-c)]','√(6×3×2×1)=6','A=‖e₁×e₂‖/2=12/2=6','signedArea=det(e₁,e₂)/2','3D 넓이는 크기 / 방향은 법선'];equation(vals[i])
    if i==3:
     parallelogram=Polygon(C,C+[3.8,0,0],C+[3.8,2.85,0],C+[0,2.85,0],color=GREEN,fill_opacity=.08);self.fixed(parallelogram);self.play(Create(parallelogram),run_time=.7)
    if i==4:foot('순서 반전: +6 ↔ -6 / 크기는 6')
   elif mode=='barycentric-basis':
    vals=['λ₁+λ₂+λ₃=1','v₁: (1,0,0)','변 중간: (.5,.5,0) / 평균: (⅓,⅓,⅓)','독립 값 2개 / 평면 위 위치','p=v₃+λ₁(v₁-v₃)+λ₂(v₂-v₃)','공면 + 모두 λ≥0: 내부·경계'];equation(vals[i])
    if i==2:self.play(obj[1].animate.move_to(dot_flat([3,0],C).get_center()),run_time=.7);self.play(obj[1].animate.move_to(dot_flat([2,4/3],C).get_center()),run_time=.7)
    if i==4:
     edges=VGroup(Arrow(dots[2].get_center(),dots[0].get_center(),buff=.08,color=RED),Arrow(dots[2].get_center(),dots[1].get_center(),buff=.08,color=GREEN));self.fixed(edges);self.play(Create(edges),run_time=.75)
    if i==5:foot('공면성 검사와 음수 가중치의 뜻')
   elif mode=='barycentric-worked':
    vals=['v₁=(0,0,0), v₂=(6,0,0), v₃=(0,4,0)','x=.3×6=1.8 / y=.5×4=2','p=(1.8,2,0) / 내부','λ=(-.2,.7,.5), 합=1','p=(4.2,2,0) / 바깥','λ: 비율 / p: 길이 단위'];equation(vals[i])
    if i==2:self.play(obj[1].animate.move_to(dot_flat([1.8,2],C).get_center()).set_color(GREEN),run_time=.85)
    if i==4:self.play(obj[1].animate.move_to(dot_flat([4.2,2],C).get_center()).set_color(RED),run_time=.9)
   elif mode=='barycentric-areas':
    vals=['λᵢ=Aᵢ_signed/A_total_signed','A_total=12 / 부분=2.4,3.6,6','절댓값만 쓰면 바깥 부호 손실','바깥 λ=(-.2,.7,.5)','분자·분모가 함께 반전 → 같은 λ','A≈0: 나누기·수치 불안정 검사'];equation(vals[i])
    if i in [1,3]:
     for p in obj[2:]:self.remove(p)
     obj=obj[:2];q=np.array([1.8,2]) if i==1 else np.array([4.2,2]);self.play(obj[1].animate.move_to(dot_flat(q,C).get_center()).set_color(GREEN if i==1 else RED),run_time=.65)
     patches=VGroup(*[tri_flat([q,V[(j+1)%3],V[(j+2)%3]],C,color=c).set_fill(c,opacity=.22) for j,c in enumerate([RED,GREEN,BLUE])]);self.fixed(patches);obj.append(patches)
    if i==5:foot('공면성·분모·좌표 단위 모두 검사',RED)
   elif mode=='barycentric-coplanarity':
    vals=['p=(1.8,2,0), q=(1.8,2,7)','같은 XY / 다른 z / 평면 거리 7','가장 큰 |nᵢ|의 축을 버려 투영','평면 거리 검사 + 투영 내부 검사','거리 ε: 길이 / 가중치 ε: 비율','finite ∧ normal ∧ area ∧ coplanar'];equation(vals[i])
    if i==1:self.play(FadeIn(obj[2]),Create(obj[3]),run_time=.9)
    if i==3:foot('XY 가중치만으로 q를 표면 안이라 하지 않기',RED)
   elif mode=='barycentric-attributes':
    vals=['a(p)=λ₁a₁+λ₂a₂+λ₃a₃','정의한 선형 RGB: R / G / B','RGB=(.2,.3,.5)','변 중간은 평균 / 꼭짓점은 그대로','높이·UV·방향: 속성에 맞는 후처리','표면 아핀 보간 / 원근 보정은 별도'];equation(vals[i])
    if i==1:self.fixed(obj[2]);self.play(FadeIn(obj[2]),run_time=.8);self.bring_to_front(*dots,*labels,obj[1])
    if i==2:self.play(obj[1].animate.move_to(dot_flat([1.8,2],C).get_center()),run_time=.85)
    if i==3:self.play(obj[1].animate.move_to(dot_flat([3,0],C).get_center()),run_time=.7);self.play(obj[1].animate.move_to(dots[1].get_center()),run_time=.7)
    if i==5:foot('선형 속성을 표시색으로 변환 / 숨은 셰이더 추정 없음')
   elif mode=='planes-practice':
    vals=['n=(0,2,0), d=4, p=(4,5,-3)','거리=3 / p₀=(4,2,-3)','λ=(.2,.3,.5) → (1.8,2,0)','q=(1.8,2,7): 공면성에서 거절','입력 → 평면 → 가중치 → 속성','다음: 삼각형 중심 / 다각형 분할'];equation(vals[i])
    if i==1:self.play(obj[0].animate.move_to(obj[1].get_center()).set_color(GREEN),run_time=.9)
    if i==2:
     self.remove(plane,normal,ax,legend,*obj[:3])
     triangle_origin=O-.40*P@np.array([2,1.5,0.]);triangle_pos=lambda p:triangle_origin+.40*P@np.array(p,float)
     triangle=Polygon(*[triangle_pos(v) for v in [[0,0,0],[6,0,0],[0,4,0]]],color=BLUE,fill_color=PALE,fill_opacity=.5)
     inside=Dot3D(triangle_pos([1.8,2,0]),radius=.08,color=GREEN,resolution=(8,8));outside=Dot3D(triangle_pos([1.8,2,7]),radius=.08,color=RED,resolution=(8,8))
     depth=DashedLine(inside.get_center(),outside.get_center(),color=GOLD,stroke_width=3);self.add(triangle,inside);obj=[triangle,inside,outside,depth]
     self.fixed(txt('삼각형 z=0 / 초록 p · 빨강 q',20,MUTED).move_to([-3.35,-2.13,0]))
    if i==3:self.play(FadeIn(obj[2]),Create(obj[3]),run_time=.85);foot('같은 XY 투영이어도 q는 z=0 평면 밖',RED)
    if i==4:foot('좌표계와 각 단계의 단위·허용 오차 확인')
  remaining=slot['seconds']-self.renderer.time
  if remaining>1/60:self.wait(remaining,frozen_frame=True)

def make_scenes(slug,module):
 data=json.loads((ROOT/f'production/batches/game-math-part2-full-series/lessons/{slug}.json').read_text(encoding='utf8'))
 return {'Scene'+s['id']:type('Scene'+s['id'],(PlaneTriangleScene,),{'slug':slug,'sid':s['id'],'__module__':module}) for s in data['scenes'] if s['kind']=='explanation'}
