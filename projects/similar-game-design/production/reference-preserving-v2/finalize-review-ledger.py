"""Consolidate completed D22 evidence without inventing human review."""
from pathlib import Path
import datetime
import hashlib
import json
from storage_paths import repo_path, relative

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]


def read(p):
    return json.loads(p.read_text('utf-8-sig'))


def artifact(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(block)
    return {'path': relative(p), 'sha256': h.hexdigest(), 'bytes': p.stat().st_size}


def main():
    plan = read(HERE / 'edit-plan-final-v4.json')
    edit = repo_path(plan['outputDir'])
    structural = read(edit / 'structural-verification.json')
    assert structural['status'] == 'pass'
    master = structural['outputs']['captioned']
    assert master['path'].endswith('similar-game-design-v4-captioned.mp4')
    assert artifact(repo_path(master['path']))['sha256'] == master['sha256']
    reports = ['script-review.json', 'source-comparison-review.json',
               'source-audio-review.json', 'representative-sample-review.json',
               'pixel-review-cues01-56.json', 'pixel-review-cues57-105.json',
               'pixel-review-footage-marks.json', 'pixel-review-v4-explanations.json',
               'pixel-review-v4-marks.json', 'pixel-review-v4-handoffs.json',
               'final-mix-comparison-review.json', 'audio-continuity-review.json',
               'audio-asr-reuse-v4.json', 'final-pipeline-audit.json',
               'source-cut-bindings-final-v4.json', 'pipeline-smoke-qa.json',
               'pair-join-repair.json']
    evidence = [artifact(HERE / name) for name in reports]
    evidence += [artifact(edit / name) for name in
                 ['structural-verification.json', 'pair-build.json', 'audio-build.json',
                  'caption-layout.json', 'caption-alignment.json', 'captions.json']]
    for name in ['pixel-review-v4-explanations.json', 'pixel-review-v4-marks.json']:
        review = read(HERE / name)
        assert 'pass' in review['status'].lower(), (name, review['status'])
    receipt_file = PROJECT / 'production/delivery-output.json'
    delivery = read(receipt_file)
    assert len(delivery['files']) == 4
    for item in delivery['files']:
        assert artifact(repo_path(delivery['directory']) / item['name'])['sha256'] == item['sha256']
    record = {
        'schemaVersion': 1, 'slug': 'similar-game-design',
        'revision': 'reference-preserving-v2-visual-v4',
        'recordedAt': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'status': 'local-four-output-review-ready-technical-and-sampled-pixels-checked',
        'master': master, 'plan': artifact(HERE / 'edit-plan-final-v4.json'),
        'evidence': evidence, 'deliveryReceipt': artifact(receipt_file),
        'teaching': {'referenceRole': 'research-reference-only',
            'sourceParagraphs': 25, 'instructionalParagraphsRetained': 21,
            'noninstructionalOmissionsWithReasons': 4,
            'narrationParagraphs': 32, 'scenes': 10,
            'wholeKoEnAndSourceOrderReviewed': True,
            'thesisPreservedRedundantDefensiveMetaOmitted': True,
            'productionUsesNoReferenceLessonPixelsAudioOrSlides': True},
        'footage': {'adoptedIndependentSources': 7,
            'actualGames': ['Deep Rock Galactic: Survivor', 'Super Mario Maker 2'],
            'differentGenresAndTeachingRoles': True,
            'nintendoPrimaryExamples': 1, 'primaryExamples': 2,
            'rounding': 'nearest feasible integer: round(2/3)=1; no unrelated padding',
            'downloadedAndDecodedMinimumFhd': True,
            'nativeSpeedAspectNoLoops': True,
            'actualBodyFrames': 10013, 'explanationBodyFrames': 6675,
            'actualBodyShare': 10013 / 16688,
            'brandingMemberExcludedFrames': 720},
        'audio': {'voice': 'approved own-voice ElevenLabs Sample B, Eleven v4',
            'originalMp3Preserved': True, 'internalPcm': '48000Hz',
            'fullSourceAndFinalAsrTextCompared': True,
            'boundedContextAmbiguitiesResolvedWithoutExpectedPrompt': True,
            'finalMusicOnlyAsrInsertionNotANewSpokenLine': True,
            'quantitativeLocalSpeechContinuityDispositionsComplete': True,
            'finalLufs': -16.37, 'finalTruePeakDb': -2.00,
            'v4ExactAacReuse': read(HERE / 'audio-asr-reuse-v4.json')['audioPacketsSha256'],
            'originalGameMixesRetained': 6,
            'worldMakerAudio': 'muted inseparable offscreen feature narration; unchanged source preserved',
            'bgm': 'Nimbus — Eveningland, original licensed YouTube Audio Library track',
            'subjectiveWholeListening': 'pending'},
        'pixels': {'completeCaptionCueCount': 105,
            'v2CueMidpointsDirectlyReadAt640And375': True,
            'v4ChangedCutCount': 8, 'v4UnchangedCutBytesReused': 31,
            'v4DeltaNativeMasterFramesExtracted': 160,
            'direct1080And375DeltaReviewsRecorded': True,
            'allEightChangedCutsActuallyPlayedMuted': True,
            'originalBrandingAndMembershipPixelsPreserved': True,
            'wholeVideoEveryFrameHumanReviewed': False,
            'resolved': ['retry line avoids labels', 'World Maker handoff follows creator clause',
                         'three experience photos follow spoken examples',
                         'VS character marks follow jumps',
                         'countdown circle only on a clear numeral',
                         'castle arrow clears hover hint',
                         'pair joins retain exact continuous 60fps PTS']},
        'structure': {'bothFullVideoFrameAndAudioDecodes': 'pass',
            'frames': 17408, 'fps': 60, 'width': 1920, 'height': 1080,
            'seconds': 17408 / 60, 'strictPtsGrid': True,
            'cleanAndCaptionedSameContinuousAac': True,
            'koEnSrtCues': [105, 105], 'fourCopiedFilesHashVerified': True},
        'publishing': {'thumbnailAndBilingualDescriptionsChaptersPrepared': True,
            'creditsAtDescriptionBottom': True,
            'baselineVideoId': '_p1IqDeg6YE', 'baselinePreserved': True,
            'youtubeMutation': False, 'driveMutation': False,
            'automaticNextVideo': False},
        'humanFinalReview': {'status': 'pending', 'userMessage': None,
            'reviewedAt': None, 'masterSha256': master['sha256'],
            'requiredBeforeYouTube': True,
            'remaining': ['actual whole listening and pronunciation judgment',
                          'user review of this exact complete captioned master']},
    }
    (HERE / 'review-ledger.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Current master evidence and four files consolidated; actual human review pending.')


if __name__ == '__main__':
    main()
