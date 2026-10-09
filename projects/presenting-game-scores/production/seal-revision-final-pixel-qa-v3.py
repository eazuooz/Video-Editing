"""Refuse final QA until every current encoded board was directly reviewed."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,time
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
W=BASE/'revision-balatro60-v2/final-v3'
read=lambda p:json.loads(p.read_text('utf-8-sig'));now=lambda:datetime.now(timezone.utc).isoformat()
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def save(p,d):
    t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
target=W/'final-pixel-direct-review-v3.json';assert not target.exists()
progress=read(W/'encoded-caption-qa-direct-progress.json');ex=read(W/'encoded-caption-qa-execution.json')
pair=read(W/'review-pair-build.json');plan=read(W/'plan.json');asr=read(W/'full-mix-asr-review.json')
assert asr['technicallyApproved'] and asr['all52WindowsDirectlyCompared'] and asr['all52CurrentMixedPcmSlicesReverified']
assert not asr['unresolvedContentDefects']
assert ex['exitCode']==ex['outerExitCode']==0 and ex['outerExitDirectlyObserved'] and ex['allActualPtsMatched']
assert (ex['sampleCount'],ex['boardCount'])==(1112,186)
assert progress['directlyReadBoards']==list(range(1,187)) and progress['reviewedSampleIndices']==list(range(1,1113))
assert not progress['unresolvedPixelDefects'] and all(b['directlyRead'] for b in progress['reviewedBoards'])
captioned=next(x for x in pair['records'] if '.captioned.' in x['path'])
assert captioned['sha256']==progress['sourceSha256']==ex['sourceSha256']
assert pair['planSha256']==asr['planSha256']==sha(W/'plan.json')
assert pair['sourceMixAacSha256']==asr['currentAacSha256'] and pair['identicalAacPayload']
assert abs(pair['inheritedSameAacLufs']+16)<=.6 and pair['inheritedSameAacTruePeakDbtp']<=-1.5
for x in pair['records']:
    assert sha(ROOT/x['path'])==x['sha256'] and x['wholeDecodeExitCode']==0 and x['allPacketPtsExact']
    assert (x['frames'],x['ptsStep'],x['timebase'])==(19988,1500,'1/90000')
for x in [*ex['samples'],*ex['boards'],*asr['windows']]:assert sha(ROOT/x['path'])==x['sha256']
anchors={a for s in ex['samples'] for a in s['anchors']}
assert all(f'{tag}:{cue}' in anchors for cue in range(1,176) for tag in ['cue-first','cue-mid','cue-last'])
assert len({s['segment'] for s in ex['samples'] if s['role']=='explanation'})==13
assert {'branding','membership'}<={s['segment'] for s in ex['samples']}
request=read(W/'encoded-caption-qa-request.json')
assert request['allCueCutIntersectionsCovered'] and request['allCurrentApprovedInputAnchorsRetained']
assert request['pcmPlacements']==len(plan['voicePlacements'])==31
assert (plan['actualFrames'],plan['explanationFrames'],plan['balatroFrames'],plan['tetrisFrames'])==(11561,7707,6936,4625)
assert abs(plan['bodyRatioFrameError'])<=1 and abs(plan['gameRatioFrameError'])<=1
pending=['Human whole-video listening/pronunciation, including recorded current recognition alternatives',
    'Final public rights','Original Nimbus Audio Library file','Source-truncated membership handles',
    'External backup','Automatic dubbing/optional CC propagation','Pinned comment posting when comments become available']
review=dict(schemaVersion=3,slug='presenting-game-scores',reviewedAt=now(),source=captioned['path'],sourceSha256=captioned['sha256'],
    planSha256=sha(W/'plan.json'),captionAssSha256=sha(W/'captions.ko.ass'),directlyReadBoards=list(range(1,187)),
    directlyReadSampleCount=1112,boards=progress['reviewedBoards'],all175KoreanCuesReviewed=True,all31CutsReviewed=True,
    all42CompleteClauseOnsetsReviewed=True,all31PcmPlacementsReviewed=True,allCueCutIntersectionsReviewed=True,
    all13ProjectedExplanationMotionPartsReviewed=True,fixedCaptionCenter=[960,970],captionStyle='boxed-white-forest-v1',
    explanationPalette='research-black-v1',captionsReadableNoConfirmedUiCollision=True,
    originalIntro120FramesPreserved=True,originalMembership600FramesAnd12IdentitiesPreserved=True,
    exactMembershipTitle='멤버쉽가입 감사드립니다.',confirmedRemainingPixelDefects=[],
    measuredFrames=dict(actual=11561,explanation=7707,body=19268,final=19988,balatro=6936,tetris=4625,
        bodyRatioErrorFrames=plan['bodyRatioFrameError'],gameRatioErrorFrames=plan['gameRatioFrameError']),
    wholeDecodeExitCodes=[0,0],exactPtsBoth=True,identicalAacPayload=True,lufs=pair['inheritedSameAacLufs'],
    truePeakDbtp=pair['inheritedSameAacTruePeakDbtp'],currentMixedAsrReview=(W/'full-mix-asr-review.json').relative_to(ROOT).as_posix(),
    currentMixedAsrReviewSha256=sha(W/'full-mix-asr-review.json'),humanWholeListeningApproved=False,
    humanPronunciationApproved=False,publicRightsApproved=False,
    approvalScope='Every planned encoded cue/cut/clause/PCM/depth-motion/identity sample, both whole decodes/exact PTS and identical AAC; not human listening or public rights.',
    allFinalPixelsReviewed=True,qaApproved=True,collectApproved=True,privateUploadTechnicallyReady=True,
    collected=False,uploaded=False,completedPrivateVideo=False,newGitImages=0,imagesLocalOnly=True,pending=pending)
save(target,review)
mp=BASE.parent/'project.json';m=read(mp)
if 'baselinePathsBeforeRevisionDelivery' not in m:m['baselinePathsBeforeRevisionDelivery']=dict(m['paths'])
m.update(status='revision-technical-QA-approved-awaiting-4file-collection-private-save',updatedAt=now())
m['approvals'].update(finalMixedAsr=True,allFinalPixels=True,render=True,qa=True,collected=False,uploaded=False)
m['paths'].update(audioMix=(W/'final-mix.m4a').relative_to(ROOT).as_posix(),narration=(W/'narration-timed.wav').relative_to(ROOT).as_posix(),
    captionsKo=(W/'presenting-game-scores.ko.srt').relative_to(ROOT).as_posix(),captionsEn=(W/'presenting-game-scores.en.srt').relative_to(ROOT).as_posix(),
    videoClean=(W/'presenting-game-scores.clean.mp4').relative_to(ROOT).as_posix(),videoBurnedCaptions=captioned['path'],
    finalPixelReview=target.relative_to(ROOT).as_posix(),qa=target.relative_to(ROOT).as_posix(),
    captionAlignmentReview=(W/'semantic-caption-alignment-review-v3.json').relative_to(ROOT).as_posix())
m['currentRevision']['checkpoints'].update(finalMixedAsr=True,pair=True,allFinalPixels=True,qa=True,collected=False)
m['currentRevision'].update(finalMixedAsrApproved=True,allFinalPixels=True,finalPixelReview=target.relative_to(ROOT).as_posix())
m['membershipOutro']['appliedToFinal']=True
m['finalRender']=dict(frames=19988,durationSeconds=19988/60,knownIssues=[],openItems=pending,technicalQaApproved=True)
save(mp,m)
cp=BASE/'latest-checkpoint.json';c=read(cp);c.update(stage=m['status'],recordedAt=now(),allFinalPixels=True,qa=True,collected=False,private=False,
    finalPixelReview=target.relative_to(ROOT).as_posix(),nextAction='Collect the four current revision files once, single new private captioned upload/settings/readback/CCoff pixels, selective Git push, then authorized matching09KST schedule.')
save(cp,c)
qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json'
for _ in range(15):
    raw=qp.read_text('utf-8-sig');q=json.loads(raw);i=next(x for x in q['items'] if x['slug']=='presenting-game-scores')
    i.update(stage=c['stage'],finalPixelReview=c['finalPixelReview'],allFinalPixels=True,qaApproved=True,collected=False,uploaded=False,nextAction=c['nextAction'])
    i['checkpoints'].update(mix=True,render=True,qa=True,collected=False);q['updatedAt']=now()
    if qp.read_text('utf-8-sig')==raw:save(qp,q);break
    time.sleep(.15)
else:raise RuntimeError('Concurrent queue preserved')
print(json.dumps(dict(boards=186,samples=1112,allFinalPixels=True,qaApproved=True,collected=False,uploaded=False)))
