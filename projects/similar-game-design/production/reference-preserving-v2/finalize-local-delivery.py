"""Bind D22's current verified local masters; never uploads or advances work."""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import os
import sys
import uuid

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PROJECT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from storage_paths import repo_path, relative
from audio_pipeline import require_authorized


def read(path):
    return json.loads(path.read_text('utf-8-sig'))


def write(path, value):
    temporary = path.with_name(path.name + '.d22-' + uuid.uuid4().hex + '.tmp')
    with temporary.open('x', encoding='utf-8') as f:
        f.write(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
        f.flush()
        os.fsync(f.fileno())
    os.replace(temporary, path)


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('stage', choices=['prepare-collection', 'record-delivery'])
    args = ap.parse_args()
    require_authorized('bind current local delivery metadata only')
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    plan_file = HERE / 'edit-plan-final-v4.json'
    plan = read(plan_file)
    edit = repo_path(plan['outputDir'])
    structural = read(edit / 'structural-verification.json')
    assert structural['status'] == 'pass'
    for suffix, entry in structural['outputs'].items():
        assert entry['path'].endswith('similar-game-design-v4-' + suffix + '.mp4')
        assert sha(repo_path(entry['path'])) == entry['sha256']
    manifest = read(PROJECT / 'project.json')
    manifest['status'] = 'reference-preserving-v2-local-review-ready'
    manifest['format'].update(durationSeconds=plan['totalFrames'] / 60, frames=plan['totalFrames'],
                              videoTimeBase='1/60000', ptsStep=1000)
    manifest['audio'].update(sourceAudio='Six original game mixes retained; World Maker feature voice muted as recorded.',
                             sourceAsr='complete-source-and-encoded-mix-compared; visual-only v4 audio reuse verified')
    manifest['tts']['status'] = 'complete-own-voice-sample-b-original-mp3-preserved'
    manifest['approvals'].update(voice='existing approved Sample B; full source/final ASR and quantitative continuity reviewed; human listening pending',
                                 sourceObservation='native event windows and encoded cue/mark/boundary samples reviewed',
                                 render=True, qa='technical-and-sampled-pixel-review-complete-human-listening-pending',
                                 finalPixels='sampled-1080-and-375-review; not every frame')
    paths = manifest['paths']
    paths.update(finalPlan=relative(plan_file), timeline=relative(plan_file),
                 videoClean=structural['outputs']['clean']['path'],
                 videoBurnedCaptions=structural['outputs']['captioned']['path'],
                 captionsKo=relative(edit / 'captions.ko.srt'), captionsEn=relative(edit / 'captions.en.srt'),
                 captionKorean=relative(edit / 'captions.ko.srt'), captionEnglish=relative(edit / 'captions.en.srt'),
                 voiceTiming='shared/output/narration/similar-game-design/reference-preserving-v2/source-scene-timings.json',
                 captionAlignmentReview=relative(edit / 'caption-alignment.json'),
                 finalMixedAsrReview=relative(HERE / 'final-mix-comparison-review.json'),
                 finalPixelReview=relative(HERE / 'review-ledger.json'), qa=relative(HERE / 'review-ledger.json'),
                 measuredPublishingPreparation=relative(PROJECT / 'publishing/reference-preserving-v2/metadata-prepared.json'))
    manifest['warnings'] = ['Actual human whole listening and final review of this exact master remain pending.']
    manifest['publishReady'] = False
    manifest['finalRender'] = {'knownIssues': [], 'openItems': ['전체 청취와 사용자 최종 검수 대기'],
                               'technicalVerification': relative(edit / 'structural-verification.json')}
    manifest['currentRevision'].update(status='local-review-ready', productionComplete=True,
                                       humanFinalReview='pending', youtubeAuthorized=False)
    manifest['updatedAt'] = now
    if args.stage == 'record-delivery':
        receipt = read(PROJECT / 'production/delivery-output.json')
        target = ROOT / receipt['directory']
        assert len(receipt['files']) == 4
        for item in receipt['files']:
            assert sha(target / item['name']) == item['sha256']
        captioned = next(x for x in receipt['files'] if x['name'].endswith('.captioned.mp4'))
        assert captioned['sha256'] == structural['outputs']['captioned']['sha256']
        manifest['approvals']['collected'] = True
        manifest['paths']['outputIndex'] = relative(target / 'index.html')
        manifest['delivery'].update(directory=receipt['directory'], index=relative(target / 'index.html'),
                                    captioned=relative(target / captioned['name']), sha256=captioned['sha256'],
                                    humanReview='pending', youtubeUploadAuthorized=False)
        checkpoint = read(HERE / 'checkpoint.json')
        checkpoint.update(updatedAt=now, stage='local-final-review-ready', status='awaiting-human-review', jobs=[],
                          nextAction='User reviews the complete local captioned master; no YouTube/Drive/next video.',
                          humanFinalReview='pending', wholeListening=False, localDelivery=manifest['delivery'])
        write(HERE / 'checkpoint.json', checkpoint)
        production = read(PROJECT / 'planning/production-plan.json')
        production.update(status='local-final-review-ready', finalEditPlan=relative(plan_file),
                          nextAction=checkpoint['nextAction'])
        production['preproduction']['currentDuplicateReview'].update(status='distinct-current-check-passed',
            evidence='production/batches/sakurai-planning-game-design/preflight/similar-game-design.json')
        completed_checks = {
            'sourcesRightsAndActualPlayback': ('native-source-events-and-encoded-sample-playback-reviewed', 'sources/footage-options-v2.json'),
            'prerequisitesMathAndPronunciation': ('rules-and-terms-explained-full-asr-compared-human-pronunciation-listening-pending', 'production/reference-preserving-v2/final-mix-comparison-review.json'),
            'allSceneDetailedSubjectsAndMotionPlan': ('implemented-and-sampled-pixels-reviewed', 'production/reference-preserving-v2/source-cut-bindings-final-v4.json'),
            'actualCaptionUiClearance': ('105-caption-cues-reviewed-with-visual-v4-delta', 'production/reference-preserving-v2/review-ledger.json'),
            'sourceCapacityAndRatioPlan': ('measured-pass-10013-to-6675-bodyframes', 'production/reference-preserving-v2/edit-plan-final-v4.json'),
            'narrationLevelContinuity': ('quantitative-dispositions-complete-human-listening-pending', 'production/reference-preserving-v2/audio-continuity-review.json'),
            'brandingMembershipAndThumbnailPlan': ('original-brand-member-preserved-thumbnail-prepared', 'publishing/reference-preserving-v2/metadata-prepared.json'),
            'representativeMovingSample': ('five-original-and-eight-changed-cuts-actually-played-muted', 'production/reference-preserving-v2/review-ledger.json'),
            'originalGamesAndModernEquivalentVersions': ('two-concept-matched-genres-one-nintendo-of-two', 'sources/footage-options-v2.json'),
            'independentGameplaySourceSeparation': ('all-seven-used-sources-independent-no-lesson-pixels-audio', 'production/reference-preserving-v2/source-cut-bindings-final-v4.json'),
            'rendererChoiceAndActualImplementation': ('Motion-Canvas-abstract-relations-and-game-screenshots', 'production/reference-preserving-v2/edit-plan-final-v4.json'),
            'brandedUiAndMobileReadability': ('sampled-1080-and375-review-complete', 'production/reference-preserving-v2/review-ledger.json'),
            'actualFootageFocusAnnotations': ('direct-source-and-v4-mark-samples-reviewed', 'production/reference-preserving-v2/pixel-review-v4-marks.json'),
        }
        for key, (status, evidence) in completed_checks.items():
            production['preproduction'][key].update(status=status, evidence=evidence)
        production['approvals']['finalUserReview'].update(directory=receipt['directory'],
            captionedPath=manifest['delivery']['captioned'], version='reference-preserving-v2-visual-v4',
            sha256=captioned['sha256'], status='pending-actual-human-review')
        production['finalReviewDelivery'] = manifest['delivery']
        write(PROJECT / 'planning/production-plan.json', production)
        meta_file = PROJECT / 'publishing/reference-preserving-v2/metadata-prepared.json'
        meta = read(meta_file)
        meta.update(status='local-master-and-publishing-package-ready-human-review-pending',
                    finalMaster=manifest['delivery'], uploadReady=False, userFinalReviewClaimed=False)
        meta['titles'].update(ko=manifest['titles']['ko'], en=manifest['titles']['en'])
        meta['sourceCreditsReconciliation']['finalSourceIdBasis'] = relative(plan_file)
        meta['sourceCreditsReconciliation']['music']['finalMixAudited'] = 'quantitative-only; whole listening pending'
        write(meta_file, meta)
        chapters_file = PROJECT / 'publishing/reference-preserving-v2/chapters.json'
        chapters = read(chapters_file)
        chapters.setdefault('originalMeasuredBasis', chapters['basis'])
        chapters['basis'].update(path=relative(plan_file), sha256=sha(plan_file))
        chapters['timingReusedReason'] = 'Visual-only v4 retains all scene boundaries, speech and chapter times.'
        write(chapters_file, chapters)
        work_file = ROOT / 'shared/publishing/video-worklist.json'
        work = read(work_file)
        row = next(x for x in work['rows'] if x['id'] == 'D22')
        row.update(productionStatus='v2 완성 · 1080p60 / 4분50초 / 로컬 4파일',
                   reviewStatus='내부 기술·표본 화면 검사 완료 · 전체 청취·사용자 검수 대기',
                   executionStatus='선택 영상 제작 완료 · 사용자 로컬 검수 대기',
                   localMasterAvailable=True, latestRulesPassed=None,
                   notes='D22 개정본 완성. 실제60:설명40, 본인 ElevenLabs B, 두 장르·닌텐도1/2. 기존 비공개 _p1IqDeg6YE 보존. 새 버전 업로드·다음 영상 없음.')
        row['currentRevision'].update(status='local-review-ready', productionComplete=True,
                                      humanFinalReview='pending', localDelivery=manifest['delivery'])
        row['evidence'] = list(dict.fromkeys(row['evidence'] + [relative(HERE / 'review-ledger.json'),
                              relative(PROJECT / 'production/delivery-output.json')]))
        write(work_file, work)
        doc = ROOT / 'docs/VIDEO_WORKLIST.md'
        lines = doc.read_text('utf-8-sig').splitlines(keepends=True)
        for i, line in enumerate(lines):
            ending = '\r\n' if line.endswith('\r\n') else '\n'
            if '| 게임디자인 | D22 [' in line:
                cells = line.split('|')
                cells[4] = ' v2 로컬 완성 · 기존 비공개본 보존 '
                cells[5] = ' ☐ 전체 청취·사용자 최종 검수 대기 '
                lines[i] = '|'.join(cells).rstrip('\r\n') + ending
            elif line.startswith('| D22 |'):
                lines[i] = '| D22 | [비슷한 게임을 고를 이유](https://youtu.be/_p1IqDeg6YE) | 기존본 ☑ / v2 로컬 완성 | 전체 청취·사용자 검수 대기 | 기존 비공개본 보존 · 새 업로드 없음 |' + ending
            elif line.startswith('| D22 '):
                lines[i] = '| D22 비슷한 게임을 고를 이유 | v2 1080p60·4분50초 완성. 로컬 4파일/한영 자막 제공, 사용자 검수 대기. 기존 비공개본 보존. |' + ending
        doc.write_text(''.join(lines), encoding='utf-8')
        control_file = ROOT / 'shared/publishing/video-production-control.json'
        control = read(control_file)
        auth = control['scopedProductionAuthorizations']['similar-game-design']
        auth.update(status='complete-local-review-pending', productionComplete=True,
                    humanFinalReview='pending', localDelivery=manifest['delivery'])
        authorization_file = HERE / 'authorization.json'
        authorization = read(authorization_file)
        authorization.update(status='complete-local-review-pending', productionComplete=True,
                             humanFinalReview='pending', localDelivery=manifest['delivery'])
        write(authorization_file, authorization)
        assert control['selectedVideo'] == 'similar-game-design'
        control['runningWorkBoundary'] = 'D22 complete: local four-file final review pending. No YouTube, Drive, baseline mutation or automatic next video.'
        write(control_file, control)
    write(PROJECT / 'project.json', manifest)
    print(args.stage, 'bound to verified v4; human review remains pending')


if __name__ == '__main__':
    main()
