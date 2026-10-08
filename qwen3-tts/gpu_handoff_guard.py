"""Keep concurrent video narration outside another batch's exclusive GPU lease."""
import json
from pathlib import Path
import subprocess
import sys
import time
import atexit
import os
import uuid

ROOT = Path(__file__).resolve().parents[1]
ENTRYPOINT_ARGUMENTS = list(sys.argv)


def check_gpu_handoff(project, device, dry_run=False):
    if dry_run or not str(device).startswith('cuda'):
        return
    lease = ROOT / 'shared/output/GPU_HANDOFF.json'
    if not lease.exists():
        return
    state = json.loads(lease.read_text(encoding='utf-8-sig'))
    import psutil
    me = psutil.Process()
    ancestors = [me, *me.parents()]
    owner = state.get('coordinator', {})
    owned = any(p.pid == owner.get('pid') and
                abs(p.create_time() - owner.get('createTime', 0)) < .01
                for p in ancestors)
    if project == state.get('project') and owned and state.get('state') in ('gpu_granted_to_tts', 'tts_running'):
        return
    raise SystemExit('GPU is reserved for a cooperative training/TTS handoff. Preserve this narration checkpoint and wait for the lease to finish.')


def schedule_gpu_handoff(project, device, dry_run=False):
    """Serialize shared Qwen entrypoints and use the inspected research queue.

    The child launched by the lease coordinator is allowed through exactly once.
    Other callers wait without allocating a model. Unknown GPU work is retained;
    no arbitrary process is killed or restarted from guessed checkpoint support.
    """
    if dry_run or not str(device).startswith('cuda'):
        return
    import psutil
    lease = ROOT / 'shared/output/GPU_HANDOFF.json'
    announced = False
    while lease.exists():
        try:
            check_gpu_handoff(project, device)
            return
        except SystemExit:
            state = json.loads(lease.read_text(encoding='utf-8-sig'))
            owner = state.get('coordinator')
            if owner:
                try:
                    running = abs(psutil.Process(owner['pid']).create_time() - owner['createTime']) < .01
                except psutil.NoSuchProcess:
                    running = False
                if not running:
                    raise SystemExit('The GPU handoff owner exited unexpectedly. Inspect its saved state and restore the original queue before retrying; do not delete an unknown lease.')
            if not announced:
                print('Waiting for the current exclusive GPU TTS handoff.', flush=True)
                announced = True
            time.sleep(10)
    queue_dir = Path(r'C:/Users/eazuo/renderformer/tmp/placement_focus_20261008')
    status_path = queue_dir / 'status.json'
    if status_path.exists():
        state = json.loads(status_path.read_text(encoding='utf-8-sig'))
        try:
            owner = psutil.Process(state['owner_pid'])
            supported = 'placement_focus' in ' '.join(owner.cmdline())
        except (KeyError, psutil.NoSuchProcess):
            supported = False
        if supported:
            # Original argv keeps force-scene/alternate-manifest options intact.
            command = [sys.executable, '-X', 'utf8', str(ROOT / 'production/batches/game-math-part2-full-series/gpu-handoff.py'),
                       '--project', project, '--queue-dir', str(queue_dir), '--',
                       sys.executable, '-X', 'utf8', *ENTRYPOINT_ARGUMENTS]
            raise SystemExit(subprocess.call(command, cwd=ROOT, creationflags=subprocess.CREATE_NO_WINDOW))
    raw = subprocess.check_output(['nvidia-smi', '--query-gpu=memory.free,utilization.gpu',
                                  '--format=csv,noheader,nounits'], text=True,
                                 creationflags=subprocess.CREATE_NO_WINDOW)
    free, util = map(int, raw.splitlines()[0].replace(' ', '').split(','))
    if free < 18000 or util >= 15:
        raise SystemExit('Unregistered GPU work is active. Inspect its safe completion/resume interface before GPU TTS; current work was preserved.')
    # Idle GPU entrypoints also serialize, including calls outside this batch.
    # Keep ownership until process exit so its model cannot retain CUDA memory
    # after releasing the lease. No research restart is needed in this case.
    me = psutil.Process()
    record = dict(schemaVersion=1, token=str(uuid.uuid4()), project=project, state='tts_running',
                  requestedAt=time.time(), queueDir=None, idleGpu=True,
                  coordinator=dict(pid=me.pid, createTime=me.create_time()),
                  gpuBeforeTts=dict(freeMiB=free, utilization=util))
    lease.parent.mkdir(parents=True, exist_ok=True)
    try:
        with lease.open('x', encoding='utf-8') as f:
            json.dump(record, f, ensure_ascii=False, indent=2)
    except FileExistsError:
        return schedule_gpu_handoff(project, device, dry_run)

    def release_idle():
        if lease.exists():
            current = json.loads(lease.read_text(encoding='utf-8-sig'))
            if current.get('token') == record['token']:
                current.update(state='tts_process_exiting', finishedAt=time.time())
                history = ROOT / 'shared/output/gpu-handoff'
                history.mkdir(parents=True, exist_ok=True)
                (history / (record['token'] + '.json')).write_text(json.dumps(current, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
                lease.unlink()
    atexit.register(release_idle)
