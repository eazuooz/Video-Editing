"""Check the stated Euler order, singular boundaries, units and composition."""
from pathlib import Path
import math,json,numpy as np
from euler import euler,rx,ry,rz,axis_rotation,P
root=Path(__file__).resolve().parents[3];slug='game-math-euler-axis-angle'
def wrap(a):
 w=math.remainder(a,2*math.pi)
 return w+2*math.pi if w<=-math.pi else w
d=math.pi/180
assert np.allclose(ry(math.pi/2)@rx(math.pi/2)@np.array([0,0,1]),[0,-1,0])
assert np.allclose(rx(math.pi/2)@ry(math.pi/2)@np.array([0,0,1]),[1,0,0])
assert np.allclose(euler(0,135*d,0),euler(math.pi,45*d,math.pi))
assert np.allclose(euler(30*d,math.pi/2,10*d),euler(20*d,math.pi/2,0))
assert np.isclose(wrap(340*d),-20*d) and np.isclose(wrap(-340*d),20*d)
assert np.isclose(wrap(-math.pi),math.pi)
assert np.allclose(axis_rotation([0,1,0],math.pi/2)@[0,0,1],[1,0,0])
assert np.allclose(axis_rotation([0,1,0],math.pi/2),axis_rotation([0,-1,0],3*math.pi/2))
assert not np.allclose(ry(math.pi/2)@rx(math.pi/2),axis_rotation([1,1,0],math.pi/math.sqrt(2)))
rng=np.random.default_rng(20261005);maxerr=0
for _ in range(1000):
 h,p,b=rng.uniform(-math.pi,math.pi,3);R=euler(h,p,b)
 assert np.allclose(R.T@R,np.eye(3)) and np.isclose(np.linalg.det(R),1)
 # Fixed Z then X then Y and moving-body Y then X then Z coincide.
 current=np.eye(3)
 for rot,a in [(ry,h),(rx,p),(rz,b)]:current=current@rot(a)
 fixed=np.eye(3)
 for rot,a in [(rz,b),(rx,p),(ry,h)]:fixed=rot(a)@fixed
 assert np.allclose(current,fixed) and np.allclose(R,fixed)
 assert np.allclose(euler(h,math.pi/2,b),euler(h-b,math.pi/2,0))
 assert np.allclose(euler(h,-math.pi/2,b),euler(h+b,-math.pi/2,0))
 a=rng.uniform(-1000,1000);w=wrap(a)
 assert -math.pi<w<=math.pi and np.isclose(np.sin(w),np.sin(a)) and np.isclose(np.cos(w),np.cos(a))
 maxerr=max(maxerr,float(np.max(np.abs(R.T@R-np.eye(3)))))
assert np.allclose(P.T@P,np.eye(3)) and np.isclose(np.linalg.det(P),1)
report={'slug':slug,'passed':True,'randomCases':1000,'maximumOrthonormalError':maxerr,'checks':['declared right-handed/column order','intrinsic Y-X-Z equals extrinsic Z-X-Y','fixed90degree order counterexample','135degree Euler alias','positive and negative gimbal identities','wrap signs and (-pi,pi] endpoints','axis-angle plus90 versus minus270 alias','finite rotation-vector nonadditivity','proper drawing basis det+1'],'humanListening':'pending','pixelReview':'separate'}
p=root/f'projects/{slug}/production/math-verification.json';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(report,indent=2)+'\n',encoding='utf8');print(json.dumps(report))
