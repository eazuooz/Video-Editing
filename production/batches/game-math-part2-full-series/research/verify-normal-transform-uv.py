from pathlib import Path
import sys,json,hashlib,datetime,math
import numpy as np
R=Path(__file__).resolve().parents[4];sys.path.insert(0,str(R/'manim/projects/game-math-part2-full-series'))
import normal_transform_uv as renderer
slug='game-math-normal-transform-uv';B=R/'production/batches/game-math-part2-full-series';P=R/f'projects/{slug}/production'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
checks=[]
def check(name,value,detail):
 assert value,name
 checks.append(dict(name=name,passed=bool(value),detail=detail))
t=np.array([1.,-1.]);n=np.array([1.,1.]);M=np.diag([2.,1.]);tt=M@t;wrong=M@n;correct=np.linalg.inv(M).T@n;unit=correct/np.linalg.norm(correct)
check('original and transformed dot products',np.dot(t,n)==0 and np.dot(tt,wrong)==3 and np.dot(tt,correct)==0,'t(1,-1),n(1,1); naive(2,1)dot3; inverse-transpose(.5,1)dot0')
check('normalization cannot fix wrong direction',abs(np.dot(tt,wrong/np.linalg.norm(wrong))-3/math.sqrt(5))<1e-12,'Wrong normalized dot3/sqrt5 remains nonzero')
check('correct unit normal',np.allclose(unit,[.4472135955,.8944271910],atol=1e-10) and abs(np.dot(tt,unit))<1e-12,'Normalize only after inverse transpose; matches both KO/EN worked values')
shear=np.array([[1.,.6],[0,1.]]);check('shear uses inverse transpose',abs(np.dot(shear@t,np.linalg.inv(shear).T@n))<1e-12,'Invertible column-vector proof also holds for shear')
check('negative repeat and truncation differ',-.75-math.floor(-.75)==.25 and -.75-math.trunc(-.75)==-.75,'floor(-.75)=-1, trunc(-.75)=0')
check('interpolate before addressing',.25*2==.5 and .75*2==1.5 and .5-math.floor(.5)==1.5-math.floor(1.5)==.5 and (2-math.floor(2))==0,'Endpoints0→2 survive interpolation; wrapping both endpoints first collapses the span')
check('UV crop',renderer.mapped_uv(0,0,'crop',1,'clamp')==(.25,.25) and renderer.mapped_uv(1,1,'crop',1,'clamp')==(.75,.75),'Central half width and height over unchanged plate')
check('rotation and horizontal flip',renderer.mapped_uv(0,0,'rotate',1,'clamp')==(0,1) and renderer.mapped_uv(1,1,'flip',1,'clamp')==(0,1),'UV corner cycling and1-u preserve geometry and winding')
check('clamp versus mirror',renderer.mapped_uv(.75,.75,'full',2,'clamp')==(1,1) and renderer.mapped_uv(.75,.75,'full',2,'mirror')==(.5,.5),'Clamp edge values and alternating mirrored tiles are distinct')
check('memory recap',4*32+6*2==140,'Four vertices and six indices; distinct from192B unindexed quad or44B local shared-record example')
d=read(B/f'lessons/{slug}.json');script=read(R/f'projects/{slug}/script/narration.ko.json');check('all independent scene contracts',len(d['scenes'])==13 and sum(s['kind']=='explanation' for s in d['scenes'])==8 and all(len(s['ko'])==len(s['en']) and (s['kind']=='actual' or len(s['beats'])==len(s['ko'])) for s in d['scenes']) and sum(len(s['ko']) for s in d['scenes'])==81 and [s['lines'] for s in script['scenes']]==[s['ko'] for s in d['scenes']],'13independent scenes,8explanation/5actual,81bilingual matched paragraphs')
record=dict(status='passed-independent-numerical-and-script-contract-review',reviewedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),lessonSha256=sha(B/f'lessons/{slug}.json'),rendererSha256=sha(Path(renderer.__file__)),checks=checks,finalRenderedPixels='pending after measured narration',humanListening='pending')
(P/'math-verification.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(P/'math-review.json').write_text(json.dumps(dict(status='reviewed-before-TTS',sourceSections=d['sourceSections'],contract=d['contract'],verification='projects/'+slug+'/production/math-verification.json',scriptSha256=sha(R/f'projects/{slug}/script/narration.ko.json'),sourcePreservation='production/batches/game-math-part2-full-series/preflight/mesh-uv-episode-refinement.json'),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(dict(checks=len(checks),passed=True)))
