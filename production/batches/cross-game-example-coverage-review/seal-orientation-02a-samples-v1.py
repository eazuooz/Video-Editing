"""Seal 100 directly viewed encoded samples and 20 boards; no continuous approval."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, psutil
ROOT=Path(__file__).resolve().parents[3]
B=Path(__file__).resolve().parent
O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):
 t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
s=read(O/'02a-tracked-render-execution-v1.json');q=read(O/'02a-tracked-pixel-execution-v1.json')
assert s['actualExitObserved'] and s['actualOuterExitCode']==0 and s['workerDead']
assert q['actualExitObserved'] and q['actualOuterExitCode']==0 and q['workerDead']
for x in [s['pid'],s['decodePid'],s['encodePid'],q['pid'],q['ffmpegPid']]:assert not psutil.pid_exists(x)
assert len(q['samples'])==100 and len(q['boards'])==20
for x in q['samples']+q['boards']:assert sha(ROOT/x['path'])==x['sha256']
for x in q['samples']:
 assert x['pts']==x['frame']*1500
 assert x['sourceFrame']==min(4770+x['frame'],5801)
 assert x['roundingHold']==(x['frame']==1032)
assert sha(ROOT/s['output'])==s['outputSha256']
t=read(O/'narration-07b-guide-repair-execution-v1.json')
for x in t['protectedInputs']+t['results']:assert sha(ROOT/x['path'])==x['sha256']
p=O/'02a-tracked-sampled-direct-review-v1.json';assert not p.exists()
d=dict(reviewedAt=datetime.now(timezone.utc).isoformat(),renderExecution='02a-tracked-render-execution-v1.json',renderExecutionSha256=sha(O/'02a-tracked-render-execution-v1.json'),pixelExecution='02a-tracked-pixel-execution-v1.json',pixelExecutionSha256=sha(O/'02a-tracked-pixel-execution-v1.json'),actualRender=dict(session=43832,exitCode=0,completion='c88764',closure='9b9e8b'),actualPixelExtraction=dict(exitCode=0,completion='1c6c78',closure='289f57'),all100EncodedSamplesDirectlyRead=True,all20BoardsDirectlyRead=True,evidence=q['samples']+q['boards'],output=s['output'],outputSha256=s['outputSha256'],frames=1033,nativeFrames=1032,timeBase='1/90000',ptsStep=1500,findings=[
 'Body observation point is a manually observed screen feature, not an engine position or physical centroid.',
 'Guides hide conservatively through foreground/dark/small-object brackets; no interpolation crosses a hidden bracket.',
 'At frame330 the cyan point returns after the hidden bracket; frame430 reveals the red half-second screen displacement.',
 'At frames570 and930 the cyan point returns; the red displacement waits for a visible previous half-second.',
 'The Awesome +2000 game UI stays above the body and separate from the guides in reviewed samples.',
 'Yellow/teal/red legends remain below the top game credit and above y900. The final fixed y970 captions are still absent.',
 'The final encoded frame1032 is one explicit rounding hold of native5801; no repeated action or slowdown is used.'
 ],conservativeSourceHideSeconds=[[83,85],[87.5,89],[92.5,95]],normalPlaybackVerified=False,narrationLandmarksReferenced=True,continuousNarrationListeningApproved=False,allBetweenFramesApproved=False,engineAxesMeasured=False,physicalCentroidMeasured=False,finalCaptionsApproved=False,finalRatioApproved=False,finalVideoApproved=False,newImageGit=0)
save(p,d)
cp=read(O/'latest-checkpoint.json');cp.update(recordedAt=d['reviewedAt'],stage='02a-sampled-tracking-reviewed-normal-playback-pending',tracked02aSampleReview=p.relative_to(ROOT).as_posix(),activeOwnedWorkers=0,ownedJob=None)
save(O/'latest-checkpoint.json',cp)
qp=B/'queue.json';before=qp.read_bytes();b=read(qp);b['currentOrientationReview'].update(stage=cp['stage'],tracked02aSampleReview=cp['tracked02aSampleReview'],activeOwnedWorkers=0,ownedJob=None);b['updatedAt']=d['reviewedAt'];assert before==qp.read_bytes();save(qp,b)
raw=ROOT/'shared/assets/presenting-game-scores/raw';link=raw/'orientation-current02a-tracked-v1.mp4';src=ROOT/s['output']
if link.exists():assert os.path.samefile(src,link)
else:os.link(src,link)
html=raw/'orientation-current02a-tracked-v1-review.html'
assert not html.exists()
html.write_text('<!doctype html><meta charset="utf-8"><title>Orientation current02a tracked review</title><style>body{background:#181818;color:white;font:18px sans-serif}video{width:960px;max-width:100%}</style><h1>02a · Superflight screen observations</h1><p>Silent measured scene; normal 1× muted review. Final narration and fixed captions pending.</p><video id="v02a" controls muted preload="metadata" src="orientation-current02a-tracked-v1.mp4"></video>','utf-8')
print(json.dumps(dict(samples=100,boards=20,protectedInputs=len(t['protectedInputs']),sameInode=os.path.samefile(src,link),normalPlayback=False)))
