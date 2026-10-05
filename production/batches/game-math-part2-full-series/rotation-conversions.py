"""Lecture reference calculations, independent of graphics and source conventions.

Right-handed, column vectors, local-to-world, Hamilton wxyz, Euler Ry(h)Rx(p)Rz(b).
This is a mathematical reference for teaching, not a claim about any game's code.
"""
import math
import numpy as np

def unit(q):
 q=np.asarray(q,dtype=float)
 if q.shape!=(4,) or not np.all(np.isfinite(q)):raise ValueError('Four finite components required')
 length=np.linalg.norm(q)
 if not np.isfinite(length) or length<1e-12:raise ValueError('Invalid quaternion norm')
 return q/length

def mul(a,b):
 a=np.asarray(a);b=np.asarray(b)
 return np.r_[a[0]*b[0]-a[1:]@b[1:],a[0]*b[1:]+b[0]*a[1:]+np.cross(a[1:],b[1:])]

def axis_quaternion(n,theta):
 n=np.asarray(n,dtype=float)
 if n.shape!=(3,) or not np.all(np.isfinite(n)) or not math.isfinite(theta):raise ValueError('Finite axis and angle required')
 length=np.linalg.norm(n)
 if not np.isfinite(length) or length<1e-12:raise ValueError('Axis norm must be finite and nonzero')
 return np.r_[math.cos(theta/2),n/length*math.sin(theta/2)]

def to_matrix(q):
 w,x,y,z=unit(q)
 return np.array([[1-2*(y*y+z*z),2*(x*y-w*z),2*(x*z+w*y)],
  [2*(x*y+w*z),1-2*(x*x+z*z),2*(y*z-w*x)],
  [2*(x*z-w*y),2*(y*z+w*x),1-2*(x*x+y*y)]])

def proper_matrix(R):
 R=np.asarray(R,dtype=float)
 if R.shape!=(3,3) or not np.all(np.isfinite(R)) or not np.allclose(R.T@R,np.eye(3),atol=1e-8,rtol=0) or abs(np.linalg.det(R)-1)>1e-8:raise ValueError('A proper orthonormal rotation is required')
 return R

def from_matrix(R):
 R=proper_matrix(R);trace=np.trace(R)
 if trace>0:
  d=2*math.sqrt(max(0,1+trace))
  q=np.array([d/4,(R[2,1]-R[1,2])/d,(R[0,2]-R[2,0])/d,(R[1,0]-R[0,1])/d])
 else:
  j=int(np.argmax(np.diag(R)))
  if j==0:
   d=2*math.sqrt(max(0,1+R[0,0]-R[1,1]-R[2,2]))
   q=np.array([(R[2,1]-R[1,2])/d,d/4,(R[0,1]+R[1,0])/d,(R[0,2]+R[2,0])/d])
  elif j==1:
   d=2*math.sqrt(max(0,1-R[0,0]+R[1,1]-R[2,2]))
   q=np.array([(R[0,2]-R[2,0])/d,(R[0,1]+R[1,0])/d,d/4,(R[1,2]+R[2,1])/d])
  else:
   d=2*math.sqrt(max(0,1-R[0,0]-R[1,1]+R[2,2]))
   q=np.array([(R[1,0]-R[0,1])/d,(R[0,2]+R[2,0])/d,(R[1,2]+R[2,1])/d,d/4])
 return unit(q)

def euler_quaternion(h,p,b):
 return unit(mul(mul(axis_quaternion([0,1,0],h),axis_quaternion([1,0,0],p)),axis_quaternion([0,0,1],b)))

def matrix_euler(R):
 R=proper_matrix(R);sp=float(np.clip(-R[1,2],-1,1));cp=math.hypot(R[1,0],R[1,1])
 p=math.atan2(sp,cp)
 if cp<1e-8:
  # Choose bank zero; at +90 h-b survives, at -90 h+b survives.
  p=math.copysign(math.pi/2,sp);h=math.atan2(-R[2,0],R[0,0]);b=0.
 else:h=math.atan2(R[0,2],R[2,2]);b=math.atan2(R[1,0],R[1,1])
 return np.array([h,p,b])

def quaternion_axis(q):
 q=unit(q)
 if q[0]<0:q=-q
 half=math.acos(float(np.clip(q[0],-1,1)));length=np.linalg.norm(q[1:])
 if length<1e-10:return np.array([1.,0,0]),0.
 return q[1:]/length,2*half

def interpolate(a,b,t,method='slerp'):
 if not math.isfinite(t) or not 0<=t<=1:raise ValueError('This lesson uses t in [0,1]')
 if method not in ['slerp','nlerp']:raise ValueError('Unknown interpolation method')
 a=unit(a);b=unit(b);dot=float(a@b)
 if dot<0:b=-b;dot=-dot
 dot=float(np.clip(dot,0,1))
 if method=='nlerp' or dot>.9995:return unit((1-t)*a+t*b)
 alpha=math.acos(dot)
 return unit(math.sin((1-t)*alpha)/math.sin(alpha)*a+math.sin(t*alpha)/math.sin(alpha)*b)
