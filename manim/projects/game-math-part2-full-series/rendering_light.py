"""Original white spatial diagrams for10.1, with explicitly projected3D faces.

Projection is for presentation, never a depth-buffer encoding or game capture.
Incident/view vectors point away from a surface. Plate example n·wi=cos(theta).
"""
from pathlib import Path
import json,math
import numpy as np
from manim import *
from lesson import ROOT,txt,fit,card,timing,INK,MUTED,RULE,RED,GREEN,BLUE,GOLD,PALE
VIEW=np.array([-.55,-1,.4]);ORIGIN_2D=np.array([-3.12,-.38,0.]);SCALE=.80
def project(p,origin=ORIGIN_2D,scale=SCALE):
 p=np.asarray(p);return np.array([p[0]-.55*p[1],.4*p[1]+p[2],0])*scale+origin
def mark(p,label,color=INK,size=23,offset=(0,.2,0)):
 return fit(txt(label,size,color),4.8).move_to(project(p)+np.array(offset))
def vec(a,b,color=GREEN,width=4):
 return Arrow(project(a),project(b),buff=0,color=color,stroke_width=width,max_tip_length_to_length_ratio=.18)
def segment(a,b,color=RULE,width=2,dashed=False):
 cls=DashedLine if dashed else Line
 return cls(project(a),project(b),color=color,stroke_width=width)
def poly(points,color,opacity=1):
 return Polygon(*[project(p) for p in points],stroke_color=RULE,stroke_width=1.1,fill_color=color,fill_opacity=opacity)
def prism(center,dimensions,color=PALE,R=None):
 c=np.asarray(center);dims=np.asarray(dimensions)/2;R=np.eye(3) if R is None else R
 faces=[]
 for axis in range(3):
  others=[i for i in range(3) if i!=axis]
  for sign in [-1,1]:
   normal=R[:,axis]*sign
   if np.dot(normal,VIEW)<=0:continue
   pts=[]
   for u,v in [(-1,-1),(1,-1),(1,1),(-1,1)]:
    p=np.zeros(3);p[axis]=sign*dims[axis];p[others[0]]=u*dims[others[0]];p[others[1]]=v*dims[others[1]];pts.append(c+R@p)
   facecolor=color if axis==2 else interpolate_color(ManimColor(color),ManimColor('#9099a1'),.28 if axis==1 else .42)
   faces.append((np.dot(np.mean(pts,axis=0),VIEW),poly(pts,facecolor)))
 return VGroup(*[f for _,f in sorted(faces,key=lambda x:x[0])])
def triangle_prism(points,color,thickness=.12):
 # A thin triangle has visible front/side faces, not a rectangular substitute.
 vertices=np.asarray(points,dtype=float)
 front=vertices+np.array([0,-thickness/2,0]);back=vertices+np.array([0,thickness/2,0])
 center=np.mean(np.concatenate([front,back]),axis=0)
 candidates=[front,back[::-1]]
 candidates.extend(np.array([front[i],front[(i+1)%3],back[(i+1)%3],back[i]]) for i in range(3))
 faces=[]
 for index,pts in enumerate(candidates):
  normal=np.cross(pts[1]-pts[0],pts[2]-pts[0]);facecenter=np.mean(pts,axis=0)
  if np.dot(normal,facecenter-center)<0:normal=-normal;pts=pts[::-1]
  if np.dot(normal,VIEW)<=0:continue
  facecolor=color if index<2 else interpolate_color(ManimColor(color),ManimColor('#9099a1'),.34)
  faces.append((np.dot(facecenter,VIEW),poly(pts,facecolor)))
 return VGroup(*[face for _,face in sorted(faces,key=lambda x:x[0])])
def surface(theta=0,color=PALE):
 a=-theta;R=np.array([[math.cos(a),0,math.sin(a)],[0,1,0],[-math.sin(a),0,math.cos(a)]])
 return prism([0,0,-.09],[3.6,2.5,.18],color,R),R[:,2]
def hemisphere(radius=2.05,color=BLUE):
 lines=VGroup()
 for az in np.linspace(0,2*PI,9)[:-1]:
  points=[project([radius*math.sin(t)*math.cos(az),radius*math.sin(t)*math.sin(az),radius*math.cos(t)]) for t in np.linspace(0,PI/2,25)]
  lines.add(VMobject(color=color,stroke_width=1.4).set_points_as_corners(points))
 for z in [0,.75,1.45]:
  r=math.sqrt(radius**2-z*z);points=[project([r*math.cos(t),r*math.sin(t),z]) for t in np.linspace(0,2*PI,45)]
  lines.add(VMobject(color=color,stroke_width=1.2).set_points_as_corners(points))
 return lines
def arrows_dome(count=8,length=1.75,color=GOLD):
 return VGroup(*[vec([0,0,0],[length*math.sin(.8)*math.cos(t),length*math.sin(.8)*math.sin(t),length*math.cos(.8)],color,2.4) for t in np.linspace(0,2*PI,count,endpoint=False)])
def light_scene(theta=0,with_dome=False):
 plane,n=surface(theta);group=VGroup(plane)
 if with_dome:group.add(hemisphere())
 group.add(vec([0,0,0],n*2.25,GREEN),mark(n*2.25,'n',GREEN,offset=(0,.15,0)))
 wi=np.array([1.2,-.6,1.85]);wo=np.array([-1.4,-1.1,1.35])
 group.add(vec([0,0,0],wi,GOLD),mark(wi,'ωᵢ: 광원 쪽',GOLD,offset=(.1,.25,0)),vec([0,0,0],wo,BLUE),mark(wo,'ωₒ: 눈 쪽',BLUE,offset=(-.2,.18,0)))
 return group
def parallel_beam(theta=0):
 # Rays intersect the actual rotated plate, rather than ending on its old
 # horizontal plane. Three guide rays are qualitative, not a photon count.
 return VGroup(*[vec([x,0,2.65],[x,0,x*math.tan(theta)+.06],GOLD,2.1) for x in [-.75,0,.75]])
def blocks(labels,colors,centers):
 return VGroup(*[VGroup(prism(c,[1.9,1.2,.64],color),mark(np.asarray(c)+[0,0,.5],label,INK,20)) for label,color,c in zip(labels,colors,centers)])

class RenderingLightScene(Scene):
 slug='';sid=''
 def replace(self,old,new):
  if old:self.play(FadeOut(old),run_time=.12);self.remove(old)
  self.play(FadeIn(new,shift=.05*UP),run_time=.22);return new
 def construct(self):
  self.camera.background_color=WHITE
  data=json.loads((ROOT/f'production/batches/game-math-part2-full-series/lessons/{self.slug}.json').read_text(encoding='utf8'));s=next(x for x in data['scenes'] if x['id']==self.sid);slot=next(x for x in timing(self.slug,data)['scenes'] if x['id']==self.sid);mode=s['mode']
  title=fit(txt(s['title'],39),12.55).to_corner(UL,buff=.58);sub=txt('게임수학 Part 2 / 렌더링 1편 · 표면 선택 / 빛의 단위 / 재질과 시선',20,MUTED).next_to(title,DOWN,aligned_edge=LEFT,buff=.14)
  self.add(title,sub,Line([-6.5,2.32,0],[6.5,2.32,0],color=RULE,stroke_width=1))
  obj=VGroup();extras=VGroup();active=None;formula=None;note=None
  def equation(value,color=BLUE):
   nonlocal formula
   formula=self.replace(formula,fit(txt(value,27,color),5.7).move_to([3.23,-.45,0]))
  def foot(value,color=MUTED):
   nonlocal note
   note=self.replace(note,fit(txt(value,23,color),12.4).move_to([0,-2.2,0]))
  def change(target,seconds=.72):
   nonlocal obj
   self.play(Transform(obj,target),run_time=seconds)
  if mode=='overview':
   obj=blocks(['1. 보이는 표면','2. 빛의 양·단위','3. 재질·시선','4. 방정식·계산'],[PALE,'#eadfbc','#dfe9de','#dfe7ed'],[[-2,-1,0],[.8,-1,.3],[-2,1.5,.6],[.8,1.5,.9]])
   obj.move_to([0,-.35,0]);self.add(obj)
  elif mode in ['ray-raster','depth-test']:
   red=triangle_prism([[-1.45,2,.05],[1.45,2,.05],[0,2,2]],'#ecd7d5');blue=triangle_prism([[-1.05,-.35,.05],[1.05,-.35,.05],[0,-.35,1.7]],'#cad9ed')
   obj=VGroup(red,blue,mark([1.2,2,1.8],'빨강: 8',RED),mark([1,-.35,1.6],'파랑: 3',BLUE),vec([0,-3.1,.85],[0,-.35,.85],GOLD),mark([0,-3.1,.85],'카메라',GOLD,offset=(-.3,-.38,0)));self.add(obj)
  elif mode=='forward-deferred':
   obj=blocks(['기하','재질·법선','조명'],[PALE,'#dfe9de','#eadfbc'],[[-1.5,-1,0],[1.2,.4,.4],[-1.2,2,.8]]);self.add(obj)
  elif mode in ['brdf-directions','rendering-equation','brdf-energy']:
   obj=light_scene(with_dome=mode!='brdf-directions');self.add(obj)
  elif mode=='scattering':
   plate=prism([0,0,-.5],[3.6,2.5,1],PALE)
   obj=VGroup(plate,vec([0,0,0],[1.2,0,1.8],GOLD),vec([0,0,0],[-1,0,1.8],BLUE));self.add(obj)
  elif mode=='energy-units':
   obj=blocks(['4 J','2 s','2 m²'],['#eadfbc',PALE,'#dfe9de'],[[-1,-.8,0],[1.4,1,.2],[-1,2.3,.45]]);self.add(obj)
  elif mode=='solid-angle':
   obj=VGroup(hemisphere(),vec([0,0,0],[0,0,2.4],GREEN),mark([0,0,2.4],'n',GREEN),surface()[0]);self.add(obj)
  elif mode=='projected-cosine':
   plate,n=surface();obj=VGroup(plate,vec([0,0,0],n*2.4,GREEN),mark(n*2.4,'n',GREEN));self.add(obj)
   extras=parallel_beam()
   self.add(extras)
  elif mode=='light-transport':
   obj=blocks(['광원','표면 A','표면 B'],['#eadfbc','#dfe9de',PALE],[[-1.1,-1,1.4],[1.2,.6,.3],[-1.6,2.6,.3]])
   extras=VGroup(vec([-1.1,-1,1.4],[1.2,.6,.3],GOLD),vec([1.2,.6,.3],[-1.6,2.6,.3],GREEN));self.add(obj,extras)
  elif mode=='sampling':
   obj=VGroup(surface()[0],hemisphere(),arrows_dome(4));self.add(obj)
  elif mode=='practice':
   obj=light_scene(with_dome=True);self.add(obj)
  for i,beat in enumerate(s['beats']):
   target=slot['lineStarts'][min(i,len(slot['lineStarts'])-1)]
   if target>self.renderer.time+1/60:self.wait(target-self.renderer.time,frozen_frame=True)
   active=self.replace(active,card(beat,width=12.0 if mode=='overview' else 6.25,size=25,color=GREEN if i==len(s['beats'])-1 else BLUE).move_to([0,1.78,0] if mode=='overview' else [3.15,1.65,0]))
   if mode=='overview':self.play(Indicate(obj[min(i,3)],color=GREEN),run_time=.6)
   elif mode=='ray-raster':
    equation(['표본 / 색 → 프레임 버퍼','pixel → ray → intersection','hit: shade / miss: background','triangle → coverage → depth','보이는 표면 → 빛 계산','여러 표본 / 후처리·복원 가능'][i])
    if i==1:self.play(Indicate(obj[4],color=GOLD),run_time=.6)
    if i==3:self.play(Indicate(obj[1],color=GREEN),run_time=.65)
    if i==5:foot('광선 방식만으로 물리적으로 정확해지지 않음')
   elif mode=='depth-test':
    equation(['작을수록 가까운 예제','∞ → 8 → 3','∞ → 3 / 8 거절','두 순서 모두 depth=3','projection depth ≠ metric distance','reversed-Z: clear와 compare 함께'][i])
    if i==1:self.play(Indicate(obj[0],color=RED),Indicate(obj[1],color=BLUE),run_time=.75)
    if i==2:
     cross=Cross(obj[0],stroke_color=RED,stroke_width=4);self.play(Create(cross),run_time=.5);extras.add(cross)
    if i==3:foot('불투명·유효 비교 / 동점 규칙 별도')
   elif mode=='forward-deferred':
    equation(['forward: geometry + shading','geometry → G-buffer','G-buffer → lighting','기하 재사용 ↔ 저장 비용','tiled / clustered forward도 존재','구조 선택 ≠ 물리 법칙'][i])
    if i in [0,1,2]:self.play(Indicate(obj[min(i,2)],color=GREEN),run_time=.65)
    if i==2:
     extras=VGroup(vec([-1.5,-1,0],[1.2,.4,.4],GREEN),vec([1.2,.4,.4],[-1.2,2,.8],GOLD));self.play(Create(extras),run_time=.7)
   elif mode=='brdf-directions':
    equation(['색 하나로 모든 반사 설명 불가','fᵣ(x,ωᵢ,ωₒ,λ)','위치 / 두 방향 / 파장','ωᵢ는 광원 쪽 / 실제 빛은 -ωᵢ','ωₒ는 눈 쪽 / n은 바깥','넓은 분포 ↔ 좁은 봉우리'][i])
    if i==3:
     travel=vec([1.2,-.6,1.85],[0,0,0],RED,2.6);self.play(Create(travel),run_time=.7);extras.add(travel)
    if i==5:
     broad=arrows_dome(8,color=GREEN);self.play(Create(broad),run_time=.7);extras.add(broad)
   elif mode=='brdf-energy':
    equation(['fᵣ의 단위: 1/sr','fᵣ > 1은 에너지 위반 증거 아님','∫ fᵣ cosθ dω ≤ 1','fᵣ ≥ 0 / 방향 교환 상반성','Lₑ는 별도의 방출 항','역사적 비정규화 식 ≠ 보존 모델'][i])
    if i==1:
     narrow=VGroup(*[vec([0,0,0],[.05*j,-.2,2.2],GOLD,3.3) for j in [-2,-1,0,1,2]]);self.play(Create(narrow),run_time=.7);extras.add(narrow)
    if i==2:
     broad=arrows_dome(10,color=GREEN);self.play(Create(broad),run_time=.7);extras.add(broad)
   elif mode=='scattering':
    equation(['BRDF: 같은 위치의 반사','BTDF / BSDF: 같은 위치의 투과 포함','BSSRDF: 입사 xᵢ ≠ 출사 xₒ','방향 추가와 위치 추가는 다름','volume: scattering + absorption','뒤 계산은 표면 반사·방출 범위'][i])
    if i==1:
     a=vec([0,0,0],[.6,0,-1.5],BLUE);self.play(Create(a),run_time=.7);extras.add(a)
    if i==2:
     a=VGroup(segment([0,0,0],[.7,.4,-.7],GREEN,dashed=True),segment([.7,.4,-.7],[1.3,.7,0],GREEN,dashed=True),vec([1.3,.7,0],[1.7,.7,1.3],BLUE),mark([1.3,.7,0],'xₒ',BLUE));self.play(Create(a),run_time=.8);extras.add(a)
     foot('내부 경로는 도식 / 숨은 선은 점선')
    if i==4:foot('안개·물속 효과를 BRDF 하나로 설명하지 않음')
   elif mode=='energy-units':
    equation(['Q=4 J / Δt=2 s','Φ=Q/Δt=2 W','E=Φ/A=2/2=1 W/m²','arrival E / departure M','에너지 ↔ 시감 효율 가중','Φ: W / 광속: lm / 조도: lx'][i])
    if i<3:self.play(Indicate(obj[i],color=GREEN),run_time=.65)
    if i==3:foot('예제는 균일한 평균 / 위치별 값은 함수')
   elif mode=='solid-angle':
    equation(['총량이 같아도 방향 분포는 다름','Ω: 단위 구에 투영한 면적','4π sr / 위쪽 반구 2π sr','L=dΦ/(dA⊥ dω)','dA⊥=dA cosθ','E=∫Ω Lᵢ cosθ dω'][i])
    if i==1:
     wedge=poly([[0,0,0],[.8,.5,1.7],[1.3,.6,1.3]],'#eadfbc',.65);self.play(FadeIn(wedge),run_time=.6);extras.add(wedge)
    if i==5:foot('입체각은 평면의 각도와 구별 / cosine 포함')
   elif mode=='projected-cosine':
    equation(['cos0°=1','cos60°=0.5','A⊥=A cosθ / 기여는 절반','|n|=|ωᵢ|=1','n·ωᵢ=cosθ / 진행 벡터는 반대','한쪽 면: max(0,n·ωᵢ)'][i])
    if i==1:
     plate,n=surface(PI/3)
     self.play(Transform(obj,VGroup(plate,vec([0,0,0],n*2.4,GREEN),mark(n*2.4,'n: 60°',GREEN))),Transform(extras,parallel_beam(PI/3)),run_time=.72)
    if i==2:foot('고정된 동일 방향별 빛 / 표면 기하만 비교')
   elif mode=='rendering-equation':
    equation(['Lₒ = Lₑ + 반사','비발광 표면: Lₑ=0','반구의 Lᵢ × fᵣ × cosθ 적분','ωₒ 고정 / ωᵢ 합산','sr⁻¹ × dω → 단위 상쇄','Lₒ는 표시용 RGB 그 자체가 아님'][i])
    if i==2:
     a=arrows_dome(8,color=GOLD);self.play(Create(a),run_time=.8);extras.add(a)
    if i==3:self.play(Indicate(obj[-2],color=BLUE),run_time=.7)
    if i==5:foot('표면 위치 x / 파장 λ 인자는 생략 표기')
   elif mode=='light-transport':
    equation(['직접 광원 / 다른 표면을 거친 간접','Lₒ(A) → Lᵢ(B)','한 점의 해가 다른 점과 연결','여러 반사·가림 경로 → 계산량','실시간 예산 / 사전·제한·혼합','광선 추적도 유한한 근사'][i])
    if i in [0,1]:self.play(Indicate(extras[i],color=GOLD if i==0 else GREEN),run_time=.65)
    if i==2:
     a=vec([-1.6,2.6,.3],[-1.1,-1,.65],BLUE);self.play(Create(a),run_time=.7);extras.add(a)
   elif mode=='sampling':
    equation(['적분은 표본의 가중 합','Σ g만 더하면 N에 비례','uniform hemisphere: p=1/(2π)','(1/N) Σ g/p / 기대값 유지','이상적 점광원: 별도 표본 모델','선형 빛의 값 → display transform'][i])
    if i==3:change(VGroup(surface()[0],hemisphere(),arrows_dome(8)))
    if i==4:foot('표본 증가 ≠ 밝기 증가 / 잡음과 정확도는 별도')
   elif mode=='practice':
    equation(['예제 결과: 파랑·깊이 3','ρ=0.6 / E=10 W/m²','Lₒ=ρE/π=6/π≈1.91','M=ρE=6 W/m² / Lₒ와 구별','정의한 조건 / 게임 픽셀 역산 아님','표면 → 단위 → 방향 / 다음 카메라'][i])
    if i==2:self.play(Indicate(obj[-2],color=BLUE),run_time=.65)
    if i==3:foot('Lₒ 단위 W/(m² sr) / 면적당 총 출사는 M')
  remaining=slot['seconds']-self.renderer.time
  if remaining>1/60:self.wait(remaining,frozen_frame=True)

def make_scenes(slug,module):
 data=json.loads((ROOT/f'production/batches/game-math-part2-full-series/lessons/{slug}.json').read_text(encoding='utf8'))
 return {'Scene'+s['id']:type('Scene'+s['id'],(RenderingLightScene,),{'slug':slug,'sid':s['id'],'__module__':module}) for s in data['scenes'] if s['kind']=='explanation'}
