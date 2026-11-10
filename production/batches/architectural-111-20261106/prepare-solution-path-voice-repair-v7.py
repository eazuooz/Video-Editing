"""Prepare two prosody-only 11.05 repair takes without staging or GPU work."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PROJECT = ROOT / 'projects/shorts-leveldesign-11-05'
PLAN = PROJECT / 'voice-subset-repair-plan-v7.json'
NARRATION = PROJECT / 'narration-final-v5.json'
ADAPTER = HERE / 'run-solution-path-voice-repair-v7.py'
PREVIOUS = HERE / 'prepare-solution-path-voice-repair-v6.py'
CONTENT_PEER = PROJECT / 'user-recording-content-peer-review-v1.json'
CONTEXT_HOLD = PROJECT / 'voice-asr-content-peer-review-v10.json'
PROTOCOL = 'architectural111-11-05-voice-subset-repair-v7'
TARGETS = ('p008-c01', 'p013-c01')
PINS = {
    PLAN: '7ad1901c0d92675fe0e6b237dbbca39cf1aa450af097dcc8d429dd9f19a42b30',
    PREVIOUS: 'b654346dd54953378463db12c4d4be35835d272c36f260c39198d1903accb3b2',
    CONTENT_PEER: 'b797c94376fac3f0666b992e0fd9ba623dcbc3f98f411b6f7ee2b7afc3616b17',
    CONTEXT_HOLD: 'efab305ba28bc113c864720eb77d9edd001498471d77c15a69a086ad46355aa8',
}
REUSE_COUNT = 46


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


SELF_SHA = sha(__file__)


def check_sources():
    if sha(__file__) != SELF_SHA or any(sha(path) != expected for path, expected in PINS.items()):
        raise RuntimeError('Pinned V7 repair source changed')
    if 'previous' in globals():
        previous.check_sources()


check_sources()
spec = importlib.util.spec_from_file_location('solution_v7_immutable_v6_preparer', PREVIOUS)
previous = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = previous
spec.loader.exec_module(previous)
Pending, need, pin, read, digest = previous.Pending, previous.need, previous.pin, previous.read, previous.digest
prep = previous.prep
base = previous.base
CONTROLLER, LIFECYCLE = previous.CONTROLLER, previous.LIFECYCLE
RUNTIME_PINS = copy.deepcopy(previous.RUNTIME_PINS)


def apply_prosody(script, mapping, targets):
    """Validate one additional comma per scoped take and retain the canonical map."""
    result = copy.deepcopy(script)
    by_scene = {scene['id']: scene for scene in result['scenes']}
    by_source = {item['sceneId']: item for item in mapping}
    need(len(by_scene) == len(by_source) == 48, 'Exact 48-sentence scope is required')
    need(tuple(row['sceneId'] for row in targets) == TARGETS, 'V7 may change only the two selected takes')
    for target in targets:
        scene = by_scene[target['sceneId']]
        original = by_source[target['sceneId']]
        canonical = target['canonicalText']
        position = target['insertCommaAfter'] + ' '
        need(scene['lines'] == [canonical] and original['canonicalText'] == canonical
             and original['paragraph'] == target['paragraph'] and canonical.count(position) == 1,
             'Original sentence or the exact prosody cue differs')
        adjusted = canonical.replace(position, position[:-1] + ', ', 1)
        need(target['engineText'] == adjusted and adjusted != canonical
             and adjusted.replace(',', '') == canonical.replace(',', ''),
             'Only the named comma addition is permitted')
        scene['lines'] = [adjusted]
    return result


def reused_rows(proof, old_pin, scenes):
    retained = [scene for scene in scenes if scene['id'] not in TARGETS]
    prior = [(scene, wav) for scene, wav in zip(proof['identity']['scenes'], proof['sceneWavs'], strict=True)
             if scene['id'] not in TARGETS]
    need(len(retained) == len(prior) == REUSE_COUNT, 'V7 requires exactly 46 raw reused takes')
    rows = []
    for scene, (old, wav) in zip(retained, prior, strict=True):
        scene_id = scene['id']
        raw = previous.OLD_OUT / 'chunks' / (scene_id + '-scene.wav')
        need(scene == old and Path(wav['path']).resolve() == raw
             and base.wav_info(raw) == wav, 'Retained V5 WAV, PCM or sentence mapping changed')
        rows.append(dict(oldSceneId=scene_id, newSceneId=scene_id, canonicalText=scene['lines'][0],
                         sourceWav=wav, sourceVoiceEvidence=dict(old_pin, fingerprint=previous.OLD_FP),
                         reuseReason='Exact V5 raw take outside the two synthesis-only prosody edits'))
    return rows


def prepare(plan_path=PLAN, native_evidence=None, native_qa=None, narration=None):
    check_sources()
    need(Path(plan_path).resolve() == PLAN and native_evidence is None and native_qa is None
         and Path(narration or NARRATION).resolve() == NARRATION, 'Exact V7 source scope is required')
    plan, prior_plan = read(PLAN), previous.load_plan(previous.PLAN)
    need(plan['schemaVersion'] == '11.05-voice-subset-repair-plan-v7' and plan['topicId'] == '11.05'
         and all(flag is False for flag in plan['policy'].values())
         and plan['actualVoiceAccepted'] is False, 'V7 repair plan relaxed its scope')
    exact_old_fields = ('sourceNarration', 'protectedProjectCheckpoint', 'oldVoiceEvidence', 'oldVoiceInputs',
                        'oldRepairInputs', 'oldVoiceFingerprint', 'oldRepairFingerprint', 'oldAsrFingerprint')
    need(all(plan[key] == prior_plan[key] for key in exact_old_fields), 'V7 old-source identity differs')
    peer = read(CONTENT_PEER)
    need(peer['acceptedForFinal'] is False and peer['actualExecution']['reviewCreated'] is True
         and peer['disposition'] == 'hold-recording-for-literal-mismatch-and-p013-sustained-decline',
         'The exact independent recording disposition is required')
    recording_pins = []
    for record in peer['inputs'].values():
        actual = pin(ROOT / record['path'])
        need(actual['sha256'] == record['sha256'], 'Held recording evidence changed')
        recording_pins.append(actual)
    need(read(CONTEXT_HOLD)['acceptedDownstreamInput'] is False, 'The prior contextual hold changed')

    prior = previous.prior_qa.repair.prepare()
    proof, old_pin, receipts = previous.immutable_prior_voice(prior_plan, prior)
    reviews = dict(previous.verify_prior_review(prior_plan, proof, old_pin), **receipts)
    full = prior['_basePrepared']
    mapping = copy.deepcopy(prior['paragraphMapping'])
    script = apply_prosody(prior['script'], mapping, plan['targetSentences'])
    scenes = [{'id': scene['id'], 'lines': scene['lines']} for scene in script['scenes']]
    need([row['sceneId'] for row in mapping] == [row['id'] for row in scenes]
         and {row['paragraph'] for row in mapping} == set(range(1, 15)),
         'Original 48 sentences and 14 paragraphs must stay in order')
    rows = reused_rows(proof, old_pin, scenes)
    adapter, plan_pin = pin(ADAPTER), pin(PLAN)
    selection = dict(protocol=PROTOCOL, plan=plan_pin, sourceVoiceEvidence=old_pin,
                     sourceVoiceFingerprint=previous.OLD_FP, newNarration=plan['sourceNarration'],
                     repairSceneIds=list(TARGETS), targetSentences=plan['targetSentences'],
                     expectedFullCount=48, expectedNewCount=2, expectedByteReusedCount=REUSE_COUNT,
                     adapterSHA256=adapter['sha256'], preparerSHA256=SELF_SHA,
                     baseControllerSHA256=previous.PINS[CONTROLLER],
                     launcherRuntimePins=copy.deepcopy(RUNTIME_PINS),
                     launcherClassification='exact-direct-venv-execute-wrapper-v7')
    identity = dict(full['identity'], scenes=scenes, repairSelection=selection)
    fingerprint = digest(identity)
    need(fingerprint != previous.OLD_FP, 'V7 must have a distinct voice identity')
    inputs = full['inputs'] + [plan_pin, old_pin, adapter, pin(__file__)]
    inputs += list(reviews.values()) + list(RUNTIME_PINS) + recording_pins + [pin(path) for path in PINS]
    inputs += [{'path': row['sourceWav']['path'], 'sha256': row['sourceWav']['sha256']} for row in rows]
    inputs = list({row['path']: row for row in inputs}.values())
    prep_fp = digest(dict(synthesisIdentity=fingerprint, inputs=inputs, script=script, paragraphMapping=mapping))
    folder = PROJECT / 'production/voice-preparation' / prep_fp[:24]
    out = previous.VOICE_ATTEMPTS / fingerprint[:24]
    manifest = copy.deepcopy(full['manifest'])
    manifest['paths']['script'] = (folder / 'narration-qwen.json').relative_to(ROOT).as_posix()
    manifest['tts']['outputDir'] = out.relative_to(ROOT).as_posix()
    manifest.update(synthesisIdentity=fingerprint, repairSelection=selection)
    command = list(full['qwenSynthesisArgv'])
    command[8] = (folder / 'voice-manifest.json').relative_to(ROOT).as_posix()
    selected = dict(full, identity=identity, fingerprint=fingerprint, preparationFingerprint=prep_fp,
                    inputs=inputs, stagingDirectory=str(folder), voiceOutputDirectory=str(out),
                    manifest=manifest, script=script, paragraphMapping=mapping,
                    qwenSynthesisArgv=command, qwenDryRunArgv=command + ['--dry-run'])
    missing = [scene for scene in scenes if scene['id'] in TARGETS]
    need(tuple(scene['id'] for scene in missing) == TARGETS, 'V7 engine scope must contain only the two new takes')
    repair_identity = dict(protocol=PROTOCOL, fullVoiceFingerprint=fingerprint, repairSelection=selection,
                           oldVoiceEvidence=dict(old_pin, fingerprint=previous.OLD_FP), previousReviewPins=reviews,
                           reuse=rows, missingScenes=missing, plan=plan_pin, adapterSHA256=adapter['sha256'],
                           baseWorkerSHA256=previous.PINS[CONTROLLER], lifecycleSource=pin(HERE / LIFECYCLE))
    repair_fp = digest(repair_identity)
    subset_folder = folder / ('repair-subset-' + repair_fp[:24])
    subset_script = dict(script, scenes=[scene for scene in script['scenes'] if scene['id'] in TARGETS])
    subset_manifest = copy.deepcopy(manifest)
    subset_manifest['paths']['script'] = (subset_folder / 'narration-missing-only.json').relative_to(ROOT).as_posix()
    subset_manifest.update(engineSceneScope='missing-subset-only', fullSynthesisIdentity=fingerprint,
                           repairFingerprint=repair_fp, engineSceneIds=list(TARGETS))
    subset_command = list(command)
    subset_command[8] = (subset_folder / 'voice-missing-only-manifest.json').relative_to(ROOT).as_posix()
    repair = dict(fingerprint=repair_fp, identity=repair_identity, rows=rows, missing=missing,
                  stagingDirectory=str(subset_folder), script=subset_script, manifest=subset_manifest,
                  command=subset_command)
    check_sources()
    need(pin(ADAPTER) == adapter and pin(PLAN) == plan_pin, 'V7 exact sources changed during preparation')
    return dict(selected, _basePrepared=selected, repair=repair,
                qwenSynthesisArgv=subset_command, qwenDryRunArgv=subset_command + ['--dry-run'])
