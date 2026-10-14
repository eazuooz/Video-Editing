"""Future11.8 numerical preparation, with explicit right-handed examples."""
from pathlib import Path
import json,hashlib,datetime,math
import sympy as sp
import numpy as np
R=Path(__file__).resolve().parents[4];B=R/'production/batches/game-math-part2-full-series'
t,r,w,phase=sp.symbols('t r omega phase',real=True); checks=[]
def passed(name,**data):checks.append({'name':name,'passed':True,**data})
p=sp.Matrix([r*sp.cos(phase+w*t),r*sp.sin(phase+w*t)])
v=p.diff(t); a=v.diff(t)
assert sp.simplify(p.dot(v))==0 and sp.simplify(a+w**2*p)==sp.zeros(2,1)
assert sp.simplify(v.dot(v))==r**2*w**2
passed('Position derivatives and constant speed with varying velocity',formulas=['v=dp/dt','a=-omega²(p-center)','speed=r*abs(omega)','ac=r*omega²=speed²/r'],condition='constant radius>0 and angular velocity; fixed center; angles in radians')
radius=5; speed=10; period=2*math.pi*radius/speed; frequency=1/period
assert math.isclose(2*math.pi*frequency,speed/radius)
passed('Period,frequency and angular speed distinguish reciprocal units',radius=radius,speed=speed,centripetalAcceleration=speed**2/radius,periodSeconds=period,frequencyHz=frequency,angularSpeedRadiansPerSecond=speed/radius,doubledSpeedAcceleration=4*speed**2/radius)
h=sp.symbols('h',real=True); chord=2*r*sp.sin(w*h/2)
assert sp.simplify(sp.limit(chord/h,h,0)-r*w)==0
passed('Chord versus arc limit needs division by elapsed time',correctLimit='lim_dt->0 norm(delta_p)/abs(dt)=speed',finiteChord='2r*abs(sin(omega*dt/2))',finiteArc='r*abs(omega*dt)',condition='nonzero finite dt:chord and traveled arc generally differ')
n=np.array([1.,1.,1.])/math.sqrt(3);rv=np.array([1.,-1.,0.]);omega=2*n; vv=np.cross(omega,rv)
assert abs(vv@rv)<1e-12 and abs(vv@n)<1e-12 and np.allclose(np.cross(rv,vv)/(rv@rv),omega)
passed('Arbitrary3Daxis perpendicular radius, speed and inverse',unitAxis=n.tolist(),radiusVector=rv.tolist(),angularVector=omega.tolist(),velocity=vv.tolist(),speed=float(np.linalg.norm(vv)),coordinateConvention='Explicit right-handed cross product; adapt the source left-handed axis/sign convention consistently,never mix the two')
omega=np.array([1.,2.,3.]);rv=np.array([0.,2.,0.]);vv=np.cross(omega,rv); recovered=np.cross(rv,vv)/(rv@rv)
assert np.allclose(recovered,[1,0,3]) and np.allclose(np.cross(omega+[0,10,0],rv),vv)
assert np.allclose(np.cross(rv,vv+4*rv)/(rv@rv),recovered)
passed('One point cannot identify angular component parallel to radius',fullAngularVector=omega.tolist(),pointVelocity=vv.tolist(),recoverablePerpendicularComponent=recovered.tolist(),condition='r!=0; remove center translation for a movingcenter;radialvelocity is discarded; uniformcircular model assumes omega perpendicular to r')
apparent=-2/(t**2+4); assert sp.diff(apparent,t).subs(t,0)==0
assert float(abs(apparent.subs(t,0)))>float(abs(apparent.subs(t,3)))
passed('Constant linear motion has changing apparent angular velocity',position='(t,2,0)',linearVelocity='(1,0,0)',omegaZ='-2/(t²+4)',maximumMagnitudeAtClosestApproach=.5,condition='Relative to fixed origin,not a uniform circular orbit')
toy=6371000*(2*math.pi/86400)**2
assert math.isclose(toy,.03369,abs_tol=.00001)
passed('SourceEarth example is a declared approximation',radiusMeters=6371000,rotationPeriodSeconds=86400,centripetalMetersPerSecondSquared=toy,scope='Use source mean-radius and24hour assumptions; not an exact geodetic model or precise sidereal-rotation calculation')
source=R/'tmp/game-math-part2-sources/3e10b1ffa61e81d4bc3ee19712b63d65.txt'
record={'status':'future-source-and-math-preparation-only','atUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'target':'game-math-circular-motion','sourceSnapshot':source.relative_to(R).as_posix(),'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),
    'directReadSections':['11.8.1','11.8.2 including notes39/40 and inverseconditioncallout'],
    'sourceFiguresDirectlyViewed':False,'exercise11.9DirectRead':'pending','freshNativeVerificationBeforeProduction':'pending',
    'passed':True,'checks':checks,'futureProjectCreated':False,'futureNarrationWritten':False,'futureTtsStarted':False,'formalDuplicateReview':'not started'}
(B/'preflight/circular-motion-source-preparation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print({'passed':True,'checks':len(checks),'sourceEarthToyAcceleration':toy})
