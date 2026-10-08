"""Independently verify the current visibility/radiometry/reflection lecture."""
from pathlib import Path
import datetime,json,math,hashlib
import numpy as np
from production_control import require_current_authorization
R=Path(__file__).resolve().parents[3];slug='game-math-rendering-light';require_current_authorization(slug,'independent rendering calculations');P=R/f'projects/{slug}'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();checks=[]
def check(name,actual,expected,tolerance=1e-9):
 assert abs(actual-expected)<=tolerance,(name,actual,expected)
 checks.append({'name':name,'actual':float(actual),'expected':float(expected),'tolerance':tolerance,'passed':True})
for ordering in [(8,3),(3,8)]:
 nearest=math.inf
 for depth in ordering:
  if depth<nearest:nearest=depth
 check('Toy opaque minimum depth '+str(ordering),nearest,3)
check('4J over2s power',4/2,2);check('2W uniformly over2m2 irradiance',2/2,1)
check('Sphere solid angle',4*math.pi,12.566370614359172)
check('Hemisphere solid angle',2*math.pi,6.283185307179586)
n=np.array([0.,0.,1.]);wi=np.array([-math.sin(math.pi/3),0.,math.cos(math.pi/3)])
check('Incident outward-vector unit norm',np.linalg.norm(wi),1)
check('Outward-normal cosine60',n@wi,.5)
check('Opposite actual incident travel has opposite dot',n@(-wi),-.5)
theta=(np.arange(20000)+.5)*(math.pi/2/20000)
integral=float(np.sum(np.cos(theta)*np.sin(theta))*(math.pi/2/20000)*2*math.pi)
check('Independent cosine hemisphere quadrature',integral,math.pi,1e-8)
rho=.6;E=10;Lo=rho*E/math.pi
check('Lambertian outgoing radiance',Lo,1.909859317102744)
check('Exitance integrates direction-independent Lo',Lo*integral,6,1e-8)
for count in [8,16]:
 # The worked uniform-direction midpoint example has constant Li=E/pi.
 cosines=(np.arange(count)+.5)/count;Li=E/math.pi;p=1/(2*math.pi)
 estimate=float(np.mean(Li*(rho/math.pi)*cosines/p))
 check('Normalized uniform-direction estimator N='+str(count),estimate,Lo)
check('Linear doubling sample count leaves same estimator',np.mean((np.arange(16)+.5)/16),np.mean((np.arange(8)+.5)/8))
lesson=read(Path(__file__).parent/f'lessons/{slug}.json');current=read(P/'production/narration-review.json')
assert current['status']=='passed-agent-script-and-ASR-difference-review' and len(current['scenes'])==22
required={'10.1.1','10.1.2','10.1.3','10.1.4'};assert set(lesson['coverage'])==required
script=read(P/'script/narration.ko.json');assert all(s['lines']==next(x['ko'] for x in lesson['scenes'] if x['id']==s['id']) for s in script['scenes'])
record={'passed':True,'reviewedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'method':'Independent numerical identities and hemisphere quadrature; complete raw current narration reviewed separately. Qualitative game pixels are never used as calibrated radiometric measurements.','checks':checks,'coverage':lesson['coverage'],'conventions':lesson['contract'],'inputs':[{'path':p.relative_to(R).as_posix(),'sha256':sha(p)} for p in [Path(__file__).parent/f'lessons/{slug}.json',P/'script/narration.ko.json',P/'script/narration.en.json',P/'production/narration-review.json',R/'manim/projects/game-math-part2-full-series/rendering_light.py']],'actualFootageScope':'Illustrative observed occlusion, surface contrast, lamp direction and fixture installation only. No inferred proprietary BRDF, rendering algorithm or light quantity.','humanListening':'pending','finalRenderedPixels':'pending-direct-review'}
(P/'production/math-verification.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(slug,len(checks),'independent rendering checks passed')
