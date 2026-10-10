import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
REV = 'projects/game-math-polar-3d/revision-teaching-clarity-v1'
PUB = REV + '/publishing'
BATCH = 'production/batches/unpublished-teaching-clarity-revision'

def read(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8-sig'))

def save(path, data):
    (ROOT / path).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def digest(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()

now = datetime.now(timezone.utc).isoformat()
before = read(PUB + '/schedule-before-actual-rows-v6.json')['rows']
after = read(PUB + '/schedule-after-actual-rows-v6.json')['rows']

def record(row):
    links = [link if isinstance(link, str) else link['href'] for link in row['links']]
    identity = next(re.search(r'/video/([^/]+)/edit', link).group(1) for link in links if re.search(r'/video/([^/]+)/edit', link))
    day = re.search(r'2026\.\s*(\d+)\.\s*(\d+)\.', row['text'])
    return identity, {'title': row['text'].splitlines()[1], 'date': f'2026-{int(day[1]):02d}-{int(day[2]):02d}'}

bmap, amap = dict(map(record, before)), dict(map(record, after))
assert len(bmap) == len(amap) == 24
assert 'ZLOewk8JHXA' in bmap and 'ZLOewk8JHXA' not in amap
assert '2kNMDlrwdU8' in amap and '2kNMDlrwdU8' not in bmap
assert bmap['ZLOewk8JHXA'] == amap['2kNMDlrwdU8']
assert amap['2kNMDlrwdU8']['date'] == '2026-10-11'
unchanged = sorted(set(bmap) - {'ZLOewk8JHXA'})
assert len(unchanged) == 23 and all(bmap[key] == amap[key] for key in unchanged)
ax = (ROOT / PUB / 'schedule-reopened-v6.ax.txt').read_text(encoding='utf-8')
assert '2026. 10. 11.' in ax and '오전 9:00' in ax and 'GMT+0900' in ax
assert '2kNMDlrwdU8/edit' in ax and 'button (disabled) 완료' in ax
baseline = (ROOT / PUB / 'baseline-private-reloaded-v6.ax.txt').read_text(encoding='utf-8')
assert 'ZLOewk8JHXA/edit' in baseline and re.search(r'공개 상태[\s\S]{0,180}text 비공개', baseline)
prod = read(PUB + '/private-delivery-git-verification-v3.json')
assert prod['pushed'] and prod['exactLocalRemoteMatch'] and prod['allRemoteBlobsVerified'] and prod['externalIndexUnchanged']
image = {'path': PUB + '/schedule-reopened-proof-v6.png', 'purpose': 'minimal-publishing-proof',
         'reason': 'One directly reviewed saved-and-reopened Studio modal proves replacement 2kNMDlrwdU8 keeps October11 09:00 GMT+0900 with Premieres off, after baseline ZLOewk8JHXA was preserved privately.',
         'sha256': digest(PUB + '/schedule-reopened-proof-v6.png'), 'reviewedAt': now, 'project': 'game-math-polar-3d'}
proof = {'schemaVersion': 6, 'slug': 'game-math-polar-3d', 'actualVideoId': '2kNMDlrwdU8',
         'baselineVideoId': 'ZLOewk8JHXA', 'status': 'actual-saved-reopened-scheduled-replacement',
         'date': '2026-10-11', 'time': '09:00', 'timezone': 'Asia/Seoul', 'timezoneOffset': '+09:00',
         'publishAt': '2026-10-11T00:00:00Z', 'premieres': False, 'baselinePreservedPrivate': True,
         'baselineDeleted': False, 'scheduleSavedAndReopened': True, 'futureListReloaded': True,
         'futureScheduleCount': 24, 'other23DatesAndTitlesUnchanged': True, 'unchangedVideoIds': unchanged,
         'beforeRows': PUB + '/schedule-before-actual-rows-v6.json', 'afterRows': PUB + '/schedule-after-actual-rows-v6.json',
         'reopenedAx': PUB + '/schedule-reopened-v6.ax.txt', 'baselinePrivateAx': PUB + '/baseline-private-reloaded-v6.ax.txt',
         'reviewedEssentialImages': [image], 'productionGitCommit': prod['commit'],
         'humanListeningApproved': False, 'pronunciationApproved': False, 'publicRightsApproved': False, 'verifiedAt': now}
save(PUB + '/schedule-direct-review-v6.json', proof)
receipt = read(PUB + '/youtube-upload-v3.json')
receipt.update(status='reviewed-scheduled-replacement-production-git-delivered', gitDelivered=True, scheduled=True,
               baselineScheduleChanged=True, updatedAt=now,
               gitEvidence=PUB + '/private-delivery-git-verification-v3.json',
               scheduleEvidence=PUB + '/schedule-direct-review-v6.json', actualSchedule={k: proof[k] for k in ['date','time','timezone','timezoneOffset','publishAt']})
save(PUB + '/youtube-upload-v3.json', receipt)
ledger = read('shared/publishing/daily-alternating-schedule.json')
entry = next(e for e in ledger['actualSchedules'] if e['slug'] == 'game-math-polar-3d')
assert entry['videoId'] == 'ZLOewk8JHXA' and entry['date'] == proof['date'] and entry['time'] == proof['time']
historical = dict(entry)
entry.update(videoId='2kNMDlrwdU8', verifiedAt=now, evidence=PUB + '/schedule-direct-review-v6.json',
             evidenceSha256=digest(PUB + '/schedule-direct-review-v6.json'), status='actual-saved-reopened',
             replacementHistory=[{'baselineSchedule': historical, 'baselineCurrentStatus': 'private-preserved',
                                  'replacementVideoId': '2kNMDlrwdU8', 'verifiedAt': now}])
ledger['updatedAt'] = now
save('shared/publishing/daily-alternating-schedule.json', ledger)
registry = read('shared/git-essential-images.json')
assert not any(e['path'] == image['path'] for e in registry['entries'])
assert image['purpose'] in registry['allowedPurposes']
registry['entries'].append(image)
save('shared/git-essential-images.json', registry)
ignore = ROOT / '.gitignore'
text = ignore.read_bytes().decode('utf-8-sig')
assert '!' + image['path'] not in text.splitlines()
with ignore.open('ab') as output:
    output.write(('\n!' + image['path'] + '\n').encode('utf-8'))
queue = read(BATCH + '/queue.json')
item = next(i for i in queue['items'] if i['slug'] == 'game-math-polar-3d')
item['status'] = 'reviewed-replacement-scheduled-evidence-git-pending'
item['review'].update(privateSettingsVerified=True, gitDelivered=True, scheduleReplacementVerified=True)
item['replacementVideoIds'] = ['2kNMDlrwdU8']
item['baseline']['currentStudioStatus'] = '비공개'
item.update(scheduleEvidence=PUB + '/schedule-direct-review-v6.json', productionGitEvidence=PUB + '/private-delivery-git-verification-v3.json')
queue['scope']['reviewedReplacements'] = 1
queue['execution'].update(currentSlug='motion-sickness-games', stage='polar-schedule-evidence-delivery-then-motion-source-clarity',
                          baselineScheduleChanged=True, next='Deliver the actual schedule/evidence records only, then finish the motion-sickness source/overview/causal-flow revision before its October12 target.')
queue['updatedAt'] = now
save(BATCH + '/queue.json', queue)
handoff = {'schemaVersion': 6, 'slug': 'game-math-polar-3d', 'actualVideoId': '2kNMDlrwdU8', 'recordedAt': now,
           'productionGitCommit': prod['commit'], 'productionGitEvidence': PUB + '/private-delivery-git-verification-v3.json',
           'privateSettingsEvidence': PUB + '/private-settings-direct-review-v3.json', 'scheduleEvidence': PUB + '/schedule-direct-review-v6.json',
           'allMediaAudioPixelQaCollectionCompleted': True, 'actualPrivateSettingsCompleted': True,
           'actualScheduleCompleted': True, 'scheduleEvidenceGitDelivered': False,
           'baselinePreservedPrivate': True, 'other23SchedulesPreserved': True, 'remainingUnpublishedRevisionsComplete': False,
           'humanListeningApproved': False, 'pronunciationApproved': False, 'publicRightsApproved': False,
           'nextSlug': 'motion-sickness-games', 'completedHeavyJobsMustNotRepeat': True}
save(PUB + '/final-handoff-v6.json', handoff)
readme = ROOT / BATCH / 'README.md'
text = readme.read_text(encoding='utf-8')
start = text.index('`queue.json`의 기존 ID')
end = text.index('\n\n', start)
text = text[:start] + '`queue.json`의 기존 ID와 날짜는 보존할 기준이다. `game-math-polar-3d`는 원문·음성·25.2초 개론을 보존하고 실제 게임 선택과 대상 추적 도형을 보강했다. 54,115프레임, 전체44음성 문맥, 386판/2,262표본, 정상속도 전체 설명 흐름, 기술 QA와 4파일 수집 및 새 ID `2kNMDlrwdU8`의 실제 비공개 게시 설정을 검수했다. production `9df320b46fc00c4cb351f61d682a5342e8409d15`는 일반 push와 모든203최종blob 확인을 마쳤다. 수정본은 2026-10-11 오전09:00 GMT+0900으로 실제 저장·재열람했고, 옛 `ZLOewk8JHXA`는 비공개로 보존했다. 목록 재접속에서 다른23편의 날짜·제목과 전체24미래예약을 대조했다. 현재 실제 예약 근거는 `schedule-direct-review-v6.json`이며 예약 증거의 별도 선택 Git 전달은 pending이다. 다음 수정은 `motion-sickness-games`다.' + text[end:]
readme.write_text(text, encoding='utf-8')
print(json.dumps({'actualScheduled': True, 'videoId': '2kNMDlrwdU8', 'baselinePrivate': True, 'other23Preserved': True, 'reviewedReplacements': 1, 'imageSha256': image['sha256'], 'evidenceGitPending': True}))
