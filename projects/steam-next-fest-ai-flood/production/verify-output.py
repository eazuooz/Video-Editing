"""One integrity pass on the current clean/captioned pair: full decode, PTS, AAC,
loudness, speech-level continuity, and a decoded contact sheet for direct review."""
from pathlib import Path
import subprocess, json, hashlib, math, sys
import numpy as np, soundfile as sf
from PIL import Image, ImageDraw
R = Path(__file__).resolve().parents[3]; P = R / 'projects/steam-next-fest-ai-flood'; O = P / 'production/local/edit'; Q = O / 'qa'; Q.mkdir(exist_ok=True)
project = json.loads((P / 'project.json').read_text(encoding='utf8')); N = R / project['tts']['outputDir']
def run(cmd): return subprocess.run(cmd, cwd=R, capture_output=True, check=True).stdout
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
plan = json.loads((O / 'edit-plan.json').read_text(encoding='utf8')); layout = json.loads((O / 'caption-layout.json').read_text(encoding='utf8')); LEAD = plan['leadSeconds']
results = []
for kind in ['clean', 'captioned']:
    f = O / f'steam-next-fest-{kind}.mp4'; digest = sha(f); receipt = Q / (kind + '-integrity.json')
    if receipt.exists() and json.loads(receipt.read_text()).get('sha256') == digest: results.append(json.loads(receipt.read_text())); continue
    info = json.loads(run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(f)])); video = next(s for s in info['streams'] if s['codec_type'] == 'video'); audio = next(s for s in info['streams'] if s['codec_type'] == 'audio')
    assert (video['width'], video['height'], video['r_frame_rate'], int(video['nb_frames'])) == (1920, 1080, '60/1', plan['totalFrames'])
    run(['ffmpeg', '-v', 'error', '-xerror', '-i', str(f), '-f', 'null', '-'])
    pts = run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'frame=best_effort_timestamp_time', '-of', 'csv=p=0', str(f)]).decode().splitlines(); times = [float(s.split(',')[0]) for s in pts if s.strip() and s.split(',')[0].strip()]
    assert len(times) == plan['totalFrames'] and all(abs(b - a - 1 / 60) < .00004 for a, b in zip(times, times[1:]))
    adts = run(['ffmpeg', '-v', 'error', '-i', str(f), '-map', '0:a', '-c:a', 'copy', '-f', 'adts', '-'])
    result = {'kind': kind, 'sha256': digest, 'bytes': f.stat().st_size, 'frames': len(times), 'width': 1920, 'height': 1080, 'fps': 60, 'fullDecodePassed': True, 'ptsMonotonicAndUniform': True, 'aacSha256': hashlib.sha256(adts).hexdigest(), 'sampleRate': audio['sample_rate'], 'duration': float(info['format']['duration'])}; receipt.write_text(json.dumps(result, indent=2) + '\n'); results.append(result)
assert results[0]['aacSha256'] == results[1]['aacSha256']
for name, src in [('stem', O / 'narration-stem.wav'), ('encoded', O / 'steam-next-fest-captioned.mp4')]:
    dest = Q / (name + '-mono.wav'); receipt = Q / (name + '-mono-source.json'); signature = {'sourceSha256': sha(src), 'sampleRate': 24000, 'channels': 1}
    if not (dest.exists() and receipt.exists() and json.loads(receipt.read_text()) == signature):
        run(['ffmpeg', '-v', 'error', '-y', '-i', str(src), '-vn', '-ac', '1', '-ar', '24000', '-c:a', 'pcm_f32le', str(dest)]); receipt.write_text(json.dumps(signature, indent=2) + '\n')
stem, sr = sf.read(Q / 'stem-mono.wav', dtype='float32'); encoded, _ = sf.read(Q / 'encoded-mono.wav', dtype='float32'); windows = []; summaries = []
db = lambda x: float(20 * np.log10(max(float(x), 1e-10)))
for scene in plan['scenes']:
    sid = scene['id']; raw, _ = sf.read(N / 'chunks' / f'{sid}-scene.wav', dtype='float32'); words = json.loads((N / 'asr' / f'{sid}.json').read_text(encoding='utf8'))['words']; mask = np.zeros(len(raw), dtype=bool)
    for w in words:
        a, b = w['timestamp']
        if a is not None and b is not None: mask[max(0, round(a * sr)):min(len(raw), round(b * sr))] = True
    origin = round((scene['paragraphs'][0]['start'] + LEAD) * sr); local = []
    for a in range(0, len(raw) - round(sr * .4), round(sr * .1)):
        b = a + round(sr * .4); m = mask[a:b]
        if m.mean() < .3: continue
        x = raw[a:b][m]; y = stem[origin + a:origin + b][m]; z = encoded[origin + a:origin + b][m]
        xr = float(np.sqrt(np.mean(x * x))); yr = float(np.sqrt(np.mean(y * y))); zr = float(np.sqrt(np.mean(z * z)))
        if db(yr) < -46: continue
        projection = float(np.sum(y * z) / max(np.sum(y * y), 1e-10)); row = {'scene': sid, 'time': origin / sr + a / sr, 'sourceDbfs': db(xr), 'stemDbfs': db(yr), 'finalMixDbfs': db(zr), 'stemMinusSourceDb': db(yr / xr), 'estimatedVoiceTransferDb': db(projection)}; windows.append(row); local.append(row)
    summaries.append({'scene': sid, 'speechWindows': len(local), 'sourceMedianDbfs': float(np.median([r['sourceDbfs'] for r in local])), 'stemMedianDbfs': float(np.median([r['stemDbfs'] for r in local])), 'minimumEstimatedVoiceTransferDb': min(r['estimatedVoiceTransferDb'] for r in local)})
flags = [r for r in windows if r['estimatedVoiceTransferDb'] < -2.5]; low = []
for r in windows:
    neighbors = [q['stemDbfs'] for q in windows if q['scene'] == r['scene'] and .5 < abs(q['time'] - r['time']) <= 3]
    if neighbors and r['stemDbfs'] < float(np.median(neighbors)) - 6: low.append({**r, 'neighborMedianDbfs': float(np.median(neighbors))})
groups = []
for r in low:
    if groups and r['scene'] == groups[-1][-1]['scene'] and r['time'] - groups[-1][-1]['time'] < .151: groups[-1].append(r)
    else: groups.append([r])
sustained = [{'scene': g[0]['scene'], 'start': g[0]['time'], 'end': g[-1]['time'] + .4, 'samples': len(g), 'maximumDifferenceDb': max(r['neighborMedianDbfs'] - r['stemDbfs'] for r in g), 'status': 'needs contextual review, may include natural sentence endings'} for g in groups if len(g) >= 5]
joins = [{'before': a['scene'], 'after': b['scene'], 'speechMedianDifferenceDb': b['stemMedianDbfs'] - a['stemMedianDbfs']} for a, b in zip(summaries, summaries[1:])]
(Q / 'audio-continuity.json').write_text(json.dumps({'windowSeconds': .4, 'hopSeconds': .1, 'scenes': summaries, 'windows': windows, 'flaggedVoiceTransferWindows': flags, 'sustainedLocalDropCandidates': sustained, 'sceneJoins': joins, 'humanListening': 'pending complete user review'}, indent=2) + '\n')
measurement = subprocess.run(['ffmpeg', '-hide_banner', '-i', str(O / 'steam-next-fest-captioned.mp4'), '-vn', '-af', 'loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json', '-f', 'null', '-'], cwd=R, capture_output=True, check=True).stderr.decode(errors='replace')
stats = json.loads(measurement[measurement.rfind('{'):measurement.rfind('}') + 1]); (Q / 'encoded-loudness.json').write_text(json.dumps(stats, indent=2) + '\n'); assert float(stats['input_tp']) <= -1.5, stats
samples = {12: ['branding early'], 108: ['branding exit'], plan['totalFrames'] - 580: ['membership enter'], plan['totalFrames'] - 300: ['membership names'], plan['totalFrames'] - 18: ['membership exit']}
for c in layout['rows']: samples.setdefault(round((c['start'] + c['end']) / 2 * 60), []).append(f"cue {c['id']}")
for c in plan['cuts']:
    for f, label in [(c['startFrame'] + min(15, c['frames'] // 3), 'in'), (c['endFrame'] - min(15, c['frames'] // 3), 'out')]: samples.setdefault(f, []).append(c['id'] + ' ' + label)
rows = [{'frame': f, 'time': f / 60, 'labels': labels} for f, labels in sorted(samples.items())]; (Q / 'pixel-sample-index.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
def balanced(terms):
    if len(terms) == 1: return terms[0]
    mid = len(terms) // 2; return '(' + balanced(terms[:mid]) + '+' + balanced(terms[mid:]) + ')'
vf = "select='" + balanced(['eq(n,' + str(r['frame']) + ')' for r in rows]) + "',scale=480:270:flags=lanczos"
run(['ffmpeg', '-v', 'error', '-i', str(O / 'steam-next-fest-captioned.mp4'), '-an', '-vf', vf, '-fps_mode', 'vfr', '-c:v', 'mjpeg', '-threads', '1', '-q:v', '3', '-y', str(Q / 'frame-%04d.jpg')])
for page in range(math.ceil(len(rows) / 12)):
    chunk = rows[page * 12:(page + 1) * 12]; sheet = Image.new('RGB', (1440, 310 * math.ceil(len(chunk) / 3)), (22, 22, 22)); draw = ImageDraw.Draw(sheet)
    for k, row in enumerate(chunk):
        image = Image.open(Q / f'frame-{page * 12 + k + 1:04}.jpg'); x = k % 3 * 480; y = k // 3 * 310; sheet.paste(image, (x, y)); draw.text((x + 5, y + 274), f"{row['time']:.2f}s | " + ' / '.join(row['labels'])[:65], fill='white')
    sheet.save(Q / f'contact-{page:02}.jpg')
report = {'outputs': results, 'bodyFrames': plan['bodyFrames'], 'ratioPolicy': 'reality-check-no-ratio-v1 (no quota)', 'ownRecordingFrames': sum(c['frames'] for c in plan['cuts']), 'noSourceLoopsOrSpeedChanges': True, 'heldLastFrameFrames': sum(c['holdFrames'] for c in plan['cuts']), 'captionPairs': len(layout['rows']), 'pixelSamples': len(rows), 'contactSheets': math.ceil(len(rows) / 12), 'actualPixelsReview': 'pending direct review', 'fullAsrReview': 'pending', 'humanWholeListening': 'pending', 'platformMutation': False}
(Q / 'integrity.json').write_text(json.dumps(report, indent=2) + '\n'); print(json.dumps({k: v for k, v in report.items() if k != 'outputs'}))
