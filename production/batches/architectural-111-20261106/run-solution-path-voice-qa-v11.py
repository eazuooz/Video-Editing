"""Blind ASR and original-sentence level review for the exact 11.05 V7 voice."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import math
import os
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
SELF_SHA = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
TOPIC, SLUG = '11.05', 'shorts-leveldesign-11-05'
PROTOCOL, OWNER = 'architectural111-11-05-voice-asr-v11', 'architectural-111-11-05-asr-v11'
QA8 = HERE / 'run-solution-path-voice-qa-v8.py'
V7_WORKER = HERE / 'run-solution-path-voice-repair-v7.py'
V7_PREPARER = HERE / 'prepare-solution-path-voice-repair-v7.py'
V7_LIFECYCLE = HERE / 'run-selected-voice-repair-v4.py'
V7_PLAN = ROOT / 'projects' / SLUG / 'voice-subset-repair-plan-v7.json'
LEVEL_PRIMITIVE = HERE / 'first-level-continuity-review.py'
PREVIOUS_QA = HERE / 'run-solution-path-voice-qa-v10.py'
PINS = {
    PREVIOUS_QA: '875771be3da91dc973aadde82143caa50c05cb511b667d026866c2026a47533f',
    QA8: 'fb5cee2bed52d0b03faac1f6f0837802620fd467a7f5a14c6e2183b299dcff91',
    V7_WORKER: 'a1a3ec46902f876337c122e0cd328fb6fc0cf582b8ee138369de59714104d5df',
    V7_PREPARER: '4852da3df87f45a64b6c92d93bb03caa01fe133132caf0ecf65037a0e199198b',
    V7_LIFECYCLE: 'c70ba7ff185f048bbb53c3b7845b5af2237d14de1ea3ef511e9afacdf8171366',
    V7_PLAN: '7ad1901c0d92675fe0e6b237dbbca39cf1aa450af097dcc8d429dd9f19a42b30',
    LEVEL_PRIMITIVE: '545104df16cf26af0c0637faa76750bea1e5b70f424cc13820f13baa8b773544',
}
EXPECTED_REPAIR_VOICE_FP = '2de4412bebf5e0bbae2154f5d8188db156c1a6602313c363843ecd5fe96f762b'
EXPECTED_REPAIR_FP = '79f449e27a5f5e35291ccf2de87c42d6e936586cb41a0197b58162cba3c3e82e'
TARGETS = ('p008-c01', 'p013-c01')
TAKE_COUNT, REUSE_COUNT, PARAGRAPH_COUNT = 48, 46, 14
JOIN_COUNT = TAKE_COUNT - 1


class SourceFreezePending(RuntimeError):
    pass


def sha(path):
    with Path(path).open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def check_sources():
    if sha(__file__) != SELF_SHA:
        raise RuntimeError('QA11 adapter changed after import')
    digests = (EXPECTED_REPAIR_VOICE_FP, EXPECTED_REPAIR_FP, *PINS.values())
    if any(not isinstance(value, str) or re.fullmatch('[0-9a-f]{64}', value) is None
           for value in digests):
        raise SourceFreezePending('Waiting for the exact reviewed V7 source and voice pins')
    for path, expected in PINS.items():
        if sha(path) != expected:
            raise RuntimeError('Reviewed QA11 input source changed: ' + str(path))
    if 'qa8' in globals():
        qa8.check_sources()
    if 'qa10' in globals():
        qa10.check_sources()
    if 'voice_worker' in globals():
        voice_worker.check_sources()


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = result
    spec.loader.exec_module(result)
    return result


try:
    check_sources()
except SourceFreezePending as exc:
    if __name__ == '__main__':
        print(json.dumps(dict(ready=False, reason=str(exc), protocol=PROTOCOL,
                              modelLoaded=False, staged=False)))
        raise SystemExit(2 if any(a in sys.argv[1:] for a in ('--execute', '--recognize', '--levels')) else 0)
    raise

# The imported controller and its globals are private to this adapter. QA8
# evidence, files, original-sentence review, and source pins are read-only.
qa8 = module('solution_v11_private_qa8', QA8)
qa10 = module('solution_v11_immutable_qa10', PREVIOUS_QA)
voice_worker = module('solution_v11_private_voice_repair', V7_WORKER)
qa7, qa, repair = qa8.qa7, qa8.qa, voice_worker.prep
Pending, PROFILE, MODEL = qa.Pending, qa.PROFILE, qa.MODEL
MEDIA, PROOF, VOICE_STATE, VOICE_ROOT = qa8.MEDIA, qa8.PROOF, qa8.VOICE_STATE, qa8.VOICE_ROOT
STATE, WORKER = MEDIA / '11-05-asr-v11-progress.json', MEDIA / '11-05-asr-v11-worker.json'
pin, digest = qa.pin, qa.digest


def legacy_barrier():
    qa10.legacy_barrier()
    for path in (qa10.STATE, qa10.WORKER):
        if not path.exists():
            continue
        try:
            row = qa.read(path)
        except (OSError, ValueError) as exc:
            raise Pending('Uninspected QA10 state or worker preserved') from exc
        if (not qa7.inspected_identity(row) or row.get('protocol') != qa10.PROTOCOL or
                row.get('owner') != qa10.OWNER):
            raise Pending('Unknown QA10 owner identity preserved')
        child = row.get('child')
        if child is not None and not qa7.inspected_identity(child):
            raise Pending('Unknown QA10 child identity preserved')
        if row.get('phase') == 'launching' and child is None:
            raise Pending('Unresolved QA10 durable launch gap preserved')
        if qa.voice.alive(row) or qa.voice.alive(child):
            raise Pending('QA10 coordinator or child is still active')
    for process in qa.psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            args = process.info['cmdline']
            if args is None:
                if (process.info.get('name') or '').lower().startswith('python'):
                    raise Pending('Uninspected Python process preserved')
                continue
            if any(flag in args for flag in ('--recognize', '--execute', '--levels')) and any(
                    Path(arg).name == PREVIOUS_QA.name for arg in args):
                raise Pending('QA10 launcher, controller, recognizer or levels reader is still active')
        except qa.psutil.NoSuchProcess:
            continue
        except qa.psutil.AccessDenied as exc:
            raise Pending('Possible QA10 process cannot be inspected') from exc


def verify_subset_engine(prov, out, proof, reuse_ids):
    selected, engine = prov['repair'], proof['engineOutputsPreserved']
    if (engine.get('engineSceneScope') != 'missing-subset-only' or
            engine.get('engineSceneIds') != list(TARGETS) or
            engine.get('engineSceneCount') != len(TARGETS) or
            engine.get('fullCanonicalSceneCount') != TAKE_COUNT or engine.get('reusedSceneIds') != reuse_ids or
            engine.get('subsetAggregateAndTimingValidated') is not True):
        raise ValueError('V7 engine proof must bind only the two new complete sentences')
    pins = engine.get('subsetInputs', [])
    names = ['narration-missing-only.json', 'voice-missing-only-manifest.json',
             'subset-repair-preparation.json', 'repair-adapter-source.py']
    if [Path(row['path']).name for row in pins] != names:
        raise ValueError('Four exact preserved V7 subset inputs are required')
    folder = Path(pins[0]['path']).resolve().parent
    scope = (ROOT / 'projects' / SLUG / 'production/voice-preparation').resolve()
    if (folder.name != 'repair-subset-' + selected['fingerprint'][:24] or folder.parent.parent != scope or
            re.fullmatch('[0-9a-f]{24}', folder.parent.name) is None or
            any(not Path(row['path']).is_absolute() or Path(row['path']).resolve().parent != folder or
                pin(row['path']) != row for row in pins) or pins[3]['sha256'] != PINS[V7_WORKER]):
        raise ValueError('Actual V7 subset input path or hash differs')
    subset = dict(prov, identity=dict(prov['identity'], scenes=selected['missing']))
    chunks, actual = voice_worker.life.original['validate_engine_outputs'](subset, out)
    selected_raw = [row for scene, row in zip(prov['identity']['scenes'], proof['sceneWavs'])
                    if scene['id'] in TARGETS]
    if chunks != selected_raw or any(engine[key] != actual[key] for key in ('aggregateWav', 'timing', 'srt')):
        raise ValueError('Preserved two-sentence engine outputs differ from the full V7 proof')


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
        raise Pending('Waiting for actual completed V7 canonical voice')
    proof, state = qa.read(PROOF), qa.read(VOICE_STATE)
    if (proof.get('fingerprint') != EXPECTED_REPAIR_VOICE_FP or
            state.get('fingerprint') != EXPECTED_REPAIR_VOICE_FP or state.get('completed') is not True):
        raise Pending('The exact V7 canonical voice is not yet published and complete')
    if (state.get('childStillAlive') is not False or qa.voice.alive(state.get('child')) or
            qa.voice.project_children(SLUG) or (MEDIA / '11-05-voice-worker.json').exists()):
        raise Pending('Preserve the current voice owner, live child or durable worker marker')
    out = (VOICE_ROOT / EXPECTED_REPAIR_VOICE_FP[:24]).resolve()
    if (out / 'pending-launch.json').exists():
        raise Pending('Preserve the unresolved V7 synthesis launch record')
    if (out.parent != VOICE_ROOT or Path(proof['output']).resolve() != out or
            Path(state.get('output') or '').resolve() != out or
            Path(state.get('evidence') or '').resolve() != PROOF.resolve() or
            qa.read(out / 'voice-complete-proof.json') != proof):
        raise ValueError('V7 publication differs from the scoped immutable proof')
    canonical = out / 'canonical'
    for key, name in (('aggregateWav', 'narration.wav'), ('timing', 'narration.timing.json'),
                      ('engineSrt', 'narration.srt')):
        if Path(proof[key]['path']).resolve() != canonical / name:
            raise ValueError('V7 canonical artifact escaped its exact immutable scope: ' + key)
    path, draft, script, mapping = qa7.source_context()
    try:
        prov = repair.prepare()
    except (repair.Pending, FileNotFoundError) as exc:
        raise Pending(str(exc)) from exc
    identity, selected = proof['identity'], prov['repair']
    if (proof.get('topicId') != TOPIC or digest(identity) != EXPECTED_REPAIR_VOICE_FP or
            prov['fingerprint'] != EXPECTED_REPAIR_VOICE_FP or identity != prov['identity'] or
            selected['fingerprint'] != EXPECTED_REPAIR_FP or
            out != Path(prov['voiceOutputDirectory']).resolve() or
            proof['paragraphMapping'] != mapping or mapping != prov['paragraphMapping']):
        raise ValueError('V7 proof differs from the reviewed prepared identity')

    engine_script = repair.apply_prosody(script, mapping, repair.read(repair.PLAN)['targetSentences'])
    scenes = [{'id': row['id'], 'lines': row['lines']} for row in engine_script['scenes']]
    scene_ids = [scene['id'] for scene in scenes]
    reuse_ids = [row['newSceneId'] for row in selected['rows']]
    if (len(scene_ids) != TAKE_COUNT or len(set(scene_ids)) != TAKE_COUNT or
            [row['sceneId'] for row in mapping] != scene_ids or
            {row['paragraph'] for row in mapping} != set(range(1, PARAGRAPH_COUNT + 1)) or
            {key: value for key, value in identity.items() if key != 'repairSelection'} !=
            qa7.profile_identity(scenes, qa.read(qa7.PROFILE_PATH)) or
            selected['missing'] != [scene for scene in scenes if scene['id'] in TARGETS] or
            [scene['id'] for scene in selected['missing']] != list(TARGETS) or
            len(reuse_ids) != REUSE_COUNT or reuse_ids != [scene for scene in scene_ids if scene not in TARGETS] or
            any(row['oldSceneId'] != row['newSceneId'] for row in selected['rows']) or
            identity['repairSelection']['newNarration'] != pin(path)):
        raise ValueError('Exact Nar5, approved profile and V7 full48/reused46/new2 mapping required')
    if voice_worker.life.verify_complete(prov, out) != proof:
        raise ValueError('Full V7 proof differs from verified PCM, reuse and repair receipt')
    receipt = voice_worker.life.validate_receipt(prov, out)
    if (pin(path) not in receipt.get('inputs', []) or proof.get('rawSceneCount') != TAKE_COUNT or
            proof.get('repairProtocol') != repair.PROTOCOL or
            proof.get('reusedRawScenes') != selected['rows'] or proof.get('newlyGeneratedSceneIds') != list(TARGETS) or
            proof.get('engineSpokeFullCombinedScript') is not False):
        raise ValueError('V7 narration or missing-only proof scope differs')
    verify_subset_engine(prov, out, proof, reuse_ids)

    timing = qa.read(proof['timing']['path'])
    entries, position, pcm = timing['entries'], 0, hashlib.sha256()
    if timing['sample_rate'] != 24000 or len(entries) != TAKE_COUNT or len(proof['sceneWavs']) != TAKE_COUNT:
        raise ValueError('Exact V7 raw sample rate and take count required')
    for scene, entry, wav in zip(scenes, entries, proof['sceneWavs']):
        if (Path(wav['path']).resolve() != out / 'chunks' / (scene['id'] + '-scene.wav') or
                entry['scene_id'] != scene['id'] or entry['text'] != scene['lines'][0] or
                type(wav.get('frames')) is not int or wav['frames'] <= 0):
            raise ValueError('V7 raw take text, path or sample count differs')
        expected = (position / 24000, (position + wav['frames']) / 24000)
        if any(type(entry.get(key)) not in (int, float) or not math.isfinite(entry[key]) or
               abs(entry[key] - value) > 1e-9 for key, value in zip(('start', 'end'), expected)):
            raise ValueError('V7 take boundaries differ from the exact raw sample clock')
        pcm.update(qa.pcm_bytes(wav['path']))
        position += wav['frames']
    if position != proof['aggregateWav']['frames'] or pcm.hexdigest() != proof['aggregateWav']['pcmSHA256']:
        raise ValueError('V7 full canonical PCM differs from exact raw take concatenation')
    return out, proof, timing, draft


def prepare_job():
    check_sources()
    job = qa8._prepare_job()
    actual_proof = qa.read(PROOF)
    immutable = Path(job['voiceOutput']) / 'voice-complete-proof.json'
    if (actual_proof['fingerprint'] != EXPECTED_REPAIR_VOICE_FP or
            job['identity']['voiceFingerprint'] != EXPECTED_REPAIR_VOICE_FP or
            job['voiceEvidence'] != pin(PROOF) or actual_proof != qa.read(immutable)):
        raise Pending('V7 publication changed while preparing blind task windows')
    tasks = job['identity']['tasks']
    takes = [task for task in tasks if task['kind'] == 'take']
    joins = [task for task in tasks if task['kind'] == 'boundary']
    scenes, mapping = actual_proof['identity']['scenes'], actual_proof['paragraphMapping']
    expected_joins = [(left['sceneId'], right['sceneId'],
                       'internal-component' if left['paragraphIndex'] == right['paragraphIndex']
                       else 'paragraph-boundary') for left, right in zip(takes, takes[1:])]
    if (len(tasks) != TAKE_COUNT + JOIN_COUNT or len(takes) != TAKE_COUNT or len(joins) != JOIN_COUNT or
            [(row['sceneId'], row['paragraphIndex'], row['expected']) for row in takes] !=
            [(scene['id'], row['paragraph'], scene['lines'][0]) for scene, row in zip(scenes, mapping)] or
            [(row['previousScene'], row['nextScene'], row['joinType']) for row in joins] != expected_joins):
        raise ValueError('Exact blind 48 take and 47 adjacent join task coverage differs')
    # Bind blind comparison to the authored words and preserve the engine-only commas.
    for take, sentence in zip(takes, mapping, strict=True):
        take['expected'] = sentence['canonicalText']
    for left, right, join in zip(takes, takes[1:], joins, strict=False):
        join['expectedContextOnly'] = dict(previousEnding=' '.join(left['expected'].split()[-8:]),
                                           nextBeginning=' '.join(right['expected'].split()[:8]))
    job['identity'].update(
        launcherRuntimePins=copy.deepcopy(qa7.LAUNCHER_RUNTIME_PINS),
        launcherClassification='exact-direct-venv-parent-base-child-argv0-and-tail-v11',
        commonAsrLibrarySHA256=qa7.PINS[qa7.BASE_PATH.name],
        currentVoiceWorkerSHA256=PINS[V7_WORKER],
        currentRepairPreparerSHA256=PINS[V7_PREPARER],
        currentRepairLifecycleSHA256=PINS[V7_LIFECYCLE],
        sourceNarration=pin(repair.NARRATION),
        repairFingerprint=EXPECTED_REPAIR_FP,
        repairSelection=copy.deepcopy(actual_proof['identity']['repairSelection']),
        paragraphMappingSHA256=digest(mapping),
        originalParentTakes=list(TARGETS),
        resourceSourcePins={name: qa7.PINS[name] for name in (
            'run-solution-path-native-v4.py', 'prospect-refuge-resource-qualification.py', 'run-first-native.py')},
    )
    job['fingerprint'] = digest(job['identity'])
    job['output'] = str(Path(job['voiceOutput']) / 'review/independent-asr-selected-v1' / job['fingerprint'][:24])
    job['publishedVoiceEvidenceAudit'] = job['voiceEvidence']
    job['voiceEvidence'] = pin(immutable)
    inherited = [*qa8.PINS, *(HERE / name for name in qa7.PINS)]
    job['sourcePins'] += ([pin(path) for path in (*PINS, *inherited, repair.NARRATION)] +
                          copy.deepcopy(qa7.LAUNCHER_RUNTIME_PINS))
    job['sourcePins'] = list({row['path']: row for row in job['sourcePins']}.values())
    return job


def direct_parent_matches(info, own, parent, argv_count):
    """Identify the exact pinned Dvenv launcher and its current Cbase body."""
    try:
        fields = ('pid', 'ppid', 'create_time', 'name', 'exe', 'cmdline')
        if any(any(row.get(key) is None for key in fields) for row in (info, own, parent)):
            return False
        if any(type(row[key]) is not int or row[key] <= 0 for row in (info, own, parent) for key in ('pid', 'ppid')):
            return False
        if (own['pid'] == parent['pid'] or own['ppid'] != parent['pid'] or info['pid'] != parent['pid'] or
                info['ppid'] != parent['ppid'] or any(row['name'].lower() != 'python.exe' for row in (info, own, parent)) or
                any(type(row['create_time']) not in (int, float) or not math.isfinite(row['create_time']) or
                    row['create_time'] <= 0 for row in (info, own, parent))):
            return False
        args, parent_args = own['cmdline'], parent['cmdline']
        if (not isinstance(args, list) or not isinstance(parent_args, list) or
                len(args) != argv_count or len(parent_args) != argv_count or
                not all(isinstance(arg, str) for arg in args + parent_args) or
                args[1:] != parent_args[1:] or args[1:4] != ['-u', '-X', 'utf8'] or
                Path(args[4]).resolve() != Path(__file__).resolve()):
            return False
        launcher = Path(qa7.LAUNCHER_RUNTIME_PINS[0]['path']).resolve()
        body = Path(qa7.LAUNCHER_RUNTIME_PINS[2]['path']).resolve()
        return (info['cmdline'] == parent_args and
                Path(parent_args[0]).resolve() == Path(qa.PYTHON).resolve() == launcher and
                Path(info['exe']).resolve() == Path(parent['exe']).resolve() == launcher and
                Path(args[0]).resolve() == Path(own['exe']).resolve() == body and
                abs(info['create_time'] - parent['create_time']) < .001 and
                0 <= own['create_time'] - parent['create_time'] < 30)
    except (AttributeError, KeyError, TypeError, ValueError, OSError):
        return False


def launcher_matches(info, own, parent):
    """Classify only the exact pinned Windows direct recognizer launcher."""
    if not direct_parent_matches(info, own, parent, 10):
        return False
    try:
        args = own['cmdline']
        if (not Path(args[4]).is_absolute() or args[5:7] != ['--recognize', '--job'] or
                args[8] != '--resource-decline'):
            return False
        job, decline = Path(args[7]), Path(args[9])
        relative = job.resolve().relative_to(VOICE_ROOT).parts
        return (job.is_absolute() and decline.is_absolute() and len(relative) == 5 and
                relative[0] == EXPECTED_REPAIR_VOICE_FP[:24] and
                relative[1:3] == ('review', 'independent-asr-selected-v1') and
                re.fullmatch('[0-9a-f]{24}', relative[3]) is not None and relative[4] == 'job.json' and
                decline.resolve().parent == job.resolve().parent and
                re.fullmatch(r'resource-decline-[0-9a-f]{8}\.json', decline.name) is not None)
    except (KeyError, TypeError, ValueError, OSError):
        return False


def execute_parent_matches(own, parent):
    return (direct_parent_matches(parent, own, parent, 8) and
            own['cmdline'][5:] == ['--execute', '--wait-hours', '6'])


def approved_execute_launcher():
    if os.name != 'nt':
        return False
    try:
        fields = ['pid', 'ppid', 'create_time', 'name', 'exe', 'cmdline']
        own = qa.psutil.Process(os.getpid()).as_dict(fields)
        parent = qa.psutil.Process(own['ppid']).as_dict(fields)
        return (own['pid'] == os.getpid() and parent['pid'] == os.getppid() and
                execute_parent_matches(own, parent))
    except (qa.psutil.NoSuchProcess, qa.psutil.AccessDenied, OSError, ValueError, KeyError, TypeError):
        return False


def scoped_process_reason(info, own_pid, qualified=frozenset()):
    if os.name == 'nt' and own_pid == os.getpid() and info.get('pid') == os.getppid():
        try:
            fields = ['pid', 'ppid', 'create_time', 'name', 'exe', 'cmdline']
            own = qa.psutil.Process(os.getpid()).as_dict(fields)
            parent = qa.psutil.Process(own['ppid']).as_dict(fields)
            if launcher_matches(info, own, parent):
                return None
        except (qa.psutil.NoSuchProcess, qa.psutil.AccessDenied):
            pass
    return qa8._process_reason(info, own_pid, qualified)


def resource_reason():
    check_sources()
    return qa8._resource_reason()


def child_processes():
    names = {Path(__file__).name, QA8.name, qa8.QA7.name, *qa7.LEGACY_ENTRIES, qa7.BASE_PATH.name,
             'run-first-asr.py', 'run-prospect-refuge-voice-qa.py', 'run-prospect-refuge-voice-qa-v2.py',
             'run-prospect-refuge-mix-asr.py', 'run-zen-view-mix-asr.py'}
    found = []
    for process in qa.psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            args = process.info['cmdline']
            if args is None:
                if (process.info.get('name') or '').lower().startswith('python'):
                    raise Pending('Uninspected Python arguments; preserve possible recognizer')
                continue
            if process.pid != os.getpid() and '--recognize' in args and any(Path(arg).name in names for arg in args):
                found.append(qa.voice.identity(process.pid))
        except qa.psutil.NoSuchProcess:
            continue
        except qa.psutil.AccessDenied as exc:
            raise Pending('Possible recognizer child cannot be inspected') from exc
    return found


def parent_sentence_levels(takes, mathqa):
    by_id = {row['sceneId']: row for row in takes}
    parents, flags = [], []
    for scene in TARGETS:
        row = by_id[scene]
        words = row['wordRecords']
        ordered = all(left['globalRawSampleRange'][1] <= right['globalRawSampleRange'][0]
                      for left, right in zip(words, words[1:]))
        trend = mathqa.trend(words, 'canonical') if ordered else dict(
            words=0, suspect=False, reason='Overlapping or unordered ASR word windows')
        parents.append(dict(logicalSentenceId=scene, sceneIds=[scene], wordTrend=trend))
        if trend['suspect']:
            flags.append(dict(kind='sustained-original-sentence-word-body-decline',
                              logicalSentenceId=scene, sceneIds=[scene], trend=trend))
        if (not words or row['invalidWordWindows'] or trend['words'] < mathqa.POLICY['longTrendMinimumWords'] or
                trend.get('spanSeconds', 0) < mathqa.POLICY['longTrendMinimumSeconds']):
            flags.append(dict(kind='original-sentence-trend-coverage-insufficient',
                              logicalSentenceId=scene, sceneIds=[scene], trend=trend))
    return parents, flags


def raw_level_review(job_path):
    """Write a separate immutable original-sentence hold beside base levels."""
    check_sources()
    legacy_barrier()
    job_path = Path(job_path).resolve()
    job = qa.read(job_path)
    voice_out = VOICE_ROOT / EXPECTED_REPAIR_VOICE_FP[:24]
    proof_pin = job['voiceEvidence']
    review_path = job_path.parent / 'review.json'
    if (job.get('protocol') != PROTOCOL or job['identity'].get('adapterSHA256') != SELF_SHA or
            job['identity'].get('voiceFingerprint') != EXPECTED_REPAIR_VOICE_FP or
            job['fingerprint'] != digest(job['identity']) or Path(job['voiceOutput']).resolve() != voice_out or
            job_path != voice_out / 'review/independent-asr-selected-v1' / job['fingerprint'][:24] / 'job.json' or
            proof_pin != pin(voice_out / 'voice-complete-proof.json')):
        raise ValueError('Level review requires the exact immutable QA11 job and V7 proof')
    if not review_path.is_file() or not STATE.is_file() or WORKER.exists() or child_processes():
        raise Pending('Wait for the exact QA11 recognition review and worker completion')
    state = qa.read(STATE)
    if (state.get('protocol') != PROTOCOL or state.get('owner') != OWNER or
            not qa7.inspected_identity(state) or state.get('completed') is not True or
            state.get('childStillAlive') is not False or qa.voice.alive(state) or
            qa.voice.alive(state.get('child')) or Path(state.get('review') or '').resolve() != review_path):
        raise Pending('Wait for the exact completed QA11 owner and recognition review')
    review_pin = pin(review_path)
    base_path = qa8.base_raw_level_review(job_path)
    check_sources()
    report, proof, review = qa.read(base_path), qa.read(proof_pin['path']), qa.read(review_path)
    if (report['voiceFingerprint'] != EXPECTED_REPAIR_VOICE_FP or report['asrReview'] != review_pin or
            report['canonicalWav'] != proof['aggregateWav'] or pin(proof_pin['path']) != proof_pin or
            qa.read(job_path) != job or pin(review_path) != review_pin or review['fingerprint'] != job['fingerprint'] or
            len(report['takes']) != TAKE_COUNT or len(report['paragraphs']) != PARAGRAPH_COUNT or
            len(report['joins']) != JOIN_COUNT or report['levelPrimitive'] != pin(LEVEL_PRIMITIVE)):
        raise ValueError('Original-sentence levels require the exact completed QA11 base report')
    mathqa = module('solution_v11_private_level_math', LEVEL_PRIMITIVE)
    if report['policy'] != mathqa.POLICY:
        raise ValueError('Original-sentence numerical policy differs')
    parents, parent_flags = parent_sentence_levels(report['takes'], mathqa)
    base_holds = {'sustained-take-word-body-decline', 'sustained-paragraph-word-body-decline',
                  'incomplete-word-level-measurement'}
    result = dict(
        protocol='architectural111-11-05-original-sentence-level-v11',
        voiceFingerprint=EXPECTED_REPAIR_VOICE_FP,
        voiceEvidence=proof_pin,
        asrJob=pin(job_path),
        asrReview=review_pin,
        canonicalWav=proof['aggregateWav'],
        physicalTakeParagraphJoinLevels=pin(base_path),
        levelPrimitive=report['levelPrimitive'],
        policy=report['policy'],
        originalSentences=parents,
        originalSentenceFlags=parent_flags,
        flags=report['flags'] + parent_flags,
        numericalHold=bool(parent_flags or any(row['kind'] in base_holds for row in report['flags'])),
        pcmModified=False,
        normalizationApplied=False,
        automaticSpeechPass=False,
        actualListening=False,
        humanApproval=False,
    )
    destination = base_path.parent / 'original-sentence-review-v11.json'
    qa.voice.immutable_json(destination, result)
    return destination


def execute(wait_hours):
    # Require the finished exact voice before acquiring the existing singleton.
    if wait_hours != 6 or not approved_execute_launcher():
        raise Pending('Use the exact eight-argument QA11 execute entry through the approved Windows venv launcher')
    exact_voice()
    return qa8._execute(wait_hours)


qa7.resource.process_reason = scoped_process_reason
qa.PROTOCOL, qa.OWNER = PROTOCOL, OWNER
qa.STATE, qa.WORKER = STATE, WORKER
qa.runtime.PROTOCOL, qa.runtime.OWNER = PROTOCOL, OWNER
qa.__file__ = str(Path(__file__).resolve())
qa.exact_voice, qa.prepare_job = exact_voice, prepare_job
qa.resource_reason, qa.raw_level_review, qa.execute = resource_reason, raw_level_review, execute
qa.child_processes = child_processes
summary, cached = qa.summary, qa.cached

if __name__ == '__main__':
    try:
        qa.main()
    except Pending as exc:
        print(json.dumps(dict(ready=False, reason=str(exc), protocol=PROTOCOL, modelLoaded=False, staged=False),
                         ensure_ascii=False))
        raise SystemExit(2 if any(a in sys.argv[1:] for a in ('--execute', '--recognize', '--levels')) else 0)
