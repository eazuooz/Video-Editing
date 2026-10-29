"""CPU evidence for the actual encoded v4 mix; model ASR stays separate.

Default is readiness only. After the coordinator's final-render signal, decode
the actual AAC, compare the FLOAT concat samples and source-to-mix continuity,
then finalize only after an independently recorded whole-transcript review.
No source voice, master, narration, or baseline QA is modified.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[3]
PROJECT = Path(__file__).resolve().parents[1]
SOURCE = PROJECT / 'production/local/audio-v4'
WORK = PROJECT / 'production/local/documentary-v4'
QA = PROJECT / 'production/local/final-qa-v4'
OUTPUT = ROOT / 'output/buckshot-roulette-reverse-engineering-v4'
MASTER = OUTPUT / (PROJECT.name + '.captioned.mp4')
DECODED = QA / 'final-encoded-v4.wav'
FFMPEG = Path('C:/Users/1/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0-full_build/bin/ffmpeg.exe')


def now():
    return datetime.now(timezone.utc).isoformat()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def digest(path):
    result = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for data in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            result.update(data)
    return result.hexdigest()


def current_master():
    auth = read(ROOT / 'shared/publishing/video-production-control.json')['scopedSetupAuthorizations'][PROJECT.name]
    assert auth['productionAllowedNow'] is True
    technical = read(WORK / 'technical-qa.json')
    assert technical['technicalDecodePassed'] and technical['pairedAudioIdentical'] and technical['audioLoudnessPassed']
    master_hash = digest(MASTER)
    assert technical['outputs']['captioned']['sha256'] == master_hash
    return technical, master_hash


def decode():
    technical, master_hash = current_master()
    receipt_path = QA / 'final-aac-decode-v4.json'
    if DECODED.exists():
        receipt = read(receipt_path)
        assert receipt['masterSha256'] == master_hash and receipt['decodedAudioSha256'] == digest(DECODED)
        return
    QA.mkdir(parents=True, exist_ok=True)
    command = [str(FFMPEG), '-hide_banner', '-nostdin', '-v', 'warning', '-threads', '2', '-i', str(MASTER),
               '-map', '0:a:0', '-vn', '-c:a', 'pcm_f32le', '-ar', '48000', '-ac', '2', '-n', str(DECODED)]
    log = QA / 'final-aac-decode-v4.log'
    with log.open('w', encoding='utf-8') as stream:
        result = subprocess.run(command, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    assert result.returncode == 0, f'Decode failed: {log}'
    import soundfile as sf
    info = sf.info(DECODED)
    streams = technical['outputs']['captioned']['probe']['streams']
    duration = float(next(s for s in streams if s['codec_type'] == 'audio')['duration'])
    assert info.samplerate == 48000 and info.channels == 2 and info.subtype == 'FLOAT'
    assert abs(info.duration - duration) <= 1024 / 48000 + .001
    save(receipt_path, {'decodedAt': now(), 'masterPath': str(MASTER), 'masterSha256': master_hash,
                       'decodedAudioFile': str(DECODED), 'decodedAudioSha256': digest(DECODED),
                       'frames': info.frames, 'seconds': info.duration, 'sampleRate': info.samplerate,
                       'channels': info.channels, 'subtype': info.subtype, 'command': command,
                       'logSha256': digest(log), 'actualAACDecoded': True})


def concat_regression():
    import numpy as np
    import soundfile as sf
    target = WORK / 'complete-mix.wav'
    inputs = [WORK / 'bookend-brand.wav', WORK / 'body-mix.wav', WORK / 'bookend-member.wav']
    results, total, largest = [], 0, 0.0
    with sf.SoundFile(target) as actual:
        assert actual.samplerate == 48000 and actual.channels == 2 and actual.subtype == 'FLOAT'
        target_frames = actual.frames
        for path in inputs:
            same, count, error = True, 0, 0.0
            with sf.SoundFile(path) as expected:
                assert expected.samplerate == 48000 and expected.channels == 2
                subtype = expected.subtype
                while True:
                    block = expected.read(65536, dtype='float32', always_2d=True)
                    if not len(block):
                        break
                    got = actual.read(len(block), dtype='float32', always_2d=True)
                    assert got.shape == block.shape
                    same = same and np.array_equal(got, block)
                    error = max(error, float(np.max(np.abs(got - block))))
                    count += len(block)
            total += count
            largest = max(largest, error)
            results.append({'file': path.relative_to(ROOT).as_posix(), 'sourceSubtype': subtype, 'frames': count,
                            'decodedFloatSamplesExactlyEqual': same, 'maximumAbsoluteError': error})
        no_extra = len(actual.read(1, dtype='float32', always_2d=True)) == 0 and total == target_frames
    report = {'schemaVersion': 1, 'checkedAt': now(), 'target': str(target), 'targetSha256': digest(target),
              'actualFrames': target_frames, 'expectedFrames': total, 'seconds': total / 48000,
              'allDecodedSamplesExactlyEqual': all(r['decodedFloatSamplesExactlyEqual'] for r in results),
              'noExtraFrames': no_extra, 'maximumAbsoluteError': largest, 'perInput': results, 'humanListening': False}
    report['passed'] = report['allDecodedSamplesExactlyEqual'] and no_extra
    save(QA / 'audio-concat-v4-regression.json', report)
    return report


def consecutive_ranges(rows, predicate, minimum=5):
    runs, current = [], []
    for row in rows + [None]:
        if row is not None and predicate(row) and (not current or row['start'] - current[-1]['start'] <= .101):
            current.append(row)
        else:
            if len(current) >= minimum:
                runs.append({'start': current[0]['start'], 'end': current[-1]['end'], 'windows': len(current)})
            current = [row] if row is not None and predicate(row) else []
    return runs


def continuity():
    """Bounded per-paragraph vector reductions; no FFT or BLAS dot products."""
    import numpy as np
    import soundfile as sf
    voice_path = SOURCE / 'narration.wav'
    timing = read(SOURCE / 'narration.timing.json')
    asr = read(SOURCE / 'review/source-full-asr.timestamps.json')
    assert asr['audio_sha256'] == digest(voice_path)
    intervals = [w['timestamp'] for w in asr['chunks'] if None not in w['timestamp'] and w['timestamp'][1] > w['timestamp'][0]]
    paragraphs, all_drops, source_quiet = [], [], []
    with sf.SoundFile(voice_path) as source, sf.SoundFile(DECODED) as final, sf.SoundFile(WORK / 'complete-mix.wav') as premix:
        assert source.samplerate == 24000 and source.channels == 1
        assert final.samplerate == premix.samplerate == 48000 and final.channels == premix.channels == 2
        for entry in timing['entries']:
            start, end = float(entry['start']), float(entry['end'])
            a, b = round(start * 24000), round(end * 24000)
            source.seek(a)
            x = source.read(b - a, dtype='float32')
            mixed_start = round((start + 2) * 48000)
            final.seek(mixed_start); premix.seek(mixed_start)
            y = final.read(2 * len(x), dtype='float32', always_2d=True)[::2].mean(axis=1)
            z = premix.read(2 * len(x), dtype='float32', always_2d=True)[::2].mean(axis=1)
            assert len(x) == len(y) == len(z)
            windows = []
            for offset in range(0, max(0, len(x) - 9600 + 1), 2400):
                begin, finish = start + offset / 24000, start + (offset + 9600) / 24000
                overlap = sum(max(0, min(finish, v) - max(begin, u)) for u, v in intervals if u < finish and v > begin)
                if overlap < .06:
                    continue
                xs, ys, zs = x[offset:offset + 9600], y[offset:offset + 9600], z[offset:offset + 9600]
                energy = float(np.sum(xs * xs, dtype=np.float64))
                if energy <= 1e-20:
                    continue
                xy = float(np.sum(xs * ys, dtype=np.float64)); xz = float(np.sum(xs * zs, dtype=np.float64))
                yy = float(np.sum(ys * ys, dtype=np.float64))
                windows.append({'start': begin, 'end': finish,
                                'sourceRmsDbfs': 10 * np.log10(energy / len(xs)),
                                'finalVoiceProjectionDb': 20 * np.log10(max(xy / energy, 1e-10)),
                                'preLimiterVoiceProjectionDb': 20 * np.log10(max(xz / energy, 1e-10)),
                                'correlation': xy / max((energy * yy) ** .5, 1e-20)})
            assert windows, ('No speech windows', entry['scene_id'], entry['paragraph'])
            median_gain = float(np.median([w['finalVoiceProjectionDb'] for w in windows]))
            median_source = float(np.median([w['sourceRmsDbfs'] for w in windows]))
            drops = consecutive_ranges(windows, lambda w: w['finalVoiceProjectionDb'] <= median_gain - 6)
            quiet = consecutive_ranges(windows, lambda w: w['sourceRmsDbfs'] <= median_source - 6)
            ident = f'{entry["scene_id"]}-{entry["paragraph"]:02}'
            all_drops.extend(dict(c, paragraph=ident) for c in drops)
            source_quiet.extend(dict(c, paragraph=ident, status='contextual listening candidate, not a proven defect') for c in quiet)
            paragraphs.append({'id': ident, 'mode': entry['mode'], 'sourceStart': start, 'sourceEnd': end, 'windows': len(windows),
                               'finalVoiceProjectionMedianDb': median_gain,
                               'preLimiterVoiceProjectionMedianDb': float(np.median([w['preLimiterVoiceProjectionDb'] for w in windows])),
                               'medianCorrelation': float(np.median([w['correlation'] for w in windows])),
                               'sourceRmsMedianDbfs': median_source, 'sustainedDropCandidates': drops})
    report = {'schemaVersion': 1, 'checkedAt': now(), 'sourceAudioSha256': digest(voice_path), 'finalDecodedAudioSha256': digest(DECODED),
              'sourceOffsetSeconds': 2, 'windowSeconds': .4, 'hopSeconds': .1,
              'method': 'Projection of source voice onto actual pre-limiter mix and decoded AAC mono average. Exact 2-second placement; every second final 48 kHz sample compared with source 24 kHz. Correlation is not isolated-voice listening.',
              'speechSelection': 'At least 60 ms overlap with current source ASR words; no source amplitude gate.',
              'candidateRule': 'At least 5 consecutive 100 ms hops with voice projection 6 dB below the paragraph median.',
              'paragraphs': paragraphs, 'sustainedSourceRelativeDropCandidates': all_drops,
              'sourceQuietCandidates': source_quiet, 'humanListening': False}
    save(QA / 'source-to-final-continuity-v4.json', report)
    return report


def measure():
    technical, master_hash = current_master()
    receipt = read(QA / 'final-aac-decode-v4.json')
    assert receipt['masterSha256'] == master_hash and receipt['decodedAudioSha256'] == digest(DECODED)
    log_path = WORK / 'logs/final-loudness.log'
    log = log_path.read_text(encoding='utf-8', errors='replace')
    def last(pattern):
        found = re.findall(pattern, log)
        assert found, ('Missing measurement', pattern)
        return float(found[-1])
    loudness = {'integratedLufs': last(r'Integrated loudness:\s+I:\s+(-?\d+(?:\.\d+)?)'),
                'truePeakDbtp': last(r'True peak:\s+Peak:\s+(-?\d+(?:\.\d+)?)'),
                'lraLu': last(r'Loudness range:\s+LRA:\s+(-?\d+(?:\.\d+)?)'),
                'maximumTruePeakDbtp': -1.5, 'log': str(log_path), 'logSha256': digest(log_path)}
    loudness['passed'] = loudness['truePeakDbtp'] <= -1.5
    assert loudness['truePeakDbtp'] == technical['encodedTruePeakDbtp']
    regression, continuity_report = concat_regression(), continuity()
    report = {'schemaVersion': 1, 'checkedAt': now(), 'masterSha256': master_hash,
              'decodedAudioSha256': receipt['decodedAudioSha256'], 'sourceAudioSha256': digest(SOURCE / 'narration.wav'),
              'loudness': loudness, 'concatRegressionPassed': regression['passed'],
              'continuityReport': 'production/local/final-qa-v4/source-to-final-continuity-v4.json',
              'continuityParagraphs': len(continuity_report['paragraphs']),
              'minParagraphVoiceCorrelation': min(p['medianCorrelation'] for p in continuity_report['paragraphs']),
              'newSustainedSourceRelativeDropCandidates': len(continuity_report['sustainedSourceRelativeDropCandidates']),
              'sourceQuietCandidates': len(continuity_report['sourceQuietCandidates']), 'humanListening': False}
    report['technicalMeasurementPassed'] = loudness['passed'] and regression['passed'] and report['continuityParagraphs'] == 19 and report['newSustainedSourceRelativeDropCandidates'] == 0 and report['minParagraphVoiceCorrelation'] >= .90
    save(QA / 'audio-technical-measurements.json', report)
    print(json.dumps(report, ensure_ascii=False))


def finalize():
    technical, master_hash = current_master()
    measurements = read(QA / 'audio-technical-measurements.json')
    transcript = read(SOURCE / 'review/mix-asr-direct-review.json')
    decode_receipt = read(QA / 'final-aac-decode-v4.json')
    assert measurements['masterSha256'] == transcript['masterSha256'] == decode_receipt['masterSha256'] == master_hash
    decoded_hash = digest(DECODED)
    assert measurements['decodedAudioSha256'] == transcript['decodedAudioSha256'] == decode_receipt['decodedAudioSha256'] == decoded_hash
    assert transcript['wholeMixAsrCompared'] is True and transcript['sentenceOmissionsFound'] is False and transcript['sentenceRepetitionsFound'] is False
    assert measurements['technicalMeasurementPassed'] is True
    source_review = read(SOURCE / 'review/source-asr-direct-review.json')
    assert source_review['sourceAudioSha256'] == measurements['sourceAudioSha256'] == digest(SOURCE / 'narration.wav')
    auditions = read(SOURCE / 'review/listening/listening-clips.json')
    assert auditions['sourceAudioSha256'] == measurements['sourceAudioSha256'] and auditions['masterSha256'] == master_hash
    retained = [{'expected': c['word'], 'recognized': c['asr'], 'baselineSourceSeconds': c['baselineWordSeconds'],
                 'sourceSeconds': c['wordSeconds'], 'finalSeconds': [v + 2 for v in c['wordSeconds']]}
                for c in auditions['clips'] if c['kind'] == 'source' and c['group'] == 'retained']
    assert len(retained) == 4
    report = {'schemaVersion': 1, 'checkedAt': now(), 'revision': 'documentary-v4', 'masterSha256': master_hash,
              'masterPath': str(MASTER), 'technicalPassed': True, 'wholeMixAsrCompared': True,
              'humanListening': False, 'humanViewing': False, 'userApproval': False,
              'status': 'technical-audio-checks-passed-human-listening-pending',
              'scope': 'Actual encoded AAC technical evidence and whole transcript comparison; not perceptual or user approval.',
              'decodedAudioSha256': decoded_hash, 'decodedAudioFile': str(DECODED),
              'decodeReceipt': str(QA / 'final-aac-decode-v4.json'), 'pairedDecodedAudioIdentical': technical['pairedAudioIdentical'],
              'wholeTextReview': transcript,
              'newSpeechPronunciationCandidates': [dict(c, finalSeconds=[v + 2 for v in c['sourceSeconds']]) for c in source_review['newSpeechCandidates']],
              'retainedPronunciationCandidates': retained,
              'retainedCandidateTimingNote': 'Source and final times refer to the current v4; original baseline source times are preserved separately.',
              'loudness': measurements['loudness'], 'continuity': measurements,
              'preservation': {'sourceNarrationSha256': measurements['sourceAudioSha256'],
                               'reusedBodyExactPcmProof': str(SOURCE / 'pcm-reuse-proof.json'),
                               'correctFloatConcatAllSamplesExact': measurements['concatRegressionPassed'],
                               'audioArtifactsChangedByReviewer': False},
              'sourceAndFinalListeningPage': str(SOURCE / 'review/listening/index.html'),
              'remaining': ['Contextual pronunciation and natural-pace listening', 'Actual full-version user review before upload']}
    save(QA / 'audio-review.json', report)
    print(json.dumps({'status': report['status'], 'masterSha256': master_hash, 'humanListening': False}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--decode', action='store_true')
    parser.add_argument('--measure', action='store_true')
    parser.add_argument('--finalize', action='store_true')
    args = parser.parse_args()
    if not any([args.decode, args.measure, args.finalize]):
        print(json.dumps({'status': 'preflight-only', 'masterExists': MASTER.is_file(), 'technicalQaExists': (WORK / 'technical-qa.json').is_file(),
                          'sourceExists': (SOURCE / 'narration.wav').is_file(), 'gpuUsed': False, 'humanListening': False}))
        return
    if args.decode: decode()
    if args.measure: measure()
    if args.finalize: finalize()


if __name__ == '__main__':
    main()
