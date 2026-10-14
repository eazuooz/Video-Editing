"""Record actual normal-rate silent playback and its bounded endpoints."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent;O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):
 t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
s=read(O/'03b-tracked-render-execution-v1.json');r=O/'03b-tracked-sampled-direct-review-v1.json';assert read(r)['all169EncodedSamplesDirectlyRead'];assert sha(ROOT/s['output'])==s['outputSha256']
p=O/'03b-tracked-normal-playback-direct-review-v1.json';assert not p.exists()
d=dict(reviewedAt=datetime.now(timezone.utc).isoformat(),tabId='106',url='http://127.0.0.1:9250/orientation-current03b-tracked-v1-review.html',sampledReview=r.relative_to(ROOT).as_posix(),sampledReviewSha256=sha(r),output=s['output'],outputSha256=s['outputSha256'],start=dict(time=.152145,duration=27.266667,paused=False,ended=False,rate=1,muted=True),end=dict(time=27.266667,duration=27.266667,paused=True,ended=True,rate=1,muted=True),action='Native video container Space; no seek or rate mutation.',endpointScreenshotObserved=True,normalRateEndpointPlaybackVerified=True,all169EncodedSamplesDirectlyRead=True,all34BoardsDirectlyRead=True,allBetweenFramesApproved=False,continuousHumanListeningApproved=False,finalCaptionsApproved=False,finalMixedApproved=False,finalRatioApproved=False,newImageGit=0)
save(p,d)
cp=read(O/'latest-checkpoint.json');cp.update(recordedAt=d['reviewedAt'],stage='03b-sampled-and-normal-reviewed-remaining-scene-allocation',tracked03bNormalReview=p.relative_to(ROOT).as_posix(),activeOwnedWorkers=0,ownedJob=None,next='Prepare measured 07b/10b and related unique Superflight extension; preserve completed 02a/03b/Manim/PCM. Current34 mixed AAC, caption timing, final pixels and ratio remain unapproved.');save(O/'latest-checkpoint.json',cp)
qp=B/'queue.json';before=qp.read_bytes();q=read(qp);q['currentOrientationReview'].update(stage=cp['stage'],tracked03bNormalReview=cp['tracked03bNormalReview'],activeOwnedWorkers=0,ownedJob=None,next=cp['next']);q['updatedAt']=d['reviewedAt'];assert before==qp.read_bytes();save(qp,q)
print(json.dumps(dict(normalRate=1,endedAt=27.266667,finalCaptions=False)))
