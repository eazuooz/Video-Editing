"""Small temporary exact-failure recovery fixtures; never loads Unity."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

spec = importlib.util.spec_from_file_location('terrain_recovery', Path(__file__).with_name('recover-unity-terrain-normalization.py'))
tool = importlib.util.module_from_spec(spec); spec.loader.exec_module(tool)


class RecoveryFixtures(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='terrain-recovery-'); self.project = Path(self.temp.name) / 'Unity'
        self.work = self.project / 'Library/YamyamAssetLibrary'; self.headless = self.work / 'headless-project'; self.stage = self.headless / tool.ROOT
        self.stage.mkdir(parents=True); self.failed = self.headless / 'Library/YamyamAssetLibrary/terrain-normalization/failed'; self.failed.mkdir(parents=True)
        self.manifest_path = self.work / 'staging-manifest.json'; self.report_path = self.headless / 'Library/YamyamAssetLibrary/terrain-normalization-report.json'
        self.product = {'id': '033', 'folder': '033-fixture', 'status': 'complete', 'files': []}
        products = [self.product] + [{'id': f'{i:03d}', 'folder': f'{i:03d}-fixture', 'status': 'complete', 'files': []} for i in range(84) if i != 33]
        self.terrains, self.layers = [], []; self.before_files = {}; self.current_files = {}
        old_guid = lambda n: f'{1000+n:032x}'
        self.old_guid, self.new_guid = old_guid(0), 'f' * 32
        for index, name in enumerate(['New Terrain 1.asset', 'New Terrain 13.asset'] + [f'Other{n}.asset' for n in range(28)]):
            path = tool.ROOT + '/033-fixture/Terrain/' + name; before = ('native-original-' + name).encode(); current = ('native-saved-' + name).encode() if index < 2 else before
            meta = ('fileFormatVersion: 2\nguid: ' + f'{2000+index:032x}' + '\n').encode(); self.put(path, current); self.put(path + '.meta', meta)
            self.before_files[path], self.before_files[path + '.meta'] = before, meta
            for suffix, raw in [('', before), ('.meta', meta)]:
                self.product['files'].append({'path': path[len(tool.ROOT)+1:] + suffix, 'bytes': len(raw), 'sha256': tool.sha(raw)})
            state = {'asset': {'guid': f'{2000+index:032x}'}, 'heightSha256': 'same-height', 'layers': [{'asset': {'guid': old_guid(index % 10), 'localId': 8574412962073106934}}]}
            after = copy.deepcopy(state)
            if index == 0: after['layers'][0]['asset']['guid'] = self.new_guid
            row = {'productId': '033', 'path': path, 'payloadBeforeSha256': tool.sha(before), 'payloadAfterSha256': tool.sha(current) if index < 2 else '',
                   'saveStarted': index < 2, 'saved': index < 2, 'backup': str(self.failed / 'backups' / path) if index < 2 else '', 'before': state, 'after': after if index < 2 else None,
                   'beforeSemanticSha256': 'equal', 'afterSemanticSha256': 'different' if index == 0 else 'equal'}
            if index < 2:
                self.write(self.failed / 'backups' / path, before); self.write(Path(str(self.failed / 'backups' / path) + '.meta'), meta)
            self.terrains.append(row)
        for index in range(25):
            source = tool.GENERATED + f'/layer{index}.terrainlayer'; destination = tool.ROOT + f'/033-fixture/Generated/TerrainLayers/layer{index}.terrainlayer'
            raw = ('%YAML 1.1\nlayer: ' + str(index) + '\n').encode(); meta = ('fileFormatVersion: 2\nguid: ' + old_guid(index) + '\n').encode(); moved = index < 10
            row = {'path': source, 'destination': destination if moved else '', 'guid': old_guid(index), 'assignedProductId': '033', 'payloadSha256': tool.sha(raw), 'metadataSha256': tool.sha(meta), 'moveStarted': moved, 'moved': moved, 'orphan': not moved}
            self.layers.append(row)
            self.before_files[source], self.before_files[source + '.meta'] = raw, meta
            if moved:
                self.put(destination, raw); self.put(destination + '.meta', meta)
                self.write(self.failed / 'backups' / source, raw); self.write(Path(str(self.failed / 'backups' / source) + '.meta'), meta)
                if index == 0:
                    self.put(source, raw); self.put(source + '.meta', meta.replace(old_guid(index).encode(), self.new_guid.encode()))
            else: self.put(source, raw); self.put(source + '.meta', meta)
        self.manifest = {'stageRoot': str(self.stage), 'products': products}; self.manifest_path.write_bytes(tool.encoded(self.manifest))
        self.report = {'runDirectory': str(self.failed), 'status': 'failed', 'apply': True, 'scenesOpened': False, 'originalArchivesModified': False, 'observedUnityErrors': 0,
                       'manifestSha256': tool.sha(self.manifest_path.read_bytes()), 'errors': ['System.IO.InvalidDataException: Terrain semantic state changed after native persistence: ' + self.terrains[0]['path']], 'terrains': self.terrains, 'layers': self.layers}
        self.save_report(); self.patch = mock.patch.object(tool, 'EXPECTED_PROJECT', self.project); self.patch.start()
        self.snapshot = self.snapshot_current()

    def tearDown(self): self.patch.stop(); self.temp.cleanup()
    def write(self, path, raw): path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(raw)
    def put(self, relative, raw): self.write(self.headless / relative, raw)
    def save_report(self):
        raw = tool.encoded(self.report); self.report_path.write_bytes(raw); (self.failed / 'report.json').write_bytes(raw)
    def snapshot_current(self): return {p: p.read_bytes() for p in self.headless.rglob('*') if p.is_file() and 'Library' not in p.relative_to(self.headless).parts}
    def call(self, apply=False):
        *_, plan = tool.prepare(self.project)
        return tool.recover(self.project, apply=apply, editor_stopped=apply, expected_manifest=tool.sha(self.manifest_path.read_bytes()), expected_report=tool.sha(self.report_path.read_bytes()), expected_plan=tool.sha(tool.encoded(plan)))

    def test_default_dryrun_leaves_all_actual_asset_bytes(self):
        result, _ = self.call(); self.assertEqual('dry-run-ready', result['status']); self.assertEqual(self.snapshot, self.snapshot_current())

    def test_exact_recovery_restores_two_native_sources_ten_layers_and_preserves_fresh(self):
        canonical = self.manifest_path.read_bytes(); result, report = self.call(True); self.assertEqual('complete', result['status'])
        for relative, raw in self.before_files.items(): self.assertEqual(raw, (self.headless / relative).read_bytes())
        for layer in self.layers[:10]: self.assertFalse((self.headless / layer['destination']).exists())
        fresh = report.parent / 'retired-fresh-duplicate' / (self.layers[0]['path'] + '.meta'); self.assertEqual(self.new_guid, tool.guid(fresh)); self.assertEqual(canonical, self.manifest_path.read_bytes())

    def test_failure_during_partial_layer_moves_rolls_back_exact_current_bytes(self):
        original = tool.os.rename; calls = 0
        def fail(source, destination):
            nonlocal calls
            calls += 1
            if calls == 5: raise OSError('synthetic layer move failure')
            return original(source, destination)
        with mock.patch.object(tool.os, 'rename', side_effect=fail):
            with self.assertRaisesRegex(OSError, 'move failure'): self.call(True)
        self.assertEqual(self.snapshot, self.snapshot_current())

    def test_native_restore_write_failure_rolls_back_layers_and_prior_native_write(self):
        original = tool.atomic; calls = 0
        def fail(path, raw):
            nonlocal calls
            if Path(path) in [self.headless / t['path'] for t in self.terrains[:2]]:
                calls += 1
                if calls == 2: raise OSError('synthetic native write failure')
            return original(path, raw)
        with mock.patch.object(tool, 'atomic', side_effect=fail):
            with self.assertRaisesRegex(OSError, 'write failure'): self.call(True)
        self.assertEqual(self.snapshot, self.snapshot_current())

    def test_unexpected_semantic_or_foreign_duplicate_changes_refuse(self):
        self.report['terrains'][0]['after']['heightSha256'] = 'changed'; self.save_report()
        with self.assertRaisesRegex(ValueError, 'more than'): self.call()
        self.report['terrains'][0]['after']['heightSha256'] = 'same-height'; self.save_report()
        (self.headless / self.layers[0]['path']).write_bytes(b'foreign-byte-change')
        with self.assertRaisesRegex(ValueError, 'fresh duplicate'): self.call()

    def test_apply_requires_reviewed_hashes_and_changed_third_native_is_refused(self):
        with self.assertRaisesRegex(ValueError, 'three exact reviewed'): tool.recover(self.project, apply=True)
        (self.headless / self.terrains[2]['path']).write_bytes(b'unjournaled-native-change')
        with self.assertRaisesRegex(ValueError, 'third TerrainData'): self.call()

    def test_foreign_change_between_prepare_and_capture_is_preserved_and_refused(self):
        _, _, _, manifest_raw, report_raw, plan = tool.prepare(self.project)
        actual_prepare = tool.prepare
        for relative in [self.terrains[0]['path'], self.layers[0]['destination'] + '.meta', self.layers[0]['path']]:
            path = self.headless / relative; before = path.read_bytes()
            def drift(*args, **kwargs):
                prepared = actual_prepare(*args, **kwargs)
                path.write_bytes(b'foreign-after-reviewed-plan')
                return prepared
            with mock.patch.object(tool, 'prepare', side_effect=drift):
                with self.assertRaisesRegex(ValueError, 'reviewed plan before capture'):
                    tool.recover(self.project, apply=True, editor_stopped=True, expected_manifest=tool.sha(manifest_raw), expected_report=tool.sha(report_raw), expected_plan=tool.sha(tool.encoded(plan)))
            self.assertEqual(b'foreign-after-reviewed-plan', path.read_bytes())
            for previous, raw in self.snapshot.items():
                if previous != path: self.assertEqual(raw, previous.read_bytes())
            path.write_bytes(before)


if __name__ == '__main__': unittest.main()
