"""Seal all 220 directly read V2 encoded samples after the two-label repair."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, psutil
ROOT=Path(__file__).resolve().parents[3]; B=Path(__file__).resolve().parent
O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):
 t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
def dead(pid,created):
 try: assert abs(psutil.Process(pid).create_time()-created)>.001
 except psutil.NoSuchProcess: pass
s=read(O/'07b-tracked-render-execution-v2.json');q=read(O/'07b-tracked-pixels-execution-v2.json');plan=read(ROOT/s['plan'])
for x in (s,q):
 assert x['actualExitObserved'] and x['actualOuterExitCode']==0 and x['workerDead'];dead(x['pid'],x['createTime'])
dead(s['encodePid'],s['encodeCreateTime']);dead(q['ffmpegPid'],q['ffmpegCreateTime'])
for x in s['decoders']:dead(x['pid'],x['createTime'])
assert len(q['samples'])==220 and len(q['boards'])==44
for x in q['samples']+q['boards']:assert sha(ROOT/x['path'])==x['sha256']
for x in q['samples']:
 assert x['pts']==x['frame']*1500
 seg=next(v for v in plan['segments'] if v['frameIn']<=x['frame']<v['frameOut'])
 assert x['classification']==seg['classification']
 assert x['nativeFrame']==(None if seg['classification']=='explanation' else seg['nativeIn']+x['frame']-seg['frameIn'])
assert sha(ROOT/s['output'])==s['outputSha256']
t=read(O/'narration-07b-guide-repair-execution-v1.json')
for x in t['protectedInputs']+t['results']:assert sha(ROOT/x['path'])==x['sha256']
p=O/'07b-tracked-sampled-direct-review-v2.json';assert not p.exists()
d=dict(reviewedAt=datetime.now(timezone.utc).isoformat(),renderExecution='07b-tracked-render-execution-v2.json',renderExecutionSha256=sha(O/'07b-tracked-render-execution-v2.json'),pixelExecution='07b-tracked-pixels-execution-v2.json',pixelExecutionSha256=sha(O/'07b-tracked-pixels-execution-v2.json'),actualRender=dict(session=11557,exitCode=0,completion='edffdb',closure='f48f00'),actualPixels=dict(session=None,exitCode=0,completion='e0cc83',closure='d8df50'),all220EncodedSamplesDirectlyRead=True,all44BoardsDirectlyRead=True,evidence=q['samples']+q['boards'],output=s['output'],outputSha256=s['outputSha256'],frames=2080,actualNativeFrames=1630,explanationFrames=450,timeBase='1/90000',ptsStep=1500,nativePtsProvenance=s['nativePtsProvenance'],findings=[
 'All V2 boards1-44 directly read: 1-20 and41-44 read before continuation;21-40 read in this continuation. V1 remains held for its two missing minus glyphs.',
 'Late mathematical example now visibly reads y -> -x and Rz=[[0,-1,0],[1,0,0],[0,0,1]], consistent with the explicitly separate right-handed +90 degree z example. It is not a measured game rotation.',
 'Takeoff, upper-wing tilt, front/wing comparison and separate camera view use distinct unique source intervals. Red observed tail-to-nose and blue upper-wing lines follow the selected visible features in the samples; uncertain spans hide the guides.',
 'The projected illustrative airplane has visible extruded body, wing and tail surfaces, depth ordering and changing orientation. Its semantic direction reveals match the prepared narration landmarks; the actual mixed placement remains pending.',
 'Board21-22 shows the final early-model comparison then the gameplay cut;23-28 front-view and side-view boundaries;29-34 related wing/front changes;35-40 separate camera view and guide hiding at the uncertain final endpoint. UI and upper-right legends remain readable in the inspected samples.',
 'All new labels and mathematical text stay above y900. Fixed y970 final captions and current mixed narration are not in this silent scene.',
 'V2 reuses the V1 decoded timeline with exact source-PTS proof; only two text-box unions change at frames1891-2079 before re-encoding. No new source acquisition, TTS, source retiming or geometry change.'
 ],normalPlaybackVerified=False,allBetweenFramesApproved=False,continuousHumanListeningApproved=False,engineAxesMeasured=False,physicalCentroidMeasured=False,finalCaptionsApproved=False,finalMixedApproved=False,finalRatioApproved=False,finalVideoApproved=False,newImageGit=0,protectedShaMatched=True,protectedCount=len(t['protectedInputs']))
helper=psutil.Process(27140);assert 'serve-native-review-v1.py' in ' '.join(helper.cmdline()) and abs(helper.create_time()-1791509666.8377817)<.001
raw=ROOT/'shared/assets/presenting-game-scores/raw';link=raw/'orientation-current07b-tracked-v2.mp4';src=ROOT/s['output']
if link.exists():assert os.path.samefile(src,link)
else:os.link(src,link)
html=raw/'orientation-current07b-tracked-v2-review.html';assert not html.exists()
html.write_text('<!doctype html><meta charset="utf-8"><title>Orientation current07b tracked V2 review</title><style>body{background:#181818;color:white;font:18px sans-serif}video{width:960px;max-width:100%}</style><h1>07b · Trailmakers front and wings</h1><p>Silent measured scene, two minus labels repaired. Normal 1× muted review; mixed narration and fixed captions pending.</p><video id="v07b" controls muted preload="metadata" src="orientation-current07b-tracked-v2.mp4"></video>','utf-8')
save(p,d)
cp=read(O/'latest-checkpoint.json');cp.update(recordedAt=d['reviewedAt'],stage='07b-v2-sampled-reviewed-normal-playback-pending',tracked07bSampleReview=p.relative_to(ROOT).as_posix(),activeOwnedWorkers=0,ownedJob=None);save(O/'latest-checkpoint.json',cp)
qp=B/'queue.json';before=qp.read_bytes();b=read(qp);b['currentOrientationReview'].update(stage=cp['stage'],tracked07bSampleReview=cp['tracked07bSampleReview'],activeOwnedWorkers=0,ownedJob=None);b['updatedAt']=d['reviewedAt'];assert before==qp.read_bytes();save(qp,b)
print(json.dumps(dict(samples=220,boards=44,sameInode=os.path.samefile(src,link),helperPid=helper.pid,helperCreateTime=helper.create_time(),finalApproved=False)))
