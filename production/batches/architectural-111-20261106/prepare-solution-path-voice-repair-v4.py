"""Prepare the selected 11.05 comma-boundary repair without writing or launching."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import sys
import types
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
PROJECT = ROOT / 'projects/shorts-leveldesign-11-05'
PLAN = PROJECT / 'voice-subset-repair-plan-v4.json'
PLAN_SHA = '9c422631b2f5873fda126aca8188a712d63a7f2a5a1697e185b19a6066d32fcb'
NARRATION = PROJECT / 'narration-final-v5.json'
NARRATION_SHA = 'e3179da81b2a23135eb6a8907ebb6205c14fc2d66e528a37372d491d0ffeaa91'
CHECKPOINT_SHA = '7123b2dffc7203700a296b2ceac45c23b3dece912d0da6887f3ee09e8a2512bb'
ADAPTER = HERE / 'run-solution-path-voice-repair-v4.py'
CONTENT_PEER = PROJECT / 'voice-asr-content-peer-review-v7.json'
CONTENT_PEER_SHA = '58031c673c787d30962b6f185586bf08ac294f4fb827ee6122b11c21f585d10b'
TOPIC = '11.05'
PROTOCOL = 'architectural111-11-05-voice-subset-repair-v4'
OLD_FP = 'e14a843b347400ab58a514884df264c912c662b8a5bc4ab0a437a6fa3b9e37f7'
OLD_REPAIR_FP = '44df1ff496ec6d1f6c6622c6b4db5d784376cef54b356e0ac25c188aa1e2c095'
VOICE_ATTEMPTS = ROOT / 'shared/output/architectural-111-20261106/11-05/voice-attempts'
OLD_OUT = VOICE_ATTEMPTS / OLD_FP[:24]
QA7 = 'run-solution-path-voice-qa-v7.py'
PINS = {
    QA7: '7a7daecd5ef47de321e777d9c3446010df4b40a4b7ceee92f0178ddd926121c1',
    'run-solution-path-voice-repair-v3.py': '416e0afd0fde4bec5e6f1f78fa26e2734e690b8d1520de9d702a9f4b3be162d7',
    'prepare-solution-path-voice-repair-v3.py': '3f4b18d0505e304e0216698b2a1c8287a3ae00587f1ddb2d3568102e89e25819',
    'run-solution-path-voice-v4.py': 'f94852008cc919308b995866ac35510163f3eabd72de45066d6c5d0f60807910',
    'run-selected-voice.py': '55ec247dafdef34bf2f31e9054e5a9fd3629ea2f220847b19694c48b59e26a99',
    'run-selected-voice-repair-v4.py': 'c70ba7ff185f048bbb53c3b7845b5af2237d14de1ea3ef511e9afacdf8171366',
}
SPLITS = {'p008-c01': ((0, 40), (41, 58)), 'p013-c01': ((0, 41), (42, 62))}
TARGETS = ('p008-c01a', 'p008-c01b', 'p013-c01a', 'p013-c01b')


class Pending(RuntimeError):
    pass


def need(condition, reason):
    if not condition:
        raise Pending(reason)


def sha(path):
    with Path(path).open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


SELF_SHA = sha(__file__)


def digest(value):
    data = json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False)
    return hashlib.sha256(data.encode()).hexdigest()


def pin(path):
    path = Path(path).resolve()
    return {'path': str(path), 'sha256': sha(path)}


def checked(row, role, expected_path=None):
    need(isinstance(row, dict) and isinstance(row.get('path'), str)
         and isinstance(row.get('sha256'), str), 'Missing pinned ' + role)
    path = Path(row['path']).resolve()
    need(expected_path is None or path == Path(expected_path).resolve(), 'Wrong path for ' + role)
    need(path.is_file() and pin(path) == {'path': row['path'], 'sha256': row['sha256']},
         'Changed pinned ' + role)
    return pin(path)


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    sys.modules[name] = result
    spec.loader.exec_module(result)
    return result


def check_sources():
    need(sha(__file__) == SELF_SHA, 'V4 preparer changed after import')
    for name, expected in PINS.items():
        need(sha(HERE / name) == expected, 'Reviewed repair dependency changed: ' + name)
    if 'prior_qa' in globals():
        prior_qa.check_sources()


check_sources()
prior_qa = module('solution_repair_v4_immutable_qa7', HERE / QA7)
voice_entry = module('solution_repair_v4_current_voice', HERE / 'run-solution-path-voice-v4.py')
prep = voice_entry.prep
base = voice_entry.base
RUNTIME_PINS = copy.deepcopy(prior_qa.LAUNCHER_RUNTIME_PINS)


def load_plan(path=PLAN):
    path = Path(path).resolve()
    need(path == PLAN.resolve() and path.is_file() and sha(path) == PLAN_SHA,
         'Frozen V4 comma-boundary plan missing or changed')
    plan = read(path)
    need(plan['schemaVersion'] == '11.05-voice-subset-repair-plan-v4' and plan['topicId'] == TOPIC,
         'Wrong repair scope')
    counts = ('logicalSentenceCount', 'canonicalSceneCount', 'paragraphCount',
              'exactReuseCount', 'newSynthesisCount')
    need(tuple(plan[k] for k in counts) == (48, 50, 14, 46, 4), 'Exact V4 scope required')
    need(plan['oldVoiceFingerprint'] == OLD_FP and plan['oldRepairFingerprint'] == OLD_REPAIR_FP,
         'Wrong prior e14a/44df identity')
    need(checked(plan['sourceNarration'], 'NarV5', NARRATION)['sha256'] == NARRATION_SHA,
         'Final source narration changed')
    need(checked(plan['protectedProjectCheckpoint'], 'frozen checkpoint', PROJECT / 'checkpoint.json')['sha256']
         == CHECKPOINT_SHA, 'Frozen project checkpoint changed')
    need(all(flag is False for flag in plan['policy'].values()), 'V4 plan waived a production boundary')
    need([row['parentSceneId'] for row in plan['logicalSentenceSplits']] == list(SPLITS),
         'Wrong split parent selection')
    return plan


def immutable_prior_voice(plan, prior):
    """Use only the e14a immutable output. Its public pointer will advance after V4."""
    proof_pin = checked(plan['oldVoiceEvidence'], 'V3 immutable voice', OLD_OUT / 'voice-complete-proof.json')
    proof = read(proof_pin['path'])
    need(prior['fingerprint'] == proof['fingerprint'] == OLD_FP
         and prior['repair']['fingerprint'] == proof['repairFingerprint'] == OLD_REPAIR_FP
         and digest(proof['identity']) == OLD_FP
         and digest(proof['repairIdentity']) == OLD_REPAIR_FP,
         'Immutable V3 voice or repair identity differs')
    lifecycle = prior_qa.voice_worker.life
    need(lifecycle.verify_complete(prior, OLD_OUT) == proof, 'Exact completed V3 proof differs')
    receipt = lifecycle.validate_receipt(prior, OLD_OUT)
    need(plan['sourceNarration'] in receipt['inputs'], 'V3 receipt does not pin exact NarV5')
    prior_qa.verify_subset_engine(prior, OLD_OUT, proof)
    receipts = {
        'priorVoiceInputs': checked(plan['oldVoiceInputs'], 'V3 voice receipt', OLD_OUT / 'voice-inputs.json'),
        'priorRepairInputs': checked(plan['oldRepairInputs'], 'V3 repair receipt', OLD_OUT / 'repair-inputs.json'),
    }
    return proof, proof_pin, receipts


def verify_prior_review(plan, proof, proof_pin):
    """Confirm the exact QA7 blind task caches and the selected numerical report."""
    job_pin = checked(plan['rawAsrJob'], 'QA7 job')
    job_path = Path(job_pin['path'])
    job = read(job_path)
    report_pin = checked(plan['rawAsrReview'], 'QA7 report', job_path.parent / 'review.json')
    report = read(report_pin['path'])
    adapter = checked(plan['rawAsrAdapter'], 'QA7 snapshot', job_path.parent / 'adapter-source.py')
    level_pin = checked(plan['rawLevelReview'], 'QA7 numerical report')
    levels = read(level_pin['path'])
    identity = job['identity']
    need(job_path == Path(job['output']) / 'job.json'
         and job_path.parent.parent == OLD_OUT / 'review/independent-asr-selected-v1'
         and job_path.parent.name == job['fingerprint'][:24]
         and job['protocol'] == prior_qa.PROTOCOL
         and digest(identity) == job['fingerprint'] == report['fingerprint'],
         'QA7 job path or identity differs')
    need(identity['voiceFingerprint'] == report['voiceFingerprint'] == OLD_FP
         and job['voiceEvidence'] == proof_pin and identity['sourceNarration'] == plan['sourceNarration']
         and identity['profile'] == prior_qa.PROFILE and identity['modelPins'] == prior_qa.qa.APPROVED['modelPins']
         and identity['trustedUtilitySHA256'] == prior_qa.qa.APPROVED['trustedSHA256']
         and adapter['sha256'] == identity['adapterSHA256'] == PINS[QA7],
         'QA7 model, narration or immutable voice binding differs')
    for source in job['sourcePins']:
        checked(source, 'QA7 source')
    tasks = identity['tasks']
    need(len(tasks) == 95 and tasks == prior_qa.qa.build_tasks(proof, read(proof['timing']['path'])),
         'Exact QA7 take/boundary sample windows differ')
    need(all(prior_qa.cached(job, task) is not None for task in tasks), 'Missing exact QA7 recognition cache')

    def existing_report(path, value):
        need(Path(path).resolve() == Path(report_pin['path']) and value == report,
             'QA7 report differs from exact recognition caches')

    summary = prior_qa.summary
    scope = dict(summary.__globals__, voice=types.SimpleNamespace(immutable_json=existing_report))
    rebuild = types.FunctionType(summary.__code__, scope, 'verify_qa7_without_write')
    need(rebuild(job) == report and report['aggregateSHA256'] == proof['aggregateWav']['sha256']
         and report['timingSHA256'] == proof['timing']['sha256']
         and (len(report['takes']), len(report['boundaryWindows']), len(report['paragraphs'])) == (48, 47, 14),
         'Wrong QA7 complete report coverage')
    need(report['aliasesApplied'] is False and report['expectedPrompt'] is None
         and report['humanListening'] is False and report['automaticSpeechPass'] is False,
         'Prior QA7 review must remain blind and pending listening')
    need(levels['voiceFingerprint'] == OLD_FP and levels['asrReview'] == report_pin
         and levels['canonicalWav'] == proof['aggregateWav']
         and (len(levels['takes']), len(levels['joins']), len(levels['paragraphs'])) == (48, 47, 14),
         'Numerical review is not bound to exact e14a/QA7 canonical PCM')
    need(checked(levels['levelPrimitive'], 'level policy primitive', HERE / 'first-level-continuity-review.py')['sha256']
         == prior_qa.qa.APPROVED['firstLevelPrimitiveSHA256'], 'Prior word-level primitive differs')
    need([row['sceneId'] for row in levels['takes']] == [row['id'] for row in proof['identity']['scenes']]
         and all(all(observed[key] == expected[key] for key in
                     ('previousScene', 'nextScene', 'joinType', 'boundarySample'))
                 for observed, expected in zip(levels['joins'], report['boundaryObservations'])),
         'Numerical take or boundary order differs')
    flags = levels['flags']
    need(len(flags) == 2 and {row['sceneId'] for row in flags} == set(SPLITS)
         and all(row['kind'] == 'sustained-take-word-body-decline' for row in flags),
         'V4 reuse excludes exactly the two sustained-decline takes')
    for split in plan['logicalSentenceSplits']:
        measured = next(row['wordTrend'] for row in levels['takes'] if row['sceneId'] == split['parentSceneId'])
        need(split['previousWordTrend'] == measured and measured['suspect'] is True,
             'Prior hard-decline evidence differs')
    peer_pin = checked(dict(path=str(CONTENT_PEER), sha256=CONTENT_PEER_SHA), 'QA7 content peer review')
    peer = read(peer_pin['path'])
    need(peer['schemaVersion'] == '11.05-voice-asr-content-peer-review-v7' and peer['topicId'] == TOPIC
         and peer['identity'] == dict(voiceFingerprint=OLD_FP, repairFingerprint=OLD_REPAIR_FP,
                                      asrFingerprint=job['fingerprint'])
         and peer['inputs'] == dict(immutableVoiceProof=proof_pin, review=report_pin,
                                    rawNumericalLevelReview=level_pin, job=job_pin, asrAdapterSnapshot=adapter)
         and peer['disposition'] == 'hold-for-two-sustained-take-body-level-declines'
         and all(value is False for value in peer['limits'].values()),
         'QA7 peer evidence is not bound to the exact held identity')
    context = peer['numericalContext']
    need(context['technicalScalarPreparationAllowed'] is False
         and {row['sceneId']: row['trend'] for row in context['neededHolds']}
         == {split['parentSceneId']: split['previousWordTrend'] for split in plan['logicalSentenceSplits']},
         'QA7 peer review must identify the exact two held takes')
    return dict(rawAsrJob=job_pin, rawAsrReview=report_pin, rawAsrAdapter=adapter,
                rawLevelReview=level_pin, contentPeerReview=peer_pin)


def physical_script(prior, plan):
    """Keep every original ID except the two replaced with a/b at exact commas."""
    script = copy.deepcopy(prior['script'])
    split_rows = {row['parentSceneId']: row for row in plan['logicalSentenceSplits']}
    original_scenes, original_mapping = script['scenes'], prior['paragraphMapping']
    need(len(original_scenes) == len(original_mapping) == 48, 'Expected all 48 authored sentence IDs')
    scenes, mapping = [], []
    for scene, row in zip(original_scenes, original_mapping):
        sid = scene['id']
        need(row['sceneId'] == sid and scene['lines'] == [row['canonicalText']], 'Prior sentence mapping differs')
        if sid not in SPLITS:
            scenes.append(scene)
            mapping.append(dict(row))
            continue
        split = split_rows[sid]
        text = row['canonicalText']
        ranges = SPLITS[sid]
        start = row['sourceCharRange'][0]
        parts = [
            {'sceneId': sid + suffix, 'sourceCharRange': [start + left, start + right], 'text': text[left:right]}
            for suffix, (left, right) in zip(('a', 'b'), ranges)
        ]
        need(parts == split['parts'] and row['paragraph'] == split['paragraph']
             and split['canonicalText'] == text and bool(split['reason'])
             and ' '.join(part['text'] for part in parts) == text and parts[0]['text'].endswith(','),
             'Split must preserve the exact authored comma, one space and full canonical sentence')
        for position, part in enumerate(parts, 1):
            scenes.append(dict(scene, id=part['sceneId'], lines=[part['text']]))
            mapping.append(dict(row, sceneId=part['sceneId'], canonicalText=part['text'],
                                sourceCharRange=part['sourceCharRange'], reason=split['reason'],
                                logicalSentenceId=sid, logicalPart=position, logicalPartCount=2))
    counts = Counter(row['paragraph'] for row in mapping)
    positions = Counter()
    for row in mapping:
        paragraph = row['paragraph']
        positions[paragraph] += 1
        row.update(component=positions[paragraph], componentCount=counts[paragraph])
    narration = read(NARRATION)
    need(len(scenes) == len({scene['id'] for scene in scenes}) == 50 and len(counts) == 14
         and len(narration['narrationKo']) == len(narration['paragraphsEn']) == 14,
         'New physical IDs or bilingual paragraph coverage differ')
    for number, text in enumerate(narration['narrationKo'], 1):
        rows = [row for row in mapping if row['paragraph'] == number]
        need(' '.join(row['canonicalText'] for row in rows) == text
             and all(text[row['sourceCharRange'][0]:row['sourceCharRange'][1]] == row['canonicalText'] for row in rows),
             'Physical mapping changed canonical NarV5 text')
    script['scenes'] = scenes
    return script, mapping


def reused_rows(proof, proof_pin, script):
    replacement_ids = set(TARGETS)
    retained = [scene for scene in script['scenes'] if scene['id'] not in replacement_ids]
    prior = [(scene, wav) for scene, wav in zip(proof['identity']['scenes'], proof['sceneWavs'])
             if scene['id'] not in SPLITS]
    need(len(retained) == len(prior) == 46, 'Expected exactly 46 e14a raw reuse rows')
    rows = []
    for scene, (old, wav) in zip(retained, prior):
        sid = scene['id']
        expected_path = OLD_OUT / 'chunks' / (sid + '-scene.wav')
        need({'id': sid, 'lines': scene['lines']} == old and Path(wav['path']).resolve() == expected_path
             and base.wav_info(expected_path) == wav, 'Retained e14a ID, text or raw WAV/PCM changed')
        rows.append(dict(oldSceneId=sid, newSceneId=sid, canonicalText=old['lines'][0],
                         sourceWav=wav, sourceVoiceEvidence=dict(proof_pin, fingerprint=OLD_FP),
                         reuseReason='Exact retained e14a raw WAV/PCM from a take without a sustained-decline flag'))
    return rows


def prepare(plan_path=PLAN, native_evidence=None, native_qa=None, narration=None):
    check_sources()
    plan = load_plan(plan_path)
    need(native_evidence is None and native_qa is None
         and Path(narration or NARRATION).resolve() == NARRATION.resolve(),
         'Only the exact completed e14a source/native and NarV5 input set is supported')
    try:
        prior = prior_qa.prepared_repair()
    except prior_qa.Pending as error:
        raise Pending(str(error)) from error
    old, old_pin, receipts = immutable_prior_voice(plan, prior)
    reviews = dict(verify_prior_review(plan, old, old_pin), **receipts)
    script, mapping = physical_script(prior, plan)
    rows = reused_rows(old, old_pin, script)
    adapter = pin(ADAPTER)
    selection = dict(protocol=PROTOCOL, plan=pin(PLAN), sourceVoiceEvidence=old_pin,
                     sourceVoiceFingerprint=OLD_FP, newNarration=plan['sourceNarration'],
                     repairSceneIds=list(TARGETS), logicalSentenceSplits=plan['logicalSentenceSplits'],
                     expectedFullCount=50, expectedNewCount=4, expectedByteReusedCount=46,
                     adapterSHA256=adapter['sha256'], preparerSHA256=SELF_SHA,
                     baseControllerSHA256=PINS['run-selected-voice.py'],
                     launcherRuntimePins=copy.deepcopy(RUNTIME_PINS),
                     launcherClassification='exact-direct-venv-execute-wrapper-v4')
    previous_full = prior['_basePrepared']
    scenes = [{'id': row['id'], 'lines': row['lines']} for row in script['scenes']]
    identity = dict(previous_full['identity'], scenes=scenes, repairSelection=selection)
    fingerprint = digest(identity)
    need(fingerprint != OLD_FP, 'New output collides with prior V3 voice')
    inputs = previous_full['inputs'] + [pin(PLAN), old_pin, adapter, pin(__file__)]
    inputs += copy.deepcopy(RUNTIME_PINS) + [pin(HERE / name) for name in PINS] + list(reviews.values())
    inputs += [{'path': row['sourceWav']['path'], 'sha256': row['sourceWav']['sha256']} for row in rows]
    inputs = list({row['path']: row for row in inputs}.values())
    prep_fp = digest(dict(synthesisIdentity=fingerprint, inputs=inputs, script=script, paragraphMapping=mapping))
    folder = PROJECT / 'production/voice-preparation' / prep_fp[:24]
    out = VOICE_ATTEMPTS / fingerprint[:24]
    manifest = copy.deepcopy(previous_full['manifest'])
    manifest['paths']['script'] = (folder / 'narration-qwen.json').relative_to(ROOT).as_posix()
    manifest['tts']['outputDir'] = out.relative_to(ROOT).as_posix()
    manifest.update(synthesisIdentity=fingerprint, repairSelection=selection)
    command = list(previous_full['qwenSynthesisArgv'])
    command[8] = (folder / 'voice-manifest.json').relative_to(ROOT).as_posix()
    selected = dict(previous_full, identity=identity, fingerprint=fingerprint, preparationFingerprint=prep_fp,
                    inputs=inputs, stagingDirectory=str(folder), voiceOutputDirectory=str(out),
                    manifest=manifest, script=script, paragraphMapping=mapping,
                    qwenSynthesisArgv=command, qwenDryRunArgv=command + ['--dry-run'])
    missing = [scene for scene in scenes if scene['id'] in TARGETS]
    need([scene['id'] for scene in missing] == list(TARGETS), 'Engine must receive only the four split clauses')
    repair_identity = dict(protocol=PROTOCOL, fullVoiceFingerprint=fingerprint, repairSelection=selection,
                           oldVoiceEvidence=dict(old_pin, fingerprint=OLD_FP), previousReviewPins=reviews,
                           reuse=rows, missingScenes=missing, plan=pin(PLAN), adapterSHA256=adapter['sha256'],
                           baseWorkerSHA256=PINS['run-selected-voice.py'],
                           lifecycleSource=pin(HERE / 'run-selected-voice-repair-v4.py'))
    repair_fp = digest(repair_identity)
    repair_folder = folder / ('repair-subset-' + repair_fp[:24])
    subset_script = dict(script, scenes=[scene for scene in script['scenes'] if scene['id'] in TARGETS])
    subset_manifest = copy.deepcopy(manifest)
    subset_manifest['paths']['script'] = (repair_folder / 'narration-missing-only.json').relative_to(ROOT).as_posix()
    subset_manifest.update(engineSceneScope='missing-subset-only', fullSynthesisIdentity=fingerprint,
                           repairFingerprint=repair_fp, engineSceneIds=list(TARGETS))
    subset_command = list(command)
    subset_command[8] = (repair_folder / 'voice-missing-only-manifest.json').relative_to(ROOT).as_posix()
    repair = dict(fingerprint=repair_fp, identity=repair_identity, rows=rows, missing=missing,
                  stagingDirectory=str(repair_folder), script=subset_script, manifest=subset_manifest,
                  command=subset_command)
    check_sources()
    need(pin(ADAPTER) == adapter, 'V4 entry source changed during preparation')
    return dict(selected, _basePrepared=selected, repair=repair,
                qwenSynthesisArgv=subset_command, qwenDryRunArgv=subset_command + ['--dry-run'])
