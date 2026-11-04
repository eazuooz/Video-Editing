"""Bounded Marine-only label revision. Preparation is CPU-only; archival is guarded separately."""
from pathlib import Path
import argparse
import copy
import importlib.util
import sys

PRODUCTION = Path(__file__).resolve().parent
ROOT = PRODUCTION.parents[2]
BATCH = ROOT / 'production/batches/tech-ten-shorts-20261030'
SLUG = 'shorts-starcraft2-marine-random-firing-delay'
sys.path.insert(0, str(BATCH))
spec = importlib.util.spec_from_file_location('marine_label_v2_runner', BATCH / 'run-batch.py')
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)


def prepare():
    ctx = r.make_context(SLUG)
    ctx['guard']()
    project, local = ctx['P'], ctx['LOCAL'].resolve()
    folder = local / 'label-v2-preparation'
    if (folder / 'prepared.json').exists():
        raise RuntimeError('Already prepared; preserve the existing revision instead of replaying this mutation.')
    oldfp = r.read(folder / 'fingerprints-before.json')
    preserved = r.read(folder / 'preserved-inputs.json')
    for item in preserved:
        r.verify([item['original'], item['preserved']])
    native = r.read(folder / 'native-original-tree.json')
    r.verify(native)
    for slug, expected in oldfp.items():
        if slug != SLUG and r.fingerprints(ROOT / 'projects' / slug) != expected:
            raise RuntimeError('Another project fingerprint changed before preparation: ' + slug)
    state_path = local / 'finite-pipeline-v1/state.json'
    state = r.read(state_path)
    if state['fingerprints'] != oldfp[SLUG]:
        raise RuntimeError('The old Marine state does not match the preserved baseline.')
    for stage in state['stages'].values():
        if stage['status'] == 'pass':
            r.verify(stage['artifacts'])
    source_manifest = r.read(PRODUCTION / 'label-v2-source-manifest.json')
    for rel, expected in source_manifest['baseSourceCode'].items():
        if r.sha(BATCH / 'unity-source' / rel) != expected:
            raise RuntimeError('Shared native source was changed: ' + rel)
    pipeline = r.read(PRODUCTION / 'visual-pipeline.json')
    old_prefix = 'production/batches/tech-ten-shorts-20261030/unity-source/'
    new_prefix = 'projects/' + SLUG + '/production/native-source-label-v2/'
    replaced = [p for p in pipeline['codePaths'] if p.startswith(old_prefix)]
    if len(replaced) != 14:
        raise RuntimeError('Expected the original fourteen native source inputs.')
    pipeline['codePaths'] = [p.replace(old_prefix, new_prefix, 1) if p.startswith(old_prefix) else p
                             for p in pipeline['codePaths']]
    pipeline['codePaths'].append('projects/' + SLUG + '/production/label-v2-source-manifest.json')
    old_name, new_name = SLUG + '-tech-ten-v1', SLUG + '-tech-ten-v1-label-v2'
    pipeline['renderCommand'] = [p.replace(old_name, new_name) for p in pipeline['renderCommand']]
    for key in ['visualOutput', 'renderReceipt']:
        pipeline[key] = pipeline[key].replace(old_name, new_name)
    pipeline['nativeCaptureCommand'][4] = '{ROOT}/projects/' + SLUG + '/production/capture-unity-label-v2.py'
    r.save(PRODUCTION / 'visual-pipeline.json', pipeline)
    manifest = r.read(project / 'project.json')
    manifest['currentFinalDirectory'] = 'production/local/final-reviewed-v2'
    manifest['currentVisualVersion'] = 'label-v2'
    for key, value in manifest['paths'].items():
        manifest['paths'][key] = value.replace('final-reviewed-v1', 'final-reviewed-v2')
    r.save(project / 'project.json', manifest)
    current = r.fingerprints(project)
    retained = {'voice', 'voice-asr', 'captions'}
    obj = r.Pipeline.__new__(r.Pipeline)
    obj.ctx, obj.project, obj.audio, obj.slug, obj.input_fingerprints = ctx, project, ctx['L'], SLUG, current
    for name in retained:
        stage = state['stages'][name]
        if stage['status'] != 'pass' or stage['dependencies'] != obj.dependencies(name):
            raise RuntimeError('An unchanged speech/caption dependency no longer matches: ' + name)
    for name in list(state['stages']):
        if name not in retained:
            state.setdefault('history', []).append({'stage': name, 'record': state['stages'].pop(name),
                'reason': 'Marine label-v2 preparation only. Prior native and visual outputs retained at original paths; not current v2 results.'})
    state.setdefault('fingerprintHistory', []).append({'previous': state['fingerprints'], 'replacedAt': r.now(),
        'reusedStages': sorted(retained), 'reason': 'Marine-only source variant, adapter, render/final destination change; exact speech/caption dependencies unchanged.'})
    state['fingerprints'] = current
    state.update(status='label-v2-prepared-native-preflight-pending', currentStage='visual-preparation', updatedAt=r.now())
    state['pendingNativeArchive'] = {'required': True, 'completed': False,
        'originalTreeManifest': str(folder / 'native-original-tree.json'),
        'command': 'prepare-label-v2.py --archive-native',
        'reason': 'Wait for competing production Unity to exit; old output must be preserved before v2 capture.'}
    r.save(state_path, state)
    readiness_path = BATCH / 'readiness.json'
    readiness = r.read(readiness_path)
    entry = readiness['projects'][SLUG]
    entry['fingerprints'] = current
    entry['codeReadyForActualProduction'] = False
    entry['marineLabelV2'] = {'status': 'cpu-prepared-native-preflight-pending',
        'sourceTreeSHA256': source_manifest['variantSourceTreeSHA256'],
        'pending': ['resource slot', 'guarded old-native archival', 'new native label/leader preflight'],
        'oldNativeTreePreservedInPlace': True, 'actualNativeLabelCheckPerformed': False}
    r.save(readiness_path, readiness)
    after = {slug: r.fingerprints(ROOT / 'projects' / slug) for slug in oldfp}
    if any(after[slug] != oldfp[slug] for slug in oldfp if slug != SLUG):
        raise RuntimeError('Non-Marine fingerprint unexpectedly changed.')
    r.verify(native)
    receipt = {'slug': SLUG, 'revision': 'label-v2', 'preparedAt': r.now(),
        'newFingerprint': current, 'retainedStages': sorted(retained),
        'preservedInputs': r.artifact(folder / 'preserved-inputs.json'),
        'preservedNativeTree': r.artifact(folder / 'native-original-tree.json'),
        'otherNineFingerprintsUnchanged': True, 'beforeFingerprints': r.artifact(folder / 'fingerprints-before.json'),
        'preparedState': r.artifact(state_path), 'sourceManifest': r.artifact(PRODUCTION / 'label-v2-source-manifest.json'),
        'nativeArchivePerformed': False, 'nativeCapturePerformed': False, 'nativeLabelPreflight': 'pending',
        'gpuWorkStarted': False, 'humanFinalReview': 'pending'}
    r.save(folder / 'fingerprints-after.json', after)
    r.save(folder / 'prepared.json', receipt)
    print('Marine v2 CPU preparation complete; nine other fingerprints unchanged; native preflight/readiness remains pending.')


def archive_native():
    ctx = r.make_context(SLUG)
    ctx['guard']()
    local = ctx['LOCAL'].resolve()
    folder = local / 'label-v2-preparation'
    prepared = r.read(folder / 'prepared.json')
    if r.fingerprints(ctx['P']) != prepared['newFingerprint']:
        raise RuntimeError('Prepared revision changed; inspect before archival.')
    if (folder / 'native-archive-receipt.json').exists():
        raise RuntimeError('Native tree is already archived; do not repeat.')
    original = local / 'unity-capture'
    destination = folder / 'native-original-preserved'
    if original.resolve() != local / 'unity-capture' or destination.resolve().parent != folder.resolve():
        raise RuntimeError('Archive paths are outside their exact selected local workspace.')
    if destination.exists():
        raise RuntimeError('Preserved archive destination already exists.')
    rows = r.read(folder / 'native-original-tree.json')
    actual_paths = sorted(str(p.resolve()) for p in original.rglob('*') if p.is_file())
    if actual_paths != sorted(item['path'] for item in rows):
        raise RuntimeError('Old native tree file set changed.')
    with r.SerialJobLock(SLUG, 'prepare-native-archive'):
        r.safe_resources(ctx, 'prepare-native-archive')
        r.verify(rows)
        # Both exact resolved paths were validated above; rename only this one tree.
        original.rename(destination)
        mapped = []
        for item in rows:
            target = destination / Path(item['path']).relative_to(original)
            proof = {'path': str(target), 'bytes': item['bytes'], 'sha256': item['sha256']}
            r.verify([proof])
            mapped.append({'originalPath': item['path'], 'archivedPath': str(target),
                           'bytes': item['bytes'], 'sha256': item['sha256']})
        source = r.read(PRODUCTION / 'label-v2-source-manifest.json')
        r.save(folder / 'native-archive-receipt.json', {'slug': SLUG, 'archivedAt': r.now(),
            'originalRoot': str(original), 'archiveRoot': str(destination), 'preservedFiles': mapped,
            'variantSourceTreeSHA256': source['variantSourceTreeSHA256'],
            'originalReceiptBytesUnmodified': True, 'pathRelocationMapRequiredForOriginalReceipt': True,
            'newNativeCapturePerformed': False})
    print('Original native bytes preserved with explicit path relocation map; no capture or readiness approval performed.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    choice = parser.add_mutually_exclusive_group(required=True)
    choice.add_argument('--prepare', action='store_true')
    choice.add_argument('--archive-native', action='store_true')
    args = parser.parse_args()
    prepare() if args.prepare else archive_native()
