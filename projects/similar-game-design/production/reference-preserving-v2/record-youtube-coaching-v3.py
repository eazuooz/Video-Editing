"""Record one observed D22 private upload/draft; dry-run unless --apply.

No network, Studio, media, Git, scheduling or deletion actions. The root agent
authors the receipt from observed UI. Autosaved drafts remain incomplete drafts.
"""
from pathlib import Path
from datetime import datetime, timezone
from copy import deepcopy
import argparse
import hashlib
import json
import os
import re
import uuid

from storage_paths import repo_path, relative

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PROJECT = ROOT / 'projects/similar-game-design'
SLUG = 'similar-game-design'
REVISION = 'coaching-silent-v3'
MASTER_SHA = '18b443d7ad8fdd8e0981de1fa54a0519fa4dc692d898705728c041840321bbfa'
BASELINE = '_p1IqDeg6YE'
RECEIPT = PROJECT / 'publishing/reference-preserving-v2/youtube-upload-coaching-silent-v3.json'
DRAFT_STATUS = 'private-draft-uploaded-human-ads-pending'


def read(path):
    return json.loads(path.read_text('utf-8-sig'))


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate_receipt(receipt, hash_master=True):
    require((receipt.get('slug'), receipt.get('revision')) == (SLUG, REVISION),
            'Receipt must identify the exact D22 coaching-silent-v3 revision')
    video_id = receipt.get('videoId', '')
    require(re.fullmatch(r'[A-Za-z0-9_-]{11}', video_id) and video_id != BASELINE,
            'A new actually observed video ID is required; baseline must remain untouched')
    is_draft = receipt.get('status') == DRAFT_STATUS
    if is_draft:
        require(receipt.get('saved') is True and receipt.get('draft') is True
                and receipt.get('wizardComplete') is False,
                'Draft receipt must explicitly identify private autosave and an incomplete wizard')
        ads = receipt.get('adSuitability', {})
        require(ads.get('owner') == 'human user' and ads.get('submittedByAgent') is False,
                'The user-reserved ad suitability evaluation must remain unsubmitted by the agent')
        require(receipt.get('fullSettingsVerified') is not True
                and receipt.get('privateUploadComplete') is not True,
                'An autosaved draft cannot claim final private upload/settings completion')
    else:
        require(receipt.get('draft') is not True and receipt.get('wizardComplete') is not False,
                'An incomplete draft must use the explicit private-draft status')
    require(is_draft or receipt.get('status') in
            ('private-saved', 'private-saved-settings-pending', 'private-upload-complete'),
            'Private save is not yet confirmed in the actual UI receipt')
    require(receipt.get('visibility') == 'private', 'Only observed private visibility can be recorded')
    require(receipt.get('scheduled') is not True and not receipt.get('scheduleAt'),
            'Scheduling is outside this upload scope')
    observed_at = receipt.get('observedAt') or receipt.get('privateSavedAt')
    require(isinstance(observed_at, str), 'Actual UI observation timestamp is required')
    datetime.fromisoformat(observed_at.replace('Z', '+00:00'))
    require(receipt.get('url') in (f'https://youtu.be/{video_id}', f'https://www.youtube.com/watch?v={video_id}'),
            'Observed URL must match the saved video ID')
    source = receipt.get('sourceMaster', {})
    require(source.get('sha256') == MASTER_SHA, 'Upload source SHA must be the accepted final master')
    source_path = repo_path(source.get('path', ''))
    expected = repo_path(PROJECT / 'production/local/reference-preserving-v2/edit/coaching-silent-v3/delivery/output/similar-game-design/similar-game-design.captioned.mp4')
    require(source_path == expected and source_path.is_file(), 'Upload source must be the current collected master')
    require(not hash_master or sha(source_path) == MASTER_SHA, 'Actual source master hash changed')
    if 'bytes' in source:
        require(source['bytes'] == source_path.stat().st_size, 'Source master byte size changed')
    authorization = receipt.get('userAuthorization', {})
    require(bool(authorization.get('message')) and authorization.get('acceptedDeliveredVersion') is True
            and authorization.get('masterSha256') == MASTER_SHA,
            'Actual user upload authorization must bind this delivered master')
    require(authorization.get('actualWholeListeningClaimed') is not True,
            'This bounded helper must not infer whole listening from upload authorization')
    baseline = receipt.get('baseline', {})
    require(baseline.get('videoId') == BASELINE and baseline.get('preserved') is True,
            'Existing private baseline preservation must be recorded')
    require(isinstance(receipt.get('observedMetadata', {}), dict), 'Observed metadata must be an object')
    # UI captures can be external tool-returned files. They are read-only evidence:
    # this helper never writes to their paths or treats a missing capture as viewed.
    screenshots = []
    for item in receipt.get('screenshotPaths', []):
        value = item['path'] if isinstance(item, dict) else item
        path = Path(value)
        path = path if path.is_absolute() else ROOT / path
        require(path.is_file(), f'UI evidence capture is absent: {value}')
        digest = sha(path)
        if isinstance(item, dict) and item.get('sha256'):
            require(digest == item['sha256'], 'UI evidence capture hash mismatch')
        screenshots.append({'path': value, 'sha256': digest, 'bytes': path.stat().st_size})
    return video_id, observed_at, screenshots


def make_updates(receipt, receipt_hash, snapshots):
    video_id, observed_at, screenshots = validate_receipt(receipt)
    now = datetime.now(timezone.utc).isoformat()
    url = receipt['url']
    is_draft = receipt.get('status') == DRAFT_STATUS
    stage = 'youtube-private-draft' if is_draft else 'youtube-private-saved'
    receipt_relative = relative(RECEIPT)
    receipt_artifact = {'path': receipt_relative, 'sha256': receipt_hash,
                        'bytes': RECEIPT.stat().st_size}
    review = {'status': 'user-authorized-upload-of-delivered-version',
              'userMessage': receipt['userAuthorization']['message'],
              'masterSha256': MASTER_SHA, 'authorizationObservedAt': observed_at,
              'wholeListening': False, 'actualWholeViewingVerified': False,
              'requiredBeforeYouTube': False,
              'basis': 'Actual user accepted this delivered version and requested upload; no full-listening claim inferred.'}
    platform = {'videoId': video_id, 'url': url, 'privacy': 'private',
                'uploaded': True, 'privateSaveVerified': not is_draft,
                'privateUploadComplete': not is_draft, 'autoSaved': True,
                'draft': is_draft, 'wizardComplete': not is_draft, 'observedAt': observed_at,
                'receipt': receipt_artifact, 'observedMetadata': deepcopy(receipt.get('observedMetadata', {})),
                'screenshotEvidence': screenshots,
                'baselineVideoId': BASELINE, 'baselinePreserved': True,
                'scheduled': False, 'automaticNextVideo': False}
    # Missing settings remain absent/pending; private save is not full settings QA.
    full_settings = not is_draft and receipt.get('fullSettingsVerified') is True
    if full_settings:
        require(bool(receipt.get('settingsVerificationEvidence')),
                'Full settings verification requires explicit observed evidence')
        platform['settingsVerificationEvidence'] = deepcopy(receipt['settingsVerificationEvidence'])
    platform['fullSettingsVerified'] = full_settings
    if 'pending' in receipt:
        platform['pending'] = deepcopy(receipt['pending'])
    if is_draft:
        platform['pending'] = list(dict.fromkeys([
            *platform.get('pending', []), 'human-ad-suitability-evaluation', 'final-private-wizard-save']))
        platform['scopeNote'] = 'File uploaded and autosaved privately; Studio still identifies a draft. The user must evaluate ads and complete final private save.'
    if 'adSuitability' in receipt:
        platform['adSuitability'] = deepcopy(receipt['adSuitability'])

    updates = {path: deepcopy(data) for path, data in snapshots.items()}
    manifest = updates[PROJECT / 'project.json']
    require(manifest['currentRevision']['id'] == REVISION and manifest['delivery']['sha256'] == MASTER_SHA,
            'Current project revision/master changed during upload')
    require(manifest['publishing'].get('baselineVideoId') == BASELINE, 'Baseline identity changed')
    old_id = manifest['publishing'].get('videoId')
    require(old_id in (None, BASELINE, video_id), 'Another current upload already exists; do not replace it silently')
    manifest.update(status=REVISION + ('-youtube-private-draft' if is_draft else '-youtube-private-saved'), updatedAt=now)
    manifest['publishing'].update(videoId=video_id, url=url, uploaded=True,
        youtubeUploadAuthorized=True, privacy='private', privateSaveVerified=not is_draft,
        privateUploadComplete=not is_draft, draft=is_draft, wizardComplete=not is_draft,
        receipt=receipt_relative, fullSettingsVerified=full_settings, scheduled=False,
        currentUpload=platform)
    manifest['paths']['publishingReceipt'] = receipt_relative
    manifest['currentRevision'].update(status=stage, youtubeAuthorized=True,
        privateUploadComplete=not is_draft, draft=is_draft,
        humanFinalReview=review['status'], uploadReceipt=receipt_relative, videoId=video_id)
    manifest['delivery'].update(humanReview=review['status'], youtubeUploadAuthorized=True)
    manifest['approvals']['uploaded'] = True
    manifest['approvals']['finalUserUploadAuthorization'] = deepcopy(review)
    # These retain their technical/sample qualifications and do not imply listening.
    manifest['publishing']['requiredBeforeYouTube'] = 'Satisfied by actual user acceptance/upload request for this exact delivered SHA; whole listening remains unverified.'

    checkpoint = updates[HERE / 'checkpoint.json']
    require(checkpoint['revision'] == REVISION, 'Current checkpoint revision changed')
    checkpoint.update(stage=stage, status=DRAFT_STATUS if is_draft else 'private-upload-recorded', updatedAt=now,
        videoId=video_id, url=url, uploaded=True, uploadReceipt=receipt_relative,
        privateUploadComplete=not is_draft, draft=is_draft, wizardComplete=not is_draft,
        humanFinalReview=review['status'], wholeListening=False,
        currentUploadAuthorization=deepcopy(receipt['userAuthorization']),
        localDelivery=deepcopy(manifest['delivery']), platform=deepcopy(platform),
        nextAction=('File uploaded and autosaved privately as a draft. User ad-suitability evaluation and final private wizard save remain pending. Preserve baseline; no scheduling, deletion or next video.' if is_draft else
                    'Private upload saved. Preserve original baseline; retain explicitly pending settings/human listening. No scheduling, deletion or next video.'))

    ledger = updates[HERE / 'review-ledger.json']
    require(ledger['revision'] == REVISION and ledger['master']['sha256'] == MASTER_SHA,
            'Review ledger does not identify this accepted master')
    ledger.update(status='user-authorized-private-draft-uploaded' if is_draft else 'user-authorized-private-upload-saved', recordedAt=now,
        privateUploadComplete=not is_draft, draft=is_draft,
        humanFinalReview=review, youtubeMutation=True, platform=deepcopy(platform),
        uploadAuthorization=deepcopy(receipt['userAuthorization']), uploadReceipt=receipt_artifact)

    work_path = ROOT / 'shared/publishing/video-worklist.json'
    work = updates[work_path]
    rows = [row for row in work['rows'] if row.get('id') == 'D22']
    require(len(rows) == 1 and rows[0].get('slug') == SLUG, 'Exactly the D22 row must be present')
    row = rows[0]
    row.update(videoId=video_id, url=url, platformStatus=('비공개 임시본 · 사용자 광고평가·최종저장 대기' if is_draft else '수정본 비공개 저장 확인'),
        baselineVideoId=BASELINE, baselineUrl=f'https://youtu.be/{BASELINE}', baselinePreserved=True,
        humanApproval='이 수정본 업로드 요청 확인 · 전체 청취 여부 미확인',
        reviewStatus='수정본 업로드 승인 · 기술·표본 검수 완료 · 전체 청취 미확인',
        executionStatus=('파일 업로드·비공개 자동저장 · 임시본 상태 확인' if is_draft else '수정본 비공개 저장 · 실제 UI 확인 항목만 기록'),
        platformEvidence=receipt_relative)
    row['currentRevision'].update(id=REVISION, status=stage,
        uploaded=True, privateUploadComplete=not is_draft, draft=is_draft,
        humanFinalReview=review['status'], youtubeUploadAuthorized=True,
        videoId=video_id, uploadReceipt=receipt_relative, localDelivery=deepcopy(manifest['delivery']))
    row['notes'] = (('마지막 코칭 광고 발화·자막 제거본을 사용자 요청에 따라 업로드하고 비공개 임시본으로 자동저장. 사용자 광고평가와 최종저장 대기. ' if is_draft else
                     '마지막 코칭 광고 발화·자막 제거본을 사용자 요청에 따라 새 비공개 영상으로 저장. ')
                  +
                    '교육 내용·음악·끝페이지/링크·4분50초 유지. 원본 _p1IqDeg6YE 보존. 전체 청취 미확인; 예약·삭제·다음 영상 없음.')
    evidence = row.setdefault('evidence', [])
    if receipt_relative not in evidence:
        evidence.append(receipt_relative)
    old_other = deepcopy(snapshots[work_path]); new_other = deepcopy(work)
    old_other['rows'] = [r for r in old_other['rows'] if r.get('id') != 'D22']
    new_other['rows'] = [r for r in new_other['rows'] if r.get('id') != 'D22']
    require(old_other == new_other, 'Worklist mutation escaped the D22 row')

    control_path = ROOT / 'shared/publishing/video-production-control.json'
    control = updates[control_path]
    scoped = control['scopedProductionAuthorizations'][SLUG]
    scoped.update(revision=REVISION, privateUploadAuthorized=True,
        status='coaching-silent-v3-private-draft' if is_draft else 'coaching-silent-v3-private-saved',
        privateUploadComplete=not is_draft, draft=is_draft, humanFinalReview=review['status'],
        localDelivery=deepcopy(manifest['delivery']), currentUploadAuthorization=deepcopy(receipt['userAuthorization']),
        actualUpload=deepcopy(platform))
    old_other = deepcopy(snapshots[control_path]); new_other = deepcopy(control)
    del old_other['scopedProductionAuthorizations'][SLUG]
    del new_other['scopedProductionAuthorizations'][SLUG]
    require(old_other == new_other, 'Control mutation escaped the current D22 scoped authorization')
    require(scoped.get('automaticNextVideo') is False and scoped.get('deleteAuthorized') is False
            and scoped.get('scheduleAuthorized') is False and scoped.get('driveAuthorized') is False,
            'Explicit platform/next-video boundaries changed')
    return updates, platform


def update_worklist_doc(text, url, draft=False):
    lines = text.splitlines(keepends=True)
    for index, line in enumerate(lines):
        end = '\r\n' if line.endswith('\r\n') else '\n'
        if '| 게임디자인 | D22 [' in line:
            cells = line.split('|')
            cells[3] = f' D22 [비슷한 게임을 고를 이유]({url}) '
            cells[4] = ' 코칭 음성 제거본 · 비공개 임시본 ' if draft else ' 코칭 음성 제거본 · 비공개 저장 '
            cells[5] = ' 업로드 요청 확인 · 전체 청취 미확인 '
            lines[index] = '|'.join(cells).rstrip('\r\n') + end
        elif line.startswith('| D22 |'):
            platform_text = '비공개 임시본 · 사용자 광고평가·최종저장 대기' if draft else '새 비공개본 저장 · 기존 비공개본 보존'
            lines[index] = f'| D22 | [비슷한 게임을 고를 이유]({url}) | 코칭 음성 제거본 완성 | 수정본 업로드 요청 확인 · 전체 청취 미확인 | {platform_text} |' + end
        elif line.startswith('| D22 '):
            platform_text = '비공개 임시본 업로드·자동저장. 사용자 광고평가·최종저장 대기.' if draft else '비공개 저장.'
            lines[index] = f'| D22 비슷한 게임을 고를 이유 | 마지막 코칭 광고 음성·말자막 제거본 {platform_text} 1080p60·4분50초·교육 결론·끝페이지/링크 유지. 기존 비공개본 보존. |' + end
    return ''.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--receipt', default=relative(RECEIPT))
    parser.add_argument('--apply', action='store_true', help='Write only the validated D22 metadata records')
    args = parser.parse_args()
    receipt_path = repo_path(args.receipt)
    require(receipt_path == RECEIPT, 'Only the exact current upload receipt is accepted')
    tracked = [PROJECT / 'project.json', HERE / 'checkpoint.json', HERE / 'review-ledger.json',
               ROOT / 'shared/publishing/video-worklist.json', ROOT / 'shared/publishing/video-production-control.json']
    originals = {path: path.read_bytes() for path in tracked}
    receipt_bytes = RECEIPT.read_bytes()
    receipt = json.loads(receipt_bytes.decode('utf-8-sig'))
    snapshots = {path: json.loads(raw.decode('utf-8-sig')) for path, raw in originals.items()}
    updates, platform = make_updates(receipt, hashlib.sha256(receipt_bytes).hexdigest(), snapshots)
    outputs = {path: (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
               for path, value in updates.items()}
    doc_path = ROOT / 'docs/VIDEO_WORKLIST.md'
    originals[doc_path] = doc_path.read_bytes()
    outputs[doc_path] = update_worklist_doc(originals[doc_path].decode('utf-8-sig'), receipt['url'], platform['draft']).encode('utf-8')
    summary = {'mode': 'apply' if args.apply else 'dry-run', 'videoId': platform['videoId'],
               'privacy': platform['privacy'], 'sourceSha256': MASTER_SHA,
               'wholeListening': False, 'baselinePreserved': True,
               'uploaded': True, 'draft': platform['draft'],
               'privateUploadComplete': platform['privateUploadComplete'],
               'fullSettingsVerified': platform['fullSettingsVerified'],
               'writes': [relative(path) for path in outputs],
               'platformActions': 0, 'mediaJobs': 0, 'gitActions': 0}
    if args.apply:
        require(RECEIPT.read_bytes() == receipt_bytes, 'Receipt changed while preparing records; retry')
        for path, original in originals.items():
            require(path.read_bytes() == original, f'Concurrent metadata change; retry instead of overwriting: {path}')
        for path, output in outputs.items():
            temp = path.with_name(path.name + '.d22-' + uuid.uuid4().hex + '.tmp')
            temp.write_bytes(output)
            os.replace(temp, path)
        report = HERE / 'youtube-record-finalization-coaching-v3.json'
        report.write_text(json.dumps({'schemaVersion': 1, 'recordedAt': datetime.now(timezone.utc).isoformat(),
            **summary, 'receipt': {'path': relative(RECEIPT), 'sha256': sha(RECEIPT)},
            'after': {relative(path): sha(path) for path in outputs}}, ensure_ascii=False, indent=2) + '\n', 'utf-8')
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
