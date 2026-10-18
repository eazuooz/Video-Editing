"""Time the 34 approved caption clauses from cached full-voice word timestamps.

This file performs no ASR, GPU work, rendering, or edits on import. Running it
requires an exact normalized transcript match, apart from the documented
허트박스에요/허트박스예요 spelling alias. It never fills missing words with
estimated times. An ambiguous transcript or timestamp requires reconciliation.
"""
from pathlib import Path
import copy
import difflib
import hashlib
import json
import math
import re
import struct
import unicodedata


P = Path(__file__).resolve().parents[1]
R = P.parents[1]
L = P / 'production/local/fairness-60s'
S = P / 'script/fairness-60s'
FPS = 60
ALIAS_FROM = '허트박스에요'
ALIAS_TO = '허트박스예요'


def read(path):
    return json.loads(Path(path).read_text(encoding='utf8'))


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def rel(path):
    return Path(path).relative_to(R).as_posix()


def normalized(text):
    return re.sub(r'[^0-9a-z가-힣]', '', unicodedata.normalize('NFC', text).lower())


def canonical_asr(text):
    value=normalized(text)
    reconciliation=read(L/'asr-reconciliation.json')
    for a,b in reconciliation['aliases'].items():value=value.replace(a,b)
    return value


def require_match(expected, actual, label):
    if expected == actual:
        return
    differences = []
    for tag, a, b, c, d in difflib.SequenceMatcher(
        None, expected, actual, autojunk=False,
    ).get_opcodes():
        if tag != 'equal':
            differences.append(dict(
                kind=tag, expectedRange=[a, b], actualRange=[c, d],
                expected=expected[max(0, a - 12):min(len(expected), b + 12)],
                actual=actual[max(0, c - 12):min(len(actual), d + 12)],
            ))
    raise RuntimeError(label + ': focused reconciliation required; no caption '
                       'times written. ' + json.dumps(differences, ensure_ascii=False))


def wav_duration(path):
    """Read RIFF timing metadata; supports the float WAV used by this project."""
    with Path(path).open('rb') as stream:
        head = stream.read(12)
        if head[:4] != b'RIFF' or head[8:] != b'WAVE':
            raise RuntimeError('Expected the current RIFF WAVE narration PCM.')
        sample_rate = block_align = data_size = None
        while True:
            chunk = stream.read(8)
            if len(chunk) != 8:
                break
            kind, size = struct.unpack('<4sI', chunk)
            if kind == b'fmt ':
                data = stream.read(size)
                if len(data) < 16:
                    raise RuntimeError('Invalid WAV fmt chunk.')
                fields = struct.unpack('<HHIIHH', data[:16])
                sample_rate, block_align = fields[2], fields[4]
            elif kind == b'data':
                data_size = size
                stream.seek(size, 1)
            else:
                stream.seek(size, 1)
            if size % 2:
                stream.seek(1, 1)
        if not sample_rate or not block_align or data_size is None:
            raise RuntimeError('Missing current PCM duration metadata.')
        if data_size % block_align:
            raise RuntimeError('Current PCM data is not sample-aligned.')
        return data_size / block_align / sample_rate


def part_bounds(part, duration):
    start = float(part['dest'])
    if 'destinationEnd' in part:
        end = float(part['destinationEnd'])
    elif 'sourceRange' in part:
        a, b = map(float, part['sourceRange'])
        end = start + (b - a) / float(part.get('rate', 1))
    else:
        raise RuntimeError('PCM part needs destinationEnd or sourceRange: '
                           + str(part.get('id', '?')))
    if not (math.isfinite(start) and math.isfinite(end)
            and 0 <= start < end <= duration + 1e-6):
        raise RuntimeError('Invalid PCM part bounds: ' + str(part.get('id', '?')))
    return start, min(end, duration)


def choose_part(parts, line_index, raw_start, raw_end):
    """Prefer explicit line ownership; otherwise use unambiguous overlap."""
    owned = [p for p in parts if line_index in p['lineIndices']]
    options = owned or parts
    if len(owned) == 1:
        return owned[0], 'lineIndices'
    scored = []
    for part in options:
        a, b = part['destinationBounds']
        overlap = max(0.0, min(raw_end, b) - max(raw_start, a))
        scored.append((overlap, part))
    scored.sort(key=lambda row: row[0], reverse=True)
    if not scored or scored[0][0] <= 0:
        raise RuntimeError('Cue has no retained PCM speech part; reconcile line '
                           + str(line_index))
    if len(scored) > 1 and abs(scored[0][0] - scored[1][0]) < 1e-9:
        raise RuntimeError('Ambiguous PCM part for line ' + str(line_index))
    return scored[0][1], ('lineIndices-overlap' if owned else 'overlap-fallback')


def encoded(data):
    return json.dumps(data, ensure_ascii=False, indent=2) + '\n'


def main():
    voice = L / 'narration-timeline.wav'
    proposal_path = S / 'caption-proposal.json'
    narration_path = S / 'narration.ko.json'
    edit_path = L / 'pcm-edit.json'
    voice_sha = sha(voice)
    asr_path = L / ('asr-voice-' + voice_sha[:12] + '.json')
    if not asr_path.exists():
        raise RuntimeError('Current full-voice ASR is not ready: ' + str(asr_path))
    asr = read(asr_path)
    if asr.get('sha256') != voice_sha or asr.get('role') != 'voice' or not asr.get('fullInput'):
        raise RuntimeError('ASR must cover the complete current narration PCM hash.')
    duration = wav_duration(voice)
    if abs(duration - 60) > 1 / FPS:
        raise RuntimeError('Expected the current complete 60-second narration PCM.')

    narration = read(narration_path)
    lines = [line for scene in narration['scenes'] for line in scene['lines']]
    proposal = read(proposal_path)
    cues = proposal['cues']
    if len(lines) != 15 or len(cues) != 34 or proposal.get('lineIndexBase') != 0:
        raise RuntimeError('Expected the approved 15-line, 34-cue proposal.')
    if any(not isinstance(c['lineIndex'], int) or not 0 <= c['lineIndex'] < len(lines)
           for c in cues):
        raise RuntimeError('Caption lineIndex is invalid.')
    if [c['lineIndex'] for c in cues] != sorted(c['lineIndex'] for c in cues):
        raise RuntimeError('Caption clauses are out of narration order.')
    expected = ''.join(normalized(line) for line in lines)
    require_match(expected, ''.join(normalized(c['ko']) for c in cues),
                  'Caption proposal differs from narration')
    for i, line in enumerate(lines):
        require_match(normalized(line), ''.join(normalized(c['ko']) for c in cues
                      if c['lineIndex'] == i), 'Caption line ' + str(i))

    chunks = asr.get('chunks', [])
    if not chunks:
        raise RuntimeError('Current full-voice ASR has no word timestamps.')
    raw_actual = ''.join(normalized(w['text']) for w in chunks)
    reconciliation=read(L/'asr-reconciliation.json')
    if reconciliation['voiceSha256']!=voice_sha:raise RuntimeError('Reconciliation is for another PCM hash')
    actual = canonical_asr(raw_actual)
    require_match(expected, actual, 'ASR words differ from narration')
    require_match(expected, canonical_asr(asr.get('text', '')),
                  'ASR full text differs from narration')

    words = []
    offset = 0
    for index, chunk in enumerate(chunks):
        text = canonical_asr(chunk['text'])
        if not text:
            continue
        times = chunk.get('timestamp')
        if not times or len(times) != 2 or any(t is None for t in times):
            raise RuntimeError('Missing word timestamp at ASR chunk ' + str(index))
        start, end = map(float, times)
        if not (math.isfinite(start) and math.isfinite(end) and 0 <= start <= end):
            raise RuntimeError('Invalid word timestamp at ASR chunk ' + str(index))
        words.append(dict(index=index, text=chunk['text'], start=start, end=end,
                          charStart=offset, charEnd=offset + len(text)))
        offset += len(text)
    if offset != len(expected):
        raise RuntimeError('Word character coverage is incomplete.')

    def at(position, edge):
        for word in words:
            a, b = word['charStart'], word['charEnd']
            inside = a <= position < b if edge == 'start' else a < position <= b
            if inside:
                fraction = (position - a) / (b - a)
                time = word['start'] + (word['end'] - word['start']) * fraction
                return time, dict(wordIndex=word['index'], charOffset=position,
                                  fraction=fraction,
                                  interpolatedWithinWord=0 < fraction < 1)
        raise RuntimeError('No timestamp covers caption character ' + str(position))

    edit = read(edit_path)
    if edit.get('sha256') and edit['sha256'] != voice_sha:
        raise RuntimeError('PCM edit manifest hash differs from current narration.')
    parts = []
    for index, item in enumerate(edit.get('parts', [])):
        part = copy.deepcopy(item)
        part['id'] = str(part.get('id', index))
        part['lineIndices'] = [int(i) for i in part.get('lineIndices', [])]
        part['destinationBounds'] = list(part_bounds(part, duration))
        parts.append(part)
    if not parts:
        raise RuntimeError('The current PCM edit manifest has no speech parts.')

    timed = []
    evidence = []
    position = 0
    previous_end_frame = 0
    for cue in cues:
        length = len(normalized(cue['ko']))
        if not length:
            raise RuntimeError('An empty caption clause cannot be timed.')
        raw_start, first = at(position, 'start')
        raw_end, last = at(position + length, 'end')
        part, method = choose_part(parts, cue['lineIndex'], raw_start, raw_end)
        lower, upper = part['destinationBounds']
        clipped_start = max(lower, min(raw_start, upper))
        clipped_end = max(lower, min(raw_end, upper))
        # Half-up nearest-frame quantization, bounded by retained PCM samples.
        start_frame = max(math.ceil(lower * FPS - 1e-8),
                          math.floor(clipped_start * FPS + 0.5))
        end_frame = min(math.floor(upper * FPS + 1e-8),
                        math.floor(clipped_end * FPS + 0.5))
        if not (previous_end_frame <= start_frame < end_frame <= round(duration * FPS)):
            raise RuntimeError('Overlapping, empty or out-of-bounds caption ' + cue['id']
                               + '; focused timestamp reconciliation required.')
        result = copy.deepcopy(cue)
        result.update(start=start_frame / FPS, end=end_frame / FPS,
                      startFrame=start_frame, endFrame=end_frame)
        timed.append(result)
        evidence.append(dict(
            id=cue['id'], lineIndex=cue['lineIndex'],
            normalizedCharRange=[position, position + length],
            rawWordTimes=[raw_start, raw_end], firstBoundary=first, lastBoundary=last,
            pcmPartId=part['id'], pcmPartSelection=method,
            pcmSource=part.get('source'), pcmSourceRange=part.get('sourceRange'),
            pcmDestinationBounds=[lower, upper],
            clampedTimes=[clipped_start, clipped_end],
            clampApplied=(raw_start != clipped_start or raw_end != clipped_end),
            frameRange=[start_frame, end_frame],
        ))
        position += length
        previous_end_frame = end_frame
    if position != len(expected):
        raise RuntimeError('Caption timing did not cover all narration characters.')

    fingerprints = dict(
        voiceSha256=voice_sha, asrSha256=sha(asr_path),
        narrationSha256=sha(narration_path), proposalSha256=sha(proposal_path),
        pcmEditSha256=sha(edit_path),
    )
    output = copy.deepcopy(proposal)
    output.update(status='exact-transcript-word-timed; contextual playback pending',
                  fps=FPS, durationSeconds=duration,
                  timingInputs=fingerprints, cues=timed)
    alignment = dict(
        status='exact-text-and-word-boundaries-passed; contextual playback pending',
        fullVoiceAsr=rel(asr_path), currentPcm=rel(voice),
        normalizedNarrationCharacters=len(expected), normalizedCoverageExact=True,
        alias=dict(fromSpelling=ALIAS_FROM, toSpelling=ALIAS_TO,
                   occurrences=raw_actual.count(ALIAS_FROM)),
        focusedReconciliation=rel(L/'asr-reconciliation.json'),
        focusedReconciliationSha256=sha(L/'asr-reconciliation.json'),
        quantization='60fps half-up nearest frame, clamped inside retained PCM parts',
        timestampPolicy='Word edges; interpolation only within a timestamped word',
        fingerprints=fingerprints, words=words, cues=evidence,
        reviewFlags=[dict(id=e['id'], first=e['firstBoundary'], last=e['lastBoundary'])
                     for e in evidence if e['firstBoundary']['interpolatedWithinWord']
                     or e['lastBoundary']['interpolatedWithinWord']],
        humanListening='pending',
    )
    targets = [(S / 'captions.json', output), (L / 'caption-alignment.json', alignment)]
    for path, data in targets:
        if path.exists() and path.read_text(encoding='utf8') != encoded(data):
            raise RuntimeError('Existing timing output differs; preserve or reconcile it '
                               'before rerunning: ' + str(path))
    for path, data in targets:
        if not path.exists():
            path.write_text(encoded(data), encoding='utf8')
    print(json.dumps(dict(captions=rel(targets[0][0]), evidence=rel(targets[1][0]),
                          cueCount=len(timed), exactCharacterCoverage=True,
                          interpolationFlags=len(alignment['reviewFlags'])),
                     ensure_ascii=False))


if __name__ == '__main__':
    main()
