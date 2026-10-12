"""Record the newly observed Studio state without assuming all checks passed."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
O = Path('projects/game-math-orientation-matrices/revision-teaching-clarity-v1')
P = O / 'publishing'
OUT = P / 'automatic-ad-followup-v2.json'

def digest(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()

def read(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8-sig'))

def write(path, value):
    (ROOT / path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

if (ROOT / OUT).exists():
    raise RuntimeError('This observation is already recorded; do not repeat it.')

proofs = [
    P / 'ui-proof-v1/automatic-ad-followup-v2.ax.txt',
    P / 'ui-proof-v1/copyright-followup-v2.ax.txt',
    P / 'ui-proof-v1/automatic-checks-followup-v2.ax.txt',
    P / 'ui-proof-v1/automatic-checks-notice-v2.ax.txt',
]
raw = [(ROOT / path).read_text(encoding='utf-8') for path in proofs]
assert 'orq0TMVkFts/monetization/ads' in raw[0] and '94 text 사용' in raw[0]
assert '동영상에서 소유권 주장이 발견되지 않았습니다' in raw[1]
assert 'orq0TMVkFts/edit' in raw[2] and '806 text 비공개' in raw[2]
assert '검토 중...' in raw[2]
assert '동영상에 대한 검토를 아직 실행 중입니다' in raw[3]

main = Path('projects/game-math-orientation-matrices/project.json')
index = Path('.git/index')
main_before, index_before = digest(main), digest(index)
now = datetime.now(timezone.utc).isoformat()
record = {
    'schemaVersion': 1,
    'observedAt': now,
    'actualVideoId': 'orq0TMVkFts',
    'tab': '116',
    'currentMonetizationPageReloaded': True,
    'actualMonetizationStatus': '사용',
    'monetizationSelected': True,
    'automaticMidrollSelected': True,
    'monetizationSaveDisabled': True,
    'copyrightNoClaimsObserved': True,
    'actualOverallChecksStatus': '검토 중...',
    'actualOverallChecksNotice': '동영상에 대한 검토를 아직 실행 중입니다. 결과가 곧 준비됩니다. 제한사항이 발견되는 즉시 여기에 표시됩니다.',
    'automaticAdCheckPassed': False,
    'allAutomaticChecksPassed': False,
    'fullSettingsComplete': False,
    'basis': 'Monetization status changed to 사용, but the current content-list notification explicitly says checks are still running. Do not infer final approval from the monetization setting or the no-claims page.',
    'currentVisibility': 'private',
    'baselineScheduleChanged': False,
    'scheduleReplacementVerified': False,
    'obsoleteDeleted': False,
    'newUploadSelections': 0,
    'newMediaWorkers': 0,
    'newGitDelivery': 0,
    'uiProofs': [{'path': path.as_posix(), 'sha256': digest(path)} for path in proofs],
    'rootMainSha256Preserved': main_before,
    'externalGitIndexBytesSha256Preserved': index_before,
    'previousObservation': (P / 'automatic-ad-followup-v1.json').as_posix(),
}
write(OUT, record)

next_action = ('Reuse116 actual orq0TMVkFts and read the current platform checks. '
    'Latest monetization page says 사용; the content list explicitly says 검토 중... and checks still running, so final automatic-check approval remains false. '
    'All available settings/manual244KOEN/localizedEN/card/member/CCoff1080p60 and production Git ee5fe58/574 blobs are complete. '
    'Once actual checks finish, read current baseline6-kP and Studio/ledger future09 slot, save/reopen replacement, then ask a new action-time confirmation only for that obsolete upload. '
    'Motion oldmBDd question remains once pending/noanswer; do not repeat it. No duplicate upload, production Git delivery, render, extract, playback, TTS, ASR or mix.')
checkpoint = read(O / 'latest-checkpoint.json')
checkpoint.update({
    'stage': 'orientation-current34-private-and-production-Git-complete;actual-platform-checks-pending',
    'next': next_action,
    'lastAutomaticAdObservation': OUT.as_posix(),
    'lastAutomaticAdObservationAt': now,
    'actualMonetizationStatus': '사용',
    'actualOverallChecksStatus': '검토 중...',
    'automaticAdCheckPassed': False,
    'fullSettingsComplete': False,
})
write(O / 'latest-checkpoint.json', checkpoint)

queue_path = Path('production/batches/cross-game-example-coverage-review/queue.json')
queue = read(queue_path)
queue['currentOrientationReview'].update({
    'stage': checkpoint['stage'],
    'next': next_action,
    'lastAutomaticAdObservation': OUT.as_posix(),
    'lastAutomaticAdObservationAt': now,
    'actualMonetizationStatus': '사용',
    'actualOverallChecksStatus': '검토 중...',
    'automaticAdCheckPassed': False,
    'fullSettingsComplete': False,
})
write(queue_path, queue)
assert digest(main) == main_before and digest(index) == index_before
print(json.dumps({'record': OUT.as_posix(), 'monetization': '사용', 'checks': '검토 중...', 'schedule': False, 'rootAndIndexPreserved': True}, ensure_ascii=False))
