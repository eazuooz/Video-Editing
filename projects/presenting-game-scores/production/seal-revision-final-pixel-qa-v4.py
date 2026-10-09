"""Seal actual corrected-pair QA without replacing preserved audio evidence."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, time
ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
B = BASE / 'revision-balatro60-v2'
W = B / 'final-v4'
OLD = B / 'final-v3'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
now = lambda: datetime.now(timezone.utc).isoformat()
rel = lambda p: p.relative_to(ROOT).as_posix()
def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''): h.update(chunk)
    return h.hexdigest()
def save(p, data):
    t = p.with_name(p.name + f'.{os.getpid()}.writing')
    t.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', 'utf-8')
    os.replace(t, p)
target = W / 'final-pixel-direct-review-v4.json'
assert not target.exists()
progress = read(W / 'encoded-caption-qa-direct-progress.json')
ex = read(W / 'encoded-caption-qa-execution.json')
pair = read(W / 'review-pair-build.json')
plan = read(W / 'plan.json')
previous_plan = read(OLD / 'plan.json')
asr_path = OLD / 'full-mix-asr-review.json'
asr = read(asr_path)
audio = read(W / 'audio-identity-provenance.json')
identity = read(W / 'unchanged-pixel-identity.json')
changed = read(W / 'corrected-cut-encoded-direct-review.json')
execution = read(W / 'source-only-pair-execution.json')
assert execution['exitCode'] == execution['actualOuterExitCode'] == 0 and execution['outerExitDirectlyObserved']
assert ex['exitCode'] == ex['outerExitCode'] == 0 and ex['outerExitDirectlyObserved']
assert ex['allActualPtsMatched'] and (ex['sampleCount'], ex['boardCount']) == (1112, 186)
assert progress['directlyReadBoards'] == list(range(1, 187))
assert progress['reviewedSampleIndices'] == list(range(1, 1113))
assert not progress['unresolvedPixelDefects'] and all(b['directlyRead'] for b in progress['reviewedBoards'])
assert identity['all18848OutsideCutDecodedFramesIdentical']
assert changed['correctedFactualClaimApproved'] and changed['directlyReadChangedSamples'] == 66
assert [b['index'] for b in changed['directlyReadBoards']] == list(range(30, 42))
assert not changed['captionUiCollisions']
assert audio['voicePlacementsIdentical'] and plan['voicePlacements'] == previous_plan['voicePlacements']
assert audio['planSha256'] == pair['planSha256'] == sha(W / 'plan.json')
assert audio['previousPlanSha256'] == asr['planSha256'] == sha(OLD / 'plan.json')
assert audio['currentMixedAsrReviewSha256'] == sha(asr_path)
assert audio['all52CurrentIdenticalAudioWindowsApproved'] and audio['all52WindowsDirectlyCompared']
assert asr['technicallyApproved'] and asr['all52WindowsDirectlyCompared'] and asr['all52CurrentMixedPcmSlicesReverified']
assert not asr['unresolvedContentDefects']
assert sha(ROOT / audio['wavPath']) == audio['wavSha256'] == asr['currentMixedAudioSha256']
assert sha(ROOT / audio['aacPath']) == audio['aacSha256'] == pair['sourceMixAacSha256'] == asr['currentAacSha256']
assert pair['identicalAacPayload'] and abs(pair['inheritedSameAacLufs'] + 16) <= .6
assert pair['inheritedSameAacTruePeakDbtp'] <= -1.5
captioned = next(x for x in pair['records'] if '.captioned.' in x['path'])
assert captioned['sha256'] == progress['sourceSha256'] == ex['sourceSha256'] == changed['sourceSha256']
for x in pair['records']:
    assert sha(ROOT / x['path']) == x['sha256'] and x['wholeDecodeExitCode'] == 0 and x['allPacketPtsExact']
    assert (x['frames'], x['ptsStep'], x['timebase']) == (19988, 1500, '1/90000')
for x in [*ex['samples'], *ex['boards'], *asr['windows']]: assert sha(ROOT / x['path']) == x['sha256']
anchors = {a for s in ex['samples'] for a in s['anchors']}
assert all(f'{tag}:{cue}' in anchors for cue in range(1, 176) for tag in ['cue-first', 'cue-mid', 'cue-last'])
assert len({s['segment'] for s in ex['samples'] if s['role'] == 'explanation'}) == 13
assert {'branding', 'membership'} <= {s['segment'] for s in ex['samples']}
request = read(OLD / 'encoded-caption-qa-request.json')
assert request['allCueCutIntersectionsCovered'] and request['allCurrentApprovedInputAnchorsRetained']
assert request['pcmPlacements'] == len(plan['voicePlacements']) == 31
assert (plan['actualFrames'], plan['explanationFrames'], plan['balatroFrames'], plan['tetrisFrames']) == (11561, 7707, 6936, 4625)
assert abs(plan['bodyRatioFrameError']) <= 1 and abs(plan['gameRatioFrameError']) <= 1
for name in ['captions.ko.ass', 'presenting-game-scores.ko.srt', 'presenting-game-scores.en.srt']:
    assert sha(W / name) == sha(OLD / name)
alignment_path = W / 'semantic-caption-alignment-review-v4.json'
alignment = read(OLD / 'semantic-caption-alignment-review-v3.json')
assert alignment['approved'] and alignment['manualSemanticReview'] and alignment['allParagraphTextsRetained']
for track in alignment['captions']:
    source = ROOT / track['path']
    dest = W / source.name
    assert sha(source) == sha(dest) == track['sha256']
    track['path'] = rel(dest)
alignment.update(sourceOnlyPathAdoptionAt=now(), sourceOnlyPathAdoptionBasis='Identical KO/EN files and unchanged paragraph/voice clock', preservedDirectReview=rel(OLD / 'semantic-caption-alignment-review-v3.json'))
save(alignment_path, alignment)
pending = ['Human whole-video listening/pronunciation, including recorded recognition alternatives', 'Final public rights', 'Original Nimbus Audio Library file', 'Source-truncated membership handles', 'External backup', 'Automatic dubbing/optional CC propagation', 'Pinned comment posting when comments become available']
review = dict(schemaVersion=4, slug='presenting-game-scores', reviewedAt=now(), source=captioned['path'], sourceSha256=captioned['sha256'], planSha256=sha(W / 'plan.json'), captionAssSha256=sha(W / 'captions.ko.ass'), directlyReadBoards=list(range(1,187)), directlyReadSampleCount=1112, boards=progress['reviewedBoards'], all175KoreanCuesReviewed=True, all31CutsReviewed=True, all42CompleteClauseOnsetsReviewed=True, all31PcmPlacementsReviewed=True, allCueCutIntersectionsReviewed=True, all13ProjectedExplanationMotionPartsReviewed=True, fixedCaptionCenter=[960,970], captionStyle='boxed-white-forest-v1', explanationPalette='research-black-v1', captionsReadableNoConfirmedUiCollision=True, originalIntro120FramesPreserved=True, originalMembership600FramesAnd12IdentitiesPreserved=True, exactMembershipTitle='멤버쉽가입 감사드립니다.', confirmedRemainingPixelDefects=[], measuredFrames=dict(actual=11561, explanation=7707, body=19268, final=19988, balatro=6936, tetris=4625, bodyRatioErrorFrames=plan['bodyRatioFrameError'], gameRatioErrorFrames=plan['gameRatioFrameError']), wholeDecodeExitCodes=[0,0], exactPtsBoth=True, identicalAacPayload=True, lufs=pair['inheritedSameAacLufs'], truePeakDbtp=pair['inheritedSameAacTruePeakDbtp'], currentMixedAsrReview=rel(asr_path), currentMixedAsrReviewSha256=sha(asr_path), identicalAudioProvenance=rel(W/'audio-identity-provenance.json'), changedCutDirectReview=rel(W/'corrected-cut-encoded-direct-review.json'), unchangedDecodedPixelIdentity=rel(W/'unchanged-pixel-identity.json'), historicalDefectPreserved=True, humanWholeListeningApproved=False, humanPronunciationApproved=False, publicRightsApproved=False, approvalScope='Every planned current encoded cue/cut/clause/PCM/depth-motion/identity sample, exact unchanged-pixel reuse, both whole decodes/exact PTS and identical AAC; not whole human listening or public rights.', allFinalPixelsReviewed=True, qaApproved=True, collectApproved=True, privateUploadTechnicallyReady=True, collected=False, uploaded=False, completedPrivateVideo=False, newGitImages=0, imagesLocalOnly=True, pending=pending)
save(target, review)
mp = BASE.parent / 'project.json'
m = read(mp)
if 'baselinePathsBeforeRevisionDelivery' not in m: m['baselinePathsBeforeRevisionDelivery'] = dict(m['paths'])
m.update(status='revision-technical-QA-approved-awaiting-4file-collection-private-save', updatedAt=now())
m['approvals'].update(finalMixedAsr=True, allFinalPixels=True, render=True, qa=True, collected=False, uploaded=False)
m['paths'].update(audioMix=audio['aacPath'], narration=rel(OLD/'narration-timed.wav'), captionsKo=rel(W/'presenting-game-scores.ko.srt'), captionsEn=rel(W/'presenting-game-scores.en.srt'), videoClean=rel(W/'presenting-game-scores.clean.mp4'), videoBurnedCaptions=captioned['path'], finalPixelReview=rel(target), qa=rel(target), captionAlignmentReview=rel(alignment_path))
m['editing'].update(finalPlan=rel(W/'plan.json'), finalPlanSha256=sha(W/'plan.json'), actualFrames=11561, explanationFrames=7707, bodyFrames=19268, finalFrames=19988, balatroFrames=6936, tetrisFrames=4625, actualGameplaySeconds=11561/60, actualExplanationSeconds=7707/60, actualGameplayShare=11561/19268, actualCommercialGameplaySeconds=11561/60, bodyRatioFrameError=plan['bodyRatioFrameError'], gameRatioFrameError=plan['gameRatioFrameError'], timingStatus='current-balanced-source-corrected-final-QA-approved')
m['currentRevision']['checkpoints'].update(finalMixedAsr=True, pair=True, allFinalPixels=True, qa=True, collected=False)
m['currentRevision'].update(finalPlan=rel(W/'plan.json'), finalPlanSha256=sha(W/'plan.json'), finalMixedAsrApproved=True, allFinalPixels=True, finalPixelReview=rel(target))
m['video']['durationSeconds'] = 19988/60
m['audio']['mixStatus'] = 'current-balanced-identical-final-mix-and-full-ASR-approved'
m['membershipOutro']['appliedToFinal'] = True
m['finalRender'] = dict(frames=19988, durationSeconds=19988/60, knownIssues=[], openItems=pending, technicalQaApproved=True)
save(mp, m)
cp = BASE / 'latest-checkpoint.json'
c = read(cp)
c.update(stage=m['status'], recordedAt=now(), allFinalPixels=True, qa=True, collected=False, private=False, finalPixelReview=rel(target), revisionFinalPlan=rel(W/'plan.json'), currentApprovalScope='Current source-corrected balanced revision technical QA; human listening/rights remain pending.', nextAction='Collect four current files once; single new private captioned upload/settings/readback/CCoff pixels; selective Git push; authorized matching09KST schedule.')
c['revisionCheckpoints'].update(finalMixedAsr=True, pair=True, allFinalPixels=True, qa=True, collected=False)
save(cp, c)
qp = ROOT / 'production/batches/sakurai-planning-game-design/queue.json'
for _ in range(15):
    raw = qp.read_text('utf-8-sig'); q = json.loads(raw)
    i = next(x for x in q['items'] if x['slug'] == 'presenting-game-scores')
    i.update(stage=c['stage'], finalPixelReview=rel(target), allFinalPixels=True, qaApproved=True, collected=False, uploaded=False, nextAction=c['nextAction'])
    i['checkpoints'].update(mix=True, render=True, qa=True, collected=False)
    q['updatedAt'] = now()
    if qp.read_text('utf-8-sig') == raw: save(qp,q); break
    time.sleep(.15)
else: raise RuntimeError('Concurrent queue preserved')
print(json.dumps(dict(boards=186, samples=1112, allFinalPixels=True, qaApproved=True, collected=False, uploaded=False)))
