"""Independent numerical checks of the narrated camera examples, no render imports."""
import math,json,hashlib
from pathlib import Path
B=Path(__file__).parent;checks=[]
def close(name,value,expected,tol=1e-10):
 assert abs(value-expected)<=tol,(name,value,expected)
 checks.append({'claim':name,'calculated':value,'expected':expected,'tolerance':tol})
def exact(name,value,expected):
 assert value==expected,(name,value,expected)
 checks.append({'claim':name,'calculated':value,'expected':expected})
close('Full image aspect',1920/1080,16/9)
close('Square physical pixel',(16/9)*(1080/1920),1)
close('Stretched4:3 pixel',(16/9)*(3/4),4/3)
close('16:10 exact resolution',1152/720,16/10)
exact('1153 is not exact16:10',1153/720!=16/10,True)
exact('Left integer pixel interval',list(range(960))[-1],959)
exact('Right origin and exclusive end',[960,960+960],[960,1920])
close('Half FOV and ray half-width',3*math.tan(math.radians(90/2)),3)
close('Full width at z3',2*3*math.tan(math.pi/4),6)
close('Full width at z6',2*6*math.tan(math.pi/4),12)
close('Zoom at ninety degrees',1/math.tan(math.pi/4),1)
close('Zoom2 full FOV',math.degrees(2*math.atan(.5)),53.13010235415598)
close('Vertical FOV in16:9',math.degrees(2*math.atan(9/16)),58.71550708558255)
close('Physical axis scales preserve circles',(1920/2)*1,(1080/2)*(16/9))
close('Both FOV ninety stretches circle',((1920/2)*1)/((1080/2)*1),16/9)
close('Two-depth zoom magnifications near',2*(1/4)/(1/4),2)
close('Two-depth zoom magnifications far',2*(1/8)/(1/8),2)
close('Dolly near4→2',4/(4-2),2)
close('Dolly far8→6',8/(8-2),4/3)
exact('Forward z is not off-axis Euclidean distance',math.sqrt(3**2+4**2)!=4,True)
close('Sensor36,f18 gives ninety',math.degrees(2*math.atan(36/(2*18))),90)
close('Sensor36,f36 gives zoom2 FOV',math.degrees(2*math.atan(36/(2*36))),53.13010235415598)
close('Sensor18,f18 gives same narrower FOV',math.degrees(2*math.atan(18/(2*18))),53.13010235415598)
close('Orthographic horizontal pixels/unit',1920/8,240)
close('Orthographic vertical pixels/unit',1080/4.5,240)
close('Halved width pixels/unit',1920/4,480)
close('Halved height pixels/unit',1080/2.25,480)
close('Orthographic zoom8',2/8,.25)
close('Orthographic zoom4',2/4,.5)
close('Half-screen window aspect',960/1080,8/9)
close('Preserve vertical zoom after split',(16/9)/(8/9),2)
close('Split-screen circle axis scales',960/2*2,1080/2*(16/9))
close('Preserve horizontal zoom after split',1*(8/9),8/9)
close('Preserve horizontal FOV gives wider vertical FOV',math.degrees(2*math.atan(9/8)),96.7329213268596)
close('Orthographic sixty-degree panel width',math.cos(math.pi/3),.5)
close('Orthographic forward translation keeps scale',240/(1920/8),1)
def inside(x,y,z):return 1<=z<=11 and abs(x)<=z and abs(y)<=(9/16)*z
exact('Near rejection',inside(0,0,.5),False)
exact('Interior center',inside(0,0,6),True)
exact('Far rejection',inside(0,0,12),False)
exact('Distance alone insufficient',inside(7,0,6),False)
exact('Six-plane corner',inside(6,3.375,6),True)
exact('Top-plane rejection',inside(0,3.4,6),False)
# A crossing triangle retains a nonempty clipped polygon despite an outside vertex.
triangle=[(-1,.5,2),(1,.5,2),(0,-.6,.5)];intersections=[]
for a,b in [(triangle[0],triangle[2]),(triangle[1],triangle[2])]:
 t=(1-a[2])/(b[2]-a[2]);intersections.append(tuple(a[k]+t*(b[k]-a[k]) for k in range(3)))
exact('Crossing triangle retains two vertices and intersections',len([p for p in triangle if p[2]>=1])+len(intersections),4)
close('Near clipped edge x',intersections[0][0],-1/3)
exact('Both generated points on near plane',[p[2] for p in intersections],[1.,1.])
close('Near clipped edge y',intersections[0][1],-7/30)
lesson=B/'lessons/game-math-camera-frustum.json'
draft=json.loads(lesson.read_text(encoding='utf8'))
scenes={s['id']:s for s in draft['scenes']}
spoken=[]
for sid,index in [('10',3),('15',3),('20',3),('22',2)]:
 line=scenes[sid]['ko'][index]
 assert '오십삼 점 일 삼 도' in line,(sid,line)
 spoken.append({'scene':sid,'paragraph':index+1,'expectedNumber':round(math.degrees(2*math.atan(.5)),2),'reviewedKo':line,'independentEn':scenes[sid]['en'][index]})
assert '일이삼' not in ' '.join(line for s in draft['scenes'] for line in s['ko'])
assert '아크탄젠트로 반각을 구한 뒤, 그 각도를 두 배로' in scenes['10']['ko'][2]
assert '아크탄젠트로 반각을 구하고, 그 각도를 두 배로' in scenes['12']['ko'][1]
assert '아크탄젠트로 반각을 구한 뒤, 그 각도를 두 배로' in scenes['15']['ko'][1]
record={'status':'passed','checks':checks,'checkCount':len(checks),'lessonSha256':hashlib.sha256(lesson.read_bytes()).hexdigest(),
 'spokenNumeralAudit':{'status':'passed corrected script; audio retake verification pending','decimal53Point13':spoken,'doubleHalfAngleKo':[scenes[sid]['ko'][i] for sid,i in [('10',2),('12',1),('15',1)]],'orthographicUnitKo':scenes['18']['ko'][:2],'audioMeaningNumberReview':'pending six replacement takes'},
 'conventions':'Defined positive-z view,top-left output origin,width/height aspect; no numeric game implementation inferred.',
 'scope':'Independent ray geometry,physical pixels,zoom/dolly,frustum halfspaces,clipping and orthographic scale; not renderer self-tests.'}
(B/'preflight/camera-frustum-math.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Passed',len(checks),'independent camera calculations')
