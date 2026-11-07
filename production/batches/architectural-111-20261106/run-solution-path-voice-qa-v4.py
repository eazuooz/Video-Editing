"""Fixed11.05 V4 independent blind ASR; default reads readiness only.

Reuses the reviewed recognizer/cache/level/lifecycle code without changing it.
Only --execute can queue ASR; --levels is a separate explicit CPU operation.
No synthesis, audio editing, implicit speech pass, aliasing or human approval.
"""
from __future__ import annotations
import copy, hashlib, importlib.util, math, os, sys
from pathlib import Path
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SELF_SHA = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
PINS = {
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


def check_sources():
    if hashlib.sha256(Path(__file__).read_bytes()).hexdigest() != SELF_SHA:
        raise RuntimeError('ASR adapter changed after import')
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
qa = module('solution_v4_private_asr_core', BASE_PATH)
voice_worker = module('solution_v4_private_voice_entry', HERE / 'run-solution-path-voice-v4.py')
qa.voice = voice_worker.base
prep = voice_worker.prep
TOPIC, SLUG = '11.05', 'shorts-leveldesign-11-05'
PROTOCOL, OWNER = 'architectural111-11-05-voice-asr-v4', 'architectural-111-11-05-asr-v4'
MEDIA = qa.MEDIA
PROOF, VOICE_STATE = MEDIA / '11-05-voice-evidence.json', MEDIA / '11-05-voice-progress.json'
STATE, WORKER = MEDIA / '11-05-asr-v4-progress.json', MEDIA / '11-05-asr-v4-worker.json'
Pending, PROFILE, MODEL = qa.Pending, qa.PROFILE, qa.MODEL
PROFILE_PATH = HERE / 'approved-selected-voice-profile-v1.json'


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


def exact_voice():
    check_sources()
    control = qa.read(ROOT / 'shared/publishing/video-production-control.json')[qa.AUTH_KEY]
    if (control.get('status') in ('paused', 'stopped', 'cancelled') or
        control.get('automaticAdvanceWithinExactList') is not True or
        control.get('automaticAdvanceOutsideList') is not False or
        control.get('humanFinalReviewRequired') is not True or control.get('youtubeAuthorized')):
        raise Pending('Exact111 local-review authority is inactive')
    if not PROOF.is_file() or not VOICE_STATE.is_file():
        raise Pending('Waiting for actual completed current11.05 V4 canonical voice')
    proof, state = qa.read(PROOF), qa.read(VOICE_STATE)
    if state.get('completed') is not True or qa.voice.alive(state.get('child')) or qa.voice.project_children(SLUG):
        raise Pending('Current11.05 Qwen child/evidence is not complete; preserve it')
    path, draft, script, mapping = source_context()
    out = Path(proof['output']).resolve()
    parent = (ROOT / 'shared/output/architectural-111-20261106/11-05/voice-attempts').resolve()
    identity = proof['identity']
    if (proof.get('topicId') != TOPIC or out.parent != parent or
        out.name != proof['fingerprint'][:24] or state.get('fingerprint') != proof['fingerprint'] or
        qa.digest(identity) != proof['fingerprint']):
        raise ValueError('Wrong selected11.05 canonical voice/output identity')
    scenes = [{'id': row['id'], 'lines': row['lines']} for row in script['scenes']]
    profile = qa.read(PROFILE_PATH)
    if identity != profile_identity(scenes, profile) or proof['paragraphMapping'] != mapping:
        raise ValueError('Current complete sentences,14-paragraph mapping or approved voice profile differ')
    current = qa.voice.verify_complete(dict(fingerprint=proof['fingerprint'], identity=identity), out)
    if current is None or any(current[k] != proof[k] for k in ('sceneWavs', 'aggregateWav', 'timing', 'paragraphMapping')):
        raise ValueError('Immutable selected canonical voice proof differs')
    receipt = qa.voice.validate_receipt(dict(fingerprint=proof['fingerprint'], identity=identity), out)
    if qa.pin(path) not in receipt.get('inputs', []):
        raise ValueError('Final narration is not pinned by the actual immutable voice input receipt')
    timing = qa.read(proof['timing']['path'])
    entries, position, pcm = timing.get('entries', []), 0, hashlib.sha256()
    if len(entries) != len(scenes) or len(proof['sceneWavs']) != len(scenes):
        raise ValueError('Selected sentence/chunk/timing counts differ')
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
    if ([t['expected'] for t in job['identity']['tasks'] if t['kind'] == 'take'] !=
        [row['lines'][0] for row in script['scenes']]):
        raise ValueError('Narration changed while preparing blind task windows')
    job['identity'].update(commonAsrLibrarySHA256=PINS[BASE_PATH.name],
                           currentVoiceWorkerSHA256=PINS['run-solution-path-voice-v4.py'],
                           sourceNarration=qa.pin(path), paragraphMappingSHA256=qa.digest(mapping),
                           resourceSourcePins={name: PINS[name] for name in (
                               'run-solution-path-native-v4.py', 'prospect-refuge-resource-qualification.py',
                               'run-first-native.py')})
    job['fingerprint'] = qa.digest(job['identity'])
    job['output'] = str(Path(job['voiceOutput']) / 'review/independent-asr-selected-v1' / job['fingerprint'][:24])
    job['publishedVoiceEvidenceAudit'] = job['voiceEvidence']
    job['voiceEvidence'] = qa.pin(Path(job['voiceOutput']) / 'voice-complete-proof.json')
    job['sourcePins'] += [qa.pin(HERE / name) for name in PINS] + [qa.pin(path)]
    job['sourcePins'] = list({r['path']: r for r in job['sourcePins']}.values())
    return job


def launcher_matches(info, own, parent):
    """Only our exact direct Windows venv launch stub, never an owner exception."""
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
        args = own['cmdline']
        if (not isinstance(args, list) or not args or '--recognize' not in args or
            not any(Path(a).resolve() == Path(__file__).resolve() for a in args if isinstance(a, str))):
            return False
        return (info['cmdline'] == parent['cmdline'] == args and
                Path(args[0]).resolve() == Path(qa.PYTHON).resolve() and
                Path(info['exe']).resolve() == Path(parent['exe']).resolve() == Path(qa.PYTHON).resolve() and
                own['name'].lower().startswith('python') and own['exe'].lower().endswith('python.exe') and
                abs(info['create_time'] - parent['create_time']) < .001 and
                0 <= own['create_time'] - parent['create_time'] < 30)
    except (KeyError, TypeError, ValueError, OSError):
        return False


_process_reason = voice_worker.resource.process_reason


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
    names = {Path(__file__).name, BASE_PATH.name, 'run-first-asr.py',
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
voice_worker.resource.process_reason = scoped_process_reason
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
