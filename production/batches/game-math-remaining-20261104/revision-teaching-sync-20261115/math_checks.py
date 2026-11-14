"""Independent numerical checks of the new diagrams' mathematical claims."""
import math
import numpy as np
from inventory import HERE,save,sha


def main():
    checks=[]
    def same(name,a,b):
        assert np.allclose(a,b,atol=1e-10,rtol=1e-10),(name,a,b)
        checks.append(name)
    x=lambda t:-t*t+6*t-1
    same('M24 same t in x and v at 2.5',[x(2.5),-2*2.5+6],[7.75,1])
    for t,h in ((.4,.1),(1.2,.01),(2.5,.001)):
        same('M24 expand, factor and cancel at nonzero h',(x(t+h)-x(t))/h,-2*t-h+6)
    same('M25 final-speed rectangle vs true triangular area',[76.8*2.4,.5*32*2.4**2],[184.32,92.16])
    same('M25 prescribed displacement acceleration',2*(15-2*3)/3**2,2)
    peak=79.25/32;back=79.25/16
    same('M25 peak speed and return position',[-79.25+32*peak,-79.25*back+16*back**2],[0,0])
    same('M25 constant power area',100*2,200)
    N=np.array([0.,1.,0.]);L=np.array([.6,.8,0.]);R=2*np.dot(N,L)*N-L
    same('M21 reflect around the surface normal',R,[-.6,.8,0])
    same('M21 reflected unit direction length',np.linalg.norm(R),1)
    A=np.array([[2.,.4,0],[0,1.5,0],[0,0,.7]])
    tangent=np.array([1.,0.,0.]);normal=np.array([0.,1.,0.])
    same('M23 inverse-transpose remains perpendicular',np.dot(A@tangent,np.linalg.inv(A).T@normal),0)
    theta=.73;r=2.3;omega=1.7
    position=r*np.array([math.cos(theta),math.sin(theta)])
    acceleration=-omega**2*position
    same('M26 centripetal magnitude',np.linalg.norm(acceleration),(r*omega)**2/r)
    velocity=r*omega*np.array([-math.sin(theta),math.cos(theta)])
    same('M26 inward acceleration is perpendicular to the current velocity',np.dot(acceleration,velocity),0)
    same('M28 critical damping initial velocity',-6-4,-10)
    same('M28 one critical crossing',(1-6*(1/6))*math.exp(-4/6),0)
    same('M28 semi-implicit one step',[0+16*.1,0+(0+16*.1)*.1],[1.6,.16])
    for mA,mB,e,n in ((2.,3.,.7,np.array([2.,1.])),(1.,4.,1.,np.array([0.,3.]))):
        a=np.array([4.,2.]);b=np.array([-1.,0.]);before=np.dot(a-b,n)
        k=(1+e)*before/((1/mA+1/mB)*np.dot(n,n))
        aa=a-k*n/mA;bb=b+k*n/mB
        same('M29 impulse conserves total momentum',mA*aa+mB*bb,mA*a+mB*b)
        same('M29 nonunit normal restitution condition',np.dot(aa-bb,n),-e*before)
    same('M30 parallel-axis units and value',.2+2*1**2,2.2)
    vc=5-75*1.25/1075;vp=vc+1.25
    same('M30 train + person momentum',1000*vc+75*vp,1075*5)
    same('M30 common 16 s displacement offset',[16*vc-16*(vc-5),16*vp-16*(vp-5)],[80,80])
    same('M31 four-point polynomial midpoint',18*.5**3-27*.5**2+10*.5+2,2.5)
    p0=np.array([0.,0.]);p1=np.array([2.,0.]);v0=np.array([0.,3.]);v1=np.array([0.,-3.])
    coefficients=np.array([p0,v0,3*(p1-p0)-2*v0-v1,2*(p0-p1)+v0+v1])
    def polynomial(t):return sum(c*t**i for i,c in enumerate(coefficients))
    def derivative(t):return sum(i*coefficients[i]*t**(i-1) for i in range(1,4))
    same('M31 Hermite four endpoint conditions',[polynomial(0),polynomial(1),derivative(0),derivative(1)],[p0,p1,v0,v1])
    same('M31 Hermite weighted midpoint',polynomial(.5),[1,.75])
    controls=np.array([coefficients[0],coefficients[0]+coefficients[1]/3,
        coefficients[0]+2*coefficients[1]/3+coefficients[2]/3,sum(coefficients)])
    def bezier(points,t):
        n=len(points)-1
        return sum(math.comb(n,i)*t**i*(1-t)**(n-i)*p for i,p in enumerate(points))
    elevated=np.array([controls[0],*[i/4*controls[i-1]+(1-i/4)*controls[i] for i in range(1,4)],controls[-1]])
    for t in (0,.17,.5,.83,1):
        same('M32 polynomial to Bezier inverse coefficients',bezier(controls,t),polynomial(t))
        same('M33 degree elevation preserves the same curve',bezier(elevated,t),bezier(controls,t))
    same('M32 cubic midpoint weights',[math.comb(3,i)*.5**3 for i in range(4)],[1/8,3/8,3/8,1/8])
    same('M33 unequal duration C1 scaling',np.array([4.,2.])/2,np.array([2.,1.])/1)
    jump=np.array([[0.,0.],[4/3,1/3],[4/3,2/3],[0.,1.]])
    for u in (0,.25,.5,.75,1):same('M33 cubic handles reproduce the two-second jump',bezier(jump,u),[4*u*(1-u),u])
    report=dict(status='pass',checks=checks,count=len(checks),
        formulaAuthoringSha256=sha(HERE/'workings.py'),motionAuthoringSha256=sha(HERE/'motion_panels.py'),
        scope='Specified algebra/conditions and exact inputs driving newly authored figures; separate from frame, audio and human review')
    save(HERE/'mathematical-qa.json',report);print(len(checks),'independent mathematical checks passed')


if __name__=='__main__':main()
