"""Independent CPU preparation for chapter12.3; no production or GPU approval."""
from pathlib import Path
import datetime, hashlib, json, math
R=Path(__file__).resolve().parents[4]; checks=[]
def add(name,condition,detail):
 assert condition,name
 checks.append(dict(name=name,passed=True,detail=detail))
close=lambda a,b:math.isclose(a,b,abs_tol=1e-11)
m,v0,F,dt=2,4,10,.3
J=F*dt; p0=m*v0; p1=p0+J
add('Impulse changes momentum, including the initial state',close(J,3) and close(p1,11) and close(p1/m,5.5), 'm2kg,v0=4m/s,F10N,dt.3s: J3N·s, p8→11kg·m/s, v4→5.5m/s; p=J only if p0=0.')
add('Equal impulse does not require equal force or duration',close(10*.3,30*.1),'10N for.3s and30N for.1s each give3N·s; no claim of equal maximum force/contact damage.')
# Variable force F(t)=(2t,3), integrating from1 to3, not assuming t0=0.
t0,t1=1,3; Jv=(t1*t1-t0*t0,3*(t1-t0)); p=(5+Jv[0],-2+Jv[1])
add('Variable vector force with a nonzero time origin',Jv==(8,6) and p==(13,4),'F=(2t,3)N on[1,3], initial p=(5,-2): impulse(8,6),final p(13,4). Differentiate p(t) to recover force.')
mass=(1,3); x=(0,4); velocity=(3,1); M=sum(mass)
xc=sum(mi*xi for mi,xi in zip(mass,x))/M; P=sum(mi*vi for mi,vi in zip(mass,velocity)); vc=P/M
add('Mass weighting, not the geometric midpoint',close(xc,3) and close(vc,1.5),'Masses1kg at0m and3kg at4m: COM3m; velocities3 and1m/s: total p6 and COM velocity1.5m/s.')
d=.2; after=(velocity[0]+10*d/mass[0],velocity[1]-10*d/mass[1])
Pafter=sum(mi*vi for mi,vi in zip(mass,after))
add('Internal equal and opposite force preserves total momentum',close(Pafter,P) and not close(after[0],velocity[0]),'Internal ±10N for.2s moves momentum between two bodies: velocities5 and1/3m/s; total p stays6. An individual body does not conserve p.')
external=4; finalP=P+external*d
add('System boundary determines external impulse',close(finalP,6.8),'Adding external4N for.2s changes total momentum by.8N·s; internal-force cancellation alone is insufficient.')
relative=sum(mi*(vi-vc) for mi,vi in zip(mass,velocity)); K=sum(.5*mi*vi*vi for mi,vi in zip(mass,velocity)); Kcom=.5*M*vc*vc; Krel=sum(.5*mi*(vi-vc)**2 for mi,vi in zip(mass,velocity))
add('Center of mass and relative motion are separate',close(relative,0) and close(K,Kcom+Krel) and close(Krel,1.5),'p=MvCOM and mass-weighted relative momentum is0; kinetic energy6J=COM4.5J+relative1.5J. Conserving p does not imply conserving kinetic energy.')
# Column vectors, rigid90-degree planar rotation: rendered origin O=C-R*cLocal.
cLocal=(2,0); C=(5,3); rotated=(-cLocal[1],cLocal[0]); O=(C[0]-rotated[0],C[1]-rotated[1])
add('Physics COM to graphics origin after rotation',O==(5,1) and (O[0]+rotated[0],O[1]+rotated[1])==C,'Local COM(2,0),world COM(5,3),90° rotation: graphics origin(5,1). Subtract the rotated offset, not the unrotated offset.')
gravity=(10,20); weights=tuple(mi*gi for mi,gi in zip(mass,gravity)); cg=sum(w*xi for w,xi in zip(weights,x))/sum(weights)
add('COM and center of gravity coincide only for uniform gravity',close(cg,24/7) and not close(cg,xc),'Toy nonuniform field g=(10,20): center of gravity24/7m differs from COM3m; uniform g cancels out of the weighting.')
source=R/'tmp/game-math-part2-sources/3e10b1ffa61e816b9141de8f5b289c86.txt'
record=dict(status='future-cpu-numerical-preparation-not-production-approval',atUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),target='game-math-momentum-collisions',preparedSection='12.3',checks=checks,source=dict(path=source.relative_to(R).as_posix(),sha256=hashlib.sha256(source.read_bytes()).hexdigest(),readScope='Full12.3,12.3.1,12.3.2 and closing correction callout; all cached text read; figures not inspected; fresh Notion comparison pending'),clarifications=['Use net external force for a defined closed system in an inertial frame; constant total mass for M*aCOM=Fext. Open mass-transfer systems require momentum flux, not an unqualified rocket F=m*a claim.','Impulse is a momentum change, not force itself; integration constants and initial momentum are retained.','Momentum conservation is independent of kinetic-energy conservation; collision response is the next section, not inferred from this chapter.','Free rigid motion decomposes into translation of COM plus rotation about COM, but need not rotate without tumbling or precession.','Model origin and physics COM are distinct; transform the local COM offset with the actual orientation before subtracting it.','The Earth/person/fan analogies and Earth-Moon orbit are simplified systems, not measured contemporary celestial dynamics.','No heavy-object throwing demonstration is requested or created; original figure observations remain pending.'],gpuWorkStarted=False,dependentNarrationWritten=False,formalDuplicateReview='not started')
out=R/'production/batches/game-math-part2-full-series/preflight/momentum-com-source-preparation.json'
out.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(dict(target=record['target'],checks=len(checks),passed=True)))
