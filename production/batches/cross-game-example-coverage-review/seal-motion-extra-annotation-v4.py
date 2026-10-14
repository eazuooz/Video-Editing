"""Save bounded53sample review and prepare reuse-only localhost playback."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,psutil,os
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
e=read(R/'extra-annotation-pieces-execution-v4.json');assert e['exitCode']==0 and len(e['pieces'])==1 and e['encodedSampleCount']==53 and e['boardCount']==14
try:
 p=psutil.Process(e['pid']);assert abs(p.create_time()-e['createTime'])>=.01
except psutil.NoSuchProcess:pass
checked={}
for p in e['pieces']:
 assert all(p[k]==0 for k in ['decodeExitCode','encodeExitCode','wholeDecodeExitCode','extractionExitCode'])
 for x in [p]+p['samples']+p['boards']:
  assert sha(ROOT/x['path'])==x['sha256'];checked[x['path']]=x['sha256']
e.update(actualOuterSession=54367,actualOuterExitCode=0,actualOuterCompletion='7dc1cb',originalWorkerAlive=False)
(R/'extra-annotation-pieces-execution-v4.json').write_text(json.dumps(e,ensure_ascii=False,indent=2)+'\n','utf-8')
proof=dict(schemaVersion=1,reviewedAt=datetime.now(timezone.utc).isoformat(),actualSession=54367,actualExitCode=0,actualCompletion='7dc1cb',actualPieceCount=1,
 directlyReadEncodedSamples=53,directlyReadBoards=14,sha256RecheckedFiles=checked,
 findings='All53 encoded samples/14boards read. Red bracket now identifies the broad visible decorated tool body at every sampled aim/downward state, with consistent tool-body label. Cyan cue identifies the small background hut/roof region through minor view changes. Full HUD and caption preview stay clear; no claimed nozzle-tip, measured movement, physical centroid or comfort result. PreviousV2/V3 offsets retained as held history.',
 sampledRoleApproval=True,allIntermediateFramesRead=False,normalPlaybackApproved=False,narrationTimed=False,finalCueApproval=False,worldMeasurementApproved=False,localOnly=True)
assert not (R/'extra-annotation-pieces-sampled-direct-review-v4.json').exists()
(R/'extra-annotation-pieces-sampled-direct-review-v4.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf-8')
raw=ROOT/'shared/assets/presenting-game-scores/raw'
targets=[('motion-extra-portal-role-v2.mp4',ROOT/'shared/output/cross-game-example-coverage/motion/extra-annotation-pieces-v2/portal-held-putdown-portal-beam/silent-role-annotation.mp4'),('motion-extra-powerwash-role-v4.mp4',ROOT/e['pieces'][0]['path'])]
for name,src in targets:
 dst=raw/name
 if dst.exists():assert os.path.samefile(src,dst)
 else:os.link(src,dst)
html='''<!doctype html><meta charset="utf-8"><title>Motion extra annotated roles review</title><style>body{margin:12px;font-family:Arial;background:#eee}video{width:min(100%,960px);display:block}button{font-size:18px;margin:8px}p{margin:8px}</style><h2>Silent annotation review · normal1×</h2><p>PortalV2 / PowerWashV4. Preview caption only; final narration timing pending.</p><button onclick="loadClip(0)">Prepare Portal V2</button><button onclick="loadClip(1)">Prepare PowerWash V4</button><button onclick="v.play()">Play 1x muted</button><video id="v" controls muted preload="metadata"></video><p id="s">Select a reviewed piece.</p><script>const names=['motion-extra-portal-role-v2.mp4','motion-extra-powerwash-role-v4.mp4'];const v=document.getElementById('v');function loadClip(n){v.pause();v.src=names[n];v.playbackRate=1;v.muted=true;v.load();document.getElementById('s').textContent=names[n]}v.onended=()=>document.getElementById('s').textContent+=' · ended';</script>'''
p=raw/'motion-extra-annotation-normal-review-v1.html';assert not p.exists();p.write_text(html,'utf-8')
cp_path=R/'latest-checkpoint.json';cp=read(cp_path);cp.update(ownedJob=dict(active=False,status='completed-sampled-powerwash-v4',sessionId=54367,exitCode=0,completion='7dc1cb'),activeOwnedWorkers=0,extraAnnotationSampledReview='extra-annotation-pieces-sampled-direct-review-v4.json',next='Reuse CUA96 for PortalV2/PowerWashV4 normal1x playback. Then paragraph-led cut timing and actual annotations/currentmix. No duplicate renders.')
cp_path.write_text(json.dumps(cp,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(samples=53,boards=14,hashes=len(checked),sampledRoleApproved=True,normalAndFinal=False)))
