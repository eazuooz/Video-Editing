"""Verify the once-rendered, measured eight guide sources; never approve pixels.

Original eight white sources and all voice PCM remain untouched. A single
terminal display-frame excess is corrected from decoded display order only.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse, ctypes, hashlib, json, os, shutil, subprocess, sys, time, traceback

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
STATE = BASE/'observation-guide-white-verification-v1.json'
SESSION = STATE.with_name(STATE.stem+'.session.json')
OUT = ROOT/'shared/output/player-customization/observation-guides-white-v1'
RAW = OUT/'player-customization-observation-guides-v1.mp4'
EXACT = OUT/'player-customization-observation-guides-v1.exact.mp4'
FF = 'C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
PROBE = 'C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
rel = lambda p: p.relative_to(ROOT).as_posix()
now = lambda: datetime.now(timezone.utc).isoformat()

def save(p, value):
    temp = p.with_name(p.name+f'.{os.getpid()}.writing')
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n','utf-8')
    for n in range(40):
        try: os.replace(temp,p); return
        except OSError:
            if n == 39: raise
            time.sleep(.15)

parser = argparse.ArgumentParser()
parser.add_argument('--resource', required=True)
args = parser.parse_args()
assert not STATE.exists() and not EXACT.exists(), 'Resume actual existing verification; do not repeat.'
resource = read(ROOT/args.resource)
assert resource['ownHeavyJobs'] == 0 and resource['cpuLoadPercent'] < 85
assert resource['freePhysicalMemoryKiB'] > 16_000_000
assert (datetime.now(timezone.utc)-datetime.fromisoformat(resource['observedAt'].replace('Z','+00:00'))).total_seconds() < 240
render = read(BASE/'observation-guides-white-render-execution-v1.json')
assert render['guiReturnedObserved'] and render['encoderAbsentObserved']
timing_path = ROOT/'motion-canvas/src/projects/player-customization/observation-guide-timing-measured-v1.json'
timing = read(timing_path)
review = read(BASE/'observation-guide-contexts-asr-direct-review-v2.json')
assert review['allCompleteContextsTextCompared'] and review['guideCurrentVoiceTextIntegrityApproved']
assert len(timing['rows']) == 8 and all(row['measured'] for row in timing['rows'])
planned = sum(row['frames'] for row in timing['rows'])
assert planned == render['plannedFrames']
original = read(BASE/'current-reviewed-original-white-inputs-v2.json')
protected = read(BASE/'observation-guides-tts-request-v1.json')['protectedInputs']
# The manifest may now carry measured metadata; immutable authored voice/content
# and the original white input set are still required to match.
for row in protected:
    if row['path'].endswith('/project.json'): continue
    assert sha(ROOT/row['path']) == row['sha256'], row['path']
if os.name == 'nt': ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x00004000)
state = dict(schemaVersion=1, slug='player-customization', pid=os.getpid(),
    commandLine=[sys.executable,*sys.argv], sessionId=None, startedAt=now(),
    status='verifying-eight-measured-guide-white-sources', cpuThreads=2, gpu=0,
    singleJob=True, resourceEvidence=args.resource, measuredTimingPath=rel(timing_path),
    measuredTimingSha256=sha(timing_path), operations=[], exitCode=None,
    sourceWhiteAnimatedPixelsApproved=False, allFinalPixelsReviewed=False,
    narrationApproved=False, finalVideoComplete=False)

def checkpoint():
    if SESSION.exists():
        launch = read(SESSION)
        if launch['pid'] == os.getpid(): state.update(sessionId=launch['sessionId'],processIdentity=launch['processIdentity'])
    state['updatedAt'] = now(); save(STATE,state)
    job = dict(status=state['status'],pid=os.getpid(),commandLine=state['commandLine'],
        sessionId=state['sessionId'],processIdentity=state.get('processIdentity'),state=rel(STATE),
        cpuThreads=2,gpu=0,singleJob=True,exitCode=state['exitCode'],workerExpectedRunning=state['exitCode'] is None)
    cp = read(BASE/'latest-checkpoint.json')
    cp.update(recordedAt=now(),stage=state['status'],ownedJob=job,
        nextAction='Read all32 paragraphs at128 actual motion samples/32 boards. Preserve original eight white sources/voice. Final source allocation, caption pixels, mixed ASR, pair QA, collection and private upload remain pending.')
    save(BASE/'latest-checkpoint.json',cp)
    qp = ROOT/'production/batches/sakurai-planning-game-design/queue.json'; q = read(qp)
    item = next(i for i in q['items'] if i['slug'] == 'player-customization')
    item.update(stage=cp['stage'],currentExecution=job,nextAction=cp['nextAction'])
    q['updatedAt'] = now(); save(qp,q)

def run(name, command):
    op = dict(name=name,commandLine=command,startedAt=now())
    state['operations'].append(op); state['status'] = name; checkpoint()
    p = subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    op['pid'] = p.pid; checkpoint(); output,error = p.communicate()
    op.update(exitCode=p.returncode,finishedAt=now())
    (OUT/(name+'.stderr.log')).write_bytes(error); checkpoint()
    assert p.returncode == 0, error.decode('utf-8','replace')
    return output

try:
    checkpoint()
    probe_command = [PROBE,'-v','error','-show_entries','stream=codec_type,width,height,r_frame_rate,time_base,duration,nb_frames','-of','json']
    raw_probe = json.loads(run('probe-actual-guide-render',probe_command+[str(RAW)]))
    assert len(raw_probe['streams']) == 1
    video = raw_probe['streams'][0]
    assert video['codec_type'] == 'video' and video['width'] == 1920 and video['height'] == 1080
    assert video['r_frame_rate'] == '60/1' and video['time_base'] == '1/90000'
    raw_frames = int(video['nb_frames']); assert raw_frames in [planned,planned+1]
    state['rawRender'] = dict(path=rel(RAW),sha256=sha(RAW),probe=raw_probe,
        guiReturnedObserved=True,encoderAbsentObserved=True,encoderExitCodeObserved=render.get('encoderExitCodeObserved',False))
    if raw_frames == planned:
        shutil.copy2(RAW,EXACT)
        state['endpointAdjustment'] = dict(extraFrames=0,videoReencoded=False)
    else:
        run('trim-one-terminal-guide-display-frame',[FF,'-nostdin','-v','error','-threads','2','-i',str(RAW),
            '-map','0:v:0','-an','-vf',f'trim=end_frame={planned},setpts=N/(60*TB)','-frames:v',str(planned),
            '-c:v','libx264','-threads','2','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-r','60',
            '-video_track_timescale','90000','-movflags','+faststart',str(EXACT)])
        state['endpointAdjustment'] = dict(extraFrames=1,videoReencoded=True,decodedDisplayOrder=True,audioChanged=False)
    probe = json.loads(run('probe-exact-guide-white',probe_command+[str(EXACT)]))
    assert int(probe['streams'][0]['nb_frames']) == planned
    assert probe['streams'][0]['time_base'] == '1/90000'
    all_frames = json.loads(run('probe-all-guide-white-pts',[PROBE,'-v','error','-threads','2','-select_streams','v:0',
        '-show_frames','-show_entries','frame=best_effort_timestamp','-of','json',str(EXACT)]))['frames']
    pts = [int(f['best_effort_timestamp']) for f in all_frames]
    assert pts == list(range(0,planned*1500,1500))
    run('whole-exact-guide-white-decode',[FF,'-nostdin','-v','error','-threads','2','-i',str(EXACT),'-an','-f','null','-'])
    samples,offset = [],0
    for row in timing['rows']:
        for pi,(a,b) in enumerate(zip(row['paragraphStarts'],row['paragraphStarts'][1:]+[row['durationSeconds']]),1):
            window = min(2.7,b-a-.1)
            assert window > 0
            local = [a+.08,a+window*.5,a+window*.95,max(a+.09,b-.15)]
            for phase,t in zip(['onset','moving','arrival','late'],local):
                frame = min(offset+row['frames']-1,offset+round(t*60))
                samples.append(dict(scene=row['id'],paragraph=pi,phase=phase,frame=frame))
        offset += row['frames']
    assert offset == planned and len(samples) == len({s['frame'] for s in samples}) == 128
    native,boards = OUT/'motion-qa-native',OUT/'motion-qa-boards'; native.mkdir(); boards.mkdir()
    expression = '+'.join(f'eq(n,{s["frame"]})' for s in samples)
    run('extract128-guide-motion-samples',[FF,'-nostdin','-v','error','-threads','2','-i',str(EXACT),
        '-vf',f"select='{expression}'",'-fps_mode','vfr','-an','-threads','2',str(native/'frame-%03d.png')])
    from PIL import Image, ImageDraw, ImageFont
    font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf',21); board_rows = []
    for i,s in enumerate(samples,1): s.update(path=rel(native/f'frame-{i:03d}.png'),sha256=sha(native/f'frame-{i:03d}.png'))
    for i,start in enumerate(range(0,128,4),1):
        board = Image.new('RGB',(1920,1170),'white'); drawing = ImageDraw.Draw(board); group = samples[start:start+4]
        for j,s in enumerate(group):
            x,y = j%2*960,j//2*585
            drawing.text((x+8,y+6),f'{s["scene"]} p{s["paragraph"]} {s["phase"]} frame{s["frame"]}',fill='black',font=font)
            im = Image.open(ROOT/s['path']).convert('RGB'); im.thumbnail((960,540)); board.paste(im,(x,y+45))
        path = boards/f'board-{i:02d}.png'; board.save(path)
        board_rows.append(dict(path=rel(path),sha256=sha(path),entries=group))
    state.update(status='eight-guide-white-source-verified-awaiting-direct-motion-review',exitCode=0,finishedAt=now(),
        currentWhite=dict(path=rel(EXACT),sha256=sha(EXACT),probe=probe,frames=planned,firstPts=0,
            lastPts=(planned-1)*1500,allPtsContiguous1500=True,wholeDecodeExitCode=0),
        originalEightWhiteInputSetPreserved=dict(path=rel(BASE/'current-reviewed-original-white-inputs-v2.json'),
            sha256=sha(BASE/'current-reviewed-original-white-inputs-v2.json')),
        samplePlan=samples,boards=board_rows,allOriginalVoicePcmPreserved=True,newGitImages=0)
    checkpoint()
    print(json.dumps(dict(frames=planned,decode=0,pts=True,samples=128,boards=32,pixelsApproved=False)),flush=True)
except BaseException:
    state.update(status='failed-guide-white-verification',exitCode=1,error=traceback.format_exc(),finishedAt=now())
    checkpoint(); raise
