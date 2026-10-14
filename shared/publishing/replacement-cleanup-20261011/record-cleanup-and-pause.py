import hashlib
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

root = Path(__file__).resolve().parents[3]
proof = Path(__file__).resolve().parent
now = datetime.now(ZoneInfo('Asia/Seoul')).isoformat()
def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))
def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

items = [
    ('game-math-polar-3d', 'ZLOewk8JHXA', '2kNMDlrwdU8', '2026-10-11', 'public'),
    ('motion-sickness-games', 'c18rkesgBSw', 'mBDd9VzSTkA', '2026-10-12', 'scheduled'),
    ('presenting-game-scores', 'oDYJlcv2Dqk', 'L5DA2xiV46M', '2026-10-28', 'scheduled'),
]
records = []
for slug, old, new, date, visibility in items:
    deletion = proof / f'{old}-deletion-current.dom.txt'
    assert '업로더가 삭제한 동영상입니다.' in deletion.read_text(encoding='utf-8')
    if visibility == 'scheduled':
        schedule = proof / f'{new}-schedule-current.dom.txt'
        text = schedule.read_text(encoding='utf-8')
        rendered_date = '. '.join(str(int(p)) for p in date.split('-')) + '.'
        assert rendered_date in text and '오전 9:00' in text and 'GMT+0900' in text
    else:
        schedule = proof / f'{new}-current-public.dom.txt'
        assert 'generic: 공개' in schedule.read_text(encoding='utf-8')
    records.append(dict(slug=slug, baselineId=old, replacementId=new,
                        baselineCurrentStatus='deleted-by-uploader-observed',
                        replacementCurrentVisibility=visibility,
                        matchedOriginalDate=date, time='09:00', timezone='Asia/Seoul',
                        deletionEvidence=deletion.relative_to(root).as_posix(),
                        replacementEvidence=schedule.relative_to(root).as_posix()))

result = dict(schemaVersion=1, observedAt=now, ui='CUA-only',
              productionPaused=True, automation24='PAUSED',
              resumeRequiresExplicitUserInstruction=True,
              automaticNextWeekResume=False, replacements=records,
              schedulingChangesInThisCleanup=0,
              originalSchedulesAlreadyMatched=True,
              newlyStartedProductionJobs=0,
              localMediaAndCheckpointsPreserved=True,
              researchProcessesAndControlsModified=False,
              originalMislabelledScreenshotPreserved=True,
              screenshotNote='ZLOewk8JHXA-deleted.png is a general Studio listing with an unrelated scheduling toast, not deletion proof. Use the new *-deletion-current files for actual deleted-by-uploader observations.',
              splitLectureScheduling=dict(status='awaiting-layout-preference',
                existingObservedSchedules={'HdJw7bgKlbM':'2026-10-17 09:00', 'SPq_41LyOG0':'2026-10-19 09:00'},
                privateUploadedIds=['_SzbJR4R6OI','n-k7zwaSum0','cOcuxWKHN5g','W5UkJkep7yo','Rzrt47-u4G0','wbZcFGzJMRg'],
                pendingQuestion='Keep first episodes on original dates and append second episodes, or use consecutive lecture slots and shift later lectures?',
                otherOwnerCheckpoint='production/batches/game-math-part2-teaching-revision/pause-20261011.json',
                notClaimedComplete=True))
result['proofs'] = [{
    'path': p.relative_to(root).as_posix(),
    'sha256': hashlib.sha256(p.read_bytes()).hexdigest(),
    'localOnly': True,
} for p in sorted(proof.iterdir()) if p.is_file() and p.suffix in {'.png','.txt'}]
write(proof/'result.json', result)

ledger_path = root/'shared/publishing/daily-alternating-schedule.json'
ledger = read(ledger_path)
for record in records:
    for entry in ledger['actualSchedules']:
        if entry.get('videoId') != record['replacementId']:
            continue
        for history in entry.get('replacementHistory', []):
            if history.get('baselineSchedule', {}).get('videoId') == record['baselineId']:
                history.update(baselineCurrentStatus='deleted-by-uploader-observed', deletionVerifiedAt=now,
                               deletionEvidence=record['deletionEvidence'])
if ledger.get('excludedBaseline', {}).get('videoId') == 'oDYJlcv2Dqk':
    ledger['excludedBaseline'].update(actualVisibility='deleted-by-uploader-observed',
        reason='Reviewed Balatro60:Tetris40 replacement is scheduled. Latest user requested removal of obsolete uploaded originals.',
        verifiedAt=now, evidence=records[2]['deletionEvidence'])
ledger['replacementCleanup'] = dict(verifiedAt=now, result='shared/publishing/replacement-cleanup-20261011/result.json',
                                   productionPause='production/USER_VIDEO_WORK_PAUSE.json')
write(ledger_path, ledger)
pause_path = root/'production/USER_VIDEO_WORK_PAUSE.json'
pause = read(pause_path)
pause.update(cleanupResult='shared/publishing/replacement-cleanup-20261011/result.json',
             cleanupVerifiedReplacements=3, splitLectureSchedulingPending=True)
write(pause_path, pause)
print(json.dumps({'verifiedDeletedOriginals':len(records), 'production':'paused', 'splitLectureScheduling':'pending-preference'}, ensure_ascii=False))
