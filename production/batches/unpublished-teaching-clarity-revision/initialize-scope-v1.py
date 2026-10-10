"""Record observed current deliveries; do not infer content approval from a list."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
LOCAL = ROOT / 'shared/output/unpublished-teaching-clarity-revision'

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def save(path, value):
    assert not path.exists(), f'Preserve existing checkpoint: {path}'
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def observed_rows(path):
    records = []
    for row in read(path):
        links = [a for a in row['links'] if re.search(r'/video/[^/]+/edit$', a['url'])]
        if not links:
            continue
        link = links[-1]
        records.append({'videoId': link['url'].split('/')[2], 'titleKo': link['text'].strip(),
                        'rowText': row['text'], 'editUrl': 'https://studio.youtube.com' + link['url']})
    return records

now = datetime.now(timezone.utc).isoformat()
ledger_path = ROOT / 'shared/publishing/daily-alternating-schedule.json'
ledger_bytes = ledger_path.read_bytes()
ledger = read(ledger_path)
scheduled_path = LOCAL / 'studio-scheduled-rows-v1.json'
private_path = LOCAL / 'studio-private-rows-page1-v1.json'
scheduled = observed_rows(scheduled_path)
private = observed_rows(private_path)
assert len(scheduled) == 24 and len(private) == 2
assert all('예약됨' in row['rowText'] for row in scheduled)
assert all('비공개' in row['rowText'] for row in private)
by_id = {item['videoId']: item for item in ledger['actualSchedules']}
assert len({row['videoId'] for row in scheduled}) == len(scheduled)
owner_path = ROOT / 'production/batches/game-math-part2-teaching-revision/queue.json'
owner_bytes = owner_path.read_bytes()
owner = read(owner_path)
owned_math = {item['slug'] for item in owner['items']}
assert len(owned_math) == 11

items = []
for row in scheduled:
    old = by_id[row['videoId']]
    date = datetime.strptime(old['date'], '%Y-%m-%d')
    assert f'{date.year}. {date.month}. {date.day}.' in row['rowText']
    assert row['titleKo'] == old['title']
    linked = old['slug'] in owned_math
    items.append({
        'slug': old['slug'], 'titleKo': row['titleKo'], 'category': old['category'],
        'status': 'linked-active-owner-audit-required' if linked else 'content-audit-required',
        'baseline': {'videoId': row['videoId'], 'actualStudioStatus': '예약됨',
                     'date': old['date'], 'time': old['time'], 'timezone': 'Asia/Seoul',
                     'freshDateObserved': True, 'freshTimeTimezoneReopened': False,
                     'originalTimeTimezoneEvidence': old['evidence'],
                     'editUrl': row['editUrl'], 'historicalCompletionPreserved': True},
        'executionOwnerQueue': 'production/batches/game-math-part2-teaching-revision/queue.json' if linked else None,
        'startDuplicateWorker': False,
        'review': {key: False for key in ['fullScriptAndClaimsRead', 'openingOverviewPassed',
                   'causalFlowPassed', 'referenceFlowCompared', 'firstTimeGameplayCompared',
                   'onFootageAnnotationMotionPassed', 'currentMixedAudioPassed', 'allFinalPixelsPassed',
                   'technicalQaPassed', 'outputsCollected', 'privateSettingsVerified',
                   'gitDelivered', 'scheduleReplacementVerified']},
        'replacementVideoIds': [], 'humanListeningApproved': False, 'publicRightsApproved': False
    })
items.sort(key=lambda item: item['baseline']['date'])
excluded = [{'videoId': 'oDYJlcv2Dqk', 'status': '비공개',
             'reason': 'Superseded score baseline; current Balatro60:Tetris40 delivery L5DA2xiV46M is in the revision scope. Preserve this history.'},
            {'videoId': '6ZzSh40WojQ', 'status': '비공개',
             'reason': 'Unrelated 2025 weekly free-assets upload; preserve rather than silently expand this game-design/lecture production request.'}]
assert {row['videoId'] for row in private} == {item['videoId'] for item in excluded}
evidence = {'schemaVersion': 1, 'observedAt': now, 'channelId': 'UCOgtkPoyC0VXhCs7Xk3jvjQ',
            'scheduledCount': len(scheduled), 'privateListTotal': len(private),
            'scheduled': scheduled, 'private': private,
            'evidence': [{'path': p.relative_to(ROOT).as_posix(), 'sha256': sha(p)} for p in
                         [scheduled_path, private_path, LOCAL / 'studio-scheduled-20261010-v1.ax.txt',
                          LOCAL / 'studio-private-20261010-v2.ax.txt']],
            'platformSettingsMutations': 0, 'listIsContentApproval': False,
            'all492ChannelVideosContentReviewed': False,
            'foreignOwnerQueue': {'path': owner_path.relative_to(ROOT).as_posix(), 'sha256': sha(owner_path),
                                  'readOnly': True, 'currentSlug': owner['execution']['currentSlug'],
                                  'currentStage': owner['execution']['stage']}}
save(HERE / 'studio-scope-direct-review-v1.json', evidence)
save(HERE / 'queue.json', {
    'schemaVersion': 1, 'createdAt': now, 'mode': 'active',
    'userEvidence': ['영상 초반에 어떤 영상인지에 대한 개론을 잘 삽입해줘 항상 ... 유기적으로 연결 되게끔 ... 마사히로 영상같은 흐름에 맞는지 검수해줘',
                     '실제 게임영상 비교해서 찾을때 좀더 잘 이해되는 영상인지 꼭 확인해서 골라줘 ... 빨간선이나 다양한 색의 도형 ... 아직 게시되지 않은 영상들 이규칟 적용해서 수정해줘'],
    'policy': {'scope': 'current unpublished reviewed game-design and game-lecture deliveries, including scheduled uploads, plus current/new productions',
               'publishedAndHistoricalBaselinesPreserved': True, 'retainOriginalUsefulMaterialAndApprovedPcm': True,
               'auditBeforeRevision': True, 'newFinalMediaMustBeReviewed': True,
               'recordingOrPreparedOverlayIsCompletion': False,
               'ratioAudioPaletteCaptionOutrosFollowEachProject': True,
               'mathReferenceComparison': 'Apply clear problem/example/result progression; compare the actual lesson source. Do not pretend there is a corresponding Sakurai math video.',
               'designReferenceComparison': 'Compare the corresponding Sakurai source sequence and game examples, record intentional independent explanation differences; never copy its full narration or media.',
               'schedule': 'Preserve existing date anchors and daily alternating09:00KST. Save a reviewed private replacement, publishing settings and Git first; then reopen actual replacement schedule. If a target cannot be met, do not publish unfinished work.'},
    'scope': {'scheduledDeliveries': 24, 'gameDesign': 10, 'gameLecture': 14,
              'linkedExistingMathRevisions': 11, 'otherScheduledAudits': 13,
              'newDesignProductions': len(ledger['pendingTargets']), 'reviewedReplacements': 0,
              'evidence': 'production/batches/unpublished-teaching-clarity-revision/studio-scope-direct-review-v1.json'},
    'execution': {'currentSlug': 'game-math-polar-3d', 'stage': 'earliest-schedule-full-script-and-footage-audit',
                  'currentNewProductionSlug': 'limited-color-world', 'heavyJob': None,
                  'foreignProcessesModified': 0, 'foreignOwnerQueueModified': False},
    'items': items, 'newProductionTargets': ledger['pendingTargets'], 'excludedPrivateHistory': excluded,
    'publishedObservedExcluded': ['xtUVcAHtQzg', 'gSN8tbGkJ5E', 'PcxaKEvbzjg', 'BYk6cLsO9Mc', 'lX7SXU7tMBc'],
    'platformMutations': 0, 'gitDelivered': False
})
assert ledger_path.read_bytes() == ledger_bytes and owner_path.read_bytes() == owner_bytes
print(json.dumps({'scheduled': len(items), 'linkedOwner': len(owned_math),
                  'newTargets': len(ledger['pendingTargets']), 'platformMutations': 0,
                  'foreignOwnerBytesUnchanged': True}, ensure_ascii=False))
