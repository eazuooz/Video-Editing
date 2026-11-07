"""Fixed11.05 V6 repaired-voice independent blind ASR; default reads readiness only.

Reuses the reviewed recognizer/cache/level/lifecycle code without changing it.
Only --execute can queue ASR; --levels is a separate explicit CPU operation.
No synthesis, audio editing, implicit speech pass, aliasing or human approval.
"""
from __future__ import annotations
import copy, hashlib, importlib.util, math, os, re, sys
from pathlib import Path
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SELF_SHA = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
# Exact independent repairV2 freeze; missing pins always block import/execution.
EXPECTED_REPAIR_VOICE_FP = '6691614beecda682a8130136a3dfd952b472e7acdba769a83cd1ca7212df8cc1'
PINS = {
    'run-solution-path-voice-qa-v5.py': '1e03fc9b071e2542c662e2d27c6a8a5bcff65402c9e769d56dcf9d0bc7c7437c',
    'run-solution-path-voice-repair-v2.py': '06825b9fbfd213b6a1a0dcfdf73ece0e3d46ca2624a6f8a5c3bbe182c37086a1',
    'prepare-solution-path-voice-repair-v2.py': '11377373c0a2d7624216f60e0219beed7601e2ec423bb9df7cf8aa88bcba95db',
    'run-selected-voice-repair-v4.py': 'c70ba7ff185f048bbb53c3b7845b5af2237d14de1ea3ef511e9afacdf8171366',
    'run-solution-path-voice-qa-v4.py': 'fe1fd24796ad659f4c1b4c6e09cc1ef53732b1e912947f310c5b35b4c34ce076',
    'run-selected-voice-qa.py': '65983206f0e0fa81dd5a5780871605fcc2665816a9f21fc3ea3a43781437e2a9',
    'run-selected-voice.py': '55ec247dafdef34bf2f31e9054e5a9fd3629ea2f220847b19694c48b59e26a99',
    'run-solution-path-voice-v4.py': 'f94852008cc919308b995866ac35510163f3eabd72de45066d6c5d0f60807910',
    'prepare-solution-path-voice-v4.py': '840889c38734f6a01511511bcfcdd1c123402fd387b2f6bda59e484555268292',
    'prepare-selected-voice.py': '7fc1afac8b7c44b7752f0b53620150cd0989238cc4cc5866a14f40480034a020',
    'approved-selected-voice-profile-v1.json': '378e12edc96c5d006ca9407ed36da13d1eff7e882cdc2670acdfd749b15b0075',
    'run-solution-path-native-v4.py': '9429b70773f3a334dd5fd45d76ecb6b2fa8b2360dfe576aac341099d7adaea5e',
    'prepare-solution-path-unity-v4.py': '74b9c7231f1a98b440d5aaee33a8de367436941e2c353730103f4aae56b8ffe0',
    'prospect-refuge-resource-qualification.py': '2dbb128a891fabf9c440e5790b88481c7901fbf087098557c540b19b8ecd5f5d',
    'run-first-native.py': 'a38205dac134e58da35a772290f0a151c7377b115b89910585277de76983a1f9',
    'run-zen-view-native.py': '64ebe5e6c2c44ef9e461e3ae82c875637ea1ba6be63fdceb049e105274154943',
    'initialize.py': '3968ca6abe9c8c4c35f67b55427dfaec8bd083af0bac1c30d85b674a383df179',
}

LAUNCHER_RUNTIME_PINS = [{'path': 'D:\\Github\\VideoEditing\\qwen3-tts\\.venv\\Scripts\\python.exe', 'sha256': 'cac98e94324b5462d41a5c6ad1847b57508a1068ba56014cf67a3d33a493dcdf'}, {'path': 'D:\\Github\\VideoEditing\\qwen3-tts\\.venv\\pyvenv.cfg', 'sha256': '2a28384eeef94485ae21f13ab5721d9dbe14d0736111b0ea2cc05212ea19c5e4'}, {'path': 'C:\\Anaconda3\\envs\\pytorch-gpu\\python.exe', 'sha256': '124cbe6203f939ff138c0ce68e26c12e4ca5836562286572ed040173daf0b787'}]


def check_sources():
    if hashlib.sha256(Path(__file__).read_bytes()).hexdigest() != SELF_SHA:
        raise RuntimeError('ASR adapter changed after import')
    if EXPECTED_REPAIR_VOICE_FP is None or any(value is None for value in PINS.values()):
        raise RuntimeError('Current repairV2 sources/fingerprint not frozen; ASR V6 is unexecutable')
    for row in LAUNCHER_RUNTIME_PINS:
        if hashlib.sha256(Path(row['path']).read_bytes()).hexdigest() != row['sha256']:
            raise RuntimeError('Reviewed Windows launcher/runtime changed: ' + row['path'])
    for name, expected in PINS.items():
        if hashlib.sha256((HERE / name).read_bytes()).hexdigest() != expected:
            raise RuntimeError('Reviewed ASR/voice/resource source changed: ' + name)


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    sys.modules[name] = result
    spec.loader.exec_module(result)
    return result


check_sources()
BASE_PATH = HERE / 'run-selected-voice-qa.py'
qa = module('solution_v6_private_asr_core', BASE_PATH)
voice_worker = module('solution_v6_private_voice_entry', HERE / 'run-solution-path-voice-repair-v2.py')
qa.voice = voice_worker.base
repair = voice_worker.prep
prep = repair.prep
resource = repair.voice_entry.resource
TOPIC, SLUG = '11.05', 'shorts-leveldesign-11-05'
PROTOCOL, OWNER = 'architectural111-11-05-voice-asr-v6', 'architectural-111-11-05-asr-v6'
MEDIA = qa.MEDIA
PROOF, VOICE_STATE = MEDIA / '11-05-voice-evidence.json', MEDIA / '11-05-voice-progress.json'
STATE, WORKER = MEDIA / '11-05-asr-v6-progress.json', MEDIA / '11-05-asr-v6-worker.json'
Pending, PROFILE, MODEL = qa.Pending, qa.PROFILE, qa.MODEL
PROFILE_PATH = HERE / 'approved-selected-voice-profile-v1.json'
LEGACY_MARKERS = tuple(MEDIA / name for name in (
    '11-05-asr-v4-progress.json', '11-05-asr-v4-worker.json',
    '11-05-asr-v5-progress.json', '11-05-asr-v5-worker.json'))
LEGACY_ENTRIES = frozenset(('run-solution-path-voice-qa-v4.py', 'run-solution-path-voice-qa-v5.py'))


def legacy_barrier():
    """Read only: preserve all V4/V5 workers, unknown markers and unregistered children."""
    for path in LEGACY_MARKERS:
        if not path.exists():
            continue
        try:
            row = qa.read(path)
        except (OSError, ValueError):
            raise Pending('Uninspected V4/V5 ASR state/worker preserved')
        if not isinstance(row, dict) or qa.voice.alive(row) or qa.voice.alive(row.get('child')):
            raise Pending('Old V4/V5 ASR coordinator/child is live or uninspected; controlled handoff required')
    for process in qa.psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            args = process.info['cmdline']
            if args is None:
                if (process.info.get('name') or '').lower().startswith('python'):
                    raise Pending('Uninspected possible legacy Python recognizer preserved')
                continue
            if '--recognize' in args and any(Path(a).name in LEGACY_ENTRIES for a in args):
                raise Pending('Existing V4/V5 recognizer/launcher preserved; no V6 overlap')
        except qa.psutil.NoSuchProcess:
            continue
        except qa.psutil.AccessDenied:
            raise Pending('Possible legacy recognizer cannot be inspected; preserve it')


def profile_identity(scenes, profile):
    return dict(protocol=prep.PROTOCOL, topicId=TOPIC, scenes=scenes,
                tts={k: v for k, v in profile['tts'].items()
                     if k not in ('filenameStem', 'gpuMinimumFreeMiB', 'gpuProfileReason')},
                **{k: profile[k] for k in ('modelPins', 'referenceSHA256', 'referenceTextSHA256',
                                           'engine', 'guard', 'rawPcmPolicy')})


def source_context():
    # CP is only the current path/hash/selection cross-check. The actual versioned
    # narration must independently be finalized; CP alone never supplies prose.
    try:
        cp, path, draft, source = prep.current_inputs()
        prep.final_narration(draft, cp)
        script, mapping = prep.sentence_plan(draft, qa.sha(path))
    except (prep.Pending, FileNotFoundError) as exc:
        raise Pending(str(exc)) from exc
    if draft.get('topicId') != TOPIC or len(draft['narrationKo']) != 14 or len(draft['paragraphsEn']) != 14:
        raise ValueError('Exact current finalized14-paragraph source required')
    return path, draft, script, mapping


def prepared_repair():
    """No stage/hooks: reconstruct the exact current source-bound repair selection."""
    try:
        prov = repair.prepare()
    except (repair.Pending, prep.Pending, FileNotFoundError) as exc:
        raise Pending(str(exc)) from exc
    if prov['fingerprint'] != EXPECTED_REPAIR_VOICE_FP:
        raise Pending('Current frozen six-take repair identity differs')
    return prov


def verify_subset_engine(prov, out, proof):
    """Re-read the real six-take engine artifacts; never accept a summary alone."""
    selected, engine = prov['repair'], proof.get('engineOutputsPreserved', {})
    missing_ids = [s['id'] for s in selected['missing']]
    reuse_ids = [row['newSceneId'] for row in selected['rows']]
    if (engine.get('engineSceneScope') != 'missing-subset-only' or
        engine.get('engineSceneIds') != missing_ids or
        engine.get('engineSceneCount') != len(missing_ids) or
        engine.get('fullCanonicalSceneCount') != len(prov['identity']['scenes']) or
        engine.get('reusedSceneIds') != reuse_ids or
        engine.get('subsetAggregateAndTimingValidated') is not True):
        raise ValueError('Actual six-only engine/full48/reused42 scope proof differs')
    pins = engine.get('subsetInputs')
    names = ['narration-missing-only.json', 'voice-missing-only-manifest.json',
             'subset-repair-preparation.json', 'repair-adapter-source.py']
    if not isinstance(pins, list) or [Path(p.get('path', '')).name for p in pins] != names:
        raise ValueError('Four exact preserved subset-input proofs are required')
    paths = [Path(p['path']) for p in pins]
    scope = (ROOT/'projects'/SLUG/'production/voice-preparation').resolve()
    folder = paths[0].resolve().parent
    if (any(not p.is_absolute() or p.resolve().parent != folder for p in paths) or
        folder.name != 'repair-subset-'+selected['fingerprint'][:24] or
        folder.parent.parent != scope or re.fullmatch('[0-9a-f]{24}', folder.parent.name) is None):
        raise ValueError('Preserved subset inputs escaped the exact selected staging scope')
    for row in pins:
        if qa.pin(row['path']) != row:
            raise ValueError('Preserved subset input path/hash differs')
    if pins[3]['sha256'] != PINS['run-solution-path-voice-repair-v2.py']:
        raise ValueError('Actual subset adapter snapshot is not the reviewed V2 worker')
    # Current CP metadata can change the preparation folder. Inspect the actual
    # preserved paths instead of substituting fresh-stage names or rewriting it.
    subset = dict(prov, identity=dict(prov['identity'], scenes=selected['missing']))
    chunks, actual = voice_worker.life.original['validate_engine_outputs'](subset, out)
    if any(key not in engine or engine[key] != actual[key] for key in ('aggregateWav', 'timing', 'srt')):
        raise ValueError('Saved engine aggregate/timing/SRT do not match actual six-take artifacts')
    selected_raw = [row for scene,row in zip(prov['identity']['scenes'], proof['sceneWavs']) if scene['id'] in missing_ids]
    if chunks != selected_raw:
        raise ValueError('Actual six engine chunks differ from the full canonical proof')
    return engine


def exact_voice():
    check_sources()
    legacy_barrier()
    control = qa.read(ROOT / 'shared/publishing/video-production-control.json')[qa.AUTH_KEY]
    if (control.get('status') in ('paused', 'stopped', 'cancelled') or
        control.get('automaticAdvanceWithinExactList') is not True or
        control.get('automaticAdvanceOutsideList') is not False or
        control.get('humanFinalReviewRequired') is not True or control.get('youtubeAuthorized')):
        raise Pending('Exact111 local-review authority is inactive')
    if not PROOF.is_file() or not VOICE_STATE.is_file():
        raise Pending('Waiting for actual completed current11.05 repaired canonical voice')
    proof, state = qa.read(PROOF), qa.read(VOICE_STATE)
    # Old e51 V4 raw output remains preserved history; it cannot masquerade as
    # completed current NarV5 repair and must decline before profile/model reads.
    if (proof.get('fingerprint') != EXPECTED_REPAIR_VOICE_FP or
        'repairSelection' not in proof.get('identity', {})):
        raise Pending('Published voice pointer is old or not the exact completed six-take repair')
    if state.get('completed') is not True or qa.voice.alive(state.get('child')) or qa.voice.project_children(SLUG):
        raise Pending('Current11.05 Qwen child/evidence is not complete; preserve it')
    path, draft, script, mapping = source_context()
    prov = prepared_repair()
    out = Path(proof['output']).resolve()
    parent = (ROOT / 'shared/output/architectural-111-20261106/11-05/voice-attempts').resolve()
    identity = proof['identity']
    if (proof.get('topicId') != TOPIC or out.parent != parent or
        out.name != proof['fingerprint'][:24] or state.get('fingerprint') != proof['fingerprint'] or
        qa.digest(identity) != proof['fingerprint'] or identity != prov['identity'] or
        out != Path(prov['voiceOutputDirectory']).resolve()):
        raise ValueError('Wrong selected11.05 repaired canonical voice/output identity')
    scenes = [{'id': row['id'], 'lines': row['lines']} for row in script['scenes']]
    profile = qa.read(PROFILE_PATH)
    plain_identity = {k: v for k, v in identity.items() if k != 'repairSelection'}
    if (plain_identity != profile_identity(scenes, profile) or
        proof['paragraphMapping'] != mapping or mapping != prov['paragraphMapping']):
        raise ValueError('Current complete sentences,14-paragraph mapping or approved voice profile differ')
    selection, selected = identity['repairSelection'], prov['repair']
    if (len(scenes) != 48 or len(selected['rows']) != 42 or len(selected['missing']) != 6 or
        selection != selected['identity']['repairSelection'] or
        selection['newNarration'] != qa.pin(path) or
        [s['id'] for s in selected['missing']] != list(repair.TARGETS) or
        selection['repairSceneIds'] != list(repair.TARGETS)):
        raise ValueError('Current48/42/6 source-bound repair selection differs')
    # Full repair prov is essential: a base fingerprint/identity stub loses
    # immutable42-byte-reuse +6-only engine/request/repair-input receipt checks.
    current = voice_worker.life.verify_complete(prov, out)
    if current is None or any(current.get(k) != proof.get(k) for k in (
        'identity', 'sceneWavs', 'aggregateWav', 'timing', 'paragraphMapping',
        'repairProtocol', 'repairFingerprint', 'repairIdentity', 'reusedRawScenes',
        'newlyGeneratedSceneIds', 'engineOutputsPreserved')):
        raise ValueError('Immutable full repaired canonical voice proof differs')
    receipt = voice_worker.life.validate_receipt(prov, out)
    if qa.pin(path) not in receipt.get('inputs', []):
        raise ValueError('Final narration is not pinned by the actual immutable repair input receipt')
    if (proof.get('reusedRawScenes') != selected['rows'] or
        proof.get('newlyGeneratedSceneIds') != list(repair.TARGETS) or
        proof.get('engineSpokeFullCombinedScript') is not False or proof.get('rawSceneCount') != len(scenes)):
        raise ValueError('Completed proof does not preserve42 raw takes and six-only engine scope')
    verify_subset_engine(prov, out, proof)
    timing = qa.read(proof['timing']['path'])
    entries, position, pcm = timing.get('entries', []), 0, hashlib.sha256()
    if timing.get('sample_rate') != 24000 or len(entries) != len(scenes) or len(proof['sceneWavs']) != len(scenes):
        raise ValueError('Selected sentence/chunk/timing counts or raw sample rate differ')
    for scene, entry, wav in zip(scenes, entries, proof['sceneWavs']):
        if (Path(wav['path']).resolve() != out / 'chunks' / (scene['id'] + '-scene.wav') or
            entry['scene_id'] != scene['id'] or entry['text'] != ' '.join(scene['lines']) or
            type(wav.get('frames')) is not int or wav['frames'] <= 0):
            raise ValueError('Exact canonical scene/time/text/sample binding differs')
        expected = (position / 24000, (position + wav['frames']) / 24000)
        if any(type(entry.get(k)) not in (int, float) or not math.isfinite(entry[k]) or
               abs(entry[k] - t) > 1e-9 for k, t in zip(('start', 'end'), expected)):
            raise ValueError('Canonical take sample boundary differs')
        pcm.update(qa.pcm_bytes(wav['path']))
        position += wav['frames']
    if position != proof['aggregateWav']['frames'] or pcm.hexdigest() != proof['aggregateWav']['pcmSHA256']:
        raise ValueError('Canonical aggregate is not exact raw scene concatenation')
    return out, proof, timing, draft


_library_prepare_job = qa.prepare_job


def prepare_job():
    check_sources()
    job = copy.deepcopy(_library_prepare_job())
    path, draft, script, mapping = source_context()
    actual_proof = qa.read(PROOF)
    if actual_proof['fingerprint'] != EXPECTED_REPAIR_VOICE_FP or job['identity']['voiceFingerprint'] != EXPECTED_REPAIR_VOICE_FP:
        raise Pending('Repair publication changed while preparing blind windows')
    if ([t['expected'] for t in job['identity']['tasks'] if t['kind'] == 'take'] !=
        [row['lines'][0] for row in script['scenes']]):
        raise ValueError('Narration changed while preparing blind task windows')
    job['identity'].update(launcherRuntimePins=copy.deepcopy(LAUNCHER_RUNTIME_PINS), launcherClassification='exact-direct-venv-parent-base-child-argv0-and-tail-v6', commonAsrLibrarySHA256=PINS[BASE_PATH.name],
                           currentVoiceWorkerSHA256=PINS['run-solution-path-voice-repair-v2.py'],
                           currentRepairPreparerSHA256=PINS['prepare-solution-path-voice-repair-v2.py'],
                           repairSelection=copy.deepcopy(actual_proof['identity']['repairSelection']),
                           sourceNarration=qa.pin(path), paragraphMappingSHA256=qa.digest(mapping),
                           resourceSourcePins={name: PINS[name] for name in (
                               'run-solution-path-native-v4.py', 'prospect-refuge-resource-qualification.py',
                               'run-first-native.py')})
    job['fingerprint'] = qa.digest(job['identity'])
    job['output'] = str(Path(job['voiceOutput']) / 'review/independent-asr-selected-v1' / job['fingerprint'][:24])
    job['publishedVoiceEvidenceAudit'] = job['voiceEvidence']
    job['voiceEvidence'] = qa.pin(Path(job['voiceOutput']) / 'voice-complete-proof.json')
    job['sourcePins'] += [qa.pin(HERE / name) for name in PINS] + [qa.pin(path)] + copy.deepcopy(LAUNCHER_RUNTIME_PINS)
    job['sourcePins'] = list({r['path']: r for r in job['sourcePins']}.values())
    return job


def launcher_matches(info, own, parent):
    """Exact Dvenv stub -> pinned Cbase body; only argv[0] may differ.

    Actual observed Windows venv behavior rewrites the real interpreter's argv0.
    This classifies only its direct parent, never a lease/owner/threshold bypass.
    """
    try:
        required = ('pid', 'ppid', 'create_time', 'name', 'exe', 'cmdline')
        if any(any(k not in r or r[k] is None for k in required) for r in (info, own, parent)):
            return False
        if any(type(r[k]) is not int or r[k] <= 0 for r in (info, own, parent) for k in ('pid', 'ppid')):
            return False
        if (own['pid'] == parent['pid'] or own['ppid'] != parent['pid'] or info['pid'] != parent['pid'] or
            info['ppid'] != parent['ppid'] or info['name'].lower() != 'python.exe' or
            any(type(r['create_time']) not in (int, float) or not math.isfinite(r['create_time'])
                for r in (info, own, parent))):
            return False
        args, parent_args = own['cmdline'], parent['cmdline']
        if (not isinstance(args, list) or not isinstance(parent_args, list) or len(args) != 10 or
            len(parent_args) != 10 or not all(isinstance(a, str) for a in args + parent_args) or
            args[1:] != parent_args[1:] or args[1:4] != ['-u', '-X', 'utf8'] or
            Path(args[4]).resolve() != Path(__file__).resolve() or not Path(args[4]).is_absolute() or
            args[5:7] != ['--recognize', '--job'] or args[8] != '--resource-decline'):
            return False
        job, decline = Path(args[7]), Path(args[9])
        voice_root = (ROOT / 'shared/output/architectural-111-20261106/11-05/voice-attempts').resolve()
        if not job.is_absolute() or not decline.is_absolute():
            return False
        relative = job.resolve().relative_to(voice_root).parts
        if (len(relative) != 5 or re.fullmatch('[0-9a-f]{24}', relative[0]) is None or
            relative[1:3] != ('review', 'independent-asr-selected-v1') or
            re.fullmatch('[0-9a-f]{24}', relative[3]) is None or relative[4] != 'job.json' or
            decline.resolve().parent != job.resolve().parent or
            re.fullmatch('resource-decline-[0-9a-f]{8}\\.json', decline.name) is None):
            return False
        launcher, base = Path(LAUNCHER_RUNTIME_PINS[0]['path']), Path(LAUNCHER_RUNTIME_PINS[2]['path'])
        return (info['cmdline'] == parent_args and
                Path(parent_args[0]).resolve() == Path(qa.PYTHON).resolve() == launcher.resolve() and
                Path(args[0]).resolve() == Path(own['exe']).resolve() == base.resolve() and
                Path(info['exe']).resolve() == Path(parent['exe']).resolve() == Path(qa.PYTHON).resolve() and
                own['name'].lower() == parent['name'].lower() == 'python.exe' and
                abs(info['create_time'] - parent['create_time']) < .001 and
                parent['create_time'] > 0 and 0 <= own['create_time'] - parent['create_time'] < 30)
    except (KeyError, TypeError, ValueError, OSError):
        return False


_process_reason = resource.process_reason


def scoped_process_reason(info, own_pid, qualified=frozenset()):
    if os.name == 'nt' and info.get('pid') == os.getppid():
        try:
            fields = ['pid', 'ppid', 'create_time', 'name', 'exe', 'cmdline']
            own = qa.psutil.Process(os.getpid()).as_dict(fields)
            parent = qa.psutil.Process(own['ppid']).as_dict(fields)
            if launcher_matches(info, own, parent):
                return None
        except (qa.psutil.NoSuchProcess, qa.psutil.AccessDenied):
            pass  # Unknown identities go to the unchanged conservative classifier.
    return _process_reason(info, own_pid, qualified)


_library_resource_reason = qa.resource_reason


def resource_reason():
    check_sources()
    return _library_resource_reason()  # Existing shared lease +9GiB/<15% gates unchanged.


def child_processes():
    names = {Path(__file__).name, *LEGACY_ENTRIES, BASE_PATH.name, 'run-first-asr.py',
             'run-prospect-refuge-voice-qa.py', 'run-prospect-refuge-voice-qa-v2.py',
             'run-prospect-refuge-mix-asr.py', 'run-zen-view-mix-asr.py'}
    found = []
    for process in qa.psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            args = process.info['cmdline']
            if args is None:
                if (process.info.get('name') or '').lower().startswith('python'):
                    raise Pending('Uninspected Python arguments; preserve possible recognizer')
                continue
            if process.pid != os.getpid() and '--recognize' in args and any(Path(a).name in names for a in args):
                found.append(qa.voice.identity(process.pid))
        except qa.psutil.NoSuchProcess:
            continue
        except qa.psutil.AccessDenied:
            raise Pending('Possible recognizer child cannot be inspected; preserve it')
    return found


# All replacements are confined to newly imported private module instances.
resource.process_reason = scoped_process_reason
qa.SLUG, qa.TOPIC, qa.PROTOCOL, qa.OWNER = SLUG, TOPIC, PROTOCOL, OWNER
qa.PROOF, qa.VOICE_STATE, qa.STATE, qa.WORKER = PROOF, VOICE_STATE, STATE, WORKER
qa.raw.SLUG = SLUG
qa.runtime.PROTOCOL, qa.runtime.OWNER = PROTOCOL, OWNER
qa.__file__ = str(Path(__file__).resolve())
qa.exact_voice, qa.prepare_job = exact_voice, prepare_job
qa.resource_reason, qa.child_processes = resource_reason, child_processes
summary, cached, raw_level_review = qa.summary, qa.cached, qa.raw_level_review
sha, digest, pin = qa.sha, qa.digest, qa.pin

if __name__ == '__main__':
    qa.main()
