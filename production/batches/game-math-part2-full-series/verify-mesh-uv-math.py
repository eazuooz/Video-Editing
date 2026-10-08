"""Independent numeric and source-preservation audit before lecture synthesis."""
from pathlib import Path
import json,hashlib,datetime,math
import numpy as np
R=Path(__file__).resolve().parents[3];B=Path(__file__).parent;slugs=['game-math-mesh-uv','game-math-normal-transform-uv'];checks=[]
def read(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check(name,evidence):checks.append(dict(name=name,passed=True,evidence=evidence))
def close(a,b):assert np.allclose(a,b,rtol=1e-10,atol=1e-10),(a,b)
assert 6*32==192 and 4*32+6*2==140 and 32+6*2==44
check('whole-quad-versus-local-record-memory',dict(array=192,indexedQuad=140,sixUseLocalRecord=44,vertexBytes=32,indexBytes=2))
triangles=[(0,1,2),(0,2,3)];edges={}
for i,t in enumerate(triangles):
 for a,b in zip(t,t[1:]+t[:1]):edges.setdefault(tuple(sorted((a,b))),[]).append(i)
assert edges[(0,2)]==[0,1] and sum(len(x)==1 for x in edges.values())==4
check('two-triangles-shared-diagonal-and-open-boundary',dict(triangles=triangles,sharedEdge=[0,2],boundaryEdges=4))
p=np.array([[0.,0.,0.],[2.,0.,0.],[2.,1.,0.]])
cross=lambda t:np.cross(t[1]-t[0],t[2]-t[0])
close(cross(p),[0,0,2]);close(cross(p[[1,2,0]]),cross(p));close(cross(p[[0,2,1]]),-cross(p));close(np.cross(p[1]-p[0],p[2]-p[1]),cross(p))
check('cyclic-winding-preserves-and-swap-reverses',dict(cross=[0,0,2],coordinateContract='Pure independent3D coordinates; front-face setting explicitly declared in narration.'))
avg=np.array([.5,.5]);close(np.linalg.norm(avg),math.sqrt(.5));close(avg/np.linalg.norm(avg),np.ones(2)/math.sqrt(2))
check('interpolated-direction-requires-renormalization',dict(blended=avg.tolist(),length=float(np.linalg.norm(avg)),unit=(avg/np.linalg.norm(avg)).tolist()))
total=np.ones(3);close(total/np.linalg.norm(total),np.ones(3)/math.sqrt(3));assert 6*4==24
check('three-unit-face-sum-and-detached-cube',dict(sum=total.tolist(),unit=(total/np.linalg.norm(total)).tolist(),cubeLocations=8,detachedRecords=24))
close(np.array([0,1,0])+np.array([0,-1,0]),[0,0,0]);close(np.cross([1,0,0],[2,0,0]),[0,0,0])
check('opposing-normals-and-degenerate-face-zero',dict(normalizationAllowed=False,required='Separate explicit policy before normalization.'))
v=np.array([1.,2.,1.]);close(np.linalg.norm(v),math.sqrt(6));close(v/np.linalg.norm(v),[1/math.sqrt(6),2/math.sqrt(6),1/math.sqrt(6)])
assert 30+60==90 and 45+45==90
check('triangle-count-bias-versus-angle-sum',dict(equalVoteSum=v.tolist(),unit=(v/np.linalg.norm(v)).tolist(),preservedQuadCornerDegrees=90))
t=np.array([1.,-1.]);n=np.array([1.,1.]);M=np.diag([2.,1.]);tp=M@t;wrong=M@n;correct=np.linalg.inv(M).T@n
close(n@t,0);close(tp,[2,-1]);close(wrong,[2,1]);close(tp@wrong,3);close(tp@(wrong/np.linalg.norm(wrong)),3/math.sqrt(5));close(correct,[.5,1]);close(tp@correct,0)
check('inverse-transpose-keeps-transformed-perpendicularity',dict(tangent=tp.tolist(),naive=wrong.tolist(),naiveDot=3,normalizedNaiveDot=3/math.sqrt(5),correct=correct.tolist(),unit=(correct/np.linalg.norm(correct)).tolist(),correctDot=0))
shear=np.array([[1.,.6,0],[0,2,0],[0,0,1]]);tn=np.array([1.,-1,0]);nn=np.array([1.,1,0]);close((shear@tn)@(np.linalg.inv(shear).T@nn),0)
rotation=np.array([[0.,-1],[1,0]]);close(np.linalg.inv(rotation).T,rotation);close(np.linalg.det(np.diag([0,1])),0)
check('shear-rotation-and-singular-boundary',dict(shearDot=0,rotationInverseTransposeEqualsOriginal=True,singularHasInverse=False))
repeat=lambda u:u-math.floor(u)
close([repeat(1.25),repeat(-.75)],[.25,.25]);assert math.floor(-.75)==-1 and math.trunc(-.75)==0
close([min(1,max(0,u)) for u in [-.75,1.25]],[0,1])
check('negative-repeat-and-clamp',dict(repeated=[.25,.25],clamped=[0,1],floorNegative=-1,truncatedNegative=0))
close([2*.25,2*.75],[.5,1.5]);close([repeat(2*.25),repeat(2*.75)],[.5,.5]);close([repeat(0),repeat(2)],[0,0])
check('interpolation-before-lookup-retains-two-tiles',dict(correctInterior=[.5,1.5],correctLookups=[.5,.5],earlyWrappedEndpoints=[0,0],wrongInterpolatedInterior=[0,0]))
lessons=[read(B/'lessons'/f'{s}.json') for s in slugs];old=read(R/'shared/output/game-math-mesh-uv/before-conceptual-episode-refinement/game-math-mesh-uv.json')
newTexts={lang:set(x for d in lessons for s in d['scenes'] for x in s[lang]) for lang in ['ko','en']}
clarifications=[]
correction_file=R/'projects/game-math-mesh-uv/production/narration-number-correction.json'
if correction_file.exists():
 correction=read(correction_file)
 assert sha(R/correction['preservedLesson'])==correction['preservedLessonSha256']
 for c in correction.get('paragraphClarifications',[]):
  assert c['language']=='ko' and not c['removedUsefulClaim']
  if c['scene']=='04':
   assert c['lineIndex']==5 and c['meaningReview']=='passed-independent-32-plus-6-times-2-equals44-versus-whole-quad140'
   assert c['valuesPreserved']==[32,6,2,12,44,140]
  else:
   assert c['scene']=='13' and c['lineIndex']==3 and c['valuesPreserved']==[]
   assert c['meaningReview']=='passed-distinct-top-normal-and-side-normal-records-and-matching-indices'
   assert c['before']=='위쪽 레코드에는 위쪽 법선을, 옆쪽 레코드에는 옆쪽 법선을 저장합니다. 인덱스도 해당 레코드를 가리키게 바꿉니다.'
   assert c['after']=='위쪽 면의 레코드에는 위를 향한 법선을 저장합니다. 옆면의 레코드에는 옆을 향한 법선을 저장합니다. 인덱스도 각 면의 레코드를 가리키게 바꿉니다.'
  current=next(s for s in lessons[0]['scenes'] if s['id']==c['scene'])['ko'][c['lineIndex']]
  assert current==c['after'] and current in newTexts['ko']
  assert any(c['before'] in s['ko'] for s in old['scenes'])
  clarifications.append(c)
for lang in ['ko','en']:
 allowed={c['before'] for c in clarifications if c['language']==lang}
 assert all(x in newTexts[lang] or x in allowed for s in old['scenes'][1:] for x in s[lang]),f'Original useful{lang}paragraph missing'
check('full-original-draft-retained-across-conceptual-boundary',dict(koAndEnOriginalBodyAndConclusionPreserved=True,explicitPreservedNumericClarifications=clarifications,overview='New independent overview for each episode.',boundary='Complete normal construction and edge/weighting algorithm before inverse-transpose andUV.'))
intervals={}
for d in lessons:
 for s in d['scenes']:
  if s['kind']!='actual':continue
  for seg in s['sourceSegments']:
   a=seg['in'];b=a+seg['maxSeconds'];intervals.setdefault(s['sourceId'],[]).append((a,b,d['slug'],s['id']))
for source,items in intervals.items():
 ordered=sorted(items)
 assert all(a[1]<=b[0]+1e-7 for a,b in zip(ordered,ordered[1:])),(source,ordered)
previous=read(R/'projects/game-math-rendering-light/production/timeline.json')
for s in previous['scenes']:
 for c in s.get('cuts',[]):
  if 'wzQLP0Z3zII' not in c['source']:continue
  for a,b,_,_ in intervals['wzQLP0Z3zII']:assert b<=c['sourceIn']+1e-7 or a>=c['sourceOut']-1e-7,(a,b,c)
check('real-footage-unique-and-old-bigwalk-intervals-preserved',dict(selectedIntervals={k:[list(x) for x in v] for k,v in intervals.items()},speed=1,sourceAudio=False,repeats=False))
out=dict(status='independent-numerical-source-preservation-and-interval-checks-passed',atUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),checks=checks,passed=len(checks),lessonFingerprints={d['slug']:sha(B/'lessons'/f'{d["slug"]}.json') for d in lessons},rendererSha256=sha(R/'manim/projects/game-math-part2-full-series/mesh_uv.py'),limits='Rendered spatial/text correctness,measured narration alignment,full listening and public rights remain separate pending checks.')
for slug in slugs:
 p=(R/f'projects/{slug}/production/math-review.json') if slug==slugs[0] else B/'preflight/normal-transform-uv-math-review.json';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(dict(passed=len(checks),scope=slugs),ensure_ascii=False))
