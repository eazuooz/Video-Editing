"""CPU checks of directly read11.1–11.5; no future video or TTS is started."""
from pathlib import Path
import json,hashlib,math
from fractions import Fraction as F
from datetime import datetime,timezone
import numpy as np
import sympy as sp
R=Path(__file__).resolve().parents[4];B=Path(__file__).resolve().parent.parent
checks=[]
def check(name,evidence):checks.append(dict(name=name,passed=True,evidence=evidence))
t,h,x=sp.symbols('t h x',real=True);position=-t**2+6*t-1
quotient=sp.cancel((position.subs(t,t+h)-position)/h)
assert quotient==-2*t-h+6 and sp.limit(quotient,h,0)==-2*t+6
assert position.subs(t,1)==4 and position.subs(t,3)==8 and sp.diff(position,t).subs(t,sp.Rational(5,2))==1
rows=[]
for delta in [F(1,2),F(1,10),F(1,20),F(1,100),F(1,200),F(1,1000)]:
    rate=1-delta;dt=F(5,2)+delta
    xp=-dt*dt+6*dt-1;change=xp-F(31,4)
    assert change/delta==rate
    rows.append(dict(deltaT=float(delta),position=float(xp),displacement=float(change),averageVelocity=float(rate)))
check('source-quadratic-limit-and-unrounded-table',dict(position='-t^2+6t-1',differenceQuotient='-2t-h+6 for h!=0',velocity='-2t+6',at2point5=1,units='Sourcefur/min, not inferred gameworld units.',rows=rows,roundingPolicy='Calculate before displayrounding;0.004975/0.005=.995 and0.000999/0.001=.999.'))
assert F(1457,100)/F(3048,10000)==F(182125,3810)
lengthFeet=float(F(1457,100)/F(3048,10000));speedFeet=float(F(188000,3600)/F(3048,10000))
assert round(lengthFeet,2)==47.80 and round(speedFeet)==171
check('exact-international-foot-and-time-conversion',dict(internationalFootMeters=.3048,meters14point57InFeet=lengthFeet,kph188InFeetPerSecond=speedFeet,sourceApproximation3point28083='Approximateconversion, not exactdefinition.',milliseconds16InSeconds=.016,displacementAt3MetersPerSecond=.048))
v0,a,total=F(3),F(-1),F(4);turn=-v0/a;turnX=v0*turn+a*turn*turn/2;finalX=v0*total+a*total*total/2
distance=turnX+(turnX-finalX)
assert turn==3 and turnX==F(9,2) and finalX==4 and distance==5
check('signed-displacement-versus-total-distance',dict(contract='1D,x0=0,v0=3m/s,a=-1m/s^2,t4s.',turnTime=3,maxPosition=4.5,finalPosition=4,distance=5,averageVelocity=1,averageSpeed=1.25,meaning='Positiveposition is independent of velocitysign; return to start may have0averagevelocity with nonzerodistance.'))
poly=3*t**5-4*t;assert sp.diff(poly,t)==15*t**4-4
reciprocal=1/t+4/t**3;assert sp.diff(reciprocal,t)==-1/t**2-12/t**4
assert sp.diff(sp.Integer(3),t)==0 and sp.diff(t,t)==1
check('power-linearity-and-domain-guards',dict(examples=['d(3t^5-4t)/dt=15t^4-4','d(1/t+4/t^3)/dt=-1/t^2-12/t^4 for t!=0','d(constant)/dt=0 including t0'],guards='Do not compute0*(t^-1) at t0 to prove constantderivative; state the constantfunction directly. Negativepowers require nonzero input.'))
sinP=x-x**3/sp.factorial(3)+x**5/sp.factorial(5)-x**7/sp.factorial(7)
assert sp.diff(sinP,x)==1-x**2/2+x**4/24-x**6/720
grid=np.linspace(-1,1,2001);values=sp.lambdify(x,sinP,'numpy')(grid);error=float(np.max(np.abs(np.sin(grid)-values)))
assert error<1/math.factorial(9)
check('radian-sine-polynomial-and-correct-factorial',dict(polynomial='x-x^3/3!+x^5/5!-x^7/7!',maximumSampledAbsoluteErrorOnMinus1To1=error,alternatingSeriesBound=1/math.factorial(9),sourceTypo='d(x^5/5!)/dx=5x^4/5!=x^4/4!, not5x^4/4!.',scope='Teachingpolynomial, not a claim of every currentmathlibraryimplementation; radians and range matter.'))
expressions=[sp.sin(3*x),sp.sin(x*x),sp.exp(sp.cos(x)+3*x),sp.exp(sp.sin(3*x)+sp.sin(x*x))]
answers=[3*sp.cos(3*x),2*x*sp.cos(x*x),(-sp.sin(x)+3)*sp.exp(sp.cos(x)+3*x),(3*sp.cos(3*x)+2*x*sp.cos(x*x))*expressions[3]]
for expr,answer in zip(expressions,answers):assert sp.simplify(sp.diff(expr,x)-answer)==0
check('chain-rule-independent-variable',dict(sourceExamples=['sin3x','sin(x^2)','exp(cosx+3x)','exp(sin3x+sin(x^2))'],correctDifferentiationVariable='x',ifXIsTimeDependent='Multiply each dx derivative by dx/dt.',slopeVsVerticalVelocity='dy/dt=(dy/ds)(ds/dt); signedtrackparameter is not totaldistancetraveled.'))
tiny=float(2.5+1e-20);assert tiny==2.5
check('finite-precision-is-not-the-limit',dict(atTime=2.5,deltaTooSmall=1e-20,tPlusDeltaEqualsT=True,result='Directfloatingdifference becomes0orundefined instead of mathematicalderivative1; smallerstep is not alwaysmoreaccurate.',corner='x=abs(t) has distinct left/rightslopes at0; do not assign a uniqueinstantaneousvelocity there.'))
source=R/'tmp/game-math-part2-sources/3e10b1ffa61e81d4bc3ee19712b63d65.txt'
record=dict(status='future-partial-chapter-source-and-independent-math-preparation',atUtc=datetime.now(timezone.utc).isoformat(),target='game-math-velocity-derivatives',source=dict(pageId='3e10b1ffa61e81d4bc3ee19712b63d65',path=source.relative_to(R).as_posix(),sha256=hashlib.sha256(source.read_bytes()).hexdigest(),wholeFetchedTextDirectlyRead=False,directlyReadInclusiveLineRanges=[[1,703]],completeSourceSections=['11.1','11.2','11.3','11.4.1–11.4.7','11.5'],followingSection='11.6introduction only; rest pending',cachedFetchDate='2026-09-20; freshnative retrieval/verification before production remains pending'),checks=checks,newProjectCreated=False,ttsStarted=False,officialDuplicateDecision='pending',primaryReference=dict(url='https://www.nist.gov/pml/special-publication-811/nist-guide-si-appendix-b-conversion-factors',supports='Internationalfoot=.3048m exactly; distinguish older U.S.survey foot. Not used for outdatedSIbaseunit definitions.'),clarifications=['Use a declaredcontinuousclassicalmodel; no claim thatspacetimequantization is proven or required.','Newton/Leibnizcalculus history is17thcentury; no15thcenturyclaim.','Masskg and weightN are distinct even underconstantgravity; J=N*m, notN*m^2.','Use same start/end times when comparingaveragevelocities; source tortoisefinish t6, not inconsistentt7.','General derivativedefinition is a two-sided limit where it exists; positiveforwardstep demonstration is not a proof for corners.','Slopeangle depends on graphaxis scales; units of dx/dt must remain explicit.','The finiteclimberdata are steps; smoothfittedsurvivalcurve is a separatemodel, with decreasingdropouts meaning Sderivative approaches0 frombelow.','Source happiness/finance sketches are illustrative, not measured empiricalfinancial advice or selectedinvestmentproducts.','Taylor equality/convergence is not guaranteed for everyfunction; source sin/cos/exp are appropriateexamples.','The source trainpositionaddition assumes straighttrack/nonrotating alignedaxes; a rotatingframe has additionalterms.'])
(B/'preflight/velocity-derivatives-source-preparation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(len(checks),'independentchecks passed; remainingchaptersections and futureproduction remain pending.')
