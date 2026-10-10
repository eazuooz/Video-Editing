import json
from datetime import datetime, timezone
from pathlib import Path

root = Path(__file__).resolve().parents[3]
revision = root / 'projects/game-math-polar-3d/revision-teaching-clarity-v1'
receipt_path = revision / 'publishing/youtube-upload-v3.json'
receipt = json.loads(receipt_path.read_text(encoding='utf-8-sig'))
assert receipt['actualVideoId'] == '2kNMDlrwdU8'
assert receipt['videoSelectedOnce'] is True
assert receipt['video']['sha256'] == '8b1aacd54034faca55809702ab332e08b80403d32a113b2834e7fa7af867d372'
now = datetime.now(timezone.utc).isoformat()
receipt['englishMetadata']['status'] = 'prepared-not-yet-published-on-replacement'
receipt['koSubtitles'] = {
    'cues': 206, 'importedWholeTextDirectlyRead': True,
    'completionSaveObserved': True, 'allPlatformCueTimesReopened': False,
    'evidence': 'projects/game-math-polar-3d/revision-teaching-clarity-v1/publishing/ko-imported-v3.ax.txt',
}
receipt['coachingCard'] = {
    'url': 'https://www.yamyamcoding.com/1430b1ff-a61e-8040-a542-d672d5d25328',
    'time': '00:00:00', 'callToAction': '프로그래밍 과외 상담',
    'teaser': '게임 프로그래밍 1:1 코칭',
    'websiteImage': 'existing YamYamCoding three-cat circular logo, directly inspected',
    'saveObserved': True, 'reopenedVerified': False,
}
receipt['membershipEndScreen'] = {
    'importedFromBaseline': 'ZLOewk8JHXA', 'saveObserved': True,
    'observedElements': ['own-channel-subscribe', 'Game Math PART2 playlist', 'canonical-coaching-url'],
    'provisionalUiStart': '14:51:27', 'provisionalUiEnd': '15:01:27',
    'targetStartSeconds': 891.9166666666666, 'targetEndSeconds': 901.9166666666666,
    'target60fpsStart': '14:51:55', 'target60fpsEnd': '15:01:55',
    'processed60fpsTimingVerified': False, 'allElementsReopened': False,
}
receipt['uploadProgressObserved'] = {'percent': 18, 'remainingMinutesUi': 57, 'observedAt': now}
receipt['updatedAt'] = now
receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
queue_path = root / 'production/batches/unpublished-teaching-clarity-revision/queue.json'
queue = json.loads(queue_path.read_text(encoding='utf-8-sig'))
queue['execution']['stage'] = 'polar-single-private-upload-transmitting-elements-saved-processing-pending'
queue['execution']['actualReplacementVideoId'] = receipt['actualVideoId']
queue['execution']['next'] = 'Finish this single upload; verify processed SD/HD, EN206/localized metadata, KO timing, card and exact60fps member elements, CC-off uploaded pixels and private settings; selectively deliver Git before replacing baseline schedule.'
item = next(x for x in queue['items'] if x['slug'] == 'game-math-polar-3d')
item['review']['onFootageAnnotationMotionPassed'] = True
item['review']['allFinalPixelsPassed'] = True
item['review']['outputsCollected'] = True
item['currentReplacementVideoId'] = receipt['actualVideoId']
item['finalPixelEvidence'] = 'projects/game-math-polar-3d/revision-teaching-clarity-v1/final-pixel-direct-review-v2.json'
item['collectionEvidence'] = 'projects/game-math-polar-3d/revision-teaching-clarity-v1/collection-private-preflight-v3.json'
item['reviewScopeNote'] = 'All386 listed boards/2262 samples and1x whole-flow endpoint reviewed; current44 complete AAC/PCM contexts and technical pair passed; four files collected once and hashes identical. Single new2kNMDlrwdU8 upload transmitting. Final processed publishing/settings/Git/schedule replacement remain pending. Human full listening/pronunciation/public rights remain false.'
queue['updatedAt'] = now
queue_path.write_text(json.dumps(queue, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'actualVideoId': receipt['actualVideoId'], 'finalPixels': True, 'collected': True, 'privateSettings': False, 'git': False, 'scheduled': False}))
