"""Read-only by default. Review one converted 11.05 recording with the approved ASR."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import sys
import wave


sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
MEDIA = Path('C:/Users/1/Videos/YamyamProduction/architectural-111-20261106')
INTAKE = MEDIA / '11-05-user-recording-b147d3b911382755'
CONVERSION = INTAKE / 'conversion-proof.json'
WAV = INTAKE / 'candidate-mono24k.wav'
REVIEW = INTAKE / 'independent-source-review-v1.json'
WORKER = INTAKE / 'source-recognition-worker.json'
PROJECT = ROOT / 'projects/shorts-leveldesign-11-05'
PEER = PROJECT / 'voice-asr-content-peer-review-v10.json'
QA10 = HERE / 'run-solution-path-voice-qa-v10.py'
LEVELS = HERE / 'first-level-continuity-review.py'
PINS = {
    CONVERSION: '95057b2ede4e7fb7a418d4910afdef64673e8e83ed4a6c7b0f058a0d6052fff0',
    WAV: 'f93ee55f18856140a7b18d586f5f3804c9f5e7e2adcf9691bcab0dc8571367fb',
    PEER: 'efab305ba28bc113c864720eb77d9edd001498471d77c15a69a086ad46355aa8',
    PROJECT / 'checkpoint.json': '7123b2dffc7203700a296b2ceac45c23b3dece912d0da6887f3ee09e8a2512bb',
    QA10: '875771be3da91dc973aadde82143caa50c05cb511b667d026866c2026a47533f',
    LEVELS: '545104df16cf26af0c0637faa76750bea1e5b70f424cc13820f13baa8b773544',
}
TARGETS = ('p008-c01', 'p013-c01')
RATE = 24000


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    with path.open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def pin(path, expected):
    if sha(path) != expected:
        raise ValueError(f'Pinned input changed: {path.name}')


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def inputs():
    for path, expected in PINS.items():
        pin(path, expected)
    control = read(ROOT / 'shared/publishing/video-production-control.json')['explicitArchitectural111Batch20261106']
    continuation = read(HERE / 'continuation.json')
    if (control['status'] in ('paused', 'cancelled', 'stopped') or
            control['youtubeAuthorized'] or control['driveAuthorized'] or
            continuation['currentTopicId'] != '11.05' or continuation['nextSelectedTopicId'] != '11.05'):
        raise ValueError('The selected local production scope changed')
    proof = read(CONVERSION)
    if not proof['authorization']['conversionOfProvidedRecording'] or Path(proof['candidate']['path']) != WAV:
        raise ValueError('The exact authorized conversion is required')
    pin(Path(proof['source']['path']), proof['source']['sha256'])
    with wave.open(str(WAV)) as source:
        if (source.getnchannels(), source.getsampwidth(), source.getframerate(), source.getcomptype()) != (1, 2, RATE, 'NONE'):
            raise ValueError('The converted candidate must remain mono PCM16 at 24 kHz')
        pcm = source.readframes(source.getnframes())
    if len(pcm) != proof['candidate']['frames'] * 2 or hashlib.sha256(pcm).hexdigest() != proof['candidate']['pcmSha256']:
        raise ValueError('Converted PCM does not match the conversion proof')
    targets = read(PEER)['nextInputAssessment']['targets']
    if tuple(row['sceneId'] for row in targets) != TARGETS:
        raise ValueError('The original sentence targets changed')
    return pcm, targets


def assess(qa10, levels, raw, samples, targets):
    words = raw.get('chunks', [])
    records = []
    for word in words:
        stamp = word.get('timestamp')
        if (not isinstance(stamp, (tuple, list)) or len(stamp) != 2 or
                any(type(t) not in (int, float) or not math.isfinite(t) for t in stamp) or
                not 0 <= stamp[0] < stamp[1] <= len(samples) / RATE):
            return {'status': 'hold', 'reason': 'Invalid independent word timestamp'}
        start, end = levels.sample_window(*stamp, RATE)
        if not 0 <= start < end <= len(samples):
            return {'status': 'hold', 'reason': 'Word crosses the candidate PCM boundary'}
        records.append({'globalRawSampleRange': [start, end], 'recognizedText': word['text'],
                        'startSeconds': stamp[0], 'endSeconds': stamp[1], 'durationSeconds': stamp[1] - stamp[0],
                        'levels': {'canonical': levels.levels(samples[start:end], RATE)}})
    alignment, reason = qa10.grouped_word_alignment(
        {'task': {'durationSeconds': len(samples) / RATE, 'offsetSample': 0, 'endSample': len(samples)},
         'rawRecognition': raw}, {'wordRecords': records, 'invalidWordWindows': []},
        [{'canonicalText': row['text']} for row in targets], levels)
    if alignment is None:
        return {'status': 'hold', 'reason': reason}
    cut, edges = alignment
    assessments = []
    for target, (begin, end) in zip(targets, ((0, cut), (cut, len(records)))):
        trend = levels.trend(records[begin:end], 'canonical')
        covered = (trend['words'] >= levels.POLICY['longTrendMinimumWords'] and
                   trend.get('spanSeconds', 0) >= levels.POLICY['longTrendMinimumSeconds'])
        assessments.append({'sceneId': target['sceneId'], 'firstWord': edges[begin], 'lastWord': edges[end - 1],
                            'wordTrend': trend, 'coverageSufficient': covered, 'sustainedDecline': trend['suspect']})
    status = ('ready-for-voice-and-join-review' if all(row['coverageSufficient'] and not row['sustainedDecline']
                                                     for row in assessments) else 'hold')
    return {'status': status, 'sentences': assessments, 'betweenSentencesSamples':
            [edges[cut - 1]['globalRawSampleRange'][1], edges[cut]['globalRawSampleRange'][0]]}


def blocker(qa10):
    qa10.legacy_barrier()
    alive = qa10.qa.raw.native.alive
    for marker in (qa10.WORKER, WORKER):
        if marker.exists():
            record = read(marker)
            if record.get('pid') != os.getpid() and (alive(record) or alive(record.get('child'))):
                return 'An existing recognition worker is active'
    if qa10.child_processes():
        return 'An existing recognizer child is active'
    return qa10.resource_reason()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    pcm, targets = inputs()
    identity = {'wavSHA256': PINS[WAV], 'conversionSHA256': PINS[CONVERSION], 'targetPeerSHA256': PINS[PEER],
                'adapterSHA256': sha(Path(__file__)), 'qa10SHA256': PINS[QA10]}
    if REVIEW.exists():
        review = read(REVIEW)
        if review.get('identity') != identity:
            raise ValueError('Existing review belongs to another recording or adapter')
        print(json.dumps({'status': review['assessment']['status'], 'existingReview': str(REVIEW)}, ensure_ascii=False))
        return 0
    qa10 = load('user_recording_qa10', QA10)
    reason = blocker(qa10)
    if reason or not args.execute:
        print(json.dumps({'ready': reason is None, 'reason': reason, 'modelLoaded': False, 'identity': identity}))
        return 75 if reason and args.execute else 0
    qa = qa10.qa
    worker = qa.raw.native.SingleWorker(WORKER).acquire()
    try:
        if REVIEW.exists():
            return 0
        worker.update(topicId='11.05', stage='recording-source-asr', source=identity)
        for model_pin in qa.APPROVED['modelPins']:
            pin(qa.MODEL / model_pin['path'], model_pin['sha256'])
        pin(qa.TRUSTED, qa.APPROVED['trustedSHA256'])
        pin(qa.GUARD, qa.APPROVED['guardSHA256'])
        reason = blocker(qa10)
        if reason:
            print(json.dumps({'ready': False, 'reason': reason, 'modelLoaded': False}))
            return 75
        os.environ.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', OMP_NUM_THREADS='2', MKL_NUM_THREADS='2')
        sys.path.insert(0, str(ROOT / 'qwen3-tts'))
        guard = load('user_recording_shared_gpu_guard', qa.GUARD)
        try:
            qa.raw.acquire_guard_before_model(guard)
        except qa.raw.PreModelResourceDeclined as exc:
            print(json.dumps({'ready': False, 'reason': str(exc), 'modelLoaded': False}))
            return 75
        trusted = load('user_recording_trusted_blind_recognizer', qa.TRUSTED)
        if trusted.MODEL != qa.MODEL:
            raise ValueError('Trusted recognizer model path changed')
        import numpy as np
        samples = np.frombuffer(pcm, dtype='<i2').astype(np.float32) / 32768
        raw = trusted.recognize(trusted.load_recognizer('cuda'), samples, RATE)
        assessment = assess(qa10, load('user_recording_level_primitives', LEVELS), raw, samples, targets)
        inputs()
        qa.voice.immutable_json(REVIEW, {'identity': identity, 'recognition': raw, 'assessment': assessment,
                                         'approvedProfile': qa.PROFILE, 'acceptedForFinal': False,
                                         'actualListening': False, 'speakerMatchVerified': False})
        print(json.dumps({'status': assessment['status'], 'review': str(REVIEW)}, ensure_ascii=False))
        return 0
    finally:
        worker.close()


if __name__ == '__main__':
    raise SystemExit(main())
