"""Bind completed, finite internal checks to the exact local review master."""
from pathlib import Path
import datetime
import importlib.util

H = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('v8_quality_common', H / 'common.py')
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)


def evidence(path):
    return dict(file=c.rel(path), sha256=c.sha(path))


def main():
    c.authorized()
    master = c.read(c.O / 'edit/master-build.json')
    selected = next(x for x in master['outputs'] if x['kind'] == 'captioned')
    digest = selected['sha256']
    assert c.sha(c.R / selected['file']) == digest
    decode = c.read(c.O / 'qa/decode-clock.json')
    assert decode['allExact'] and len(decode['results']) == 2
    for row in decode['results']:
        assert row['sha256'] == c.sha(c.R / row['file'])
        assert row['completeSoftwareDecode'] and row['errorCount'] == 0
        assert row['frames'] == master['frames'] == 90288 and row['rate'] == '60/1'
    paths = [c.O / 'qa/final-unity-math-visual-review.json',
             c.O / 'qa/final-caption-game-pixel-review.json']
    for path in paths:
        report = c.read(path)
        assert report['masterSha256'] == digest and report['unresolvedIssueCount'] == 0
        assert report['unresolvedIssues'] == []
    bounds = c.read(c.O / 'qa/caption-pixels-bounds.json')
    assert bounds['masterSha256'] == digest and bounds['all475Checked'] and not bounds['issues']
    pixels = c.read(c.O / 'qa/caption-pixels-review.json')
    assert pixels['masterSha256'] == digest and pixels['extractedFrames'] == 757 and pixels['missingFrames'] == 0
    audio = c.read(c.O / 'audio/final-aac-content-review.json')
    levels = c.read(c.O / 'audio/final-aac-level-review.json')
    assert audio['masterSha256'] == levels['masterSha256'] == digest
    assert audio['all76ParagraphsDirectlyCompared'] and audio['criticalFractionAndMatrixSignsResolved']
    assert audio['verdict'].startswith('TECHNICAL_AUDIO_INTEGRITY_PASS')
    assert levels['actualFinalMasterBindingComplete'] and levels['measuredVoicedSampleShift'] == 0
    assert levels['encodedTransferCandidateWindows'] == levels['decodedSamplesAtOrAboveFullScale'] == 0
    assert audio['approvedScriptSha256'] == c.sha(c.S / 'narration.ko.json')
    paths += [c.O / p for p in ['qa/decode-clock.json', 'qa/visual-proof.json',
        'qa/caption-pixels-review.json', 'qa/caption-pixels-bounds.json',
        'qa/root-targeted-visual-review.json', 'audio/final-aac-content-review.json',
        'audio/final-aac-level-review.json', 'audio/final-context-review.json',
        'audio/measured-mix-focus-review.json', 'edit/clock-repair/repair.json',
        'mix/mix-report.json']]
    paths += [c.P / 'planning/revision-v8-orientation-matrix' / p
              for p in ['coverage-audit.json', 'technical-audit.json']]
    result = dict(revision='orientation-matrix-v8', masterSha256=digest,
        master=selected['file'], technicalStatus='passed',
        technicalScope='Complete file decoding and frame clocks; finite actual-pixel review; source/math coverage; actual AAC ASR and measured level continuity. Not whole subjective listening.',
        scope='Approved article8.1–8.2.5 only', approvedScriptSha256=audio['approvedScriptSha256'],
        durationSeconds=1504.8, frames=90288, dimensions=[1920, 1080], fps=60,
        evidence=[evidence(p) for p in paths], unresolvedTechnicalIssues=[],
        actualWholeListening='pending', humanFinalReview='pending', actualUserReview=None,
        limitations=audio['limitations'] + ['Still contacts and targeted native clips do not establish human viewing of every final frame.'],
        platformMutation=False, automaticNextVideo=False,
        recordedAt=datetime.datetime.now(datetime.timezone.utc).isoformat())
    c.save(c.O / 'qa/quality-review.json', result)
    c.save(H / 'quality-review.json', result)
    print('Bound completed internal checks to exact master; user viewing/listening remains pending.')


if __name__ == '__main__':
    main()
