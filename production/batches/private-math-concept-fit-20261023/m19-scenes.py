"""Editable mesh teaching stages; fixed geometry, separate topology and shading guides."""
from pathlib import Path
import importlib.util,json,os
import numpy as np
from manim import *
spec=importlib.util.spec_from_file_location('depth_stage',Path(__file__).with_name('m18-scenes.py'));b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
v=b.v;text=b.text;BG=b.BG;FG=b.FG;BLUE=b.BLUE;GREEN=b.GREEN;YELLOW=b.YELLOW;SECOND=b.SECOND
TITLES={'02':'형태의 윤곽 / 표면의 무늬','06':'이음선과 삼각형 연결은 다릅니다','07':'위치 고정 · 법선 방향만 비교','10':'평면과 곡면이 만나는 경계','11':'구멍의 실제 형태와 표면 방향','15':'실루엣과 밝기를 따로 점검'}
PHRASES={
'02':['지붕의 외곽과 기와 선 구분','지붕 회전 / 높이 변경','우리 모형: 표면 격자와 외곽','게임의 숨은 삼각형 수는 미확인','명시한 작은 메시로 저장 방식 확인'],
'06':['부품 외곽과 판의 이음선 구분','형태 변경 ≠ 면 안의 선','우리 판: 4정점과 2삼각형','게임 이음선 ≠ 확인된 인덱스','0—2는 우리가 정한 연결','위치와 빛 계산 방향을 분리','표면은 고정 · 화살표만 변경'],
'07':['꺾인 윤곽과 면의 밝기','보이는 각짐만으로 법선을 추정하지 않기','빛 고정 · 서로 다른 면 방향','재질과 그림자도 밝기에 영향','같은 위치 / 다른 셰이딩 법선','육각기둥의 실루엣은 그대로'],
'10':['벽·지붕·탑이 만나는 곳','매끄러운 방향과 실제 경계','이웃 법선을 합산하고 필요한 곳은 분리'],
'11':['평평한 벽 / 구멍의 둥근 경계','윤곽과 면 안 밝기는 다른 단서','구멍 내부의 실제 두께','게임 정점 수·알고리즘은 미확인','이웃 면의 방향을 합산','날카로운 경계를 무조건 평균하지 않기','연결할 면과 분리할 면 선택'],
'15':['평면과 둥근 가장자리','밝기를 섞어도 구멍은 남음','기하 위치 / 셰이딩 방향','상자 경계는 법선 분리','적은 정점보다 의도에 맞는 결과','가로 확대 뒤 법선은 어떻게?','다음: 접선과 법선의 수직 검산']}
def hole():
 fs=[];N=32
 for k in range(N):
  a=TAU*k/N;z=TAU*(k+1)/N
  def p(t,outer,y):
   r=1.8/max(abs(np.cos(t)),abs(np.sin(t))) if outer else .78
   return [r*np.cos(t),y,1.9+r*np.sin(t)]
  fs += [(np.array([p(a,True,-.3),p(z,True,-.3),p(z,False,-.3),p(a,False,-.3)]),'#B4C6CE'),(np.array([p(a,True,.3),p(a,False,.3),p(z,False,.3),p(z,True,.3)]),'#8096A8'),(np.array([p(a,False,-.3),p(z,False,-.3),p(z,False,.3),p(a,False,.3)]),'#6D8D98')]
 return fs
def hexagon():
 fs=[]
 for k in range(6):
  a=TAU*k/6;z=TAU*(k+1)/6
  fs.append((np.array([[1.5*np.cos(a),1.5*np.sin(a),0],[1.5*np.cos(z),1.5*np.sin(z),0],[1.5*np.cos(z),1.5*np.sin(z),2.4],[1.5*np.cos(a),1.5*np.sin(a),2.4]]),['#6AA4CB','#93C7E8','#C0D8E8','#8AA6BD','#4B728B','#7AA6C4'][k]))
 fs.append((np.array([[1.5*np.cos(TAU*k/6),1.5*np.sin(TAU*k/6),2.4] for k in range(6)]),'#D0E2E9'));return fs
class Replacement(Scene):
 sid=''
 def construct(self):
  slot=next(s for s in json.loads(Path(os.environ['MATH_RENDER_TIMING']).read_text(encoding='utf8'))['scenes'] if s['id']==self.sid)
  self.camera.background_color=BG;self.add(v.v.base.fit(text(TITLES[self.sid],34,YELLOW),11.5).to_corner(UL,buff=.45),text('우리 설명 모형',18,SECOND).to_corner(UR,buff=.45))
  az=ValueTracker(-65*DEGREES);elev=ValueTracker(26*DEGREES);yaw=ValueTracker(0);height=ValueTracker(1.7);blend=ValueTracker(0);phase=[0];active=None;metric=None
  def drawing():
   target=np.array([0,0,1.3]);eye=target+9*np.array([np.cos(elev.get_value())*np.cos(az.get_value()),np.cos(elev.get_value())*np.sin(az.get_value()),np.sin(elev.get_value())]);f=target-eye;f/=np.linalg.norm(f);r=np.cross(f,[0,0,1]);r/=np.linalg.norm(r);u=np.cross(r,f);center=np.array([-3.55,.10,0])
   def pr(p):q=np.array(p)-eye;z=np.dot(q,f);return center+np.array([np.dot(q,r),np.dot(q,u),0])*6.7/z,z
   fs=[];lines=[];marks=[];normals=[];i=phase[0]
   if self.sid=='02':
    fs=b.cuboid(0,0,2.8,2.3,height.get_value(),BLUE);h=height.get_value();c=np.cos(yaw.get_value());s=np.sin(yaw.get_value());rot=np.array([[c,-s,0],[s,c,0],[0,0,1]])
    roof=[np.array([[-1.65,-1.4,h],[1.65,-1.4,h],[1.65,0,h+1.1],[-1.65,0,h+1.1]]),np.array([[-1.65,0,h+1.1],[1.65,0,h+1.1],[1.65,1.4,h],[-1.65,1.4,h]])]
    for p in roof:
     p=p@rot.T;fs.append((p,'#88B8A0'))
     for t in np.linspace(0,1,7):lines.append((p[0]*(1-t)+p[1]*t,p[3]*(1-t)+p[2]*t,BLUE,2))
     for t in np.linspace(0,1,5):lines.append((p[0]*(1-t)+p[3]*t,p[1]*(1-t)+p[2]*t,BLUE,2))
     for a,z in zip(p,np.roll(p,-1,axis=0)):lines.append((a,z,YELLOW,4))
   elif self.sid=='06':
    p=np.array([[-1.7,0,.25],[1.7,0,.25],[1.7,0,2.8],[-1.7,0,2.8]])
    fs=[(p[[0,1,2]],'#5A8DAC'),(p[[0,2,3]],'#8AB7CA')]
    if i<2:
     for t in np.linspace(.125,.875,7):lines.append((p[0]*(1-t)+p[1]*t,p[3]*(1-t)+p[2]*t,SECOND,2))
    if i>=2:
     lines.append((p[0],p[2],YELLOW,5));marks=[(p[k],str(k)) for k in range(4)]
    if i>=5:
     for q in [p.mean(axis=0),p[0],p[2]]:normals.append((q,np.array([.55*blend.get_value(),-1,.2*blend.get_value()]),GREEN))
   elif self.sid=='07':
    fs=[];normals=[];light=np.array([-.5,-.8,.7]);light/=np.linalg.norm(light)
    def lit(n):
     n=n/np.linalg.norm(n);value=.22+.78*max(0,float(np.dot(n,light)));rgb=np.rint(np.array([145,190,225])*value).astype(int);return '#'+''.join(f'{q:02x}' for q in rgb)
    for k in range(6):
     aa=TAU*k/6;zz=TAU*(k+1)/6;a=(aa+zz)/2;n=np.array([np.cos(a),np.sin(a),0]);n0=np.array([np.cos(aa),np.sin(aa),0]);n1=np.array([np.cos(zz),np.sin(zz),0]);p0=1.5*n0;p1=1.5*n1
     for cell in range(12):
      u0=cell/12;u1=(cell+1)/12;sample_u=(u0+u1)/2;q0=p0*(1-u0)+p1*u0;q1=p0*(1-u1)+p1*u1;nn=n*(1-blend.get_value())+(n0*(1-sample_u)+n1*sample_u)*blend.get_value()
      fs.append((np.array([q0,q1,q1+[0,0,2.4],q0+[0,0,2.4]]),lit(nn)))
     mid=np.array([1.3*np.cos(a),1.3*np.sin(a),1.2]);normals.append((mid,n,BLUE))
     if i>=4:
      a=TAU*k/6;q=np.array([1.5*np.cos(a),1.5*np.sin(a),1.2]);normals.append((q,np.array([np.cos(a),np.sin(a),0]),GREEN))
    fs.append((np.array([[1.5*np.cos(TAU*k/6),1.5*np.sin(TAU*k/6),2.4] for k in range(6)]),lit(np.array([0,0,1]))));normals.append((np.array([0,0,2.4]),np.array([0,0,1]),BLUE))
   elif self.sid=='10':
    fs=v.architecture()
    for k in range(24):
     a=TAU*k/24;z=TAU*(k+1)/24;fs.append((np.array([[.8+.65*np.cos(a),-1.5+.65*np.sin(a),0],[.8+.65*np.cos(z),-1.5+.65*np.sin(z),0],[.8+.65*np.cos(z),-1.5+.65*np.sin(z),2.2],[.8+.65*np.cos(a),-1.5+.65*np.sin(a),2.2]]),'#8FA9B5'))
    fs.append((np.array([[.8+.65*np.cos(TAU*k/24),-1.5+.65*np.sin(TAU*k/24),2.2] for k in range(24)]),'#CBDCE3'))
    lines=[(np.array([-.8,-.8,2.5]),np.array([.8,-.8,2.5]),YELLOW,4)]
   else:
    fs=hole()
    if i>=2:
     for k in range(6):
      a=TAU*k/6;normals.append((np.array([.79*np.cos(a),0,1.9+.79*np.sin(a)]),np.array([-np.cos(a),0,-np.sin(a)]),GREEN))
    if i>=4:normals.append((np.array([1.35,-.31,2.9]),np.array([0,-1,0]),BLUE))
   g=VGroup();shapes=[]
   for pts,col in fs:
    pp=[pr(p) for p in pts];shapes.append((np.mean([z for p,z in pp]),Polygon(*[p for p,z in pp],fill_color=col,fill_opacity=1,stroke_color=col if self.sid=='07' else BG,stroke_width=.35 if self.sid=='07' else .6)))
   for _,shape in sorted(shapes,key=lambda z:z[0],reverse=True):g.add(shape)
   for a,z,col,w in lines:g.add(Line(pr(a)[0],pr(z)[0],color=col,stroke_width=w))
   for q,label in marks:g.add(Dot(pr(q)[0],color=YELLOW,radius=.055),text(label,26,YELLOW).move_to(pr(q)[0]+[.15,.20,0]))
   for q,n,col in normals:
    n=n/np.linalg.norm(n)
    if self.sid=='07' and np.dot(n,eye-q)<0:continue
    a=pr(q)[0];z=pr(q+.85*n)[0]
    if np.linalg.norm(z-a)>.02:g.add(Arrow(a,z,buff=0,color=col,stroke_width=5,max_tip_length_to_length_ratio=.23))
   return g
  model=always_redraw(drawing);self.add(model)
  notes={
  '02':['외곽선은 노랑 / 표면 격자는 파랑','지붕 방향과 높이를 바꾸는 조작','무늬 선 ≠ 확인된 메시 연결선','내부 데이터는 원본 프로젝트로 확인','다음: 4정점과 인덱스 목록'],
  '06':['겉으로 보이는 선과 데이터 구분','부품 유무는 전체 형태에 영향','(0, 1, 2) / (0, 2, 3)','게임 내부의 연결 정보는 미확인','노랑 대각선: 명시한 공통 모서리','위치는 그대로 · 방향 정보는 별도','초록 화살표: 설명용 법선'],
  '07':['색·빛·그림자와 형태를 따로 관찰','법선 숫자를 게임에서 읽은 것 아님','파랑: 면의 수직 방향','밝기만으로 내부 방향을 역산하지 않기','초록: 정점에 저장할 방향','법선 안내만 변경 · 실루엣 고정'],
  '10':['평평한 면과 둥근 표면 구분','경계의 위치와 방향 정보는 별도','다음: 같은 정점에 연결된 면'],
  '11':['구멍은 표면 색이 아니라 빈 공간','바깥 모양과 조명 입력 분리','앞면·뒷면 사이의 두께','우리 모형의 구조만 명시','초록: 구멍 안쪽 표면 방향','파랑: 평평한 앞면의 방향','경계에서는 레코드를 나눌 수 있음'],
  '15':['같은 벽을 다른 질문으로 점검','표면 방향만 바꿔도 구멍은 유지','지금 화살표는 자체 모형의 방향','기하 위치와 전체 레코드를 구분','의도한 모서리와 조명을 맞추기','다음: 비균일 확대','수직 조건 n · t = 0 확인']}
  for i,tm in enumerate(slot['lineStarts']):
   if tm>self.renderer.time:self.wait(tm-self.renderer.time)
   phase[0]=i
   if active:self.remove(active)
   if metric:self.remove(metric)
   active=v.v.base.fit(text(PHRASES[self.sid][i],27),5.8).move_to([3.2,1.65,0]);metric=v.v.base.fit(text(notes[self.sid][i],25,GREEN if i%2 else YELLOW),5.8).move_to([3.2,.05,0]);self.add(active,metric);model.update(0)
   if self.sid=='02' and i==1:self.play(yaw.animate.set_value(PI/2),height.animate.set_value(2.1),run_time=2)
   elif self.sid=='06' and i==6:self.play(blend.animate.set_value(1),run_time=1.8)
   elif self.sid=='07' and i==2:self.play(az.animate.set_value(-30*DEGREES),run_time=1.8)
   elif self.sid=='07' and i==4:self.play(blend.animate.set_value(1),run_time=1.8)
   elif self.sid in ['11','15'] and i==2:self.play(az.animate.set_value(-28*DEGREES),run_time=1.8)
   model.update(0)
  if self.renderer.time<slot['seconds']:self.wait(slot['seconds']-self.renderer.time)
for sid in TITLES:globals()['Scene'+sid]=type('Scene'+sid,(Replacement,),{'sid':sid,'__module__':__name__})
