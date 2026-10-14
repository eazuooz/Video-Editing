"""CPU-only future preparation: independent force/friction worked checks.

No project creation, footage selection, TTS authorization or listening/pixel pass.
"""
from pathlib import Path
import math,json,hashlib,datetime
R=Path(__file__).resolve().parents[4];B=R/'production/batches/game-math-part2-full-series'
checks=[]
def check(name,passed,detail):
 assert passed,name
 checks.append(dict(name=name,passed=bool(passed),detail=detail))
# Constant positive mass, declared inertial frame; net force, not one force.
forces=[(4.,0.),(-1.,2.),(0.,-2.)];net=tuple(sum(v[i] for v in forces) for i in range(2));m=2.
check('net force then divide by mass',net==(3.,0.) and tuple(v/m for v in net)==(1.5,0.),'Three forces sum first; constant mass2kg gives acceleration(1.5,0)m/s². A balanced vertical pair contributes zero net vertical force.')
pair=(10.,-10.);aA=pair[0]/2;aB=pair[1]/4
check('third-law pair belongs to distinct bodies',pair[0]+pair[1]==0 and aA==5 and aB==-2.5,'Equal opposite10N act on different2kg/4kg bodies. Separate free-body diagrams give unequal accelerations; cancellation belongs to the combined system only.')
g=9.8;frameA=-g;physicalA=-g;relativeA=physicalA-frameA;mass=2
check('accelerating frame and normal force',relativeA==0 and -mass*g-mass*frameA==0 and mass*(g+2)==23.6,'Freely falling elevator has zero relative sandwich acceleration after fictitious -mA. Upward2m/s² elevator requires23.6N support for2kg. No claim every stationary coordinate frame is inertial.')
N=10.;mus=.5;muk=.3;requested=2.;static=-requested
check('static force adjusts up to a maximum',abs(static)<=mus*N and requested+static==0 and mus*N==5 and (6-muk*N)/2==1.5,'N10,μs.5: maximum5N but actual static friction2N against a2N push. A6N push exceeds capacity; illustrativeμk.3 gives1.5m/s² for2kg while sliding.')
theta=math.radians(30);critical=math.degrees(math.atan(mus));slip=g*(math.sin(theta)-muk*math.cos(theta))
check('incline threshold and mass cancellation',abs(critical-26.56505117707799)<1e-12 and math.tan(theta)>mus and slip>0 and all((mass*g*math.sin(theta)>mus*mass*g*math.cos(theta)) for mass in [1,10]),dict(criticalAngleDegrees=critical,slidingAcceleration=slip,assumptions='Fixed planar contact, no other forces or normal relative acceleration. N=mgcosθ only under these conditions; relative tangent velocity sets kinetic direction.'))
Ghistoric=6.673e-11;Mehistoric=5.98e24;Rehistoric=6.371e6;ga=Ghistoric*Mehistoric/Rehistoric**2
check('historic spherical gravity and inverse square',9.82<ga<9.84 and Ghistoric*Mehistoric/(2*Rehistoric)**2==ga/4,dict(historicApproximateAcceleration=ga,precision='Reproduce rounded book constants in a spherical/point-mass model. This does not establish actual equatorial gravity or a current CODATA G.'))
h=2.;T=.4;acc=-2*h/T**2;v0=2*h/T
check('designed jump height and rise time',abs(acc+25)<1e-12 and abs(v0-10)<1e-12 and abs(v0+acc*T)<1e-12 and abs(v0*T+.5*acc*T*T-h)<1e-12,'2m apex after.4s: a=-25m/s², v0=10m/s. One constant-acceleration ascent; alternate falling acceleration is a different model, not a claim about a named game.')
v=2.;deceleration=3.;stop=v/deceleration;distance=v*v/(2*deceleration)
check('kinetic friction stopping event',abs(stop-2/3)<1e-12 and abs(distance-2/3)<1e-12 and v-deceleration*1<0 and max(0.,v-deceleration*1)==0,'Pure sliding resistance cannot drive a resting block backwards. A1s naive velocity update overshoots; resolve stopping/contact/static conditions. No general clamp for systems with other accelerating forces.')
check('contact pressure direction',10/.5==2*(10/1),'Same10N over half the apparent area doubles average pressure. Area independence is an ideal Coulomb model, not universal material behavior.')
files=['3e10b1ffa61e810d85dcd6f6e2c81129.txt','3e10b1ffa61e813b8611ee04a6c6c3ea.txt']
records=[dict(path='tmp/game-math-part2-sources/'+f,sha256=hashlib.sha256((R/'tmp/game-math-part2-sources'/f).read_bytes()).hexdigest()) for f in files]
value=dict(status='future-cpu-numerical-preparation-not-production-approval',atUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),target='game-math-forces-friction',checks=checks,sourceRecords=records,directSourceRead=dict(cachedChapter121='all text including corrections and notes',cachedChapter122='all cached text through closing content/page directly read, including gravity, friction, springs and control-system corrections',freshNativeSource='pending',sourceFigures='not directly viewed'),clarifications=['Net force and constant positive mass/inertial-frame assumptions are explicit.','Action/reaction forces act on different bodies, not two cancellable arrows in one body diagram.','A rigid body can have relative centripetal acceleration while internal force pairs cancel in center-of-mass translation.','Coulomb coefficients depend on material pair and conditions. The contradictory wet-concrete/rubber table row is not selected as a production constant.','A conveyor can accelerate a block via friction: kinetic friction opposes relative contact velocity, not necessarily world velocity.','N=mg or mgcosθ is conditional; support acceleration and other normal forces change N.','Historical9.796 equatorial model and rounded G are not exact Earth measurements.','Jump design examples describe declared toy equations, not proprietary named-game code.','Avoid rigid-body variable-mass and fully relativistic extrapolations of F=ma.'],production=dict(projectCreated=False,footageSelected=False,ttsStarted=False,duplicateReview='pending after current private delivery'),preserveCurrentProduction=True)
(B/'preflight/forces-friction-source-preparation.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(dict(passed=True,checks=len(checks),productionStarted=False)))
