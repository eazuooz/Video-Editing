"""Independent arithmetic for future11.6–11.7; no future production started."""
from pathlib import Path
import json, hashlib, datetime, math
import sympy as sp
R=Path(__file__).resolve().parents[4]
B=R/'production/batches/game-math-part2-full-series'
t=sp.symbols('t',real=True); checks=[]
def passed(name,**evidence): checks.append({'name':name,'passed':True,**evidence})
T=sp.Rational(12,5); a=sp.Integer(32)
sums=[]
for n,want in [(6,76.8),(12,84.48),(24,88.32)]:
    dt=T/n; value=sum(a*i*dt*dt for i in range(n))
    assert math.isclose(float(value),want,abs_tol=1e-12)
    sums.append({'rectangles':n,'leftEndpointSumFeet':float(value)})
exact=sp.integrate(a*t,(t,0,T)); assert exact==sp.Rational(2304,25)
passed('Constant32ft/s2 left rectangles approach signed integral92.16ft',sums=sums,exactFeet=float(exact))
v0=sp.Integer(3); dt=sp.Integer(4); displacement=sp.Integer(4)
correct=2*(displacement-v0*dt)/dt**2; wrong=(2*displacement-v0*dt)/dt**2
assert correct==-1 and wrong==sp.Rational(-1,4)
assert v0*dt+correct*dt**2/2==displacement
passed('Scalar/vector acceleration inverse needs factor2 on both terms',correctAcceleration=float(correct),sourceTypoValue=float(wrong),condition='t!=0; components use the same scalar formula')
fall=math.sqrt(2*1353/32); initial=1353/12-32*12/2
assert math.isclose(initial,-79.25) and math.isclose(initial*12+16*12**2,1353)
passed('Historical1353ft toy arithmetic unrounded',gravityFeetPerSecondSquared=32,fallSeconds=fall,impactFeetPerSecond=32*fall,initialFor12s=initial,roundedSourceInitial=-79.2,roundingResidualFeet=-79.2*12+16*12**2-1353,condition='No air resistance;32ft/s2 is the declared approximation, not an exact physical constant or verified building measurement')
roots=sp.solve(10*t-5*t**2-4,t); assert len(roots)==2 and all(r>0 for r in roots)
passed('Choose physically valid quadratic roots and handle a0 separately',twoPositiveRoots=[float(r) for r in roots],linearCaseSeconds=2,unreachableExample='10t-5t² cannot reach6 because its maximum is5')
H=sp.Integer(2); apex=sp.Integer(1); g=2*H/apex**2; vy=2*H/apex
assert g==vy==4 and vy*apex-g*apex**2/2==H
assert 3*(2*apex)==6
base_range=sp.Rational(2)*vy*3/g; doubled_range=sp.Rational(2)*(2*vy)*(2*3)/g
assert doubled_range==4*base_range
passed('Jump design and equal-elevation range conditions',heightMeters=2,apexSeconds=1,gravityMagnitude=4,initialVerticalSpeed=4,horizontalSpeed=3,flightSeconds=2,rangeMeters=6,doublingSpeedRangeMultiplier=4,condition='constant gravity; no drag/collision; landing at initial elevation')
acc=sp.Matrix([0,-4,0]); vel=sp.Matrix([3,4,0]); target=sp.Matrix([7,0,0])
candidate=sp.Integer(2); pos=vel*candidate+acc*candidate**2/2
assert (pos-target).dot(acc)==0 and pos!=target
passed('Projection supplies a candidate, full vector residual proves hit or miss',candidateSeconds=2,position=list(pos),target=list(target),missDistance=1,condition='Project consistently; nonunit direction scales all coefficients equally;a0 and zero projected acceleration need separate linear handling')
v=3-t; signed=sp.integrate(v,(t,0,4)); distance=sp.integrate(v,(t,0,3))-sp.integrate(v,(t,3,4))
assert signed==4 and distance==5
n=sp.symbols('n',integer=True,positive=True)
right=sp.summation(sp.Symbol('i',integer=True)/n**2,(sp.Symbol('i',integer=True),1,n))
assert sp.limit(right,n,sp.oo)==sp.Rational(1,2)
power=100+50*t; energy=sp.integrate(power,(t,0,2)); assert energy==300
passed('Signed integral versus traveled distance, endpoint convention and units',netDisplacement=4,totalDistance=5,rightEndpoint='a+i*dx,i1..n',leftEndpoint='a+(i-1)*dx,i1..n',rightSumLimit=.5,toyEnergyJoules=int(energy),kWh=float(energy/3600000),conditions='continuous/piecewise continuous scoped functions; distance integrates absolute speed;W*s=J')
F=sp.integrate(v,t); assert sp.diff(F+7,t)==v and (F+7).subs(t,4)-(F+7).subs(t,0)==signed
assert sp.integrate(0,(t,0,1))==0
passed('Fundamental theorem, integration variable and arbitrary constant',correct='integral_a^b f(t)dt=F(b)-F(a)',initialPosition='x(t)=x0+integral_t0^t v(u)du',counterexample='f=0:changing only the lower endpoint cannot represent every constant',conditions='continuous f; v power rule excludes exponent-1 unless logarithm/domain handled separately')
source=R/'tmp/game-math-part2-sources/3e10b1ffa61e81d4bc3ee19712b63d65.txt'
record={'status':'future-source-reading-and-math-preparation-only','atUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'target':'game-math-acceleration-integration','sourceSnapshot':source.relative_to(R).as_posix(),'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),
    'directReadSections':['11.5','11.6 complete including both rectangle tables and multidimensional cases','11.7.1','11.7.2','11.7.3'],
    'directReadRanges':['1–1407, with truncated middle passages reread separately'],
    'wholeChapter11DirectlyRead':False,'sourceFiguresDirectlyViewed':False,'freshNativeVerificationBeforeProduction':'pending',
    'passed':all(c['passed'] for c in checks),'checks':checks,
    'futureProjectCreated':False,'formalDuplicateReview':'not started','futureNarrationWritten':False,'futureTtsStarted':False}
(B/'preflight/acceleration-integration-source-preparation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2,default=lambda x:float(x))+'\n',encoding='utf8')
print({'passed':record['passed'],'checks':len(checks),'fallSeconds':fall,'initialFor12s':initial})
