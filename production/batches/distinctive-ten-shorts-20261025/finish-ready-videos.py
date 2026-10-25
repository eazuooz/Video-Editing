"""Finite, serial local finalizer for the ten explicitly selected Shorts.

Default/--validate-only: print and validate commands; no media or state is written.
--execute: consume existing approved PCM, never generate voice or use a platform.
--wait-minutes 720 bounds waiting for this batch only; no recurring automation.
Failed stages retain logs/media and do not prevent another prepared project.
"""
from pathlib import Path
import argparse
import ast
import datetime
import hashlib
import html
import importlib.util
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time
import uuid

from batch_job_lock import SerialJobLock, JobBusy, LOCK_PROTOCOL, MEDIA_ROOT, inspect_lock

ROOT = Path(__file__).resolve().parents[3]
BATCH = Path(__file__).parent
REVISION = 'distinctive-ten-v1'
AUTH_ID = 'explicit-ten-distinctive-shorts-20261025'
VOICE_PYTHON = ROOT / 'qwen3-tts/.venv/Scripts/python.exe'
TRIO = {'shorts-noita-material-pixels', 'shorts-rain-world-body-chunks', 'shorts-obra-dinn-dithering'}
UNITY = {'shorts-viewfinder-mesh-slicing', 'shorts-outer-wilds-gravity'}
ARCH = {'shorts-d2r-renderer-logic-separation', 'shorts-d2r-controller-input-adapter'}
DIABLO = {'shorts-d2r-ultrawide-ai-range': 'ultrawide', 'shorts-d2r-loot-grass-clearance': 'grass',
          'shorts-d2-modular-sprite-equipment': 'sprites'}
SLUGS = TRIO | UNITY | ARCH | set(DIABLO)
GAME_NAMES = {'monsterhunterwilds.exe', 'd2r.exe', 'diablo ii.exe', 'unity.exe', 'unrealeditor.exe'}
CREATION_FLAGS = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0


class Deferred(RuntimeError):
    """An external/resource prerequisite can change without modifying artifacts."""


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf8'))


def text_json(value):
    return json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n'


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for part in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            h.update(part)
    return h.hexdigest()


def write_atomic(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.' + uuid.uuid4().hex + '.partial')
    with temporary.open('x', encoding='utf8', newline='\n') as stream:
        stream.write(value if isinstance(value, str) else text_json(value))
    os.replace(temporary, path)


def immutable(path, value):
    payload = value if isinstance(value, str) else text_json(value)
    path = Path(path)
    if path.exists():
        if path.read_text(encoding='utf8') != payload:
            raise RuntimeError('Preserve differing existing artifact: ' + str(path))
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf8', newline='\n') as stream:
        stream.write(payload)


def artifact(path):
    path = Path(path)
    if not path.is_file() or path.stat().st_size == 0:
        raise RuntimeError('Required nonempty artifact missing: ' + str(path))
    return dict(path=str(path), sha256=sha(path), bytes=path.stat().st_size)


def verify_artifacts(rows):
    for row in rows:
        p = Path(row['path'])
        if not p.is_file() or p.stat().st_size != row['bytes'] or sha(p) != row['sha256']:
            raise RuntimeError('Previous successful artifact changed: ' + str(p))


def authorization(slug=None):
    auth = read(ROOT / 'shared/publishing/video-production-control.json').get('scopedBatchAuthorizations', {}).get(AUTH_ID, {})
    rows = read(BATCH / 'batch.json')['projects']
    if auth.get('status') != 'active' or not auth.get('fullProductionAuthorized'):
        raise Deferred('Explicit finite ten-Short authorization is not active.')
    if {r['slug'] for r in rows} != SLUGS or not SLUGS.issubset(auth.get('slugs', [])):
        raise RuntimeError('Finite batch inventory changed; never advance outside the ten selected projects.')
    if slug:
        if slug not in SLUGS:
            raise RuntimeError('Project is outside the finite batch.')
        p = ROOT / 'projects' / slug
        manifest = read(p / 'project.json')
        plan = read(p / 'planning/production-plan.json')
        if manifest.get('currentRevision') != REVISION:
            raise Deferred('Selected project revision changed.')
        if not plan.get('scriptFinalized') or not plan.get('independentFootageViewed'):
            raise Deferred('Source/script preparation remains incomplete.')
        if (p / 'production/local').resolve().is_relative_to(MEDIA_ROOT.resolve()) is False:
            raise RuntimeError('Use the verified C: media junction; D: is not the final-render destination.')
    return rows


def coordinated_queue_pids(processes, status):
    """Allow the registered live interpreter and its exact queue launcher wrappers."""
    if status.get('serialProtocol') != LOCK_PROTOCOL:
        return set()
    queue_path = str(BATCH / 'generate-ready-voices.py').replace('\\', '/').casefold()
    def is_queue(row):
        return any(str(Path(arg).absolute()).replace('\\', '/').casefold() == queue_path
                   for arg in (row.get('cmdline') or []) if arg.lower().endswith('generate-ready-voices.py'))
    by_pid = {row['pid']: row for row in processes}
    row = by_pid.get(status.get('pid'))
    if not row or not is_queue(row) or abs(float(row.get('create_time', -1)) - float(status.get('processCreateTime', -2))) >= .05:
        return set()
    accepted = {row['pid']}
    while row.get('ppid') in by_pid:
        row = by_pid[row['ppid']]
        if row['pid'] in accepted or not is_queue(row):
            break
        accepted.add(row['pid'])
    return accepted


def is_python_interpreter(row):
    # Shell command text can mention our script while the coordinated Python
    # child does the work. It is not an independent production worker.
    return (row.get('name') or '').casefold() in {'python.exe', 'pythonw.exe', 'python', 'python3', 'python3.exe'}


def is_unity_hub_server(row):
    """Exclude only the observed Hub service, never an Editor with the same name."""
    executable = (row.get('exe') or '').replace('\\', '/').casefold()
    command = row.get('cmdline') or []
    return ((row.get('name') or '').casefold() == 'unity.exe'
            and executable == 'c:/program files/unity hub/resources/unity.exe'
            and len(command) == 2
            and str(command[0]).replace('\\', '/').casefold() == executable
            and str(command[1]).casefold() == 'serve')


def mc_entry(slug):
    route = 'diablo-tricks-shorts-20261025/' + DIABLO[slug] if slug in DIABLO else slug
    return ROOT / 'motion-canvas/src/projects' / route / 'project.ts'


def mc_dependencies(entry):
    """Follow relative code imports, including Outer->Viewfinder and actor helpers."""
    found, pending = set(), [Path(entry)]
    while pending:
        path = pending.pop()
        if path in found:
            continue
        if not path.is_file():
            raise RuntimeError('Missing Motion Canvas code dependency: ' + str(path))
        found.add(path)
        for module in re.findall(r'''(?:from\s*|import\s*)['"]([^'"]+)['"]''', path.read_text(encoding='utf8')):
            if not module.startswith('.'):
                continue
            base = path.parent / module.split('?')[0]
            if base.suffix not in ('', '.ts', '.tsx', '.js', '.mjs', '.cjs'):
                continue
            candidates = [base] if base.suffix else [base.with_suffix(ext) for ext in ('.ts', '.tsx', '.js')] + [base / 'index.ts']
            selected = next((p.absolute() for p in candidates if p.is_file()), None)
            if selected:
                # Normalize .. without following media junctions; code remains in D:.
                pending.append(Path(os.path.normpath(selected)))
            elif base.suffix in ('', '.ts', '.tsx', '.js'):
                raise RuntimeError('Unresolved local code import: ' + module + ' from ' + str(path))
    return found


def production_code_map(slug):
    project = ROOT / 'projects' / slug
    files = {Path(__file__), BATCH / 'batch_job_lock.py', BATCH / 'render-one.cjs'}
    for pattern in ('*.py', '*.ps1', '*.cjs'):
        files.update((project / 'production').glob(pattern))
    files.update(mc_dependencies(mc_entry(slug)))
    command = visual_command(slug)
    files.update(Path(arg) for arg in command if arg.endswith(('.py', '.ps1', '.cjs')))
    if slug in UNITY:
        for folder in (project / 'production/unity-source', project / 'production/local/unity-render/Assets/Lesson'):
            files.update(folder.rglob('*.cs'))
    # Static dependency manifests are separate from generated timing/caption JSON.
    files.add(ROOT / 'motion-canvas/package-lock.json')
    return {str(p.relative_to(ROOT)).replace('\\', '/'): sha(p) for p in sorted(files)}


def readiness_template():
    return dict(schemaVersion=1, revision=REVISION, internalProductionReadinessOnly=True, humanApprovalImplied=False,
                projects={slug: dict(codeReadyForActualProduction=False, productionCodeSha256=production_code_map(slug),
                                     note='Root sets true only after the assigned code/visual corrections and internal preparation are complete.')
                          for slug in [r['slug'] for r in authorization()]})


def require_readiness(slug):
    path = BATCH / 'local/finalizer-readiness.json'
    if not path.is_file():
        raise Deferred('Internal code-readiness signal is not present; no final production starts.')
    document = read(path)
    entry = document.get('projects', {}).get(slug, {})
    if document.get('revision') != REVISION or not document.get('internalProductionReadinessOnly') or entry.get('codeReadyForActualProduction') is not True:
        raise Deferred('Internal code-readiness for this project remains pending.')
    actual = production_code_map(slug)
    if entry.get('productionCodeSha256') != actual:
        raise Deferred('Internal code-readiness hashes changed; root must check the current static production code.')
    return actual


def resources(stage):
    """Read only. Do not stop a game, queue, editor or in-flight child job."""
    import psutil
    if shutil.disk_usage(ROOT).free < 64 * 2**20:
        raise Deferred('Workspace storage: D: needs at least 64 MiB for safe script/timing metadata writes. User was asked to free 2 GiB; media remains on C:.')
    queue_status = BATCH / 'local/voice-queue-status.json'
    try:
        queue = read(queue_status) if queue_status.exists() else {}
    except (ValueError, OSError):
        queue = {}
    current = psutil.Process()
    own = {os.getpid(), *(p.pid for p in current.parents()), *(p.pid for p in current.children(recursive=True))}
    busy, external, process_rows = [], [], []
    for proc in psutil.process_iter(['pid', 'ppid', 'name', 'cmdline', 'exe', 'create_time']):
        try:
            process_rows.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    coordinated = coordinated_queue_pids(process_rows, queue)
    for item in process_rows:
        try:
            if item['pid'] in own:
                continue
            name = (item['name'] or '').lower()
            command = ' '.join(item['cmdline'] or []).lower().replace('\\', '/')
            executable = (item['exe'] or '').lower().replace('\\', '/')
            if (name in GAME_NAMES and not is_unity_hub_server(item)) or ('/steamapps/common/' in executable and name.endswith('.exe') and 'crash' not in name):
                busy.append(dict(pid=item['pid'], name=item['name']))
            if is_python_interpreter(item) and 'generate-ready-voices.py' in command:
                if item['pid'] not in coordinated:
                    external.append(dict(pid=item['pid'], kind='uncoordinated-voice-queue'))
            elif is_python_interpreter(item) and any(token in command for token in ('render-voice.py', '/tts_runner.py', '/transcribe.py', 'finish-ready-videos.py')):
                external.append(dict(pid=item['pid'], kind='other-expensive-production-job'))
        except (psutil.NoSuchProcess, psutil.AccessDenied, TypeError):
            continue
    snapshot = dict(activeApps=busy, externalJobs=external, availableMemoryMiB=psutil.virtual_memory().available // 2**20)
    if busy or external:
        raise Deferred('Resource boundary: ' + json.dumps(snapshot, ensure_ascii=False))
    if snapshot['availableMemoryMiB'] < (5000 if 'asr' in stage else 2500):
        raise Deferred('Insufficient free system memory: ' + json.dumps(snapshot))
    if (ROOT / 'shared/output/GPU_HANDOFF.json').exists():
        raise Deferred('Another explicit GPU handoff is active; preserve it.')
    if stage == 'unity-capture':
        query = subprocess.run(['nvidia-smi', '--query-gpu=memory.free,utilization.gpu', '--format=csv,noheader,nounits'],
                               capture_output=True, text=True, creationflags=CREATION_FLAGS)
        if query.returncode:
            raise Deferred('GPU availability could not be verified before the Unity stage.')
        values = [tuple(map(int, line.strip().split(','))) for line in query.stdout.splitlines() if line.strip()]
        if not values or any(free < 4800 or usage >= 35 for free, usage in values):
            raise Deferred('GPU remains busy; even CPU/WARP Unity capture waits for the user resource boundary.')
    if shutil.disk_usage(MEDIA_ROOT).free < 8 * 2**30:
        raise Deferred('Fewer than 8 GiB free on the verified C: media volume.')
    return snapshot


def visual_command(slug):
    p = ROOT / 'projects' / slug / 'production'
    if slug in TRIO:
        return [sys.executable, '-X', 'utf8', str(ROOT / 'projects/shorts-noita-material-pixels/production/prepare-actual-visuals.py'), '--slug', slug]
    if slug in ARCH:
        return [sys.executable, '-X', 'utf8', str(BATCH / 'prepare-architecture-visuals.py'), '--actual', '--slug', slug]
    if slug in DIABLO:
        return [sys.executable, '-X', 'utf8', str(ROOT / 'projects/shorts-d2r-ultrawide-ai-range/production/prepare-exact-visuals.py'), DIABLO[slug]]
    if slug in UNITY:
        return ['powershell.exe', '-NoProfile', '-File', str(p / 'run-after-voice.ps1'), '-CaptureOnly']
    raise RuntimeError('No explicit preparation route for ' + slug)


def commands(slug, frames='ACTUAL_CAPTION_FRAMES', render_name='UNIQUE_HASHED_RENDER_NAME'):
    p = ROOT / 'projects' / slug / 'production'
    py = [sys.executable, '-X', 'utf8']
    return [
        ('voice-asr', [str(VOICE_PYTHON), '-X', 'utf8', str(p / 'transcribe.py'), 'voice']),
        ('strict-caption-timing', py + [str(p / 'time-captions.py')]),
        ('unity-capture' if slug in UNITY else 'actual-visual-preparation', visual_command(slug)),
        ('visual-render', ['node', str(BATCH / 'render-one.cjs'), slug, render_name, '0', str(frames)]),
        ('audio-mix', [str(VOICE_PYTHON), '-X', 'utf8', str(p / 'finish-audio.py'), 'mix']),
        ('audio-report', [str(VOICE_PYTHON), '-X', 'utf8', str(p / 'finish-audio.py'), 'report']),
        ('mix-asr', [str(VOICE_PYTHON), '-X', 'utf8', str(p / 'transcribe.py'), 'mix']),
        ('video-pair', py + [str(p / 'finish-video.py'), 'pair', '--visual', str(MEDIA_ROOT / 'motion-canvas-output' / (render_name + '.mp4'))]),
        ('video-integrity', py + [str(p / 'finish-video.py'), 'integrity']),
        ('qa-artifact-generation', py + [str(p / 'finish-video.py'), 'qa']),
    ]


def publishing_metadata(project):
    """Honor existing text metadata, falling back to the preserved draft schema."""
    folder = project / 'publishing'
    draft_path = folder / 'metadata-draft.json'
    draft = read(draft_path) if draft_path.is_file() else {}
    sources, values = [], {}
    for key, filename, field in [('title', 'title.ko.txt', 'titleKo'), ('description', 'description.ko.txt', 'descriptionKo')]:
        path = folder / filename
        if path.is_file():
            values[key] = path.read_text(encoding='utf8').strip(); sources.append(path)
        else:
            values[key] = draft.get(field, '').strip(); sources.append(draft_path)
        if not values[key]:
            raise RuntimeError('No exact publishing ' + key + ' prepared for ' + project.name)
    values['sourceFiles'] = sorted(set(sources))
    return values


def static_project_inputs(project):
    inputs = [project / 'script/narration.spoken.ko.json', project / 'script/clauses.json',
              project / 'sources/selected-footage.json', project / 'production/local/static-header-v1.png']
    if project.name in UNITY:
        inputs += [project / 'planning/production-plan.json', project / 'production/visual-timing.draft.json']
    else:
        inputs.append(project / 'production/section-plan.json')
    return inputs + publishing_metadata(project)['sourceFiles']


def prerequisite_paths(project):
    """All current inputs; intentionally excludes not-yet-produced PCM/captions."""
    paths = set(static_project_inputs(project))
    evidence = read(project / 'sources/selected-footage.json')
    def scan(value):
        if isinstance(value, dict):
            for key, item in value.items():
                if isinstance(item, str) and key in ('path', 'source', 'rightsReceipt') and not item.startswith(('https:', 'http:')) and Path(item).suffix.lower() in ('.mp4', '.mov', '.webm', '.json'):
                    paths.add(ROOT / item)
                elif isinstance(item, (dict, list)):
                    scan(item)
        elif isinstance(value, list):
            for item in value: scan(item)
    scan(evidence)
    music = ROOT / 'shared/assets/music/incompetech/Pixel-Peeker-Polka-faster.mp3'
    paths.update([music, music.with_suffix('.LICENSE.md'),
                  ROOT / 'shared/assets/branding/cat-reactions-v1/realize.png',
                  ROOT / 'shared/assets/branding/cat-reactions-v1/relief.png'])
    if project.name in UNITY:
        paths.update([Path('C:/Program Files/Unity/Hub/Editor/6000.6.0f1/Editor/Unity.exe'),
                      project / 'production/local/unity-render/ProjectSettings/ProjectVersion.txt'])
    return sorted(paths)


def validate_plan(slugs):
    authorization()
    if not VOICE_PYTHON.is_file():
        raise RuntimeError('The existing Whisper/Qwen environment is missing.')
    for tool in ('node', 'ffmpeg', 'ffprobe', 'powershell.exe'):
        if not shutil.which(tool):
            raise RuntimeError('Required executable unavailable: ' + tool)
    plans = []
    for slug in slugs:
        authorization(slug)
        rows = commands(slug)
        for _, command in rows:
            for arg in command:
                if arg.endswith(('.py', '.cjs', '.ps1')) and not Path(arg).is_file():
                    raise RuntimeError('Missing stage script: ' + arg)
        code = production_code_map(slug)
        project = ROOT / 'projects' / slug
        metadata = publishing_metadata(project)
        prerequisites = prerequisite_paths(project)
        missing = [str(p) for p in prerequisites if not p.is_file()]
        if missing:
            raise RuntimeError('Current non-PCM prerequisite missing for ' + slug + ': ' + ', '.join(missing))
        plans.append(dict(slug=slug, exactTitle=metadata['title'], metadataSources=[str(p) for p in metadata['sourceFiles']], verifiedExistingPrerequisites=[str(p) for p in prerequisites], staticProductionCodeFiles=len(code), commands=[dict(stage=name, argv=argv) for name, argv in rows],
                          playbackAndListening='pending, never inferred from technical tools'))
    print(text_json(dict(mode='validated-command-plan-only', mediaJobsStarted=0, filesystemOutputsWritten=0,
                         serialProtocol=LOCK_PROTOCOL, lock=str(MEDIA_ROOT / 'locks/serial-job.lock'), projects=plans)))


def probe(path):
    result = subprocess.run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(path)],
                            capture_output=True, text=True, creationflags=CREATION_FLAGS)
    if result.returncode:
        raise RuntimeError('Media probe failed: ' + result.stderr[-2000:])
    return json.loads(result.stdout)


def actual_captions(project):
    a = project / 'production/local/audio-v1'
    voice = a / 'voice/narration.wav'
    c = read(project / 'script/captions.json')
    inputs = c.get('timingInputs', {})
    for key, path in [('voiceSha256', voice), ('clausesSha256', project / 'script/clauses.json'),
                      ('narrationSha256', project / 'script/narration.spoken.ko.json')]:
        if inputs.get(key) != sha(path):
            raise RuntimeError('Actual caption input mismatch: ' + key)
    import soundfile as sf  # The approved assembler writes IEEE FLOAT WAV, not only integer PCM.
    audio = sf.info(voice)
    duration = audio.frames / audio.samplerate
    expected = math.ceil((duration + .2 + .4) * 60 - 1e-8)
    if c.get('revision') != REVISION or c.get('fps') != 60 or c.get('frames') != expected or abs(c['durationSeconds'] - expected / 60) > 1e-7:
        raise RuntimeError('Actual PCM/60fps caption duration contract differs.')
    if abs(c.get('voiceOffsetSeconds', -1) - .2) > 1e-8:
        raise RuntimeError('The already-applied voice offset must be 0.20 seconds.')
    canonical = read(project / 'script/clauses.json')['clauses']
    if [x['id'] for x in c['cues']] != [x['id'] for x in canonical]:
        raise RuntimeError('Canonical cue IDs, including b-clauses, must remain intact.')
    alignment = read(a / 'caption-alignment.json')
    if alignment.get('normalizedCoverageExact') is not True:
        raise RuntimeError('Strict caption coverage has not passed. Never fabricate ASR reconciliation.')
    return c


def validate_timing(project):
    c = actual_captions(project)
    path = project / 'production/visual-timing.json'
    local = project / 'production/local/visual-timing.json'
    if sha(path) != sha(local):
        raise RuntimeError('Render and audio must consume identical actual visual timing.')
    timing = read(path)
    if timing.get('previewOnly') or timing.get('revision') != REVISION or timing.get('frames') != c['frames']:
        raise RuntimeError('Full render needs the actual current caption frame count.')
    cursor = 0
    for row in timing['sections']:
        if row['startFrame'] != cursor or row['endFrame'] <= cursor:
            raise RuntimeError('Visual sections have a frame gap/overlap.')
        for key in ('start', 'end'):
            if abs(row[key] - row[key + 'Frame'] / 60) > 1e-7:
                raise RuntimeError('Frame/second visual timing differs.')
        if row['kind'] == 'game':
            source = timing['sources'][row['source']]
            if float(row.get('rate', 1)) != 1:
                raise RuntimeError('Game footage must remain native speed.')
            if 'sourceEnd' in row and abs(row['sourceEnd'] - row['sourceStart'] - (row['end'] - row['start'])) > 1/60 + 1e-7:
                raise RuntimeError('Source interval differs from visual duration.')
            if not any(key in row or key in source for key in ('nativeAudioAdopted', 'sourceAudioAdopted')):
                raise RuntimeError('Source audio adoption must be explicit.')
        cursor = row['endFrame']
    if cursor != c['frames']:
        raise RuntimeError('Visual sections do not cover all caption frames.')
    for source in timing['sources'].values():
        path = ROOT / source['path']
        if source.get('sourceSHA256') != sha(path):
            raise RuntimeError('Registered source hash differs from current source.')
    return timing


def resolved_frame_root(project, value, repo_relative=False):
    raw = Path(value)
    path = raw if raw.is_absolute() else ROOT / raw if repo_relative or raw.parts[0] == 'projects' else project / 'production/local' / raw
    if not path.resolve().is_relative_to((project / 'production/local').resolve()):
        raise RuntimeError('Frame root escaped this selected project: ' + str(path))
    return path


def frame_inventory(project, timing):
    local = project / 'production/local'
    folders = []
    slug = project.name
    if slug in TRIO:
        folders = [(ROOT / row['path'], row['frames']) for row in timing['preparedFrames']]
    elif slug in UNITY:
        folders = [(local / timing['nativeFolder'], timing['nativeFrames'])]
        folders += [(local / timing['gameFramesFolder'] / s['id'], s['endFrame'] - s['startFrame'])
                    for s in timing['sections'] if s['kind'] == 'game']
    elif slug in DIABLO:
        root = timing.get('frameRoot')
        # Exact Diablo helper publishes the repo-relative *game folder*, unlike
        # architecture's local-relative family root containing section folders.
        root_path = resolved_frame_root(project, root) if root else local / 'game-frames/game'
        folders = [(root_path, sum(s['endFrame'] - s['startFrame'] for s in timing['sections'] if s['kind'] == 'game'))]
    else:
        root = timing.get('frameRoot', 'game-frames')
        root_path = resolved_frame_root(project, root)
        folders = [(root_path / s['id'], s['endFrame'] - s['startFrame']) for s in timing['sections'] if s['kind'] == 'game']
    result = []
    for folder, count in folders:
        if not folder.resolve().is_relative_to(MEDIA_ROOT.resolve()):
            raise RuntimeError('Frame directory escaped the owned batch media volume.')
        files = sorted(folder.glob('*.jpg'))
        if [p.name for p in files] != [f'{i:05}.jpg' for i in range(count)]:
            raise RuntimeError('Missing/extra source frames in ' + str(folder))
        result.append(dict(folder=str(folder), frames=count, files=[artifact(path) for path in files]))
    return result


class ProjectRun:
    def __init__(self, slug, lock, retry=False):
        self.project = ROOT / 'projects' / slug
        self.slug, self.lock = slug, lock
        self.local = self.project / 'production/local'
        self.audio = self.local / 'audio-v1'
        self.directory = self.local / 'finite-finalizer-v1'
        self.state_path = self.directory / 'state.json'
        voice = self.audio / 'voice/narration.wav'
        required = [voice, self.audio / 'voice/narration.timing.json', self.audio / 'line-levels.json']
        if not all(x.is_file() for x in required):
            raise Deferred('Actual PCM, paragraph timing or line-level evidence is not ready.')
        inputs = [*required, *static_project_inputs(self.project)]
        levels = read(self.audio / 'line-levels.json')
        if levels.get('voiceSha256') != sha(voice) or levels.get('allRawPcmPreserved') is not True:
            raise Deferred('Actual PCM paragraph matching evidence is not ready for this voice hash.')
        self.inputs = [artifact(path) for path in inputs]
        self.code = require_readiness(slug)
        self.fingerprint = hashlib.sha256(text_json(dict(inputs=self.inputs, productionCodeSha256=self.code)).encode()).hexdigest()
        self.state = read(self.state_path) if self.state_path.exists() else dict(schemaVersion=1, revision=REVISION,
                    slug=slug, fingerprint=self.fingerprint, inputs=self.inputs, stages={}, createdAt=now(),
                    humanReview='pending', completeListening='pending', fullMovingReview='pending', platformActionsPerformed=False)
        if self.state.get('fingerprint') != self.fingerprint:
            raise RuntimeError('Finalizer inputs changed. Preserve/version the previous run before continuing.')
        if self.state.get('status') == 'failed' and not retry:
            raise Deferred('Prior failed stage is preserved. Inspect its log and use --retry-failed after resolving it.')
        self.current = 'initial-validation'

    def save(self):
        self.state['updatedAt'] = now()
        write_atomic(self.state_path, self.state)

    def stage(self, name, function):
        self.current = name
        authorization(self.slug)
        require_readiness(self.slug)
        previous = self.state['stages'].get(name)
        if previous and previous.get('status') == 'pass':
            verify_artifacts(previous['artifacts'])
            return previous.get('result', {})
        self.lock.set_stage(name)
        snapshot = resources(name)
        self.state.update(status='running', currentStage=name)
        if previous:
            self.state.setdefault('stageHistory', []).append(dict(stage=name, previous=previous))
        self.state['stages'][name] = dict(status='running', startedAt=now(), resources=snapshot)
        self.save()
        result, paths = function()
        self.state['stages'][name].update(status='pass', endedAt=now(), artifacts=[artifact(p) for p in paths], result=result)
        self.save()
        return result

    def run(self, name, command):
        self.directory.mkdir(parents=True, exist_ok=True)
        log = self.directory / ('log-' + name + '-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S') + '-' + uuid.uuid4().hex[:6] + '.txt')
        self.state['stages'][self.current].setdefault('commands', []).append(dict(argv=command, log=str(log)))
        self.save()
        print('STAGE_START', self.slug, name, flush=True)
        with log.open('x', encoding='utf8') as stream:
            stream.write(text_json(dict(argv=command, startedAt=now()))); stream.flush()
            result = subprocess.run(command, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT,
                                    creationflags=CREATION_FLAGS, env={**os.environ, 'PYTHONUTF8': '1'})
        if result.returncode:
            raise RuntimeError(f'{name} exited {result.returncode}; retained log: {log}')
        print('STAGE_END', self.slug, name, flush=True)
        return log

    def simple(self, name, command, outputs):
        self.run(name, command)
        return {}, outputs

    def asr(self, role, command):
        self.run(role + '-asr', command)
        source = self.audio / ('voice/narration.wav' if role == 'voice' else 'final-mix.m4a')
        target = self.audio / f'asr-{role}-{sha(source)[:12]}.json'
        result = read(target)
        if result.get('sha256') != sha(source) or result.get('role') != role or not result.get('fullInput') or not result.get('chunks'):
            raise RuntimeError('ASR cache lacks exact-hash complete-input evidence.')
        if result.get('expectedTextPromptUsed') is not False or result.get('rawRecognitionUnmodified') is not True:
            raise RuntimeError('ASR must be unprompted and preserve its raw recognition.')
        if result.get('expectedSourceSha256') != sha(self.project / 'script/narration.spoken.ko.json'):
            raise RuntimeError('ASR expected script fingerprint changed.')
        return dict(normalizedMatch=result.get('normalizedMatch'), similarity=result.get('similarity'),
                    humanListening='pending', rawAsrPreserved=True), [target]

    def captions(self, command):
        self.run('strict-caption-timing', command)
        c = actual_captions(self.project)
        return dict(frames=c['frames'], cues=len(c['cues']), manualReconciliationCreated=False), [
            self.project / 'script/captions.json', self.audio / 'caption-alignment.json', self.audio / 'caption-layout.json',
            self.audio / 'captions.ko.ass', self.audio / 'captions.ko.srt', self.audio / 'captions.en.srt']

    def visuals(self, command):
        archive = self.directory / 'preserved-pre-actual'
        for name in ('visual-timing.json', 'visual-config.json', 'scene-config.json'):
            path = self.project / 'production' / name
            if path.exists():
                immutable(archive / (path.stem + '-' + sha(path)[:12] + '.json'), path.read_text(encoding='utf8'))
        if self.slug in UNITY and (self.local / 'unity-capture').exists():
            success = self.local / 'unity-capture/success.json'
            phase = self.local / 'native-phase-plan.json'
            c = actual_captions(self.project)
            if not success.is_file() or not phase.is_file() or read(success).get('frames') != c['frames'] or read(phase).get('voiceSha256') != c['timingInputs']['voiceSha256']:
                raise RuntimeError('Existing Unity capture is incomplete or belongs to another PCM; preserve it.')
            command = [sys.executable, '-X', 'utf8', str(self.project / 'production/prepare-visual.py')]
        self.run('actual-visual-preparation', command)
        timing = validate_timing(self.project)
        inventory = frame_inventory(self.project, timing)
        target = self.directory / ('frame-inventory-' + sha(self.project / 'production/visual-timing.json')[:12] + '.json')
        immutable(target, inventory)
        return dict(frames=timing['frames'], frameFolders=len(inventory), inventory=str(target), humanViewing='pending'), [
            self.project / 'production/visual-timing.json', self.local / 'visual-timing.json', target]

    def render(self):
        c = actual_captions(self.project)
        validate_timing(self.project)
        prep_stage = 'unity-capture' if self.slug in UNITY else 'actual-visual-preparation'
        for row in read(self.state['stages'][prep_stage]['result']['inventory']):
            verify_artifacts(row['files'])
        # Code+actual timeline changes yield a new name; an old render never gets overwritten.
        inputs = [self.project / 'production/visual-timing.json', BATCH / 'render-one.cjs']
        inputs += sorted(mc_dependencies(mc_entry(self.slug)))
        digest = hashlib.sha256(text_json([artifact(p) for p in inputs]).encode()).hexdigest()
        name = self.slug + '-actual-' + digest[:12]
        output = MEDIA_ROOT / 'motion-canvas-output' / (name + '.mp4')
        receipt = self.local / (name + '-render.json')
        if not output.exists():
            self.run('visual-render', ['node', str(BATCH / 'render-one.cjs'), self.slug, name, '0', str(c['frames'])])
        if not receipt.exists():
            raise RuntimeError('Existing render has no successful receipt; preserve it before retrying.')
        record = read(receipt)
        if not record.get('done') or record.get('result') != 0 or record.get('errors'):
            raise RuntimeError('Motion Canvas did not report an error-free complete render.')
        v = next(row for row in probe(output)['streams'] if row['codec_type'] == 'video')
        if (v['width'], v['height'], v['r_frame_rate'], int(v['nb_frames'])) != (1080, 1920, '60/1', c['frames']):
            raise RuntimeError('Rendered picture is not the complete exact-frame FHD60 vertical master.')
        return dict(path=str(output), renderName=name, fullMovingReview='pending'), [output, receipt]

    def pair(self, visual):
        final = self.project / read(self.project / 'project.json')['currentFinalDirectory']
        build = final / 'pair-build.json'
        if (final / 'clean.mp4').exists() or (final / 'captioned.mp4').exists():
            if not build.exists():
                raise RuntimeError('Partial/unreceipted pair preserved; do not overwrite or silently repair.')
            b = read(build)
            checks = {'visual': Path(visual), 'audio': self.audio / 'final-mix.m4a', 'ass': self.audio / 'captions.ko.ass',
                      'clean': final / 'clean.mp4', 'captioned': final / 'captioned.mp4'}
            if any(not p.exists() or b.get(k) != sha(p) for k, p in checks.items()):
                raise RuntimeError('Existing successful pair differs from the current inputs.')
        else:
            self.run('video-pair', [sys.executable, '-X', 'utf8', str(self.project / 'production/finish-video.py'), 'pair', '--visual', visual])
        return dict(directory=str(final)), [final / 'clean.mp4', final / 'captioned.mp4', build]

    def finish(self):
        routes = dict(commands(self.slug))
        self.stage('voice-asr', lambda: self.asr('voice', routes['voice-asr']))
        self.stage('strict-caption-timing', lambda: self.captions(routes['strict-caption-timing']))
        prep_stage = 'unity-capture' if self.slug in UNITY else 'actual-visual-preparation'
        self.stage(prep_stage, lambda: self.visuals(routes[prep_stage]))
        rendered = self.stage('visual-render', self.render)
        self.stage('audio-mix', lambda: self.simple('audio-mix', routes['audio-mix'], [self.audio / 'audio-build.json', self.audio / 'final-mix.m4a']))
        self.stage('audio-report', lambda: self.simple('audio-report', routes['audio-report'], [self.audio / 'audio-continuity.json']))
        self.stage('mix-asr', lambda: self.asr('mix', routes['mix-asr']))
        pair = self.stage('video-pair', lambda: self.pair(rendered['path']))
        final = Path(pair['directory'])
        self.stage('video-integrity', lambda: self.simple('video-integrity', routes['video-integrity'], [final / 'integrity.json']))
        def qa():
            self.run('qa-artifact-generation', routes['qa-artifact-generation'])
            index = final / ('qa-sequential-' + sha(final / 'captioned.mp4')[:12]) / 'index.json'
            return dict(generatedOnly=True, humanViewed=False), [index, final / 'mobile-review.mp4']
        self.stage('qa-artifact-generation', qa)
        delivery = self.stage('local-delivery', lambda: self.deliver(final))
        self.state.update(status=delivery['status'], currentStage='local-delivery', delivery=delivery,
                          generatedForReview=True, internalVisualReview='pending', internalListeningReview='pending', actualHumanReview='pending',
                          humanReview='pending', completeListening='pending', fullMovingReview='pending', platformActionsPerformed=False)
        self.save()
        return self.state

    def deliver(self, final):
        integrity = read(final / 'integrity.json')
        if integrity.get('status') != 'pass' or integrity.get('identicalAac') is not True:
            raise RuntimeError('Pair technical integrity has not passed.')
        source_rows = [artifact(final / 'clean.mp4'), artifact(final / 'captioned.mp4'),
                       artifact(self.audio / 'captions.ko.srt'), artifact(self.audio / 'captions.en.srt')]
        digest = source_rows[1]['sha256']
        folder = MEDIA_ROOT / 'delivery' / self.slug / (REVISION + '-' + digest[:12])
        folder.mkdir(parents=True, exist_ok=True)
        files = []
        for row in source_rows:
            source = Path(row['path']); destination = folder / source.name
            if not destination.exists():
                temporary = destination.with_name(destination.name + '.' + uuid.uuid4().hex + '.partial')
                shutil.copy2(source, temporary)
                if sha(temporary) != row['sha256']:
                    raise RuntimeError('Delivery copy differs; partial file retained.')
                if destination.exists():
                    raise RuntimeError('Another delivery writer appeared; preserve both files.')
                temporary.rename(destination)
            if sha(destination) != row['sha256']:
                raise RuntimeError('Existing delivery version differs; never replace it.')
            files.append(artifact(destination))
        metadata = publishing_metadata(self.project)
        title, description = metadata['title'], metadata['description']
        continuity = read(self.audio / 'audio-continuity.json')
        mix_asr = self.state['stages']['mix-asr']['result']
        flags = dict(mixAsrExactMatch=mix_asr.get('normalizedMatch') is True,
                     sustainedAttenuation=continuity.get('sustainedEncodedAttenuationCandidates', []),
                     contextualListeningRanges=continuity.get('contextPlaybackRequiredRanges', []))
        status = 'review-files-generated-internal-review-pending' if flags['mixAsrExactMatch'] and not flags['sustainedAttenuation'] else 'review-files-generated-technical-issues-pending'
        result = dict(slug=self.slug, revision=REVISION, status=status, title=title, description=description,
                      directory=str(folder), captioned=str(folder / 'captioned.mp4'), masterSha256=digest, files=files,
                      evidence=dict(integrity=str(final / 'integrity.json'), audioReport=str(self.audio / 'audio-continuity.json'),
                                    qa=str(final / ('qa-sequential-' + digest[:12]) / 'index.json')),
                      generatedForReview=True, internalVisualReview='pending', internalListeningReview='pending', actualHumanReview='pending',
                      technicalFlags=flags, humanReview='pending', completeListening='pending', pronunciation='pending',
                      fullMovingReview='pending', mobileVisualReview='pending', youtubeUploaded=False, driveUploaded=False)
        result['sourceRightsRecord'] = artifact(self.project / 'sources/selected-footage.json')
        result['publicationClearance'] = 'Not granted or inferred by this local-only finalizer; preserve the source record conditions and any unresolved public/monetized-use limits.'
        immutable(folder / 'delivery.json', result)
        immutable(folder / 'title.ko.txt', title + '\n'); immutable(folder / 'description.ko.txt', description + '\n')
        speech_status = '문장 자동 대조에서 일치했습니다. 실제 발음과 듣기 편한지는 확인이 남아 있습니다.' if flags['mixAsrExactMatch'] else '음성 자동 대조에서 확인할 부분이 있습니다. 실제 청취가 필요합니다.'
        body = '<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>' + html.escape(title) + '</title><style>body{background:#090d0c;color:white;font:17px sans-serif;max-width:1000px;margin:auto;padding:22px}video{width:min(100%,375px);background:black}a{color:#73d7cd}pre{white-space:pre-wrap;overflow-wrap:anywhere}h1{color:#ffd25a;font-size:26px}</style><h1>' + html.escape(title) + '</h1><p>검수 파일이 생성되었습니다. 전체 영상·모바일 화면·발음·청취의 내부 검수와 사용자 최종검수는 남아 있습니다. 업로드되지 않았습니다.</p><video controls playsinline preload="metadata" src="captioned.mp4"></video><p><a href="clean.mp4">자막 없는 MP4</a> · <a href="captioned.mp4">전체 자막 MP4</a> · <a href="captions.ko.srt">한국어 자막</a> · <a href="captions.en.srt">영어 자막</a></p><p>' + speech_status + '</p><p><a href="delivery.json">파일 해시와 상세 검사 기록</a></p><pre>' + html.escape(description) + '</pre></html>'
        immutable(folder / 'index.html', body)
        return result, [folder / 'delivery.json', folder / 'index.html', *(Path(x['path']) for x in files)]


def display_status(row):
    status, category = row['status'], row.get('category', '')
    if 'workspace storage' in row.get('reason', '').lower(): return 'D드라이브 공간 확보 대기'
    if status == 'review-files-generated-internal-review-pending': return '검수 파일 생성됨'
    if status == 'review-files-generated-technical-issues-pending': return '검수 파일 생성됨 · 확인할 항목 있음'
    if category == 'actual-voice-not-ready': return '음성 생성 대기'
    if category == 'internal-code-readiness': return '제작 준비 확인 중'
    if category == 'resources-serial-lock': return '이전 작업 완료 대기'
    if category == 'asr-caption-alignment': return '음성·자막 확인 필요'
    if category == 'rights-or-credit-evidence': return '자료 사용조건 확인 필요'
    if status == 'deferred' and 'activeapps' in row.get('reason', '').lower(): return '게임·Unity 종료 대기'
    if status == 'deferred': return '작업 여건 확인 중'
    if status == 'failed': return '확인 필요한 문제'
    return '제작 대기'


def batch_index(status):
    folder = MEDIA_ROOT / 'delivery'
    entries = []
    for row in status['projects']:
        delivery = row.get('delivery')
        title = html.escape(row.get('title', row['slug']))
        if delivery:
            relative = Path(delivery['directory']).relative_to(folder).as_posix() + '/index.html'
            title = '<a href="' + html.escape(relative, quote=True) + '">' + title + '</a>'
        entries.append('<li>' + title + ' — ' + display_status(row) + '</li>')
    body = '<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="refresh" content="60"><title>얌얌코딩 쇼츠 10편 검수</title><style>body{background:#090d0c;color:white;font:18px sans-serif;max-width:900px;margin:30px auto;padding:20px}a{color:#73d7cd}li{margin:18px 0}h1{color:#ffd25a}</style><h1>쇼츠 10편 · 제작 상태</h1><p>영상 파일이 생성되면 아래 제목에서 볼 수 있습니다. 생성 이후 전체 영상·모바일 화면·발음·청취의 내부 검수와 사용자 최종검수는 별도로 진행합니다. 아직 업로드하지 않았습니다.</p><ul>' + ''.join(entries) + '</ul><p><a href="status.json">상세 제작 기록</a></p></html>'
    write_atomic(folder / 'index.html', body)
    write_atomic(folder / 'status.json', status)


def execute(slugs, wait_minutes, retry):
    run_id = datetime.datetime.now().strftime('%Y%m%d-%H%M%S') + '-' + uuid.uuid4().hex[:6]
    run_path = BATCH / 'local/finalizer-runs' / (run_id + '.json')
    deadline = time.monotonic() + wait_minutes * 60
    rows = {row['slug']: row for row in authorization()}
    status = dict(runId=run_id, startedAt=now(), finiteBatch=True, serialProtocol=LOCK_PROTOCOL,
                  youtubeActions=False, driveActions=False, humanReview='pending', projects=[])
    results = {slug: dict(slug=slug, title=rows[slug]['title'], status='pending') for slug in slugs}
    terminal = set()
    while True:
        for slug in slugs:
            if slug in terminal:
                continue
            job = None
            try:
                authorization(slug)
                resources('project-start')
                with SerialJobLock(slug=slug, stage='project-start', wait_seconds=0) as lock:
                    job = ProjectRun(slug, lock, retry=retry)
                    result = job.finish()
                    results[slug].update(status=result['status'], title=result['delivery']['title'], delivery=result['delivery'], state=str(job.state_path))
                    terminal.add(slug)
            except (Deferred, JobBusy) as error:
                results[slug].update(status='deferred', reason=str(error), category=failure_category(job.current if job else 'prerequisite', error), checkedAt=now())
                if job:
                    job.state.update(status='deferred', currentStage=job.current, reason=str(error)); job.save()
            except Exception as error:
                results[slug].update(status='failed', reason=str(error), category=failure_category(job.current if job else 'prerequisite', error), checkedAt=now())
                if job:
                    category = failure_category(job.current, error)
                    job.state.update(status='failed', currentStage=job.current, reason=str(error), failureCategory=category)
                    if job.current in job.state['stages']:
                        job.state['stages'][job.current].update(status='failed', reason=str(error), category=category, endedAt=now())
                    job.save()
                    results[slug]['state'] = str(job.state_path)
                terminal.add(slug)
                print('PROJECT_FAILED', slug, str(error), flush=True)
            status['projects'] = list(results.values()); status['updatedAt'] = now()
            write_atomic(run_path, status); write_atomic(BATCH / 'local/finalizer-status.json', status); batch_index(status)
        if len(terminal) == len(slugs) or time.monotonic() >= deadline:
            break
        time.sleep(min(30, max(0, deadline - time.monotonic())))
    status.update(endedAt=now(), outcome='finite-pass-finished', unfinished=[r['slug'] for r in results.values() if r['status'] in ('deferred', 'failed')])
    write_atomic(run_path, status); write_atomic(BATCH / 'local/finalizer-status.json', status); batch_index(status)
    print(text_json(status))
    return 2 if status['unfinished'] else 0


def failure_category(stage, error):
    text = str(error).lower()
    if isinstance(error, JobBusy): return 'resources-serial-lock'
    if 'code-readiness' in text: return 'internal-code-readiness'
    if 'rights' in text or 'license' in text: return 'rights-or-credit-evidence'
    if 'authorization' in text or 'scope' in text: return 'authorization-scope'
    if 'not ready' in text and ('pcm' in text or 'paragraph' in text): return 'actual-voice-not-ready'
    if isinstance(error, Deferred): return 'resources-or-external-prerequisite'
    if 'asr' in stage or stage == 'strict-caption-timing': return 'asr-caption-alignment'
    if 'visual-preparation' in stage or stage == 'unity-capture' or 'source' in text: return 'source-or-native-scene'
    if stage.startswith('audio'): return 'audio-mix-or-measurement'
    if stage.startswith('video') or stage == 'visual-render': return 'render-or-encoded-integrity'
    return 'local-artifact-or-validation'


def self_test():
    # No subprocess, real lock, media, queue or production state is touched.
    assert not is_python_interpreter({'name':'pwsh.exe', 'cmdline':['-Command','python generate-ready-voices.py']})
    assert is_python_interpreter({'name':'python.exe', 'cmdline':['python','generate-ready-voices.py']})
    hub = dict(name='unity.exe', exe='C:/Program Files/Unity Hub/resources/unity.exe',
               cmdline=['C:/Program Files/Unity Hub/resources/unity.exe', 'serve'])
    assert is_unity_hub_server(hub)
    assert is_unity_hub_server({**hub, 'exe': hub['exe'].replace('/', '\\').upper()})
    assert not is_unity_hub_server({**hub, 'exe': 'C:/Program Files/Unity/Hub/Editor/6000.6.0f1/Editor/Unity.exe'})
    assert not is_unity_hub_server({**hub, 'cmdline': [hub['exe'], '-projectPath', 'D:/Game']})
    assert not is_unity_hub_server({**hub, 'cmdline': [hub['exe'], 'serve', '-projectPath', 'D:/Game']})
    assert not is_unity_hub_server({**hub, 'exe': None})
    assert not is_unity_hub_server({**hub, 'cmdline': None})
    assert set(TRIO | UNITY | ARCH | set(DIABLO)) == SLUGS and len(SLUGS) == 10
    for slug in sorted(SLUGS):
        planned = commands(slug, 3600, slug + '-test')
        assert len(planned) == 10 and planned[0][0] == 'voice-asr' and planned[-1][0] == 'qa-artifact-generation'
        assert all(isinstance(a, str) for _, command in planned for a in command)
        text = text_json(planned)
        assert 'render-voice.py' not in text and 'youtube' not in text.lower() and 'drive.google' not in text
        if slug in TRIO: assert planned[2][1][-2:] == ['--slug', slug]
        if slug in UNITY: assert planned[2][1][-1] == '-CaptureOnly'
        if slug in ARCH: assert '--actual' in planned[2][1]
        if slug in DIABLO: assert planned[2][1][-1] == DIABLO[slug]
    ast.parse(Path(__file__).read_text(encoding='utf8'))
    ast.parse((BATCH / 'batch_job_lock.py').read_text(encoding='utf8'))
    queue = str(BATCH / 'generate-ready-voices.py')
    fake = [dict(pid=10, ppid=1, create_time=1., cmdline=['python.exe', queue]),
            dict(pid=11, ppid=10, create_time=2., cmdline=['python.exe', queue]),
            dict(pid=12, ppid=1, create_time=3., cmdline=['python.exe', queue]),
            dict(pid=13, ppid=11, create_time=4., cmdline=['python.exe', 'render-voice.py'])]
    status = dict(serialProtocol=LOCK_PROTOCOL, pid=11, processCreateTime=2.)
    assert coordinated_queue_pids(fake, status) == {10, 11}
    assert coordinated_queue_pids(fake, {**status, 'processCreateTime': 0.}) == set()
    assert coordinated_queue_pids(fake, {**status, 'serialProtocol': 'other'}) == set()
    assert failure_category('strict-caption-timing', RuntimeError('mismatch')) == 'asr-caption-alignment'
    assert failure_category('audio-mix', RuntimeError('missing license')) == 'rights-or-credit-evidence'
    for slug in SLUGS:
        p = ROOT / 'projects' / slug
        assert resolved_frame_root(p, f'projects/{slug}/production/local/test/game') == p / 'production/local/test/game'
        assert resolved_frame_root(p, 'game-frames/test') == p / 'production/local/game-frames/test'
    print('Pure plan checks passed for ten exact routes, strict caption stage, serial design and local-only boundary. No production jobs run.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--execute', action='store_true')
    group.add_argument('--validate-only', action='store_true')
    group.add_argument('--self-test', action='store_true')
    group.add_argument('--readiness-template', action='store_true')
    parser.add_argument('--slug', action='append', choices=sorted(SLUGS))
    parser.add_argument('--wait-minutes', type=float, default=0)
    parser.add_argument('--retry-failed', action='store_true')
    args = parser.parse_args()
    if not 0 <= args.wait_minutes <= 720:
        parser.error('Bounded waiting must be between 0 and 720 minutes.')
    if args.self_test:
        self_test(); return
    if args.readiness_template:
        print(text_json(readiness_template())); return
    selected = set(args.slug or SLUGS)
    slugs = [r['slug'] for r in authorization() if r['slug'] in selected]
    if not args.execute:
        validate_plan(slugs); return
    raise SystemExit(execute(slugs, args.wait_minutes, args.retry_failed))


if __name__ == '__main__':
    main()
