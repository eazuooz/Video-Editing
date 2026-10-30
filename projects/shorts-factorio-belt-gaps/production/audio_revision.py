"""Finite daily-Short paths and guards; importing this module starts no work."""
from pathlib import Path
import json
import re
import unicodedata

P = Path(__file__).resolve().parents[1]
R = P.parents[1]
SLUG = 'shorts-factorio-belt-gaps'
REVISION = 'belt-gaps-v1'
PRODUCTION_DATE_KST = '2026-10-26'
AUTH_ID = 'daily-five-topics-one-short-v2'
MEDIA_ROOT = Path('C:/Users/1/Videos/YamyamProduction/daily-shorts-20261026') / SLUG
LOCAL = P / 'production/local'
L = LOCAL / 'audio-v1'
VOICE = L / 'voice/narration.wav'
GAME_NAMES = {
    'overwatch.exe', 'monsterhunterwilds.exe', 'd2r.exe', 'diablo ii.exe', 'duckov.exe',
    'escapefromduckov.exe', 'escape from duckov.exe',
    'factorio.exe', 'cult of the lamb.exe',
    'unity.exe', 'unrealeditor.exe', 'unrealeditor-cmd.exe',
}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf8'))


def normalize_speech(text, aliases):
    for display, speech in sorted(aliases.items(), key=lambda item: -len(item[0])):
        text = re.sub(re.escape(display), lambda match: speech, text, flags=re.I)
    text = re.sub(r'[−-]\s*(?=\d)', '마이너스', text)
    text = re.sub(r'\+\s*(?=\d)', '플러스', text)
    return re.sub(r'[^0-9a-z가-힣]', '', unicodedata.normalize('NFC', text).lower())


def media_allowed(path):
    resolved = Path(path).resolve()
    return resolved.is_relative_to(R.resolve()) or resolved.is_relative_to(MEDIA_ROOT.resolve())


def media_reference(path):
    """Keep valid D: aliases, but validate their real C: destination first."""
    path = Path(path).absolute()
    if not media_allowed(path):
        raise ValueError('Unregistered external media path: ' + str(path))
    if path.is_relative_to(R):
        return path.relative_to(R).as_posix()
    return path.resolve().as_posix()


def guard():
    control = read(R / 'shared/publishing/video-production-control.json')
    auth = control.get('shortsRecurringAuthorization', {})
    project = read(P / 'project.json')
    selection = project.get('authorization', {})
    active = str(auth.get('status', auth.get('automationStatus', ''))).lower() == 'active'
    if (P.name != SLUG or project.get('slug') != SLUG
            or project.get('currentRevision') != REVISION
            or auth.get('id') != AUTH_ID or not active
            or selection.get('fullProductionAuthorized') is not True
            or selection.get('productionDateKst') != PRODUCTION_DATE_KST):
        raise RuntimeError('Selected daily Short/revision/date authorization changed; preserve all outputs.')
    plan = read(P / 'planning/production-plan.json')
    if plan.get('scriptFinalized') is not True or plan.get('independentFootageViewed') is not True:
        raise RuntimeError('Actual independent-footage viewing and finalized script remain required.')
    if not LOCAL.is_dir() or LOCAL.resolve() != (MEDIA_ROOT / 'local').resolve():
        raise RuntimeError('Production local must resolve to this daily Short\'s C: directory; D: media writes are forbidden.')
    return control


def assert_no_game_apps():
    """Read-only process check. Never stop, pause or reconfigure another app."""
    import psutil
    busy = []
    for proc in psutil.process_iter(['name', 'exe', 'cmdline']):
        try:
            info = proc.info
            name = (info.get('name') or '').casefold()
            if name not in GAME_NAMES:
                continue
            executable = (info.get('exe') or '').replace('\\', '/').casefold()
            args = info.get('cmdline') or []
            hub = (name == 'unity.exe'
                   and executable == 'c:/program files/unity hub/resources/unity.exe'
                   and len(args) == 2
                   and str(args[0]).replace('\\', '/').casefold() == executable
                   and str(args[1]).casefold() == 'serve')
            allowed_editor = False
            permission = read(P / 'project.json').get('resourcePermission', {})
            # The user resumed this one Short after the exact open production
            # editor was identified. PID creation time prevents PID-reuse leaks.
            if name == 'unity.exe' and permission.get('id') == 'current-production-editor-resume-20261030':
                pid = permission.get('editorPid')
                root = psutil.Process(pid) if pid and psutil.pid_exists(pid) else None
                if root and abs(root.create_time() - permission.get('editorCreateTime', 0)) < .01:
                    project_args = [str(a).replace('\\', '/').casefold() for a in args]
                    project = str(permission.get('projectPath', '')).replace('\\', '/').casefold()
                    same_project = any(project_args[j].strip('"') == project for j in range(1,len(project_args)) if project_args[j-1].casefold() == '-projectpath')
                    approved_exe = str(permission.get('editorExe', '')).replace('\\', '/').casefold()
                    own_process = proc.pid == pid or (proc.ppid() == pid and any('assetimportworker' in a for a in project_args))
                    allowed_editor = same_project and executable == approved_exe and own_process
            if not hub and not allowed_editor:
                busy.append({'pid': proc.pid, 'name': info.get('name'), 'exe': info.get('exe')})
        except (psutil.NoSuchProcess, psutil.ZombieProcess):
            continue
        except psutil.AccessDenied:
            raise RuntimeError('Unable to verify an active game/editor process; defer GPU work.')
    if busy:
        raise RuntimeError('User game/editor remains active; defer GPU work: ' + json.dumps(busy))
    return busy


def assert_gpu_available():
    """Pre-launch device check; caller still owns serial execution and its lease."""
    import subprocess
    guard()
    assert_no_game_apps()
    if (R / 'shared/output/GPU_HANDOFF.json').exists():
        raise RuntimeError('Foreign GPU lease preserved; do not start another GPU job.')
    result = subprocess.check_output([
        'nvidia-smi', '--query-gpu=memory.free,utilization.gpu',
        '--format=csv,noheader,nounits'], text=True).strip().splitlines()
    if len(result) != 1:
        raise RuntimeError('Expected the verified single-GPU host; inspect device selection.')
    free, utilization = map(int, result[0].split(','))
    if free < 4800 or utilization >= 35:
        raise RuntimeError('GPU not idle enough for selected serial job: ' + str((free, utilization)))
    return {'freeMiB': free, 'utilizationPercent': utilization, 'activeGameApps': []}
