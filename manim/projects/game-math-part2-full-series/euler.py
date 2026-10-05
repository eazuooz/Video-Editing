"""Euler and axis-angle diagrams in the explicitly declared right-handed frame."""
from lesson import *

def euler(h,p,b):return ry(h)@rx(p)@rz(b)
def axis_rotation(n,a):
 n=np.asarray(n,dtype=float);n=n/np.linalg.norm(n)
 K=np.array([[0,-n[2],n[1]],[n[2],0,-n[0]],[-n[1],n[0],0.]])
 return np.eye(3)*np.cos(a)+(1-np.cos(a))*np.outer(n,n)+np.sin(a)*K
def screen_point(x,y):
 phi,theta=64*DEGREES,-48*DEGREES
 right=np.array([-np.sin(theta),np.cos(theta),0.])
 up=np.array([-np.cos(phi)*np.cos(theta),-np.cos(phi)*np.sin(theta),np.sin(phi)])
 return (x*right+y*up)/.85
def ring(normal,radius,color,origin):
 c=Circle(radius=radius,color=color,stroke_width=3)
 normal=normal/np.linalg.norm(normal);axis=np.cross(OUT,normal)
 if np.linalg.norm(axis)>1e-8:c.rotate(np.arccos(np.clip(OUT@normal,-1,1)),axis=axis)
 elif OUT@normal<0:c.rotate(PI,axis=RIGHT)
 return c.shift(origin)

class EulerScene(ThreeDScene):
 slug='';sid=''
 fixed=LectureScene.fixed
 replace_fixed=LectureScene.replace_fixed
 def construct(self):
  self.camera.background_color=WHITE
  data=json.loads((ROOT/f'production/batches/game-math-part2-full-series/lessons/{self.slug}.json').read_text(encoding='utf8'))
  s=next(x for x in data['scenes'] if x['id']==self.sid);slot=next(x for x in timing(self.slug,data)['scenes'] if x['id']==self.sid);mode=s['mode']
  self.set_camera_orientation(phi=64*DEGREES,theta=-48*DEGREES,zoom=.85)
  title=fit(txt(s['title'],40),12.65).to_corner(UL,buff=.6)
  sub=fit(txt('게임수학 Part 2 / 3D 회전 2편 · 오른손 / 열벡터 / 몸체 Y-X-Z',20,MUTED),12.65).next_to(title,DOWN,aligned_edge=LEFT,buff=.14)
  self.fixed(title,sub,Line([-6.5,2.63,0],[6.5,2.63,0],color=RULE,stroke_width=1))
  flat=mode in ['overview','wrap','wrap-code','angular-rate','practice','summary']
  wide=flat and mode!='wrap'
  paired=mode in ['extrinsic','order','aliases','gimbal-values','axis-aliases','nonadd']
  origin=screen_point(-3.35,-.2);origins=[screen_point(-4.8,-.25),screen_point(-1.7,-.25)]
  obj=None;objects=[];active=None;note=None;special=None;circle=None;needle=None;glrings=None
  if not flat:
   if paired:
    matrices=[np.eye(3),np.eye(3)]
    if mode=='aliases':matrices=[euler(0,135*DEGREES,0),euler(PI,45*DEGREES,PI)]
    if mode=='gimbal-values':matrices=[euler(30*DEGREES,PI/2,10*DEGREES),euler(20*DEGREES,PI/2,0)]
    for O,R in zip(origins,matrices):
     world=VGroup(*[DashedLine(O-1.35*P[:,i],O+1.5*P[:,i],color=RULE,stroke_width=1.2) for i in range(3)])
     x=basis(R,O,scale=1.4);self.add(world,x);objects.append(x)
    labels={'extrinsic':['몸체 Y → X → Z','고정 Z → X → Y'],'order':['고정 X → Y','고정 Y → X'],'aliases':['(0°,135°,0°)','(180°,45°,180°)'],'gimbal-values':['(30°,90°,10°)','(20°,90°,0°)'],'axis-aliases':['+90° · n','+270° · -n'],'nonadd':['X90° 후 Y90°','벡터를 더한 한 회전']}[mode]
    for x,label in zip([-4.8,-1.7],labels):self.fixed(fit(txt(label,22,GREEN if x< -3 else BLUE),3.05).move_to([x,-1.95,0]))
   else:
    obj=basis(np.eye(3),origin);self.add(VGroup(*[DashedLine(origin-2.05*P[:,i],origin+2.2*P[:,i],color=RULE,stroke_width=1.4) for i in range(3)]),obj)
    self.fixed(VGroup(txt('x',23,RED),txt('y',23,GREEN),txt('z 앞',23,BLUE)).arrange(RIGHT,buff=.7).move_to([-3.35,-2.25,0]))
  if mode=='overview':
   special=VGroup(*[card(v,width=2.85,size=27) for v in ['세 각과 순서','짐벌락','각도 보간','축·각과 실습']]).arrange(RIGHT,buff=.3).move_to([0,.1,0]);self.fixed(special)
   self.fixed(VGroup(*[Arrow(special[i].get_right(),special[i+1].get_left(),buff=.03,color=MUTED,stroke_width=2) for i in range(3)]))
  elif mode=='gimbal':
   self.remove(obj);obj=basis(np.eye(3),origin,scale=1.8);self.add(obj)
   glrings=VGroup(ring(P[:,1],1.8,GREEN,origin),ring(P[:,0],1.55,RED,origin),ring(P[:,2],1.3,BLUE,origin));self.add(glrings)
  elif mode=='wrap':
   circle=Circle(radius=1.65,color=RULE).move_to([-3.35,-.05,0])
   a,b=-170*DEGREES,170*DEGREES;center=circle.get_center()
   points=[center+1.65*np.array([np.cos(t),np.sin(t),0.]) for t in [a,b]]
   self.fixed(circle,Dot(points[0],color=BLUE),Dot(points[1],color=GREEN),txt('start -170°',22,BLUE).move_to([-4.9,-1.35,0]),txt('end +170°',22,GREEN).move_to([-4.9,1.25,0]))
   self.fixed(Arrow(center,points[0],buff=0,color=BLUE),Arrow(center,points[1],buff=0,color=GREEN))
  elif mode=='wrap-code':
   code=VGroup(*[Text(line,font='Consolas',font_size=20,color=INK,t2c={'double':BLUE,'constexpr':GOLD,'return':GREEN,'if':GREEN,'std::remainder':GOLD,'delta':RED}) for line in s['code']]).arrange(DOWN,aligned_edge=LEFT,buff=.13);fit(code,12.0);code.move_to([0,-.65,0]);self.fixed(code);special=code
  elif mode=='angular-rate':
   special=VGroup()
   for x,label,col in [(-3.25,'720°/s = 2회전',BLUE),(3.25,'1080°/s = 3회전',GREEN)]:
    c=Circle(radius=1.35,color=RULE).move_to([x,-.25,0]);a=Arrow(c.get_center(),c.get_center()+1.18*RIGHT,buff=0,color=col)
    self.fixed(c,a,txt(label,29,col).move_to([x,-1.85,0]));special.add(a)
  elif mode=='practice':
   special=card('문제 1 · +170° → -170°',width=10,size=34,color=GREEN).move_to([0,.15,0]);self.fixed(special)
  elif mode=='summary':
   special=VGroup(*[card(v,width=10.9,size=30,color=GREEN) for v in ['오일러 각: 축과 순서를 함께 기록','짐벌락: 표현의 특이점 / 물체는 회전 가능','축·각과 회전벡터: 단위·중복·합성 구분']]).arrange(DOWN,buff=.25).move_to([0,-.45,0]);self.fixed(special)
  def display(text,color=GREEN):
   nonlocal note
   note=self.replace_fixed(note,fit(txt(text,26,color),12 if wide else 6).move_to([0 if wide else 3.12,-2.35,0]))
  def turn(x,O,axis,angle,seconds=.95):self.play(Rotate(x,angle=angle,axis=axis,about_point=O),run_time=seconds)
  for i,beat in enumerate(s['beats']):
   ts=slot['lineStarts'][min(i,len(slot['lineStarts'])-1)]
   if ts>self.renderer.time+1/60:self.wait(ts-self.renderer.time,frozen_frame=True)
   active=self.replace_fixed(active,card(beat,width=12 if wide else 6,size=27,color=GREEN if i==len(s['beats'])-1 else BLUE).move_to([0 if wide else 3.12,1.65,0]))
   if mode=='overview':self.play(Indicate(special[min(i,3)],color=GREEN),run_time=.6)
   elif mode=='euler':
    if i==2:self.play(Indicate(obj[1],color=GOLD),run_time=.8)
    if i==3:display('Ry(h) Rx(p) Rz(b)')
    if i==4:display('좌표계 변경 ≠ 단순 전치',RED)
   elif mode=='intrinsic':
    if i==0:turn(obj,origin,P[:,1],45*DEGREES)
    if i==1:turn(obj,origin,P@ry(45*DEGREES)[:,0],30*DEGREES)
    if i==2:turn(obj,origin,P@(ry(45*DEGREES)@rx(30*DEGREES))[:,2],35*DEGREES)
    if i==3:display('R = Ry(45°) Rx(30°) Rz(35°)')
    if i==4:display('부호는 이름보다 축과 오른손 규칙으로 확인',GOLD)
   elif mode=='extrinsic':
    if i==1:
     R=np.eye(3)
     for axis,a,rot in [(1,45*DEGREES,ry),(0,30*DEGREES,rx),(2,35*DEGREES,rz)]:
      turn(objects[0],origins[0],P@R[:,axis],a,.7);R=R@rot(a)
    if i==2:
     for axis,a in [(2,35*DEGREES),(0,30*DEGREES),(1,45*DEGREES)]:turn(objects[1],origins[1],P[:,axis],a,.7)
    if i==3:display('두 최종 회전 행렬이 같다')
   elif mode=='order':
    if i==1:turn(objects[0],origins[0],P[:,0],PI/2)
    if i==2:turn(objects[0],origins[0],P[:,1],PI/2);display('왼쪽 결과: (0,-1,0)',BLUE)
    if i==3:turn(objects[1],origins[1],P[:,1],PI/2)
    if i==4:turn(objects[1],origins[1],P[:,0],PI/2);display('오른쪽 결과: (1,0,0)',GREEN)
    if i==5:display('같은 두 각도 / 서로 다른 앞쪽 방향',RED)
   elif mode=='aliases':
    if i in [2,3]:self.play(Indicate(objects[i-2][1],color=GOLD),run_time=.7)
    if i==3:display('두 자세가 같음: R₁ = R₂')
   elif mode=='gimbal':
    if i==0:
     def moving_rings(m,alpha):m.become(VGroup(ring(P[:,1],1.8,GREEN,origin),ring(P[:,0],1.55,RED,origin),ring(P@rx(alpha*PI/2)[:,2],1.3,BLUE,origin)))
     self.play(Rotate(obj,angle=PI/2,axis=P[:,0],about_point=origin),UpdateFromAlphaFunc(glrings,moving_rings),run_time=1.5,rate_func=linear)
    if i==1:self.play(Indicate(glrings[0],color=GOLD),Indicate(glrings[2],color=GOLD),run_time=.8)
    if i==2:display('p = +90°: body +z = world -y',GOLD)
    if i==5:display('오일러 매개화의 문제 / 물체는 회전 가능')
   elif mode=='gimbal-values':
    if i==2:self.play(*[Indicate(x[1],color=GOLD) for x in objects],run_time=.8);display('R(30°,90°,10°) = R(20°,90°,0°)')
    if i==3:display('p = -90°이면 h + b')
   elif mode=='wrap':
    if i in [1,2]:
     a=Arc(radius=1.9 if i==1 else 1.78,start_angle=-170*DEGREES,angle=(340 if i==1 else -20)*DEGREES,color=RED if i==1 else GREEN,stroke_width=6).shift(circle.get_center());self.fixed(a);self.play(Create(a),run_time=1.35 if i==1 else .8)
    if i==4:display('절반: -170° + 0.5(-20°) = -180° ≡ +180°')
   elif mode=='wrap-code':
    rows=[1,3,4,4,7,8];highlight=SurroundingRectangle(special[rows[i]],buff=.07,color=GREEN,stroke_width=2);self.fixed(highlight)
    if note:self.remove(note)
    note=highlight;self.play(Create(highlight),run_time=.45)
   elif mode=='interpolation':
    if i==1:turn(obj,origin,P[:,0],85*DEGREES,1.15)
    if i==2:
     def update(m,alpha):m.become(basis(euler(alpha*60*DEGREES,(20+alpha*65)*DEGREES,alpha*60*DEGREES),origin))
     self.play(UpdateFromAlphaFunc(obj,update),run_time=2.2,rate_func=linear)
    if i==4:display('편집용 Euler / 보간용 표현은 따로 검토')
   elif mode=='axis-angle':
    if i==1:self.play(Create(arrow(origin-1.95*P[:,1],origin+2.2*P[:,1],GOLD,6)),run_time=.6)
    if i==2:turn(obj,origin,P[:,1],PI/2,1.4)
    if i==3:self.play(Indicate(obj[1],color=GOLD),run_time=.7)
    if i==5:turn(obj,origin,P[:,1],-PI/4,1);display('같은 축의 45°: 90°의 절반')
   elif mode=='rotation-vector':
    if i==0:self.play(Create(arrow(origin,origin+P[:,1]*1.57,GOLD,6)),run_time=.7)
    if i==2:turn(obj,origin,P[:,1],PI/2,1.3);display('e = (0, π/2, 0) rad')
    if i==3:display('||e|| > 0일 때 n = e / ||e||')
    if i==4:display('e = 0: 회전 없음 / 0으로 나누지 않기',RED)
   elif mode=='axis-aliases':
    if i==0:self.play(Rotate(objects[0],angle=PI/2,axis=P[:,1],about_point=origins[0]),Rotate(objects[1],angle=-3*PI/2,axis=P[:,1],about_point=origins[1]),run_time=1.8,rate_func=linear)
    if i==2:display('90° < 360° / 270° < 360° / 같은 끝 자세',RED)
    if i==4:display('180° 경계: 축 부호 규칙 필요',GOLD)
   elif mode=='nonadd':
    if i==1:
     turn(objects[0],origins[0],P[:,0],PI/2,.9);turn(objects[0],origins[0],P[:,1],PI/2,.9)
     turn(objects[1],origins[1],P@np.array([1.,1,0])/np.sqrt(2),PI/np.sqrt(2),1.4)
    if i==2:display('두 결과의 몸체 축이 다르다',RED)
    if i==4:display('작은 각도에서만 1차 근사로 접근')
   elif mode=='angular-rate':
    if i==1:self.play(Rotate(special[0],angle=4*PI,about_point=np.array([-3.25,-.25,0.])),Rotate(special[1],angle=6*PI,about_point=np.array([3.25,-.25,0.])),run_time=2,rate_func=linear)
    if i==2:display('1초 후 자세는 같음 / 누적 회전량은 다름')
    if i==4:display('ω_body와 ω_world: 기준 공간을 맞춘 뒤 합산')
   elif mode=='practice':
    if i in [1,2,3,4,5]:
     labels=['Δ = -340° + 360° = +20°','θ(0.5) = +180°','문제 2 · e = (0, π/2, 0) rad','n = (0,1,0), θ = 90° → +z가 +x로','다른 축 회전: 적용 순서를 먼저 정하기']
     special=self.replace_fixed(special,card(labels[i-1],width=11.6,size=30,color=GREEN).move_to([0,.15,0]))
   elif mode=='summary' and i<3:self.play(Indicate(special[i],color=GREEN),run_time=.7)
  remaining=slot['seconds']-self.renderer.time
  if remaining>1/60:self.wait(remaining,frozen_frame=True)

def make_scenes(slug,module):
 data=json.loads((ROOT/f'production/batches/game-math-part2-full-series/lessons/{slug}.json').read_text(encoding='utf8'))
 return {'Scene'+s['id']:type('Scene'+s['id'],(EulerScene,),{'slug':slug,'sid':s['id'],'__module__':module}) for s in data['scenes'] if s['kind']=='explanation'}
