"""Reconcile verified Studio UI receipts; never performs platform mutations."""
import hashlib
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BATCH = Path(__file__).resolve().parent
PROOF = ROOT / 'shared/publishing/schedule-replacement-20261011'
KST = timezone(timedelta(hours=9))
NOW = datetime.now(KST).isoformat()

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def write(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

queue = read(BATCH / 'queue.json')
rows = read(PROOF / 'studio-two-day-final-rows.json')['rows']
row_by_id = {r['videoId']: r for r in rows}
start = datetime(2026, 10, 17, 9, tzinfo=KST)
assignments = []
for item in queue['items']:
    if item['order'] <= 4:
        assert item['revision']['privateUploadComplete'] and item['revision']['renderComplete']
        assert len(item['revision']['videoIds']) == len(item['revision']['episodeSlugs']) == 2
        for slug, video_id in zip(item['revision']['episodeSlugs'], item['revision']['videoIds']):
            receipt = read(ROOT / f'projects/{slug}/publishing/youtube-upload.json')
            assert receipt['videoId'] == video_id and receipt['privateUploadComplete']
            assignments.append((item, slug, video_id, True))
    else:
        assignments.append((item, item['slug'], item['baseline']['videoId'], False))
assert len(assignments) == 15
records = []
for index, (item, slug, video_id, revised) in enumerate(assignments):
    expected = start + timedelta(days=2 * index)
    row = row_by_id[video_id]
    observed = re.search(r'(\d{4})\.\s*(\d+)\.\s*(\d+)\.', row['date'])
    assert observed and tuple(map(int, observed.groups())) == (expected.year, expected.month, expected.day)
    assert row['visibility'] == '예약됨'
    relative_proof = f'shared/publishing/schedule-replacement-20261011/{video_id}-reopened.dom.txt'
    proof_path = ROOT / relative_proof
    proof_text = proof_path.read_text(encoding='utf-8')
    display_date = f'{expected.year}. {expected.month}. {expected.day}.'
    assert f'button "{display_date}"' in proof_text
    assert 'textbox: 오전 9:00' in proof_text and 'GMT+0900' in proof_text
    assert f'https://youtu.be/{video_id}' in proof_text
    records.append(dict(slug=slug, videoId=video_id, title=row['title'], category='game-lecture',
                        categoryOrder=index + 4, date=expected.date().isoformat(), time='09:00',
                        timezone='Asia/Seoul', timezoneOffset='+09:00',
                        publishAt=expected.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z'),
                        verifiedAt=NOW, evidence=relative_proof,
                        evidenceSha256=hashlib.sha256(proof_path.read_bytes()).hexdigest(),
                        status='actual-saved-reopened'))
scheduled_dates = []
for row in rows:
    if row['visibility'] == '예약됨':
        parsed = re.search(r'(\d{4})\.\s*(\d+)\.\s*(\d+)\.', row['date'])
        scheduled_dates.append(tuple(map(int, parsed.groups())))
assert len(scheduled_dates) == len(set(scheduled_dates)), 'Duplicate lecture date in current Studio'

schedule_path = ROOT / 'shared/publishing/daily-alternating-schedule.json'
schedule = read(schedule_path)
affected = {r['videoId'] for r in records}
changed_history = [r for r in schedule['actualSchedules']
                   if r['videoId'] in affected and r['date'] != next(x['date'] for x in records if x['videoId'] == r['videoId'])]
for historical in changed_history:
    historical['supersededAt'] = NOW
    historical['reason'] = 'Eight-day shift to retain two-day lecture order after four chapters became eight completed episodes'
schedule.setdefault('replacementHistory', []).extend(changed_history)
schedule['actualSchedules'] = sorted([r for r in schedule['actualSchedules'] if r['videoId'] not in affected] + records,
                                     key=lambda r: r.get('publishAt', r['date']))
schedule['updatedAt'] = NOW
schedule['latestPart2RevisionScheduleEvidence'] = 'shared/publishing/schedule-replacement-20261011/studio-two-day-final-rows.json'
write(schedule_path, schedule)

for (item, slug, video_id, revised), record in zip(assignments, records):
    receipt_path = ROOT / f'projects/{slug}/publishing/youtube-upload.json'
    receipt = read(receipt_path)
    receipt['scheduleVerification'] = record
    receipt['currentVisibility'] = 'scheduled'
    receipt['scheduledAt'] = record['publishAt']
    receipt['scheduleReplacementVerifiedAt'] = NOW
    write(receipt_path, receipt)
    if not revised:
        baseline = item['baseline']
        baseline.setdefault('originalPublicationAnchor', {k: baseline[k] for k in ('date', 'time', 'timezone', 'scheduledAt')})
        baseline.update(date=record['date'], time='09:00', timezone='Asia/Seoul',
                        scheduledAt=record['publishAt'], actualStudioStatus='예약됨', currentScheduleEvidence=record['evidence'])
for item in queue['items'][:4]:
    item['revision']['scheduleReplacementComplete'] = True
    item['revision']['scheduledEpisodes'] = [r for r in records if r['videoId'] in item['revision']['videoIds']]
    item['status'] = 'reviewed-revised-episodes-scheduled; completed-production-preserved'
queue['updatedAt'] = NOW
assert queue['execution']['mode'] == 'paused-by-user'
queue['execution']['publishingHandoverComplete'] = True
write(BATCH / 'queue.json', queue)

publication = read(BATCH / 'replacement-publication-20261011.json')
publication['pendingDateDecision'] = None
publication['dateDecisionUserEvidence'] = '날짜 2일씩 계산해서 잘 올려줘~'
publication['scheduleReplacementComplete'] = True
publication['verifiedSchedules'] = records
publication['scheduleSpacingDays'] = 2
publication['subsequentSevenExistingLecturesShiftDays'] = 8
publication['completedAt'] = NOW
publication['productionPaused'] = True
write(BATCH / 'replacement-publication-20261011.json', publication)

old_plan_path = BATCH / 'expanded-publication-plan.json'
historical_plan_path = BATCH / 'expanded-publication-plan-before-two-day-finalization.json'
if not historical_plan_path.exists():
    historical_plan_path.write_bytes(old_plan_path.read_bytes())
write(old_plan_path, dict(updatedAt=NOW, userEvidence='날짜 2일씩 계산해서 잘 올려줘~',
                         policy='shared/publishing/daily-alternating-schedule.json',
                         actualSchedules=records, revisedEpisodeCount=8, retainedExistingLectureCount=7,
                         scheduleSpacingDays=2, time='09:00', timezone='Asia/Seoul',
                         productionPaused=True, futureIncompleteRevisionsScheduled=False,
                         previousPlanningHistory=historical_plan_path.name))
write(PROOF / 'two-day-final-audit.json', dict(verifiedAt=NOW, complete=True, reviewedReplacementEpisodes=8,
                                             retainedExistingLectures=7, exactTwoDaySpacing=True,
                                             dateTimeTimezoneReopenedCount=15, duplicateLectureDates=False,
                                             firstDate=records[0]['date'], lastDate=records[-1]['date'],
                                             unrelatedAndPublishedVideosPreserved=True, productionRemainsPaused=True))
print(f'PASS: {len(records)} actual Studio schedules, every 2 days at 09:00 Asia/Seoul; production paused.')
