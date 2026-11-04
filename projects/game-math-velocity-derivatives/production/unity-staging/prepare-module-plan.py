"""Write CPU-only staging profiles; never starts or copies a Unity project."""
from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parent;ROOT=P.parents[3]
def dump(name,data): (P/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def vec(x=0,y=0,z=0):return {'x':x,'y':y,'z':z}
profiles=[
 {'id':'M24-polynomial','parameters':{'kind':0,'quadratic':-1,'linear':6,'constant':-1},'startTime':1,'endTime':3,'timeUnit':'min','positionUnit':'fur','worldOrigin':vec(-7,.5,0),'worldUnitsPerModelUnit':.65,'positionMin':3,'positionMax':9,'velocityMin':-1,'velocityMax':5,'showVelocityGraph':True,'showAccelerationGraph':False,'showVelocity':True,'englishTerm':'Derivative','koreanTerm':'미분','meaning':'한 순간의 변화율을 함수로 만들기'},
 {'id':'M24-chain-slope','parameters':{'kind':6,'chainSlope':.25,'pathSpeed':4},'startTime':0,'endTime':2,'timeUnit':'s','positionUnit':'m','worldOrigin':vec(-7,0,0),'worldUnitsPerModelUnit':.6,'positionMin':0,'positionMax':3,'velocityMin':0,'velocityMax':2,'graphY':True,'showVelocityGraph':True,'showAccelerationGraph':False,'englishTerm':'Chain rule','koreanTerm':'연쇄 법칙','meaning':'높이 변화 비율 × 경로를 가는 속도'},
 {'id':'M25-fall-left-rectangles','parameters':{'kind':2,'origin':vec(),'velocity':vec(),'acceleration':vec(0,32,0)},'startTime':0,'endTime':2.4,'timeUnit':'s','positionUnit':'ft','positiveYIsDown':True,'axisConvention':'낙하 예제: 아래쪽을 양수로 정의','worldOrigin':vec(-4,4,0),'worldUnitsPerModelUnit':.045,'velocityArrowScale':.02,'accelerationArrowScale':.02,'positionMin':0,'positionMax':100,'velocityMin':0,'velocityMax':80,'accelerationMin':0,'accelerationMax':40,'graphY':True,'showVelocityGraph':True,'showAccelerationGraph':True,'showAcceleration':True,'showRiemann':True,'riemannCount':6,'riemannDuration':2.4,'riemannAcceleration':32,'englishTerm':'Riemann sum','koreanTerm':'리만 합','meaning':'작은 시간 구간의 이동량을 더하기'},
 {'id':'M25-designed-jump','parameters':{'kind':3,'jumpHeight':2,'timeToApex':1,'horizontalSpeed':3},'startTime':0,'endTime':2,'timeUnit':'s','positionUnit':'m','worldOrigin':vec(-7,0,0),'worldUnitsPerModelUnit':.8,'positionMin':0,'positionMax':2.5,'velocityMin':-5,'velocityMax':5,'accelerationMin':-5,'accelerationMax':1,'graphY':True,'showVelocityGraph':True,'showAccelerationGraph':True,'showAcceleration':True,'englishTerm':'Projectile motion','koreanTerm':'포물체 운동','meaning':'정점 높이와 시간으로 점프 설계'},
 {'id':'M26-uniform-circle','parameters':{'kind':4,'radius':2,'omega':1,'axis':vec(0,0,1),'radiusDirection':vec(1,0,0)},'startTime':0,'endTime':6.283185307179586,'timeUnit':'s','positionUnit':'m','worldOrigin':vec(-4,2,0),'worldUnitsPerModelUnit':1,'positionMin':-2.5,'positionMax':2.5,'velocityMin':-2.5,'velocityMax':2.5,'accelerationMin':-2.5,'accelerationMax':2.5,'showVelocityGraph':True,'showAccelerationGraph':True,'showVelocity':True,'showAcceleration':True,'showRadius':True,'englishTerm':'Centripetal acceleration','koreanTerm':'구심가속도','meaning':'같은 빠르기로 돌아도 방향은 변한다'},
 {'id':'M26-piecewise-exercises','parameters':{'kind':5},'startTime':0,'endTime':9,'timeUnit':'s','positionUnit':'위치 단위','worldOrigin':vec(-4,2,0),'worldUnitsPerModelUnit':1.5,'positionMin':-2.5,'positionMax':1.5,'velocityMin':-3.5,'velocityMax':3.5,'accelerationMin':-11,'accelerationMax':11,'showVelocityGraph':True,'showAccelerationGraph':True,'showAcceleration':True,'accelerationArrowScale':.1,'englishTerm':'Piecewise motion','koreanTerm':'구간별 운동','meaning':'현재 구간을 고르고 위치·속도·가속도 계산'}
]
for p in profiles:
 p['beatId']='UNBOUND-'+p['id'];p['bindingStatus']='Needs actual narration/native-motion footage cue alignment; not a production cut.'
dump('model-profiles.json',{'profiles':profiles,'enumValues':{'Polynomial':0,'ConstantVelocity':1,'ConstantAcceleration':2,'DesignedJump':3,'Circle':4,'PiecewiseExercise':5,'ChainSlope':6},'timing':'startTime/endTime are mathematical model coordinates, not final edit seconds. No prescribed silent hold and no loop.'})
asset=json.loads((ROOT/'projects/game-math-shading-lights/planning/unity-plan.json').read_text(encoding='utf-8'))['assetRecords']
robot=next(x for x in asset if x.get('guid')=='c33a4d5ba9cee3d4fb7e7b6adc0084f1').copy()
robot['role']='Identifiable toy robot is moved as one tracked particle on the same lab stage. No walking rig, simulation of its motors, or commercial gameplay claim. Centre marker is the model point.'
robot['limits']='Prefab must be supplied by the parent isolated project with rights record and compatible materials; no silent primitive fallback. Full movement/appeal/occlusion/mobile QA remains pending.'
mapping=[]
for slug in ['game-math-velocity-derivatives','game-math-acceleration-integration','game-math-circular-motion']:
 d=json.loads((ROOT/'projects'/slug/'script/draft-narration.ko.json').read_text(encoding='utf-8'))
 for b in d['segments']:
  section=b['section'];candidate=[]
  if d['episodeId']=='M24':
   if section.startswith(('11.3','11.4.1','11.4.3')):candidate=['M24-polynomial']
   if section=='11.4.7':candidate=['M24-chain-slope']
  elif d['episodeId']=='M25':
   if section in ['11.5','11.6']:candidate=['M25-designed-jump','M25-fall-left-rectangles']
   if section=='11.7.1':candidate=['M25-fall-left-rectangles']
  elif d['episodeId']=='M26':
   if section=='11.8':candidate=['M26-uniform-circle']
   if any('연습 '+str(n)+':' in b['title'] for n in range(2,8)):candidate=['M26-piecewise-exercises']
  mapping.append({'beatId':b['id'],'title':b['title'],'candidateProfiles':candidate,'mappingKind':'capability suggestion, not finalized shot selection','existingScreenPlan':b['screenPlan'],'remaining':'Bind math/model ranges and labels to precise speech; use separately inspected independent game footage where it proves the claim. Additional formula/series/units diagrams authored separately.'})
dump('module-plan.json',{
 'status':'cpu-source-staging-only','editor':'6000.6.0f1','pipeline':'URP 17.6.0','targetOutput':{'width':1920,'height':1080,'fps':60},
 'scope':['M24 velocity/derivatives','M25 acceleration/integration','M26 circular motion/exercises'],
 'assetsConsulted':['shared/assets/unity-asset-library.json','docs/UNITY_ASSET_LIBRARY.md','projects/game-math-shading-lights/planning/unity-plan.json'],
 'assetRecords':[robot],
 'rightsSource':asset[0],
 'sharedAssetPaths':[robot['assetPath']],
 'sourceKind':'our implementation / analytic teaching model; never observed game internals',
 'rendererReason':'The same recognizable object visibly moves while exact analytic p/v/a, path, tangents, radius, velocity and acceleration arrows update; formulas are anchored to that movement.',
 'coordinateMapping':'Mathematics uses right-handed x/y/z. ToUnity maps (x,y,z) to (x,y,-z); compute all cross products in mathematical coordinates first. 1D falling scene additionally maps positive down only with explicit caption; do not reuse that convention for circle.',
 'design':{'stage':'black, same framing and subject','colors':{'position':'#e8cf83','velocity':'#73c7c2','acceleration':'#ef8585','secant':'#a4c6a0','body':'#f5f5f5'},'caption':'fixed 960,970; no scene UI below y870','definition':'3-line English/Korean/plain meaning card, compact term after introduction','values':'Directly evaluated from current mathematical state; graph axes/components and units explicit','animation':'External normalized cue required; no wall-clock Update, no modulo loops, no playback padding','gameSeparation':'Independent commercial-game footage must remain distinct and carry editorial annotations, never relabel this model as actual game footage'},
 'integration':{'liveProjectModificationAllowed':False,'newProjectCopied':False,'unityStarted':False,'savedScenes':[],'sourceReady':['MotionMathModel.cs','MotionTeachingStage.cs'],'nextSteps':['Root coordinates an isolated project after GPU availability and live work checks.','Supply verified prefab and compatible materials plus local dynamic Malgun Gothic font.','Copy sources only, compile, create one editable scene per assigned beat, save only after files exist.','Call stage.Build() then Evaluate(normalizedCue) from approved capture driver; capture exactly 1920x1080/60.','Inspect shader line colors, object material, graph/source labels, derivative joins, arrow occlusion, caption clearance and 375px output before reporting visual success.']},
 'qa':{'cpuCSharpCompilation':'compile-check.json','pureMathInvariants':'83 checks passed in C# harness','gpuRuntime':False,'shaderAppearance':False,'actualPrefabMovement':False,'fontReadability':False,'mobile':False,'humanReview':False},
 'capabilityMapping':mapping
})
print('Prepared',len(profiles),'profiles and',len(mapping),'draft beat capability records; zero renders or scene-save claims.')
