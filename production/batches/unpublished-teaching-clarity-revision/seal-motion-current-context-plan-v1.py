"""Seal the directly read 52 quiet junctions and scope current queue records."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
R=ROOT/'projects/motion-sickness-games/production/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
now=lambda:datetime.now(timezone.utc).isoformat()
def save(p,v):
    t=p.with_name(p.name+'.writing');t.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
source=R/'current-mixed-independent-context-plan-proposed-v1.json';p=read(source)
assert len(p['contexts'])==66 and len(p['boundaries'])==52
reviewpath=R/'current-mixed-whole-asr-direct-review-v1.json';review=read(reviewpath)
assert review['all14WholeTextsDirectlyCompared'] and review['actualOuterExitCode']==0 and review['workerCurrentlyAlive']==False
assert p['mixAacSha256']==review['mixAacSha256'] and p['sourceSha256']==review['decodedAacSha256']
for v in p['boundaries']:
    assert v['rms8ms']<70 and abs(v['sourceSeconds']-v['nominalSeconds'])<.081
    v.update(directlyReviewed=True,wholeWordTimesAreApproximate=True,
      reviewNote='Full expected texts/whole word rows and all52 nearby word/actual raw PCM quiet-junction rows directly read; approximate ASR endings can extend into silence. Independent whole paragraph recognition remains pending.')
for v in p['contexts']:
    assert sha(ROOT/v['originalPcmPath'])==v['originalPcmSha256']
    assert v['startSample']<v['endSample'] and v['independentCompleteSentence']
dest=R/'current-mixed-independent-context-plan-v1.json';assert not dest.exists()
p.update(recordedAt=now(),wholeReview=reviewpath.relative_to(ROOT).as_posix(),wholeReviewSha256=sha(reviewpath),
  boundaryProposal=source.relative_to(ROOT).as_posix(),boundaryProposalSha256=sha(source),
  currentWholeWordsAndPcmBoundariesDirectlyCompared=True,all14WholeTextsDirectlyCompared=True,
  all66IndependentContextsDirectlyCompared=False,humanPronunciationApproved=False)
save(dest,p)
qp=B/'queue.json';raw=qp.read_text('utf-8-sig');q=json.loads(raw);e=q['execution']
assert e['currentSlug']=='motion-sickness-games' and e['ownedJob']['pid']==33428 and e['ownedJob']['exitCode']==0
oldfields=['actualNewVideoId','actualReplacementVideoId','baselineScheduleChanged','collectionEvidence','finalMediaAdoption','finalPixelReviewProgress','privateUploadReceipt']
assert e['actualReplacementVideoId']=='2kNMDlrwdU8'
history={k:e.pop(k) for k in oldfields if k in e}
e['lastCompletedReplacement']=dict(slug='game-math-polar-3d',historicalFields=history,
  scopeNote='Preserved prior completed polar delivery; these are not current motion-sickness delivery claims.')
e.update(actualNewVideoId=None,actualReplacementVideoId=None,baselineScheduleChanged=False,
  currentMixedWholeReview=reviewpath.relative_to(ROOT).as_posix(),independentContextPlan=dest.relative_to(ROOT).as_posix(),
  finalMediaAdoption=None,collectionEvidence=None,privateUploadReceipt=None,
  stage='current14-whole-directly-read-66-contexts-prepared',next='One CPU2/GPU0 current decoded-AAC66 complete contexts, direct every result, retime KOEN/captions/chapters/ending, guardedpair/finalpixels/collection/private/Git before replacing Oct12 schedule.')
item=next(v for v in q['items'] if v['slug']=='motion-sickness-games')
item.update(status=e['stage'],currentMixedWholeDirectReview=e['currentMixedWholeReview'],
  currentMixedIndependentContextPlan=e['independentContextPlan'],actualReplacementVideoId=None)
q['updatedAt']=now();assert qp.read_text('utf-8-sig')==raw;save(qp,q)
cp=read(R/'latest-checkpoint.json');cp.update(recordedAt=now(),stage=e['stage'],currentMixedWholeReview=e['currentMixedWholeReview'],
  independentContextPlan=e['independentContextPlan'],currentMixedAudioApproved=False,actualReplacementVideoId=None,
  allFinalPixelsApproved=False,qaApproved=False,next=e['next']);save(R/'latest-checkpoint.json',cp)
print(json.dumps(dict(whole14DirectlyCompared=True,quietJunctions52DirectlyRead=True,contextsPrepared=66,modelRun=False,currentActualId=None)))
