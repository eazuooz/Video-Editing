"""Seal actual normal-rate muted playback endpoints of the repaired scene."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent;O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):
 t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
s=read(O/'07b-tracked-render-execution-v2.json');r=O/'07b-tracked-sampled-direct-review-v2.json';assert read(r)['all220EncodedSamplesDirectlyRead'];assert sha(ROOT/s['output'])==s['outputSha256']
p=O/'07b-tracked-normal-playback-direct-review-v2.json';assert not p.exists()
d=dict(reviewedAt=datetime.now(timezone.utc).isoformat(),tabId='106',url='http://127.0.0.1:9250/orientation-current07b-tracked-v2-review.html',sampledReview=r.relative_to(ROOT).as_posix(),sampledReviewSha256=sha(r),output=s['output'],outputSha256=s['outputSha256'],start=dict(time=.148178,duration=34.666667,paused=False,ended=False,rate=1,muted=True),end=dict(time=34.666667,duration=34.666667,paused=True,ended=True,rate=1,muted=True),action='Native video container Space; no seek or rate mutation.',endpointScreenshotObserved=True,endpointFinding='Two mathematical minus signs visible; projected wing upright in separate +90 degree z explanation.',normalRateEndpointPlaybackVerified=True,all220EncodedSamplesDirectlyRead=True,all44BoardsDirectlyRead=True,allBetweenFramesApproved=False,continuousHumanListeningApproved=False,finalCaptionsApproved=False,finalMixedApproved=False,finalRatioApproved=False,newImageGit=0)
save(p,d)
cp=read(O/'latest-checkpoint.json');cp.update(recordedAt=d['reviewedAt'],stage='07b-v2-sampled-and-normal-reviewed-10b-preparation',tracked07bNormalReview=p.relative_to(ROOT).as_posix(),activeOwnedWorkers=0,ownedJob=None,next='Prepare measured10b Space Engineers preview/rotation/placement/size comparison and related unique Superflight extension, then current34 distributed PCM mix and final QA. Preserve all completed source/voice/render reviews.');save(O/'latest-checkpoint.json',cp)
qp=B/'queue.json';before=qp.read_bytes();q=read(qp);q['currentOrientationReview'].update(stage=cp['stage'],tracked07bNormalReview=cp['tracked07bNormalReview'],activeOwnedWorkers=0,ownedJob=None,next=cp['next']);q['updatedAt']=d['reviewedAt'];assert before==qp.read_bytes();save(qp,q)
print(json.dumps(dict(normalRate=1,endedAt=34.666667,finalCaptions=False)))
