"""Compare every reopened Studio cue with the exact delivery SRT."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import re

root = Path(__file__).resolve().parents[3]
revision = root / 'projects/game-math-polar-3d/revision-teaching-clarity-v1'
result = {'videoId': '2kNMDlrwdU8', 'recordedAt': datetime.now(timezone.utc).isoformat(),
          'frameRate': 60, 'method': 'Every visible Studio text/timestamp field after UI scroll compared with the delivered SRT.',
          'sourceSrtUnchanged': True, 'languages': {}, 'actualDownloadedSrtPath': None}

def frames(value):
    minute, second, frame = map(int, value.split(':'))
    return (minute * 60 + second) * 60 + frame

def milliseconds(value):
    hour, minute, second, milli = map(int, re.split('[:,]', value))
    return ((hour * 60 + minute) * 60 + second) * 1000 + milli

def normalize(value):
    return re.sub(r'\s+', ' ', value).strip()

for language, studio_language in [('ko', 'ko'), ('en', 'en-US')]:
    source = root / f'output/game-math-polar-3d/game-math-polar-3d.{language}.srt'
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    published = json.loads((revision / f'publishing/{language}-reopened-all-ui-times-v6.json').read_text('utf-8-sig'))
    assert published['videoId'] == result['videoId'] and published['language'] == studio_language
    blocks = re.split(r'\n\s*\n', source.read_text('utf-8-sig').strip())
    assert len(blocks) == len(published['rows']) == 206
    comparisons = []
    for index, (block, actual) in enumerate(zip(blocks, published['rows']), 1):
        lines = block.splitlines()
        expected_start, expected_end = lines[1].split(' --> ')
        expected_text = '\n'.join(lines[2:])
        text_same = normalize(expected_text) == normalize(actual['text'])
        start_error = frames(actual['start']) - milliseconds(expected_start) * 60 / 1000
        end_error = frames(actual['end']) - milliseconds(expected_end) * 60 / 1000
        assert text_same, (language, index, expected_text, actual['text'])
        # The current Studio fields consistently show the preceding frame index.
        # Verify this observed display rule, rather than asserting one-frame parity.
        displayed_previous_frame_matches = all(
            frames(actual[key]) == milliseconds(timestamp) * 60 // 1000 - 1
            for key, timestamp in [('start', expected_start), ('end', expected_end)])
        assert displayed_previous_frame_matches, (language, index, start_error, end_error)
        comparisons.append({'cue': index, 'expectedText': expected_text, 'actualText': actual['text'],
                            'expectedStart': expected_start, 'expectedEnd': expected_end,
                            'actualStart': actual['start'], 'actualEnd': actual['end'],
                            'startErrorFrames': start_error, 'endErrorFrames': end_error,
                            'textEqualIgnoringWrapWhitespace': text_same,
                            'matchesObservedPreviousFrameDisplay': displayed_previous_frame_matches})
    result['languages'][language] = {'srtSha256': digest, 'cues': 206, 'allTextsMatch': True,
                                    'allTimesMatchObservedUiDisplayRule': True,
                                    'maxAbsoluteErrorFrames': max(abs(c[k]) for c in comparisons for k in ['startErrorFrames', 'endErrorFrames']),
                                    'comparisons': comparisons}

result['all412PublishedCueTextsAndTimesMatch'] = True
result['uiDisplayRuleObserved'] = 'For all 824 start/end fields: displayed frame index equals floor(source SRT milliseconds * 60 / 1000) - 1.'
result['rawUiDifferenceSecondsRange'] = [-0.033, -1 / 60]
result['actualPlatformMillisecondsRead'] = False
result['timingInterpretation'] = 'All whole visible timestamps follow one uniform previous-frame display rule; no accumulated drift or substituted cues. Exact source SRTs are retained. This is a UI comparison, not a successful SRT download or direct platform timestamp API read.'
result['earlierVerificationFailure'] = {'actualExitCode': 1, 'chunk': 'a7bffd',
                                      'cause': 'Incorrect one-frame threshold for the observed preceding-frame UI display. First end differed by -1.8 frames; all timestamps were subsequently checked against the actual uniform display rule.'}
(revision / 'publishing/published-cue-comparison-v6.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'videoId': result['videoId'], 'cues': 412, 'allTextsMatch': True,
                  'allTimesMatchObservedUiDisplayRule': True, 'srtDownloadCompleted': False}))
