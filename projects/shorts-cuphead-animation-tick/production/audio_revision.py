"""Cuphead finite-batch input/resource guards. Importing starts no media work."""
from contextlib import contextmanager
from pathlib import Path
import hashlib
import json
import os
import re
import stat
import time
import unicodedata
import uuid

P = Path(__file__).resolve().parents[1]
R = P.parents[1]
SLUG = 'shorts-cuphead-animation-tick'
REVISION = 'animation-tick-v1'
PRODUCTION_DATE_KST = '2026-10-26'
AUTH_ID = 'explicit-cuphead-teardown-splatoon-20261026'
BATCH_PATH = 'production/batches/cuphead-teardown-splatoon-20261026/batch.json'
MEDIA_ROOT = Path('C:/Users/1/Videos/YamyamProduction/cuphead-teardown-splatoon-20261026') / SLUG
LOCAL = P / 'production/local'
L = LOCAL / 'audio-v1'
VOICE = L / 'voice/narration.wav'
LEASE = R / 'shared/output/GPU_HANDOFF.json'
SCRIPT_SHA256 = '368818e83b5560b114f7fda58cbf7d3be7b93da51c847b93ff99dc1e894940ee'
SOURCE_SHA256 = '2c65d42024ad2c1a0ca62092ba8ce7ff886d0653960a86b2753c141b463e3ca4'
CLAUSES_SHA256 = 'b5a98f191e38daefe8e4db38eb739339190aba84bf33327659b43f3faa62236c'
REFERENCE_SHA256 = 'f0d59e79530ffc06bf0eb1541d31040042c6f108f2222e4991669748624ee089'
REFERENCE_TEXT_SHA256 = 'a22dbc1cc8a7d5bcaa8a412b5212439b86b51035bcaf692622374db48cffec20'
MODEL_CONFIG_SHA256 = 'b4f01752d15a488abde3e1ab44723ae4f4b9e68a4037257b098b3737893cc1f9'
GAME_NAMES = {
    'overwatch.exe', 'monsterhunterwilds.exe', 'd2r.exe', 'diablo ii.exe',
    'duckov.exe', 'escapefromduckov.exe', 'escape from duckov.exe',
    'factorio.exe', 'cult of the lamb.exe', 'cuphead.exe', 'teardown.exe',
    'unity.exe', 'unrealeditor.exe', 'unrealeditor-cmd.exe',
}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf8'))


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


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
    """Validate the real destination before retaining the repository junction alias."""
    path = Path(path).absolute()
    if not media_allowed(path):
        raise ValueError('Unregistered external media path: ' + str(path))
    return (path.relative_to(R).as_posix() if path.is_relative_to(R)
            else path.resolve().as_posix())


def validate_authorization(control, project, batch, plan):
    """Pure validation of this selected finite batch; recurring daily auth is irrelevant."""
    selected = control.get('shortsDirectSelection', {})
    auth = batch.get('authorization', {})
    project_auth = project.get('authorization', {})
    entries = [item for item in batch.get('projects', []) if item.get('slug') == SLUG]
    if (control.get('selectedShortVideo') != SLUG or selected.get('slug') != SLUG
            or selected.get('selectedRevision') != REVISION
            or selected.get('fullProductionAuthorized') is not True
            or selected.get('batch') != BATCH_PATH or SLUG not in selected.get('slugs', [])
            or batch.get('id') != 'cuphead-teardown-splatoon-20261026'
            or auth.get('id') != AUTH_ID
            or auth.get('authority') != 'direct-human-message-in-current-chat'
            or auth.get('fullProductionAuthorized') is not True
            or auth.get('requestedOnKst') != PRODUCTION_DATE_KST
            or auth.get('humanFinalReviewRequired') is not True
            or auth.get('advanceOutsideList') is not False
            or len(entries) != 1 or entries[0].get('revision') != REVISION
            or project.get('slug') != SLUG or project.get('currentRevision') != REVISION
            or project_auth.get('id') != AUTH_ID
            or project_auth.get('fullProductionAuthorized') is not True
            or project_auth.get('productionDateKst') != PRODUCTION_DATE_KST
            or project_auth.get('humanFinalReviewRequired') is not True
            or plan.get('slug') != SLUG or plan.get('revision') != REVISION
            or plan.get('authorizationId') != AUTH_ID):
        raise RuntimeError('Exact Cuphead finite-batch selection/revision/authorization changed; preserve outputs.')
    if plan.get('scriptFinalized') is not True or plan.get('independentFootageViewed') is not True:
        raise RuntimeError('A finalized script and actually viewed independent FHD source are required.')


def assert_media_junction():
    expected = MEDIA_ROOT / 'local'
    # Approved Qwen venv is Python3.11; os.path.isjunction arrived in3.12.
    is_junction = (LOCAL.is_dir() and
                   getattr(os.lstat(LOCAL), 'st_reparse_tag', None) == stat.IO_REPARSE_TAG_MOUNT_POINT)
    if (not is_junction
            or LOCAL.resolve() != expected.resolve()
            or expected.drive.casefold() != 'c:'):
        raise RuntimeError('Production local must be the checked native junction to this Cuphead C: directory.')


def guard():
    """Read-only preflight; no output directories, lease, model, GPU query or jobs."""
    control = read(R / 'shared/publishing/video-production-control.json')
    project = read(P / 'project.json')
    plan = read(P / 'planning/production-plan.json')
    validate_authorization(control, project, read(R / BATCH_PATH), plan)
    if P.name != SLUG:
        raise RuntimeError('Audio code must remain in the selected Cuphead project.')
    assert_media_junction()
    manifest = read(P / 'production/tts-manifest.json')
    locks = manifest.get('inputLocks', {})
    if (manifest.get('slug') != SLUG or manifest.get('revision') != REVISION
            or manifest.get('authorizationId') != AUTH_ID
            or locks.get('scriptSha256') != SCRIPT_SHA256
            or locks.get('sourceSha256') != SOURCE_SHA256
            or locks.get('clausesSha256') != CLAUSES_SHA256):
        raise RuntimeError('Cuphead audio manifest input locks changed.')
    fixed = {
        'script': f'projects/{SLUG}/script/narration.spoken.ko.json',
        'reference': 'shared/voice-reference/reference-15-35s.wav',
        'referenceText': 'shared/voice-reference/reference-15-35s.ko.txt',
        'model': 'qwen3-tts/models/Qwen3-TTS-12Hz-1.7B-Base',
    }
    tts = manifest.get('tts', {})
    if (manifest.get('paths', {}).get('script') != fixed['script']
            or any(tts.get(key) != fixed[key] for key in ('reference', 'referenceText', 'model'))
            or tts.get('engine') != 'qwen3-tts' or tts.get('language') != 'Korean'
            or tts.get('renderMode') != 'line' or tts.get('cpuFallbackAllowed') is not False
            or tts.get('outputDir') != f'projects/{SLUG}/production/local/audio-v1/voice'):
        raise RuntimeError('Preserve the approved Qwen voice/model and GPU-only execution choice.')
    checks = [
        (R / fixed['script'], SCRIPT_SHA256),
        (P / 'script/clauses.json', CLAUSES_SHA256),
        (R / fixed['reference'], REFERENCE_SHA256),
        (R / fixed['referenceText'], REFERENCE_TEXT_SHA256),
        (R / fixed['model'] / 'config.json', MODEL_CONFIG_SHA256),
    ]
    for path, expected in checks:
        if not path.is_file() or sha(path) != expected:
            raise RuntimeError('Missing/changed approved input: ' + str(path))
    source = read(P / 'sources/selected-footage.json')
    path = R / source.get('path', '')
    if (source.get('classification') != 'independent-gameplay'
            or source.get('sourceSHA256') != SOURCE_SHA256
            or source.get('nativeDimensions') != [1920, 1080]
            or source.get('nativeFrameRate') != '60/1'
            or source.get('inspection', {}).get('actuallyViewed') is not True
            or source.get('decodeCheck', {}).get('result') != 'exit0; empty error log'
            or not path.is_file() or not path.resolve().is_relative_to((MEDIA_ROOT / 'local').resolve())
            or sha(path) != SOURCE_SHA256):
        raise RuntimeError('Actually viewed native-FHD Cuphead source proof/hash changed.')
    document = read(R / fixed['script'])
    lines = [line for scene in document['scenes'] for line in scene['lines']]
    clauses = read(P / 'script/clauses.json')
    aliases = clauses.get('pronunciationAliases', {})
    if (not lines or any(not isinstance(line, str) or not normalize_speech(line, aliases) for line in lines)
            or normalize_speech(' '.join(lines), aliases)
               != normalize_speech((P / 'script/narration.ko.txt').read_text(encoding='utf8'), aliases)):
        raise RuntimeError('Narration inputs differ or contain an empty paragraph.')
    model_dir = R / fixed['model']
    if not any(model_dir.glob('*.safetensors')) and not (model_dir / 'pytorch_model.bin').is_file():
        raise RuntimeError('The existing approved local TTS weights are unavailable; never download a replacement.')
    return control


def assert_no_game_apps():
    """Read-only process inspection; never terminate/pause/reconfigure another app."""
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
            auth_broker = False
            if (name == 'unity.exe' and executable == 'c:/users/1/appdata/local/unity/bin/unity.exe'
                    and len(args) == 2 and args[1] == '--internal-auth-broker-serve'):
                parent = proc.parent()
                auth_broker = bool(parent and parent.exe().replace('\\', '/').casefold()
                                   == 'c:/program files/unity hub/unity hub.exe')
            if not hub and not auth_broker:
                busy.append({'pid': proc.pid, 'name': info.get('name'), 'exe': info.get('exe')})
        except (psutil.NoSuchProcess, psutil.ZombieProcess):
            continue
        except psutil.AccessDenied as error:
            raise RuntimeError('Unable to verify an active game/editor; defer GPU work.') from error
    if busy:
        raise RuntimeError('User game/editor remains active; defer GPU work: ' + json.dumps(busy))
    return busy


def assert_gpu_available():
    import subprocess
    guard()
    assert_no_game_apps()
    if LEASE.exists():
        raise RuntimeError('Existing GPU lease preserved; do not start another GPU job.')
    rows = subprocess.check_output([
        'nvidia-smi', '--query-gpu=memory.free,utilization.gpu',
        '--format=csv,noheader,nounits'], text=True).strip().splitlines()
    if len(rows) != 1:
        raise RuntimeError('Expected the verified single-GPU host; inspect device selection.')
    free, utilization = map(int, rows[0].split(','))
    if free < 4800 or utilization >= 35:
        raise RuntimeError('GPU not idle enough for this serial job: ' + str((free, utilization)))
    return {'freeMiB': free, 'utilizationPercent': utilization, 'activeGameApps': []}


def assert_owned_lease(record):
    current = read(LEASE)
    if (current.get('token') != record['token']
            or current.get('coordinator') != record['coordinator']
            or current.get('project') != SLUG or current.get('revision') != REVISION):
        raise RuntimeError('This process no longer owns the GPU lease; preserve the current lease.')
    guard()
    assert_no_game_apps()


def release_owned_lease(record):
    """Never remove a foreign or malformed lease, including after a failed job."""
    if not LEASE.exists():
        return False
    try:
        current = read(LEASE)
    except (OSError, ValueError):
        return False
    if (current.get('token') == record.get('token')
            and current.get('coordinator') == record.get('coordinator')
            and current.get('project') == SLUG and current.get('revision') == REVISION):
        LEASE.unlink()
        return True
    return False


@contextmanager
def gpu_lease(job):
    """Exclusive serial lease, acquired before any model import/load or CUDA work."""
    import psutil
    snapshot = assert_gpu_available()
    process = psutil.Process()
    record = {
        'project': SLUG, 'revision': REVISION, 'authorizationId': AUTH_ID,
        'job': job, 'token': uuid.uuid4().hex,
        'coordinator': {'pid': process.pid, 'createTime': process.create_time()},
        'startedAt': time.time(), 'resourceSnapshotBefore': snapshot,
        'foreignProcessesPaused': [],
    }
    if not LEASE.parent.is_dir():
        raise RuntimeError('Existing shared GPU-lease parent is required; inspect coordinator setup.')
    with LEASE.open('x', encoding='utf8') as stream:
        json.dump(record, stream, ensure_ascii=False)
    try:
        assert_owned_lease(record)
        yield record
    finally:
        release_owned_lease(record)
