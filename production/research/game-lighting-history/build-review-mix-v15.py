"""Place current PCM losslessly and build a CPU Nimbus mix for direct review."""
import importlib.util, os, re, traceback
from pathlib import Path
os.environ.setdefault('OMP_NUM_THREADS', '2')
os.environ.setdefault('MKL_NUM_THREADS', '2')
import numpy as np
import soundfile as sf
_p = Path(__file__).with_name('review-media-common-v15.py')
_s = importlib.util.spec_from_file_location('review_media', _p)
m = importlib.util.module_from_spec(_s); _s.loader.exec_module(m)
ROOT, PROD, FF, FP = m.ROOT, m.PROD, m.FF, m.FP
out = ROOT / 'production/research/game-lighting-history/local/review-mix-v15'
plan_path = PROD / 'measured-native-timeline-candidate-v15.json'
plan = m.read(plan_path)
for x in plan['inputHashes']: assert m.sha(ROOT / x['path']) == x['sha256'], 'Measured PCM input changed'
guide_approval = PROD / 'native-guide01-onset-asr-direct-review-v3.json'
assert m.read(guide_approval)['allCurrentGuideContentApproved'], 'Current guide content not directly reviewed'
assert abs(plan['ratioFrameError']) <= 1 and plan['totals']['finalFrames'] == 93084
original = ROOT / 'shared/output/narration/game-lighting-history-03/qwen3-1.7b-balanced-v1/game-lighting-history-03-qwen3-1.7b-balanced-v1.wav'
assert m.sha(original) == '687a39416d916d0666ff1fee7cd5c1712e5566a7bb347d7526cbd05bec3a58cc'
manifest = m.read(PROD.parent / 'project.json')
music_approval = manifest['audio']['backgroundMusic']
music = ROOT / music_approval['file']
assert music_approval['approvalStatus'] == 'approved'
assert m.sha(music) == music_approval['restoration']['sha256'] == '36a0c40b73e7dc656470c242cce0047bd987abc595f28b013265d947a10d98ef'
observation = m.resources()
state_path = PROD / 'review-mix-execution-v15.json'
assert not state_path.exists(), 'Preserve existing mix state; inspect/resume completed steps explicitly'
out.mkdir(parents=True, exist_ok=True)
state = dict(startedAt=m.stamp(), status='running', worker=m.worker(), active=None,
             resourceObservation=observation, commands=[], results=[], cpuThreads=2, gpuJobs=0,
             newTts=0, finalMixedAsrApproved=False, allFinalPixelsReviewed=False,
             humanWholeListening='pending', humanPronunciation='pending')
m.save(state_path, state)
def ff(args, label):
    return m.run([FF, '-n', '-hide_banner', '-nostdin', '-threads', '2', *args],
                 label, state, state_path, out)
def scan(p, label, target_i=-16, target_tp=-2):
    job = ff(['-i', p, '-af', f'loudnorm=I={target_i}:TP={target_tp}:LRA=11:print_format=json',
              '-f', 'null', 'NUL'], label)
    log = (ROOT / job['log']).read_text('utf-8')
    measurement = m.json.loads(re.search(r'\{\s*"input_i"[\s\S]*?\}', log).group())
    return dict(measurement=measurement, command=job)
try:
    final_frames = plan['totals']['finalFrames']; duration = final_frames / 60
    source, sr = sf.read(original, dtype='float32'); assert sr == 24000 and source.ndim == 1 and len(source) == 26073601
    # PCM16 original values have an exact float32 representation; FLOAT guide WAVs
    # retain every sample value. No int16 conversion is used for the placed master.
    timeline = np.zeros(final_frames * 400, dtype='float32')
    placements, source_ranges = [], []
    previous_frame = plan['introFrames']
    for slot in plan['slots']:
        assert slot['fromFrame'] == previous_frame
        previous_frame = slot['toFrame']
        if slot['kind'] == 'original-paragraph':
            a, b = slot['sourceSampleRange']; x = source[a:b]
            source_ranges.append((a, b)); source_path = original; source_sha = m.sha(original) if not placements else placements[0]['sourceSha256']
        else:
            source_path = ROOT / slot['pcm']['path']; source_sha = m.sha(source_path)
            assert source_sha == slot['pcm']['sha256']
            x, rate = sf.read(source_path, dtype='float32')
            assert rate == 24000 and x.ndim == 1 and len(x) == slot['pcm']['samples']
        start = slot['fromFrame'] * 400
        assert len(x) + slot['paddingSamples'] == slot['frames'] * 400
        timeline[start:start + len(x)] = x
        assert np.array_equal(timeline[start:start + len(x)], x)
        placements.append(dict(id=slot['id'], kind=slot['kind'], startFrame=slot['fromFrame'],
                               frames=slot['frames'], samples=len(x), sourcePath=m.rel(source_path),
                               sourceSha256=source_sha, sourceSampleRange=slot.get('sourceSampleRange'),
                               paddingSamples=slot['paddingSamples'], allSourceSampleValuesExact=True))
    assert source_ranges[0][0] == 0 and source_ranges[-1][1] == len(source)
    assert all(source_ranges[i][1] == source_ranges[i + 1][0] for i in range(len(source_ranges) - 1))
    assert sum(b - a for a, b in source_ranges) == len(source)
    assert np.count_nonzero(timeline[:120 * 400]) == 0 and np.count_nonzero(timeline[-600 * 400:]) == 0
    voice = out / 'narration-timed.wav'; assert not voice.exists()
    sf.write(voice, timeline, 24000, subtype='FLOAT')
    back, rate = sf.read(voice, dtype='float32')
    assert rate == 24000 and np.array_equal(back, timeline)
    placement_proof = dict(createdAt=m.stamp(), planSha256=m.sha(plan_path),
                           currentGuideContentApprovalSha256=m.sha(guide_approval),
                           originalFileSha256=m.sha(original), originalSamples=len(source),
                           voicePath=m.rel(voice), voiceSha256=m.sha(voice), samples=len(back),
                           seconds=duration, sampleRate=24000, subtype='FLOAT', placements=placements,
                           allOriginalSamplesPartitionedOnce=True, all104CurrentSourceValuesExact=True,
                           placedMasterRoundTripExact=True, introAndMembershipNarrationSilent=True,
                           sourceAudioStreams=0, newTts=0, finalMixedAsrApproved=False)
    m.save(PROD / 'review-pcm-preservation-v15.json', placement_proof)
    del timeline, back, source
    raw_scan = scan(voice, '01-raw-voice-scan'); raw = raw_scan['measurement']
    normal = out / 'voice-normalized-pass.wav'
    norm = (f"loudnorm=I=-16:TP=-2:LRA=11:measured_I={raw['input_i']}:measured_TP={raw['input_tp']}:"
            f"measured_LRA={raw['input_lra']}:measured_thresh={raw['input_thresh']}:offset={raw['target_offset']}:"
            'linear=true,aresample=48000,aformat=channel_layouts=stereo')
    ff(['-i', voice, '-af', norm, '-c:a', 'pcm_f32le', normal], '02-two-pass-voice-normalization')
    x, rate = sf.read(normal, dtype='float32', always_2d=True)
    assert rate == 48000 and len(x) == final_frames * 800
    outside_nonzero = int(np.count_nonzero(x[:120 * 800]) + np.count_nonzero(x[-600 * 800:]))
    x[:120 * 800] = 0; x[-600 * 800:] = 0
    body_only = out / 'voice-normalized-body-only.wav'
    sf.write(body_only, x, rate, subtype='FLOAT'); del x
    measured_scan = scan(body_only, '03-normalized-voice-scan'); measured = measured_scan['measurement']
    gain = min(-16 - float(measured['input_i']), -2 - float(measured['input_tp']))
    normalized = out / 'voice-normalized.wav'
    ff(['-i', body_only, '-af', f'volume={gain}dB', '-c:a', 'pcm_f32le', normalized], '04-voice-constant-gain')
    music_sha = m.sha(music)
    pr = m.json.loads(m.subprocess.run([str(FP), '-v', 'error', '-show_format', '-of', 'json', str(music)],
                                     capture_output=True, text=True, check=True).stdout)
    music_duration = float(pr['format']['duration']); n = int(np.ceil((duration - 1) / (music_duration - 1)))
    if n > 1:
        chain = ';'.join(f"{'[0:a]' if k == 1 else '[b' + str(k - 1) + ']'}[{k}:a]acrossfade=d=1:c1=tri:c2=tri[b{k}]" for k in range(1, n))
        continuous = out / 'nimbus-continuous.wav'
        ff([*sum((['-i', music] for _ in range(n)), []), '-filter_complex', chain, '-map', f'[b{n - 1}]',
            '-c:a', 'pcm_f32le', continuous], '05-continuous-Nimbus')
        music = continuous
    bg = out / 'bgm-before-ducking.wav'
    bg_filter = (f'atrim=duration={duration},asetpts=PTS-STARTPTS,loudnorm=I=-28:TP=-3:LRA=11,'
                 f'aresample=48000,aformat=channel_layouts=stereo,afade=t=in:d=0.45,afade=t=out:st={duration - .45}:d=0.45')
    ff(['-i', music, '-af', bg_filter, '-c:a', 'pcm_f32le', bg], '06-background-level')
    mix = out / 'review-mix.wav'; aac = out / 'review-mix.m4a'
    filt = ('[0:a]asplit[n][d];[1:a][d]sidechaincompress=threshold=0.08:ratio=2.2:attack=15:release=280[bg];'
            '[n][bg]amix=inputs=2:normalize=0,alimiter=limit=0.80:level=false:latency=true[mix]')
    ff(['-i', normalized, '-i', bg, '-filter_complex', filt, '-map', '[mix]', '-ar', '48000', '-ac', '2',
        '-c:a', 'pcm_s16le', mix], '07-Nimbus-ducked-mix')
    ff(['-i', mix, '-c:a', 'aac', '-b:a', '192k', aac], '08-review-AAC')
    final_scan = scan(aac, '09-mixed-AAC-scan', -16, -1.5); final = final_scan['measurement']
    assert abs(float(final['input_i']) + 16) <= .6 and float(final['input_tp']) <= -1.5, final
    assert sf.info(mix).frames == final_frames * 800
    decode = ff(['-i', aac, '-f', 'null', 'NUL'], '10-mixed-AAC-decode')
    settings = dict(createdAt=m.stamp(), status='candidate-built-awaiting-direct-current-mixed-review',
                    durationSeconds=duration, frames=final_frames, planSha256=m.sha(plan_path),
                    pcmPlacementProofSha256=m.sha(PROD / 'review-pcm-preservation-v15.json'),
                    voiceSourceSha256=m.sha(voice), narration=raw_scan, normalizedVoice=measured_scan,
                    constantVoiceGainDb=gain, normalizedOutsideBodyNonzeroBeforeRepair=outside_nonzero,
                    changedNormalizedOutsideBodyOnly=True, allBodyNormalizedSamplesRetained=True,
                    finalAacMeasurement=final_scan, wav=m.rel(mix), wavSha256=m.sha(mix), aac=m.rel(aac),
                    aacSha256=m.sha(aac), wholeAacDecode=decode, bgmSha256=m.sha(bg),
                    approvedNimbusReferenceSha256=music_sha, continuousApprovedNimbus=True,
                    sourceAudioStreams=0, newTts=0, originalNimbusFileVerified=False,
                    finalMixedAsrApproved=False, humanWholeListening='pending', humanPronunciation='pending',
                    allFinalPixelsReviewed=False, collected=False, uploaded=False)
    m.save(PROD / 'review-mix-settings-v15.json', settings)
    state.update(status='complete', completedAt=m.stamp(), exitCode=0, active=None,
                 settings='projects/game-lighting-history-03/production/review-mix-settings-v15.json')
    m.save(state_path, state)
    print(m.json.dumps(dict(frames=final_frames, seconds=duration, lufs=final['input_i'], truePeak=final['input_tp'],
                           sourcePcmSamplesExact=True, finalMixedAsrApproved=False)), flush=True)
except BaseException:
    state.update(status='failed', failedAt=m.stamp(), exitCode=1, error=traceback.format_exc())
    m.save(state_path, state)
    raise
