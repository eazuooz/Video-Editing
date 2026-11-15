"""Pixel anchors from the unchanged Unity analytic movement/camera, not game measurements."""
import math,json
import numpy as np

def vec(d):return np.array([d.get(k,0) for k in ('x','y','z')],float)
def state(p,t):
    kind=p.get('kind',0);o=vec(p.get('origin',{}));v=vec(p.get('velocity',{'x':3}));a=vec(p.get('acceleration',{'y':-4}));valid=True
    if kind==0:
        q,l,c=p.get('quadratic',-1),p.get('linear',6),p.get('constant',-1);x=q*t*t+l*t+c;v=np.array([2*q*t+l,0,0]);a=np.array([2*q,0,0]);r=np.array([x,0,0])
    elif kind==1:r=v*t
    elif kind==2:r=v*t+a*t*t/2;v=v+a*t
    elif kind==3:
        g=2*p.get('jumpHeight',2)/p.get('timeToApex',1)**2;vy=g*p.get('timeToApex',1);vx=p.get('horizontalSpeed',3);r=np.array([vx*t,vy*t-g*t*t/2,0]);v=np.array([vx,vy-g*t,0]);a=np.array([0,-g,0])
    elif kind==4:
        n=vec(p.get('axis',{'z':1}));n/=np.linalg.norm(n);e=vec(p.get('radiusDirection',{'x':1}));e-=n*np.dot(n,e);e/=np.linalg.norm(e);angle=p.get('theta0',0)+p.get('omega',1)*t;r=(e*math.cos(angle)+np.cross(n,e)*math.sin(angle))*p.get('radius',2);v=np.cross(n*p.get('omega',1),r);a=-r*p.get('omega',1)**2
    elif kind==5:
        valid=all(abs(t-k)>1e-10 for k in (0,2,4,7))
        if t<2:x,y,z=2*t-t*t,2-2*t,-2
        elif t<4:x=y=z=0
        elif t<7:x,y,z=math.sin(math.pi*t),math.pi*math.cos(math.pi*t),-math.pi**2*math.sin(math.pi*t)
        else:x,y,z=7-t,-1,0
        r=np.array([x,0,0]);v=np.array([y,0,0]);a=np.array([z,0,0])
    elif kind==6:
        slope=p.get('chainSlope',.25);direction=np.array([math.sqrt(1-slope*slope),slope,0]);v=direction*p.get('pathSpeed',4);r=v*t;a=np.zeros(3)
    elif kind==7:r=np.array([3*t if t<=2 else 12-3*t,0,0]);v=np.array([3 if t<2 else -3,0,0]);a=np.zeros(3);valid=abs(t-2)>1e-10
    elif kind in (8,9,10,11,12,13,14,18):
        amp=p.get('amplitude',1);f=p.get('frequency',1);rate=p.get('rate',1);power=p.get('power',3)
        if kind==8:x,y,z=amp*math.sin(f*t),amp*f*math.cos(f*t),-amp*f*f*math.sin(f*t)
        elif kind==9:x,y,z=amp*math.cos(f*t),-amp*f*math.sin(f*t),-amp*f*f*math.cos(f*t)
        elif kind==10:x=amp*math.exp(rate*t);y=rate*x;z=rate*rate*x
        elif kind==11:x,y,z=amp*t**power,amp*power*t**(power-1),amp*power*(power-1)*t**(power-2)
        elif kind==12:x,y,z=math.sin(t*t),2*t*math.cos(t*t),2*math.cos(t*t)-4*t*t*math.sin(t*t)
        elif kind==13:
            g=math.cos(t)+3*t;dg=-math.sin(t)+3;ddg=-math.cos(t);x=math.exp(g);y=x*dg;z=x*(dg*dg+ddg)
        elif kind==14:
            g=math.sin(3*t)+math.sin(t*t);dg=3*math.cos(3*t)+2*t*math.cos(t*t);ddg=-9*math.sin(3*t)+2*math.cos(t*t)-4*t*t*math.sin(t*t);x=math.exp(g);y=x*dg;z=x*(dg*dg+ddg)
        else:x,y,z=math.log(abs(t)),1/t,-1/(t*t)
        r=np.array([x,0,0]);v=np.array([y,0,0]);a=np.array([z,0,0])
    elif kind==15:
        x=y=z=0
        for k,c in zip(p.get('powers',[]),p.get('coefficients',[])):
            x+=c*t**k
            if k:y+=c*k*t**(k-1)
            if k not in (0,1):z+=c*k*(k-1)*t**(k-2)
        r=np.array([x,0,0]);v=np.array([y,0,0]);a=np.array([z,0,0])
    elif kind==16:
        x=4*t if t<1 else 4-2*(t-1) if t<2 else 2 if t<4 else 2+5*(t-4);r=np.array([x,0,0]);v=np.array([4 if t<1 else -2 if t<2 else 0 if t<4 else 5,0,0]);a=np.zeros(3)
    elif kind==17:
        after=max(0,t-1);r=np.array([2*t+after*after,0,0]);v=np.array([2+2*after,0,0]);a=np.array([0 if t<1 else 2,0,0])
    else:raise ValueError(('Do not invent an unported visible model',kind))
    return o+r,v,a,valid

def raw(m,p):
    p=np.array(p,float).copy();p[2]*=-1
    if m.get('positiveYIsDown'):p[1]*=-1
    x,y,z=np.radians(vec(m.get('displayEuler',{})))
    # Unity Quaternion.Euler is Z then X then Y.
    rz=np.array([[math.cos(z),-math.sin(z),0],[math.sin(z),math.cos(z),0],[0,0,1]])
    rx=np.array([[1,0,0],[0,math.cos(x),-math.sin(x)],[0,math.sin(x),math.cos(x)]])
    ry=np.array([[math.cos(y),0,math.sin(y)],[0,1,0],[-math.sin(y),0,math.cos(y)]])
    return ry@rx@rz@p

def world(m,p):return vec(m.get('worldOrigin',{'x':-6}))+raw(m,p)*m.get('worldUnitsPerModelUnit',.65)

def fit(lesson):
    models=[lesson['motion']]+[s['motionOverride'] for s in lesson['steps'] if s.get('useMotionOverride')]
    points=[]
    for m in models:
        for t in np.linspace(m.get('startTime',0),m.get('endTime',3),161):
            p,v,a,valid=state(m['parameters'],float(t));at=world(m,p);points.append(at)
            if valid and m.get('showVelocity',True):points.append(at+raw(m,v)*m.get('velocityArrowScale',.3))
            if valid and m.get('showAcceleration',False):points.append(at+raw(m,a)*m.get('accelerationArrowScale',.15))
            if m.get('showRadius'):points.append(world(m,vec(m['parameters'].get('origin',{}))))
    points=np.asarray(points);lo=points.min(0);hi=points.max(0);size=hi-lo;scale=min(1,6.8/max(.001,size[0]),1.1/max(.001,size[1]));offset=np.array([-4.55,.75,0])-(lo+hi)/2*scale
    return scale,offset

def at(lesson,seconds,fitting=None):
    duration=lesson['durationSeconds'];u=min(1,max(0,seconds/duration));times=lesson.get('stepSeconds',[]);values=lesson.get('stepPositions',[])
    if times:u=float(np.interp(seconds,times,values))
    n=len(lesson['steps']);index=min(n-1,int(u*n));fraction=min(1,u*n-index);s=lesson['steps'][index];m=s['motionOverride'] if s.get('useMotionOverride') else lesson['motion'];t=s.get('modelFrom',0)+(s.get('modelTo',0)-s.get('modelFrom',0))*fraction
    scale,offset=fitting or fit(lesson);p,v,a,valid=state(m['parameters'],t);w=world(m,p)*scale+offset
    return dict(x=960+96*w[0],y=540-96*(w[1]-2),t=t,model=m,position=p.tolist(),velocity=v.tolist(),acceleration=a.tolist(),valid=valid)

def visible(lesson):
    if not lesson.get('motion'):return False
    if lesson['motion'].get('subjectKind')=='hare' or lesson['motion'].get('scalarFunction'):return False
    if lesson.get('diagramMode')=='flow-accumulation':return False
    if lesson.get('beatId','').startswith('M26-') and (lesson.get('diagramMode') or lesson['beatId']=='M26-025'):return False
    return True
