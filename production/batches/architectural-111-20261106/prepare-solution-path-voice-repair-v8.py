"""Prepare the user-authorized canonical rephrasing from an immutable receipt.

Verify each distinct input once, instead of recursively preparing every historical
repair. Synthesis, source facts, voice profile and resource gates remain unchanged.
"""
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
PLAN = PROJECT / 'voice-subset-repair-plan-v8.json'
NARRATION = PROJECT / 'narration-final-v6.json'
ADAPTER = HERE / 'run-solution-path-voice-repair-v8.py'
RESOURCE_QUALIFIER = HERE / 'prospect-refuge-resource-qualification-v2.py'
PREVIOUS = HERE / 'prepare-solution-path-voice-repair-v7.py'
PROTOCOL = 'architectural111-11-05-voice-subset-repair-v8'
TARGETS = ('p008-c01', 'p013-c01')

def sha(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

PINS = {
    PLAN: 'b96156a56ac9be75b3788f715b2ee9b30fa2b0af0b53b6e09f4049706f0969ae',
    NARRATION: '10ca24e3ab44cf07c55d32ad18b232ec2ea58e67cad68a26c338628a3edcf59a',
    PREVIOUS: '4852da3df87f45a64b6c92d93bb03caa01fe133132caf0ecf65037a0e199198b',
}
SELF_SHA = sha(__file__)

def check_sources():
    if sha(__file__) != SELF_SHA or any(sha(p) != s for p, s in PINS.items()):
        raise RuntimeError('Pinned V8 canonical revision changed')

check_sources()
spec = importlib.util.spec_from_file_location('v8_frozen_v7_dependencies', PREVIOUS)
previous = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = previous
spec.loader.exec_module(previous)
Pending, need, pin, read, digest = previous.Pending, previous.need, previous.pin, previous.read, previous.digest
prep, base = previous.prep, previous.base
CONTROLLER, LIFECYCLE = previous.CONTROLLER, previous.LIFECYCLE
RUNTIME_PINS = copy.deepcopy(previous.RUNTIME_PINS)

def checked(record):
    need(pin(record['path']) == record, 'Changed immutable V8 source: ' + record['path'])
    return read(record['path'])

def source_context():
    result = prepare()
    return NARRATION, read(NARRATION), result['script'], result['paragraphMapping']

def apply_prosody(script, mapping, targets):
    """QA compatibility: the canonical V8 input already includes the rewrite."""
    by_id = {r['sceneId']: r for r in mapping}
    scenes = {s['id']: s for s in script['scenes']}
    need(tuple(r['sceneId'] for r in targets) == TARGETS, 'Wrong V8 comparison targets')
    for row in targets:
        sid = row['sceneId']
        need(by_id[sid]['canonicalText'] == row['newKo'] and scenes[sid]['lines'] == [row['newKo']],
             'QA must compare against the actual revised canonical words')
    return copy.deepcopy(script)

def prepare(plan_path=PLAN, native_evidence=None, native_qa=None, narration=None):
    check_sources()
    need(Path(plan_path).resolve() == PLAN and native_evidence is None and native_qa is None
         and Path(narration or NARRATION).resolve() == NARRATION, 'Exact V8 scope required')
    plan = read(PLAN)
    need(plan['schemaVersion'] == '11.05-voice-subset-repair-plan-v8' and plan['actualVoiceAccepted'] is False,
         'Wrong V8 source plan')
    auth = checked(plan['authorization'])
    need(auth['scriptRevisionAuthorized'] is True and '11.05' in auth['newlySelected'], 'Missing script revision authority')
    checked(plan['protectedProjectCheckpoint'])
    old, new = checked(plan['previousNarration']), checked(plan['sourceNarration'])
    snapshot, proof = checked(plan['priorPreparationSnapshot']), checked(plan['oldVoiceEvidence'])
    need(digest(proof['identity']) == proof['fingerprint'] == snapshot['fingerprint'] == plan['oldVoiceFingerprint']
         and snapshot['paragraphMapping'] == proof['paragraphMapping'], 'Prior receipt identity differs')
    need(tuple(r['sceneId'] for r in plan['targetSentences']) == TARGETS, 'Wrong rewrite scope')
    # Keep all historical sources pinned; verify once per distinct path.
    inputs = {r['path']: r for r in snapshot['inputs']}
    for r in inputs.values():
        need(sha(r['path']) == r['sha256'], 'Historical source changed: ' + r['path'])
    script = copy.deepcopy(snapshot['script'])
    mapping = copy.deepcopy(snapshot['paragraphMapping'])
    replacements = {r['sceneId']: r for r in plan['targetSentences']}
    for scene, row in zip(script['scenes'], mapping, strict=True):
        sid = scene['id']
        need(row['sceneId'] == sid, 'Source component ordering differs')
        if sid in replacements:
            r = replacements[sid]
            need(row['canonicalText'] == r['oldKo'] and row['paragraph'] == r['paragraph'], 'Old rewrite prose differs')
            row['canonicalText'] = r['newKo']
            row['reason'] = r['reason']
            scene['lines'] = [r['newKo']]
        else:
            need(scene['lines'] == [row['canonicalText']], 'Unchanged engine text differs')
    for paragraph in range(1, 15):
        rows = [r for r in mapping if r['paragraph'] == paragraph]
        text = ' '.join(r['canonicalText'] for r in rows)
        need(text == new['narrationKo'][paragraph-1], 'New canonical paragraph differs')
        cursor = 0
        for row in rows:
            row['sourceCharRange'] = [cursor, cursor+len(row['canonicalText'])]
            cursor += len(row['canonicalText'])+1
        if paragraph not in (8, 13):
            need(new['narrationKo'][paragraph-1] == old['narrationKo'][paragraph-1]
                 and new['paragraphsEn'][paragraph-1] == old['paragraphsEn'][paragraph-1], 'Unaffected paragraph changed')
    scenes = [{'id':s['id'], 'lines':s['lines']} for s in script['scenes']]
    need(len(scenes) == 48 and len(set(s['id'] for s in scenes)) == 48, 'Keep 48 stable component IDs')
    rows = []
    for scene, prior_scene, wav in zip(scenes, proof['identity']['scenes'], proof['sceneWavs'], strict=True):
        if scene['id'] in TARGETS:
            continue
        need(scene == prior_scene and base.wav_info(wav['path']) == wav, 'Reused raw WAV, PCM or text changed')
        rows.append(dict(oldSceneId=scene['id'], newSceneId=scene['id'], canonicalText=scene['lines'][0],
                         sourceWav=wav, sourceVoiceEvidence=dict(plan['oldVoiceEvidence'], fingerprint=proof['fingerprint']),
                         reuseReason='Exact unaffected raw take; both held target takes excluded'))
    need(len(rows) == 46, 'Exactly 46 unaffected raw takes required')
    selection = dict(protocol=PROTOCOL, plan=pin(PLAN), sourceVoiceEvidence=plan['oldVoiceEvidence'],
                     sourceVoiceFingerprint=proof['fingerprint'], newNarration=pin(NARRATION),
                     repairSceneIds=list(TARGETS), targetSentences=plan['targetSentences'],
                     expectedFullCount=48, expectedNewCount=2, expectedByteReusedCount=46,
                     adapterSHA256=sha(ADAPTER), preparerSHA256=SELF_SHA,
                     baseControllerSHA256=sha(HERE/CONTROLLER), launcherRuntimePins=RUNTIME_PINS,
                     launcherClassification='exact-direct-venv-execute-wrapper-v8')
    identity = dict(snapshot['identity'], scenes=scenes, repairSelection=selection)
    fingerprint = digest(identity)
    extra = [pin(p) for p in (*PINS, RESOURCE_QUALIFIER, ADAPTER, Path(__file__))]
    extra += [plan[k] for k in ('authorization','sourceNarration','previousNarration','priorPreparationSnapshot','oldVoiceEvidence','protectedProjectCheckpoint')]
    extra += [{'path':r['sourceWav']['path'], 'sha256':r['sourceWav']['sha256']} for r in rows]
    for r in extra:
        inputs[r['path']] = r
    prep_fp = digest(dict(synthesisIdentity=fingerprint, inputs=list(inputs.values()), script=script, paragraphMapping=mapping))
    folder = PROJECT/'production/voice-preparation'/prep_fp[:24]
    out = ROOT/'shared/output/architectural-111-20261106/11-05/voice-attempts'/fingerprint[:24]
    manifest = copy.deepcopy(snapshot['manifest'])
    manifest['paths']['script'] = (folder/'narration-qwen.json').relative_to(ROOT).as_posix()
    manifest['tts']['outputDir'] = out.relative_to(ROOT).as_posix()
    manifest.update(sourceNarrationSHA256=sha(NARRATION), synthesisIdentity=fingerprint, repairSelection=selection)
    command = list(snapshot['qwenSynthesisArgv'])
    command[8] = (folder/'voice-manifest.json').relative_to(ROOT).as_posix()
    selected = dict(snapshot, identity=identity, fingerprint=fingerprint, preparationFingerprint=prep_fp,
                    inputs=list(inputs.values()), sourceNarration=pin(NARRATION), stagingDirectory=str(folder),
                    voiceOutputDirectory=str(out), manifest=manifest, script=script, paragraphMapping=mapping,
                    qwenSynthesisArgv=command, qwenDryRunArgv=command+['--dry-run'])
    missing = [s for s in scenes if s['id'] in TARGETS]
    repair_identity = dict(protocol=PROTOCOL, fullVoiceFingerprint=fingerprint, repairSelection=selection,
                           oldVoiceEvidence=dict(plan['oldVoiceEvidence'], fingerprint=proof['fingerprint']),
                           previousReviewPins={}, reuse=rows, missingScenes=missing, plan=pin(PLAN),
                           adapterSHA256=sha(ADAPTER), baseWorkerSHA256=sha(HERE/CONTROLLER), lifecycleSource=pin(HERE/LIFECYCLE))
    repair_fp = digest(repair_identity)
    subset_folder = folder/('repair-subset-'+repair_fp[:24])
    subset_script = dict(script, scenes=[s for s in script['scenes'] if s['id'] in TARGETS])
    subset_manifest = copy.deepcopy(manifest)
    subset_manifest['paths']['script'] = (subset_folder/'narration-missing-only.json').relative_to(ROOT).as_posix()
    subset_manifest.update(engineSceneScope='missing-subset-only', fullSynthesisIdentity=fingerprint,
                           repairFingerprint=repair_fp, engineSceneIds=list(TARGETS))
    subset_command = list(command)
    subset_command[8] = (subset_folder/'voice-missing-only-manifest.json').relative_to(ROOT).as_posix()
    repair = dict(fingerprint=repair_fp, identity=repair_identity, rows=rows, missing=missing,
                  stagingDirectory=str(subset_folder), script=subset_script, manifest=subset_manifest, command=subset_command)
    check_sources()
    return dict(selected, _basePrepared=selected, repair=repair,
                qwenSynthesisArgv=subset_command, qwenDryRunArgv=subset_command+['--dry-run'])
