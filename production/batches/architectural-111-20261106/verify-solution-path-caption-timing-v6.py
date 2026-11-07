"""Pure synthetic word/sample fixtures. No actual prepare/profile/model/media."""
from __future__ import annotations
import ast, contextlib, copy, difflib, importlib.util, io, math, re, sys, types, unicodedata, unittest
from pathlib import Path
from unittest.mock import patch
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('solution_caption_v6_pure_tests', HERE / 'build-solution-path-caption-timing-v6.py')
c = importlib.util.module_from_spec(spec); spec.loader.exec_module(c)


def strict_primitives():
    """Compile only the already-reviewed pure functions, no module imports."""
    raw = HERE / 'run-first-asr.py'
    assert c.sha(raw) == '7e38f2565fcf44b45ff6a94c68c7a359a497515c28ed462c729a36c7d1e6864e'
    scope = dict(re=re, unicodedata=unicodedata, difflib=difflib)
    nodes = [x for x in ast.parse(raw.read_text(encoding='utf8')).body if isinstance(x, ast.FunctionDef) and x.name in ('folded', 'comparison')]
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(raw), 'exec'), scope)
    helper = HERE / 'build-prospect-refuge-caption-timing.py'
    assert c.sha(helper) == 'e5cfcc3994a2d52bced9ee66b9ff6213355acbaef45286d31aa3e1461d7ef609'
    ns = dict(require=c.require, Pending=c.Pending, asr=types.SimpleNamespace(folded=scope['folded'], comparison=scope['comparison']),
              sample=c.sample, frame_from_sample=c.frame_from_sample, RATE=24000, math=math, re=re, difflib=difflib)
    nodes = [x for x in ast.parse(helper.read_text(encoding='utf8')).body if isinstance(x, ast.FunctionDef) and x.name in ('aligned_sentence', 'char_boundary')]
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(helper), 'exec'), ns)
    return ns


STRICT = strict_primitives()


def full_build_fixture(particle=False):
    """Actual14 source texts, entirely SYNTHETIC per-word sample envelopes."""
    old = types.ModuleType('synthetic_caption_v5_pure_body')
    names = {'validate_translated', 'one_line_emphasis', 'display_cue', 'paragraph_boundary', 'build', 'char_boundary'}
    tree = ast.parse((HERE / 'build-solution-path-caption-timing-v5.py').read_text(encoding='utf8'))
    display_spec = importlib.util.spec_from_file_location('synthetic_font_only_validator', HERE / 'verify-solution-path-caption-clauses.py')
    display = importlib.util.module_from_spec(display_spec); display_spec.loader.exec_module(display)
    old.__dict__.update(require=c.require, Pending=c.Pending, copy=copy, re=re, TOPIC='11.05', FPS=60, RATE=24000,
                        SCHEMA=c.SCHEMA, display=display, _scope=STRICT, SOURCE_PINS={})
    exec(compile(ast.Module(body=[x for x in tree.body if isinstance(x, ast.FunctionDef) and x.name in names], type_ignores=[]), 'frozen-pure-caption-body', 'exec'), old.__dict__)
    narration = c.read(c.PROJECT / 'narration-final-v5.json')
    clauses = c.read(c.PROJECT / 'caption-clauses-v2.json')
    translated = c.read(c.PROJECT / 'translated-caption-display-boundaries-v2.json')
    c.configure_display(old, clauses, translated, narration)
    sentences, takes, pins, position = [], [], {}, 0
    for group in clauses['groups']:
        for part in group['koLogicalSentences']:
            tokens = re.findall(r'\S+', part['canonicalKo']); end = position + (len(tokens) + 1) * 4800
            sentence = dict(sceneId=part['sceneId'], paragraph=group['paragraph'], canonicalKo=part['canonicalKo'],
                            paragraphCharRange=part['sourceCharRange'], startSample=position, endSample=end,
                            startFrame=c.frame_from_sample(position), endFrameExclusive=c.frame_from_sample(end),
                            rawWav=dict(path='synthetic/' + part['sceneId'] + '.wav', sha256='a' * 64, pcmSHA256='b' * 64,
                                        sampleRate=24000, channels=1, sampleWidthBytes=2, frames=end - position))
            words = [dict(text=(' ' if i else '') + token, timestamp=[(position + 1200 + i * 4800) / 24000,
                     (position + 3600 + i * 4800) / 24000]) for i, token in enumerate(tokens)]
            if particle and part['sceneId'] == 'p001-c02': words[2]['text'] = ' 동굴의'
            takes.append(dict(task=dict(sceneId=part['sceneId'], expected=part['canonicalKo'], offsetSample=position, endSample=end),
                              text=''.join(w['text'] for w in words), globalWords=words))
            sentences.append(sentence); pins[part['sceneId']] = dict(path='synthetic/' + part['sceneId'] + '-asr.json', sha256='c' * 64)
            position = end
    binding = dict(sentences=sentences, totalSamples=position, totalFrames=(position * 60 + 23999) // 24000,
                   aggregate=dict(path='synthetic/raw.wav', sha256='d' * 64), timing=dict(path='synthetic/timing.json', sha256='e' * 64))
    old.aligned_sentence = STRICT['aligned_sentence']
    return old, narration, clauses, translated, dict(takes=takes), binding, pins


def fixture(merged=False):
    text = '출구 좌표를 정합니다.' if merged else '매번 달라지는 동굴에 출구로 이어집니다.'
    words = [('출구좌표를', .1, .5), (' 정합니다.', .6, .9)] if merged else [
        ('매번', .1, .2), (' 달라지는', .3, .6), (' 동굴의', .7, 1.), (' 출구로', 1.1, 1.4), (' 이어집니다.', 1.5, 1.8)]
    raw = dict(path='fixture/take.wav', sha256='a' * 64, pcmSHA256='b' * 64, sampleRate=24000, channels=1,
               sampleWidthBytes=2, frames=48000, durationSeconds=2.)
    sentence = dict(sceneId='p001-c02', paragraph=1, canonicalKo=text, paragraphCharRange=[0, len(text)],
                    startSample=0, endSample=48000, startFrame=0, endFrameExclusive=120, rawWav=raw)
    take = dict(task=dict(sceneId=sentence['sceneId'], expected=text, offsetSample=0, endSample=48000),
                text=''.join(x[0] for x in words), globalWords=[dict(text=t, timestamp=[a, b]) for t, a, b in words])
    aligned = STRICT['aligned_sentence'](sentence, take)
    a, b = (0, 6) if merged else (8, 11)
    indices = [0] if merged else [2]
    selected = [aligned['words'][i] for i in indices]
    result_pin = dict(path='fixture/current-take-asr.json', sha256='c' * 64)
    row = dict(id='synthetic-merged' if merged else 'synthetic-particle', sceneId=sentence['sceneId'],
               rawWav=copy.deepcopy(raw), asrResult=copy.deepcopy(result_pin), canonicalTakeLiteral=text, recognizedTakeLiteral=take['text'],
               canonicalCharRange=[a, b], canonicalLiteral=text[a:b], actualWordIndices=indices,
               recognizedWords=copy.deepcopy(selected), recognizedLiteral=''.join(x['text'] for x in selected),
               boundaryMappings=[dict(canonicalOffset=b, actualEdge='end'), dict(canonicalOffset=b + 1, actualEdge='end')],
               reason='Synthetic explicit whole-word edge fixture; mismatch remains a listening target')
    context = dict(sourceNarration=dict(path='fixture/narration-v5.json', sha256='d' * 64),
                   voiceEvidence=dict(path='fixture/current-immutable-voice.json', sha256='e' * 64),
                   voiceFingerprint='f' * 64, rawAsrReview=dict(path='fixture/current-review.json', sha256='1' * 64),
                   rawAsrJob=dict(path='fixture/current-job.json', sha256='2' * 64))
    document = dict(schemaVersion=c.EVIDENCE_SCHEMA, topicId='11.05', reviewScope='technical-caption-display-whole-word-edges-only',
                    reviewedBy='synthetic-test-reviewer', **copy.deepcopy(context), rows=[row], aliasesApplied=False,
                    recognitionModified=False, pcmModified=False, expectedPromptsUsed=False, automaticSpeechPass=False,
                    actualListening=False, humanApproval=False)
    return document, context, {sentence['sceneId']: aligned}, {sentence['sceneId']: take}, {sentence['sceneId']: result_pin}


def applied(args):
    document, context, sentences, takes, pins = args
    validated = c.validate_evidence(document, context, sentences, takes, pins)
    sid = next(iter(sentences))
    return c.apply_evidence(sentences[sid], validated.get(sid, []), dict(path='fixture/evidence.json', sha256='3' * 64))


class WordEdges(unittest.TestCase):
    def bad(self, args):
        with self.assertRaises((c.Pending, ValueError, KeyError, TypeError)): c.validate_evidence(*args)

    def test_exact_literal_missing_particle_boundary_is_reproduced(self):
        args = fixture(); row = next(iter(args[2].values()))
        self.assertRaises(c.Pending, STRICT['char_boundary'], row, 11)
        self.assertTrue(row['alignmentReview']['comparison']['characterDifferences'])

    def test_audited_whole_word_end_adds_only_actual_edges(self):
        args = fixture(); row = applied(args)
        expected = args[2]['p001-c02']['words'][2]['endSample']
        self.assertEqual(STRICT['char_boundary'](row, 11)['sample'], expected)
        self.assertEqual(STRICT['char_boundary'](row, 12)['sample'], expected)
        self.assertEqual(row['canonicalKo'], args[2]['p001-c02']['canonicalKo'])
        self.assertEqual(row['alignmentReview']['comparison'], args[2]['p001-c02']['alignmentReview']['comparison'])
        self.assertEqual(row['alignmentReview']['recognizedLiteral'], args[3]['p001-c02']['text'])
        self.assertFalse(row['alignmentReview']['automaticSpeechPass'])
        self.assertFalse(row['alignmentReview']['explicitWordEdgeEvidence']['aliasesApplied'])

    def test_literal_choice_wins_without_manual_clock_override(self):
        args = fixture(); sentence = args[2]['p001-c02']
        for offset in (11, 12): sentence['canonicalWordBoundaries'].append(dict(charOffset=offset, sample=25000, frame=c.frame_from_sample(25000), method='literal-first'))
        row = applied(args)
        self.assertEqual(STRICT['char_boundary'](row, 11)['sample'], 25000)
        self.assertEqual(row['alignmentReview']['explicitWordEdgeEvidence']['appliedBoundaryCount'], 0)

    def test_merged_asr_word_internal_cut_stays_pending_until_reflow(self):
        args = fixture(True); row = applied(args)
        self.assertRaises(c.Pending, STRICT['char_boundary'], row, 2)
        self.assertRaises(c.Pending, STRICT['char_boundary'], row, 3)
        self.assertGreater(STRICT['char_boundary'](row, 6)['sample'], STRICT['char_boundary'](row, 0)['sample'])
        self.assertEqual(' '.join(['출구 좌표를', '정합니다.']), row['canonicalKo'])

    def test_interior_endpoint_cannot_be_fabricated(self):
        args = fixture(True); args[0]['rows'][0]['boundaryMappings'] = [dict(canonicalOffset=2, actualEdge='end')]
        self.bad(args)

    def test_partial_canonical_word_span_rejected(self):
        args = fixture(); r = args[0]['rows'][0]; r['canonicalCharRange'] = [9, 11]; r['canonicalLiteral'] = r['canonicalTakeLiteral'][9:11]
        self.bad(args)

    def test_wrong_source_voice_review_job_context_rejected(self):
        for key in ('sourceNarration', 'voiceEvidence', 'voiceFingerprint', 'rawAsrReview', 'rawAsrJob'):
            args = fixture(); args[0][key] = 'wrong'
            self.bad(args)

    def test_wrong_wav_pcm_format_or_cache_pin_rejected(self):
        for field in ('sha256', 'pcmSHA256', 'frames', 'channels'):
            args = fixture(); args[0]['rows'][0]['rawWav'][field] = 'wrong'; self.bad(args)
        args = fixture(); args[0]['rows'][0]['asrResult']['sha256'] = '0' * 64; self.bad(args)

    def test_raw_recognized_literal_cannot_be_rewritten_as_canonical(self):
        args = fixture(); args[0]['rows'][0]['recognizedLiteral'] = ' 동굴에'; self.bad(args)
        args = fixture(); args[0]['rows'][0]['recognizedTakeLiteral'] = args[0]['rows'][0]['canonicalTakeLiteral']; self.bad(args)

    def test_canonical_literal_and_context_omission_rejected(self):
        args = fixture(); args[0]['rows'][0]['canonicalLiteral'] = '동굴'; self.bad(args)
        args = fixture(); args[0]['rows'][0]['canonicalTakeLiteral'] += '.'; self.bad(args)

    def test_actual_word_timestamp_and_sample_tampering_rejected(self):
        for key, value in (('end', 1.01), ('endSample', 24001), ('sourceWordIndex', False)):
            args = fixture(); args[0]['rows'][0]['recognizedWords'][0][key] = value; self.bad(args)

    def test_noncontiguous_or_bool_word_indices_rejected(self):
        for indices in ([0, 2], [2, 2], [True], [-1], [99]):
            args = fixture(); args[0]['rows'][0]['actualWordIndices'] = indices; self.bad(args)

    def test_duplicate_ids_and_mapping_offsets_rejected(self):
        args = fixture(); args[0]['rows'].append(copy.deepcopy(args[0]['rows'][0])); self.bad(args)
        args = fixture(); args[0]['rows'][0]['boundaryMappings'] *= 2; self.bad(args)

    def test_overlapping_or_reversed_canonical_word_maps_rejected(self):
        args = fixture(); extra = copy.deepcopy(args[0]['rows'][0]); extra['id'] = 'different-id'; args[0]['rows'].append(extra); self.bad(args)

    def test_unclipped_only_endpoints_with_no_zero_or_reversal(self):
        args = fixture(); sentence = args[2]['p001-c02']; word = sentence['words'][2]
        word['start'] = -1.; args[0]['rows'][0]['recognizedWords'] = [copy.deepcopy(word)]; self.bad(args)
        args = fixture(); word = args[2]['p001-c02']['words'][2]; word['endSample'] = word['startSample']; word['end'] = word['start']; args[0]['rows'][0]['recognizedWords'] = [copy.deepcopy(word)]; self.bad(args)

    def test_support_cannot_reverse_an_existing_literal_clock(self):
        args = fixture(); row = args[2]['p001-c02']; row['canonicalWordBoundaries'].append(dict(charOffset=7, sample=30000, frame=75))
        with self.assertRaises(c.Pending): applied(args)

    def test_claimed_alias_prompt_speech_or_human_pass_rejected(self):
        for key in ('aliasesApplied', 'recognitionModified', 'pcmModified', 'expectedPromptsUsed', 'automaticSpeechPass', 'actualListening', 'humanApproval'):
            args = fixture(); args[0][key] = True; self.bad(args)

    def test_no_evidence_preserves_literal_unsupported_records(self):
        args = fixture(); row = args[2]['p001-c02']; result = c.apply_evidence(row, [], None)
        self.assertEqual(result['unsupportedWordBoundaries'], row['unsupportedWordBoundaries'])
        self.assertEqual(result['literalUnsupportedWordBoundaries'], row['unsupportedWordBoundaries'])
        self.assertRaises(c.Pending, STRICT['char_boundary'], result, 11)

    def test_actual_frame_rounding_has_no_fraction_or_audio_padding(self):
        self.assertEqual(c.frame_from_sample(24000), 60)
        self.assertEqual(c.frame_from_sample(200), 1)
        self.assertEqual(c.frame_from_sample(199), 0)
        self.assertRaises(c.Pending, c.frame_from_sample, True)

    def test_immutable_and_published_voice_metadata_only_compatibility(self):
        voice = {k: 'synthetic-' + k for k in c.VOICE_DATA_KEYS}
        published = dict(voice, publicationMetadata='pointer-only', actualListening=False, humanApproval=False)
        c.same_voice_data(voice, published)
        for key in ('identity', 'aggregateWav', 'repairIdentity', 'engineOutputsPreserved'):
            changed = dict(voice, **{key: 'changed'})
            self.assertRaises(c.Pending, c.same_voice_data, changed, published)
        self.assertRaises(c.Pending, c.same_voice_data, dict(voice, humanApproval=True), published)

    def test_default_pending_does_not_write_or_start_anything(self):
        output = io.StringIO()
        with patch.object(sys, 'argv', ['caption-v6']), patch.object(c, 'prepare', side_effect=c.Pending('Synthetic current ASR absent')), \
             patch.object(c, 'write_outputs', side_effect=AssertionError('No output')), contextlib.redirect_stdout(output): c.main()
        self.assertEqual(__import__('json').loads(output.getvalue())['jobLaunched'], False)

    def test_evidence_path_without_explicit_hash_rejected_before_prepare(self):
        with patch.object(sys, 'argv', ['caption-v6', '--alignment-evidence', 'unreviewed.json']), \
             patch.object(c, 'prepare', side_effect=AssertionError('No auto-hash evidence acceptance')):
            self.assertRaises(c.Pending, c.main)

    def test_complete_source_build_v2_display_shim_and_line_local_emphasis(self):
        args = full_build_fixture(); timing = args[0].build(*args[1:])
        self.assertEqual(timing['schemaVersion'], c.SCHEMA)
        self.assertEqual((len(timing['paragraphs']), len(timing['sentences']), len(timing['groups'])), (14, 48, 43))
        self.assertEqual((len(timing['captions']['ko']), len(timing['captions']['en'])), (98, 86))
        for lang in ('ko', 'en'):
            for cue in timing['captions'][lang]:
                self.assertLessEqual(len(cue['emphasis']), 1)
                for span in cue['emphasis']:
                    self.assertEqual(cue['lines'][span['line']][span['start']:span['end']], span['text'])

    def test_full_build_remains_pending_then_uses_only_explicit_current_word_end(self):
        args = full_build_fixture(True); old, narration, clauses, translated, review, binding, pins = args
        self.assertRaisesRegex(c.Pending, 'p001-c02 char 11', old.build, *args[1:])
        aligned = {s['sceneId']: STRICT['aligned_sentence'](s, take) for s, take in zip(binding['sentences'], review['takes'])}
        evidence, context, _, _, _ = fixture(); sentence = aligned['p001-c02']; take = review['takes'][1]; row = evidence['rows'][0]
        row.update(rawWav=copy.deepcopy(sentence['rawWav']), asrResult=pins['p001-c02'], canonicalTakeLiteral=sentence['canonicalKo'],
                   recognizedTakeLiteral=take['text'], recognizedWords=[sentence['words'][2]], recognizedLiteral=sentence['words'][2]['text'])
        supported = c.validate_evidence(evidence, context, aligned, {t['task']['sceneId']: t for t in review['takes']}, pins)
        proof = dict(path='synthetic/explicit-evidence.json', sha256='f' * 64)
        old.aligned_sentence = lambda source, take: c.apply_evidence(aligned[source['sceneId']], supported.get(source['sceneId'], []), proof)
        timing = old.build(*args[1:]); result = timing['sentences'][1]
        self.assertTrue(result['alignmentReview']['comparison']['characterDifferences'])
        self.assertEqual(STRICT['char_boundary'](result, 11)['sample'], sentence['words'][2]['endSample'])
        self.assertEqual((len(timing['captions']['ko']), len(timing['captions']['en'])), (98, 86))


if __name__ == '__main__': unittest.main(verbosity=2)
