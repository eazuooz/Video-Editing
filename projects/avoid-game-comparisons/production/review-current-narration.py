"""CPU whole-scene readback evidence; direct script review is a separate gate."""
from __future__ import annotations

import hashlib
import json
import os
import re
import runpy
import subprocess
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
SLUG = 'avoid-game-comparisons'
STATE = BASE / 'narration-asr-execution.json'
LOG = BASE / 'narration-asr.log'
QUEUE = ROOT / 'production/batches/sakurai-planning-game-design/queue.json'
PROOF = ROOT / 'production/batches/sakurai-planning-game-design/proof-avoid-game-comparisons'
NODE = 'C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'


def now():
    return datetime.now(timezone.utc).isoformat()


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    temporary = path.with_name(path.name + f'.{os.getpid()}.writing')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temporary.replace(path)


tts = read(BASE / 'narration-tts-execution.json')
if not tts.get('generationCompleted') or tts.get('exitCode') != 0:
    raise RuntimeError('Finish current synthesis and inspect its actual state before readback')
alive = subprocess.run(['powershell', '-NoProfile', '-Command',
                       f'Get-CimInstance Win32_Process -Filter "ProcessId={tts["pid"]}" | Select-Object -ExpandProperty CommandLine'],
                       capture_output=True, text=True)
if 'render-reviewed-narration.py' in alive.stdout:
    raise RuntimeError('Synthesis runner remains alive; finish its actual session first')
if STATE.exists():
    raise RuntimeError('Read actual ASR execution/caches before continuing; do not duplicate it')
subprocess.run([NODE, 'scripts/review-video-duplicates.cjs', SLUG, '--check'], cwd=ROOT, check=True)
review = read(BASE / 'script-source-review.json')
for source in review['inputs']:
    if sha(ROOT / source['path']) != source['sha256']:
        raise RuntimeError('Stale locked narration/source input: ' + source['path'])
for m in tts['measurements']:
    if sha(ROOT / m['path']) != m['sha256']:
        raise RuntimeError('Measured PCM changed before readback: ' + m['scene'])
state = {'schemaVersion': 1, 'pid': os.getpid(), 'sessionId': None,
         'startedAt': now(), 'status': 'loading-local-whisper-CPU', 'device': 'cpu',
         'gpuJobs': 0, 'cpuJobs': 1, 'log': LOG.relative_to(ROOT).as_posix(),
         'scriptInputs': review['inputs'], 'audioInputs': tts['measurements'],
         'readbackComplete': False, 'wholeDirectScriptReview': False,
         'humanWholeListening': 'pending', 'finalVideoComplete': False,
         'nextAction': 'Directly compare every current-hash readback against all50 KO paragraphs; independently transcribe ambiguous contexts before narration approval. Preserve useful explanation PCM and acquire more unique relevant actions.'}


def checkpoint():
    state['updatedAt'] = now()
    launch = BASE / 'narration-asr-session.json'
    if launch.exists():
        s = read(launch)
        if s.get('pid') == os.getpid():
            state['sessionId'] = s['sessionId']
    save(STATE, state)
    q = read(QUEUE)
    item = next(i for i in q['items'] if i['slug'] == SLUG)
    previous = item.get('execution', {})
    if previous.get('pid') != os.getpid():
        item.setdefault('executionHistory', []).append(previous)
    execution = dict(previous)
    secondary = execution.get('secondaryTasks', [])
    execution.update(phase='current-hash-full-narration-ASR', status=state['status'],
                     pid=os.getpid(), sessionId=state['sessionId'], alive=state['cpuJobs'] > 0,
                     state=STATE.relative_to(ROOT).as_posix(), log=state['log'],
                     activeTasks=[] if state['cpuJobs'] == 0 else [{'kind': 'full-scene-CPU-ASR', 'pid': os.getpid(), 'sessionId': state['sessionId'], 'scenes': 12}],
                     gpuSynthesisJobs=0, primaryCpuProductionJobs=state['cpuJobs'],
                     cpuProductionJobs=state['cpuJobs'] + sum(x.get('kind') == 'full-decode' for x in secondary),
                     renderJobs=0, uploads=0, observedAt=now())
    item['stage'] = 'current-PCM-full-ASR-and-additional-native-actions'
    item['execution'] = execution
    item['narrationReadback'] = {'state': STATE.relative_to(ROOT).as_posix(), 'readbackComplete': state['readbackComplete'], 'wholeDirectScriptReview': False}
    item['checkpoints']['narration'] = False
    item['nextAction'] = state['nextAction']
    item['updatedAt'] = now()
    save(QUEUE, q)
    for path in [BASE / 'latest-checkpoint.json', PROOF / 'latest-checkpoint.json']:
        v = read(path)
        v.update(stage=item['stage'], execution=execution, narrationReadback=item['narrationReadback'], nextAction=state['nextAction'], updatedAt=now())
        save(path, v)


original_stdout, original_stderr = sys.stdout, sys.stderr


class Tee:
    def __init__(self, file):
        self.file = file
        self.buffer = ''

    def write(self, text):
        original_stdout.write(text)
        original_stdout.flush()
        self.file.write(text)
        self.file.flush()
        self.buffer += text
        while '\n' in self.buffer:
            line, self.buffer = self.buffer.split('\n', 1)
            found = re.match(r'Transcribing scene (\d+)', line)
            if found:
                state['status'] = 'transcribing-current-scene-' + found.group(1)
                checkpoint()
        return len(text)

    def flush(self):
        original_stdout.flush()
        self.file.flush()


checkpoint()
with LOG.open('a', encoding='utf-8') as log:
    sys.stdout = Tee(log)
    sys.stderr = sys.stdout
    try:
        sys.argv = ['review_project_narration.py', '--project', SLUG, '--device', 'cpu']
        runpy.run_path(str(ROOT / 'qwen3-tts/review_project_narration.py'), run_name='__main__')
        for m in tts['measurements']:
            if sha(ROOT / m['path']) != m['sha256']:
                raise RuntimeError('PCM changed during readback: ' + m['scene'])
        manifest = read(BASE.parent / 'project.json')
        report_path = ROOT / manifest['tts']['outputDir'] / (manifest['tts']['filenameStem'] + '.asr-review.json')
        report = read(report_path)
        if not report['complete'] or report['sceneCount'] != 12:
            raise RuntimeError('Full12-scene current readbacks were not generated')
        state.update(status='finished-awaiting-direct-full-script-and-context-review',
                     cpuJobs=0, endedAt=now(), exitCode=0, readbackComplete=True,
                     report=report_path.relative_to(ROOT).as_posix(), reportSha256=sha(report_path))
        checkpoint()
        print('Full12-scene evidence generated; direct review and human listening remain separate.', flush=True)
    except BaseException:
        state.update(status='failed', cpuJobs=0, endedAt=now(), exitCode=1, error=traceback.format_exc())
        checkpoint()
        traceback.print_exc()
        raise
    finally:
        sys.stdout, sys.stderr = original_stdout, original_stderr
