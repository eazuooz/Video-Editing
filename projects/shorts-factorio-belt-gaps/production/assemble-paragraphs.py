"""Assemble immutable raw paragraph takes with constant per-take level matching."""
import hashlib
import json
import math
from pathlib import Path

import numpy as np
import soundfile as sf

from audio_revision import P, R, L, VOICE, REVISION, read, guard, media_reference


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def relative(path):
    return media_reference(path)


def db(value):
    return 20 * math.log10(max(float(value), 1e-12))


def frame_levels(samples, rate, seconds=.05):
    count = max(1, round(rate * seconds))
    return np.array([db(np.sqrt(np.mean(samples[i:i + count].astype(np.float64) ** 2)))
                     for i in range(0, len(samples), count)])


def edges(samples, rate):
    hop = max(1, round(rate * .005))
    levels = frame_levels(samples, rate, .005)
    threshold = max(-60, min(-42, float(levels.max()) - 35))
    active = np.flatnonzero(levels >= threshold)
    if not len(active):
        raise RuntimeError('No speech-active frame in a paragraph take.')
    return (int(active[0]) * hop / rate,
            max(0, (len(samples) - min(len(samples), (int(active[-1]) + 1) * hop)) / rate), threshold)


def stamp(seconds):
    milliseconds = round(seconds * 1000)
    seconds, ms = divmod(milliseconds, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f'{hours:02}:{minutes:02}:{seconds:02},{ms:03}'


def main():
    guard()
    manifest = read(P / 'production/tts-manifest.json')
    document = read(R / manifest['paths']['script'])
    profile = manifest['tts']['paragraphLevelNormalization']
    assert manifest['revision'] == REVISION and manifest['tts']['renderMode'] == 'line'
    jobs = [(scene, index, text) for scene in document['scenes']
            for index, text in enumerate(scene['lines'], 1)]
    if VOICE.exists():
        prior = read(L / 'line-levels.json')
        if (prior['voiceSha256'] != sha(VOICE)
                or prior['scriptSha256'] != sha(R / manifest['paths']['script'])
                or any(sha(R / row['rawTake']) != row['rawTakeSha256'] for row in prior['paragraphs'])):
            raise RuntimeError('Existing paragraph assembly differs; preserve/version before changes.')
        print('Reused exact current paragraph assembly: ' + relative(VOICE))
        return
    rows, samples_list, rate = [], [], None
    for scene, index, text in jobs:
        path = VOICE.parent / 'chunks' / f"{scene['id']}-{index:02}.wav"
        samples, sr = sf.read(path, dtype='float32', always_2d=False)
        if samples.ndim == 2:
            samples = samples.mean(axis=1)
        if not len(samples) or not np.isfinite(samples).all() or (rate is not None and sr != rate):
            raise RuntimeError('Invalid, nonfinite or inconsistent paragraph PCM: ' + str(path))
        rate = sr
        levels = frame_levels(samples, rate, float(profile['frameSeconds']))
        gate = min(float(profile['gateMaximumDbfs']), float(levels.max()) - float(profile['adaptiveGateBelowPeakDb']))
        voiced = levels[levels >= gate]
        if not len(voiced):
            raise RuntimeError('No voiced50ms normalization frames: ' + str(path))
        before = float(np.median(voiced))
        desired = float(profile['targetMedianDbfs']) - before
        gain_db = max(-float(profile['maximumGainDb']), min(float(profile['maximumGainDb']), desired))
        peak = float(np.max(np.abs(samples)))
        peak_gain_limit = db(.98 / max(peak, 1e-12))
        gain_db = min(gain_db, peak_gain_limit)
        matched = (samples * 10 ** (gain_db / 20)).astype(np.float32)
        leading, trailing, edge_gate = edges(matched, rate)
        destination = VOICE.parent / 'normalized-takes' / path.name
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            raise RuntimeError('Unreceipted normalized paragraph already exists; preserve it.')
        sf.write(destination, matched, rate, subtype='FLOAT')
        after = float(np.median(frame_levels(matched, rate, float(profile['frameSeconds']))[levels >= gate]))
        rows.append({'lineIndex': index - 1, 'sceneId': scene['id'], 'text': text,
            'rawTake': relative(path), 'rawTakeSha256': sha(path), 'normalizedTake': relative(destination),
            'normalizedTakeSha256': sha(destination), 'samples': len(samples), 'rate': rate,
            'frameSeconds': profile['frameSeconds'], 'gateDbfs': gate, 'voicedFrames': len(voiced),
            'beforeMedianDbfs': before, 'afterMedianDbfs': after, 'constantGainDb': gain_db,
            'targetMedianDbfs': profile['targetMedianDbfs'], 'targetErrorDb': after - float(profile['targetMedianDbfs']),
            'gainLimitApplied': abs(desired - gain_db) > .001,
            'peakBeforeDbfs': db(peak), 'peakAfterDbfs': db(np.max(np.abs(matched))),
            'leadingNonactiveSeconds': leading, 'trailingNonactiveSeconds': trailing, 'edgeGateDbfs': edge_gate,
            'rawSamplesRetained': True, 'trimmedSamples': 0, 'speechSpeed': 1})
        samples_list.append(matched)
    parts, position, entries, joins = [], 0, [], []
    for index, (row, samples) in enumerate(zip(rows, samples_list)):
        start = position
        parts.append(samples)
        position += len(samples)
        row['destinationSampleRange'] = [start, position]
        row['startSeconds'], row['endSeconds'] = start / rate, position / rate
        entries.append({'index': index + 1, 'scene_id': row['sceneId'], 'lineIndex': row['lineIndex'],
                        'text': row['text'], 'start': start / rate, 'end': position / rate})
        if index + 1 < len(rows):
            existing = row['trailingNonactiveSeconds'] + rows[index + 1]['leadingNonactiveSeconds']
            gap = max(0, round((float(profile['minimumIntendedJoinSeconds']) - existing) * rate))
            joins.append({'afterLineIndex': row['lineIndex'], 'seconds': position / rate,
                          'existingTailAndLeadSeconds': existing, 'insertedSamples': gap,
                          'insertedSeconds': gap / rate, 'totalNonactiveJoinSeconds': existing + gap / rate,
                          'speechOrBreathTrimmed': False, 'contextListening': 'pending'})
            if gap:
                parts.append(np.zeros(gap, dtype=np.float32))
                position += gap
    result = np.concatenate(parts)
    VOICE.parent.mkdir(parents=True, exist_ok=True)
    temporary = VOICE.with_suffix('.partial.wav')
    if temporary.exists():
        raise RuntimeError('Previous partial assembly needs inspection.')
    sf.write(temporary, result, rate, subtype='FLOAT')
    guard()
    temporary.rename(VOICE)
    stem = manifest['tts']['filenameStem']
    timing = {'revision': REVISION, 'sample_rate': rate, 'duration_seconds': len(result) / rate,
              'render_mode': 'paragraph-line', 'entries': entries, 'joins': joins, 'speechSpeed': 1,
              'lineLevelPolicy': 'line-level-takes-v1', 'voiceSha256': sha(VOICE)}
    (VOICE.parent / f'{stem}.timing.json').write_text(json.dumps(timing, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    (VOICE.parent / f'{stem}.srt').write_text('\n\n'.join(
        f"{entry['index']}\n{stamp(entry['start'])} --> {stamp(entry['end'])}\n{entry['text']}" for entry in entries) + '\n', encoding='utf8')
    report = {'revision': REVISION, 'policy': 'line-level-takes-v1', 'scriptSha256': sha(R / manifest['paths']['script']),
              'manifestSha256': sha(P / 'production/tts-manifest.json'), 'voice': relative(VOICE), 'voiceSha256': sha(VOICE),
              'durationSeconds': len(result) / rate, 'sampleRate': rate, 'paragraphs': rows, 'joins': joins,
              'profile': profile, 'allRawPcmPreserved': True, 'speechSpeed': 1, 'globalCompressionApplied': False,
              'actualPaceHumanListening': 'pending', 'pronunciation': 'pending'}
    (L / 'line-levels.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print(json.dumps({'voice': relative(VOICE), 'seconds': len(result) / rate, 'paragraphs': len(rows),
                      'joins': len(joins), 'addedGapSeconds': sum(x['insertedSeconds'] for x in joins)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
