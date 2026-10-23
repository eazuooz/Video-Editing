"""Editable surface/UV explanations using the existing mathematical projection stage."""
from pathlib import Path
import importlib.util,json,os
import numpy as np
from manim import *
spec=importlib.util.spec_from_file_location('surface_stage',Path(__file__).with_name('m18-scenes.py'));b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
v=b.v;text=b.text;BG=b.BG;FG=b.FG;BLUE=b.BLUE;GREEN=b.GREEN;YELLOW=b.YELLOW;SECOND=b.SECOND
TITLES={'04':'형태는 그대로 · 표면 속성 변경','05':'벽의 윤곽과 표면 정보를 분리','08':'표면은 고정 · 관찰 방향 변경','09':'반복되는 모양과 주소 규칙 구분','12':'실루엣 → 법선 → UV 순서로 점검'}
PHRASES={
'04':['같은 부품의 바깥 윤곽과 색','모서리 고정 / 표면 색만 변경','같은 판에 이미지 무늬 연결','게임의 색 변경 ≠ 확인된 UV 수정','수직 방향 다음은 이미지 좌표','위치·법선·UV는 서로 다른 입력'],
'05':['벽 윤곽과 창문 위치 유지','큰 형태와 작은 세부는 별개','표면 위치와 이미지 위치 연결','게임 내부 텍스처·주소 모드는 미확인','같은 판 / 다른 이미지 영역'],
'08':['기존 지붕과 새 지붕을 구분','무늬는 화면이 아니라 표면에 부착','관찰 방향만 바꾸어 비교','우리가 정의한 UV와 실제 장면 구분','전체 이미지 / 일부 이미지','반복된 모습만으로 주소 모드 추정 금지'],
'09':['바닥의 반복 구조 관찰','화면 위치 ≠ 표면 위치','같은 표면에 남아 있는 무늬','반복 기하와 반복 이미지는 다를 수 있음','격자선 ≠ 확인된 삼각형 인덱스','우리 예제의 UV 범위와 규칙','좌표 보간 다음 텍스처 조회'],
'12':['밝기가 달라져도 큰 윤곽 유지','형태 / 방향 / 무늬를 따로 보기','반복 개수로 정점 수를 추정하지 않기','인덱스·법선·UV의 역할 구분','실루엣 → 법선 경계 → 무늬 배치','작은 메시의 저장·계산 순서 검산']}
NOTES={
'04':['화면 관찰과 내부 데이터는 구분','같은 정점 위치 / 다른 표면 속성','UV: 표면과 이미지의 대응','색 변경의 실제 구현은 미확인','n · t = 0 다음은 (u, v)','같은 위치에도 속성은 다를 수 있음'],
'05':['큰 면의 형태를 먼저 확인','많은 세부 ≠ 많은 정점의 증거','무늬는 표면과 별도로 정의','보이는 결과만으로 구현을 단정하지 않음','4정점의 위치는 그대로'],
'08':['오른쪽 기존 지붕을 기준으로 추적','표면의 같은 부분에 무늬가 남음','자체 모형의 카메라만 이동','게임 UV를 측정한 결과 아님','우리 UV 예제에서 조건을 직접 지정','기하 반복 / 이미지 속 반복 / 주소 반복'],
'09':['반복 선과 구멍을 구분해 관찰','고정 표면 / 달라지는 화면 투영','자체 모형은 단순한 무늬 판','게임의 주소 설정은 알 수 없음','겉에 보이는 선과 데이터 구조를 분리','다음: Repeat / Clamp / Mirror','정점에서 미리 접지 않기'],
'12':['같은 표면에도 빛과 재질이 영향','각 입력의 역할을 나누어 검사','눈에 보이는 결과 ≠ 데이터 목록','연결 / 수직 방향 / 이미지 대응','처음 어긋난 속성부터 확인','다음 계산은 우리 모델의 값']}
def roof_house():
 fs=b.cuboid(0,0,2.6,2,1.7,'#B4C8D5');roof=[np.array([[-1.5,-1.2,1.7],[1.5,-1.2,1.7],[1.5,0,2.7],[-1.5,0,2.7]]),np.array([[-1.5,0,2.7],[1.5,0,2.7],[1.5,1.2,1.7],[-1.5,1.2,1.7]])]
 fs += [(p,'#8AB9A4') for p in roof]
 for x in [-.65,.65]:fs.append((np.array([[x-.18,-1.006,.7],[x+.18,-1.006,.7],[x+.18,-1.006,1.2],[x-.18,-1.006,1.2]]),'#25384C'))
 return fs,roof
def bilerp(p,u,w):return (1-u)*(1-w)*p[0]+u*(1-w)*p[1]+u*w*p[2]+(1-u)*w*p[3]
class Replacement(Scene):
 sid=''
 def construct(self):
  slot=next(s for s in json.loads(Path(os.environ['MATH_RENDER_TIMING']).read_text(encoding='utf8'))['scenes'] if s['id']==self.sid)
  self.camera.background_color=BG;self.add(v.v.base.fit(text(TITLES[self.sid],34,YELLOW),11.5).to_corner(UL,buff=.45),text('우리 설명 모형',18,SECOND).to_corner(UR,buff=.45))
  az=ValueTracker(-65*DEGREES);el=ValueTracker(28*DEGREES);colour=ValueTracker(0);uvcrop=ValueTracker(1);lightturn=ValueTracker(0);phase=[0];active=None;metric=None
  def drawing():
   target=np.array([0,0,1.25]);eye=target+9*np.array([np.cos(el.get_value())*np.cos(az.get_value()),np.cos(el.get_value())*np.sin(az.get_value()),np.sin(el.get_value())]);f=target-eye;f/=np.linalg.norm(f);r=np.cross(f,[0,0,1]);r/=np.linalg.norm(r);up=np.cross(r,f);center=np.array([-3.55,.1,0])
   def pr(p):q=np.array(p)-eye;z=np.dot(q,f);return center+np.array([np.dot(q,r),np.dot(q,up),0])*6.7/z,z
   i=phase[0];fs=[];outlines=[];marks=[];normals=[];tile_labels=[]
   panel=np.array([[-1.7,0,.3],[1.7,0,.3],[1.7,0,2.8],[-1.7,0,2.8]])
   if self.sid in ['05','08','12']:
    fs,roof=roof_house()
    if self.sid=='05' and i<4:
     rgb=np.rint(np.array([120,175,220])*(1-colour.get_value())+np.array([226,190,97])*colour.get_value()).astype(int);fs[0]=(fs[0][0],'#'+''.join(f'{q:02x}' for q in rgb))
     outlines=[np.array([[-1.3,-1.02,0],[1.3,-1.02,0],[1.3,-1.02,1.7],[-1.3,-1.02,1.7]])] if i==0 else []
    if self.sid in ['08','12']:
     # Replace the whole roof faces with their tiles. A coplanar background
     # quad sorted by its centre can otherwise cover half the checker.
     fs=[(p,c) for p,c in fs if not any(np.array_equal(p,z) for z in roof)]
     for p in roof:
      for ix in range(8):
       for iy in range(5):
        q=np.array([bilerp(p,ix/8,iy/5),bilerp(p,(ix+1)/8,iy/5),bilerp(p,(ix+1)/8,(iy+1)/5),bilerp(p,ix/8,(iy+1)/5)])+[0,0,.004];fs.append((q,BLUE if (ix+iy)%2 else '#DCE6EC'))
     if self.sid=='12' and i>=1:normals=[(np.array([0,-1.05,1]),np.array([0,-1,0])),(np.array([.5,-.6,2.2]),np.array([0,-1,1.2]))]
     if self.sid=='12':outlines=roof[:1]
    if self.sid=='05' and i>=4:fs=[]
   if self.sid in ['04','09'] or self.sid=='05' and i>=4:
    if self.sid=='09':panel=np.array([[-1.9,-1.5,.4],[1.9,-1.5,.4],[1.9,1.5,.4],[-1.9,1.5,.4]])
    rgb=np.rint(np.array([120,175,220])*(1-colour.get_value())+np.array([242,207,100])*colour.get_value()).astype(int);flat='#'+''.join(f'{q:02x}' for q in rgb)
    patterned=self.sid!='04' or i>=2
    for ix in range(12):
     for iy in range(8):
      p=np.array([bilerp(panel,ix/12,iy/8),bilerp(panel,(ix+1)/12,iy/8),bilerp(panel,(ix+1)/12,(iy+1)/8),bilerp(panel,ix/12,(iy+1)/8)])
      u=.5+((ix+.5)/12-.5)*uvcrop.get_value();w=.5+((iy+.5)/8-.5)*uvcrop.get_value();nx,ny=(3,2) if self.sid=='05' else (6,4);col=(BLUE if (int(u*nx)+int(w*ny))%2 else '#DCE6EC') if patterned else flat;fs.append((p,col))
    if self.sid=='05':
     for ty in range(2):
      for tx in range(3):
       pu=.5+((tx+.5)/3-.5)/uvcrop.get_value();pv=.5+((ty+.5)/2-.5)/uvcrop.get_value()
       if .02<pu<.98 and .02<pv<.98:tile_labels.append((bilerp(panel,pu,pv),str(1+tx+ty*3)))
    outlines=[panel];marks=[(p,chr(65+j)) for j,p in enumerate(panel)]
    if self.sid=='04' and i>=4:normals=[(panel.mean(axis=0),np.array([0,-1,0]))]
   g=VGroup();shapes=[];front_windows=[]
   light=np.array([-.5+lightturn.get_value(),-.9,.8]);light/=np.linalg.norm(light)
   for points,col in fs:
    pts=[pr(p) for p in points]
    if self.sid=='12':
     n=np.cross(points[1]-points[0],points[2]-points[0]);n/=max(np.linalg.norm(n),1e-6)
     # The input cuboid uses mixed winding. Select the exterior-facing normal
     # before the illustrative Lambert term, rather than lighting both sides.
     if np.dot(n,points.mean(axis=0)-np.array([0,0,1]))<0:n=-n
     strength=.35+.65*max(0,float(np.dot(n,light)));raw=np.array([int(col[k:k+2],16) for k in [1,3,5]]);col='#'+''.join(f'{q:02x}' for q in np.rint(raw*strength).astype(int))
    shape=Polygon(*[p for p,z in pts],fill_color=col,fill_opacity=1,stroke_color=col,stroke_width=.35)
    # Windows are attached to the visible front wall, below both roof eaves.
    if np.allclose(points[:,1],-1.006):front_windows.append(shape)
    else:shapes.append((np.mean([z for p,z in pts]),shape))
   for _,shape in sorted(shapes,key=lambda x:x[0],reverse=True):g.add(shape)
   g.add(*front_windows)
   for points in outlines:
    for a,z in zip(points,np.roll(points,-1,axis=0)):g.add(Line(pr(a)[0],pr(z)[0],color=YELLOW,stroke_width=4))
   for p,label in marks:g.add(Dot(pr(p)[0],radius=.055,color=YELLOW),text(label,24,YELLOW).move_to(pr(p)[0]+[.13,.17,0]))
   for p,label in tile_labels:g.add(text(label,22,'#101512').move_to(pr(p)[0]))
   for p,n in normals:
    n=n/np.linalg.norm(n);g.add(Arrow(pr(p)[0],pr(p+.9*n)[0],color=GREEN,buff=0,stroke_width=5,max_tip_length_to_length_ratio=.23))
   return g
  model=always_redraw(drawing);self.add(model)
  for i,tm in enumerate(slot['lineStarts']):
   if tm>self.renderer.time:self.wait(tm-self.renderer.time)
   phase[0]=i
   if active:self.remove(active)
   if metric:self.remove(metric)
   active=v.v.base.fit(text(PHRASES[self.sid][i],27),5.8).move_to([3.2,1.65,0]);metric=v.v.base.fit(text(NOTES[self.sid][i],24,GREEN if i%2 else BLUE),5.8).move_to([3.2,.05,0]);self.add(active,metric);model.update(0)
   if self.sid=='04' and i==1:self.play(colour.animate.set_value(1),run_time=1.6)
   elif self.sid=='05' and i==0:self.play(colour.animate.set_value(1),run_time=1.6)
   elif self.sid=='05' and i==4:self.play(uvcrop.animate.set_value(.5),run_time=1.8)
   elif self.sid=='08' and i==2:self.play(az.animate.set_value(-25*DEGREES),el.animate.set_value(16*DEGREES),run_time=2)
   elif self.sid=='09' and i==1:self.play(az.animate.set_value(-25*DEGREES),el.animate.set_value(15*DEGREES),run_time=2)
   elif self.sid=='12' and i==0:self.play(lightturn.animate.set_value(1.3),run_time=2)
   model.update(0)
  if self.renderer.time<slot['seconds']:self.wait(slot['seconds']-self.renderer.time)
for sid in TITLES:globals()['Scene'+sid]=type('Scene'+sid,(Replacement,),{'sid':sid,'__module__':__name__})
