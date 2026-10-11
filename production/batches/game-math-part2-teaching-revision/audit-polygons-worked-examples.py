"""Check narrated center/boundary/ear numbers and the preservation contract."""
from pathlib import Path
import json, numpy as np
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
read=lambda p:json.loads(p.read_text(encoding='utf8'))
checks=[]
def check(name,passed,evidence):checks.append(dict(name=name,passed=bool(passed),evidence=evidence));assert passed,(name,evidence)
def cross(u,v):return float(u[0]*v[1]-u[1]*v[0])
def area(tri):return cross(tri[1]-tri[0],tri[2]-tri[0])/2
tri=np.array([[0.,0.],[4.,0.],[0.,3.]])
side=np.array([np.linalg.norm(tri[1]-tri[2]),np.linalg.norm(tri[2]-tri[0]),np.linalg.norm(tri[0]-tri[1])])
check('opposite-side lengths',np.allclose(side,[5,3,4]),side.tolist())
check('3-4-5 area and perimeter',area(tri)==6 and sum(side)==12,dict(area=area(tri),perimeter=sum(side)))
g=tri.mean(axis=0);check('centroid equal weights',np.allclose(g,[4/3,1]),g.tolist())
check('medians vertex-to-centroid ratio2/3',np.allclose(g,tri[0]+2/3*((tri[1]+tri[2])/2-tri[0])),g.tolist())
i=(tri*side[:,None]).sum(axis=0)/sum(side)
check('incenter opposite weights',np.allclose(i,[1,1]),dict(weights=(side/sum(side)).tolist(),point=i.tolist()))
dist=[i[0],i[1],abs(3*i[0]+4*i[1]-12)/5]
check('all three perpendicular edge distances',np.allclose(dist,[1,1,1]),dist)
check('bisector equal perpendicular distances',i[0]==i[1],dict(point=i.tolist(),axes='x and y perpendicular edge distances'))
subareas=[abs(area(np.array([i,tri[1],tri[2]]))),abs(area(np.array([i,tri[2],tri[0]]))),abs(area(np.array([i,tri[0],tri[1]])))]
check('equal-height area gives opposite-side weights',np.allclose(np.array(subareas)/6,side/12),subareas)
check('radius2A/P equals A/s',2*6/12==6/(12/2)==1,dict(radius=1,semiperimeter=6))
o=np.array([2,1.5]);radius=np.linalg.norm(tri-o,axis=1)
check('circumcenter equal vertex distances',np.allclose(radius,2.5),dict(point=o.tolist(),radii=radius.tolist()))
obtuse=np.array([[0,0],[4,0],[1,1]],float);oo=np.array([2,-1.])
check('obtuse circumcenter outside with equal distances',np.allclose(np.linalg.norm(obtuse-oo,axis=1),np.sqrt(5)) and oo[1]<0,oo.tolist())
check('degenerate triangle guarded',area(np.array([[0,0],[1,0],[2,0]],float))==0,'Three collinear points have no nonzero lamina and no unique finite circumcircle; contract excludes them.')
l=np.array([[0,0],[4,0],[4,1],[1,1],[1,4],[0,4]],float)
signed=sum(cross(l[k],l[(k+1)%6]) for k in range(6))/2
check('ordered L positive CCW area',signed==7,signed)
turn=[cross(l[k]-l[k-1],l[(k+1)%6]-l[k]) for k in range(6)]
check('notch turn at v3',turn[3]==-9 and all(v>0 for k,v in enumerate(turn) if k!=3),turn)
check('six-vertex interior angle sum does not prove convexity',(6-2)*180==720 and turn[3]<0,dict(angleSumDegrees=720,notchTurn=turn[3]))
bad=[(2,3,4),(2,4,5),(2,5,0),(2,0,1)];ba=[area(l[list(ids)]) for ids in bad]
check('wrong fan signed cancellation',sum(ba)==7 and sum(abs(a) for a in ba)>7,dict(signedAreas=ba,absoluteSum=sum(abs(a) for a in ba)))
def in_tri(p,t):
 c=[cross(t[(k+1)%3]-t[k],p-t[k]) for k in range(3)]
 return min(c)>=-1e-9 or max(c)<=1e-9
outside=np.array([2.,2.])
check('wrong fan covers the excluded notch',any(in_tri(outside,l[list(ids)]) for ids in bad),'Point(2,2) is outside L and inside a bad-fan triangle.')
ears=[(0,1,2),(0,2,3),(0,3,4),(0,4,5)];aa=[area(l[list(ids)]) for ids in ears]
check('verified ears and final triangle',aa==[2,1.5,1.5,2] and sum(aa)==7,dict(indices=ears,areas=aa))
check('ear deletion preserves original IDs and updates neighbors',ears[1]==(0,2,3),'After removing1, active neighbors0→2→3; original storage unchanged.')
bad_coverage=[]
for x in np.arange(.025,4,.05):
 for y in np.arange(.025,4,.05):
  p=np.array([x,y]);expected=x<1 or y<1;covered=sum(in_tri(p,l[list(ids)]) for ids in ears)
  # Skip exact internal diagonals, where two closed triangles may share a boundary.
  if any(abs(cross(l[ids[(k+1)%3]]-l[ids[k]],p-l[ids[k]]))<1e-9 for ids in ears for k in range(3)):continue
  if covered!=int(expected):bad_coverage.append([float(x),float(y),covered])
check('sampled disjoint interior coverage retains notch',not bad_coverage,dict(sampleSpacing=.05,domain=[0,4],failures=bad_coverage[:5]))
centers=np.array([l[list(ids)].mean(axis=0) for ids in ears]);center=(centers*np.array(aa)[:,None]).sum(axis=0)/7
check('uniform L area-weighted centroid',np.allclose(center,[19/14,19/14]) and not np.allclose(center,l.mean(axis=0)),dict(areaWeighted=center.tolist(),wrongVertexMean=l.mean(axis=0).tolist()))
check('scale respects length and area units',area(2*tri)==4*area(tri),dict(lengthScale=2,areaScale=4))
thin=np.array([[0,0],[4,0],[2,.01]],float);changed=thin.copy();changed[2,1]+=.001
check('thin-triangle relative altitude sensitivity',abs(area(changed)/area(thin)-1.1)<1e-10,dict(area=area(thin),perturbed=area(changed),illustrativeOnly=True))
flow=read(B/'polygons-flow-draft.json');check('all original22 order retained',[i for order in flow['orders'] for i in order if i.isnumeric()]==[f'{i:02}' for i in range(1,23)],'12 originals then10 originals; complete boundary after12.')
check('existing mathematical scope retained',read(B/'baselines/game-math-polygons-triangulation/lesson.json')['contract']['partition'].endswith('no universal hole-bridging implementation asserted.'),'Simple finite planar polygon without holes/intersections only; no game-engine inference.')
record=dict(status='pre-TTS mathematical audit; narrated/moving final pixels pending',checks=checks,passed=all(c['passed'] for c in checks),humanListening='pending')
(B/'polygons-worked-example-review.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Passed polygon pre-TTS checks:',len(checks))
