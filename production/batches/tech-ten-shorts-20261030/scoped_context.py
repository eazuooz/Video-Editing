"""Explicit ten-Short scope and resources. Importing this module starts no work."""
from pathlib import Path
import datetime
import hashlib
import json
import re
import subprocess
import unicodedata

BATCH = Path(__file__).resolve().parent
ROOT = BATCH.parents[2]
AUTH_ID = 'explicit-tech-ten-shorts-20261030'
REVISION = 'tech-ten-v1'
MEDIA = Path('C:/Users/1/Videos/YamyamProduction/tech-ten-shorts-20261030')
RESEARCH = ROOT / 'shared/publishing/shorts-research-20261030-ten.json'
RESEARCH_SHA = 'bd53b4984c62a4ab9a75170b626f2da96093e51fe33c9495f676bc5f7d47403d'
GAME_NAMES = {
    'overwatch.exe', 'monsterhunterwilds.exe', 'd2r.exe', 'diablo ii.exe',
    'duckov.exe', 'escapefromduckov.exe', 'escape from duckov.exe', 'factorio.exe',
    'cult of the lamb.exe', 'starcraft.exe', 'starcraft remastered.exe',
    'sc2.exe', 'sc2_x64.exe', 'hlvr.exe', 'batmanorigins.exe', 'sotgame.exe',
    'seaofthieves.exe', 'u4.exe', 'unity.exe', 'unrealeditor.exe', 'unrealeditor-cmd.exe',
}


class Deferred(RuntimeError):
    pass


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def inventory():
    if sha(RESEARCH) != RESEARCH_SHA:
        raise RuntimeError('The selected research record changed; inspect before changing finite scope.')
    selected = ['shorts-' + x['id'] for x in read(RESEARCH)['candidates']]
    batch = read(BATCH / 'batch.json')
    rows = batch['projects']
    if len(rows) != 10 or [x['slug'] for x in rows] != selected:
        raise RuntimeError('Only the exact selected ten research candidates may be produced.')
    return batch, rows


def authorization(slug=None):
    batch, rows = inventory()
    control = read(ROOT / 'shared/publishing/video-production-control.json')
    auth = control.get('explicitTechTenBatch20261030', {})
    if auth.get('id') != AUTH_ID or auth.get('status') not in {'preproduction-active', 'production-active', 'active'}:
        raise Deferred('New explicit ten-Short production scope is not active in the control record.')
    if (auth.get('batch') != BATCH.relative_to(ROOT).as_posix() + '/batch.json'
            or auth.get('research') != RESEARCH.relative_to(ROOT).as_posix()
            or batch.get('fullProductionAuthorized') is not True):
        raise RuntimeError('Control authorization must identify the exact selected ten-project record.')
    if slug and slug not in {x['slug'] for x in rows}:
        raise RuntimeError('Project is outside the selected ten.')
    return control


def normalize_speech(text, aliases):
    for display, speech in sorted(aliases.items(), key=lambda item: -len(item[0])):
        text = re.sub(re.escape(display), lambda match: speech, text, flags=re.I)
    text = re.sub(r'[−-]\s*(?=\d)', '마이너스', text)
    text = re.sub(r'\+\s*(?=\d)', '플러스', text)
    return re.sub(r'[^0-9a-z가-힣]', '', unicodedata.normalize('NFC', text).lower())


def process_snapshot():
    """Return safe process metadata only; never log raw command lines or auth args."""
    import psutil
    rows = []
    # Read command lines only for relevant names. Scanning every system process
    # can stall on protected services and unnecessarily handles unrelated secrets.
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            item = proc.info
            name = (item.get('name') or '').casefold()
            if name not in GAME_NAMES:
                continue
            item = proc.as_dict(['pid', 'ppid', 'name', 'exe', 'cmdline', 'create_time'])
            exe = (item.get('exe') or '').replace('\\', '/').casefold()
            args = item.get('cmdline') or []
            hub = (name == 'unity.exe' and exe == 'c:/program files/unity hub/resources/unity.exe'
                   and len(args) == 2 and str(args[1]).casefold() == 'serve')
            if hub:
                continue
            project = None
            for i, arg in enumerate(args[:-1]):
                if str(arg).casefold() == '-projectpath':
                    project = str(args[i + 1]).replace('\\', '/')
            rows.append({'pid': item['pid'], 'parentPid': item['ppid'], 'name': item['name'],
                         'exe': item.get('exe'), 'createTime': item.get('create_time'),
                         'projectPath': project, 'assetImportWorker': any('assetimportworker' in str(a).casefold() for a in args)})
        except (psutil.NoSuchProcess, psutil.ZombieProcess):
            continue
        except psutil.AccessDenied:
            raise Deferred('Cannot verify an active game/editor process.')
    return rows


def assert_no_game_apps():
    rows = process_snapshot()
    # No previous project's exact-editor exception is inherited by this batch.
    permission_path = BATCH / 'gpu-authorization.json'
    permission = read(permission_path) if permission_path.is_file() else {}
    allowed = []
    if permission.get('id') == 'explicit-tech-ten-gpu-20261030' and permission.get('userEvidence'):
        recorded = permission.get('allowedExistingEditor', {})
        expected_pid = recorded.get('pid')
        expected_time = datetime.datetime.fromisoformat(recorded['creationTimeUtc'].replace('Z', '+00:00')).timestamp()
        expected_exe = str(recorded.get('executable', '')).replace('\\', '/').casefold()
        expected_project = str(recorded.get('project', '')).replace('\\', '/').casefold()
        roots = [r for r in rows if r['pid'] == expected_pid
                 and abs(float(r['createTime']) - float(expected_time)) < .01
                 and str(r['exe']).replace('\\', '/').casefold() == expected_exe
                 and str(r['projectPath']).casefold() == expected_project]
        if roots:
            allowed = [r['pid'] for r in rows if r['pid'] == expected_pid or
                       (r['parentPid'] == expected_pid and r['assetImportWorker']
                        and str(r['projectPath']).casefold() == expected_project
                        and str(r['exe']).replace('\\', '/').casefold() == expected_exe)]
    busy = [r for r in rows if r['pid'] not in allowed]
    if busy:
        raise Deferred('Game/editor remains active: ' + json.dumps(busy, ensure_ascii=False))
    return []


def make_context(slug):
    _, rows = inventory()
    if slug not in {row['slug'] for row in rows}:
        raise RuntimeError('Unknown project.')
    project = ROOT / 'projects' / slug
    media_root = MEDIA / slug
    local = project / 'production/local'
    audio = local / 'audio-v1'
    voice = audio / 'voice/narration.wav'

    def media_allowed(path):
        resolved = Path(path).resolve()
        return resolved.is_relative_to(ROOT.resolve()) or resolved.is_relative_to(MEDIA.resolve())

    def media_reference(path):
        path = Path(path).absolute()
        if not media_allowed(path):
            raise RuntimeError('Unregistered media path: ' + str(path))
        return path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else path.resolve().as_posix()

    def guard():
        control = authorization(slug)
        manifest = read(project / 'project.json')
        if (manifest.get('slug') != slug or manifest.get('currentRevision') != REVISION
                or manifest.get('authorization', {}).get('id') != AUTH_ID
                or manifest['authorization'].get('fullProductionAuthorized') is not True):
            raise Deferred('Project authorization/revision changed.')
        plan = read(project / 'planning/production-plan.json')
        if plan.get('scriptFinalized') is not True or plan.get('independentFootageViewed') is not True:
            raise Deferred('Final script and actual independent footage viewing are not yet recorded.')
        if local.resolve() != (media_root / 'local').resolve() or not local.is_dir():
            raise RuntimeError('Production local must be the selected C: media junction.')
        return control

    def assert_gpu_available():
        guard()
        assert_no_game_apps()
        if (ROOT / 'shared/output/GPU_HANDOFF.json').exists():
            raise Deferred('Existing GPU lease preserved.')
        output = subprocess.check_output(['nvidia-smi', '--query-gpu=memory.free,utilization.gpu',
            '--format=csv,noheader,nounits'], text=True).strip().splitlines()
        if len(output) != 1:
            raise RuntimeError('Expected the recorded single GPU.')
        free, utilization = map(int, output[0].split(','))
        if free < 4800 or utilization >= 35:
            raise Deferred(f'GPU not idle enough: freeMiB={free}, utilization={utilization}.')
        return {'freeMiB': free, 'utilizationPercent': utilization, 'activeGameApps': []}

    return dict(P=project, R=ROOT, SLUG=slug, REVISION=REVISION, AUTH_ID=AUTH_ID,
                MEDIA_ROOT=media_root, LOCAL=local, L=audio, VOICE=voice,
                read=read, normalize_speech=normalize_speech, media_allowed=media_allowed,
                media_reference=media_reference, guard=guard, assert_no_game_apps=assert_no_game_apps,
                assert_gpu_available=assert_gpu_available)
