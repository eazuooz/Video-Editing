import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BATCH = 'production/batches/unpublished-teaching-clarity-revision'
REV = 'projects/motion-sickness-games/production/revision-teaching-clarity-v1'
PUB = REV + '/publishing'
OLD, NEW = 'c18rkesgBSw', 'mBDd9VzSTkA'

def read(p):
    return json.loads((ROOT / p).read_text(encoding='utf-8-sig'))

def save(p, value):
    target = ROOT / p
    temporary = target.with_name(target.name + '.motion-schedule.tmp')
    assert not temporary.exists()
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temporary.replace(target)

def digest(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()

def rowrecord(row):
    links = [e if isinstance(e, str) else e['href'] for e in row['links']]
    identity = next(re.search(r'/video/([^/]+)/edit', e)[1] for e in links if re.search(r'/video/([^/]+)/edit', e))
    day = re.search(r'2026\.\s*(\d+)\.\s*(\d+)\.', row['text'])
    assert day and '예약됨' in row['text']
    return identity, {'title': row['text'].splitlines()[1], 'date': f'2026-{int(day[1]):02d}-{int(day[2]):02d}'}

assert not (ROOT / PUB / 'schedule-direct-review-v1.json').exists(), 'Preserve completed schedule record'
now = datetime.now(timezone.utc).isoformat()
bmap = dict(map(rowrecord, read(PUB + '/schedule-before-actual-rows-v1.json')['rows']))
amap = dict(map(rowrecord, read(PUB + '/schedule-after-actual-rows-v1.json')['rows']))
assert len(bmap) == len(amap) == 24 and OLD in bmap and OLD not in amap and NEW in amap and NEW not in bmap
assert bmap[OLD] == amap[NEW] and amap[NEW]['date'] == '2026-10-12'
unchanged = sorted(set(bmap) - {OLD})
assert len(unchanged) == 23 and all(bmap[k] == amap[k] for k in unchanged)
ax = (ROOT / PUB / 'schedule-reopened-v1.ax.txt').read_text(encoding='utf-8')
assert '2026. 10. 12.' in ax and '오전 9:00' in ax and 'GMT+0900' in ax
assert f'https://youtu.be/{NEW}' in ax and 'button "완료" [disabled]' in ax
assert 'checkbox "Premieres 동영상으로 설정"\n' in ax
baseline = (ROOT / PUB / 'baseline-private-reloaded-v1.ax.txt').read_text(encoding='utf-8')
assert f'https://youtu.be/{OLD}' in baseline and re.search(r'공개 상태[\s\S]{0,80}generic: 비공개', baseline)
prod = read(PUB + '/private-delivery-git-verification-v1.json')
assert all(prod[k] for k in ['pushed', 'exactLocalRemoteMatch', 'allFinalRemoteBlobsVerified', 'externalIndexUnchanged'])
assert prod['commit'] == 'a25531cd424f1010de6a88f1f11466ebd468962a' and prod['verifiedBlobCount'] == 441
receipt = read(PUB + '/youtube-upload-v1.json')
assert receipt['actualVideoId'] == NEW and all(receipt[k] for k in ['uploaded', 'privateSaveVerified', 'fullSettingsVerified', 'automaticChecksPassed', 'burnedCaptionPixelsVerified'])
image = {'path': PUB + '/schedule-reopened-proof-v1.png', 'purpose': 'minimal-publishing-proof',
         'reason': 'Directly reviewed saved-and-reopened Studio schedule with October12 09:00 GMT+0900, Premieres off and disabled Done; paired current AX identifies mBDd9VzSTkA. Original c18rkesgBSw is preserved privately.',
         'sha256': digest(PUB + '/schedule-reopened-proof-v1.png'), 'reviewedAt': now, 'project': 'motion-sickness-games'}
proof = {'schemaVersion': 1, 'slug': 'motion-sickness-games', 'actualVideoId': NEW, 'baselineVideoId': OLD,
         'date': '2026-10-12', 'time': '09:00', 'timezone': 'Asia/Seoul', 'timezoneOffset': '+09:00',
         'publishAt': '2026-10-12T00:00:00Z', 'premieres': False, 'scheduleSavedAndReopened': True,
         'baselinePreservedPrivate': True, 'baselineDeleted': False, 'futureListReloaded': True,
         'futureScheduleCount': 24, 'other23DatesAndTitlesUnchanged': True, 'unchangedVideoIds': unchanged,
         'beforeRows': PUB + '/schedule-before-actual-rows-v1.json', 'afterRows': PUB + '/schedule-after-actual-rows-v1.json',
         'reopenedAx': PUB + '/schedule-reopened-v1.ax.txt', 'baselinePrivateAx': PUB + '/baseline-private-reloaded-v1.ax.txt',
         'reviewedEssentialImages': [image], 'productionGitCommit': prod['commit'],
         'humanListeningApproved': False, 'pronunciationApproved': False, 'publicRightsApproved': False, 'verifiedAt': now}

# Replace only the owned JSON object, preserving every byte outside its span.
ledgerpath = ROOT / 'shared/publishing/daily-alternating-schedule.json'
original = ledgerpath.read_bytes()
text = original.decode('utf-8-sig')
decoder = json.JSONDecoder()
start = text.index('[', text.index('"actualSchedules"')) + 1
while True:
    while text[start].isspace() or text[start] == ',':
        start += 1
    assert text[start] != ']'
    entry, end = decoder.raw_decode(text, start)
    if entry.get('slug') == 'motion-sickness-games':
        break
    start = end
assert entry['videoId'] == OLD and entry['date'] == proof['date'] and entry['time'] == proof['time']
history = dict(entry)
replacement = {**entry, 'videoId': NEW, 'verifiedAt': now, 'evidence': PUB + '/schedule-direct-review-v1.json',
               'status': 'actual-saved-reopened', 'replacementHistory': [{'baselineSchedule': history,
               'baselineCurrentStatus': 'private-preserved', 'replacementVideoId': NEW, 'verifiedAt': now}]}
save(PUB + '/schedule-direct-review-v1.json', proof)
replacement['evidenceSha256'] = digest(PUB + '/schedule-direct-review-v1.json')
newline = '\r\n' if '\r\n' in text else '\n'
indent = re.search(r'^[ \t]*', text[text.rfind('\n', 0, start) + 1:start])[0]
encoded = json.dumps(replacement, ensure_ascii=False, indent=2).replace('\n', newline + indent)
prefix = b'\xef\xbb\xbf' if original.startswith(b'\xef\xbb\xbf') else b''
updated = prefix + (text[:start] + encoded + text[end:]).encode('utf-8')
assert ledgerpath.read_bytes() == original, 'Concurrent ledger update; preserve it'
ledgerpath.write_bytes(updated)
outsidebefore = (text[:start] + text[end:]).encode('utf-8')
save(PUB + '/schedule-ledger-owned-patch-v1.json', {'schemaVersion': 1, 'recordedAt': now,
     'path': 'shared/publishing/daily-alternating-schedule.json', 'beforeEntry': history,
     'replacementSchedule': replacement, 'otherWorkingBytesPreserved': True,
     'outsideOwnedSpanSha256': hashlib.sha256(outsidebefore).hexdigest(),
     'beforeSha256': hashlib.sha256(original).hexdigest(), 'afterSha256': hashlib.sha256(updated).hexdigest()})
receipt.update(status='reviewed-scheduled-replacement-production-git-delivered', gitDelivered=True, scheduled=True,
               baselineScheduleChanged=True, updatedAt=now, gitEvidence=PUB + '/private-delivery-git-verification-v1.json',
               scheduleEvidence=PUB + '/schedule-direct-review-v1.json', actualSchedule={k: proof[k] for k in ['date', 'time', 'timezone', 'timezoneOffset', 'publishAt']})
save(PUB + '/youtube-upload-v1.json', receipt)
checkpoint = read(REV + '/latest-checkpoint.json')
checkpoint.update(stage='reviewed-scheduled-replacement;schedule-evidence-git-pending', gitDelivered=True,
                  scheduled=True, scheduleReplacementVerified=True, productionGitEvidence=receipt['gitEvidence'],
                  scheduleEvidence=receipt['scheduleEvidence'], recordedAt=now,
                  next='Deliver schedule evidence once, then audit orientation matrices before revising unmet teaching requirements.')
save(REV + '/latest-checkpoint.json', checkpoint)
queue = read(BATCH + '/queue.json')
item = next(e for e in queue['items'] if e['slug'] == 'motion-sickness-games')
item.update(status='reviewed-replacement-scheduled-evidence-git-pending', scheduleEvidence=receipt['scheduleEvidence'],
            productionGitEvidence=receipt['gitEvidence'], currentDuplicateReview=REV + '/inventory-change-direct-review-v13.json',
            reviewScopeNote='Current narration content, complete 1x flow, sampled final moving pixels, technical QA, four outputs, actual private settings, production Git and reopened schedule verified. Human listening/pronunciation/public rights remain pending.')
item['baseline'].update(currentStudioStatus='비공개', freshTimeTimezoneReopened=True)
item['review'].update(gitDelivered=True, scheduleReplacementVerified=True)
queue['scope']['reviewedReplacements'] = 2
queue['execution'].update(currentSlug='game-math-orientation-matrices', stage='motion-schedule-evidence-delivery-then-orientation-audit',
                          next='Deliver motion schedule evidence; compare orientation source, causal chain and gameplay before creating a replacement.')
queue['updatedAt'] = now
save(BATCH + '/queue.json', queue)
manifest = read('projects/motion-sickness-games/project.json')
manifest['publishing'].update(privacyStatus='private-until-scheduled-publication', scheduledPublishAt=proof['publishAt'],
    videoId=NEW, actualVideoId=NEW, videoUrl=f'https://youtu.be/{NEW}', uploaded=True, scheduled=True,
    status='reviewed-scheduled-replacement', fullSettingsVerified=True, ccOffPixelVerification=PUB + '/uploaded-pixel-observations-v1.json',
    baselineScheduleChanged=True, baselinePreserved=True, productionGitEvidence=receipt['gitEvidence'], scheduleEvidence=receipt['scheduleEvidence'])
save('projects/motion-sickness-games/project.json', manifest)
save(PUB + '/final-handoff-v1.json', {'schemaVersion': 1, 'slug': 'motion-sickness-games', 'actualVideoId': NEW,
    'recordedAt': now, 'productionGitCommit': prod['commit'], 'productionGitEvidence': receipt['gitEvidence'],
    'privateSettingsEvidence': PUB + '/private-settings-direct-review-v1.json', 'scheduleEvidence': receipt['scheduleEvidence'],
    'allMediaAudioPixelQaCollectionCompleted': True, 'actualPrivateSettingsCompleted': True, 'actualScheduleCompleted': True,
    'scheduleEvidenceGitDelivered': False, 'baselinePreservedPrivate': True, 'other23SchedulesPreserved': True,
    'remainingUnpublishedRevisionsComplete': False, 'humanListeningApproved': False, 'pronunciationApproved': False,
    'publicRightsApproved': False, 'nextSlug': 'game-math-orientation-matrices', 'completedHeavyJobsMustNotRepeat': True})
readme = ROOT / BATCH / 'README.md'
content = readme.read_text(encoding='utf-8')
content = content.replace('최소 게시 증거3PNG만 선택Git 후보이며 나머지QA/AX/원본미디어는local-only다. 실제 비공개 설정은 `private-settings-direct-review-v1.json`으로 봉인했고 선택Git·예약 교체는 pending이다. 기존 `c18rkesgBSw`의10/12 오전9시 예약은 검수된 대체본 전달까지 보존한다.',
    'production `a25531cd424f1010de6a88f1f11466ebd468962a`는 일반push와441최종blob 확인을 마쳤고, 최소 게시 증거3PNG만 개별검수로 추가했다. 실제 비공개 설정은 `private-settings-direct-review-v1.json`으로 봉인했다. 수정본 `mBDd9VzSTkA`의2026-10-12 오전09:00 GMT+0900을 저장재열람했고 옛 `c18rkesgBSw`는 비공개로 보존했다. 목록 재접속에서 다른23편의 날짜·제목이 그대로임을 대조했다. 예약 증거 별도Git은 pending이며 다음은 `game-math-orientation-matrices` 검수다. 나머지QA/AX/미디어는local-only다.')
readme.write_text(content, encoding='utf-8')
print(json.dumps({'actualScheduled': True, 'actualVideoId': NEW, 'baselinePrivate': True, 'other23Preserved': True,
                  'reviewedReplacements': 2, 'workingLedgerOtherBytesPreserved': True, 'evidenceGitPending': True}))
