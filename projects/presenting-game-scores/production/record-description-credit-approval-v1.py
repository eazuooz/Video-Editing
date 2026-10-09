"""Record the user's explicit, video-scoped description credit exception."""
import hashlib
import json
import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[3]
REV = ROOT / 'projects/presenting-game-scores/production/revision-balatro60-v2'
PROOF = REV / 'description-credit-approval-v1.json'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

if PROOF.exists():
    raise SystemExit('Existing approval must be reused; refusing to record it twice.')
handoff = read(REV / 'preflight-handoff-v4.json')
for item in handoff['preserved']:
    if sha(ROOT / item['path']) != item['sha256']:
        raise SystemExit('Protected baseline input changed: ' + item['path'])

now = datetime.now(ZoneInfo('Asia/Seoul')).isoformat()
relative = PROOF.relative_to(ROOT).as_posix()
credit = handoff['attribution']['proposedDescriptionLine']
proof = {
    'schemaVersion': 1, 'slug': 'presenting-game-scores',
    'revision': 'balatro60-tetris40-v2', 'recordedAt': now,
    'userEvidence': '응 넣어',
    'answeredQuestion': '이번 영상만 녹화자 링크 한 줄을 넣어도 될까요?',
    'scope': 'This revised video only; one description recorder link and required visible onscreen credit.',
    'descriptionLineKo': credit,
    'descriptionLineEn': 'Gameplay recording: Squeaky Whale Gameplay Archive — https://www.youtube.com/channel/UCoMF_6EsJYSq8vWG8zqRvtA',
    'sourceVideo': 'https://www.youtube.com/watch?v=c1WD4x9Dyg0',
    'sourceConditionScreenshot': handoff['attribution']['sourceConditionScreenshot'],
    'sourceConditionScreenshotSha256': handoff['attribution']['sourceConditionScreenshotSha256'],
    'descriptionExceptionApproved': True, 'visibleOnscreenCreditRequired': True,
    'sourceAdopted': False, 'exactNativeCutsApproved': False,
    'allCaptionCreditUiPixelsApproved': False,
    'revisedNarrationOrTtsCreated': False, 'humanListeningApproved': False,
    'humanPronunciationApproved': False, 'finalPublicRightsApproved': False,
    'baselineVideoId': 'oDYJlcv2Dqk', 'baselineDeleted': False,
    'pastPendingEvidencePreserved': 'projects/presenting-game-scores/production/revision-balatro60-v2/preflight-handoff-v4.json',
    'protectedInputsUnchanged': handoff['preserved'],
    'newMediaCreated': 0, 'newImagesGitAdded': 0, 'researchProcessChanges': 0,
}
condition = ROOT / proof['sourceConditionScreenshot']
if sha(condition) != proof['sourceConditionScreenshotSha256']:
    raise SystemExit('Source condition proof changed.')
next_action = ('Explicit description credit exception is approved. Refresh current full-content/Studio duplicate review; '
               'finish exact native cut and fixed-caption/credit/UI framing review, then selectively revise dependent '
               'KO/EN narration while preserving unchanged approved PCM and useful black 2.5D explanations.')
paths = [REV / 'request.json', ROOT / 'projects/presenting-game-scores/production/latest-checkpoint.json',
         ROOT / 'production/batches/sakurai-planning-game-design/queue.json']
original = {p: p.read_bytes() for p in paths}
docs = {p: read(p) for p in paths}
request, cp, queue = (docs[p] for p in paths)
request['attributionUserAnswer'] = 'allowed-one-line-description-credit'
request['descriptionCreditApproval'] = relative
request['stage'] = 'description-credit-approved-source-boundary-and-framing-review'
request['nextAction'] = next_action
cp['stage'] = 'balatro60-source-credit-approved-boundary-and-framing-review'
cp['descriptionCreditApproval'] = {'path': relative, 'descriptionExceptionApproved': True}
cp['nextAction'] = next_action
cp['revisionCheckpoints']['currentDuplicateReview'] = False
item = next(x for x in queue['items'] if x['slug'] == 'presenting-game-scores')
item['stage'] = cp['stage']
item['nextAction'] = next_action
item['revisionAttributionException'] = {'path': relative, 'approved': True, 'userEvidence': '응 넣어',
                                      'scope': 'this revision only', 'sourceAdopted': False}
item['revisionCheckpoints']['currentDuplicateReview'] = False
item['updatedAt'] = now
for p in paths:
    if p.read_bytes() != original[p]:
        raise SystemExit('Concurrent change detected: ' + str(p))
PROOF.write_text(json.dumps(proof, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
for p in paths:
    temp = p.with_name(p.name + '.credit-approval-v1.tmp')
    if temp.exists():
        raise SystemExit('Preserve existing temporary update: ' + str(temp))
    temp.write_text(json.dumps(docs[p], ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    if p.read_bytes() != original[p]:
        raise SystemExit('Concurrent change before replacement: ' + str(p))
    os.replace(temp, p)
print(json.dumps({'approval': relative, 'approved': True, 'scope': 'this revision only',
                  'sourceAdopted': False, 'mediaCreated': 0, 'researchChanges': 0}, ensure_ascii=False))
