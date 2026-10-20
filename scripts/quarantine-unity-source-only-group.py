"""Preserve an exactly proved incomplete provider demo group outside Assets.

This separate route covers the twelve newly diagnosed TerrainData and only their
incoming serialized scene/prefab consumers. It never changes layer/tree payloads,
usable outgoing models/materials, or the immutable historical binary proof scope.
Preparing a plan and quarantining are both dry-run operations unless --apply is
explicit. A fresh full-root Unity dependency proof is mandatory for any move.
"""
from __future__ import annotations
import argparse
import collections
import copy
import datetime as dt
import importlib.util
import json
import os
from pathlib import Path
import re
import tempfile


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(filename))
    value = importlib.util.module_from_spec(spec); spec.loader.exec_module(value); return value


BASE = module('yamyam_group_source_safety', 'quarantine-unity-source-only-terrain.py')
SAFE, ROOT = BASE.SAFE, BASE.ROOT
sha, read_bytes, literal, child = SAFE.sha, SAFE.read_bytes, SAFE.literal_path, SAFE.child
atomic_write, write_new, encoded = SAFE.atomic_write, SAFE.write_new, SAFE.json_bytes
json_input, ordinal_key = BASE.json_input, BASE.ordinal_key
KIND = 'incomplete-provider-demo-group'
PRODUCTS = {'004', '033', '084'}
TERRAIN_COUNT = 12
MISSING_COUNT = 31
SHA = re.compile(r'^[a-f0-9]{64}$')


def utc(): return dt.datetime.now(dt.timezone.utc).isoformat()


def context(project):
    project = literal(project); work = child(project, 'Library/YamyamAssetLibrary')
    headless = child(work, 'headless-project'); stage = child(headless, ROOT)
    manifest_path = child(work, 'staging-manifest.json'); manifest, raw = json_input(manifest_path)
    products = {p['id']: p for p in manifest['products']}
    if (literal(manifest['stageRoot']) != stage or manifest.get('targetAssetRoot', ROOT) != ROOT
            or len(manifest['products']) != 84 or len(products) != 84 or any(p.get('status') != 'complete' or not p.get('files') for p in products.values())):
        raise ValueError('Only the complete84-product isolated library is eligible')
    records = {r['path']: (p, r) for p in products.values() for r in p['files']}
    if len(records) != sum(len(p['files']) for p in products.values()):
        raise ValueError('Duplicate canonical record paths')
    return project, work, headless, stage, manifest_path, manifest, raw, products, records


def owned_input(work, path):
    path = literal(path)
    if not path.is_relative_to(work): raise ValueError('Input evidence must be under this owned Library')
    return path, *json_input(path)


def original_evidence(work, products, diagnosis, source_index):
    missing_by_product = collections.defaultdict(set)
    targets = []
    for row in diagnosis['terrains']:
        missing = {p['guid'] for slots in row['layers'].values() for p in slots if p.get('status') == 'external-guid-not-in-current-library'}
        missing |= {p['prefab']['guid'] for p in row['treePrototypes'] if p['prefab']['status'] == 'external-guid-not-in-current-library'}
        if missing:
            if not row['path'].startswith(ROOT + '/') or row['productId'] not in PRODUCTS:
                raise ValueError('Unexpected diagnosed TerrainData scope')
            targets.append({'path': row['path'][len(ROOT) + 1:], 'productId': row['productId'], 'missingGuids': sorted(missing)})
            missing_by_product[row['productId']].update(missing)
    if (diagnosis.get('errors') != [] or len(targets) != TERRAIN_COUNT or len({t['path'] for t in targets}) != TERRAIN_COUNT
            or set(missing_by_product) != PRODUCTS or len(set().union(*missing_by_product.values())) != MISSING_COUNT):
        raise ValueError('Exact twelve-terrain/31-omitted-GUID diagnosis is required')
    if source_index.get('sourceArchivesModified') is not False:
        raise ValueError('Original package inspection must be read-only')
    index_rows = {r['productId']: r for r in source_index['products']}
    if set(index_rows) != PRODUCTS: raise ValueError('All three original package indexes are required')
    index_proofs = []
    for product_id in sorted(PRODUCTS):
        row = index_rows[product_id]
        if set(row['queriedMissingGuids']) != missing_by_product[product_id] or row.get('exactMatches') != []:
            raise ValueError('Original package missing-GUID query coverage differs')
        path, index, raw = owned_input(work, row['index'])
        archive = literal(index['archive'])
        inputs = [i for i in products[product_id]['inputs'] if literal(i['path']) == archive]
        if (len(inputs) != 1 or inputs[0]['bytes'] != index['archiveBytes'] or not archive.is_file()
                or archive.stat().st_size != index['archiveBytes'] or archive.stat().st_mtime_ns != index['archiveMtimeNs']):
            raise ValueError('Indexed original archive identity/size/stamp is stale')
        guid_entries = [entry for entry in index.get('entries', []) if re.fullmatch('[a-f0-9]{32}', entry.get('folderGuid', ''))]
        extra_entries = [entry for entry in index.get('entries', []) if entry not in guid_entries]
        if (len(index.get('entries', [])) != index.get('guidFolders') or index.get('metadataFiles', 0) < 1
                or index.get('pathnames', 0) != len(guid_entries) or index.get('metadataFiles') != len(guid_entries)
                or any(entry != {'folderGuid': 'packagemanagermanifest', 'originalPath': None, 'metadata': None} for entry in extra_entries)
                or index.get('availableUnitypackageMembers') != row.get('availableUnitypackageMembers')
                or len(index.get('availableUnitypackageMembers', [])) != 1):
            raise ValueError('Source package index is incomplete or has an uninspected package variant')
        actual_guids = {str(v).lower() for entry in index['entries'] for v in (entry.get('folderGuid'), (entry.get('metadata') or {}).get('guid')) if v}
        if actual_guids & missing_by_product[product_id]:
            raise ValueError('An original missing-GUID recovery candidate is available')
        index_proofs.append({'productId': product_id, 'path': str(path), 'sha256': sha(raw),
                             'archive': str(archive), 'archiveBytes': index['archiveBytes'], 'archiveMtimeNs': index['archiveMtimeNs'],
                             'selectedMember': index.get('selectedMember'), 'missingGuids': sorted(missing_by_product[product_id])})
    return {'schemaVersion': 1, 'kind': KIND, 'sourceArchivesModified': False, 'incompleteTerrainTargets': targets,
            'missingGuids': sorted(set().union(*missing_by_product.values())), 'sourcePackageIndexes': index_proofs}


def verify_evidence(work, products, evidence):
    if (evidence.get('schemaVersion') != 1 or evidence.get('kind') != KIND or evidence.get('sourceArchivesModified') is not False
            or len(evidence.get('incompleteTerrainTargets', [])) != TERRAIN_COUNT or len(set(evidence.get('missingGuids', []))) != MISSING_COUNT):
        raise ValueError('Missing-provider evidence has an unexpected scope')
    targets = {t['path']: t for t in evidence['incompleteTerrainTargets']}
    if len(targets) != TERRAIN_COUNT or {t['productId'] for t in targets.values()} != PRODUCTS:
        raise ValueError('Missing-provider terrain identities differ')
    union = set().union(*(set(t['missingGuids']) for t in targets.values()))
    if union != set(evidence['missingGuids']): raise ValueError('Missing-provider GUID sets disagree')
    for item in evidence['sourcePackageIndexes']:
        path, index, raw = owned_input(work, item['path'])
        if sha(raw) != item['sha256']: raise ValueError('Original source package index SHA changed')
        archive = literal(item['archive'])
        if (literal(index['archive']) != archive or archive.stat().st_size != item['archiveBytes']
                or archive.stat().st_mtime_ns != item['archiveMtimeNs']
                or index['archiveBytes'] != item['archiveBytes'] or index['archiveMtimeNs'] != item['archiveMtimeNs']):
            raise ValueError('Original archive/index binding is stale')
        if not any(literal(i['path']) == archive and i['bytes'] == item['archiveBytes'] for i in products[item['productId']]['inputs']):
            raise ValueError('Source package no longer belongs to canonical product')
        query = set().union(*(set(t['missingGuids']) for t in targets.values() if t['productId'] == item['productId']))
        if query != set(item['missingGuids']): raise ValueError('Indexed omitted GUID set differs')
        candidates = {str(v).lower() for entry in index['entries'] for v in (entry.get('folderGuid'), (entry.get('metadata') or {}).get('guid')) if v}
        if query & candidates: raise ValueError('An exact original source recovery candidate exists')
    if len(evidence['sourcePackageIndexes']) != 3 or {i['productId'] for i in evidence['sourcePackageIndexes']} != PRODUCTS:
        raise ValueError('Missing original source package coverage')
    return targets


def prepare(project, graph_path=None, diagnosis_path=None, source_index_path=None):
    _, work, _, stage, _, manifest, manifest_raw, products, records = context(project)
    graph_path, graph, graph_raw = owned_input(work, graph_path or work / 'incomplete-terrain-incoming-consumers.json')
    diagnosis_path, diagnosis, diagnosis_raw = owned_input(work, diagnosis_path or work / 'terrain-source-reference-diagnosis.json')
    source_index_path, source_index, source_index_raw = owned_input(work, source_index_path or work / 'terrain-missing-reference-source-index-proof.json')
    if graph.get('diagnosisSha256') != sha(diagnosis_raw) or graph.get('filesChangedWhileRead'):
        raise ValueError('Incoming graph diagnosis binding or source stability failed')
    # Previously proven initial033 source-only removals can occur during this
    # read-only scan. No other unknown/missing/parse error can be waived.
    preserved = {ROOT + '/' + r['path'] for p in products.values() for r in p.get('sourceOnlyFiles', [])}
    if any(error.get('path') not in preserved for error in graph.get('errors', [])):
        raise ValueError('Incoming graph has unresolved serialized parse/read errors')
    evidence = original_evidence(work, products, diagnosis, source_index)
    expected_terrains = {t['path'] for t in evidence['incompleteTerrainTargets']}
    graph_terrains = {t['relativePath'] for t in graph['incompleteTerrainTargets']}
    if graph_terrains != expected_terrains: raise ValueError('Incoming graph excludes a different TerrainData set')
    closure = {a['path'][len(ROOT) + 1:]: a for a in graph['incomingClosureAssets']}
    if not expected_terrains <= set(closure): raise ValueError('Incoming graph omitted a target')
    # Prove the declared closure derives only by following incoming edges.
    reachable = set(expected_terrains)
    edges = [(e['consumer'][len(ROOT) + 1:], e['target'][len(ROOT) + 1:]) for e in graph['incomingEdges']]
    while True:
        following = reachable | {consumer for consumer, target in edges if target in reachable}
        if following == reachable: break
        reachable = following
    if reachable != set(closure): raise ValueError('Incoming graph includes unrelated assets')
    rows = []
    for relative in sorted(closure, key=ordinal_key):
        product, record = records[relative]; meta = records[relative + '.meta'][1]
        role = 'incomplete-terrain' if relative in expected_terrains else 'incoming-demo-consumer'
        if role == 'incoming-demo-consumer' and Path(relative).suffix.lower() not in {'.unity', '.prefab'}:
            raise ValueError('Additional non-scene/prefab consumer needs explicit separate scope: ' + relative)
        if record['sha256'] != closure[relative]['actualSha256'] or record['bytes'] != closure[relative]['actualBytes']:
            raise ValueError('Incoming group payload changed since offline graph; rerun graph')
        for candidate, rec in ((relative, record), (relative + '.meta', meta)):
            raw = read_bytes(child(stage, candidate))
            if sha(raw) != rec['sha256'] or len(raw) != rec['bytes']:
                raise ValueError('Current candidate differs from canonical bytes; recorder adoption required')
        rows.append({'productId': product['id'], 'path': relative, 'bytes': record['bytes'], 'sha256': record['sha256'],
                     'metadataPath': relative + '.meta', 'metadataBytes': meta['bytes'], 'metadataSha256': meta['sha256'],
                     'guid': meta['guid'], 'role': role, 'reason': 'provider-omitted-original-layer-or-tree-source' if role == 'incomplete-terrain' else 'serialized-incoming-consumer-of-incomplete-provider-terrain'})
    stamp = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    run = child(work, 'source-only-group-plans/' + stamp); run.mkdir(parents=True)
    evidence.update(diagnosis={'path': str(diagnosis_path), 'sha256': sha(diagnosis_raw)}, sourceIndex={'path': str(source_index_path), 'sha256': sha(source_index_raw)})
    evidence_path = run / 'missing-evidence.json'; evidence_raw = encoded(evidence); write_new(evidence_path, evidence_raw)
    plan = {'schemaVersion': 1, 'kind': KIND, 'createdUtc': utc(), 'sourceManifestSha256': sha(manifest_raw),
            'missingEvidence': {'path': str(evidence_path), 'sha256': sha(evidence_raw)},
            'sourceIncomingGraph': {'path': str(graph_path), 'sha256': sha(graph_raw)}, 'targets': rows}
    plan_path = run / 'group-plan.json'; write_new(plan_path, encoded(plan))
    atomic_write(work / 'incomplete-provider-demo-group-plan.json', encoded(plan))
    return plan, plan_path


def verify_current_pointer_guids(work, raw, expected):
    if raw.startswith(b'%YAML'):
        guids = {m.group(1).decode().lower() for m in re.finditer(rb'\bguid:[ \t]*([a-fA-F0-9]{32})', raw)}
    else:
        with tempfile.TemporaryDirectory(prefix='group-external-proof-', dir=literal(work)) as directory:
            guids = {r['canonicalGuid'] for r in SAFE.parse_data(raw, child(Path(directory), 'native.bin'))['externals']}
    if not set(expected) <= guids: raise ValueError('Current TerrainData lost the exact omitted original references')


def _verify_runtime(report, runtime_raw, headless, manifest_path, manifest, manifest_raw, plan_path, plan_raw, plan, receipts, inputs):
    if (report.get('schemaVersion') != 1 or report.get('kind') != KIND or report.get('status') != 'dependency-proof-complete'
            or report.get('apply') is not False or report.get('errors') != [] or report.get('blockers') != []
            or report.get('observedUnityErrors') != 0 or report.get('originalArchivesModified') is not False
            or report.get('scenesOpened') is not False or report.get('terrainDataLoaded') is not False
            or report.get('assetsSaved') is not False or not report.get('completedUtc')
            or literal(report.get('project', '')) != headless or literal(report.get('manifestPath', '')) != manifest_path
            or report.get('manifestSha256') != sha(manifest_raw) or literal(report.get('groupPlanPath', '')) != plan_path
            or report.get('groupPlanSha256') != sha(plan_raw) or report.get('sourceMissingEvidenceSha256') != plan['missingEvidence']['sha256']
            or report.get('sourceIncomingGraphSha256') != plan['sourceIncomingGraph']['sha256']):
        raise ValueError('Fresh clean current-manifest/group/evidence-bound runtime proof is required')
    receipt_bindings = {r['productId']: r['sha256'] for r in report.get('receiptSha256ByProduct', [])}
    if receipt_bindings != {product_id: sha(raw) for product_id, (_, raw) in receipts.items()}:
        raise ValueError('Runtime current product receipt bindings differ')
    proof = report.get('dependencyProof', {})
    paths = {r['path'] for r in plan['targets']}
    roots = sorted((ROOT + '/' + r['path'] for p in manifest['products'] for r in p['files'] if not r['path'].endswith('.meta') and r['path'] not in paths), key=ordinal_key)
    if (proof.get('proofVersion') != 1 or proof.get('status') != 'unreferenced-by-other-root-assets'
            or not proof.get('startedUtc') or not proof.get('completedUtc')
            or not str(proof.get('method', '')).startswith('AssetDatabase.GetDependencies(') or 'recursive:true' not in proof.get('method', '')
            or proof.get('rootAssetsChecked') != len(roots) or proof.get('rootPathsSha256') != sha('\n'.join(roots).encode())
            or type(proof.get('dependencyClosurePaths')) is not int or proof['dependencyClosurePaths'] < len(roots)
            or not SHA.fullmatch(str(proof.get('closurePathsSha256', '')))):
        raise ValueError('Runtime proof must cover every current outside-group library root')
    targets = proof.get('excludedTargets', [])
    if len(targets) != len(paths) or {r.get('relativePath') for r in targets} != paths:
        raise ValueError('Runtime excluded a different exact asset group')
    expected = {r['path']: r for r in plan['targets']}
    for row in targets:
        t = expected[row['relativePath']]; body, meta = inputs[t['path']], inputs[t['metadataPath']]
        if (row.get('path') != ROOT + '/' + t['path'] or row.get('metadataPath') != ROOT + '/' + t['metadataPath']
                or any(row.get(k) != t[k] for k in ('productId', 'guid', 'role', 'reason'))
                or row.get('bytes') != body['bytes'] or row.get('canonicalSha256') != body['sha256']
                or row.get('actualSha256') != body['sha256'] or row.get('sourceArtifactSha256') != body['sha256']
                or row.get('metadataBytes') != meta['bytes'] or row.get('metadataSha256') != meta['sha256']
                or row.get('canonicalMetadataSha256') != meta['sha256']
                or row.get('referencedByOtherRootAssets') is not False or row.get('checkedInboundReferences') != 0):
            raise ValueError('Runtime target payload/meta/GUID/role/inbound proof differs')


def verify_runtime(report, plan, plan_bytes, original_manifest, original_bytes, receipt_bytes_by_product, headless, expected_files):
    """Replay interface for the final installer; performs no writes or Unity IO."""
    headless = literal(headless)
    receipts = {product_id: (headless.parent / 'receipts' / (product_id + '.json'), raw)
                for product_id, raw in receipt_bytes_by_product.items()}
    _verify_runtime(report, b'', headless, headless.parent / 'staging-manifest.json', original_manifest,
                    original_bytes, literal(report['groupPlanPath']), plan_bytes, plan, receipts, expected_files)


def verify_missing_evidence(missing, plan, original_manifest):
    """Replay original-package proof for the exact immutable approved group."""
    work = literal(original_manifest['stageRoot']).parents[3]
    targets = verify_evidence(work, {p['id']: p for p in original_manifest['products']}, missing)
    if {t['path'] for t in plan['targets'] if t['role'] == 'incomplete-terrain'} != set(targets):
        raise ValueError('Original omitted GUID evidence targets differ from approved group')
    return targets


def quarantine(project, plan_path, runtime_path, apply=False, editor_stopped=False, expected_manifest=None, expected_plan=None, expected_runtime=None):
    _, work, headless, stage, manifest_path, manifest, manifest_raw, products, records = context(project)
    plan_path, plan, plan_raw = owned_input(work, plan_path)
    runtime_path, runtime, runtime_raw = owned_input(work, runtime_path)
    if not runtime_path.is_relative_to(headless / 'Library/YamyamAssetLibrary'): raise ValueError('Runtime proof must belong to isolated project')
    if plan.get('schemaVersion') != 1 or plan.get('kind') != KIND or plan.get('sourceManifestSha256') != sha(manifest_raw):
        raise ValueError('Exact group plan belongs to a stale/different canonical manifest')
    evidence_path, evidence, evidence_raw = owned_input(work, plan['missingEvidence']['path'])
    graph_path, graph, graph_raw = owned_input(work, plan['sourceIncomingGraph']['path'])
    if sha(evidence_raw) != plan['missingEvidence']['sha256'] or sha(graph_raw) != plan['sourceIncomingGraph']['sha256']:
        raise ValueError('Group original evidence/incoming graph SHA changed')
    terrain_targets = verify_evidence(work, products, evidence)
    planned = {t['path']: t for t in plan['targets']}
    if len(planned) != len(plan['targets']) or {p for p, t in planned.items() if t.get('role') == 'incomplete-terrain'} != set(terrain_targets):
        raise ValueError('Plan omitted/added an incomplete TerrainData target')
    if set(planned) != {r['path'][len(ROOT) + 1:] for r in graph['incomingClosureAssets']}:
        raise ValueError('Plan differs from exact incoming serialized closure')
    originals, inputs, affected = {}, {}, set()
    owners = collections.defaultdict(list)
    missing = set(evidence['missingGuids'])
    for product in products.values():
        for record in product['files']:
            if not record['path'].endswith('.meta'): continue
            if any(str(v).lower() in missing for v in (record.get('guid'), record.get('originalGuid'), record.get('source', {}).get('originalGuid')) if v):
                raise ValueError('Current canonical metadata supplies an omitted GUID recovery candidate')
            if record.get('guid'): owners[record['guid']].append(record['path'])
    for relative, target in planned.items():
        if target['metadataPath'] != relative + '.meta' or relative not in records or relative + '.meta' not in records:
            raise ValueError('Planned exact asset/meta is absent or differs')
        product, body = records[relative]; meta = records[relative + '.meta'][1]
        if target['productId'] != product['id'] or owners.get(target['guid']) != [relative + '.meta']:
            raise ValueError('Planned product/GUID does not have exactly one canonical owner')
        if target['role'] == 'incoming-demo-consumer':
            if Path(relative).suffix.lower() not in {'.unity', '.prefab'}: raise ValueError('Usable non-demo outgoing asset cannot enter group')
        elif target['role'] != 'incomplete-terrain': raise ValueError('Unknown group target role')
        for candidate, record, expected_sha, expected_bytes in ((relative, body, target['sha256'], target['bytes']), (relative + '.meta', meta, target['metadataSha256'], target['metadataBytes'])):
            raw = read_bytes(child(stage, candidate))
            if sha(raw) != record['sha256'] or len(raw) != record['bytes'] or record['sha256'] != expected_sha or record['bytes'] != expected_bytes:
                raise ValueError('Current exact group source differs from canonical/plan SHA or bytes')
            originals[candidate] = raw; inputs[candidate] = {'sha256': sha(raw), 'bytes': len(raw)}
        guid = re.search(rb'(?m)^guid:[ \t]*([a-f0-9]{32})\s*$', originals[relative + '.meta'])
        if not guid or guid.group(1).decode() != target['guid'] or meta.get('guid') != target['guid']:
            raise ValueError('Current original metadata GUID changed')
        if target['role'] == 'incomplete-terrain': verify_current_pointer_guids(work, originals[relative], terrain_targets[relative]['missingGuids'])
        affected.add(product['id'])
    receipts = {}
    for product_id in sorted(affected):
        receipt_path = child(work, 'receipts/' + product_id + '.json'); receipt, raw = json_input(receipt_path)
        if receipt != products[product_id]: raise ValueError('Canonical product receipt differs')
        receipts[product_id] = (receipt_path, raw)
    _verify_runtime(runtime, runtime_raw, headless, manifest_path, manifest, manifest_raw, plan_path, plan_raw, plan, receipts, inputs)
    if apply:
        if (not editor_stopped or expected_manifest != sha(manifest_raw) or expected_plan != sha(plan_raw) or expected_runtime != sha(runtime_raw)):
            raise ValueError('Apply needs stopped Editor and three exact reviewed input hashes')
        SAFE.editor_lock_guard(work)
    run = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    run_root = child(work, 'source-only-group-quarantine/' + run); run_root.mkdir(parents=True)
    report_path = run_root / 'report.json'; latest = child(work, 'source-only-group-quarantine-latest.json')
    destinations = {p: child(work, 'SourceOnly/' + p) for p in originals}
    if any(os.path.lexists(p) for p in destinations.values()): raise ValueError('SourceOnly destination already exists; overwrite forbidden')
    report = {'schemaVersion': 2, 'kind': KIND, 'run': run, 'status': 'prepared' if apply else 'dry-run-ready', 'apply': apply,
              'sourceManifestSha256': sha(manifest_raw), 'sourceRuntimeProofSha256': sha(runtime_raw),
              'sourceMissingEvidenceSha256': sha(evidence_raw), 'sourceIncomingGraphSha256': sha(graph_raw), 'sourceGroupPlanSha256': sha(plan_raw),
              'runtimeProof': str(runtime_path), 'missingEvidence': str(evidence_path), 'incomingGraph': str(graph_path), 'groupPlan': str(plan_path),
              'sourceArchivesModified': False, 'actualMainAssetsModified': False, 'terrainPayloadsChanged': False,
              'terrainAssets': TERRAIN_COUNT, 'groupAssets': len(planned), 'consumerAssets': len(planned) - TERRAIN_COUNT,
              'historicalBinaryProofFieldsPreserved': True, 'files': [
                  {'path': relative, 'productId': records[relative][0]['id'], **proof, 'destination': str(destinations[relative]),
                   'backupPath': str(child(run_root, 'backups/' + relative)), 'originalRecord': records[relative][1]} for relative, proof in inputs.items()]}
    atomic_write(report_path, encoded(report)); atomic_write(latest, encoded({'report': str(report_path), 'status': report['status'], 'files': len(originals), 'groupAssets': len(planned)}))
    if not apply: return report, report_path
    updated = copy.deepcopy(manifest); outputs = []
    for product in updated['products']:
        if product['id'] not in affected: continue
        prior = products[product['id']]
        product['files'] = [r for r in product['files'] if r['path'] not in originals]
        rows = [r for r in report['files'] if r['productId'] == product['id']]
        for row in rows:
            preserved = copy.deepcopy(row['originalRecord'])
            preserved.update(preservedPath=row['destination'], sourceOnlyRun=run, sourceOnlyReason='incomplete-provider-terrain-demo-group',
                             runtimeProofSha256=sha(runtime_raw), missingEvidenceSha256=sha(evidence_raw), groupPlanSha256=sha(plan_raw))
            product.setdefault('sourceOnlyFiles', []).append(preserved)
        product.setdefault('sourceOnlyHistory', []).append({'kind': KIND, 'run': run, 'report': str(report_path), 'files': len(rows), 'groupAssets': len(rows) // 2})
        if 'finalImportFileCount' in product: product['finalImportFileCount'] = len(product['files'])
        for field in ('originalBinaryGuidCollisionBlockers', 'binaryGuidRecoveryProofs'):
            if product.get(field) != prior.get(field): raise ValueError('Immutable historical896 proof scope changed')
        receipt_path, before = receipts[product['id']]; outputs.append((receipt_path, before, encoded(product)))
    updated.setdefault('sourceOnlyHistory', []).append({'kind': KIND, 'run': run, 'report': str(report_path), 'productIds': sorted(affected), 'files': len(originals), 'groupAssets': len(planned)})
    updated['updatedAt'] = utc(); updated.setdefault('summary', {}).update(files=sum(len(p['files']) for p in updated['products']), bytes=sum(r['bytes'] for p in updated['products'] for r in p['files']), sourceOnlyFiles=sum(len(p.get('sourceOnlyFiles', [])) for p in updated['products']))
    outputs.append((manifest_path, manifest_raw, encoded(updated)))
    for relative, raw in originals.items(): write_new(child(run_root, 'backups/' + relative), raw)
    for name, raw in [('manifest.json', manifest_raw), ('runtime-proof.json', runtime_raw), ('missing-evidence.json', evidence_raw), ('incoming-graph.json', graph_raw), ('group-plan.json', plan_raw)] + [('receipt' + product_id + '.json', value[1]) for product_id, value in receipts.items()]:
        write_new(run_root / name, raw)
    write_new(run_root / 'plan.json', plan_raw)
    for product_id, (_, raw) in receipts.items(): write_new(child(run_root, 'receipts/' + product_id + '.json'), raw)
    SAFE.editor_lock_guard(work)
    for path, expected in [(manifest_path, manifest_raw), (plan_path, plan_raw), (runtime_path, runtime_raw), (evidence_path, evidence_raw), (graph_path, graph_raw)] + list(receipts.values()):
        if read_bytes(path) != expected: raise ValueError('Canonical/evidence changed during preparation')
    for relative, raw in originals.items():
        if read_bytes(child(stage, relative)) != raw: raise ValueError('Owned group source changed during preparation')
    moved, written = [], []
    try:
        for relative, destination in destinations.items():
            source = child(stage, relative); destination.parent.mkdir(parents=True, exist_ok=True); literal(destination)
            if os.path.lexists(destination) or read_bytes(source) != originals[relative]: raise ValueError('Source/destination changed before owned move')
            os.rename(source, destination); moved.append((source, destination, inputs[relative]))
            if read_bytes(destination) != originals[relative] or source.exists(): raise ValueError('Exact moved bytes not preserved')
        for path, before, after in outputs:
            if read_bytes(path) != before: raise ValueError('Canonical bookkeeping changed before write')
            atomic_write(path, after); written.append((path, before, after))
        report.update(status='complete', completedUtc=utc(), updatedManifestSha256=sha(outputs[-1][2]))
        atomic_write(report_path, encoded(report)); atomic_write(latest, encoded({'report': str(report_path), 'status': 'complete', 'files': len(originals), 'groupAssets': len(planned)}))
    except BaseException as error:
        failures = []
        for path, original, committed in reversed(written):
            try:
                if read_bytes(path) != committed: raise ValueError('Preserve later foreign canonical write')
                atomic_write(path, original)
            except BaseException as failure: failures.append({'path': str(path), 'error': str(failure)})
        for source, destination, expected in reversed(moved):
            try:
                if os.path.lexists(source) or not destination.exists(): raise ValueError('Rollback destination/source conflict')
                raw = read_bytes(destination)
                if sha(raw) != expected['sha256'] or len(raw) != expected['bytes']: raise ValueError('Preserve foreign-modified SourceOnly bytes; original backup remains')
                os.rename(literal(destination), literal(source))
            except BaseException as failure: failures.append({'path': str(source), 'error': str(failure)})
        report.update(status='failed', error=str(error), rollbackErrors=failures)
        atomic_write(report_path, encoded(report)); atomic_write(latest, encoded({'report': str(report_path), 'status': 'failed', 'files': len(originals)})); raise
    return report, report_path


def main():
    parser = argparse.ArgumentParser(description=__doc__); commands = parser.add_subparsers(dest='command', required=True)
    prep = commands.add_parser('prepare'); prep.add_argument('--project', required=True, type=Path)
    prep.add_argument('--incoming-graph', type=Path); prep.add_argument('--diagnosis', type=Path); prep.add_argument('--source-index-proof', type=Path)
    run = commands.add_parser('quarantine'); run.add_argument('--project', required=True, type=Path); run.add_argument('--group-plan', required=True, type=Path); run.add_argument('--runtime-proof', required=True, type=Path)
    run.add_argument('--apply', action='store_true'); run.add_argument('--editor-stopped', action='store_true')
    run.add_argument('--expected-manifest-sha256'); run.add_argument('--expected-group-plan-sha256'); run.add_argument('--expected-runtime-proof-sha256')
    args = parser.parse_args()
    if args.command == 'prepare':
        plan, path = prepare(args.project, args.incoming_graph, args.diagnosis, args.source_index_proof)
        print(json.dumps({'status': 'plan-prepared', 'plan': str(path), 'sha256': sha(encoded(plan)), 'assets': len(plan['targets'])})); return
    report, path = quarantine(args.project, args.group_plan, args.runtime_proof, args.apply, args.editor_stopped, args.expected_manifest_sha256, args.expected_group_plan_sha256, args.expected_runtime_proof_sha256)
    print(json.dumps({'status': report['status'], 'report': str(path), 'files': len(report['files']), 'assets': report['groupAssets']}))


if __name__ == '__main__': main()
