"""Inspect encoded pixels at every cue/cut and retained paragraph boundary."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, math, os, subprocess, sys, time, traceback
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
work_index = sys.argv.index('--work-directory') if '--work-directory' in sys.argv else None
W = BASE / (sys.argv[work_index + 1] if work_index is not None else 'final-v1')
assert W.parent == BASE and W.name in ('final-v1', 'final-v2')
DEST = W / 'encoded-caption-qa-local-v1'
FF = 'C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
rel = lambda p: p.relative_to(ROOT).as_posix()
now = lambda: datetime.now(timezone.utc).isoformat()


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def write(path, data):
    temporary = path.with_name(path.name + f'.{os.getpid()}.writing')
    for attempt in range(120):
        try:
            temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
            os.replace(temporary, path)
            return
        except OSError:
            if attempt == 119:
                raise
            time.sleep(.25)


plan = read(W / 'plan.json')
visual = read(W / 'visual-build.json')
tracks = read(W / 'caption-tracks.json')
assert visual['planSha256'] == sha(W / 'plan.json')
assert len(tracks['koRows']) == 308 and len(tracks['enRows']) == 173
assert tracks['everyCurrentScriptCharacterPreserved'] and tracks['all60ParagraphsIncluded']
points = {}


def add(frame, anchor, cue=None):
    frame = int(frame)
    if 0 <= frame < plan['finalFrames']:
        row = points.setdefault(frame, dict(frame=frame, anchors=[], cues=[]))
        if anchor not in row['anchors']:
            row['anchors'].append(anchor)
        if cue is not None and cue not in row['cues']:
            row['cues'].append(cue)


for segment in visual['segments']:
    a, z = segment['startFrame'], segment['startFrame'] + segment['frames']
    add(a, 'first:' + segment['id'])
    add(z - 1, 'last:' + segment['id'])
    add((a + z - 1) // 2, 'middle:' + segment['id'])
    for cue in tracks['koRows']:
        # ASS uses centisecond truncation; sample the actual display intersection.
        cue_a = math.ceil(math.floor(cue['startSeconds'] * 100 + 1e-7) * .6 - 1e-7)
        cue_z = math.ceil(math.floor(cue['endSeconds'] * 100 + 1e-7) * .6 - 1e-7)
        first, end = max(a, cue_a), min(z, cue_z)
        if end > first:
            add((first + end - 1) // 2, 'cue/segment:' + segment['id'], cue['index'])
for scene in plan['scenes']:
    for paragraph in scene['speechEvidence']:
        frame = scene['startFrame'] + round(paragraph['outputSpeechFromSample'] / 400)
        for offset in [-1, 0, 1]:
            add(frame + offset, f'PCM-onset:{scene["id"]}p{paragraph["paragraph"]}')
for frame in [119, 120, 1568, 1569, 32173, 32174, 32176, 32177, 32178, 34982, 34983, 35283, 35582]:
    add(frame, 'targeted-branding/overview/overhead/member-edge')
covered_cues = {cue for row in points.values() for cue in row['cues']}
assert covered_cues == {cue['index'] for cue in tracks['koRows']}
for frame, row in points.items():
    segment = next(segment for segment in visual['segments']
                   if segment['startFrame'] <= frame < segment['startFrame'] + segment['frames'])
    row.update(segment=segment['id'], classification=segment['classification'],
               scene=segment.get('sceneId'), localFrame=frame - segment['startFrame'])
    row['visibleCueIds'] = [cue['index'] for cue in tracks['koRows']
        if math.floor(cue['startSeconds'] * 100 + 1e-7) / 100 <= frame / 60
        < math.floor(cue['endSeconds'] * 100 + 1e-7) / 100]
request = dict(createdAt=now(), planSha256=sha(W / 'plan.json'), captionTracksSha256=sha(W / 'caption-tracks.json'),
               captionAssSha256=sha(W / 'captions.ko.ass'), sampledFrames=len(points), cueCount=308,
               nativeCutCount=85, whiteCount=7, all60ParagraphOnsetsCovered=True,
               allImagesLocalOnly=True, noNewGitImages=True, allEncodedPixelsDirectlyReviewed=False,
               points=[points[frame] for frame in sorted(points)])
if '--plan-only' in sys.argv:
    write(W / 'encoded-caption-qa-request.json', request)
    print(json.dumps(dict(frames=len(points), cueCount=308, nativeCuts=85, imagesCreated=0,
                          encodedReviewApproved=False)))
    sys.exit(0)

pair = read(W / 'review-pair-build.json')
assert pair['planSha256'] == request['planSha256']
assert pair['captionAssSha256'] == request['captionAssSha256'] and pair['identicalAacPayload']
captioned = ROOT / next(record['path'] for record in pair['records'] if '.captioned.' in record['path'])
assert sha(captioned) == next(record['sha256'] for record in pair['records'] if '.captioned.' in record['path'])
assert not DEST.exists()
DEST.mkdir()
state = dict(schemaVersion=1, startedAt=now(), pid=os.getpid(), sessionId=None,
             status='CPU-exact-encoded-caption-and-cut-pixel-extraction', threads=2, gpuJobs=0,
             source=rel(captioned), sourceSha256=sha(captioned), frames=plan['finalFrames'],
             request=request, images=[], sheets=[], activeTasks=[], newGitImages=0,
             allFinalPixelsApproved=False, qaApproved=False)


def checkpoint():
    session = DEST / 'session.json'
    if session.exists() and read(session).get('pid') == os.getpid():
        state['sessionId'] = read(session)['sessionId']
    state['observedAt'] = now()
    write(DEST / 'execution.json', state)
    qp = ROOT / 'production/batches/sakurai-planning-game-design/queue.json'
    queue = read(qp)
    item = next(row for row in queue['items'] if row['slug'] == 'making-game-sequels')
    item.update(stage='current13-guided60-encoded-caption-and-cut-pixel-QA', updatedAt=state['observedAt'],
        nextAction='Directly inspect all encoded cue/segment intersections, cut and PCM edges, branding/member identities; keep QA/collection/private false until actual review.')
    item['execution'].update(status=state['status'], phase=item['stage'], observedAt=state['observedAt'],
        pid=os.getpid(), sessionId=state['sessionId'], state=rel(DEST / 'execution.json'),
        commandLine='extract-encoded-caption-qa-v1.py CPU2/GPU0', activeTasks=state['activeTasks'],
        alive='endedAt' not in state, cpuProductionJobs=int('endedAt' not in state),
        primaryCpuProductionJobs=int('endedAt' not in state), gpuSynthesisJobs=0, renderJobs=0, uploads=0)
    queue['updatedAt'] = item['updatedAt']
    write(qp, queue)
    for path in [BASE / 'latest-checkpoint.json', ROOT / 'production/batches/sakurai-planning-game-design/proof-making-game-sequels/latest-checkpoint.json']:
        data = read(path)
        for key in ['stage', 'updatedAt', 'nextAction', 'execution']:
            data[key] = item[key]
        write(path, data)


try:
    checkpoint()
    expression = '+'.join(f'eq(n\\,{frame})' for frame in sorted(points))
    command = [FF, '-v', 'error', '-nostdin', '-threads', '2', '-i', str(captioned),
               '-an', '-filter_threads', '1', '-vf', f"select='{expression}'", '-fps_mode', 'passthrough',
               '-threads', '2', '-frames:v', str(len(points)), str(DEST / 'frame-%04d.png')]
    log = DEST / 'extract.log'
    with log.open('wb') as stream:
        child = subprocess.Popen(command, stdout=stream, stderr=stream, creationflags=subprocess.CREATE_NO_WINDOW)
        state['activeTasks'] = [dict(pid=child.pid, command=command, log=rel(log))]
        checkpoint()
        exit_code = child.wait()
    state['activeTasks'] = []
    assert exit_code == 0 and not log.read_text().strip(), (exit_code, rel(log))
    files = sorted(DEST.glob('frame-*.png'))
    assert len(files) == len(points)
    for path, frame in zip(files, sorted(points)):
        state['images'].append(dict(points[frame], path=rel(path), sha256=sha(path), directlyRead=False))
    checkpoint()
    font = ImageFont.truetype('C:/Windows/Fonts/malgun.ttf', 20)
    for offset in range(0, len(state['images']), 6):
        subset = state['images'][offset:offset + 6]
        board = Image.new('RGB', (1920, 1740), 'white')
        draw = ImageDraw.Draw(board)
        for slot, row in enumerate(subset):
            x, y = slot % 2 * 960, slot // 2 * 580
            with Image.open(ROOT / row['path']) as image:
                assert image.size == (1920, 1080)
                board.paste(image.resize((960, 540)), (x, y + 40))
            draw.text((x + 5, y + 4), f'{offset + slot + 1:04d} n{row["frame"]} {row["segment"][:45]} cue{row["visibleCueIds"]}', font=font, fill='black')
        path = DEST / f'final-sheet-{offset // 6 + 1:03d}.jpg'
        board.save(path, quality=94)
        state['sheets'].append(dict(path=rel(path), sha256=sha(path),
                                   imageIndices=list(range(offset + 1, offset + len(subset) + 1)), directlyRead=False))
    state.update(status='closed-encoded-pixels-awaiting-direct-review', exitCode=0, endedAt=now(), activeTasks=[])
    checkpoint()
    print(json.dumps(dict(images=len(state['images']), sheets=len(state['sheets']), newGitImages=0, approved=False)))
except BaseException:
    state.update(status='closed-encoded-pixel-extraction-failed', exitCode=1, endedAt=now(),
                 error=traceback.format_exc(), activeTasks=[])
    checkpoint()
    raise
