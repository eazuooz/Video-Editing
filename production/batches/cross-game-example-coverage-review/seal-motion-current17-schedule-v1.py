"""Seal observed schedule and pending irreversible deletion; no platform operation."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, re, copy

ROOT = Path(__file__).resolve().parents[3]
B = Path(__file__).resolve().parent
R = ROOT / 'projects/motion-sickness-games/production/revision-cross-game-four-v1'
P = R / 'publishing'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
now = datetime.now(timezone.utc).isoformat()

def save(p, value):
    tmp = p.with_name(p.name + '.schedule-v1.writing')
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf-8')
    os.replace(tmp, p)

def rows(text):
    result = {}
    for block in re.split(r'(?m)^\t{7}\d+ row\r?$', text):
        title = re.search(r'link Description: (.*?), Value: studio\.youtube\.com/video/([\w-]+)/edit, ID: video-title', block)
        date = re.search(r'text (2026\. \d+\. \d+\.)', block)
        if title and date:
            result[title[2]] = dict(title=title[1], date=date[1], scheduled='text 예약됨' in block)
    return result

assert not (P / 'schedule-direct-review-v1.json').exists(), 'Existing sealed proof: do not repeat'
promotion = read(R / 'current17-main-promotion-v1.json')
for row in promotion['otherProtectedInputs']:
    assert sha(ROOT / row['path']) == row['sha256'], row['path']
git = read(P / 'production-git-verification-v1.json')
assert git['pushed'] and git['allFinalRemoteBlobsVerified'] and git['exactLocalRemoteMatch']
private = read(P / 'private-settings-direct-review-v1.json')
assert private['fullAvailableSettingsVerified'] and private['actualVideoId'] == 'lXjDBqONLWs'
reopened = (P / 'current17-schedule-reopened-v1.ax.txt').read_text('utf-8')
assert 'lXjDBqONLWs' in reopened and '2026. 10. 12.' in reopened
assert '오전 9:00' in reopened and 'GMT+0900' in reopened
assert '모든 변경사항이 저장되었습니다.' in reopened and 'button (disabled) 저장' in reopened
before = rows((P / 'current17-future-slots-before-schedule-v1.ax.txt').read_text('utf-8'))
after = rows((P / 'current17-future-slots-after-schedule-v1.ax.txt').read_text('utf-8'))
assert len(before) == 27 and len(after) == 28, (len(before), len(after))
assert all(after.get(k) == v for k, v in before.items()), 'Unrelated scheduled title/date changed'
assert after['lXjDBqONLWs']['date'] == '2026. 10. 12.' and after['lXjDBqONLWs']['scheduled']
assert not any(v['date'] == '2026. 10. 12.' for v in before.values())
old_text = (P / 'current17-obsolete-before-delete-v1.ax.txt').read_text('utf-8')
assert 'mBDd9VzSTkA' in old_text and 'text 비공개' in old_text
delete_text = (P / 'current17-obsolete-delete-confirmation-v1.ax.txt').read_text('utf-8')
assert '영구적으로 삭제' in delete_text and 'button (disabled) 영구 삭제' in delete_text
evidence_names = ['current17-schedule-reopened-v1.ax.txt',
    'current17-future-slots-before-schedule-v1.ax.txt', 'current17-future-slots-after-schedule-v1.ax.txt',
    'current17-obsolete-before-delete-v1.ax.txt', 'current17-obsolete-delete-confirmation-v1.ax.txt']
proof = dict(schemaVersion=1, reviewedAt=now, actualVideoId='lXjDBqONLWs',
    actualCuaTabs=[100,102,103], actualDate='2026-10-12', actualTime='09:00',
    timezone='Asia/Seoul', savedTimezoneSelection='서울 (GMT+09:00)', reopenedTimezone='GMT+0900',
    scheduledAt='2026-10-12T09:00:00+09:00', publishAt='2026-10-12T00:00:00Z',
    actualSaveObserved=True, savedAndReopened=True, unchangedDoneAndSaveDisabled=True,
    futureScheduledListVerified=True, beforeRowCount=27, afterRowCount=28,
    previous27ScheduledTitlesAndDatesUnchanged=True, currentSlotEmptyBefore=True,
    originalHistoricalSlotRetained=True, oldVideoId='mBDd9VzSTkA', oldCurrentVisibility='private',
    obsoleteDeleted=False, irreversibleDeletionConfirmation='pending-action-time-user-reply',
    privateSettingsEvidence='publishing/private-settings-direct-review-v1.json',
    productionGitCommit=git['commit'], productionGitVerified=True,
    humanListeningApproved=False, publicRightsApproved=False,
    evidence=[dict(path=(P / f).relative_to(ROOT).as_posix(), sha256=sha(P / f)) for f in evidence_names],
    localOnlyImages=[dict(path=(P / f).relative_to(ROOT).as_posix(), sha256=sha(P / f)) for f in [
        'current17-schedule-reopened-v1.png', 'current17-obsolete-delete-confirmation-v1.png']])
save(P / 'schedule-direct-review-v1.json', proof)
upload = read(P / 'youtube-upload-v1.json')
upload.update(status='scheduled-saved-reopened;obsolete-deletion-confirmation-pending',
    scheduled=True, scheduledAt=proof['scheduledAt'], publishAt=proof['publishAt'],
    scheduleSavedReopenedVerified=True, scheduleEvidence=(P / 'schedule-direct-review-v1.json').relative_to(ROOT).as_posix(),
    productionGitEvidence=(P / 'production-git-verification-v1.json').relative_to(ROOT).as_posix(),
    productionGitDelivered=True, lastObservedAt=now, privacy='scheduled-until-public-private',
    obsoleteDeleted=False)
save(P / 'youtube-upload-v1.json', upload)
main_path = ROOT / 'projects/motion-sickness-games/project.json'
main_before = sha(main_path)
main = read(main_path)
main['status'] = 'cross-game-four-current17-reviewed-scheduled;obsolete-delete-confirmation-pending'
main['publishing'].update(scheduled=True, scheduledPublishAt=proof['publishAt'],
    scheduledAt=proof['scheduledAt'], privacyStatus='scheduled', scheduleSavedReopenedVerified=True,
    status='reviewed-replacement-scheduled-saved-reopened',
    productionGitEvidence=upload['productionGitEvidence'], scheduleEvidence=upload['scheduleEvidence'])
save(main_path, main)
save(R / 'current17-main-schedule-update-v1.json', dict(schemaVersion=1, recordedAt=now,
    beforeSha256=main_before, afterSha256=sha(main_path), actualVideoId='lXjDBqONLWs',
    intentionalPublishingUpdate=True, localMediaPathsUnchanged=True,
    other70ProtectedInputsUnchanged=True, obsoleteDeleted=False))
ledger_path = ROOT / 'shared/publishing/daily-alternating-schedule.json'
ledger_before = sha(ledger_path)
ledger = read(ledger_path)
foreign_before = copy.deepcopy([v for v in ledger['actualSchedules'] if v['slug'] != 'motion-sickness-games'])
matches = [v for v in ledger['actualSchedules'] if v['slug'] == 'motion-sickness-games']
assert len(matches) == 1 and matches[0]['videoId'] == 'mBDd9VzSTkA'
old = copy.deepcopy(matches[0])
entry = matches[0]
entry.update(videoId='lXjDBqONLWs', date='2026-10-12', time='09:00', timezone='Asia/Seoul',
    timezoneOffset='+09:00', publishAt=proof['publishAt'], verifiedAt=now,
    evidence=upload['scheduleEvidence'], evidenceSha256=sha(P / 'schedule-direct-review-v1.json'),
    status='actual-saved-reopened', oldVideoId='mBDd9VzSTkA', oldCurrentVisibility='private',
    oldVideoPermanentlyDeleted=False)
ledger.setdefault('replacementHistory', []).append(dict(replacedAt=now, oldSchedule=old,
    newSchedule=copy.deepcopy(entry), oldVideoCurrentVisibility='private', oldVideoPermanentlyDeleted=False,
    deletionConfirmation='pending-action-time-user-reply', evidence=upload['scheduleEvidence']))
ledger['updatedAt'] = now
assert [v for v in ledger['actualSchedules'] if v['slug'] != 'motion-sickness-games'] == foreign_before
save(ledger_path, ledger)
save(P / 'schedule-ledger-update-v1.json', dict(schemaVersion=1, recordedAt=now,
    beforeSha256=ledger_before, afterSha256=sha(ledger_path),
    changedSlugOnly='motion-sickness-games', allOtherActualScheduleEntriesPreserved=True,
    obsoleteDeleted=False))
next_step = ('Reviewed lXjDBqONLWs production/private/Git complete; Oct12 09:00Asia/Seoul schedule '
    'saved/reopened and future list verified. Await action-time confirmation for obsolete mBDd9VzSTkA '
    'permanent deletion; do not repeat question or upload. Continue Oct13 orientation from actual '
    'checkpoint, preserve completed6PCM/native/pilots; minimum4games and finaldelivery pending. '
    'Stop after normal-transform-UV; no newSakurai6.')
cp = read(R / 'latest-checkpoint.json')
cp.update(recordedAt=now, stage='current17-reviewed-scheduled-obsolete-deletion-confirmation-pending',
    gitDelivered=True, productionGitVerification=upload['productionGitEvidence'],
    scheduleReplacementVerified=True, scheduleDirectReview=upload['scheduleEvidence'],
    actualScheduledAt=proof['scheduledAt'], deletionConfirmationPending=True,
    oldUploadDeleted=False, next=next_step)
save(R / 'latest-checkpoint.json', cp)
queue = read(B / 'queue.json')
queue.update(updatedAt=now, status='active-orientation-next-motion-delete-confirmation-pending', next=next_step)
queue['currentMotionReview'].update(stage=cp['stage'], status=cp['stage'], next=next_step,
    gitDelivered=True, scheduleReplacementVerified=True, actualScheduledAt=proof['scheduledAt'],
    currentStudioVisibility='scheduled', oldCurrentStudioVisibility='private',
    oldUploadDeleted=False, deletionConfirmationPending=True, scheduleDirectReview=upload['scheduleEvidence'])
for item in queue['futureScheduledPriority']:
    if item['slug'] == 'motion-sickness-games':
        item.update(videoId='lXjDBqONLWs', reviewedReplacementScheduled=True,
            oldVideoId='mBDd9VzSTkA', oldUploadDeleted=False)
save(B / 'queue.json', queue)
print(json.dumps(dict(actualVideoId='lXjDBqONLWs', scheduledAt=proof['scheduledAt'],
    savedReopened=True, previous27Unchanged=True, other70Unchanged=True,
    productionGitDelivered=True, obsoleteDeleted=False)))
