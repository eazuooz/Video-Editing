"""Record directly observed English publication; keep unfinished upload gates false."""
from pathlib import Path
from datetime import datetime, timezone
import json

root = Path(__file__).resolve().parents[3]
rev = root / 'projects/game-math-polar-3d/revision-teaching-clarity-v1'
target = rev / 'publishing/youtube-upload-v3.json'
record = json.loads(target.read_text('utf-8-sig'))
assert record['actualVideoId'] == '2kNMDlrwdU8'
assert not record['uploaded'] and not record['scheduled']
now = datetime.now(timezone.utc).isoformat()
record['englishMetadata'].update({
    'status': 'published-and-full-title-description-reopened',
    'publicationToastObserved': '영어(미국) 제목 및 설명이 게시되었습니다.',
    'fullTitleDescriptionReopened': True,
})
record['englishSubtitles'] = {
    'cues': 206, 'timingIncludedSrtSelectedOnce': True,
    'importedWholeTextDirectlyRead': True,
    'publishedRowDirectlyObserved': True,
    'actualPublishedStatus': '수동 자막 / 수동 / 게시됨',
    'importEvidence': 'projects/game-math-polar-3d/revision-teaching-clarity-v1/publishing/en-imported-v3.ax.txt',
    'reopenedEvidence': 'projects/game-math-polar-3d/revision-teaching-clarity-v1/publishing/en-reopened-first-cues-v3.ax.txt',
    'reopenedVisibleCueTimesRead': 5,
    'allPlatformCueTimesReopened': False,
    'publishedDownloadAttempt': {
        'attempts': 1, 'format': '.srt', 'timeoutMs': 25000,
        'completedDownloadPath': None, 'result': 'download event timed out',
        'repeatAttempted': False,
    },
    'observedAt': now,
}
record['privacySelection'] = {
    'explicitPrivateRadioChecked': True,
    'saveClickedOnce': True,
    'authoritativeModal': '비공개 동영상을 아직 업로드하는 중입니다. 업로드가 완료될 때까지 이 브라우저 탭을 열린 상태로 유지하세요.',
    'finalCompletedPrivateSaveVerified': False,
}
record['updatedAt'] = now
target.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'englishMetadataPublished': True, 'manualEnPublished': True,
                  'uploadComplete': False, 'allSettings': False, 'baselineChanged': False}))
