from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,os
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
R=ROOT/'projects/motion-sickness-games/production/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for chunk in iter(lambda:f.read(1048576),b''):h.update(chunk)
 return h.hexdigest()
def save(p,v):
 t=p.with_name(p.name+'.writing');t.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
now=datetime.now(timezone.utc).isoformat()
pair=read(R/'final-pair-execution-v2.json');ps=read(R/'final-pair-execution-v2.session.json')
ex=read(R/'final-pixel-execution-v2.json');es=read(R/'final-pixel-execution-v2.session.json')
assert pair['exitCode']==ex['exitCode']==ps['actualOuterExitCode']==es['actualOuterExitCode']==0
assert not ps['workerCurrentlyAlive'] and not es['workerCurrentlyAlive']
ixp=ROOT/ex['index'];ix=read(ixp);cmp=read(ixp.parent/'v1-decoded-sample-comparison.json')
prior=read(R/'final-pixel-direct-review-v1.json');oldIx=read(ROOT/prior['index'])
assert sha(ROOT/prior['index'])==prior['indexSha256'] and prior['all1180SamplesDirectlyRead']
obs=read(R/'final-board-observations-v2.json')
required=[int(Path(x['path']).stem.split('-')[-1]) for x in cmp['currentBoardsRequired']]
assert sorted(x['board'] for x in obs['currentBoardNotes'])==required and obs['all12CurrentRequiredBoardsActuallyDirectlyRead']
assert len(ix['samples'])==1180 and len(ix['boards'])==197 and ix['sourceSha256']==pair['pair'][1]['sha256']==cmp['sourceSha256']
assert sha(ROOT/ix['source'])==ix['sourceSha256']
reviewed={i for x in cmp['currentBoardsRequired'] for i in x['sampleIndices']}
reused=0;fresh=0
for x,old in zip(ix['samples'],oldIx['samples']):
 assert x['index']==old['index'] and x['frame']==old['frame'] and x['pts']==x['frame']*1500
 assert sha(ROOT/x['path'])==x['sha256']
 assert x['priorSampleSha256']==old['sha256'] and sha(ROOT/old['path'])==old['sha256']
 if x['reusedPriorDirectPixelObservation']:
  assert x['decodedPngByteIdenticalToReviewedV1'] and x['sha256']==old['sha256'];reused+=1
 else:
  assert x['currentDirectPixelReviewRequired'] and x['index'] in reviewed;fresh+=1
for x in ix['boards']:assert sha(ROOT/x['path'])==x['sha256']
assert reused==1120 and fresh==60 and cmp['byteIdentical']==1120
critical={6573,6747,6922,20400,20524}
assert {x['frame'] for x in obs['fullSizeFollowup']}==critical
assert all(x['directlyRead'] and sha(ROOT/x['path'])==x['sha256'] for x in obs['fullSizeFollowup'])
targets=read(R/'two-target-repair-direct-review-v3.json');assert targets['normalSpeedTargetMotionApproved'] and not targets['unresolved']
p=R/'final-pixel-direct-review-v2.json';assert not p.exists()
save(p,dict(schemaVersion=1,recordedAt=now,status='all-listed-current-final-cue-cut-pixels-reviewed',
 source=ix['source'],sourceSha256=ix['sourceSha256'],index=ex['index'],indexSha256=sha(ixp),
 currentSamples=1180,currentBoards=197,reusedByteIdenticalPriorDirectObservations=reused,currentDirectlyReadRequiredSamples=fresh,
 currentDirectlyReadBoards=len(required),currentDirectlyReadBoardSampleCount=len(reviewed),
 allListedPixelsDirectlyReviewedCurrentOrByteIdenticalPrior=True,allFinalCueCutPixelsApproved=True,
 allExactAbsolutePtsVerified=True,unresolved=[],resolvedHistoricalFindings=prior['unresolvedFindings'],
 currentObservation='final-board-observations-v2.json',priorDirectReview='final-pixel-direct-review-v1.json',
 unchangedOther18Pieces=True,originalIntroMemberPreserved=True,allIntermediateFramesViewed=False,
 humanListeningApproved=False,humanPronunciationApproved=False,publicRightsApproved=False,newGitImages=0))
cp=read(R/'latest-checkpoint.json');cp.update(recordedAt=now,stage='final-v2-cue-cut-pixels-approved; whole-normal-flow-running',
 ownedJob=None,allFinalPixelsApproved=True,qaApproved=False,finalPixelReview=p.relative_to(ROOT).as_posix(),
 next='Finish actual current normal1x playback and inspect selected transitions; then adopt/collect verified current pair. No new upload/Git/schedule yet.')
save(R/'latest-checkpoint.json',cp)
qp=B/'queue.json';before=qp.read_text('utf-8-sig');q=json.loads(before)
q['execution'].update(stage=cp['stage'],ownedJob=None,next=cp['next'])
item=next(v for v in q['items'] if v['slug']=='motion-sickness-games');item.update(status=cp['stage'],currentExecution=None)
item['review']['allFinalPixelsPassed']=True;q['updatedAt']=now
assert qp.read_text('utf-8-sig')==before;save(qp,q)
print(json.dumps(dict(currentFinalPixelApproval=True,samples=1180,currentDirectRead=60,byteIdenticalReused=1120,boardsDirectRead=12,unresolved=0,flowStillPending=True)))
