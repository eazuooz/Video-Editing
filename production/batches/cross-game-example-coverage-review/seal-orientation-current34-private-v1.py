"""Seal actual current34 private UI observations; preserve automatic-review limits."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
O = ROOT / 'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def save(path, data):
    pending = path.with_name(path.name + '.private-seal.tmp')
    pending.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    pending.replace(path)

proof_path = O / 'publishing/private-settings-direct-review-v1.json'
if proof_path.exists():
    raise SystemExit('Private proof exists: reuse its actual follow-up, never reseal blindly.')
receipt_path = O / 'publishing/youtube-upload-v1.json'
receipt = read(receipt_path)
assert receipt['actualVideoId'] == 'orq0TMVkFts'
assert receipt['privateSaveReopenVerified'] and receipt['uploaded']
assert receipt['englishMetadata']['saveReopenVerified']
assert receipt['subtitles'][1]['saveReopenVerified']
assert receipt['subtitles'][0]['status'] == 'saved-in-current-upload-wizard'
assert receipt['coachingCard']['saveReopenVerified']
assert receipt['endScreen']['saveReopenVerified']
assert receipt['burnedCaptionVerification']['verified']
assert receipt['checks']['adSuitability'] == 'review-in-progress'
promotion = read(O / 'current34-main-promotion-v1.json')
assert sha(ROOT / promotion['baselineMain']['path']) == promotion['baselineMain']['sha256']
for row in promotion['otherProtectedInputs'] + promotion['repairCandidates']:
    assert sha(ROOT / row['path']) == row['sha256'], row['path']
main_path = ROOT / 'projects/game-math-orientation-matrices/project.json'
assert sha(main_path) == promotion['currentMain']['sha256']
main_before = sha(main_path)
main = read(main_path)
now = datetime.now(timezone.utc).isoformat()
receipt['subtitles'][0].update(status='manual-source-saved-and-reopened', saveReopenVerified=True,
                              actualLanguageLabel='한국어: 자막 수정/수동 업로드 source controls')
receipt['thumbnail'].update(status='saved-reopened-and-illustrated-thumbnail-pixels-observed',
                            saveReopenVerified=True)
receipt['monetization'].update(status='use-selected-saved-reopened;automatic-review-in-progress',
                               useSelected=True, automaticMidrollSelected=True,
                               actualStatus='검사 중', saveDisabled=True)
receipt.update(status='private-all-available-settings-verified;automatic-ad-review-pending',
               fullAvailableSettingsVerified=True, fullSettingsComplete=False, recordedAt=now)
proof = {
    'schemaVersion': 1, 'reviewedAt': now, 'actualVideoId': 'orq0TMVkFts',
    'privateSavedAndReopened': True, 'fullAvailableSettingsVerified': True,
    'fullSettingsComplete': False, 'automaticAdCheckPassed': False,
    'actualAdStatus': '검사 중', 'actualCopyrightNoIssuesObserved': True,
    'actualSdHdComplete': True, 'manualKoEn244Saved': True,
    'localizedEnglishTitleAndFullDescriptionReopened': True,
    'coachingCardZeroSecondsReopened': True, 'memberThreeElementsReopened': True,
    'endScreenActualUiFps': 60, 'endScreenUiStart': '18:08:38',
    'endScreenUiEnd': '18:18:36', 'memberIdentityPanelAndTitleClear': True,
    'uploadedCcOff1080p60SelectedFramesReviewed': True,
    'uploadedFrameProofs': receipt['burnedCaptionVerification']['selectedFrameProofs'],
    'optionalCcPropagationPending': True, 'automaticDubbingHumanReviewPending': True,
    'humanListeningApproved': False, 'humanPronunciationApproved': False,
    'publicRightsApproved': False, 'pinnedCommentPosted': False,
    'baselineVideoId': '6-kP65hrZcI', 'baselineScheduleChanged': False,
    'gitDelivered': False, 'scheduleReplacementVerified': False, 'obsoleteDeleted': False,
    'newGitMedia': 0, 'newGitImages': 0,
    'claimScope': 'Actual private save/reopen, available settings and bounded uploaded frames. '
                  'Automatic ad review, optional tracks propagation and human approvals remain pending.',
}
save(receipt_path, receipt)
save(proof_path, proof)
main['publishing'].update(privateUploadComplete=True, videoId='orq0TMVkFts',
    actualVideoId='orq0TMVkFts', videoUrl='https://youtu.be/orq0TMVkFts', uploaded=True,
    privacyStatus='private', fullAvailableSettingsVerified=True, fullSettingsComplete=False,
    fullSettingsVerified=False, automaticAdStatus='검사 중',
    status=receipt['status'], privateSettingsReview=str(proof_path.relative_to(ROOT)).replace('\\', '/'))
main['status'] = 'current34-detailed-four-game-private-saved;automatic-ad-Git-schedule-pending'
main['approvals']['privateUpload'] = ('Private upload and available settings authorized; actual reviewed '
    'replacement may be scheduled at09:00 Asia/Seoul after Git and current Studio verification.')
save(main_path, main)
transition_path = O / 'current34-main-private-update-v1.json'
save(transition_path, {
    'recordedAt': now, 'intentionalPublishingMetadataTransition': True,
    'previousMain': {'path': str(main_path.relative_to(ROOT)).replace('\\', '/'), 'sha256': main_before},
    'currentMain': {'path': str(main_path.relative_to(ROOT)).replace('\\', '/'), 'sha256': sha(main_path)},
    'promotion': str((O / 'current34-main-promotion-v1.json').relative_to(ROOT)).replace('\\', '/'),
    'originalBackupUnchanged': True, 'other78ProtectedInputsUnchanged': True,
    'repairCandidatesUnchanged': True, 'newActualVideoId': 'orq0TMVkFts',
    'automaticAdCheckPassed': False, 'gitDelivered': False, 'scheduleReplacementVerified': False,
})
next_step = ('Reuse actual orq0TMVkFts private upload. All available settings and uploaded CCoff1080p60 '
             'frames verified. Selective Git delivery while automatic ad review is pending; '
             'then current Studio09 slot saved/reopened replacement when actual checks pass. '
             'No duplicate upload/render/review; baseline6-kP unchanged.')
cp_path = O / 'latest-checkpoint.json'
checkpoint = read(cp_path)
checkpoint.update(recordedAt=now, stage=main['status'], next=next_step,
    privateReplacementSaved=True, privateSettingsReview=str(proof_path.relative_to(ROOT)).replace('\\', '/'),
    fullAvailableSettingsVerified=True, fullSettingsComplete=False,
    uploadedCaptionPixelsReviewed=True, automaticAdCheckPassed=False,
    postPromotionGuard=str(transition_path.relative_to(ROOT)).replace('\\', '/'))
save(cp_path, checkpoint)
queue_path = ROOT / 'production/batches/cross-game-example-coverage-review/queue.json'
queue = read(queue_path)
queue['currentOrientationReview'].update(stage=checkpoint['stage'], next=next_step,
    privateReplacementSaved=True, privateSettingsReview=checkpoint['privateSettingsReview'],
    fullAvailableSettingsVerified=True, fullSettingsComplete=False,
    uploadedCaptionPixelsReviewed=True, automaticAdCheckPassed=False,
    postPromotionGuard=checkpoint['postPromotionGuard'])
queue['updatedAt'] = now
save(queue_path, queue)
print(json.dumps({'privateReopened': True, 'availableSettingsVerified': True,
                  'automaticAdPending': True, 'mainSha256': sha(main_path),
                  'other78ProtectedUnchanged': True, 'newGitMedia': 0}))
