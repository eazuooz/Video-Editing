from pathlib import Path
from datetime import datetime, timezone
import json

ROOT = Path(__file__).resolve().parents[3]
BATCH = 'production/batches/unpublished-teaching-clarity-revision'
REV = 'projects/motion-sickness-games/production/revision-teaching-clarity-v1'
PUB = REV + '/publishing'
read = lambda p: json.loads((ROOT / p).read_text('utf-8-sig'))
save = lambda p, data: (ROOT / p).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', 'utf-8')
proof = read(PUB + '/schedule-evidence-git-verification-v1.json')
assert proof['commit'] == '531328f8f631d111d0029d6a2c458621a5a7cad6' and proof['verifiedBlobCount'] == 23
assert all(proof[k] for k in ['pushed', 'exactLocalRemoteMatch', 'allFinalRemoteBlobsVerified', 'externalIndexUnchanged', 'sharedWorkingBytesPreserved'])
now = datetime.now(timezone.utc).isoformat()
handoff = read(PUB + '/final-handoff-v1.json')
assert not handoff['scheduleEvidenceGitDelivered']
handoff.update(scheduleEvidenceGitDelivered=True, scheduleEvidenceGitCommit=proof['commit'],
    scheduleEvidenceGitVerification=PUB + '/schedule-evidence-git-verification-v1.json', recordedAt=now,
    finalGitVerification=PUB + '/final-handoff-git-verification-v1.json')
save(PUB + '/final-handoff-v1.json', handoff)
checkpoint = read(REV + '/latest-checkpoint.json')
checkpoint.update(stage='reviewed-replacement-delivered-and-scheduled', scheduleEvidenceGitDelivered=True,
    scheduleEvidenceGitVerification=handoff['scheduleEvidenceGitVerification'], recordedAt=now,
    next='Audit orientation matrices. Do not repeat completed motion media/audio/QA/collection/upload/settings/Git/schedule.')
save(REV + '/latest-checkpoint.json', checkpoint)
queue = read(BATCH + '/queue.json')
item = next(e for e in queue['items'] if e['slug'] == 'motion-sickness-games')
item.update(status='reviewed-replacement-delivered-and-scheduled', scheduleEvidenceGitDelivered=True,
    scheduleEvidenceGitVerification=handoff['scheduleEvidenceGitVerification'], finalHandoff=PUB + '/final-handoff-v1.json')
queue['execution'].update(stage='orientation-content-and-gameplay-clarity-audit', currentSlug='game-math-orientation-matrices',
    next='Read current orientation source/claims/Studio; compare gameplay readability and retained explanations before dependent revisions.')
queue['updatedAt'] = now
save(BATCH + '/queue.json', queue)
readme = ROOT / BATCH / 'README.md'
content = readme.read_text('utf-8').replace('예약 증거 별도Git은 pending이며 다음은',
    '예약 증거도 `531328f8f631d111d0029d6a2c458621a5a7cad6` 일반push와23최종blob 일치로 전달했다. 완료한 멀미편 미디어·게시·예약을 반복하지 않는다. 다음은')
readme.write_text(content, 'utf-8')
print(json.dumps({'completedActualVideoId': 'mBDd9VzSTkA', 'actualDate': '2026-10-12', 'time': '09:00',
    'scheduleEvidenceGitDelivered': True, 'reviewedReplacements': 2, 'wholeBatchComplete': False}))
