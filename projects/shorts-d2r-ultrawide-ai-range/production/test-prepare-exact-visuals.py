"""Synthetic preservation checks; no real media, FFmpeg, TTS or render jobs."""
from pathlib import Path
import hashlib
import importlib.util
import json
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace
from PIL import Image

SOURCE = Path(__file__).with_name('prepare-exact-visuals.py')
SPEC = importlib.util.spec_from_file_location('exact_visuals', SOURCE)
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


class Preservation(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='diablo-frame-test-')
        self.root = Path(self.temp.name)
        self.addCleanup(self.temp.cleanup)

    def extract(self, directory, count=3):
        for index in range(count):
            Image.new('RGB', (8, 8), (index * 30, 0, 0)).save(directory / f'{index:05d}.jpg')

    def test_exact_receipt_reuses_without_extraction(self):
        inputs = {'voice': 'a', 'captions': 'b', 'source': 'c', 'builder': 'd'}
        directory, receipt, reused = M.ensure_frames(self.root, inputs, 3, (8, 8), self.extract)
        self.assertFalse(reused)
        before = {p.name: p.read_bytes() for p in directory.iterdir()}
        directory2, receipt2, reused = M.ensure_frames(self.root, inputs, 3, (8, 8), lambda _: self.fail('Unexpected extraction'))
        self.assertTrue(reused)
        self.assertEqual((directory, receipt), (directory2, receipt2))
        self.assertEqual(before, {p.name: p.read_bytes() for p in directory.iterdir()})

    def test_each_input_change_preserves_success(self):
        inputs = {'voice': 'a', 'captions': 'b', 'source': 'c', 'builder': 'd'}
        original, _, _ = M.ensure_frames(self.root, inputs, 3, (8, 8), self.extract)
        original_hash = M.sha(original / '00000.jpg')
        for key in inputs:
            new, _, reused = M.ensure_frames(self.root, dict(inputs, **{key: 'changed'}), 3, (8, 8), self.extract)
            self.assertFalse(reused)
            self.assertNotEqual(new.parent.parent, original.parent.parent)
            self.assertEqual(M.sha(original / '00000.jpg'), original_hash)

    def test_partial_attempt_is_preserved_and_retry_is_new(self):
        def fail(directory):
            self.extract(directory, 1)
            raise RuntimeError('Synthetic interruption')
        with self.assertRaises(RuntimeError):
            M.ensure_frames(self.root, {'voice': 'a'}, 3, (8, 8), fail)
        partial = next(self.root.glob('*/attempt-0001/game'))
        previous = (partial / '00000.jpg').read_bytes()
        complete, _, _ = M.ensure_frames(self.root, {'voice': 'a'}, 3, (8, 8), self.extract)
        self.assertEqual(complete.parent.name, 'attempt-0002')
        self.assertEqual((partial / '00000.jpg').read_bytes(), previous)
        self.assertFalse((partial.parent / 'receipt.json').exists())

    def test_missing_middle_extra_file_and_hash_mismatch_prevent_reuse(self):
        for case in ['missing-middle', 'extra-file', 'changed-frame', 'wrong-receipt']:
            base = self.root / case
            old, _, _ = M.ensure_frames(base, {'voice': 'a'}, 3, (8, 8), self.extract)
            if case == 'missing-middle':
                (old / '00001.jpg').rename(old.parent / 'preserved-middle.jpg')
            elif case == 'extra-file':
                (old / 'extra.txt').write_text('unexpected')
            elif case == 'changed-frame':
                Image.new('RGB', (8, 8), 'green').save(old / '00001.jpg')
            else:
                receipt = M.read(old.parent / 'receipt.json')
                receipt['frames'] = 4
                (old.parent / 'receipt.json').write_bytes(M.encoded(receipt))
            saved = {p.name: p.read_bytes() for p in old.iterdir()}
            new, _, reused = M.ensure_frames(base, {'voice': 'a'}, 3, (8, 8), self.extract)
            self.assertFalse(reused)
            self.assertNotEqual(old, new)
            self.assertEqual(saved, {p.name: p.read_bytes() for p in old.iterdir()})

    def test_short_extraction_never_gets_success_receipt(self):
        with self.assertRaises(RuntimeError):
            M.ensure_frames(self.root, {'voice': 'a'}, 3, (8, 8), lambda p: self.extract(p, 2))
        self.assertEqual(list(self.root.glob('*/attempt-*/receipt.json')), [])

    def test_timing_snapshot_keeps_exact_bytes_and_idempotent_pointer(self):
        destination = self.root / 'visual-timing.json'
        old = b'{"state":"previous"}\r\n'
        destination.write_bytes(old)
        history = self.root / 'history'
        M.publish_preserving(destination, {'state': 'current'}, history)
        self.assertEqual((history / (hashlib.sha256(old).hexdigest() + '.json')).read_bytes(), old)
        timestamp = destination.stat().st_mtime_ns
        M.publish_preserving(destination, {'state': 'current'}, history)
        self.assertEqual(destination.stat().st_mtime_ns, timestamp)
        self.assertEqual(len(list(history.iterdir())), 1)

    def test_synthetic_main_publishes_frame_root_and_reuses(self):
        project = self.root / 'projects' / M.SLUGS['grass']
        def save(path, value):
            M.write_new(path, M.encoded(value))
        save(self.root / 'shared/publishing/video-production-control.json', {'scopedBatchAuthorizations': {'explicit-ten-distinctive-shorts-20261025': {'status': 'active', 'fullProductionAuthorized': True, 'slugs': [project.name]}}})
        save(project / 'planning/production-plan.json', {'scriptFinalized': True, 'independentFootageViewed': True})
        narration = project / 'script/narration.spoken.ko.json'
        save(narration, {'synthetic': True})
        pcm = project / 'production/local/audio-v1/voice/narration.wav'
        M.write_new(pcm, b'synthetic PCM fixture; no real speech')
        save(pcm.with_suffix('.timing.json'), {'voiceSha256': M.sha(pcm), 'entries': [{'start': i * .1} for i in range(6)]})
        save(project / 'script/captions.json', {'revision': 'distinctive-ten-v1', 'timingInputs': {'narrationSha256': M.sha(narration), 'voiceSha256': M.sha(pcm)}, 'voiceOffsetSeconds': .2, 'frames': 60, 'durationSeconds': 1, 'cues': [{'id': 'p3-2', 'start': .4, 'end': .5}, {'id': 'p6-1', 'start': .7, 'end': .9}]})
        save(project / 'production/section-plan.json', [{'id': str(i), 'kind': 'game' if i == 0 else 'illustration'} for i in range(6)])
        source = self.root / 'synthetic-source.mp4'
        M.write_new(source, b'synthetic source fixture; no game')
        save(project / 'sources/selected-footage.json', {'sources': [{'source': {'path': source.name, 'sha256': M.sha(source), 'width': 1920, 'height': 1080}, 'sourceStart': 0, 'availableUntil': 1}]})
        save(project / 'production/scene-config.json', {'footageReady': False})
        old = b'{"previewOnly":true}\r\n'
        for path in [project / 'production/visual-timing.json', project / 'production/local/visual-timing.json']:
            M.write_new(path, old)
        calls = []
        def fake_run(command, **_):
            if command == ['ffmpeg', '-version']:
                return SimpleNamespace(stdout='synthetic decoder\n')
            self.assertIn('-n', command)
            self.assertNotIn('-y', command)
            calls.append(command)
            start, count = int(command[command.index('-start_number') + 1]), int(command[command.index('-frames:v') + 1])
            for index in range(start, start + count):
                Image.new('RGB', (1920, 1080), 'black').save(Path(command[-1].replace('%05d', f'{index:05d}')))
            return SimpleNamespace(returncode=0)
        with patch.object(M, 'ROOT', self.root), patch('sys.argv', [str(SOURCE), 'grass']), patch.object(M.subprocess, 'run', fake_run):
            M.main()
            timing = M.read(project / 'production/local/visual-timing.json')
            self.assertEqual(timing['frameRoot'], (self.root / timing['frameRoot']).relative_to(self.root).as_posix())
            self.assertTrue((self.root / timing['frameReceipt']).exists())
            self.assertEqual(len(list((self.root / timing['frameRoot']).glob('*.jpg'))), 18)
            self.assertEqual((project / 'production/local/visual-timing-history' / (hashlib.sha256(old).hexdigest() + '.json')).read_bytes(), old)
            M.main()
            self.assertEqual(len(calls), 1)


if __name__ == '__main__':
    unittest.main()
