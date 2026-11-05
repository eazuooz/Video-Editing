"""Narration stem from the approved-reference PCM (constant per-scene gain, global
-16 LUFS gain + short limiter) and the approved YouTube Audio Library track ducked
under speech. No game audio exists in this reality-check video."""
from pathlib import Path
import json, math, subprocess, hashlib
import numpy as np, soundfile as sf
from edition import BASE, EXTENDED, LOCAL, voice_dir
R = Path(__file__).resolve().parents[3]; P = Path(__file__).resolve().parents[1]; O = LOCAL
def run(args, name):
    p = subprocess.run(['ffmpeg', '-hide_banner', '-y', *args], cwd=R, capture_output=True); (O / (name + '.log')).write_bytes(p.stderr)
    if p.returncode: raise RuntimeError(p.stderr.decode(errors='replace')[-3000:])
    return p.stderr.decode(errors='replace')
def db(v): return float(20 * np.log10(max(float(v), 1e-10)))
def rms(a): return float(np.sqrt(np.mean(a * a))) if len(a) else 0.
def speech_mask(n, rate, words):
    mask = np.zeros(n, dtype=bool)
    for w in words:
        a, b = w['timestamp']
        if a is None or b is None: continue
        mask[max(0, round(a * rate)):min(n, round(b * rate))] = True
    return mask
plan = json.loads((O / 'timeline.json').read_text(encoding='utf8')); duration = plan['totalFrames'] / 60; LEAD = 2.0
assert len(plan['scenes']) == (17 if EXTENDED else 12) and plan['totalFrames'] == plan['bodyFrames'] + 720
sr = 24000; voice = np.zeros(round(duration * sr), dtype=np.float32); reports = []
for s in plan['scenes']:
    N = voice_dir(s['id'])
    f = N / 'chunks' / (s['id'] + '-scene.wav'); a, r = sf.read(f, dtype='float32'); assert r == sr
    q = json.loads((N / 'asr' / (s['id'] + '.json')).read_text(encoding='utf8')); assert q['audio_sha256'] == hashlib.sha256(f.read_bytes()).hexdigest()
    mask = speech_mask(len(a), sr, q['words']); level = db(rms(a[mask]))
    # Equalize scenes on the median of 1 s speech windows (perceptual level), not on peak-weighted RMS.
    wl = [db(rms(a[i:i + sr][mask[i:i + sr]])) for i in range(0, len(a) - sr, round(sr * .5)) if mask[i:i + sr].sum() >= sr * .25]
    median = float(np.median(wl)) if wl else level; gain = float(10 ** ((-21 - median) / 20))
    out = a * gain; edge = min(round(.006 * sr), len(out) // 2); out[:edge] *= np.linspace(0, 1, edge); out[-edge:] *= np.linspace(1, 0, edge)
    start = round((s['voiceStart'] + LEAD) * sr); voice[start:start + len(out)] = out
    windows = []
    for i in range(0, len(a) - sr, round(sr * .5)):
        m = mask[i:i + sr]; v = a[i:i + sr][m]
        if len(v) >= sr * .25: windows.append({'time': i / sr, 'sourceSpeechDbfs': db(rms(v)), 'afterConstantGainDbfs': db(rms(v * gain))})
    reports.append({'scene': s['id'], 'sourceSha256': q['audio_sha256'], 'sourceSpeechRmsDbfs': level, 'fixedGainDb': db(gain), 'windows': windows, 'noSourcePcmOverwrite': True})
sf.write(O / 'voice-fixed-gain.wav', voice, sr, subtype='FLOAT')
# Qwen syllable onsets carry 40–110 ms bursts 15–18 dB above the speech median (crest 23–30 dB in
# every take). Taming only those peaks (threshold 8 dB above the −22 dBFS speech median, peak
# detection) keeps ordinary speech untouched and stops the −16 LUFS gain from driving the limiter.
TAME = 'acompressor=threshold=0.2:ratio=4:attack=2:release=80:knee=2:detection=peak:makeup=1'
run(['-i', str(O / 'voice-fixed-gain.wav'), '-af', TAME, '-c:a', 'pcm_f32le', str(O / 'voice-tamed.wav')], 'voice-tame')
# Measure the delivered dual-mono image: BS.1770 sums both channels, so a mono file reads 3 LU quieter than the stereo stem it becomes.
logs = run(['-i', str(O / 'voice-tamed.wav'), '-af', 'pan=stereo|c0=c0|c1=c0,loudnorm=I=-16:TP=-2:LRA=9:print_format=json', '-f', 'null', '-'], 'voice-measure')
stats = json.loads(logs[logs.rfind('{'):logs.rfind('}') + 1]); gainDb = -16 - float(stats['input_i'])
norm = f'volume={gainDb}dB:precision=double,alimiter=limit=0.7499:attack=5:release=50:level=false:latency=true'
run(['-i', str(O / 'voice-tamed.wav'), '-af', norm + ',pan=stereo|c0=c0|c1=c0', '-ar', '48000', '-c:a', 'pcm_s24le', str(O / 'narration-stem.wav')], 'voice-normalize')
music = R / 'shared/assets/music/youtube-audio-library/Nimbus-Eveningland.mp3'
assert hashlib.sha256(music.read_bytes()).hexdigest() == '06ddb8d0f2aa82e499ab2cb398b8a241c626d9d3da82bbaf274d1178435f8c08'
musicDuration = float(json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'json', str(music)]))['format']['duration'])
repeat = max(1, math.ceil((duration - 1) / (musicDuration - 1))); inputs = sum((['-i', str(music)] for _ in range(repeat)), []); filters = []; last = '0:a'
for i in range(1, repeat): filters.append(f'[{last}][{i}:a]acrossfade=d=1:c1=tri:c2=tri[m{i}]'); last = f'm{i}'
filters.append(f'[{last}]atrim=duration={duration},loudnorm=I=-28:TP=-4:LRA=7,afade=t=in:st=0:d=0.45,afade=t=out:st={duration - .45}:d=0.45[music]')
run([*inputs, '-filter_complex', ';'.join(filters), '-map', '[music]', '-t', str(duration), '-ar', '48000', '-ac', '2', '-c:a', 'pcm_s24le', str(O / 'music-stem.wav')], 'music-level')
graph = '[0:a]asplit=2[voice][side];[1:a][side]sidechaincompress=threshold=0.025:ratio=3:attack=35:release=400[bg];[voice][bg]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.794:level=false:latency=true[out]'
run(['-i', str(O / 'narration-stem.wav'), '-i', str(O / 'music-stem.wav'), '-filter_complex', graph, '-map', '[out]', '-t', str(duration), '-ar', '48000', '-c:a', 'pcm_s24le', str(O / 'final-mix.wav')], 'final-mix')
if EXTENDED:
    # Preserve every PCM sample of the first twelve scenes, including the
    # original continuous music and actual compressor/limiter envelope.
    prefix=round((2+plan['baseBodyFrames']/60)*48000)
    bridge=round(.24*48000)
    assert (2+plan['scenes'][12]['voiceStart'])*48000>=prefix+bridge
    preserved={}
    for name in ['narration-stem.wav','final-mix.wav']:
        counter=hashlib.sha256()
        tmp=O/('preserved-'+name)
        with sf.SoundFile(BASE/name) as old, sf.SoundFile(O/name) as new, sf.SoundFile(tmp,'w',samplerate=48000,channels=2,subtype='PCM_24') as combined:
            assert old.samplerate==new.samplerate==48000 and old.channels==new.channels==2
            for start in range(0,prefix,48000):
                block=old.read(min(48000,prefix-start),dtype='int32')
                combined.write(block); counter.update(block.astype('<i4',copy=False).tobytes())
            earlier=old.read(bridge,dtype='float64')
            new.seek(prefix)
            later=new.read(bridge,dtype='float64')
            weight=np.linspace(0,1,bridge)[:,None]
            combined.write(earlier*(1-weight)+later*weight)
            while new.tell()<len(new):
                combined.write(new.read(48000,dtype='int32'))
            assert combined.tell()==len(new)
        tmp.replace(O/name)
        with sf.SoundFile(O/name) as checked:
            verify=hashlib.sha256()
            for start in range(0,prefix,48000):
                verify.update(checked.read(min(48000,prefix-start),dtype='int32').astype('<i4',copy=False).tobytes())
        assert verify.digest()==counter.digest()
        preserved[name]=counter.hexdigest()
    (O/'retained-prefix.json').write_text(json.dumps({'frames48k':prefix,'channels':2,
        'pcmSha256AsSigned32Le':preserved,'firstNewPictureSeconds':prefix/48000,
        'musicBridgeSeconds':bridge/48000,'firstNewVoicePlacementSeconds':2+plan['scenes'][12]['voiceStart']},
        indent=2)+'\n',encoding='utf-8')
    from balance_coda import balance
    balance(O,plan)
report = {'scenes': reports, 'gameAudio': 'none (reality-check video; no gameplay)', 'duration': duration, 'normalizationMeasurementOnly': stats, 'voiceGainMode': 'line-level-equalized-takes + onset-peak-taming + constant-global-gain + short-peak-limiter', 'onsetTaming': TAME, 'globalGainDb': gainDb, 'musicInitialLufs': -28, 'music': 'Nimbus — Eveningland (YouTube Audio Library, approved license file)', 'voiceDucked': False, 'amixNormalize': False, 'sourcePcmPreserved': True, 'sourceToStemToEncodedContinuity': 'pending', 'fullFinalAsr': 'pending', 'humanWholeListening': 'pending'}
(O / 'audio-build.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf8'); print('Mixed', duration, 'seconds')
