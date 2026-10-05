"""Independent matrix and Rodrigues checks, including singular boundaries."""
from pathlib import Path
import importlib.util,math,json,hashlib,datetime
import numpy as np
B=Path(__file__).parent;R=B.parents[2]
spec=importlib.util.spec_from_file_location('conv',B/'rotation-conversions.py');c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
rng=np.random.default_rng(81005);errors=[]
def axmat(n,a):
 n=np.asarray(n,dtype=float);n/=np.linalg.norm(n);x,y,z=n
 K=np.array([[0,-z,y],[z,0,-x],[-y,x,0]])
 return np.eye(3)*math.cos(a)+(1-math.cos(a))*np.outer(n,n)+math.sin(a)*K
def eu(h,p,b):return axmat([0,1,0],h)@axmat([1,0,0],p)@axmat([0,0,1],b)
for _ in range(1000):
 n=rng.normal(size=3);a=rng.uniform(-math.pi,math.pi);q=c.axis_quaternion(n,a);M=axmat(n,a)
 errors.extend([np.max(abs(c.to_matrix(q)-M)),np.max(abs(c.to_matrix(c.from_matrix(M))-M))])
 h,p,b=rng.uniform(-math.pi,math.pi,3);M=eu(h,p,b)
 errors.extend([np.max(abs(c.to_matrix(c.euler_quaternion(h,p,b))-M)),np.max(abs(eu(*c.matrix_euler(M))-M))])
 axis,angle=c.quaternion_axis(q);errors.append(np.max(abs(axmat(axis,angle)-c.to_matrix(q))))
 qa=c.unit(rng.normal(size=4));qb=c.unit(rng.normal(size=4));d=abs(qa@qb);alpha=math.acos(np.clip(d,0,1))
 for t in [0,.25,.5,.75,1]:
  qi=c.interpolate(qa,qb,t);distance=2*math.acos(np.clip(abs(qa@qi),0,1))
  if alpha>.04:errors.append(abs(distance-2*alpha*t))
  assert abs(qi@qi-1)<1e-12
  assert np.allclose(c.to_matrix(c.interpolate(qa,-qb,t)),c.to_matrix(qi),atol=1e-12)
for p in [math.pi/2,-math.pi/2]:
 for h,b in [(math.radians(30),math.radians(10)),(.7,-1.2),(-2.4,2.8)]:
  M=eu(h,p,b);out=c.matrix_euler(M);assert out[2]==0
  assert np.allclose(eu(*out),M,atol=1e-12)
for n in [[1,0,0],[0,1,0],[0,0,1],[1,2,3]]:
 M=axmat(n,math.pi);assert np.allclose(c.to_matrix(c.from_matrix(M)),M,atol=1e-12)
for bad in [np.diag([-1,1,1]),np.diag([2,1,1]),np.zeros((3,3)),np.array([[1,.1,0],[0,1,0],[0,0,1]])]:
 try:c.from_matrix(bad);raise AssertionError('Invalid rotation accepted')
 except ValueError:pass
for bad in [[0,0,0,0],[float('nan'),0,0,1]]:
 try:c.unit(bad);raise AssertionError('Invalid q accepted')
 except ValueError:pass
I=np.array([1.,0,0,0]);qb=c.axis_quaternion([0,0,1],math.pi/2)
for t,degrees in [(.25,22.5),(.5,45),(.75,67.5)]:assert np.allclose(c.to_matrix(c.interpolate(I,qb,t)),axmat([0,0,1],math.radians(degrees)),atol=1e-12)
# Matrix component LERP collapses x/y at a half-turn, independently of quaternions.
assert np.allclose((np.eye(3)+axmat([0,0,1],math.pi))/2,np.diag([0,0,1]),atol=1e-12)
assert np.allclose(c.interpolate(I,-I,.5),I)
assert max(errors)<2e-7,max(errors)
result={'passed':True,'randomCases':1000,'maximumError':max(errors),'contract':'RH column local-to-world Hamilton wxyz; Euler RyRxRz',
 'checks':['Rodrigues axis-angle','quaternion-matrix round trip including180-degree dominant-component branches','Euler composition and canonical round trip','both positive and negative gimbal choices bank zero','q sign invariance and shortest SLERP','unit input normalization and invalid zero/nonfinite guards','invalid scale/reflection/shear matrices rejected','SLERP22.5/45/67.5 degree samples','matrix lerp collapse','antipodal identical-orientation repair'],
 'referenceSha256':hashlib.sha256((B/'rotation-conversions.py').read_bytes()).hexdigest(),'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'humanListening':'pending'}
out=R/'shared/output/game-math-rotation-interpolation';out.mkdir(parents=True,exist_ok=True)
(out/'math-reference-verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8');print(json.dumps(result))
