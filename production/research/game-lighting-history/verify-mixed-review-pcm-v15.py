"""Verify existing current PCM/windows without synthesis or recognition.

This establishes provenance and placement, not listening or language approval.
Run only after the sole current mixed-ASR worker has completed.
"""
import importlib.util, os
from pathlib import Path
os.environ.setdefault('OMP_NUM_THREADS', '2')
os.environ.setdefault('MKL_NUM_THREADS', '2')
import numpy as np
import soundfile as sf
import psutil
_p = Path(__file__).with_name('review-media-common-v15.py')
_s = importlib.util.spec_from_file_location('review_media', _p)
m = importlib.util.module_from_spec(_s); _s.loader.exec_module(m)
ROOT, PROD = m.ROOT, m.PROD
state = m.read(PROD / 'review-mixed-asr-execution-v15.json')
assert state['status'] == 'complete' and state['exitCode'] == 0 and len(state['results']) == 54
worker = state['worker']
if psutil.pid_exists(worker['pid']):
    assert abs(psutil.Process(worker['pid']).create_time() - worker['createTime']) > .01, 'ASR worker still alive'
assert not m.owned_media(), 'Preserve active owned media job'
dest = PROD / 'review-mixed-asr-pcm-corroboration-v15.json'
assert not dest.exists(), 'Preserve completed verification'
resource_observation = m.resources()
verification_worker = m.worker()
settings_path = PROD / 'review-mix-settings-v15.json'
settings = m.read(settings_path)
plan_path = PROD / 'measured-native-timeline-candidate-v15.json'
assert state['planSha256'] == settings['planSha256'] == m.sha(plan_path)
mix = ROOT / settings['wav']
assert m.sha(mix) == settings['wavSha256'] == state['mixSha256']
proof_path = PROD / 'review-pcm-preservation-v15.json'
proof = m.read(proof_path)
assert settings['pcmPlacementProofSha256'] == m.sha(proof_path)
voice_path = ROOT / proof['voicePath']
assert m.sha(voice_path) == settings['voiceSourceSha256'] == proof['voiceSha256']
voice, rate = sf.read(voice_path, dtype='float32')
assert rate == 24000 and voice.ndim == 1 and len(voice) == proof['samples']
placements, ranges, hashes = [], [], {}
for p in proof['placements']:
    source_path = ROOT / p['sourcePath']
    if p['sourcePath'] not in hashes: hashes[p['sourcePath']] = m.sha(source_path)
    assert hashes[p['sourcePath']] == p['sourceSha256']
    with sf.SoundFile(source_path) as source:
        assert source.samplerate == 24000 and source.channels == 1
        span = p.get('sourceSampleRange')
        if span:
            source.seek(span[0]); original = source.read(span[1] - span[0], dtype='float32')
            ranges.append(span)
        else: original = source.read(dtype='float32')
    assert len(original) == p['samples']
    begin = p['startFrame'] * 400
    assert np.array_equal(voice[begin:begin + len(original)], original)
    end = begin + p['frames'] * 400
    assert np.count_nonzero(voice[begin + len(original):end]) == 0
    placements.append(dict(id=p['id'], sourceSha256=p['sourceSha256'], samples=p['samples'],
                           startFrame=p['startFrame'], sourceValuesExact=True, paddingOnlySilence=True))
assert ranges[0][0] == 0 and ranges[-1][1] == proof['originalSamples']
assert all(a[1] == b[0] for a, b in zip(ranges, ranges[1:]))
assert sum(b - a for a, b in ranges) == proof['originalSamples']
assert len(placements) == 105 and len(hashes) == 21
assert np.count_nonzero(voice[:120 * 400]) == np.count_nonzero(voice[-600 * 400:]) == 0
del voice
windows = []
for item in state['results']:
    result_path = ROOT / item['path']
    assert m.sha(result_path) == item['sha256']
    result = m.read(result_path); window = result['window']
    window_path = result_path.with_suffix('.wav')
    assert m.sha(window_path) == result['windowSha256']
    actual, sr = sf.read(window_path, dtype='float32')
    with sf.SoundFile(mix) as source:
        assert source.samplerate == 48000 and source.channels == 2
        source.seek(window['fromFrame'] * 800)
        expected = source.read((window['toFrame'] - window['fromFrame']) * 800,
                               dtype='float32', always_2d=True).mean(axis=1)
    assert sr == 48000 and len(actual) == result['sourceSamples']
    assert np.array_equal(actual, expected)
    windows.append(dict(label=item['label'], resultSha256=item['sha256'], windowSha256=result['windowSha256'],
                        fromFrame=window['fromFrame'], toFrame=window['toFrame'],
                        allCurrentMixedSampleValuesExact=True))
m.save(dest, dict(verifiedAt=m.stamp(), status='provenance-verified-language-review-separate',
                  worker=verification_worker, resourceObservation=resource_observation,
                  cpuThreads=2, gpuJobs=0, exitCode=0,
                  mixSha256=state['mixSha256'], planSha256=state['planSha256'],
                  pcmPlacementProofSha256=m.sha(proof_path), voiceSha256=proof['voiceSha256'],
                  placements=placements, sourceHashes=hashes, windows=windows,
                  allOriginalSamplesPartitionedOnce=True, all105PlacementsSourceValuesExact=True,
                  all54RecognitionWindowsCurrentMixExact=True, noNewAudioOrImages=True,
                  automaticContentApproval=False, finalMixedAsrApproved=False,
                  humanWholeListening='pending', humanPronunciation='pending'))
print(m.json.dumps(dict(placements=len(placements), windows=len(windows), provenanceVerified=True,
                        languageApproved=False, mediaCreated=0, imagesCreated=0)))
