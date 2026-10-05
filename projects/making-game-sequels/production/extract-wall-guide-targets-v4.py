"""Extract every actual cue intersection and three encoded anchors per cut.

All raster output stays local. These are framing trials, not pixel approvals.
Only CPU decoding is used; no synthesis, acquisition or final video rendering.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, subprocess, time, traceback
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
WORK = BASE / 'measured-edit-v4'
DEST = WORK / 'wall-guide-target-local-v4'
FF = 'C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
rel = lambda p: p.relative_to(ROOT).as_posix()
now = lambda: datetime.now(timezone.utc).isoformat()

def write(p, d):
    tmp = p.with_name(p.name + f'.{os.getpid()}.writing')
    for attempt in range(30):
        try:
            tmp.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
            os.replace(tmp, p)
            return
        except OSError:
            if attempt == 29: raise
            time.sleep(.1)

assert not DEST.exists(), 'Preserve an existing extraction; inspect the actual execution first.'
DEST.mkdir()
plan = read(WORK / 'plan.json')
compiled = read(WORK / 'native-review-v4/compiled.json')
layout = read(WORK / 'caption-layout-v4.json')
assert compiled['planSha256'] == sha(WORK / 'plan.json') and not plan['finalTimingApproved']
assert read(WORK / 'native-review-v4/execution.json')['exitCode'] == 0
cuts = [c for s in plan['scenes'] for c in s['segments'] if c['classification'] == 'actual-existing-game' and ((s['id']=='02' and c['paragraph']==4) or (s['id']=='06' and c['paragraph']==2))]
guide_word_frames=[]
for s in plan['scenes']:
    for p in s['speechEvidence']:
        if not (p.get('guideId')=='02-g1' or (s['id']=='06' and p['paragraph']==2)):continue
        asr=read(ROOT/p['asrEvidence']['path'])
        for w in asr['words']:
            a,z=w['timestamp']
            if a is None or z is None or z<=a:continue
            a=max(p['pcmFromSample']/24000,a);z=min(p['pcmToSample']/24000,z)
            if z<=a:continue
            guide_word_frames.append((round((s['startFrame']/60+(p['outputSpeechFromSample']-p['pcmFromSample'])/24000+(a+z)/2)*60),p.get('guideId') or ('06-p2' if s['id']=='06' else '02-p4'),w['text']))
        for sample in [p['outputSpeechFromSample'],p['outputSpeechToSample']]:
            edge=s['startFrame']+round(sample/400)
            for delta in [-1,0,1]:guide_word_frames.append((edge+delta,p.get('guideId') or ('06-p2' if s['id']=='06' else '02-p4'),'guide-PCM-edge'))
state = {'schemaVersion': 1, 'startedAt': now(), 'pid': os.getpid(), 'sessionId': None,
    'status': 'CPU-local-all-actual-cue-and-native-boundary-trial-extraction', 'threads': 2,
    'activeTasks': [], 'processes': [], 'images': [], 'sheets': [], 'completedCuts': 0,
    'planSha256': sha(WORK / 'plan.json'), 'captionLayoutSha256': sha(WORK / 'caption-layout-v4.json'),
    'allCaptionPixelsReviewed': False, 'framingApproved': False, 'newGitImages': 0}

def save():
    session_file = DEST / 'session.json'
    if session_file.exists():
        session = read(session_file)
        if session['pid'] == state['pid']: state['sessionId'] = session['sessionId']
    state['updatedAt'] = now()
    write(DEST / 'execution.json', state)
    qpath = ROOT / 'production/batches/sakurai-planning-game-design/queue.json'
    q = read(qpath)
    item = next(i for i in q['items'] if i['slug'] == 'making-game-sequels')
    item['stage'] = 'current13-guided60-changed-native-cue-and-word-pixel-trials'
    item['execution'].update(observedAt=state['updatedAt'], phase=item['stage'], status=state['status'],
        pid=state['pid'], sessionId=state['sessionId'], alive='endedAt' not in state,
        activeTasks=state['activeTasks'], gpuSynthesisJobs=0,
        cpuProductionJobs=0 if 'endedAt' in state else 1, renderJobs=0, uploads=0,
        actualCueExtraction={'state': rel(DEST / 'execution.json'), 'completedCuts': state['completedCuts'],
                             'totalCuts': len(cuts), 'images': len(state['images'])})
    item['nextAction'] = 'Directly compare the changed guide words/caption intersections, new native edges and resource crops. Preserve all554.584s components and original six white explanations; final timing/new joins/mix/render remain pending.'
    item['updatedAt'] = state['updatedAt'];q['updatedAt'] = state['updatedAt'];write(qpath, q)
    cp = read(BASE / 'latest-checkpoint.json')
    cp.update(stage=item['stage'], updatedAt=state['updatedAt'], execution=item['execution'], nextAction=item['nextAction'])
    cp['actualCuePixelTrials'] = {'state': rel(DEST / 'execution.json'), 'completedCuts': state['completedCuts'],
        'images': len(state['images']), 'allDirectlyRead': False, 'finalApproved': False}
    write(BASE / 'latest-checkpoint.json', cp)

try:
    save()
    for c in cuts:
        media = next(x for x in compiled['cuts'] if x['id'] == c['id'])
        assert sha(ROOT / media['video']) == media['sha256']
        frames = {0: {'anchors': ['start'], 'cues': []}, c['frames'] // 2: {'anchors': ['middle'], 'cues': []},
                  c['frames'] - 1: {'anchors': ['last'], 'cues': []}}
        for row in layout['rows']:
            if row['segment'] != c['id']: continue
            f = row['localFrame']
            frames.setdefault(f, {'anchors': [], 'cues': []})['cues'].append(row['cue'])
        for g,gid,word in guide_word_frames:
            if c['startFrame']<=g<c['endFrameExclusive']:
                frames.setdefault(g-c['startFrame'],{'anchors':[],'cues':[]})['anchors'].append(gid+':'+word)
        if c.get('bankCutId') in [28,49]:
            for f in range(0,c['frames'],30):frames.setdefault(f,{'anchors':[],'cues':[]})['anchors'].append('crop-motion-half-second')
        crop_values = media['composition']['proposedCrop']
        x,y,w,h = crop_values
        crop = f'crop={w}:{h}:{x}:{y},' if crop_values != [0,0,1920,1080] else ''
        context = None
        label_filter = ''
        selection = '+'.join(f'eq(n\\,{f})' for f in sorted(frames))
        vf = f"{crop}scale=1920:1080,setsar=1,{label_filter}setpts=PTS+{c['startFrame']/60:.9f}/TB,subtitles=captions.ko.candidate.v4.ass,select='{selection}'"
        folder = DEST / c['id'];folder.mkdir()
        command = [FF, '-v', 'error', '-nostdin', '-threads', '2', '-filter_threads', '1', '-i', str(ROOT / media['video']),
            '-vf', vf, '-fps_mode', 'passthrough', '-frames:v', str(len(frames)), str(folder / 'sample-%03d.png')]
        log = folder / 'extraction.log'
        with log.open('wb') as fh:
            proc = subprocess.Popen(command, cwd=WORK, stdout=fh, stderr=fh,
                creationflags=subprocess.CREATE_NO_WINDOW)
            state['activeTasks'] = [{'kind': 'CPU-cue-pixel-trials', 'pid': proc.pid, 'log': rel(log), 'command': command}]
            save();code = proc.wait()
        state['processes'].append({'pid': proc.pid, 'exitCode': code, 'cut': c['id'], 'log': rel(log)})
        state['activeTasks'] = []
        assert code == 0 and not log.read_text(encoding='utf-8').strip(), c['id']
        files = sorted(folder.glob('sample-*.png'))
        assert len(files) == len(frames)
        for p, f in zip(files, sorted(frames)):
            state['images'].append({'path': rel(p), 'sha256': sha(p), 'cut': c['id'], 'localFrame': f,
                'globalFrame': c['startFrame'] + f, 'anchorRoles': frames[f]['anchors'], 'cueIds': frames[f]['cues'],
                'framingTrialFilter': crop or 'full', 'contextLabel': context,
                'directlyRead': False, 'finalApproved': False})
        state['completedCuts'] += 1;save()
    font = ImageFont.truetype('C:/Windows/Fonts/malgun.ttf', 23)
    for offset in range(0, len(state['images']), 6):
        subset = state['images'][offset:offset+6]
        sheet = Image.new('RGB', (1920, 1740), 'white');d = ImageDraw.Draw(sheet)
        for k, record in enumerate(subset):
            x, y = (k % 2) * 960, (k // 2) * 580
            with Image.open(ROOT / record['path']) as im:
                sheet.paste(im.resize((960, 540)), (x, y + 40))
            d.text((x+8, y+7), f'{offset+k+1:03d} {record["cut"]} n{record["localFrame"]} cue{record["cueIds"]}', font=font, fill='black')
        p = DEST / f'review-sheet-{offset//6+1:03d}.jpg'
        sheet.save(p, quality=94)
        state['sheets'].append({'path': rel(p), 'sha256': sha(p), 'imageIndices': list(range(offset+1, offset+len(subset)+1)), 'directlyRead': False})
    state.update(status='closed-local-cue-and-boundary-trials-awaiting-direct-review', endedAt=now(), exitCode=0)
    save();print(json.dumps({'pid': state['pid'], 'cuts': len(cuts), 'images': len(state['images']), 'sheets': len(state['sheets']), 'newGitImages': 0}))
except Exception:
    state.update(status='closed-cue-trial-extraction-failed', endedAt=now(), exitCode=1,
                 error=traceback.format_exc(), activeTasks=[])
    save();raise
