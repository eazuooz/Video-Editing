"""Compare every directly read published cue with the unchanged delivered SRT."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[3]
REL = 'projects/motion-sickness-games/production/revision-teaching-clarity-v1'
PUB = ROOT / REL / 'publishing'
result = dict(actualVideoId='mBDd9VzSTkA', recordedAt=datetime.now(timezone.utc).isoformat(),
              uiFps=60, languages={}, actualPlatformMillisecondsRead=False,
              srtDownloadCompleted=False, actualDownloadedSrtPath=None)

def frames(value):
    minute, second, frame = map(int, value.split(':'))
    assert second < 60 and frame < 60
    return (minute * 60 + second) * 60 + frame

def milliseconds(value):
    hour, minute, second, milli = map(int, re.split('[:,]', value))
    return ((hour * 60 + minute) * 60 + second) * 1000 + milli

def normalize(value):
    return re.sub(r'\s+', ' ', value).strip()

receipt = json.loads((PUB / 'youtube-upload-v1.json').read_text('utf-8-sig'))
for language in ['ko', 'en']:
    source = ROOT / f'output/motion-sickness-games/motion-sickness-games.{language}.srt'
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    assert digest == next(f['sha256'] for f in receipt['subtitleFiles'] if f['language'] == language)
    published = json.loads((PUB / f'{language}-published-current-ui-rows-v3.json').read_text('utf-8-sig'))
    assert published['actualVideoId'] == result['actualVideoId'] and published['language'] == language
    assert published['uiFps'] == 60
    blocks = re.split(r'\n\s*\n', source.read_text('utf-8-sig').strip())
    assert len(blocks) == len(published['rows']) == 179
    comparisons = []
    for index, (block, actual) in enumerate(zip(blocks, published['rows']), 1):
        lines = block.splitlines()
        start, end = lines[1].split(' --> ')
        expected_text = '\n'.join(lines[2:])
        assert normalize(expected_text) == normalize(actual['text']), (language, index)
        assert all(frames(a) == milliseconds(e) * 60 // 1000 - 1
                   for a, e in zip(actual['times'], [start, end])), (language, index, actual['times'], start, end)
        comparisons.append(dict(cue=index, expectedText=expected_text, actualText=actual['text'],
                                sourceStart=start, sourceEnd=end, actualUiTimes=actual['times'],
                                textEqualIgnoringWrapWhitespace=True, matchesObservedPreviousFrameDisplay=True,
                                uiMinusSourceFrames=[frames(a) - milliseconds(e) * 60 / 1000
                                                     for a, e in zip(actual['times'], [start, end])]))
    result['languages'][language] = dict(cues=179, sourceSrtSha256=digest, allTextsMatch=True,
        allTimesMatchObservedUiDisplayRule=True, comparisons=comparisons)
result['all358PublishedCueTextsAnd716VisibleTimesMatch'] = True
result['uiDisplayRuleObserved'] = 'Every visible start/end frame equals floor(source SRT milliseconds * 60 / 1000) - 1.'
result['interpretation'] = 'Uniform Studio preceding-frame display verified for every cue; no accumulated drift. This is not a completed SRT download or direct platform millisecond read.'
(PUB / 'published-cue-comparison-v3.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', 'utf-8')
print(json.dumps(dict(actualVideoId=result['actualVideoId'], cues=358, visibleTimes=716, allMatch=True,
                      sourceSrtUnchanged=True, srtDownloadCompleted=False)))
