"""CPU-only fault fixtures. All writes are confined to TemporaryDirectory.

No Unity, GPU probe, model, real lease, project or scheduling operation is run.
"""
from __future__ import annotations
import csv
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch
from PIL import Image

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
spec = importlib.util.spec_from_file_location('native_recovery_under_test', HERE/'run-first-native.py')
driver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(driver)
Worker = driver.SingleWorker


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='yamyam-native-recovery-cpu-')
        self.base = Path(self.temp.name)
        root = self.base/'repo'
        topic = self.base/'topic'
        self.globals = patch.multiple(driver, ROOT=root, HERE=root/'batch', MEDIA=self.base/'media',
            PROJECT=self.base/'capture', TOPIC_MEDIA=topic, OUTPUT=topic/'native-v1', ATTEMPTS=topic/'native-attempts',
            STATE=self.base/'progress.json', WORKER=self.base/'worker.json', LEASE=self.base/'gpu.json')
        self.globals.start()
        self.prov = driver.fingerprint([dict(source='fixture.cs', target='fixture.cs', sha256='a'*64)], '6000.6.0f1')
        self.template = self.base/'black-fixture.jpg'
        Image.new('RGB', (1920, 1080), 'black').save(self.template)

    def tearDown(self):
        self.globals.stop()
        self.temp.cleanup()

    def mode(self, output, mode, fp=None):
        folder = output/mode
        folder.mkdir(parents=True)
        fp = fp or self.prov['fingerprint']
        driver.save(folder/'mode-complete.json', dict(fingerprint=fp, mode=mode,
            **{k: driver.CONTRACT[k] for k in ('frames', 'width', 'height', 'fps', 'cameras')}))
        with (folder/'trace.csv').open('w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['frame', 'width', 'sideClearance', 'playerDiameter', 'commandX',
                'commandZ', 'playerX', 'playerZ', 'travelled', 'blocked'])
            writer.writeheader()
            for n in range(270):
                distance = min(n*.03, 1.3) if mode == 'narrow' else n*.03
                writer.writerow(dict(frame=n, width=2.5 if mode == 'narrow' else 3.5, sideClearance=.5 if mode == 'narrow' else 1,
                    playerDiameter=.72, commandX=1.08 if n<48 else 0, commandZ=1.44 if n<48 else 1.8,
                    playerX=.855, playerZ=-2.85+distance, travelled=distance, blocked=int(mode=='narrow' and n>60)))
        for view in driver.CONTRACT['cameras']:
            (folder/view).mkdir()
            for n in range(270):
                driver.link_or_copy(self.template, folder/view/f'{n:04}.jpg')
        return folder

    def full(self):
        output = driver.stage_attempt(self.prov, {})
        for mode in driver.CONTRACT['modes']:
            self.mode(output, mode)
        return output

    def scene_files(self):
        source = driver.PROJECT/'Assets/VideoScenes/architectural-111-20261106'
        (source/'03-02').mkdir(parents=True)
        for name in ('02-narrow.unity', '04-wide.unity'):
            (source/'03-02'/name).write_text('CPU fixture, not a Unity scene render', encoding='utf-8')
            (source/'03-02'/(name+'.meta')).write_text('fixture metadata', encoding='utf-8')
        driver.save(driver.HERE/'first-unity-preparation.json', {'unrelated': 'keep'})
        project = driver.ROOT/'projects/shorts-leveldesign-03-02'
        driver.save(project/'project.json', {'unrelated': 'keep', 'humanApproval': False})
        driver.save(project/'checkpoint.json', {'unrelated': 'keep', 'completedStages': []})

    def run_fake_main(self, **patches):
        from contextlib import ExitStack
        with ExitStack() as stack:
            stack.enter_context(patch.object(sys, 'argv', ['run-first-native.py', '--execute', '--wait-hours', '0']))
            stack.enter_context(patch.object(driver, 'authorize', return_value=self.prov))
            stack.enter_context(patch.object(driver, 'SingleWorker', side_effect=lambda: Worker(driver.WORKER)))
            stack.enter_context(patch.object(driver.subprocess, 'check_output', side_effect=AssertionError('GPU/process probes forbidden in CPU fixtures')))
            if not isinstance(driver.subprocess.Popen, Mock):
                stack.enter_context(patch.object(driver.subprocess, 'Popen', side_effect=AssertionError('Native process launch forbidden in CPU fixtures')))
            for name, replacement in patches.items():
                stack.enter_context(patch.object(driver, name, replacement))
            driver.main()

    def test_fingerprint_changes_with_original_metadata_or_unity_version(self):
        a = driver.fingerprint([{'source': 'x.meta', 'sha256': 'a'}], '6000.6.0f1')['fingerprint']
        self.assertNotEqual(a, driver.fingerprint([{'source': 'x.meta', 'sha256': 'b'}], '6000.6.0f1')['fingerprint'])
        self.assertNotEqual(a, driver.fingerprint([{'source': 'x.meta', 'sha256': 'a'}], 'different')['fingerprint'])

    def test_authorization_keeps_original_metadata_pinned_but_allows_import_reserialization(self):
        catalog = driver.ROOT/'catalog.txt'; catalog.parent.mkdir(parents=True); catalog.write_text('111 fixture topics')
        driver.save(driver.ROOT/'shared/publishing/video-production-control.json', {driver.AUTH_KEY: dict(
            userEvidence='111개 전체 제작 들어가줘', status='preproduction-in-progress',
            automaticAdvanceWithinExactList=True, automaticAdvanceOutsideList=False,
            humanFinalReviewRequired=True, youtubeAuthorized=False)})
        projects = [dict(topicId='03.02', slug='shorts-leveldesign-03-02')]+[dict(topicId='fixture', slug='fixture')]*110
        driver.save(driver.HERE/'batch.json', dict(localFinalReviewOnly=True, projects=projects,
                    sourceCatalog='catalog.txt', sourceCatalogSHA256=driver.sha(catalog)))
        code = driver.HERE/'unity-source/Fixture.cs'; code.parent.mkdir(parents=True); code.write_text('// source fixture')
        meta = code.with_suffix('.cs.meta'); meta.write_text('original metadata')
        inputs = []
        for source in (code, meta):
            target = 'Assets/'+source.name; dest = driver.PROJECT/target
            dest.parent.mkdir(parents=True, exist_ok=True); dest.write_bytes(source.read_bytes())
            inputs.append(dict(source=source.relative_to(driver.ROOT).as_posix(), target=target, sha256=driver.sha(source)))
        driver.save(driver.HERE/'first-unity-preparation.json', dict(editorVersion='6000.6.0f1', files=inputs))
        driver.save(driver.HERE/'first-unity-compiler-preflight.json', dict(compilerExitCode=0,
                    sourceHashes={'unity-source/Fixture.cs': driver.sha(code)}))
        first = driver.authorize()['fingerprint']
        (driver.PROJECT/'Assets/Fixture.cs.meta').write_text('Unity import reserialized metadata')
        self.assertEqual(first, driver.authorize()['fingerprint'])
        meta.write_text('changed original provenance')
        with self.assertRaises(AssertionError): driver.authorize()

    def test_complete_receipts_recover_without_state_or_completion_marker(self):
        output = self.full()
        self.scene_files()
        def forbidden(*args, **kwargs):
            self.fail('CPU recovery must not probe GPU or launch Unity')
        with patch.object(driver.subprocess, 'Popen', side_effect=forbidden):
            self.run_fake_main(busy_reason=forbidden)
        state = driver.read(driver.STATE)
        self.assertEqual(state['status'], 'native-complete-review-pending')
        self.assertFalse(state['gpuStarted'])
        self.assertFalse(state['finalMovieComplete'])
        self.assertTrue((output/'capture-complete.txt').exists())
        checkpoint = driver.read(driver.ROOT/'projects/shorts-leveldesign-03-02/checkpoint.json')
        self.assertEqual(len(checkpoint['editableUnityScenesSaved']), 2)
        self.assertFalse(checkpoint['finalOutputsVerified'])
        self.assertEqual(checkpoint['unrelated'], 'keep')

    def test_partial_success_is_reused_in_new_attempt_without_touching_failed_mode(self):
        old = driver.stage_attempt(self.prov, {})
        self.mode(old, 'narrow')
        (old/'wide').mkdir(); (old/'wide/partial.jpg').write_bytes(b'failed mode retained')
        digest = driver.sha(old/'narrow/trace.csv')
        complete, reusable = driver.scan_attempts(self.prov)
        self.assertIsNone(complete)
        self.assertEqual(set(reusable), {'narrow'})
        new = driver.stage_attempt(self.prov, reusable)
        self.assertNotEqual(new, old)
        self.assertEqual(driver.sha(new/'narrow/trace.csv'), digest)
        self.assertFalse((new/'wide').exists())
        self.assertEqual((old/'wide/partial.jpg').read_bytes(), b'failed mode retained')
        self.assertIn('narrow', driver.read(new/'attempt.json')['reusedModes'])

    def test_other_fingerprint_is_never_reused(self):
        self.full()
        other = driver.fingerprint([{'source': 'changed', 'sha256': 'b'}], '6000.6.0f1')
        self.assertEqual(driver.scan_attempts(other), (None, {}))

    def test_missing_frame_and_wrong_receipt_are_rejected(self):
        output = driver.stage_attempt(self.prov, {}); folder = self.mode(output, 'narrow')
        (folder/'top/0160.jpg').unlink()
        with self.assertRaises(ValueError): driver.check_mode(output, 'narrow', self.prov['fingerprint'])
        driver.link_or_copy(self.template, folder/'top/0160.jpg')
        rec = driver.read(folder/'mode-complete.json'); rec['width'] = 1280
        driver.save(folder/'mode-complete.json', rec)
        with self.assertRaises(ValueError): driver.check_mode(output, 'narrow', self.prov['fingerprint'])

    def test_different_input_streams_are_rejected(self):
        output = self.full(); path = output/'wide/trace.csv'
        text = path.read_text(encoding='utf-8'); path.write_text(text.replace(',1.08,1.44,', ',1.07,1.44,', 1), encoding='utf-8')
        with self.assertRaises(ValueError): driver.check_capture(output, self.prov['fingerprint'])

    def test_singleton_guard_blocks_second_worker(self):
        first = Worker(driver.WORKER).acquire()
        try:
            with self.assertRaises(RuntimeError): Worker(driver.WORKER).acquire()
        finally: first.close()
        self.assertFalse(driver.WORKER.exists())

    def test_dead_owned_worker_is_archived_but_live_child_blocks_reclamation(self):
        rec = dict(protocol=driver.PROTOCOL, owner=driver.OWNER, token='old', pid=999999999, createTime=1, child={'pid': 2, 'createTime': 1})
        driver.save(driver.WORKER, rec)
        with self.assertRaises(RuntimeError): Worker(driver.WORKER, is_alive=lambda r: bool(r and r.get('pid')==2)).acquire()
        self.assertEqual(driver.read(driver.WORKER), rec)
        worker = Worker(driver.WORKER, is_alive=lambda r: False).acquire()
        self.assertEqual(worker.previous['token'], 'old'); worker.close()
        self.assertTrue(list((driver.WORKER.parent/'native-recovery-history').glob('*.json')))

    def test_foreign_unknown_and_live_child_leases_are_preserved(self):
        driver.save(driver.LEASE, ['unknown schema'])
        self.assertFalse(driver.recover_own_lease({'foreign'}, is_alive=lambda r: False))
        driver.save(driver.LEASE, {'project': 'foreign-math', 'token': 'foreign'})
        self.assertFalse(driver.recover_own_lease({'foreign'}, is_alive=lambda r: False))
        self.assertTrue(driver.LEASE.exists())
        rec = dict(protocol=driver.PROTOCOL, owner=driver.OWNER, token='own', pid=1, createTime=1, child={'pid': 2, 'createTime': 1}, phase='running')
        driver.save(driver.LEASE, rec)
        self.assertFalse(driver.recover_own_lease({'wrong'}, is_alive=lambda r: False))
        self.assertFalse(driver.recover_own_lease({'own'}, is_alive=lambda r: bool(r and r.get('pid')==2)))
        self.assertTrue(driver.recover_own_lease({'own'}, is_alive=lambda r: False))
        self.assertFalse(driver.LEASE.exists())

    def test_launch_gap_lease_is_not_reclaimed_with_unrecorded_live_child(self):
        driver.save(driver.LEASE, dict(protocol=driver.PROTOCOL, owner=driver.OWNER, token='own', pid=1,
            createTime=1, child=None, phase='launching'))
        self.assertFalse(driver.recover_own_lease({'own'}, is_alive=lambda r: False, unrecorded=lambda r: True))
        self.assertTrue(driver.recover_own_lease({'own'}, is_alive=lambda r: False, unrecorded=lambda r: False))

    def test_interrupt_retains_owned_lease_and_child_identity(self):
        class FakeChild:
            pid = 999999999
            def wait(self): raise KeyboardInterrupt('CPU fixture interruption')
            def poll(self): return None
        actual_identity = driver.identity
        with patch.object(driver.subprocess, 'Popen', return_value=FakeChild()):
            with self.assertRaises(KeyboardInterrupt):
                self.run_fake_main(busy_reason=lambda *a: None,
                    identity=lambda pid=None: {'pid': FakeChild.pid, 'createTime': 123} if pid else actual_identity())
        lease = driver.read(driver.LEASE); state = driver.read(driver.STATE)
        self.assertEqual(lease['token'], state['leaseToken'])
        self.assertEqual(lease['child']['pid'], FakeChild.pid)
        self.assertEqual(state['status'], 'worker-yielded-child-still-running')
        self.assertTrue(driver.WORKER.exists())

    def test_known_recovery_tokens_survive_a_resource_wait_timeout(self):
        driver.save(driver.STATE, dict(pid=999999999, createTime=1, leaseToken='proven-old-lease'))
        with self.assertRaises(RuntimeError):
            self.run_fake_main(busy_reason=lambda *a: 'still occupied', recover_own_lease=lambda *a: False)
        state = driver.read(driver.STATE)
        self.assertEqual(state['recoverableLeaseTokens'], ['proven-old-lease'])
        observed = []
        def preserve(tokens):
            observed.append(set(tokens)); return False
        with self.assertRaises(RuntimeError):
            self.run_fake_main(busy_reason=lambda *a: 'still occupied', recover_own_lease=preserve)
        self.assertTrue(observed)
        self.assertTrue(all('proven-old-lease' in tokens for tokens in observed))

    def test_export_conflict_preserves_capture_then_cpu_resume_finishes(self):
        output = self.full(); self.scene_files()
        target = driver.ROOT/'unity/VideoEditing/Assets/VideoScenes/architectural-111-20261106/03-02/02-narrow.unity'
        target.parent.mkdir(parents=True); target.write_text('different prior scene', encoding='utf-8')
        def forbidden(*a, **k): self.fail('Export recovery must never launch or probe GPU')
        with patch.object(driver.subprocess, 'Popen', side_effect=forbidden):
            with self.assertRaises(RuntimeError): self.run_fake_main(busy_reason=forbidden)
            self.assertEqual(target.read_text(encoding='utf-8'), 'different prior scene')
            self.assertIsNotNone(driver.scan_attempts(self.prov)[0])
            target.unlink()  # Resolve only the isolated fixture conflict.
            self.run_fake_main(busy_reason=forbidden)
        self.assertTrue(driver.read(driver.STATE)['completed'])
        self.assertEqual(driver.read(driver.STATE)['output'], str(output))

    def test_concurrent_unrelated_record_addition_is_preserved(self):
        path = self.base/'record.json'; driver.save(path, {'unrelated': 'initial'})
        first = [True]
        def change(value):
            if first[0]:
                first[0] = False; concurrent = driver.read(path); concurrent['anotherTask'] = 'keep'; driver.save(path, concurrent)
            value['native'] = True
        driver.update_json(path, change)
        self.assertEqual(driver.read(path), {'unrelated': 'initial', 'anotherTask': 'keep', 'native': True})

    def test_later_final_movie_review_and_platform_states_survive_repeat_export(self):
        output = self.full(); self.scene_files()
        project = driver.ROOT/'projects/shorts-leveldesign-03-02'
        advanced = dict(fingerprint=self.prov['fingerprint'], visualReviewPending=False,
                        fullRealTimeReview=True, humanApproval=True, finalMovieComplete=True)
        driver.save(project/'project.json', dict(status='published-final-reviewed', finalMovieComplete=True,
            humanApproval=True, platformStatus='scheduled', nativeCapture=advanced))
        driver.save(project/'checkpoint.json', dict(stage='local-final-reviewed', completedStages=['captioned-master'],
            finalMovieComplete=True, finalOutputsVerified=True, humanReview='approved', platformActions=['scheduled'],
            editableUnityScenesSaved=['later-extra-scene.unity'], nativeCapture=advanced))
        driver.verify_export(output, self.prov)
        p = driver.read(project/'project.json'); c = driver.read(project/'checkpoint.json')
        self.assertEqual(p['status'], 'published-final-reviewed')
        self.assertTrue(p['finalMovieComplete']); self.assertTrue(p['humanApproval'])
        self.assertEqual(p['platformStatus'], 'scheduled')
        self.assertEqual(c['stage'], 'local-final-reviewed')
        self.assertTrue(c['finalOutputsVerified']); self.assertTrue(c['finalMovieComplete'])
        self.assertEqual(c['humanReview'], 'approved'); self.assertEqual(c['platformActions'], ['scheduled'])
        self.assertIn('later-extra-scene.unity', c['editableUnityScenesSaved'])
        self.assertFalse(c['nativeCapture']['visualReviewPending'])
        self.assertTrue(c['nativeCapture']['fullRealTimeReview'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
