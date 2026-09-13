import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from balance_subtitle_translation import partition_timed
from build_translated_srt import wrapped_lines


class SubtitleBalanceTest(unittest.TestCase):
    def test_short_cue_gets_less_text(self):
        text = 'Use a small input and check the result before adding more features to your game.'
        chunks = partition_timed(text, 46, [1, 5])
        self.assertEqual(' '.join(chunks), text)
        self.assertEqual(len(chunks), 2)
        self.assertLess(len(chunks[0]), len(chunks[1]))
        self.assertTrue(all(len(wrapped_lines(c, 46)) <= 2 for c in chunks))

    def test_invalid_duration(self):
        with self.assertRaises(ValueError):
            partition_timed('Some text', 46, [0])

    def test_single_cue(self):
        self.assertEqual(partition_timed('A complete sentence.', 46, [3]), ['A complete sentence.'])


if __name__ == '__main__':
    unittest.main()
