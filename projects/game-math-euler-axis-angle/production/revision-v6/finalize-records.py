"""Register the completed, evidenced M04 V6 local delivery. Never upload media.

Default/--check validates existing files and reports only. --run updates the
selected project's records; --run --collect additionally invokes the established
four-file collector. No decoder, renderer, ASR model or GPU process is started.
Human listening, continuous motion playback and user approval are not inferred
from numerical checks, sampled frame boards, ASR or delivery of a link.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import copy
import hashlib
import json
import os
import subprocess
import sys

R = Path(__file__).resolve().parents[4]
P = R / 'projects/game-math-euler-axis-angle'
H = Path(__file__).resolve().parent
O = P / 'production/local/revision-v6'
SLUG = P.name
REV = 'article-flow-v6'
FILES = {
    'project': P / 'project.json',
    'plan': P / 'planning/production-plan.json',
    'checkpoint': P / 'production/checkpoint.json',
    'ledger': P / 'production/review-ledger.json',
    'qa': P / 'production/qa.json',
    'worklist': R / 'shared/publishing/video-worklist.json',
}


def require(value, message):
    if not value:
        raise ValueError(message)


def now():
    return datetime.now(timezone.utc).isoformat()


def read(path):
    require(Path(path).is_file(), 'Required file missing: ' + str(path))
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def path(value):
    p = Path(value)
    p = (p if p.is_absolute() else R / p).resolve()
    require(p != R and p.is_relative_to(R), 'Path escapes the workspace: ' + str(value))
    require(p.is_file(), 'Required file missing: ' + str(value))
    return p


def rel(value):
    return Path(value).resolve().relative_to(R).as_posix()


class Evidence:
    def __init__(self):
        self.checked = {}

    def sha(self, value):
        p = path(value)
        stat = p.stat()
        identity = (stat.st_size, stat.st_mtime_ns)
        old = self.checked.get(p)
        if old and old['identity'] == identity:
            return old['sha256']
        h = hashlib.sha256()
        with p.open('rb') as stream:
            for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
                h.update(block)
        require(identity == (p.stat().st_size, p.stat().st_mtime_ns), 'File changed while hashing: ' + rel(p))
        result = h.hexdigest()
        self.checked[p] = {'identity': identity, 'sha256': result}
        return result

    def proof(self, value):
        p = path(value)
        return {'file': rel(p), 'sha256': self.sha(p)}

    def check(self, reference, label):
        require(isinstance(reference, dict), label + ': file/SHA256 reference required')
        p = path(reference.get('file', ''))
        require(reference.get('sha256') == self.sha(p), label + ': SHA256 mismatch: ' + rel(p))
        return p

    def unchanged(self):
        for p, old in self.checked.items():
            s = p.stat()
            require((s.st_size, s.st_mtime_ns) == old['identity'], 'Validated input changed: ' + rel(p))


def selected():
    control = read(R / 'shared/publishing/video-production-control.json')
    require(control.get('selectedVideo') == SLUG, 'M04 is no longer the selected video')
    auth = control.get('newProductionAuthorization', {})
    require(auth.get('fullProductionAuthorized') is True, 'Selected full production is not authorized')
    require('local final review' in auth.get('scope', '').lower(), 'Unexpected production boundary')
    require(control.get('automaticNextVideoEnabled') is False, 'Automatic next-video state changed')
    return control


def unique_report(folder, filename):
    candidates = sorted(Path(folder).rglob(filename))
    require(len(candidates) == 1, 'Expected exactly one current ' + filename + '; found ' + str(len(candidates)))
    return candidates[0]


def zero_flags(value):
    return value == 0 or value == []


def verify_descriptions(build, e, timeline_sha):
    require(build.get('revision') == REV, 'Descriptions belong to another revision')
    require(build.get('platformMutationPerformed') is False and build.get('uploadAuthorizedByThisBuild') is False, 'Description preparation cannot authorize an upload')
    require(build['inputs']['timeline']['sha256'] == timeline_sha, 'Description chapter timing is stale')
    for name, reference in build['inputs'].items():
        e.check(reference, 'Description build input ' + name)
    for reference in build.get('sourceEvidence', []):
        e.check(reference, 'Actual description source evidence')
    require(build.get('sourceCreditsPolicy') == 'description-sources-last-v1', 'Description sources-last policy missing')
    for key in ['sourcesAtAbsoluteBottomBothLanguages', 'bothDescriptionsWithin5000Utf16Units']:
        require(build['checks'].get(key) is True, 'Description check incomplete: ' + key)
    for language, metadata in [('ko', 'metadata'), ('en', 'englishMetadata')]:
        output = build['outputs'][language]
        filename = e.check(output, 'Current ' + language + ' description')
        require(filename == P / ('publishing/revision-v6-description.' + language + '.txt'), 'Unexpected current description path')
        text = filename.read_text(encoding='utf-8-sig').rstrip('\r\n')
        require(text == build[metadata]['description'], language + ': actual description differs from the prepared metadata')
        credits = build['sourceCredits'][language].strip()
        require(bool(credits) and text.endswith(credits), language + ': nothing may follow the actual source credits')
        units = len(text.encode('utf-16-le')) // 2
        require(len(text) <= 5000 and units <= 5000, language + ': actual YouTube description exceeds 5000 characters/UTF16 units')
        require((output['characters'], output['utf16CodeUnits']) == (len(text), units), language + ': description length receipt stale')


def accepted_caption_report(report, e):
    if 'rawAutomatedReport' not in report:
        require(report.get('failureCount') == 0 and not report.get('failures'), 'Encoded caption pixels have unresolved failures')
        require(str(report.get('status', '')).startswith('pass'), 'Encoded caption QA incomplete')
        return report
    # Accept only the three demonstrated producer/oracle first-frame clock
    # differences. Preserve the raw failure report and its strict thresholds.
    raw_path = e.check(report['rawAutomatedReport'], 'Preserved raw caption report')
    raw = read(raw_path); frames = [50547, 103449, 212868]
    require(report.get('inputs') == raw.get('inputs'), 'Reviewed caption extension binds different inputs')
    require(report.get('rawAutomatedFailureCount') == raw.get('failureCount') == 3, 'Unexpected raw caption failure count')
    require(sorted(x['frame'] for x in raw['failures']) == frames == report.get('rawAutomatedFailureFrames'), 'Reviewed caption exception exceeds the proven three frames')
    require(report.get('unresolvedFailureCount') == 0 and report.get('reviewedBoundaryCount') == 3, 'Clock-boundary review incomplete')
    require(report.get('strictPixelThresholdsChanged') is False and report.get('originalRawFailureReportPreserved') is True, 'Raw caption thresholds/report were not preserved')
    maximum = report.get('maximumAcceptedBoundaryDifference', {})
    require(maximum.get('observedFrames') == 1 and maximum.get('appliesOnlyToFrames') == frames, 'Caption exception must remain limited to these three single frames')
    evidence = read(e.check(report['reviewedEvidence'], 'Clock-boundary reproduction evidence'))
    require(evidence['currentCaptionedMaster']['sha256'] == raw['inputs']['master']['sha256'], 'Clock reproduction belongs to another master')
    require(evidence['timeline']['sha256'] == raw['inputs']['timeline']['sha256'], 'Clock reproduction timeline is stale')
    require(evidence['rawAutomatedReport']['sha256'] == e.sha(raw_path), 'Clock reproduction raw report is stale')
    require(evidence.get('unresolvedCount') == 0 and evidence.get('preservesStrictPixelThresholds') is True, 'Clock reproduction unresolved/relaxed')
    require(sorted(x['originalFailure']['frame'] for x in evidence['rows']) == frames, 'Clock reproduction frame coverage incomplete')
    for row in evidence['rows']:
        require(row.get('unresolved') is False and row.get('maximumObservedFrameDifference') == 1, 'Unproven caption boundary deviation')
        require(row['integerTruncatedMilliseconds']['oracle'] - row['integerTruncatedMilliseconds']['producer'] == 1, 'Unproven clock-truncation cause')
        require(row['existingCueMidpointSample']['pass'] is True, 'Caption midpoint does not meet the unchanged strict thresholds')
        require(any(x['frame'] == row['originalFailure']['frame'] + 1 and x['pass'] is True for x in row['existingNeighborSamples']), 'Next caption frame does not pass strict comparison')
        direct = row['existingCueMidpointDirectViewing']
        require(direct.get('openedAtNativeRoiResolution') is True and direct.get('intendedCompleteCaptionReadable') is True and direct.get('typoOrMidCueDisappearanceObserved') is False, 'Direct current caption pixel review incomplete')
        e.check(direct['actualPng'], 'Directly viewed current cue midpoint')
    return raw


def accepted_caption_range_report(report_file, e, cap_sha, timeline_sha, integrity_file, sceneplan_sha, timeline, reports):
    """Verify current changed-range pixels plus hash-identical retained samples.

    This normalizes only the common input/coverage interface. The underlying raw,
    reviewed and range-reuse reports stay unchanged and separately registered.
    """
    report = read(report_file)
    folder = Path(report_file).parent
    reuse_file = folder / 'caption-range-reuse.json'
    reuse = read(reuse_file); inputs = reuse['inputs']
    require(report.get('inputs') == inputs, 'Caption range reviewed/report inputs differ')
    require(inputs['currentMaster']['sha256'] == cap_sha, 'Caption range proof binds another current master')
    require(inputs['currentIntegrity']['sha256'] == e.sha(integrity_file), 'Caption range proof binds another integrity receipt')
    require(inputs['currentScenePlan']['sha256'] == sceneplan_sha, 'Caption range proof binds another composed scene plan')
    for key in ['priorMaster', 'currentMaster', 'priorIntegrity', 'currentIntegrity', 'priorRawCaptionReport',
                'priorReviewedCaptionReport', 'priorSamplePlan', 'priorActualExtraction', 'priorExpectedExtraction',
                'priorClockProof', 'priorScenePlan', 'currentScenePlan', 'implementation']:
        e.check(inputs[key], 'Caption range input ' + key)
    require(inputs['priorMaster']['sha256'] != cap_sha, 'Range reuse must identify the preserved previous master separately')
    stable = inputs['stableInputs']
    require(stable['timeline']['sha256'] == timeline_sha, 'Caption range timeline is stale')
    for key, reference in stable.items():
        e.check(reference, 'Stable caption range input ' + key)
    for kind in ['clean', 'captioned']:
        require(reuse['frameChanges'][kind].get('all217544FramesCompared') is True, 'Incomplete retained-frame comparison: ' + kind)
        for role in ['prior', 'current']:
            e.check(inputs['framehash'][kind][role], 'Caption range actual decoded frame hashes ' + kind + '/' + role)
    require(reuse.get('completionState') == 'all-required-artifacts-written-and-hashed', 'Caption range job did not complete')
    require(bool(reuse.get('completedFiles')), 'Caption range completed artifacts missing')
    completed = {r['file']: r for r in reuse['completedFiles']}
    for reference in completed.values():
        e.check(reference, 'Completed caption range evidence')
    for key in ['actualExtraction', 'expectedExtraction', 'inputCoverage', 'visualReviewTargets', 'repairReviewTargets']:
        e.check(reuse[key], 'Caption range current result ' + key)
    require(reuse.get('newFullMasterDecodePasses') == 0 and reuse['scope'].get('newFullMasterDecodePasses') == 0, 'Range reuse must not conceal a repeated whole-video caption decode')
    require(reuse.get('strictPixelThresholdsChanged') is False and reuse.get('unresolvedFailureCount') == 0 and reuse.get('unresolvedFailures') == [], 'Caption range flags remain unresolved/relaxed')
    raw_file = e.check(report['rawAutomatedReport'], 'Current strict raw caption range report')
    raw = read(raw_file)
    require(raw['inputs'] == inputs and raw.get('captionCueCount') == report.get('captionCueCount') == 588, 'Caption range raw/track coverage differs')
    frames = [50547, 103449, 212868]
    require(raw.get('failureCount') == report.get('rawAutomatedFailureCount') == 3, 'Unexpected current raw caption failure count')
    require(sorted(x['frame'] for x in raw['failures']) == report.get('rawAutomatedFailureFrames') == frames, 'Range exceptions exceed the proven three frames')
    require(report.get('unresolvedFailureCount') == 0 and report.get('strictPixelThresholdsChanged') is False and report.get('reviewedBoundaryCount') == 3, 'Current caption boundary review incomplete')
    prior_raw = read(path(inputs['priorRawCaptionReport']['file']))
    prior_reviewed = read(path(inputs['priorReviewedCaptionReport']['file']))
    accepted_caption_report(prior_reviewed, e)
    require(prior_reviewed['rawAutomatedReport']['sha256'] == inputs['priorRawCaptionReport']['sha256'], 'Prior caption strict report identity differs')
    require(prior_reviewed['reviewedEvidence']['sha256'] == inputs['priorClockProof']['sha256'], 'Prior clock reproduction identity differs')
    require(prior_raw['inputs']['master']['sha256'] == inputs['priorMaster']['sha256'], 'Prior raw pixels belong to another preserved master')
    prior_plan = read(path(inputs['priorSamplePlan']['file']))
    current_plan_file = folder / 'sample-plan.json'
    require(rel(current_plan_file) in completed, 'Current caption sample plan is not in the completed artifact inventory')
    current_plan = read(current_plan_file)
    require(current_plan['samples'] == prior_plan['samples'] and current_plan['nativeFrames'] == prior_plan['nativeFrames'], 'Retained caption/cut sample timing changed')
    require(len(current_plan['samples']) == len(raw['samples']) == len(reuse['samples']) == 2269, 'Caption/cut sample coverage incomplete')
    require(len(current_plan['nativeFrames']) == 1813 and len(reuse['temporalTargets']) == 107, 'Native/motion sample inventory incomplete')
    require([x['frame'] for x in raw['samples']] == [x['frame'] for x in current_plan['samples']], 'Current caption samples missing/reordered')
    for key in stable:
        require(stable[key]['sha256'] == prior_raw['inputs'][key]['sha256'], 'Retained caption contract changed: ' + key)
    require(report['clockExceptions'] == reuse['reusedClockBoundaries'], 'Caption exception rows differ from the completed range proof')
    require(sorted(x['frame'] for x in report['clockExceptions']) == frames, 'Caption clock exception coverage differs')
    clock = read(path(inputs['priorClockProof']['file']))
    prior_rows = {x['originalFailure']['frame']: x for x in clock['rows']}
    scenes = {s['id']: s for s in timeline['scenes']}
    for row in report['clockExceptions']:
        require(row.get('entireSceneDecodedEqualCleanAndCaptioned') is True and row.get('clockExceptionReusedOnlyForThisFrame') is True, 'Clock exception is not supported by whole-scene retained pixels')
        require(row['scene'] in ['v6-12', 'v6-22', 'v6-41'] and row['priorClockRow'] == prior_rows[row['frame']], 'Clock exception has another scene/cause')
        require(len(row['oldMd5']) == 32 and row['oldMd5'] == row['newMd5'], 'Clock exception current decoded pixels differ')
        sc = scenes[row['scene']]
        for kind in ['clean', 'captioned']:
            require(not any(a < sc['endFrame'] and b > sc['startFrame'] for a, b in reuse['frameChanges'][kind]['ranges']), 'A clock-exception scene has changed decoded frames')
    coverage = read(path(reuse['inputCoverage']['file']))
    for key in ['sameKoEnSrtAssCanonicalDisplayedTextAndTiming', 'all250SourceParagraphsReconstructedInEachLanguage', 'fixedBox960x970Font48Max2Lines']:
        require(coverage.get(key) is True, 'Current caption range text/geometry contract incomplete: ' + key)
    reports['captionRangeReuse'] = e.proof(reuse_file)
    reports['captionRangeRaw'] = e.proof(raw_file)
    reports['captionRangePriorReviewed'] = inputs['priorReviewedCaptionReport']
    reports['captionRangeRepairTargets'] = reuse['repairReviewTargets']
    reports['captionRangeVisualTargets'] = reuse['visualReviewTargets']
    return {**raw, 'inputs': {**stable, 'master': inputs['currentMaster']},
            'scope': {**prior_raw['scope'], 'sourceMasterDecodePasses': 0,
                      'comparison': 'Fresh changed-range strict pixels plus identical decoded retained samples; original raw clock flags preserved.'}}


def verify_review(direct, e, cap_sha, timeline_sha, reports):
    require(direct.get('revision') == REV, 'Direct review belongs to another revision')
    require(direct.get('captionedMasterSha256') == cap_sha, 'Direct review does not bind the current captioned master')
    require(direct.get('timelineSha256') == timeline_sha, 'Direct review does not bind the current timeline')
    for name in ['sourceAsr', 'finalMixAsr']:
        row = direct.get(name, {})
        require(row.get('completeTextDirectlyCompared') is True, name + ': full current text comparison pending')
        require(row.get('unresolvedConfirmedContentErrors') == 0, name + ': unresolved content errors')
        evidence_file = e.check(row.get('evidence'), name + ' direct comparison evidence')
        if name == 'finalMixAsr':
            require(e.sha(evidence_file) == reports['finalAsr']['sha256'], 'Final ASR direct review references a different ASR report')
    visual = direct.get('visual', {})
    for key in ['allCaptionCutSamplesReviewed', 'allMotionTargetsReviewed', 'native1080Reviewed', 'mobile375Reviewed']:
        require(visual.get(key) is True, 'Direct visual review pending: ' + key)
    e.check(visual.get('evidence'), 'Direct visual evidence')
    # Sample coverage is required; real-time playback is a separate fact, not a gate.
    require(visual.get('scope') or visual.get('samplingScope'), 'Direct visual review must describe the sampled scope')
    return {
        'scope': copy.deepcopy(visual.get('scope', visual.get('samplingScope'))),
        'realTimeMotionReviewed': visual.get('realTimeMotionReviewed', False),
        'realTimeMotionReview': 'completed only within the separately recorded scope' if visual.get('realTimeMotionReviewed') is True else 'pending; chronological frame-board review is not continuous playback',
        'native1080Reviewed': True, 'mobile375Reviewed': True,
        'allCaptionCutSamplesReviewed': True, 'allMotionTargetsReviewed': True,
        'humanWholeListening': 'pending', 'humanPaceListening': 'pending',
        'humanPronunciationReview': 'pending', 'userReview': 'pending',
    }


def verify_selected_contexts(report_file, e, asr, timeline_sha, reports):
    """Register the one bounded content-evidence batch without calling it listening."""
    context = read(report_file)
    require(context.get('complete') is True and context.get('contextCount') == context.get('recognizedContexts') == 39 and not context.get('missingContexts'), 'Selected encoded paragraph ASR evidence incomplete')
    require(context.get('newAudioDecode') is False and context.get('originalWholeAsrRepeated') is False and context.get('expectedTextPassedToInference') is False, 'Selected paragraph evidence has an unexpected decode/inference scope')
    require(context.get('validatesOriginalFinalTiming') is False and context.get('stitchedParagraphContextCount') == 19, 'Selected paragraph timing/stitching scope must remain explicit')
    require(context['inputs']['timeline']['sha256'] == timeline_sha, 'Selected paragraph contexts use old timing')
    for key, reference in context['inputs'].items():
        e.check(reference, 'Selected paragraph context input ' + key)
    prep = read(e.check(context['preparation'], 'Selected paragraph context preparation'))
    require(prep['inputs'] == context['inputs'], 'Selected paragraph preparation differs from the completed report')
    require(prep['inputs']['decodedFile']['sha256'] == asr['decodedSha256'], 'Selected paragraph contexts use different encoded audio')
    plan = read(path(context['inputs']['plan']['file']))
    require(len(context['contexts']) == len(plan['contexts']) == 39 and [r['id'] for r in context['contexts']] == [r['id'] for r in plan['contexts']], 'Selected paragraph context identities missing/reordered')
    for row, planned in zip(context['contexts'], plan['contexts']):
        require(row['segments48k'] == planned['segments48k'] and row['expectedSpoken'] == planned['expectedSpoken'], 'Selected paragraph source sample mapping/text changed')
        require(0 < row['durationSeconds'] <= 25, 'Selected paragraph context exceeds the approved complete-context length')
        cache = read(e.check({'file': row['cacheFile'], 'sha256': row['cacheSha256']}, 'Actual selected paragraph ASR cache'))
        require(cache.get('status') == 'recognized-context-evidence-only' and cache['text'] == row['recognized'], 'Selected paragraph recognition is not a completed cache')
        require(cache['modelConfigurationSha256'] == prep['modelConfigurationSha256'] and cache['asrMono16kSha256'] == row['asrMono16kSha256'], 'Selected paragraph inference identity differs')
        require(cache.get('expectedTextPassedToInference') is False and cache.get('automaticSpeechPass') is False, 'Selected paragraph ASR must remain unprompted evidence, not speech approval')
    reports['selectedContextAsr'] = e.proof(report_file)
    reports['selectedContextPlan'] = context['inputs']['plan']


def validate(args):
    control = selected()
    e = Evidence()
    t = read(H / 'timeline.json'); timeline_sha = e.sha(H / 'timeline.json')
    require((t.get('revision'), t.get('sceneCount'), t.get('lineCount'), t.get('beatCount')) == (REV, 41, 250, 106), 'Unexpected current lecture structure')
    require((t['width'], t['height'], t['fps'], t['introFrames'], t['outroFrames']) == (1920, 1080, 60, 120, 600), 'Native format/branding/member contract mismatch')
    require(t['totalFrames'] == t['introFrames'] + sum(s['frames'] for s in t['scenes']) + t['outroFrames'], 'Timeline frame sum mismatch')
    require(t.get('actualExplanationRatioEnforced') is False, 'V6 uses concept-sized gameplay without a padding quota')
    script = P / 'script/revision-v6-article-flow/narration.ko.json'; ko = read(script)
    en_script = P / 'script/revision-v6-article-flow/narration.en.json'; read(en_script)
    require(len(ko['scenes']) == 41 and sum(len(s['lines']) for s in ko['scenes']) == 250, 'Current script is not the approved 41-scene/250-line structure')
    require(e.sha(script) == t['inputs']['koSha256'], 'Timeline narration is stale')
    require([s['id'] for s in ko['scenes']] == [s['id'] for s in t['scenes']], 'Script/timeline scenes differ')
    contract = ko['speechContract']['coordinateConvention']
    require(all(x in contract for x in ['left-handed', 'row vectors', 'object-to-upright', 'R=Rz(b)Rx(p)Ry(h)']), 'Unexpected coordinate convention')
    current_pcm_path = O / 'voice/current-pcm.json'; pcm = read(current_pcm_path)
    require(e.sha(current_pcm_path) == t['inputs']['currentPcmMappingSha256'], 'Timeline current PCM mapping is stale')
    require(pcm.get('sceneCount') == 41 and len(pcm['scenes']) == 41, 'Current PCM inventory incomplete')
    require([r['id'] for r in pcm['scenes']] == [s['id'] for s in t['scenes']], 'Current PCM scene order differs')
    for row in pcm['scenes']:
        e.check(row, 'Selected PCM ' + row['id'])
        e.check({'file': row['asrFile'], 'sha256': row['asrSha256']}, 'Selected source ASR ' + row['id'])
    reuse_file = path(args.audio_reuse_report) if args.audio_reuse_report else None
    reuse = read(reuse_file) if reuse_file else None
    required = {
        'timeline': H / 'timeline.json', 'scriptKo': script, 'scriptEn': en_script,
        'currentPcm': current_pcm_path, 'integrity': O / 'qa/integrity.json',
        'audioMix': O / 'audio-build.json', 'sourcePcmProof': O / 'audio/audio-build.json',
        'encodedCaptions': Path(args.caption_report) if args.caption_report else O / 'qa/encoded-captions/caption-output-review.json',
        'finalAsr': Path(args.asr_report) if args.asr_report else (Path(reuse['asrReview']['file']) if reuse else unique_report(O / 'qa/final-mix-asr', 'final-mix-asr-review.json')),
        'audioContinuity': Path(reuse['audioContinuity']['file']) if reuse else O / 'qa/audio-level-continuity.json',
        'directReview': H / 'final-direct-review.json', 'spatial': H / 'spatial-production-review.json',
        'savedScenes': H / 'spatial-saved-scenes.json', 'spatialReadouts': O / 'spatial-clips/readouts/outputs.json',
        'mathAssets': O / 'math/outputs.json', 'scenePlan': O / 'edit/scene-plan.json',
        'captionKo': O / 'captions.ko.srt', 'captionEn': O / 'captions.en.srt',
        'captionAssKo': O / 'captions.ko.ass', 'captionAssEn': O / 'captions.en.ass',
        'descriptionBuild': P / 'publishing/revision-v6-description-build.json',
        'descriptionKo': P / 'publishing/revision-v6-description.ko.txt',
        'descriptionEn': P / 'publishing/revision-v6-description.en.txt',
    }
    required = {k: (v if v.is_absolute() else R / v) for k, v in required.items()}
    reports = {k: e.proof(v) for k, v in required.items()}
    if reuse_file:
        reports['audioReuseOutputs'] = e.proof(reuse_file)
    verify_descriptions(read(required['descriptionBuild']), e, timeline_sha)
    integrity = read(required['integrity']); outputs = integrity.get('outputs', [])
    require(integrity.get('status') == 'technical-integrity-passed', 'Current final output integrity not passed')
    require(integrity['inputs']['timelineSha256'] == timeline_sha, 'Integrity timeline is stale')
    require(integrity['inputs']['mixReceiptSha256'] == reports['audioMix']['sha256'], 'Integrity mix receipt is stale')
    require(integrity.get('exactAACStreamEqual') is True, 'Encoded audio differs between final masters/reference')
    require(sorted(x['kind'] for x in outputs) == ['captioned', 'clean'], 'Integrity needs both current masters')
    by_kind = {x['kind']: x for x in outputs}
    aac = integrity['aacSha256']
    for kind, row in by_kind.items():
        require(path(row['file']) == O / ('euler-' + kind + '.mp4'), 'Unexpected final master path')
        e.check(row, kind + ' final master')
        require((row['width'], row['height'], row['fps'], row['frames']) == (1920, 1080, 60, t['totalFrames']), kind + ': format/frame mismatch')
        require(row.get('startSeconds') == 0 and row.get('audioSampleRate') == 48000 and row.get('audioChannels') == 2, kind + ': audio/start mismatch')
        for key in ['fullDecodePassed', 'audioNullDecodePassed', 'ptsMonotonicAndUniform', 'exactAACStreamEqual', 'audioPacketTimingExactlyEqual']:
            require(row.get(key) is True, kind + ': incomplete integrity check ' + key)
        require(row.get('decodedFrameTimesChecked') == t['totalFrames'], kind + ': decoded frame PTS coverage incomplete')
        require(row['aacSha256'] == aac, kind + ': AAC stream hash differs')
        e.check({'file': row['frameHashFile'], 'sha256': row['frameHashSha256']}, kind + ' decoded frame hash evidence')
        decode = read(path(row['decodeReceipt'])); e.proof(row['decodeReceipt'])
        require(decode.get('fullDecodePassed') is True and decode.get('audioNullDecodePassed') is True, kind + ': decode receipt incomplete')
        pair_path = O / ('euler-' + kind + '.json'); pair = read(pair_path)
        require(e.sha(pair_path) == integrity['inputs']['pairReceiptSha256'][kind], kind + ': assembly receipt stale')
        require(pair.get('sha256') == row['sha256'] and pair['inputs']['timelineSha256'] == timeline_sha, kind + ': assembly/master mismatch')
        require(pair['inputs']['audioSha256'] == integrity['inputs']['audioFileSha256'], kind + ': assembly/audio mismatch')
        require(len(pair['inputs']['files']) == 43, kind + ': 41 scenes plus original intro/outro required')
        for filename, digest in pair['inputs']['files']:
            e.check({'file': filename, 'sha256': digest}, kind + ' actual assembly source')
    preserved = integrity.get('brandingAndMembership', {})
    require(preserved.get('authenticatedAssemblySourceSha256Equal') is True and preserved.get('sourceFrameCountsEqual') is True, 'Original branding/member source identity not proved')
    for name, frames in [('branding', 120), ('membership', 600)]:
        row = preserved['sources'][name]; e.check(row, name + ' identity source')
        require(row['frames'] == frames, name + ': duration changed')
    mix = read(required['audioMix']); source = read(required['sourcePcmProof'])
    require(mix['inputs']['timelineSha256'] == timeline_sha, 'Audio mix timeline stale')
    require(mix['sourcePcmProofSha256'] == reports['sourcePcmProof']['sha256'], 'Original PCM preservation proof stale')
    require(source.get('everyOriginalSamplePreserved') is True and source.get('noOriginalPcmMutation') is True, 'Source sample preservation incomplete')
    gain_path = e.check(mix.get('sourceFixedGainEquivalenceProof'), 'Independent raw-source to fixed-gain placement proof')
    gain = read(gain_path); reports['sourceFixedGain'] = e.proof(gain_path)
    require(gain.get('sceneCount') == 41 and len(gain.get('scenes', [])) == 41, 'Raw-source fixed-gain proof scene coverage incomplete')
    require(gain.get('maximumAbsoluteError', 1) < 2e-6 and gain.get('everySelectedSourceSampleOnceInOrder') is True, 'Raw-source fixed-gain placement not proved')
    require(gain['inputs']['timelineSha256'] == timeline_sha and gain['inputs']['preparationSha256'] == reports['sourcePcmProof']['sha256'], 'Raw-source fixed-gain proof binds old timing/preparation')
    selected_pcm = {row['id']: row for row in pcm['scenes']}
    require({row['id'] for row in gain['scenes']} == set(selected_pcm), 'Raw-source fixed-gain proof scene identities differ')
    for row in gain['scenes']:
        require(row['sourceSha256'] == selected_pcm[row['id']]['sha256'], 'Raw-source fixed-gain proof uses different selected PCM')
        require(row.get('maximumAbsoluteError', 1) < 2e-6 and row.get('everySelectedSourceSampleOnceInOrder') is True, 'Incomplete individual raw-source fixed-gain comparison')
    require(gain.get('resampledSourceSamplesCompared', 0) > 0 and gain['resampledSourceSamplesCompared'] == sum(row['resampledSourceSamplesCompared'] for row in gain['scenes']), 'Raw-source comparison sample coverage incomplete')
    require(mix.get('separatelyAddedBgm') is False, 'Lecture must not have separately added background music')
    require((mix['totalFrames'], mix['totalSamples'], mix['sampleRate'], mix['channels']) == (t['totalFrames'], t['totalFrames'] * 800, 48000, 2), 'Final mix sample/frame contract mismatch')
    require(zero_flags(mix.get('sourceToStemProcessingDropFlags')), 'Unresolved source-to-stem processing drops')
    require(len(mix.get('sourceToFinalNarrationStem', [])) == 41, 'Source-to-final narration coverage incomplete')
    for row in mix['sourceToFinalNarrationStem']:
        require(row.get('entireResampledSourceCompared') is True and row.get('sourceToStemMaximumAbsoluteError', 1) < 2e-6, 'Entire source-to-stem numerical comparison incomplete')
    require(mix.get('finalMixEqualsVoicePlusGameMaximumAbsoluteError', 1) < 2e-6, 'Final mix differs from synchronized stems')
    for row in mix['outputs']:
        e.check(row, 'Current mix output')
    require(e.sha(mix['encodedAudio']) == integrity['inputs']['audioFileSha256'], 'Integrity encoded AAC file is stale')
    for name in ['audioMix', 'encodedAudio', 'narrationStem', 'gameStem']:
        require(any(path(x['file']) == path(mix[name]) for x in mix['outputs']), 'Missing hash-bound mix output: ' + name)
    cap_sha = by_kind['captioned']['sha256']
    selected_captions = read(required['encodedCaptions'])
    if 'currentMaster' in selected_captions.get('inputs', {}):
        captions = accepted_caption_range_report(required['encodedCaptions'], e, cap_sha, timeline_sha,
            required['integrity'], reports['scenePlan']['sha256'], t, reports)
    else:
        captions = accepted_caption_report(selected_captions, e)
    require(captions['inputs']['master']['sha256'] == cap_sha and captions['inputs']['timeline']['sha256'] == timeline_sha, 'Caption QA binds a different master/timeline')
    for key in ['everyKoCueMidpoint', 'everySceneAndPhaseCutAtMinusOneZeroPlusOne', 'expectedSparseGlobalPtsVerified']:
        require(captions['scope'].get(key) is True, 'Caption/cut sample coverage incomplete: ' + key)
    for key, name in [('assKo', 'captionAssKo'), ('srtKo', 'captionKo'), ('assEn', 'captionAssEn'), ('srtEn', 'captionEn')]:
        require(captions['inputs'][key]['sha256'] == reports[name]['sha256'], 'Encoded caption QA track is stale: ' + key)
        require(integrity['inputs']['captions'][Path(required[name]).name]['sha256'] == reports[name]['sha256'], 'Integrity caption track is stale: ' + key)
    asr = read(required['finalAsr'])
    require(asr.get('completeAsrEvidence') is True and asr.get('fullMainBodyCovered') is True, 'Whole final-mix ASR coverage incomplete')
    require(asr.get('sceneCount') == 41 and not asr.get('missingScenes'), 'Whole final-mix ASR scenes incomplete')
    require(asr['inputs']['master']['sha256'] == cap_sha and asr['inputs']['timeline']['sha256'] == timeline_sha, 'ASR binds a different master/timeline')
    require(asr['inputs']['finalMixReceipt']['sha256'] == reports['audioMix']['sha256'], 'ASR mix receipt is stale')
    e.check(asr['preparation'], 'Final ASR preparation')
    e.check(asr['inputs']['extraction'], 'Final ASR shared encoded audio extraction')
    e.check({'file': asr['decodedFile'], 'sha256': asr['decodedSha256']}, 'Final ASR shared decoded audio')
    context_file = path(args.context_asr_report) if args.context_asr_report else O / 'qa/final-mix-contexts/context-asr-review.json'
    verify_selected_contexts(context_file, e, asr, timeline_sha, reports)
    continuity = read(required['audioContinuity'])
    if reuse:
        require(reuse.get('captionedMasterSha256') == cap_sha, 'Audio reuse wrapper binds a different new master')
        require(reuse.get('asrInferenceRun') is False and reuse.get('audioDecodeRun') is False, 'Rebinding must not assert a new decode/recognition')
        for key in ['equivalence', 'extraction', 'preparation', 'audioContinuity', 'asrReview']:
            e.check(reuse[key], 'Current audio reuse ' + key)
        equivalent = read(path(reuse['equivalence']['file']))
        require(all(equivalent.get(k) is True for k in ['exactAACStreamEqual', 'packetTimingExactlyEqual', 'codecAndExtradataExactlyEqual', 'deterministicDecodedAudioEquivalenceEstablished']), 'Audio equivalence proof incomplete')
        require(equivalent.get('aacSha256') == aac, 'Audio reuse AAC differs from current integrity reference')
        require(equivalent['inputs']['currentMaster']['sha256'] == cap_sha and equivalent['inputs']['timeline']['sha256'] == timeline_sha, 'Audio equivalence binds a different current master/timeline')
        require(equivalent['inputs']['audioMixReceipt']['sha256'] == reports['audioMix']['sha256'], 'Audio equivalence mix receipt stale')
        for key, reference in equivalent['inputs'].items():
            e.check(reference, 'Audio equivalence original/current input ' + key)
        require(asr['inputs']['extraction']['sha256'] == reuse['extraction']['sha256'], 'Rebound ASR extraction proof is stale')
        require(continuity['inputs']['extractionSha256'] == reuse['extraction']['sha256'], 'Rebound continuity extraction proof is stale')
        require(continuity['originalNumericReport']['sha256'] == equivalent['inputs']['originalContinuity']['sha256'], 'Rebound numeric evidence provenance changed')
        reports['audioEquivalence'] = reuse['equivalence']
    require(continuity.get('captionedMasterSha256') == cap_sha and continuity['inputs']['timelineSha256'] == timeline_sha, 'Encoded audio continuity binds a different master/timeline')
    require(continuity['inputs']['audioBuildSha256'] == reports['audioMix']['sha256'], 'Encoded audio continuity mix receipt stale')
    require(continuity['inputs']['decodedSha256'] == asr['decodedSha256'], 'Continuity and ASR did not use the same encoded audio extraction')
    require(continuity['inputs']['extractionSha256'] == asr['inputs']['extraction']['sha256'], 'Continuity shared extraction receipt is stale')
    require(continuity.get('status') == 'numeric-analysis-complete-contextual-listening-pending', 'Encoded continuity numerical analysis incomplete')
    require((continuity.get('sampleRate'), continuity.get('channels')) == (48000, 2), 'Encoded continuity audio format mismatch')
    expected_paragraphs = {(s['id'], line['line']) for s in t['scenes'] for line in s['lines']}
    actual_paragraphs = [(row['scene'], row['line']) for row in continuity.get('paragraphs', [])]
    require(len(actual_paragraphs) == 250 and set(actual_paragraphs) == expected_paragraphs, 'Encoded continuity does not cover all current250 paragraphs exactly once')
    expected_joins = [(previous['id'], current['id']) for previous, current in zip(t['scenes'], t['scenes'][1:])]
    actual_joins = [(row['previous'], row['next']) for row in continuity.get('joins', [])]
    require(actual_joins == expected_joins, 'Encoded continuity does not cover all40 current scene joins')
    require({row['scene'] for row in continuity.get('windows', [])} == set(selected_pcm), 'Encoded speech-active window coverage incomplete')
    require(continuity.get('knownMixEqualsStemsMaximumError', 1) < 2e-6, 'Encoded review known-reference mix is inconsistent')
    require(zero_flags(continuity.get('sourceToStemProcessingDropFlags')), 'Encoded audio continuity has source processing drops')
    for key in ['activeProcessingTransferFlags', 'encodedReferenceMismatchRanges']:
        require(continuity.get(key) == [], 'Unresolved encoded audio continuity flags: ' + key)
    scope = verify_review(read(required['directReview']), e, cap_sha, timeline_sha, reports)
    spatial = read(required['spatial']); require(spatial['capture']['clipCount'] == 49 and spatial['capture']['frames'] == 19200, 'Finite spatial source coverage incomplete')
    require(spatial['savedEditableScenes']['count'] == 27, 'Editable Unity scene inventory incomplete')
    e.check({'file': spatial['capture']['receipt'], 'sha256': spatial['capture']['sha256']}, 'Actual spatial capture')
    e.check({'file': spatial['savedEditableScenes']['proof'], 'sha256': spatial['savedEditableScenes']['sha256']}, 'Saved editable scenes')
    saved = read(required['savedScenes'])
    require(saved['actualEditorSave']['totalSceneFiles'] == 27 and len(saved['scenes']) == 27, 'Saved scene files are incomplete')
    for row in saved['scenes']:
        e.check(row, 'Actual editable Unity scene')
    for name, count in [('spatialReadouts', 49), ('mathAssets', 54)]:
        require(len(read(required[name])['outputs']) == count, name + ' inventory incomplete')
    sceneplan = read(required['scenePlan'])
    require(sceneplan['timelineSha256'] == timeline_sha and len(sceneplan['scenes']) == 41, 'Current composed scene plan incomplete/stale')
    for filename, digest in sceneplan['sourceAssetFiles'].items():
        e.check({'file': filename, 'sha256': digest}, 'Actual composed source asset')
    return dict(control=control, evidence=e, timeline=t, timelineSha256=timeline_sha, script=ko,
                reports=reports, outputs=by_kind, integrity=integrity, mix=mix, captions=captions,
                source=source, scope=scope, aacSha256=aac, saved=saved, sceneplan=sceneplan)


def archive_once(document, field, snapshot, identity):
    history = document.setdefault(field, [])
    require(isinstance(history, list), 'Unexpected history schema: ' + field)
    if not any(row.get('identity') == identity for row in history):
        history.append({'identity': identity, 'state': copy.deepcopy(snapshot)})


def updated_script_record(row):
    row = copy.deepcopy(row)
    row.update(status='produced-to-local-final-review', authorizedScope='Selected full V6 production through local user review; no platform/next video.',
               newTts='complete-current-selected-41-source-PCM', newVideo='complete-current-FHD60-clean-and-captioned',
               humanReview='pending', actualSpeechPaceAndListening='pending; automated/direct-text checks are not whole human listening',
               conventionChange='V6 narration, formulas, captions and authored geometry use the same left-hand/row/object-upright convention; V5 remains historical.')
    return row


def listening_priority_notes(timeline):
    scenes = {s['id']: s for s in timeline['scenes']}
    def clock(scene, line):
        s = scenes[scene]
        matches = [r for r in s['lines'] if r['line'] == line]
        require(len(matches) == 1, 'Listening priority source line missing')
        seconds = s['startFrame'] / timeline['fps'] + matches[0]['start']
        whole = int(seconds + 1e-9)
        return f'{whole // 60:02d}:{whole % 60:02d}'
    return [
        f'{clock("v6-26", 7)}·{clock("v6-27", 4)} 범위 조건(안일 때만/범위 밖) 발음 최종 청취 필요 — ASR만으로 실제 발음 오류 여부 미확정',
        f'{clock("v6-33", 3)}·{clock("v6-33", 4)}·{clock("v6-40", 4)} 용어(라디안/정규화/세계 좌표) 발음 최종 청취 필요',
    ]


def documents(v, originals, collected):
    docs = copy.deepcopy(originals); stamp = now(); t = v['timeline']; reports = v['reports']; cap = v['outputs']['captioned']
    status = 'ready-for-local-user-review' if collected else 'technical-production-complete-local-collection-pending'
    review = dict(policyId='local-final-review-before-youtube-v1', provider='local-filesystem', directory='output/' + SLUG,
                  captioned='output/' + SLUG + '/' + SLUG + '.captioned.mp4', index='output/' + SLUG + '/index.html',
                  version=REV, sha256=cap['sha256'], sizeBytes=path(cap['file']).stat().st_size,
                  status=status, filesCollectedAndHashVerified=collected, linksReady=collected,
                  humanReview='pending', userReviewMessage=None, reviewedAt=None, deliveredAt=None,
                  driveUploadRequired=False, driveUploadOnExplicitRequestOnly=True)
    summary = dict(schemaVersion=6, slug=SLUG, revision=REV, updatedAt=stamp, status=status,
                   outputs=[copy.deepcopy(v['outputs'][k]) for k in ['clean', 'captioned']],
                   evidence=copy.deepcopy(reports), frames=t['totalFrames'], durationSeconds=t['seconds'], fps=60,
                   dimensions=[1920, 1080], exactAACStreamEqual=True, aacSha256=v['aacSha256'],
                   addedBackgroundMusic=False, synchronizedGameSound=True, reviewScope=v['scope'],
                   humanWholeListening='pending', humanPaceListening='pending', humanPronunciationReview='pending',
                   userReview='pending', localReview=review, noPlatformMutation=True, automaticNextVideo=False)
    p = docs['project']; old_id = p.get('revision', {}).get('id', 'previous')
    if old_id != REV:
        snapshot = {k: p.get(k) for k in ['revision', 'paths', 'finalRender', 'video', 'lecture', 'audio', 'tts', 'editing', 'visualStyle', 'engines', 'rendererDecision', 'approvals']}
        snapshot['deliveryReview'] = p.get('delivery', {}).get('review')
        archive_once(p, 'completedRevisionHistory', snapshot, old_id)
    p.update(updatedAt=stamp, status=status, publishReady=False)
    p['paths'].update(script=reports['scriptKo']['file'], scriptEn=reports['scriptEn']['file'],
        publishingKo=reports['descriptionKo']['file'], publishingEn=reports['descriptionEn']['file'],
        videoClean=v['outputs']['clean']['file'], videoBurnedCaptions=cap['file'], captionsKo=reports['captionKo']['file'], captionsEn=reports['captionEn']['file'],
        audioMix=rel(path(v['mix']['encodedAudio'])), editorAudioMix=rel(path(v['mix']['audioMix'])), narration=rel(path(v['mix']['narrationStem'])),
        audioReport=reports['audioContinuity']['file'], renderReport=rel(FILES['qa']), timeline=reports['timeline']['file'], footageCuts=reports['timeline']['file'],
        productionData=reports['scenePlan']['file'], productionBuilder=rel(H / 'composite.py'), manimProject=rel(H / 'math-clips.py'),
        unityScenePlan=rel(H / 'spatial-plan.json'), productionReadme=rel(H / 'spatial-readme.md'))
    p['delivery']['review'] = copy.deepcopy(review)
    p['publishing'].update(currentRevision=REV, localReview=copy.deepcopy(review), finalUserReviewRequired=True,
                           finalReviewProvider='local-filesystem', driveFinalReviewRequired=False)
    p['publishing']['currentRevisionUploaded'] = False
    p['publishing']['currentRevisionPublishingMetadata'] = 'prepared-local-only; Studio save pending'
    p['publishing']['currentRevisionDescriptionBuild'] = reports['descriptionBuild']
    p['revision'] = dict(id=REV, selectedAt=v['control']['newProductionAuthorization']['selectedOn'],
                         scope=v['control']['newProductionAuthorization']['scope'], previousCompletedRevision=old_id if old_id != REV else p['revision'].get('previousCompletedRevision'),
                         baselineVideoId=p['publishing'].get('baseline', {}).get('videoId'), baselineKept=True,
                         localMasterSha256=cap['sha256'], humanFinalReview='pending')
    p['video'].update(width=1920, height=1080, fps=60, durationSeconds=t['seconds'])
    p['visualStyle'] = 'research-black-v1'
    p['engines'] = ['Unity-authored-spatial-scenes', 'manim-community', 'ffmpeg-final-composition']
    p['lecture']['contract'] = dict(handedness='left', vector='row', transform='object-to-upright',
        axes='+X right/+Y up/+Z forward; positive left-hand rotations; +h:Z→X, +p:Z→-Y, +b:Y→-X.',
        order='Intrinsic moving body Y-X-Z; R=Rz(b)Rx(p)Ry(h), equivalent extrinsic fixed Z-X-Y.',
        sourceConvention=v['script']['speechContract']['coordinateConvention'],
        units='Narrative examples in degrees; rotation vectors and code explicitly radians.', engineMapping='Unity column operation is the transpose of the displayed row matrix; no Z reflection.')
    p['lecture']['backgroundMusic'] = False
    p['rendererDecision'].update(unityEditor=v['saved']['actualEditorSave']['editor'],
        reason='Detailed spatial object/upright frames and authored rotation geometry use Unity; calculations and code use Manim; self-authored footage remains explanation.')
    edit = p['editing']; edit.update(targetGameplayShare=None, targetExplanationShare=None, gameplayShareRange=None,
        ratioPolicy=t['ratioPolicy'], ratioPolicyVersion='lecture-concept-sized-game-examples-v1', actualGameplayShare=t['actualFrames']/t['bodyFrames'],
        actualGameplaySeconds=t['actualFrames']/60, actualCommercialGameplaySeconds=t['actualFrames']/60, actualExplanationSeconds=t['explanationFrames']/60,
        finalBodyFrames=dict(total=t['bodyFrames'], actual=t['actualFrames'], explanation=t['explanationFrames'], ratioEnforced=False),
        timingStatus='current-v6-measured-and-verified', exampleSecondsPolicy='Concept-matched actual actions once at native speed; no ratio quota.',
        explanationStyle='Unity actual authored rotation geometry; Manim mathematical/code derivations; timed finite motions and current captions.')
    edit['exampleExpansion'] = dict(policy='not-used-for-selected-v6', preserveExplanationContent=True, paddingAllowed=False)
    p['audio'].update(mixStatus='current-encoded-numerical-and-ASR-reviewed-human-whole-listening-pending',
                      currentMixReceipt=reports['audioMix'], currentContinuityReview=reports['audioContinuity'], bgmPlacement='none')
    p['audio']['backgroundMusic'].update(enabled=False, required=False, policy='lecture-no-added-bgm-standard-game-audio-v3')
    p['tts'].update(currentManifest=rel(H / 'voice-tts-manifest.json'), currentPcmMapping=reports['currentPcm'],
                    outputDir=rel(O / 'voice'), filenameStem='euler-article-flow-v6', renderMode='selected-current-source-scenes')
    p['approvals'].update(humanListening='pending', humanPaceListening='pending', humanPronunciationReview='pending',
                          visualPixelReview='direct current native/375 chronological sample boards; see scoped evidence',
                          privateUpload='not authorized for this V6 master before its local user review')
    p['finalRender'] = dict(status=status, revision=REV, currentRevisionComplete=True, durationSeconds=t['seconds'], frames=t['totalFrames'],
        fps=60, width=1920, height=1080, qa=rel(FILES['qa']), integrity=reports['integrity'],
        renderer='Unity' + v['saved']['actualEditorSave']['editor'] + ' built-in isolated capture; canonical URP17.6 editable source; Manim/FFmpeg composition',
        backgroundMusic=False, actualGames=len({c['sourceId'] for c in t['cuts']}), independentGameplayCuts=len(t['cuts']),
        sceneCount=41, teachingBeats=106, finiteVisuals=dict(Manim=54, Unity=49, actualGameplay=4),
        openItems=['Whole human listening, pace and pronunciation review pending', 'Current complete local master user review pending',
                   'Continuous real-time moving review pending where not separately documented', 'YouTube upload/settings not performed for V6',
                   *listening_priority_notes(t)])
    if 'pendingScriptRevision' in p:
        p['pendingScriptRevision'] = updated_script_record(p['pendingScriptRevision'])
    plan = docs['plan']
    if plan.get('revision') != REV:
        archive_once(plan, 'previousProductionRevisions', {k: plan.get(k) for k in ['revision', 'selectedRevision', 'format', 'scenes', 'audio', 'contentReview', 'representativePixelPreflight', 'finalReviewDelivery', 'visualRevision']}, plan.get('revision', 'previous'))
    plan.update(revision=REV, updatedAt=stamp, status=status)
    plan['format'].update(width=1920, height=1080, fps=60, actualShare=None, explanationShare=None, ratioEnforced=False,
                          measuredActualFrames=t['actualFrames'], measuredExplanationFrames=t['explanationFrames'], totalFrames=t['totalFrames'], durationSeconds=t['seconds'])
    plan['selectedRevision'] = dict(id=REV, authorization=copy.deepcopy(v['control']['newProductionAuthorization']), stage=status,
        currentScript=reports['scriptKo']['file'], bilingualScript=reports['scriptEn']['file'], timeline=reports['timeline']['file'],
        coordinateContract=p['lecture']['contract'], sourceBackbone='Actual supplied primary lesson8.3–8.4, source-order map preserved',
        noAddedBgm=True, ratioEnforced=False, previousCompleteMasterPreserved=True, evidence=copy.deepcopy(reports))
    plan['currentProduction'].update(status=status, timeline=reports['timeline'], finalOutputs=summary['outputs'], evidence=copy.deepcopy(reports),
                                     humanWholeListening='pending', humanPaceListening='pending', userReview='pending')
    composed = {s['id']: s for s in v['sceneplan']['scenes']}
    script_scenes = {s['id']: s for s in v['script']['scenes']}
    plan['scenes'] = [dict(id=s['id'], title=script_scenes[s['id']]['title'], articleSection=script_scenes[s['id']]['articleSection'],
        globalStartFrame=s['startFrame'], frames=s['frames'],
        script=dict(file=reports['scriptKo']['file'], sceneId=s['id']),
        composition=dict(file=reports['scenePlan']['file'], sceneId=s['id']),
        teachingBeats=[b['id'] for b in s['teachingBeats']],
        rendererRoles=sorted({p['renderer'] for p in composed[s['id']]['phases'] if p.get('renderer')}),
        sourceKinds=sorted({p['sourceKind'] for p in composed[s['id']]['phases'] if p.get('sourceKind')}),
        transitionToNext=script_scenes[s['id']].get('transitionToNext'), evidence=reports['directReview']) for s in t['scenes']]
    plan['contentReview'] = reports['directReview']
    plan['representativePixelPreflight'] = dict(currentFinalReview=reports['directReview'],
        scope=v['scope'], formerPreflightPreservedInHistory=True)
    plan['visualRevision'] = dict(id=REV, completeEncodedMaster=cap['file'], masterSha256=cap['sha256'],
        evidence=copy.deepcopy(reports), scope=copy.deepcopy(v['scope']))
    plan['audio'] = dict(addedBackgroundMusic=False, gameAudioTargetLufs=-23, narrationTargetLufs=-16,
        selectedRawPcm=reports['currentPcm'], sourcePcmPreserved=reports['sourcePcmProof'], finalMix=reports['audioMix'],
        review=reports['audioContinuity'], narrationUnchangedFromV5=False,
        gameSourceLimit='Original synchronized game tracks retained where present; native silent recordings remain silent; no effects-only isolation claim.',
        humanWholeListening='pending', humanPaceListening='pending', humanPronunciationReview='pending')
    plan['finalReviewDelivery'].update(status=status, version=REV, localSha256=cap['sha256'], directory=review['directory'],
        captionedPath=review['captioned'], sizeBytes=review['sizeBytes'], filesCollectedAndHashVerified=collected,
        localPlaybackAndIntegrityEvidence=reports['integrity'], userReviewMessage=None, reviewedAt=None)
    if 'scriptRevision' in plan:
        plan['scriptRevision'] = updated_script_record(plan['scriptRevision'])
    plan['articleFaithfulTeaching'].update(evidenceScope='Current script, source-text review, actual generated PCM/current ASR, native FHD60 output, sampled encoded visuals and numerical integrity. Whole listening/continuous playback/user approval are not inferred.',
        existingScenes='V5 retained as history; current V6 left-hand/row/object-upright scenes and captions migrated together.', ratio=t['ratioPolicy'], currentEvidence=copy.deepcopy(reports))
    checkpoint = docs['checkpoint']
    if checkpoint.get('revision') != REV:
        archive_once(checkpoint, 'previousMasters', dict(revision=checkpoint.get('revision'), currentMaster=checkpoint.get('currentMaster'),
            delivery=checkpoint.get('delivery'), visualRevisionEvidence=checkpoint.get('visualRevisionEvidence')), checkpoint.get('revision', 'previous'))
    checkpoint.update(updatedAt=stamp, revision=REV, revisionUnderWork=REV, stage=status, runningJob=None,
        currentMaster=dict(outputs={k: {'file': row['file'], 'sha256': row['sha256']} for k, row in v['outputs'].items()}, frames=t['totalFrames'], durationSeconds=t['seconds'],
            dimensions=[1920,1080], fps=60, additionalBgm=False, actualGames=len({c['sourceId'] for c in t['cuts']}), status=status),
        nextAction='Deliver complete local folder/captioned MP4 links for user review; preserve old Drive/private YouTube. No upload or next video.',
        localReview=copy.deepcopy(review), visualRevisionEvidence=copy.deepcopy(reports), blockers=[], automaticNextVideo=False,
        activeProduction=dict(revision=REV, status=status, timelineFrames=t['totalFrames'], timelineSeconds=t['seconds'], timelineSha256=v['timelineSha256'],
            captions=v['captions']['captionCueCount'], finiteVisualsComplete=dict(Manim=54, Unity=49, actualGameplay=4),
            newMasterExists=True, humanListening='pending', humanPaceListening='pending', userReview='pending', currentEvidence=copy.deepcopy(reports)))
    # Old remote delivery fields remain byte-for-byte facts for their old hash.
    checkpoint['delivery'].update(localReview=copy.deepcopy(review), currentLocalMasterSha256=cap['sha256'], currentLocalRevision=REV,
        currentRevisionDriveUploaded=False, historicalDriveFieldsReferToRevision='tracked-gizmos-code-colors-v5', driveUploadRequired=False,
        fourOutputs=rel(P / 'production/delivery-output.json') if collected else None, filesCollectedAndHashVerified=collected)
    checkpoint['productionPreparation'].update(stage=status, wholeSourceHumanListening='pending', currentFrameCount=t['totalFrames'], currentEvidence=copy.deepcopy(reports))
    if 'pendingScriptRevision' in checkpoint:
        checkpoint['pendingScriptRevision'] = updated_script_record(checkpoint['pendingScriptRevision'])
    ledger = docs['ledger']
    if ledger.get('currentOutput', {}).get('revision') != REV:
        previous = ledger.setdefault('previousOutputs', [])
        prior = ledger.get('currentOutput')
        if prior and not any(x.get('revision') == prior.get('revision') for x in previous):
            previous.append(copy.deepcopy(prior))
    ledger.update(revision=REV, updatedAt=stamp, currentOutput=copy.deepcopy(summary), currentLocalReview=copy.deepcopy(review),
                  reviewProvider='local-filesystem', humanWholeListening='pending', activeProduction=copy.deepcopy(checkpoint['activeProduction']))
    check = dict(id=REV + '-final-technical-and-scoped-visual', name='V6 current output technical/text/encoded-pixel sample review',
                 status='pass-with-recorded-scope; human listening and local user review pending', evidence=copy.deepcopy(reports), scope=copy.deepcopy(v['scope']))
    ledger['checks'] = [x for x in ledger['checks'] if x.get('id') != check['id']] + [check]
    if 'pendingScriptRevision' in ledger:
        ledger['pendingScriptRevision'] = updated_script_record(ledger['pendingScriptRevision'])
    worklist = docs['worklist']; row = next(x for x in worklist['rows'] if x.get('id') == 'M04')
    require(row.get('slug') == SLUG, 'M04 worklist identity changed')
    row.update(productionComplete=True, productionStatus='V6 전체 완성 · 1080p60 · 41씬 / 한영 자막',
        reviewStatus='기술 무결성·전체 ASR 텍스트·현재 자막/컷 및 동작 표본 검수 완료 · 전체 청취/사용자 검수 대기',
        humanApproval='V6 전체 로컬 완성본 최종 검수 전', platformStatus='기존 V5 Drive·비공개 YouTube 보존 · V6 업로드 안 함',
        executionStatus='로컬 검수본 준비 완료 · 사용자 확인 대기' if collected else '영상 기술 완료 · 로컬 4종 수집 대기',
        localMasterAvailable=True, localReview=copy.deepcopy(review), driveUploadRequired=False, latestRulesPassed=None,
        technicalReview=copy.deepcopy(reports), currentRevision=REV,
        notes='V6 글 순서·왼손/행벡터/물체→직립 규약으로 전체 재제작. 게임 예시는 필요한 실제 동작만; 비율 강제 없음. 별도 BGM 없음. 원본 게임음·기존 브랜드/회원 영상 보존. 시간순 표본 검토는 연속 재생/전체 청취 승인과 구분. 사용자 검수 전 업로드·다음 편 진행 없음.')
    for ref in [rel(FILES['qa']), reports['integrity']['file'], reports['directReview']['file']]:
        if ref not in row['evidence']:
            row['evidence'].append(ref)
    if 'pendingScriptRevision' in row:
        row['pendingScriptRevision'] = updated_script_record(row['pendingScriptRevision'])
    worklist['updatedAt'] = stamp
    require([x for x in originals['worklist']['rows'] if x.get('id') != 'M04'] == [x for x in worklist['rows'] if x.get('id') != 'M04'], 'Unrelated worklist rows changed')
    docs['qa'] = summary
    return docs


def collected_current(v):
    receipt = P / 'production/delivery-output.json'
    if not receipt.is_file():
        return False
    d = read(receipt)
    if d.get('slug') != SLUG or d.get('directory') != 'output/' + SLUG:
        return False
    sources = {'captioned.mp4': v['outputs']['captioned']['file'], 'clean.mp4': v['outputs']['clean']['file'],
               'ko.srt': v['reports']['captionKo']['file'], 'en.srt': v['reports']['captionEn']['file']}
    by_name = {x['name']: x for x in d.get('files', [])}
    for suffix, source in sources.items():
        name = SLUG + '.' + suffix; row = by_name.get(name); target = R / 'output' / SLUG / name
        if not row or not target.is_file() or row.get('sha256') != v['evidence'].sha(source):
            return False
        if row.get('source') != source or v['evidence'].sha(target) != row['sha256']:
            return False
    return (R / 'output' / SLUG / 'index.html').is_file()


def atomic_write(p, value):
    data = json.dumps(value, ensure_ascii=False, indent=2) + '\n'
    tmp = p.with_name(p.name + '.finalize-' + str(os.getpid()) + '.tmp')
    require(not tmp.exists(), 'Temporary registration file already exists: ' + str(tmp))
    try:
        tmp.write_text(data, encoding='utf-8')
        os.replace(tmp, p)
    finally:
        if tmp.exists():
            tmp.unlink()


def run(args):
    v = validate(args); originals = {k: read(p) for k, p in FILES.items()}
    before = {p: p.read_bytes() for p in FILES.values()}
    collected = collected_current(v)
    docs = documents(v, originals, collected)
    print(json.dumps(dict(status='validated-only' if not args.run else 'validated-for-registration',
        frames=v['timeline']['totalFrames'], seconds=v['timeline']['seconds'], captionedSha256=v['outputs']['captioned']['sha256'],
        cleanSha256=v['outputs']['clean']['sha256'], collectedCurrent=collected, reports=v['reports'], reviewScope=v['scope'],
        wouldWrite=[rel(p) for p in FILES.values()], collectorRequested=args.collect, noMediaDecodeRenderOrAsr=True), ensure_ascii=False, indent=2))
    if not args.run:
        return
    selected(); v['evidence'].unchanged()
    for p, raw in before.items():
        require(p.read_bytes() == raw, 'Metadata changed during validation; re-run rather than overwrite: ' + rel(p))
    # The collector reads project.paths. Register these only after validation;
    # on collector failure restore the exact original project config and stop.
    staged_project_bytes = None
    if args.collect and not collected:
        atomic_write(FILES['project'], docs['project'])
        staged_project_bytes = FILES['project'].read_bytes()
        try:
            result = subprocess.run(['node', 'scripts/collect-video-output.cjs', SLUG], cwd=R, check=False)
            require(result.returncode == 0, 'Established collector failed; other records not finalized')
            collected = collected_current(v)
            require(collected, 'Four collected output hashes do not match the validated current sources')
        except BaseException:
            FILES['project'].write_bytes(before[FILES['project']])
            raise
        docs = documents(v, originals, True)
    selected(); v['evidence'].unchanged()
    for key, p in FILES.items():
        if key == 'project' and staged_project_bytes is not None:
            require(p.read_bytes() == staged_project_bytes, 'Project changed during collection')
        else:
            require(p.read_bytes() == before[p], 'Concurrent metadata update: ' + rel(p))
    for key, p in FILES.items():
        atomic_write(p, docs[key])
    result = subprocess.run([sys.executable, 'scripts/render-video-worklist.py'], cwd=R, check=False)
    require(result.returncode == 0, 'Worklist rendering failed; JSON records saved, rendered document pending')
    receipt = dict(schemaVersion=1, revision=REV, status=docs['qa']['status'], completedAt=now(),
        implementationSha256=v['evidence'].sha(Path(__file__)), inputs=copy.deepcopy(v['reports']),
        masterSha256=v['outputs']['captioned']['sha256'], collectedCurrent=collected,
        records=[v['evidence'].proof(p) for p in FILES.values()], worklistDocument=v['evidence'].proof(R / 'docs/VIDEO_WORKLIST.md'),
        otherWorklistRowsPreserved=True, platformStatesPreserved=True, platformActions=0,
        humanWholeListening='pending', humanPaceListening='pending', humanPronunciationReview='pending', userReview='pending',
        realTimeMotionReviewed=v['scope']['realTimeMotionReviewed'], realTimeMotionReview=v['scope']['realTimeMotionReview'])
    atomic_write(H / 'finalization-receipt.json', receipt)
    print('Registered current M04 V6 local records. User review/listening remain pending. No platform action.')


def self_test():
    # No file writes, collector invocation, media access or future success receipt.
    d = {'previousOutputs': []}; archive_once(d, 'previousOutputs', {'x': 1}, 'v5'); archive_once(d, 'previousOutputs', {'x': 2}, 'v5')
    require(len(d['previousOutputs']) == 1, 'History deduplication failed')
    require(zero_flags(0) and zero_flags([]) and not zero_flags(None) and not zero_flags([1]), 'Flag validation failed')
    class FakeEvidence:
        def check(self, reference, label):
            require(reference == {'file': 'f', 'sha256': 's'}, label); return 'f'
        def sha(self, value): return 's'
    direct = dict(revision=REV, captionedMasterSha256='c', timelineSha256='t',
        sourceAsr=dict(completeTextDirectlyCompared=True, unresolvedConfirmedContentErrors=0, evidence={'file':'f','sha256':'s'}),
        finalMixAsr=dict(completeTextDirectlyCompared=True, unresolvedConfirmedContentErrors=0, evidence={'file':'f','sha256':'s'}),
        visual=dict(allCaptionCutSamplesReviewed=True, allMotionTargetsReviewed=True, native1080Reviewed=True, mobile375Reviewed=True,
                    scope='107 finite motions, five chronological frame samples each; no continuous playback claim', evidence={'file':'f','sha256':'s'}, realTimeMotionReviewed=False))
    scope = verify_review(direct, FakeEvidence(), 'c', 't', {'finalAsr': {'sha256':'s'}})
    require(scope['realTimeMotionReviewed'] is False and scope['humanWholeListening'] == 'pending', 'Sample review must not turn into playback/listening approval')
    rejected = 0
    for field, value in [('captionedMasterSha256', 'stale'), ('timelineSha256', 'stale')]:
        broken = copy.deepcopy(direct); broken[field] = value
        try: verify_review(broken, FakeEvidence(), 'c', 't', {'finalAsr': {'sha256':'s'}})
        except ValueError: rejected += 1
    for section, field, value in [('sourceAsr','completeTextDirectlyCompared',False), ('finalMixAsr','unresolvedConfirmedContentErrors',1), ('visual','scope','')]:
        broken = copy.deepcopy(direct); broken[section][field] = value
        try: verify_review(broken, FakeEvidence(), 'c', 't', {'finalAsr': {'sha256':'s'}})
        except ValueError: rejected += 1
    require(rejected == 5, 'Incomplete/stale evidence rejection failed')
    print('CPU self-test passed: five stale/incomplete reviews rejected; sampled motion accepted without false real-time/listening approval. Files/media changed:0.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--check', action='store_true', help='Default: validate current evidence, do not write')
    mode.add_argument('--run', action='store_true', help='Root-only final registration after current reports are complete')
    parser.add_argument('--collect', action='store_true', help='With --run, use established four-output collector if hashes are not already current')
    parser.add_argument('--caption-report', help='Explicit current caption-output-review.json path if non-default')
    parser.add_argument('--asr-report', help='Explicit current final-mix-asr-review.json path if multiple preserved attempts exist')
    parser.add_argument('--audio-reuse-report', help='Current audio-reuse/<old>--<new>/outputs.json; validates preserved decoded/ASR/continuity chain')
    parser.add_argument('--context-asr-report', help='Completed bounded39-paragraph final encoded ASR evidence; defaults to current V6 context report')
    parser.add_argument('--self-test', action='store_true', help='Pure CPU synthetic checks; no source/output mutation')
    args = parser.parse_args()
    if args.self_test:
        self_test(); return
    require(not args.collect or args.run, '--collect requires explicit --run')
    run(args)


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    try:
        main()
    except (ValueError, KeyError, FileNotFoundError) as exc:
        print('Registration stopped: ' + str(exc), file=sys.stderr)
        raise SystemExit(2)
