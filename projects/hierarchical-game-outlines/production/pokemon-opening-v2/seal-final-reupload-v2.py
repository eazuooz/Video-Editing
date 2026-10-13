"""Seal the observed final private reupload; never render, upload or delete."""
from pathlib import Path
import datetime
import hashlib
import json

P = Path(__file__).resolve().parent
R = P.parents[3]
H = P.parents[1]
Q = P / 'publishing/final-upload-v2'


def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))


def write(p, obj):
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def rel(p):
    return p.relative_to(R).as_posix()


request = read(Q / 'request.json')
review = read(Q / 'private-settings-direct-review-v1.json')
upload = read(Q / 'youtube-upload-v1.json')
checks = read(Q / 'automatic-checks-v1.json')
video = 'x04OdXSt98U'
old_video = 'Bjh2e5f5ync'
assert request['newVideoId'] == review['videoId'] == upload['videoId'] == checks['videoId'] == video
assert request['oldReviewVideoId'] == old_video and request['fileSelectionCount'] == 1
assert review['privateSavedAndReopened'] and review['fullAvailableSettingsVerified']
assert review['automaticAdCheckPassed'] and checks['automaticAdCheckPassed']
assert not review['scheduled'] and not review['baselineMutated'] and not request['deletePerformed']
assert sha(R / request['sourceFile']) == request['sourceSha256']
assert read(P / 'final-direct-review-v1.json')['captionedSha256'] == request['sourceSha256']
assert read(P / 'collection-verification-v2.json')['exitCode'] == 0

main = H / 'project.json'
prior = read(P / 'publishing/main-private-transition-v1.json')
assert sha(main) == prior['current']['sha256']
assert not (Q / 'main-final-reupload-v1.json').exists()
backup = R / '.git/hierarchy-final-reupload-v2/pre-final-main.json'
assert not backup.exists()
backup.parent.mkdir(parents=True, exist_ok=True)
backup.write_bytes(main.read_bytes())
at = datetime.datetime.now(datetime.timezone.utc).isoformat()
j = read(main)
assert j['publishing']['actualVideoId'] == old_video
j.setdefault('publishingHistory', []).append({
    'at': at,
    'reason': 'User accepted the content and explicitly requested a final private reupload with captions and links.',
    'publishing': j['publishing'].copy(),
    'currentReviewDeletion': 'Requested by user; action-time confirmation pending. No deletion performed.'
})
j['status'] = 'approved-content-final-private-delivered'
j['publishing'].update(
    actualVideoId=video, videoUrl=upload['videoUrl'], studioUrl=upload['studioUrl'],
    receipt=rel(Q / 'youtube-upload-v1.json'), verification=rel(Q / 'private-settings-direct-review-v1.json'),
    fullSettingsVerified=True, automaticAdCheckPassed=True, privacyStatus='private', scheduled=False,
    previousReviewVideoId=old_video, previousReviewDeletionStatus='pending-action-time-confirmation')
j['userReview'].update(status='content-accepted-final-links-delivered', contentAccepted=True,
                       humanFullListening=False, pronunciationApproved=False, publicRightsApproved=False,
                       nextVideoAuthorized=False)
write(main, j)
write(Q / 'main-final-reupload-v1.json', {
    'at': at, 'purpose': 'Explicit final private reupload of identical approved content; no other IDs or schedules changed.',
    'before': {'path': rel(backup), 'sha256': sha(backup)},
    'current': {'path': rel(main), 'sha256': sha(main)},
    'oldReviewId': old_video, 'newVideoId': video, 'oldReviewDeleted': False,
    'preservedIds': ['JoHXz7YtEPw', 'jBRt3xatdPk'], 'scheduled': False,
    'mediaChanged': False, 'newRender': False, 'newTts': False, 'newCollection': False
})
ledger_path = H / 'production/review-ledger.json'
ledger = read(ledger_path)
assert not any(e.get('check') == 'final-private-reupload-v2' for e in ledger['entries'])
ledger['entries'].append({
    'check': 'final-private-reupload-v2', 'status': 'pass-for-private-delivery',
    'videoId': video, 'userContentAccepted': True,
    'evidence': rel(Q / 'private-settings-direct-review-v1.json'),
    'sha256': sha(Q / 'private-settings-direct-review-v1.json'),
    'sourceFileSha256': request['sourceSha256'], 'unchangedMediaQaReused': True,
    'humanFullListening': False, 'publicRightsApproved': False,
    'oldReviewDeletion': 'pending-action-time-confirmation'
})
ledger.update(updatedAt=at, privateUploadComplete=True, availablePublishingSettingsComplete=True,
              userReviewPending=False, userContentAccepted=True, automaticNextVideo=False)
write(ledger_path, ledger)
cp = read(P / 'latest-checkpoint.json')
cp['priorProductionGit'] = {k: cp.get(k) for k in ['gitCommit', 'gitVerification', 'gitActualSession',
                                                  'gitActualExitCode', 'gitCompletionChunk', 'verifiedRemoteBlobs']}
for key in ['gitCommit', 'gitActualSession', 'gitActualExitCode', 'gitCompletionChunk', 'verifiedRemoteBlobs']:
    cp.pop(key, None)
cp.update(updatedAt=at, stage='final-private-reupload-ready-selective-git', actualVideoId=video,
          privateUpload=True, fullSettingsComplete=True, gitDelivered=False,
          gitVerification='publishing/final-upload-v2/production-git-verification-v1.json',
          currentFinalization='publishing/final-upload-v2/request.json',
          next='Deliver the selected settings to Git; request exact Bjh2e5f5ync permanent-deletion confirmation once at action time; stop after this video.',
          automaticNextVideo=False, humanFullListening=False, pronunciationApproved=False, publicRightsApproved=False)
write(P / 'latest-checkpoint.json', cp)
evidence = []
for f in sorted((Q / 'media-proof-local').iterdir()):
    if f.is_file() and ('-local.' in f.name or f.name == 'private-save-before-local.ax.txt'):
        evidence.append({'path': rel(f), 'sha256': sha(f), 'bytes': f.stat().st_size, 'git': False})
write(Q / 'evidence-index-v1.json', {
    'at': at, 'videoId': video, 'method': 'CUA observations recorded during the current final reupload',
    'files': evidence, 'rawEvidenceLocalOnly': True, 'newMediaOrRasterGitAdditions': 0
})
print(json.dumps({'videoId': video, 'mainSha256': sha(main), 'gitPending': True,
                  'oldReviewDeleted': False, 'mediaJobsRepeated': 0}))
