"""Synthetic native/YAML group transactions only; no real assets or Unity."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(filename)); value = importlib.util.module_from_spec(spec); spec.loader.exec_module(value); return value


tool = load('group_quarantine', 'quarantine-unity-source-only-group.py')
binary = load('group_binary_fixture', 'test-finalize-unity-asset-library.py')


class GroupFixtures(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='yamyam-group-'); self.project = Path(self.temp.name) / 'Unity'
        self.work = self.project / 'Library/YamyamAssetLibrary'; self.headless = self.work / 'headless-project'; self.stage = self.headless / tool.ROOT
        self.stage.mkdir(parents=True); (self.work / 'receipts').mkdir(); (self.project / 'Assets').mkdir()
        self.main = self.project / 'Assets/Keep.txt'; self.main.write_bytes(b'unrelated main assets remain exact')
        self.products = {}; self.archive_paths = []
        for i in [n for n in range(85) if n != 83]:
            product_id = f'{i:03d}'; folder = product_id + '-fixture'; self.products[product_id] = {'id': product_id, 'folder': folder, 'status': 'complete', 'files': [], 'inputs': [], 'originalBinaryGuidCollisionBlockers': [], 'binaryGuidRecoveryProofs': []}
            self.add(product_id, folder + '/Keep.txt', b'usable models/materials and unrelated files remain')
        self.targets = []; self.terrains = []; self.index_rows = []; self.source_indices = []
        missing_counter = 1; terrain_counter = 0
        for product_id, count, missing_sizes in [('004', 1, [3]), ('033', 10, [3] * 7 + [2] * 3), ('084', 1, [1])]:
            archive = Path(self.temp.name) / (product_id + '.unitypackage'); archive.write_bytes(('original-' + product_id).encode()); self.archive_paths.append(archive)
            self.products[product_id]['inputs'] = [{'path': str(archive), 'bytes': archive.stat().st_size}]
            missing_product = []
            for i, missing_size in enumerate(missing_sizes):
                missing = [f'{n:032x}' for n in range(missing_counter, missing_counter + missing_size)]; missing_counter += missing_size; missing_product += missing
                relative = product_id + '-fixture/Terrain/Incomplete' + str(i) + '.asset'; guid = f'{1000 + terrain_counter:032x}'; terrain_counter += 1
                raw = binary.serialized_fixture(22, [tool.SAFE.FINALIZER.guid_byte_forms(g)['unity-byte-nibbles'].hex() for g in missing])
                self.add(product_id, relative, raw); self.add(product_id, relative + '.meta', ('fileFormatVersion: 2\nguid: ' + guid + '\n').encode(), guid)
                self.targets.append({'path': relative, 'productId': product_id, 'missingGuids': missing})
                self.terrains.append({'path': tool.ROOT + '/' + relative, 'productId': product_id, 'layers': {'m_TerrainLayers': [{'guid': g, 'status': 'external-guid-not-in-current-library'} for g in missing]}, 'treePrototypes': []})
            index = {'archive': str(archive), 'archiveBytes': archive.stat().st_size, 'archiveMtimeNs': archive.stat().st_mtime_ns,
                     'availableUnitypackageMembers': [archive.name], 'guidFolders': 1, 'metadataFiles': 1, 'pathnames': 1, 'entries': [{'folderGuid': 'f' * 32, 'metadata': {'guid': 'f' * 32}}]}
            path = self.work / ('index-' + product_id + '.json'); path.write_bytes(tool.encoded(index))
            self.source_indices.append({'productId': product_id, 'path': str(path), 'sha256': tool.sha(path.read_bytes()), 'archive': str(archive), 'archiveBytes': index['archiveBytes'], 'archiveMtimeNs': index['archiveMtimeNs'], 'missingGuids': missing_product})
            self.index_rows.append({'productId': product_id, 'index': str(path), 'queriedMissingGuids': missing_product, 'exactMatches': [], 'availableUnitypackageMembers': [archive.name]})
        # Exactly two upstream consumers. The valid empty TerrainData remains.
        self.empty = '033-fixture/Terrain/New Terrain.asset'; self.add('033', self.empty, binary.serialized_fixture(22, [])); self.add('033', self.empty + '.meta', b'fileFormatVersion: 2\nguid: eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee\n', 'e' * 32)
        terrain = self.targets[1]['path']; terrain_guid = self.record(terrain + '.meta')['guid']
        self.prefab = '033-fixture/Demo/TerrainRoot.prefab'; self.scene = '033-fixture/Demo/OnlyIncompleteDemo.unity'
        self.add('033', self.prefab, ('%YAML 1.1\n--- !u!1 &1\nm_TerrainData: {fileID: 15600000, guid: ' + terrain_guid + ', type: 2}\n').encode()); self.add('033', self.prefab + '.meta', b'fileFormatVersion: 2\nguid: dddddddddddddddddddddddddddddddd\n', 'd' * 32)
        self.add('033', self.scene, b'%YAML 1.1\n--- !u!1 &1\nm_SourcePrefab: {fileID: 1, guid: dddddddddddddddddddddddddddddddd, type: 3}\n'); self.add('033', self.scene + '.meta', b'fileFormatVersion: 2\nguid: cccccccccccccccccccccccccccccccc\n', 'c' * 32)
        self.products['084']['originalBinaryGuidCollisionBlockers'] = [self.targets[-1]['path']]
        self.products['084']['binaryGuidRecoveryProofs'] = [{'path': self.targets[-1]['path'], 'proofVersion': 2, 'important': 'historical scope remains exact'}]
        self.paths = {t['path'] for t in self.targets} | {self.prefab, self.scene}
        self.manifest = {'stageRoot': str(self.stage), 'targetAssetRoot': tool.ROOT, 'products': list(self.products.values()), 'summary': {}}
        self.manifest_path = self.work / 'staging-manifest.json'; self.plan_path = self.work / 'group-plan.json'; self.evidence_path = self.work / 'missing-evidence.json'; self.graph_path = self.work / 'incoming.json'
        self.runtime_path = self.headless / 'Library/YamyamAssetLibrary/provider-proof/report.json'; self.runtime_path.parent.mkdir(parents=True)
        self.evidence = {'schemaVersion': 1, 'kind': tool.KIND, 'sourceArchivesModified': False, 'incompleteTerrainTargets': self.targets,
                         'missingGuids': sorted({g for t in self.targets for g in t['missingGuids']}), 'sourcePackageIndexes': self.source_indices}
        self.graph = {'incomingClosureAssets': [{'path': tool.ROOT + '/' + p, 'actualSha256': self.record(p)['sha256'], 'actualBytes': self.record(p)['bytes']} for p in sorted(self.paths)],
                      'incomingEdges': [{'consumer': tool.ROOT + '/' + self.prefab, 'target': tool.ROOT + '/' + terrain}, {'consumer': tool.ROOT + '/' + self.scene, 'target': tool.ROOT + '/' + self.prefab}],
                      'incompleteTerrainTargets': [{'relativePath': t['path']} for t in self.targets], 'errors': [], 'filesChangedWhileRead': []}
        self.finish()

    def tearDown(self): self.temp.cleanup()

    def add(self, product_id, relative, raw, guid=None):
        path = self.stage / relative; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(raw)
        r = {'path': relative, 'bytes': len(raw), 'sha256': tool.sha(raw), 'source': {'kind': 'unitypackage'}}
        if guid: r['guid'] = guid
        self.products[product_id]['files'].append(r); return path

    def record(self, relative): return next(r for p in self.products.values() for r in p['files'] if r['path'] == relative)

    def finish(self):
        self.manifest_path.write_bytes(tool.encoded(self.manifest))
        for p in self.products.values(): (self.work / 'receipts' / (p['id'] + '.json')).write_bytes(tool.encoded(p))
        self.evidence_path.write_bytes(tool.encoded(self.evidence)); self.graph_path.write_bytes(tool.encoded(self.graph))
        rows = []
        for path in sorted(self.paths):
            body, meta = self.record(path), self.record(path + '.meta')
            rows.append({'productId': path[:3], 'path': path, 'bytes': body['bytes'], 'sha256': body['sha256'], 'metadataPath': path + '.meta', 'metadataBytes': meta['bytes'], 'metadataSha256': meta['sha256'], 'guid': meta['guid'], 'role': 'incomplete-terrain' if path in {t['path'] for t in self.targets} else 'incoming-demo-consumer', 'reason': 'fixture-original-provider-omission'})
        self.plan = {'schemaVersion': 1, 'kind': tool.KIND, 'sourceManifestSha256': tool.sha(self.manifest_path.read_bytes()), 'missingEvidence': {'path': str(self.evidence_path), 'sha256': tool.sha(self.evidence_path.read_bytes())}, 'sourceIncomingGraph': {'path': str(self.graph_path), 'sha256': tool.sha(self.graph_path.read_bytes())}, 'targets': rows}
        self.plan_path.write_bytes(tool.encoded(self.plan)); self.runtime = self.runtime_for(self.plan); self.runtime_path.write_bytes(tool.encoded(self.runtime))

    def runtime_for(self, plan):
        roots = sorted((tool.ROOT + '/' + r['path'] for p in self.products.values() for r in p['files'] if not r['path'].endswith('.meta') and r['path'] not in self.paths), key=tool.ordinal_key)
        targets = []
        for t in plan['targets']:
            targets.append({'productId': t['productId'], 'path': tool.ROOT + '/' + t['path'], 'relativePath': t['path'], 'guid': t['guid'], 'bytes': t['bytes'], 'canonicalSha256': t['sha256'], 'actualSha256': t['sha256'], 'sourceArtifactSha256': t['sha256'], 'metadataPath': tool.ROOT + '/' + t['metadataPath'], 'metadataBytes': t['metadataBytes'], 'metadataSha256': t['metadataSha256'], 'canonicalMetadataSha256': t['metadataSha256'], 'reason': t['reason'], 'role': t['role'], 'referencedByOtherRootAssets': False, 'checkedInboundReferences': 0})
        return {'schemaVersion': 1, 'kind': tool.KIND, 'status': 'dependency-proof-complete', 'apply': False, 'errors': [], 'blockers': [], 'observedUnityErrors': 0, 'originalArchivesModified': False, 'scenesOpened': False, 'terrainDataLoaded': False, 'assetsSaved': False, 'completedUtc': '2026-10-19T00:00:01Z', 'project': str(self.headless), 'manifestPath': str(self.manifest_path), 'manifestSha256': tool.sha(self.manifest_path.read_bytes()), 'groupPlanPath': str(self.plan_path), 'groupPlanSha256': tool.sha(self.plan_path.read_bytes()), 'sourceMissingEvidenceSha256': plan['missingEvidence']['sha256'], 'sourceIncomingGraphSha256': plan['sourceIncomingGraph']['sha256'], 'receiptSha256ByProduct': [{'productId': p, 'sha256': tool.sha((self.work / 'receipts' / (p + '.json')).read_bytes())} for p in sorted(tool.PRODUCTS)], 'dependencyProof': {'proofVersion': 1, 'status': 'unreferenced-by-other-root-assets', 'startedUtc': '2026-10-19T00:00:00Z', 'completedUtc': '2026-10-19T00:00:01Z', 'method': 'AssetDatabase.GetDependencies(all outside group, recursive:true)', 'rootAssetsChecked': len(roots), 'rootPathsSha256': tool.sha('\n'.join(roots).encode()), 'dependencyClosurePaths': len(roots), 'closurePathsSha256': tool.sha('\n'.join(roots).encode()), 'excludedTargets': targets}}

    def run_tool(self, apply=False):
        return tool.quarantine(self.project, self.plan_path, self.runtime_path, apply, apply, tool.sha(self.manifest_path.read_bytes()), tool.sha(self.plan_path.read_bytes()), tool.sha(self.runtime_path.read_bytes()))

    def original_bytes(self):
        paths = [self.stage / p for p in self.paths | {p + '.meta' for p in self.paths}]
        paths += [self.manifest_path, self.main, self.stage / self.empty] + self.archive_paths + [self.work / 'receipts' / (p + '.json') for p in tool.PRODUCTS]
        return {p: p.read_bytes() for p in paths}

    def test_default_dryrun_preserves_every_asset_and_source(self):
        before = self.original_bytes(); report, _ = self.run_tool(); self.assertEqual('dry-run-ready', report['status']); self.assertEqual(28, len(report['files']))
        self.assertFalse((self.work / 'SourceOnly').exists())
        for path, raw in before.items(): self.assertEqual(raw, path.read_bytes())

    def test_apply_moves_only_exact_group_and_preserves_historical896_fields(self):
        before = self.original_bytes(); proof = copy.deepcopy(self.products['084']['binaryGuidRecoveryProofs']); blockers = copy.deepcopy(self.products['084']['originalBinaryGuidCollisionBlockers'])
        report, report_path = self.run_tool(True); current = json.loads(self.manifest_path.read_bytes()); self.assertEqual('complete', report['status'])
        for row in report['files']:
            self.assertFalse((self.stage / row['path']).exists()); self.assertEqual(before[self.stage / row['path']], Path(row['destination']).read_bytes()); self.assertEqual(before[self.stage / row['path']], Path(row['backupPath']).read_bytes())
        p84 = next(p for p in current['products'] if p['id'] == '084'); self.assertEqual(proof, p84['binaryGuidRecoveryProofs']); self.assertEqual(blockers, p84['originalBinaryGuidCollisionBlockers'])
        self.assertEqual(28, current['summary']['sourceOnlyFiles']); self.assertEqual(before[self.main], self.main.read_bytes()); self.assertEqual(before[self.stage / self.empty], (self.stage / self.empty).read_bytes())
        for archive in self.archive_paths: self.assertEqual(before[archive], archive.read_bytes())
        self.assertEqual(before[self.manifest_path], (report_path.parent / 'manifest.json').read_bytes())

    def test_stale_manifest_plan_runtime_and_evidence_refuse(self):
        self.runtime['manifestSha256'] = '0' * 64; self.runtime_path.write_bytes(tool.encoded(self.runtime))
        with self.assertRaisesRegex(ValueError, 'Fresh clean'): self.run_tool()
        self.finish(); self.evidence_path.write_bytes(b'{}')
        with self.assertRaisesRegex(ValueError, 'SHA changed'): self.run_tool()
        self.finish(); self.plan['sourceManifestSha256'] = '0' * 64; self.plan_path.write_bytes(tool.encoded(self.plan))
        with self.assertRaisesRegex(ValueError, 'stale/different'): self.run_tool()

    def test_failed_job_inbound_reference_and_incomplete_root_refuse(self):
        self.runtime['status'] = 'failed'; self.runtime_path.write_bytes(tool.encoded(self.runtime))
        with self.assertRaisesRegex(ValueError, 'Fresh clean'): self.run_tool()
        self.finish(); self.runtime['dependencyProof']['excludedTargets'][0]['checkedInboundReferences'] = 1; self.runtime_path.write_bytes(tool.encoded(self.runtime))
        with self.assertRaisesRegex(ValueError, 'inbound'): self.run_tool()
        self.finish(); self.runtime['dependencyProof']['rootAssetsChecked'] -= 1; self.runtime_path.write_bytes(tool.encoded(self.runtime))
        with self.assertRaisesRegex(ValueError, 'every current'): self.run_tool()

    def test_provider_recovery_candidate_or_original_archive_drift_refuses(self):
        self.add('033', '033-fixture/Recovered.meta', ('guid: ' + self.targets[0]['missingGuids'][0] + '\n').encode(), self.targets[0]['missingGuids'][0]); self.finish()
        with self.assertRaisesRegex(ValueError, 'recovery candidate'): self.run_tool()
        self.products['033']['files'].pop(); self.finish(); self.archive_paths[0].write_bytes(b'changed-source')
        with self.assertRaisesRegex(ValueError, 'archive/index binding'): self.run_tool()

    def test_added_usable_outgoing_asset_or_valid_empty_target_refuses(self):
        self.plan['targets'][0]['role'] = 'incoming-demo-consumer'; self.plan_path.write_bytes(tool.encoded(self.plan))
        with self.assertRaisesRegex(ValueError, 'TerrainData target'): self.run_tool()
        self.finish(); self.plan['targets'].append(copy.deepcopy(self.plan['targets'][0])); self.plan_path.write_bytes(tool.encoded(self.plan))
        with self.assertRaisesRegex(ValueError, 'TerrainData target'): self.run_tool()

    def test_source_payload_meta_guid_or_missing_reference_drift_refuses(self):
        relative = self.targets[0]['path']; (self.stage / relative).write_bytes(b'foreign')
        with self.assertRaisesRegex(ValueError, 'canonical/plan'): self.run_tool()
        raw = binary.serialized_fixture(22, ['f' * 32]); (self.stage / relative).write_bytes(raw); self.record(relative).update(bytes=len(raw), sha256=tool.sha(raw)); self.graph['incomingClosureAssets'][0].update(actualBytes=len(raw), actualSha256=tool.sha(raw)); self.finish()
        with self.assertRaisesRegex(ValueError, 'omitted original'): self.run_tool()

    def test_existing_destination_or_main_stage_redirect_refuses(self):
        relative = self.targets[0]['path']; destination = self.work / 'SourceOnly' / relative; destination.parent.mkdir(parents=True); destination.write_bytes(b'earlier-source')
        with self.assertRaisesRegex(ValueError, 'already exists'): self.run_tool()
        self.manifest['stageRoot'] = str(self.project / tool.ROOT); self.finish()
        with self.assertRaisesRegex(ValueError, 'isolated library'): self.run_tool()

    def test_manifest_write_failure_rolls_back_all_moves_and_receipts(self):
        before = self.original_bytes(); actual = tool.atomic_write; failed = False
        def fail(path, raw):
            nonlocal failed
            if Path(path) == self.manifest_path and not failed: failed = True; raise OSError('synthetic canonical failure')
            return actual(path, raw)
        with mock.patch.object(tool, 'atomic_write', side_effect=fail):
            with self.assertRaisesRegex(OSError, 'canonical failure'): self.run_tool(True)
        for path, raw in before.items(): self.assertEqual(raw, path.read_bytes())

    def test_partial_move_failure_rolls_back_already_moved_files(self):
        before = self.original_bytes(); actual = tool.os.rename; calls = 0
        def fail(source, destination):
            nonlocal calls
            calls += 1
            if calls == 4: raise OSError('synthetic move failure')
            return actual(source, destination)
        with mock.patch.object(tool.os, 'rename', side_effect=fail):
            with self.assertRaisesRegex(OSError, 'move failure'): self.run_tool(True)
        for path, raw in before.items(): self.assertEqual(raw, path.read_bytes())

    def test_final_report_failure_rolls_back_transaction(self):
        before = self.original_bytes(); actual = tool.atomic_write; failed = False
        def fail(path, raw):
            nonlocal failed
            if Path(path).name == 'report.json' and json.loads(raw).get('status') == 'complete' and not failed: failed = True; raise OSError('synthetic final report failure')
            return actual(path, raw)
        with mock.patch.object(tool, 'atomic_write', side_effect=fail):
            with self.assertRaisesRegex(OSError, 'final report failure'): self.run_tool(True)
        for path, raw in before.items(): self.assertEqual(raw, path.read_bytes())

    def test_rollback_preserves_foreign_canonical_write(self):
        actual = tool.atomic_write; foreign = b'foreign-receipt'; receipt_path = self.work / 'receipts/004.json'; failed = False
        def fail(path, raw):
            nonlocal failed
            if Path(path) == self.manifest_path and not failed:
                failed = True; receipt_path.write_bytes(foreign); raise OSError('concurrent canonical write')
            return actual(path, raw)
        with mock.patch.object(tool, 'atomic_write', side_effect=fail):
            with self.assertRaisesRegex(OSError, 'concurrent'): self.run_tool(True)
        self.assertEqual(foreign, receipt_path.read_bytes()); report = json.loads(Path(json.loads((self.work / 'source-only-group-quarantine-latest.json').read_bytes())['report']).read_bytes()); self.assertTrue(report['rollbackErrors'])

    def test_rollback_preserves_foreign_sourceonly_write_and_backup(self):
        actual = tool.os.rename; calls = 0; first_destination = None
        def fail(source, destination):
            nonlocal calls, first_destination
            calls += 1
            if calls == 1: first_destination = Path(destination)
            if calls == 2: first_destination.write_bytes(b'foreign-sourceonly'); raise OSError('concurrent payload write')
            return actual(source, destination)
        with mock.patch.object(tool.os, 'rename', side_effect=fail):
            with self.assertRaisesRegex(OSError, 'concurrent'): self.run_tool(True)
        self.assertEqual(b'foreign-sourceonly', first_destination.read_bytes()); report = json.loads(Path(json.loads((self.work / 'source-only-group-quarantine-latest.json').read_bytes())['report']).read_bytes()); self.assertTrue(report['rollbackErrors']); self.assertTrue(Path(report['files'][0]['backupPath']).is_file())

    def test_apply_requires_reviewed_hashes_and_editor_stopped(self):
        with self.assertRaisesRegex(ValueError, 'stopped Editor'): tool.quarantine(self.project, self.plan_path, self.runtime_path, True)

    def test_installer_replay_interfaces_accept_exact_original_snapshot(self):
        inputs = {r['path']: {'sha256': r['sha256'], 'bytes': r['bytes']} for p in self.products.values() for r in p['files'] if r['path'] in self.paths or (r['path'].endswith('.meta') and r['path'][:-5] in self.paths)}
        receipts = {p: (self.work / 'receipts' / (p + '.json')).read_bytes() for p in tool.PRODUCTS}
        tool.verify_runtime(self.runtime, self.plan, self.plan_path.read_bytes(), self.manifest, self.manifest_path.read_bytes(), receipts, self.headless, inputs)
        self.assertEqual(12, len(tool.verify_missing_evidence(self.evidence, self.plan, self.manifest)))

    def preparation_inputs(self):
        diagnosis = {'terrains': self.terrains + [{'path': tool.ROOT + '/' + self.empty, 'productId': '033', 'layers': {}, 'treePrototypes': []}], 'errors': []}
        diagnosis_path = self.work / 'diagnosis.json'; diagnosis_path.write_bytes(tool.encoded(diagnosis))
        self.graph['diagnosisSha256'] = tool.sha(diagnosis_path.read_bytes()); self.graph_path.write_bytes(tool.encoded(self.graph))
        index_path = self.work / 'index-proof.json'; index_path.write_bytes(tool.encoded({'sourceArchivesModified': False, 'products': self.index_rows}))
        return diagnosis_path, index_path

    def test_prepare_derives_exact_incoming_group_and_retains_valid_empty(self):
        diagnosis_path, index_path = self.preparation_inputs()
        plan, path = tool.prepare(self.project, self.graph_path, diagnosis_path, index_path)
        self.assertEqual(self.paths, {t['path'] for t in plan['targets']}); self.assertNotIn(self.empty, {t['path'] for t in plan['targets']})
        self.assertEqual(path.read_bytes(), (self.work / 'incomplete-provider-demo-group-plan.json').read_bytes())

    def test_prepare_refuses_unrelated_consumer_and_unclassified_read_error(self):
        diagnosis_path, index_path = self.preparation_inputs()
        self.graph['incomingClosureAssets'].append({'path': tool.ROOT + '/' + self.empty}); self.graph_path.write_bytes(tool.encoded(self.graph))
        with self.assertRaisesRegex(ValueError, 'unrelated'): tool.prepare(self.project, self.graph_path, diagnosis_path, index_path)
        self.graph['incomingClosureAssets'].pop(); self.graph['errors'] = [{'path': tool.ROOT + '/Unknown.asset'}]; self.graph_path.write_bytes(tool.encoded(self.graph))
        with self.assertRaisesRegex(ValueError, 'parse/read errors'): tool.prepare(self.project, self.graph_path, diagnosis_path, index_path)

    def test_prepare_permits_only_exact_known_non_guid_package_manifest_entry(self):
        diagnosis_path, index_path = self.preparation_inputs(); source = Path(self.index_rows[0]['index']); value = json.loads(source.read_bytes())
        value['entries'].append({'folderGuid': 'packagemanagermanifest', 'originalPath': None, 'metadata': None}); value['guidFolders'] += 1; source.write_bytes(tool.encoded(value))
        tool.prepare(self.project, self.graph_path, diagnosis_path, index_path)
        value['entries'][-1]['folderGuid'] = 'unknown-lost-metadata'; source.write_bytes(tool.encoded(value))
        with self.assertRaisesRegex(ValueError, 'incomplete'): tool.prepare(self.project, self.graph_path, diagnosis_path, index_path)

    def test_no_terrain_load_or_asset_save_scope_is_explicit(self):
        self.runtime['terrainDataLoaded'] = True; self.runtime_path.write_bytes(tool.encoded(self.runtime))
        with self.assertRaisesRegex(ValueError, 'Fresh clean'): self.run_tool()
        self.finish(); del self.runtime['assetsSaved']; self.runtime_path.write_bytes(tool.encoded(self.runtime))
        with self.assertRaisesRegex(ValueError, 'Fresh clean'): self.run_tool()

    def test_duplicate_canonical_product_entry_refuses(self):
        self.manifest['products'].append(copy.deepcopy(self.products['004']))
        self.manifest_path.write_bytes(tool.encoded(self.manifest))
        with self.assertRaisesRegex(ValueError, 'complete84-product'): self.run_tool()


if __name__ == '__main__': unittest.main()
