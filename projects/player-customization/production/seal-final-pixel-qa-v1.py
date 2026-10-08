"""Seal directly read current final pixels without repeating render/decode/extraction."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, time

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
W = BASE / 'final-v1'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
now = lambda: datetime.now(timezone.utc).isoformat()
rel = lambda p: p.relative_to(ROOT).as_posix()

def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def save(p, obj):
    tmp = p.with_name(p.name + f'.{os.getpid()}.writing')
    for attempt in range(60):
        try:
            tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', 'utf-8')
            os.replace(tmp, p)
            return
        except OSError:
            if attempt == 59:
                raise
            time.sleep(.15)

target = W / 'final-pixel-direct-review-v1.json'
assert not target.exists(), 'Read sealed current review; never repeat completed QA.'
progress_path = W / 'encoded-caption-qa-direct-progress.json'
progress = read(progress_path)
execution_path = W / 'encoded-caption-qa-execution.json'
execution = read(execution_path)
pair_path = W / 'review-pair-build.json'
pair = read(pair_path)
plan = read(W / 'plan.json')
asr = read(W / 'full-mix-asr-review.json')
assert asr['technicallyApproved'] and asr['all32WindowsDirectlyCompared'] and asr['all32CurrentMixedPcmSlicesReverified']
assert asr['planSha256'] == pair['planSha256'] and asr['currentMixedAacSha256'] == pair['sourceMixAacSha256']
assert not asr['unresolvedContentDefects'] and not asr['timestampAnomalies']
assert progress['directlyReadBoards'] == list(range(1, 329))
assert execution['exitCode'] == 0 and execution['sampleCount'] == 1965 and execution['boardCount'] == 328
assert pair['planSha256'] == sha(W / 'plan.json')
assert pair['captionAssSha256'] == sha(W / 'captions.ko.ass')
assert pair['identicalAacPayload'] and pair['inheritedSameAacLufs'] == -16.0
assert pair['inheritedSameAacTruePeakDbtp'] == -1.98
captioned = next(r for r in pair['records'] if '.captioned.' in r['path'])
assert progress['sourceSha256'] == execution['sourceSha256'] == captioned['sha256']
for record in pair['records']:
    assert sha(ROOT / record['path']) == record['sha256']
    assert record['wholeDecodeExitCode'] == 0
    assert record['exactPresentationClock'] == dict(timeBase='1/90000', count=36041, firstPts=0, lastPts=54060000, step=1500, allPacketPtsExact=True)
for row in [*execution['boards'], *execution['samples']]:
    assert sha(ROOT / row['path']) == row['sha256']

# The earlier review notes associated adjacent board panels incorrectly.
# Seven already-extracted full-resolution images were directly reread, all blank.
corrected = []
for frame, cue in [(372,3),(3052,33),(14434,168),(15836,185),(32682,382),(34603,405),(34846,408)]:
    row = next(r for r in execution['samples'] if r['frame'] == frame)
    assert row['visibleCueIds'] == []
    corrected.append(dict(frame=frame, sampleIndex=row['index'], path=row['path'], sha256=row['sha256'],
        previousBoardAssociation=f'cue{cue} retained', fullResolutionDirectObservation='No bottom caption is present. Expected blank is correct.',
        resolved=True, imageRegenerated=False, captionTimingChanged=False))

pending = ['Human whole-video listening/pronunciation', 'Final public rights', 'Original Nimbus Audio Library file verification',
    'Source-truncated membership handles', 'External backup', 'Automatic dubbing/optional CC propagation', 'Private-video pinned comment posting']
review = dict(schemaVersion=1, slug='player-customization', reviewedAt=now(), status='approved-current-final-technical-pixels-and-QA',
    source=captioned['path'], sourceSha256=captioned['sha256'], planSha256=pair['planSha256'], captionAssSha256=pair['captionAssSha256'],
    extraction=rel(execution_path), extractionSha256=sha(execution_path), directProgress=rel(progress_path),
    directProgressBeforeSealSha256=sha(progress_path), directlyReadBoards=list(range(1,329)), directlyReadSampleCount=1965,
    boards=[dict(index=r['index'],path=r['path'],sha256=r['sha256'],sampleIndices=r['sampleIndices'],directlyRead=True) for r in execution['boards']],
    all415KoreanCuesReviewed=True, all139CutsReviewed=True, all64PcmOnsetsReviewed=True, allCueCutIntersectionsReviewed=True,
    whiteProjectedDepthAndMotionReviewed=True, all16IndependentScenesReviewed=True, fixedCaptionCenter=[960,970],
    captionStyle='boxed-white-forest-v1', captionsReadableNoConfirmedUiCollision=True,
    originalIntro120FramesPreserved=True, originalMembership600FramesAnd12IdentitiesPreserved=True,
    exactMembershipTitle='멤버쉽가입 감사드립니다.', correctedAdjacentPanelAssociations=corrected, confirmedRemainingPixelDefects=[],
    measuredFrames=dict(actual=21193,explanation=14128,body=35321,final=36041,ratioErrorFrames=.4),
    wholeDecodeExitCodes=[0,0], exactPtsBoth=True, identicalAacPayload=True, lufs=-16.0, truePeakDbtp=-1.98,
    currentMixedAsrReview=rel(W/'full-mix-asr-review.json'), currentMixedAsrReviewSha256=sha(W/'full-mix-asr-review.json'),
    humanWholeListeningApproved=False, humanPronunciationApproved=False, publicRightsApproved=False,
    allFinalPixelsReviewed=True, qaApproved=True, collectApproved=True, privateUploadTechnicallyReady=True,
    collected=False, uploaded=False, completedPrivateVideo=False, newGitImages=0, imagesLocalOnly=True, pending=pending,
    scope='Technical approval from all328 directly read boards/1965 current final encoded samples plus existing closed pair/ASR evidence. Human approval and actual private platform settings are separate.')
save(target, review)
progress.update(status='all328-direct-read-boundary-reread-resolved-and-QA-sealed', reviewedAt=now(),
    allFinalPixelsReviewed=True, qaApproved=True, collectApproved=True, privateUploadApproved=False,
    edgeAudit=rel(target), edgeAuditConfirmedPixelDefects=0,
    correction='Prior one-frame persistence notes were incorrect associations with adjacent board panels. All seven original1920x1080 extracted frames directly reread blank; no media or caption timing changes.',
    pending=['Collection and actual private platform save/settings verification', *pending])
save(progress_path, progress)
manifest_path = BASE.parent / 'project.json'
manifest = read(manifest_path)
manifest.update(status='technical-QA-approved-awaiting-4file-collection-private-save', updatedAt=now())
manifest['visualStyle']['finalAnimatedPixelsReviewed'] = True
manifest['approvals'].update(finalPixels=True, qa=True, collected=False, privateUpload=False)
manifest['paths'].update(videoClean=next(r['path'] for r in pair['records'] if '.clean.' in r['path']),
    videoBurnedCaptions=captioned['path'], finalPixelReview=rel(target), qa=rel(target))
manifest['reviewWarnings'] = [x for x in manifest['reviewWarnings'] if not x.startswith('Conditional Warframe beginning-notice')]
manifest['reviewWarnings'].append('Warframe beginning notice present in directly read final overview; internal source/creator rights records preserved, final public rights still pending')
save(manifest_path, manifest)
cp_path = BASE / 'latest-checkpoint.json'
cp = read(cp_path)
cp.update(stage='technical-QA-approved-awaiting-4file-collection-private-save', recordedAt=now(), finalPixelReview=rel(target),
    allFinalPixels=True, qaApproved=True, collected=False, uploaded=False,
    nextAction='Collect reviewed clean/captioned/KOEN once, then single new private captioned upload/settings/actual platform checks/selective normal Git push.')
save(cp_path, cp)
qp = ROOT / 'production/batches/sakurai-planning-game-design/queue.json'
q = read(qp); item = next(x for x in q['items'] if x['slug'] == 'player-customization')
item.update(stage=cp['stage'], finalPixelReview=rel(target), allFinalPixels=True, qaApproved=True, collected=False, uploaded=False, nextAction=cp['nextAction'])
q['updatedAt'] = now(); save(qp, q)
print(json.dumps(dict(boards=328,samples=1965,confirmedPixelDefects=0,allFinalPixels=True,qaApproved=True,collected=False,uploaded=False)))
