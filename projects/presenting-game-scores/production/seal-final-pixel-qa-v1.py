"""Refuse until all1015 encoded samples/170 boards are explicitly reviewed."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,time
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent;W=BASE/'final-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));now=lambda:datetime.now(timezone.utc).isoformat()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def save(p,d):
 t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf-8')
 for n in range(40):
  try:os.replace(t,p);return
  except OSError:
   if n==39:raise
   time.sleep(.15)
target=W/'final-pixel-direct-review-v1.json';assert not target.exists()
progress=read(W/'encoded-caption-qa-direct-progress.json');ex=read(W/'encoded-caption-qa-execution.json')
pair=read(W/'review-pair-build.json');plan=read(W/'plan.json');asr=read(W/'full-mix-asr-review.json')
assert asr['technicallyApproved'] and asr['all31WindowsDirectlyCompared'] and asr['all31CurrentMixedPcmSlicesReverified']
assert not asr['unresolvedContentDefects']
assert ex['exitCode']==ex['outerExitCode']==0 and ex['outerExitDirectlyObserved'] and ex['allActualPtsMatched']
assert (ex['sampleCount'],ex['boardCount'])==(1015,170)
assert progress['directlyReadBoards']==list(range(1,171)) and progress['reviewedSampleIndices']==list(range(1,1016))
assert not progress['unresolvedPixelDefects'] and all(b['directlyRead']for b in progress['reviewedBoards'])
captioned=next(x for x in pair['records']if '.captioned.'in x['path'])
assert captioned['sha256']==progress['sourceSha256']==ex['sourceSha256']
assert pair['planSha256']==asr['planSha256']==sha(W/'plan.json')
assert pair['sourceMixAacSha256']==asr['currentAacSha256'] and pair['identicalAacPayload']
assert abs(pair['inheritedSameAacLufs']+16)<=.6 and pair['inheritedSameAacTruePeakDbtp']<=-1.5
for x in pair['records']:
 assert sha(ROOT/x['path'])==x['sha256'] and x['wholeDecodeExitCode']==0 and x['allPacketPtsExact']
 assert (x['frames'],x['ptsStep'],x['timebase'])==(19052,1500,'1/90000')
for x in [*ex['samples'],*ex['boards'],*asr['windows']]:assert sha(ROOT/x['path'])==x['sha256']
anchors={a for s in ex['samples']for a in s['anchors']}
assert all(f'{tag}:{cue}'in anchors for cue in range(1,169)for tag in ['cue-first','cue-mid','cue-last'])
assert len({s['segment']for s in ex['samples']if s['role']=='explanation'})==12
assert {'branding','membership'}<={s['segment']for s in ex['samples']}
request=read(W/'encoded-caption-qa-request.json');assert request['allCueCutIntersectionsCovered'] and request['all651ApprovedInputAnchorsRetained']
pending=['Human whole-video listening/pronunciation; current08 기여/기어 and 읽게/잃게 remain unresolved recognition alternatives',
 'Final public rights','Original Nimbus Audio Library file','Source-truncated membership handles','External backup','Automatic dubbing/optional CC propagation','Private-video pinned comment posting']
review=dict(schemaVersion=1,slug='presenting-game-scores',reviewedAt=now(),source=captioned['path'],sourceSha256=captioned['sha256'],
 planSha256=sha(W/'plan.json'),captionAssSha256=sha(W/'captions.ko.ass'),
 directlyReadBoards=list(range(1,171)),directlyReadSampleCount=1015,boards=progress['reviewedBoards'],
 all168KoreanCuesReviewed=True,all24CutsReviewed=True,all40CompleteClauseOnsetsReviewed=True,all30PcmPlacementsReviewed=True,
 allCueCutIntersectionsReviewed=True,all12ProjectedExplanationMotionPartsReviewed=True,
 fixedCaptionCenter=[960,970],captionStyle='boxed-white-forest-v1',explanationPalette='research-black-v1',
 captionsReadableNoConfirmedUiCollision=True,originalIntro120FramesPreserved=True,originalMembership600FramesAnd12IdentitiesPreserved=True,
 exactMembershipTitle='멤버쉽가입 감사드립니다.',confirmedRemainingPixelDefects=[],
 measuredFrames=dict(actual=10999,explanation=7333,body=18332,final=19052,ratioErrorFrames=.2),
 wholeDecodeExitCodes=[0,0],exactPtsBoth=True,identicalAacPayload=True,lufs=pair['inheritedSameAacLufs'],truePeakDbtp=pair['inheritedSameAacTruePeakDbtp'],
 currentMixedAsrReview='projects/presenting-game-scores/production/final-v1/full-mix-asr-review.json',currentMixedAsrReviewSha256=sha(W/'full-mix-asr-review.json'),
 humanWholeListeningApproved=False,humanPronunciationApproved=False,publicRightsApproved=False,
 approvalScope='All planned encoded cue/cut/clause/PCM/depth-motion/identity samples, both whole decodes/exact PTS and identical AAC. Not human listening, phoneme correctness or final public rights.',
 allFinalPixelsReviewed=True,qaApproved=True,collectApproved=True,privateUploadTechnicallyReady=True,
 collected=False,uploaded=False,completedPrivateVideo=False,newGitImages=0,imagesLocalOnly=True,pending=pending)
save(target,review)
mp=BASE.parent/'project.json';m=read(mp);m.update(status='technical-QA-approved-awaiting-4file-collection-private-save',updatedAt=now())
m['approvals'].update(finalMixedAsr=True,allFinalPixels=True,render=True,qa=True,collected=False,uploaded=False)
m['paths'].update(finalPixelReview=target.relative_to(ROOT).as_posix(),qa=target.relative_to(ROOT).as_posix())
m['membershipOutro']['appliedToFinal']=True
m['finalRender']=dict(frames=19052,durationSeconds=19052/60,knownIssues=[],openItems=pending,technicalQaApproved=True)
save(mp,m)
cp=BASE/'latest-checkpoint.json';c=read(cp);c.update(stage=m['status'],recordedAt=now(),allFinalPixels=True,qa=True,collected=False,private=False,
 finalPixelReview=target.relative_to(ROOT).as_posix(),nextAction='Collect four reviewed files once; single new private captioned upload, saved settings/readback/CCoff pixels, then selective normal Git push.')
save(cp,c)
qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json'
for _ in range(15):
 raw=qp.read_text('utf-8-sig');q=json.loads(raw);i=next(x for x in q['items']if x['slug']=='presenting-game-scores')
 i.update(stage=c['stage'],finalPixelReview=c['finalPixelReview'],allFinalPixels=True,qaApproved=True,collected=False,uploaded=False,nextAction=c['nextAction'])
 i['checkpoints'].update(mix=True,render=True,qa=True,collected=False);q['updatedAt']=now()
 if qp.read_text('utf-8-sig')==raw:save(qp,q);break
 time.sleep(.15)
else:raise RuntimeError('Concurrent queue preserved')
print(json.dumps(dict(boards=170,samples=1015,allFinalPixels=True,qaApproved=True,collected=False,uploaded=False)))
