"""Pure synthetic annotation mapping tests. No footage generation or GPU access."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('prepare_visual', Path(__file__).with_name('prepare-visual.py'))
module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)


class SourceAnnotationTests(unittest.TestCase):
    def source(self):
        return {'original': {'decodedDurationSeconds': 80, 'sourceSHA256': 'synthetic-test-sha'}}

    def mark(self):
        return {'start': 10, 'end': 18, 'label': 'synthetic fixture', 'kind': 'ellipse',
                'labelCenter': [300, 100], 'keyframes': [
                    {'at': 10, 'center': [100, 200], 'size': [40, 60]},
                    {'at': 14, 'center': [140, 240], 'size': [80, 100], 'visible': False},
                    {'at': 16, 'center': [160, 260], 'size': [80, 100]},
                    {'at': 18, 'center': [180, 280], 'size': [80, 100]}]}

    def test_clip_and_clear_at_each_cut(self):
        sections = [{'id': 'one', 'kind': 'game', 'source': 'original', 'sourceStart': 12, 'sourceEnd': 15},
                    {'id': 'explain', 'kind': 'diagram'},
                    {'id': 'two', 'kind': 'game', 'source': 'original', 'sourceStart': 16.5, 'sourceEnd': 19}]
        result = module.remap_source_annotations(sections, {'sourceAnnotations': {'original': [self.mark()]}}, self.source())
        self.assertEqual(set(result), {'one', 'two'})
        first = result['one'][0]; second = result['two'][0]
        self.assertEqual((first['start'], first['end']), (0, 3))
        self.assertEqual(first['keyframes'][0]['center'], [120, 220])
        self.assertEqual(first['keyframes'][0]['size'], [60, 80])
        self.assertFalse(first['keyframes'][-1]['visible'])
        self.assertEqual((second['start'], second['end']), (0, 1.5))
        self.assertEqual(second['labelCenter'], [300, 100])
        self.assertEqual(second['sourceProvenance']['sourceStart'], 16.5)
        self.assertEqual(second['sourceProvenance']['sourceSHA256'], 'synthetic-test-sha')

    def test_keyframe_label_interpolation(self):
        keys = [{'at': 1, 'center': [0, 0], 'size': [10, 10], 'labelCenter': [100, 100]},
                {'at': 3, 'center': [20, 20], 'size': [10, 10], 'labelCenter': [200, 300]}]
        self.assertEqual(module.annotation_geometry(keys, 2)['labelCenter'], [150, 200])

    def test_extrapolation_rejected(self):
        mark = self.mark(); mark['start'] = 9
        with self.assertRaisesRegex(RuntimeError, 'extrapolate'):
            module.remap_source_annotations([], {'sourceAnnotations': {'original': [mark]}}, self.source())

    def test_unadopted_source_rejected(self):
        with self.assertRaisesRegex(RuntimeError, 'not an adopted'):
            module.remap_source_annotations([], {'sourceAnnotations': {'other': [self.mark()]}}, self.source())


if __name__ == '__main__': unittest.main()
