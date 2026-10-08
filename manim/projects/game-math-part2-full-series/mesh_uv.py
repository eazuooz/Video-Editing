"""Original projected spatial mesh/normal/UV explanations, timed to narration.

Projection only lays out diagrams; mathematical values use explicit column vectors.
Each surface has visible side/top faces. UV artwork is original vector geometry.
"""
import json,math
import numpy as np
from manim import *
from lesson import ROOT,txt,fit,timing,INK,MUTED,RULE,RED,GREEN,BLUE,GOLD,PALE
from rendering_light import prism,poly,project,vec,segment,VIEW

def tag(p,text,color=INK,size=21):
 return fit(txt(text,size,color),3.4).move_to(project(p)+[0,.16,0])
def plane(points,color=PALE):
 # True thin triangular plate with front/side faces; presentation z is up.
 v=np.asarray(points,float);back=v+[0,0,-.14]
 return VGroup(poly(back,'#a9b5be'),*[poly([v[j],v[(j+1)%len(v)],back[(j+1)%len(v)],back[j]],'#c2ccd3') for j in range(len(v))],poly(v,color))
def quad(stage=0):
 pts=[[-1.8,-1,0],[1.8,-1,0],[1.8,1,0],[-1.8,1,0]]
 tris=[[pts[j] for j in ids] for ids in [(0,1,2),(0,2,3)]]
 g=VGroup(*[plane(t,PALE if j==0 else '#d8e7d7') for j,t in enumerate(tris)])
 for j,p in enumerate(pts):g.add(Dot(project(p),radius=.075,color=BLUE),tag(np.array(p)+[0,0,.26],str(j),BLUE))
 if stage==1:g.add(segment(pts[0],pts[2],RED,5))
 return g
def records(count=4,indices=False):
 g=VGroup();labels=VGroup()
 for j in range(count):
  row=j//3;col=j%3;p=np.array([-1.55+1.45*col,0,.6-1.1*row])
  g.add(prism(p,[1.04,.65,.28],PALE))
  labels.add(tag(p+[0,-.1,.46],str(j) if not indices else ['0','1','2','0','2','3'][j],BLUE,24))
 g.add(labels)
 return g
def cylinder(smooth=False,normals=False,n=6):
 g=VGroup();radius=1.45;z0=-.65;z1=.8
 # Sort translucent-free faces in projected depth and keep same silhouette.
 faces=[]
 for j in range(n):
  a=2*PI*j/n;b=2*PI*(j+1)/n
  if np.dot([math.cos((a+b)/2),math.sin((a+b)/2),0],VIEW)<=0:continue
  strips=10 if smooth else 1
  for k in range(strips):
   t=k/strips;u=(k+1)/strips
   pa=np.array([radius*math.cos(a),radius*math.sin(a),z0]);pb=np.array([radius*math.cos(b),radius*math.sin(b),z0]);p=pa*(1-t)+pb*t;q=pa*(1-u)+pb*u
   direction=np.array([math.cos(a),math.sin(a),0])*(1-(t+u)/2)+np.array([math.cos(b),math.sin(b),0])*(t+u)/2 if smooth else np.array([math.cos((a+b)/2),math.sin((a+b)/2),0])
   direction/=np.linalg.norm(direction);strength=max(0,np.dot(direction,np.array([-.45,-.86,.24])))
   color=interpolate_color(ManimColor('#748b72'),ManimColor('#eef3e8'),strength)
   face=Polygon(*[project(x) for x in [p,q,q+[0,0,z1-z0],p+[0,0,z1-z0]]],stroke_width=0,fill_color=color,fill_opacity=1)
   faces.append((np.dot((p+q)/2,VIEW),face))
 for _,face in sorted(faces,key=lambda x:x[0]):g.add(face)
 top=[[radius*math.cos(2*PI*j/n),radius*math.sin(2*PI*j/n),z1] for j in range(n)];g.add(poly(top,PALE))
 if normals:
  for j in range(n):
   a=2*PI*j/n;p=np.array([radius*math.cos(a),radius*math.sin(a),0]);nvec=np.array([math.cos(a),math.sin(a),0]);g.add(vec(p,p+nvec*.75,GREEN,2))
 return g
def cube(split=False):
 g=prism([0,0,0],[2.2,2.2,1.6],PALE)
 corner=np.array([1.1,-1.1,.8])
 if split:
  for n,c in [(np.array([1,0,0]),RED),(np.array([0,-1,0]),BLUE),(np.array([0,0,1]),GREEN)]:g.add(vec(corner,corner+n*1.08,c,3))
 else:g.add(vec(corner,corner+np.array([1,-1,1])/math.sqrt(3)*1.8,GREEN,4))
 g.add(Dot(project(corner),radius=.09,color=GOLD));return g
def fan(stage=0,biased=False):
 # Logical+x,+y,+z map to drawing+x,+z,-y. These ordered triangles
 # have exactly those three face normals; avoid unrelated artistic fan arrows.
 c=np.array([0,0,.12]);x=c+[1.8,0,0];y=c+[0,0,1.5];z=c+[0,-1.5,0]
 triangles=[[c,y,z],[c,z,x],[c,x,y]]
 if biased:
  midpoint=(z+x)/2;triangles=[[c,y,z],[c,z,midpoint],[c,midpoint,x],[c,x,y]]
 g=VGroup(*[plane(t,['#e3eafa','#dcebd7','#efe2c7','#f2ded8'][j]) for j,t in enumerate(triangles)])
 g.add(Dot(project(c),radius=.1,color=GOLD))
 dirs=[np.array([1,0,0]),np.array([0,0,1]),np.array([0,-1,0])]
 for j,n in enumerate(dirs):
  if stage>=j+1:g.add(vec(c,c+n*1.4,[RED,GREEN,BLUE][j],3))
 if stage>=4:
  n=np.array([1,-1,2 if biased else 1],float);n/=np.linalg.norm(n);g.add(vec(c,c+n*2.05,GOLD,5))
 return g
def perpendicular(stage=0):
 scaled=stage>=1;t=np.array([2 if scaled else 1,0,-1],float);n=np.array([1,0,1],float)
 if stage in [2,3]:n[0]=2
 if stage>=4:n[0]=.5
 if stage in [3,5,6]:n/=np.linalg.norm(n)
 t=t/np.linalg.norm(t)*2.15
 # Thin surface tangent to t, visibly projected with thickness and depth.
 points=[-t+[0,-.7,0],t+[0,-.7,0],t+[0,.7,0],-t+[0,.7,0]]
 g=plane(points);g.add(vec([0,0,0],t,BLUE),vec([0,0,0],n*1.6,RED if stage in [2,3] else GREEN))
 g.add(tag(t,'t′' if scaled else 't',BLUE),tag(n*1.6,'n′' if scaled else 'n',RED if stage in [2,3] else GREEN))
 return g
TEXTURE=['#e4ead8','#dbe8f4','#f0d9d2','#f0e2b7']
def uv_plate(kind='full',out=1,address='repeat',flat=False):
 # Original asymmetric labelled4quadrant texture. Sampling at cell centers.
 size=3.55;cells=12;g=VGroup(prism([0,0,-.12],[size,size,.24],PALE))
 for iy in range(cells):
  for ix in range(cells):
   u=(ix+.5)/cells*out;v=(iy+.5)/cells*out
   if kind=='crop':u=.25+u*.5;v=.25+v*.5
   elif kind=='rotate':u,v=v,1-u
   elif kind=='flip':u=1-u
   elif kind=='wrong':u=0;v=0
   if address=='clamp':u=max(0,min(1,u));v=max(0,min(1,v))
   elif address=='mirror':u=1-abs(u%2-1);v=1-abs(v%2-1)
   else:u=u-math.floor(u);v=v-math.floor(v)
   q=min(1,int(v*2))*2+min(1,int(u*2));x=-size/2+ix*size/cells;y=-size/2+iy*size/cells;d=size/cells
   g.add(Polygon(*[project(p) for p in [[x,y,.02],[x+d,y,.02],[x+d,y+d,.02],[x,y+d,.02]]],stroke_width=0,fill_color=TEXTURE[q],fill_opacity=1))
 if kind=='full' and out==1:
  for j,(x,y) in enumerate([[-.88,-.88],[.88,-.88],[-.88,.88],[.88,.88]]):g.add(tag([x,y,.08],str(j+1),INK,29))
 # Explicit vertex pins on unchanged geometry in every mapping.
 for p in [[-size/2,-size/2,.05],[size/2,-size/2,.05],[size/2,size/2,.05],[-size/2,size/2,.05]]:g.add(Dot(project(p),radius=.065,color=BLUE))
 return g
def mappings(stage=0):return uv_plate(['full','full','crop','rotate','flip','crop','full'][min(stage,6)])
def diagram(mode,i):
 if mode=='overview':return [quad(),records(4),cube(True),uv_plate()][min(i,3)]
 if mode=='mesh-overview':return [quad(),records(4),fan(4),cube(True)][min(i,3)]
 if mode=='transform-uv-overview':return [perpendicular(2),perpendicular(5),uv_plate(),uv_plate(out=2)][min(i,3)]
 if mode=='representation':
  if i<3:
   g=VGroup(prism([-.65,0,0],[1.9,1.8,1.5],PALE),prism([.65,.55,.3],[1.5,1.4,1.5],'#dbe6d5'))
   if i==1:
    g=prism([0,0,0],[2.5,2.5,1.5],PALE)
    hole=[[.6*math.cos(a),.6*math.sin(a),.755] for a in np.linspace(0,2*PI,41)]
    g.add(poly(hole,'#88989d'))
    bottom=[[.42*math.cos(a),.42*math.sin(a),.56] for a in np.linspace(0,2*PI,41)]
    g.add(poly(bottom,'#46595d'))
   if i==2:g.add(tag([0,0,1.25],'부피 → 표시할 표면',BLUE))
   return g
  return quad(i>=4)
 if mode=='indexed':return quad() if i==0 else records(6,indices=True) if i in [1,3] else records(4) if i in [2,4,6] else records(1)
 if mode=='topology':
  g=quad(i>=3)
  if i in [1,2]:
   ps=[[-1.8,-1,.18],[1.8,-1,.18],[1.8,1,.18]];order=[0,1,2] if i==1 else [0,2,1]
   for a,b in zip(order,order[1:]+order[:1]):g.add(vec(ps[a],ps[b],GREEN if i==1 else RED,3))
  if i==0:g.add(vec([-1.8,-1,0],[-1.8,-1,1.3],GREEN),vec([-1.8,-1,0],[-.5,-1,0],RED))
  return g
 if mode=='normal-kinds':return cylinder(smooth=i>=3,normals=i>=1)
 if mode=='interpolation':
  if i in [3,4]:
   g=plane([[-1.8,-.8,0],[1.8,-.8,0],[1.8,.8,0],[-1.8,.8,0]]);g.add(vec([0,0,0],[1.5,0,0],BLUE),vec([0,0,0],[0,0,1.5],RED),vec([0,0,0],[.75 if i==3 else 1.06,0,.75 if i==3 else 1.06],GREEN));return g
  return cylinder(smooth=i>0,normals=i in [2,5,6])
 if mode=='accumulation':return fan(min(i,4))
 if mode=='hard-edges':return cube(split=i>=2)
 if mode=='weighting':return fan(4,biased=i<3)
 if mode in ['normal-matrix','normal-example']:return perpendicular(i if mode=='normal-example' else [0,2,4,4,5,4,4][i])
 if mode=='uv-basics':return uv_plate() if i<5 else quad()
 if mode=='uv-mapping':return mappings(i)
 if mode=='addressing':return uv_plate(out=2,address='clamp' if i==4 else 'mirror' if i==5 else 'repeat')
 if mode=='repeat-order':return uv_plate(kind='wrong' if i==3 else 'full',out=2)
 if mode=='mesh-practice':return records(4) if i==0 else cube(True) if i in [1,3] else fan(4) if i==2 else perpendicular(5)
 if mode=='practice':return records(4) if i==0 else cube(True) if i==1 else perpendicular(5) if i==2 else uv_plate(out=2) if i==3 else VGroup(cube(True).scale(.7).shift(.9*LEFT),uv_plate().scale(.6).shift(1.6*RIGHT))
 raise ValueError(mode)

class MeshUvScene(Scene):
 slug='';sid=''
 def construct(self):
  self.camera.background_color=WHITE
  data=json.loads((ROOT/f'production/batches/game-math-part2-full-series/lessons/{self.slug}.json').read_text(encoding='utf8'))
  s=next(x for x in data['scenes'] if x['id']==self.sid);slot=next(x for x in timing(self.slug,data)['scenes'] if x['id']==self.sid)
  title=fit(txt(s['title'],38),12.5).to_corner(UL,buff=.58)
  sub=fit(txt('게임수학 Part 2 / 메시·법선·UV  ·  직접 정의한 데이터와 계산',20,MUTED),12.5).next_to(title,DOWN,aligned_edge=LEFT,buff=.13)
  self.add(title,sub,Line([-6.5,2.35,0],[6.5,2.35,0],color=RULE,stroke_width=1))
  obj=None;formula=None;stage_label=None
  for i,beat in enumerate(s['beats']):
   start=slot['lineStarts'][i]
   if start>self.renderer.time+1/60:self.wait(start-self.renderer.time,frozen_frame=True)
   # Hide old numeric statements before changing their diagram; every visible
   # formula must correspond to the current spatial state even in transitions.
   if formula is not None:self.play(FadeOut(formula),run_time=.10);self.remove(formula);formula=None
   target=diagram(s['mode'],i)
   if target.width>6.3:target.scale(6.3/target.width,about_point=target.get_center())
   # Keep every formula/artifact inside the original explanation space.
   if target.height>3.3:target.scale(3.3/target.height,about_point=target.get_center())
   target.move_to([-3.05,-.35,0])
   if obj is None:self.play(FadeIn(target),run_time=.35);obj=target
   else:self.play(Transform(obj,target),run_time=.65)
   formula=fit(txt(beat,26,BLUE),5.9).move_to([3.3,-.28,0]);self.play(FadeIn(formula),run_time=.2)
   if stage_label is not None:self.remove(stage_label)
   stage_label=fit(txt(f'{i+1}/{len(s["beats"])}  '+('형태를 보존한 원래 도식' if s['mode'] in ['interpolation','uv-mapping','repeat-order'] else '원래 예제 / 게임 내부 구현 추정 아님'),21,MUTED),12.2).move_to([0,-2.45,0]);self.add(stage_label)
   if s['mode']=='accumulation':
    code=['sum[v] = 0','cross = edge1 × edge2','sum[index] += normalize(cross)','sum=(1,1,1)','n=normalize(sum)','if length(sum)==0: handle','policy: equal face weights'][i]
    active=fit(Text(code,font='Consolas',font_size=21,color=INK,t2c={'sum':BLUE,'index':'#7c3aad','normalize':GREEN,'cross':GOLD,'if':RED,'0':GOLD}),5.85).move_to([3.3,-1.1,0]);self.play(FadeIn(active),run_time=.2)
    next_start=slot['lineStarts'][i+1] if i+1<len(slot['lineStarts']) else slot['seconds']
    if next_start>self.renderer.time+.15:self.wait(next_start-self.renderer.time-.15,frozen_frame=True)
    self.play(FadeOut(active),run_time=.15)
  remaining=slot['seconds']-self.renderer.time
  if remaining>1/60:self.wait(remaining,frozen_frame=True)

def make_scenes(slug,module):
 data=json.loads((ROOT/f'production/batches/game-math-part2-full-series/lessons/{slug}.json').read_text(encoding='utf8'))
 return {'Scene'+s['id']:type('Scene'+s['id'],(MeshUvScene,),{'slug':slug,'sid':s['id'],'__module__':module}) for s in data['scenes'] if s['kind']=='explanation'}
