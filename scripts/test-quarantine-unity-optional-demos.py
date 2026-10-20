"""Temporary synthetic49-scene transactions; no actual library or Unity."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock


def load(name, file):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(file)); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


m = load('optional_quarantine_fixture', 'quarantine-unity-optional-demos.py')
old = load('optional_existing_fixtures', 'test-quarantine-unity-source-only-group.py')


class OptionalFixtures(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='yamyam-optional-'); self.project = Path(self.temp.name) / 'Unity'
        self.work = self.project / 'Library/YamyamAssetLibrary'; self.headless = self.work / 'headless-project'; self.stage = self.headless / m.ROOT
        self.stage.mkdir(parents=True); (self.work / 'receipts').mkdir(); (self.project / 'Assets').mkdir()
        self.keep = self.project / 'Assets/Keep.txt'; self.keep.write_bytes(b'foreign assets remain')
        self.products = {}; self.paths = set(); self.targets = []
        for i in [n for n in range(85) if n != 83]:
            product = {'id': f'{i:03d}', 'folder': f'{i:03d}-fixture', 'status': 'complete', 'files': [], 'sourceOnlyHistory': [], 'inputs': []}
            self.products[product['id']] = product; self.add(product['id'], product['folder'] + '/Keep.txt', b'usable model/material remains')
        issues = []
        for i in range(49):
            pid = ['004', '033', '084'][i % 3]; relative = pid + '-fixture/Demo' + str(i) + '.unity'; self.paths.add(relative)
            guid = f'{10000 + i % 14:032x}'
            raw = ('%YAML 1.1\n--- !u!114 &1\nMonoBehaviour:\n  m_Script: {fileID: 11500000, guid: ' + guid + ', type: 3}\n').encode()
            self.add(pid, relative, raw); self.add(pid, relative + '.meta', ('fileFormatVersion: 2\nguid: ' + f'{i + 100:032x}' + '\n').encode(), f'{i + 100:032x}')
            issues.append({'kind': 'missing-scene-mono-script', 'path': m.ROOT + '/' + relative, 'detail': 'guid:' + guid + '; fileID:11500000'})
        historical = next(p for p in sorted(self.paths) if p.startswith('084'))
        self.products['084']['originalBinaryGuidCollisionBlockers'] = [historical]
        self.products['084']['binaryGuidRecoveryProofs'] = [{'path': historical, 'proofVersion': 2, 'unchanged': True}]
        self.manifest = {'stageRoot': str(self.stage), 'targetAssetRoot': m.ROOT, 'products': list(self.products.values()), 'sourceOnlyHistory': [{'kind': 'previous-immutable-history'}]}
        self.manifest_path = self.work / 'staging-manifest.json'
        self.write(self.work / 'missing-script-validation-snapshot.json', {'issues': issues})
        self.write(self.work / 'binary-scene-script-references.json', {'scenes': []})
        cases = [{'originalGuid': f'{i + 1000 if i < 30 else 10000 + i - 30:032x}', 'originalFileId': '11500000', 'guid': f'{i + 1000 if i < 30 else 10000 + i - 30:032x}', 'fileId': '11500000', 'expectedClass': 'Fixture.Type' if i < 30 else '', 'expectedResolved': i < 30} for i in range(44)]
        self.write(self.work / 'optional-demo-script-resolution-probe.json', {'schemaVersion': 1, 'cases': cases})
        graph = {'status': 'complete-read-only', 'diagnosisSha256': m.sha((self.work / 'missing-script-validation-snapshot.json').read_bytes()), 'errors': [], 'filesChangedWhileRead': [], 'incomingEdges': [],
                 'incompleteOptionalDemoTargets': [{'relativePath': p} for p in self.paths],
                 'incomingClosureAssets': [{'path': m.ROOT + '/' + p, 'actualSha256': self.record(p)['sha256'], 'actualBytes': self.record(p)['bytes']} for p in self.paths]}
        self.write(self.work / 'optional-demo-incoming-consumers.json', graph)
        self.flush()
        self.plan, _ = m.prepare(self.project); self.plan_path = self.work / 'incomplete-optional-demo-script-group-plan.json'
        self.runtime_path = self.headless / 'Library/YamyamAssetLibrary/optional-demo-group-proof-report.json'
        self.runtime = old.GroupFixtures.runtime_for(self, self.plan); self.runtime['kind'] = m.KIND
        self.runtime['scriptResolutionEvidenceSha256'] = m.sha((self.work / 'optional-demo-script-resolution-probe.json').read_bytes())
        self.runtime['scriptResolutions'] = [dict(c, actualResolved=c['expectedResolved'], resolvedClass=c['expectedClass'], matches=True) for c in cases]
        self.write(self.runtime_path, self.runtime)

    def tearDown(self): self.temp.cleanup()
    def write(self, path, value): path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(m.encoded(value))
    def add(self, pid, relative, raw, guid=None):
        p = self.stage / relative; p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(raw)
        row = {'path': relative, 'bytes': len(raw), 'sha256': m.sha(raw)}
        if guid: row['guid'] = guid
        self.products[pid]['files'].append(row)
    def record(self, path): return next(r for p in self.products.values() for r in p['files'] if r['path'] == path)
    def flush(self):
        self.write(self.manifest_path, self.manifest)
        for pid, product in self.products.items(): self.write(self.work / 'receipts' / (pid + '.json'), product)
    def run_tool(self, apply=False):
        return m.quarantine(self.project, self.plan_path, self.runtime_path, apply, apply, m.sha(self.manifest_path.read_bytes()), m.sha(self.plan_path.read_bytes()), m.sha(self.runtime_path.read_bytes()))

    def test_dry_run_and_apply_exact98_files_keep_prior_history_and896_scope(self):
        original = self.manifest_path.read_bytes(); dry, _ = self.run_tool(); self.assertEqual('dry-run-ready', dry['status']); self.assertEqual(98, len(dry['files'])); self.assertEqual(original, self.manifest_path.read_bytes())
        proof = copy.deepcopy(self.products['084']['binaryGuidRecoveryProofs']); result, path = self.run_tool(True); self.assertEqual('complete', result['status'])
        current = json.loads(self.manifest_path.read_bytes()); self.assertEqual(self.manifest['sourceOnlyHistory'], current['sourceOnlyHistory'][:-1]); self.assertEqual(m.KIND, current['sourceOnlyHistory'][-1]['kind'])
        self.assertEqual(proof, next(p for p in current['products'] if p['id'] == '084')['binaryGuidRecoveryProofs'])
        for row in result['files']: self.assertEqual(Path(row['destination']).read_bytes(), Path(row['backupPath']).read_bytes()); self.assertFalse((self.stage / row['path']).exists())
        self.assertEqual(b'foreign assets remain', self.keep.read_bytes()); self.assertEqual(original, (path.parent / 'manifest.json').read_bytes())

    def test_failed_or_inbound_runtime_proof_refuses(self):
        self.runtime['dependencyProof']['excludedTargets'][0]['checkedInboundReferences'] = 1; self.write(self.runtime_path, self.runtime)
        with self.assertRaisesRegex(ValueError, 'inbound'): self.run_tool()

    def test_newly_restored_or_wrong_native_class_refuses(self):
        self.runtime['scriptResolutions'][-1].update(actualResolved=True, resolvedClass='Recovered.Type', matches=False); self.write(self.runtime_path, self.runtime)
        with self.assertRaisesRegex(ValueError, 'script resolution'): self.run_tool()

    def test_native_probe_cannot_substitute_an_unrelated_unresolved_identifier(self):
        path = Path(self.plan['scriptResolutionEvidence']['path']); evidence = json.loads(path.read_bytes())
        evidence['cases'][30].update(guid='f' * 32, originalGuid='f' * 32); self.write(path, evidence)
        self.plan['scriptResolutionEvidence']['sha256'] = m.sha(path.read_bytes()); self.write(self.plan_path, self.plan)
        self.runtime['groupPlanSha256'] = m.sha(self.plan_path.read_bytes()); self.runtime['scriptResolutionEvidenceSha256'] = m.sha(path.read_bytes())
        self.runtime['scriptResolutions'][30].update(guid='f' * 32, originalGuid='f' * 32); self.write(self.runtime_path, self.runtime)
        with self.assertRaisesRegex(ValueError, 'negative cases'): self.run_tool()

    def test_recovered_runtime_class_cannot_enter_missing_evidence(self):
        evidence = json.loads(Path(self.plan['missingEvidence']['path']).read_bytes())
        path = Path(evidence['validationSnapshot']['path']); j = json.loads(path.read_bytes()); j['issues'][0]['detail'] = 'guid:f9dfa5b682dcd46bda6128250e975f58; fileID:11500000'; self.write(path, j)
        with self.assertRaisesRegex(ValueError, 'evidence changed'): self.run_tool()

    def test_source_drift_and_existing_destination_refuse(self):
        relative = next(iter(self.paths)); (self.stage / relative).write_bytes(b'foreign change')
        with self.assertRaisesRegex(ValueError, 'canonical/plan'): self.run_tool()

    def test_unrelated_outgoing_asset_in_graph_refuses(self):
        graph_path = self.work / 'optional-demo-incoming-consumers.json'; graph = json.loads(graph_path.read_bytes()); graph['incomingClosureAssets'].append({'path': m.ROOT + '/004-fixture/Keep.txt'}); self.write(graph_path, graph)
        self.plan['sourceIncomingGraph']['sha256'] = m.sha(graph_path.read_bytes()); self.write(self.plan_path, self.plan)
        with self.assertRaisesRegex(ValueError, 'closure'): self.run_tool()

    def test_move_failure_restores_exact_inputs(self):
        before = self.manifest_path.read_bytes(); rename = m.os.rename; calls = 0
        def fail(a, b):
            nonlocal calls
            calls += 1
            if calls == 3: raise OSError('fixture move failure')
            return rename(a, b)
        with mock.patch.object(m.os, 'rename', side_effect=fail):
            with self.assertRaisesRegex(OSError, 'move failure'): self.run_tool(True)
        self.assertEqual(before, self.manifest_path.read_bytes()); self.assertTrue(all((self.stage / p).exists() for p in self.paths))

    def test_installer_independently_replays_optional_transaction_and_refuses_tampering(self):
        installer = load('optional_install_replay', 'install-unity-asset-library.py')
        report, _ = self.run_tool(True); current = json.loads(self.manifest_path.read_bytes())
        validation = {'completedUtc': '2099-01-01T00:00:00Z'}
        accepted, original = installer.validate_group_source_only(self.project, self.stage, current, validation, current['sourceOnlyHistory'][-1])
        self.assertEqual(98, accepted['files']); self.assertEqual(self.manifest, original)
        row = report['files'][0]; Path(row['destination']).write_bytes(b'foreign change')
        with self.assertRaisesRegex(ValueError, 'SHA/bytes'): installer.validate_group_source_only(self.project, self.stage, current, validation, current['sourceOnlyHistory'][-1])

    def test_installer_refuses_unknown_or_reordered_third_history(self):
        installer = load('optional_install_history_replay', 'install-unity-asset-library.py')
        self.run_tool(True); current = json.loads(self.manifest_path.read_bytes())
        with self.assertRaisesRegex(ValueError, 'exact immutable'): installer.validate_source_only(self.project, self.stage, current, {'completedUtc': '2099-01-01T00:00:00Z'})


if __name__ == '__main__': unittest.main()
