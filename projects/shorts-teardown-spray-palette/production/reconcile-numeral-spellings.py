"""Audit only six Teardown numeral/unit spellings against the new complete ASR.

No TTS, ASR, decoding, rendering or model/device load. --check is read-only.
--write saves a current voice/ASR-hash-bound reconciliation after every other
character matches exactly. Proper names and other words are never normalized.
This is text/timestamp normalization, not evidence of actual audio listening.
"""
from pathlib import Path
import argparse
import datetime
import difflib
import importlib.util
import json
import math
import re

from audio_revision import P, R, L, VOICE, REVISION, CAPTION_CLAUSES, guard, read, sha, normalize_speech

SITES = [
    ('p4-1', '삼번', '3번', 3, '번', 0),
    ('p4-2', '구번', '9번', 9, '번', 0),
    ('p5-2', '이백오십오칸', '255칸', 255, '칸', 0),
    ('p5-3', '네단계', '4단계', 4, '단계', 0),
    ('p5-3', '네단계', '4단계', 4, '단계', 1),
    ('p5-4', '아홉칸', '9칸', 9, '칸', 0),
]


def norm(text):
    return normalize_speech(text, {})


def describe_difference(expected, actual):
    return [{
        'kind': tag, 'expectedRange': [a, b], 'actualRange': [c, d],
        'expected': expected[max(0, a - 12):b + 12],
        'actual': actual[max(0, c - 12):d + 12],
    } for tag, a, b, c, d in difflib.SequenceMatcher(
        None, expected, actual, autojunk=False).get_opcodes() if tag != 'equal']


def build_audit(lines, clauses, asr, duration):
    """Pure validation, used by tests without writing synthetic production data."""
    if (not lines or '티어다운' not in lines[0] or '테어다운' in lines[0]
            or '태어다운' in lines[0]):
        raise RuntimeError('The first-paragraph canonical-title repair must precede this audit.')
    expected = ''.join(norm(line) for line in lines)
    by_id, cursor = {}, 0
    for clause in clauses:
        if clause['id'] in by_id:
            raise RuntimeError('Duplicate clause ID.')
        text = norm(clause['spoken'])
        by_id[clause['id']] = (cursor, text)
        cursor += len(text)
    if ''.join(norm(clause['spoken']) for clause in clauses) != expected:
        raise RuntimeError('All derived spoken clauses must preserve the exact current narration.')
    locations = []
    for clause_id, target, alternative, value, unit, occurrence in SITES:
        offset, text = by_id[clause_id]
        matches = list(re.finditer(re.escape(target), text))
        if len(matches) != (2 if clause_id == 'p5-3' else 1):
            raise RuntimeError('The six approved numeric contexts changed: ' + clause_id)
        match = matches[occurrence]
        locations.append({'clauseId': clause_id, 'target': target,
                          'alternative': alternative, 'value': value, 'unit': unit,
                          'expectedRange': [offset + match.start(), offset + match.end()]})
    if locations != sorted(locations, key=lambda x: x['expectedRange'][0]):
        raise RuntimeError('Numeric sites must retain the source teaching order.')
    pieces, cursor = [], 0
    for i, site in enumerate(locations):
        start, end = site['expectedRange']
        pieces.extend([re.escape(expected[cursor:start]),
                       '(?P<n' + str(i) + '>' + re.escape(site['target']) + '|' +
                       re.escape(site['alternative']) + ')'])
        cursor = end
    pieces.append(re.escape(expected[cursor:]))
    raw = norm(asr['text'])
    match = re.fullmatch(''.join(pieces), raw)
    if not match:
        # This diagnostic does not create or apply any additional alias.
        diagnostic = raw
        for _, target, alternative, _, _, _ in SITES:
            diagnostic = diagnostic.replace(alternative, target)
        raise RuntimeError('Non-approved words/names/values differ; no reconciliation written: ' +
                           json.dumps(describe_difference(expected, diagnostic), ensure_ascii=False))
    words, cursor, previous_start = [], 0, -1.0
    for index, chunk in enumerate(asr.get('chunks', [])):
        text = norm(chunk['text'])
        if not text:
            continue
        stamp = chunk.get('timestamp')
        if (not isinstance(stamp, (list, tuple)) or len(stamp) != 2
                or any(type(x) not in (float, int) or not math.isfinite(x) for x in stamp)):
            raise RuntimeError('Each raw recognized word requires measured timestamps.')
        start, end = map(float, stamp)
        if not 0 <= start <= end <= duration + 0.05 or start < previous_start:
            raise RuntimeError('Invalid, out-of-PCM or unordered raw word timestamp.')
        words.append({'index': index, 'rawText': chunk['text'], 'start': start, 'end': end,
                      'rawCharRange': [cursor, cursor + len(text)]})
        cursor += len(text)
        previous_start = start
    if ''.join(norm(word['rawText']) for word in words) != raw:
        raise RuntimeError('Raw full recognition and raw word chunks differ.')

    def edge(position, end_edge):
        choices = [word for word in words if
                   (word['rawCharRange'][0] < position <= word['rawCharRange'][1] if end_edge else
                    word['rawCharRange'][0] <= position < word['rawCharRange'][1])]
        if len(choices) != 1:
            raise RuntimeError('The numeric character boundary lacks a unique measured word.')
        word = choices[0]
        lo, hi = word['rawCharRange']
        fraction = (position - lo) / (hi - lo)
        return {'seconds': word['start'] + fraction * (word['end'] - word['start']),
                'wordIndex': word['index'], 'fractionWithinWord': fraction,
                'interpolatedWithinWord': 0 < fraction < 1}

    aliases, sites, allowed_ranges = {}, [], set()
    for i, site in enumerate(locations):
        source = match.group('n' + str(i))
        lo, hi = match.span('n' + str(i))
        applied = source != site['target']
        if applied:
            aliases[source] = site['target']
            allowed_ranges.add((lo, hi))
        sites.append(dict(site, rawSpelling=source, normalizedSpelling=site['target'],
                          rawCharRange=[lo, hi], normalizationApplied=applied,
                          actualWordStart=edge(lo, False), actualWordEnd=edge(hi, True),
                          sourceWords=[w for w in words if
                                       w['rawCharRange'][0] < hi and w['rawCharRange'][1] > lo],
                          semanticReview='Identical integer value and unit in the same source clause.'))
    # Verify the consumer's global alias algorithm cannot affect another occurrence.
    spec = importlib.util.spec_from_file_location('teardown_caption_audit', P / 'production/time-captions.py')
    captions = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(captions)
    canonical, bounds, events = captions.apply_aliases(raw, aliases)
    if (canonical != expected or {tuple(e['rawCharRange']) for e in events} != allowed_ranges
            or len(events) != len(allowed_ranges)):
        raise RuntimeError('Alias consumption would change text outside the six verified numeric sites.')
    return {'aliases': aliases, 'numericSites': sites, 'aliasApplications': events,
            'fullExpectedText': ' '.join(lines), 'rawASRTextUnmodified': asr['text'],
            'fullNormalizedTextMatches': True, 'nonNumericChangesAllowed': False,
            'properNameAliasesAllowed': False, 'wordTimestampMapping':
            'Original ASR word timestamps retained; sub-word boundaries use documented character interpolation.',
            'normalizedCharacterCount': len(bounds), 'actualAudioListening': 'pending',
            'humanListening': False, 'acousticPronunciationVerified': False,
            'rawRecognitionEdited': False, 'meaningAndNumericValueReview': 'same value plus exact unit',
            'scope': 'Six predeclared sites only; zero permission to repair names, omissions or other words.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--asr-path', help='Explicit raw complete-voice JSON inside current audio attempt.')
    parser.add_argument('--asr-reason', help='Why this alternative raw ASR is selected; both records remain preserved.')
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--check', action='store_true')
    mode.add_argument('--write', action='store_true')
    args = parser.parse_args()
    guard(require_current_selection=args.write)
    manifest = read(P / 'production/tts-manifest.json')
    if (L.name != 'audio-v2' or manifest.get('repairAttempt', {}).get('id') != 'audio-v2'
            or manifest['repairAttempt']['regenerateRawTakes'] != ['main-01.wav']):
        raise RuntimeError('Wait for the prepared title-correction audio-v2 attempt; audio-v1 is preserved.')
    voice_sha = sha(VOICE)
    from asr_selection import select_asr
    asr_path, asr, asr_selection = select_asr(args.asr_path, args.asr_reason)
    narration_path = R / manifest['paths']['script']
    document = read(narration_path)
    lines = [line for scene in document['scenes'] for line in scene['lines']]
    clauses_doc = read(CAPTION_CLAUSES)
    if clauses_doc.get('pronunciationAliases', {}):
        raise RuntimeError('This numeric audit permits no pre-existing proper-name/word aliases.')
    spec = importlib.util.spec_from_file_location('teardown_duration', P / 'production/time-captions.py')
    caption_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(caption_module)
    duration = caption_module.wav_duration(VOICE)
    if (asr.get('role') != 'voice' or asr.get('sha256') != voice_sha
            or asr.get('revision') != REVISION or asr.get('fullInput') is not True
            or (asr.get('rawRecognitionUnmodified') is not True
                and not asr_selection.get('derivedFromUnmodifiedSources'))
            or asr.get('expectedTextPromptUsed') is not False
            or asr.get('normalizationAliases') not in ({}, None)
            or abs(float(asr.get('inputDurationSeconds', -1)) - duration) > 1 / 24000):
        raise RuntimeError('Require this complete unprompted, unmodified voice ASR and current expected input.')
    result = build_audit(lines, clauses_doc['clauses'], asr, duration)
    record = dict(result, schemaVersion=1, slug=P.name, revision=REVISION,
                  policy='six-value-and-unit-spellings-only-v1', voiceSha256=voice_sha,
                  asrSha256=sha(asr_path), asrPath=str(asr_path.resolve()),
                  scriptSha256=sha(narration_path), clausesSha256=sha(CAPTION_CLAUSES),
                  durationSeconds=duration, createdAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  asrSelection=asr_selection, mediaJobsStarted=0, captionTimingGenerated=False)
    output = L / 'asr-reconciliation.json'
    if args.write:
        if output.exists():
            prior = read(output)
            if {k: v for k, v in prior.items() if k != 'createdAt'} != {
                    k: v for k, v in record.items() if k != 'createdAt'}:
                raise RuntimeError('Existing reconciliation differs; preserve it for a reviewed new attempt.')
            print('Reused identical numeric-only reconciliation; actual listening remains pending.')
            return
        with output.open('x', encoding='utf8') as stream:
            stream.write(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
        print('Saved hash-bound numeric-only reconciliation: ' + str(output.resolve()))
    else:
        print(json.dumps({'checked': True, 'voiceSha256': voice_sha, 'asrSha256': sha(asr_path),
                          'sites': 6, 'normalizedSites': len(record['aliasApplications']),
                          'nonNumericDifferences': 0, 'writes': 0,
                          'actualListening': 'pending'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
