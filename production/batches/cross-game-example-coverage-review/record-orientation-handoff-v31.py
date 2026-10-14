"""Seal the completed actual schedule/Git and the single requested delete confirmation."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import psutil

ROOT = Path(__file__).resolve().parents[3]
B = Path(__file__).resolve().parent
O = ROOT / 'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
R = ROOT / 'projects/motion-sickness-games/production/revision-cross-game-four-v1'
P = O / 'publishing'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
rel = lambda p: p.relative_to(ROOT).as_posix()


def save(p, value):
    temp = p.with_name(p.name + '.v31.writing')
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf-8')
    os.replace(temp, p)


out = R / 'resource-and-annotation-handoff-v31.json'
assert not out.exists(), 'Do not repeat a completed handoff'
promotion = read(O / 'current34-main-promotion-v1.json')
transition = read(O / 'current34-main-schedule-update-v1.json')
assert sha(ROOT / 'projects/game-math-orientation-matrices/project.json') == transition['afterSha256']
for entry in promotion['otherProtectedInputs'] + promotion['repairCandidates'] + [promotion['baselineMain']]:
    assert sha(ROOT / entry['path']) == entry['sha256'], entry['path']
assert sha(ROOT / transition['exactPrivateMainBackup']) == transition['beforeSha256']
git = read(P / 'schedule-git-verification-v1.json')
assert git['pushed'] and git['allFinalRemoteBlobsVerified'] and git['exactLocalRemoteMatch']
assert git['commit'] == 'c8a656139dbb6d430a4e0572237f5e5de5a5a78d' and git['verifiedBlobCount'] == 20
assert git['externalIndexUnchanged'] and git['foreignRebuildUnchanged']
schedule = read(P / 'schedule-direct-review-v1.json')
settings = read(P / 'private-settings-direct-review-v2.json')
assert schedule['savedAndReopened'] and schedule['previous26OtherScheduledTitlesAndDatesUnchanged']
assert settings['fullSettingsComplete'] and settings['automaticAdCheckPassed']
confirmation_path = P / 'obsolete-deletion-action-time-confirmation-v1.json'
confirmation = read(confirmation_path)
assert confirmation['questionCount'] == 0 and not confirmation['questionAsked']
assert not confirmation['permanentDeletionExecuted'] and not confirmation['checkboxChecked']
workers = []
for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
    try:
        command = ' '.join(proc.info['cmdline'] or [])
        if (proc.pid != os.getpid() and (proc.info['name'] or '').lower() in ['python.exe', 'node.exe', 'ffmpeg.exe']
                and 'cross-game-example-coverage-review' in command
                and any(token in command for token in ['render-orientation', 'review-orientation',
                    'extract-orientation', 'build-orientation', 'assemble-orientation', 'collect-orientation',
                    'render-motion', 'review-motion', 'extract-motion', 'deliver-orientation'])):
            workers.append(dict(pid=proc.pid, createTime=proc.info['create_time'], command=command))
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass
assert not workers, workers
research = Path('C:/Users/eazuo/renderformer/tmp/placement_focus_20261008/status.json')
assert sha(research) == 'bbeac85c5f493baec614eeb5fae13f15d8b9b913f58631dce2d2ee211f07b0b8'
assert read(research)['completed'] == 1088
helper = None
try:
    process = psutil.Process(27140)
    if abs(process.create_time() - 1791509666.837781) < .01:
        helper = dict(pid=27140, createTime=process.create_time(), command=process.cmdline(),
            cwd=process.cwd(), alive=True, newServerStarted=False)
except (psutil.NoSuchProcess, psutil.AccessDenied):
    pass
now = datetime.now(timezone.utc).isoformat()
git.update(actualSession=78709, initialChunk='234f34', completionChunk='b572fa', actualOuterExitCode=0)
save(P / 'schedule-git-verification-v1.json', git)
confirmation.update(status='pending-action-time-user-reply', questionAsked=True, questionCount=1,
    requestedAt=now, requestTool='functions.request_user_input_async', requestAccepted=True,
    actualQuestion='새 검수본 orq0TMVkFts의 10월 13일 오전 9시(서울) 예약 교체와 Git 전달이 완료됐습니다. '
        '현재 비공개인 옛 영상 ‘게임수학 Part 2 · 3D 회전 ① 방향과 회전 행렬’(6-kP65hrZcI, 15:03)을 '
        'YouTube에서 영구 삭제할까요? 삭제하면 동영상과 기존 분석 기록을 복구할 수 없습니다.',
    scheduleGitVerification=rel(P / 'schedule-git-verification-v1.json'), scheduleGitCommit=git['commit'])
save(confirmation_path, confirmation)
upload_path = P / 'youtube-upload-v1.json'
upload = read(upload_path)
upload.update(status='scheduled-saved-reopened;obsolete-deletion-question-once-pending',
    scheduleGitDelivered=True, scheduleGitCommit=git['commit'],
    scheduleGitVerification=rel(P / 'schedule-git-verification-v1.json'),
    deletionQuestionAsked=True, deletionQuestionCount=1, deletionConfirmationPending=True,
    obsoleteDeleted=False, lastFollowupRecordedAt=now)
save(upload_path, upload)
previous = R / 'resource-and-annotation-handoff-v30.json'
data = read(previous)
next_step = ('Orientation orq0TMVkFts full private settings/automatic checks/production Git and actual Oct13 '
    '09:00Asia/Seoul replacement are complete; follow-up Git c8a6561/20 exact final blobs delivered. '
    'Old6-kP private; action-time permanent-delete question requested exactly once through actual async '
    'input tool and still pending/noanswer; do not repeat or delete without its answer. Motion oldmBDd '
    'question already once pending/noanswer, do not repeat. Continue closest actual future hierarchical '
    'Oct14 and remaining authorized revisions from their real checkpoints; preserve foreign Part2, '
    'lighting/research/index and completed media/upload/playback/Git. Remain ACTIVE until normal-transform-UV '
    'final3D complete delivery and actual schedule replacement; then pause task-owned continuation. '
    'No new lectures/Sakurai6. Quiet on unchanged healthy state.')
data.update(schemaVersion=1, recordedAt=now, previousHandoff=rel(previous), previousHandoffSha256=sha(previous),
    stage='orientation-current34-reviewed-scheduled-and-Git-delivered;obsolete-question-once-pending',
    fullSettingsComplete=True, automaticAdCheckPassed=True, lastActualAdStatus='사용;completed-no-notices',
    actualScheduleSavedReopened=True, scheduleReplacementVerified=True,
    actualScheduledAt=schedule['scheduledAt'], actualPublishAt=schedule['publishAt'],
    actualOriginalFutureSlotReplaced=True, previous26OtherScheduledTitlesAndDatesUnchanged=True,
    actualScheduleGitSession=78709, scheduleGitCompletionChunk='b572fa', actualScheduleGitOuterExitCode=0,
    scheduleGitCommit=git['commit'], scheduleGitRemote=git['remoteCommit'], all20FollowupRemoteBlobsVerified=True,
    followupSharedHeadSubsetsOnly=True, followupForeignRebuildCount=git['foreignRebuildCount'],
    mainCurrentSha256=transition['afterSha256'], postPromotionGuard=rel(O / 'current34-main-schedule-update-v1.json'),
    baselineScheduleChanged=True, baselineCurrentVisibility='private', baselinePrivateSaveReopenVerified=True,
    lastBaselineActualReservation='Original Oct13 09GMT+0900 actually verified before replacement; now private',
    orientationOldDelete=dict(videoId='6-kP65hrZcI', questionAskedOnce=True, questionCount=1,
        answerReceived=False, deletePerformed=False, checkboxChecked=False, finalDeleteDisabled=True,
        confirmation=rel(confirmation_path)),
    activeOwnedWorkers=0, helper9250=helper, next=next_step)
records = ['current34-final-technical-and-pixel-direct-review-v5.json', 'current34-final-normal-direct-review-v5.json',
    'current34-main-promotion-v1.json', 'current34-main-private-update-v1.json', 'current34-main-schedule-update-v1.json',
    'current34-four-output-collection-verification-v1.json', 'publishing/youtube-upload-v1.json',
    'publishing/private-settings-direct-review-v2.json', 'publishing/production-git-verification-v1.json',
    'publishing/automatic-ad-followup-v3.json', 'publishing/schedule-direct-review-v1.json',
    'publishing/schedule-git-verification-v1.json', 'publishing/obsolete-deletion-action-time-confirmation-v1.json',
    'publishing/schedule-seal-prewrite-failure-v1.json']
data['boundRecords'] = [dict(path=rel(O / f), sha256=sha(O / f)) for f in records]
save(out, data)
for p in [O / 'latest-checkpoint.json', R / 'latest-checkpoint.json']:
    checkpoint = read(p)
    checkpoint.update(recordedAt=now, latestHandoff=rel(out))
    if p.parent == O:
        checkpoint.update(stage=data['stage'], next=next_step, scheduleGitDelivered=True,
            scheduleGitCommit=git['commit'], scheduleGitVerification=rel(P / 'schedule-git-verification-v1.json'),
            deletionQuestionAsked=True, deletionQuestionCount=1, deletionConfirmationPending=True,
            oldUploadDeleted=False, postPromotionGuard=data['postPromotionGuard'])
    save(p, checkpoint)
q_path = B / 'queue.json'
raw = q_path.read_bytes()
queue = read(q_path)
queue.update(updatedAt=now, next=next_step, latestHandoff=rel(out))
queue['currentOrientationReview'].update(stage=data['stage'], next=next_step, latestHandoff=rel(out),
    scheduleGitDelivered=True, scheduleGitCommit=git['commit'],
    scheduleGitVerification=rel(P / 'schedule-git-verification-v1.json'), deletionQuestionAsked=True,
    deletionQuestionCount=1, deletionConfirmationPending=True, oldUploadDeleted=False,
    postPromotionGuard=data['postPromotionGuard'])
assert q_path.read_bytes() == raw
save(q_path, queue)
print(json.dumps(dict(handoff=rel(out), actualVideoId='orq0TMVkFts', scheduleSavedReopened=True,
    scheduledAt=schedule['scheduledAt'], scheduleGit=git['commit'], protectedOthers=78,
    ownedWorkers=0, researchUnchanged=True, deletionQuestionCount=1, obsoleteDeleted=False)))
