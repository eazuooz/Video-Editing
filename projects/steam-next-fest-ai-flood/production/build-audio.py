"""Narration stem from the approved-reference PCM (constant per-scene gain, global
-16 LUFS gain + short limiter) and the approved YouTube Audio Library track ducked
under speech. No game audio exists in this reality-check video."""
from pathlib import Path
import json, math, subprocess, hashlib
import numpy as np, soundfile as sf
R = Path(__file__).resolve().parents[3]; P = R / 'projects/steam-next-fest-ai-flood'; O = P / 'production/local/edit'
project = json.loads((P / 'project.json').read_text(encoding='utf8')); N = R / project['tts']['outputDir']
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
plan = json.loads((O / 'edit-plan.json').read_text(encoding='utf8')); duration = plan['totalFrames'] / 60; LEAD = plan['leadSeconds']
assert plan.get('timing') == 'measured-and-asr-aligned'
sr = 24000; voice = np.zeros(round(duration * sr), dtype=np.float32); reports = []
for s in plan['scenes']:
    f = N / 'chunks' / (s['id'] + '-scene.wav'); a, r = sf.read(f, dtype='float32'); assert r == sr
    q = json.loads((N / 'asr' / (s['id'] + '.json')).read_text(encoding='utf8')); assert q['audio_sha256'] == hashlib.sha256(f.read_bytes()).hexdigest()
    mask = speech_mask(len(a), sr, q['words']); level = db(rms(a[mask])); gain = float(10 ** ((-20 - level) / 20))
    out = a * gain; edge = min(round(.006 * sr), len(out) // 2); out[:edge] *= np.linspace(0, 1, edge); out[-edge:] *= np.linspace(1, 0, edge)
    start = round((s['paragraphs'][0]['start'] + LEAD) * sr); voice[start:start + len(out)] = out
    windows = []
    for i in range(0, len(a) - sr, round(sr * .5)):
        m = mask[i:i + sr]; v = a[i:i + sr][m]
        if len(v) >= sr * .25: windows.append({'time': i / sr, 'sourceSpeechDbfs': db(rms(v)), 'afterConstantGainDbfs': db(rms(v * gain))})
    reports.append({'scene': s['id'], 'sourceSha256': q['audio_sha256'], 'sourceSpeechRmsDbfs': level, 'fixedGainDb': db(gain), 'windows': windows, 'noSourcePcmOverwrite': True})
sf.write(O / 'voice-fixed-gain.wav', voice, sr, subtype='FLOAT')
logs = run(['-i', str(O / 'voice-fixed-gain.wav'), '-af', 'loudnorm=I=-16:TP=-2:LRA=9:print_format=json', '-f', 'null', '-'], 'voice-measure')
stats = json.loads(logs[logs.rfind('{'):logs.rfind('}') + 1]); gainDb = -16 - float(stats['input_i'])
norm = f'volume={gainDb}dB:precision=double,alimiter=limit=0.7499:attack=5:release=50:level=false:latency=true'
run(['-i', str(O / 'voice-fixed-gain.wav'), '-af', norm + ',pan=stereo|c0=c0|c1=c0', '-ar', '48000', '-c:a', 'pcm_s24le', str(O / 'narration-stem.wav')], 'voice-normalize')
music = R / 'shared/assets/music/youtube-audio-library/Nimbus-Eveningland.mp3'
assert hashlib.sha256(music.read_bytes()).hexdigest() == '06ddb8d0f2aa82e499ab2cb398b8a241c626d9d3da82bbaf274d1178435f8c08'
musicDuration = float(json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'json', str(music)]))['format']['duration'])
repeat = max(1, math.ceil((duration - 1) / (musicDuration - 1))); inputs = sum((['-i', str(music)] for _ in range(repeat)), []); filters = []; last = '0:a'
for i in range(1, repeat): filters.append(f'[{last}][{i}:a]acrossfade=d=1:c1=tri:c2=tri[m{i}]'); last = f'm{i}'
filters.append(f'[{last}]atrim=duration={duration},loudnorm=I=-28:TP=-4:LRA=7,afade=t=in:st=0:d=0.45,afade=t=out:st={duration - .45}:d=0.45[music]')
run([*inputs, '-filter_complex', ';'.join(filters), '-map', '[music]', '-t', str(duration), '-ar', '48000', '-ac', '2', '-c:a', 'pcm_s24le', str(O / 'music-stem.wav')], 'music-level')
graph = '[0:a]asplit=2[voice][side];[1:a][side]sidechaincompress=threshold=0.025:ratio=3:attack=35:release=400[bg];[voice][bg]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.794:level=false:latency=true[out]'
run(['-i', str(O / 'narration-stem.wav'), '-i', str(O / 'music-stem.wav'), '-filter_complex', graph, '-map', '[out]', '-t', str(duration), '-ar', '48000', '-c:a', 'pcm_s24le', str(O / 'final-mix.wav')], 'final-mix')
report = {'scenes': reports, 'gameAudio': 'none (reality-check video; no gameplay)', 'duration': duration, 'normalizationMeasurementOnly': stats, 'voiceGainMode': 'constant-global-gain-with-short-peak-limiter', 'globalGainDb': gainDb, 'musicInitialLufs': -28, 'music': 'Nimbus — Eveningland (YouTube Audio Library, approved license file)', 'voiceDucked': False, 'amixNormalize': False, 'sourcePcmPreserved': True, 'sourceToStemToEncodedContinuity': 'pending', 'fullFinalAsr': 'pending', 'humanWholeListening': 'pending'}
(O / 'audio-build.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf8'); print('Mixed', duration, 'seconds')
