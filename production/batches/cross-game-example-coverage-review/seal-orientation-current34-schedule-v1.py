"""Record the actual saved/reopened replacement schedule. No platform operation."""
from pathlib import Path
from datetime import datetime, timezone
import copy
import hashlib
import json
import os
import re

ROOT = Path(__file__).resolve().parents[3]
B = Path(__file__).resolve().parent
O = ROOT / 'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
P = O / 'publishing'
UI = P / 'ui-proof-v1'
SLUG = 'game-math-orientation-matrices'
NEW = 'orq0TMVkFts'
OLD = '6-kP65hrZcI'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
rel = lambda p: p.relative_to(ROOT).as_posix()
now = datetime.now(timezone.utc).isoformat()


def save(p, value):
    temp = p.with_name(p.name + '.schedule-v1.writing')
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf-8')
    os.replace(temp, p)


def rows(text):
    result = {}
    for block in re.split(r'(?m)^\s*\d+ row\r?$', text):
        title = re.search(r'link Description: (.*?), Value: studio\.youtube\.com/video/([\w-]+)/edit, ID: video-title', block)
        date = re.search(r'text (2026\.\s*\d+\.\s*\d+\.)', block)
        if title and date:
            assert title[2] not in result, 'Duplicate actual video row'
            result[title[2]] = dict(title=title[1], date=date[1], scheduled='text 예약됨' in block)
    return result


assert not (P / 'schedule-direct-review-v1.json').exists(), 'Already recorded; do not repeat'
promotion = read(O / 'current34-main-promotion-v1.json')
for item in promotion['otherProtectedInputs'] + promotion['repairCandidates']:
    assert sha(ROOT / item['path']) == item['sha256'], item['path']
assert sha(ROOT / promotion['baselineMain']['path']) == promotion['baselineMain']['sha256']
git = read(P / 'production-git-verification-v1.json')
assert git['pushed'] and git['allFinalRemoteBlobsVerified'] and git['exactLocalRemoteMatch']
assert git['commit'] == 'ee5fe58fc23f9750d616e80a11cda29d436396e3'
settings = read(P / 'private-settings-direct-review-v2.json')
assert settings['actualVideoId'] == NEW and settings['privateSavedAndReopened']
assert settings['fullSettingsComplete'] and settings['automaticAdCheckPassed'] and settings['gitDelivered']
checks = read(P / 'automatic-ad-followup-v3.json')
assert checks['automaticAdCheckPassed'] and checks['allAutomaticChecksPassed']

old_schedule = (UI / 'baseline-schedule-before-v1.ax.txt').read_text('utf-8')
reopened = (UI / 'replacement-schedule-reopened-v1.ax.txt').read_text('utf-8')
prepared = (UI / 'replacement-schedule-prepared-v1.ax.txt').read_text('utf-8')
old_private = (UI / 'baseline-private-reopened-v1.ax.txt').read_text('utf-8')
delete_prepared = (UI / 'baseline-delete-confirmation-v1.ax.txt').read_text('utf-8')
for text, video in [(old_schedule, OLD), (reopened, NEW)]:
    assert video in text and '2026. 10. 13.' in text
    assert '오전 9:00' in text and 'GMT+0900' in text
    assert 'button (disabled) 저장' in text and 'button (disabled) 완료' in text
assert '서울(GMT+09:00)' in prepared and NEW in prepared
assert 'checkbox Description: Premieres 동영상으로 설정, Value: 0' in reopened
assert OLD in old_private and 'text 비공개' in old_private and 'button (disabled) 저장' in old_private
assert OLD in delete_prepared and 'checkbox Value: 0' in delete_prepared
assert 'button (disabled) 영구 삭제' in delete_prepared and '영구적으로 삭제' in delete_prepared
before = rows((UI / 'automatic-checks-complete-v3.ax.txt').read_text('utf-8'))
after = rows((UI / 'future-slots-after-replacement-v1.ax.txt').read_text('utf-8'))
assert len(before) == 30 and len(after) == 30
assert before[OLD]['scheduled'] and not before[NEW]['scheduled']
assert after[NEW]['scheduled'] and after[NEW]['date'] == '2026. 10. 13.'
foreign_before = {k: v for k, v in before.items() if v['scheduled'] and k not in [NEW, OLD]}
foreign_after = {k: v for k, v in after.items() if v['scheduled'] and k not in [NEW, OLD]}
assert foreign_before == foreign_after and len(foreign_before) == 26, 'Unrelated future booking changed'
assert not any(v['date'] == '2026. 10. 13.' for v in foreign_after.values())

main_path = ROOT / f'projects/{SLUG}/project.json'
main_before = sha(main_path)
assert main_before == read(O / 'current34-main-private-update-v1.json')['currentMain']['sha256']
main = read(main_path)
main_paths = copy.deepcopy(main['paths'])
ledger_path = ROOT / 'shared/publishing/daily-alternating-schedule.json'
ledger_before = sha(ledger_path)
ledger = read(ledger_path)
ledger_foreign_before = copy.deepcopy({k: v for k, v in ledger.items() if k not in ['updatedAt', 'actualSchedules', 'replacementHistory']})
foreign_entries = copy.deepcopy([v for v in ledger['actualSchedules'] if v['slug'] != SLUG])
matches = [v for v in ledger['actualSchedules'] if v['slug'] == SLUG]
assert len(matches) == 1 and matches[0]['videoId'] == OLD
assert matches[0]['date'] == '2026-10-13' and matches[0]['time'] == '09:00'
old_entry = copy.deepcopy(matches[0])
history_before = copy.deepcopy(ledger.get('replacementHistory', []))
evidence_names = ['automatic-checks-complete-v3.ax.txt', 'baseline-before-replacement-v1.ax.txt',
    'baseline-schedule-before-v1.ax.txt', 'baseline-private-reopened-v1.ax.txt',
    'replacement-schedule-prepared-v1.ax.txt', 'replacement-schedule-saved-v1.ax.txt',
    'replacement-schedule-reopened-v1.ax.txt', 'future-slots-after-replacement-v1.ax.txt',
    'baseline-delete-confirmation-v1.ax.txt']
proof = dict(schemaVersion=1, reviewedAt=now, actualVideoId=NEW, oldVideoId=OLD,
    actualCuaTabs=[116, 118], actualDate='2026-10-13', actualTime='09:00', timezone='Asia/Seoul',
    savedTimezoneSelection='서울(GMT+09:00)', reopenedTimezone='GMT+0900',
    scheduledAt='2026-10-13T09:00:00+09:00', publishAt='2026-10-13T00:00:00Z',
    actualSaveObserved=True, savedAndReopened=True, unchangedDoneAndSaveDisabled=True,
    premiereEnabled=False, futureScheduledListVerified=True, beforeVisibleRowCount=30,
    afterVisibleRowCount=30, previous26OtherScheduledTitlesAndDatesUnchanged=True,
    otherScheduledRows=foreign_after, originalFutureSlotVerified=True,
    oldCurrentVisibility='private', baselineReservationRemovedAfterReviewedReplacementReady=True,
    oldPrivateSaveReopenVerified=True, obsoleteDeleted=False,
    irreversibleDeletionConfirmation='required-not-yet-asked', deletionQuestionCount=0,
    privateSettingsEvidence=rel(P / 'private-settings-direct-review-v2.json'),
    automaticChecksEvidence=rel(P / 'automatic-ad-followup-v3.json'),
    productionGitCommit=git['commit'], productionGitVerified=True,
    humanListeningApproved=False, humanPronunciationApproved=False, publicRightsApproved=False,
    optionalCcPropagationPending=True, automaticDubbingHumanReviewPending=True,
    evidence=[dict(path=rel(UI / f), sha256=sha(UI / f)) for f in evidence_names],
    localOnlyImages=[dict(path=rel(UI / f), sha256=sha(UI / f)) for f in
        ['replacement-schedule-reopened-v1.jpg', 'baseline-delete-confirmation-v1.jpg']])
save(P / 'schedule-direct-review-v1.json', proof)
confirmation = dict(schemaVersion=1, preparedAt=now, actualCuaTab='118', actualVideoId=OLD,
    replacementVideoId=NEW, replacementScheduledAt=proof['scheduledAt'],
    replacementSaveReopenVerified=True, previousVideoVisibility='private',
    status='required-not-yet-asked', questionAsked=False, questionCount=0, userAnswer=None,
    irreversibleDeletionApproved=False, permanentDeletionExecuted=False,
    checkboxChecked=False, finalDeleteDisabled=True,
    question='새 검수본으로 예약 교체가 완료되었습니다. 옛 영상 6-kP65hrZcI를 YouTube에서 영구 삭제해도 될까요?',
    confirmationPolicy='Computer Use: Permanently delete data requires confirmation at action time.',
    preparedScreen=rel(UI / 'baseline-delete-confirmation-v1.jpg'),
    preparedScreenSha256=sha(UI / 'baseline-delete-confirmation-v1.jpg'),
    doNotRepeatQuestionWithoutMaterialChange=True,
    oldMotionQuestionAlreadyPendingNoAnswer=True, oldMotionQuestionRepeated=False)
save(P / 'obsolete-deletion-action-time-confirmation-v1.json', confirmation)
upload = read(P / 'youtube-upload-v1.json')
upload.update(status='scheduled-saved-reopened;obsolete-deletion-action-time-confirmation-required',
    scheduled=True, scheduledAt=proof['scheduledAt'], publishAt=proof['publishAt'],
    scheduleSavedReopenedVerified=True, scheduleEvidence=rel(P / 'schedule-direct-review-v1.json'),
    productionGitEvidence=rel(P / 'production-git-verification-v1.json'), productionGitDelivered=True,
    lastObservedAt=now, privacy='scheduled-until-public-private', baselineScheduleChanged=True,
    baselineCurrentVisibility='private', baselinePrivateReopenedVerified=True, baselinePreserved=True,
    obsoleteDeleted=False, deletionConfirmation=rel(P / 'obsolete-deletion-action-time-confirmation-v1.json'))
save(P / 'youtube-upload-v1.json', upload)
main['status'] = 'current34-four-game-reviewed-scheduled;obsolete-delete-confirmation-required'
main['publishing'].update(fullSettingsComplete=True, fullSettingsVerified=True,
    privateSettingsReview=proof['privateSettingsEvidence'], automaticAdStatus='사용;checks-complete-no-notices',
    scheduled=True, scheduledPublishAt=proof['publishAt'], scheduledAt=proof['scheduledAt'],
    privacyStatus='scheduled', scheduleSavedReopenedVerified=True, baselineScheduleChanged=True,
    baselineCurrentVisibility='private', baselinePreserved=True, obsoleteDeleted=False,
    status='reviewed-replacement-scheduled-saved-reopened',
    productionGitEvidence=upload['productionGitEvidence'], scheduleEvidence=upload['scheduleEvidence'])
assert main['paths'] == main_paths
backup = O / 'main-before-current34-schedule-update-v1.json'
assert not backup.exists()
backup.write_bytes(main_path.read_bytes())
save(main_path, main)
save(O / 'current34-main-schedule-update-v1.json', dict(schemaVersion=1, recordedAt=now,
    beforeSha256=main_before, afterSha256=sha(main_path), actualVideoId=NEW,
    exactPrivateMainBackup=rel(backup), exactPrivateMainBackupSha256=sha(backup),
    intentionalPublishingUpdate=True, localMediaPathsUnchanged=True,
    preservedOriginalMain=promotion['baselineMain'], preservationGuard=rel(O / 'current34-main-promotion-v1.json'),
    other78ProtectedInputsUnchanged=True, repairCandidateUnchanged=True, obsoleteDeleted=False))
entry = matches[0]
entry.update(videoId=NEW, timezone='Asia/Seoul', publishAt=proof['publishAt'], verifiedAt=now,
    evidence=upload['scheduleEvidence'], evidenceSha256=sha(P / 'schedule-direct-review-v1.json'),
    status='actual-saved-reopened', oldVideoId=OLD, oldCurrentVisibility='private',
    oldVideoPermanentlyDeleted=False)
ledger.setdefault('replacementHistory', []).append(dict(replacedAt=now, oldSchedule=old_entry,
    newSchedule=copy.deepcopy(entry), oldVideoCurrentVisibility='private', oldVideoPermanentlyDeleted=False,
    deletionConfirmation='required-not-yet-asked', evidence=upload['scheduleEvidence']))
ledger['updatedAt'] = now
assert ledger_foreign_before == {k: v for k, v in ledger.items() if k not in ['updatedAt', 'actualSchedules', 'replacementHistory']}
assert [v for v in ledger['actualSchedules'] if v['slug'] != SLUG] == foreign_entries
assert ledger['replacementHistory'][:-1] == history_before
save(ledger_path, ledger)
save(P / 'schedule-ledger-update-v1.json', dict(schemaVersion=1, recordedAt=now,
    beforeSha256=ledger_before, afterSha256=sha(ledger_path), changedSlugOnly=SLUG,
    allOtherActualScheduleEntriesPreserved=True, allPreviousReplacementHistoryPreserved=True,
    allOtherLedgerFieldsPreserved=True, obsoleteDeleted=False))
next_step = ('Orientation orq0TMVkFts completed production/private settings/checks/Git and actual Oct13 '
    '09:00Asia/Seoul schedule saved/reopened. Old6-kP private preserved, final deletion unchecked/disabled. '
    'Deliver only changed scheduling metadata then ask one action-time deletion confirmation for6-kP; '
    'do not repeat motion oldmBDd already-once-pending question or any completed media/upload/Git. '
    'Continue closest actual future hierarchical Oct14 and remaining authorized revisions from actual '
    'checkpoints, preserve foreign Part2/lighting/research/index; stop after normal-transform-UV fulldelivery '
    'and actual replacement. No new lectures/Sakurai6.')
cp = read(O / 'latest-checkpoint.json')
cp.update(recordedAt=now, stage='orientation-current34-reviewed-scheduled;obsolete-deletion-confirmation-required',
    productionGitDelivered=True, scheduleReplacementVerified=True, scheduleDirectReview=upload['scheduleEvidence'],
    actualScheduledAt=proof['scheduledAt'], baselineCurrentStudioVisibility='private',
    oldUploadDeleted=False, deletionConfirmationPending=True, deletionQuestionAsked=False,
    deletionConfirmation=upload['deletionConfirmation'], postPromotionGuard=rel(O / 'current34-main-schedule-update-v1.json'),
    next=next_step)
save(O / 'latest-checkpoint.json', cp)
queue = read(B / 'queue.json')
queue.update(updatedAt=now, status='active-hierarchical-next;orientation-motion-obsolete-confirmations-pending', next=next_step)
queue['currentOrientationReview'].update(stage=cp['stage'], next=next_step,
    productionGitDelivered=True, scheduleReplacementVerified=True, actualScheduledAt=proof['scheduledAt'],
    currentStudioVisibility='scheduled', oldCurrentStudioVisibility='private', oldUploadDeleted=False,
    deletionConfirmationPending=True, deletionQuestionAsked=False, deletionConfirmation=upload['deletionConfirmation'],
    scheduleDirectReview=upload['scheduleEvidence'], postPromotionGuard=cp['postPromotionGuard'])
for item in queue['futureScheduledPriority']:
    if item['slug'] == SLUG:
        item.update(videoId=NEW, reviewedReplacementScheduled=True, actualDate='2026-10-13',
            dateIsLocalLedgerPendingFreshStudio=False, oldVideoId=OLD, oldUploadDeleted=False)
save(B / 'queue.json', queue)
print(json.dumps(dict(actualVideoId=NEW, scheduledAt=proof['scheduledAt'], savedReopened=True,
    other26ScheduledRowsUnchanged=True, other78Unchanged=True, productionGitDelivered=True,
    obsoleteDeleted=False, deletionQuestionAsked=False)))
