"""Seal observed completed checks; no UI action or media work."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, re, copy, os

ROOT = Path(__file__).resolve().parents[3]
O = ROOT / 'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
P = O / 'publishing'
Q = ROOT / 'production/batches/cross-game-example-coverage-review/queue.json'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
rel = lambda p: p.relative_to(ROOT).as_posix()

def save(p, value):
    tmp = p.with_name(p.name + '.checks-v3.writing')
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf-8')
    os.replace(tmp, p)

out = P / 'automatic-ad-followup-v3.json'
assert not out.exists(), 'Already sealed; do not repeat'
proofs = [P / 'ui-proof-v1' / f for f in [
    'automatic-checks-complete-v3.ax.txt', 'private-checks-complete-v3.ax.txt',
    'monetization-complete-v3.ax.txt']]
raw = [p.read_text('utf-8') for p in proofs]
blocks = re.split(r'(?m)^\s*\d+ row\s*$', raw[0])
matching = [b for b in blocks if 'studio.youtube.com/video/orq0TMVkFts/edit, ID: video-title' in b]
assert len(matching) == 1
assert 'text —' in matching[0] and 'text 비공개' in matching[0]
assert '검토 중' not in matching[0] and '검사 중' not in matching[0]
assert 'orq0TMVkFts/edit' in raw[1] and 'text 비공개' in raw[1]
assert 'button (disabled) 저장' in raw[1]
assert '표준 화질 완료' in raw[1] and '고화질 완료' in raw[1]
assert 'orq0TMVkFts/monetization/ads' in raw[2] and 'text 사용' in raw[2]
assert '검사 중' not in raw[2] and 'button (disabled) 저장' in raw[2]
prior = read(P / 'private-settings-direct-review-v1.json')
git = read(P / 'production-git-verification-v1.json')
assert prior['fullAvailableSettingsVerified'] and prior['uploadedCcOff1080p60SelectedFramesReviewed']
assert git['pushed'] and git['allFinalRemoteBlobsVerified'] and git['exactLocalRemoteMatch']
main = ROOT / 'projects/game-math-orientation-matrices/project.json'
main_before, index_before = sha(main), sha(ROOT / '.git/index')
now = datetime.now(timezone.utc).isoformat()
record = dict(schemaVersion=1, observedAt=now, actualVideoId='orq0TMVkFts', tab='116',
    contentPageReloaded=True, contentListNotice='—', actualMonetizationStatus='사용',
    currentVisibility='private', automaticAdCheckPassed=True, allAutomaticChecksPassed=True,
    fullAvailableSettingsVerified=True, fullSettingsComplete=True,
    actualSdHdComplete=True, productionGitDelivered=True, productionGitCommit=git['commit'],
    previousObservation=rel(P / 'automatic-ad-followup-v2.json'),
    previousPrivateSettings=rel(P / 'private-settings-direct-review-v1.json'),
    productionGitEvidence=rel(P / 'production-git-verification-v1.json'),
    basis='Fresh content row has no notices and no checking marker; current monetization page shows 사용 and saved state. Retain the previously verified available settings and bounded uploaded-pixel proof.',
    optionalCcPropagationPending=prior['optionalCcPropagationPending'],
    automaticDubbingHumanReviewPending=prior['automaticDubbingHumanReviewPending'],
    humanListeningApproved=False, humanPronunciationApproved=False, publicRightsApproved=False,
    scheduleReplacementVerified=False, obsoleteDeleted=False,
    uiProofs=[dict(path=rel(p), sha256=sha(p)) for p in proofs],
    newUploadSelections=0, newMediaWorkers=0, newProductionGitDelivery=0)
save(out, record)
review = copy.deepcopy(prior)
review.update(schemaVersion=2, reviewedAt=now, fullSettingsComplete=True,
    automaticAdCheckPassed=True, actualAdStatus='사용;current-content-list-no-notices',
    gitDelivered=True, productionGitCommit=git['commit'],
    previousPrivateSettingsReview=record['previousPrivateSettings'],
    automaticChecksReview=rel(out),
    claimScope='Completed available private settings and platform checks with retained bounded upload-pixel proof; human whole listening, pronunciation, public rights and automatic dubbing review remain pending.')
save(P / 'private-settings-direct-review-v2.json', review)
upload = read(P / 'youtube-upload-v1.json')
assert upload['actualVideoId'] == 'orq0TMVkFts'
upload.update(status='private-full-available-settings-and-automatic-checks-verified;ready-for-schedule-replacement',
    fullSettingsComplete=True, automaticAdCheckPassed=True, allAutomaticChecksPassed=True,
    actualAdStatus=record['actualAdStatus'] if 'actualAdStatus' in record else '사용',
    lastObservedAt=now, privateSettingsEvidence=rel(P / 'private-settings-direct-review-v2.json'),
    automaticChecksEvidence=rel(out))
upload['checks'].update(adSuitability='actual-monetization-enabled;completed-content-list-no-notices',
    overall='actual-content-list-no-notices')
save(P / 'youtube-upload-v1.json', upload)
next_step = ('Current orq0TMVkFts has completed platform checks, full available private settings and production Git ee5fe58. '
    'Read the current baseline6-kP and actual Studio/ledger future09 slot, save/reopen the reviewed replacement, then record its schedule and selectively deliver changed metadata. '
    'Ask one new action-time confirmation for corresponding orientation obsolete deletion only after replacement verification; motion oldmBDd question already once pending/noanswer, do not repeat. '
    'No repeat upload, media, playback or production Git delivery. Continue through normal-transform-UV only, then pause task-owned continuation.')
checkpoint = read(O / 'latest-checkpoint.json')
checkpoint.update(stage='orientation-current34-private-settings-checks-and-production-Git-complete;ready-for-actual-schedule-replacement',
    next=next_step, fullSettingsComplete=True, automaticAdCheckPassed=True,
    actualMonetizationStatus='사용', actualOverallChecksStatus='completed-no-notices',
    privateSettingsReview=rel(P / 'private-settings-direct-review-v2.json'),
    lastAutomaticAdObservation=rel(out), lastAutomaticAdObservationAt=now)
save(O / 'latest-checkpoint.json', checkpoint)
queue = read(Q)
queue['currentOrientationReview'].update(stage=checkpoint['stage'], next=next_step,
    fullSettingsComplete=True, automaticAdCheckPassed=True,
    privateSettingsReview=checkpoint['privateSettingsReview'],
    actualMonetizationStatus='사용', actualOverallChecksStatus='completed-no-notices',
    lastAutomaticAdObservation=rel(out), lastAutomaticAdObservationAt=now)
save(Q, queue)
assert sha(main) == main_before and sha(ROOT / '.git/index') == index_before
print(json.dumps(dict(actualVideoId='orq0TMVkFts', checksComplete=True,
    privateSettingsComplete=True, productionGitVerified=True, scheduleChanged=False,
    rootAndExternalIndexUnchanged=True)))
