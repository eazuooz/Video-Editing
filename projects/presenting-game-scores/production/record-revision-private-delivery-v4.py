"""Record actual saved publishing observations; never generates media or alters Studio."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'projects/presenting-game-scores'
REV = BASE / 'production/revision-balatro60-v2'
now = datetime.now(timezone.utc).isoformat()

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

receipt = read(REV / 'publishing/youtube-upload-v3.json')
assert receipt['actualVideoId'] == 'L5DA2xiV46M'
assert all(receipt[k] for k in ['privateSaveVerified', 'fullSettingsVerified', 'platformAutomaticChecksComplete', 'burnedCaptionUploadedPixelsVerified'])
assert not receipt['scheduled'] and not receipt['git']['delivered']
assert not receipt['humanWholeListeningApproved'] and not receipt['publicRightsApproved']

images = [
    ('projects/presenting-game-scores/publishing/thumbnail-v2.png', 'delivery-thumbnail', 'Directly reviewed natural cat illustration with yellow header, correct three-block comparison and YamYamCoding branding.'),
    ('projects/presenting-game-scores/production/revision-balatro60-v2/publishing/private-details-proof-v4.png', 'minimal-publishing-proof', 'Actual reopened Studio details verify the new private ID, saved thumbnail and measured chapters, SD and HD processing.'),
    ('projects/presenting-game-scores/production/revision-balatro60-v2/publishing/uploaded-game-caption-proof-v4.png', 'minimal-publishing-proof', 'Actual uploaded Balatro pixels show the full recorder credit and fixed Korean caption with optional player captions off.'),
    ('projects/presenting-game-scores/production/revision-balatro60-v2/publishing/uploaded-black-caption-proof-v4.png', 'minimal-publishing-proof', 'Actual uploaded black spatial explanation pixels show projected faces and the fixed Korean caption with player captions off.'),
]
registry_path = ROOT / 'shared/git-essential-images.json'
registry = read(registry_path)
reviewed = []
for path, purpose, reason in images:
    digest = hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
    entry = {'path': path, 'purpose': purpose, 'reason': reason, 'reviewedAt': now, 'sha256': digest, 'project': 'presenting-game-scores'}
    existing = next((e for e in registry['entries'] if e['path'] == path), None)
    assert existing is None or existing['sha256'] == digest, path
    if existing is None:
        registry['entries'].append(entry)
    reviewed.append(entry)
save(registry_path, registry)
ignore_path = ROOT / '.gitignore'
ignore = ignore_path.read_text(encoding='utf-8-sig')
for path, _, _ in images:
    if '!' + path not in ignore.splitlines():
        ignore = ignore.rstrip() + '\n!' + path + '\n'
ignore_path.write_text(ignore, encoding='utf-8')

evidence = {'schemaVersion': 4, 'actualVideoId': 'L5DA2xiV46M', 'recordedAt': now,
    'receipt': str((REV / 'publishing/youtube-upload-v3.json').relative_to(ROOT)).replace('\\', '/'),
    'singleCaptionedUpload': True, 'privateSavedAndReopened': True, 'fullAvailableSettingsVerified': True,
    'manualKoCues': 175, 'manualEnCues': 70, 'englishMetadataSavedAndReopened': True,
    'coachingCardSeconds': 0, 'endScreen': receipt['endScreen'],
    'platformChecks': receipt['monetization'], 'uploadedPixels': receipt['uploadedPixelReview'],
    'minimalReviewedImages': reviewed, 'baselineVideoId': 'oDYJlcv2Dqk', 'baselineStillPrivateObserved': True,
    'noBaselineDeletionOrSchedule': True, 'humanWholeListeningApproved': False, 'humanPronunciationApproved': False,
    'publicRightsApproved': False, 'automaticDubbingAndOptionalCcPropagationPending': True,
    'gitDelivered': False, 'scheduled': False, 'newMediaGenerated': 0}
save(REV / 'publishing/private-settings-direct-review-v4.json', evidence)

checkpoint_path = BASE / 'production/latest-checkpoint.json'
checkpoint = read(checkpoint_path)
checkpoint.update(stage='revision-reviewed-private-awaiting-git-and-schedule', recordedAt=now,
    actualVideoId='L5DA2xiV46M', private=True, fullSettingsVerified=True,
    nextAction='Selective reviewed production Git push, verify remote, then save/reopen matching 2026-10-28 09:00 Asia/Seoul schedule. Preserve baseline private and incomplete human/rights records.')
for key in ['privateSaved', 'fullSettingsVerified']:
    checkpoint['revisionCheckpoints'][key] = True
checkpoint['revisionCheckpoints']['additionalSources'] = True
checkpoint['revisionCheckpoints']['revisedScript'] = True
checkpoint['revisionPrivateReceipt'] = evidence['receipt']
checkpoint['revisionCurrentDistinct'] = 'projects/presenting-game-scores/production/revision-balatro60-v2/duplicate-direct-review-v4.json'
checkpoint['ownedJob']['status'] = 'closed-current-final-qa-and-collection-complete'
save(checkpoint_path, checkpoint)

project_path = BASE / 'project.json'
project = read(project_path)
project['status'] = 'reviewed-private-revision-awaiting-git-and-schedule'
project['currentRevision']['checkpoints'].update(privateSaved=True, fullSettingsVerified=True)
project['currentRevision'].update(actualVideoId='L5DA2xiV46M', privateReceipt=evidence['receipt'])
project['updatedAt'] = now
save(project_path, project)

queue_path = ROOT / 'production/batches/sakurai-planning-game-design/queue.json'
queue = read(queue_path)
item = next(i for i in queue['items'] if i['slug'] == 'presenting-game-scores')
item.update(stage=checkpoint['stage'], videoId='L5DA2xiV46M', uploaded=True, qa=True, fullSettingsVerified=True,
    privateSaveVerified=True, nextAction=checkpoint['nextAction'], updatedAt=now,
    publishingReceipt=evidence['receipt'], revisionCurrentDistinct=checkpoint['revisionCurrentDistinct'])
item['revisionCheckpoints'] = dict(project['currentRevision']['checkpoints'])
item['revisionAttributionException']['sourceAdopted'] = True
item['finalPlan'] = 'projects/presenting-game-scores/production/revision-balatro60-v2/final-v4/plan.json'
item['activePlatformJob'] = {'tabId': '89', 'actualVideoId': 'L5DA2xiV46M', 'status': 'saved-private-and-full-settings-directly-verified', 'workerExpectedRunning': False}
item['preflight']['inputsDigest'] = '84324fab821f4bbfdab8845beff9581e7690d47154db44df9970ec5434810e9c'
queue['lastProgressAt'] = now
save(queue_path, queue)

readme = BASE / 'README.md'
text = readme.read_text(encoding='utf-8-sig')
marker = '## Balanced revision delivery (2026-10-10)'
if marker not in text:
    readme.write_text(text.rstrip() + '\n\n' + marker + '\n\nThe reviewed 333.133333-second revision is privately saved as `L5DA2xiV46M`. Actual gameplay uses 6,936 Balatro frames and 4,625 Tetris frames; the body separately uses 11,561 actual and 7,707 explanation frames. The recorder credit is saved in both descriptions with user approval. KO175/EN70 manual captions, English metadata, thumbnail, 00-second coaching card, three 10-second member-ending elements, HD and automatic checks have been saved and reopened. The original `oDYJlcv2Dqk` remains private. Git delivery and the planned October 28 09:00 KST schedule are still pending; human listening, pronunciation and final public-rights reviews remain incomplete.\n', encoding='utf-8')
print(json.dumps({'actualVideoId': 'L5DA2xiV46M', 'privateSettingsVerified': True, 'essentialImages': len(images), 'git': False, 'scheduled': False}))
