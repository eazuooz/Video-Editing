"""CPU-only tamper/boundary tests; synthetic evidence is never production review."""
from pathlib import Path
import importlib.util
import json
import struct
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('finite_runner', Path(__file__).with_name('run-batch.py'))
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class ReconciliationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.voice = self.root / 'voice.wav'
        self.voice.write_bytes(b'synthetic voice fixture, not playable production audio')
        self.script = self.root / 'narration.json'
        self.expected = '마스크 메시를 둡니다. 배 안의 바다는 사라졌죠.'
        self.write(self.script, {'scenes': [{'lines': [self.expected]}]})
        self.raw = '마스크 메쉬를 둡니다. 배 안에 바다는 사라졌죠.'
        self.report = self.root / 'raw.json'
        self.write(self.report, {'role': 'voice', 'sha256': runner.sha(self.voice),
            'expectedSourceSha256': runner.sha(self.script), 'fullInput': True,
            'expectedTextPromptUsed': False, 'rawRecognitionUnmodified': True,
            'normalizedMatch': False, 'text': self.raw, 'chunks': [{'text': self.raw, 'timestamp': [0, 1]}]})
        self.independent = self.root / 'independent.json'
        self.write(self.independent, {'voiceSha256': runner.sha(self.voice),
            'expectedTextPromptUsed': False, 'rawRecognitionUnmodified': True, 'text': self.raw})
        self.receipt = self.root / 'asr-reconciliation.json'
        self.review = {'status': 'reviewed-orthography-only', 'role': 'voice',
            'inputSha256': runner.sha(self.voice), 'voiceSha256': runner.sha(self.voice),
            'asrSha256': runner.sha(self.report), 'scriptSha256': runner.sha(self.script),
            'unresolvedCount': 0, 'unresolved': [], 'rawAsrPreserved': True,
            'actualListening': 'pending', 'humanListening': 'pending',
            'aliases': {'메쉬': '메시', '배 안에 바다는': '배 안의 바다는'},
            'changes': [
                {'source': '메쉬', 'target': '메시', 'kind': 'mesh-loanword-orthography',
                 'reason': 'Synthetic spelling-only test.', 'evidenceIds': ['independent'], 'occurrences': 1},
                {'source': '배 안에 바다는', 'target': '배 안의 바다는', 'kind': 'contextual-possessive-pronunciation',
                 'reason': 'Synthetic contextual pronunciation test.', 'evidenceIds': ['independent'], 'occurrences': 1}],
            'independentEvidence': [{'id': 'independent', 'path': str(self.independent), 'sha256': runner.sha(self.independent)}]}

    def tearDown(self):
        self.temp.cleanup()

    @staticmethod
    def write(path, document):
        path.write_text(json.dumps(document, ensure_ascii=False), encoding='utf8')

    def validate(self):
        self.write(self.receipt, self.review)
        return runner.validate_asr_reconciliation(self.receipt, self.report, self.voice,
                                                   self.voice, self.script, self.expected, {})

    def test_bounded_variants_preserve_false_raw_result(self):
        before = runner.sha(self.report)
        result, files = self.validate()
        self.assertFalse(result['rawNormalizedMatch'])
        self.assertTrue(result['reconciledContentMatch'])
        self.assertEqual(result['actualListening'], 'pending')
        self.assertIn(self.independent, files)
        self.assertEqual(runner.sha(self.report), before)

    def test_wrong_voice_is_rejected(self):
        self.review['voiceSha256'] = '0' * 64
        with self.assertRaisesRegex(RuntimeError, 'voiceSha256 differs'):
            self.validate()

    def cached_normalization(self, text):
        script_dir = self.root / 'script'
        script_dir.mkdir(exist_ok=True)
        script = script_dir / 'narration.spoken.ko.json'
        self.write(script, {'scenes': [{'lines': ['언차티드 포에서 줄을 잡습니다.']} ]})
        clauses = script_dir / 'caption-clauses.json'
        self.write(clauses, {'pronunciationAliases': {'Uncharted 4': '언차티드 포'}})
        report = self.root / f'asr-voice-{runner.sha(self.voice)[:12]}.json'
        self.write(report, {'role': 'voice', 'sha256': runner.sha(self.voice),
            'expectedSourceSha256': runner.sha(script), 'fullInput': True,
            'expectedTextPromptUsed': False, 'rawRecognitionUnmodified': True,
            'normalizedMatch': False, 'text': text, 'chunks': [{'text': text, 'timestamp': [0, 1]}]})
        obj = runner.Pipeline.__new__(runner.Pipeline)
        obj.project = self.root
        obj.audio = self.root
        obj.ctx = {'VOICE': self.voice}
        obj.py = lambda *args: args
        obj.command = lambda *args: None  # Cached recognizer fixture, no model.
        before = runner.sha(report)
        result, files = obj.asr('voice')
        self.assertEqual(runner.sha(report), before)
        self.assertEqual(result['normalizationAliasesSha256'], runner.sha(clauses))
        return result

    def test_current_aliases_accept_exact_cached_name_without_rewriting_raw(self):
        result = self.cached_normalization('Uncharted 4에서 줄을 잡습니다.')
        self.assertFalse(result['rawNormalizedMatch'])
        self.assertTrue(result['currentNormalizationMatch'])
        self.assertEqual(result['actualListening'], 'pending')

    def test_current_aliases_reject_different_name(self):
        with self.assertRaisesRegex(RuntimeError, 'Raw ASR differs'):
            self.cached_normalization('Uncharted 3에서 줄을 잡습니다.')

    def test_current_aliases_reject_missing_word(self):
        with self.assertRaisesRegex(RuntimeError, 'Raw ASR differs'):
            self.cached_normalization('Uncharted 4에서 잡습니다.')

    def test_raw_tamper_is_rejected(self):
        self.report.write_text('{}', encoding='utf8')
        with self.assertRaisesRegex(RuntimeError, 'role differs|asrSha256 differs'):
            self.validate()

    def test_independent_evidence_tamper_is_rejected(self):
        self.independent.write_text('{}', encoding='utf8')
        with self.assertRaisesRegex(RuntimeError, 'evidence file changed'):
            self.validate()

    def test_unresolved_name_is_rejected(self):
        self.review['unresolvedCount'] = 1
        self.review['unresolved'] = ['game-name']
        with self.assertRaisesRegex(RuntimeError, 'unresolved differences'):
            self.validate()

    def test_name_alias_cannot_use_generic_review(self):
        self.review['aliases'] = {'Sea of Sea of G': '씨 오브 시브즈'}
        self.review['changes'] = [{'source': 'Sea of Sea of G', 'target': '씨 오브 시브즈',
            'kind': 'proper-name', 'reason': 'Unresolved name cannot be fixed by alias.',
            'evidenceIds': ['independent'], 'occurrences': 1}]
        with self.assertRaisesRegex(RuntimeError, 'names and semantic replacements are forbidden'):
            self.validate()

    def test_partial_coverage_is_rejected(self):
        self.expected += ' 없는 문장.'
        with self.assertRaisesRegex(RuntimeError, 'complete canonical content still differs'):
            self.validate()

    def contextual_fixture(self, source, target, kind, independent=None):
        self.raw, self.expected = source, target
        self.write(self.script, {'scenes': [{'lines': [target]}]})
        self.write(self.report, {'role': 'voice', 'sha256': runner.sha(self.voice),
            'expectedSourceSha256': runner.sha(self.script), 'fullInput': True,
            'expectedTextPromptUsed': False, 'rawRecognitionUnmodified': True,
            'normalizedMatch': False, 'text': source, 'chunks': [{'text': source, 'timestamp': [0, 1]}]})
        self.write(self.independent, {'voiceSha256': runner.sha(self.voice),
            'expectedTextPromptUsed': False, 'rawRecognitionUnmodified': True,
            'text': source if independent is None else independent})
        self.review.update(asrSha256=runner.sha(self.report), scriptSha256=runner.sha(self.script),
            aliases={source: target}, changes=[{'source': source, 'target': target, 'kind': kind,
            'reason': 'Synthetic exact-context homophone test.', 'evidenceIds': ['independent'], 'occurrences': 1}])
        self.review['independentEvidence'][0]['sha256'] = runner.sha(self.independent)

    def test_exact_bridge_liaison_can_be_independently_spelled_canonically(self):
        a, b = '이 스타크래프트 달이, 대각선으로 놓여 있죠.', '이 스타크래프트 다리, 대각선으로 놓여 있죠.'
        self.contextual_fixture(a, b, 'contextual-bridge-liaison-orthography', independent=b)
        self.assertTrue(self.validate()[0]['reconciledContentMatch'])

    def test_bridge_liaison_rejects_different_noun_or_name(self):
        for noun in ['자리', '마리오']:
            self.contextual_fixture('이 스타크래프트 달이, 대각선으로 놓여 있죠.',
                f'이 스타크래프트 {noun}, 대각선으로 놓여 있죠.', 'contextual-bridge-liaison-orthography')
            with self.assertRaisesRegex(RuntimeError, 'exact bridge liaison context'):
                self.validate()

    def test_bridge_liaison_rejects_unbound_context(self):
        self.contextual_fixture('달이', '다리', 'contextual-bridge-liaison-orthography')
        with self.assertRaisesRegex(RuntimeError, 'exact bridge liaison context'):
            self.validate()

    def test_exact_same_area_locative_accepts_only_authored_context(self):
        self.contextual_fixture('같은 넓이의 가로 네 칸', '같은 넓이에 가로 네 칸',
            'contextual-locative-pronunciation')
        self.assertTrue(self.validate()[0]['reconciledContentMatch'])
        self.contextual_fixture('넓이의', '넓이에', 'contextual-locative-pronunciation')
        with self.assertRaisesRegex(RuntimeError, 'exact reviewed locative context'):
            self.validate()

    def test_exact_between_systems_locative_context(self):
        self.contextual_fixture('새 게임 사이의 통역기를 둔다면 어떨까요?',
            '새 게임 사이에 통역기를 둔다면 어떨까요?', 'contextual-locative-pronunciation')
        self.assertTrue(self.validate()[0]['reconciledContentMatch'])

    def test_method_liaison_rejects_semantic_change_and_unbound_word(self):
        self.contextual_fixture('그 값을 찾아 주는 시기죠.', '그 값을 찾아 주는 식이죠.',
            'contextual-method-liaison-orthography')
        self.assertTrue(self.validate()[0]['reconciledContentMatch'])
        for source, target in [('시기죠', '식이죠'), ('그 값을 찾아 주는 시기죠.', '그 값을 찾아 주는 방식이죠.')]:
            self.contextual_fixture(source, target, 'contextual-method-liaison-orthography')
            with self.assertRaisesRegex(RuntimeError, 'exact value-lookup method liaison context'):
                self.validate()

    def test_prior_evidence_requires_unchanged_pcm_chain(self):
        oldvoice = self.root / 'old-voice.wav'; oldvoice.write_bytes(b'old complete voice')
        rawtake = self.root / 'p3-raw.wav'; rawtake.write_bytes(b'exact reused raw paragraph')
        normalized = self.root / 'p3-normalized.wav'; normalized.write_bytes(b'exact reused normalized paragraph')
        row = {'lineIndex': 2, 'text': self.raw, 'rawTake': str(rawtake), 'rawTakeSha256': runner.sha(rawtake),
               'normalizedTake': str(normalized), 'normalizedTakeSha256': runner.sha(normalized),
               'samples': 24000, 'rate': 24000, 'destinationSampleRange': [48000, 72000]}
        oldlevels = self.root / 'old-levels.json'; newlevels = self.root / 'new-levels.json'
        self.write(oldlevels, {'voiceSha256': runner.sha(oldvoice), 'paragraphs': [row]})
        self.write(newlevels, {'voiceSha256': runner.sha(self.voice), 'paragraphs': [{**row, 'destinationSampleRange': [50000, 74000]}]})
        self.write(self.independent, {'voiceSha256': runner.sha(oldvoice), 'expectedTextPromptUsed': False,
            'rawRecognitionUnmodified': True, 'paragraphs': [{'id': 'paragraph-3', 'startSample': 48000,
            'endSample': 72000, 'sampleRate': 24000, 'raw': {'text': self.raw}}]})
        item = self.review['independentEvidence'][0]
        item.update(sha256=runner.sha(self.independent), unchangedParagraphs=[{'lineIndex': 2, 'evidenceParagraphId': 'paragraph-3'}])
        for key, path in [('sourceVoice', oldvoice), ('priorLineLevels', oldlevels), ('currentLineLevels', newlevels)]:
            item[key] = {'path': str(path), 'sha256': runner.sha(path)}
        self.assertTrue(self.validate()[0]['reconciledContentMatch'])
        rawtake.write_bytes(b'changed raw PCM')
        with self.assertRaisesRegex(RuntimeError, 'evidence file changed'):
            self.validate()

    def test_float_wav_metadata_is_distinct_from_audio_samples(self):
        def wav(timestamp, value):
            fmt = struct.pack('<HHIIHH', 3, 1, 24000, 96000, 4, 32)
            data = struct.pack('<ff', value, .25)
            peak = struct.pack('<II', 1, timestamp)
            body = b'WAVE' + b'fmt ' + struct.pack('<I', len(fmt)) + fmt
            body += b'PEAK' + struct.pack('<I', len(peak)) + peak
            body += b'data' + struct.pack('<I', len(data)) + data
            return b'RIFF' + struct.pack('<I', len(body)) + body
        old = self.root / 'old-float.wav'; new = self.root / 'new-float.wav'
        old.write_bytes(wav(1, .5)); new.write_bytes(wav(2, .5))
        self.assertNotEqual(runner.sha(old), runner.sha(new))
        self.assertEqual(runner.float32_mono_wav_data(old), runner.float32_mono_wav_data(new))
        new.write_bytes(wav(2, .50001))
        self.assertNotEqual(runner.float32_mono_wav_data(old), runner.float32_mono_wav_data(new))


    def test_new_contexts_reject_names_and_unbound_replacements(self):
        allowed = [
            ('쉐이더', '셰이더', 'shader-loanword-orthography'),
            ('물보다는 붓박이 그림처럼 보이죠.', '물보다는 붙박이 그림처럼 보이죠.', 'contextual-built-in-spelling'),
            ('릴리프 맵핑으로 파인 깊이를 표현합니다.', '릴리프 매핑으로 파인 깊이를 표현합니다.', 'contextual-relief-mapping-spelling'),
            ('병의 액체 무늬를 고정하면', '병에 액체 무늬를 고정하면', 'contextual-locative-pronunciation'),
            ('검은 바탕의 흰색으로 그립니다.', '검은 바탕에 흰색으로 그립니다.', 'contextual-locative-pronunciation'),
            ('모두 한 박자의 움직이는 느낌을 줄이는 거죠.', '모두 한 박자에 움직이는 느낌을 줄이는 거죠.', 'contextual-locative-pronunciation'),
            ('이 초의 이동, 사 초의 공격을 기록해 볼게요.', '이 초에 이동, 사 초에 공격을 기록해 볼게요.', 'contextual-locative-pronunciation')]
        for source, target, kind in allowed:
            self.contextual_fixture(source, target, kind, independent=target)
            self.assertTrue(self.validate()[0]['reconciledContentMatch'])
            self.contextual_fixture(source, target + ' 아캄 오리진', kind)
            with self.assertRaises(RuntimeError): self.validate()
        for source, target, kind in [('붓박이', '붙박이', 'contextual-built-in-spelling'),
                                      ('투형', '투영', 'shader-loanword-orthography'),
                                      ('의', '에', 'contextual-locative-pronunciation')]:
            self.contextual_fixture(source, target, kind)
            with self.assertRaises(RuntimeError): self.validate()

if __name__ == '__main__':
    unittest.main()
