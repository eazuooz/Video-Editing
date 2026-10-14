"""CPU-only independent checks of12.2.3; no production/TTS approval."""
from pathlib import Path
import json,math,hashlib,datetime
import numpy as np
R=Path(__file__).resolve().parents[4];B=R/'production/batches/game-math-part2-full-series';checks=[]
def check(name,ok,detail):
 assert ok,name
 checks.append(dict(name=name,passed=bool(ok),detail=detail))
x0=1.;v0=2.;w=2.;A=math.hypot(x0,v0/w);phase=math.atan2(-v0/w,x0)
check('undamped amplitude and signed initial velocity',abs(A*math.cos(phase)-x0)<1e-12 and abs(-A*w*math.sin(phase)-v0)<1e-12 and abs(A-math.sqrt(2))<1e-12,'A√2,θ=-π/4,ω2 reconstruct x0=1,v0=2. A and x0 alone allow ±v0; zero amplitude has arbitrary phase. k/m has units s^-2 and ω has rad/s.')
m=2.;k=8.;ccrit=2*math.sqrt(m*k)
check('physical versus mass-normalized coefficients',ccrit==8 and k/m==4 and ccrit/m==4 and math.sqrt(4*k/m)==2*math.sqrt(k/m),'Critical physical c8kg/s for m2kg,k8N/m; mass-normalized code k4,c4. Quadruple k with fixed m doubles frequency, not quadruples it.')
def under(t,omega,zeta,x,v):
 d=zeta*omega;wd=omega*math.sqrt(1-zeta*zeta);a=x;b=(d*x+v)/wd
 f=a*math.cos(wd*t)+b*math.sin(wd*t);fp=wd*(-a*math.sin(wd*t)+b*math.cos(wd*t));fpp=-wd*wd*f;e=math.exp(-d*t)
 return e*f,e*(fp-d*f),e*(fpp-2*d*fp+d*d*f)
states=[under(t,4,.25,1,.5) for t in [0,.1,.5,1]]
check('underdamped solution and differential equation',abs(states[0][0]-1)<1e-12 and abs(states[0][1]-.5)<1e-12 and all(abs(a+16*x+2*v)<1e-11 for x,v,a in states),'ω0=4,ζ=.25 givesωd=√15; initial position/velocity and x″+ω0²x+2ζω0x′=0 independently checked. ζ0 has no decay; ζ1 requires its own limit formula.')
def critical(t,omega,x,v):
 b=omega*x+v;e=math.exp(-omega*t);f=x+b*t
 return f*e,(b-omega*f)*e,(-2*omega*b+omega*omega*f)*e
states=[critical(t,2,1,-10) for t in [0,.125,.5,1]]
check('critical damping can cross the target once',abs(states[0][1]+10)<1e-12 and states[1][0]==0 and states[2][0]<0 and all(abs(a+4*x+4*v)<1e-12 for x,v,a in states),'x=(1-8t)e^-2t with x0=1,v0=-10 crosses at.125s. Nonoscillatory does not guarantee no overshoot for arbitrary initial velocity.')
r1=-4+math.sqrt(12);r2=-4-math.sqrt(12);a=-r2/(r1-r2);b=1-a
check('overdamped real roots and initial conditions',r1<0 and r2<0 and abs(a+b-1)<1e-12 and abs(a*r1+b*r2)<1e-12 and all(abs(r*r+8*r+4)<1e-12 for r in [r1,r2]),dict(omega0=2,zeta=2,roots=[r1,r2],assumptions='Positive m,k,c; comparison depends on initial conditions and criterion. No blanket fastest/no-overshoot guarantee.'))
x,v,a=under(.5,4,.25,1,.5);energyRate=16*x*v+v*a
check('viscous damping dissipates energy',abs(energyRate+2*v*v)<1e-11 and energyRate<=0,'For fixed rest position,m1,k16,c2: d(.5mv²+.5kx²)/dt=-cv². A moving set point can supply energy; do not extrapolate autonomous decay to arbitrary inputs.')
def updateMatrix(dt,k,c):return np.array([[1-k*dt*dt,dt*(1-c*dt)],[-k*dt,1-c*dt]])
small=max(abs(np.linalg.eigvals(updateMatrix(.05,4,4))));large=max(abs(np.linalg.eigvals(updateMatrix(1,4,4))))
check('semi-implicit Euler does not inherit unconditional stability',small<1 and large>1 and np.allclose(updateMatrix(1,4,4),[[-3,-3],[-4,-3]]),dict(spectralRadiusSmallDt=float(small),spectralRadiusLargeDt=float(large),codeOrder='velocity+=accel*dt; position+=updatedVelocity*dt. Continuous critical damping is stable, butdt1 discrete update diverges.'))
q=10.;r=2.;lam=3.;one=r+(q-r)*math.exp(-lam)
for _ in range(60):q=r+(q-r)*math.exp(-lam/60)
check('first-order lag sign and constant-target composition',abs(q-one)<1e-12 and one>r and one<10,'Positiveλ with x′=-λx decays. Exact qnew=r+(q-r)e^-λdt is independent of step subdivision for a fixed target; changing targets are a different forcing problem. A first-order filter has no separate velocity state.')
p=R/'tmp/game-math-part2-sources/3e10b1ffa61e813b8611ee04a6c6c3ea.txt'
value=dict(status='future-cpu-numerical-preparation-not-production-approval',atUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),target='game-math-springs-control',checks=checks,source=dict(path=p.relative_to(R).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),cachedTextDirectlyRead='all12.2 including all equations/code/corrections',freshNative='pending',figures='not directly viewed'),clarifications=['Hooke signed force is different from its magnitude; nonsingular spring direction and elastic range need guards.','k1/k2 integration constants are not the physical spring constant k.','Set point derivatives affect whether D uses value velocity or error velocity; the historical code damps value velocity.','PID integral action removes steady bias only under suitable stable control assumptions; no universal guarantee.','Nearζ1 avoid evaluating an underdamped expression with vanishingωd as a numerically safe universal solution.','Zero k/m,negative damping and arbitrary changing inputs require separate handling.','No named-game camera spring implementation is inferred from a gameplay shot.'],production=dict(projectCreated=False,footageSelected=False,ttsStarted=False,duplicateReview='pending after current private delivery'))
(B/'preflight/springs-control-source-preparation.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(dict(passed=True,checks=len(checks),productionStarted=False)))
