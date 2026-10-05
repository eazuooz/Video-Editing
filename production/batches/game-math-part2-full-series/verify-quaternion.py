"""Check lecture claims against independent Rodrigues/matrix calculations."""
from pathlib import Path
import sys,json,hashlib,datetime
import numpy as np
R=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(R/'manim/projects/game-math-part2-full-series'))
from quaternion import qmul,qaxis,qmatrix,qrotate,qinverse,qconj,qpower,P,rz
rng=np.random.default_rng(20261005);maximum=0
def close(a,b,tol=1e-9):
 global maximum
 error=float(np.max(np.abs(np.asarray(a)-np.asarray(b))));maximum=max(maximum,error)
 assert error<tol,(a,b,error)
def rodrigues(n,a):
 n=n/np.linalg.norm(n);x,y,z=n;K=np.array([[0,-z,y],[z,0,-x],[-y,x,0]])
 return np.eye(3)*np.cos(a)+(1-np.cos(a))*np.outer(n,n)+K*np.sin(a)
for _ in range(1000):
 n=rng.normal(size=3);angle=rng.uniform(-2*np.pi,2*np.pi);a=qaxis(n,angle)
 b=qaxis(rng.normal(size=3),rng.uniform(-2*np.pi,2*np.pi));c=qaxis(rng.normal(size=3),rng.uniform(-2*np.pi,2*np.pi))
 A=qmatrix(a);B=qmatrix(b);v=rng.normal(size=3)
 close(A,rodrigues(n,angle));close(A.T@A,np.eye(3));close(np.linalg.det(A),1)
 close(qrotate(a,v),A@v);close(qmatrix(-a),A);close(qinverse(a),qconj(a))
 close(qmul(qmul(a,b),c),qmul(a,qmul(b,c)));close(qmatrix(qmul(a,b)),A@B)
 scale=rng.uniform(.2,5);close(qrotate(scale*a,v),A@v)
 world=qmul(b,qinverse(a));body=qmul(qinverse(a),b)
 close(qmatrix(qmul(world,a)),B);close(qmatrix(qmul(a,body)),B)
 minimal=2*np.arccos(np.clip(abs(a@b),0,1));matrix_angle=np.arccos(np.clip((np.trace(B@A.T)-1)/2,-1,1))
 close(minimal,matrix_angle,1e-7)
z90=qaxis([0,0,1],np.pi/2);v=np.array([1.,0,1])
close(qmul(z90,z90),[0,0,0,1]);close(qmul(qmul(z90,z90),qmul(z90,z90)),[-1,0,0,0])
close(qinverse([2.,0,0,0]),[.5,0,0,0]);close(qmul([2.,0,0,0],qinverse([2.,0,0,0])),[1,0,0,0])
close(qmul(z90,np.r_[0,v])[0],-np.sqrt(2)/2);close(qrotate(z90,v),[0,1,1]);close(qrotate(qconj(z90),[0,1,1]),v)
close(qmatrix(qpower(z90,.5)),rz(np.pi/4));close(qmatrix(qpower(-z90,.5)),rz(-3*np.pi/4))
x90=qaxis([1,0,0],np.pi/2);y90=qaxis([0,1,0],np.pi/2)
close(qrotate(qmul(y90,x90),[0,0,1]),[0,-1,0]);close(qrotate(qmul(x90,y90),[0,0,1]),[1,0,0])
for bad in ([0,0,0,0],[np.nan,0,0,0],[np.inf,0,0,0]):
 try:qinverse(bad)
 except ValueError:pass
 else:raise AssertionError('Invalid inverse accepted')
try:qpower([-1.,0,0,0],.5)
except ValueError:pass
else:raise AssertionError('Negative identity branch needs an axis')
close(np.linalg.det(P),1)
source=R/'manim/projects/game-math-part2-full-series/quaternion.py'
d={'slug':'game-math-quaternion-operations','passed':True,'randomCases':1000,'maximumNumericalError':maximum,
 'source':source.relative_to(R).as_posix(),'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),
 'reviewedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'checks':['RH column Rodrigues versus quaternion matrix','unit norm and det+1 orthogonality','general inverse norm squared and unit conjugate','q versus -q same orientation','Hamilton composition and associativity','world and body relative deltas','four-component dot physical minimal angle','nonunit quaternion with correct general inverse','90-degree vector example and one-sided scalar leakage','quarter-turn square and negative identity after360degrees','fractional powers depend on sign branch','invalid inverse and negative identity branch guards','proper drawing basis det+1'],
 'humanListening':'pending','pixelReview':'separate'}
(R/'projects/game-math-quaternion-operations/production/math-verification.json').write_text(json.dumps(d,indent=2)+'\n',encoding='utf8')
print(json.dumps(d))
