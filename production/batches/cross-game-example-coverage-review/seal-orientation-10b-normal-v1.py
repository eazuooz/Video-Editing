"""Seal native normal-rate muted playback endpoints without continuous approval."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent;O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):
 t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
s=read(O/'10b-tracked-render-execution-v1.json');r=O/'10b-tracked-sampled-direct-review-v1.json';assert read(r)['all215EncodedSamplesDirectlyRead'];assert sha(ROOT/s['output'])==s['outputSha256']
p=O/'10b-tracked-normal-playback-direct-review-v1.json';assert not p.exists()
d=dict(reviewedAt=datetime.now(timezone.utc).isoformat(),tabId='106',url='http://127.0.0.1:9250/orientation-current10b-tracked-v1-review.html',sampledReview=r.relative_to(ROOT).as_posix(),sampledReviewSha256=sha(r),output=s['output'],outputSha256=s['outputSha256'],start=dict(time=.162367,duration=31.683333,paused=False,ended=False,rate=1,muted=True),end=dict(time=31.683333,duration=31.683333,paused=True,ended=True,rate=1,muted=True),action='Native video container Space; no seek or rate mutation.',endpointScreenshotObserved=True,endpointFinding='Extruded aircraft and mounting component are both upright after the illustrative turn; red/teal/blue reference arrows and separate-model caveat are visible above the fixed-caption region.',normalRateEndpointPlaybackVerified=True,all215EncodedSamplesDirectlyRead=True,all43BoardsDirectlyRead=True,allBetweenFramesApproved=False,continuousHumanListeningApproved=False,finalCaptionsApproved=False,finalMixedApproved=False,finalRatioApproved=False,newImageGit=0)
save(p,d)
cp=read(O/'latest-checkpoint.json');cp.update(recordedAt=d['reviewedAt'],stage='10b-sampled-and-normal-reviewed-extension-preparation',tracked10bNormalReview=p.relative_to(ROOT).as_posix(),activeOwnedWorkers=0,ownedJob=None,next='Prepare unique related Superflight66-74.1s extension and measured current34 timeline; preserve distributed24 baseline PCM, current10 added PCM and all completed reviews. Final mix/captions/QA/private/Git/schedule pending.');save(O/'latest-checkpoint.json',cp)
qp=B/'queue.json';before=qp.read_bytes();q=read(qp);q['currentOrientationReview'].update(stage=cp['stage'],tracked10bNormalReview=cp['tracked10bNormalReview'],activeOwnedWorkers=0,ownedJob=None,next=cp['next']);q['updatedAt']=d['reviewedAt'];assert before==qp.read_bytes();save(qp,q)
print(json.dumps(dict(normalRate=1,endedAt=31.683333,finalCaptions=False)))
