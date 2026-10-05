"""Measure12 newly reviewed sequel scenes on CPU; preserve external GPU training. No final approval."""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
SLUG = 'making-game-sequels'
NODE = 'C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
QUEUE = ROOT / 'production/batches/sakurai-planning-game-design/queue.json'
PROOF = ROOT / 'production/batches/sakurai-planning-game-design/proof-making-game-sequels'
STATE = BASE / 'narration-tts-execution.json'
LOG = BASE / 'narration-tts.log'
SCENES = [f'{i:02}' for i in range(1, 13)]
EXPLANATIONS = ['01', '03', '05', '07', '09', '11']


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def save(path, value):
    temporary = path.with_name(path.name + f'.{os.getpid()}.writing')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temporary.replace(path)


subprocess.run([NODE, 'scripts/review-video-duplicates.cjs', SLUG, '--check'], cwd=ROOT, check=True)
review = read(BASE / 'script-source-review.json')
for source in review['inputs']:
    if sha(ROOT / source['path']) != source['sha256']:
        raise RuntimeError('Stale text/source review: ' + source['path'])
manifest = read(BASE.parent / 'project.json')
if not manifest['editing']['openingOverview']['fullBodyPromiseReviewComplete']:
    raise RuntimeError('Whole overview promises must be reviewed before synthesis')
if manifest['tts']['reference'] != 'shared/voice-reference/reference-15-35s.wav':
    raise RuntimeError('Preserve the approved voice reference')
if manifest['tts']['model'] != 'qwen3-tts/models/Qwen3-TTS-12Hz-1.7B-Base':
    raise RuntimeError('Preserve the approved model')
if STATE.exists():
    previous = read(STATE)
    if previous.get('generationCompleted'):
        raise RuntimeError('Completed PCM must be preserved; review it rather than rerun')
    raise RuntimeError('Inspect prior execution and surviving files before resuming')
gpu = subprocess.run(['nvidia-smi', '--query-gpu=memory.used,utilization.gpu', '--format=csv,noheader,nounits'], capture_output=True, text=True, check=True)
memory, utilization = [int(x.strip()) for x in gpu.stdout.strip().split(',')]
# CPU-only synthesis preserves live external GPU training, regardless of utilization.

state = {
    'schemaVersion': 1, 'pid': os.getpid(), 'sessionId': None, 'startedAt': now(),
    'status': 'loading-approved-qwen-model-on-CPU', 'scope': SCENES,
    'scriptInputs': review['inputs'], 'referenceSha256': sha(ROOT / manifest['tts']['reference']),
    'referenceTextSha256': sha(ROOT / manifest['tts']['referenceText']),
    'model': manifest['tts']['model'], 'device': 'cpu', 'log': LOG.relative_to(ROOT).as_posix(),
    'gpuBeforeLaunch': {'memoryUsedMiB': memory, 'utilizationPercent': utilization, 'usedByThisWorker': False},
    'externalGpuTrainingPreserved': True,
    'renderedScenes': [], 'gpuJobs': 0, 'cpuJobs': 1, 'cpuThreads': 8, 'generationCompleted': False,
    'finalVideoComplete': False, 'fullNarrationApproved': False, 'wholeAsrReview': False,
    'heuristicIsApproval': False,
    'nextAction': 'Measure12 scene PCM; directly compare all48 current-hash paragraphs with full ASR and independent ambiguous contexts. Preserve explanation PCM and secure more unique related actions as needed before final60:40/caption approval.'
}


def checkpoint():
    state['updatedAt'] = now()
    launch = BASE / 'narration-tts-session.json'
    if launch.exists():
        session = read(launch)
        if session.get('pid') == os.getpid():
            state['sessionId'] = session.get('sessionId')
    save(STATE, state)
    q = read(QUEUE)
    item = next(x for x in q['items'] if x['slug'] == SLUG)
    previous = item.get('execution', {})
    if previous.get('pid') != os.getpid():
        item.setdefault('executionHistory', []).append(previous)
    execution = dict(previous)
    execution.update(phase='reviewed-source-first-narration-measurement', status=state['status'],
                     pid=os.getpid(), sessionId=state['sessionId'], alive=state['cpuJobs'] > 0,
                     state=STATE.relative_to(ROOT).as_posix(), log=state['log'],
                     activeTasks=[] if state['cpuJobs'] == 0 else [{'kind': 'qwen-scene-context-TTS', 'pid': os.getpid(), 'sessionId': state['sessionId'], 'scenes': SCENES}],
                     gpuSynthesisJobs=0, cpuProductionJobs=state['cpuJobs'], renderJobs=0, uploads=0,
                     newNarrationCreated=bool(state['renderedScenes']), observedAt=now())
    item['stage'] = 'reviewed-narration-measurement-and-independent-scenes'
    item['execution'] = execution
    item['narrationMeasurement'] = {'state': STATE.relative_to(ROOT).as_posix(), 'renderedScenes': state['renderedScenes'], 'generationCompleted': state['generationCompleted'], 'wholeAsrReview': False}
    item['checkpoints']['narration'] = False
    item['nextAction'] = state['nextAction']
    item['updatedAt'] = now()
    save(QUEUE, q)
    for path in [BASE / 'latest-checkpoint.json', PROOF / 'latest-checkpoint.json']:
        checkpoint_value = read(path)
        checkpoint_value.update(stage=item['stage'], execution=execution, nextAction=state['nextAction'], updatedAt=now(), narrationMeasurement=item['narrationMeasurement'], ttsStarted=True, narrationApproved=False)
        save(path, checkpoint_value)


checkpoint()
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
            found = re.match(r'Rendered (\d+)-scene ', line)
            if found and found.group(1) not in state['renderedScenes']:
                state['renderedScenes'].append(found.group(1))
                checkpoint()
        return len(text)

    def flush(self):
        original_stdout.flush()
        self.file.flush()


with LOG.open('a', encoding='utf-8') as log:
    sys.stdout = Tee(log)
    sys.stderr = sys.stdout
    try:
        sys.path.insert(0, str(ROOT / 'qwen3-tts'))
        import render_narration as rn
        rn.configure_project(SLUG)
        rn.INFERENCE_DEVICE = 'cpu'
        rn.load_tts_dependencies()
        items = rn.build_render_items(rn.load_jobs())
        if [i.key.split('-')[0] for i in items] != SCENES:
            raise RuntimeError('Expected12 independent scene contexts')
        state['status'] = 'synthesizing-reviewed-narration'
        checkpoint()
        rn.render_chunks(items, batch_size=1)
        for source in review['inputs']:
            if sha(ROOT / source['path']) != source['sha256']:
                raise RuntimeError('Locked synthesis input changed during generation: ' + source['path'])
        measured = []
        for item in items:
            audio, rate = rn._read_mono(item.path)
            measured.append({'scene': item.key.split('-')[0], 'path': item.path.relative_to(ROOT).as_posix(),
                             'sha256': sha(item.path), 'frames': len(audio), 'sampleRate': rate,
                             'seconds': len(audio) / rate, 'text': item.text,
                             'tailRatio': rn._tail_ratio(audio, rate), 'tailDecayMs': rn._tail_decay_ms(audio, rate),
                             'fullAsrReview': False, 'humanListening': 'pending'})
        explanation = sum(m['seconds'] for m in measured if m['scene'] in EXPLANATIONS)
        actual = sum(m['seconds'] for m in measured if m['scene'] not in EXPLANATIONS)
        state.update(status='finished-awaiting-full-current-hash-ASR', endedAt=now(), gpuJobs=0, cpuJobs=0,
                     exitCode=0, generationCompleted=True, measurements=measured,
                     explanationSpeechSeconds=explanation, actualSpeechSeconds=actual,
                     minimumActualSecondsAt60_40=1.5 * explanation,
                     candidateSourceSeconds=manifest['editing']['plannedCandidateActualSeconds'])
        save(BASE / 'narration-speech-measurements.json', state)
        checkpoint()
        print(json.dumps({'status': state['status'], 'explanationSpeechSeconds': explanation, 'actualSpeechSeconds': actual, 'minimumActualSeconds': 1.5 * explanation}), flush=True)
    except BaseException:
        state.update(status='failed', endedAt=now(), gpuJobs=0, cpuJobs=0, exitCode=1, error=traceback.format_exc())
        checkpoint()
        traceback.print_exc()
        raise
    finally:
        sys.stdout, sys.stderr = original_stdout, original_stderr
