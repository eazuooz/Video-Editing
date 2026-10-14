"""Preserve completed v137 video; restore complete PCM-derived AAC for source review."""
from pathlib import Path
from datetime import datetime, timezone
from PIL import ImageFont
import hashlib, json, math, psutil, shutil, subprocess, wave

ROOT = Path(__file__).resolve().parents[3]
P = ROOT / 'projects/game-lighting-history-04/production'
BASE = ROOT / 'production/research/game-lighting-history/local/guided-focus-label-v140'
OUT = ROOT / 'production/research/game-lighting-history/local/episode04-guided-source-review-v142'
SP = P / 'guided-source-review-execution-v142.json'
FF = Path('C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe')
FP = FF.with_name('ffprobe.exe')
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
rel = lambda p: p.relative_to(ROOT).as_posix()
stamp = lambda: datetime.now(timezone.utc).isoformat()
plan = read(BASE / 'plan.json')
assembly = read(BASE / 'audio-assembly.json')
job = plan['jobs'][0]
source = ROOT / job['output']
audio = ROOT / assembly['path']
N = job['frames']
assert N == 1100 and assembly['samples'] == N * 400
assert read(ROOT / job['execution'])['exitCode'] == 0
assert assembly['allSelectedPcm16ByteIdentical'] and sha(audio) == assembly['sha256']
review = read(ROOT / plan['review']['path'])
assert sha(ROOT / plan['review']['path']) == plan['review']['sha256']
assert read(ROOT / plan['followupReview']['path'])['wholeAndIndependentPhraseCoverageAccepted']
for key in ['selected', 'followupSelected', 'model', 'focusModel', 'runtime']:
    assert sha(ROOT / plan[key]['path']) == plan[key]['sha256']
for scene in plan['scenes']:
    assert sha(ROOT / scene['source']['path']) == scene['source']['sha256']
    assert sha(ROOT / scene['wrapper']['path']) == scene['wrapper']['sha256']
assert not OUT.exists() and not SP.exists(), 'Preserve prior attempts'
assert shutil.disk_usage(ROOT).free > 3 * 1024**3
processes = []
for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
    try:
        d = proc.info
        cmd = ' '.join(d['cmdline'] or [])
        if 'python' in (d['name'] or '').lower() or 'ffmpeg' in (d['name'] or '').lower():
            processes.append(d)
        if 'ffmpeg' in (d['name'] or '').lower() and 'game-lighting-history' in cmd:
            raise RuntimeError('Owned media worker already active')
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass
gpu = subprocess.run(['nvidia-smi', '--query-gpu=memory.used,memory.total,utilization.gpu', '--format=csv,noheader'], capture_output=True, text=True, check=True).stdout.strip()
OUT.mkdir()
me = psutil.Process()
state = {'startedAt': stamp(), 'status': 'running', 'worker': {'pid': me.pid, 'createTime': me.create_time(), 'commandLine': me.cmdline(), 'cwd': str(ROOT)}, 'resources': {'processes': processes, 'gpu': gpu}, 'plan': {'path': rel(BASE / 'plan.json'), 'sha256': sha(BASE / 'plan.json')}, 'sourceVideo': {'path': rel(source), 'sha256': sha(source)}, 'assembly': {'path': rel(BASE / 'audio-assembly.json'), 'sha256': sha(BASE / 'audio-assembly.json')}, 'cpuThreads': 2, 'gpuJobs': 0, 'active': None, 'commands': [], 'allMovingPixelsReviewed': False, 'allFinalPixelsReviewed': False, 'finalMixedAsrApproved': False, 'qaApproved': False, 'collected': False, 'uploaded': False, 'newGitImages': 0}
def save():
    SP.write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n', 'utf-8')
def checkpoint():
    path = ROOT / 'production/research/game-lighting-history/checkpoint.json'
    j = read(path)
    j['episode04GuidedSourceReviewV142'] = {'execution': rel(SP), 'status': state['status'], 'worker': state['worker'], 'active': state['active'], 'sourceModelsRerendered': 0, 'allFinalPixelsReviewed': False}
    j['ownedActiveWork'] = {'type': 'CPU-guided-source-review-v142', 'execution': rel(SP), 'worker': state['worker'], 'active': state['active'], 'status': state['status'], 'cpuThreads': 2, 'gpuJobs': 0, 'next': 'Directly review all6 encoded cues, stage/cut pixels and moving scenes; then expand concept-matched game comparisons and physical episode timing'}
    j['updatedAt'] = stamp()
    tmp = path.with_suffix('.guided-source-review-v142.tmp')
    tmp.write_text(json.dumps(j, ensure_ascii=False, indent=2) + '\n', 'utf-8')
    tmp.replace(path)
def run(cmd, label):
    cmd = [str(x) for x in cmd]
    log = OUT / (label + '.log')
    with log.open('w', encoding='utf-8') as f:
        proc = subprocess.Popen(cmd, cwd=ROOT, stdout=f, stderr=f)
        obs = psutil.Process(proc.pid)
        state['active'] = {'pid': proc.pid, 'createTime': obs.create_time(), 'commandLine': cmd, 'cwd': str(ROOT), 'log': rel(log), 'startedAt': stamp()}
        save(); checkpoint()
        code = proc.wait()
    result = {**state['active'], 'exitCode': code, 'endedAt': stamp()}
    state['commands'].append(result); state['active'] = None; save()
    assert code == 0, (label, code)
    return result
def probe(file):
    j = json.loads(subprocess.run([str(FP), '-v', 'error', '-threads', '2', '-count_frames', '-show_entries', 'stream=codec_type,codec_name,width,height,r_frame_rate,time_base,nb_read_frames,duration,duration_ts,start_pts,sample_rate,channels:format=duration', '-of', 'json', str(file)], capture_output=True, text=True, check=True).stdout)
    v = next(s for s in j['streams'] if s['codec_type'] == 'video')
    a = next(s for s in j['streams'] if s['codec_type'] == 'audio')
    assert (v['width'], v['height'], v['r_frame_rate'], v['time_base'], int(v['nb_read_frames'])) == (1920, 1080, '60/1', '1/90000', N)
    assert abs(float(v['duration']) - N / 60) < 1 / 90000
    packets = json.loads(subprocess.run([str(FP), '-v', 'error', '-select_streams', 'v:0', '-show_packets', '-show_entries', 'packet=pts,duration', '-of', 'json', str(file)], capture_output=True, text=True, check=True).stdout)['packets']
    assert sorted(p['pts'] for p in packets) == list(range(0, N * 1500, 1500))
    assert all(p['duration'] == 1500 for p in packets if 'duration' in p)
    assert a['codec_name'] == 'aac' and int(a['sample_rate']) == 48000 and a['channels'] == 2
    assert abs(float(a['duration']) - N / 60) < 1 / 48000
    assert int(a['duration_ts']) == N * 800 and int(a.get('start_pts', 0)) == 0
    ap = json.loads(subprocess.run([str(FP), '-v', 'error', '-select_streams', 'a:0', '-show_packets', '-show_data_hash', 'sha256', '-show_entries', 'packet=pts,duration,data_hash', '-of', 'json', str(file)], capture_output=True, text=True, check=True).stdout)['packets']
    assert ap[-1]['pts'] + ap[-1]['duration'] == N * 800
    return {'path': rel(file), 'sha256': sha(file), 'probe': j, 'frames': N, 'allPresentationPtsContinuous': True, 'aacPacketCount': len(ap), 'aacPacketsPtsDurationPayloadSha256': hashlib.sha256(json.dumps(ap, sort_keys=True, separators=(',', ':')).encode()).hexdigest(), 'completeAudioDurationVerified': True}
def ts(frame):
    cs = round(frame / 60 * 100)
    return f'{cs // 360000}:{cs // 6000 % 60:02d}:{cs // 100 % 60:02d}.{cs % 100:02d}'
try:
    save(); checkpoint()
    with wave.open(str(audio), 'rb') as w:
        assert (w.getframerate(), w.getnchannels(), w.getsampwidth(), w.getnframes()) == (24000, 1, 2, N * 400)
        pcm = w.readframes(w.getnframes())
    for r in assembly['ranges']:
        with wave.open(str(ROOT / r['source']['path']), 'rb') as w:
            original = w.readframes(w.getnframes())
        assert original == pcm[r['startSample'] * 2:r['endSample'] * 2]
        pad = pcm[r['endSample'] * 2:(r['endSample'] + r['silentPaddingSamples']) * 2]
        assert not any(pad)
    font_path = Path('C:/Windows/Fonts/malgun.ttf')
    font = ImageFont.truetype(str(font_path), 48)
    header = (ROOT / 'production/research/game-lighting-history/local/episode04-first-chapter-review-v10/captions.ko.ass').read_text('utf-8').split('Dialogue:')[0]
    events, cues = [], []
    for scene in plan['scenes']:
        for i, c in enumerate(scene['cues']):
            first, end = scene['fromFrame'] + c['fromFrame'], scene['fromFrame'] + c['toFrame']
            lines = c['text'].split('\n')
            assert len(lines) <= 2 and not any(ch in c['text'] for ch in '{}\\')
            width, height = math.ceil(max(font.getlength(x) for x in lines) + 44), len(lines) * 62 + 22
            assert width <= 1570
            x, y = math.floor(960 - width / 2), 970 - height / 2
            rect = f'm 0 0 l {width} 0 {width} {height} 0 {height}'
            start, finish = ts(first), ts(end)
            for layer, text in [(0, f'{{\\an7\\pos({x+14},{y+14:g})\\p1\\bord0\\shad0\\1c&H323C07&}}' + rect), (1, f'{{\\an7\\pos({x},{y:g})\\p1\\bord3\\shad0\\1c&HFFFFFF&\\3c&H181B16&}}' + rect)]:
                events.append(f'Dialogue: {layer},{start},{finish},Default,,0,0,0,,{text}')
            for k, line in enumerate(lines):
                events.append(f'Dialogue: 2,{start},{finish},Default,,0,0,0,,{{\\an5\\pos(960,{970-(len(lines)-1)*31+k*62})\\bord0\\shad0}}' + line)
            af, ef = math.ceil(round(first / 60 * 100) / 100 * 60 - 1e-7), math.ceil(round(end / 60 * 100) / 100 * 60 - 1e-7)
            assert abs(af-first) <= 1 and abs(ef-end) <= 1
            cues.append({'id': f'{scene["id"]}-cue-{i+1}', 'scene': scene['id'], 'text': c['text'], 'firstFrame': af, 'exclusiveEndFrame': ef, 'plannedFirstFrame': first, 'plannedExclusiveEndFrame': end, 'box': {'x': x, 'y': y, 'width': width, 'height': height, 'center': [960, 970]}, 'encodedPixelsReviewed': False})
    assert len(cues) == 6
    ass = OUT / 'captions.ko.ass'; ass.write_text(header + '\n'.join(events) + '\n', 'utf-8')
    (OUT / 'caption-layout.json').write_text(json.dumps({'font': str(font_path), 'fontSha256': sha(font_path), 'fontSize': 48, 'captionStyle': 'boxed-white-forest-v1', 'center': [960, 970], 'cues': cues, 'assSha256': sha(ass), 'allFinalPixelsReviewed': False}, ensure_ascii=False, indent=2) + '\n', 'utf-8')
    old = json.loads(subprocess.run([str(FP), '-v', 'error', '-show_entries', 'stream=codec_type,duration', '-of', 'json', str(source)], capture_output=True, text=True, check=True).stdout)
    old_audio = next(s for s in old['streams'] if s['codec_type'] == 'audio')
    state['sourceAacShortfall'] = {'audioDuration': float(old_audio['duration']), 'pcmDuration': N / 60, 'shortBySeconds': N / 60 - float(old_audio['duration']), 'oldExportPreserved': True, 'replacementScope': 'Audio only; v137 video copied'}
    clean = OUT / 'guided-source.clean.mp4'; cap = OUT / 'guided-source.captioned.mp4'
    run([FF, '-n', '-hide_banner', '-threads', '2', '-i', source, '-i', audio, '-map', '0:v:0', '-map', '1:a:0', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-ac', '2', '-video_track_timescale', '90000', '-movie_timescale', '48000', '-movflags', '+faststart', clean], 'complete-audio-clean')
    video = OUT / 'captioned-video-only.mp4'
    run([FF, '-n', '-hide_banner', '-threads', '2', '-reinit_filter', '0', '-i', clean, '-filter_threads', '2', '-vf', 'ass=' + rel(ass), '-frames:v', str(N), '-an', '-fps_mode', 'passthrough', '-enc_time_base', '1:90000', '-c:v', 'libx264', '-threads', '2', '-preset', 'fast', '-crf', '20', '-pix_fmt', 'yuv420p', '-video_track_timescale', '90000', '-movflags', '+faststart', video], 'burn-captions')
    run([FF, '-n', '-hide_banner', '-i', video, '-i', clean, '-map', '0:v:0', '-map', '1:a:0', '-c', 'copy', '-video_track_timescale', '90000', '-movie_timescale', '48000', '-movflags', '+faststart', cap], 'captioned-complete-aac')
    outputs = []
    for file in [clean, cap]:
        proof = probe(file)
        proof['wholeDecode'] = run([FF, '-v', 'error', '-threads', '2', '-i', file, '-f', 'null', 'NUL'], file.stem + '-whole-decode')
        outputs.append(proof)
    assert outputs[0]['aacPacketsPtsDurationPayloadSha256'] == outputs[1]['aacPacketsPtsDurationPayloadSha256']
    record = {'builtAt': stamp(), 'scope': 'One repaired black projected guided explanation source scenes only; voice-only review, not final delivery', 'plan': state['plan'], 'sourceVideo': state['sourceVideo'], 'assembly': state['assembly'], 'execution': rel(SP), 'captionLayout': {'path': rel(OUT / 'caption-layout.json'), 'sha256': sha(OUT / 'caption-layout.json')}, 'outputs': outputs, 'sourceAacShortfall': state['sourceAacShortfall'], 'allSelectedPcm16ByteIdentical': True, 'identicalAacPayloadAndPtsAndDuration': True, 'frames': N, 'captionCues': len(cues), 'captionCenter': [960, 970], 'sourceModelsRerendered': 0, 'newTts': 0, 'newGitImages': 0, 'allFinalPixelsReviewed': False, 'allMovingPixelsReviewed': False, 'captionTimingApproved': False, 'finalMixedAsrApproved': False, 'wholeEpisode60to40Approved': False, 'qaApproved': False, 'collected': False, 'uploaded': False, 'humanWholeListening': 'pending'}
    (P / 'guided-source-review-build-v142.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', 'utf-8')
    state['status'] = 'technical-source-review-pair-ready'; state['endedAt'] = stamp(); save(); checkpoint()
    print(json.dumps({'status': state['status'], 'frames': N, 'sameAac': True, 'completeAudio': True, 'finalApproved': False}), flush=True)
except Exception as e:
    state['status'] = 'failed'; state['error'] = repr(e); state['endedAt'] = stamp(); save(); checkpoint(); raise
