"""A saved toast is not final language approval when a reopen contradicts it."""
from pathlib import Path
from datetime import datetime, timezone
import json

root = Path(__file__).resolve().parents[3]
path = root / 'projects/game-math-polar-3d/revision-teaching-clarity-v1/publishing/youtube-upload-v3.json'
record = json.loads(path.read_text('utf-8-sig'))
assert record['actualVideoId'] == '2kNMDlrwdU8'
assert not record['uploaded'] and not record['baselineScheduleChanged']
assert 'languageSaveReopenDuringTransfer' not in record
record['languageSaveReopenDuringTransfer'] = {
    'observedAt': datetime.now(timezone.utc).isoformat(),
    'titleDescriptionKoreanSelected': True,
    'saveClickedOnce': True,
    'actualToast': '모든 변경사항이 저장되었습니다.',
    'editPageReloadedAfterToast': True,
    'reopenedAudioLanguage': '선택',
    'reopenedTitleDescriptionLanguage': '선택',
    'finalLanguageVerified': False,
    'reason': 'The current reopened selection supersedes the earlier saved toast. Finish transfer, set the languages on the actual completed record and reopen them before approving publishing settings.',
    'evidence': 'projects/game-math-polar-3d/revision-teaching-clarity-v1/publishing/advanced-after-save-reopened-v5.ax.txt',
    'repeatBeforeTransferComplete': False,
}
record['fullSettingsVerified'] = False
record['updatedAt'] = datetime.now(timezone.utc).isoformat()
path.write_text(json.dumps(record, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps({'recordedActualReopen': True, 'finalLanguageVerified': False,
                  'duplicateUpload': False, 'baselineScheduleChanged': False}))
