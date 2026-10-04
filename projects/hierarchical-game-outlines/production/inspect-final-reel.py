"""Inspect measured explanation reel and every proposed final PPT caption placement."""
from pathlib import Path
import json, hashlib, subprocess, os
from datetime import datetime, timezone
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
WORK = ROOT / 'projects/hierarchical-game-outlines/production/final-v1'
OUT = WORK / 'explanation-pixel-review-v1'
FF = 'C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
PROBE = 'C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe'
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
plan = read(WORK / 'plan.json')
reel = ROOT / 'shared/output/motion-canvas/hierarchical-game-outlines-explanation-reel.mp4'
result = read(WORK / 'explanation-render-result.json')
assert result['done'] and result['result'] == 0 and not result['errors']
assert not OUT.exists(), 'Inspect existing reel review.'
OUT.mkdir()
def state(status, count, exit_code=None):
    (WORK / 'explanation-pixel-execution.json').write_text(json.dumps({'pid': os.getpid(), 'status': status,
        'images': count, 'updatedAt': datetime.now(timezone.utc).isoformat(), 'exitCode': exit_code}, indent=2) + '\n', encoding='utf-8')
state('running', 0)
probe = subprocess.run([PROBE, '-v', 'error', '-show_streams', '-of', 'json', str(reel)], capture_output=True)
assert probe.returncode == 0 and not probe.stderr
streams = json.loads(probe.stdout)['streams']
assert len(streams) == 1
video = streams[0]
assert (video['width'], video['height'], video['avg_frame_rate'], int(video['nb_frames'])) == (1920,1080,'60/1',plan['explanationReelFrames'])
decode = subprocess.run([FF, '-v', 'error', '-xerror', '-threads', '2', '-i', str(reel), '-f', 'null', '-'], capture_output=True)
(OUT / 'whole-decode.log').write_bytes(decode.stdout + decode.stderr)
assert decode.returncode == 0 and not decode.stderr
font = ImageFont.truetype('C:/Windows/Fonts/malgun.ttf', 20)
scenes = {s['id']: s for s in plan['scenes']}
def capture(name, reel_time, global_time=None):
    file = OUT / f'{name}.png'
    command = [FF, '-v', 'error', '-threads', '2', '-ss', str(reel_time), '-i', str(reel)]
    if global_time is not None:
        command += ['-vf', f'setpts=PTS+{global_time}/TB,ass=projects/hierarchical-game-outlines/production/final-v1/captions.ko.ass']
    command += ['-frames:v', '1', str(file)]
    r = subprocess.run(command, capture_output=True)
    assert r.returncode == 0 and not r.stderr, (name, r.stderr)
    return file.relative_to(ROOT).as_posix()
def sheets(rows, kind):
    pages = []
    for first in range(0, len(rows), 12):
        im = Image.new('RGB', (1920, 1580), 'white')
        d = ImageDraw.Draw(im)
        for j, row in enumerate(rows[first:first+12]):
            x, y = (j % 3)*640, (j // 3)*395
            im.paste(Image.open(ROOT / row['file']).convert('RGB').resize((640,360)), (x,y))
            d.text((x+5,y+363), row['label'], font=font, fill='black')
        p = OUT / f'{kind}-{first//12+1:02}.jpg'
        im.save(p, quality=95)
        pages.append(p.relative_to(ROOT).as_posix())
    return pages
captions = []
for c in read(WORK / 'caption-layout-qa.json')['cues']:
    if c['cut'] is not None:
        continue
    scene = scenes[c['scene']]
    global_time = (c['start'] + c['end'])/2
    reel_time = scene['reelStart'] + global_time - scene['start']
    captions.append({'cue': c['cue'], 'scene': c['scene'], 'globalTime': global_time,
        'reelTime': reel_time, 'label': f"Cue {c['cue']} / scene{c['scene']}",
        'file': capture(f"cue-{c['cue']}", reel_time, global_time)})
    state('running', len(captions))
assert len(captions) == 50
composition = [{'label': 'Original cat intro / 1.65s', 'file': capture('intro', 1.65)}]
for scene in plan['scenes']:
    if scene['classification'] == 'explanation':
        for ratio in [.08,.5,.92]:
            name=f"scene{scene['id']}-{ratio}"
            composition.append({'label': f"Scene{scene['id']} / phase {ratio}",
                'file': capture(name,scene['reelStart']+scene['seconds']*ratio)})
composition.append({'label': 'Original member identities / 10-second outro',
                    'file': capture('outro', 2+plan['explanationSeconds']+5)})
index = {'reel': reel.relative_to(ROOT).as_posix(), 'reelSha256': sha(reel), 'frames': plan['explanationReelFrames'],
    'audioStreams': 0, 'wholeDecodeExitCode': 0, 'captions': captions, 'composition': composition,
    'captionPages': sheets(captions,'captions'), 'compositionPages': sheets(composition,'composition'),
    'assSha256': sha(WORK/'captions.ko.ass'), 'directReview': 'pending', 'finalVideoApproved': False}
(OUT / 'index.json').write_text(json.dumps(index, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
state('finished', len(captions)+len(composition), 0)
print(json.dumps({'captionViews':len(captions), 'compositionViews':len(composition), 'decodeExitCode':0}))
