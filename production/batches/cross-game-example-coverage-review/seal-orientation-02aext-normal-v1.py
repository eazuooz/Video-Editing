"""Record actual1x muted endpoints; no narration/final-frame claim."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,os
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent;O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):
 t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
s=read(O/'02aext-tracked-render-execution-v1.json');r=O/'02aext-tracked-sampled-direct-review-v1.json';assert read(r)['all41DisplayedEncodedSamplesDirectlyRead'];assert sha(ROOT/s['output'])==s['outputSha256']
p=O/'02aext-tracked-normal-playback-direct-review-v1.json';assert not p.exists()
d=dict(reviewedAt=datetime.now(timezone.utc).isoformat(),tabId='106',url='http://127.0.0.1:9250/orientation-current02aext-tracked-v1-review.html',sampledReview=r.relative_to(ROOT).as_posix(),sampledReviewSha256=sha(r),output=s['output'],outputSha256=s['outputSha256'],start=dict(time=.19605,duration=8.1,paused=False,ended=False,rate=1,muted=True),end=dict(time=8.1,duration=8.1,paused=True,ended=True,rate=1,muted=True),action='Native video container5 Space; no seek or rate mutation.',endpointScreenshotObserved=True,endpointFinding='Character continues flying beyond the structure; torso observation marker and screen displacement remain on the visible body, game score1119 and top legends remain readable.',normalRateEndpointPlaybackVerified=True,all41DisplayedEncodedSamplesDirectlyRead=True,all9BoardsDirectlyRead=True,allBetweenFramesApproved=False,continuousHumanListeningApproved=False,finalCaptionsApproved=False,finalMixedApproved=False,finalRatioApproved=False,newImageGit=0)
save(p,d)
cp=read(O/'latest-checkpoint.json');cp.update(recordedAt=d['reviewedAt'],stage='02aext-sampled-and-normal-reviewed-current34-timing-preparation',tracked02aextNormalReview=p.relative_to(ROOT).as_posix(),activeOwnedWorkers=0,ownedJob=None,next='Prepare measured current34 distributed PCM placements and whole/independent mixed ASR; preserve all24 baseline PCM and10 reviewed additions. Current final captions/pixels/ratio/delivery/private/Git/schedule pending.');save(O/'latest-checkpoint.json',cp)
qp=B/'queue.json';before=qp.read_bytes();q=read(qp);q['currentOrientationReview'].update(stage=cp['stage'],tracked02aextNormalReview=cp['tracked02aextNormalReview'],activeOwnedWorkers=0,ownedJob=None,next=cp['next']);q['updatedAt']=d['reviewedAt'];assert before==qp.read_bytes();save(qp,q)
print(json.dumps(dict(normalRate=1,endedAt=8.1,finalCaptions=False)))
