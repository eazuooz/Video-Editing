"""Root-run D22 BGM-only metadata binding: bind, record, optional upload.

No media, network, Studio or Git actions. Only the selected D22 records and its
worklist rows/scoped control may change. Prior media and upload receipts remain.
Default is dry-run; --apply performs the validated metadata writes.
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
from storage_paths import repo_path, relative, local_output

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PROJECT = ROOT / 'projects/similar-game-design'
SLUG = 'similar-game-design'
REVISION = 'bgm-restored-v4'
BASE_REVISION = 'coaching-silent-v3'
OLDEST = '_p1IqDeg6YE'
SUPERSEDED = 'YHpnG3kGcQ4'
USER_REQUEST = '재렌더해서 기존거 내리고 다시 업로드해줘'
PLAN_FILE = HERE / 'edit-plan-bgm-restored-v4.json'
UPLOAD_RECEIPT = PROJECT / 'publishing/reference-preserving-v2/youtube-upload-bgm-restored-v4.json'


def require(test, message):
    if not test:
        raise ValueError(message)


def read(path):
    return json.loads(path.read_text('utf-8-sig'))


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def artifact(path):
    return {'path': relative(path), 'sha256': sha(path), 'bytes': path.stat().st_size}


def encoded(data):
    return (json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def check_report(path, structural=False):
    data = read(path)
    status = str(data.get('status', '')).lower()
    require(not any(word in status for word in ['fail', 'error', 'pending']),
            f'Current verification is not complete: {path}: {status}')
    if structural:
        require(status == 'pass', 'Current structural verification must explicitly pass')
    return data


def shared_scope(before, after, work, control):
    old, new = deepcopy(before[work]), deepcopy(after[work])
    old['rows'] = [r for r in old['rows'] if r.get('id') != 'D22']
    new['rows'] = [r for r in new['rows'] if r.get('id') != 'D22']
    require(old == new, 'Mutation escaped the D22 worklist row')
    old, new = deepcopy(before[control]), deepcopy(after[control])
    del old['scopedProductionAuthorizations'][SLUG]
    del new['scopedProductionAuthorizations'][SLUG]
    require(old == new, 'Mutation escaped the D22 scoped control entry')


def doc_lines(text, row):
    lines = text.splitlines(keepends=True)
    label = row.get('url', f'https://youtu.be/{SUPERSEDED}')
    for n, line in enumerate(lines):
        end = '\r\n' if line.endswith('\r\n') else '\n'
        if '| 게임디자인 | D22 [' in line:
            cells = line.split('|')
            cells[3] = f' D22 [비슷한 게임을 고를 이유]({label}) '
            cells[4] = ' 원래 Nimbus BGM 복구 · 1080p60 '
            cells[5] = ' 기술 검사 기록 · 새 오디오 전체 청취 미확인 '
            lines[n] = '|'.join(cells).rstrip('\r\n') + end
        elif line.startswith('| D22 |'):
            lines[n] = f'| D22 | [비슷한 게임을 고를 이유]({label}) | 원래 Nimbus BGM 복구본 | 새 오디오 전체 청취 미확인 | {row["platformStatus"]} |' + end
        elif line.startswith('| D22 '):
            lines[n] = '| D22 비슷한 게임을 고를 이유 | 원래 Nimbus BGM만 가청 수준으로 복구. 영상·TTS·104쌍 자막·끝페이지 유지. 사용자 요청에 따른 교체 업로드 범위; 실제 전체 청취·플랫폼 완료는 별도 관찰 기록. |' + end
    return ''.join(lines)


def upload_state(receipt, manifest):
    require(receipt.get('slug') == SLUG and receipt.get('revision') == REVISION,
            'Actual upload receipt must identify this BGM-restored revision')
    video_id = receipt.get('videoId', '')
    require(re.fullmatch(r'[A-Za-z0-9_-]{11}', video_id) and video_id not in [OLDEST, SUPERSEDED],
            'A new actually observed replacement video ID is required')
    require(receipt.get('visibility') == 'private', 'Only private upload observations are in scope')
    require(receipt.get('url') in [f'https://youtu.be/{video_id}', f'https://www.youtube.com/watch?v={video_id}'],
            'Observed upload URL/ID mismatch')
    require(receipt.get('scheduled') is not True and not receipt.get('scheduleAt'), 'No scheduling authorized')
    source = receipt['sourceMaster']
    require(source['sha256'] == manifest['delivery']['sha256']
            and repo_path(source['path']) == repo_path(manifest['delivery']['captioned']),
            'Actual uploaded source must match the current collected master')
    require(sha(repo_path(source['path'])) == source['sha256'], 'Uploaded source master changed')
    user = receipt.get('userAuthorization', {})
    require(bool(user.get('message')) and user.get('masterSha256') == source['sha256']
            and user.get('actualWholeListeningClaimed') is not True,
            'Actual reupload authorization must bind this version without a listening claim')
    when = receipt.get('observedAt')
    require(isinstance(when, str), 'Actual observation timestamp is required')
    datetime.fromisoformat(when.replace('Z', '+00:00'))
    draft = receipt.get('draft') is True
    if draft:
        require(receipt.get('status') == 'private-draft-uploaded-human-ads-pending'
                and receipt.get('saved') is True and receipt.get('wizardComplete') is False,
                'Autosaved draft must remain explicitly incomplete')
        ads = receipt.get('adSuitability', {})
        require(ads.get('owner') == 'human user' and ads.get('submittedByAgent') is False,
                'User-owned advertising self-assessment must remain unsubmitted')
        require(receipt.get('privateUploadComplete') is not True and receipt.get('fullSettingsVerified') is not True,
                'Draft cannot imply final private save or complete settings')
    else:
        require(receipt.get('saved') is True and receipt.get('wizardComplete') is True
                and receipt.get('privateUploadComplete') is True,
                'Final private completion needs explicit actual save/wizard evidence')
    full_settings = not draft and receipt.get('fullSettingsVerified') is True
    if full_settings:
        require(bool(receipt.get('settingsVerificationEvidence')), 'Full settings need observed evidence')
    shots = []
    for item in receipt.get('screenshotPaths', []):
        value = item['path'] if isinstance(item, dict) else item
        file = Path(value)
        file = file if file.is_absolute() else ROOT / file
        require(file.is_file(), 'Actual UI capture missing: ' + value)
        digest = sha(file)
        if isinstance(item, dict) and item.get('sha256'):
            require(digest == item['sha256'], 'Actual UI capture hash mismatch')
        shots.append({'path': value, 'sha256': digest, 'bytes': file.stat().st_size})
    # Taking the old upload down is recorded ONLY if the root observed it. No
    # action is requested/performed by this metadata helper.
    old_state = deepcopy(receipt.get('supersededVideoObservation', {
        'videoId': SUPERSEDED, 'withdrawalObserved': False, 'status': 'not-recorded'}))
    require(old_state.get('videoId') == SUPERSEDED, 'Only the specifically superseded upload is in replacement scope')
    return {'videoId': video_id, 'url': receipt['url'], 'observedAt': when,
            'uploaded': True, 'privacy': 'private', 'autoSaved': receipt.get('saved') is True,
            'draft': draft, 'wizardComplete': not draft, 'privateUploadComplete': not draft,
            'privateSaveVerified': not draft, 'fullSettingsVerified': full_settings,
            'receipt': artifact(UPLOAD_RECEIPT), 'observedMetadata': deepcopy(receipt.get('observedMetadata', {})),
            'screenshotEvidence': shots, 'adSuitability': deepcopy(receipt.get('adSuitability', {})),
            'pending': deepcopy(receipt.get('pending', [])), 'supersededVideoObservation': old_state,
            'oldestBaselineVideoId': OLDEST, 'oldestBaselinePreserved': True,
            'scheduled': False, 'automaticNextVideo': False}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('stage', choices=['bind', 'record', 'upload'])
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()
    now = datetime.now(timezone.utc).isoformat()
    plan = read(PLAN_FILE)
    require(plan['totalFrames'] == 17408 and plan['fps'] == 60, 'Original timeline must remain unchanged')
    edit = local_output(plan['outputDir'])
    expected = repo_path(PROJECT / 'production/local/reference-preserving-v2/edit/bgm-restored-v4')
    require(edit == expected, 'Only the exact C-routed BGM revision output is permitted')
    structural_file = edit / 'structural-verification.json'
    structural = check_report(structural_file, structural=True)
    require(set(structural['outputs']) == {'clean', 'captioned'}, 'Both current masters must be verified')
    for role, item in structural['outputs'].items():
        require(repo_path(item['path']) == edit / (plan['outputStem'] + '-' + role + '.mp4')
                and sha(repo_path(item['path'])) == item['sha256'], 'Verified master path/hash mismatch')
    correction_file = edit / 'bgm-restoration-verification.json'
    check_report(correction_file)
    asr_file, comparison_file = edit / 'final-mix-asr.json', edit / 'final-mix-text-comparison.json'
    require(asr_file.is_file() and comparison_file.is_file(), 'Current changed-mix ASR/comparison records are required')
    check_report(comparison_file)
    work_file = ROOT / 'shared/publishing/video-worklist.json'
    control_file = ROOT / 'shared/publishing/video-production-control.json'
    paths = [PROJECT / 'project.json', HERE / 'checkpoint.json', HERE / 'review-ledger.json',
             work_file, control_file, PROJECT / 'planning/production-plan.json']
    metadata_file = PROJECT / 'publishing/reference-preserving-v2/metadata-prepared.json'
    chapters_file = PROJECT / 'publishing/reference-preserving-v2/chapters.json'
    if args.stage in ['record', 'upload']:
        paths.extend([metadata_file, chapters_file])
    originals = {p: p.read_bytes() for p in paths}
    before = {p: json.loads(b.decode('utf-8-sig')) for p, b in originals.items()}
    after = deepcopy(before)
    manifest = after[PROJECT / 'project.json']
    require(manifest['currentRevision']['id'] in [BASE_REVISION, REVISION], 'Another project revision became current')
    require(manifest['publishing'].get('baselineVideoId') == OLDEST, 'Oldest original baseline must be preserved')
    request = {'id': REVISION, 'userMessage': USER_REQUEST,
        'recordedAt': now, 'scope': 'Restore original Nimbus BGM only, retain pixels/TTS/captions/timing, take down the specifically superseded upload and reupload the corrected file privately.',
        'actualWholeListeningClaimed': False, 'newTtsAuthorized': False,
        'platformMutationAuthorized': True, 'supersededVideoId': SUPERSEDED,
        'oldestBaselineVideoId': OLDEST, 'oldestBaselinePreserved': True}
    history = manifest.setdefault('revisionHistory', [])
    if not any(x.get('id') == BASE_REVISION for x in history):
        history.append({'id': BASE_REVISION, 'preserved': True,
            'captionedMaster': manifest['paths']['videoBurnedCaptions'],
            'sha256': manifest['delivery']['sha256'], 'videoId': SUPERSEDED,
            'uploadReceipt': 'publishing/reference-preserving-v2/youtube-upload-coaching-silent-v3.json'})
    master = structural['outputs']['captioned']
    upload_authorization = {'status': 'user-directed-bgm-repair-and-reupload',
        'message': USER_REQUEST, 'userMessage': USER_REQUEST, 'masterSha256': master['sha256'],
        'recordedAt': now, 'actualWholeListeningClaimed': False, 'wholeListening': False,
        'actualWholeViewingVerified': False, 'acceptedDeliveredVersion': False,
        'basis': 'Explicit request to repair original BGM and replace the prior upload; no actual review/acceptance of the newly mixed file is inferred.'}
    previous_upload = before[PROJECT / 'project.json']['publishing'].get('currentUpload', {})
    if previous_upload.get('videoId') == SUPERSEDED:
        manifest['publishing']['previousRevisionUpload'] = deepcopy(previous_upload)
    previous_approval = manifest['approvals'].get('finalUserUploadAuthorization', {})
    if previous_approval.get('masterSha256') != master['sha256'] and previous_approval:
        manifest['approvals']['priorVersionFinalUserUploadAuthorization'] = deepcopy(previous_approval)
    manifest['approvals']['finalUserUploadAuthorization'] = deepcopy(upload_authorization)
    unobserved_platform = {'revision': REVISION, 'status': 'replacement-upload-pending',
        'sourceMasterSha256': master['sha256'], 'uploaded': False,
        'videoId': None, 'url': None, 'draft': None, 'wizardComplete': None,
        'autoSaved': False, 'privateUploadComplete': False, 'privateSaveVerified': False,
        'fullSettingsVerified': False, 'wholeListening': False,
        'expectedReceipt': relative(UPLOAD_RECEIPT)}
    delivery = {'localStorageRoot': relative(edit / 'delivery'),
                'sha256': master['sha256'], 'humanReview': 'not-observed-for-this-new-audio',
                'youtubeUploadAuthorized': True}
    manifest.update(status=REVISION + '-local-complete', updatedAt=now)
    manifest['paths'].update(finalPlan=relative(PLAN_FILE), timeline=relative(PLAN_FILE),
        videoClean=structural['outputs']['clean']['path'], videoBurnedCaptions=master['path'],
        audioMix=relative(edit / 'final-mix.wav'),
        captionsKo=relative(edit / 'captions.ko.srt'), captionsEn=relative(edit / 'captions.en.srt'),
        captionKorean=relative(edit / 'captions.ko.srt'), captionEnglish=relative(edit / 'captions.en.srt'),
        captionAlignmentReview=relative(edit / 'caption-alignment.json'),
        finalMixedAsrReview=relative(comparison_file))
    manifest['delivery'] = delivery
    manifest['audio'].update(backgroundMusic='Nimbus — Eveningland; original track restored to audible level',
        bgmRevision=REVISION, narratedCoachingCta=False, ttsRegenerated=False,
        currentBgmVerification=relative(correction_file), currentMixAsr=relative(comparison_file))
    manifest['currentRevision'].update(id=REVISION, status='local-complete', productionComplete=True,
        humanFinalReview='not-observed-for-this-new-audio', youtubeAuthorized=True,
        latestUserRevision=request, automaticNextVideo=False,
        videoId=None, uploadReceipt=None, draft=None, wizardComplete=None)
    manifest['publishing'].update(uploaded=False, youtubeUploadAuthorized=True,
        privateUploadComplete=False, privateSaveVerified=False, fullSettingsVerified=False,
        replacementVideoId=SUPERSEDED, replacementReceipt=relative(UPLOAD_RECEIPT),
        replacementUploadPending=True, automaticNextVideo=False,
        videoId=None, url=None, receipt=relative(UPLOAD_RECEIPT), receiptObserved=False,
        draft=None, wizardComplete=None, currentUpload=deepcopy(unobserved_platform),
        currentUploadAuthorization=deepcopy(upload_authorization),
        requiredBeforeYouTube='Explicit user BGM-repair/reupload request authorizes this correction; actual review/listening of the new mix is unobserved.')
    manifest['paths']['publishingReceipt'] = relative(UPLOAD_RECEIPT)
    manifest['approvals'].update(uploaded=False, collected=False,
        voice='Existing approved Sample B PCM unchanged; new music-only mix reports attached; actual human whole listening remains unverified.',
        qa='BGM-only current technical records attached; no new whole-listening claim')
    manifest['finalRender']['technicalVerification'] = relative(structural_file)
    manifest['finalRender']['openItems'] = ['복구한 오디오 실제 전체 청취 여부 미확인']
    checkpoint = after[HERE / 'checkpoint.json']
    checkpoint.update(revision=REVISION, status='local-complete', stage='bgm-restored-local-complete', updatedAt=now,
        wholeListening=False, humanFinalReview='not-observed-for-this-new-audio', latestUserRevision=request,
        nextAction='Collect four outputs and privately reupload this explicitly requested music repair. Record actual superseded-video action separately; preserve oldest baseline and other videos.',
        localDelivery=delivery, privateUploadComplete=False, uploaded=False,
        videoId=None, url=None, uploadReceipt=None, draft=None, wizardComplete=None,
        platform=deepcopy(unobserved_platform), currentUploadAuthorization=deepcopy(upload_authorization))
    production = after[PROJECT / 'planning/production-plan.json']
    production.update(status=REVISION + '-local-complete', finalEditPlan=relative(PLAN_FILE),
        selectedUserCorrection=request, finalReviewDelivery=delivery,
        nextAction=checkpoint['nextAction'])
    row = next(r for r in after[work_file]['rows'] if r.get('id') == 'D22')
    require(row.get('slug') == SLUG, 'D22 worklist identity mismatch')
    row.update(activeRevision=REVISION, productionComplete=True,
        productionStatus='원래 Nimbus BGM 가청 수준 복구 · 영상·TTS·자막 보존',
        reviewStatus='현재 믹스 기술 검사 기록 · 새 오디오 전체 청취 미확인',
        humanApproval='BGM 복구·기존 업로드 교체 요청 확인 · 새 전체 청취 미확인',
        executionStatus='오디오만 재믹스 · 영상 스트림 복사',
        platformStatus='이전 비공개 임시본 유지 · BGM 복구본 교체 업로드 대기',
        replacementVideoId=SUPERSEDED, oldestBaselineVideoId=OLDEST,
        notes='원래 Nimbus BGM만 복구. 1080p60·4분50초·104쌍 자막·끝페이지와 코칭 대사 제거 유지. 교체 요청은 승인 근거이며 새 버전 실제 전체 청취의 증거가 아님.')
    row['currentRevision'].update(id=REVISION, status='local-complete', productionComplete=True,
        humanFinalReview='not-observed-for-this-new-audio', youtubeUploadAuthorized=True,
        privateUploadComplete=False, localDelivery=delivery, uploaded=False,
        videoId=None, uploadReceipt=None, draft=None, wizardComplete=None)
    scoped = after[control_file]['scopedProductionAuthorizations'][SLUG]
    if scoped.get('actualUpload', {}).get('videoId') == SUPERSEDED:
        scoped['previousRevisionUpload'] = deepcopy(scoped['actualUpload'])
    scoped.update(revision=REVISION, status='bgm-restored-local-complete',
        latestUserRevision=request, privateUploadAuthorized=True, localDelivery=delivery,
        humanFinalReview='not-observed-for-this-new-audio', privateUploadComplete=False,
        currentUploadAuthorization=deepcopy(upload_authorization), actualUpload=deepcopy(unobserved_platform),
        scopedReplacementAuthorization={'userMessage': USER_REQUEST, 'supersededVideoId': SUPERSEDED,
            'oldestBaselinePreserved': OLDEST, 'actionObserved': False})

    outputs = {}
    if args.stage in ['record', 'upload']:
        collection_file = PROJECT / 'production/delivery-output.json'
        collection = read(collection_file)
        directory = repo_path(collection['directory'])
        require(directory == edit / 'delivery/output/similar-game-design', 'Collection is not the new BGM revision')
        require(len(collection['files']) == 4 and collection['cues'] == 104, 'Require four current outputs and104 cues')
        for item in collection['files']:
            require(sha(directory / item['name']) == item['sha256'], 'Collected output hash changed')
        require(sha(directory / 'similar-game-design.captioned.mp4') == master['sha256'], 'Collected master mismatch')
        delivery.update(directory=relative(directory), index=relative(directory / 'index.html'),
            captioned=relative(directory / 'similar-game-design.captioned.mp4'))
        manifest['paths']['outputIndex'] = delivery['index']
        manifest['approvals']['collected'] = True
        manifest['status'] = REVISION + '-local-delivery-ready'
        checkpoint.update(stage='bgm-restored-four-output-ready', status='explicit-reupload-request-awaiting-platform',
            nextAction='Privately upload the exact collected BGM repair under the actual user request; record observed draft/final-save and superseded-upload state without inferring listening.')
        for item in [manifest['currentRevision'], row['currentRevision']]:
            item['status'] = 'local-delivery-ready'
        prepared = after[metadata_file]
        prior_master = prepared.get('finalMaster', {})
        if prior_master.get('sha256') and prior_master.get('sha256') != master['sha256']:
            prepared['previousVersionFinalMaster'] = deepcopy(prior_master)
        prepared.update(revision=REVISION, finalMaster=deepcopy(delivery),
            status='bgm-restored-local-master-explicit-reupload-request',
            uploadReady=True, platformMutationPerformed=False, userFinalReviewClaimed=False,
            currentUploadAuthorization=deepcopy(upload_authorization),
            audioCorrection={'request': request, 'plan': artifact(PLAN_FILE),
                'verification': artifact(correction_file), 'wholeListening': False})
        music_info = prepared.get('sourceCreditsReconciliation', {}).get('music')
        if isinstance(music_info, dict):
            music_info.update(finalMixAudited='Current BGM restoration technical measurements/ASR attached; actual whole listening remains unverified.',
                finalTimelineSelected=True)
        chapters = after[chapters_file]
        if chapters.get('basis', {}).get('path') != relative(PLAN_FILE):
            chapters['previousVersionBasis'] = deepcopy(chapters.get('basis', {}))
        chapters['basis'].update(path=relative(PLAN_FILE), sha256=sha(PLAN_FILE),
            fps=plan['fps'], totalFrames=plan['totalFrames'], totalSeconds=plan['totalFrames']/plan['fps'])
        chapters['timingReusedReason'] = 'Only original Nimbus BGM gain/ducking changed; every scene/chapter boundary, video frame, narration/caption clock and end page retained.'
        previous_ledger = HERE / 'review-ledger-coaching-silent-v3.json'
        if not previous_ledger.exists():
            require(before[HERE / 'review-ledger.json'].get('revision') == BASE_REVISION,
                    'Original v3 ledger must be preserved before replacing the current ledger')
            outputs[previous_ledger] = originals[HERE / 'review-ledger.json']
            prior = {'path': relative(previous_ledger), 'sha256': hashlib.sha256(outputs[previous_ledger]).hexdigest(),
                     'bytes': len(outputs[previous_ledger])}
        else:
            prior = artifact(previous_ledger)
        after[HERE / 'review-ledger.json'] = {'schemaVersion': 1, 'slug': SLUG, 'revision': REVISION,
            'recordedAt': now, 'status': 'music-repaired-local-delivery-ready-explicit-reupload-request',
            'master': deepcopy(master), 'plan': artifact(PLAN_FILE), 'retainedV3Evidence': prior,
            'scope': 'Original Nimbus BGM restored only. Source voice/game PCM, all video pixels,104paired captions, duration and ending retained.',
            'currentCorrectionReview': artifact(correction_file),
            'currentStructuralVerification': artifact(structural_file),
            'currentMixAsr': artifact(asr_file), 'currentMixTextComparison': artifact(comparison_file),
            'deliveryReceipt': artifact(collection_file),
            'humanFinalReview': {'status': 'not-observed-for-this-new-audio', 'wholeListening': False,
                'actualWholeViewingVerified': False, 'masterSha256': master['sha256']},
            'uploadAuthorization': request, 'youtubeMutation': False, 'driveMutation': False,
            'oldestBaselinePreserved': True, 'supersededActionObserved': False, 'automaticNextVideo': False}

    if args.stage == 'upload':
        require(UPLOAD_RECEIPT.is_file(), 'Actual replacement upload receipt is absent')
        receipt = read(UPLOAD_RECEIPT)
        platform = upload_state(receipt, manifest)
        stage = 'youtube-private-draft' if platform['draft'] else 'youtube-private-saved'
        manifest.update(status=REVISION + '-' + stage)
        manifest['publishing'].update(videoId=platform['videoId'], url=platform['url'], uploaded=True,
            receipt=relative(UPLOAD_RECEIPT), currentUpload=platform, replacementUploadPending=False,
            receiptObserved=True, currentUploadAuthorization=deepcopy(receipt['userAuthorization']),
            privateUploadComplete=platform['privateUploadComplete'], privateSaveVerified=platform['privateSaveVerified'],
            fullSettingsVerified=platform['fullSettingsVerified'], draft=platform['draft'], wizardComplete=platform['wizardComplete'])
        manifest['paths']['publishingReceipt'] = relative(UPLOAD_RECEIPT)
        manifest['currentRevision'].update(status=stage, videoId=platform['videoId'],
            uploadReceipt=relative(UPLOAD_RECEIPT), draft=platform['draft'], wizardComplete=platform['wizardComplete'],
            privateUploadComplete=platform['privateUploadComplete'])
        manifest['approvals']['uploaded'] = True
        checkpoint.update(stage=stage, status=receipt['status'], uploaded=True, platform=platform,
            videoId=platform['videoId'], url=platform['url'], privateUploadComplete=platform['privateUploadComplete'],
            draft=platform['draft'], wizardComplete=platform['wizardComplete'],
            currentUploadAuthorization=deepcopy(receipt['userAuthorization']),
            uploadReceipt=relative(UPLOAD_RECEIPT),
            nextAction='Retain user-owned ad evaluation/final private save if draft; preserve original baseline. No scheduling or next video.')
        ledger = after[HERE / 'review-ledger.json']
        ledger.update(status=stage, youtubeMutation=True, platform=platform,
            uploadReceipt=artifact(UPLOAD_RECEIPT), supersededActionObserved=platform['supersededVideoObservation'])
        row.update(videoId=platform['videoId'], url=platform['url'], uploaded=True,
            platformStatus='비공개 임시본 · 사용자 광고평가·최종저장 대기' if platform['draft'] else 'BGM 복구본 비공개 저장 확인',
            platformEvidence=relative(UPLOAD_RECEIPT))
        row['currentRevision'].update(status=stage, videoId=platform['videoId'],
            uploaded=True, privateUploadComplete=platform['privateUploadComplete'], draft=platform['draft'],
            wizardComplete=platform['wizardComplete'], uploadReceipt=relative(UPLOAD_RECEIPT))
        scoped.update(status=stage, actualUpload=platform, privateUploadComplete=platform['privateUploadComplete'],
            currentUploadAuthorization=deepcopy(receipt['userAuthorization']))
        prepared = after[metadata_file]
        prepared.update(platformMutationPerformed=True, uploadReady=False,
            status='bgm-restored-' + stage, currentUpload=deepcopy(platform),
            currentUploadAuthorization=deepcopy(receipt['userAuthorization']), userFinalReviewClaimed=False)

    # Do not update the old historical production/latest-checkpoint or any old
    # receipt. Current manifest.paths.checkpoint points to this scoped checkpoint.
    shared_scope(before, after, work_file, control_file)
    require(scoped.get('automaticNextVideo') is False and scoped.get('scheduleAuthorized') is False
            and scoped.get('driveAuthorized') is False, 'Out-of-scope boundary changed')
    for file, data in after.items():
        if args.stage == 'bind' and file == HERE / 'review-ledger.json':
            continue
        outputs[file] = encoded(data)
    doc = ROOT / 'docs/VIDEO_WORKLIST.md'
    originals[doc] = doc.read_bytes()
    outputs[doc] = doc_lines(originals[doc].decode('utf-8-sig'), row).encode('utf-8')
    report = {'schemaVersion': 1, 'stage': args.stage, 'mode': 'apply' if args.apply else 'dry-run',
        'revision': REVISION, 'currentMasterSha256': master['sha256'], 'wholeListening': False,
        'platformJobs': 0, 'mediaJobs': 0, 'gitJobs': 0,
        'writes': [relative(p) for p in outputs],
        'oldestBaselinePreserved': OLDEST, 'onlySupersededUploadInScope': SUPERSEDED}
    if args.apply:
        for file, old in originals.items():
            require(file.read_bytes() == old, 'Concurrent metadata write; retry instead of overwriting: ' + str(file))
        for file, raw in outputs.items():
            temporary = file.with_name(file.name + '.d22-' + uuid.uuid4().hex + '.tmp')
            temporary.write_bytes(raw)
            os.replace(temporary, file)
        report_file = HERE / ('bgm-finalization-' + args.stage + '.json')
        report_file.write_bytes(encoded({**report, 'recordedAt': now,
            'after': {relative(p): sha(p) for p in outputs}}))
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
