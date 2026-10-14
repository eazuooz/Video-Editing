"""Seal directly read41 encoded samples9 boards; no whole-frame or final approval."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,psutil
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent;O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):
 t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
s=read(O/'02aext-tracked-render-execution-v1.json');q=read(O/'02aext-tracked-pixel-execution-v1.json')
for x in [s,q]:assert x['actualExitObserved'] and x['actualOuterExitCode']==0 and x['workerDead']
assert len(q['samples'])==41 and len(q['boards'])==9
for x in q['samples']+q['boards']:assert sha(ROOT/x['path'])==x['sha256']
for x in q['samples']:assert x['pts']==x['frame']*1500 and x['sourceFrame']==3960+x['frame'] and not x['roundingHold']
assert sha(ROOT/s['output'])==s['outputSha256']
t=read(O/'narration-07b-guide-repair-execution-v1.json')
for x in t['protectedInputs']+t['results']:assert sha(ROOT/x['path'])==x['sha256']
helper=psutil.Process(27140);assert abs(helper.create_time()-1791509666.8377817)<.001 and 'serve-native-review-v1.py' in ' '.join(helper.cmdline())
p=O/'02aext-tracked-sampled-direct-review-v1.json';assert not p.exists()
d=dict(reviewedAt=datetime.now(timezone.utc).isoformat(),actualRender=dict(session=58002,initial='e1d11b',completion='4e165f',closure='9b898d',exitCode=0),actualPixels=dict(completion='d21947',closure='773929',exitCode=0),renderExecutionSha256=sha(O/'02aext-tracked-render-execution-v1.json'),pixelExecutionSha256=sha(O/'02aext-tracked-pixel-execution-v1.json'),all41DisplayedEncodedSamplesDirectlyRead=True,all9BoardsDirectlyRead=True,evidence=q['samples']+q['boards'],output=s['output'],outputSha256=s['outputSha256'],frames=486,nativeIn=3960,nativeOutExclusive=4446,timeBase='1/90000',ptsStep=1500,findings=[
 'Cyan manually selected torso feature follows the approaching and emerging character in displayed samples. It is not a physical centroid or engine position.',
 'The guide is absent after native4110 and through4259 because null neighboring observations and the conservative hide bracket prevent interpolation through dark structures.',
 'Cyan returns native4260; the red half-second screen displacement returns native4290 only after a complete visible half-second. No trace crosses the hidden bracket.',
 'Native4290..4445 shows changing body attitude and continued movement after the structure. Red compares screen positions and includes camera motion; it is not a measured world trajectory or roll angle.',
 'Game score feedback remains visible. All four explanatory legends and credit stay above900; fixed narration captions are absent in this silent assembly input.',
 'All486 frames use consecutive exact sourcePTS at normal speed, with no loop, slowdown or quota hold. It continues the comparison already introduced by02a voice.'
 ],protectedCount=len(t['protectedInputs']),protectedShaMatched=True,normalPlaybackVerified=False,allBetweenFramesApproved=False,continuousNarrationListeningApproved=False,finalCaptionsApproved=False,finalRatioApproved=False,finalVideoApproved=False,newImageGit=0)
save(p,d)
cp=read(O/'latest-checkpoint.json');cp.update(recordedAt=d['reviewedAt'],stage='02aext-sampled-review-normal-playback-pending',tracked02aextSampleReview=p.relative_to(ROOT).as_posix(),activeOwnedWorkers=0,ownedJob=None);save(O/'latest-checkpoint.json',cp)
qp=B/'queue.json';before=qp.read_bytes();b=read(qp);b['currentOrientationReview'].update(stage=cp['stage'],tracked02aextSampleReview=cp['tracked02aextSampleReview'],activeOwnedWorkers=0,ownedJob=None);b['updatedAt']=d['reviewedAt'];assert before==qp.read_bytes();save(qp,b)
raw=ROOT/'shared/assets/presenting-game-scores/raw';link=raw/'orientation-current02aext-tracked-v1.mp4';src=ROOT/s['output']
if link.exists():assert os.path.samefile(src,link)
else:os.link(src,link)
html=raw/'orientation-current02aext-tracked-v1-review.html';assert not html.exists()
html.write_text('<!doctype html><meta charset="utf-8"><title>Orientation02a continuation</title><style>body{background:#181818;color:white;font:18px sans-serif}video{width:960px;max-width:100%}</style><h1>Superflight · related observation continuation</h1><p>Silent8.1s assembly input; normal1× muted review. Final mix and fixed captions pending.</p><video id="v02aext" controls muted preload="metadata" src="orientation-current02aext-tracked-v1.mp4"></video>','utf-8')
print(json.dumps(dict(samples=41,boards=9,protected=len(t['protectedInputs']),sameInode=os.path.samefile(src,link),helperReused=True)))
