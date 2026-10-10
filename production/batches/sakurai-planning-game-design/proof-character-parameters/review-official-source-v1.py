"""Offline CPU2 source decode and native-PTS discovery; no narration or adoption."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, math, os, shutil, subprocess, sys, traceback
import psutil
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[4]
PROOF = Path(__file__).resolve().parent
LOCAL = ROOT / 'shared/output/character-parameters/preflight'
MEDIA = ROOT / 'shared/assets/character-parameters/raw'
QA = LOCAL / 'official-coarse-v1'
STATE = PROOF / 'official-source-review-execution-v1.json'
QUEUE = ROOT / 'production/batches/sakurai-planning-game-design/queue.json'
FF = 'C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
FP = 'C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe'
NODE = 'C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
stamp = lambda: datetime.now(timezone.utc).isoformat()
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def write(p, d):
    t = p.with_name(p.name + f'.{os.getpid()}.tmp')
    t.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    os.replace(t, p)

if STATE.exists():
    raise SystemExit('Existing CPU source execution; inspect, do not repeat extraction/decode.')
old = json.loads((PROOF / 'official-acquisition-execution-v1.json').read_text(encoding='utf-8-sig'))
if old['status'] != 'failed' or old['children'][-1].get('exitCode') != 0:
    raise SystemExit('Unexpected acquisition state; do not assume downloaded source')
info_path = MEDIA / 'gBbKFYZYvbc.info.json'
info = json.loads(info_path.read_text(encoding='utf-8'))
movie = MEDIA / 'gBbKFYZYvbc.mp4'
if info.get('id') != 'gBbKFYZYvbc' or info.get('channel_id') != 'UCjJe1z4OSKKav9MLVEvXWfA' or not movie.is_file():
    raise SystemExit('Official owner/source file mismatch')
# Preserve the original metadata and add an exact ignore rule, without touching foreign entries.
ignore = ROOT / '.gitignore'
before_ignore = ignore.read_bytes()
rule = b'/shared/assets/character-parameters/raw/gBbKFYZYvbc.info.json'
if rule not in before_ignore.splitlines():
    if ignore.read_bytes() != before_ignore:
        raise SystemExit('Foreign ignore edit occurred; preserve and reconcile')
    with ignore.open('ab') as f:
        if before_ignore and not before_ignore.endswith(b'\n'):
            f.write(b'\n')
        f.write(rule + b'\n')
copy_info = LOCAL / 'source-info/gBbKFYZYvbc.info.json'
if copy_info.exists():
    if sha(copy_info) != sha(info_path):
        raise SystemExit('Preserve divergent metadata copies')
else:
    shutil.copy2(info_path, copy_info)
sources = list(old['sources']) + [{
    'kind': 'official-tournament-recording', 'sourceVideoId': info['id'], 'sourceUrl': info['webpage_url'],
    'title': info['title'], 'channel': info['channel'], 'channelId': info['channel_id'],
    'metadataUploadDate': info.get('upload_date'), 'observedYouTubeLocalDate': '2017-12-24',
    'localPath': str(movie.relative_to(ROOT)).replace('\\', '/'), 'bytes': movie.stat().st_size,
    'sha256': sha(movie), 'metadata': str(copy_info.relative_to(ROOT)).replace('\\', '/'), 'adopted': False,
}]
recovery = {
    'schemaVersion': 1, 'recordedAt': stamp(), 'acquisitionState': str((PROOF / 'official-acquisition-execution-v1.json').relative_to(ROOT)).replace('\\', '/'),
    'originalOuterSessionId': 71878, 'originalOuterExitCode': 1, 'actualDownloadChildExitCode': 0,
    'failureCause': 'Absolute output template placed completed info.json alongside MP4; expected infojson --paths directory was empty.',
    'completedOriginalFilesPreserved': True, 'downloadRepeated': False, 'sourceCount': len(sources), 'sources': sources,
    'sourceAudioForFinal': 'exclude-all', 'decodeApproved': False, 'sourceAdoptionApproved': False,
}
write(PROOF / 'official-acquisition-recovery-v2.json', recovery)
subprocess.run([NODE, 'scripts/review-video-duplicates.cjs', 'character-parameters', '--check'], cwd=ROOT, check=True)
QA.mkdir(parents=True, exist_ok=True)
state = {'schemaVersion': 1, 'slug': 'character-parameters', 'status': 'initializing', 'startedAt': stamp(),
         'pid': os.getpid(), 'processCreateTime': psutil.Process().create_time(), 'commandLine': sys.argv,
         'workingDirectory': str(ROOT), 'sessionId': None, 'cpuThreads': 2, 'gpuJobs': 0, 'children': [],
         'sources': [], 'wholeDecodeApproved': False, 'directPixelReviewApproved': False,
         'sourceAdoptionApproved': False, 'newScriptOrTts': False, 'externalResearchChanges': 0}

def save(status):
    state.update(status=status, updatedAt=stamp())
    sp = STATE.with_name(STATE.name + '.session.json')
    if sp.exists():
        session = json.loads(sp.read_text(encoding='utf-8-sig'))
        if session.get('pid') == os.getpid():
            state['sessionId'] = session.get('sessionId')
    write(STATE, state)
    before = QUEUE.read_bytes()
    q = json.loads(before)
    item = next(x for x in q['items'] if x['slug'] == 'character-parameters')
    if item.get('videoId') or any(item['checkpoints'].values()):
        raise RuntimeError('Character item advanced; no overwrite')
    item.update(status='in-progress', stage='official-source-' + status, updatedAt=state['updatedAt'])
    item['execution'] = {k: state[k] for k in ('status', 'pid', 'processCreateTime', 'commandLine', 'workingDirectory', 'sessionId', 'cpuThreads', 'gpuJobs')}
    item['execution'].update(phase='source-decode-and-coarse-extraction', state=str(STATE.relative_to(ROOT)).replace('\\', '/'),
                             child=state['children'][-1] if state['children'] else None)
    item['nextAction'] = 'Directly inspect every generated board, then select exact native action intervals and framing; no adoption or narration on coarse evidence alone.'
    q['updatedAt'] = q['lastProgressAt'] = state['updatedAt']
    if QUEUE.read_bytes() != before:
        raise RuntimeError('Concurrent queue changed; preserve foreign data')
    write(QUEUE, q)

def run(args, label, output=None):
    log_path = QA / (label + '.log')
    with log_path.open('wb') as log:
        c = subprocess.Popen(args, cwd=ROOT, stdout=subprocess.PIPE if output else log, stderr=log, creationflags=subprocess.CREATE_NO_WINDOW)
        rec = {'label': label, 'pid': c.pid, 'processCreateTime': psutil.Process(c.pid).create_time(),
               'commandLine': args, 'status': 'running', 'startedAt': stamp(), 'log': str(log_path.relative_to(ROOT)).replace('\\', '/')}
        state['children'].append(rec)
        save('single-cpu-job-running')
        data = c.communicate()[0]
        rec.update(status='exited', exitCode=c.returncode, endedAt=stamp())
        if c.returncode:
            raise RuntimeError(label + f' failed: {c.returncode}')
        if output:
            output.write_bytes(data)
            return json.loads(data)

try:
    save('cpu-review-initializing')
    font = ImageFont.truetype('C:/Windows/Fonts/consola.ttf', 18)
    for s in sources:
        p = ROOT / s['localPath']
        if sha(p) != s['sha256']:
            raise RuntimeError('Source changed: ' + str(p))
        key = p.stem
        sub = QA / key
        sub.mkdir(exist_ok=True)
        meta = run([FP, '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(p)], key+'-probe', sub/'probe.json')
        video = next(v for v in meta['streams'] if v['codec_type'] == 'video')
        frames_data = run([FP, '-v', 'error', '-select_streams', 'v:0', '-show_frames',
                           '-show_entries', 'frame=best_effort_timestamp,best_effort_timestamp_time,pkt_duration',
                           '-of', 'json', str(p)], key+'-frame-pts', sub/'native-pts.json')
        frames = frames_data['frames']
        pts = [int(f['best_effort_timestamp']) for f in frames]
        if len(set(pts)) != len(pts) or any(b <= a for a,b in zip(pts, pts[1:])):
            raise RuntimeError('Nonmonotonic native source PTS requires explicit investigation')
        run([FF, '-nostdin', '-v', 'error', '-threads', '2', '-filter_threads', '2', '-i', str(p),
             '-map', '0:v:0', '-an', '-f', 'null', '-'], key+'-whole-decode')
        step = 2.0 if s['kind'] == 'official-tournament-recording' else 0.5
        chosen=[]; next_time=0.0
        for idx, f in enumerate(frames):
            t=float(f['best_effort_timestamp_time'])
            if t + 1e-8 >= next_time:
                chosen.append({'nativeFrame': idx, 'pts': pts[idx], 'timeSeconds': t})
                next_time += step
        if chosen[-1]['nativeFrame'] != len(frames)-1:
            chosen.append({'nativeFrame': len(frames)-1, 'pts': pts[-1], 'timeSeconds': float(frames[-1]['best_effort_timestamp_time'])})
        expr = '+'.join('eq(pts,'+str(f['pts'])+')' for f in chosen)
        run([FF, '-nostdin', '-v', 'error', '-threads', '2', '-filter_threads', '2', '-i', str(p),
             '-vf', "select='"+expr+"'", '-fps_mode', 'passthrough', '-an', '-threads', '2', str(sub/'sample-%04d.png')], key+'-coarse-extract')
        files = sorted(sub.glob('sample-*.png'))
        if len(files) != len(chosen):
            raise RuntimeError('Extraction count mismatch; do not approve or guess PTS')
        for sample, image_path in zip(chosen, files):
            sample.update(path=str(image_path.relative_to(ROOT)).replace('\\','/'), sha256=sha(image_path))
        boards=[]
        for off in range(0, len(files), 6):
            board=Image.new('RGB',(1920,816),(24,24,24)); draw=ImageDraw.Draw(board)
            for n,(file,sample) in enumerate(zip(files[off:off+6], chosen[off:off+6])):
                x=(n%3)*640; y=(n//3)*408
                im=Image.open(file).convert('RGB'); im.thumbnail((640,360))
                board.paste(im,(x+(640-im.width)//2,y+36+(360-im.height)//2))
                draw.text((x+6,y+3),key+' #'+str(sample['nativeFrame']),font=font,fill='white')
                draw.text((x+6,y+384),'PTS '+str(sample['pts'])+'  t '+format(sample['timeSeconds'],'.6f'),font=font,fill=(180,230,230))
            board_path=sub/f'board-{off//6+1:03d}.jpg'; board.save(board_path, quality=92)
            boards.append({'path':str(board_path.relative_to(ROOT)).replace('\\','/'), 'sha256':sha(board_path), 'sampleRange':[off,min(off+6,len(files))]})
        state['sources'].append({**s,'probe':str((sub/'probe.json').relative_to(ROOT)).replace('\\','/'),
                                 'video':{k:video.get(k) for k in ('width','height','r_frame_rate','time_base','duration','nb_frames')},
                                 'decodedFrames':len(frames),'wholeDecodeExitCode':0,'nativePtsMonotonic':True,
                                 'samples':chosen,'boards':boards,'directPixelReviewApproved':False,'adopted':False})
        save('source-coarse-extracted')
    state['wholeDecodeApproved']=True
    state['totalSamples']=sum(len(s['samples']) for s in state['sources'])
    state['totalBoards']=sum(len(s['boards']) for s in state['sources'])
    save('coarse-extracted-awaiting-direct-review')
    print(json.dumps({'status':state['status'],'sources':len(state['sources']),'samples':state['totalSamples'],'boards':state['totalBoards']},ensure_ascii=False),flush=True)
except BaseException:
    state['error']=traceback.format_exc()
    try: save('failed')
    except Exception: write(STATE,state)
    print(state['error'],flush=True)
    sys.exit(1)
