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
PLAN = PROJECT / 'voice-subset-repair-plan-v10.json'
NARRATION = PROJECT / 'narration-final-v7.json'
ADAPTER = HERE / 'run-solution-path-voice-repair-v10.py'
RESOURCE_QUALIFIER = HERE / 'prospect-refuge-resource-qualification-v2.py'
PREVIOUS = HERE / 'prepare-solution-path-voice-repair-v9.py'
PROTOCOL = 'architectural111-11-05-voice-subset-repair-v10'
PARENTS = ('p008-c01', 'p013-c01')
TARGETS = ('p008-c01a','p013-c01b','p013-c01c')

def sha(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

PINS = {
    PLAN: '7fe50fdda901221cb632473e40631e2139c7141d3207f693d99b02a302e2f64b',
    NARRATION: '0e4786acc33531b5e1df18a95f6c4a07ab85fc86c4c8f07221ae800662ccf0a1',
    PREVIOUS: 'a1f69766e834a1957bf1d5c03337a368982419fd7945e3a4c4a7790096c57439',
}
SELF_SHA = sha(__file__)

def check_sources():
    if sha(__file__) != SELF_SHA or any(sha(p) != s for p, s in PINS.items()):
        raise RuntimeError('Pinned V10 canonical revision changed')

check_sources()
spec = importlib.util.spec_from_file_location('v10_frozen_v7_dependencies', PREVIOUS)
previous = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = previous
spec.loader.exec_module(previous)
Pending, need, pin, read, digest = previous.Pending, previous.need, previous.pin, previous.read, previous.digest
prep, base = previous.prep, previous.base
CONTROLLER, LIFECYCLE = previous.CONTROLLER, previous.LIFECYCLE
RUNTIME_PINS = copy.deepcopy(previous.RUNTIME_PINS)

def checked(record):
    need(pin(record['path']) == record, 'Changed immutable V10 source: ' + record['path'])
    return read(record['path'])

def source_context():
    result = prepare()
    return NARRATION, read(NARRATION), result['script'], result['paragraphMapping']

def apply_prosody(script, mapping, targets):
    """QA compatibility: the canonical V10 input already includes the rewrite."""
    by_id = {r['sceneId']: r for r in mapping}
    scenes = {s['id']: s for s in script['scenes']}
    need(tuple(r['parentSceneId'] for r in targets) == PARENTS, 'Wrong complete-sentence parents')
    for group in targets:
        for part in group['parts']:
            sid = part['sceneId']
            need(by_id[sid]['canonicalText'] == part['text'] and scenes[sid]['lines'] == [part['text']],
                 'QA must compare the actual full sentence')
    return copy.deepcopy(script)


def prepare(plan_path=PLAN, native_evidence=None, native_qa=None, narration=None):
    check_sources()
    need(Path(plan_path).resolve() == PLAN and native_evidence is None and native_qa is None
         and Path(narration or NARRATION).resolve() == NARRATION, 'Exact V10 scope required')
    plan = read(PLAN)
    need(plan['schemaVersion'] == '11.05-voice-subset-repair-plan-v10' and plan['actualVoiceAccepted'] is False,
         'Wrong V10 source plan')
    auth = checked(plan['authorization'])
    need(auth['scriptRevisionAuthorized'] is True and '11.05' in auth['newlySelected'], 'Missing script revision authority')
    checked(plan['protectedProjectCheckpoint'])
    new = checked(plan['sourceNarration'])
    prior_review = checked(plan['priorQaReview'])
    need(prior_review['disposition'].startswith('preserve-v9-do-not-adopt'), 'Prior held review differs')
    snapshot, proof = checked(plan['priorPreparationSnapshot']), checked(plan['oldVoiceEvidence'])
    need(digest(proof['identity']) == proof['fingerprint'] == snapshot['fingerprint'] == plan['oldVoiceFingerprint']
         and snapshot['paragraphMapping'] == proof['paragraphMapping'], 'Prior receipt identity differs')
    need(tuple(r['parentSceneId'] for r in plan['logicalSentenceSplits']) == PARENTS, 'Wrong split scope')
    inputs = {r['path']: r for r in snapshot['inputs']}
    for r in inputs.values():
        need(sha(r['path']) == r['sha256'], 'Historical source changed: ' + r['path'])
    script = copy.deepcopy(snapshot['script'])
    replacements={r['oldSceneId']:r for r in plan['physicalPriorChanges']}
    need(set(replacements)=={'p008-c01a','p013-c01b'}, 'Exact previous component scope required')
    full,mapping=[],[]
    for scene,row in zip(script['scenes'],snapshot['paragraphMapping'],strict=True):
        sid=scene['id']
        need(row['sceneId']==sid and scene['lines']==[row['canonicalText']], 'Prior mapping differs')
        if sid not in replacements:
            full.append(copy.deepcopy(scene));mapping.append(copy.deepcopy(row));continue
        change=replacements[sid]
        need(change['oldKo']==row['canonicalText'], 'Previous wording changed')
        for part in change['parts']:
            need(part['sceneId'] in TARGETS and part['text'].endswith('.'), 'Complete canonical sentence required')
            full.append(dict(scene,id=part['sceneId'],lines=[part['text']]))
            mapping.append(dict(row,sceneId=part['sceneId'],canonicalText=part['text']))
    script['scenes']=full
    by_id={row['sceneId']:row for row in mapping}
    for group in plan['logicalSentenceSplits']:
        need(' '.join(by_id[part['sceneId']]['canonicalText'] for part in group['parts'])==group['canonicalText'], 'Whole semantic explanation differs')
        for i,part in enumerate(group['parts'],1):
            by_id[part['sceneId']].update(logicalSentenceId=group['parentSceneId'],logicalPart=i,logicalPartCount=len(group['parts']),reason=group['reason'])
    old_narration=checked(plan['previousNarration'])
    for paragraph in range(1,15):
        rows=[r for r in mapping if r['paragraph']==paragraph]
        need(' '.join(r['canonicalText'] for r in rows)==new['narrationKo'][paragraph-1], 'Canonical paragraph/order changed')
        if paragraph not in (8,13):
            need(new['narrationKo'][paragraph-1]==old_narration['narrationKo'][paragraph-1] and new['paragraphsEn'][paragraph-1]==old_narration['paragraphsEn'][paragraph-1], 'Unaffected bilingual paragraph changed')
        cursor=0
        for i,row in enumerate(rows,1):
            row.update(sourceCharRange=[cursor,cursor+len(row['canonicalText'])],component=i,componentCount=len(rows));cursor+=len(row['canonicalText'])+1
    scenes=[{'id':s['id'],'lines':s['lines']} for s in script['scenes']]
    need(len(scenes)==51 and len(set(s['id'] for s in scenes))==51, 'Exactly 51 physical sentences required')
    rows = []
    old_rows = {s['id']:(s,w) for s,w in zip(proof['identity']['scenes'],proof['sceneWavs'],strict=True)}
    for scene in scenes:
        if scene['id'] in TARGETS:
            continue
        prior_scene,wav=old_rows[scene['id']]
        need(scene == prior_scene and base.wav_info(wav['path']) == wav, 'Reused raw WAV, PCM or text changed')
        rows.append(dict(oldSceneId=scene['id'], newSceneId=scene['id'], canonicalText=scene['lines'][0],
                         sourceWav=wav, sourceVoiceEvidence=dict(plan['oldVoiceEvidence'], fingerprint=proof['fingerprint']),
                         reuseReason='Exact unaffected raw take; both held target takes excluded'))
    need(len(rows) == 48, 'Exactly 48 unaffected raw takes required')
    selection = dict(protocol=PROTOCOL, plan=pin(PLAN), sourceVoiceEvidence=plan['oldVoiceEvidence'],
                     sourceVoiceFingerprint=proof['fingerprint'], newNarration=pin(NARRATION),
                     repairSceneIds=list(TARGETS), logicalSentenceSplits=plan['logicalSentenceSplits'],
                     expectedFullCount=51, expectedNewCount=3, expectedByteReusedCount=48,
                     adapterSHA256=sha(ADAPTER), preparerSHA256=SELF_SHA,
                     baseControllerSHA256=sha(HERE/CONTROLLER), launcherRuntimePins=RUNTIME_PINS,
                     launcherClassification='exact-direct-venv-execute-wrapper-v10')
    identity = dict(snapshot['identity'], scenes=scenes, repairSelection=selection)
    fingerprint = digest(identity)
    extra = [pin(p) for p in (*PINS, RESOURCE_QUALIFIER, ADAPTER, Path(__file__))]
    extra += [plan[k] for k in ('authorization','sourceNarration','previousNarration','scenePlan','priorQaReview','priorPreparationSnapshot','oldVoiceEvidence','protectedProjectCheckpoint')]
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
