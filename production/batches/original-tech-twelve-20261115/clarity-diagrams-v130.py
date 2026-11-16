"""Source-coupled surface examples: real projected geometry and face lighting."""
from pathlib import Path
import importlib.util,math
import numpy as np
H=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('retained_clarity_diagrams130',H/'clarity-diagrams-v88.py');old=importlib.util.module_from_spec(s);s.loader.exec_module(old)
base,lines,arrow,C=old.base,old.lines,old.arrow,old.C
def mesh(section,phases,center,height=430):
 rings=[]
 for i,a in enumerate(phases):
  y=-height/2+height*i/(len(phases)-1);bend=17*math.sin(i/(len(phases)-1)*math.pi)
  rings.append([np.array([x*math.cos(a)+z*math.sin(a)+bend,y,-x*math.sin(a)+z*math.cos(a)])for x,z in section])
 light=np.array([-.5,-.35,1.]);light/=np.linalg.norm(light);faces=[];count=len(section)
 for i in range(len(rings)-1):
  for k in range(count):
   vs=[rings[i][k],rings[i][(k+1)%count],rings[i+1][(k+1)%count],rings[i+1][k]];n=np.cross(vs[3]-vs[0],vs[1]-vs[0]);n/=max(float(np.linalg.norm(n)),1e-12)
   if n[2]<=0:continue
   shade=.22+.78*max(0,float(n@light));faces.append(dict(z=float(np.mean([v[2]for v in vs])),points=[(center[0]+float(v[0]),center[1]+float(v[1]))for v in vs],normal=n.tolist(),shade=shade,stripe=k==2))
 return rings,sorted(faces,key=lambda x:x['z'])
def draw_mesh(d,faces,color):
 for f in faces:
  rgb=(238,166,77)if f['stripe']else color;fill=tuple(round(x*f['shade'])for x in rgb);d.polygon(f['points'],fill=fill)
def ribbon(t):
 im,d=base('옆으로 돌리면 두께 차이가 보입니다','Ribbon / Cylinder (납작한 띠와 원통) · 해설 모형')
 a=math.pi/2*min(1,max(0,t)/1.4);flat=[(-96,-2),(96,-2),(96,2),(-96,2)];circle=[(96*math.cos(k*math.tau/48),96*math.sin(k*math.tau/48))for k in range(48)];e=[]
 for x,section,color,label in [(260,flat,(190,151,84),'납작한 띠'),(720,circle,(95,196,197),'둥근 원통')]:
  rings,faces=mesh(section,[a]*18,(x,540));draw_mesh(d,faces,color);width=max(v[0]for v in rings[0])-min(v[0]for v in rings[0]);e.append(dict(kind=label,projectedCrossSectionWidth=float(width),phaseRadians=a,faces=faces))
  lines(d,label,(x,235),43,'title');lines(d,'얇은 옆면만 남음'if x==260 and a>1.3 else'방향을 돌리는 중'if x==260 else'둥근 두께가 남음',(x,830),32,'relation')
 lines(d,'같은 중심 곡선 · 단면 모양만 다름',(492,915),30,'muted')
 return im,dict(kind='authored orthographic rotating flat ribbon and cylindrical mesh',phaseRadians=a,geometryAndLightingShareFaceNormals=True,sections=e,originalEngine=False)
def orientation(t):
 im,d=base('표면 방향과 빛의 변화를 함께 봅니다','Surface orientation (표면 방향) · 해설 모형')
 section=[(91*math.cos(k*math.tau/12),91*math.sin(k*math.tau/12))for k in range(12)];e=[]
 for panel,x in enumerate([260,720]):
  phases=[(.27*math.sin(t*.6)+(.16 if math.sin(i*.9+t*1.5)>0 else-.16))if panel==0 else .27*math.sin(t*.6)+.12*math.sin(i*.25+t*.3)for i in range(21)]
  rings,faces=mesh(section,phases,(x,555),440);draw_mesh(d,faces,(96,190,191));e.append(dict(panel=panel,phases=phases,faces=faces))
  lines(d,'방향이 갑자기 달라짐'if panel==0 else'방향을 이어 다듬음',(x,235),34,'title')
  lines(d,'줄무늬·밝기가 들쑥날쑥'if panel==0 else'줄무늬·밝기가 부드럽게',(x,835),30,'relation')
 lines(d,'같은 빛 · 주황 면은 같은 줄무늬',(492,925),31,'muted')
 return im,dict(kind='authored faceted tube orientation comparison',geometryAndLightingShareFaceNormals=True,sameFixedLight=[-.5,-.35,1.],panels=e,notOriginalTransportOrFilterImplementation=True)
DIAGRAMS=dict(old.DIAGRAMS,**{'returnal-ribbon-easy':ribbon,'returnal-orientation-easy':orientation})
def render(key,t):return DIAGRAMS[key](t)
