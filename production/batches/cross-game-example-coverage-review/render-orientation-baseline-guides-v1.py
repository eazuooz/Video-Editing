"""One serial CPU render of eight exact-native cuts with bounded image guides."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, math, os, re, subprocess, traceback
for k in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[k] = '2'
import psutil
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
B = Path(__file__).resolve().parent
O = ROOT / 'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
LOCAL = ROOT / 'shared/output/unpublished-teaching-clarity-revision/orientation/current34-baseline-guides-v1'
FF = 'C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
FP = 'C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
rel = lambda p: p.relative_to(ROOT).as_posix()
now = lambda: datetime.now(timezone.utc).isoformat()

def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda: f.read(8 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def save(p, data):
    tmp = p.with_name(p.name + f'.{os.getpid()}.writing')
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', 'utf-8')
    os.replace(tmp, p)

FONTS = {n: ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf', n) for n in (22, 26, 28)}
TEAL, RED, GOLD = '#43ddce', '#f54e4e', '#ffe16b'

def label(d, xy, text, color='#ffffff', size=26):
    font = FONTS[size]
    bb = d.textbbox(xy, text, font=font)
    assert bb[0] >= 0 and bb[2] + 10 < 1920 and bb[3] + 12 < 900
    d.rounded_rectangle((bb[0]-9, bb[1]-5, bb[2]+9, bb[3]+9), radius=5, fill=(14, 19, 23, 226))
    d.text(xy, text, font=font, fill=color)

def within(frame, interval):
    return len(interval) == 2 and interval[0] <= frame < interval[1]

def point_at(scene_frame, row):
    p = row['pointWindow']
    f = scene_frame - p['sceneFrameIn']
    if not 0 <= f < p['sceneFrameOut'] - p['sceneFrameIn']:
        return None
    if not within(scene_frame, row['pointVisibleSceneFrameRange']):
        return None
    if any(a <= f < b for a, b in p['hiddenLocalFrameRanges']):
        return None
    keys = p['keyframes']
    for a, b in zip(keys, keys[1:]):
        if a['frame'] <= f <= b['frame']:
            # An occlusion anywhere in the interpolation bracket also hides it.
            if any(a['frame'] < end and b['frame'] >= start for start, end in p['hiddenLocalFrameRanges']):
                return None
            u = (f-a['frame']) / (b['frame']-a['frame'])
            return [a[k] + u*(b[k]-a[k]) for k in ('x', 'y')]
    # The 02 historical anchor set contains the native endpoint at frame360;
    # other rows end at359. The exclusive render boundary never consumes360.
    return None

def arrow(d, a, b, color):
    dx, dy = b[0]-a[0], b[1]-a[1]
    n = math.hypot(dx, dy)
    if n < 6:
        return False
    u, v = dx/n, dy/n
    d.line((tuple(a), tuple(b)), fill='#10191c', width=9)
    d.line((tuple(a), tuple(b)), fill=color, width=5)
    d.polygon([tuple(b), (b[0]-15*u+7*v, b[1]-15*v-7*u),
               (b[0]-15*u-7*v, b[1]-15*v+7*u)], fill=color)
    return True

def draw_frame(raw, frame, row):
    im = Image.frombytes('RGB', (1920, 1080), raw)
    point = point_at(frame, row)
    gold = within(frame, row['goldImageUpSceneFrameRange'])
    red = False
    layer = Image.new('RGBA', im.size)
    d = ImageDraw.Draw(layer)
    # No persistent card obscures the native game view outside the relevant cue.
    if point is not None or gold:
        label(d, (64, 28), 'Superflight · 화면 관찰', size=22)
        label(d, (64, 88), row['guideNote'], GOLD, 28)
    if point is not None:
        x, y = point
        d.ellipse((x-15, y-15, x+15, y+15), outline='#10191c', width=6)
        d.ellipse((x-12, y-12, x+12, y+12), outline=TEAL, width=4)
        d.ellipse((x-3, y-3, x+3, y+3), fill=TEAL)
        label(d, (64, 145), '청록 p: 몸통 위치의 화면 관찰점', TEAL, 26)
        if within(frame, row['redScreenDisplacementSceneFrameRange']):
            previous = point_at(frame-30, row)
            if previous is not None and all(point_at(f, row) is not None for f in range(frame-30, frame+1)):
                red = arrow(d, previous, point, RED)
                if red:
                    label(d, (64, 201), '빨강 Δp: 0.5초 동안의 화면 위치 변화', RED, 26)
    if gold:
        arrow(d, (1580, 305), (1580, 195), GOLD)
        label(d, (1400, 330), '화면의 위', GOLD, 26)
        label(d, (64, 257), '노랑: 화면 기준 · 물체/월드 축 아님', GOLD, 26)
    box = layer.getbbox()
    assert box is None or box[3] < 900
    out = Image.alpha_composite(im.convert('RGBA'), layer).convert('RGB')
    return out.tobytes(), dict(point=point, redScreenChange=red, goldImageUp=gold,
        hidden=point is None, worldAxes=False, armAxis=False, internalErrorMeasured=False)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--resource', required=True)
    args = ap.parse_args()
    sp = O / 'current34-baseline-guides-render-execution-v1.json'
    pp = O / 'current34-baseline-guide-plan-v2.json'
    assert not sp.exists() and not LOCAL.exists(), 'Preserve completed/running outputs.'
    plan = read(pp)
    resource = read(ROOT / args.resource)
    assert (datetime.now(timezone.utc)-datetime.fromisoformat(resource['observedAt'])).total_seconds() < 240
    assert resource['ownHeavyJobs'] == 0 and resource['cpuLoadPercent'] < 85 and resource['freePhysicalMemoryKiB'] > 8_000_000
    review = read(O / 'current34-mixed-complete-direct-review-v1.json')
    assert review['all180ContextsDirectlyCompared'] and review['all34WholeTextsDirectlyCompared']
    assert review['mixAacSha256'] == plan['currentAacSha256']
    assert plan['currentNarrationGuideTimingDirectlyReviewed'], 'Review retained cue/point meanings before rendering.'
    mix = read(O / 'current34-mix-execution-v2.json')
    assert mix['actualOuterExitCode'] == 0 and mix['workerDead']
    for x in mix['protectedInputs']:
        assert sha(ROOT / x['path']) == x['sha256']
    source = ROOT / plan['scenes'][0]['source']
    source_sha = sha(source)
    assert source_sha == plan['scenes'][0]['sourceSha256']
    assert sha(ROOT / plan['measuredTiming']) == plan['measuredTimingSha256']
    for row in plan['scenes']:
        assert row['source'] == plan['scenes'][0]['source'] and row['sourceSha256'] == source_sha
        for x in row['pointWindow']['keyframes']:
            assert sha(ROOT / x['inspectedImage']) == x['inspectedImageSha256']
    LOCAL.mkdir(parents=True)
    me = psutil.Process()
    state = dict(startedAt=now(), pid=me.pid, createTime=me.create_time(), commandLine=me.cmdline(), cwd=me.cwd(),
        sessionId=None, cpuThreads=2, gpuJobs=0, resource=args.resource, resourceSha256=sha(ROOT / args.resource),
        plan=rel(pp), planSha256=sha(pp), totalScenes=8, completedScenes=0, totalFrames=21370, results=[],
        status='rendering-current34-baseline-native-guides', workerExitCode=None, actualOuterExitCode=None,
        finalCueApproved=False, allIntermediateFramesApproved=False, all79ProtectedInputsUnchanged=False, newImageGit=0)
    def checkpoint():
        ss = sp.with_name(sp.stem + '.session.json')
        if ss.exists():
            session = read(ss)
            assert session['pid'] == me.pid and abs(session['createTime']-me.create_time()) < .01
            state['sessionId'] = session['sessionId']
        state['updatedAt'] = now(); save(sp, state)
        cp = read(O / 'latest-checkpoint.json')
        cp.update(stage=state['status'], activeOwnedWorkers=1, ownedJob=dict(state),
            next='Observe actual guide worker exit, verify native PTS and decode; directly review encoded guide samples/cuts/captions. Preserve all approved PCM and original explanations.')
        save(O / 'latest-checkpoint.json', cp)
        qp = B / 'queue.json'; before = qp.read_bytes(); q = read(qp)
        q['currentOrientationReview'].update(stage=state['status'], activeOwnedWorkers=1, ownedJob=dict(state))
        assert qp.read_bytes() == before; save(qp, q)
    ep = dp = None
    try:
        checkpoint()
        for row in plan['scenes']:
            sid = row['id']; folder = LOCAL / sid; folder.mkdir()
            target = folder / f'{sid}.guided.silent.mp4'
            enc = [FF, '-hide_banner', '-nostdin', '-v', 'error', '-f', 'rawvideo', '-pixel_format', 'rgb24',
                '-video_size', '1920x1080', '-framerate', '60', '-i', 'pipe:0', '-frames:v', str(row['frames']),
                '-an', '-c:v', 'libx264', '-threads', '1', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p',
                '-video_track_timescale', '90000', '-movflags', '+faststart', str(target)]
            audit = []; commands = []; native_pts = []
            with (folder / 'encode.log').open('wb') as el:
                ep = subprocess.Popen(enc, stdin=subprocess.PIPE, stderr=el, cwd=ROOT)
                state.update(scene=sid, encodePid=ep.pid, encodeCreateTime=psutil.Process(ep.pid).create_time())
                checkpoint()
                for cut in row['windows']:
                    first, last = cut['firstNativeFrame'], cut['endExclusiveNativeFrame']
                    dec = [FF, '-hide_banner', '-nostdin', '-v', 'info', '-threads', '1', '-filter_threads', '1',
                        '-ss', str(first/60), '-copyts', '-i', str(source), '-an',
                        '-vf', f'trim=start_pts={first*256}:end_pts={last*256},showinfo',
                        '-frames:v', str(last-first), '-pix_fmt', 'rgb24', '-f', 'rawvideo', 'pipe:1']
                    commands.append(dict(nativeIn=first, nativeOutExclusive=last, decode=dec))
                    log = folder / f'decode-{cut["segment"]:02d}.log'
                    with log.open('wb') as dl:
                        dp = subprocess.Popen(dec, stdout=subprocess.PIPE, stderr=dl, cwd=ROOT)
                        state.update(decodePid=dp.pid, decodeCreateTime=psutil.Process(dp.pid).create_time())
                        checkpoint()
                        for local in range(last-first):
                            frame = cut['sceneFrameIn'] + local
                            raw = dp.stdout.read(1920*1080*3)
                            assert len(raw) == 1920*1080*3, (sid, frame, len(raw))
                            data, observed = draw_frame(raw, frame, row)
                            ep.stdin.write(data)
                            audit.append(dict(frame=frame, sourceNativeFrame=first+local,
                                sourcePts=(first+local)*256, **observed))
                            if frame % 300 == 0:
                                state['sceneWrittenFrames'] = frame+1; checkpoint()
                        assert dp.stdout.read(1) == b''
                        dp.stdout.close(); dx = dp.wait(); assert dx == 0
                    pts = [int(x) for x in re.findall(r'\bn:\s*\d+\s+pts:\s*(\d+)', log.read_text('utf-8', errors='replace'))]
                    assert pts == [(first+i)*256 for i in range(last-first)]
                    native_pts.extend(pts)
                ep.stdin.close(); ex = ep.wait(); assert ex == 0
            assert len(audit) == row['frames'] and [x['frame'] for x in audit] == list(range(row['frames']))
            save(folder / 'commands.json', dict(encode=enc, nativeWindows=commands))
            save(folder / 'frame-observation-audit.json', dict(planSha256=state['planSha256'], frames=audit,
                claimsExactSourcePts=True, worldAxesMeasured=False, allIntermediatePixelApproval=False))
            probe = json.loads(subprocess.check_output([FP, '-v', 'error', '-select_streams', 'v:0', '-show_entries',
                'stream=width,height,r_frame_rate,time_base,nb_frames,duration', '-of', 'json', str(target)], text=True))
            v = probe['streams'][0]
            assert v['width'] == 1920 and v['height'] == 1080 and v['r_frame_rate'] == '60/1'
            assert v['time_base'] == '1/90000' and int(v['nb_frames']) == row['frames']
            with (folder / 'whole-decode.log').open('wb') as ql:
                dx = subprocess.run([FF, '-hide_banner', '-nostdin', '-v', 'error', '-threads', '2', '-i',
                    str(target), '-f', 'null', '-'], stdout=ql, stderr=subprocess.STDOUT).returncode
            assert dx == 0
            state['results'].append(dict(id=sid, output=rel(target), outputSha256=sha(target), frames=row['frames'],
                nativePtsCount=len(native_pts), allNativePtsExact=True, encoderExitCode=ex, wholeDecodeExitCode=dx,
                probe=probe, frameAudit=rel(folder / 'frame-observation-audit.json'),
                frameAuditSha256=sha(folder / 'frame-observation-audit.json')))
            state['completedScenes'] = len(state['results']); checkpoint()
            print(json.dumps(dict(scene=sid, frames=row['frames'], exactNativePts=True, exitCode=0)), flush=True)
        for x in mix['protectedInputs']:
            assert sha(ROOT / x['path']) == x['sha256']
        assert sum(x['frames'] for x in state['results']) == 21370
        state.update(status='current34-baseline-guides-complete-awaiting-encoded-review', workerExitCode=0,
            finishedAt=now(), all79ProtectedInputsUnchanged=True)
        checkpoint()
    except BaseException:
        cleanup = []
        for child, pipe in [(dp, 'stdout'), (ep, 'stdin')]:
            if child is None:
                continue
            stream = getattr(child, pipe, None)
            try:
                if stream is not None and not stream.closed:
                    stream.close()
            except (BrokenPipeError, OSError):
                pass
            try:
                cleanup.append(dict(pid=child.pid, exitCode=child.wait(timeout=20), pipeClosed=True))
            except subprocess.TimeoutExpired:
                cleanup.append(dict(pid=child.pid, exitCode=None, pipeClosed=True, stillAlive=True))
        state.update(status='current34-baseline-guides-failed-preserve-history', workerExitCode=1,
            error=traceback.format_exc(), finishedAt=now(), ownPipeCleanup=cleanup)
        checkpoint(); raise

if __name__ == '__main__':
    main()
