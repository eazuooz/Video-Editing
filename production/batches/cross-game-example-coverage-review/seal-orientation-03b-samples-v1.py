"""Seal the 169 encoded samples directly read on 34 boards; bounded approval."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json,os,psutil
ROOT=Path(__file__).resolve().parents[3]; B=Path(__file__).resolve().parent
O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):
 t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
s=read(O/'03b-tracked-render-execution-v1.json'); q=read(O/'03b-tracked-pixels-execution-v1.json'); plan=read(ROOT/s['plan'])
for x in (s,q):assert x['actualExitObserved'] and x['actualOuterExitCode']==0 and x['workerDead'] and not psutil.pid_exists(x['pid'])
assert not psutil.pid_exists(s['encodePid']) and not psutil.pid_exists(q['ffmpegPid'])
for x in s['decoders']:assert not psutil.pid_exists(x['pid']) and x['exactNativePtsMatched']
assert len(q['samples'])==169 and len(q['boards'])==34
for x in q['samples']+q['boards']:assert sha(ROOT/x['path'])==x['sha256']
for x in q['samples']:
 assert x['pts']==x['frame']*1500
 seg=next(v for v in plan['segments'] if v['frameIn']<=x['frame']<v['frameOut'])
 assert x['classification']==seg['classification']
 assert x['nativeFrame']==(None if seg['classification']=='explanation' else seg['nativeIn']+x['frame']-seg['frameIn'])
assert sha(ROOT/s['output'])==s['outputSha256']
t=read(O/'narration-07b-guide-repair-execution-v1.json')
for x in t['protectedInputs']+t['results']:assert sha(ROOT/x['path'])==x['sha256']
p=O/'03b-tracked-sampled-direct-review-v1.json';assert not p.exists()
d=dict(reviewedAt=datetime.now(timezone.utc).isoformat(),renderExecution='03b-tracked-render-execution-v1.json',renderSha256=sha(O/'03b-tracked-render-execution-v1.json'),pixelExecution='03b-tracked-pixels-execution-v1.json',pixelSha256=sha(O/'03b-tracked-pixels-execution-v1.json'),actualRender=dict(session=23682,exitCode=0,completion='4b396b',closure='0aa731'),actualPixels=dict(session=None,exitCode=0,completion='f0c339',closure='501828'),all169EncodedSamplesDirectlyRead=True,all34BoardsDirectlyRead=True,evidence=q['samples']+q['boards'],output=s['output'],outputSha256=s['outputSha256'],frames=1636,actualNativeFrames=1050,explanationFrames=586,timeBase='1/90000',ptsStep=1500,findings=[
 'Road frames show the observed head/hip line leaning with the rider while the cyan hip screen feature follows position. Neither is a rigid bike axis or physical centroid.',
 'Guides hide during fast inversion and uncertain views; sampled return boundaries do not interpolate across hidden brackets.',
 'The first jump shows inverted wheels then wheels below before the landing sequence. The second unique sequence shows another inversion, recovery and landing, then a further jump returning wheels below before the cut; its endpoint is not claimed as an exact ground-contact frame.',
 'Game speed, trick and objective UI remain distinct from the top-right legends in reviewed samples. All new legends and model labels remain above y900; fixed y970 captions are pending.',
 'The illustrative model has visible extruded frame front/side faces and cylindrical wheel sides, with changing projected pitch and fixed movement arrow. Front f appears at frame1509, up u at1530, and the combined-direction label at1566.',
 'The 306-frame second-action observation pause is planned at original PCM sample390960; no mixed voice placement has been approved yet.'
 ],normalPlaybackVerified=False,allBetweenFramesApproved=False,continuousHumanListeningApproved=False,engineAxesMeasured=False,physicalCentroidMeasured=False,finalCaptionsApproved=False,finalMixedApproved=False,finalRatioApproved=False,finalVideoApproved=False,newImageGit=0)
save(p,d)
cp=read(O/'latest-checkpoint.json');cp.update(recordedAt=d['reviewedAt'],stage='03b-sampled-tracking-reviewed-normal-playback-pending',tracked03bSampleReview=p.relative_to(ROOT).as_posix(),activeOwnedWorkers=0,ownedJob=None);save(O/'latest-checkpoint.json',cp)
qp=B/'queue.json';before=qp.read_bytes();b=read(qp);b['currentOrientationReview'].update(stage=cp['stage'],tracked03bSampleReview=cp['tracked03bSampleReview'],activeOwnedWorkers=0,ownedJob=None);b['updatedAt']=d['reviewedAt'];assert before==qp.read_bytes();save(qp,b)
raw=ROOT/'shared/assets/presenting-game-scores/raw';link=raw/'orientation-current03b-tracked-v1.mp4';src=ROOT/s['output']
if link.exists():assert os.path.samefile(src,link)
else:os.link(src,link)
html=raw/'orientation-current03b-tracked-v1-review.html';assert not html.exists()
html.write_text('<!doctype html><meta charset="utf-8"><title>Orientation current03b tracked review</title><style>body{background:#181818;color:white;font:18px sans-serif}video{width:960px;max-width:100%}</style><h1>03b · Descenders position and orientation</h1><p>Silent measured scene; normal 1× muted review. Current mixed narration and fixed captions pending.</p><video id="v03b" controls muted preload="metadata" src="orientation-current03b-tracked-v1.mp4"></video>','utf-8')
helper=psutil.Process(27140);assert 'serve-native-review-v1.py' in ' '.join(helper.cmdline())
print(json.dumps(dict(samples=169,boards=34,sameInode=os.path.samefile(src,link),helperPid=helper.pid,helperCreateTime=helper.create_time(),finalApproved=False)))
