"""Numerical boundary and randomized invariants for the actual lesson claims."""
from pathlib import Path
import json,numpy as np
root=Path(__file__).resolve().parents[3];slug='game-math-orientation-matrices'
P=np.array([[1,0,0],[0,0,-1],[0,1,0.]])
assert np.allclose(P.T@P,np.eye(3)) and np.isclose(np.linalg.det(P),1)
R=np.array([[0,-1,0],[1,0,0],[0,0,1.]])
assert np.allclose(R@[2,1,0],[-1,2,0])
assert np.allclose(R.T@[-1,2,0],[2,1,0])
assert np.allclose(R.T@(np.array([4,5,0])-np.array([3,3,0])),[2,-1,0])
assert np.allclose(R@[2,-1,0]+np.array([3,3,0]),[4,5,0])
assert np.allclose((np.eye(3)+np.diag([-1,-1,1]))*.5,np.diag([0,0,1]))
assert np.isclose(np.linalg.det(np.diag([-1,1,1])),-1)
assert np.isclose(np.linalg.det(np.diag([-1,-1,1])),1)
assert np.allclose(np.diag([-1,1,1]).T@np.diag([-1,1,1]),np.eye(3))
rng=np.random.default_rng(20261005);maxerr=0
for _ in range(1000):
 a=rng.normal(size=(3,3));q,_=np.linalg.qr(a)
 if np.linalg.det(q)<0:q[:,2]*=-1
 v=rng.normal(size=3);w=q@v
 assert np.allclose(q.T@w,v)
 assert np.isclose(np.linalg.norm(w),np.linalg.norm(v))
 # Columns contain local axes expressed in world; common-frame dot product.
 for i in range(3):
  for j in range(3):assert np.isclose(q[i,j],np.eye(3)[:,i]@q[:,j])
 maxerr=max(maxerr,float(np.max(np.abs(q.T@q-np.eye(3)))))
report={'slug':slug,'passed':True,'randomRotationCases':1000,'maximumOrthonormalError':maxerr,'checks':['proper y-up to z-up drawing map det+1','90degree weighted-axis calculation','pure-rotation transpose inverse','point translation-before-inverse','corrected common-frame DCM','reflection vs proper half-turn','matrix midpoint collapse','1000random length-preserving roundtrips'],'method':'Tests verify numerical claims; human listening and pixel QA are separate'}
out=root/f'projects/{slug}/production/math-verification.json';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf8');print(json.dumps(report))
