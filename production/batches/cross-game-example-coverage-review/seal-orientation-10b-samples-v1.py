"""Seal the directly read 215 encoded samples; this is not final video approval."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, psutil
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):
 t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
def dead(pid,created):
 try:assert abs(psutil.Process(pid).create_time()-created)>.001
 except psutil.NoSuchProcess:pass
s=read(O/'10b-tracked-render-execution-v1.json');q=read(O/'10b-tracked-pixels-execution-v1.json');plan=read(ROOT/s['plan'])
for x in (s,q):
 assert x['actualExitObserved'] and x['actualOuterExitCode']==0 and x['workerDead'];dead(x['pid'],x['createTime'])
dead(s['encodePid'],s['encodeCreateTime']);dead(q['ffmpegPid'],q['ffmpegCreateTime'])
for x in s['decoders']:dead(x['pid'],x['createTime']);assert x['exitCode']==0 and x['exactNativePtsMatched']
assert len(q['samples'])==215 and len(q['boards'])==43
for x in q['samples']+q['boards']:assert sha(ROOT/x['path'])==x['sha256']
for x in q['samples']:
 assert x['pts']==x['frame']*1500
 seg=next(v for v in plan['segments'] if v['frameIn']<=x['frame']<v['frameOut'])
 assert x['classification']==seg['classification']
 assert x['nativeFrame']==(None if seg['classification']=='explanation' else seg['nativeIn']+x['frame']-seg['frameIn'])
assert sha(ROOT/s['output'])==s['outputSha256']
t=read(O/'narration-07b-guide-repair-execution-v1.json')
for x in t['protectedInputs']+t['results']:assert sha(ROOT/x['path'])==x['sha256']
p=O/'10b-tracked-sampled-direct-review-v1.json';assert not p.exists()
d=dict(reviewedAt=datetime.now(timezone.utc).isoformat(),renderExecution='10b-tracked-render-execution-v1.json',renderExecutionSha256=sha(O/'10b-tracked-render-execution-v1.json'),pixelExecution='10b-tracked-pixels-execution-v1.json',pixelExecutionSha256=sha(O/'10b-tracked-pixels-execution-v1.json'),actualRender=dict(session=27696,exitCode=0,completion='eec6de',closure='171353'),actualPixels=dict(session=None,exitCode=0,completion='5e2890',closure='173b15'),all215EncodedSamplesDirectlyRead=True,all43BoardsDirectlyRead=True,evidence=q['samples']+q['boards'],output=s['output'],outputSha256=s['outputSha256'],frames=1901,actualNativeFrames=510,explanationFrames=1391,timeBase='1/90000',ptsStep=1500,all510NativePtsMatched=s['all510NativePtsMatched'],findings=[
 'All43 boards/215 encoded samples directly read: boards1-5 before continuation,6-43 in this continuation. Opening extruded aircraft and mounting component expose front/side/top surfaces and change projected orientation.',
 'Boards7-11 full source context retains the original upper-right rotation-key help and green ghosted preview. Frozen prerequisite analysis is explanation, not actual quota.',
 'Boards12-22 enlarged preview: teal observation rectangle and red observed long-direction line follow the selected vertical/horizontal part features. Guides hide at the uncertain rotation transitions; no world angle or specific keypress is asserted.',
 'Boards22-31 explicitly announce a separate placement interval. The small orientation-selection preview, opaque placed part and overlapping next orange preview are distinguished; overlapping/uncertain spans hide guides. A teal label names the solid placed part only after the later clear source observation.',
 'Boards32-34 show a separate full-source size selection/camera-change comparison, including original large part clipping. This is not labelled a pure rotation or a measured physical scale change; original component counts and rotation-key help remain visible.',
 'Boards34-43 return to the projected illustrative model and reveal red x, teal y, blue z reference directions at the recorded voice landmark. The text explicitly distinguishes this separate model from gameplay observation.',
 'All added labels remain above y900; crop analysis uses a same-frame blurred footer for fixed y970 captions. Silent-scene review does not approve current mixed AAC or final captions/UI.',
 'All actual intervals are unique native60fps actions with exact native*256 PTS proof. The prerequisite freeze counts as explanation. No source acquisition, TTS, loop or slowdown.'
 ],normalPlaybackVerified=False,allBetweenFramesApproved=False,continuousHumanListeningApproved=False,engineAxesMeasured=False,physicalCentroidMeasured=False,exactFirstTransitionMeasured=False,finalCaptionsApproved=False,finalMixedApproved=False,finalRatioApproved=False,finalVideoApproved=False,newImageGit=0,protectedShaMatched=True,protectedCount=len(t['protectedInputs']))
helper=psutil.Process(27140);assert 'serve-native-review-v1.py' in ' '.join(helper.cmdline()) and abs(helper.create_time()-1791509666.8377817)<.001
raw=ROOT/'shared/assets/presenting-game-scores/raw';link=raw/'orientation-current10b-tracked-v1.mp4';src=ROOT/s['output']
if link.exists():assert os.path.samefile(src,link)
else:os.link(src,link)
html=raw/'orientation-current10b-tracked-v1-review.html';assert not html.exists()
html.write_text('<!doctype html><meta charset="utf-8"><title>Orientation current10b tracked V1 review</title><style>body{background:#181818;color:white;font:18px sans-serif}video{width:960px;max-width:100%}</style><h1>10b · Space Engineers preview and placement</h1><p>Silent measured scene. Normal 1× muted review; mixed narration and fixed captions pending.</p><video id="v10b" controls muted preload="metadata" src="orientation-current10b-tracked-v1.mp4"></video>','utf-8')
save(p,d)
cp=read(O/'latest-checkpoint.json');cp.update(recordedAt=d['reviewedAt'],stage='10b-sampled-reviewed-normal-playback-pending',tracked10bSampleReview=p.relative_to(ROOT).as_posix(),activeOwnedWorkers=0,ownedJob=None);save(O/'latest-checkpoint.json',cp)
qp=B/'queue.json';before=qp.read_bytes();b=read(qp);b['currentOrientationReview'].update(stage=cp['stage'],tracked10bSampleReview=cp['tracked10bSampleReview'],activeOwnedWorkers=0,ownedJob=None);b['updatedAt']=d['reviewedAt'];assert before==qp.read_bytes();save(qp,b)
print(json.dumps(dict(samples=215,boards=43,sameInode=os.path.samefile(src,link),helperPid=helper.pid,helperCreateTime=helper.create_time(),protectedCount=len(t['protectedInputs']),finalApproved=False)))
