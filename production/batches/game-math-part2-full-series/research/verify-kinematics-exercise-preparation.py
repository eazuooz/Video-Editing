"""Check chapter 11 exercises before scripts; this is not production approval."""
from pathlib import Path
import cmath, hashlib, json, math

R = Path(__file__).resolve().parents[4]
source = R / 'tmp/game-math-part2-sources/3e10b1ffa61e81d4bc3ee19712b63d65.txt'
checks = []
def record(name, evidence):
    checks.append(dict(name=name, passed=True, evidence=evidence))

# Exact international inch and conventional pound-force, not pound-mass.
psi_pa = 4.4482216152605 / .0254**2
assert math.isclose(psi_pa, 6894.757293168, rel_tol=1e-12)
record('pressure uses force per area', dict(pascalPerPsi=psi_pa, psiPerPascal=1/psi_pa,
    inputs='1 international inch=.0254m; conventional pound-force=4.4482216152605N'))

def x(t):
    if t < 2: return 2*t-t*t
    if t < 4: return 0
    if t < 7: return math.sin(math.pi*t)
    return 7-t
intervals = [(0,1),(1,2),(0,2),(5.5,6.5),(0,9)]
averages = [(x(b)-x(a))/(b-a) for a,b in intervals]
assert all(math.isclose(v,e,abs_tol=1e-12) for v,e in zip(averages,[1,-1,0,2,-2/9]))
record('piecewise average velocities', dict(intervals=intervals, answers=averages))

times = [.1,1,1.9,4.1,5,6.5,8,9]
def v(t):
    if 0<t<2: return 2-2*t
    if 2<t<4: return 0
    if 4<t<7: return math.pi*math.cos(math.pi*t)
    if t>7: return -1
    raise ValueError('join or domain boundary requires one-sided interpretation')
def a(t):
    if 0<t<2: return -2
    if 2<t<4: return 0
    if 4<t<7: return -math.pi**2*math.sin(math.pi*t)
    if t>7: return 0
    raise ValueError('ordinary acceleration undefined at a velocity jump')
for t in times:
    h=1e-5
    assert math.isclose((x(t+h)-x(t-h))/(2*h),v(t),abs_tol=1e-8)
    assert math.isclose((v(t+h)-v(t-h))/(2*h),a(t),abs_tol=1e-8)
joins=[dict(t=2,position=0,leftVelocity=-2,rightVelocity=0),
       dict(t=4,position=0,leftVelocity=0,rightVelocity=math.pi),
       dict(t=7,position=0,leftVelocity=-math.pi,rightVelocity=-1)]
record('interior derivatives and continuous positions with velocity jumps',
       dict(times=times,velocities=[v(t) for t in times],accelerations=[a(t) for t in times],
            joins=joins,joinDerivative='undefined; no ordinary finite acceleration at these jumps'))

# Exercise 9 explicitly uses the chapter's ideal 32 ft/s^2 constant gravity.
vx=150*math.cos(math.radians(40)); vy=150*math.sin(math.radians(40)); g=32
peak=vy/g; sameHeight=2*peak
assert math.isclose(10+vy*sameHeight-.5*g*sameHeight**2,10,abs_tol=1e-10)
record('projectile at forty degrees',dict(gravityFeetPerSecondSquared=g,
    initialVelocity=[vx,vy],peakSeconds=peak,peakPosition=[vx*peak,10+vy**2/(2*g)],
    sameInitialHeightSeconds=sameHeight,horizontalDisplacement=vx*sameHeight))

# Dotting with acceleration finds candidates; it is not a complete vector hit test.
aa=16; av=-16; ad=0
candidate=(-av+math.sqrt(av*av+2*aa*ad))/aa
assert candidate==2
actual=[3*candidate,4*candidate-.5*4*candidate*candidate,0]
assert actual==[6,0,0] and actual!=[7,0,0]
record('vector quadratic requires full residual',dict(formula='t=(-a·v0 ± sqrt((a·v0)^2+2|a|^2 a·delta))/|a|^2',
    guards=['a=0: linear motion','negative discriminant: no real projected candidate',
            'filter t>=0 and compare all position components'],
    counterexample=dict(v0=[3,4,0],a=[0,-4,0],target=[7,0,0],candidateSeconds=candidate,actualPosition=actual)))

for theta in [-2,-.5,0,.7,2]:
    series=sum((1j*theta)**n/math.factorial(n) for n in range(31))
    assert abs(series-(math.cos(theta)+1j*math.sin(theta)))<1e-14
record('Euler formula from convergent complex series',dict(result='exp(i theta)=cos(theta)+i sin(theta)',
    grouping='even powers form cosine; odd powers form i times sine; theta is in radians'))

# Historical exercise conditions; do not claim current ISS operating values.
radius=(6371+340)*1000; speed=27740*1000/3600
period=2*math.pi*radius/speed; centripetal=speed*speed/radius
assert 5400<period<5500 and 8.8<centripetal<8.9
record('orbital radius includes altitude',dict(status='declared ideal circular toy; source historical conditions',
    earthMeanRadiusMetres=6371000,altitudeMetres=340000,speedMetresPerSecond=speed,
    orbitalRadiusMetres=radius,periodSeconds=period,periodMinutes=period/60,
    centripetalMetresPerSecondSquared=centripetal))

out=R/'production/batches/game-math-part2-full-series/preflight/kinematics-exercises-source-preparation.json'
result=dict(status='CPU-source-and-math-preparation-only',source=dict(path=source.relative_to(R).as_posix(),
    sha256=hashlib.sha256(source.read_bytes()).hexdigest(),directReadSections=['11.1 through 11.8.2','11.9 all twelve exercises and closing source note'],
    wholeCachedChapterRead=True,freshNativePageVerification='pending',sourceFiguresViewed=False),
    checks=checks,passed=True,productionCreated=False,narrationWritten=False,ttsStarted=False,formalDuplicateReview='pending')
out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Passed',len(checks),'chapter11 exercise checks; fresh source/figures/production review remains pending.')
