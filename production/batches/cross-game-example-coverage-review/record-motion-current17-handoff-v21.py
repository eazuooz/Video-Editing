"""Seal final local delivery and the one in-progress private upload.

No media worker, platform action, research control or Git-index operation.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, psutil

ROOT = Path(__file__).resolve().parents[3]
B = Path(__file__).resolve().parent
R = ROOT / 'projects/motion-sickness-games/production/revision-cross-game-four-v1'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def save(path, value):
    temporary = path.with_name(path.name + '.v21.writing')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf-8')
    os.replace(temporary, path)

pair = read(R / 'current17-final-pair-execution-v2.session.json')
pixels = read(R / 'current17-final-pixel-execution-v1.session.json')
for job in [pair, pixels]:
    assert job['actualOuterExitCode'] == 0 and not job['workerCurrentlyAlive']
    if psutil.pid_exists(job['pid']):
        assert abs(psutil.Process(job['pid']).create_time() - job['createTime']) > .01
promotion = read(R / 'current17-main-promotion-v1.json')
assert promotion['intentionalProtectedMainTransition'] and promotion['other70ProtectedInputsUnchanged']
for row in promotion['otherProtectedInputs']:
    assert sha(ROOT / row['path']) == row['sha256'], row['path']
upload_path = R / 'publishing/youtube-upload-v1.json'
upload = read(upload_path)
assert upload['actualVideoId'] == 'lXjDBqONLWs' and upload['uploadSelections'] == 1
now = datetime.now(timezone.utc).isoformat()
upload.update(lastObservedAt=now, observedProgressPercent=92,
    observedPlatformText='92% 업로드 중 ... 2분 남음',
    privateRadioSelected=True, manualKoSrtSaved=True, cardSaved=True, endScreenSaved=True,
    card=dict(url='https://www.yamyamcoding.com/1430b1ff-a61e-8040-a542-d672d5d25328',
        startSeconds=0, title='프로그래밍 과외', teaser='프로그래밍 과외',
        callToAction='프로그래밍 과외', originalChannelImageSelected=True,
        saveObservedViaModifyButton=True, reopenedVerified=False),
    endScreen=dict(startSeconds=843.1, endSeconds=853.1,
        uiStart='14:03:03', uiEnd='14:13:03', uiFps=30,
        elements=['subscribe-own-channel', 'Planning & Game Design & Tech', 'coaching-external-link'],
        membersTitleAndCoachingCopyClearAt847=True, saveObservedViaModifyButton=True,
        reopenedVerified=False, privateViewPageElementsUnavailable=True),
    fullSettingsVerified=False)
save(upload_path, upload)
refs = ['current17-final-encoded-pixel-direct-review-v1.json',
    'current17-final-normal-playback-direct-review-v1.json',
    'current17-main-promotion-v1.json', 'current17-four-output-collection-verification-v1.json',
    'publishing/youtube-upload-v1.json', 'publishing/current17-upload-end-screen-clearance-v1.ax.txt',
    'publishing/current17-upload-end-screen-clearance-v1.png',
    'publishing/current17-upload-card-zero-v1.ax.txt', 'publishing/current17-upload-card-zero-v1.png']
next_step = ('Reuse CUA100 single actual lXjDBqONLWs upload; never select/upload again. '
    'Private radio is selected; transfer/SDHD/checks remain pending. Finish saved private upload, '
    'EN timed SRT/localized metadata, card/end-screen reopen and CC-off1080p60 pixels. '
    'Then explicit-path isolated-index Git delivery/current Studio09slot save-reopen; '
    'only then corresponding obsolete deletion with CUA action-time confirmation. '
    'Root main intentionally promoted: use promotion70other protection, never old71 root guard. '
    'Do not rerun completed TTS/ASR/mix/pair/pixels/collection. Pause after normal-transform-UV; no Sakurai6.')
handoff = dict(schemaVersion=1, recordedAt=now, previousHandoff='resource-and-annotation-handoff-v20.json',
    activeOwnedWorkers=0, closedPair=pair, closedPixelExtraction=pixels,
    sampledFinalPixelCount=1425, sampledFinalBoardCount=238, all220CueSamplesReviewed=True,
    allContinuousFramesReviewed=False, currentMixedContentReviewed=True, humanListeningApproved=False,
    publicRightsApproved=False, mainIntentionallyPromoted=True, other70ProtectedInputsUnchanged=True,
    outputCollected=True, collectorInitialExit=1, collectorInitialFailure='UNKNOWN write projects/rebuild-index.json',
    collectorTailRecoveryExit=0, allFourSourceDeliveryShaMatched=True,
    sharedRebuildIndexAlreadyCorrectAndPreserved=True,
    actualReplacementVideoId=upload['actualVideoId'], uploadSelections=1, uploadPercentObserved=92,
    uploadComplete=False, privateRadioSelected=True, fullSettingsVerified=False, gitDelivered=False,
    scheduleReplacementVerified=False, obsoleteDeleted=False, baselineVideoId='mBDd9VzSTkA',
    baselineActualPrivacy='private', historicalOct12ScheduleIsNotCurrentFutureProof=True,
    originalResearch=dict(pid=75876, currentAlive=False, status='complete_pending_visual_review',
        completed=1088, total=1088, restarted=False),
    evidence=[dict(path=x, sha256=sha(R/x)) for x in refs], next=next_step)
out = R / 'resource-and-annotation-handoff-v21.json'
assert not out.exists()
save(out, handoff)
cp_path = R / 'latest-checkpoint.json'
cp = read(cp_path)
cp.update(recordedAt=now, latestResourceAndAnnotationHandoff=out.name, currentHandoff=out.name,
    activeOwnedWorkers=0, next=next_step)
save(cp_path, cp)
queue_path = B / 'queue.json'
queue = read(queue_path)
queue.update(updatedAt=now, next=next_step)
queue['currentMotionReview'].update(currentHandoff=out.relative_to(ROOT).as_posix(),
    currentOwnedWorkers=0, actualReplacementVideoId=upload['actualVideoId'],
    privateSettingsVerified=False, outputCollected=True)
save(queue_path, queue)
print(json.dumps(dict(handoff=out.name, actualVideoId=upload['actualVideoId'],
    activeOwnedWorkers=0, protectedOther=70, transferPercentObserved=92, fullSettings=False)))
