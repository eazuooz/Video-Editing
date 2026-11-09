"""Prepare two exact contiguous sentence groups for 11.05 without writing or launching."""
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
PLAN = PROJECT / 'voice-subset-repair-plan-v6.json'
PLAN_SHA = '53cc4ab288eb82a97f7d80517f325b3b17bcb3302ef4bc30a731c809507d488d'
NARRATION = PROJECT / 'narration-final-v5.json'
NARRATION_SHA = 'e3179da81b2a23135eb6a8907ebb6205c14fc2d66e528a37372d491d0ffeaa91'
CHECKPOINT_SHA = '7123b2dffc7203700a296b2ceac45c23b3dece912d0da6887f3ee09e8a2512bb'
ADAPTER = HERE / 'run-solution-path-voice-repair-v6.py'
CONTENT_PEER = PROJECT / 'voice-asr-content-peer-review-v9.json'
CONTENT_PEER_SHA = 'd30cd043ecd737265bdf6a0dee0d905c9567130458a81079a5c46462f024ce24'
TOPIC = '11.05'
PROTOCOL = 'architectural111-11-05-voice-subset-repair-v6'
OLD_FP = 'cc4613a2ea742d612e6efb1e7aaf0d2a4bc65eeb24c345647fde761dc75eb9b6'
OLD_REPAIR_FP = '1b7d09da3ceb930ebf5c8849a3cb4fe898d84bbea44669a4b74b04147b991575'
OLD_ASR_FP = '909d54e4551baf2b437e411a8b79e6c87f4351b72ea44a165257b56421375d68'
VOICE_ATTEMPTS = ROOT / 'shared/output/architectural-111-20261106/11-05/voice-attempts'
OLD_OUT = VOICE_ATTEMPTS / OLD_FP[:24]
OLD_ASR_OUT = OLD_OUT / 'review/independent-asr-selected-v1' / OLD_ASR_FP[:24]
CONTEXT_GROUPS = {'p008-g01': ('p008-c01', 'p008-c02'), 'p013-g01': ('p013-c01', 'p013-c02')}
TARGETS = tuple(CONTEXT_GROUPS)
FAILED_SENTENCES = tuple(members[0] for members in CONTEXT_GROUPS.values())
REPLACED_SENTENCES = tuple(member for members in CONTEXT_GROUPS.values() for member in members)
QA9 = 'run-solution-path-voice-qa-v9.py'
LIFECYCLE = 'run-selected-voice-repair-v4.py'
CONTROLLER = 'run-selected-voice.py'
PINS = {
    QA9: '4297a851234d5510a0e740338c43398dfd6449f2694ec1bc0f899562ba2ad77f',
    'run-solution-path-voice-repair-v5.py': '5b7507eb9f425aa35f7aec087c9ab6976272b71bc0a6ed7520688086e5bf191b',
    'prepare-solution-path-voice-repair-v5.py': '9fb371c219c59a14291bcbcd551f70fb03b6cb64a19b0a2cd83d98f57872a960',
    LIFECYCLE: 'c70ba7ff185f048bbb53c3b7845b5af2237d14de1ea3ef511e9afacdf8171366',
    CONTROLLER: '55ec247dafdef34bf2f31e9054e5a9fd3629ea2f220847b19694c48b59e26a99',
}
JOB_SHA = '4e1868a9c68f4edb2a61889dd47017326c0213b37491ceca630e8c93496d9cef'
VOICE_PROOF_SHA = '2f88f6442fe3fba0761384685e05611ff39f49c23b35f5bbe9bdcd79ac9bad87'
BASE_HOLDS = {
    'sustained-take-word-body-decline', 'sustained-paragraph-word-body-decline',
    'incomplete-word-level-measurement',
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
    need(sha(__file__) == SELF_SHA, 'V6 preparer changed after import')
    for name, expected in PINS.items():
        need(sha(HERE / name) == expected, 'Reviewed V6 dependency changed: ' + name)
    if 'prior_qa' in globals():
        prior_qa.check_sources()


check_sources()
prior_qa = module('solution_repair_v6_immutable_qa9', HERE / QA9)
voice_entry = prior_qa.repair.voice_entry
prep = voice_entry.prep
base = voice_entry.base
RUNTIME_PINS = copy.deepcopy(prior_qa.qa7.LAUNCHER_RUNTIME_PINS)


def load_plan(path):
    need(bool(PLAN_SHA) and bool(CONTENT_PEER_SHA), 'Awaiting frozen official QA9 levels and peer pins')
    path = Path(path).resolve()
    need(path == PLAN.resolve() and path.is_file() and sha(path) == PLAN_SHA,
         'Frozen V6 contextual repair plan missing or changed')
    plan = read(path)
    need(plan['schemaVersion'] == '11.05-voice-subset-repair-plan-v6' and plan['topicId'] == TOPIC,
         'Wrong V6 repair scope')
    counts = ('logicalSentenceCount', 'canonicalSceneCount', 'paragraphCount',
              'exactReuseCount', 'newSynthesisCount')
    need(tuple(plan[key] for key in counts) == (48, 46, 14, 44, 2), 'Exact V6 scope required')
    need(plan['oldVoiceFingerprint'] == OLD_FP and plan['oldRepairFingerprint'] == OLD_REPAIR_FP
         and plan['oldAsrFingerprint'] == OLD_ASR_FP, 'Wrong V5 or QA9 identity')
    checked(plan['sourceNarration'], 'NarV5', NARRATION, NARRATION_SHA)
    checked(plan['protectedProjectCheckpoint'], 'frozen checkpoint', PROJECT / 'checkpoint.json', CHECKPOINT_SHA)
    need(all(flag is False for flag in plan['policy'].values()), 'V6 plan waived a production boundary')
    need([(row['sceneId'], tuple(row['sentenceIds'])) for row in plan['contextGroups']]
         == list(CONTEXT_GROUPS.items()), 'V6 requires only the two exact adjacent sentence groups')
    return plan


def immutable_prior_voice(plan, prior):
    proof_pin = checked(plan['oldVoiceEvidence'], 'V5 immutable voice',
                        OLD_OUT / 'voice-complete-proof.json', VOICE_PROOF_SHA)
    proof = read(proof_pin['path'])
    need(prior['fingerprint'] == proof['fingerprint'] == digest(proof['identity']) == OLD_FP
         and prior['repair']['fingerprint'] == proof['repairFingerprint']
         == digest(proof['repairIdentity']) == OLD_REPAIR_FP
         and proof['rawSceneCount'] == len(proof['sceneWavs']) == len(proof['paragraphMapping']) == 48
         and tuple(proof['newlyGeneratedSceneIds']) == FAILED_SENTENCES
         and proof['paragraphMapping'] == prior['paragraphMapping'],
         'Immutable V5 voice or repair identity differs')
    lifecycle = prior_qa.voice_worker.life
    need(lifecycle.verify_complete(prior, OLD_OUT) == proof, 'Exact completed V5 proof differs')
    receipt = lifecycle.validate_receipt(prior, OLD_OUT)
    need(plan['sourceNarration'] in receipt['inputs'], 'V5 receipt does not pin exact NarV5')
    prior_qa.verify_subset_engine(prior, OLD_OUT, proof,
                                 [row['newSceneId'] for row in prior['repair']['rows']])
    return proof, proof_pin, {
        'priorVoiceInputs': checked(plan['oldVoiceInputs'], 'V5 voice receipt', OLD_OUT / 'voice-inputs.json'),
        'priorRepairInputs': checked(plan['oldRepairInputs'], 'V5 repair receipt', OLD_OUT / 'repair-inputs.json'),
    }


def verify_parent_levels(plan, proof, proof_pin, job_pin, report_pin, report):
    level_pin = checked(plan['rawLevelReview'], 'QA9 take, paragraph and join level report')
    level_path = Path(level_pin['path'])
    need(level_path.parent.parent == OLD_ASR_OUT / 'raw-level-review' and level_path.name == 'review.json',
         'Wrong QA9 physical level report scope')
    parent_pin = checked(plan['rawOriginalSentenceLevelReview'], 'QA9 original-sentence levels',
                         level_path.parent / 'original-sentence-review-v9.json')
    levels, original = read(level_path), read(parent_pin['path'])
    mathqa = module('solution_repair_v6_parent_level_math', prior_qa.LEVEL_PRIMITIVE)
    expected_primitive = pin(prior_qa.LEVEL_PRIMITIVE)
    need(levels['voiceFingerprint'] == original['voiceFingerprint'] == OLD_FP
         and levels['asrReview'] == original['asrReview'] == report_pin
         and levels['canonicalWav'] == original['canonicalWav'] == proof['aggregateWav']
         and original['voiceEvidence'] == proof_pin and original['asrJob'] == job_pin
         and original['physicalTakeParagraphJoinLevels'] == level_pin
         and original['protocol'] == 'architectural111-11-05-original-sentence-level-v9'
         and (len(levels['takes']), len(levels['joins']), len(levels['paragraphs'])) == (48, 47, 14)
         and levels['policy'] == original['policy'] == mathqa.POLICY
         and levels['levelPrimitive'] == original['levelPrimitive'] == expected_primitive,
         'QA9 level reports do not bind the exact V5 raw voice and approved level math')
    need([row['sceneId'] for row in levels['takes']] == [scene['id'] for scene in proof['identity']['scenes']]
         and all(all(observed[key] == expected[key] for key in
                     ('previousScene', 'nextScene', 'joinType', 'boundarySample'))
                 for observed, expected in zip(levels['joins'], report['boundaryObservations'], strict=True)),
         'QA9 physical take or join scope changed')
    hard_base = [(row.get('sceneId'), row['kind']) for row in levels['flags'] if row['kind'] in BASE_HOLDS]
    need(hard_base == [(scene, 'sustained-take-word-body-decline') for scene in FAILED_SENTENCES],
         'QA9 physical holds must be limited to the two exact failed V5 takes')
    parents, flags = prior_qa.parent_sentence_levels(levels['takes'], mathqa)
    need(original['originalSentences'] == parents and original['originalSentenceFlags'] == flags
         and original['flags'] == levels['flags'] + flags and original['numericalHold'] is True
         and [(row['logicalSentenceId'], row['kind']) for row in flags]
         == [(scene, 'sustained-original-sentence-word-body-decline') for scene in FAILED_SENTENCES]
         and all(original[key] is False for key in
                 ('pcmModified', 'normalizationApplied', 'automaticSpeechPass', 'actualListening', 'humanApproval')),
         'Exact two original-sentence holds must reproduce under unchanged policy')
    for group, flag in zip(plan['contextGroups'], flags, strict=True):
        need(group['sentenceIds'][0] == flag['logicalSentenceId'] and group['priorHoldKind'] == flag['kind']
             and group['priorWordTrend'] == flag['trend'], 'V6 context group level evidence differs')
    return level_pin, parent_pin


def verify_prior_review(plan, proof, proof_pin):
    job_pin = checked(plan['rawAsrJob'], 'QA9 job', OLD_ASR_OUT / 'job.json', JOB_SHA)
    report_pin = checked(plan['rawAsrReview'], 'QA9 report', OLD_ASR_OUT / 'review.json')
    adapter = checked(plan['rawAsrAdapter'], 'QA9 snapshot', OLD_ASR_OUT / 'adapter-source.py', PINS[QA9])
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
         'QA9 job, model, narration or immutable voice binding differs')
    for source in job['sourcePins']:
        checked(source, 'QA9 source')
    tasks = identity['tasks']
    need(len(tasks) == 95 and tasks == prior_qa.qa.build_tasks(proof, read(proof['timing']['path'])),
         'Exact QA9 take and join sample windows differ')

    def existing_report(path, value):
        need(Path(path).resolve() == Path(report_pin['path']) and value == report,
             'QA9 report differs from exact recognition caches')

    summary = prior_qa.summary
    scope = dict(summary.__globals__, voice=types.SimpleNamespace(immutable_json=existing_report))
    rebuild = types.FunctionType(summary.__code__, scope, 'verify_qa9_without_write')
    need(rebuild(job) == report and report['aggregateSHA256'] == proof['aggregateWav']['sha256']
         and report['timingSHA256'] == proof['timing']['sha256']
         and (len(report['takes']), len(report['boundaryWindows']), len(report['paragraphs'])) == (48, 47, 14)
         and report['aliasesApplied'] is False and report['expectedPrompt'] is None
         and report['humanListening'] is False and report['automaticSpeechPass'] is False,
         'QA9 blind summary, literal timing or scope differs')
    level_pin, parent_pin = verify_parent_levels(plan, proof, proof_pin, job_pin, report_pin, report)
    peer_pin = checked(dict(path=str(CONTENT_PEER), sha256=CONTENT_PEER_SHA), 'QA9 content peer review')
    peer = read(peer_pin['path'])
    peer_inputs = dict(immutableVoiceProof=proof_pin, review=report_pin, job=job_pin, asrAdapterSnapshot=adapter,
                       rawNumericalLevelReview=level_pin, rawOriginalSentenceLevelReview=parent_pin)
    need(peer['schemaVersion'] == '11.05-voice-asr-content-peer-review-v9' and peer['topicId'] == TOPIC
         and peer['identity'] == dict(voiceFingerprint=OLD_FP, repairFingerprint=OLD_REPAIR_FP,
                                      asrFingerprint=OLD_ASR_FP)
         and all(peer['inputs'].get(key) == value for key, value in peer_inputs.items())
         and peer['disposition'] == 'hold-for-sustained-original-sentence-word-body-decline',
         'QA9 content peer is not bound to the exact held review and voice identity')
    return dict(rawAsrJob=job_pin, rawAsrReview=report_pin, rawAsrAdapter=adapter, rawLevelReview=level_pin,
                rawOriginalSentenceLevelReview=parent_pin, contentPeerReview=peer_pin)


def exact_context_plan(plan, prior):
    source, draft, logical_script, logical_mapping = prior_qa.qa7.source_context()
    ko = draft['narrationKo']
    need(pin(source) == plan['sourceNarration'] and prior['paragraphMapping'] == logical_mapping
         and len(logical_script['scenes']) == len(logical_mapping) == 48
         and len(ko) == len(draft['paragraphsEn']) == 14,
         'Expected V5 exact NarV5 sentence map')
    scene_by_id = {row['id']: row for row in logical_script['scenes']}
    group_by_start = {row['sentenceIds'][0]: row for row in plan['contextGroups']}
    skip = {members[1] for members in CONTEXT_GROUPS.values()}
    paragraphs = {n: [] for n in range(1, len(ko) + 1)}
    for index, logical in enumerate(logical_mapping):
        sid, paragraph = logical['sceneId'], logical['paragraph']
        if sid in skip:
            continue
        group = group_by_start.get(sid)
        members = [logical]
        physical_id, reason = sid, logical['reason']
        if group is not None:
            members.append(logical_mapping[index + 1])
            physical_id, reason = group['sceneId'], group['reason']
            need([member['sceneId'] for member in members] == group['sentenceIds']
                 and all(member['paragraph'] == paragraph for member in members)
                 and group['paragraph'] == paragraph and bool(reason.strip()),
                 'Context group must contain the exact two adjacent full sentences in one paragraph')
        start, end = members[0]['sourceCharRange'][0], members[-1]['sourceCharRange'][1]
        text = ko[paragraph - 1][start:end]
        need(text == ' '.join(member['canonicalText'] for member in members),
             'Context text changed canonical wording, order or spacing')
        source_sentences = [
            dict(sentenceId=member['sceneId'], sourceCharRange=member['sourceCharRange'],
                 sceneCharRange=[member['sourceCharRange'][0] - start, member['sourceCharRange'][1] - start],
                 canonicalText=member['canonicalText'])
            for member in members
        ]
        if group is not None:
            need(group['sourceCharRange'] == [start, end] and group['canonicalText'] == text
                 and group['sourceSentences'] == source_sentences,
                 'Context plan source spans or exact text differ')
        scene = dict(scene_by_id[sid], id=physical_id, lines=[text])
        row = dict(paragraph=paragraph, sceneId=physical_id, sourceCharRange=[start, end],
                   canonicalText=text, reason=reason, sourceSentences=source_sentences)
        paragraphs[paragraph].append((scene, row))

    semantic = dict(topicId=TOPIC, sourceNarrationSHA256=plan['sourceNarration']['sha256'], paragraphs=[
        dict(paragraph=n, components=[dict(text=row['canonicalText'], reason=row['reason']) for _, row in entries])
        for n, entries in paragraphs.items() if len(entries) > 1
    ])
    # The approved semantic validator keeps the whole P8 paragraph by default.
    # Every multi-component paragraph is checked against its exact sentence boundaries.
    approved = prep.core.components_for(ko, semantic, plan['sourceNarration']['sha256'])
    scenes, mapping = [], []
    for n, entries in paragraphs.items():
        need([row['canonicalText'] for _, row in entries] == [row['text'] for row in approved[n]],
             'Context grouping differs from the approved full-sentence component policy')
        for component, (scene, row) in enumerate(entries, 1):
            scenes.append(scene)
            mapping.append(dict(row, component=component, componentCount=len(entries)))
    need(len(scenes) == len(mapping) == len({scene['id'] for scene in scenes}) == 46
         and [span['sentenceId'] for row in mapping for span in row['sourceSentences']]
         == [row['sceneId'] for row in logical_mapping], 'Context map must cover all 48 original sentences once')
    return dict(logical_script, scenes=scenes), mapping


def reused_rows(proof, proof_pin, script):
    retained = [scene for scene in script['scenes'] if scene['id'] not in TARGETS]
    prior = [(scene, wav) for scene, wav in zip(proof['identity']['scenes'], proof['sceneWavs'], strict=True)
             if scene['id'] not in REPLACED_SENTENCES]
    need(len(retained) == len(prior) == 44, 'Expected exactly 44 V5 raw reuse rows')
    rows = []
    for scene, (old, wav) in zip(retained, prior, strict=True):
        scene_id = scene['id']
        expected_path = OLD_OUT / 'chunks' / (scene_id + '-scene.wav')
        need({'id': scene_id, 'lines': scene['lines']} == old and Path(wav['path']).resolve() == expected_path
             and base.wav_info(expected_path) == wav, 'Retained V5 ID, text or raw WAV/PCM changed')
        rows.append(dict(oldSceneId=scene_id, newSceneId=scene_id, canonicalText=old['lines'][0],
                         sourceWav=wav, sourceVoiceEvidence=dict(proof_pin, fingerprint=OLD_FP),
                         reuseReason='Exact retained V5 raw WAV/PCM outside the two contextual groups'))
    return rows


def prepare(plan_path=PLAN, native_evidence=None, native_qa=None, narration=None):
    check_sources()
    plan = load_plan(plan_path)
    need(native_evidence is None and native_qa is None
         and Path(narration or NARRATION).resolve() == NARRATION.resolve(),
         'Only the exact completed V5 source, native evidence and NarV5 inputs are supported')
    try:
        prior = prior_qa.repair.prepare()
        script, mapping = exact_context_plan(plan, prior)
    except (prior_qa.Pending, prior_qa.repair.Pending) as error:
        raise Pending(str(error)) from error
    old, old_pin, receipts = immutable_prior_voice(plan, prior)
    reviews = dict(verify_prior_review(plan, old, old_pin), **receipts)
    rows = reused_rows(old, old_pin, script)
    adapter, plan_pin = pin(ADAPTER), pin(PLAN)
    selection = dict(protocol=PROTOCOL, plan=plan_pin, sourceVoiceEvidence=old_pin,
                     sourceVoiceFingerprint=OLD_FP, newNarration=plan['sourceNarration'],
                     repairSceneIds=list(TARGETS), contextGroups=plan['contextGroups'],
                     replacedSentenceIds=list(REPLACED_SENTENCES), expectedLogicalSentenceCount=48,
                     expectedFullCount=46, expectedNewCount=2, expectedByteReusedCount=44,
                     adapterSHA256=adapter['sha256'], preparerSHA256=SELF_SHA,
                     baseControllerSHA256=PINS[CONTROLLER], launcherRuntimePins=copy.deepcopy(RUNTIME_PINS),
                     launcherClassification='exact-direct-venv-execute-wrapper-v6')
    previous_full = prior['_basePrepared']
    scenes = [{'id': row['id'], 'lines': row['lines']} for row in script['scenes']]
    identity = dict(previous_full['identity'], scenes=scenes, repairSelection=selection)
    need(identity['rawPcmPolicy']['semanticComponents'] ==
         'optional exact contiguous full-sentence groups; no arbitrary line quotas',
         'Approved profile does not bind the contextual sentence policy')
    fingerprint = digest(identity)
    need(fingerprint != OLD_FP, 'New output collides with prior V5 voice')
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
    need(tuple(scene['id'] for scene in missing) == TARGETS, 'Engine must receive only the two contextual groups')
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
    need(pin(ADAPTER) == adapter and pin(PLAN) == plan_pin, 'V6 entry source or plan changed during preparation')
    return dict(selected, _basePrepared=selected, repair=repair,
                qwenSynthesisArgv=subset_command, qwenDryRunArgv=subset_command + ['--dry-run'])
