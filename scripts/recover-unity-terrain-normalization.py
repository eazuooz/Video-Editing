"""Recover only the reviewed partial Terrain normalization; dry-run by default.

Restore two backed-up TerrainData bodies, return ten unchanged moved layer/meta
pairs, and preserve the single proved fresh duplicate outside Assets. All native
semantics and GUIDs remain strict. No original archive/canonical record changes.
"""
from __future__ import annotations
import argparse
import datetime as dt
import importlib.util
import json
import os
from pathlib import Path
import re


def module(name, file):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(file)); value = importlib.util.module_from_spec(spec); spec.loader.exec_module(value); return value


SAFE = module('terrain_recovery_safety', 'repair-unity-binary-references.py')
sha, read, literal, child = SAFE.sha, SAFE.read_bytes, SAFE.literal_path, SAFE.child
atomic, new, encoded = SAFE.atomic_write, SAFE.write_new, SAFE.json_bytes
EXPECTED_PROJECT = Path('D:/Github/VideoEditing/unity/VideoEditing')
ROOT = 'Assets/ThirdParty/YamyamAssetLibrary'
GENERATED = 'Assets/_TerrainAutoUpgrade'
SAVED_NAMES = {'New Terrain 1.asset', 'New Terrain 13.asset'}
GUID = re.compile(rb'(?m)^guid:[ \t]*([a-fA-F0-9]{32})[ \t]*\r?$')


def utc(): return dt.datetime.now(dt.timezone.utc).isoformat()


def json_input(path):
    raw = read(path); return json.loads(raw.decode('utf-8-sig')), raw


def file_proof(path, expected=None):
    raw = read(path); proof = {'bytes': len(raw), 'sha256': sha(raw)}
    if expected and any(proof[k] != expected[k] for k in ('bytes', 'sha256')):
        raise ValueError('Exact file bytes differ from reviewed evidence: ' + str(path))
    return proof


def guid(path):
    match = GUID.search(read(path))
    if not match: raise ValueError('Original metadata has no GUID: ' + str(path))
    return match.group(1).decode().lower()


def differences(a, b, path=''):
    if type(a) is not type(b): return [(path, a, b)]
    if isinstance(a, dict): return [d for key in sorted(set(a) | set(b)) for d in differences(a.get(key), b.get(key), path + '.' + key)]
    if isinstance(a, list):
        if len(a) != len(b): return [(path + '.length', len(a), len(b))]
        return [d for index, pair in enumerate(zip(a, b)) for d in differences(*pair, path + '[' + str(index) + ']')]
    return [] if a == b else [(path, a, b)]


def inventory(root, headless):
    result = []
    for directory, subdirs, files in os.walk(literal(root), followlinks=False):
        literal(directory)
        for name in subdirs: literal(Path(directory) / name)
        for name in files:
            path = literal(Path(directory) / name)
            result.append({'path': path.relative_to(headless).as_posix(), **file_proof(path)})
    return sorted(result, key=lambda r: r['path'])


def prepare(project, report_path=None):
    project = literal(project)
    if project != literal(EXPECTED_PROJECT): raise ValueError('Only the exact original primary project is accepted')
    work = child(project, 'Library/YamyamAssetLibrary'); headless = child(work, 'headless-project')
    manifest_path = child(work, 'staging-manifest.json'); manifest, manifest_raw = json_input(manifest_path)
    products = {p['id']: p for p in manifest['products']}
    if len(manifest['products']) != 84 or len(products) != 84 or any(p.get('status') != 'complete' for p in products.values()) or literal(manifest['stageRoot']) != child(headless, ROOT):
        raise ValueError('Current canonical84-product isolated root differs')
    report_path = literal(report_path or headless / 'Library/YamyamAssetLibrary/terrain-normalization-report.json')
    if not report_path.is_relative_to(headless / 'Library/YamyamAssetLibrary'): raise ValueError('Failure evidence is outside isolated Library')
    report, report_raw = json_input(report_path); failed_run = literal(report['runDirectory'])
    if (not failed_run.is_relative_to(headless / 'Library/YamyamAssetLibrary/terrain-normalization') or failed_run == headless / 'Library/YamyamAssetLibrary/terrain-normalization'
            or read(failed_run / 'report.json') != report_raw or report.get('status') != 'failed' or report.get('apply') is not True
            or report.get('scenesOpened') is not False or report.get('originalArchivesModified') is not False
            or report.get('observedUnityErrors') != 0 or report.get('manifestSha256') != sha(manifest_raw)
            or len(report.get('errors', [])) != 1 or not report['errors'][0].startswith('System.IO.InvalidDataException: Terrain semantic state changed after native persistence: ')):
        raise ValueError('Only the exact quiescent reviewed semantic-failure report can be recovered')
    saved = [t for t in report['terrains'] if t.get('saveStarted')]
    moved = [l for l in report['layers'] if l.get('moved')]
    if (len(report['terrains']) != 30 or len(report['layers']) != 25 or len(saved) != 2 or {Path(t['path']).name for t in saved} != SAVED_NAMES
            or any(t.get('productId') != '033' or not t.get('saved') for t in saved) or len(moved) != 10
            or any(l.get('moveStarted') and not l.get('moved') for l in report['layers'])):
        raise ValueError('Recovery is bounded to the exact30-terrain/25-layer/two-save/ten-move failure')
    records = {ROOT + '/' + r['path']: r for p in products.values() for r in p['files']}
    terrains, native_inventory = [], []
    changed_guids = []
    for t in report['terrains']:
        path = child(headless, t['path']); record = records.get(t['path'])
        if record is None or record['sha256'] != t['payloadBeforeSha256']: raise ValueError('Terrain failure snapshot differs from canonical source')
        current = file_proof(path); metadata = file_proof(str(path) + '.meta', records[t['path'] + '.meta'])
        if t not in saved:
            if current != {'bytes': record['bytes'], 'sha256': t['payloadBeforeSha256']}: raise ValueError('An unjournaled third TerrainData source changed')
        else:
            expected_backup = child(failed_run, 'backups/' + t['path'])
            if literal(t['backup']) != expected_backup or current['sha256'] != t['payloadAfterSha256']:
                raise ValueError('Current changed TerrainData or original backup path differs')
            original = file_proof(expected_backup, record); file_proof(str(expected_backup) + '.meta', metadata)
            if read(str(expected_backup) + '.meta') != read(str(path) + '.meta') or guid(str(path) + '.meta') != t['before']['asset']['guid']:
                raise ValueError('TerrainData original metadata GUID changed')
            delta = differences(t['before'], t['after'])
            if Path(t['path']).name == 'New Terrain 1.asset':
                if len(delta) != 1 or delta[0][0] != '.layers[0].asset.guid' or delta[0][1] == delta[0][2]:
                    raise ValueError('New Terrain1 changed more than the one freshly regenerated layer GUID')
                changed_guids.append({'path': t['path'], 'oldGuid': delta[0][1], 'newGuid': delta[0][2]})
            elif delta or t['beforeSemanticSha256'] != t['afterSemanticSha256']:
                raise ValueError('New Terrain13 no longer has exact successful semantics')
            terrains.append({'path': t['path'], 'backup': str(expected_backup), 'current': current, 'original': original, 'metadata': metadata})
        native_inventory.append({'path': t['path'], 'before': {'bytes': record['bytes'], 'sha256': t['payloadBeforeSha256']}, 'current': current, 'metadata': metadata})
    if len(changed_guids) != 1: raise ValueError('Exactly one fresh regenerated GUID difference is required')
    delta = changed_guids[0]; layer_plans, fresh = [], []
    expected_current_generated = set(); original_generated = []
    for layer in report['layers']:
        source = child(headless, layer['path'])
        if not layer['path'].startswith(GENERATED + '/') or Path(layer['path']).suffix != '.terrainlayer': raise ValueError('Layer source is outside generated subtree')
        original_expected = {'sha256': layer['payloadSha256'], 'bytes': None}
        if layer.get('moved'):
            folder = products[layer['assignedProductId']]['folder']
            wanted = ROOT + '/' + folder + '/Generated/TerrainLayers/' + Path(layer['path']).name
            if layer.get('orphan') or layer['destination'] != wanted: raise ValueError('Moved layer destination/owner differs')
            destination = child(headless, wanted); backup = child(failed_run, 'backups/' + layer['path'])
            body = file_proof(backup); meta = file_proof(str(backup) + '.meta')
            if body['sha256'] != layer['payloadSha256'] or meta['sha256'] != layer['metadataSha256']:
                raise ValueError('Original moved-layer backup differs from report')
            file_proof(destination, body); file_proof(str(destination) + '.meta', meta)
            if guid(str(destination) + '.meta') != layer['guid'] or guid(str(backup) + '.meta') != layer['guid']:
                raise ValueError('Moved original layer GUID changed')
            layer_plans.append({'source': layer['path'], 'destination': wanted, 'guid': layer['guid'], 'body': body, 'metadata': meta})
            if os.path.lexists(source) or os.path.lexists(str(source) + '.meta'):
                if layer['guid'] != delta['oldGuid'] or file_proof(source) != body or guid(str(source) + '.meta') != delta['newGuid']:
                    raise ValueError('Existing original layer slot is not the exact proven fresh duplicate')
                oldmeta, newmeta = read(str(backup) + '.meta'), read(str(source) + '.meta')
                if GUID.sub(lambda m: m.group(0).replace(m.group(1), delta['newGuid'].encode()), oldmeta) != newmeta:
                    raise ValueError('Fresh layer metadata changed more than its known GUID')
                fresh.append({'path': layer['path'], 'originalGuid': layer['guid'], 'freshGuid': delta['newGuid'], 'body': body, 'metadata': file_proof(str(source) + '.meta')})
                expected_current_generated.update({layer['path'], layer['path'] + '.meta'})
        else:
            if not layer.get('orphan'): raise ValueError('Unmoved non-orphan layer is unjournaled')
            body, meta = file_proof(source), file_proof(str(source) + '.meta')
            if body['sha256'] != layer['payloadSha256'] or meta['sha256'] != layer['metadataSha256'] or guid(str(source) + '.meta') != layer['guid']:
                raise ValueError('Unrelated existing generated layer changed')
            expected_current_generated.update({layer['path'], layer['path'] + '.meta'})
        original_generated.extend([{'path': layer['path'], **body}, {'path': layer['path'] + '.meta', **meta}])
    if len(fresh) != 1: raise ValueError('Exactly one fresh duplicate pair must be preserved')
    current_generated = inventory(child(headless, GENERATED), headless)
    if {r['path'] for r in current_generated} != expected_current_generated: raise ValueError('Unexpected files appeared in generated subtree')
    plan = {'schemaVersion': 1, 'kind': 'restore-partial-terrain-normalization', 'project': str(project), 'headless': str(headless),
            'sourceManifestSha256': sha(manifest_raw), 'failedReportPath': str(report_path), 'failedReportSha256': sha(report_raw), 'failedRun': str(failed_run),
            'terrains': sorted(terrains, key=lambda r: r['path']), 'layers': sorted(layer_plans, key=lambda r: r['source']), 'freshDuplicates': fresh,
            'nativeInventory': sorted(native_inventory, key=lambda r: r['path']), 'currentGeneratedInventory': current_generated, 'originalGeneratedInventory': sorted(original_generated, key=lambda r: r['path'])}
    return work, headless, manifest_path, manifest_raw, report_raw, plan


def recover(project, report_path=None, apply=False, editor_stopped=False, expected_manifest=None, expected_report=None, expected_plan=None):
    work, headless, manifest_path, manifest_raw, failed_raw, plan = prepare(project, report_path)
    plan_hash = sha(encoded(plan))
    if apply:
        if not editor_stopped or expected_manifest != sha(manifest_raw) or expected_report != sha(failed_raw) or expected_plan != plan_hash:
            raise ValueError('Apply requires stopped isolated Editor and three exact reviewed hashes')
        SAFE.editor_lock_guard(work)
    run = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'); run_root = child(work, 'terrain-normalization-recovery/' + run); run_root.mkdir(parents=True)
    report_path = run_root / 'report.json'; latest = child(work, 'terrain-normalization-recovery-latest.json')
    result = {'schemaVersion': 1, 'kind': plan['kind'], 'run': run, 'status': 'prepared' if apply else 'dry-run-ready', 'apply': apply,
              'plan': plan, 'planSha256': plan_hash, 'startedUtc': utc(), 'sourceArchivesModified': False, 'canonicalModified': False, 'actualMainAssetsModified': False}
    atomic(report_path, encoded(result)); atomic(latest, encoded({'status': result['status'], 'report': str(report_path), 'planSha256': plan_hash}))
    if not apply: return result, report_path
    new(run_root / 'manifest.json', manifest_raw); new(run_root / 'failed-report.json', failed_raw)
    sources = set()
    for terrain in plan['terrains']: sources.update({terrain['path'], terrain['path'] + '.meta'})
    for layer in plan['layers']: sources.update({layer['destination'], layer['destination'] + '.meta'})
    for duplicate in plan['freshDuplicates']: sources.update({duplicate['path'], duplicate['path'] + '.meta'})
    expected_inputs = {}
    for terrain in plan['terrains']:
        expected_inputs[terrain['path']] = terrain['current']
        expected_inputs[terrain['path'] + '.meta'] = terrain['metadata']
    for layer in plan['layers']:
        expected_inputs[layer['destination']] = layer['body']
        expected_inputs[layer['destination'] + '.meta'] = layer['metadata']
    for duplicate in plan['freshDuplicates']:
        expected_inputs[duplicate['path']] = duplicate['body']
        expected_inputs[duplicate['path'] + '.meta'] = duplicate['metadata']
    if set(expected_inputs) != sources:
        raise ValueError('Capture input set differs from the exact reviewed recovery plan')
    originals = {relative: read(child(headless, relative)) for relative in sorted(sources)}
    for relative, raw in originals.items():
        expected = expected_inputs[relative]
        if len(raw) != expected['bytes'] or sha(raw) != expected['sha256']:
            raise ValueError('Recovery source changed from reviewed plan before capture: ' + relative)
    for relative, raw in originals.items(): new(child(run_root, 'backups/' + relative), raw)
    if read(manifest_path) != manifest_raw or read(plan['failedReportPath']) != failed_raw:
        raise ValueError('Canonical/failure evidence changed during recovery preparation')
    SAFE.editor_lock_guard(work)
    moved, written = [], []
    try:
        for duplicate in plan['freshDuplicates']:
            for suffix in ('', '.meta'):
                source = child(headless, duplicate['path'] + suffix); destination = child(run_root, 'retired-fresh-duplicate/' + duplicate['path'] + suffix)
                destination.parent.mkdir(parents=True, exist_ok=True); literal(destination)
                if os.path.lexists(destination) or read(source) != originals[duplicate['path'] + suffix]: raise ValueError('Fresh duplicate changed before preserve move')
                os.rename(source, destination); moved.append((source, destination, originals[duplicate['path'] + suffix]))
        for layer in plan['layers']:
            for suffix in ('', '.meta'):
                source = child(headless, layer['destination'] + suffix); destination = child(headless, layer['source'] + suffix)
                if os.path.lexists(destination) or read(source) != originals[layer['destination'] + suffix]: raise ValueError('Moved layer changed before original-slot restore')
                destination.parent.mkdir(parents=True, exist_ok=True); literal(destination); os.rename(source, destination)
                moved.append((source, destination, originals[layer['destination'] + suffix]))
        for terrain in plan['terrains']:
            source = child(headless, terrain['path']); current = originals[terrain['path']]; original = read(terrain['backup'])
            if read(source) != current or sha(original) != terrain['original']['sha256'] or len(original) != terrain['original']['bytes']: raise ValueError('Terrain restore inputs changed')
            atomic(source, original); written.append((source, current, original))
        if read(manifest_path) != manifest_raw or read(plan['failedReportPath']) != failed_raw: raise ValueError('Canonical/failure evidence changed during recovery')
        for row in plan['nativeInventory']:
            file_proof(child(headless, row['path']), row['before']); file_proof(child(headless, row['path'] + '.meta'), row['metadata'])
        if inventory(child(headless, GENERATED), headless) != plan['originalGeneratedInventory']: raise ValueError('Recovered generated tree differs from exact original25layer inventory')
        for layer in plan['layers']:
            if os.path.lexists(child(headless, layer['destination'])) or os.path.lexists(child(headless, layer['destination'] + '.meta')):
                raise ValueError('Restored layer still exists at moved destination')
        result.update(status='complete', completedUtc=utc(), restoredTerrainData=2, restoredLayerPairs=10, preservedFreshDuplicatePairs=1)
        atomic(report_path, encoded(result)); atomic(latest, encoded({'status': 'complete', 'report': str(report_path), 'planSha256': plan_hash}))
    except BaseException as error:
        failures = []
        for path, before, after in reversed(written):
            try:
                if read(path) != after: raise ValueError('Preserve later foreign native-source write')
                atomic(path, before)
            except BaseException as failure: failures.append({'path': str(path), 'error': str(failure)})
        for source, destination, raw in reversed(moved):
            try:
                if os.path.lexists(source) or read(destination) != raw: raise ValueError('Preserve later foreign move/source bytes')
                os.rename(literal(destination), literal(source))
            except BaseException as failure: failures.append({'path': str(source), 'error': str(failure)})
        result.update(status='failed', completedUtc=utc(), error=str(error), rollbackErrors=failures)
        atomic(report_path, encoded(result)); atomic(latest, encoded({'status': 'failed', 'report': str(report_path), 'planSha256': plan_hash})); raise
    return result, report_path


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--project', type=Path, default=EXPECTED_PROJECT)
    parser.add_argument('--failed-report', type=Path); parser.add_argument('--apply', action='store_true'); parser.add_argument('--editor-stopped', action='store_true')
    parser.add_argument('--expected-manifest-sha256'); parser.add_argument('--expected-failed-report-sha256'); parser.add_argument('--expected-recovery-plan-sha256')
    args = parser.parse_args(); result, path = recover(args.project, args.failed_report, args.apply, args.editor_stopped, args.expected_manifest_sha256, args.expected_failed_report_sha256, args.expected_recovery_plan_sha256)
    print(json.dumps({'status': result['status'], 'report': str(path), 'planSha256': result['planSha256'], 'sourceManifestSha256': result['plan']['sourceManifestSha256'], 'failedReportSha256': result['plan']['failedReportSha256'], 'terrains': len(result['plan']['terrains']), 'layers': len(result['plan']['layers']), 'freshDuplicates': len(result['plan']['freshDuplicates'])}))


if __name__ == '__main__': main()
