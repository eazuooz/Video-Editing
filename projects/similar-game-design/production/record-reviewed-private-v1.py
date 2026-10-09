"""Seal actual saved/reopened UI facts for one reviewed private upload."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'projects/similar-game-design'
P = BASE / 'publishing'
QA = ROOT / 'shared/output/similar-game-design/publishing-qa-v1'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
def save(p, x):
    p.write_text(json.dumps(x, ensure_ascii=False, indent=2) + '\n', 'utf-8')
now = datetime.now(timezone.utc).isoformat()
proofs = {}
def observed(name, expected):
    p = QA / name
    t = p.read_text('utf-8')
    for text in expected:
        assert text in t, (name, text)
    proofs[name] = dict(path=p.relative_to(ROOT).as_posix(), sha256=sha(p))
    return t

r = read(P / 'youtube-upload-v1.json')
assert r['actualVideoId'] == '_p1IqDeg6YE' and r['privateSaveVerified']
seal = read(BASE / 'production/final-v1/final-pixel-direct-review-v1.json')
assert seal['allFinalPixelsReviewed'] and r['video']['sha256'] == seal['sourceSha256']
observed('details-current-completed.ax.txt', ['비공개', '표준 화질 완료', '고화질 완료', '업로드된 썸네일', 'Planning & Game Design & Tech', r['metadata']['title'], r['metadata']['description']])
observed('english-saved-reopened.ax.txt', [r['englishMetadata']['title'], r['englishMetadata']['description'], '수동', '게시됨'])
observed('korean-saved-reopened.ax.txt', ['수동 자막', '수동', '게시됨'])
observed('card-saved-reopened.ax.txt', [r['coachingCard']['url'], '프로그래밍 과외', '00:00'])
for name, expected in [('end-subscribe-saved-reopened.ax.txt', '얌얌코딩'), ('end-playlist-saved-reopened.ax.txt', 'Planning & Game Design & Tech'), ('end-link-saved-reopened.ax.txt', r['coachingCard']['url'])]:
    observed(name, [expected, '10:08:18', '10:18:18'])
observed('monetization-saved-reopened.ax.txt', ['사용', '동영상 재생 중에 미드롤 광고 게재, Value: 1'])
observed('copyright-saved-no-claims.ax.txt', ['동영상에서 소유권 주장이 발견되지 않았습니다'])
observed('current-no-notices-monetization-result.ax.txt', ['_p1IqDeg6YE', '알림 없음', '이 동영상은 설정에 따라 시청자에게 도달하여 수익을 창출하고 있습니다.'])
observed('advanced-saved-reopened.ax.txt', ['동영상에 유료 프로모션이 포함되어 있지 않습니다., Value: 1', '아니요, AI를 사용하지 않았습니다., Value: 1', '한국어', '표준 YouTube 라이선스', '교육'])
for name in ['uploaded-game-cc-off.ax.txt', 'uploaded-25d-cc-off.ax.txt']:
    observed(name, ['_p1IqDeg6YE', '자막 사용 불가, Value: 0', '비공개'])

images = [
    ('uploaded-game-cc-off-v1.png', 'Actual private watch page at30s: full-screen Brotato action and permanently burned bottom Korean caption; player optional captions are off/unavailable.'),
    ('uploaded-25d-cc-off-v1.png', 'Actual private watch page at50s: projected platforms with visible top/side faces, route comparison and fixed bottom Korean caption; optional captions are off/unavailable.'),
    ('end-screen-saved-reopened-v1.png', 'Actual saved/reopened608.3–618.3s three-element end screen: own subscribe, relevant playlist and canonical coaching URL; original member identities remain unobscured at613s.')]
registry = read(ROOT / 'shared/git-essential-images.json')
ignore_path = ROOT / '.gitignore'
ignore = ignore_path.read_text('utf-8-sig')
image_records = []
for name, reason in images:
    p = P / name
    assert p.is_file()
    entry = dict(path=p.relative_to(ROOT).as_posix(), purpose='minimal-publishing-proof', reason=reason,
                 sha256=sha(p), reviewedAt=now, project='similar-game-design', directlyReviewed=True)
    previous = next((x for x in registry['entries'] if x['path'] == entry['path']), None)
    assert previous is None or previous['sha256'] == entry['sha256']
    if previous is None:
        registry['entries'].append(entry)
    if '!' + entry['path'] not in ignore.splitlines():
        ignore = ignore.rstrip() + '\n!' + entry['path'] + '\n'
    image_records.append(entry)
save(ROOT / 'shared/git-essential-images.json', registry)
ignore_path.write_text(ignore, 'utf-8')

pending = ['Human whole listening/pronunciation', 'Public rights', 'Original Nimbus library file',
           'Source-truncated member handles', 'External backup', 'Automatic dubbing/optional CC propagation',
           'Private pinned comment: exact original prepared, not posted']
r.update(updatedAt=now, status='reviewed-single-private-settings-complete-git-pending',
    captionedSha256=seal['sourceSha256'], privateUpload=True, scheduled=False,
    fullSettingsVerified=True, availableSettingsVerified=True, platformAutomaticChecksComplete=True,
    automaticChecks='Current post-processing Studio: no notices, monetization according to settings, no copyright claims.',
    automaticCheckEvidence=proofs['current-no-notices-monetization-result.ax.txt'],
    explicitAdCheckCompletionModalObserved=False,
    checkObservation='The initial ad-check pending is superseded by the current authoritative no-notices/earning tooltip. No separate final wizard/ad-check completion modal was observed.',
    burnedCaptionPixelsVerified=True, burnedCaptionUploadedPixelsVerified=True,
    thumbnailSavedVerified=True, sdComplete=True, hdComplete=True,
    manualKoPublished=True, manualEnPublished=True, englishMetadataSavedReopened=True,
    platformEvidence=proofs, minimumPublishingImages=image_records, pending=pending,
    humanWholeListeningApproved=False, humanPronunciationApproved=False, publicRightsApproved=False,
    alteredContent=dict(value=False, scope='Platform realistic altered-content criteria; actual gameplay, non-realistic explanatory diagrams and illustrated thumbnail. Production uses approved synthesized narration.', policySource='https://support.google.com/youtube/answer/14328491?hl=en'),
    paidPromotion=False, category='Education', originalLanguage='ko', license='Standard YouTube License')
r['englishMetadata'].update(saved=True, savedReopened=True, published=True)
for item, language, cues in zip(r['subtitles'], ['ko', 'en'], [400, 148]):
    item.update(status='manually-published-and-reopened', language=language, cues=cues, sha256=sha(ROOT / item['path']))
r['coachingCard'].update(saved=True, savedReopened=True, titleKo='프로그래밍 과외', teaserKo='프로그래밍 과외')
r['endScreen'].update(saved=True, savedReopened=True, savedUiFps=60, startDisplay='10:08:18', endDisplay='10:18:18',
    memberIdentitiesUnobscured=True, privateWatchEndElementsUnavailable=True)
r['pending'] = pending
save(P / 'youtube-upload-v1.json', r)
execution_path = P / 'private-upload-execution-v1.json'
e = read(execution_path)
assert e['actualVideoId'] == r['videoId'] and e['uploadCountThisAttempt'] == 1
e.update(updatedAt=now, status=r['status'], fullSettingsVerified=True, availableSettingsVerified=True,
    platformAutomaticChecksComplete=True, burnedCaptionPixelsVerified=True, finishedAt=now,
    next='Selective normal Git push and actual remote/blob verification; then presenting-game-scores full-source/current duplicate review with future black explanation palette.')
save(execution_path, e)
cp_path = BASE / 'production/latest-checkpoint.json'
c = read(cp_path)
c.update(updatedAt=now, stage=r['status'], status=r['status'], fullSettingsVerified=True,
         availableSettingsVerified=True, platformAutomaticChecksComplete=True, allFinalPixelsReviewed=True,
         burnedCaptionPixelsVerified=True, nextAction=e['next'])
save(cp_path, c)
qp = ROOT / 'production/batches/sakurai-planning-game-design/queue.json'
q = read(qp)
i = next(x for x in q['items'] if x['slug'] == 'similar-game-design')
i.update(stage=r['status'], fullSettingsVerified=True, availableSettingsVerified=True,
    platformAutomaticChecksComplete=True, allFinalPixelsReviewed=True, burnedCaptionPixelsVerified=True,
    uploadTransferComplete=True, privateUpload=True, actualUploadId=r['videoId'], publishingExecution=execution_path.relative_to(ROOT).as_posix())
q['progress'].update(rendered=15, collected=15, uploaded=15, productionRendered=15, productionCollected=15,
    privateSaved=15, fullSettingsDelivered=15, productionDelivered=15, remainingProduction=8,
    productionGitDelivered=14, remaining=9, inProgress=1, queued=8)
q.update(updatedAt=now, lastProgressAt=now)
save(qp, q)
rp = ROOT / 'production/batches/sakurai-planning-game-design/README.md'
t = rp.read_text('utf-8-sig')
note = '2026-10-09 latest: similar-game-design is saved once privately as _p1IqDeg6YE; current618.3s/37098frames,48mixed-ASR windows and all1810encoded samples/302boards are technically reviewed, and clean/captioned/400KO/148EN files are collected. Thumbnail, manual KOEN, separate EN information, canonical00s coaching card and608.3–618.3s playlist/subscribe/link are saved/reopened; original member identities remain unobscured. SD/HD complete, current Studio reports no notices/earning according to settings and no copyright claims. CC-off uploaded game30s and projected explanation50s fixed-caption pixels were directly reviewed. Selective normal Git delivery remains. Separate completion modal was not observed; human listening/pronunciation/public-rights/Nimbus/handles/backup/dubbing/optionalCC/private comment remain pending. Next unstarted presenting-game-scores uses research-black-v1; this already-started video retains white. Completed media/upload/research handoff are not repeated.'
assert note not in t
t = t.replace('\n', '\n\n' + note + '\n', 1)
rp.write_text(t, 'utf-8')
print(json.dumps(dict(videoId=r['videoId'], privateVerified=True, availableSettingsVerified=True,
    uploadedGameAndSpatialCaptionsVerified=True, minimalProofImages=len(images), gitPending=True)))
