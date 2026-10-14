"""Seal all84 directly read native anchors; manual screen estimates are not world data."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,psutil
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sp=R/'extra-anchors-execution-v1.json';e=read(sp)
assert not (R/'extra-anchors-direct-review-v1.json').exists()
try:
    p=psutil.Process(e['pid']);assert abs(p.create_time()-e['createTime'])>=.01
except psutil.NoSuchProcess:pass
assert e['sampleCount']==84 and e['boardCount']==21 and e['freshSamples']==61 and e['reusedSamples']==23
assert all(x['exitCode']==0 for x in e['results'])
checked={}
for x in e['samples']+e['boards']:
    assert sha(ROOT/x['path'])==x['sha256'];checked[x['path']]=x['sha256']
e.update(actualOuterSession=61053,actualOuterExitCode=0,actualOuterCompletion='c47190',originalWorkerAlive=False,
         status='completed-directly-read-native-anchors-bounded')
sp.write_text(json.dumps(e,ensure_ascii=False,indent=2)+'\n','utf-8')
stamp=datetime.now(timezone.utc).isoformat()
proof=dict(schemaVersion=1,reviewedAt=stamp,execution=sp.name,executionSha256=sha(sp),
    actualSession=61053,actualOuterCompletion='c47190',actualExitCode=0,
    directlyReadNativeSamples=84,directlyReadBoards=21,fresh61=True,reused23=True,sha256RecheckedFiles=checked,
    findings={
      'Portal':'43-44.5 is a short held/lit-cube before state; view changes45-45.5, putdown/cube foreground46-48.5, portal placement49-51, pickup51.5-52.5, lit/redirection53-54, putdown54.5-55, changed view55.5-58. Keep cube markers hidden across uncertain pickup/drop/partial-crop intervals. Do not call the whole15seconds continuous aim motion or player portal traversal.',
      'PowerWash':'234-236 tool aims left-to-right while hut/fence reference remains almost stable;236.5-238.25 small camera shifts and vertical tool changes;238.5-241 tool aims down/left with partial nozzle occlusion239.25-240;241.25-243.25 aims left;243.25-244.0 similar short state;244.25-247 varied up/down/right/left aim. Blue hut follows observed screen position, never asserted mathematically fixed camera. No cleaning percentage increase or comfort result claimed.'},
    sampledNativePlanningApproved=True,allIntermediateFramesRead=False,
    exactFirstTransitionsMeasured=False,engineWorldMeasurementApproved=False,
    finalAnnotationPixelsApproved=False,narrationTimedApproval=False,finalCutAllocationApproved=False,
    finalRatioMeasured=False,localOnly=True)
(R/'extra-anchors-direct-review-v1.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf-8')
# Coordinates estimated by directly reading960x540 board cells after removing the40px header.
# Brackets indicate a visible role, not a physical centroid or a measured axis.
portal_points={1289:[480,265],1304:[480,265],1319:[480,265],1334:[480,265],1349:[500,265],1364:[480,265],
               1559:[480,282],1574:[480,280],1589:[480,265],1604:[480,265],1619:[480,265]}
pw_points=[
 [494,285],[494,248],[485,270],[345,270],[327,270],[348,272],[595,270],[630,268],[770,273],
 [827,276],[817,276],[807,276],[807,238],[807,215],[807,190],[807,190],[807,190],
 [807,293],[807,335],[807,355],[807,380],None,None,None,None,
 [533,430],[510,464],[505,483],[483,380],[444,358],[411,338],[411,338],[369,338],[352,338],
 [285,340],[281,340],[293,338],[293,338],[285,340],[285,340],[407,275],[409,286],[425,215],
 [431,275],[425,307],[425,365],[425,407],[425,433],[627,312],[694,345],[629,325],[560,337],[630,350]]
assert len(pw_points)==53
pw_hut=[]
for i in range(53):
    if i<=9: pt=[300,191]
    elif i==10:pt=[260,191]
    elif i==11:pt=[245,190]
    elif i==12:pt=[245,190]
    elif i<=16:pt=[255,230]
    elif i<=23:pt=[255,230]
    elif i<=33:pt=[255,230]
    else:pt=[279,230]
    pw_hut.append(pt)
rows=[]
for s in e['samples']:
    if s['id'].startswith('portal'):
        red=portal_points.get(s['frame']);blue=[800,225] if s['frame']<=1334 else None
        red_label='조작 대상: 큐브';blue_label='방의 단서: 벽'
    else:
        i=(s['frame']-14040)//15;red=pw_points[i];blue=pw_hut[i]
        red_label='조작 대상: 도구';blue_label='주변 단서: 작은 집'
    def cv(pt):return [round(v*4/3) for v in pt] if pt else None
    rows.append(dict(sourceId=s['id'],nativeFrame=s['frame'],pts=s['pts'],timeBase=s['timeBase'],
       samplePath=s['path'],sampleSha256=s['sha256'],redObservedSamplePoint=cv(red),blueObservedSamplePoint=cv(blue),
       redLabel=red_label,blueLabel=blue_label,coordinateSystem='1280x720 sampled source screen pixels estimated manually from960x540 board cell'))
plan=dict(schemaVersion=1,preparedAt=stamp,status='manual-role-anchor-plan-requires-encoded-pixel-review',
    sourceReview='extra-anchors-direct-review-v1.json',observations=rows,
    interpolation='Only within contiguous same-role visible ranges. Hide across missing anchors, camera/crop uncertainty or pickup/drop transition. Never interpolate a world trajectory.',
    pointPrecision='Approximate manual visible-screen role points. Bracket placement must be checked on encoded pixels before adoption.',
    reframe=dict(scaleTo1920=1.5,shiftY=-120,bottomSameFrameBlurPixels=120,captionCenter=[960,970]),
    physicalCentroidClaim=False,worldAxesClaim=False,narrationTimed=False,movingAnnotationApproved=False,finalCueApproval=False)
(R/'extra-annotation-observation-plan-v1.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n','utf-8')
cp_path=R/'latest-checkpoint.json';cp=read(cp_path)
cp.update(ownedJob=dict(status='completed',active=False,sessionId=61053,exitCode=0,completion='c47190'),
          activeOwnedWorkers=0,extraAnchorReview='extra-anchors-direct-review-v1.json',
          extraAnnotationPlan='extra-annotation-observation-plan-v1.json')
cp_path.write_text(json.dumps(cp,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(samples=84,boards=21,fresh=61,reused=23,hashChecks=len(checked),movingApproved=False)))
