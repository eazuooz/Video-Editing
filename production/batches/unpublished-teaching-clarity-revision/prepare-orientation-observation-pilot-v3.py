"""Preserve held automatic tracks and author directly inspected image-point anchors."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json
ROOT=Path(__file__).resolve().parents[3]
B=ROOT/'production/batches/unpublished-teaching-clarity-revision'
R=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf8')
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
    return h.hexdigest()
def rel(p):return p.relative_to(ROOT).as_posix()
now=datetime.now(timezone.utc).isoformat()
ex=read(R/'observation-pilot-execution-v2.json')
assert ex['workerExitCode']==ex['wholeDecodeExitCode']==ex['extractionExitCode']==0
assert len(ex['samples'])==25 and len(ex['boards'])==5
assert all(sha(ROOT/x['path'])==x['sha256'] for x in ex['samples']+ex['boards'])
baseline=read(R/'baseline-preservation-v1.json')
assert all(sha(ROOT/x['path'])==x['sha256'] for x in baseline['protectedFiles'])
review=R/'observation-pilot-direct-review-v2.json'
anchors=R/'observation-point-keyframes-v3.json'
script=B/'render-orientation-observation-pilot-v3.py'
assert not any(p.exists() for p in (review,anchors,script,R/'observation-pilot-execution-v3.json'))
write(review,dict(observedAt=now,actualSessionId=73579,actualOuterExitCode=0,outerExitObservedChunk='fae4cc',
    workerGenerationAbsentObservedChunk='d34109',all25ListedEncodedSamplesDirectlyRead=True,
    all5BoardsDirectlyRead=True,allHashesMatched=True,baseline38Unchanged=True,hiddenFrames=40,
    observations=['f90 merges a horizontal background edge and marks empty space above the visible torso.',
        'f135 and150 hide the guide although the torso is visible.',
        'Later partial silhouette groups are inconsistent; automatic centroid is unsuitable for an uninterrupted lesson guide.'],
    prototypeApproved=False,allMovingPixelsApproved=False,sourceAdoptionApproved=False,
    finalCueApproved=False,timedNarrationApproved=False,samples=ex['samples'],boards=ex['boards']))
ex.update(actualSessionId=73579,actualOuterExitCode=0,outerExitObservedChunk='fae4cc',
    status='completed-direct-reviewed-held-for-tracking-repair',directReview=rel(review))
write(R/'observation-pilot-execution-v2.json',ex)
# An illustrative point on the visible torso/back block, not a physical centroid,
# anatomical landmark, optical-flow solution or the game's transform origin.
xy=[(956,385),(914,395),(903,414),(889,455),(895,523),(888,535),(885,567),
    (887,604),(889,638),(894,660),(900,654),(902,643),(920,627),(930,650),
    (930,660),(950,645),(940,630),(940,603),(930,571),(891,576),(840,569),
    (810,557),(818,550),(820,545),(821,549)]
keyframes=[dict(frame=s['frame'],sourceFrame=50400+s['frame'],sourcePts=(50400+s['frame'])*256,
    x=p[0],y=p[1],inspectedImage=s['path'],inspectedImageSha256=s['sha256'],directlyRead=True,
    observation='Visible torso/back block image point; approximate screen location only') for s,p in zip(ex['samples'],xy)]
write(anchors,dict(preparedAt=now,sourceFirstNativeFrame=50400,sourceEndExclusiveNativeFrame=50760,
    authoredMethod='25 directly read image anchors, linearly interpolated between anchors. Inspect moving output before adoption.',
    keyframes=keyframes,allAnchorImagesDirectlyRead=True,allIntermediateFramesDirectlyRead=False,
    physicalCentroid=False,gameWorldMeasurement=False,rigidBodyRotationMeasurement=False,
    sourceAdoptionApproved=False,allMovingPixelsApproved=False,finalCueApproved=False))
s=(B/'render-orientation-observation-pilot-v2.py').read_text('utf8')
s=s.replace('observation-pilot-v2','observation-pilot-v3').replace('observation-pilot-execution-v2','observation-pilot-execution-v3')
s=s.replace('import numpy as np\nfrom scipy import ndimage\n','')
start=s.index('def drawing(');end=s.index('\ndef main():',start)
s=s[:start]+'''def drawing(im,frame,t):
    layer=Image.new('RGBA',im.size);d=ImageDraw.Draw(layer)
    label(d,(64,28),'Superflight · NCR Gameplay · 화면 관찰','#ffffff',22)
    label(d,(64,95),'화면 위치와 몸의 자세를 구분하세요',GOLD,34)
    if frame>=20:
        arrow(d,(1720,370),(1720,195),GOLD)
        label(d,(1580,390),'화면의 위',GOLD)
    x,y=t['screenPoint']
    if frame>=35:
        d.ellipse((x-15,y-15,x+15,y+15),outline='#10191c',width=6)
        d.ellipse((x-12,y-12,x+12,y+12),outline=TEAL,width=4)
        d.ellipse((x-3,y-3,x+3,y+3),fill=TEAL)
        label(d,(64,178),'청록: 몸통의 화면 관찰점 p',TEAL)
    if frame>=100:
        arrow(d,t['previousScreenPoint'],t['screenPoint'],RED,5)
        label(d,(64,242),'빨강: 0.5초 동안의 화면 위치 변화',RED)
        label(d,(64,310),'Δp = p(t) − p(t − 0.5s)',RED,26)
    label(d,(64,810),'화면 위치에는 카메라의 움직임도 함께 나타납니다.','#ffffff',27)
    label(d,(64,855),'몸의 3D 자세는 다음 모형에서 세 축으로 설명합니다.','#ffffff',25)
    assert layer.getbbox()[3]<=910
    return Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB')

def point_at(frame,keyframes):
    for a,b in zip(keyframes,keyframes[1:]):
        if a['frame']<=frame<=b['frame']:
            u=(frame-a['frame'])/(b['frame']-a['frame'])
            return [round(a[k]+u*(b[k]-a[k]),3) for k in ('x','y')]
    raise ValueError(frame)
''' +s[end:]
s=s.replace("previous=np.array([963.,364.])/3;axisPrevious=np.array([1.,0.]);tracks=[]", "keyframes=read(R/'observation-point-keyframes-v3.json')['keyframes'];tracks=[]\n    assert all(sha(ROOT/a['inspectedImage'])==a['inspectedImageSha256'] for a in keyframes)")
start=s.index('                pix=np.asarray(');end=s.index('                tracks.append(t);',start)
s=s[:start]+'''                point=point_at(frame,keyframes)
                previous=point_at(max(0,frame-30),keyframes)
                t=dict(frame=frame,sourceFrame=50400+frame,sourcePts=(50400+frame)*256,screenOnly=True,
                    visible=True,screenPoint=point,previousScreenPoint=previous,
                    screenDisplacementPixels=[round(point[k]-previous[k],3) for k in range(2)],
                    physicalCentroid=False,gameWorldAxis=False)
''' +s[end:]
s=s.replace('observation-silhouette-track-v2','observation-point-track-v3')
s=s.replace('Brown/dark silhouette with local closing, proximity selection and image centroid. Red vector is centroid(t)-centroid(t-0.5s), in image pixels including camera effects. Invalid observations are hidden.', 'Manually inspected torso/back-block image observation point with linear interpolation. Red vector is p(t)-p(t-0.5s); it includes camera projection effects. This is not a physical centroid or world-space vector.')
s=s.replace("f\"f{r['frame']} source{t['sourceFrame']} visible{t['visible']} ratio{t['anisotropy']:.1f}\"", "f\"f{r['frame']} source{t['sourceFrame']} authored image observation\"")
s=s.replace('Observe a segmented visible silhouette. The centroid and principal line describe\nimage pixels only, and are neither anatomical landmarks nor game-world axes.', 'Observe a manually inspected torso image point and its screen displacement.\nThese describe image coordinates only, not physical centroids or game-world axes.')
assert 'np.' not in s and 'ndimage' not in s and 'anisotropy' not in s
script.write_text(s,'utf8')
cp=read(R/'latest-checkpoint.json');cp.update(observedAt=now,
    stage='manual-image-observation-v3-prepared-after-held-v2',
    observationPilotV2=rel(review),observationPointKeyframes=rel(anchors),
    next='Run one CPU2/GPU0 silent v3 pilot, directly inspect the moving image-point guide and encoded samples. Continue normal-speed source comparisons; do not start dependent voice before source adoption.')
write(R/'latest-checkpoint.json',cp)
q=read(B/'queue.json');q['updatedAt']=now;q['execution'].update(stage=cp['stage'],ownedJob=None,next=cp['next'])
q['execution']['completedOwnedJobs'].append(dict(script=rel(B/'render-orientation-observation-pilot-v2.py'),
    sessionId=73579,pid=ex['pid'],createTime=ex['createTime'],actualOuterExitCode=0,
    outerExitObservedChunk='fae4cc',directReview=rel(review),approved=False))
write(B/'queue.json',q)
print(json.dumps(dict(v2ActualExit=0,v2Approved=False,manualAnchors=25,baselineUnchanged=38,v3PreparedOnly=True)))
