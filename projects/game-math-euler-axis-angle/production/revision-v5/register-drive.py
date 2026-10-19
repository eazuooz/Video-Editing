"""Record observed V5 full-master Drive delivery; never upload/delete/publish.

After register-local.py and the collector, root supplies three existing files:
  local/revision-v5/drive-provider-metadata.json
  local/revision-v5/drive-provider-revisions.json
  local/revision-v5/drive-review-observation.json
The last file binds actual upload/access/playback observations to fileId and
localSha256. Processing is a valid honest delivery state, never human approval.
"""
from pathlib import Path
import argparse
import copy
import datetime
import hashlib
import json
import os
import subprocess
import sys

R = Path(__file__).resolve().parents[4]
P = R / 'projects/game-math-euler-axis-angle'
H = Path(__file__).resolve().parent
O = P / 'production/local/revision-v5'
B = P / 'production/local/revision-v4-clarity'
REVISION = 'tracked-gizmos-code-colors-v5'
CONTROL = R / 'shared/publishing/video-production-control.json'
WORKLIST = R / 'shared/publishing/video-worklist.json'


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def save(path, value):
    temporary = path.with_name(path.name + '.register-v5.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    os.replace(temporary, path)


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def rel(path):
    return path.relative_to(R).as_posix()


def project_rel(path):
    return path.relative_to(P).as_posix()


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def selected():
    value = read(CONTROL)
    require(value['selectedVideo'] == P.name, 'Selected video changed; no delivery registration.')
    return value


def unwrap(value, required_key):
    """Accept saved connector structuredContent or its plain decoded payload."""
    if isinstance(value, dict) and required_key in value:
        return value
    if isinstance(value, dict):
        for key in ('structuredContent', 'data', 'result'):
            nested = value.get(key)
            if isinstance(nested, dict):
                try:
                    return unwrap(nested, required_key)
                except ValueError:
                    pass
        for block in value.get('content', []):
            if isinstance(block, dict) and block.get('type') == 'text':
                try:
                    return unwrap(json.loads(block['text']), required_key)
                except (ValueError, TypeError, KeyError):
                    pass
    raise ValueError(f'Provider payload missing {required_key!r}.')


def build_receipt(metadata_path, revisions_path, observation_path):
    selected()
    metadata = unwrap(read(metadata_path), 'id')
    revisions = unwrap(read(revisions_path), 'revisions')
    observed = read(observation_path)
    pair = read(O / 'pair-source.json')
    qa = read(P / 'production/qa.json')
    project = read(P / 'project.json')
    integrity = read(O / 'qa/integrity.json')
    delivery = read(P / 'production/delivery-output.json')
    require(qa['revision'] == integrity['revision'] == observed['revision'] == REVISION, 'V5 registration/QA/observation revision mismatch.')
    require(project['revision']['id'] == REVISION, 'Register current V5 local pair first.')
    for key, name in (('audioMix', 'final-mix.m4a'), ('editorAudioMix', 'final-mix.wav'),
                      ('captionsKo', 'captions.ko.srt'), ('captionsEn', 'captions.en.srt')):
        retained = qa['retainedInputs'][key]
        require(project['paths'][key] == retained['file'] == rel(B / name), 'Retained audio/subtitle path changed.')
        require(sha(R / retained['file']) == retained['sha256'], 'Retained audio/subtitle file changed.')
    require(qa['evidence']['integrity']['sha256'] == sha(O / 'qa/integrity.json'), 'Registered integrity changed.')
    current = pair['outputs']['captioned']
    require(observed['localSha256'] == current['sha256'], 'Observation refers to a different master.')
    captioned = next(x for x in delivery['files'] if x['name'] == P.name + '.captioned.mp4')
    require(captioned['sha256'] == current['sha256'] and captioned['source'] == current['file'], 'Collect the current V5 pair before Drive registration.')
    collected = R / delivery['directory'] / captioned['name']
    require(collected.is_file() and collected.stat().st_size == captioned['bytes'], 'Collected upload source absent or byte count changed.')
    require(sha(collected) == current['sha256'], 'Collected file hash differs from exact reviewed master.')
    expected = next(x for x in integrity['outputs'] if x['kind'] == 'captioned')
    require(expected['sha256'] == current['sha256'] and expected['fullDecodePassed'] is True
            and expected['ptsMonotonicAndUniform'] is True, 'Current complete pair integrity absent.')
    require((expected['width'], expected['height'], expected['frames'], float(expected['fps'])) == (1920, 1080, 93100, 60), 'Publishing source must be full FHD60 master.')
    require(observed['uploadComplete'] is True and bool(observed['uploadMethod'])
            and bool(observed['observedAt']), 'Actual complete upload observation missing.')
    file_id = str(metadata['id'])
    require(file_id == observed['fileId'] == revisions['fileId'], 'Provider IDs do not match observed upload.')
    remote_bytes = int(metadata['size'])
    require(remote_bytes == captioned['bytes'], 'Remote is not the complete exact-byte-count master.')
    revision_id = revisions.get('currentRevisionId') or metadata.get('headRevisionId')
    require(bool(revision_id), 'Actual current Drive revision ID was not returned.')
    version = next((x for x in revisions['revisions'] if x['id'] == revision_id), None)
    require(version is not None, 'Current Drive revision absent from actual revisions list.')
    if version.get('size') is not None:
        require(int(version['size']) == remote_bytes, 'Drive revision byte count mismatch.')
    require(metadata.get('mime_type', metadata.get('mimeType')) == 'video/mp4', 'Remote file is not MP4.')
    url = metadata.get('url') or metadata.get('webViewLink') or metadata.get('display_url')
    require(bool(url) and file_id in url, 'Provider did not return the actual file URL.')
    access = copy.deepcopy(observed['access'])
    require(access['visibility'] == 'restricted' and access['changed'] is False
            and bool(access['verifiedBy']), 'Existing restricted access must be observed and preserved.')
    permissions = metadata.get('permissions')
    require(isinstance(permissions, list) and permissions, 'Provider permission metadata unavailable.')
    require(all(x.get('type') not in ('anyone', 'domain') for x in permissions), 'Remote permissions are not restricted.')
    # Do not copy private account identifiers into the tracked delivery receipt.
    access['permissions'] = [{key: x[key] for key in ('type', 'role') if key in x} for x in permissions]
    playback = copy.deepcopy(observed['playback'])
    require(playback['status'] in ('processing', 'verified', 'unverified'), 'Unrecognized playback state.')
    require(playback['directLinkReopened'] is True and bool(playback['verificationScope']), 'Direct Drive access/playback observation missing.')
    if playback['status'] == 'verified':
        times = playback.get('observedPlayingSeconds', [])
        require(len({float(x) for x in times}) >= 2 and playback.get('leftPaused') is True,
                'Verified playback requires observed advancing time and a paused final player.')
    playback.setdefault('streamFpsVerified', False)
    remote_sha = metadata.get('sha256Checksum') or metadata.get('sha256_checksum')
    if remote_sha is not None:
        require(remote_sha == current['sha256'], 'Returned remote SHA256 differs from the reviewed master.')
    proof = copy.deepcopy(observed.get('proof', {}))
    proof.update(metadata=project_rel(metadata_path), metadataSha256=sha(metadata_path),
        revision=project_rel(revisions_path), revisionSha256=sha(revisions_path),
        observations=project_rel(observation_path), observationsSha256=sha(observation_path))
    return dict(schemaVersion=5, slug=P.name, revision=REVISION, label=REVISION,
        status=('uploaded-playback-verified-awaiting-human-review' if playback['status'] == 'verified'
                else 'uploaded-playback-processing-human-review-pending' if playback['status'] == 'processing'
                else 'uploaded-playback-unverified-human-review-pending'),
        fileId=file_id, url=url, name=metadata.get('title', metadata.get('name')),
        driveRevisionId=revision_id, driveRevisionStatus='observed-revisions-list',
        createdTime=metadata.get('created_time', metadata.get('createdTime')),
        modifiedTime=metadata.get('modified_time', metadata.get('modifiedTime')),
        remoteBytes=remote_bytes, localMaster=(Path(delivery['directory']) / captioned['name']).as_posix(),
        localSha256=current['sha256'], remoteSha256=remote_sha,
        checksumNote=('Provider SHA256 equals the independently hashed complete captioned upload source.'
            if remote_sha else 'Provider exposes size and revision identity but no remote SHA256. Exact full-master upload source hash recorded; remote checksum equality is not claimed.'),
        dimensions=[1920, 1080], masterFps=60, frames=93100, durationSeconds=93100 / 60,
        uploadMethod=observed['uploadMethod'], access=access, playback=playback, proof=proof,
        humanReview={'status': 'pending', 'reviewedSha256': None, 'wholeListening': 'pending',
            'remaining': 'User review of this exact complete V5 version, whole listening and subjective term pronunciation.'},
        youtube={'uploaded': False, 'uploadAuthorized': False, 'previousPrivateVideoId': 'iv9esV7vv_g',
            'previousPrivateVideoUnchanged': True},
        preservedEarlierVersions=True,
        dimensionVerification='Current complete master full decode/PTS: native1920x1080/60,93100frames. Same SHA256 collected upload source; Drive streaming FPS not inferred from local master.',
        observedAt=observed['observedAt'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--metadata', type=Path, default=O / 'drive-provider-metadata.json')
    parser.add_argument('--revisions', type=Path, default=O / 'drive-provider-revisions.json')
    parser.add_argument('--observations', type=Path, default=O / 'drive-review-observation.json')
    args = parser.parse_args()
    metadata_path, revisions_path, observation_path = (x.resolve() for x in (args.metadata, args.revisions, args.observations))
    for path in (metadata_path, revisions_path, observation_path):
        require(path.is_relative_to(O.resolve()), 'Keep observed provider artifacts under the selected V5 local folder.')
    incoming = build_receipt(metadata_path, revisions_path, observation_path)
    selected()
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    receipt_path = P / 'publishing/drive-review.json'
    old = read(receipt_path)
    same_version = (old.get('fileId'), old.get('driveRevisionId'), old.get('localSha256')) == (
        incoming['fileId'], incoming['driveRevisionId'], incoming['localSha256'])
    incoming['previousVersions'] = copy.deepcopy(old.get('previousVersions', [])) if same_version else [old]
    incoming['recordedAt'] = now
    ready = incoming['playback']['status'] == 'verified'
    stage = ('awaiting-human-drive-final-review' if ready
        else 'drive-upload-complete-playback-processing' if incoming['playback']['status'] == 'processing'
        else 'drive-upload-complete-playback-unverified')
    project = read(P / 'project.json')
    require(project['revision']['id'] == REVISION, 'Register current V5 local pair first.')
    project.update(status=stage, publishReady=False)
    project['publishing'].update(driveReview=rel(receipt_path), driveFileId=incoming['fileId'],
        driveUrl=incoming['url'], driveRevisionId=incoming['driveRevisionId'],
        driveMasterSha256=incoming['localSha256'], currentRevision=REVISION,
        youtubeReplacementAuthorized=False)
    project['publishing'].pop('pendingDriveRevision', None)
    project['revision']['nextRevision'] = {'id': REVISION, 'stage': stage}
    project['finalRender']['openItems'] = ['현재 V5 전체 Drive 버전 사용자 최종 검수 및 전체 청취·발음 확인 대기',
        '기존 모든 Drive와 비공개 YouTube 유지']
    if not ready:
        project['finalRender']['openItems'].insert(0, 'Drive 실제 재생 확인 대기; 업로드 원본은1920×1080/60fps 전체 마스터')
    elif incoming['playback'].get('highDefinitionProcessing') == 'pending':
        project['finalRender']['openItems'].insert(0, 'Drive1080p 미리보기 변환 대기; 업로드 원본은1920×1080/60fps')
    checkpoint = read(P / 'production/checkpoint.json')
    checkpoint.update(updatedAt=now, revision=REVISION, stage=stage, runningJob=None,
        nextAction='Wait for user review of the exact complete V5 Drive version; no YouTube or next video.')
    checkpoint['delivery'].update(newFinalVideoExists=True, fourOutputs='production/delivery-output.json',
        driveUploaded=True, driveReceipt='publishing/drive-review.json', fileId=incoming['fileId'],
        url=incoming['url'], driveRevisionId=incoming['driveRevisionId'],
        masterSha256=incoming['localSha256'], playback=incoming['playback']['status'],
        humanReview='pending', youtubeBaselinePreserved=True)
    checkpoint['delivery'].pop('pendingRevision', None)
    checkpoint['delivery'].pop('pendingMasterSha256', None)
    qa = read(P / 'production/qa.json')
    qa.update(drive='publishing/drive-review.json', driveMasterSha256=incoming['localSha256'],
        drivePlayback=incoming['playback']['status'], humanWholeListening='pending',
        status='changed-visual-and-technical-checks-complete-exact-V4-audio-reused-human-review-pending')
    ledger = read(P / 'production/review-ledger.json')
    ledger.update(updatedAt=now, currentOutput=qa, currentDriveReview=incoming, humanWholeListening='pending')
    plan = read(P / 'planning/production-plan.json')
    plan.update(updatedAt=now, revision=REVISION, status=stage)
    plan['selectedRevision'].update(id=REVISION, stage=stage)
    plan['currentProduction'].update(driveReview='publishing/drive-review.json',
        humanWholeListening='pending exact complete V5 Drive version')
    for path, value in ((receipt_path, incoming), (P / 'project.json', project),
                        (P / 'production/checkpoint.json', checkpoint), (P / 'production/qa.json', qa),
                        (P / 'production/review-ledger.json', ledger),
                        (P / 'planning/production-plan.json', plan)):
        save(path, value)
    selected()
    work = read(WORKLIST)
    row = next(x for x in work['rows'] if x['slug'] == P.name)
    require(row['id'] == 'M04', 'Wrong worklist row.')
    row.update(productionComplete=True, localMasterAvailable=True,
        productionStatus='V5 회전 기즈모·코드 색상 수정 완료 / 기존 음성·게임 원음 유지',
        reviewStatus='변경 화면·연결·FHD60 기술검수 완료 / 전체 청취·발음 검수 대기',
        humanApproval='현재 V5 전체 Drive 완성본 사용자 검수 대기',
        platformStatus='새 V5 전체 마스터 Drive 업로드 완료 · 이전 Drive와 비공개 YouTube 유지',
        executionStatus='사용자 최종 검수 대기' if ready else 'Drive 실제 재생 확인 대기',
        latestRulesPassed=None)
    row.pop('pendingDriveRevision', None)
    row['driveReview'] = dict(receipt='publishing/drive-review.json',
        **{key: incoming[key] for key in ('fileId', 'url', 'driveRevisionId', 'localSha256',
            'remoteSha256', 'remoteBytes', 'access', 'playback', 'humanReview')},
        readyForHumanReview=ready)
    row['notes'] = 'V5는 네 회전 안내 기즈모와15·25 코드/설명 색상만 수정. 음성·게임 원음·한영 자막·시간은 V4와 동일. 전체 FHD60 마스터를 Drive에 업로드; 이전 Drive와 비공개 YouTube 보존. 사용자 검수·전체 청취 대기.'
    work['updatedAt'] = now
    save(WORKLIST, work)
    control = selected()
    control['selectedDelivery'].update(revision=REVISION, stage=stage,
        driveReview=rel(receipt_path), driveId=incoming['fileId'],
        driveRevisionId=incoming['driveRevisionId'], masterSha256=incoming['localSha256'],
        userReview='pending exact V5 complete version', youtubeUploadAuthorized=False,
        completedAt=now)
    control['selectedDelivery'].pop('pendingDriveRevision', None)
    control['selectedDelivery'].pop('nextRevision', None)
    control['updatedAt'] = now
    save(CONTROL, control)
    subprocess.run([sys.executable, str(R / 'scripts/render-video-worklist.py')], cwd=R, check=True)
    print(f'{REVISION}: {stage}; current Drive ID {incoming["fileId"]}; human review pending.')


if __name__ == '__main__':
    main()
