"""Independent quaternion diagrams: Hamilton wxyz, right-handed column vectors."""
from lesson import *

def qmul(a,b):
 a=np.asarray(a,dtype=float);b=np.asarray(b,dtype=float)
 return np.r_[a[0]*b[0]-a[1:]@b[1:],a[0]*b[1:]+b[0]*a[1:]+np.cross(a[1:],b[1:])]
def qconj(q):
 q=np.asarray(q,dtype=float);return q*np.array([1,-1,-1,-1])
def qinverse(q):
 q=np.asarray(q,dtype=float);n2=q@q
 if not np.isfinite(n2) or n2<1e-24:raise ValueError('Zero, near-zero or nonfinite inverse input')
 return qconj(q)/n2
def qaxis(n,a):
 n=np.asarray(n,dtype=float);length=np.linalg.norm(n)
 if not np.isfinite(length) or length<1e-12:raise ValueError('Axis must be nonzero and finite')
 return np.r_[np.cos(a/2),n/length*np.sin(a/2)]
def qrotate(q,v):return qmul(qmul(q,np.r_[0,v]),qinverse(q))[1:]
def qmatrix(q):
 q=np.asarray(q,dtype=float)
 if not np.all(np.isfinite(q)) or abs(q@q-1)>1e-8:raise ValueError('Matrix formula requires unit q')
 w,x,y,z=q
 return np.array([[1-2*(y*y+z*z),2*(x*y-w*z),2*(x*z+w*y)],
  [2*(x*y+w*z),1-2*(x*x+z*z),2*(y*z-w*x)],
  [2*(x*z-w*y),2*(y*z+w*x),1-2*(x*x+y*y)]])
def qpower(q,t):
 q=np.asarray(q,dtype=float)
 if not np.all(np.isfinite(q)) or abs(q@q-1)>1e-8 or not np.isfinite(t):raise ValueError('Unit finite q and finite exponent required')
 half=np.arccos(np.clip(q[0],-1,1));length=np.linalg.norm(q[1:])
 if length<1e-12:
  if q[0]>0:return np.array([1.,0,0,0])
  raise ValueError('Negative identity branch needs an explicitly chosen axis')
 return np.r_[np.cos(t*half),q[1:]/length*np.sin(t*half)]
def screen_point(x,y):
 phi,theta=64*DEGREES,-48*DEGREES
 right=np.array([-np.sin(theta),np.cos(theta),0.])
 up=np.array([-np.cos(phi)*np.cos(theta),-np.cos(phi)*np.sin(theta),np.sin(phi)])
 return (x*right+y*up)/.85

class QuaternionScene(ThreeDScene):
 slug='';sid=''
 fixed=LectureScene.fixed
 replace_fixed=LectureScene.replace_fixed
 def construct(self):
  self.camera.background_color=WHITE
  data=json.loads((ROOT/f'production/batches/game-math-part2-full-series/lessons/{self.slug}.json').read_text(encoding='utf8'))
  s=next(x for x in data['scenes'] if x['id']==self.sid);slot=next(x for x in timing(self.slug,data)['scenes'] if x['id']==self.sid);mode=s['mode']
  self.set_camera_orientation(phi=64*DEGREES,theta=-48*DEGREES,zoom=.85)
  title=fit(txt(s['title'],40),12.65).to_corner(UL,buff=.6)
  sub=fit(txt('게임수학 Part 2 / 3D 회전 3편 · 오른손 / 열벡터 / Hamilton / wxyz',20,MUTED),12.65).next_to(title,DOWN,aligned_edge=LEFT,buff=.14)
  self.fixed(title,sub,Line([-6.5,2.63,0],[6.5,2.63,0],color=RULE,stroke_width=1))
  flat=mode in ['overview','components','identity','normalize','general-inverse','hamilton','difference','dot','limits','summary']
  paired=mode in ['double-cover','composition','power']
  origin=screen_point(-3.35,-.2);origins=[screen_point(-4.8,-.25),screen_point(-1.7,-.25)]
  obj=None;objects=[];active=None;note=None;formula=None;special=None;vector=None
  if not flat:
   if paired:
    initial=rz(PI/2) if mode=='double-cover' else np.eye(3)
    for O in origins:
     x=basis(initial,O,scale=1.4);self.add(x);objects.append(x)
    labels={'double-cover':['q = [c,0,0,c]','-q = [-c,0,0,-c]'],'composition':['고정 X90° → Y90°','고정 Y90° → X90°'],'power':['입력 q: θ=90°, n=+z','입력 -q: θ=270°, n=-z']}[mode]
    for x,label in zip([-4.8,-1.7],labels):self.fixed(fit(txt(label,20,GREEN if x< -3 else BLUE),3.05).move_to([x,-1.95,0]))
   else:
    obj=basis(np.eye(3),origin);self.add(obj)
    self.add(VGroup(*[DashedLine(origin-2.05*P[:,j],origin+2.2*P[:,j],color=RULE,stroke_width=1.2) for j in range(3)]))
    self.fixed(VGroup(txt('x',23,RED),txt('y',23,GREEN),txt('z 앞',23,BLUE)).arrange(RIGHT,buff=.7).move_to([-3.35,-2.25,0]))
  if mode=='overview':
   special=VGroup(*[card(v,width=2.85,size=25) for v in ['네 성분과 반각','역회전과 곱셈','회전 차이','벡터 회전 실습']]).arrange(RIGHT,buff=.3).move_to([0,-.1,0]);self.fixed(special)
   self.fixed(VGroup(*[Arrow(special[j].get_right(),special[j+1].get_left(),buff=.03,color=MUTED,stroke_width=2) for j in range(3)]))
  elif mode in ['components','normalize']:
   special=VGroup(*[card(label,width=2.25,size=32,color=c) for label,c in [('w',GOLD),('x',RED),('y',GREEN),('z',BLUE)]]).arrange(RIGHT,buff=.32).move_to([0,.1,0]);self.fixed(special)
   self.fixed(txt('스칼라 1개 + 벡터 3개',27,MUTED).move_to([0,-1.05,0]))
  elif mode=='identity':
   special=VGroup(card('[1,0,0,0]',width=4.5,color=GREEN),card('[-1,0,0,0]',width=4.5,color=BLUE)).arrange(RIGHT,buff=.8).move_to([0,0,0]);self.fixed(special)
  elif mode=='general-inverse':
   special=VGroup(card('q = [2,0,0,0]',width=4.9,color=BLUE),card('q⁻¹ = [0.5,0,0,0]',width=4.9,color=GREEN)).arrange(RIGHT,buff=.6).move_to([0,-.15,0]);self.fixed(special)
  elif mode=='hamilton':
   formula=VGroup(fit(txt('s₁s₂ - v₁·v₂',36,GOLD),11),fit(txt('s₁v₂ + s₂v₁ + v₁×v₂',36,GREEN),11)).arrange(DOWN,buff=.55).move_to([0,-.5,0]);self.fixed(formula)
  elif mode=='difference':
   special=VGroup(card('현재 a',width=3.2,color=BLUE),card('델타 Δ',width=3.2,color=GOLD),card('목표 b',width=3.2,color=GREEN)).arrange(RIGHT,buff=.6).move_to([0,0,0]);self.fixed(special)
   self.fixed(Arrow(special[0].get_right(),special[1].get_left(),buff=.03,color=MUTED),Arrow(special[1].get_right(),special[2].get_left(),buff=.03,color=MUTED))
  elif mode=='dot':
   special=VGroup(*[card(v,width=3.5,size=29,color=c) for v,c in [('a·b',BLUE),('|a·b|',GOLD),('2 acos(d)',GREEN)]]).arrange(RIGHT,buff=.45).move_to([0,0,0]);self.fixed(special)
  elif mode=='limits':
   special=VGroup(*[card(v,width=3.55,size=28,color=c) for v,c in [('Quaternion 16 B',GOLD),('Euler: 각도 편집',BLUE),('Matrix: 벡터 변환',GREEN)]]).arrange(RIGHT,buff=.4).move_to([0,-.15,0]);self.fixed(special)
  elif mode=='summary':
   special=VGroup(*[card(v,width=10.9,size=28,color=GREEN) for v in ['단위 축·반각·네 성분 / 자유도 3','±q의 자세 / 켤레·일반 역원 구분','곱셈 순서·기준 공간 / 재적용으로 검증']]).arrange(DOWN,buff=.26).move_to([0,-.5,0]);self.fixed(special)
  def display(text,color=GREEN):
   nonlocal note
   note=self.replace_fixed(note,fit(txt(text,25,color),12 if flat else 6).move_to([0 if flat else 3.12,-2.35,0]))
  def equation(text):
   nonlocal formula
   formula=self.replace_fixed(formula,fit(txt(text,29,GOLD),6).move_to([3.12,-.2,0]))
  def turn(x,O,axis,angle,seconds=1):self.play(Rotate(x,angle=angle,axis=axis,about_point=O),run_time=seconds)
  for i,beat in enumerate(s['beats']):
   ts=slot['lineStarts'][min(i,len(slot['lineStarts'])-1)]
   if ts>self.renderer.time+1/60:self.wait(ts-self.renderer.time,frozen_frame=True)
   active=self.replace_fixed(active,card(beat,width=12 if flat else 6,size=26,color=GREEN if i==len(s['beats'])-1 else BLUE).move_to([0 if flat else 3.12,1.65,0]))
   if mode=='overview':self.play(Indicate(special[min(i,3)],color=GREEN),run_time=.6)
   elif mode=='components':
    if i==0:self.play(Indicate(special[0],color=GOLD),run_time=.7)
    if i==1:display('한 제약 조건 / 연속 자유도 3')
    if i==4:display('ij = k / ji = -k',RED)
   elif mode=='half-angle':
    if i==1:equation('q = [cos(θ/2), n sin(θ/2)]')
    if i==2:equation('θ=0 → [1,0,0,0]')
    if i==3:equation('θ=90° / θ/2=45°');turn(obj,origin,P[:,2],PI/2,1.4)
    if i==4:display('실제 자세는 Z90° / 반각으로 저장')
   elif mode=='double-angle':
    if i==0:turn(obj,origin,P[:,2],PI/2,1);equation('q90 = [c,0,0,c] / c=√2/2')
    if i==1:equation('scalar(q90²) = 0')
    if i==2:equation('vector(q90²) = (0,0,1)')
    if i==3:equation('q90² = [0,0,0,1]');turn(obj,origin,P[:,2],PI/2,1)
    if i==4:equation('q90⁴ = [-1,0,0,0]');turn(obj,origin,P[:,2],PI,1.6)
   elif mode=='double-cover':
    if i in [0,2]:self.play(*[Indicate(x[1],color=GOLD) for x in objects],run_time=.8)
    if i==1:equation('q*=[w,-x,-y,-z] / -q≠q*')
    if i==3:display('회전 거리로 비교 / 성분만 비교하지 않기')
    if i==5:display('끝 자세에 회전 이력은 저장되지 않음')
   elif mode=='identity':
    if i in [0,1]:self.play(Indicate(special[i],color=GOLD),run_time=.7)
    if i==2:display('(-1q)q = -q / R(-q)=R(q)')
    if i==3:display('[0,0,0,0]는 단위 회전 입력이 아님',RED)
   elif mode=='normalize':
    if i==0:self.play(*[Indicate(x,color=GOLD) for x in special],run_time=.8)
    if i==2:display('모든 성분을 같은 ||q||로 나눔')
    if i==3:display('isfinite(norm) && norm > epsilon',RED)
    if i==4:display('비단위 q: q[0,v]q⁻¹에서 크기 상쇄')
   elif mode=='conjugate':
    if i==0:equation('q* = [w,-x,-y,-z]')
    if i==1:turn(obj,origin,P[:,2],PI/2,1)
    if i==2:equation('q90* = [c,0,0,-c]');turn(obj,origin,P[:,2],-PI/2,1)
    if i==3:equation('q90 q90* = [1,0,0,0]')
    if i==4:display('켤레 / 전체 부호 반전 구분',RED)
   elif mode=='general-inverse':
    if i==1:display('||[2,0,0,0]||² = 4')
    if i==2:self.play(Indicate(special[1],color=GOLD),run_time=.7)
    if i==3:display('검증: q q⁻¹ = [1,0,0,0]')
    if i==5:display('q=0 또는 비유한 입력: 역원 사용 금지',RED)
   elif mode=='hamilton':
    if i in [1,2]:self.play(Indicate(formula[i-1],color=GOLD),run_time=.8)
    if i==3:display('외적 순서 반전 → 부호 반전',RED)
    if i==4:display('결합법칙 성립 / 교환법칙은 일반적으로 불성립')
   elif mode=='composition':
    if i==1:turn(objects[0],origins[0],P[:,0],PI/2,.9)
    if i==2:turn(objects[0],origins[0],P[:,1],PI/2,.9);display('왼쪽 앞 방향: -y')
    if i==3:
     turn(objects[1],origins[1],P[:,1],PI/2,.9);turn(objects[1],origins[1],P[:,0],PI/2,.9);display('오른쪽 앞 방향: +x')
    if i==4:equation('world: Δq / body: qΔ')
   elif mode=='difference':
    if i==1:display('Δworld a = b → Δworld = b a⁻¹')
    if i==2:display('a Δbody = b → Δbody = a⁻¹ b')
    if i==3:display('Z30° + Z60° = Z90°')
    if i==5:self.play(Indicate(special[2],color=GOLD),run_time=.7)
   elif mode=='dot':
    if i==1:self.play(Indicate(special[1],color=GOLD),run_time=.7)
    if i==2:self.play(Indicate(special[2],color=GOLD),run_time=.7);display('θmin ∈ [0°,180°]')
    if i==3:display('q·(-q)=-1 / |dot|=1 / θmin=0°')
    if i==4:display('단위 검증 → 미세 오차 clamp → acos')
   elif mode=='power':
    if i==1:equation('q^0.5 = [cos22.5°,0,0,sin22.5°]');turn(objects[0],origins[0],P[:,2],PI/4,1.2)
    if i==2:display('log q: 벡터 크기 θ/2')
    if i==3:display('회전벡터와 log q: 2배 차이',RED)
    if i==4:turn(objects[1],origins[1],P[:,2],-3*PI/4,1.6);display('선택한 -q 가지의 절반: Z-135°',RED)
   elif mode in ['sandwich','practice']:
    if i==0:vector=arrow(origin,origin+.8*P@np.array([1.,0,1]),GOLD,6);self.add(vector);equation('v = (1,0,1)')
    if mode=='sandwich':
     if i==2:equation('q[0,v]: scalar = -√2/2')
     if i==3:
      equation('q[0,v]q⁻¹ = [0,0,1,1]');self.play(Transform(vector,arrow(origin,origin+.8*P@np.array([0.,1,1]),GOLD,6)),run_time=1.1);turn(obj,origin,P[:,2],PI/2,1)
     if i==4:display('z는 유지 / x → y')
    else:
     if i==2:
      equation('v′=(0,1,1) / ||v′||=√2');self.play(Transform(vector,arrow(origin,origin+.8*P@np.array([0.,1,1]),GOLD,6)),run_time=1.1);turn(obj,origin,P[:,2],PI/2,1)
     if i==3:display('전체 부호 -q: 같은 회전 / 역회전 아님',RED)
     if i==4:
      equation('q*로 복원: v=(1,0,1)');self.play(Transform(vector,arrow(origin,origin+.8*P@np.array([1.,0,1]),GOLD,6)),run_time=1.1);turn(obj,origin,P[:,2],-PI/2,1)
   elif mode=='limits':
    if i<3:self.play(Indicate(special[i],color=GOLD),run_time=.6)
    if i==3:display('wxyz / xyzw · Hamilton · 좌표축 · input/output')
   elif mode=='summary' and i<3:self.play(Indicate(special[i],color=GREEN),run_time=.7)
  remaining=slot['seconds']-self.renderer.time
  if remaining>1/60:self.wait(remaining,frozen_frame=True)

def make_scenes(slug,module):
 data=json.loads((ROOT/f'production/batches/game-math-part2-full-series/lessons/{slug}.json').read_text(encoding='utf8'))
 return {'Scene'+s['id']:type('Scene'+s['id'],(QuaternionScene,),{'slug':slug,'sid':s['id'],'__module__':module}) for s in data['scenes'] if s['kind']=='explanation'}
