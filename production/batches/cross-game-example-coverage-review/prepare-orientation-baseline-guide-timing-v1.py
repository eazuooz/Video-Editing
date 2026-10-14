"""Native-bounded guide allocation beside retained narration; no render approval."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
ROOT=Path(__file__).resolve().parents[3];O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
rd=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rel=lambda p:p.relative_to(ROOT).as_posix()
out=O/'current34-baseline-guide-timing-proposal-v1.json';assert not out.exists()
recut=rd(O/'conservative-source-recut-proposal-v2.json');anchors=rd(O/'annotation-observation-keyframes-v1.json');first=rd(O/'observation-point-keyframes-v3.json')
plan=rd(O/'current34-measured-timing-plan-v1.json');base=rd(ROOT/plan['sourceBaselineTimeline'])
scripts={s['id']:s['lines'] for s in rd(O/'script/current34-combined-v1.ko.json')['scenes']}
assert sha(ROOT/recut['source'])==recut['sourceSha256']==anchors['sourceSha256']
for window in anchors['windows']:
 for v in window['keyframes']:assert sha(ROOT/v['inspectedImage'])==v['inspectedImageSha256']
for v in first['keyframes']:assert sha(ROOT/v['inspectedImage'])==v['inspectedImageSha256']
points={w['scene']:w for w in anchors['windows']}
points['02']=dict(startNativeFrame=first['sourceFirstNativeFrame'],endNativeFrameExclusive=first['sourceEndExclusiveNativeFrame'],keyframes=first['keyframes'],hiddenLocalFrameRanges=[])
rows=[]
for sid in ['02','05','08','11','14','17','20','23']:
 clips=[v for v in recut['windows'] if v['scene']==sid];cursor=0;windows=[]
 for v in clips:
  windows.append(dict(**v,sceneFrameIn=cursor,sceneFrameOut=cursor+v['frames']));cursor+=v['frames']
 s=next(v for v in plan['scenes'] if v['id']==sid);b=next(v for v in base['scenes'] if v['id']==sid)
 assert cursor==s['frames']==s['actualFrames']
 p=points[sid];matches=[v for v in windows if v['firstNativeFrame']<=p['startNativeFrame']<p['endNativeFrameExclusive']<=v['endExclusiveNativeFrame']];assert len(matches)==1
 c=matches[0];local=c['sceneFrameIn']+p['startNativeFrame']-c['firstNativeFrame'];end=local+p['endNativeFrameExclusive']-p['startNativeFrame']
 cue_neighbors=[dict(paragraph=i+1,startSeconds=v['start'],endSeconds=v['end'],expectedKo=scripts[sid][i]) for i,v in enumerate(b['cues']) if v['start']<end/60 and v['end']>local/60]
 rows.append(dict(id=sid,frames=cursor,source=recut['source'],sourceSha256=recut['sourceSha256'],windows=windows,pointWindow=dict(nativeIn=p['startNativeFrame'],nativeOutExclusive=p['endNativeFrameExclusive'],sceneFrameIn=local,sceneFrameOut=end,keyframes=p['keyframes'],hiddenLocalFrameRanges=p['hiddenLocalFrameRanges']),neighboringOriginalNarrationCues=cue_neighbors,
  scope='Cyan approximate observed torso screen point; red half-second screen-position change only while both endpoints remain visible. Golden screen-up reference is camera-image up, never engine/world/body up. Hide guides outside the manually observed native window and on every occlusion; no extrapolated trajectory.',
  noPhysicalCentroid=True,noRecoveredWorldAxes=True,noRigidBodyRollMeasured=True,currentNarrationAlignmentApproved=False,movingFinalPixelApproved=False))
assert sum(v['frames'] for v in rows)==21370
data=dict(preparedAt=datetime.now(timezone.utc).isoformat(),recutPlan=rel(O/'conservative-source-recut-proposal-v2.json'),recutPlanSha256=sha(O/'conservative-source-recut-proposal-v2.json'),anchorPlan=rel(O/'annotation-observation-keyframes-v1.json'),anchorPlanSha256=sha(O/'annotation-observation-keyframes-v1.json'),firstAnchorPlan=rel(O/'observation-point-keyframes-v3.json'),firstAnchorPlanSha256=sha(O/'observation-point-keyframes-v3.json'),scenes=rows,actualFrames=21370,normalSpeed=1,sourceAudio=False,all24PcmPreserved=True,sourceOrAnchorReExtraction=False,renderExecuted=False,currentMixedNarrationAlignmentApproved=False,allFinalPixelsApproved=False,newImageGit=0)
out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(dict(preparedScenes=8,actualFrames=21370,rendered=False,finalApproval=False)))
