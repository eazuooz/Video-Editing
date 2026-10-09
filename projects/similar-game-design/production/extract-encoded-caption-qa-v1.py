"""Plan or extract current encoded cue/cut/motion pixels; never approve automatically."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, ctypes, hashlib, json, math, os, re, subprocess, sys, time, traceback
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
W = BASE / 'final-v1'
DEST = ROOT / 'shared/output/similar-game-design/final-encoded-caption-qa-v1'
STATE = W / 'encoded-caption-qa-execution.json'
SESSION = W / 'encoded-caption-qa-session.json'
FF = Path('C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe')
read = lambda p: json.loads(p.read_text('utf-8-sig'))
now = lambda: datetime.now(timezone.utc).isoformat()
rel = lambda p: p.relative_to(ROOT).as_posix()


def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def save(p, data):
    temp = p.with_name(p.name + f'.{os.getpid()}.writing')
    for attempt in range(60):
        try:
            temp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', 'utf-8')
            os.replace(temp, p)
            return
        except OSError:
            if attempt == 59:
                raise
            time.sleep(.15)


parser = argparse.ArgumentParser()
parser.add_argument('--plan-only', action='store_true')
parser.add_argument('--resource')
args = parser.parse_args()
plan = read(W / 'plan.json')
clock = read(W / 'caption-clock-adoption.json')
timing = read(ROOT / plan['voiceTiming'])
assert sha(ROOT / plan['voiceTiming']) == plan['voiceTimingSha256']
assert clock['koCueCount'] == 400 and clock['enCueCount'] == 148
assert clock['finalAssSha256'] == sha(W / 'captions.ko.ass')
assert plan['finalFrames'] == 37098 and plan['bodyFrames'] == 36378
segments = [dict(id='branding', startFrame=0, frames=120, role='branding')]
segments += [dict(id=f'{cut["index"]:03d}-{cut["scene"]}', startFrame=cut['startFrame'],
                 frames=cut['frames'], role=cut['role'], scene=cut['scene'], source=cut.get('source'))
             for cut in plan['cuts']]
segments += [dict(id='membership', startFrame=36498, frames=600, role='membership')]
assert len(plan['cuts']) == 69
assert sum(x['frames'] for x in segments) == 37098
assert all(x['startFrame'] + x['frames'] == y['startFrame'] for x, y in zip(segments, segments[1:]))


def ass_seconds(value):
    hours, minutes, seconds = value.split(':')
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


cues = []
cue_clock = {}
text_rows = 0
for line in (W / 'captions.ko.ass').read_text('utf-8-sig').splitlines():
    if line.startswith('Dialogue: 2,'):
        fields = line.split(',', 9)
        text_rows += 1
        key = (fields[1], fields[2])
        if key not in cue_clock:
            cue = dict(index=len(cues) + 1, startSeconds=ass_seconds(fields[1]),
                       endSeconds=ass_seconds(fields[2]), textRows=0)
            cue_clock[key] = cue
            cues.append(cue)
        cue_clock[key]['textRows'] += 1
assert len(cues) == 400
assert text_rows == 437 and all(1 <= x['textRows'] <= 2 for x in cues)
points = {}


def add(frame, anchor, cue=None):
    frame = int(frame)
    if 0 <= frame < 37098:
        row = points.setdefault(frame, dict(frame=frame, anchors=[], cueIds=[]))
        if anchor not in row['anchors']:
            row['anchors'].append(anchor)
        if cue is not None and cue not in row['cueIds']:
            row['cueIds'].append(cue)


for cue in cues:
    lo = math.ceil(cue['startSeconds'] * 60 - 1e-7)
    hi = math.ceil(cue['endSeconds'] * 60 - 1e-7)
    assert hi > lo
    for frame, label in [(lo, 'cue-first'), ((lo + hi - 1) // 2, 'cue-mid'), (hi - 1, 'cue-last')]:
        add(frame, f'{label}:{cue["index"]}', cue['index'])
    for segment in segments:
        left = max(lo, segment['startFrame'])
        right = min(hi, segment['startFrame'] + segment['frames'])
        if right > left:
            add((left + right - 1) // 2, f'cue/segment:{segment["id"]}', cue['index'])
for segment in segments:
    lo = segment['startFrame']
    hi = lo + segment['frames']
    for frame, label in [(lo - 1, 'before-cut'), (lo, 'first-cut'), ((lo + hi - 1) // 2, 'mid-cut'),
                         (hi - 1, 'last-cut'), (hi, 'after-cut')]:
        add(frame, f'{label}:{segment["id"]}')
    if segment['role'] == 'explanation':
        for fraction in [.25, .75]:
            add(lo + int((hi - lo - 1) * fraction), f'white-motion:{segment["id"]}')
onsets = 0
for scene in timing['rows']:
    for paragraph, sample in enumerate(scene['paragraphStartSamples'], 1):
        frame = scene['startFrame'] + round(sample / 400)
        onsets += 1
        for offset in [-1, 0, 1]:
            add(frame + offset, f'PCM-onset:{scene["id"]}p{paragraph}')
assert onsets == 73
selected = read(BASE / 'selected-inputs-execution-v1.json')
assert selected['allInputSegmentCaptionPixelsReviewed'] and selected['exitCode'] == 0
assert len(selected['samples']) == 664
for sample in selected['samples']:
    add(sample['finalFrame'], f'approved-input-anchor:{sample["index"]}')
for frame in [0, 60, 119, 120, 1435, 1436, 36497, 36498, 36558, 36798, 37038, 37097]:
    add(frame, 'branding/overview/member-edge')
for frame, row in points.items():
    segment = next(x for x in segments if x['startFrame'] <= frame < x['startFrame'] + x['frames'])
    row.update(segment=segment['id'], role=segment['role'], scene=segment.get('scene'),
               source=segment.get('source'), seconds=frame / 60, expectedPts=frame * 1500)
    row['visibleCueIds'] = [x['index'] for x in cues if x['startSeconds'] <= frame / 60 + 1e-7 < x['endSeconds']]
assert {cue for row in points.values() for cue in row['cueIds']} == set(range(1, 401))
request = dict(createdAt=now(), planSha256=sha(W / 'plan.json'), captionAssSha256=sha(W / 'captions.ko.ass'),
               frames=37098, sampledFrames=len(points), koCueCount=400, enCueCount=148, cutCount=69,
               assTextRows=437, twoLineCues=37,
               actualCutCount=sum(x['role'] == 'actual' for x in segments),
               explanationCutCount=sum(x['role'] == 'explanation' for x in segments),
               pcmOnsets=73, allCueCutIntersectionsCovered=True, all664ApprovedInputAnchorsRetained=True,
               points=[points[frame] for frame in sorted(points)], imagesLocalOnly=True, newGitImages=0,
               allFinalPixels=False, actualExtractionStarted=False)
save(W / 'encoded-caption-qa-request.json', request)
if args.plan_only:
    print(json.dumps(dict(plannedFrames=len(points), plannedBoards=math.ceil(len(points) / 6),
                         koCues=400, cuts=69, pcmOnsets=73, actualImagesCreated=0, allFinalPixels=False)))
    sys.exit(0)
assert args.resource
resource = read(ROOT / args.resource)
assert resource['ownHeavyJobs'] == 0 and resource['cpuLoadPercent'] < 85 and resource['freePhysicalMemoryKiB'] > 8000000
assert (datetime.now(timezone.utc) - datetime.fromisoformat(resource['observedAt'].replace('Z', '+00:00'))).total_seconds() < 240
pair = read(W / 'review-pair-build.json')
assert pair['planSha256'] == request['planSha256'] and pair['captionAssSha256'] == request['captionAssSha256']
assert pair['identicalAacPayload'] and read(W / 'review-pair-execution.json')['exitCode'] == 0
record = next(x for x in pair['records'] if '.captioned.' in x['path'])
source = ROOT / record['path']
assert sha(source) == record['sha256']
assert not STATE.exists() and not DEST.exists(), 'Read actual extraction checkpoint; never repeat completed frames.'
if os.name == 'nt':
    ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x00004000)
DEST.mkdir()
(DEST / 'frames').mkdir()
(DEST / 'boards').mkdir()
state = dict(schemaVersion=1, slug='similar-game-design', pid=os.getpid(), sessionId=None, commandLine=[sys.executable, *sys.argv],
             startedAt=now(), status='extracting-current-final-encoded-pixels', resourceEvidence=args.resource,
             cpuThreads=2, gpu=0, singleJob=True, exitCode=None, activeTask=None, source=rel(source), sourceSha256=record['sha256'],
             requestPath=rel(W / 'encoded-caption-qa-request.json'), requestSha256=sha(W / 'encoded-caption-qa-request.json'),
             samples=[], boards=[], allFinalPixels=False, qaApproved=False, collected=False, uploaded=False,
             imagesLocalOnly=True, newGitImages=0)


def checkpoint():
    if SESSION.exists():
        session = read(SESSION)
        if session['pid'] == os.getpid():
            state.update(sessionId=session['sessionId'], processIdentity=session['processIdentity'])
    state['observedAt'] = now()
    save(STATE, state)
    job = dict(pid=state['pid'], sessionId=state['sessionId'], processIdentity=state.get('processIdentity'),
               commandLine=state['commandLine'], state=rel(STATE), status=state['status'], cpuThreads=2, gpu=0,
               singleJob=True, activeTask=state['activeTask'], exitCode=state['exitCode'], workerExpectedRunning=state['exitCode'] is None)
    cp_path = BASE / 'latest-checkpoint.json'
    cp = read(cp_path)
    cp.update(stage=state['status'], ownedJob=job, recordedAt=now(), encodedPixelExecution=rel(STATE),
              allFinalPixels=False, qaApproved=False, collected=False, uploaded=False,
              nextAction='Directly read every current final board/cue/cut/PCM/motion/member identity; then QA/4file collection/private settings/Git.')
    save(cp_path, cp)
    qp = ROOT / 'production/batches/sakurai-planning-game-design/queue.json'
    queue = read(qp)
    item = next(x for x in queue['items'] if x['slug'] == 'similar-game-design')
    item.update(stage=state['status'], currentExecution=job, encodedPixelExecution=rel(STATE), allFinalPixels=False,
                qaApproved=False, collected=False, uploaded=False, nextAction=cp['nextAction'])
    queue['updatedAt'] = now()
    save(qp, queue)


try:
    request['actualExtractionStarted'] = True
    save(W / 'encoded-caption-qa-request.json', request)
    state['requestSha256'] = sha(W / 'encoded-caption-qa-request.json')
    checkpoint()
    expression = "select='" + '+'.join(f'eq(pts,{frame * 1500})' for frame in sorted(points)) + "',showinfo"
    filter_path = DEST / 'absolute-pts-select.filter'
    filter_path.write_text(expression, 'utf-8')
    command = [str(FF), '-hide_banner', '-v', 'info', '-nostdin', '-threads', '2', '-i', str(source), '-an',
               '-filter_threads', '1', '-filter_script:v', str(filter_path), '-fps_mode', 'passthrough',
               '-frames:v', str(len(points)), '-threads', '2', str(DEST / 'frames/frame-%04d.png')]
    log = DEST / 'extract.log'
    with log.open('w', encoding='utf-8') as stream:
        child = subprocess.Popen(command, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW)
        state['activeTask'] = dict(pid=child.pid, commandLine=command, log=rel(log))
        checkpoint()
        code = child.wait()
    assert code == 0, (code, rel(log))
    text = log.read_text('utf-8-sig')
    decoded_pts = [int(x) for x in re.findall(r'\[Parsed_showinfo[^\]]*\]\s+n:\s*\d+\s+pts:\s*(\d+)', text)]
    expected_pts = [frame * 1500 for frame in sorted(points)]
    assert decoded_pts == expected_pts, 'Actual decoded PTS must match every planned frame; preserve failures.'
    files = sorted((DEST / 'frames').glob('frame-*.png'))
    assert len(files) == len(points)
    for index, (path, frame, pts) in enumerate(zip(files, sorted(points), decoded_pts), 1):
        state['samples'].append(dict(index=index, **points[frame], decodedPts=pts, path=rel(path), sha256=sha(path), directlyRead=False))
    state.update(status='creating-current-final-review-boards', activeTask=None)
    checkpoint()
    font = ImageFont.truetype('C:/Windows/Fonts/malgun.ttf', 20)
    for offset in range(0, len(files), 6):
        rows = state['samples'][offset:offset + 6]
        board = Image.new('RGB', (1920, 1740), 'white')
        draw = ImageDraw.Draw(board)
        for slot, row in enumerate(rows):
            x, y = slot % 2 * 960, slot // 2 * 580
            with Image.open(ROOT / row['path']) as frame_image:
                assert frame_image.size == (1920, 1080)
                board.paste(frame_image.resize((960, 540)), (x, y + 40))
            draw.text((x + 5, y + 4), f'{row["index"]:04d} f{row["frame"]} {row["segment"][:32]} cue{row["visibleCueIds"]}', font=font, fill='black')
        path = DEST / f'boards/board-{offset // 6 + 1:03d}.jpg'
        board.save(path, quality=94, subsampling=0)
        state['boards'].append(dict(index=offset // 6 + 1, path=rel(path), sha256=sha(path),
                                    sampleIndices=[row['index'] for row in rows], directlyRead=False))
    state.update(status='closed-current-final-pixels-awaiting-full-direct-review', exitCode=0, endedAt=now(), activeTask=None,
                 sampleCount=len(state['samples']), boardCount=len(state['boards']), allActualPtsMatched=True)
    checkpoint()
    print(json.dumps(dict(exitCode=0, frames=len(files), boards=len(state['boards']), allFinalPixels=False, newGitImages=0)), flush=True)
except BaseException:
    state.update(status='closed-current-final-pixel-extraction-failed', exitCode=1, endedAt=now(), activeTask=None, error=traceback.format_exc())
    checkpoint()
    raise
