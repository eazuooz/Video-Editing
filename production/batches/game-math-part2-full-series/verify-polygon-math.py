"""Independent calculation and coverage checks for the current polygon lecture.

Render and narration approval remain separate from these numeric checks.
"""
from pathlib import Path
import datetime,hashlib,json,math
import numpy as np
R=Path(__file__).resolve().parents[3];slug='game-math-polygons-triangulation'
P=R/f'projects/{slug}/production';checks=[]
def close(a,b):assert np.allclose(a,b,rtol=1e-10,atol=1e-10),(a,b)
def cross(a,b):return float(a[0]*b[1]-a[1]*b[0])
def area(v):return sum(cross(v[i],v[(i+1)%len(v)]) for i in range(len(v)))/2
def save(name,evidence):checks.append({'name':name,'passed':True,'evidence':evidence})
tri=np.array([[0.,0.],[4.,0.],[0.,3.]])
G=tri.mean(0);sides=np.array([np.linalg.norm(tri[1]-tri[2]),np.linalg.norm(tri[2]-tri[0]),np.linalg.norm(tri[0]-tri[1])]);I=sides@tri/sides.sum()
O=np.linalg.solve(2*(tri[1:]-tri[0]),(tri[1:]**2).sum(1)-(tri[0]**2).sum())
close(G,[4/3,1]);close(sides,[5,3,4]);close(I,[1,1]);close(O,[2,1.5]);close(np.linalg.norm(tri-O,axis=1),[2.5]*3)
close(2*area(tri)/sides.sum(),1);close(abs(3*I[0]+4*I[1]-12)/5,1)
save('right-triangle-three-distinct-centers',{'vertices':tri.tolist(),'centroid':G.tolist(),'oppositeSideWeights':sides.tolist(),'incenter':I.tolist(),'inradius':1,'circumcenter':O.tolist(),'circumradius':2.5,'area':6,'perimeter':12})
obt=np.array([[0.,0.],[4.,0.],[1.,1.]])
obtO=np.linalg.solve(2*(obt[1:]-obt[0]),(obt[1:]**2).sum(1)-(obt[0]**2).sum());close(obtO,[2,-1]);close(np.linalg.norm(obt-obtO,axis=1),[math.sqrt(5)]*3)
save('obtuse-outside-circumcenter',{'vertices':obt.tolist(),'circumcenter':obtO.tolist(),'equalVertexDistance':math.sqrt(5),'outside':bool(obtO[1]<0)})
v=np.array([[0.,0.],[4.,0.],[4.,1.],[1.,1.],[1.,4.],[0.,4.]])
close(area(v),7);turns=[cross(v[(i+1)%6]-v[i],v[(i+2)%6]-v[(i+1)%6]) for i in range(6)];assert min(turns)<0<max(turns)
close((len(v)-2)*180,720)
save('ordered-concave-boundary-turns-and-angle-sum',{'vertices':v.tolist(),'area':7,'successiveTurnCrosses':turns,'interiorAngleSumDegrees':720,'scope':'Finite planar simple boundary validated before a convexity turn test; sum does not prove convexity.'})
fan=[(2,3,4),(2,4,5),(2,5,0),(2,0,1)];fa=[area(v[list(t)]) for t in fan];close(fa,[-4.5,1.5,8,2]);close(sum(fa),7);close(sum(map(abs,fa)),16)
save('bad-concave-fan-signed-cancellation',{'anchor':2,'triangles':fan,'signedAreas':fa,'signedSum':sum(fa),'absoluteSum':sum(map(abs,fa)),'valid':False})
def in_tri(p,t,strict=False):
 a,b,c=v[list(t)];signs=[cross(b-a,p-a),cross(c-b,p-b),cross(a-c,p-c)]
 return min(signs)>1e-10 if strict else min(signs)>=-1e-10
remaining=list(range(6));ears=[];parts=[]
for vertex in [1,2,3]:
 i=remaining.index(vertex);t=(remaining[i-1],vertex,remaining[(i+1)%len(remaining)])
 assert area(v[list(t)])>0;others=[j for j in remaining if j not in t]
 assert not any(in_tri(v[j],t) for j in others)
 parts.append(t);ears.append({'removedVertex':vertex,'triangle':t,'otherRemainingVertices':others,'containsOtherVertex':False});remaining.remove(vertex)
parts.append(tuple(remaining));aa=[area(v[list(t)]) for t in parts];close(aa,[2,1.5,1.5,2]);close(sum(aa),7);assert len(parts)==len(v)-2
save('ear-sequence-and-positive-areas',{'ears':ears,'triangles':parts,'positiveAreas':aa,'sum':sum(aa)})
samples=0
for x in np.linspace(.031,3.973,47):
 for y in np.linspace(.043,3.967,43):
  p=np.array([x,y]);on_edge=any(any(abs(cross(v[t[(j+1)%3]]-v[t[j]],p-v[t[j]]))<1e-10 for j in range(3)) for t in parts)
  if on_edge:continue
  assert sum(in_tri(p,t,strict=True) for t in parts)==int(x<1 or y<1),(x,y)
  samples+=1
save('independent-coverage-with-no-gap-or-overlap',{'nonBoundarySamples':samples,'expectedRegion':'0<x<4,0<y<4 and (x<1 or y<1)','outsideNotchExcluded':True,'algorithmScope':'Specific no-hole simple L; no general hole bridging assertion.'})
files=[f'production/batches/game-math-part2-full-series/lessons/{slug}.json',f'projects/{slug}/script/narration.ko.json',f'projects/{slug}/script/narration.en.json','manim/projects/game-math-part2-full-series/geometry_polygons.py']
record={'status':'passed-independent-current-numeric-checks','checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':checks,'fingerprints':{f:hashlib.sha256((R/f).read_bytes()).hexdigest() for f in files},'finalRenderedPixels':'pending','currentNarrationReview':'pending','humanListening':'pending','passed':False}
dest=P/'math-verification.json';old=P/'math-verification-before-current-20261008.json'
if dest.exists() and not old.exists():old.write_bytes(dest.read_bytes())
dest.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'checks':len(checks),'coverageSamples':samples,'allNumericChecksPassed':True,'finalReview':'pending'}))
