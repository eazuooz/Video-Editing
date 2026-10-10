"""Seal directly observed private settings; preserve prior transfer observations."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json

root = Path(__file__).resolve().parents[3]
rel = 'projects/game-math-polar-3d/revision-teaching-clarity-v1'
revision = root / rel
pub = revision / 'publishing'
now = datetime.now(timezone.utc).isoformat()
def read(path):
    return json.loads(path.read_text('utf-8-sig'))
def write(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
def text(name):
    return (pub / name).read_text('utf-8-sig')

receipt = read(pub / 'youtube-upload-v3.json')
assert receipt['actualVideoId'] == '2kNMDlrwdU8' and not receipt['baselineScheduleChanged']
history = pub / 'youtube-upload-history-through-v5.json'
if not history.exists():
    history.write_bytes((pub / 'youtube-upload-v3.json').read_bytes())
timings = read(pub / 'member-timings-actual-ui-v6.json')
assert timings['saveButtonDisabled'] and len(timings['elements']) == 3
assert all(e['actualUiInputs'][:2] == ['14:51:55', '15:01:55'] for e in timings['elements'])
cues = read(pub / 'published-cue-comparison-v6.json')
assert cues['all412PublishedCueTextsAndTimesMatch']
assert '동영상에서 소유권 주장이 발견되지 않았습니다' in text('copyright-completed-v6.ax.txt')
assert '동영상에서 설정에 따라 수익을 창출하고 있습니다' in text('copyright-completed-v6.ax.txt')
assert '고화질 완료' in text('private-completed-v6.ax.txt') and '비공개' in text('private-completed-v6.ax.txt')
assert '한국어' in text('advanced-completed-record-v6.ax.txt')
assert '자막 사용 안함' in text('player-cc-off-quality-v6.ax.txt') and '1080p60 HD' in text('player-cc-off-quality-v6.ax.txt')

images = []
for name, reason in [
    ('private-thumbnail-HD-saved-v6.png', 'One directly reviewed completed Studio record proves the exact new private ID, saved original channel thumbnail, SD/HD completion and no current notification.'),
    ('cc-off-annotated-game-v6.png', 'One directly reviewed actual 1080p60 upload frame at 38.832740s proves red horizontal/green height/blue relation geometry, subject focus, recorder credit, readable HUD and fixed burned Korean captions with CC off.'),
    ('cc-off-projected-explanation-v6.png', 'One directly reviewed actual 1080p60 upload frame at 90s proves projected cylindrical geometry, declared z-up axes and fixed burned Korean captions with CC off; original approved white palette retained.')]:
    path = f'{rel}/publishing/{name}'
    assert (root / path).is_file()
    images.append({'path': path, 'purpose': 'minimal-publishing-proof', 'reason': reason,
                   'sha256': hashlib.sha256((root / path).read_bytes()).hexdigest(),
                   'reviewedAt': now, 'project': 'game-math-polar-3d'})

review = {'schemaVersion': 3, 'actualVideoId': receipt['actualVideoId'], 'reviewedAt': now,
          'originalThumbnailSavedReopenedAndDirectlyRead': True,
          'privateSavedAndSdHdComplete': True,
          'allKoEnCueTextsAndVisibleTimesReopened': True,
          'publishedCueComparison': f'{rel}/publishing/published-cue-comparison-v6.json',
          'exactSourceSrtPreserved': True,
          'actualPlatformSrtDownloadCompleted': False,
          'languageLoadedRecord': {'audio': '한국어', 'titleDescription': '한국어', 'earlierTransferSelectionEvidencePreserved': True},
          'actualCopyrightStatus': '동영상에서 소유권 주장이 발견되지 않았습니다',
          'actualCurrentMonetizationStatement': '동영상에서 설정에 따라 수익을 창출하고 있습니다.',
          'currentDetailsNotification': '—',
          'separateAdCompletionModalObserved': False,
          'separateWizardCompletionModalObserved': False,
          'cardCanonicalUrlAnd00TimeReopened': True,
          'membershipEndScreen': {'start60fps': '14:51:55', 'end60fps': '15:01:55', 'allThreeElementsReopened': True,
                                 'inputEvidence': f'{rel}/publishing/member-timings-actual-ui-v6.json',
                                 'memberIdentitiesAndTitleUnobscured': True, 'layoutImageLocalOnly': f'{rel}/publishing/member-layout-reopened-v6.png'},
          'uploadPixelReview': {'cc': '사용 안함', 'quality': '1080p60 HD', 'rate': 1, 'actualDecodedDimensions': [1920, 1080],
                               'overviewObservedAtSeconds': 22.835802, 'annotatedGameObservedAtSeconds': 38.832740,
                               'projectedExplanationObservedAtSeconds': 90, 'cameraGamePlayedFromSeconds': 710,
                               'cameraGamePausedAtSeconds': 733.357216,
                               'cameraObservation': 'Red camera-to-subject and blue subject-to-camera arrows, distinct labeled center, explanation-only relative vector relation, moving target, recorder credit, HUD and readable fixed boxed caption directly observed.',
                               'everyLocalCueCutSampleApproved': True, 'everyUploadedFrameDirectlyRead': False,
                               'uploadedWholeAudioHumanListening': False},
          'minimalReviewedImages': images,
          'pending': ['whole human listening and pronunciation', 'final public rights', 'original Nimbus external backup',
                      'original truncated member handles', 'external media backup', 'automatic dubbing',
                      'optional CC propagation', 'comment posting and pinning after public availability'],
          'baselineChanged': False, 'mediaRegenerated': False, 'newUploadCount': 1}
write(pub / 'private-settings-direct-review-v3.json', review)
receipt.update({'status': 'reviewed-private-settings-complete-awaiting-selective-git-and-schedule-replacement',
                'uploaded': True, 'savedPrivate': True, 'fullSettingsVerified': True, 'checksVerified': True,
                'ccOffPixelsVerified': True, 'updatedAt': now})
receipt['thumbnail']['savedAndReopened'] = True
receipt['privacySelection']['finalCompletedPrivateSaveVerified'] = True
receipt['adSelfAssessment'].update({'automaticChecksComplete': True,
                                   'completionEvidence': 'current no-notification completed Studio record and no-impact current monetization statement; no separate completion modal observed'})
for language in ['ko', 'english']:
    key = 'koSubtitles' if language == 'ko' else 'englishSubtitles'
    receipt[key].update({'allPlatformCueTimesReopened': True, 'reopenedVisibleCueTimesRead': 206,
                         'publishedCueComparison': f'{rel}/publishing/published-cue-comparison-v6.json',
                         'actualUiDisplayRule': cues['uiDisplayRuleObserved'], 'srtDownloadCompleted': False})
receipt['membershipEndScreen'].update({'processed60fpsTimingVerified': True, 'allElementsReopened': True,
                                     'actualUiStart': '14:51:55', 'actualUiEnd': '15:01:55',
                                     'targetDurationSeconds': 10, 'allElementsInputEvidence': f'{rel}/publishing/member-timings-actual-ui-v6.json'})
receipt['languageCompletedRecord'] = review['languageLoadedRecord']
receipt['currentChecks'] = {k: review[k] for k in ['actualCopyrightStatus', 'actualCurrentMonetizationStatement', 'currentDetailsNotification', 'separateAdCompletionModalObserved', 'separateWizardCompletionModalObserved']}
receipt['privateReviewEvidence'] = f'{rel}/publishing/private-settings-direct-review-v3.json'
write(pub / 'youtube-upload-v3.json', receipt)

queue_path = root / 'production/batches/unpublished-teaching-clarity-revision/queue.json'
queue = read(queue_path)
queue['execution'].update({'stage': 'polar-reviewed-private-settings-complete-selective-git-pending',
                           'actualNewVideoId': receipt['actualVideoId'], 'baselineScheduleChanged': False})
queue['updatedAt'] = now
write(queue_path, queue)

registry_path = root / 'shared/git-essential-images.json'
registry = read(registry_path)
for entry in images:
    existing = next((e for e in registry['entries'] if e['path'] == entry['path']), None)
    assert existing is None or existing['sha256'] == entry['sha256']
    if existing is None:
        registry['entries'].append(entry)
write(registry_path, registry)
ignore = root / '.gitignore'
old_ignore = ignore.read_bytes()
existing_lines = old_ignore.decode('utf-8-sig').splitlines()
additions = ['!' + e['path'] for e in images if '!' + e['path'] not in existing_lines]
if additions:
    with ignore.open('ab') as handle:
        if old_ignore and not old_ignore.endswith(b'\n'):
            handle.write(b'\n')
        handle.write(('\n'.join(additions) + '\n').encode('utf-8'))
print(json.dumps({'actualId': receipt['actualVideoId'], 'reviewedPrivate': True, 'essentialImages': len(images),
                  'baselineChanged': False, 'gitDelivered': False, 'scheduled': False}))
