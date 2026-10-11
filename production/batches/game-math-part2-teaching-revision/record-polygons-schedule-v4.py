"""Reconcile only actual saved/reopened polygon replacement schedules.

All eight current Studio modals must already exist. Preserve unrelated anchors,
published videos, original receipts and incomplete human/IP approval.
"""
import copy
import hashlib
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BATCH = ROOT / 'production/batches/game-math-part2-teaching-revision'
REVIEW = BATCH / 'cross-game-review-20261011'
EVIDENCE = ROOT / 'shared/publishing/polygons-four-game-schedule-20261011'
NOW = datetime.now(timezone(timedelta(hours=9))).isoformat()
DATES = [('game-math-polygon-centers-v2','YgcN8vs0gNo','2026-11-02'),
         ('game-math-polygon-partition-v2','pfagaQK-xfI','2026-11-04'),
         ('game-math-rendering-light','-19ngvEqhao','2026-11-06'),
         ('game-math-camera-frustum','CbX6KQ-_zsc','2026-11-08'),
         ('game-math-camera-projection','c96qTnlHBVU','2026-11-10'),
         ('game-math-projection-depth','PuXZUArWFko','2026-11-12'),
         ('game-math-mesh-uv','xnIA0EAJtiA','2026-11-14'),
         ('game-math-normal-transform-uv','nalAZHtEtw0','2026-11-16')]

def read(path):
    return json.loads(path.read_text(encoding='utf-8'))

def write(path,data):
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

verified = []
for slug, video_id, date in DATES:
    path = EVIDENCE / (video_id+'-reopened.txt')
    source = path.read_text(encoding='utf-8')
    year, month, day = map(int,date.split('-'))
    assert f'{year}. {month}. {day}.' in source
    assert 'textbox: 오전 9:00' in source and 'GMT+0900' in source
    assert '비공개에서 공개로" [checked]' in source
    assert 'checkbox "Premieres 동영상으로 설정" [checked]' not in source
    assert '/video/'+video_id+'/' in source or 'https://youtu.be/'+video_id in source
    verified.append(dict(slug=slug,videoId=video_id,date=date,time='09:00',
        timezone='Asia/Seoul',timezoneOffset='+09:00',publishAt=date+'T00:00:00Z',
        verifiedAt=NOW,evidence=path.relative_to(ROOT).as_posix(),
        evidenceSha256=sha(path),status='actual-saved-reopened'))
assert all((datetime.fromisoformat(b['date'])-datetime.fromisoformat(a['date'])).days==2
           for a,b in zip(verified,verified[1:]))
old_private = (EVIDENCE/'L7SXFwn4i2k-private-reopened.txt').read_text(encoding='utf-8')
assert 'radio "비공개" [checked]' in old_private
assert '비공개에서 공개로" [checked]' not in old_private

git_records = []
for slug, _, _ in DATES[:2]:
    record = read(ROOT/'shared/output/polygons-git-delivery-v4'/f'{slug}.json')
    assert record['committed'] and record['pushed'] and record['commit'] == record['remoteSha']
    assert record['realIndexBeforeSha256'] == record['realIndexAfterSha256']
    git_records.append({k:record[k] for k in ['slug','commit','remoteSha','pushed']})

ledger_path = ROOT/'shared/publishing/daily-alternating-schedule.json'
ledger = read(ledger_path)
original_entries = copy.deepcopy(ledger['actualSchedules'])
old = next(e for e in original_entries if e['videoId']=='L7SXFwn4i2k')
entries = []
by_id = {v['videoId']:v for v in verified}
for entry in original_entries:
    if entry['videoId']=='L7SXFwn4i2k':
        for offset,new in enumerate(verified[:2]):
            receipt = read(ROOT/'projects'/new['slug']/'publishing/youtube-upload.json')
            assert receipt['uploadComplete'] and receipt['fullPublishingSettingsComplete']
            replacement = dict(new,title=receipt['metadata']['title'],category='game-lecture',
                               categoryOrder=old['categoryOrder']+offset)
            replacement['replacementHistory'] = [dict(baselineSchedule=old,
                baselineCurrentStatus='private; schedule removed; permanent deletion confirmation pending',
                replacementVideoIds=[v['videoId'] for v in verified[:2]],
                verifiedAt=NOW,baselinePrivateEvidence='shared/publishing/polygons-four-game-schedule-20261011/L7SXFwn4i2k-private-reopened.txt')]
            entries.append(replacement)
    elif entry['videoId'] in by_id:
        replacement = copy.deepcopy(entry)
        replacement.setdefault('scheduleChangeHistory',[]).append(dict(previousSchedule=copy.deepcopy(entry),
            reason='One original polygon lecture replaced by two complete four-game episodes; keep subsequent lecture order and two-day spacing.'))
        replacement.update(by_id[entry['videoId']])
        replacement['categoryOrder'] = entry['categoryOrder']+1
        entries.append(replacement)
    else:
        entries.append(entry)
assert len({(e['date'],e.get('time','09:00')) for e in entries}) == len(entries), 'Actual ledger double-booking'
ledger['actualSchedules'] = entries
ledger['updatedAt'] = NOW
ledger.setdefault('replacementCadenceHistory',[]).append(dict(verifiedAt=NOW,
    userEvidence='날짜 2일씩 계산해서 잘 올려줘; 첫 편은 기존 날짜, 둘째 편은 다음 강의 날짜',
    affectedActualVideoIds=[v['videoId'] for v in verified],time='09:00',timezone='Asia/Seoul',
    publishedAndUnrelatedEntriesPreserved=True))
write(ledger_path,ledger)

for row in verified:
    path = ROOT/'projects'/row['slug']/'publishing/youtube-upload.json'
    receipt = read(path)
    if receipt.get('scheduleVerification'):
        receipt.setdefault('scheduleVerificationHistory',[]).append(copy.deepcopy(receipt['scheduleVerification']))
    receipt.update(scheduled=True,currentVisibility='scheduled',scheduledAt=row['publishAt'],
        scheduleReplacementVerifiedAt=NOW,scheduleVerification=dict(row),
        status='actual-reviewed-upload-scheduled; human-listening-and-game-IP-review-pending')
    write(path,receipt)
    if row['slug'] in [s for s,_,_ in DATES[:2]]:
        manifest_path = ROOT/'projects'/row['slug']/'project.json'
        manifest = read(manifest_path)
        manifest['status'] = 'reviewed-four-game-revision-scheduled; human-and-IP-review-pending'
        manifest['publishing'].update(scheduled=True,videoId=row['videoId'],scheduleVerification=dict(row))
        manifest['finalRender']['openItems'] = ['Human whole listening and game-IP review pending.',
            'Obsolete original upload privately retained; permanent deletion confirmation pending.']
        write(manifest_path,manifest)

baseline_path = ROOT/'projects/game-math-polygons-triangulation/publishing/youtube-upload.json'
baseline = read(baseline_path)
baseline.setdefault('historicalSchedules',[]).append(copy.deepcopy(old))
baseline.update(scheduled=False,currentVisibility='private',
    status='privately-retained-after-reviewed-two-episode-replacement; deletion-confirmation-pending',
    replacedByVideoIds=[v['videoId'] for v in verified[:2]],
    privateAfterReplacementEvidence='shared/publishing/polygons-four-game-schedule-20261011/L7SXFwn4i2k-private-reopened.txt')
write(baseline_path,baseline)
queue_path = BATCH/'queue.json'
queue = read(queue_path)
item = next(i for i in queue['items'] if i['slug']=='game-math-polygons-triangulation')
item['status'] = 'four-game-two-episode-revisions-reviewed-scheduled-and-Git-delivered; baseline-deletion-confirmation-pending'
item['revision'].update(scheduleReplacementComplete=True,gitDelivered=True,
                       gitDelivery=git_records,scheduleVerification=verified[:2])
item['baseline']['actualStudioStatus'] = '비공개; 예약 해제; 영구 삭제 확인 대기'
queue['execution']['stage'] = 'polygons-v4-delivered-and-scheduled; continue closest remaining four-game gaps'
write(queue_path,queue)
progress_path = REVIEW/'polygons-v4-current-progress.json'
progress = read(progress_path)
progress.update(recordedAt=NOW,scheduleReplacementComplete=True,gitDelivered=True,
                gitDelivery=git_records,baselineStatus='private; deletion confirmation pending')
for upload in progress['actualUploads']:
    row = next(v for v in verified if v['videoId']==upload['videoId'])
    upload.update(privacy='private-until-scheduled-publication',scheduled=True,
                  scheduledAt=row['publishAt'],scheduleEvidence=row['evidence'])
write(progress_path,progress)
write(EVIDENCE/'actual-verified-schedule.json',dict(verifiedAt=NOW,entries=verified,
    allTwoDaysApart=True,all09KST=True,actualNoDoubleBooking=True,
    gameDesignAndPublishedEntriesPreserved=True,gitBeforeReplacementSchedule=git_records,
    baselineVideoId='L7SXFwn4i2k',baselineCurrentStatus='private; deletion confirmation pending',
    humanWholeListening='pending',gameIPHumanApproval='pending',fullUserTaskComplete=False))
print(json.dumps(verified,ensure_ascii=False,indent=2))
