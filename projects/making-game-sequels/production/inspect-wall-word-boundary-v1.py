"""Inspect only the newly proposed wall-clause endpoint; preserve old samples."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, re, subprocess
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
STATE = BASE / 'wall-word-boundary-v1.json'
OUT = BASE / 'word-alignment-local/wall-end-v1'
assert not STATE.exists(), 'Reuse the completed targeted inspection.'
OUT.mkdir(parents=True, exist_ok=True)
source = ROOT / 'production/batches/sakurai-planning-game-design/proof-making-game-sequels/research-local/game-sources/MXxOg1xuWcI.mp4'
nums = [12748, 12749, 12750, 12760, 12766, 12769, 12770, 12771]
relative = lambda p: p.relative_to(ROOT).as_posix()
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
now = lambda: datetime.now(timezone.utc).isoformat()
state = {'schemaVersion': 1, 'pid': os.getpid(), 'startedAt': now(), 'status': 'extracting',
         'scope': 'Eight new native images around the proposed5.666667s wall excerpt, not a repeat of completed native extraction.',
         'source': relative(source), 'sourceSha256': sha(source), 'sourceFps': 30,
         'requestedNativeFrames': nums, 'gpuJobs': 0, 'cpuThreads': 2, 'newGitImages': 0,
         'finalIntervalApproved': False, 'allCaptionPixelsReviewed': False}
assert state['sourceSha256'] == '83ffc617ab1d5a005f235d3e584139789eeb96ed2758fc922f0ee5e39504024d'
def save():
    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    qpath = ROOT / 'production/batches/sakurai-planning-game-design/queue.json'
    q = json.loads(qpath.read_text('utf-8'))
    item = next(i for i in q['items'] if i['slug'] == 'making-game-sequels')
    item['execution'].update(phase='targeted-native-wall-word-boundary', pid=os.getpid(),
                             state=relative(STATE), alive=state['status']=='extracting',
                             cpuProductionJobs=int(state['status']=='extracting'),
                             gpuSynthesisJobs=0, renderJobs=0, uploads=0,
                             commandLine='python projects/making-game-sequels/production/inspect-wall-word-boundary-v1.py')
    item['nextAction'] = 'Directly inspect the eight new wall endpoints; then preserve current13 PCM in a word-aligned native candidate. Final timing and pixels remain pending.'
    q['updatedAt'] = now()
    qpath.write_text(json.dumps(q, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
save()
log = OUT / 'extract.log'
# Input seek begins at an exact native30fps second. showinfo verifies the
# relative PTS against every explicitly selected native frame.
expr = '+'.join(f'eq(n\\,{n-12600})' for n in nums)
with log.open('wb') as f:
    child = subprocess.Popen(['C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe',
        '-hide_banner', '-threads', '2', '-filter_threads', '1', '-ss', '420',
        '-i', str(source), '-t', '6', '-an', '-vf', f'select={expr},showinfo',
        '-vsync', '0', '-q:v', '2', str(OUT / 'native-%02d.jpg')],
        stdout=f, stderr=f, creationflags=subprocess.CREATE_NO_WINDOW)
    state['childPid'] = child.pid
    save()
    state['exitCode'] = child.wait()
assert state['exitCode'] == 0
files = sorted(OUT.glob('native-*.jpg'))
pts = [float(v) for v in re.findall(r'Parsed_showinfo[^\n]*?\bn:\s*\d+[^\n]*?pts_time:([\d.]+)', log.read_text('utf-8', errors='replace'))]
assert len(files) == len(nums) == len(pts)
assert all(abs(t-(n-12600)/30) < .00001 for n,t in zip(nums,pts))
state['images'] = [{'frame': n, 'pts': n/30, 'seekRelativePts': t,
                    'path': relative(p), 'sha256': sha(p)} for n,t,p in zip(nums,pts,files)]
sheet = Image.new('RGB', (2560, 776), '#eeeeee')
d = ImageDraw.Draw(sheet)
font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 22)
for k, r in enumerate(state['images']):
    x,y = (k%4)*640, (k//4)*388
    d.text((x+4,y+3), f"n{r['frame']} {r['pts']:.6f}s", font=font, fill='black')
    sheet.paste(Image.open(ROOT/r['path']).resize((640,360)), (x,y+28))
file = OUT / 'endpoints.jpg'
sheet.save(file, quality=95)
state.update(status='finished-awaiting-direct-eight-endpoint-review', endedAt=now(), childPid=None,
             sheets=[{'path': relative(file), 'sha256': sha(file), 'tiles': 8}],
             log=relative(log), localOnlyRaster=True)
save()
print(json.dumps({'pid': state['pid'], 'exitCode': state['exitCode'], 'images': len(files), 'sheets': 1}))
