"""Scoped user-authorized 25% entry profile; preserve shared-job exclusion."""
import atexit
import json
import time
import uuid


def install_voice_profile(approved):
    import gpu_handoff_guard as handoff
    guard = approved.resource_guard()
    guard.OWNER = 'elden-ring-causal-v11'
    guard.PROTOCOL = 'elden-ring-causal-v11-voice'

    def busy(_guard, minimum):
        reason = guard.busy_reason()
        if reason:
            return reason
        free, use = approved.headroom()
        if free < minimum or use > 25:
            return f'GPU {free} MiB free / {use}% utilization; requires {minimum} MiB and <=25%'
        return None

    def reserve(project, device, dry_run=False, minimum_free_mib=8192):
        assert project.startswith('elden-ring-causal-v11-voice-')
        assert device == 'cuda:0' and minimum_free_mib >= 8192
        if dry_run:
            return
        if reason := busy(guard, minimum_free_mib):
            raise RuntimeError(reason)
        token = uuid.uuid4().hex
        identity = guard.identity()
        free, use = approved.headroom()
        if free < minimum_free_mib or use > 25:
            raise RuntimeError('Resource headroom changed before reservation.')
        record = dict(schemaVersion=1, protocol=guard.PROTOCOL, owner=guard.OWNER,
                      token=token, project=project, state='tts_running', phase='running',
                      **identity, coordinator=identity, requestedAt=time.time(), queueDir=None,
                      resourceProfile='explicit-user-authorized-25pct; single-model; 8GiB-free; allocator7GiB',
                      gpuBeforeTts=dict(freeMiB=free, utilization=use, minimumFreeMiB=minimum_free_mib))
        guard.LEASE.parent.mkdir(parents=True, exist_ok=True)
        with guard.LEASE.open('x', encoding='utf8') as target:
            json.dump(record, target)

        def release():
            if guard.LEASE.exists():
                current = approved.read(guard.LEASE)
                if guard.ours(current) and current.get('token') == token:
                    archive = guard.LEASE.parent / 'gpu-handoff'
                    archive.mkdir(exist_ok=True)
                    current.update(state='tts_process_exiting', finishedAt=time.time())
                    approved.save(archive / f'{token}.json', current)
                    guard.LEASE.unlink()
        atexit.register(release)
        if reason := guard.busy_reason(own_token=token):
            raise RuntimeError(reason)
        # Compatible ownership is also understood by the unchanged Qwen entrypoint.
        handoff.check_gpu_handoff(project, device)

    approved.busy = busy
    handoff.schedule_gpu_handoff = reserve
