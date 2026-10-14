"""Record actual normal-playback observations; raw sources do not approve final pixels."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
ROOT=Path(__file__).resolve().parents[3];P=ROOT/'projects/game-lighting-history-04/production'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
stamp=lambda:datetime.now(timezone.utc).isoformat()
observations={
 'first:original-overview-1':'Whole22.8s normal playback: projected platforms, changing arrows and occlusion; logical-series label explicitly identifies this physical part. Heading and fixed caption region remain clear.',
 'tsr-silhouette-history:model':'Whole3.966667s normal playback: foreground car/boundary occlusion changes, exposing background and the history-arrow relationship.',
 'tsr-rotation-vectors:model':'Whole6.483333s normal playback: rotating spatial object and motion-vector relationship remain legible.',
 'horizon-comparison-before:model':'Whole11.683333s normal playback: distinct projected comparison surfaces and timed movement retain the observed-detail question.',
 'cyber-comparison-before:model':'Whole7.283333s normal playback: reconstruction input roles are spatially compared without pretending the model is gameplay.',
 'cyber-light-reconstruction:model':'Whole2.4s normal playback: two XYZ platforms and four orange/teal vectors develop; heading distinguishes reconstruction input data.',
 'mobile-compiler-availability:model':'Whole9.483333s normal playback: right projected outline cube, orange vertical arrows and red route develop opposite the left solid data block; availability/target/compiler distinctions stay visible.',
 'fortnite-comparison-before:model':'Whole8.25s normal playback: three projected material columns and diagonal connector develop into a diagnostic trace, relating different material conditions within the same game.',
 'rivalry-surface-observation:model':'Whole4.2s normal playback: yaw, block/plane occlusion and red connecting arrows change in space, linking shape input to visible light.'}
requestPath=P/'part1-moving-input-request-v247.json';request=read(requestPath)
records=[]
for row in request['rows']:
 assert sha(ROOT/row['path'])==row['sha256']
 records.append({**row,'normalSpeedPlaybackDirectlyObserved':True,'movingPixelsApproved':row['id'] in observations,
  'finding':observations.get(row['id'],'Direct normal playback found a native marker/source-condition defect; preserve this failed observation and require v250 corrected moving pixels.')})
progress={'recordedAt':stamp(),'requestSha256':sha(requestPath),'planSha256':request['planSha256'],'records':records,
 'approvedUnchangedMovingRows':len(observations),'allCurrentMovingPixelsReviewed':False,'allFinalPixelsReviewed':False,'qaApproved':False,'uploaded':False,'newGitImages':0}
(P/'part1-moving-input-direct-review-v247.json').write_text(json.dumps(progress,ensure_ascii=False,indent=2)+'\n','utf8')
OP=P/'part1-input-overrides-v249.json';overrides=read(OP)
rawNotes={
 'horizon-detail-motion:native':'Normal source1–6.683333s: zoom initially shows heads, then embroidered bag edges. Mark only from local0.75s; CNN/Transformer conditions remain at the source bottom.',
 'outer-displayed-frames:native':'Normal source0–16.333333s and direct0.27/2/3/4/5.65/13/16.48s: central FPS card is near source766,220 and moves right; later4x/5x cards occupy the top-right. Do not outline the transitional2.6–4s. Preserve top FPS/condition pixels.',
 'cyber-light-reconstruction:native':'Both normal selected ranges8–10.283333s and46.5–62.3s contain city action without title cards. Statue/neon action precedes market/combat. Original FPS, DLSS/full-ray-tracing conditions and RTX badge remain; FPS is a bundled-condition source observation, not a measured ray-reconstruction-only gain.',
 'cyber-surface-observation:native':'All three normal source ranges10.3–11.833333s,15–29.4s and33–42.2s contain actual city/sign/wet-floor before/after action. DLSS Off/3.5 labels remain at the bottom. Source32s black Ray Reconstruction title is excluded.',
 'fortnite-mobile-test:native':'Normal source240–259s: character/camera pass HQ/LQ Noise bump map rocks and end at Dual Normal Clear Coat; original left diagnostic graph remains above the joystick. Tighten graph outline to height550.'}
rows=[]
for cut in overrides['effectiveCuts']:
 if cut['id'] not in overrides['changes']:continue
 assert sha(ROOT/cut['video']['path'])==cut['video']['sha256']
 rows.append({'id':cut['id'],'source':cut['video'],'sourceCuts':cut['proposedCuts'],'normalSpeed':1,
  'allSelectedRangesNormalPlaybackDirectlyReviewed':True,'finding':rawNotes[cut['id']],
  'originalSourceConditionsPreservedInPlan':True,'correctedEncodedMovingPixelsReviewed':False})
assert len(rows)==5
source={'recordedAt':stamp(),'overridesSha256':sha(OP),'inputPlan':overrides['inputPlan'],'records':rows,
 'allSelectedSourcesNormalPlaybackDirectlyReviewed':True,'allCorrectedEncodedMovingPixelsReviewed':False,
 'allFinalPixelsReviewed':False,'qaApproved':False,'uploaded':False,'newGitImages':0,'sourceAudio':0,'loops':0,'slowdown':0,
 'rightsApproved':False,'next':'Render only these five native corrections after the single ASR ends; directly inspect corrected moving pixels before final pair.'}
(P/'part1-native-overrides-direct-review-v249.json').write_text(json.dumps(source,ensure_ascii=False,indent=2)+'\n','utf8')
print(json.dumps({'unchangedMovingRowsReviewed':len(observations),'rawSourcesReviewed':len(rows),'finalApproved':False}))
