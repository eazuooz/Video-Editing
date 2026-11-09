"""11.05 blind ASR for the exact V4 split-clause repair.

Default is read-only. Execution requires the complete V4 publication and uses
the existing finite controller and GPU guards. CPU levels include the original
two sentence spans, alongside the physical take, paragraph and join report.
"""
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
PROTOCOL, OWNER = 'architectural111-11-05-voice-asr-v8', 'architectural-111-11-05-asr-v8'
QA7 = HERE / 'run-solution-path-voice-qa-v7.py'
V4_WORKER = HERE / 'run-solution-path-voice-repair-v4.py'
V4_PREPARER = HERE / 'prepare-solution-path-voice-repair-v4.py'
V4_LIFECYCLE = HERE / 'run-selected-voice-repair-v4.py'
V4_PLAN = ROOT / 'projects' / SLUG / 'voice-subset-repair-plan-v4.json'
VOICE_ROOT = (ROOT / 'shared/output/architectural-111-20261106/11-05/voice-attempts').resolve()
LEVEL_PRIMITIVE = HERE / 'first-level-continuity-review.py'
PINS = {
    QA7: '7a7daecd5ef47de321e777d9c3446010df4b40a4b7ceee92f0178ddd926121c1',
    V4_WORKER: '2eb51314d0210daf04d0fd97af83eb1c674fc4088557b1e4b7ded89f93282854',
    V4_PREPARER: '9a70bbe5d3886e08b3afb4a3dbc16e3751dbd039a561f5003850736d26b5dfd3',
    V4_LIFECYCLE: 'c70ba7ff185f048bbb53c3b7845b5af2237d14de1ea3ef511e9afacdf8171366',
    V4_PLAN: '9c422631b2f5873fda126aca8188a712d63a7f2a5a1697e185b19a6066d32fcb',
    LEVEL_PRIMITIVE: '545104df16cf26af0c0637faa76750bea1e5b70f424cc13820f13baa8b773544',
}
EXPECTED_REPAIR_VOICE_FP = '7c14ab3038b59c5ed3e903af076bb37f9f6cc6843de518ceff34a42e536e7e02'
EXPECTED_REPAIR_FP = '0a0cf97f6164ab04e86a02a144baa805d96cd389edbd7f5abf5497eb7356a67f'
PARENT_CLAUSES = {
    'p008-c01': ('p008-c01a', 'p008-c01b'),
    'p013-c01': ('p013-c01a', 'p013-c01b'),
}
TARGETS = tuple(scene for pair in PARENT_CLAUSES.values() for scene in pair)


class SourceFreezePending(RuntimeError):
    pass


def sha(path):
    with Path(path).open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def check_sources():
    if sha(__file__) != SELF_SHA:
        raise RuntimeError('QA8 adapter changed after import')
    if not all((EXPECTED_REPAIR_VOICE_FP, EXPECTED_REPAIR_FP, *PINS.values())):
        raise SourceFreezePending('Waiting for the exact independently reviewed V4 source and voice pins')
    for path, expected in PINS.items():
        if sha(path) != expected:
            raise RuntimeError('Reviewed QA8 input source changed: ' + str(path))
    if 'qa7' in globals():
        qa7.check_sources()
    if 'voice_worker' in globals():
        voice_worker.check_sources()


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    sys.modules[name] = result
    spec.loader.exec_module(result)
    return result


try:
    check_sources()
except SourceFreezePending as exc:
    if __name__ == '__main__':
        print(json.dumps(dict(ready=False, reason=str(exc), protocol=PROTOCOL, modelLoaded=False, staged=False)))
        raise SystemExit(2 if any(a in sys.argv[1:] for a in ('--execute', '--recognize', '--levels')) else 0)
    raise

# Both imported contexts are private to this new entry. QA7's files, protocol
# and historical evidence are never changed.
qa7 = module('solution_v8_private_qa7', QA7)
voice_worker = module('solution_v8_private_voice_repair', V4_WORKER)
repair = voice_worker.prep
qa = qa7.qa
Pending, PROFILE, MODEL = qa.Pending, qa.PROFILE, qa.MODEL
MEDIA, PROOF, VOICE_STATE = qa7.MEDIA, qa7.PROOF, qa7.VOICE_STATE
STATE, WORKER = MEDIA / '11-05-asr-v8-progress.json', MEDIA / '11-05-asr-v8-worker.json'
LEGACY_V7 = (qa7.STATE, qa7.WORKER)
_prepare_job = qa7._library_prepare_job
_resource_reason = qa7._library_resource_reason
_process_reason = qa7._process_reason
_execute = qa.execute
_single_worker = qa.runtime.SingleWorker
base_raw_level_review = qa.raw_level_review
pin, digest = qa.pin, qa.digest


def legacy_barrier():
    qa7.legacy_barrier()
    for path in LEGACY_V7:
        if not path.exists():
            continue
        try:
            row = qa.read(path)
        except (OSError, ValueError) as exc:
            raise Pending('Uninspected QA7 state/worker preserved') from exc
        if (not qa7.inspected_identity(row) or row.get('protocol') != qa7.PROTOCOL or
                row.get('owner') != qa7.OWNER):
            raise Pending('Unknown QA7 owner identity preserved')
        child = row.get('child')
        if child is not None and not qa7.inspected_identity(child):
            raise Pending('Unknown QA7 child identity preserved')
        if row.get('phase') == 'launching' and child is None:
            raise Pending('Unresolved QA7 durable launch gap preserved')
        if qa.voice.alive(row) or qa.voice.alive(child):
            raise Pending('QA7 coordinator or child is still active')
    for process in qa.psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            args = process.info['cmdline']
            if args is None:
                if (process.info.get('name') or '').lower().startswith('python'):
                    raise Pending('Uninspected Python process preserved')
                continue
            if any(flag in args for flag in ('--recognize', '--execute', '--levels')) and any(
                    Path(arg).name == QA7.name for arg in args):
                raise Pending('QA7 launcher, controller or recognizer is still active')
        except qa.psutil.NoSuchProcess:
            continue
        except qa.psutil.AccessDenied as exc:
            raise Pending('Possible QA7 process cannot be inspected') from exc


def prepared_repair():
    try:
        prov = repair.prepare()
    except (repair.Pending, FileNotFoundError) as exc:
        raise Pending(str(exc)) from exc
    if prov['fingerprint'] != EXPECTED_REPAIR_VOICE_FP or prov['repair']['fingerprint'] != EXPECTED_REPAIR_FP:
        raise Pending('Prepared V4 repair differs from the reviewed voice and repair fingerprints')
    return prov


def verify_subset_engine(prov, out, proof):
    selected = prov['repair']
    reuse_ids = [row['newSceneId'] for row in selected['rows']]
    engine = proof['engineOutputsPreserved']
    if (engine.get('engineSceneScope') != 'missing-subset-only' or
            engine.get('engineSceneIds') != list(TARGETS) or engine.get('engineSceneCount') != 4 or
            engine.get('fullCanonicalSceneCount') != 50 or engine.get('reusedSceneIds') != reuse_ids or
            engine.get('subsetAggregateAndTimingValidated') is not True):
        raise ValueError('Actual V4 engine must preserve four-only synthesis and 46 original raw takes')
    pins = engine.get('subsetInputs', [])
    expected_names = ['narration-missing-only.json', 'voice-missing-only-manifest.json',
                      'subset-repair-preparation.json', 'repair-adapter-source.py']
    if [Path(row['path']).name for row in pins] != expected_names:
        raise ValueError('Four exact preserved V4 subset inputs are required')
    folder = Path(pins[0]['path']).resolve().parent
    scope = (ROOT / 'projects' / SLUG / 'production/voice-preparation').resolve()
    if (folder.name != 'repair-subset-' + selected['fingerprint'][:24] or folder.parent.parent != scope or
            re.fullmatch('[0-9a-f]{24}', folder.parent.name) is None or
            any(not Path(row['path']).is_absolute() or Path(row['path']).resolve().parent != folder or
                pin(row['path']) != row for row in pins) or pins[3]['sha256'] != PINS[V4_WORKER]):
        raise ValueError('Actual V4 subset input path/hash differs')
    subset = dict(prov, identity=dict(prov['identity'], scenes=selected['missing']))
    chunks, actual = voice_worker.life.original['validate_engine_outputs'](subset, out)
    selected_raw = [row for scene, row in zip(prov['identity']['scenes'], proof['sceneWavs'])
                    if scene['id'] in TARGETS]
    if chunks != selected_raw or any(engine[key] != actual[key] for key in ('aggregateWav', 'timing', 'srt')):
        raise ValueError('Preserved actual four engine outputs differ from the full V4 proof')


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
        raise Pending('Waiting for the exact completed V4 clause-split voice')
    proof, state = qa.read(PROOF), qa.read(VOICE_STATE)
    if (proof.get('fingerprint') != EXPECTED_REPAIR_VOICE_FP or
            state.get('fingerprint') != EXPECTED_REPAIR_VOICE_FP or state.get('completed') is not True):
        raise Pending('The current V4 clause-split canonical voice is not yet published and complete')
    if (state.get('childStillAlive') is not False or qa.voice.alive(state.get('child')) or
            qa.voice.project_children(SLUG) or (MEDIA / '11-05-voice-worker.json').exists()):
        raise Pending('Preserve the current voice owner, live child or durable worker marker')
    out = (VOICE_ROOT / EXPECTED_REPAIR_VOICE_FP[:24]).resolve()
    if (out.parent != VOICE_ROOT or Path(proof['output']).resolve() != out or
            qa.read(out / 'voice-complete-proof.json') != proof):
        raise ValueError('V4 publication differs from its scoped immutable proof')

    path, draft, _, _ = qa7.source_context()
    prov = prepared_repair()
    identity = proof['identity']
    if (proof.get('topicId') != TOPIC or digest(identity) != EXPECTED_REPAIR_VOICE_FP or
            identity != prov['identity'] or out != Path(prov['voiceOutputDirectory']).resolve() or
            proof['paragraphMapping'] != prov['paragraphMapping']):
        raise ValueError('V4 proof differs from the reviewed prepared identity')
    scenes, mapping, selected = identity['scenes'], proof['paragraphMapping'], prov['repair']
    scene_ids = [scene['id'] for scene in scenes]
    reuse_ids = [row['newSceneId'] for row in selected['rows']]
    if (len(scene_ids) != 50 or len(set(scene_ids)) != 50 or
            [row['sceneId'] for row in mapping] != scene_ids or
            [scene['id'] for scene in selected['missing']] != list(TARGETS) or
            len(reuse_ids) != 46 or reuse_ids != [scene for scene in scene_ids if scene not in TARGETS] or
            any(row['oldSceneId'] != row['newSceneId'] for row in selected['rows']) or
            identity['repairSelection']['newNarration'] != pin(path)):
        raise ValueError('Exact V4 physical 50 / reused 46 / new 4 mapping required')
    if ({key: value for key, value in identity.items() if key != 'repairSelection'} !=
            qa7.profile_identity(scenes, qa.read(qa7.PROFILE_PATH))):
        raise ValueError('V4 changed the reviewed model, reference, profile or PCM policy')
    paragraphs = {}
    for scene, row in zip(scenes, mapping):
        paragraphs.setdefault(row['paragraph'], []).append(scene['lines'][0])
    if (list(paragraphs) != list(range(1, 15)) or
            [' '.join(words) for words in paragraphs.values()] != draft['narrationKo']):
        raise ValueError('Physical V4 clauses do not reconstruct the 14 original paragraphs')
    verify_parent_mapping(mapping)

    if voice_worker.life.verify_complete(prov, out) != proof:
        raise ValueError('Full V4 canonical proof differs from verified PCM, reuse and repair receipt')
    receipt = voice_worker.life.validate_receipt(prov, out)
    if (pin(path) not in receipt.get('inputs', []) or proof.get('rawSceneCount') != 50 or
            proof.get('repairProtocol') != repair.PROTOCOL or
            proof.get('reusedRawScenes') != selected['rows'] or proof.get('newlyGeneratedSceneIds') != list(TARGETS) or
            proof.get('engineSpokeFullCombinedScript') is not False):
        raise ValueError('Exact V4 narration or missing-only proof scope differs')
    verify_subset_engine(prov, out, proof)

    timing = qa.read(proof['timing']['path'])
    entries, position, pcm = timing['entries'], 0, hashlib.sha256()
    if timing['sample_rate'] != 24000 or len(entries) != 50 or len(proof['sceneWavs']) != 50:
        raise ValueError('Exact V4 raw sample rate and take count required')
    for scene, entry, wav in zip(scenes, entries, proof['sceneWavs']):
        if (Path(wav['path']).resolve() != out / 'chunks' / (scene['id'] + '-scene.wav') or
                entry['scene_id'] != scene['id'] or entry['text'] != scene['lines'][0] or
                type(wav.get('frames')) is not int or wav['frames'] <= 0):
            raise ValueError('V4 raw take text, path or sample count differs')
        expected = (position / 24000, (position + wav['frames']) / 24000)
        if any(type(entry.get(key)) not in (int, float) or not math.isfinite(entry[key]) or
               abs(entry[key] - value) > 1e-9 for key, value in zip(('start', 'end'), expected)):
            raise ValueError('V4 physical take boundaries differ from the exact raw sample clock')
        pcm.update(qa.pcm_bytes(wav['path']))
        position += wav['frames']
    if position != proof['aggregateWav']['frames'] or pcm.hexdigest() != proof['aggregateWav']['pcmSHA256']:
        raise ValueError('V4 full canonical PCM is not the exact physical take concatenation')
    return out, proof, timing, draft


def verify_parent_mapping(mapping):
    positions = {row['sceneId']: i for i, row in enumerate(mapping)}
    for parent, pair in PARENT_CLAUSES.items():
        first, second = (positions[scene] for scene in pair)
        if second != first + 1:
            raise ValueError('Original sentence clauses are not consecutive')
        for number, row in enumerate((mapping[first], mapping[second]), 1):
            if (row['paragraph'] != int(parent[1:4]) or row.get('logicalSentenceId') != parent or
                    row.get('logicalPart') != number or row.get('logicalPartCount') != 2):
                raise ValueError('Original sentence mapping differs from the reviewed two-clause split')


def prepare_job():
    check_sources()
    job = _prepare_job()
    actual_proof = qa.read(PROOF)
    immutable = Path(job['voiceOutput']) / 'voice-complete-proof.json'
    if (actual_proof['fingerprint'] != EXPECTED_REPAIR_VOICE_FP or
            job['identity']['voiceFingerprint'] != EXPECTED_REPAIR_VOICE_FP or
            job['voiceEvidence'] != pin(PROOF) or actual_proof != qa.read(immutable)):
        raise Pending('V4 publication changed while preparing blind task windows')
    tasks = job['identity']['tasks']
    takes = [task for task in tasks if task['kind'] == 'take']
    joins = [task for task in tasks if task['kind'] == 'boundary']
    scenes = actual_proof['identity']['scenes']
    mapping = actual_proof['paragraphMapping']
    expected_joins = [(left['sceneId'], right['sceneId'],
                       'internal-component' if left['paragraphIndex'] == right['paragraphIndex']
                       else 'paragraph-boundary') for left, right in zip(takes, takes[1:])]
    if (len(tasks) != 99 or len(takes) != 50 or len(joins) != 49 or
            [(row['sceneId'], row['paragraphIndex'], row['expected']) for row in takes] !=
            [(scene['id'], row['paragraph'], scene['lines'][0]) for scene, row in zip(scenes, mapping)] or
            [(row['previousScene'], row['nextScene'], row['joinType']) for row in joins] != expected_joins or
            {row['paragraphIndex'] for row in takes} != set(range(1, 15))):
        raise ValueError('Exact blind 50 take and 49 join task coverage differs')
    job['identity'].update(
        launcherRuntimePins=copy.deepcopy(qa7.LAUNCHER_RUNTIME_PINS),
        launcherClassification='exact-direct-venv-parent-base-child-argv0-and-tail-v8',
        commonAsrLibrarySHA256=qa7.PINS[qa7.BASE_PATH.name],
        currentVoiceWorkerSHA256=PINS[V4_WORKER],
        currentRepairPreparerSHA256=PINS[V4_PREPARER],
        currentRepairLifecycleSHA256=PINS[V4_LIFECYCLE],
        sourceNarration=pin(repair.NARRATION),
        repairFingerprint=EXPECTED_REPAIR_FP,
        repairSelection=copy.deepcopy(actual_proof['identity']['repairSelection']),
        paragraphMappingSHA256=digest(actual_proof['paragraphMapping']),
        originalParentClauses={parent: list(pair) for parent, pair in PARENT_CLAUSES.items()},
        resourceSourcePins={name: qa7.PINS[name] for name in (
            'run-solution-path-native-v4.py', 'prospect-refuge-resource-qualification.py', 'run-first-native.py')},
    )
    job['fingerprint'] = digest(job['identity'])
    job['output'] = str(Path(job['voiceOutput']) / 'review/independent-asr-selected-v1' / job['fingerprint'][:24])
    job['publishedVoiceEvidenceAudit'] = job['voiceEvidence']
    job['voiceEvidence'] = pin(immutable)
    job['sourcePins'] += ([pin(path) for path in PINS] + [pin(HERE / name) for name in qa7.PINS] +
                          [pin(repair.NARRATION)] + copy.deepcopy(qa7.LAUNCHER_RUNTIME_PINS))
    job['sourcePins'] = list({row['path']: row for row in job['sourcePins']}.values())
    return job


def launcher_matches(info, own, parent):
    """Recognize only the actual pinned Windows direct recognizer launcher."""
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
                len(args) != 10 or len(parent_args) != 10 or
                not all(isinstance(arg, str) for arg in args + parent_args) or
                args[1:] != parent_args[1:] or args[1:4] != ['-u', '-X', 'utf8'] or
                not Path(args[4]).is_absolute() or Path(args[4]).resolve() != Path(__file__).resolve() or
                args[5:7] != ['--recognize', '--job'] or args[8] != '--resource-decline'):
            return False
        job, decline = Path(args[7]), Path(args[9])
        relative = job.resolve().relative_to(VOICE_ROOT).parts
        if (not job.is_absolute() or not decline.is_absolute() or len(relative) != 5 or
                relative[0] != EXPECTED_REPAIR_VOICE_FP[:24] or
                relative[1:3] != ('review', 'independent-asr-selected-v1') or
                re.fullmatch('[0-9a-f]{24}', relative[3]) is None or relative[4] != 'job.json' or
                decline.resolve().parent != job.resolve().parent or
                re.fullmatch(r'resource-decline-[0-9a-f]{8}\.json', decline.name) is None):
            return False
        launcher = Path(qa7.LAUNCHER_RUNTIME_PINS[0]['path']).resolve()
        body = Path(qa7.LAUNCHER_RUNTIME_PINS[2]['path']).resolve()
        return (info['cmdline'] == parent_args and
                Path(parent_args[0]).resolve() == Path(qa.PYTHON).resolve() == launcher and
                Path(info['exe']).resolve() == Path(parent['exe']).resolve() == launcher and
                Path(args[0]).resolve() == Path(own['exe']).resolve() == body and
                abs(info['create_time'] - parent['create_time']) < .001 and
                0 <= own['create_time'] - parent['create_time'] < 30)
    except (KeyError, TypeError, ValueError, OSError):
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
    return _process_reason(info, own_pid, qualified)


def resource_reason():
    check_sources()
    return _resource_reason()


def child_processes():
    names = {Path(__file__).name, QA7.name, *qa7.LEGACY_ENTRIES, qa7.BASE_PATH.name,
             'run-first-asr.py', 'run-prospect-refuge-voice-qa.py', 'run-prospect-refuge-voice-qa-v2.py',
             'run-prospect-refuge-mix-asr.py', 'run-zen-view-mix-asr.py'}
    children = []
    for process in qa.psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            args = process.info['cmdline']
            if args is None:
                if (process.info.get('name') or '').lower().startswith('python'):
                    raise Pending('Uninspected possible recognizer preserved')
                continue
            if process.pid != os.getpid() and '--recognize' in args and any(
                    Path(arg).name in names for arg in args):
                children.append(qa.voice.identity(process.pid))
        except qa.psutil.NoSuchProcess:
            continue
        except qa.psutil.AccessDenied as exc:
            raise Pending('Possible recognizer child cannot be inspected') from exc
    return children


def preserve_unresolved_worker(path, is_alive):
    def active(record):
        if record is not None and (not qa7.inspected_identity(record) or
                                   (record.get('phase') == 'launching' and record.get('child') is None)):
            return True
        return is_alive(record)

    return _single_worker(path, is_alive=active)


def parent_sentence_levels(takes, mathqa):
    by_id = {row['sceneId']: row for row in takes}
    parents, flags = [], []
    for parent, pair in PARENT_CLAUSES.items():
        rows = [by_id[scene] for scene in pair]
        words = [word for row in rows for word in row['wordRecords']]
        ordered = all(left['globalRawSampleRange'][1] <= right['globalRawSampleRange'][0]
                      for left, right in zip(words, words[1:]))
        trend = mathqa.trend(words, 'canonical') if ordered else dict(
            words=0, suspect=False, reason='Overlapping or unordered ASR word windows')
        parents.append(dict(logicalSentenceId=parent, sceneIds=list(pair), wordTrend=trend))
        if trend['suspect']:
            flags.append(dict(kind='sustained-original-sentence-word-body-decline',
                              logicalSentenceId=parent, sceneIds=list(pair), trend=trend))
        if (any(not row['wordRecords'] or row['invalidWordWindows'] for row in rows) or
                trend['words'] < mathqa.POLICY['longTrendMinimumWords'] or
                trend.get('spanSeconds', 0) < mathqa.POLICY['longTrendMinimumSeconds']):
            flags.append(dict(kind='original-sentence-trend-coverage-insufficient',
                              logicalSentenceId=parent, sceneIds=list(pair), trend=trend))
    return parents, flags


def raw_level_review(job_path):
    """Write a separate immutable original-sentence report beside base levels."""
    check_sources()
    job_path = Path(job_path).resolve()
    job = qa.read(job_path)
    voice_out = VOICE_ROOT / EXPECTED_REPAIR_VOICE_FP[:24]
    proof_pin = job['voiceEvidence']
    if (job['identity'].get('voiceFingerprint') != EXPECTED_REPAIR_VOICE_FP or
            job['fingerprint'] != digest(job['identity']) or
            Path(job['voiceOutput']).resolve() != voice_out or
            proof_pin != pin(voice_out / 'voice-complete-proof.json')):
        raise ValueError('Level review requires the exact immutable V4 job and voice proof')
    base_path = base_raw_level_review(job_path)
    check_sources()
    report = qa.read(base_path)
    review_pin = pin(job_path.parent / 'review.json')
    proof = qa.read(proof_pin['path'])
    if (report['voiceFingerprint'] != EXPECTED_REPAIR_VOICE_FP or report['asrReview'] != review_pin or
            report['canonicalWav'] != proof['aggregateWav'] or pin(proof_pin['path']) != proof_pin or
            qa.read(job_path) != job or qa.read(review_pin['path'])['fingerprint'] != job['fingerprint'] or
            len(report['takes']) != 50 or len(report['paragraphs']) != 14 or len(report['joins']) != 49 or
            report['levelPrimitive'] != pin(LEVEL_PRIMITIVE)):
        raise ValueError('Original-sentence levels require the exact completed V4 base report')
    mathqa = module('solution_v8_private_level_math', LEVEL_PRIMITIVE)
    if report['policy'] != mathqa.POLICY:
        raise ValueError('Original-sentence numerical policy differs')
    parents, parent_flags = parent_sentence_levels(report['takes'], mathqa)
    base_holds = {'sustained-take-word-body-decline', 'sustained-paragraph-word-body-decline',
                  'incomplete-word-level-measurement'}
    result = dict(
        protocol='architectural111-11-05-original-sentence-level-v8',
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
    destination = base_path.parent / 'original-sentence-review-v8.json'
    qa.voice.immutable_json(destination, result)
    return destination


def execute(wait_hours):
    # Fail before even acquiring the new ASR singleton if V4 is not complete.
    exact_voice()
    return _execute(wait_hours)


qa7.resource.process_reason = scoped_process_reason
qa.PROTOCOL, qa.OWNER = PROTOCOL, OWNER
qa.STATE, qa.WORKER = STATE, WORKER
qa.runtime.PROTOCOL, qa.runtime.OWNER = PROTOCOL, OWNER
qa.runtime.SingleWorker = preserve_unresolved_worker
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
