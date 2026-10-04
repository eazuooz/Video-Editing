"""Local-only native-frame action samples and candidate cut-edge triplets.

This creates inspection material from already acquired official sources, not a
game, narration or final render. Scene-score candidates need direct review;
they do not themselves establish a valid clip or exact action boundary.
"""
import hashlib, json, os, re, subprocess, sys, time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
BATCH = ROOT / 'production/batches/sakurai-planning-game-design'
REQUEST = json.loads((HERE / sys.argv[1]).read_text(encoding='utf-8')) if len(sys.argv) > 1 else None
STATE = HERE / (REQUEST['stateFile'] if REQUEST else 'native-review-v1.json')
OUT = HERE.parent / 'research-local' / (REQUEST['localRasterFolder'] if REQUEST else 'native-review-v1')
FFMPEG = 'C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
stamp = lambda: time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
relative = lambda p: str(p.relative_to(ROOT)).replace('\\', '/')

WINDOWS = {
    'z4utn4Sm6SY': [(5, 30), (38, 54)],
    '4c-3gbC5mc4': [(5, 11), (18, 20), (23, 35), (46, 55)],
    'WFIvd2HrMNY': [(12, 20), (30, 56), (58, 62)],
    'JdNZo7E_hXU': [(3, 14), (17, 20), (22, 28), (53, 62), (73, 77), (80, 82), (91, 104)],
}
if REQUEST:
    WINDOWS = REQUEST['candidateWindowsSeconds']
if STATE.exists():
    raise RuntimeError('Native inspection state exists. Reuse it; do not rerun a completed extraction.')
acq = json.loads((HERE / (REQUEST['acquisitionFile'] if REQUEST else 'acquisition.json')).read_text(encoding='utf-8'))
if acq['status'] != 'acquired-decoded-awaiting-direct-action-review':
    raise RuntimeError('Original acquisition is incomplete')
OUT.mkdir(parents=True, exist_ok=True)
font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 22)
state = {'schemaVersion': 1, 'pid': os.getpid(), 'startedAt': stamp(), 'status': 'initializing',
         'method': 'Source-native frame numbers at half-second spacing in discovery candidates, plus native frames before/at/after scene-score and proposed window edges. No interpolation or source slowdown.',
         'sceneCandidateThreshold': 0.22, 'sources': [], 'approvedIntervals': [], 'approvedActualSeconds': 0,
         'actualCutApproval': False, 'sourceAudioUsed': False, 'gpuJobs': 0, 'renderJobs': 0, 'uploads': 0,
         'localOnlyRaster': True}

def digest(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def write(p, v):
    tmp = Path(str(p) + '.' + str(os.getpid()) + '.tmp')
    tmp.write_text(json.dumps(v, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    tmp.replace(p)

def save():
    launch_file = Path(str(STATE) + '.session.json')
    if launch_file.exists():
        launch = json.loads(launch_file.read_text(encoding='utf-8'))
        if launch.get('pid') == os.getpid(): state['sessionId'] = launch.get('sessionId')
    state['updatedAt'] = stamp()
    write(STATE, state)
    q = json.loads((BATCH / 'queue.json').read_text(encoding='utf-8'))
    item = next(i for i in q['items'] if i['slug'] == 'avoid-game-comparisons')
    if REQUEST and REQUEST.get('executionRole') == 'additional-official-source-after-measurement':
        running = state['status'] in ['initializing', 'extracting']
        item['sourceExpansionNativeReview'] = {'pid': os.getpid(), 'sessionId': state.get('sessionId'), 'status': state['status'], 'state': relative(STATE), 'sources': state['sources'], 'cpuJobs': 1 if running else 0, 'actualCutApproval': False, 'updatedAt': stamp()}
        item['execution'].update(secondaryTasks=[{'kind': 'source-discovery', 'phase': 'native-action-boundaries', 'pid': os.getpid(), 'sessionId': state.get('sessionId')}] if running else [], cpuProductionJobs=item['execution'].get('primaryCpuProductionJobs', 0) + (1 if running else 0))
        item['updatedAt'] = stamp(); q['updatedAt'] = stamp(); write(BATCH / 'queue.json', q)
        return
    item['stage'] = 'native-action-and-boundary-review'
    item['execution'].update({'phase': 'CPU-native-source-inspection', 'pid': os.getpid(), 'status': state['status'],
                            'state': relative(STATE), 'updatedAt': stamp(), 'activeTasks': [s for s in state['sources'] if s.get('status') == 'extracting'],
                            'gpuSynthesisJobs': 0, 'renderJobs': 0, 'uploads': 0, 'newNarrationCreated': False, 'newSceneCreated': False})
    item['nextAction'] = 'Directly review native action samples, before/at/after cut edges and cross-source duplicate shots. Do not approve runtime from extracted files alone.'
    q['updatedAt'] = stamp()
    write(BATCH / 'queue.json', q)

def run(rec, args, logfile):
    with logfile.open('ab') as f:
        child = subprocess.Popen([FFMPEG, '-hide_banner', '-threads', '2', '-filter_threads', '1'] + args,
                                 stdout=f, stderr=f, creationflags=subprocess.CREATE_NO_WINDOW)
        rec['childPid'] = child.pid
        rec['log'] = relative(logfile)
        save()
        code = child.wait()
    if code:
        raise RuntimeError(f'{rec["videoId"]} extraction exited {code}')
    rec['childPid'] = None

def sheets(frames, labels, folder, prefix, cols=4, rows=4):
    records = []
    for offset in range(0, len(frames), cols * rows):
        sheet = Image.new('RGB', (cols * 640, rows * 388), (238, 238, 238))
        draw = ImageDraw.Draw(sheet)
        for j, frame in enumerate(frames[offset:offset + cols * rows]):
            with Image.open(frame) as src:
                im = src.resize((640, 360))
            x, y = (j % cols) * 640, (j // cols) * 388
            sheet.paste(im, (x, y + 28))
            draw.text((x + 6, y + 2), labels[offset + j], font=font, fill=(0, 0, 0))
        target = folder / f'{prefix}-{offset // (cols * rows) + 1:02d}.jpg'
        sheet.save(target, quality=93)
        records.append({'path': relative(target), 'sha256': digest(target), 'tiles': len(frames[offset:offset + cols * rows])})
    return records

try:
    for vid, windows in WINDOWS.items():
        source = next(s for s in acq['results'] if s['videoId'] == vid)
        media = ROOT / source['localMediaPath']
        if digest(media) != source['fileSha256']:
            raise RuntimeError(f'Source hash changed: {vid}')
        vs = next(s for s in source['streams'] if s['codec_type'] == 'video')
        a, b = map(int, vs['r_frame_rate'].split('/'))
        fps = a / b
        if (a, b) not in ((30, 1), (60, 1), (60000, 1001)):
            raise RuntimeError('Inspection requires a verified known source-native frame rate')
        total = int(vs['nb_frames'])
        folder = OUT / vid
        folder.mkdir(exist_ok=True)
        rec = {'videoId': vid, 'source': source['localMediaPath'], 'sourceSha256': source['fileSha256'],
               'nativeFps': fps, 'nativeFrameRate': vs['r_frame_rate'], 'nativeFrameCount': total, 'candidateWindowsSeconds': windows, 'status': 'extracting'}
        state['sources'].append(rec)
        state['status'] = 'extracting'
        save()
        # Scene detector reports actual source PTS; the accepted cut remains a visual decision.
        scene_log = folder / 'scene-candidates.log'
        run(rec, ['-i', str(media), '-an', '-vf', "select=gt(scene\\,0.22),showinfo", '-vsync', '0', '-f', 'null', '-'], scene_log)
        pts = [float(v) for v in re.findall(r'Parsed_showinfo[^\n]*?\bn:\s*\d+[^\n]*?pts_time:([\d.]+)', scene_log.read_text(encoding='utf-8', errors='replace'))]
        boundaries = sorted({round(t * fps) for t in pts if any(start - 1 <= t <= end + 1 for start, end in windows)})
        boundaries = sorted(set(boundaries) | {round(t * fps) for w in windows for t in w})
        if REQUEST and REQUEST.get('manualBoundaryFrames'):
            boundaries = sorted(set(boundaries) | set(REQUEST['manualBoundaryFrames'].get(vid, [])))
        rec['candidateBoundaryFrames'] = boundaries
        nums = sorted({n for start, end in windows for n in range(round(start * fps), round(end * fps), round(fps / 2))})
        expression = '+'.join(f'eq(n\\,{n})' for n in nums)
        sample_log = folder / 'action-samples.log'
        run(rec, ['-i', str(media), '-an', '-vf', f'select={expression},showinfo,scale=960:540', '-vsync', '0', '-q:v', '3', str(folder / 'action-%04d.jpg')], sample_log)
        frames = sorted(folder.glob('action-*.jpg'))
        actual_pts = [float(v) for v in re.findall(r'Parsed_showinfo[^\n]*?\bn:\s*\d+[^\n]*?pts_time:([\d.]+)', sample_log.read_text(encoding='utf-8', errors='replace'))]
        # showinfo prints PTS to six significant digits. Above100 seconds,
        # allow its text rounding while retaining exact selected native frames.
        rec['showinfoPtsTextToleranceSeconds'] = 0.00051
        if len(frames) != len(nums) or len(actual_pts) != len(nums) or any(abs(t - n / fps) > 0.00051 for t, n in zip(actual_pts, nums)):
            raise RuntimeError('Native action frame/PTS count mismatch')
        rec['actionSamples'] = [{'frame': n, 'pts': t, 'path': relative(p), 'sha256': digest(p)} for p, n, t in zip(frames, nums, actual_pts)]
        rec['actionSheets'] = sheets(frames, [f'{vid} n{n} {t:.3f}s' for n, t in zip(nums, actual_pts)], folder, 'action-sheet')
        edge_nums = sorted({n for cut in boundaries for n in (cut - 1, cut, cut + 1) if 0 <= n < total})
        edge_expression = '+'.join(f'eq(n\\,{n})' for n in edge_nums)
        edge_log = folder / 'boundary-samples.log'
        run(rec, ['-i', str(media), '-an', '-vf', f'select={edge_expression},showinfo,scale=960:540', '-vsync', '0', '-q:v', '3', str(folder / 'edge-%04d.jpg')], edge_log)
        edge_files = sorted(folder.glob('edge-*.jpg'))
        edge_pts = [float(v) for v in re.findall(r'Parsed_showinfo[^\n]*?\bn:\s*\d+[^\n]*?pts_time:([\d.]+)', edge_log.read_text(encoding='utf-8', errors='replace'))]
        if len(edge_files) != len(edge_nums) or len(edge_pts) != len(edge_nums):
            raise RuntimeError('Native boundary frame/PTS count mismatch')
        rec['boundarySamples'] = [{'frame': n, 'pts': t, 'path': relative(p), 'sha256': digest(p)} for p, n, t in zip(edge_files, edge_nums, edge_pts)]
        mapping = dict(zip(edge_nums, edge_files))
        triplets = []
        labels = []
        for cut in boundaries:
            for n in (cut - 1, cut, cut + 1):
                if n in mapping:
                    triplets.append(mapping[n])
                    labels.append(f'edge n{cut}: n{n} {n / fps:.3f}s')
        rec['boundarySheets'] = sheets(triplets, labels, folder, 'boundary-sheet', cols=3, rows=5)
        rec['status'] = 'extracted-awaiting-direct-review'
        rec['endedAt'] = stamp()
        save()
    state['status'] = 'native-samples-extracted-awaiting-direct-review'
    state['endedAt'] = stamp()
    save()
    print(json.dumps({'status': state['status'], 'pid': state['pid'], 'actionFrames': sum(len(s['actionSamples']) for s in state['sources']),
                      'boundaries': sum(len(s['candidateBoundaryFrames']) for s in state['sources']), 'sheets': sum(len(s['actionSheets']) + len(s['boundarySheets']) for s in state['sources'])}))
except Exception as exc:
    state['status'] = 'failed'
    state['error'] = repr(exc)
    save()
    raise
