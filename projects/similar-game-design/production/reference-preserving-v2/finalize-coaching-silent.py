"""Bind the user's silent-coaching correction to the current four-file delivery."""
from pathlib import Path
import argparse
import datetime
import json
import os
import shutil
import uuid
import audio_pipeline as audio
from storage_paths import repo_path, relative

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
ROOT = HERE.parents[3]
REVISION = 'coaching-silent-v3'


def save(path, obj):
    tmp = path.with_name(path.name + '.d22-' + uuid.uuid4().hex + '.tmp')
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    os.replace(tmp, path)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('stage', choices=['bind', 'record'])
    args = ap.parse_args()
    audio.require_authorized('bind user-requested silent-coaching correction')
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    plan_file = HERE / 'edit-plan-coaching-silent-v3.json'
    plan = audio.read(plan_file)
    edit = repo_path(plan['outputDir'])
    structural = audio.read(edit / 'structural-verification.json')
    assert structural['status'] == 'pass'
    assert plan['totalFrames'] == 17408
    for suffix, item in structural['outputs'].items():
        assert item['path'].endswith('similar-game-design-coaching-silent-v3-' + suffix + '.mp4')
        assert audio.sha(repo_path(item['path'])) == item['sha256']
    captions = audio.read(edit / 'captions.json')
    assert len(captions['cues']) == 104 and captions['cues'][-1]['end'] == 274.72
    manifest = audio.read(PROJECT / 'project.json')
    if manifest['currentRevision']['id'] != REVISION:
        history = manifest.setdefault('revisionHistory', [])
        history.append({'id': manifest['currentRevision']['id'], 'visualVersion': 'visual-v4',
            'captionedMaster': manifest['paths']['videoBurnedCaptions'],
            'sha256': manifest['delivery']['sha256'], 'preserved': True,
            'sourceCommit': '1175364fa850eaddfdb8c285b93c7012a426120c'})
    manifest['status'] = REVISION + '-local-review-ready'
    manifest['updatedAt'] = now
    manifest['audio'].update(narratedCoachingCta=False, ttsRegenerated=False,
        sourceAsr='retained teaching reviewed previously; final CTA removed by verified sample mask; bounded encoded ending reviewed',
        correction='Final advertising sentence removed; teaching, timing, music and final page/links retained.')
    manifest['tts']['status'] = 'approved-sample-b-reused-no-new-generation-cta-muted-in-processed-stem'
    manifest['currentRevision'].update(id=REVISION, status='local-review-ready',
        productionComplete=True, humanFinalReview='pending', youtubeAuthorized=False)
    paths = manifest['paths']
    script_dir = PROJECT / 'script' / REVISION
    paths.update(script=relative(script_dir / 'narration.ko.json'),
        scriptEnglish=relative(script_dir / 'narration.en.json'),
        scriptEn=relative(script_dir / 'narration.en.json'),
        scriptSpoken=relative(script_dir / 'narration.spoken-ko.json'),
        finalPlan=relative(plan_file), timeline=relative(plan_file),
        videoClean=structural['outputs']['clean']['path'],
        videoBurnedCaptions=structural['outputs']['captioned']['path'],
        captionsKo=relative(edit / 'captions.ko.srt'), captionsEn=relative(edit / 'captions.en.srt'),
        captionKorean=relative(edit / 'captions.ko.srt'), captionEnglish=relative(edit / 'captions.en.srt'),
        captionAlignmentReview=relative(edit / 'caption-alignment.json'),
        finalMixedAsrReview=relative(HERE / 'coaching-silent-v3-review.json'))
    manifest['approvals']['collected'] = args.stage == 'record'
    # Keep the already-open previous review directory usable on Windows.
    # This correction has a versioned C-backed delivery root of its own.
    manifest['delivery']['localStorageRoot'] = relative(edit / 'delivery')
    manifest['publishReady'] = False
    manifest['finalRender']['technicalVerification'] = relative(edit / 'structural-verification.json')
    manifest['finalRender']['openItems'] = ['수정본 전체 청취와 사용자 최종 검수 대기']
    if args.stage == 'record':
        receipt_file = PROJECT / 'production/delivery-output.json'
        receipt = audio.read(receipt_file)
        target = repo_path(receipt['directory'])
        assert len(receipt['files']) == 4 and receipt['cues'] == 104
        for item in receipt['files']:
            assert audio.sha(target / item['name']) == item['sha256']
        master = structural['outputs']['captioned']
        assert next(x for x in receipt['files'] if x['name'].endswith('.captioned.mp4'))['sha256'] == master['sha256']
        manifest['delivery'].update(directory=receipt['directory'], index=relative(target / 'index.html'),
            captioned=relative(target / 'similar-game-design.captioned.mp4'),
            sha256=master['sha256'], humanReview='pending', youtubeUploadAuthorized=False)
        manifest['paths']['outputIndex'] = manifest['delivery']['index']
        ledger_file = HERE / 'review-ledger.json'
        previous_ledger = HERE / 'review-ledger-visual-v4.json'
        if not previous_ledger.exists():
            shutil.copy2(ledger_file, previous_ledger)
        review_file = HERE / 'coaching-silent-v3-review.json'
        assert audio.read(review_file)['status'] == 'pass-scoped-correction-human-final-review-pending'
        save(ledger_file, {'schemaVersion': 1, 'slug': 'similar-game-design', 'revision': REVISION,
            'recordedAt': now, 'status': 'local-four-output-review-ready',
            'master': master, 'plan': audio.artifact(plan_file),
            'retainedLessonEvidence': audio.artifact(previous_ledger),
            'scope': 'Only final coaching CTA removed from processed narration and paired speech captions; all teaching and final page/links retained.',
            'currentCorrectionReview': audio.artifact(review_file),
            'currentStructuralVerification': audio.artifact(edit / 'structural-verification.json'),
            'deliveryReceipt': audio.artifact(receipt_file),
            'humanFinalReview': {'status': 'pending', 'userMessage': None, 'reviewedAt': None,
                'masterSha256': master['sha256'], 'wholeListening': False,
                'requiredBeforeYouTube': True},
            'youtubeMutation': False, 'driveMutation': False, 'baselinePreserved': True,
            'automaticNextVideo': False})
        checkpoint = audio.read(HERE / 'checkpoint.json')
        checkpoint.update(revision=REVISION, stage='local-final-review-ready', status='awaiting-human-review',
            updatedAt=now, jobs=[], localDelivery=manifest['delivery'],
            nextAction='User reviews corrected local master; no YouTube, Drive or next video.')
        save(HERE / 'checkpoint.json', checkpoint)
        auth_file = HERE / 'authorization.json'
        auth = audio.read(auth_file)
        auth.update(status='complete-coaching-silent-v3-local-review-pending', localDelivery=manifest['delivery'])
        save(auth_file, auth)
        production_file = PROJECT / 'planning/production-plan.json'
        production = audio.read(production_file)
        production.update(status=REVISION + '-local-review-ready', finalEditPlan=relative(plan_file),
                          nextAction=checkpoint['nextAction'])
        production['inputs']['scripts'].update(ko=paths['script'], en=paths['scriptEn'], spokenKo=paths['scriptSpoken'])
        for script in production['inputs']['scripts'].values():
            production['inputs']['inputHashes'][script] = audio.sha(repo_path(script))
        production['selectedUserCorrection'] = auth['latestUserRevision']
        production['preproduction']['actualCaptionUiClearance'].update(
            status='104-retained-cues-plus-changed-ending-1080-and375-review',
            evidence='production/reference-preserving-v2/coaching-silent-v3-review.json')
        production['approvals']['finalUserReview'].update(status='pending-actual-human-review',
            version=REVISION, sha256=master['sha256'], captionedPath=manifest['delivery']['captioned'])
        production['finalReviewDelivery'] = manifest['delivery']
        save(production_file, production)
        meta_file = PROJECT / 'publishing/reference-preserving-v2/metadata-prepared.json'
        meta = audio.read(meta_file)
        meta.update(finalMaster=manifest['delivery'], narrationCorrection=auth['latestUserRevision'])
        meta['currentScripts'] = [audio.artifact(repo_path(paths[key])) for key in
                                  ['script', 'scriptEn', 'scriptSpoken']]
        meta['currentCaptionCueCounts'] = {'ko': 104, 'en': 104}
        save(meta_file, meta)
        chapter_file = PROJECT / 'publishing/reference-preserving-v2/chapters.json'
        chapters = audio.read(chapter_file)
        chapters['basis'].update(path=relative(plan_file), sha256=audio.sha(plan_file))
        chapters['timingReusedReason'] = 'Speech CTA muted only; every scene boundary and chapter time retained.'
        save(chapter_file, chapters)
        work_file = ROOT / 'shared/publishing/video-worklist.json'
        work = audio.read(work_file)
        row = next(x for x in work['rows'] if x['id'] == 'D22')
        row.update(productionStatus='코칭 안내 음성 제거 완료 · 1080p60 / 4분50초',
            reviewStatus='해당 대사·자막 제거 검사 완료 · 수정본 사용자 최종 검수 대기',
            executionStatus='로컬 수정본 완성 · TTS 재생성 없음', activeRevision=REVISION)
        row['currentRevision'].update(id=REVISION, status='local-review-ready',
            humanFinalReview='pending', localDelivery=manifest['delivery'])
        row['notes'] = '마지막 코칭 광고 발화와 한영 자막105만 제거. 교육 내용·배경음악·끝페이지/링크·4분50초 유지. 기존 비공개본 보존, 새 업로드 없음.'
        save(work_file, work)
        doc = ROOT / 'docs/VIDEO_WORKLIST.md'
        lines = doc.read_text('utf-8-sig').splitlines(keepends=True)
        for i, line in enumerate(lines):
            end = '\r\n' if line.endswith('\r\n') else '\n'
            if '| 게임디자인 | D22 [' in line:
                cells = line.split('|'); cells[4] = ' 코칭 안내 음성 제거 · 로컬 완성 '; cells[5] = ' ☐ 수정본 전체 청취·사용자 검수 대기 '
                lines[i] = '|'.join(cells).rstrip('\r\n') + end
            elif line.startswith('| D22 |'):
                lines[i] = '| D22 | [비슷한 게임을 고를 이유](https://youtu.be/_p1IqDeg6YE) | 코칭 음성 제거본 완성 | 수정본 사용자 검수 대기 | 기존 비공개본 보존 · 새 업로드 없음 |' + end
            elif line.startswith('| D22 '):
                lines[i] = '| D22 비슷한 게임을 고를 이유 | 마지막 코칭 광고 음성·말자막 제거. 1080p60·4분50초·교육 결론·마지막 페이지/링크 유지. |' + end
        temporary = doc.with_name(doc.name + '.d22-' + uuid.uuid4().hex + '.tmp')
        temporary.write_text(''.join(lines), encoding='utf-8'); os.replace(temporary, doc)
        control_file = ROOT / 'shared/publishing/video-production-control.json'
        control = audio.read(control_file)
        scoped = control['scopedProductionAuthorizations']['similar-game-design']
        scoped.update(status='complete-coaching-silent-v3-local-review-pending',
            localDelivery=manifest['delivery'], latestUserRevision=auth['latestUserRevision'])
        save(control_file, control)
    save(PROJECT / 'project.json', manifest)
    print(args.stage, 'silent-coaching correction; same timeline, human review pending')


if __name__ == '__main__':
    main()
