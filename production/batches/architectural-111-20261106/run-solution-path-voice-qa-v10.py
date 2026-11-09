"""Blind ASR and original-sentence level review for the exact 11.05 V6 voice."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import math
import os
import re
import sys
import unicodedata
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
SELF_SHA = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
TOPIC, SLUG = '11.05', 'shorts-leveldesign-11-05'
PROTOCOL, OWNER = 'architectural111-11-05-voice-asr-v10', 'architectural-111-11-05-asr-v10'
QA9 = HERE / 'run-solution-path-voice-qa-v9.py'
V6_WORKER = HERE / 'run-solution-path-voice-repair-v6.py'
V6_PREPARER = HERE / 'prepare-solution-path-voice-repair-v6.py'
V6_LIFECYCLE = HERE / 'run-selected-voice-repair-v4.py'
V6_PLAN = ROOT / 'projects' / SLUG / 'voice-subset-repair-plan-v6.json'
LEVEL_PRIMITIVE = HERE / 'first-level-continuity-review.py'
PINS = {
    QA9: '4297a851234d5510a0e740338c43398dfd6449f2694ec1bc0f899562ba2ad77f',
    V6_WORKER: 'eec9ae7b77d3da8cec009aa7ccc800e0cf80a2d0e8d6b2800b28003af6f3a81b',
    V6_PREPARER: 'b654346dd54953378463db12c4d4be35835d272c36f260c39198d1903accb3b2',
    V6_LIFECYCLE: 'c70ba7ff185f048bbb53c3b7845b5af2237d14de1ea3ef511e9afacdf8171366',
    V6_PLAN: '53cc4ab288eb82a97f7d80517f325b3b17bcb3302ef4bc30a731c809507d488d',
    LEVEL_PRIMITIVE: '545104df16cf26af0c0637faa76750bea1e5b70f424cc13820f13baa8b773544',
}
EXPECTED_REPAIR_VOICE_FP = 'e230758531510298444578c302da94490146b9cee1e5424c6f31e0c06dfc7b7e'
EXPECTED_REPAIR_FP = '0606e6a27153e121bc826520ccff744602727ce8b63e32b638f8387ca07dfcce'
TARGETS = ('p008-c01', 'p013-c01')
CONTEXT_GROUPS = {
    'p008-g01': ('p008-c01', 'p008-c02'),
    'p013-g01': ('p013-c01', 'p013-c02'),
}
GROUP_IDS = tuple(CONTEXT_GROUPS)
TAKE_COUNT, REUSE_COUNT, LOGICAL_COUNT, PARAGRAPH_COUNT = 46, 44, 48, 14
JOIN_COUNT = TAKE_COUNT - 1
LOGICAL_JOIN_COUNT = LOGICAL_COUNT - 1


class SourceFreezePending(RuntimeError):
    pass


def sha(path):
    with Path(path).open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def check_sources():
    if sha(__file__) != SELF_SHA:
        raise RuntimeError('QA10 adapter changed after import')
    digests = (EXPECTED_REPAIR_VOICE_FP, EXPECTED_REPAIR_FP, *PINS.values())
    if any(not isinstance(value, str) or re.fullmatch('[0-9a-f]{64}', value) is None
           for value in digests):
        raise SourceFreezePending('Waiting for the exact reviewed V6 source and voice pins')
    for path, expected in PINS.items():
        if sha(path) != expected:
            raise RuntimeError('Reviewed QA10 input source changed: ' + str(path))
    if 'qa9' in globals():
        qa9.check_sources()
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

# The imported controller and its globals are private to this adapter. QA9
# evidence, files, original-sentence review, and source pins are read-only.
qa9 = module('solution_v10_private_qa9', QA9)
voice_worker = module('solution_v10_private_voice_repair', V6_WORKER)
qa8, qa7, qa, repair = qa9.qa8, qa9.qa7, qa9.qa, voice_worker.prep
Pending, PROFILE, MODEL = qa.Pending, qa.PROFILE, qa.MODEL
MEDIA, PROOF, VOICE_STATE, VOICE_ROOT = qa8.MEDIA, qa8.PROOF, qa8.VOICE_STATE, qa8.VOICE_ROOT
STATE, WORKER = MEDIA / '11-05-asr-v10-progress.json', MEDIA / '11-05-asr-v10-worker.json'
pin, digest = qa.pin, qa.digest


def legacy_barrier():
    qa9.legacy_barrier()
    for path in (qa9.STATE, qa9.WORKER):
        if not path.exists():
            continue
        try:
            row = qa.read(path)
        except (OSError, ValueError) as exc:
            raise Pending('Uninspected QA9 state or worker preserved') from exc
        if (not qa7.inspected_identity(row) or row.get('protocol') != qa9.PROTOCOL or
                row.get('owner') != qa9.OWNER):
            raise Pending('Unknown QA9 owner identity preserved')
        child = row.get('child')
        if child is not None and not qa7.inspected_identity(child):
            raise Pending('Unknown QA9 child identity preserved')
        if row.get('phase') == 'launching' and child is None:
            raise Pending('Unresolved QA9 durable launch gap preserved')
        if qa.voice.alive(row) or qa.voice.alive(child):
            raise Pending('QA9 coordinator or child is still active')
    for process in qa.psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            args = process.info['cmdline']
            if args is None:
                if (process.info.get('name') or '').lower().startswith('python'):
                    raise Pending('Uninspected Python process preserved')
                continue
            if any(flag in args for flag in ('--recognize', '--execute', '--levels')) and any(
                    Path(arg).name == QA9.name for arg in args):
                raise Pending('QA9 launcher, controller, recognizer or levels reader is still active')
        except qa.psutil.NoSuchProcess:
            continue
        except qa.psutil.AccessDenied as exc:
            raise Pending('Possible QA9 process cannot be inspected') from exc


def verify_subset_engine(prov, out, proof, reuse_ids):
    selected, engine = prov['repair'], proof['engineOutputsPreserved']
    if (engine.get('engineSceneScope') != 'missing-subset-only' or
            engine.get('engineSceneIds') != list(GROUP_IDS) or
            engine.get('engineSceneCount') != len(GROUP_IDS) or
            engine.get('fullCanonicalSceneCount') != TAKE_COUNT or engine.get('reusedSceneIds') != reuse_ids or
            engine.get('subsetAggregateAndTimingValidated') is not True):
        raise ValueError('V6 engine proof must bind only the two new exact contextual groups')
    pins = engine.get('subsetInputs', [])
    names = ['narration-missing-only.json', 'voice-missing-only-manifest.json',
             'subset-repair-preparation.json', 'repair-adapter-source.py']
    if [Path(row['path']).name for row in pins] != names:
        raise ValueError('Four exact preserved V6 subset inputs are required')
    folder = Path(pins[0]['path']).resolve().parent
    scope = (ROOT / 'projects' / SLUG / 'production/voice-preparation').resolve()
    if (folder.name != 'repair-subset-' + selected['fingerprint'][:24] or folder.parent.parent != scope or
            re.fullmatch('[0-9a-f]{24}', folder.parent.name) is None or
            any(not Path(row['path']).is_absolute() or Path(row['path']).resolve().parent != folder or
                pin(row['path']) != row for row in pins) or pins[3]['sha256'] != PINS[V6_WORKER]):
        raise ValueError('Actual V6 subset input path or hash differs')
    subset = dict(prov, identity=dict(prov['identity'], scenes=selected['missing']))
    chunks, actual = voice_worker.life.original['validate_engine_outputs'](subset, out)
    selected_raw = [row for scene, row in zip(prov['identity']['scenes'], proof['sceneWavs'])
                    if scene['id'] in GROUP_IDS]
    if chunks != selected_raw or any(engine[key] != actual[key] for key in ('aggregateWav', 'timing', 'srt')):
        raise ValueError('Preserved contextual engine outputs differ from the full V6 proof')


def exact_logical_mapping(scenes, mapping, originals, draft):
    """Reconstruct Nar5 from exact contiguous original sentences, without deriving any audio clock."""
    physical_ids = [scene['id'] for scene in scenes]
    if (len(physical_ids) != TAKE_COUNT or len(set(physical_ids)) != TAKE_COUNT or
            [row['sceneId'] for row in mapping] != physical_ids or
            {row['paragraph'] for row in mapping} != set(range(1, PARAGRAPH_COUNT + 1))):
        raise ValueError('Exact contextual physical scope differs')
    logical = []
    for scene, row in zip(scenes, mapping):
        members = row['sourceSentences']
        expected_ids = CONTEXT_GROUPS.get(scene['id'], (scene['id'],))
        if tuple(member['sentenceId'] for member in members) != expected_ids:
            raise ValueError('Only the two declared contextual groups may replace original take IDs')
        joined = ' '.join(member['canonicalText'] for member in members)
        start, end = row['sourceCharRange']
        paragraph_text = draft['narrationKo'][row['paragraph'] - 1]
        if (scene['lines'] != [joined] or row['canonicalText'] != joined or
                not 0 <= start < end <= len(paragraph_text) or paragraph_text[start:end] != joined):
            raise ValueError('Physical group text is not the exact authored paragraph substring')
        cursor = 0
        for member in members:
            text = member['canonicalText']
            member_end = cursor + len(text)
            if (member['sceneCharRange'] != [cursor, member_end] or
                    member['sourceCharRange'] != [start + cursor, start + member_end] or
                    joined[cursor:member_end] != text):
                raise ValueError('Source sentence range is not an exact half-open literal slice')
            logical.append((member['sentenceId'], row['paragraph'], member['sourceCharRange'], text))
            cursor = member_end + 1
    expected = [(row['sceneId'], row['paragraph'], row['sourceCharRange'], row['canonicalText'])
                for row in originals]
    if len(expected) != LOGICAL_COUNT or logical != expected:
        raise ValueError('Contextual groups omit, repeat, reorder or change the original Nar5 sentences')
    return logical


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
        raise Pending('Waiting for actual completed V6 canonical voice')
    proof, state = qa.read(PROOF), qa.read(VOICE_STATE)
    if (proof.get('fingerprint') != EXPECTED_REPAIR_VOICE_FP or
            state.get('fingerprint') != EXPECTED_REPAIR_VOICE_FP or state.get('completed') is not True):
        raise Pending('The exact V6 canonical voice is not yet published and complete')
    if (state.get('childStillAlive') is not False or qa.voice.alive(state.get('child')) or
            qa.voice.project_children(SLUG) or (MEDIA / '11-05-voice-worker.json').exists()):
        raise Pending('Preserve the current voice owner, live child or durable worker marker')
    out = (VOICE_ROOT / EXPECTED_REPAIR_VOICE_FP[:24]).resolve()
    if (out / 'pending-launch.json').exists():
        raise Pending('Preserve the unresolved V6 synthesis launch record')
    if (out.parent != VOICE_ROOT or Path(proof['output']).resolve() != out or
            Path(state.get('output') or '').resolve() != out or
            Path(state.get('evidence') or '').resolve() != PROOF.resolve() or
            qa.read(out / 'voice-complete-proof.json') != proof):
        raise ValueError('V6 publication differs from the scoped immutable proof')
    canonical = out / 'canonical'
    for key, name in (('aggregateWav', 'narration.wav'), ('timing', 'narration.timing.json'),
                      ('engineSrt', 'narration.srt')):
        if Path(proof[key]['path']).resolve() != canonical / name:
            raise ValueError('V6 canonical artifact escaped its exact immutable scope: ' + key)
    path, draft, _, originals = qa7.source_context()
    try:
        prov = repair.prepare()
    except (repair.Pending, FileNotFoundError) as exc:
        raise Pending(str(exc)) from exc
    identity, selected = proof['identity'], prov['repair']
    mapping = prov['paragraphMapping']
    if (proof.get('topicId') != TOPIC or digest(identity) != EXPECTED_REPAIR_VOICE_FP or
            prov['fingerprint'] != EXPECTED_REPAIR_VOICE_FP or identity != prov['identity'] or
            selected['fingerprint'] != EXPECTED_REPAIR_FP or
            out != Path(prov['voiceOutputDirectory']).resolve() or proof['paragraphMapping'] != mapping):
        raise ValueError('V6 proof differs from the reviewed prepared identity')

    scenes = identity['scenes']
    exact_logical_mapping(scenes, mapping, originals, draft)
    reuse_ids = [row['newSceneId'] for row in selected['rows']]
    if ({key: value for key, value in identity.items() if key != 'repairSelection'} !=
            qa7.profile_identity(scenes, qa.read(qa7.PROFILE_PATH)) or
            selected['missing'] != [scene for scene in scenes if scene['id'] in GROUP_IDS] or
            [scene['id'] for scene in selected['missing']] != list(GROUP_IDS) or
            len(reuse_ids) != REUSE_COUNT or
            reuse_ids != [scene['id'] for scene in scenes if scene['id'] not in GROUP_IDS] or
            any(row['oldSceneId'] != row['newSceneId'] for row in selected['rows']) or
            identity['repairSelection']['newNarration'] != pin(path)):
        raise ValueError('Exact Nar5, approved profile and V6 physical46/reused44/new2 scope required')

    if voice_worker.life.verify_complete(prov, out) != proof:
        raise ValueError('Full V6 proof differs from verified PCM, reuse and repair receipt')
    receipt = voice_worker.life.validate_receipt(prov, out)
    if (pin(path) not in receipt.get('inputs', []) or proof.get('rawSceneCount') != TAKE_COUNT or
            proof.get('repairProtocol') != repair.PROTOCOL or
            proof.get('reusedRawScenes') != selected['rows'] or proof.get('newlyGeneratedSceneIds') != list(GROUP_IDS) or
            proof.get('engineSpokeFullCombinedScript') is not False):
        raise ValueError('V6 narration or missing-only proof scope differs')
    verify_subset_engine(prov, out, proof, reuse_ids)

    timing = qa.read(proof['timing']['path'])
    entries, position, pcm = timing['entries'], 0, hashlib.sha256()
    if timing['sample_rate'] != 24000 or len(entries) != TAKE_COUNT or len(proof['sceneWavs']) != TAKE_COUNT:
        raise ValueError('Exact V6 raw sample rate and take count required')
    for scene, entry, wav in zip(scenes, entries, proof['sceneWavs']):
        if (Path(wav['path']).resolve() != out / 'chunks' / (scene['id'] + '-scene.wav') or
                entry['scene_id'] != scene['id'] or entry['text'] != scene['lines'][0] or
                type(wav.get('frames')) is not int or wav['frames'] <= 0):
            raise ValueError('V6 raw take text, path or sample count differs')
        expected = (position / 24000, (position + wav['frames']) / 24000)
        if any(type(entry.get(key)) not in (int, float) or not math.isfinite(entry[key]) or
               abs(entry[key] - value) > 1e-9 for key, value in zip(('start', 'end'), expected)):
            raise ValueError('V6 take boundaries differ from the exact raw sample clock')
        pcm.update(qa.pcm_bytes(wav['path']))
        position += wav['frames']
    if position != proof['aggregateWav']['frames'] or pcm.hexdigest() != proof['aggregateWav']['pcmSHA256']:
        raise ValueError('V6 full canonical PCM differs from exact raw take concatenation')
    return out, proof, timing, draft


def prepare_job():
    check_sources()
    job = qa8._prepare_job()
    actual_proof = qa.read(PROOF)
    immutable = Path(job['voiceOutput']) / 'voice-complete-proof.json'
    if (actual_proof['fingerprint'] != EXPECTED_REPAIR_VOICE_FP or
            job['identity']['voiceFingerprint'] != EXPECTED_REPAIR_VOICE_FP or
            job['voiceEvidence'] != pin(PROOF) or actual_proof != qa.read(immutable)):
        raise Pending('V6 publication changed while preparing blind task windows')
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
        raise ValueError('Exact blind 46 take and 45 physical join task coverage differs')
    job['identity'].update(
        launcherRuntimePins=copy.deepcopy(qa7.LAUNCHER_RUNTIME_PINS),
        launcherClassification='exact-direct-venv-parent-base-child-argv0-and-tail-v10',
        commonAsrLibrarySHA256=qa7.PINS[qa7.BASE_PATH.name],
        currentVoiceWorkerSHA256=PINS[V6_WORKER],
        currentRepairPreparerSHA256=PINS[V6_PREPARER],
        currentRepairLifecycleSHA256=PINS[V6_LIFECYCLE],
        sourceNarration=pin(repair.NARRATION),
        repairFingerprint=EXPECTED_REPAIR_FP,
        repairSelection=copy.deepcopy(actual_proof['identity']['repairSelection']),
        paragraphMappingSHA256=digest(mapping),
        originalTargetSentenceIds=list(TARGETS),
        contextualSourceSentences={row['sceneId']: row['sourceSentences']
                                   for row in mapping if row['sceneId'] in CONTEXT_GROUPS},
        physicalTakeCount=TAKE_COUNT,
        physicalJoinCount=JOIN_COUNT,
        originalSentenceCount=LOGICAL_COUNT,
        originalLogicalBoundaryCount=LOGICAL_JOIN_COUNT,
        resourceSourcePins={name: qa7.PINS[name] for name in (
            'run-solution-path-native-v4.py', 'prospect-refuge-resource-qualification.py', 'run-first-native.py')},
    )
    job['fingerprint'] = digest(job['identity'])
    job['output'] = str(Path(job['voiceOutput']) / 'review/independent-asr-selected-v1' / job['fingerprint'][:24])
    job['publishedVoiceEvidenceAudit'] = job['voiceEvidence']
    job['voiceEvidence'] = pin(immutable)
    inherited = [*qa9.PINS, *qa8.PINS, *(HERE / name for name in qa7.PINS)]
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
    names = {Path(__file__).name, QA9.name, qa9.QA8.name, qa8.QA7.name, *qa7.LEGACY_ENTRIES, qa7.BASE_PATH.name,
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


def literal_fold(value):
    """Fold punctuation, spacing and Latin case while retaining every other character."""
    return ''.join(char.lower() if 'A' <= char <= 'Z' else char
                   for char in unicodedata.normalize('NFC', value)
                   if not char.isspace() and not unicodedata.category(char).startswith('P'))


def grouped_word_alignment(recognized, physical_levels, members, mathqa):
    """Return the only exact literal partition over entire unchanged ASR words, or its hold reason."""
    task, raw = recognized['task'], recognized['rawRecognition']
    words = raw.get('chunks', [])
    records = physical_levels['wordRecords']
    if not words or physical_levels['invalidWordWindows'] or len(words) != len(records):
        return None, 'Incomplete grouped raw word windows'
    expected = [literal_fold(member['canonicalText']) for member in members]
    literals = [literal_fold(word['text']) for word in words]
    if (len(expected) != 2 or not all(expected) or not all(literals) or
            ''.join(literals) != ''.join(expected) or literal_fold(raw['text']) != ''.join(expected)):
        return None, 'Blind grouped transcript or whole ASR words do not match both authored sentences literally'
    boundaries = [index for index in range(1, len(words))
                  if ''.join(literals[:index]) == expected[0] and ''.join(literals[index:]) == expected[1]]
    if len(boundaries) != 1:
        return None, 'No unique whole-word edge separates the original sentences'
    edges = []
    for word, record in zip(words, records):
        stamp = word.get('timestamp')
        if (not isinstance(stamp, (list, tuple)) or len(stamp) != 2 or
                any(type(t) not in (int, float) or not math.isfinite(t) for t in stamp) or
                not 0 <= stamp[0] < stamp[1] <= task['durationSeconds']):
            return None, 'Nonpositive or out-of-take raw ASR word endpoint'
        start, end = mathqa.sample_window(*stamp, 24000)
        expected_range = [task['offsetSample'] + start, task['offsetSample'] + end]
        if (not 0 <= start < end <= task['endSample'] - task['offsetSample'] or
                record['globalRawSampleRange'] != expected_range or record['recognizedText'] != word['text'] or
                (edges and edges[-1]['globalRawSampleRange'][1] > expected_range[0])):
            return None, 'Clipped, overlapping or mismatched grouped word interval'
        edges.append(dict(text=word['text'], rawTimestampSeconds=list(stamp),
                          globalRawSampleRange=expected_range))
    return (boundaries[0], edges), None


def contextual_sentence_levels(takes, review, mapping, mathqa):
    by_id = {row['sceneId']: row for row in takes}
    recognized = {row['task']['sceneId']: row for row in review['takes']}
    sentences, internal, flags = [], [], []
    for row in mapping:
        scene, members = row['sceneId'], row['sourceSentences']
        if scene not in CONTEXT_GROUPS:
            continue
        result, reason = grouped_word_alignment(recognized[scene], by_id[scene], members, mathqa)
        left, right = (member['sentenceId'] for member in members)
        if result is None:
            flags.append(dict(kind='unresolved-contextual-original-sentence-boundary', sceneId=scene,
                              previousSentenceId=left, nextSentenceId=right, reason=reason))
            internal.append(dict(sceneId=scene, previousSentenceId=left, nextSentenceId=right,
                                 resolved=False, reason=reason))
            sentences.extend(dict(logicalSentenceId=member['sentenceId'], sceneIds=[scene],
                                  sourceCharRange=member['sourceCharRange'], resolved=False, reason=reason)
                             for member in members)
            continue
        cut, edges = result
        internal.append(dict(sceneId=scene, previousSentenceId=left, nextSentenceId=right, resolved=True,
                             leftWord=edges[cut - 1], rightWord=edges[cut],
                             leftWordIndex=cut - 1, rightWordIndex=cut,
                             sampleGridWordGapSamples=edges[cut]['globalRawSampleRange'][0] -
                             edges[cut - 1]['globalRawSampleRange'][1],
                             interpretation='Raw word endpoints inside one blind contextual take'))
        words = by_id[scene]['wordRecords']
        for member, (start, end) in zip(members, ((0, cut), (cut, len(words)))):
            sentence = member['sentenceId']
            trend = mathqa.trend(words[start:end], 'canonical')
            measured = dict(logicalSentenceId=sentence, sceneIds=[scene], wordTrend=trend)
            sentences.append(dict(**measured, sourceCharRange=member['sourceCharRange'], resolved=True,
                                  recognizedWordIndexRange=[start, end],
                                  firstWord=edges[start], lastWord=edges[end - 1]))
            if trend['suspect']:
                flags.append(dict(kind='sustained-original-sentence-word-body-decline', **measured))
            if (sentence in TARGETS and
                    (trend['words'] < mathqa.POLICY['longTrendMinimumWords'] or
                     trend.get('spanSeconds', 0) < mathqa.POLICY['longTrendMinimumSeconds'])):
                flags.append(dict(kind='original-sentence-trend-coverage-insufficient', **measured))
            if sentence not in TARGETS and not trend['words']:
                flags.append(dict(kind='incomplete-original-sentence-word-level-measurement', **measured))
    if len(internal) != len(CONTEXT_GROUPS) or len(sentences) != 2 * len(CONTEXT_GROUPS):
        raise ValueError('The two contextual boundaries and four original sentences must all be reviewed')
    return sentences, internal, flags


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
        raise ValueError('Level review requires the exact immutable QA10 job and V6 proof')
    if not review_path.is_file() or not STATE.is_file() or WORKER.exists() or child_processes():
        raise Pending('Wait for the exact QA10 recognition review and worker completion')
    state = qa.read(STATE)
    if (state.get('protocol') != PROTOCOL or state.get('owner') != OWNER or
            not qa7.inspected_identity(state) or state.get('completed') is not True or
            state.get('childStillAlive') is not False or qa.voice.alive(state) or
            qa.voice.alive(state.get('child')) or Path(state.get('review') or '').resolve() != review_path):
        raise Pending('Wait for the exact completed QA10 owner and recognition review')
    review_pin = pin(review_path)
    base_path = qa8.base_raw_level_review(job_path)
    check_sources()
    report, proof, review = qa.read(base_path), qa.read(proof_pin['path']), qa.read(review_path)
    if (report['voiceFingerprint'] != EXPECTED_REPAIR_VOICE_FP or report['asrReview'] != review_pin or
            report['canonicalWav'] != proof['aggregateWav'] or pin(proof_pin['path']) != proof_pin or
            qa.read(job_path) != job or pin(review_path) != review_pin or review['fingerprint'] != job['fingerprint'] or
            len(report['takes']) != TAKE_COUNT or len(report['paragraphs']) != PARAGRAPH_COUNT or
            len(report['joins']) != JOIN_COUNT or report['levelPrimitive'] != pin(LEVEL_PRIMITIVE)):
        raise ValueError('Original-sentence levels require the exact completed QA10 base report')
    mathqa = module('solution_v10_private_level_math', LEVEL_PRIMITIVE)
    if report['policy'] != mathqa.POLICY:
        raise ValueError('Original-sentence numerical policy differs')
    sentences, internal, parent_flags = contextual_sentence_levels(
        report['takes'], review, proof['paragraphMapping'], mathqa)
    by_scene = {row['sceneId']: row for row in proof['paragraphMapping']}
    joins = [dict(kind='physical-blind-join', previousScene=row['previousScene'], nextScene=row['nextScene'],
                  previousSentenceId=by_scene[row['previousScene']]['sourceSentences'][-1]['sentenceId'],
                  nextSentenceId=by_scene[row['nextScene']]['sourceSentences'][0]['sentenceId'],
                  boundarySample=row['boundarySample'])
             for row in report['joins']]
    joins.extend(dict(kind='internal-contextual-boundary', **row) for row in internal)
    logical_ids = [member['sentenceId'] for row in proof['paragraphMapping']
                   for member in row['sourceSentences']]
    by_pair = {(row['previousSentenceId'], row['nextSentenceId']): row for row in joins}
    ordered_pairs = list(zip(logical_ids, logical_ids[1:]))
    if len(joins) != LOGICAL_JOIN_COUNT or set(by_pair) != set(ordered_pairs):
        raise ValueError('Physical and internal evidence do not cover every original logical boundary')
    base_holds = {'sustained-take-word-body-decline', 'sustained-paragraph-word-body-decline',
                  'incomplete-word-level-measurement'}
    result = dict(
        protocol='architectural111-11-05-original-sentence-level-v10',
        voiceFingerprint=EXPECTED_REPAIR_VOICE_FP,
        voiceEvidence=proof_pin,
        asrJob=pin(job_path),
        asrReview=review_pin,
        canonicalWav=proof['aggregateWav'],
        physicalTakeParagraphJoinLevels=pin(base_path),
        levelPrimitive=report['levelPrimitive'],
        policy=report['policy'],
        physicalTakeCount=TAKE_COUNT,
        physicalJoinCount=JOIN_COUNT,
        paragraphCount=PARAGRAPH_COUNT,
        originalLogicalSentenceCount=LOGICAL_COUNT,
        originalLogicalSentenceIds=logical_ids,
        originalLogicalBoundaries=[by_pair[pair] for pair in ordered_pairs],
        originalSentences=sentences,
        originalSentenceFlags=parent_flags,
        flags=report['flags'] + parent_flags,
        numericalHold=bool(parent_flags or any(row['kind'] in base_holds for row in report['flags'])),
        pcmModified=False,
        normalizationApplied=False,
        automaticSpeechPass=False,
        actualListening=False,
        humanApproval=False,
    )
    destination = base_path.parent / 'original-sentence-review-v10.json'
    qa.voice.immutable_json(destination, result)
    return destination


def execute(wait_hours):
    # Require the finished exact voice before acquiring the existing singleton.
    if wait_hours != 6 or not approved_execute_launcher():
        raise Pending('Use the exact eight-argument QA10 execute entry through the approved Windows venv launcher')
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
