"""New, dark projected explanations; existing white lectures remain unchanged.

Geometry and texture correspondence are original vector illustrations. Directions
use column vectors; x/z in the drawing is the explicit 2D worked section.
"""
import json, math
import numpy as np
from manim import *
from lesson import ROOT, fit, timing
from rendering_light import project, VIEW

BG='#000000';INK='#f5f5f5';MUTED='#b8b8b8';RULE='#6b7280'
TITLE='#e8cf83';BLUE='#73c7c2';RED='#ef8585';GREEN='#a4c6a0';GOLD='#f39a4b'
TOP='#34454b';FRONT='#243239';SIDE='#162026'

def txt(s,size=28,color=INK,font='Malgun Gothic'):
 return Text(s,font=font,font_size=size,color=color)
def poly(points,color,stroke=True):
 return Polygon(*[project(p) for p in points],stroke_color=RULE,stroke_width=.9 if stroke else 0,fill_color=color,fill_opacity=1)
def vec(a,b,color=GREEN,width=4):
 return Arrow(project(a),project(b),buff=0,color=color,stroke_width=width,max_tip_length_to_length_ratio=.15)
def tag(p,text,color=INK,size=22,offset=(0,.17,0)):
 return fit(txt(text,size,color),3.2).move_to(project(p)+offset)
def prism(center,dimensions):
 c=np.asarray(center,float);dims=np.asarray(dimensions,float)/2;faces=[]
 for axis in range(3):
  others=[i for i in range(3) if i!=axis]
  for sign in [-1,1]:
   normal=np.eye(3)[axis]*sign
   if np.dot(normal,VIEW)<=0:continue
   pts=[]
   for u,v in [(-1,-1),(1,-1),(1,1),(-1,1)]:
    p=np.zeros(3);p[axis]=sign*dims[axis];p[others[0]]=u*dims[others[0]];p[others[1]]=v*dims[others[1]];pts.append(c+p)
   faces.append((np.dot(np.mean(pts,axis=0),VIEW),poly(pts,[FRONT,SIDE,TOP][axis])))
 return VGroup(*[face for _,face in sorted(faces,key=lambda x:x[0])])
def plane(points):
 v=np.asarray(points,float);back=v+[0,0,-.16]
 return VGroup(poly(back,SIDE),*[poly([v[j],v[(j+1)%len(v)],back[(j+1)%len(v)],back[j]],FRONT) for j in range(len(v))],poly(v,TOP))
def perpendicular(stage=0):
 scaled=stage>=1;t=np.array([2 if scaled else 1,0,-1],float);n=np.array([1,0,1],float)
 if stage in [2,3]:n[0]=2
 if stage>=4:n[0]=.5
 if stage in [3,5,6]:n/=np.linalg.norm(n)
 draw_t=t/np.linalg.norm(t)*2.15
 g=plane([-draw_t+[0,-.7,0],draw_t+[0,-.7,0],draw_t+[0,.7,0],-draw_t+[0,.7,0]])
 nc=RED if stage in [1,2,3] else GREEN
 g.add(vec([0,0,0],draw_t,BLUE),vec([0,0,0],n*1.6,nc))
 g.add(tag(draw_t,'t′' if scaled else 't',BLUE),tag(n*1.6,'n (변환 전)' if stage==1 else 'n′' if scaled else 'n',nc))
 # Right-angle marker exists only when the actual semantic dot product is zero.
 if abs(np.dot(t,n))<1e-10:
  a=t/np.linalg.norm(t)*.25;b=n/np.linalg.norm(n)*.25
  g.add(poly([a,a+b,b],GREEN))
 return g

TEXTURE=['#35545a','#3d466e','#714a37','#48614a']
def mapped_uv(x,y,kind,out,address):
 u=x*out;v=y*out
 if kind=='crop':u=.25+.5*u;v=.25+.5*v
 elif kind=='rotate':u,v=v,1-u
 elif kind=='flip':u=1-u
 elif kind=='wrong':u=0
 if address=='clamp':u=max(0,min(1,u));v=max(0,min(1,v))
 elif address=='mirror':u=1-abs(u%2-1);v=1-abs(v%2-1)
 else:u-=math.floor(u);v-=math.floor(v)
 return u,v
def uv_plate(kind='full',out=1,address='repeat',pins=False):
 # v increases from the upper/back edge towards the lower/front edge. The
 # asymmetric original image has four numbers and a bright central cross.
 size=3.55;cells=16;d=size/cells;g=VGroup(prism([0,0,-.14],[size,size,.28]))
 for iy in range(cells):
  for ix in range(cells):
   u,v=mapped_uv((ix+.5)/cells,(iy+.5)/cells,kind,out,address)
   color=TEXTURE[min(1,int(v*2))*2+min(1,int(u*2))]
   if abs(u-.5)<.045 or abs(v-.5)<.045:color=TITLE
   if u<.09 or u>.91 or v<.09 or v>.91:color=SIDE
   x=-size/2+ix*d;y=size/2-iy*d
   g.add(poly([[x,y,.02],[x+d,y,.02],[x+d,y-d,.02],[x,y-d,.02]],color,False))
 # Place labels by the exact inverse UV mapping, preserving rotation and flip.
 targets=[(.18,.18),(.82,.18),(.18,.82),(.82,.82)]
 if kind!='wrong':
  for tile_y in range(math.ceil(out) if address!='clamp' else 1):
   for tile_x in range(math.ceil(out) if address!='clamp' else 1):
    for j,(u,v) in enumerate(targets):
     if address=='mirror':
      if tile_x%2:u=1-u
      if tile_y%2:v=1-v
     if kind=='crop':x=(u-.25)/.5;y=(v-.25)/.5
     elif kind=='rotate':x=1-v;y=u
     elif kind=='flip':x=1-u;y=v
     else:x=u;y=v
     x=(x+tile_x)/out;y=(y+tile_y)/out
     if 0<x<1 and 0<y<1:
      g.add(tag([-size/2+size*x,size/2-size*y,.07],str(j+1),INK,24,offset=(0,0,0)))
 corners=[[-size/2,size/2,.06],[size/2,size/2,.06],[size/2,-size/2,.06],[-size/2,-size/2,.06]]
 for j,p in enumerate(corners):
  g.add(Dot(project(p),radius=.065,color=BLUE))
  if pins:
   uv=mapped_uv(*[(0,0),(1,0),(1,1),(0,1)][j],kind,out,'clamp')
   # For full mapping preserve the endpoint1 instead of repeating it to0.
   offset=[(-.14,.30,0),(.14,.30,0),(.18,-.28,0),(-.18,-.28,0)][j]
   g.add(tag(p,f'({uv[0]:g},{uv[1]:g})',BLUE,19,offset=offset))
 return g
def records():
 g=VGroup()
 for j in range(4):
  p=np.array([-1.7+(j%2)*2,0,.7-(j//2)*1.25])
  g.add(prism(p,[1.2,.8,.36]),tag(p+[0,-.1,.38],str(j),BLUE,28))
 return g
def cube():
 g=prism([0,0,0],[2.2,2.2,1.6]);corner=np.array([1.1,-1.1,.8])
 for n,c in [(np.array([1,0,0]),RED),(np.array([0,-1,0]),BLUE),(np.array([0,0,1]),GREEN)]:g.add(vec(corner,corner+n*1.08,c,3))
 g.add(Dot(project(corner),radius=.09,color=GOLD));return g
def diagram(mode,i):
 if mode=='transform-uv-overview':return [perpendicular(2),perpendicular(5),uv_plate(),uv_plate(out=2)][min(i,3)]
 if mode in ['normal-matrix','normal-example']:return perpendicular(i if mode=='normal-example' else [0,1,4,4,5,4,4][i])
 if mode=='uv-basics':return uv_plate(pins=i in [2,3,4,6])
 if mode=='uv-mapping':return uv_plate(kind=['full','full','crop','rotate','flip','crop','full'][min(i,6)],pins=i in [0,1,2,3,4])
 if mode=='addressing':return uv_plate(out=2,address='clamp' if i==4 else 'mirror' if i==5 else 'repeat')
 if mode=='repeat-order':return uv_plate(kind='wrong' if i==3 else 'full',out=2)
 if mode=='practice':return records() if i==0 else cube() if i==1 else perpendicular(5) if i==2 else uv_plate(out=2) if i==3 else VGroup(cube().scale(.7).shift(.9*LEFT),uv_plate().scale(.6).shift(1.6*RIGHT))
 raise ValueError(mode)

class NormalTransformUvScene(Scene):
 slug='';sid=''
 def construct(self):
  self.camera.background_color=BG
  data=json.loads((ROOT/f'production/batches/game-math-part2-full-series/lessons/{self.slug}.json').read_text(encoding='utf8'))
  s=next(x for x in data['scenes'] if x['id']==self.sid);slot=next(x for x in timing(self.slug,data)['scenes'] if x['id']==self.sid)
  title=fit(txt(s['title'],38,TITLE),12.5).to_corner(UL,buff=.58)
  sub=fit(txt('게임수학 Part 2 / 법선 변환·UV  ·  직접 정의한 데이터와 계산',20,MUTED),12.5).next_to(title,DOWN,aligned_edge=LEFT,buff=.13)
  self.add(title,sub,Line([-6.5,2.35,0],[6.5,2.35,0],color=RULE,stroke_width=1))
  obj=None;formula=None;stage_label=None
  for i,beat in enumerate(s['beats']):
   start=slot['lineStarts'][i]
   if start>self.renderer.time+1/60:self.wait(start-self.renderer.time,frozen_frame=True)
   if formula is not None:self.play(FadeOut(formula),run_time=.10);self.remove(formula)
   target=diagram(s['mode'],i)
   if target.width>6.3:target.scale(6.3/target.width,about_point=target.get_center())
   if target.height>3.3:target.scale(3.3/target.height,about_point=target.get_center())
   target.move_to([-3.05,-.35,0])
   if obj is None:self.play(FadeIn(target),run_time=.35);obj=target
   elif s['mode'] in ['transform-uv-overview','practice']:
    # Different kinds of objects should not morph thousands of unrelated
    # texture/text paths. Keep the spatial construction visible and distinct.
    self.play(FadeOut(obj),run_time=.18);self.remove(obj)
    self.play(FadeIn(target,shift=.08*UP),run_time=.35);obj=target
   else:self.play(Transform(obj,target),run_time=.65)
   formula=fit(txt(beat,26,BLUE),5.9).move_to([3.3,-.28,0]);self.play(FadeIn(formula),run_time=.2)
   if stage_label is not None:self.remove(stage_label)
   stage_label=fit(txt(f'{i+1}/{len(s["beats"])}  '+('같은 판 / UV와 조회 규칙 비교' if s['mode'] in ['uv-mapping','repeat-order','addressing'] else '원래 예제 / 게임 내부 구현 추정 아님'),21,MUTED),12.2).move_to([0,-2.45,0]);self.add(stage_label)
  remaining=slot['seconds']-self.renderer.time
  if remaining>1/60:self.wait(remaining,frozen_frame=True)

def make_scenes(slug,module):
 data=json.loads((ROOT/f'production/batches/game-math-part2-full-series/lessons/{slug}.json').read_text(encoding='utf8'))
 return {'Scene'+s['id']:type('Scene'+s['id'],(NormalTransformUvScene,),{'slug':slug,'sid':s['id'],'__module__':module}) for s in data['scenes'] if s['kind']=='explanation'}
