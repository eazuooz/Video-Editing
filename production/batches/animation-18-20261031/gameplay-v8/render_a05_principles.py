"""A05-only spatial/outline clarification, retaining the approved soundtrack."""
from common import *
import visuals as v, render, qa, math, sys
from PIL import Image,ImageDraw

original_draw=v.draw
original_graph=v.graph_panel

def spatial_board(im,u):
 d=ImageDraw.Draw(im);d.rectangle((1015,210,1880,895),fill=v.BG)
 v.text(d,(1045,216),'직접 구성한 공간 도식 · 같은 팔과 상대',28,v.MUTED,790)
 v.text(d,(1045,268),'옆에서는 겹쳐 보여도',35,v.YELLOW,790)
 floor=515;shoulder=(1170,405);hand=(1720,405)
 d.line((1080,floor,1830,floor),fill=v.LINE,width=3)
 d.ellipse((1138,327,1186,375),outline=v.WHITE,width=6)
 d.line((1162,376,1162,455),fill=v.WHITE,width=12)
 d.line((1162,455,1125,floor),fill=v.WHITE,width=10);d.line((1162,455,1200,floor),fill=v.WHITE,width=10)
 v.arrow(d,shoulder,hand,v.TEAL,10)
 v.text(d,(1390,350),'공격 경로',28,v.TEAL,430)
 d.ellipse((1680,365,1760,445),outline=v.RED,width=7)
 v.text(d,(1390,468),'손끝과 상대가 겹침',28,v.WHITE,430)
 v.text(d,(1045,535),'위에서 보면 깊이가 드러납니다',34,v.YELLOW,790)
 y=705;z=.6*(1-u);end=(1720,y-150*z)
 d.line((1080,y,1830,y),fill=v.LINE,width=3)
 for x in range(1080,1820,35):d.line((x,y,x+18,y),fill=v.YELLOW,width=4)
 d.ellipse((1100,y-25,1150,y+25),outline=v.TEAL,width=7)
 d.ellipse((1680,y-40,1760,y+40),outline=v.RED if z>.15 else v.GREEN,width=7)
 v.arrow(d,(1150,y),end,v.TEAL,9)
 if z>.15:v.arrow(d,end,(1720,y),v.RED,5)
 v.text(d,(1060,772),'기준 평면을 위에서 본 선',28,v.YELLOW,780)
 v.text(d,(1060,823),'깊이가 어긋남' if z>.15 else '같은 깊이로 맞춤',32,v.RED if z>.15 else v.GREEN,780)

def camera_board(im):
 d=ImageDraw.Draw(im);d.rectangle((1015,210,1880,895),fill=v.BG)
 v.text(d,(1045,216),'Perspective Projection (원근 투영)',31,v.YELLOW,790)
 v.text(d,(1045,264),'같은 설명용 자세 · 보는 방향만 변경',30,v.MUTED,790)
 for index,(cx,a) in enumerate([(1235,0),(1660,math.radians(55))]):
  v.text(d,(cx,327),'정면' if not index else '비스듬히',34,v.TEAL if not index else v.RED,370,anchor='mm')
  def project(p):
   x,y,z=p;xx=x*math.cos(a)+z*math.sin(a);zz=-x*math.sin(a)+z*math.cos(a)
   scale=500/(3-zz);return (cx+scale*xx,765-scale*y),zz
  def point(p):return project(p)[0]
  segments=[((.23,1.35,0),(.23,1.08,-.5),v.TEAL,17),((.23,1.08,-.5),(.23,1.08,-.95),v.TEAL,17),
   ((-.22,1.35,0),(-.42,1.14,.2),v.WHITE,16),((-.42,1.14,.2),(-.45,1.32,.5),v.WHITE,16),
   ((-.14,.8,0),(-.25,.38,.08),v.WHITE,17),((-.25,.38,.08),(-.28,0,.1),v.WHITE,17),
   ((.14,.8,0),(.32,.38,-.12),v.WHITE,17),((.32,.38,-.12),(.43,0,-.2),v.WHITE,17)]
  primitives=[(sum(project(p)[1] for p in [p1,p2])/2,'line',(p1,p2,c,w)) for p1,p2,c,w in segments]
  primitives.append((0,'body',None))
  for _,kind,data in sorted(primitives,key=lambda t:t[0]):
   if kind=='body':
    body=[point(p) for p in [(-.25,1.39,0),(.25,1.39,0),(.16,.8,0),(-.16,.8,0)]];d.polygon(body,fill=v.WHITE)
    q=point((0,1.66,0));r=25;d.ellipse((q[0]-r,q[1]-r,q[0]+r,q[1]+r),fill=v.WHITE)
   else:
    p1,p2,c,w=data;aa,bb=point(p1),point(p2);d.line((aa,bb),fill=c,width=w)
    for q in [aa,bb]:d.ellipse((q[0]-w/2,q[1]-w/2,q[0]+w/2,q[1]+w/2),fill=c)
  v.text(d,(cx,814),'몸통 뒤에 겹친 팔' if not index else '바깥으로 드러나는 팔',27,v.TEAL if not index else v.RED,380,anchor='mm')

# Hand-traced, simplified outer boundary of the inspected19.5s frozen pose.
# This is an explicitly authored diagram, never a claimed CV mask or game rig.
BODY=[(342,518),(345,505),(368,497),(368,478),(386,468),(413,463),(440,485),(465,487),(476,491),(464,506),(488,516),(496,520),(473,531),(446,539),(443,565),(453,568),(495,552),(510,539),(514,526),(526,522),(532,510),(544,500),(563,500),(574,510),(569,524),(555,531),(542,540),(529,540),(516,551),(493,577),(475,591),(478,610),(496,603),(508,609),(506,622),(498,631),(480,633),(470,650),(459,678),(447,702),(453,710),(461,718),(463,734),(459,750),(469,764),(463,775),(447,777),(441,769),(436,752),(431,735),(423,727),(421,712),(431,698),(429,675),(427,651),(420,634),(401,624),(390,616),(383,604),(384,596),(374,592),(365,585),(366,575),(376,565),(386,562),(391,558),(384,552),(372,553),(351,547),(341,535)]
PLUME=[(440,507),(438,490),(444,466),(449,453),(445,445),(436,446),(430,451),(425,448),(424,433),(433,419),(451,415),(469,423),(477,437),(479,448),(478,462),(473,476),(466,487),(457,497),(453,508)]

def outline_board(im):
 d=ImageDraw.Draw(im);d.rectangle((45,177,1885,895),fill=v.BG)
 v.text(d,(65,184),'고정한 실제 공격 자세',36,v.TEAL,880)
 v.text(d,(1030,184),'Silhouette (실루엣)',36,v.RED,830)
 pic=v.detail('peach',120).crop((300,320,800,810));v.fit(im,pic,(65,245,850,545))
 art=Image.new('RGB',(1000,980),v.BG);dd=ImageDraw.Draw(art)
 def coords(points):return [((x-300)*2,(y-320)*2) for x,y in points]
 dd.polygon(coords(BODY),fill=v.WHITE);dd.polygon(coords(PLUME),fill=v.WHITE)
 dd.polygon(coords([(442,558),(490,562),(543,575),(573,604),(521,589),(473,591)]),fill=v.WHITE)
 dd.line(coords([(552,509),(755,360)]),fill=v.WHITE,width=7)
 v.fit(im,art,(1030,245,820,545))
 v.text(d,(1030,815),'실제 자세의 바깥 윤곽을 단순화한 도식',28,v.MUTED,820)

def graph(im,kind,u,key,full=False):
 if not full and key in ['plane','top']:return spatial_board(im,u)
 if not full and key=='camera':return camera_board(im)
 return original_graph(im,kind,u,key,full)
v.graph_panel=graph

def clarified_draw(ep,row,span,local_frame,absolute_frame):
 cues=row['bodyNarrationCues'];seconds=absolute_frame/60
 if ep=='A05' and span['key'] in ['outline','camera']:
  if cues[56]['start']<=seconds<cues[57]['start']:
   ss=dict(span,mode='native');ss.pop('nativeLeadCompleted',None);ss.pop('nativeLeadFrame',None)
   return original_draw(ep,row,ss,local_frame%192,absolute_frame)
  if cues[52]['start']<=seconds<cues[56]['start']:
   im=v.backdrop(ep,span['key'],row['title'],'peach','pose').copy();outline_board(im);return im
  if cues[47]['start']<=seconds<cues[52]['start']:
   ss=dict(span,key='camera',nativeLeadCompleted=True);ss.pop('nativeLeadFrame',None)
   return original_draw(ep,row,ss,local_frame,absolute_frame)
 return original_draw(ep,row,span,local_frame,absolute_frame)
v.draw=clarified_draw;render.draw=clarified_draw

base_points=qa.points

def points(e,audio):
 rows=base_points(e,audio);index={r['frame']:r for r in rows}
 for t,role in [(131,'study:side-top-depth'),(209,'study:camera-projection'),(231,'study:silhouette-outline')]:
  n=map_frame(round(t*60),audio['changes']);index.setdefault(n,dict(frame=n,roles=[]))['roles'].append(role)
 return [index[n] for n in sorted(index)]
qa.points=points

def main(preview=False):
 plan=read(HERE/'plan.json');e=next(e for e in plan['episodes'] if e['id']=='A05')
 for key in ['plane','top','camera','outline']:e['studyDefinitions'][key].update(rendererAdapter=str(Path(__file__)),rendererAdapterSha256=sha(__file__))
 e['queuedVisualEnhancement']=dict(stage='previewed-pending-encode',reason='Show the actual narrated side/top depth mismatch, same-pose camera occlusion and visible silhouette, rather than a generic pair of circles.',outlineSourceFrame=120,outlineSourceLocalSeconds=19.5,outlineSourceBank='peach',outlineKind='hand-traced simplified diagram, not segmentation output')
 save(HERE/'plan.json',plan)
 if preview:
  e=dict(e,renderNarrationCues=srt(WORK/'A05/ko.srt'))
  for name,t in [('space',131),('camera',209),('outline',231)]:
   old=round(t*60);s=next(s for s in e['replacementSpans'] if s['start']<=old<s['end']);new=map_frame(old,read(WORK/'A05/audio.json')['changes'])
   im=clarified_draw('A05',e,dict(s,newFrame=new,nativeLeadCompleted=True),100,old)
   im.save(WORK/'A05'/('clarified-'+name+'.png'));im.resize((375,211)).save(WORK/'A05'/('clarified-'+name+'-mobile.png'))
  return
 render.render_episode(e)
 plan=read(HERE/'plan.json');next(e for e in plan['episodes'] if e['id']=='A05')['queuedVisualEnhancement']['stage']='encoded-awaiting-internal-review';save(HERE/'plan.json',plan)
if __name__=='__main__':main('--preview' in sys.argv)
