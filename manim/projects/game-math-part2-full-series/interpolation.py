"""Original unit-sphere diagrams and conversion demonstrations; not gameplay."""
from lesson import *
import importlib.util
refpath=ROOT/'production/batches/game-math-part2-full-series/rotation-conversions.py'
spec=importlib.util.spec_from_file_location('rotation_reference',refpath)
conv=importlib.util.module_from_spec(spec);spec.loader.exec_module(conv)

def screen_point(x,y):
 phi,theta=64*DEGREES,-48*DEGREES
 return (x*np.array([-np.sin(theta),np.cos(theta),0.])+y*np.array([-np.cos(phi)*np.cos(theta),-np.cos(phi)*np.sin(theta),np.sin(phi)]))/.85

class InterpolationScene(ThreeDScene):
 slug='';sid=''
 fixed=LectureScene.fixed
 replace_fixed=LectureScene.replace_fixed
 def construct(self):
  self.camera.background_color=WHITE
  data=json.loads((ROOT/f'production/batches/game-math-part2-full-series/lessons/{self.slug}.json').read_text(encoding='utf8'))
  s=next(v for v in data['scenes'] if v['id']==self.sid);slot=next(v for v in timing(self.slug,data)['scenes'] if v['id']==self.sid);mode=s['mode']
  self.set_camera_orientation(phi=64*DEGREES,theta=-48*DEGREES,zoom=.85)
  title=fit(txt(s['title'],40),12.65).to_corner(UL,buff=.6)
  sub=fit(txt('게임수학 Part 2 / 3D 회전 4편 · 오른손 / 열벡터 / Hamilton / wxyz',20,MUTED),12.65).next_to(title,DOWN,aligned_edge=LEFT,buff=.14)
  self.fixed(title,sub,Line([-6.5,2.63,0],[6.5,2.63,0],color=RULE,stroke_width=1))
  flat=mode in ['overview','short-path','sphere','slerp-code','time','continuity','representations','contract','summary']
  paired=mode in ['collapse','speed']
  origin=screen_point(-3.35,-.25);origins=[screen_point(-4.85,-.35),screen_point(-1.7,-.35)]
  obj=None;objects=[];special=None;formula=None;active=None;note=None;matrix=None;dot=None
  if not flat:
   if paired:
    for O in origins:
     v=basis(np.eye(3),O,scale=1.35);self.add(v);objects.append(v)
    labels=['Matrix LERP / 축 붕괴','단위 쿼터니언 / 회전'] if mode=='collapse' else ['NLERP / 변하는 각속도','SLERP / 선형 t']
    for x,label in zip([-4.85,-1.7],labels):self.fixed(fit(txt(label,20,BLUE if x<-3 else GREEN),3.08).move_to([x,-2.05,0]))
   else:
    obj=basis(np.eye(3),origin);self.add(obj)
    self.add(VGroup(*[DashedLine(origin-2*P[:,j],origin+2.15*P[:,j],color=RULE,stroke_width=1.2) for j in range(3)]))
    self.fixed(VGroup(txt('x',23,RED),txt('y ↑',23,GREEN),txt('z 앞',23,BLUE)).arrange(RIGHT,buff=.6).move_to([-3.35,-2.35,0]))
  if mode=='overview':
   special=VGroup(*[card(v,width=2.85,size=26) for v in ['보간 경로','회전 속도','네 표현 변환','왕복 검증']]).arrange(RIGHT,buff=.3).move_to([0,-.05,0]);self.fixed(special)
   self.fixed(VGroup(*[Arrow(special[j].get_right(),special[j+1].get_left(),buff=.02,color=MUTED,stroke_width=2) for j in range(3)]))
  elif mode=='short-path':
   special=VGroup(card('a',width=3,color=BLUE),card('-a',width=3,color=RED),card('b := a',width=3,color=GREEN)).arrange(RIGHT,buff=.65).move_to([0,0,0]);self.fixed(special)
   self.fixed(Arrow(special[1].get_right(),special[2].get_left(),buff=.04,color=GREEN))
  elif mode=='sphere':
   center=np.array([-3.6,-.15,0]);radius=1.72
   circle=Circle(radius=radius,color=RULE,stroke_width=2).move_to(center)
   arc=Arc(radius=radius,start_angle=0,angle=PI/4,color=GREEN,stroke_width=5).shift(center)
   a=center+radius*RIGHT;b=center+radius*np.array([np.cos(PI/4),np.sin(PI/4),0.])
   self.fixed(circle,arc,Line(center,a,color=BLUE),Line(center,b,color=GREEN),Dot(a,color=BLUE),Dot(b,color=GREEN),DashedLine(a,b,color=RED))
   self.fixed(txt('a',25,BLUE).next_to(Dot(a),RIGHT),txt('b',25,GREEN).move_to(b+[.25,.2,0]),txt('4D 구면의 2D 단면 개념도',20,MUTED).move_to([-3.6,-2.2,0]))
   dot=Dot(a,color=GOLD,radius=.1);self.fixed(dot)
  elif mode=='slerp-code':
   lines=['t = checked_t(t,0,1)','a,b = checked_unit(a), checked_unit(b)','d = dot(a,b)','if d < 0: b,d = -b,-d','d = clamp(d,0,1)','if d > .9995: return unit(lerp(a,b,t))','alpha = acos(d)','return unit((sin((1-t)*alpha)*a','             + sin(t*alpha)*b) / sin(alpha))']
   special=VGroup(*[Text(v,font='Consolas',font_size=20,color=INK,t2c={'return':GREEN,'unit':BLUE,'clamp':GOLD,'if':RED}) for v in lines]).arrange(DOWN,aligned_edge=LEFT,buff=.11);fit(special,11.9);special.move_to([0,-.45,0]);self.fixed(special)
  elif mode in ['time','continuity']:
   labels=['고정 시작 a','선형 시간 t','고정 끝 b'] if mode=='time' else ['이전 q','dot 부호 검사','현재 q 또는 -q']
   special=VGroup(*[card(v,width=3.6,size=28) for v in labels]).arrange(RIGHT,buff=.48).move_to([0,.1,0]);self.fixed(special)
   self.fixed(VGroup(*[Arrow(special[j].get_right(),special[j+1].get_left(),buff=.03,color=MUTED) for j in range(2)]))
  elif mode=='representations':
   special=VGroup(*[card(v,width=5.2,size=29,color=c) for v,c in [('Euler / 12 B',BLUE),('Quaternion / 16 B',GOLD),('Matrix / 36 B',GREEN),('Axis-angle / 설명',BLUE)]]).arrange_in_grid(rows=2,cols=2,buff=(.6,.35)).move_to([0,-.25,0]);self.fixed(special)
  elif mode=='contract':
   special=VGroup(*[card(v,width=2.85,size=29) for v in ['Euler','Matrix','Quaternion','Axis-angle']]).arrange(RIGHT,buff=.32).move_to([0,-.1,0]);self.fixed(special)
   self.fixed(VGroup(*[DoubleArrow(special[j].get_right(),special[j+1].get_left(),buff=.03,color=MUTED,stroke_width=2) for j in range(3)]))
  elif mode=='summary':
   special=VGroup(*[card(v,width=11,size=28,color=GREEN) for v in ['단위·부호와 경로 / 시간 조건','같은 규약으로 네 표현 변환','영도·반 바퀴·특이점 / 왕복 검증']]).arrange(DOWN,buff=.28).move_to([0,-.65,0]);self.fixed(special)
  def equation(v):
   nonlocal formula
   formula=self.replace_fixed(formula,fit(txt(v,27,GOLD),6 if not flat or mode=='sphere' else 11.8).move_to([3.1 if not flat or mode=='sphere' else 0,-.65,0]))
  def display(v,color=GREEN):
   nonlocal note
   note=self.replace_fixed(note,fit(txt(v,23,color),6 if not flat or mode=='sphere' else 11.8).move_to([3.1 if not flat or mode=='sphere' else 0,-2.25,0]))
  def orient(v,O,M):self.play(Transform(v,basis(M,O,scale=1.35 if paired else 2.05)),run_time=.85)
  for i,beat in enumerate(s['beats']):
   ts=slot['lineStarts'][min(i,len(slot['lineStarts'])-1)]
   if ts>self.renderer.time+1/60:self.wait(ts-self.renderer.time,frozen_frame=True)
   panel=not flat or mode=='sphere'
   active=self.replace_fixed(active,card(beat,width=6 if panel else 12,size=26,color=GREEN if i==len(s['beats'])-1 else BLUE).move_to([3.1 if panel else 0,1.65,0]))
   if mode=='overview':self.play(Indicate(special[min(i,3)],color=GREEN),run_time=.55)
   elif mode=='collapse':
    if i==1:
     orient(objects[0],origins[0],np.diag([0,0,1]));orient(objects[1],origins[1],rz(PI/2));equation('LERP(I,Rzπ,.5): det=0')
    if i==3:display('정규화 선형 보간 / 구면 호 보간')
    if i==4:display('다른 회전 구조 보존 방법도 가능')
   elif mode=='short-path':
    if i==1:self.play(Indicate(special[1],color=RED),Indicate(special[2],color=GREEN),run_time=.8);equation('dot(a,b)<0 → b=-b')
    if i==3:equation('SLERP(a,-a,t) = a (부호 정렬 후)')
    if i==4:display('물리 180°에서 두 동률 경로',RED)
    if i==5:equation('Δ=b a⁻¹ / q(t)=Δᵗ a');display('단위·부호 정렬 / 선택한 거듭제곱 분기')
   elif mode=='sphere':
    if i==2:equation('α = acos(d)')
    if i==3:equation('S³: α=45° / 물체: 2α=90°')
    if i==4:
     target=np.array([-3.6,-.15,0])+1.72*np.array([np.cos(PI/8),np.sin(PI/8),0.]);self.play(dot.animate.move_to(target),run_time=.9)
     formula=self.replace_fixed(formula,VGroup(fit(txt('k₀=sin((1-t)α)/sinα',25,GOLD),5.8),fit(txt('k₁=sin(tα)/sinα',25,GREEN),5.8),txt('q(t)=k₀a+k₁b',27,BLUE)).arrange(DOWN,buff=.22).move_to([3.1,-.45,0]))
   elif mode=='slerp-code':
    groups={0:[0,1],1:[1],2:[2,3,4],3:[5],4:[6,7,8]}
    self.play(*[Indicate(special[j],color=GOLD) for j in groups[i]],run_time=.6)
    if i==1:
     note=self.replace_fixed(note,txt('checked_unit: 유한·비영 입력 검증',23,RED).move_to([0,-2.25,0]))
   elif mode=='slerp-example':
    q0=np.array([1.,0,0,0]);q1=conv.axis_quaternion([0,0,1],PI/2)
    if i==1:equation('α=45° / Δθ=90°')
    if i==2:
     for t in [.25,.5]:orient(obj,origin,conv.to_matrix(conv.interpolate(q0,q1,t)));equation(f't={t:g} / θ={90*t:g}°')
    if i==3:orient(obj,origin,conv.to_matrix(conv.interpolate(q0,q1,.75)));equation('t=.75 / θ=67.5°')
    if i==4:display('같은 Δt → 같은 Δθ')
   elif mode=='speed':
    q0=np.array([1.,0,0,0]);q1=conv.axis_quaternion([0,0,1],2*PI/3)
    if i in [2,3]:
     t=.25 if i==2 else .5
     self.play(*[Transform(v,basis(conv.to_matrix(conv.interpolate(q0,q1,t,method=method)),O,scale=1.35)) for v,O,method in zip(objects,origins,['nlerp','slerp'])],run_time=1.2)
     equation('t=.25: 27.8° / 30°' if i==2 else 't=.5: 두 방법 모두60°')
    if i==4:display('속도·요구 움직임·실제 비용 비교')
   elif mode=='time':
    if i==0:equation('t = elapsed / duration')
    if i==1:equation('θ(u)=Δθ·ease(u)')
    if i==2:display('현재값→목표 반복은 다른 시간 동작')
    if i==3:equation('k = 1-exp(-λΔt)')
   elif mode=='continuity':
    if i==0:display('대표 부호가 바뀌는 경계 주의',RED)
    if i==1:equation('dot(previous,current)<0 → -current')
    if i==3:display('중간 키 / 누적 회전량은 별도 저장')
   elif mode=='representations':
    if i in [0,1,2]:self.play(Indicate(special[i],color=GOLD),run_time=.6)
    if i==3:display('float32 성분만 / 정렬·메타데이터 제외')
    if i==4:self.play(Indicate(special[3],color=GOLD),run_time=.6)
   elif mode=='contract':
    if i==2:display('R=Ry(h)Rx(p)Rz(b) / radians')
    if i==3:display('책: 왼손·행벡터 / 강의: 오른손·열벡터',RED)
    if i==4:self.play(*[Indicate(v,color=GREEN) for v in special],run_time=.8)
   elif mode=='euler-matrix':
    if i==0:orient(obj,origin,conv.to_matrix(conv.euler_quaternion(30*DEGREES,20*DEGREES,10*DEGREES)));equation('R=Ry(h)Rx(p)Rz(b)')
    if i==1:equation('sp=-R[1,2]')
    if i==2:formula=self.replace_fixed(formula,VGroup(txt('h=atan2(R02,R22)',26,GOLD),txt('b=atan2(R10,R11)',26,GREEN)).arrange(DOWN,buff=.3).move_to([3.1,-.5,0]))
    if i==3:formula=self.replace_fixed(formula,VGroup(txt('cp=hypot(R10,R11)',26,GOLD),txt('p=atan2(sp,cp)',26,GREEN)).arrange(DOWN,buff=.3).move_to([3.1,-.5,0]))
    if i==4:orient(obj,origin,conv.to_matrix(conv.euler_quaternion(30*DEGREES,PI/2,10*DEGREES)));equation('h=atan2(-R20,R00) / b=0')
    if i==5:display('회전 행렬 / 기준축으로 왕복 비교')
   elif mode=='quaternion-matrix':
    if i==1:
     orient(obj,origin,rz(PI/2));matrix,_=numeric_matrix([[0,-1,0],[1,0,0],[0,0,1]]);matrix.move_to([3.1,-.4,0]);self.fixed(matrix)
    if i==2:self.play(Indicate(obj[1][0],color=GOLD),run_time=.6)
    if i==3:self.add(arrow(origin,origin+1.8*P@np.array([0,1,0.]),GOLD,5));display('(1,0,0) → (0,1,0)')
   elif mode=='matrix-quaternion':
    if i==0:equation('RᵀR≈I / det(R)≈+1')
    if i==1:equation('trace=R00+R11+R22 / w 분기')
    if i==2:equation('Z180°: trace=-1 / w=0');orient(obj,origin,rz(PI))
    if i==3:equation('max(R00,R11,R22) → x,y,z')
    if i==4:equation('Z180° → [0,0,0,1]')
    if i==5:display('q 정규화 / R 재구성 / 원래 R 비교')
   elif mode=='euler-quaternion':
    if i==0:orient(obj,origin,conv.to_matrix(conv.euler_quaternion(30*DEGREES,20*DEGREES,10*DEGREES)))
    if i==1:equation('q=qy(h) qx(p) qz(b)')
    if i==2:equation('q → R(q) → Euler')
    if i==3:equation('p=copysign(π/2,sp) / b=0')
    if i==4:display('유효한 단위 q 먼저 검사',RED)
   elif mode=='axis-angle':
    if i==0:equation('q=[cos(θ/2), n sin(θ/2)]')
    if i==1:display('w<0이면 q=-q / θ∈[0,π]')
    if i==2:equation('θ=2acos(w) / n=v÷||v||')
    if i==3:equation('θ=0: 축 임의 / 예제 대표 +x')
    if i==4:orient(obj,origin,rz(PI));equation('θ=π: ±n은 같은 끝 자세')
   elif mode=='practice':
    if i==1:orient(obj,origin,rz(PI/4));equation('qmid=[cos22.5°,0,0,sin22.5°]')
    if i==2:
     self.add(arrow(origin,origin+1.8*P@np.array([np.sqrt(.5),np.sqrt(.5),0.]),GOLD,5));equation('R(qmid)(1,0,0)=(c,c,0)')
    if i==4:orient(obj,origin,rz(PI));equation('q=[0,0,0,1] / R=diag(-1,-1,1)')
    if i==5:display('같은 행렬 / 같은 변환된 기준축')
   elif mode=='summary':self.play(Indicate(special[min(i//2,2)],color=GOLD),run_time=.55)
  remaining=slot['seconds']-self.renderer.time
  if remaining>1/60:self.wait(remaining,frozen_frame=True)

def make_scenes(slug,module):
 data=json.loads((ROOT/f'production/batches/game-math-part2-full-series/lessons/{slug}.json').read_text(encoding='utf8'))
 generated={f'Scene{s["id"]}':type(f'Scene{s["id"]}',(InterpolationScene,),{'slug':slug,'sid':s['id'],'__module__':module}) for s in data['scenes'] if s['kind']=='explanation'}
 # Preserve the verified original logo and member profile/name/badge assets.
 from lesson import make_scenes as brand_scenes
 brand=brand_scenes(slug,module)
 generated.update({k:v for k,v in brand.items() if k in ['BrandIntro','MemberOutro']})
 return generated
