"""Independent white2.5D/3D geometry explanations; every diagram is explanation."""
from lesson import *
from itertools import product

def screen_point(x,y):
 phi,theta=64*DEGREES,-48*DEGREES
 return (x*np.array([-np.sin(theta),np.cos(theta),0.])+y*np.array([-np.cos(phi)*np.cos(theta),-np.cos(phi)*np.sin(theta),np.sin(phi)]))/.85

def box_wire(lo,hi,O,scale=.22,R=None,color=BLUE,width=2):
 lo,hi=np.array(lo,float),np.array(hi,float);R=np.eye(3) if R is None else R
 ps=[np.array(v,float) for v in product(*zip(lo,hi))]
 edges=VGroup()
 for i,p in enumerate(ps):
  for j,q in enumerate(ps):
   if j>i and sum(a!=b for a,b in zip(p,q))==1:
    edges.add(Line(O+scale*P@R@p,O+scale*P@R@q,color=color,stroke_width=width))
 return edges

def axes3(O,scale=1.8):
 return VGroup(*[arrow(O,O+scale*P[:,j],c,2) for j,c in enumerate([RED,GREEN,BLUE])])

class GeometryScene(ThreeDScene):
 slug='';sid=''
 fixed=LectureScene.fixed
 replace_fixed=LectureScene.replace_fixed
 def construct(self):
  self.camera.background_color=WHITE
  self.set_camera_orientation(phi=64*DEGREES,theta=-48*DEGREES,zoom=.85)
  data=json.loads((ROOT/f'production/batches/game-math-part2-full-series/lessons/{self.slug}.json').read_text(encoding='utf8'))
  s=next(v for v in data['scenes'] if v['id']==self.sid);slot=next(v for v in timing(self.slug,data)['scenes'] if v['id']==self.sid);mode=s['mode']
  title=fit(txt(s['title'],40),12.65).to_corner(UL,buff=.6)
  sub=fit(txt(f'게임수학 Part 2 / 기하 {data["part"]}편 · 오른손 / 열벡터 / 좌표·단위 명시',20,MUTED),12.65).next_to(title,DOWN,aligned_edge=LEFT,buff=.14)
  self.fixed(title,sub,Line([-6.5,2.63,0],[6.5,2.63,0],color=RULE,stroke_width=1))
  full=mode in ['overview','point-bounds'];C=np.array([-3.35,-.18,0.]);O=screen_point(-3.35,-.1)
  formula=note=active=codehl=None;objects=[];dots=[];special=None
  def fixed2(*m):self.fixed(*m)
  def seteq(v,color=GOLD):
   nonlocal formula
   formula=self.replace_fixed(formula,fit(txt(v,27,color),11.8 if full else 5.9).move_to([0 if full else 3.15,-.6,0]))
  def setnote(v,color=GREEN):
   nonlocal note
   note=self.replace_fixed(note,fit(txt(v,22,color),11.8 if full else 5.9).move_to([0 if full else 3.15,-2.13,0]))
  if mode=='overview':
   special=VGroup(*[card(v,width=3.8,size=27) for v in ['선·범위·단위','구·표면·내부','상자 생성·변환']]).arrange(RIGHT,buff=.35).move_to([0,-.05,0]);fixed2(special)
   fixed2(VGroup(*[Arrow(special[j].get_right(),special[j+1].get_left(),buff=.04,color=MUTED) for j in range(2)]))
  elif mode in ['forms','conic']:
   grid=NumberPlane(x_range=[-1,5,1] if mode=='conic' else [-3,3,1],y_range=[-1,5,1] if mode=='conic' else [-2,2,1],x_length=3.9 if mode=='conic' else 5.6,y_length=3.9 if mode=='conic' else 3.5,background_line_style={'stroke_color':RULE,'stroke_width':.6,'stroke_opacity':.6},axis_config={'stroke_color':MUTED,'stroke_width':1}).move_to(C)
   center=C if mode=='forms' else grid.c2p(0,0);r=.65 if mode=='conic' else 1.15
   circle=Circle(radius=r,color=BLUE,stroke_width=3).move_to(center);centerDot=Dot(center,color=INK)
   dot=Dot(center+r*RIGHT,color=GOLD,radius=.09);radius=Line(center,dot.get_center(),color=GREEN)
   fixed2(grid,circle,centerDot,dot,radius);objects=[grid,circle,centerDot,dot,radius]
   fixed2(txt('x',21,RED).next_to(grid,RIGHT),txt('y',21,GREEN).next_to(grid,UP))
  elif mode in ['domains','ray-units']:
   X=C+[-2.2,-.5,0];Y=C+[1.15,1.05,0]
   if mode=='domains':
    v=(Y-X);line=Line(X-v*.28,Y+v*.3,color=RULE,stroke_width=3)
    segment=Line(X,Y,color=BLUE,stroke_width=5);ray=Arrow(X,Y+v*.32,buff=0,color=GREEN)
    fixed2(line,segment,Dot(X,color=RED),Dot(Y,color=GREEN),txt('o / t=0',22,RED).next_to(Dot(X),DOWN),txt('끝 / t=1',22,GREEN).next_to(Dot(Y),UP))
    dot=Dot(X,color=GOLD,radius=.1);fixed2(dot);objects=[line,segment,ray,dot,X,Y]
   else:
    X=C+[-2.0,-.8,0];Y=C+[1.65,1.02,0];mid=(X+Y)/2
    fixed2(Line(X,Y,color=BLUE,stroke_width=4),Dot(X,color=RED),Dot(Y,color=GREEN))
    fixed2(txt('(2,1)',23,RED).next_to(Dot(X),DOWN),txt('(8,4)',23,GREEN).next_to(Dot(Y),UP))
    dot=Dot(X,color=GOLD,radius=.1);fixed2(dot);objects=[dot,mid]
  elif mode=='line-normal':
   left=C+[-1.25,-.65,0];right=C+[1.25,-.65,0];mid=(left+right)/2
   line=Line(mid+2.15*DOWN,mid+1.95*UP,color=BLUE,stroke_width=3)
   fixed2(Line(left,right,color=RULE),Dot(left,color=RED),Dot(right,color=GREEN),line)
   fixed2(txt('q=(0,0)',21,RED).next_to(Dot(left),DOWN),txt('r=(2,0)',21,GREEN).next_to(Dot(right),DOWN),txt('x=1',24,BLUE).next_to(line,UP))
   norm=Arrow(mid,mid+2.5*RIGHT,buff=0,color=GOLD);dots=[norm,Dot(mid,color=GOLD)]
  elif mode=='sphere-test':
   sphere=Sphere(radius=1.38,resolution=(14,20),fill_color=PALE,fill_opacity=.32,stroke_color=BLUE,stroke_width=.6).shift(O)
   self.add(sphere,axes3(O,1.9));dot=Dot3D(O,radius=.1,color=GREEN,resolution=(8,8));self.add(dot);objects=[sphere,dot]
   fixed2(txt('중심 c / 3D 구의 표면',22,MUTED).move_to([-3.35,-2.14,0]))
  elif mode=='sphere-measures':
   small=Sphere(radius=.66,resolution=(12,18),fill_color=PALE,fill_opacity=.75,stroke_color=BLUE,stroke_width=.6).shift(screen_point(-4.7,-.15))
   big=Sphere(radius=1.32,resolution=(12,18),fill_color=PALE,fill_opacity=.75,stroke_color=GREEN,stroke_width=.6).shift(screen_point(-2.5,-.15))
   self.add(small,big);objects=[small,big]
   fixed2(txt('r',26,BLUE).move_to([-4.7,-1.85,0]),txt('2r',26,GREEN).move_to([-2.5,-1.85,0]))
  elif mode=='box-data':
   self.add(axes3(O,1.85));b=box_wire([-1.8,-1.2,-.8],[1.8,1.2,.8],O,scale=.77,color=BLUE);self.add(b);objects=[b]
   d=Dot3D(O,radius=.08,color=GOLD,resolution=(8,8));self.add(d);objects.append(d)
   fixed2(txt('x / y↑ / z: 고정 기준축',21,MUTED).move_to([-3.35,-2.15,0]))
  elif mode=='point-bounds':
   # Independent explanatory diagram + editable syntax-colored code.
   special=VGroup(*[Text(v,font='Consolas',font_size=21,color=INK,t2c={'if':RED,'min':BLUE,'max':GREEN,'finite':GOLD,'return':GREEN}) for v in ['if empty(points): return EMPTY','require(all_finite(points))','lo = hi = points[0]','for p in points[1:]:','    lo = component_min(lo,p)','    hi = component_max(hi,p)']]).arrange(DOWN,aligned_edge=LEFT,buff=.16);fit(special,6.15);special.move_to([3.2,-.25,0]);fixed2(special)
   pts=np.array(s['points'],float);center=np.array([1,2,1.5]);origin=screen_point(-4.65,-.12)
   colors=[RED,GREEN,BLUE,GOLD,MUTED]
   dots=VGroup(*[Dot3D(origin+.14*P@(p-center),radius=.065,color=c,resolution=(6,6)) for p,c in zip(pts,colors)]);self.add(dots)
   table=VGroup(*[txt(f'({p[0]:g},{p[1]:g},{p[2]:g})',20,c,font='Consolas') for p,c in zip(pts,colors)]).arrange(DOWN,buff=.21).move_to([-1.55,-.1,0]);fixed2(table,txt('입력점 (x,y,z)',18,MUTED).move_to([-1.55,1.08,0]))
   objects=[pts,center,origin]
  elif mode=='proxy-overlap':
   u=np.array([np.sqrt(.5),np.sqrt(.5),0]);n=np.array([-u[1],u[0],0]);centers=[C-.32*n,C+.32*n]
   for center,col in zip(centers,[BLUE,GREEN]):
    pts=[center+.55*(a*u+b*n) for a,b in [(-3,-.1),(3,-.1),(3,.1),(-3,.1)]]
    poly=Polygon(*pts,color=col,fill_opacity=.42,stroke_width=3);fixed2(poly);objects.append(poly)
   boxes=VGroup(*[Rectangle(width=obj.width,height=obj.height,stroke_color=col,stroke_width=2,fill_opacity=.08,fill_color=col).move_to(obj) for obj,col in zip(objects,[BLUE,GREEN])]);objects.append(boxes)
   fixed2(txt('평면 단면 / 실제 두 도형은 분리',20,MUTED).move_to([-3.35,-2.15,0]))
  elif mode=='rotated-minmax':
   square=Square(side_length=2.4,color=BLUE,fill_color=PALE,fill_opacity=.28,stroke_width=3).move_to(C)
   d0=Dot(C+[-1.2,-1.2,0],color=RED);d1=Dot(C+[1.2,1.2,0],color=RED);fixed2(square,d0,d1);objects=[square,d0,d1]
   fixed2(txt('z축 회전 / XY 단면',21,MUTED).move_to([-3.35,-2.13,0]))
  elif mode=='affine-bounds':
   self.add(axes3(O,1.75));box=box_wire([-2,-1,-.5],[2,1,.5],O,scale=.78,color=BLUE);self.add(box);objects=[box]
   fixed2(txt('Rz45° / 입력 상자의 아핀 변환',20,MUTED).move_to([-3.35,-2.13,0]))
  elif mode=='bounds-practice':
   ps=np.array([[7,11,-5],[2,3,8],[-3,3,1],[-5,-7,0],[6,3,4]],float);Rot=rz(PI/4);center=Rot@np.array([1,2,1.5])
   origin=O;dots=VGroup(*[Dot3D(origin+.17*P@(Rot@p-center),radius=.08,color=GOLD,resolution=(6,6)) for p in ps])
   # Compare two world-axis AABBs. A rotated OBB is not the transformed-box
   # AABB computed in the preceding lesson and does not establish containment.
   corners=(Rot@np.array(list(product(*zip([-5,-7,-5],[7,11,8]))),float).T).T
   box=box_wire(corners.min(0),corners.max(0),origin-.17*P@center,.17,color=BLUE)
   rp=(Rot@ps.T).T;pointbox=box_wire(rp.min(0),rp.max(0),origin-.17*P@center,.17,color=GREEN)
   X=C+[1.25,-.7,0];Y=C+[-1.25,1.02,0]
   ray=VGroup(Arrow(X,Y,buff=0,color=BLUE),Dot(X,color=RED),Dot(Y,color=GOLD),txt('(5,3)',21,RED).next_to(Dot(X),DOWN),txt('δ=(-7,5)',21,BLUE).move_to(C+[-.2,.6,0]));fixed2(ray)
   legend=txt('문제1: 출발점 + 차이 벡터',18,MUTED).move_to([-3.35,-2.16,0]);fixed2(legend)
   objects=[box,pointbox,dots,ray,legend,X,Y]
  else:raise ValueError('Unimplemented independent geometry mode: '+mode)
  for i,beat in enumerate(s['beats']):
   ts=slot['lineStarts'][min(i,len(slot['lineStarts'])-1)]
   if ts>self.renderer.time+1/60:self.wait(ts-self.renderer.time,frozen_frame=True)
   active=self.replace_fixed(active,card(beat,width=12 if full else 6,size=25,color=GREEN if i==len(s['beats'])-1 else BLUE).move_to([0 if full else 3.15,1.66,0]))
   if mode=='overview':self.play(Indicate(special[max(0,min(i-1,2))],color=GREEN),run_time=.55)
   elif mode=='forms':
    _,circle,centerDot,dot,rad=objects
    if i==0:seteq('중심 c / 반지름 r')
    if i==1:
     self.play(MoveAlongPath(dot,circle),run_time=1.6);seteq('p(θ)=c+r(cosθ,sinθ)')
    if i==2:seteq('F(p)=‖p-c‖²-r²')
    if i==3:
     self.play(dot.animate.move_to(C+.6*RIGHT).set_color(GREEN),run_time=.65);setnote('내부: F<0',GREEN)
     self.play(dot.animate.move_to(C+1.65*RIGHT).set_color(RED),run_time=.65);setnote('외부: F>0',RED)
    if i==4:setnote('점 생성 / 후보점 검사 / 데이터 저장')
    if i==5:setnote('θ를 시간으로 쓰려면 θ(t)를 따로 정의')
   elif mode=='conic':
    grid,circle,centerDot,dot,rad=objects
    if i==1:
     shift=grid.c2p(2,3)-centerDot.get_center();self.play(*[v.animate.shift(shift) for v in [circle,centerDot,dot,rad]],run_time=.9);seteq('(x-2)²+(y-3)²=1');setnote('중심=(2,3), 반지름=1 / 같은 축 단위')
    if i==2:seteq('x²+y²-4x-6y+12=0')
    if i==3:seteq('Ax²+Bxy+Cy²+Dx+Ey+F=0');setnote('일차항 Dx+Ey를 빠뜨리지 않기')
    if i==4:setnote('원: cx,cy,r / 구: cx,cy,cz,r')
    if i==5:self.play(circle.animate.stretch(1.45,0),run_time=.9);setnote('서로 다른 축 반지름 / 타원체')
   elif mode=='domains':
    line,seg,ray,dot,X,Y=objects
    if i==0:seteq('p(t)=o+tδ')
    if i==1:self.play(dot.animate.move_to(Y),run_time=1.1);seteq('t=0 → o / t=1 → o+δ')
    if i==2:self.play(dot.animate.move_to(X-(Y-X)*.28),run_time=.8);seteq('직선: -∞<t<+∞')
    if i==3:fixed2(ray);self.play(Create(ray),dot.animate.move_to(Y+.1*(Y-X)).set_color(GREEN),run_time=.65);seteq('레이: t≥0')
    if i==4:setnote('유한 검사: 최대 거리까지')
    if i==5:self.play(dot.animate.move_to(X-.28*(Y-X)).set_color(RED),run_time=.6);setnote('선분 밖의 점 / 범위 조건으로 거절',RED)
   elif mode=='ray-units':
    dot,mid=objects
    if i==1:self.play(dot.animate.move_to(mid),run_time=.9);seteq('p(.5)=(2,1)+(.5)(6,3)=(5,2.5)')
    if i==2:setnote('t는 무차원 비율')
    if i==3:seteq('u=(6,3)/√45 / ‖u‖=1')
    if i==4:seteq('p(s)=o+su / s=√45/2');setnote('s: 길이 단위')
    if i==5:setnote('‖δ‖=0 또는 비유한이면 정규화 거절',RED)
   elif mode=='line-normal':
    if i==0:seteq('수직선 x=1 / 기울기 Δy/0 불가')
    if i==1:seteq('n·p=d')
    if i==2:fixed2(*dots);self.play(Create(dots[0]),run_time=.7);setnote('법선은 선 방향에 직각')
    if i==3:seteq('n=(2,0), 중점=(1,0), d=2')
    if i==4:seteq('2x=2 → x=1');self.play(Indicate(dots[1],color=GOLD),run_time=.5)
    if i==5:seteq('n′=n/‖n‖, d′=d/‖n‖');setnote('n과 d를 함께 정규화 / n≠0')
   elif mode=='sphere-test':
    sphere,dot=objects
    if i==0:seteq('‖p-c‖² 비교 r²')
    if i==1:seteq('c=(1,2,3), r²=4')
    if i in [2,3,4]:
     dist=[0,2,3][i-2];color=[GREEN,GOLD,RED][i-2]
     self.play(dot.animate.move_to(O+.69*dist*P[:,0]).set_color(color),run_time=.8)
     seteq(['거리²=0 <4','거리²=4 =4','거리²=9 >4'][i-2],color)
    if i==5:setnote('표면 = / 채운 구 ≤ / 경계 허용오차 명시')
   elif mode=='sphere-measures':
    eq=['r → 2r','D=2r, C=2πr','A_circle=πr², A_sphere=4πr²','V=(4/3)πr³','길이×2 / 넓이×4 / 부피×8','단위와 게임 설계 비용은 별도']
    seteq(eq[i]);
    if i==4:self.play(Indicate(objects[1],color=GREEN),run_time=.6)
   elif mode=='box-data':
    if i==0:seteq('6면 / 3축 독립 범위')
    if i==1:seteq('min=(min x,min y,min z)')
    if i==2:seteq('c=(min+max)/2 / e=(max-min)/2');self.play(Indicate(objects[1],color=GOLD),run_time=.55)
    if i==3:seteq('x 범위 ∧ y 범위 ∧ z 범위')
    if i==4:setnote('y는 min.y,max.y / z는 min.z,max.z')
    if i==5:
     Rot=rz(PI/5);self.play(Transform(objects[0],box_wire([-1.8,-1.2,-.8],[1.8,1.2,.8],O,.77,Rot,GREEN)),run_time=1);setnote('OBB: 방향 행렬도 저장')
   elif mode=='point-bounds':
    pts,center,origin=objects
    if codehl:self.remove(codehl)
    row=[2,4,5,5,0,1][i];codehl=SurroundingRectangle(special[row],color=GOLD,buff=.08,stroke_width=2);fixed2(codehl)
    if i==0:setnote('첫 유효한 점 / 축별로 독립 비교')
    if i==1:
     for k in range(1,6):
      lo,hi=pts[:k].min(0),pts[:k].max(0);target=box_wire(lo,hi,origin-.14*P@center,.14,color=BLUE)
      if k==1:b=target;self.add(b)
      else:self.play(Transform(b,target),run_time=.45)
     setnote('최소/최대 성분은 서로 다른 점에서 나옴')
    if i==2:setnote('min=(-5,-7,-5) / max=(7,11,8)')
    if i==3:setnote('center=(1,2,1.5) / half=(6,9,6.5)')
    if i==4:setnote('영 초기화는 원점을 잘못 포함할 수 있음',RED)
    if i==5:setnote('빈 입력 / 비유한 좌표 / 실제 점 개수 검증')
   elif mode=='proxy-overlap':
    if i==1:fixed2(objects[2]);self.play(Create(objects[2]),run_time=.8);seteq('AABB overlap=True / shape contact=False')
    if i==2:setnote('Broad phase: 후보 선별')
    if i==3:setnote('분리 결론은 올바른 포함 경계가 전제')
    if i==4:seteq('Sphere / AABB / OBB')
    if i==5:setnote('갱신·후보 수·정밀 검사: 실제 비용 비교')
   elif mode=='rotated-minmax':
    square,d0,d1=objects
    if i==1:
     self.play(Rotate(square,PI/4,about_point=C),d0.animate.move_to(C+[0,-1.2*np.sqrt(2),0]),d1.animate.move_to(C+[0,1.2*np.sqrt(2),0]),run_time=1.1);seteq('두 옛 대각점: 새 x=0')
    if i==2:
     bad=Line(d0.get_center(),d1.get_center(),color=RED,stroke_width=4);good=Rectangle(width=2.4*np.sqrt(2),height=2.4*np.sqrt(2),color=GREEN,stroke_width=2).move_to(C);fixed2(bad,good);self.play(Create(good),run_time=.6);seteq('실제 x: -√2 … +√2')
    if i==3:setnote('극값을 주는 꼭짓점이 달라짐')
    if i==4:seteq('3D: 모든 8꼭짓점 변환')
    if i==5:setnote('기존 상자를 변환한 경계 / 실제 점 경계와 구분')
   elif mode=='affine-bounds':
    if i==0:seteq('p′=Ap+t / c′=Ac+t')
    if i==1:seteq('e′x=|A00|ex+|A01|ey+|A02|ez')
    if i==2:seteq('e′=|A|e / 성분별 절댓값')
    if i==3:
     Rot=rz(PI/4);self.play(Transform(objects[0],box_wire([-2,-1,-.5],[2,1,.5],O,.78,Rot,BLUE)),run_time=.9)
     e=np.array([3/np.sqrt(2),3/np.sqrt(2),.5]);b=box_wire(-e,e,O,.78,color=GREEN);self.play(Create(b),run_time=.8);seteq('e′=(3/√2,3/√2,.5)')
    if i==4:seteq('min′=c′-e′ / max′=c′+e′')
    if i==5:setnote('아핀 입력 상자 한정 / 원근 나눗셈 별도')
   elif mode=='bounds-practice':
    if i==0:seteq('p(1)=(5,3)+(-7,5)')
    if i==1:
     seteq('(-2,8) / y=(-5/7)x+46/7');answer=txt('(-2,8)',21,GREEN).next_to(Dot(objects[6]),UP);fixed2(answer);objects[3].add(answer)
    if i==2:
     self.remove(objects[3],*objects[3].submobjects);self.add(objects[2])
     objects[4]=self.replace_fixed(objects[4],fit(txt('초록: 변환한 5점 / 파랑: 변환한 8꼭짓점 AABB',18,MUTED),6).move_to([-3.35,2.28,0]))
     self.play(Create(objects[1]),run_time=.8);seteq('5점 x: [-6/√2,3/√2]')
    if i==3:seteq('y: [-12/√2,18/√2], z: [-5,8]')
    if i==4:self.play(Create(objects[0]),run_time=.9);setnote('기존 상자의 빈 공간까지 함께 변환')
    if i==5:setnote('다음: 평면의 거리 / 삼각형의 가중치')
  remaining=slot['seconds']-self.renderer.time
  if remaining>1/60:self.wait(remaining,frozen_frame=True)

def make_scenes(slug,module):
 data=json.loads((ROOT/f'production/batches/game-math-part2-full-series/lessons/{slug}.json').read_text(encoding='utf8'))
 generated={f'Scene{s["id"]}':type(f'Scene{s["id"]}',(GeometryScene,),{'slug':slug,'sid':s['id'],'__module__':module}) for s in data['scenes'] if s['kind']=='explanation'}
 from lesson import make_scenes as brand_scenes
 generated.update({k:v for k,v in brand_scenes(slug,module).items() if k in ['BrandIntro','MemberOutro']})
 return generated
