"""Seal the observed private upload; no media or platform actions."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / 'projects/hierarchical-game-outlines'
HERE = Path(__file__).resolve().parent
PUB = HERE / 'publishing'

def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))

def save(p, data):
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

proof_path = PUB / 'main-private-transition-v1.json'
if proof_path.exists():
    raise RuntimeError('Private transition already sealed; do not repeat.')
review = read(PUB / 'private-settings-direct-review-v1.json')
assert review['videoId'] == 'JoHXz7YtEPw'
assert review['privateSavedAndReopened'] and review['fullAvailableSettingsVerified']
assert not review['scheduled'] and not review['baselineMutated']
final = read(HERE / 'final-direct-review-v2.json')
collection = read(HERE / 'collection-verification-v1.json')
assert final['captionedSha256'] == '80071935bf249c490a7f25c40241a8a5fc7812d83eaac6890357d95dcb8b9ca4'
assert collection['exitCode'] == 0 and len(collection['files']) == 4
promotion = read(HERE / 'main-promotion-v1.json')
main = BASE / 'project.json'
assert sha(main) == promotion['current']['sha256']
assert sha(ROOT / promotion['baseline']['path']) == promotion['baseline']['sha256']
backup = HERE / 'pre-private-main-local.json'
if backup.exists():
    raise RuntimeError('Preserve existing private transition backup.')
backup.write_bytes(main.read_bytes())
at = datetime.now(timezone.utc).isoformat()
upload = read(PUB / 'youtube-upload-v1.json')
assert upload['fileSelectionCount'] == 1
upload['initialProgressObservation'] = {'percent': upload.pop('observedProgress'), 'at': upload.pop('observedAt')}
upload.update(status='private-saved-settings-verified-user-review-pending', privateSaved=True,
              fullSettingsComplete=True, sdHdProcessed=True, automaticCopyrightCheckPassed=True,
              automaticAdCheckPassed=True, verifiedAt=at, studioUrl='https://studio.youtube.com/video/JoHXz7YtEPw/edit',
              settingsReview='private-settings-direct-review-v1.json', pinnedCommentStatus='prepared-private-unavailable')
save(PUB / 'youtube-upload-v1.json', upload)
p = read(main)
p['status'] = 'private-delivered-awaiting-user-review'
p['publishing'].update(uploaded=True, actualVideoId=upload['videoId'], videoUrl=upload['videoUrl'],
                       studioUrl=upload['studioUrl'], fullSettingsVerified=True,
                       verification=str((PUB / 'private-settings-direct-review-v1.json').relative_to(ROOT)).replace('\\', '/'),
                       automaticAdCheckPassed=True, scheduled=False)
p['userReview'] = {'status': 'pending', 'humanFullListening': False, 'pronunciationApproved': False,
                   'publicRightsApproved': False, 'nextVideoAuthorized': False,
                   'notes': review['pending']}
save(main, p)
save(proof_path, {'at': at, 'purpose': 'Current private receipt only; baseline reservation untouched',
                 'before': {'path': str(backup.relative_to(ROOT)).replace('\\', '/'), 'sha256': sha(backup)},
                 'current': {'path': str(main.relative_to(ROOT)).replace('\\', '/'), 'sha256': sha(main)},
                 'originalBaselineBackupUnchanged': True, 'baselineYouTubeId': 'jBRt3xatdPk',
                 'baselineMutated': False, 'scheduled': False})
ledger_path = BASE / 'production/review-ledger.json'
ledger = read(ledger_path)
ledger['entries'].append({'check': 'current-private-upload-settings', 'status': 'pass-for-private-editorial-review',
                         'scopeVersion': 'reference-preserving-v1', 'appliesToCurrentReferenceRevision': True,
                         'evidence': str((PUB / 'private-settings-direct-review-v1.json').relative_to(ROOT)).replace('\\', '/'),
                         'sha256': sha(PUB / 'private-settings-direct-review-v1.json'), 'videoId': upload['videoId'],
                         'humanFullListening': False, 'publicRightsApproved': False})
ledger.update(updatedAt=at, privateUploadComplete=True, availablePublishingSettingsComplete=True,
              userReviewPending=True, automaticNextVideo=False)
save(ledger_path, ledger)
checkpoint = read(HERE / 'latest-checkpoint.json')
checkpoint.update(updatedAt=at, stage='private-complete-ready-selective-git', finalDelivery=True,
                  actualVideoId=upload['videoId'], privateUploadComplete=True, fullSettingsComplete=True,
                  next='Deliver selected production/rule files once through isolated Git index, then stop for user review.',
                  gitVerification='publishing/production-git-verification-v1.json', gitDelivered=False)
save(HERE / 'latest-checkpoint.json', checkpoint)
print(json.dumps({'videoId': upload['videoId'], 'privateSettings': True, 'mainSha256': sha(main), 'gitPending': True}))
