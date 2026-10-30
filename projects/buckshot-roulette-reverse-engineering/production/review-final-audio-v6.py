"""Actual v6 encoded-mix evidence. Default is readiness only.

Coordinator explicitly invokes decode/measure/ASR after completed encoding.
Whole-range checkpointed CPU ASR is new evidence, never human listening.
Finalization requires a separate direct transcript-comparison receipt.
Preserves every source, previous revision and master.
"""
from __future__ import annotations

import argparse
import os
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[3]
PROJECT = Path(__file__).resolve().parents[1]
SOURCE = PROJECT / 'production/local/audio-v4'
BASEWORK = PROJECT / 'production/local/documentary-v4'
WORK = PROJECT / 'production/local/documentary-v6'
QA = PROJECT / 'production/local/final-qa-v6'
OUTPUT = ROOT / 'output/buckshot-roulette-reverse-engineering-v6'
MASTER = OUTPUT / (PROJECT.name + '.captioned.mp4')
DECODED = QA / 'final-encoded-v6.wav'
OFFSET = 32.0
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
    receipt_path = QA / 'final-aac-decode-v6.json'
    if DECODED.exists():
        receipt = read(receipt_path)
        assert receipt['masterSha256'] == master_hash and receipt['decodedAudioSha256'] == digest(DECODED)
        return
    QA.mkdir(parents=True, exist_ok=True)
    command = [str(FFMPEG), '-hide_banner', '-nostdin', '-v', 'warning', '-threads', '2', '-i', str(MASTER),
               '-map', '0:a:0', '-vn', '-c:a', 'pcm_f32le', '-ar', '48000', '-ac', '2', '-n', str(DECODED)]
    log = QA / 'final-aac-decode-v6.log'
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
    target = WORK / 'base-mix.wav'
    inputs = [BASEWORK / 'bookend-brand.wav', WORK / 'intro-audio.wav', BASEWORK / 'body-mix.wav', BASEWORK / 'bookend-member.wav']
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
    save(QA / 'audio-concat-v6-regression.json', report)
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
            mixed_start = round((start + OFFSET) * 48000)
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
              'sourceOffsetSeconds': OFFSET, 'windowSeconds': .4, 'hopSeconds': .1,
              'method': 'Projection of source voice onto actual pre-limiter mix and decoded AAC mono average. Exact 32-second placement; every second final 48 kHz sample compared with source 24 kHz. Correlation is not isolated-voice listening.',
              'speechSelection': 'At least 60 ms overlap with current source ASR words; no source amplitude gate.',
              'candidateRule': 'At least 5 consecutive 100 ms hops with voice projection 6 dB below the paragraph median.',
              'paragraphs': paragraphs, 'sustainedSourceRelativeDropCandidates': all_drops,
              'sourceQuietCandidates': source_quiet, 'humanListening': False}
    # Source-relative gain changes identify mixer changes independently of the
    # naturally different speech RMS in adjacent paragraphs.
    report['adjacentProjectionJumpCandidates'] = [
        {'from': a['id'], 'to': b['id'], 'finalSeconds': b['sourceStart'] + OFFSET,
         'differenceDb': b['finalVoiceProjectionMedianDb'] - a['finalVoiceProjectionMedianDb']}
        for a, b in zip(paragraphs, paragraphs[1:])
        if abs(b['finalVoiceProjectionMedianDb'] - a['finalVoiceProjectionMedianDb']) >= 3
    ]
    save(QA / 'source-to-final-continuity-v6.json', report)
    return report


def measure():
    technical, master_hash = current_master()
    receipt = read(QA / 'final-aac-decode-v6.json')
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
              'continuityReport': 'production/local/final-qa-v6/source-to-final-continuity-v6.json',
              'continuityParagraphs': len(continuity_report['paragraphs']),
              'minParagraphVoiceCorrelation': min(p['medianCorrelation'] for p in continuity_report['paragraphs']),
              'newSustainedSourceRelativeDropCandidates': len(continuity_report['sustainedSourceRelativeDropCandidates']),
              'sourceQuietCandidates': len(continuity_report['sourceQuietCandidates']),
              'adjacentProjectionJumpCandidates': continuity_report['adjacentProjectionJumpCandidates'],
              'humanListening': False}
    import numpy as np
    import soundfile as sf
    clipping, total, maximum = 0, 0, 0.0
    with sf.SoundFile(DECODED) as actual:
        while True:
            block = actual.read(65536, dtype='float32', always_2d=True)
            if not len(block): break
            clipping += int(np.sum(np.abs(block) >= 1.0))
            total += block.size
            maximum = max(maximum, float(np.max(np.abs(block))))
    report['sampleClipping'] = {'sampleValuesAtOrBeyondFullScale': clipping,
                               'sampleValuesChecked': total, 'maximumAbsoluteAmplitude': maximum}
    report['technicalMeasurementPassed'] = (loudness['passed'] and regression['passed']
        and report['continuityParagraphs'] == len(read(SOURCE / 'narration.timing.json')['entries'])
        and report['newSustainedSourceRelativeDropCandidates'] == 0
        and not report['adjacentProjectionJumpCandidates']
        and report['minParagraphVoiceCorrelation'] >= .90 and clipping == 0)
    save(QA / 'audio-technical-measurements.json', report)
    print(json.dumps(report, ensure_ascii=False))


def run_asr():
    """One checkpointed CPU pass over all current final samples, music included.

    Paragraph windows use 0.2s overlap solely for edge context. The disjoint
    core intervals cover the entire decoded audio without silence assumptions.
    This writes automatic comparisons only, never a direct-review receipt.
    """
    import difflib
    import gc
    import psutil
    import soundfile as sf
    technical, master_hash = current_master()
    decoded_hash = digest(DECODED)
    receipt = read(QA / 'final-aac-decode-v6.json')
    assert receipt['masterSha256'] == master_hash and receipt['decodedAudioSha256'] == decoded_hash
    memory = psutil.virtual_memory()
    assert memory.available >= 8 * 2**30, 'Less than 8 GiB available; leave other applications untouched.'
    folder = QA / 'segment-asr'
    folder.mkdir(parents=True, exist_ok=True)
    lock = folder / 'active.lock'
    descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    os.write(descriptor, json.dumps({'pid': os.getpid(), 'startedAt': now(), 'masterSha256': master_hash}).encode())
    os.close(descriptor)
    state = {'schemaVersion': 1, 'startedAt': now(), 'status': 'preparing', 'masterSha256': master_hash,
             'decodedAudioSha256': decoded_hash, 'device': 'cpu', 'humanListening': False,
             'foreignProcessesChanged': False, 'gpuLeaseCreated': False, 'completedSegments': 0}
    try:
        info = sf.info(DECODED)
        entries = read(SOURCE / 'narration.timing.json')['entries']
        body_end = OFFSET + read(PROJECT / 'production/timeline-v5.json')['bodyFrameCount'] / 60
        assert abs(info.duration - body_end - 10) <= 1024 / 48000 + .001
        segments = [
            {'id': 'opening-01', 'kind': 'non-narration', 'expected': '', 'coreStart': 0.0, 'coreEnd': 16.0},
            {'id': 'opening-02', 'kind': 'non-narration', 'expected': '', 'coreStart': 16.0, 'coreEnd': OFFSET}
        ]
        for index, entry in enumerate(entries):
            end = float(entries[index + 1]['start']) + OFFSET if index + 1 < len(entries) else body_end
            segments.append({'id': f'{entry["scene_id"]}-{entry["paragraph"]:02}', 'kind': 'narration',
                             'expected': entry['text'], 'coreStart': OFFSET if index == 0 else float(entry['start']) + OFFSET,
                             'coreEnd': end})
        segments.append({'id': 'membership', 'kind': 'non-narration', 'expected': '',
                         'coreStart': body_end, 'coreEnd': info.duration})
        for row in segments:
            row['windowStart'] = max(0, row['coreStart'] - .2)
            row['windowEnd'] = min(info.duration, row['coreEnd'] + .2)
            assert 0 < row['windowEnd'] - row['windowStart'] < 36
        assert all(abs(a['coreEnd'] - b['coreStart']) < 1e-8 for a, b in zip(segments, segments[1:]))
        state.update(status='running', segments=segments, availableMemoryGiB=memory.available / 2**30)
        save(folder / 'execution.json', state)
        mono = folder / 'final-encoded-16k.wav'
        mono_receipt = folder / 'resample-receipt.json'
        if mono.exists():
            prior = read(mono_receipt)
            assert prior['decodedAudioSha256'] == decoded_hash and prior['monoSha256'] == digest(mono)
        else:
            command = [str(FFMPEG), '-hide_banner', '-nostdin', '-v', 'warning', '-threads', '2',
                       '-i', str(DECODED), '-vn', '-ac', '1', '-ar', '16000', '-c:a', 'pcm_f32le', '-n', str(mono)]
            with (folder / 'resample.log').open('w', encoding='utf-8') as log:
                result = subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
                                        creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
            assert result.returncode == 0
            save(mono_receipt, {'masterSha256': master_hash, 'decodedAudioSha256': decoded_hash,
                               'monoSha256': digest(mono), 'command': command})
        data, rate = sf.read(mono, dtype='float32')
        assert rate == 16000 and abs(len(data) / rate - info.duration) < .001
        completed, pending = [], []
        for row in segments:
            target = folder / (row['id'] + '.json')
            if target.exists():
                value = read(target)
                assert value['masterSha256'] == master_hash and value['decodedAudioSha256'] == decoded_hash and value['segment'] == row
                completed.append(value)
            else:
                pending.append(row)
        if pending:
            os.environ.update(CUDA_VISIBLE_DEVICES='', OMP_NUM_THREADS='2', MKL_NUM_THREADS='2',
                              OPENBLAS_NUM_THREADS='2', NUMEXPR_NUM_THREADS='2', HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1')
            import torch
            from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
            torch.set_num_threads(2)
            torch.set_num_interop_threads(1)
            assert not torch.cuda.is_initialized()
            model_path = Path('C:/Users/1/.cache/huggingface/hub/models--openai--whisper-large-v3-turbo/snapshots/41f01f3fe87f28c78e2fbf8b568835947dd65ed9')
            assert (model_path / 'model.safetensors').exists()
            model = AutoModelForSpeechSeq2Seq.from_pretrained(str(model_path), dtype=torch.float32,
                    low_cpu_mem_usage=True, use_safetensors=True, attn_implementation='sdpa').to('cpu').eval()
            processor = AutoProcessor.from_pretrained(str(model_path))
            transcriber = pipeline('automatic-speech-recognition', model=model, tokenizer=processor.tokenizer,
                feature_extractor=processor.feature_extractor, dtype=torch.float32, device='cpu')
            print('Local Whisper loaded once on CPU; current final mix full range, no source transcription.', flush=True)
            for row in pending:
                samples = data[round(row['windowStart'] * rate):round(row['windowEnd'] * rate)].copy()
                with torch.inference_mode():
                    result = transcriber({'array': samples, 'sampling_rate': rate},
                        generate_kwargs={'language': 'korean', 'task': 'transcribe'}, return_timestamps=True)
                chunks, selected = [], []
                for chunk in result.get('chunks', []):
                    a, b = chunk['timestamp']
                    a = 0 if a is None else float(a)
                    b = len(samples) / rate if b is None else float(b)
                    begin, end = row['windowStart'] + a, row['windowStart'] + b
                    chunks.append({'text': chunk['text'], 'timestamp': [begin, end]})
                    if row['coreStart'] <= (begin + end) / 2 < row['coreEnd']:
                        selected.append(chunk['text'])
                core_text = ' '.join(selected).strip() or str(result['text']).strip()
                normalize = lambda text: re.sub(r'[^a-z0-9가-힣]', '', text.lower())
                expected, recognized = normalize(row['expected']), normalize(core_text)
                comparison = difflib.SequenceMatcher(None, expected, recognized, autojunk=False)
                value = {'schemaVersion': 1, 'completedAt': now(), 'masterSha256': master_hash,
                         'decodedAudioSha256': decoded_hash, 'segment': row, 'language': 'korean',
                         'timestampMode': 'segment', 'rawText': str(result['text']).strip(), 'coreText': core_text,
                         'chunks': chunks, 'device': 'cpu', 'humanListening': False,
                         'automaticComparison': {'normalizedCharacterSimilarity': comparison.ratio(),
                           'opcodes': comparison.get_opcodes(), 'notAContentAccuracyOrListeningPass': True}}
                save(folder / (row['id'] + '.json'), value)
                completed.append(value)
                state['completedSegments'] = len(completed)
                save(folder / 'execution.json', state)
                print(json.dumps({'segment': row['id'], 'completed': len(completed), 'total': len(segments),
                                  'rawText': value['rawText']}, ensure_ascii=False), flush=True)
                del samples, result
                gc.collect()
        by_id = {value['segment']['id']: value for value in completed}
        ordered = [by_id[row['id']] for row in segments]
        aggregate = {'schemaVersion': 1, 'completedAt': now(), 'masterSha256': master_hash,
                     'audio_sha256': decoded_hash, 'audio': str(DECODED), 'language': 'korean',
                     'timestampMode': 'segment', 'device': 'cpu', 'sourceOffsetSeconds': OFFSET,
                     'text': ' '.join(value['coreText'] for value in ordered), 'segments': ordered,
                     'narrationParagraphCount': len(entries), 'allRangeCoverage': [0, info.duration],
                     'fullDecodedRangeAccountedFor': True, 'musicOnlyRangesAlsoTranscribed': True,
                     'humanListening': False, 'directComparisonPerformed': False,
                     'reviewStatus': 'Current full mix transcribed once by contiguous core coverage; direct text comparison still required.'}
        save(QA / 'mix-segment-asr.json', aggregate)
        state.update(status='finished', finishedAt=now(), completedSegments=len(ordered))
    except BaseException as error:
        state.update(status='failed', failedAt=now(), error=repr(error))
        raise
    finally:
        save(folder / 'execution.json', state)
        lock.unlink(missing_ok=True)


def finalize():
    technical, master_hash = current_master()
    measurements = read(QA / 'audio-technical-measurements.json')
    transcript = read(QA / 'mix-asr-direct-review.json')
    aggregate = read(QA / 'mix-segment-asr.json')
    decoded_hash = digest(DECODED)
    assert measurements['masterSha256'] == transcript['masterSha256'] == aggregate['masterSha256'] == master_hash
    assert measurements['decodedAudioSha256'] == transcript['decodedAudioSha256'] == aggregate['audio_sha256'] == decoded_hash
    assert aggregate['fullDecodedRangeAccountedFor'] and aggregate['sourceOffsetSeconds'] == OFFSET
    assert transcript['wholeMixAsrCompared'] is True
    assert transcript['sentenceOmissionsFound'] is False and transcript['sentenceRepetitionsFound'] is False
    assert measurements['technicalMeasurementPassed'] is True
    previous = read(PROJECT / 'production/local/final-qa-v5/audio-review.json')
    shifted_candidates = {}
    for name in ['newSpeechPronunciationCandidates', 'retainedPronunciationCandidates']:
        shifted_candidates[name] = [dict(candidate, finalSeconds=[value + 30 for value in candidate['finalSeconds']])
                                    for candidate in previous[name]]
    report = {'schemaVersion': 1, 'checkedAt': now(), 'revision': 'v6', 'masterSha256': master_hash,
              'masterPath': str(MASTER), 'technicalPassed': True, 'wholeMixAsrCompared': True,
              'newAsrPerformed': True, 'humanListening': False, 'humanViewing': False, 'userApproval': False,
              'status': 'technical-audio-checks-passed-human-listening-pending',
              'scope': 'Actual new encoded AAC technical evidence and separately recorded whole transcript comparison; not perceptual or user approval.',
              'decodedAudioSha256': decoded_hash, 'decodedAudioFile': str(DECODED),
              'decodeReceipt': str(QA / 'final-aac-decode-v6.json'), 'pairedDecodedAudioIdentical': technical['pairedAudioIdentical'],
              'wholeTextReview': transcript, 'loudness': measurements['loudness'], 'continuity': measurements,
              'preservation': {'sourceNarrationSha256': measurements['sourceAudioSha256'],
                               'baseConcatAllSamplesExact': measurements['concatRegressionPassed'],
                               'bodyStartSeconds': OFFSET, 'audioArtifactsChangedByReviewer': False},
              'remaining': ['Contextual pronunciation, music/effects balance and natural-pace listening',
                            'Actual full-version user review before upload'], **shifted_candidates}
    save(QA / 'audio-review.json', report)
    print(json.dumps({'status': report['status'], 'masterSha256': master_hash, 'humanListening': False}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--decode', action='store_true')
    parser.add_argument('--measure', action='store_true')
    parser.add_argument('--asr', action='store_true', help='Explicitly run checkpointed CPU full-current-mix ASR after final encoding.')
    parser.add_argument('--finalize', action='store_true')
    args = parser.parse_args()
    if not any([args.decode, args.measure, args.asr, args.finalize]):
        print(json.dumps({'status': 'preflight-only', 'masterExists': MASTER.is_file(),
                          'technicalQaExists': (WORK / 'technical-qa.json').is_file(),
                          'sourceExists': (SOURCE / 'narration.wav').is_file(),
                          'sourceOffsetSeconds': OFFSET, 'gpuUsed': False, 'humanListening': False}))
        return
    if args.decode: decode()
    if args.measure: measure()
    if args.asr: run_asr()
    if args.finalize: finalize()


if __name__ == '__main__':
    main()

