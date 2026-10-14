"""Record actual CUA1x silent playback after the sampled tracking review."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent;O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):
 t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
s=read(O/'02a-tracked-render-execution-v1.json');r=O/'02a-tracked-sampled-direct-review-v1.json';assert read(r)['all100EncodedSamplesDirectlyRead']
assert sha(ROOT/s['output'])==s['outputSha256']
p=O/'02a-tracked-normal-playback-direct-review-v1.json';assert not p.exists()
d=dict(reviewedAt=datetime.now(timezone.utc).isoformat(),tabId='106',url='http://127.0.0.1:9250/orientation-current02a-tracked-v1-review.html',sampledReview=r.relative_to(ROOT).as_posix(),sampledReviewSha256=sha(r),output=s['output'],outputSha256=s['outputSha256'],start=dict(time=.038459,paused=False,ended=False,rate=1,muted=True,duration=17.216667),intermediateObservation=dict(time=12.040873,paused=False,ended=False,bodyPointVisible=True,screenGuidesAndLegendClear=True),end=dict(time=17.216667,paused=True,ended=True,rate=1,muted=True,duration=17.216667),action='Native video control Space; no seek or rate mutation.',normalRateEndpointPlaybackVerified=True,all100EncodedSamplesDirectlyRead=True,all20BoardsDirectlyRead=True,allBetweenFramesApproved=False,continuousHumanListeningApproved=False,finalCaptionsApproved=False,finalMixedApproved=False,finalRatioApproved=False,newImageGit=0)
save(p,d)
cp=read(O/'latest-checkpoint.json');cp.update(recordedAt=d['reviewedAt'],stage='02a-tracked-sampled-and-normal-reviewed-remaining-scene-allocation',tracked02aNormalReview=p.relative_to(ROOT).as_posix(),activeOwnedWorkers=0,ownedJob=None)
save(O/'latest-checkpoint.json',cp)
qp=B/'queue.json';before=qp.read_bytes();q=read(qp);q['currentOrientationReview'].update(stage=cp['stage'],tracked02aNormalReview=cp['tracked02aNormalReview'],activeOwnedWorkers=0,ownedJob=None);q['updatedAt']=d['reviewedAt'];assert before==qp.read_bytes();save(qp,q)
print(json.dumps(dict(normalRate=1,endedAt=17.216667,finalCaptions=False)))
