"""Prepare one exact two-sentence redraw for held 11.05, without writing or launching."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import sys
import types
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PROJECT = ROOT / 'projects/shorts-leveldesign-11-05'
PLAN = PROJECT / 'voice-subset-repair-plan-v5.json'
PLAN_SHA = 'd3e4fd112eb8a1e424f4436e086ff00a5c8a0839e7d6a2e991c8acc48ce67c81'
NARRATION = PROJECT / 'narration-final-v5.json'
NARRATION_SHA = 'e3179da81b2a23135eb6a8907ebb6205c14fc2d66e528a37372d491d0ffeaa91'
CHECKPOINT_SHA = '7123b2dffc7203700a296b2ceac45c23b3dece912d0da6887f3ee09e8a2512bb'
ADAPTER = HERE / 'run-solution-path-voice-repair-v5.py'
CONTENT_PEER = PROJECT / 'voice-asr-content-peer-review-v8.json'
CONTENT_PEER_SHA = 'b248bcde4cbc8ee26e4e0c3a6dc0d0daeeddb61e8ed304273851a82b76f45843'
TOPIC = '11.05'
PROTOCOL = 'architectural111-11-05-voice-subset-repair-v5'
OLD_FP = '7c14ab3038b59c5ed3e903af076bb37f9f6cc6843de518ceff34a42e536e7e02'
OLD_REPAIR_FP = '0a0cf97f6164ab04e86a02a144baa805d96cd389edbd7f5abf5497eb7356a67f'
OLD_ASR_FP = 'c9cea5e23108e6033a92406a6f97aded038630bfd730fd431ea3c5ba537425ff'
VOICE_ATTEMPTS = ROOT / 'shared/output/architectural-111-20261106/11-05/voice-attempts'
OLD_OUT = VOICE_ATTEMPTS / OLD_FP[:24]
OLD_ASR_OUT = OLD_OUT / 'review/independent-asr-selected-v1' / OLD_ASR_FP[:24]
TARGETS = ('p008-c01', 'p013-c01')
EXCLUDED_V4_SCENES = tuple(parent + suffix for parent in TARGETS for suffix in ('a', 'b'))
QA8 = 'run-solution-path-voice-qa-v8.py'
LIFECYCLE = 'run-selected-voice-repair-v4.py'
CONTROLLER = 'run-selected-voice.py'
PINS = {
    QA8: 'fb5cee2bed52d0b03faac1f6f0837802620fd467a7f5a14c6e2183b299dcff91',
    'run-solution-path-voice-repair-v4.py': '2eb51314d0210daf04d0fd97af83eb1c674fc4088557b1e4b7ded89f93282854',
    'prepare-solution-path-voice-repair-v4.py': '9a70bbe5d3886e08b3afb4a3dbc16e3751dbd039a561f5003850736d26b5dfd3',
    LIFECYCLE: 'c70ba7ff185f048bbb53c3b7845b5af2237d14de1ea3ef511e9afacdf8171366',
    CONTROLLER: '55ec247dafdef34bf2f31e9054e5a9fd3629ea2f220847b19694c48b59e26a99',
}
REVIEW_SHA = 'd49a456868dd36961b56cfbaa44d92cfe9b0deca14db779908478533782ca855'
JOB_SHA = '087d012135a82df442b574a104d3c956e618f5ddd8a12293e7e1815369553057'
VOICE_PROOF_SHA = '195f61fd32d3be041cbbc30c667976187a8217ede4cc50ea3646cb7418e7449d'
HOLD_KINDS = {
    'sustained-take-word-body-decline',
    'sustained-paragraph-word-body-decline',
    'incomplete-word-level-measurement',
}
PARENT_HOLDS = {
    'p008-c01': 'original-sentence-trend-coverage-insufficient',
    'p013-c01': 'sustained-original-sentence-word-body-decline',
}


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


def checked(row, role, expected_path=None, expected_sha=None):
    need(isinstance(row, dict) and isinstance(row.get('path'), str)
         and isinstance(row.get('sha256'), str), 'Missing pinned ' + role)
    path = Path(row['path']).resolve()
    need(expected_path is None or path == Path(expected_path).resolve(), 'Wrong path for ' + role)
    need(expected_sha is None or row['sha256'] == expected_sha, 'Wrong SHA for ' + role)
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
    need(sha(__file__) == SELF_SHA, 'V5 preparer changed after import')
    for name, expected in PINS.items():
        need(sha(HERE / name) == expected, 'Reviewed V5 dependency changed: ' + name)
    if 'prior_qa' in globals():
        prior_qa.check_sources()


check_sources()
prior_qa = module('solution_repair_v5_immutable_qa8', HERE / QA8)
voice_entry = prior_qa.repair.voice_entry
prep = voice_entry.prep
base = voice_entry.base
RUNTIME_PINS = copy.deepcopy(prior_qa.qa7.LAUNCHER_RUNTIME_PINS)


def load_plan(path):
    need(bool(PLAN_SHA) and bool(CONTENT_PEER_SHA), 'Awaiting the frozen official QA8 level and peer pins')
    path = Path(path).resolve()
    need(path == PLAN.resolve() and path.is_file() and sha(path) == PLAN_SHA,
         'Frozen V5 two-sentence repair plan missing or changed')
    plan = read(path)
    need(plan['schemaVersion'] == '11.05-voice-subset-repair-plan-v5' and plan['topicId'] == TOPIC,
         'Wrong V5 repair scope')
    counts = ('logicalSentenceCount', 'canonicalSceneCount', 'paragraphCount',
              'exactReuseCount', 'newSynthesisCount')
    need(tuple(plan[key] for key in counts) == (48, 48, 14, 46, 2), 'Exact V5 scope required')
    need(plan['oldVoiceFingerprint'] == OLD_FP and plan['oldRepairFingerprint'] == OLD_REPAIR_FP
         and plan['oldAsrFingerprint'] == OLD_ASR_FP, 'Wrong V4 or QA8 identity')
    checked(plan['sourceNarration'], 'NarV5', NARRATION, NARRATION_SHA)
    checked(plan['protectedProjectCheckpoint'], 'frozen checkpoint', PROJECT / 'checkpoint.json', CHECKPOINT_SHA)
    need(all(flag is False for flag in plan['policy'].values()), 'V5 plan waived a production boundary')
    need(tuple(row['sceneId'] for row in plan['targetSentences']) == TARGETS,
         'V5 must redraw only the two original complete sentences')
    return plan


def immutable_prior_voice(plan, prior):
    proof_pin = checked(plan['oldVoiceEvidence'], 'V4 immutable voice',
                        OLD_OUT / 'voice-complete-proof.json', VOICE_PROOF_SHA)
    proof = read(proof_pin['path'])
    need(prior['fingerprint'] == proof['fingerprint'] == digest(proof['identity']) == OLD_FP
         and prior['repair']['fingerprint'] == proof['repairFingerprint']
         == digest(proof['repairIdentity']) == OLD_REPAIR_FP
         and proof['rawSceneCount'] == len(proof['sceneWavs']) == len(proof['paragraphMapping']) == 50
         and tuple(proof['newlyGeneratedSceneIds']) == EXCLUDED_V4_SCENES,
         'Immutable V4 voice or repair identity differs')
    lifecycle = prior_qa.voice_worker.life
    need(lifecycle.verify_complete(prior, OLD_OUT) == proof, 'Exact completed V4 proof differs')
    receipt = lifecycle.validate_receipt(prior, OLD_OUT)
    need(plan['sourceNarration'] in receipt['inputs'], 'V4 receipt does not pin exact NarV5')
    prior_qa.verify_subset_engine(prior, OLD_OUT, proof)
    receipts = {
        'priorVoiceInputs': checked(plan['oldVoiceInputs'], 'V4 voice receipt', OLD_OUT / 'voice-inputs.json'),
        'priorRepairInputs': checked(plan['oldRepairInputs'], 'V4 repair receipt', OLD_OUT / 'repair-inputs.json'),
    }
    return proof, proof_pin, receipts


def verify_parent_levels(plan, proof, proof_pin, job_pin, report_pin, report):
    level_pin = checked(plan['rawLevelReview'], 'QA8 take, paragraph and join level report')
    level_path = Path(level_pin['path'])
    need(level_path.parent.parent == OLD_ASR_OUT / 'raw-level-review' and level_path.name == 'review.json',
         'Wrong QA8 physical level report scope')
    parent_pin = checked(plan['rawOriginalSentenceLevelReview'], 'QA8 original-sentence levels',
                         level_path.parent / 'original-sentence-review-v8.json')
    levels, original = read(level_path), read(parent_pin['path'])
    mathqa = module('solution_repair_v5_parent_level_math', prior_qa.LEVEL_PRIMITIVE)
    expected_primitive = pin(prior_qa.LEVEL_PRIMITIVE)
    need(levels['voiceFingerprint'] == original['voiceFingerprint'] == OLD_FP
         and levels['asrReview'] == original['asrReview'] == report_pin
         and levels['canonicalWav'] == original['canonicalWav'] == proof['aggregateWav']
         and original['voiceEvidence'] == proof_pin and original['asrJob'] == job_pin
         and original['physicalTakeParagraphJoinLevels'] == level_pin
         and original['protocol'] == 'architectural111-11-05-original-sentence-level-v8'
         and (len(levels['takes']), len(levels['joins']), len(levels['paragraphs'])) == (50, 49, 14)
         and levels['policy'] == original['policy'] == mathqa.POLICY
         and levels['levelPrimitive'] == original['levelPrimitive'] == expected_primitive,
         'QA8 level reports are not bound to the exact V4 raw voice and approved level math')
    need([row['sceneId'] for row in levels['takes']] == [scene['id'] for scene in proof['identity']['scenes']]
         and all(all(observed[key] == expected[key] for key in
                     ('previousScene', 'nextScene', 'joinType', 'boundarySample'))
                 for observed, expected in zip(levels['joins'], report['boundaryObservations'], strict=True))
         and not any(flag['kind'] in HOLD_KINDS for flag in levels['flags']),
         'V5 may reuse only the 46 takes from the exact checked QA8 scope')
    parents, flags = prior_qa.parent_sentence_levels(levels['takes'], mathqa)
    need(original['originalSentences'] == parents and original['originalSentenceFlags'] == flags
         and original['flags'] == levels['flags'] + flags and original['numericalHold'] is True
         and len(flags) == 2 and {flag['logicalSentenceId']: flag['kind'] for flag in flags} == PARENT_HOLDS
         and all(original[key] is False for key in
                 ('pcmModified', 'normalizationApplied', 'automaticSpeechPass', 'actualListening', 'humanApproval')),
         'Exact two original-sentence holds must be reproduced without relaxing coverage or thresholds')
    for target, flag in zip(plan['targetSentences'], flags, strict=True):
        need(target['sceneId'] == flag['logicalSentenceId'] and target['priorHoldKind'] == flag['kind']
             and target['priorWordTrend'] == flag['trend'], 'V5 target level evidence differs')
    return level_pin, parent_pin


def verify_prior_review(plan, proof, proof_pin):
    job_pin = checked(plan['rawAsrJob'], 'QA8 job', OLD_ASR_OUT / 'job.json', JOB_SHA)
    report_pin = checked(plan['rawAsrReview'], 'QA8 report', OLD_ASR_OUT / 'review.json', REVIEW_SHA)
    adapter = checked(plan['rawAsrAdapter'], 'QA8 snapshot', OLD_ASR_OUT / 'adapter-source.py', PINS[QA8])
    job, report = read(job_pin['path']), read(report_pin['path'])
    identity = job['identity']
    need(Path(job['output']).resolve() == OLD_ASR_OUT and Path(job['voiceOutput']).resolve() == OLD_OUT
         and job['protocol'] == identity['protocol'] == prior_qa.PROTOCOL
         and digest(identity) == job['fingerprint'] == report['fingerprint'] == OLD_ASR_FP
         and identity['voiceFingerprint'] == report['voiceFingerprint'] == OLD_FP
         and identity['repairFingerprint'] == OLD_REPAIR_FP and job['voiceEvidence'] == proof_pin
         and identity['sourceNarration'] == plan['sourceNarration']
         and identity['profile'] == prior_qa.PROFILE and identity['modelPins'] == prior_qa.qa.APPROVED['modelPins']
         and identity['trustedUtilitySHA256'] == prior_qa.qa.APPROVED['trustedSHA256']
         and adapter['sha256'] == identity['adapterSHA256'],
         'QA8 job, model, narration or immutable voice binding differs')
    for source in job['sourcePins']:
        checked(source, 'QA8 source')
    tasks = identity['tasks']
    need(len(tasks) == 99 and tasks == prior_qa.qa.build_tasks(proof, read(proof['timing']['path'])),
         'Exact QA8 take and join sample windows differ')

    def existing_report(path, value):
        need(Path(path).resolve() == Path(report_pin['path']) and value == report,
             'QA8 report differs from exact recognition caches')

    summary = prior_qa.summary
    scope = dict(summary.__globals__, voice=types.SimpleNamespace(immutable_json=existing_report))
    rebuild = types.FunctionType(summary.__code__, scope, 'verify_qa8_without_write')
    need(rebuild(job) == report and report['aggregateSHA256'] == proof['aggregateWav']['sha256']
         and report['timingSHA256'] == proof['timing']['sha256']
         and (len(report['takes']), len(report['boundaryWindows']), len(report['paragraphs'])) == (50, 49, 14)
         and report['aliasesApplied'] is False and report['expectedPrompt'] is None
         and report['humanListening'] is False and report['automaticSpeechPass'] is False,
         'QA8 blind summary, literal timing or scope differs')
    level_pin, parent_pin = verify_parent_levels(plan, proof, proof_pin, job_pin, report_pin, report)
    peer_pin = checked(dict(path=str(CONTENT_PEER), sha256=CONTENT_PEER_SHA), 'QA8 content peer review')
    peer = read(peer_pin['path'])
    peer_inputs = dict(immutableVoiceProof=proof_pin, review=report_pin, job=job_pin, asrAdapterSnapshot=adapter,
                       rawNumericalLevelReview=level_pin, rawOriginalSentenceLevelReview=parent_pin)
    need(peer['schemaVersion'] == '11.05-voice-asr-content-peer-review-v8' and peer['topicId'] == TOPIC
         and peer['identity'] == dict(voiceFingerprint=OLD_FP, repairFingerprint=OLD_REPAIR_FP,
                                      asrFingerprint=OLD_ASR_FP)
         and all(peer['inputs'].get(key) == value for key, value in peer_inputs.items())
         and peer['disposition'] == 'hold-for-original-sentence-level-or-coverage',
         'QA8 content peer is not bound to the exact held review and voice identity')
    return dict(rawAsrJob=job_pin, rawAsrReview=report_pin, rawAsrAdapter=adapter, rawLevelReview=level_pin,
                rawOriginalSentenceLevelReview=parent_pin, contentPeerReview=peer_pin)


def exact_sentence_plan(plan, prior):
    source, draft, script, mapping = prior_qa.qa7.source_context()
    scenes = script['scenes']
    need(pin(source) == plan['sourceNarration']
         and len(scenes) == len(mapping) == len({row['id'] for row in scenes}) == 48
         and len(draft['narrationKo']) == len(draft['paragraphsEn']) == 14,
         'Expected 48 canonical NarV5 sentences and 14 bilingual paragraphs')
    by_id = {row['sceneId']: row for row in mapping}
    prior_by_id = {row['sceneId']: row for row in prior['paragraphMapping']}
    for target in plan['targetSentences']:
        scene_id = target['sceneId']
        row = by_id[scene_id]
        parts = [prior_by_id[scene_id + suffix] for suffix in ('a', 'b')]
        need(row['canonicalText'] == target['canonicalText'] and row['paragraph'] == target['paragraph']
             and row['sourceCharRange'] == target['sourceCharRange'] and bool(target['reason'])
             and row['canonicalText'] == ' '.join(part['canonicalText'] for part in parts)
             and row['sourceCharRange'] == [parts[0]['sourceCharRange'][0], parts[1]['sourceCharRange'][1]]
             and parts[0]['canonicalText'].endswith(','),
             'V5 whole sentence must reproduce both V4 parts and the original authored comma')
    return script, mapping


def reused_rows(proof, proof_pin, script):
    retained = [scene for scene in script['scenes'] if scene['id'] not in TARGETS]
    prior = [(scene, wav) for scene, wav in zip(proof['identity']['scenes'], proof['sceneWavs'], strict=True)
             if scene['id'] not in EXCLUDED_V4_SCENES]
    need(len(retained) == len(prior) == 46, 'Expected exactly 46 V4 raw reuse rows')
    rows = []
    for scene, (old, wav) in zip(retained, prior, strict=True):
        scene_id = scene['id']
        expected_path = OLD_OUT / 'chunks' / (scene_id + '-scene.wav')
        need({'id': scene_id, 'lines': scene['lines']} == old and Path(wav['path']).resolve() == expected_path
             and base.wav_info(expected_path) == wav, 'Retained V4 ID, text or raw WAV/PCM changed')
        rows.append(dict(oldSceneId=scene_id, newSceneId=scene_id, canonicalText=old['lines'][0],
                         sourceWav=wav, sourceVoiceEvidence=dict(proof_pin, fingerprint=OLD_FP),
                         reuseReason='Exact retained V4 raw WAV/PCM outside the two held original sentences'))
    return rows


def prepare(plan_path=PLAN, native_evidence=None, native_qa=None, narration=None):
    check_sources()
    plan = load_plan(plan_path)
    need(native_evidence is None and native_qa is None
         and Path(narration or NARRATION).resolve() == NARRATION.resolve(),
         'Only the exact completed V4 source, native evidence and NarV5 inputs are supported')
    try:
        prior = prior_qa.prepared_repair()
        script, mapping = exact_sentence_plan(plan, prior)
    except prior_qa.Pending as error:
        raise Pending(str(error)) from error
    old, old_pin, receipts = immutable_prior_voice(plan, prior)
    reviews = dict(verify_prior_review(plan, old, old_pin), **receipts)
    rows = reused_rows(old, old_pin, script)
    adapter = pin(ADAPTER)
    plan_pin = pin(PLAN)
    selection = dict(protocol=PROTOCOL, plan=plan_pin, sourceVoiceEvidence=old_pin,
                     sourceVoiceFingerprint=OLD_FP, newNarration=plan['sourceNarration'],
                     repairSceneIds=list(TARGETS), targetSentences=plan['targetSentences'],
                     expectedFullCount=48, expectedNewCount=2, expectedByteReusedCount=46,
                     adapterSHA256=adapter['sha256'], preparerSHA256=SELF_SHA,
                     baseControllerSHA256=PINS[CONTROLLER], launcherRuntimePins=copy.deepcopy(RUNTIME_PINS),
                     launcherClassification='exact-direct-venv-execute-wrapper-v5')
    previous_full = prior['_basePrepared']
    scenes = [{'id': row['id'], 'lines': row['lines']} for row in script['scenes']]
    identity = dict(previous_full['identity'], scenes=scenes, repairSelection=selection)
    fingerprint = digest(identity)
    need(fingerprint != OLD_FP, 'New output collides with prior V4 voice')
    inputs = previous_full['inputs'] + [plan_pin, old_pin, adapter, pin(__file__)]
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
    need(tuple(scene['id'] for scene in missing) == TARGETS, 'Engine must receive only the two complete sentences')
    repair_identity = dict(protocol=PROTOCOL, fullVoiceFingerprint=fingerprint, repairSelection=selection,
                           oldVoiceEvidence=dict(old_pin, fingerprint=OLD_FP), previousReviewPins=reviews,
                           reuse=rows, missingScenes=missing, plan=plan_pin, adapterSHA256=adapter['sha256'],
                           baseWorkerSHA256=PINS[CONTROLLER], lifecycleSource=pin(HERE / LIFECYCLE))
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
    need(pin(ADAPTER) == adapter and pin(PLAN) == plan_pin, 'V5 entry source or plan changed during preparation')
    return dict(selected, _basePrepared=selected, repair=repair,
                qwenSynthesisArgv=subset_command, qwenDryRunArgv=subset_command + ['--dry-run'])
