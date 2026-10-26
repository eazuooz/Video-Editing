"""Record observed D22 schedule preparation or saved reservation, metadata only.

Default dry-run; --apply updates only D22 records. Does not operate Studio, Git,
media, old receipts, other reservations or the historical global daily schedule.
"""
from pathlib import Path
from datetime import datetime
from copy import deepcopy
import argparse
import hashlib
import json
import os
import uuid
from storage_paths import relative

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PROJECT = ROOT / 'projects/similar-game-design'
SLUG = 'similar-game-design'
REVISION = 'bgm-restored-v4'
VIDEO_ID = 'YRMWX7bdmyM'
MASTER = '8eb5447b25d34c239242fa87c1115d3cecff58e391da4c1f9f8ff7dc12218380'
RECEIPT = PROJECT / 'publishing/reference-preserving-v2/youtube-schedule-bgm-restored-v4.json'
PENDING = 'schedule-fields-prepared-user-ad-evaluation-required'


def require(test, message):
    if not test:
        raise ValueError(message)


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for part in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(part)
    return digest.hexdigest()


def encode(data):
    return (json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def evidence(receipt):
    require((receipt.get('slug'), receipt.get('revision'), receipt.get('videoId')) ==
            (SLUG, REVISION, VIDEO_ID), 'Schedule receipt must identify only the current D22 upload')
    require(receipt.get('masterSha256') == MASTER, 'Schedule receipt master changed')
    require(receipt.get('url') == f'https://youtu.be/{VIDEO_ID}', 'Observed video URL mismatch')
    require(bool(receipt.get('userMessage')), 'Actual schedule request is required')
    datetime.fromisoformat(receipt['observedAt'].replace('Z', '+00:00'))
    require(receipt.get('existingReservationsModified') is False
            and receipt.get('oldUploadsDeleted') is False
            and receipt.get('humanWholeListeningClaimed') is False,
            'Preservation and no-listening-inference scope must remain explicit')
    target, previous = receipt['target'], receipt['lastExistingReservation']
    require(target.get('timezone') == 'Asia/Seoul' and target.get('timezoneOffset') == '+09:00'
            and bool(target.get('actualTimezoneUi')), 'Actual target timezone evidence is required')
    chosen = datetime.fromisoformat(target['date'] + 'T' + target['time'] + ':00' + target['timezoneOffset'])
    utc = datetime.fromisoformat(target['publishAtIfSaved'].replace('Z', '+00:00'))
    require(chosen == utc, 'Displayed local schedule and recorded UTC do not match')
    require(previous.get('actualStatus') == '예약됨' and previous.get('videoId') != VIDEO_ID
            and bool(previous.get('queueScope')), 'Actual final existing reservation evidence is required')
    prior = datetime.fromisoformat(previous['date'] + 'T' + previous['time'] + ':00' + target['timezoneOffset'])
    require(chosen > prior, 'Chosen target must be after the last actually observed reservation')
    saved = receipt.get('scheduled') is True
    if saved:
        require(receipt.get('status') in ['scheduled', 'scheduled-verified', 'schedule-saved-verified']
                and receipt.get('scheduleSaved') is True
                and receipt.get('draft') is False and receipt.get('wizardComplete') is True
                and target.get('isObservedSavedReservation') is True,
                'Successful scheduling requires explicit actual save and reopened reservation evidence')
        require(bool(receipt.get('savedReservationEvidence')),
                'Saved scheduling needs actual saved/reopened UI observation, beyond prepared input fields')
    else:
        require(receipt.get('status') == PENDING and receipt.get('scheduleSaved') is False
                and receipt.get('draft') is True and receipt.get('wizardComplete') is False
                and target.get('isObservedSavedReservation') is False,
                'Unconfirmed target must remain a pending draft, never a saved reservation')
        blocker = receipt['blocker']
        require(blocker.get('actualScheduleButtonDisabled') is True
                and blocker.get('adSuitabilityOwner') == 'human user'
                and blocker.get('agentAnsweredAnyCategory') is False
                and blocker.get('evaluationSubmittedByAgent') is False,
                'Actual user-owned ad-evaluation blocker must remain unsubmitted')
    captures = []
    for value in receipt.get('evidencePaths', []):
        path = Path(value)
        path = path if path.is_absolute() else ROOT / path
        require(path.is_file(), 'Actual schedule capture is absent: ' + value)
        captures.append({'path': value, 'sha256': sha(path), 'bytes': path.stat().st_size})
    require(bool(captures), 'At least one actual UI evidence capture is required')
    return saved, captures


def worklist_doc(text, platform_text):
    lines = text.splitlines(keepends=True)
    for index, line in enumerate(lines):
        end = '\r\n' if line.endswith('\r\n') else '\n'
        if '| 게임디자인 | D22 [' in line:
            cells = line.split('|')
            cells[5] = ' ' + platform_text + ' '
            lines[index] = '|'.join(cells).rstrip('\r\n') + end
        elif line.startswith('| D22 |'):
            cells = line.split('|')
            cells[-2] = ' ' + platform_text + ' '
            lines[index] = '|'.join(cells).rstrip('\r\n') + end
        elif line.startswith('| D22 '):
            lines[index] = '| D22 비슷한 게임을 고를 이유 | Nimbus BGM 복구본. ' + platform_text + '. 영상·TTS·자막·원본 및 기존 예약 유지. 새 오디오 전체 청취 미확인. |' + end
    return ''.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    receipt_bytes = RECEIPT.read_bytes()
    receipt = json.loads(receipt_bytes.decode('utf-8-sig'))
    scheduled, captures = evidence(receipt)
    artifact = {'path': relative(RECEIPT), 'sha256': hashlib.sha256(receipt_bytes).hexdigest(), 'bytes': len(receipt_bytes)}
    observation = {'receipt': artifact, 'videoId': VIDEO_ID, 'masterSha256': MASTER,
        'observedAt': receipt['observedAt'], 'scheduled': scheduled,
        'scheduleSaved': scheduled, 'draft': receipt['draft'], 'wizardComplete': receipt['wizardComplete'],
        'target': deepcopy(receipt['target']), 'lastExistingReservation': deepcopy(receipt['lastExistingReservation']),
        'evidence': captures, 'wholeListening': False, 'existingReservationsModified': False}
    observation['publishAt'] = receipt['target']['publishAtIfSaved'] if scheduled else None
    if not scheduled:
        observation['blocker'] = deepcopy(receipt['blocker'])
    else:
        observation['savedReservationEvidence'] = deepcopy(receipt['savedReservationEvidence'])
    paths = [PROJECT / 'project.json', HERE / 'checkpoint.json', HERE / 'review-ledger.json',
        PROJECT / 'publishing/reference-preserving-v2/metadata-prepared.json',
        ROOT / 'shared/publishing/video-worklist.json', ROOT / 'shared/publishing/video-production-control.json',
        HERE / 'authorization.json']
    original = {p: p.read_bytes() for p in paths}
    before = {p: json.loads(raw.decode('utf-8-sig')) for p, raw in original.items()}
    after = deepcopy(before)
    project, checkpoint, ledger, metadata, work, control, auth = [after[p] for p in paths]
    require(project['currentRevision']['id'] == REVISION and project['delivery']['sha256'] == MASTER
            and project['publishing']['videoId'] == VIDEO_ID
            and ledger['revision'] == REVISION and ledger['master']['sha256'] == MASTER,
            'Current project/master/upload no longer matches this observed scheduling scope')
    scoped = control['scopedProductionAuthorizations'][SLUG]
    for permission in [scoped, auth]:
        latest = permission.get('latestScheduleAuthorization', {})
        require(permission.get('scheduleAuthorized') is True and latest.get('scheduleAuthorized') is True
                and latest.get('videoId') == VIDEO_ID and latest.get('masterSha256') == MASTER,
                'Actual user-backed schedule permission must target only this exact D22 upload')
    stage = 'youtube-scheduled' if scheduled else 'youtube-schedule-prepared-user-ads-pending'
    display = receipt['target']['date'] + ' ' + receipt['target']['time'] + ' KST'
    platform_text = (display + ' 예약 저장 확인') if scheduled else (display + ' 예약 입력 · 사용자 광고평가·예약 저장 대기')
    project.update(status=REVISION + '-' + stage, updatedAt=receipt['observedAt'])
    publishing = project['publishing']
    publishing.update(scheduled=scheduled, publishAt=observation['publishAt'],
        scheduleReceipt=relative(RECEIPT), scheduleObservation=deepcopy(observation),
        scheduleAuthorized=True, draft=receipt['draft'], wizardComplete=receipt['wizardComplete'])
    project['currentRevision'].update(status=stage, scheduled=scheduled,
        publishAt=observation['publishAt'], scheduleReceipt=relative(RECEIPT),
        draft=receipt['draft'], wizardComplete=receipt['wizardComplete'])
    checkpoint.update(stage=stage, status=receipt['status'], updatedAt=receipt['observedAt'],
        scheduled=scheduled, publishAt=observation['publishAt'], scheduleReceipt=relative(RECEIPT),
        scheduleObservation=deepcopy(observation), draft=receipt['draft'], wizardComplete=receipt['wizardComplete'],
        wholeListening=False, nextAction=('Selected video reservation verified. Preserve other reservations and videos; no next video.' if scheduled else
            'User completes the reserved ad-suitability evaluation; then root saves and rereads the prepared reservation. Do not claim it scheduled before actual success.'))
    ledger.update(status=stage, scheduleObservation=deepcopy(observation))
    require(ledger['humanFinalReview'].get('wholeListening') is False,
            'This metadata-only action cannot alter actual whole-listening status')
    metadata.update(status=REVISION + '-' + stage, scheduleObservation=deepcopy(observation),
        scheduleReceipt=relative(RECEIPT), userFinalReviewClaimed=False)
    for container in [publishing, checkpoint, metadata, ledger, scoped]:
        platform = container.get('currentUpload') if 'currentUpload' in container else container.get('platform')
        if container is scoped:
            platform = container.get('actualUpload')
        if isinstance(platform, dict):
            require(platform.get('videoId') == VIDEO_ID, 'Current platform observation identity mismatch')
            platform.update(scheduled=scheduled, publishAt=observation['publishAt'],
                draft=receipt['draft'], wizardComplete=receipt['wizardComplete'],
                scheduleObservation=deepcopy(observation))
            if scheduled:
                platform['pending'] = deepcopy(receipt.get('remainingPending', []))
            else:
                platform['pending'] = ['User-owned ad-suitability self-assessment',
                    'Reservation save and saved-schedule verification']
    row = next(r for r in work['rows'] if r.get('id') == 'D22')
    require(row.get('slug') == SLUG and row.get('videoId') == VIDEO_ID, 'D22 worklist identity mismatch')
    row.update(platformStatus=platform_text, scheduleReceipt=relative(RECEIPT),
        scheduled=scheduled, publishAt=observation['publishAt'], platformEvidence=relative(RECEIPT))
    row['currentRevision'].update(status=stage, scheduled=scheduled, publishAt=observation['publishAt'],
        draft=receipt['draft'], wizardComplete=receipt['wizardComplete'], scheduleReceipt=relative(RECEIPT))
    for permission in [scoped, auth]:
        latest = permission['latestScheduleAuthorization']
        latest.update(dateNotYetAssigned=False, targetFieldsPrepared=True,
            reservationConfirmed=scheduled, target=deepcopy(receipt['target']),
            receipt=artifact, observedAt=receipt['observedAt'],
            scheduledPublicationAuthorized=True,
            authorizationBasis='Direct user instruction to schedule publication of this exact uploaded master after the actual reservation queue.',
            actualWholeViewingInferred=False, actualWholeListeningInferred=False)
        permission.update(scheduleAuthorized=True, status=stage,
            scheduleObservation=deepcopy(observation), scheduled=scheduled)
    publishing['currentScheduleAuthorization'] = deepcopy(auth['latestScheduleAuthorization'])
    checkpoint['currentScheduleAuthorization'] = deepcopy(auth['latestScheduleAuthorization'])
    ledger['scheduleAuthorization'] = deepcopy(auth['latestScheduleAuthorization'])
    # Authorize only this one video; preserve every unrelated control field and row.
    old, new = deepcopy(before[paths[4]]), deepcopy(work)
    old['rows'] = [r for r in old['rows'] if r.get('id') != 'D22']
    new['rows'] = [r for r in new['rows'] if r.get('id') != 'D22']
    require(old == new, 'Worklist update escaped D22')
    old, new = deepcopy(before[paths[5]]), deepcopy(control)
    del old['scopedProductionAuthorizations'][SLUG]
    del new['scopedProductionAuthorizations'][SLUG]
    require(old == new, 'Control update escaped D22 scoped authorization')
    require(project['paths'] == before[paths[0]]['paths'] and project['delivery'] == before[paths[0]]['delivery']
            and ledger['master'] == before[paths[2]]['master'], 'Scheduling must not change media/source/delivery')
    outputs = {path: encode(after[path]) for path in paths}
    doc = ROOT / 'docs/VIDEO_WORKLIST.md'
    original[doc] = doc.read_bytes()
    outputs[doc] = worklist_doc(original[doc].decode('utf-8-sig'), platform_text).encode('utf-8')
    summary = {'mode': 'apply' if args.apply else 'dry-run', 'videoId': VIDEO_ID,
        'scheduled': scheduled, 'confirmedPublishAt': observation['publishAt'],
        'preparedTarget': receipt['target'], 'wholeListening': False,
        'writes': [relative(p) for p in outputs], 'uiActions': 0, 'mediaJobs': 0, 'gitActions': 0}
    if args.apply:
        require(RECEIPT.read_bytes() == receipt_bytes, 'Concurrent schedule receipt change; retry')
        for path, raw in original.items():
            require(path.read_bytes() == raw, 'Concurrent metadata change; retry: ' + str(path))
        for path, raw in outputs.items():
            temporary = path.with_name(path.name + '.d22-' + uuid.uuid4().hex + '.tmp')
            temporary.write_bytes(raw)
            os.replace(temporary, path)
        (HERE / 'schedule-record-finalization-bgm-v4.json').write_bytes(encode({**summary,
            'receipt': artifact, 'after': {relative(p): sha(p) for p in outputs}}))
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
