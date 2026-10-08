"""Finish an existing research job, run one video TTS batch, then resume its queue.

Only cooperative STOP controls are supported. Never terminate/suspend GPU work.
The original queue validates and seals each completed run before it stops.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
import uuid
import psutil

ROOT = Path(__file__).resolve().parents[3]
LEASE = ROOT / 'shared/output/GPU_HANDOFF.json'
HISTORY = ROOT / 'shared/output/gpu-handoff'


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + '.tmp-' + str(os.getpid()))
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    os.replace(tmp, path)


def alive(identity):
    try:
        p = psutil.Process(identity['pid'])
        return abs(p.create_time() - identity['createTime']) < .01
    except psutil.NoSuchProcess:
        return False


def snapshot(p):
    return dict(pid=p.pid, createTime=p.create_time(), command=p.cmdline(), cwd=p.cwd(), exe=p.exe())


def owned_remove(path, token):
    if path.exists() and read(path).get('token') == token:
        path.unlink()


def update(record, **changes):
    record.update(changes)
    record['updatedAt'] = time.time()
    write(LEASE, record)
    write(HISTORY / (record['token'] + '.json'), record)
    print(json.dumps(changes, ensure_ascii=False), flush=True)


def request(args):
    q = Path(args.queue_dir).resolve()
    original = read(q / 'status.json')
    owner = psutil.Process(original['owner_pid'])
    identity = snapshot(owner)
    if 'placement_focus' not in ' '.join(identity['command']):
        raise RuntimeError('Unsupported queue: inspect its cooperative boundary and resume controls first.')
    external = Path(identity['cwd'])
    state = dict(schemaVersion=1, token=str(uuid.uuid4()), requestedAt=time.time(),
                 userEvidence=args.evidence, project=args.project, state='waiting_for_current_job_boundary',
                 queueDir=str(q), originalStatus=original, queueOwner=identity,
                 ownedFiles=[], existingPauseFiles=[])
    LEASE.parent.mkdir(parents=True, exist_ok=True)
    with LEASE.open('x', encoding='utf-8') as f:
        json.dump(state, f)
    try:
        for path in [q / 'STOP', external / 'GPU_PAUSE', external / 'tools/logs/GPU_PAUSE']:
            try:
                with path.open('x', encoding='utf-8') as f:
                    json.dump(dict(owner='video-tts-handoff', token=state['token']), f)
                state['ownedFiles'].append(str(path))
            except FileExistsError:
                state['existingPauseFiles'].append(str(path))
        update(state)
        return state
    except BaseException:
        for path in map(Path, state['ownedFiles']):
            owned_remove(path, state['token'])
        owned_remove(LEASE, state['token'])
        raise


def wait_boundary(state):
    q = Path(state['queueDir'])
    last = None
    while alive(state['queueOwner']):
        status = read(q / 'status.json')
        if status.get('status') == 'failed':
            raise RuntimeError('Research queue failed; preserve the failure and do not conceal it by restarting.')
        label = (status.get('status'), status.get('job'))
        if label != last:
            print('Waiting for cooperative boundary: ' + str(label), flush=True)
            last = label
        time.sleep(10)
    status = read(q / 'status.json')
    if status.get('status') not in ('stopped', 'complete_pending_visual_review'):
        raise RuntimeError('Original queue did not confirm a normal stopped/completed boundary.')
    original_job = state['originalStatus'].get('job')
    if original_job and state['originalStatus'].get('status') == 'running':
        marker_path = q / 'done' / (original_job + '.json')
        marker = read(marker_path)
        if marker.get('validation', {}).get('numerically_finite') is False:
            raise RuntimeError('Completed training validation is non-finite.')
        evidence = dict(marker=str(marker_path), markerSha256=hashlib.sha256(marker_path.read_bytes()).hexdigest(),
                        validation=marker['validation'], outputs=marker.get('outputs', []))
    else:
        evidence = None
    update(state, state='research_boundary_saved', boundaryStatus=status, completedJobEvidence=evidence)
    stable_since = None
    while True:
        raw = subprocess.check_output(['nvidia-smi', '--query-gpu=memory.free,utilization.gpu',
                                      '--format=csv,noheader,nounits'], text=True,
                                     creationflags=subprocess.CREATE_NO_WINDOW)
        free, util = map(int, raw.splitlines()[0].replace(' ', '').split(','))
        # This model previously fits below 12 GB. Allow only a stable idle GPU.
        stable_since = (stable_since or time.monotonic()) if free >= 18000 and util < 15 else None
        if stable_since and time.monotonic() - stable_since >= 20:
            update(state, state='gpu_granted_to_tts', gpuBeforeTts=dict(freeMiB=free, utilization=util))
            return
        time.sleep(10)


def resume(state, env):
    q = Path(state['queueDir'])
    status = read(q / 'status.json')
    for path in map(Path, state['ownedFiles']):
        owned_remove(path, state['token'])
    if status.get('status') == 'stopped' and not alive(state['queueOwner']):
        if (q / 'STOP').exists():
            update(state, state='resume_pending_foreign_stop', reason='A separate STOP owner remains; it was preserved.')
            return
        log_path = q / 'logs' / ('resume_after_tts_' + state['token'] + '.log')
        with log_path.open('w', encoding='utf-8') as log:
            p = subprocess.Popen(state['queueOwner']['command'], cwd=state['queueOwner']['cwd'],
                                 env=env, stdout=log, stderr=subprocess.STDOUT,
                                 creationflags=subprocess.CREATE_NO_WINDOW)
        identity = snapshot(psutil.Process(p.pid))
        update(state, state='research_queue_restarted', resumedQueue=identity, resumeLog=str(log_path))
        deadline = time.monotonic() + 60
        while time.monotonic() < deadline:
            current = read(q / 'status.json')
            if current.get('owner_pid') == p.pid and current.get('status') in ('waiting_for_resources', 'running'):
                update(state, state='research_resume_verified', resumedStatus=current)
                break
            if p.poll() is not None:
                raise RuntimeError('Resumed queue exited; inspect its preserved resume log.')
            time.sleep(2)
        else:
            raise RuntimeError('Queue was relaunched but its fresh ownership was not verified.')
    elif alive(state['queueOwner']):
        update(state, state='original_queue_continues', reason='TTS did not start; cooperative stop request withdrawn.')
    else:
        update(state, state='research_already_complete_or_failed', boundaryStatus=status)
    owned_remove(LEASE, state['token'])


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--project', required=True)
    ap.add_argument('--queue-dir')
    ap.add_argument('--evidence', default='TTS 전 현재 GPU 학습 실행 완료 후 중단하고 TTS 종료 후 원래 작업 재개')
    ap.add_argument('--adopt-token')
    ap.add_argument('command', nargs=argparse.REMAINDER)
    args = ap.parse_args()
    command = args.command[1:] if args.command[:1] == ['--'] else args.command
    if not command:
        ap.error('Provide the exact TTS command after --.')
    if args.adopt_token:
        state = read(LEASE)
        if state['token'] != args.adopt_token or state['project'] != args.project:
            raise RuntimeError('Lease token/project mismatch.')
    else:
        if not args.queue_dir:
            ap.error('--queue-dir is required for a new request.')
        state = request(args)
    env = os.environ.copy()
    if alive(state['queueOwner']):
        # Keep original launcher variables locally; never print/store credentials.
        try:
            env = psutil.Process(state['queueOwner']['pid']).environ()
        except psutil.NoSuchProcess:
            # A cooperative STOP can complete between the identity check and
            # environment read. Its queue config still supplies child settings.
            pass
    update(state, coordinator=snapshot(psutil.Process()), ttsCommand=command)
    code = 1
    child = None
    try:
        wait_boundary(state)
        update(state, state='tts_running')
        child = subprocess.Popen(command, cwd=ROOT, creationflags=subprocess.CREATE_NO_WINDOW)
        update(state, ttsOwner=snapshot(psutil.Process(child.pid)))
        code = child.wait()
        update(state, state='tts_finished', ttsExitCode=code)
    except BaseException:
        # A coordinator interruption must never resume research over live TTS.
        if child is not None and child.poll() is None:
            print('Finish the already-running TTS process before restoring research.', flush=True)
            child.wait()
        raise
    finally:
        resume(state, env)
    return code


if __name__ == '__main__':
    raise SystemExit(main())
