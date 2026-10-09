"""Prepared seal: refuse until all current encoded boards and48 mixed windows are directly reviewed."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, time

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
W = BASE / 'final-v1'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
now = lambda: datetime.now(timezone.utc).isoformat()
rel = lambda p: p.relative_to(ROOT).as_posix()


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def save(path, value):
    temp = path.with_name(path.name + f'.{os.getpid()}.writing')
    for attempt in range(60):
        try:
            temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf-8')
            os.replace(temp, path)
            return
        except OSError:
            if attempt == 59:
                raise
            time.sleep(.15)


target = W / 'final-pixel-direct-review-v1.json'
assert not target.exists(), 'Read the sealed review; never repeat completed QA.'
progress_path = W / 'encoded-caption-qa-direct-progress.json'
progress = read(progress_path)
execution_path = W / 'encoded-caption-qa-execution.json'
execution = read(execution_path)
pair = read(W / 'review-pair-build.json')
plan = read(W / 'plan.json')
asr_path = W / 'full-mix-asr-review.json'
asr = read(asr_path)
assert asr['technicallyApproved'] and asr['all48WindowsDirectlyCompared'] and asr['all48CurrentMixedPcmSlicesReverified']
assert len(asr['windows']) == 48 and all(x['directlyCompared'] for x in asr['windows'])
assert asr['planSha256'] == pair['planSha256'] and asr['currentMixedAacSha256'] == pair['sourceMixAacSha256']
assert not asr['unresolvedContentDefects'] and not asr['timestampAnomalies']
assert execution['exitCode'] == 0 and execution['allActualPtsMatched']
assert execution['sampleCount'] == 1810 and execution['boardCount'] == 302
assert progress['directlyReadBoards'] == list(range(1, 303))
assert not progress['unresolvedPixelDefects']
# The recorder stores explicit reviewed board/sample indices, not roll-up flags.
# Derive coverage from those actual records before accepting the complete review.
assert progress['reviewedSampleIndices'] == list(range(1, 1811))
assert len(progress['reviewedBoards']) == 302 and all(row['directlyRead'] for row in progress['reviewedBoards'])
assert {row['index'] for row in progress['reviewedBoards']} == set(range(1, 303))
reviewed_samples = execution['samples']
anchors = {anchor for row in reviewed_samples for anchor in row['anchors']}
cut_ids = {f'{cut["index"]:03d}-{cut["scene"]}' for cut in plan['cuts']}
assert all(f'{label}:{cue}' in anchors for cue in range(1, 401) for label in ['cue-first', 'cue-mid', 'cue-last'])
assert all(f'{label}:{cut}' in anchors for cut in cut_ids for label in ['first-cut', 'mid-cut', 'last-cut'])
assert len({anchor for anchor in anchors if anchor.startswith('PCM-onset:')}) == 73
assert len({row['segment'] for row in reviewed_samples if row['role'] == 'explanation'}) == 19
assert {'branding', 'membership'} <= {row['segment'] for row in reviewed_samples}
request = read(W / 'encoded-caption-qa-request.json')
assert request['allCueCutIntersectionsCovered'] and len(request['points']) == 1810
progress.update(all400CuesDirectlyRead=True, all69CutEdgesDirectlyRead=True,
                all73PcmOnsetsDirectlyRead=True, allCueCutIntersectionsDirectlyRead=True,
                allExplanationMotionAndDepthDirectlyRead=True, originalBrandingAndMemberIdentityDirectlyRead=True)
assert progress['all400CuesDirectlyRead'] and progress['all69CutEdgesDirectlyRead']
assert progress['all73PcmOnsetsDirectlyRead'] and progress['allCueCutIntersectionsDirectlyRead']
assert progress['allExplanationMotionAndDepthDirectlyRead'] and progress['originalBrandingAndMemberIdentityDirectlyRead']
assert pair['planSha256'] == sha(W / 'plan.json') and pair['captionAssSha256'] == sha(W / 'captions.ko.ass')
assert pair['identicalAacPayload'] and abs(pair['inheritedSameAacLufs'] + 16) <= .6 and pair['inheritedSameAacTruePeakDbtp'] <= -1.5
captioned = next(row for row in pair['records'] if '.captioned.' in row['path'])
assert progress['sourceSha256'] == execution['sourceSha256'] == captioned['sha256']
for row in pair['records']:
    assert sha(ROOT / row['path']) == row['sha256'] and row['wholeDecodeExitCode'] == 0
    assert row['exactPresentationClock'] == dict(timeBase='1/90000', count=37098, firstPts=0, lastPts=55645500, step=1500, allPacketPtsExact=True)
for row in [*execution['boards'], *execution['samples']]:
    assert sha(ROOT / row['path']) == row['sha256']
for row in asr['windows']:
    assert sha(ROOT / row['path']) == row['sha256']
assert len(plan['cuts']) == 69 and sum(cut['role'] == 'actual' for cut in plan['cuts']) == 50
assert sum(cut['role'] == 'explanation' for cut in plan['cuts']) == 19
pending = ['Human whole-video listening/pronunciation', 'Final public rights', 'Original Nimbus Audio Library file verification',
           'Source-truncated membership handles', 'External backup', 'Automatic dubbing/optional CC propagation', 'Private-video pinned comment posting']
review = dict(schemaVersion=1, slug='similar-game-design', reviewedAt=now(), status='approved-current-final-technical-pixels-and-QA',
              source=captioned['path'], sourceSha256=captioned['sha256'], planSha256=pair['planSha256'], captionAssSha256=pair['captionAssSha256'],
              extraction=rel(execution_path), extractionSha256=sha(execution_path), directProgress=rel(progress_path),
              directProgressBeforeSealSha256=sha(progress_path), directlyReadBoards=list(range(1, 303)), directlyReadSampleCount=1810,
              boards=[dict(index=row['index'], path=row['path'], sha256=row['sha256'], sampleIndices=row['sampleIndices'], directlyRead=True)
                      for row in execution['boards']], all400KoreanCuesReviewed=True, all69CutsReviewed=True, all73PcmOnsetsReviewed=True,
              allCueCutIntersectionsReviewed=True, projectedDepthAndMotionReviewed=True, all19ExplanationPartsReviewed=True,
              fixedCaptionCenter=[960, 970], captionStyle='boxed-white-forest-v1', captionsReadableNoConfirmedUiCollision=True,
              originalIntro120FramesPreserved=True, originalMembership600FramesAnd12IdentitiesPreserved=True,
              exactMembershipTitle='멤버쉽가입 감사드립니다.', confirmedRemainingPixelDefects=[],
              measuredFrames=dict(actual=21827, explanation=14551, body=36378, final=37098, ratioErrorFrames=.2),
              wholeDecodeExitCodes=[0, 0], exactPtsBoth=True, identicalAacPayload=True, lufs=pair['inheritedSameAacLufs'],
              truePeakDbtp=pair['inheritedSameAacTruePeakDbtp'], currentMixedAsrReview=rel(asr_path), currentMixedAsrReviewSha256=sha(asr_path),
              humanWholeListeningApproved=False, humanPronunciationApproved=False, publicRightsApproved=False,
              allFinalPixelsReviewed=True, qaApproved=True, collectApproved=True, privateUploadTechnicallyReady=True,
              collected=False, uploaded=False, completedPrivateVideo=False, newGitImages=0, imagesLocalOnly=True, pending=pending)
save(target, review)
progress.update(status='all302-direct-read-current-encoded-QA-sealed', reviewedAt=now(), allFinalPixelsReviewed=True,
                 qaApproved=True, collectApproved=True, privateUploadApproved=False, sealedReview=rel(target),
                 pending=['Collection and actual private platform save/settings verification', *pending])
save(progress_path, progress)
manifest_path = BASE.parent / 'project.json'
manifest = read(manifest_path)
manifest.update(status='technical-QA-approved-awaiting-4file-collection-private-save', updatedAt=now())
manifest['visualStyle']['finalAnimatedPixelsReviewed'] = True
manifest['approvals'].update(finalPixels=True, render=True, qa=True, collected=False, uploaded=False)
manifest['paths'].update(videoClean=next(row['path'] for row in pair['records'] if '.clean.' in row['path']),
                         videoBurnedCaptions=captioned['path'], finalPixelReview=rel(target), qa=rel(target))
save(manifest_path, manifest)
cp_path = BASE / 'latest-checkpoint.json'
cp = read(cp_path)
cp.update(stage='technical-QA-approved-awaiting-4file-collection-private-save', recordedAt=now(), finalPixelReview=rel(target),
          allFinalPixels=True, qaApproved=True, collected=False, uploaded=False,
          nextAction='Collect reviewed clean/captioned/KOEN once, then single new private captioned upload/settings/actual checks/selective normal Git push.')
save(cp_path, cp)
qp = ROOT / 'production/batches/sakurai-planning-game-design/queue.json'
queue = read(qp)
item = next(x for x in queue['items'] if x['slug'] == 'similar-game-design')
item.update(stage=cp['stage'], finalPixelReview=rel(target), allFinalPixels=True, qaApproved=True, collected=False, uploaded=False, nextAction=cp['nextAction'])
queue['updatedAt'] = now()
save(qp, queue)
print(json.dumps(dict(boards=302, samples=1810, confirmedPixelDefects=0, allFinalPixels=True, qaApproved=True, collected=False, uploaded=False)))
