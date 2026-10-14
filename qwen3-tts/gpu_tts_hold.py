"""Honor a user-requested GPU handoff without interrupting active narration."""
import json
from pathlib import Path

HOLD_PATH = Path(__file__).resolve().parents[1] / 'shared/output/GPU_TTS_HOLD.json'


def permitted_active_run(config, project, ancestors):
    """Permit only descendants of the recorded, already-running video batch."""
    if project != config.get('allowed_project'):
        return False
    owner = config.get('allowed_owner', {})
    return any(
        proc['pid'] == owner.get('pid')
        and abs(proc['create_time'] - owner.get('create_time', -1)) < 0.01
        and proc['cmdline'] == owner.get('cmdline')
        for proc in ancestors
    )


def check_gpu_tts_hold(project, device, dry_run=False):
    if dry_run or not device.startswith('cuda') or not HOLD_PATH.exists():
        return
    try:
        config = json.loads(HOLD_PATH.read_text(encoding='utf-8-sig'))
        if not config.get('active', True):
            return
        import psutil
        ancestors = [
            {'pid': p.pid, 'create_time': p.create_time(), 'cmdline': p.cmdline()}
            for p in psutil.Process().parents()
        ]
        if permitted_active_run(config, project, ancestors):
            print('GPU handoff: finishing the already-running video TTS batch.', flush=True)
            return
    except Exception as exc:
        raise SystemExit(f'GPU TTS hold could not be verified; no synthesis started: {exc}')
    raise SystemExit(
        f'GPU TTS paused by user: retargeting research has priority. '
        f'Existing WAV files are preserved. Hold: {HOLD_PATH}'
    )
