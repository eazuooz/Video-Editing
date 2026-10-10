"""Seal actual complete planned final-pixel review; no human/rights inference."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent;W=BASE/'final-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));rel=lambda p:p.relative_to(ROOT).as_posix();now=lambda:datetime.now(timezone.utc).isoformat()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf-8')
dest=W/'final-pixel-direct-review-v1.json';assert not dest.exists(),'Preserve actual completed final QA'
notes_path=W/'encoded-caption-qa-direct-notes-v1.json';notes=read(notes_path)
ex=read(W/'encoded-caption-qa-execution.json');pair=read(W/'review-pair-build.json');pair_ex=read(W/'review-pair-execution.json');request=read(W/'encoded-caption-qa-request.json');plan=read(W/'plan.json');asr_path=W/'full-mix-asr-review.json';asr=read(asr_path)
assert ex['exitCode']==ex['outerExitCode']==pair_ex['exitCode']==pair_ex['outerExitCode']==0
assert ex['outerExitDirectlyObserved'] and ex['sessionClosed'] and pair_ex['outerExitDirectlyObserved'] and pair_ex['sessionClosed']
assert ex['allActualPtsMatched'] and (ex['sampleCount'],ex['boardCount'])==(1266,211)
assert sorted(b for g in notes['groups']for b in g['boards'])==list(range(1,212))
assert notes['allPlannedSamplesDirectlyRead'] and not notes['unresolvedPixelDefects']
assert asr['technicallyApproved'] and asr['all49WindowsDirectlyCompared'] and asr['all49CurrentMixedPcmSlicesReverified'] and not asr['unresolvedContentDefects']
assert sha(W/'plan.json')==pair['planSha256']==asr['planSha256']==request['planSha256']
assert sha(W/'final-mix.wav')==asr['currentMixedAudioSha256']
assert sha(W/'final-mix.m4a')==asr['currentAacSha256']==pair['sourceMixAacSha256']
assert pair['identicalAacPayload'] and abs(pair['inheritedSameAacLufs']+16)<=.6 and pair['inheritedSameAacTruePeakDbtp']<=-1.5
captioned=next(x for x in pair['records']if '.captioned.'in x['path'])
assert ex['sourceSha256']==captioned['sha256']
for r in pair['records']:
 assert sha(ROOT/r['path'])==r['sha256'] and r['wholeDecodeExitCode']==0 and r['allPacketPtsExact']
 assert (r['frames'],r['ptsStep'],r['timebase'])==(23397,1500,'1/90000')
for r in [*ex['samples'],*ex['boards'],*asr['windows']]:assert sha(ROOT/r['path'])==r['sha256']
assert all(r['decodedPts']==r['frame']*1500 for r in ex['samples'])
anchors={a for r in ex['samples']for a in r['anchors']}
assert all(f'{tag}:{cue}'in anchors for cue in range(1,202)for tag in ['cue-first','cue-mid','cue-last'])
assert len({r['segment']for r in ex['samples']if r['role']=='explanation'})==17
assert {'branding','membership'}<={r['segment']for r in ex['samples']}
assert request['allCueCutIntersectionsCovered'] and request['all845ApprovedInputAnchorsRetained']
assert request['completeClauseOnsets']==37 and request['pcmPlacements']==len(plan['voicePlacements'])==17
assert (plan['actualFrames'],plan['explanationFrames'],plan['bodyFrames'],plan['finalFrames'])==(13606,9071,22677,23397) and abs(plan['bodyRatioFrameError'])<=1
pending=['Human whole-video listening/pronunciation, including recognizer alternatives','Final public rights','Original Nimbus Audio Library file','Source-truncated membership handles','External backup','Automatic dubbing/optional CC propagation','Pinned comment when comments become available']
proof=dict(schemaVersion=1,slug='character-parameters',reviewedAt=now(),source=captioned['path'],sourceSha256=captioned['sha256'],planSha256=sha(W/'plan.json'),captionAssSha256=sha(W/'captions.ko.ass'),
 manualNotes=rel(notes_path),manualNotesSha256=sha(notes_path),groups=notes['groups'],directlyReadBoards=list(range(1,212)),directlyReadSampleCount=1266,
 all201KoreanCuesReviewed=True,all41CutsReviewed=True,all37CompleteClauseOnsetsReviewed=True,all17PcmPlacementsReviewed=True,allCueCutIntersectionsReviewed=True,all17ProjectedExplanationMotionPartsReviewed=True,
 fixedCaptionCenter=[960,970],captionStyle='boxed-white-forest-v1',explanationPalette='research-black-v1',confirmedRemainingPixelDefects=[],
 originalIntro120FramesPreserved=True,originalMembership600FramesAnd12IdentitiesPreserved=True,exactMembershipTitle='멤버쉽가입 감사드립니다.',
 wholeDecodeExitCodes=[0,0],exactPtsBoth=True,identicalAacPayload=True,lufs=pair['inheritedSameAacLufs'],truePeakDbtp=pair['inheritedSameAacTruePeakDbtp'],
 currentMixedAsrReview=rel(asr_path),currentMixedAsrReviewSha256=sha(asr_path),measuredFrames=dict(actual=13606,explanation=9071,body=22677,final=23397,bodyRatioErrorFrames=plan['bodyRatioFrameError']),
 sourceLimitations=notes.get('sourceLimitations',[]),allContinuousFramesReviewed=False,humanWholeListeningApproved=False,humanPronunciationApproved=False,publicRightsApproved=False,
 approvalScope='Every planned current encoded cue/cut/clause/PCM/depth-motion/identity sample and both whole decodes/exact PTS/AAC; not human continuous listening or rights approval.',
 allFinalPixelsReviewed=True,qaApproved=True,collectApproved=True,privateUploadTechnicallyReady=True,collected=False,uploaded=False,completedPrivateVideo=False,newGitImages=0,imagesLocalOnly=True,pending=pending)
save(dest,proof)
mp=BASE.parent/'project.json';m=read(mp);m.update(status='technical-QA-approved-awaiting-4file-collection-private-save',updatedAt=now())
m['approvals'].update(finalMixedAsr=True,allFinalPixels=True,render=True,qa=True,collected=False,uploaded=False)
m['paths'].update(finalPixelReview=rel(dest),qa=rel(dest));m['membershipOutro']['appliedToFinal']=True
m['review'].update(mixedAsr=True,allFinalPixels=True,qa=True,humanListening=False,publicRights=False)
m['audio'].update(mixStatus='current37-PCM-complete-final-mix-and49-contexts-reviewed',measuredFinalAacLufs=pair['inheritedSameAacLufs'],measuredFinalAacTruePeakDbtp=pair['inheritedSameAacTruePeakDbtp'])
m['editing']['exampleInterleaving']['reviewStatus']='measured-source-actions-and-all-planned-final-cue-cut-pixels-reviewed'
m['finalRender']=dict(frames=23397,durationSeconds=389.95,knownIssues=[],openItems=pending,technicalQaApproved=True);save(mp,m)
cp=read(BASE/'latest-checkpoint.json');cp.update(stage=m['status'],recordedAt=now(),mixedAsrApproved=True,allFinalPixelsApproved=True,allFinalPixels=True,qa=True,collected=False,private=False,finalPixelReview=rel(dest),publishingPreparation='projects/character-parameters/publishing/publishing-text-preparation-v2.json',selectedInputDirectReview=plan['selectedInputReview'],nextAction='Collect4files once, new private reviewed captioned upload/settings/CCoff, selective normal Git push, actual matching future09KST schedule.');save(BASE/'latest-checkpoint.json',cp)
qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qp);i=next(x for x in q['items']if x['slug']=='character-parameters');i.update(stage=cp['stage'],mixedAsrApproved=True,allFinalPixelsApproved=True,allFinalPixels=True,qa=True,qaApproved=True,collected=False,uploaded=False,finalPixelReview=rel(dest),nextAction=cp['nextAction']);i['checkpoints'].update(mix=True,render=True,qa=True,collected=False);q['updatedAt']=now();save(qp,q)
print(json.dumps(dict(boards=211,samples=1266,qaApproved=True,collected=False,uploaded=False)))
