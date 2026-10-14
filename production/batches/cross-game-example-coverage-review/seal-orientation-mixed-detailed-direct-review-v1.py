"""Record completed direct board inspection and actual CUA normal endpoints."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json,os
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def save(p,v):
 t=p.with_name(p.name+'.writing');t.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
now=datetime.now(timezone.utc).isoformat()
sp=O/'current34-mixed-detailed-render-execution-v2.json';s=read(sp)
assert s['actualOuterExitCode']==0 and s['workerDead'] and s['all3696RetainedDecoderInputFramesMatched']
assert s['actualSession']==51842 and s['actualCompletion']=='696714'
notes={
 '03b':'Helmet face/eye/nose, clothing, bent arms/legs, gloved hands on the handlebar, shoes, open tubular bicycle frame, fork, thick tyres, rims/spokes/hubs and pedals remain distinguishable during sampled flips. Late1336–1480 inversion settles without subtitle/header collision; red-forward1509 and teal-up1530 reveals plus1566 second note remain readable. Model/game cuts219/220,663/664,963/964 and1269/1270 have separate states rather than a fabricated continuous path. Reserved fixed-caption area is clear in selected silent samples.',
 '07b':'Detailed aircraft canopy, tapered hull, swept thick wings/ailerons, paired nacelles/intakes, tail and projected top/side faces are readable in the742–1002 EX interval. Red-forward786, blue-wing852 and paired944 markers appear in narration order. Native camera changes are labelled. Late1891–2079 illustrative Rz+90 matrix, x→y/y→−x/z→z and coherent body/axis rotation remain readable; the wing clears the header/formula in the final sampled pose. Game geometry is not asserted as measured world axes.',
 '10b':'Aircraft hull/canopy/wings/engines and mounted landing gear pad/bolts/pivot/shaft/paired actuators/hose/ribs are clearly differentiated with projected face occlusion. Early arrow131 and later1578–1664 rotation retain the meaningful comparison.379/380 game transition,647 frozen enlargement,886 question and1276/1428 EX transitions are explicit. Late1734 red-x/teal-y/blue-z labels remain separate from objects and the reserved caption band. Frozen analysis remains explanation; no game input, physical centroid or internal world-axis measurement is inferred.'}
endpoints={'03b':(.169645,27.266667),'07b':(.149826,34.666667),'10b':(.162541,31.683333)}
rows=[]
for r in s['results']:
 assert sha(ROOT/r['output'])==r['outputSha256']
 assert r['wholeDecodeExitCode']==0 and r['extractExitCode']==0 and r['allFramePts1500Matched']
 assert r['preservedDecoderInputSha256']==r['newEncoderInputSha256']
 for x in r['samples']+r['boards']:assert sha(ROOT/x['path'])==x['sha256']
 start,end=endpoints[r['id']]
 rows.append(dict(scene=r['id'],video=r['output'],videoSha256=r['outputSha256'],samples=r['samples'],boards=r['boards'],allSamplesDirectlyRead=True,observation=notes[r['id']],normalPlayback=dict(tabId='110',videoElement='v'+r['id'],start=dict(duration=end,ended=False,muted=True,paused=False,rate=1,time=start),end=dict(duration=end,ended=True,muted=True,paused=True,rate=1,time=end))))
assert sum(len(x['samples']) for x in rows)==172 and sum(len(x['boards']) for x in rows)==44
proof=read(O/'narration-07b-guide-repair-execution-v1.json')
for x in proof['protectedInputs']+proof['results']:assert sha(ROOT/x['path'])==x['sha256']
out=O/'current34-mixed-detailed-direct-review-v1.json';assert not out.exists()
save(out,dict(recordedAt=now,execution=sp.relative_to(ROOT).as_posix(),executionSha256=sha(sp),rows=rows,allNewEncodedSamplesDirectlyRead=True,all172SamplesDirectlyRead=True,all44BoardsDirectlyRead=True,all3NormalStartEndObserved=True,normalPlaybackReviewed=True,captionReservedAreaClearInSelectedSamples=True,sourceDecoderInputPreservationVerified=True,preservationScope='3696 retained actual/frozen RGB frames match the prior decoder input fed to the new encoder. Lossy compressed output bytes or final decoded output bytes are not claimed identical.',reviewScope='All planned encoded selected EX/cut/moving samples directly read on44 boards; actual CUA1x muted running and ended endpoints for all3 scenes. This is bounded sampled review, not continuous observation of every intervening frame.',allInterveningFramesReviewed=False,continuousListeningApproved=False,humanPronunciationApproved=False,final244CaptionPixelsApproved=False,finalDeliveryApproved=False,newTts=0,newAsr=0,newMix=0,newImageGit=0))
cp=read(O/'latest-checkpoint.json');assert cp['activeOwnedWorkers']==0
cp.update(recordedAt=now,stage='current34-detailed-mixed-samples-and-normal-endpoints-reviewed',mixedDetailedReview=out.relative_to(ROOT).as_posix(),mixedDetailedReviewSha256=sha(out),next='Bind reviewed detailed subjects,overview and guides in37-piece assemblyV3; fresh resource then single final pairV3. All244 final caption/cut pixels and delivery remain pending.')
save(O/'latest-checkpoint.json',cp)
qp=B/'queue.json';raw=qp.read_bytes();q=read(qp);q['currentOrientationReview'].update(stage=cp['stage'],activeOwnedWorkers=0,mixedDetailedReview=cp['mixedDetailedReview'],next=cp['next']);q['updatedAt']=now;assert qp.read_bytes()==raw;save(qp,q)
print(json.dumps(dict(samples=172,boards=44,normalEndpoints=3,protected79=True,candidate=True,final244Pixels=False)))
