"""Preserve only an exactly diagnosed optional-demo incoming group outside Assets.

This third, separate history route retains existing SourceOnly transactions and
all usable outgoing models/materials/runtime code. It requires byte-bound missing
script evidence and a clean full-root Unity dependency proof. Default is dry run.
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


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(filename))
    value = importlib.util.module_from_spec(spec); spec.loader.exec_module(value); return value


GROUP = module('yamyam_optional_group_safety', 'quarantine-unity-source-only-group.py')
BASE, SAFE, ROOT = GROUP.BASE, GROUP.SAFE, GROUP.ROOT
sha, read_bytes, literal, child = GROUP.sha, GROUP.read_bytes, GROUP.literal, GROUP.child
atomic_write, write_new, encoded = GROUP.atomic_write, GROUP.write_new, GROUP.encoded
json_input, ordinal_key, context, owned_input = GROUP.json_input, GROUP.ordinal_key, GROUP.context, GROUP.owned_input
KIND = 'incomplete-optional-demo-script-group'
SEED_COUNT = 49
SHA = GROUP.SHA
RECOVERED = {'f70555f144d8491a825f0804e09c671c', '55d150653329a5f49bbc49441497dcda',
             'd618a5e072a94b648a5feceeec506f5d', 'bc7d77ecb696b7c46a3ff95a62c26a44',
             '68bb026fafb42b14791938953eaace77', '72ece51f2901e7445ab60da3685d6b5f',
             'f9dfa5b682dcd46bda6128250e975f58', 'f4044717213e31446939f7bd49c896ea',
             '99a9c787e5d1bbf48a389834c4a9641c', '89875cdc57c54474a8a74efd9b2a3b5d',
             '3b5d7c088409d9a40b7b09aa707777f8', '9384ab8608cdc3d479fe89cd51eed48f',
             '2d37e5385efd7064cb1d54c94960acae', 'ac0b09e7857660247b1477e93731de29',
             'f38bda98361e1de48a4ca2bd86ea3c17', 'a200b19ca1a9685429ed7e043c28e904',
             '625c14eee3ad46c99df7c7c891ef668a', '418e42c7d0405cc48a7b83f63ea53bb3',
             '45e653bab7fb20e499bda25e1b646fea', 'dab5c7d4c32e743048dfca98e2d5914f'}
SCRIPT = re.compile(rb'm_Script:[ \t]*\{fileID:[ \t]*(-?\d+),[ \t]*guid:[ \t]*([a-fA-F0-9]{32}),[ \t]*type:[ \t]*3\}')


def utc(): return dt.datetime.now(dt.timezone.utc).isoformat()


def evidence_targets(snapshot, binary):
    """Derive only unresolved scene roots, keeping all recovered runtime classes."""
    targets = collections.defaultdict(set)
    for issue in snapshot.get('issues', []):
        if issue.get('kind') != 'missing-scene-mono-script' or not issue['path'].endswith('.unity'): continue
        match = re.fullmatch(r'guid:([a-fA-F0-9]{32}); fileID:(-?\d+)', issue['detail'])
        if not match: raise ValueError('Unrecognized exact scene script identifier')
        guid, local = match.group(1).lower(), match.group(2)
        if guid not in RECOVERED: targets[issue['path']].add((guid, local))
    known_missing = {g for refs in targets.values() for g, _ in refs}
    for scene in binary.get('scenes', []):
        if scene.get('status') != 'decoded': raise ValueError('Incomplete offline binary scene decoding')
        for ref in scene.get('references', []):
            guid, local = ref.get('scriptGuid'), ref.get('scriptLocalFileId')
            if guid in known_missing: targets[scene['scenePath']].add((guid, str(local)))
    if len(targets) != SEED_COUNT: raise ValueError('Unexpected optional-demo seed count')
    return targets


def verify_evidence(work, products, evidence):
    if (evidence.get('schemaVersion') != 1 or evidence.get('kind') != KIND
            or evidence.get('sourceArchivesModified') is not False or evidence.get('unityLaunched') is not False):
        raise ValueError('Unexpected optional-demo evidence scope')
    loaded = {}
    for key in ('validationSnapshot', 'offlineBinaryEvidence'):
        item = evidence[key]; _, value, raw = owned_input(work, item['path'])
        if sha(raw) != item['sha256']: raise ValueError('Immutable diagnostic evidence changed')
        loaded[key] = value
    derived = evidence_targets(loaded['validationSnapshot'], loaded['offlineBinaryEvidence'])
    rows = {row['path']: row for row in evidence.get('seedTargets', [])}
    if len(rows) != SEED_COUNT or len(evidence['seedTargets']) != SEED_COUNT:
        raise ValueError('Exact49 scene seeds required')
    expected = {path[len(ROOT) + 1:]: sorted([{'guid': g, 'localId': f} for g, f in refs], key=lambda r: (r['guid'], r['localId'])) for path, refs in derived.items()}
    if set(rows) != set(expected): raise ValueError('Evidence added/omitted scene roots')
    all_guids = set()
    for path, row in rows.items():
        if not path.endswith('.unity') or row.get('missingScripts') != expected[path]:
            raise ValueError('Missing-script pointers differ from original diagnosis')
        owners = [p for p in products.values() if path.startswith(p['folder'] + '/')]
        if len(owners) != 1 or row.get('productId') != owners[0]['id']: raise ValueError('Scene product ownership differs')
        all_guids.update(r['guid'] for r in row['missingScripts'])
    if set(evidence.get('missingGuids', [])) != all_guids or all_guids & RECOVERED:
        raise ValueError('Recovered runtime code entered an optional-demo exclusion')
    for product in products.values():
        for record in product['files']:
            if not record['path'].endswith('.meta'): continue
            for guid in (record.get('guid'), record.get('originalGuid'), record.get('source', {}).get('originalGuid')):
                if guid and str(guid).lower() in all_guids: raise ValueError('An owned exact MonoScript recovery candidate exists')
    return rows


def verify_current_scripts(work, raw, target, evidence):
    expected = {(r['guid'], r['localId']) for r in evidence['missingScripts']}
    if raw.startswith(b'%YAML'):
        actual = {(m.group(2).decode().lower(), m.group(1).decode()) for m in SCRIPT.finditer(raw)}
    else:
        _, binary, binary_raw = owned_input(work, target['offlineBinaryEvidence']['path'])
        if sha(binary_raw) != target['offlineBinaryEvidence']['sha256']: raise ValueError('Binary scene evidence changed')
        rows = [r for r in binary['scenes'] if r['scenePath'] == ROOT + '/' + evidence['path']]
        if len(rows) != 1 or rows[0]['sourceSha256'] != sha(raw) or rows[0]['sourceBytes'] != len(raw):
            raise ValueError('Binary script evidence does not bind current scene bytes')
        actual = {(r.get('scriptGuid'), str(r.get('scriptLocalFileId'))) for r in rows[0]['references']}
    if not expected <= actual: raise ValueError('Current scene no longer contains the diagnosed missing script pointers')


def verify_runtime(report, plan, plan_bytes, original_manifest, original_bytes, receipt_bytes_by_product, headless, expected_files):
    headless = literal(headless)
    receipts = {key: (headless.parent / 'receipts' / (key + '.json'), raw) for key, raw in receipt_bytes_by_product.items()}
    _verify_runtime(report, b'', headless, headless.parent / 'staging-manifest.json', original_manifest,
                    original_bytes, literal(report['groupPlanPath']), plan_bytes, plan, receipts, expected_files)


def verify_missing_evidence(missing, plan, original_manifest):
    work = literal(original_manifest['stageRoot']).parents[3]
    targets = verify_evidence(work, {p['id']: p for p in original_manifest['products']}, missing)
    if {t['path'] for t in plan['targets'] if t['role'] == 'incomplete-optional-demo'} != set(targets):
        raise ValueError('Optional-demo evidence targets differ from approved group')
    return targets


def _verify_runtime(*args):
    previous = GROUP.KIND
    try:
        GROUP.KIND = KIND
        GROUP._verify_runtime(*args)
    finally: GROUP.KIND = previous
    report, _, headless, _, _, _, _, _, plan, _, _ = args
    artifact = plan.get('scriptResolutionEvidence', {})
    _, evidence, raw = owned_input(headless.parent, artifact.get('path', ''))
    if sha(raw) != artifact.get('sha256') or report.get('scriptResolutionEvidenceSha256') != sha(raw):
        raise ValueError('Native script identities lack exact current input binding')
    cases = evidence.get('cases', [])
    actual = report.get('scriptResolutions', [])
    if len(cases) != 44 or sum(c.get('expectedResolved') is True for c in cases) != 30 or len(actual) != 44:
        raise ValueError('Exact44 native script identities including30 restored classes required')
    _, missing, missing_raw = owned_input(headless.parent, plan['missingEvidence']['path'])
    if sha(missing_raw) != plan['missingEvidence']['sha256']:
        raise ValueError('Missing-script evidence binding changed during native replay')
    required_missing = {(r['guid'], r['localId']) for t in missing['seedTargets'] for r in t['missingScripts']}
    negatives = [c for c in cases if c.get('expectedResolved') is False]
    negative_pairs = {(c.get('guid'), c.get('fileId')) for c in negatives}
    originals = {(c.get('originalGuid'), c.get('originalFileId')) for c in cases}
    positives = {(c.get('guid'), c.get('fileId')) for c in cases if c.get('expectedResolved') is True}
    if (negative_pairs != required_missing or len(negative_pairs) != len(negatives) or len(originals) != len(cases)
            or positives & required_missing or any((c.get('originalGuid'), c.get('originalFileId')) != (c.get('guid'), c.get('fileId')) for c in negatives)):
        raise ValueError('Native negative cases must equal every exact missing scene-script pointer, with no unrelated or duplicate substitutions')
    for expected, result in zip(cases, actual):
        if (any(expected.get(k) != result.get(k) for k in ('originalGuid', 'originalFileId', 'guid', 'fileId', 'expectedResolved'))
                or result.get('matches') is not True or result.get('actualResolved') != expected['expectedResolved']
                or (expected['expectedResolved'] and result.get('resolvedClass') != expected.get('expectedClass'))):
            raise ValueError('Native script resolution did not match every exact retained/missing class')


def prepare(project, graph_path=None):
    _, work, _, stage, _, manifest, manifest_raw, products, records = context(project)
    graph_path, graph, graph_raw = owned_input(work, graph_path or work / 'optional-demo-incoming-consumers.json')
    snapshot_path, snapshot, snapshot_raw = owned_input(work, work / 'missing-script-validation-snapshot.json')
    binary_path, binary, binary_raw = owned_input(work, work / 'binary-scene-script-references.json')
    if (graph.get('status') != 'complete-read-only' or graph.get('errors') != [] or graph.get('filesChangedWhileRead') != []
            or graph.get('diagnosisSha256') != sha(snapshot_raw)):
        raise ValueError('Complete unchanged-source static incoming graph is required')
    derived = evidence_targets(snapshot, binary)
    seeds = []
    for path, refs in sorted(derived.items()):
        relative = path[len(ROOT) + 1:]; product, _ = records[relative]
        seeds.append({'path': relative, 'productId': product['id'],
                      'missingScripts': sorted([{'guid': g, 'localId': f} for g, f in refs], key=lambda r: (r['guid'], r['localId']))})
    evidence = {'schemaVersion': 1, 'kind': KIND, 'sourceArchivesModified': False, 'unityLaunched': False,
                'validationSnapshot': {'path': str(snapshot_path), 'sha256': sha(snapshot_raw)},
                'offlineBinaryEvidence': {'path': str(binary_path), 'sha256': sha(binary_raw)},
                'seedTargets': seeds, 'missingGuids': sorted({r['guid'] for t in seeds for r in t['missingScripts']}),
                'limitation': 'Missing exact MonoScript identities in the selected complete library; no claim that these optional dependencies do not exist elsewhere or that legacy effects were converted.'}
    seed_rows = verify_evidence(work, products, evidence)
    graph_seeds = {t['relativePath'] for t in graph['incompleteOptionalDemoTargets']}
    if graph_seeds != set(seed_rows): raise ValueError('Static graph seed identities differ')
    closure = {r['path'][len(ROOT) + 1:]: r for r in graph['incomingClosureAssets']}
    reachable = set(seed_rows)
    edges = [(e['consumer'][len(ROOT) + 1:], e['target'][len(ROOT) + 1:]) for e in graph['incomingEdges']]
    while True:
        following = reachable | {consumer for consumer, target in edges if target in reachable}
        if following == reachable: break
        reachable = following
    if reachable != set(closure): raise ValueError('Static graph contains unrelated outgoing assets')
    targets = []
    for relative in sorted(closure, key=ordinal_key):
        product, record = records[relative]; meta = records[relative + '.meta'][1]
        role = 'incomplete-optional-demo' if relative in seed_rows else 'incoming-demo-consumer'
        if Path(relative).suffix.lower() not in ({'.unity'} if role == 'incomplete-optional-demo' else {'.unity', '.prefab'}):
            raise ValueError('Only exact optional scene roots and incoming scene/prefab consumers are eligible')
        for path, rec in ((relative, record), (relative + '.meta', meta)):
            raw = read_bytes(child(stage, path))
            if sha(raw) != rec['sha256'] or len(raw) != rec['bytes']:
                raise ValueError('Current group bytes differ from canonical; recorder adoption required: ' + path)
        if closure[relative]['actualSha256'] != record['sha256'] or closure[relative]['actualBytes'] != record['bytes']:
            raise ValueError('Static graph source bytes changed')
        if role == 'incomplete-optional-demo': verify_current_scripts(work, read_bytes(child(stage, relative)), evidence, seed_rows[relative])
        targets.append({'productId': product['id'], 'path': relative, 'bytes': record['bytes'], 'sha256': record['sha256'],
                        'metadataPath': relative + '.meta', 'metadataBytes': meta['bytes'], 'metadataSha256': meta['sha256'],
                        'guid': meta['guid'], 'role': role,
                        'reason': 'optional-vendor-demo-missing-exact-incompatible-or-omitted-script' if role == 'incomplete-optional-demo' else 'serialized-incoming-consumer-of-incomplete-optional-demo'})
    run = child(work, 'optional-demo-group-plans/' + dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')); run.mkdir(parents=True)
    # The latest seven-scene evidence will later become a four-scene evidence
    # file. Bind this transaction to immutable complete original snapshots.
    for name, source, field in (('validation-snapshot.json', snapshot_raw, 'validationSnapshot'), ('binary-scene-references.json', binary_raw, 'offlineBinaryEvidence')):
        snapshot = run / name; write_new(snapshot, source); evidence[field]['path'] = str(snapshot)
    evidence_path = run / 'missing-evidence.json'; evidence_raw = encoded(evidence); write_new(evidence_path, evidence_raw)
    plan = {'schemaVersion': 1, 'kind': KIND, 'createdUtc': utc(), 'sourceManifestSha256': sha(manifest_raw),
            'missingEvidence': {'path': str(evidence_path), 'sha256': sha(evidence_raw)},
            'sourceIncomingGraph': {'path': str(graph_path), 'sha256': sha(graph_raw)}, 'targets': targets}
    script_path, _, script_raw = owned_input(work, work / 'optional-demo-script-resolution-probe.json')
    script_path = run / 'script-resolution.json'; write_new(script_path, script_raw)
    plan['scriptResolutionEvidence'] = {'path': str(script_path), 'sha256': sha(script_raw)}
    plan_path = run / 'group-plan.json'; write_new(plan_path, encoded(plan))
    atomic_write(work / 'incomplete-optional-demo-script-group-plan.json', encoded(plan))
    return plan, plan_path


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
    seed_targets = verify_evidence(work, products, evidence)
    planned = {t['path']: t for t in plan['targets']}
    if len(planned) != len(plan['targets']) or {p for p, t in planned.items() if t.get('role') == 'incomplete-optional-demo'} != set(seed_targets):
        raise ValueError('Plan omitted/added an incomplete optional scene target')
    if set(planned) != {r['path'][len(ROOT) + 1:] for r in graph['incomingClosureAssets']}:
        raise ValueError('Plan differs from exact incoming serialized closure')
    if graph.get('status') != 'complete-read-only' or graph.get('errors') != [] or graph.get('filesChangedWhileRead') != []:
        raise ValueError('Static graph is incomplete or source changed')
    if {t['relativePath'] for t in graph['incompleteOptionalDemoTargets']} != set(seed_targets):
        raise ValueError('Static graph has different optional seed roots')
    reachable = set(seed_targets)
    edges = [(e['consumer'][len(ROOT) + 1:], e['target'][len(ROOT) + 1:]) for e in graph['incomingEdges']]
    while True:
        following = reachable | {consumer for consumer, target in edges if target in reachable}
        if following == reachable: break
        reachable = following
    if reachable != set(planned): raise ValueError('Unrelated outgoing assets entered optional group')
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
        elif target['role'] != 'incomplete-optional-demo' or not relative.endswith('.unity'): raise ValueError('Unknown group target role')
        for candidate, record, expected_sha, expected_bytes in ((relative, body, target['sha256'], target['bytes']), (relative + '.meta', meta, target['metadataSha256'], target['metadataBytes'])):
            raw = read_bytes(child(stage, candidate))
            if sha(raw) != record['sha256'] or len(raw) != record['bytes'] or record['sha256'] != expected_sha or record['bytes'] != expected_bytes:
                raise ValueError('Current exact group source differs from canonical/plan SHA or bytes')
            originals[candidate] = raw; inputs[candidate] = {'sha256': sha(raw), 'bytes': len(raw)}
        guid = re.search(rb'(?m)^guid:[ \t]*([a-f0-9]{32})\s*$', originals[relative + '.meta'])
        if not guid or guid.group(1).decode() != target['guid'] or meta.get('guid') != target['guid']:
            raise ValueError('Current original metadata GUID changed')
        if target['role'] == 'incomplete-optional-demo': verify_current_scripts(work, originals[relative], evidence, seed_targets[relative])
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
    run_root = child(work, 'source-only-optional-demo-quarantine/' + run); run_root.mkdir(parents=True)
    report_path = run_root / 'report.json'; latest = child(work, 'source-only-optional-demo-quarantine-latest.json')
    destinations = {p: child(work, 'SourceOnly/' + p) for p in originals}
    if any(os.path.lexists(p) for p in destinations.values()): raise ValueError('SourceOnly destination already exists; overwrite forbidden')
    report = {'schemaVersion': 2, 'kind': KIND, 'run': run, 'status': 'prepared' if apply else 'dry-run-ready', 'apply': apply,
              'sourceManifestSha256': sha(manifest_raw), 'sourceRuntimeProofSha256': sha(runtime_raw),
              'sourceMissingEvidenceSha256': sha(evidence_raw), 'sourceIncomingGraphSha256': sha(graph_raw), 'sourceGroupPlanSha256': sha(plan_raw),
              'runtimeProof': str(runtime_path), 'missingEvidence': str(evidence_path), 'incomingGraph': str(graph_path), 'groupPlan': str(plan_path),
              'sourceArchivesModified': False, 'actualMainAssetsModified': False, 'terrainPayloadsChanged': False,
              'optionalDemoAssets': SEED_COUNT, 'groupAssets': len(planned), 'consumerAssets': len(planned) - SEED_COUNT,
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
            preserved.update(preservedPath=row['destination'], sourceOnlyRun=run, sourceOnlyReason=KIND,
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
    prep = commands.add_parser('prepare'); prep.add_argument('--project', required=True, type=Path); prep.add_argument('--incoming-graph', type=Path)
    run = commands.add_parser('quarantine'); run.add_argument('--project', required=True, type=Path); run.add_argument('--group-plan', required=True, type=Path); run.add_argument('--runtime-proof', required=True, type=Path)
    run.add_argument('--apply', action='store_true'); run.add_argument('--editor-stopped', action='store_true')
    run.add_argument('--expected-manifest-sha256'); run.add_argument('--expected-group-plan-sha256'); run.add_argument('--expected-runtime-proof-sha256')
    args = parser.parse_args()
    if args.command == 'prepare':
        plan, path = prepare(args.project, args.incoming_graph)
        print(json.dumps({'status': 'plan-prepared', 'plan': str(path), 'sha256': sha(encoded(plan)), 'assets': len(plan['targets'])})); return
    report, path = quarantine(args.project, args.group_plan, args.runtime_proof, args.apply, args.editor_stopped, args.expected_manifest_sha256, args.expected_group_plan_sha256, args.expected_runtime_proof_sha256)
    print(json.dumps({'status': report['status'], 'report': str(path), 'files': len(report['files']), 'assets': report['groupAssets']}))


if __name__ == '__main__': main()
