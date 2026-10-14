"""Prepare and extract provisional native crops, not final/composite pixels."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, subprocess
import psutil

ROOT = Path(__file__).resolve().parents[3]
FOLDER = ROOT / 'projects/game-lighting-history-04/production/local/part1-mobile-framing-v173'
STATE = FOLDER / 'execution.json'
SOURCE = ROOT / 'production/research/game-lighting-history/local/episode04-additional-action-v44/mobile-profile-shader-editor2024.mp4'
SOURCE_SHA = '507fa8459952670bbb0b298f4b251b5acd6877e32f877f412d50a51b58cec80e'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
if STATE.exists() or sha(SOURCE) != SOURCE_SHA:
    raise RuntimeError('Preserve extraction or changed source')
FOLDER.mkdir(parents=True, exist_ok=True)
me = psutil.Process()
rows = [
 dict(id='group', seconds=12, crop=[396,426,1120,630], scope='Texture preview and right group list. Original slide heading excluded.'),
 dict(id='compiler', seconds=140, crop=[396,360,1120,630], scope='One Android GLES compiler warning and other actual present entries. No zero-cost inference.'),
 dict(id='phone-rock', seconds=240, crop=[112,90,1600,900], scope='Game graph, HQ/LQ rock labels, moving character; outer rounded phone mask excluded. Right irrelevant button partly excluded.'),
 dict(id='phone-wall', seconds=281, crop=[632,364,1120,630], scope='Later phone inset to full screen. Presenter and conference frame excluded; same game graph and GBuffer Normals test wall retained.'),
 dict(id='profile-native', seconds=40, crop=None, scope='Native profile view for a separate precise crop.'),
 dict(id='lod-native', seconds=80, crop=None, scope='Native LOD group fields for a separate precise crop.'),
 dict(id='cvar-native', seconds=100, crop=None, scope='Native console policy fields for a separate precise crop.'),
 dict(id='phone-transition-native', seconds=267, crop=None, scope='Locate full-game to inset framing transition; never bridge mismatched crops as the same view.')
]
state = dict(startedAt=datetime.now(timezone.utc).isoformat(), worker=dict(pid=me.pid, createTime=me.create_time(), command=me.cmdline(), cwd=me.cwd()),
             source=dict(path=SOURCE.relative_to(ROOT).as_posix(), sha256=SOURCE_SHA), status='extracting-provisional-framing',
             cpuThreads=1, gpuJobs=0, results=[], localOnly=True, exactBoundariesApproved=False, allFinalPixelsReviewed=False, movingPixelReview=False)
def save():
    temp = STATE.with_name(STATE.name+'.writing-'+str(me.pid)); temp.write_text(json.dumps(state, ensure_ascii=False, indent=2)+'\n', 'utf-8'); os.replace(temp, STATE)
save()
try:
    for row in rows:
        out=FOLDER/(row['id']+'.png')
        command=['C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe','-hide_banner','-loglevel','error','-threads','1','-ss',str(row['seconds']),'-i',str(SOURCE)]
        if row['crop']:
            x,y,w,h=row['crop']; command += ['-vf',f'crop={w}:{h}:{x}:{y},scale=1920:1080,setsar=1','-filter_threads','1']
        command += ['-frames:v','1','-an','-threads','1','-n',str(out)]
        run=subprocess.run(command,cwd=ROOT,creationflags=subprocess.CREATE_NO_WINDOW,capture_output=True,text=True)
        if run.returncode: raise RuntimeError(run.stderr)
        state['results'].append({**row,'path':out.relative_to(ROOT).as_posix(),'sha256':sha(out),'command':command,'exitCode':0}); save()
    state.update(status='native-framing-samples-ready', endedAt=datetime.now(timezone.utc).isoformat(),exitCode=0); save()
    print('8 native samples local-only. Crop inspection is separate from moving and final encoded approval.')
except BaseException as exc:
    state.update(status='failed-preserving-local-samples',error=repr(exc),exitCode=1,endedAt=datetime.now(timezone.utc).isoformat());save();raise
