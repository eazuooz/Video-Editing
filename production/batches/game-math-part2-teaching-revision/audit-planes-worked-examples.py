"""Compute prerequisite examples before voice; no publication or listening approval."""
from pathlib import Path
import json,hashlib,math
import numpy as np
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
read=lambda p:json.loads(p.read_text(encoding='utf8'))
base=read(B/'baselines/game-math-planes-barycentric/lesson.json');draft=read(B/'planes-flow-draft.json');checks=[]
def check(name,observed,expected):
 a=np.asarray(observed,dtype=float);z=np.asarray(expected,dtype=float);assert np.allclose(a,z,atol=1e-10,rtol=1e-10),name
 checks.append({'name':name,'observed':a.tolist(),'expected':z.tolist(),'passed':True})
n=np.array([0.,2.,0.]);d=4.;p=np.array([4.,5.,-3.]);res=n@p-d;norm=np.linalg.norm(n)
check('same-floor residual and distance',[res,norm,res/norm],[6,2,3]);check('nearest point preserves x/z',p-res/norm*n/norm,[4,2,-3])
for scale in [.5,1,3]:check('normalize n and d together scale'+str(scale),(scale*n@(p)-scale*d)/np.linalg.norm(scale*n),3)
A=np.array([0.,0.,0.]);Bb=np.array([6.,0.,0.]);C=np.array([0.,4.,0.]);cross=np.cross(Bb-A,C-A)
check('six-by-four cross',cross,[0,0,24]);area=np.linalg.norm(cross)/2;check('six-by-four triangle area',area,12);check('cross order reversed',np.cross(C-A,Bb-A),[0,0,-24])
check('separate four-by-three area',4*3/2,6);check('three-four-five Heron',math.sqrt(6*(6-3)*(6-4)*(6-5)),6)
weights=np.array([.2,.3,.5]);q=weights@np.array([A,Bb,C]);check('weighted address sums to one',weights.sum(),1);check('same weighted point',q,[1.8,2,0])
normal=cross/np.linalg.norm(cross)
signed=lambda v,w:np.dot(np.cross(v,w),normal)/2
sub=np.array([signed(Bb-q,C-q),signed(C-q,A-q),signed(A-q,Bb-q)])
check('opposite-vertex subareas',sub,[2.4,3.6,6]);check('point-to-address recovers weights',sub/area,weights)
outside_weights=np.array([-.2,.7,.5]);outside=outside_weights@np.array([A,Bb,C]);check('outside same-plane point',outside,[4.2,2,0]);check('outside signed first subarea',signed(Bb-outside,C-outside)/area,-.2)
off=q+np.array([0.,0.,7.]);check('same projected address',off[:2],q[:2]);check('separate plane distance',normal@(off-A),7)
check('linear RGB attributes',weights@np.eye(3),[.2,.3,.5])
# Newell on an ordered square and its reverse; never random unordered point fitting.
square=np.array([[0.,0.,0.],[6.,0.,0.],[6.,4.,0.],[0.,4.,0.]])
newell=lambda vertices:sum((np.array([(a[1]-z[1])*(a[2]+z[2]),(a[2]-z[2])*(a[0]+z[0]),(a[0]-z[0])*(a[1]+z[1])]) for a,z in zip(vertices,np.roll(vertices,-1,axis=0))),np.zeros(3))
check('ordered closed-boundary Newell',newell(square),[0,0,48]);check('reversed ordered Newell',newell(square[::-1]),[0,0,-48])
record={'status':'worked prerequisite numbers reviewed before synthesis; footage and final scripts still pending','baselineOriginalCount':len(base['scenes']),'baselineOriginalSceneSha256':{s['id']:hashlib.sha256(json.dumps(s,ensure_ascii=False,sort_keys=True).encode()).hexdigest() for s in base['scenes']},'originalContract':base['contract'],'checks':checks,'analogyLimits':['shadow compares projected position only, not lighting','screen observations do not measure game-world planes or hidden triangles','barycentric proportions are dimensionless and not necessarily physical masses'],'announcedChanges':['y=2 floor to xy triangle with perpendicular z','6x4 area12 to separate4x3 area6, then return6x4','construct point from weights then invert point to weights'],'humanListeningComplete':False,'finalPixelApproval':False}
(B/'planes-worked-example-review.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'passingNumericChecks':len(checks),'originalSceneCount':len(base['scenes'])}))
