"""Four local-only native stills for precise framing; no final approval."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, subprocess, sys
import psutil

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'projects/game-lighting-history-04/production'
FOLDER = BASE / 'local/part1-mobile-crop-v172'
STATE = FOLDER / 'execution.json'
SOURCE = ROOT / 'production/research/game-lighting-history/local/episode04-additional-action-v44/mobile-profile-shader-editor2024.mp4'
SOURCE_SHA = '507fa8459952670bbb0b298f4b251b5acd6877e32f877f412d50a51b58cec80e'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
stamp = lambda: datetime.now(timezone.utc).isoformat()
if STATE.exists():
    raise RuntimeError('Preserve existing extraction')
if sha(SOURCE) != SOURCE_SHA:
    raise RuntimeError('Native source changed')
me = psutil.Process()
state = dict(startedAt=stamp(), worker=dict(pid=me.pid, createTime=me.create_time(), command=me.cmdline(), cwd=me.cwd()),
             cpuThreads=1, gpuJobs=0, status='extracting-four-native-framing-stills', results=[],
             source=dict(path=SOURCE.relative_to(ROOT).as_posix(), sha256=SOURCE_SHA),
             allFinalPixelsReviewed=False, fourGamesApproved=False, localOnly=True)
FOLDER.mkdir(parents=True, exist_ok=True)
def save():
    temp = STATE.with_name(STATE.name + '.writing-' + str(me.pid))
    temp.write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n', 'utf-8')
    os.replace(temp, STATE)
save()
try:
    for name, seconds in [('editor-group', 12), ('compiler', 140), ('phone-full', 240), ('phone-inset', 281)]:
        output = FOLDER / (name + '.png')
        if output.exists():
            raise RuntimeError('Preserve existing still')
        command = ['C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe', '-hide_banner', '-loglevel', 'error',
                   '-threads', '1', '-ss', str(seconds), '-i', str(SOURCE), '-frames:v', '1',
                   '-an', '-threads', '1', '-n', str(output)]
        run = subprocess.run(command, cwd=ROOT, creationflags=subprocess.CREATE_NO_WINDOW, capture_output=True, text=True)
        if run.returncode:
            raise RuntimeError(run.stderr)
        state['results'].append(dict(label=name, seconds=seconds, path=output.relative_to(ROOT).as_posix(), sha256=sha(output), command=command, exitCode=0))
        save()
    state.update(status='four-native-framing-stills-ready', endedAt=stamp(), exitCode=0)
    save()
    print('4 native1920x1080 stills, local-only, no gameplay/final pixel approval')
except BaseException as exc:
    state.update(status='failed-preserve-existing', endedAt=stamp(), exitCode=1, error=repr(exc)); save(); raise
