"""Record only the two polygon revisions actually verified in Studio.

Run after real private saves, manual KO/EN subtitle publishing, and CC-off
uploaded-pixel review. This does not schedule or authorize human/IP review.
"""
import hashlib
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BATCH = ROOT / 'production/batches/game-math-part2-teaching-revision'
REVIEW = BATCH / 'cross-game-review-20261011'
NOW = datetime.now(timezone(timedelta(hours=9))).isoformat()

def read(path):
    return json.loads(path.read_text(encoding='utf-8'))

def write(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

deliveries = []
for slug, video_id in [('game-math-polygon-centers-v2', 'YgcN8vs0gNo'),
                       ('game-math-polygon-partition-v2', 'pfagaQK-xfI')]:
    project = ROOT / 'projects' / slug
    work = ROOT / 'shared/output' / slug
    receipt_path = project / 'publishing/youtube-upload.json'
    receipt = read(receipt_path)
    assert receipt['videoId'] == video_id
    assert read(project / 'production/current-pixel-review.json')['sha256'] == receipt['video']['sha256']
    proofs = {}
    for filename in ['studio-languages-published-v4.txt',
                     'studio-card-saved-reopened-v4.txt',
                     'uploaded-game-cc-off-v4.json', 'uploaded-game-cc-off-v4.png',
                     'uploaded-explanation-cc-off-v4.json', 'uploaded-explanation-cc-off-v4.png']:
        path = work / filename
        assert path.is_file(), path
        proofs[filename] = {'path': path.relative_to(ROOT).as_posix(),
                            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
    language_state = (work / 'studio-languages-published-v4.txt').read_text(encoding='utf-8')
    assert '1개 게시됨 게시됨' in language_state
    for filename in ['uploaded-game-cc-off-v4.json', 'uploaded-explanation-cc-off-v4.json']:
        observed = read(work / filename)
        # The first lecture's already-saved proof nests its media fields.
        media = observed.get('video', observed)
        if isinstance(media, list):
            media = media[0]
        assert media.get('height', media.get('videoHeight')) == 1080, observed
        assert media.get('width', media.get('videoWidth')) == 1920, observed
        assert all(c.get('pressed') == 'false' for c in observed['cc']), observed
    receipt.update(status='actual-Studio-private-upload-verified', uploadComplete=True,
                   fullPublishingSettingsComplete=True, scheduled=False,
                   verifiedAt=NOW, platformEvidence=proofs)
    receipt['metadata']['privacyStatus'] = 'private'
    receipt['englishMetadata']['status'] = 'published-and-reopened'
    for subtitle in receipt['subtitles']:
        subtitle['status'] = 'manual-timed-file-published; Studio language status verified'
        subtitle['platformReviewScope'] = 'File accepted with timing; bounded visible editor cues and published status. Editor fields are virtualized.'
    receipt['thumbnail']['status'] = 'uploaded-thumbnail-reopened-in-saved-details'
    receipt['burnedCaptionVerification'].update(status='verified-actual-uploaded1080p-pixels-with-player-CC-off',
                                               playerCaptionsOff=True, evidence=proofs)
    receipt['coachingCard']['status'] = 'saved-and-reopened; one link card at00:00:00'
    receipt['endScreen']['status'] = 'three-elements-saved-and-reopened; original10-second-membership-outro'
    receipt['coachingEndingLink']['status'] = 'external-link-saved-and-reopened; original-member-identities-clear'
    receipt['studioProgress'] = dict(observedAt=NOW, uploadPercent=100,
        state='비공개; 실제 저장 후 재확인', language='한국어', aiDisclosure='yes',
        paidPromotion='no', playlist='게임 수학(Game Math) PART 2',
        category='Education', monetization='enabled',
        adSelfRating='lowest game-violence tier; submitted',
        automaticCopyright='completed; no issues found', automaticAdSuitability='completed; no issues found',
        platformAutoDub='English-US and Indonesian processing observed; separate from our manual subtitles; not claimed reviewed')
    receipt['humanListening'] = 'pending; CPU unprompted mixed-AAC transcription is not human listening'
    receipt['rightsReview'] = 'Recording/source permissions retained; separate game-IP and human review pending. Studio automatic checks are not IP approval.'
    write(receipt_path, receipt)
    manifest = read(project / 'project.json')
    manifest['status'] = 'reviewed-four-game-revision-privately-uploaded; scheduling-pending'
    manifest['publishing'].update(videoId=video_id, privateUploadComplete=True,
                                  fullPublishingSettingsComplete=True, scheduled=False)
    manifest['finalRender']['openItems'] = ['Human whole listening and game-IP review pending.',
                                          'Two-day schedule replacement and selective Git delivery pending.']
    write(project / 'project.json', manifest)
    pixels = read(project / 'production/current-pixel-review.json')
    pixels['uploadedCaptionProof'] = {'verified': True, 'videoId': video_id,
                                      'width': 1920, 'height': 1080, 'playerCC': 'off',
                                      'evidence': proofs}
    write(project / 'production/current-pixel-review.json', pixels)
    deliveries.append(dict(slug=slug, videoId=video_id, uploadComplete=True,
                           fullPublishingSettingsComplete=True, privacy='private', scheduled=False))

queue_path = BATCH / 'queue.json'
queue = read(queue_path)
item = next(i for i in queue['items'] if i['slug'] == 'game-math-polygons-triangulation')
item['status'] = 'four-game-two-episode-revisions-reviewed-and-private-uploaded; schedule-and-Git-pending'
item['revision'].update(flowReviewPassed=True, annotationMotionReviewPassed=True,
                       renderComplete=True, localOutputsCollected=True, privateUploadComplete=True,
                       currentPixelReviewComplete=True, firstEpisodeMasterStaleAfterQG01QG03=False,
                       videoIds=[d['videoId'] for d in deliveries])
queue['execution']['stage'] = 'polygons-v4-private-delivery-verified; two-day-schedule-and-selective-Git-pending'
write(queue_path, queue)

progress_path = REVIEW / 'polygons-v4-current-progress.json'
progress = read(progress_path)
progress.update(recordedAt=NOW, wholeMixedAudioReview='Both current mixed masters fully transcribed without prompts on CPU and directly compared; focused overlap windows reviewed.',
                currentCaptionedRender='Both current final renders approved and collected; uploaded1080p gameplay/explanation pixels directly reviewed with CC off.',
                newPlatformMutations=2, newUploadsComplete=2, actualUploads=deliveries,
                fullTaskComplete=False, humanListening='pending', gameIPHumanReview='pending')
write(progress_path, progress)

inventory_path = REVIEW / 'adopted-game-inventory.json'
inventory = read(inventory_path)
for row in inventory['projects']:
    delivery = next((d for d in deliveries if d['slug'] == row.get('slug')), None)
    if delivery:
        row.update(currentFinalMovingPixelsReviewed=True, currentMixedAudioReviewed=True,
                   teachingReview='four-game-transfer-reviewed; current-private-delivery-verified',
                   reviewedActualDelivery=delivery,
                   currentCoverage='projects/' + row['slug'] + '/planning/game-example-coverage.json',
                   historicalInventoryPreserved=True, humanListening=False, humanGameIPApproval=False)
write(inventory_path, inventory)
print(json.dumps(deliveries, ensure_ascii=False))
