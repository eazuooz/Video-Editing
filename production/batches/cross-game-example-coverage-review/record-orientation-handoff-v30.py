"""Continue actual private orq0 upload after verified Git, without repeating media work."""
import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
import psutil

ROOT = Path(__file__).resolve().parents[3]
B = Path(__file__).resolve().parent
O = ROOT / 'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
R = ROOT / 'projects/motion-sickness-games/production/revision-cross-game-four-v1'

def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))

def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1048576), b''):
            h.update(chunk)
    return h.hexdigest()

def rel(p):
    return p.relative_to(ROOT).as_posix()

def save(p, data):
    pending = p.with_name(p.name + '.writing')
    pending.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    os.replace(pending, p)

out = R / 'resource-and-annotation-handoff-v30.json'
assert not out.exists()
promotion = read(O / 'current34-main-promotion-v1.json')
transition = read(O / 'current34-main-private-update-v1.json')
assert sha(ROOT / transition['currentMain']['path']) == transition['currentMain']['sha256']
assert sha(ROOT / promotion['baselineMain']['path']) == promotion['baselineMain']['sha256']
for entry in promotion['otherProtectedInputs'] + promotion['repairCandidates']:
    assert sha(ROOT / entry['path']) == entry['sha256'], entry['path']
git_proof = read(O / 'publishing/production-git-verification-v1.json')
assert git_proof['pushed'] and git_proof['allFinalRemoteBlobsVerified']
assert git_proof['exactLocalRemoteMatch'] and git_proof['verifiedBlobCount'] == 574
assert git_proof['commit'] == 'ee5fe58fc23f9750d616e80a11cda29d436396e3'
settings = read(O / 'publishing/private-settings-direct-review-v1.json')
upload = read(O / 'publishing/youtube-upload-v1.json')
assert upload['actualVideoId'] == 'orq0TMVkFts' and upload['privateSaveReopenVerified']
assert settings['fullAvailableSettingsVerified'] and not upload['scheduled']
workers = []
for process in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
    try:
        command = ' '.join(process.info['cmdline'] or [])
        if ((process.info['name'] or '').lower() in ['python.exe', 'node.exe', 'ffmpeg.exe']
                and process.pid != os.getpid() and 'cross-game-example-coverage-review' in command
                and any(token in command for token in ['render-orientation', 'review-orientation',
                    'extract-orientation', 'build-orientation', 'assemble-orientation', 'collect-orientation',
                    'render-motion', 'review-motion', 'extract-motion', 'deliver-orientation'])):
            workers.append({'pid': process.pid, 'createTime': process.info['create_time'], 'command': command})
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass
assert not workers, workers
research = Path('C:/Users/eazuo/renderformer/tmp/placement_focus_20261008/status.json')
assert sha(research) == 'bbeac85c5f493baec614eeb5fae13f15d8b9b913f58631dce2d2ee211f07b0b8'
helper = None
try:
    process = psutil.Process(27140)
    if abs(process.create_time() - 1791509666.837781) < .01:
        helper = {'pid': process.pid, 'createTime': process.create_time(), 'command': process.cmdline(),
                  'cwd': process.cwd(), 'alive': True, 'newServerStarted': False}
except (psutil.NoSuchProcess, psutil.AccessDenied):
    pass
records = ['current34-final-pair-execution-v5.json', 'current34-pair-pixel-execution-v4.json',
    'current34-final-technical-and-pixel-direct-review-v5.json', 'current34-final-normal-direct-review-v5.json',
    'current34-main-promotion-v1.json', 'current34-main-private-update-v1.json',
    'current34-four-output-collection-verification-v1.json', 'publishing/youtube-upload-v1.json',
    'publishing/private-settings-direct-review-v1.json', 'publishing/production-git-verification-v1.json',
    'publishing/git-precommit-failure-v1.json', 'publishing/git-preflight-rebuild-v2.json']
now = datetime.now(timezone.utc).isoformat()
next_step = ('Reuse116 actual orq0TMVkFts private upload and actual current ad-review status; last UI 검사 중. '
    'All available settings/manual244KOEN/localizedEN/card/member/CCoff1080p60 are verified. '
    'Production Git ee5fe58/574 remote blobs and external index preservation are complete. '
    'Once actual automatic checks finish, verify current baseline6-kP and Studio/ledger future09 slot, '
    'save/reopen replacement and record only that actual reservation. Then corresponding obsolete deletion '
    'requires a new action-time confirmation. Motion oldmBDd question already once pending/noanswer; do not repeat it. '
    'No duplicate upload, Git delivery, render, extract, local playback, TTS, ASR or mix.')
data = {
    'schemaVersion': 1, 'recordedAt': now,
    'stage': 'orientation-current34-private-and-production-Git-complete;actual-ad-review-pending',
    'newActualVideoId': 'orq0TMVkFts', 'actualPrivateSavedReopened': True, 'currentStudioTab': '116',
    'currentUploadedReviewTab': '117', 'newCaptionedFileSelections': 1,
    'fullAvailableSettingsVerified': True, 'fullSettingsComplete': False,
    'automaticAdCheckPassed': False, 'lastActualAdStatus': '검사 중',
    'actualSdHdComplete': True, 'actualCopyrightNoIssuesObserved': True,
    'manualKoEn244Saved': True, 'localizedEnglishMetadataSavedReopened': True,
    'coachingCard00SavedReopened': True, 'memberThreeElementsSavedReopened': True,
    'memberEndScreenUiFps': 60, 'memberUiStart': '18:08:38', 'memberUiEnd': '18:18:36',
    'uploadedCcOff1080p60SelectedFramesReviewed': True,
    'actualProductionGitSession': 39640, 'gitCompletionChunk': '55c644', 'actualGitOuterExitCode': 0,
    'productionGitCommit': git_proof['commit'], 'productionGitRemote': git_proof['remoteCommit'],
    'all574FinalRemoteBlobsVerified': True, 'externalIndexBytesAndEntriesPreserved': True,
    'sharedWorktreeAndForeignRebuildsPreserved': True,
    'gitPrecommitWhitespaceFailurePreserved': True, 'whitespaceSourcePythonAstUnchanged': True,
    'mainIntentionallyPromoted': True, 'mainCurrentSha256': transition['currentMain']['sha256'],
    'postPromotionGuard': rel(O / 'current34-main-private-update-v1.json'),
    'doNotRunOld79IncludingMainGuard': True, 'other78ProtectedInputsUnchanged': True,
    'originalMainExactBackupUnchanged': True, 'repairCandidatesUnchanged': True,
    'finalV5PairAndPixelsClosed': True, 'totalSelectedFinalPixels': 3170,
    'newDirectSamples': 118, 'inheritedExactPriorPixels': 3052,
    'all244CueSelectedPixelsReviewed': True, 'all37CutsReviewed': True,
    'finalTechnicalAndRatioApproved': True, 'normal1xMutedStartEndAlreadyVerified': True,
    'fourOutputsVerified': True, 'activeOwnedWorkers': 0, 'helper9250': helper,
    'baselineVideoId': '6-kP65hrZcI', 'baselineScheduleChanged': False,
    'lastBaselineActualReservation': '2026-10-13 09:00 GMT+0900; re-read current Studio before changing',
    'scheduleReplacementVerified': False, 'obsoleteDeleted': False,
    'motionOldDelete': {'videoId': 'mBDd9VzSTkA', 'questionAskedOnce': True,
                        'answerReceived': False, 'deletePerformed': False},
    'researchUnchanged': True, 'researchWorkerAlive': False, 'researchCompleted': 1088,
    'detailedSubjectRulesRecordedAndDelivered': True, 'newGitImages': 0, 'newGitMedia': 0,
    'newRenderRequired': False, 'newTts': 0, 'newAsr': 0, 'newMix': 0,
    'humanListeningApproved': False, 'humanPronunciationApproved': False, 'publicRightsApproved': False,
    'optionalCcPropagationPending': True, 'automaticDubbingHumanReviewPending': True,
    'boundRecords': [{'path': rel(O / f), 'sha256': sha(O / f)} for f in records],
    'next': next_step, 'continuationBoundary': 'Remain ACTIVE through normal-transform-UV final3D '
        'delivery and actual schedule replacement, then pause only task-owned continuation. '
        'No new lectures or Sakurai6. Quiet on unchanged healthy waits.'}
save(out, data)
for p in [O / 'latest-checkpoint.json', R / 'latest-checkpoint.json']:
    checkpoint = read(p)
    checkpoint.update(recordedAt=now, latestHandoff=rel(out))
    if p.parent == O:
        checkpoint.update(next=next_step, stage=data['stage'], postPromotionGuard=data['postPromotionGuard'])
    save(p, checkpoint)
q_path = B / 'queue.json'
raw = q_path.read_bytes()
queue = read(q_path)
queue['currentOrientationReview'].update(latestHandoff=rel(out), next=next_step,
    stage=data['stage'], postPromotionGuard=data['postPromotionGuard'])
queue['updatedAt'] = now
assert q_path.read_bytes() == raw
save(q_path, queue)
print(json.dumps({'handoff': rel(out), 'actualVideo': 'orq0TMVkFts', 'remoteCommit': git_proof['remoteCommit'],
    'ownedWorkers': 0, 'protectedOthers': 78, 'researchUnchanged': True, 'adReviewPending': True,
    'scheduleReplacement': False}))
