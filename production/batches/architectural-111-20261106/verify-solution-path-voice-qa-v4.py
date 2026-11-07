"""Synthetic CPU fixtures only: no real recognizer, GPU, model or media job."""
import copy, hashlib, importlib.util, io, json, struct, tempfile, unittest, wave
from contextlib import ExitStack, redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('solution_asr_v4_cpu', HERE / 'run-solution-path-voice-qa-v4.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def dump(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return path


class VoiceFixture(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='solution-asr-v4-cpu-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def fixture(self, extra_sentence=False):
        draft = dict(topicId='11.05', titleKo='Synthetic fixture', narrationFinalized=True, ttsReady=True,
                     narrationKo=['첫 방을 살펴봅니다. 다음 문으로 이동합니다.'] * 14,
                     paragraphsEn=['Inspect the room. Move to the next door.'] * 14)
        if extra_sentence:
            draft['narrationKo'][0] += ' 마지막 경계를 확인합니다.'
        np = dump(self.root / 'projects/shorts-leveldesign-11-05/narration-test-final.json', draft)
        cp = dict(expandedNarrationDraft=dict(finalized=True),
                  currentProduction=dict(narrationFinalized=True, ttsReady=True))
        script, mapping = m.prep.sentence_plan(draft, m.sha(np))
        profile = m.qa.read(m.PROFILE_PATH)
        identity = m.profile_identity([dict(id=s['id'], lines=s['lines']) for s in script['scenes']], profile)
        fp = m.digest(identity)
        out = self.root / 'shared/output/architectural-111-20261106/11-05/voice-attempts' / fp[:24]
        for i, scene in enumerate(script['scenes']):
            p = out / 'chunks' / (scene['id'] + '-scene.wav')
            p.parent.mkdir(parents=True, exist_ok=True)
            with wave.open(str(p), 'wb') as w:
                w.setparams((1, 2, 24000, 48, 'NONE', 'not compressed'))
                w.writeframes(struct.pack('<h', i + 1) * 48)
        prov = dict(topicId='11.05', identity=identity, fingerprint=fp, paragraphMapping=mapping)
        proof = m.qa.voice.canonical_outputs(prov, out, {})
        dump(out / 'voice-complete-proof.json', proof)
        dump(out / 'voice-inputs.json', dict(protocol=m.qa.voice.PROTOCOL, fingerprint=fp,
                                            identity=identity, inputs=[m.pin(np)]))
        vp = dump(self.root / 'voice-evidence.json', proof)
        state = dump(self.root / 'voice-state.json', dict(completed=True, fingerprint=fp, child=None))
        dump(self.root / 'shared/publishing/video-production-control.json',
             {m.qa.AUTH_KEY: dict(status='active', automaticAdvanceWithinExactList=True,
                                 automaticAdvanceOutsideList=False, humanFinalReviewRequired=True,
                                 youtubeAuthorized=False)})
        stack = ExitStack()
        self.addCleanup(stack.close)
        stack.enter_context(patch.object(m, 'ROOT', self.root))
        stack.enter_context(patch.object(m, 'PROOF', vp))
        stack.enter_context(patch.object(m, 'VOICE_STATE', state))
        stack.enter_context(patch.object(m.prep, 'current_inputs', return_value=(cp, np, draft, np)))
        stack.enter_context(patch.object(m.qa.voice, 'project_children', return_value=[]))
        return proof, out, vp, state, np, draft

    def republish(self, proof, out, vp):
        dump(out / 'voice-complete-proof.json', proof)
        dump(vp, proof)

    def test_exact14_paragraph_pcm_and_blind_joins(self):
        proof, out, *_ = self.fixture()
        _, actual, timing, _ = m.exact_voice()
        tasks = m.qa.build_tasks(actual, timing)
        self.assertEqual(len(actual['sceneWavs']), 28)
        self.assertEqual(len(tasks), 55)
        self.assertEqual(sum(t['kind'] == 'boundary' and t['joinType'] == 'paragraph-boundary' for t in tasks), 13)
        self.assertEqual(tasks[27]['endSample'], proof['aggregateWav']['frames'])
        self.assertTrue(all(t['beginSample'] == 0 and t['endSample'] == proof['aggregateWav']['frames']
                            for t in tasks if t['kind'] == 'boundary'))

    def test_final_sentence_count_is_derived_not_hard48(self):
        self.fixture(extra_sentence=True)
        _, proof, timing, _ = m.exact_voice()
        self.assertEqual(len(proof['sceneWavs']), 29)
        self.assertEqual(len(m.qa.build_tasks(proof, timing)), 57)

    def test_one_sample_start_shift_rejected_even_with_rebound_hash(self):
        proof, out, vp, *_ = self.fixture()
        path = Path(proof['timing']['path'])
        timing = m.qa.read(path)
        timing['entries'][0]['start'] += 1 / 24000
        dump(path, timing)
        proof['timing']['sha256'] = m.sha(path)
        self.republish(proof, out, vp)
        with self.assertRaisesRegex(ValueError, 'sample boundary'):
            m.exact_voice()

    def test_one_sample_end_shift_rejected(self):
        proof, out, vp, *_ = self.fixture()
        path = Path(proof['timing']['path'])
        timing = m.qa.read(path)
        timing['entries'][0]['end'] += 1 / 24000
        dump(path, timing)
        proof['timing']['sha256'] = m.sha(path)
        self.republish(proof, out, vp)
        with self.assertRaisesRegex(ValueError, 'sample boundary'):
            m.exact_voice()

    def test_changed_aggregate_with_rebound_file_pcm_hash_is_not_concat(self):
        proof, out, vp, *_ = self.fixture()
        p = Path(proof['aggregateWav']['path'])
        data = bytearray(p.read_bytes())
        data[-2] ^= 1
        p.write_bytes(data)
        proof['aggregateWav'] = m.qa.voice.wav_info(p)
        self.republish(proof, out, vp)
        with self.assertRaisesRegex(ValueError, 'concatenation'):
            m.exact_voice()

    def test_reordered_mapping_rejected(self):
        proof, out, vp, *_ = self.fixture()
        proof['paragraphMapping'][0], proof['paragraphMapping'][1] = proof['paragraphMapping'][1], proof['paragraphMapping'][0]
        self.republish(proof, out, vp)
        with self.assertRaisesRegex(ValueError, 'mapping'):
            m.exact_voice()

    def test_changed_source_character_mapping_rejected(self):
        proof, out, vp, *_ = self.fixture()
        proof['paragraphMapping'][0]['sourceCharRange'][1] -= 1
        self.republish(proof, out, vp)
        with self.assertRaisesRegex(ValueError, 'mapping'):
            m.exact_voice()

    def test_foreign_topic_output_rejected(self):
        proof, out, vp, *_ = self.fixture()
        proof['topicId'] = '07.04'
        self.republish(proof, out, vp)
        with self.assertRaisesRegex(ValueError, 'identity'):
            m.exact_voice()

    def test_changed_chunk_pcm_rejected(self):
        proof, *_ = self.fixture()
        p = Path(proof['sceneWavs'][0]['path'])
        data = bytearray(p.read_bytes())
        data[-2] ^= 1
        p.write_bytes(data)
        with self.assertRaisesRegex(RuntimeError, 'PCM changed'):
            m.exact_voice()

    def test_unpinned_final_source_rejected(self):
        proof, out, *_ = self.fixture()
        receipt = m.qa.read(out / 'voice-inputs.json')
        receipt['inputs'] = []
        dump(out / 'voice-inputs.json', receipt)
        with self.assertRaisesRegex(ValueError, 'not pinned'):
            m.exact_voice()

    def test_provisional_source_cannot_become_final_from_cp(self):
        *_, draft = self.fixture()
        draft['narrationFinalized'] = False
        with self.assertRaises(m.Pending):
            m.exact_voice()

    def test_live_qwen_child_preserved(self):
        self.fixture()
        with patch.object(m.qa.voice, 'project_children', return_value=[dict(pid=99)]):
            with self.assertRaises(m.Pending):
                m.exact_voice()

    def test_missing_voice_returns_before_source_resources_or_model(self):
        self.fixture()
        with patch.object(m, 'PROOF', self.root / 'missing.json'), \
             patch.object(m, 'source_context', side_effect=AssertionError('not yet')), \
             patch.object(m.qa, 'resource_reason', side_effect=AssertionError('no resource queries')):
            with self.assertRaises(m.Pending):
                m.exact_voice()

    def test_exact_profile_and_all_nonspoken_voice_pins_checked(self):
        proof, *_ = self.fixture()
        profile = m.qa.read(m.PROFILE_PATH)
        expected = m.profile_identity(proof['identity']['scenes'], profile)
        self.assertEqual(expected, proof['identity'])
        for key in ('referenceSHA256', 'referenceTextSHA256', 'modelPins', 'engine', 'guard', 'rawPcmPolicy', 'tts'):
            wrong = copy.deepcopy(expected)
            wrong[key] = 'changed'
            self.assertNotEqual(wrong, m.profile_identity(proof['identity']['scenes'], profile))

    def test_rebound_foreign_profile_declines_before_audio_or_model(self):
        proof, out, vp, state, *_ = self.fixture()
        proof['identity']['tts']['language'] = 'English'
        proof['fingerprint'] = m.digest(proof['identity'])
        proof['output'] = str(out.parent / proof['fingerprint'][:24])
        dump(vp, proof)
        dump(state, dict(completed=True, fingerprint=proof['fingerprint'], child=None))
        with self.assertRaisesRegex(ValueError, 'approved voice profile'):
            m.exact_voice()

    def test_job_binds_current_source_resource_and_immutable_voice_proof(self):
        proof, out, vp, *_ = self.fixture()
        tasks = m.qa.build_tasks(proof, m.qa.read(proof['timing']['path']))
        original = dict(identity=dict(tasks=tasks), voiceOutput=str(out), voiceEvidence=m.pin(vp), sourcePins=[])
        with patch.object(m, '_library_prepare_job', return_value=original):
            job = m.prepare_job()
        self.assertEqual(job['voiceEvidence'], m.pin(out / 'voice-complete-proof.json'))
        self.assertEqual(job['publishedVoiceEvidenceAudit'], m.pin(vp))
        self.assertEqual(job['identity']['currentVoiceWorkerSHA256'], m.PINS['run-solution-path-voice-v4.py'])
        self.assertEqual(job['identity']['resourceSourcePins']['prospect-refuge-resource-qualification.py'], m.PINS['prospect-refuge-resource-qualification.py'])
        self.assertEqual(job['fingerprint'], m.digest(job['identity']))


class ResourceAndEvidenceTests(unittest.TestCase):
    def launcher(self):
        args = [str(m.qa.PYTHON), '-u', str(HERE / 'run-solution-path-voice-qa-v4.py'), '--recognize', '--job', 'job.json']
        parent = dict(pid=100, ppid=50, create_time=10., name='python.exe', exe=str(m.qa.PYTHON), cmdline=args)
        own = dict(pid=101, ppid=100, create_time=10.05, name='python.exe', exe='C:/Anaconda3/envs/pytorch-gpu/python.exe', cmdline=args)
        return copy.deepcopy(parent), own, parent

    def test_exact_own_direct_venv_launcher_allowed(self):
        self.assertTrue(m.launcher_matches(*self.launcher()))

    def test_wrong_pid_rejected(self):
        info, own, parent = self.launcher(); info['pid'] += 1
        self.assertFalse(m.launcher_matches(info, own, parent))

    def test_reused_pid_creation_time_rejected(self):
        info, own, parent = self.launcher(); info['create_time'] += .1
        self.assertFalse(m.launcher_matches(info, own, parent))

    def test_wrong_executable_rejected(self):
        info, own, parent = self.launcher(); info['exe'] = 'C:/other/python.exe'
        self.assertFalse(m.launcher_matches(info, own, parent))

    def test_wrong_argv_rejected(self):
        info, own, parent = self.launcher(); info['cmdline'] = info['cmdline'] + ['foreign']
        self.assertFalse(m.launcher_matches(info, own, parent))

    def test_indirect_parent_rejected(self):
        info, own, parent = self.launcher(); own['ppid'] = 102
        self.assertFalse(m.launcher_matches(info, own, parent))

    def test_wrong_parent_chain_rejected(self):
        info, own, parent = self.launcher(); info['ppid'] = 999
        self.assertFalse(m.launcher_matches(info, own, parent))

    def test_unknown_launcher_identity_rejected(self):
        info, own, parent = self.launcher(); info['cmdline'] = None
        self.assertFalse(m.launcher_matches(info, own, parent))

    def test_other_recognizer_with_identical_args_not_our_parent(self):
        info, own, parent = self.launcher(); info['pid'] = 500
        self.assertFalse(m.launcher_matches(info, own, parent))
        self.assertIsNotNone(m._process_reason(info, own['pid']))

    def test_unrelated_executable_cannot_be_our_launcher(self):
        info, own, parent = self.launcher(); parent['exe'] = info['exe'] = 'C:/other/python.exe'
        self.assertFalse(m.launcher_matches(info, own, parent))

    def test_nonrecognize_parent_not_exempt(self):
        info, own, parent = self.launcher()
        for row in (info, own, parent): row['cmdline'] = [str(m.qa.PYTHON), str(Path(m.__file__)), '--execute']
        self.assertFalse(m.launcher_matches(info, own, parent))

    def test_foreign_old_recognizer_child_preserved(self):
        process = SimpleNamespace(pid=987654, info=dict(pid=987654, name='python.exe', cmdline=['python', 'run-selected-voice-qa.py', '--recognize']))
        with patch.object(m.qa.psutil, 'process_iter', return_value=[process]), \
             patch.object(m.qa.voice, 'identity', return_value=dict(pid=987654)):
            self.assertEqual(len(m.child_processes()), 1)

    def test_unknown_python_child_preserved(self):
        process = SimpleNamespace(pid=987654, info=dict(pid=987654, name='python.exe', cmdline=None))
        with patch.object(m.qa.psutil, 'process_iter', return_value=[process]):
            with self.assertRaises(m.Pending): m.child_processes()

    def test_blind_profile_unchanged_no_expected_prompt_or_alias(self):
        self.assertEqual(m.PROFILE['minimumFreeMiB'], 9216)
        for key in ('expectedPrompt', 'hotwords', 'aliases'): self.assertIsNone(m.PROFILE[key])
        self.assertEqual(m.qa.recognize.__code__.co_filename, str(m.BASE_PATH))
        self.assertEqual(m.qa.execute.__code__.co_filename, str(m.BASE_PATH))

    def test_resource_query_delegates_unchanged_after_source_check(self):
        with patch.object(m, '_library_resource_reason', return_value='strict9GiBdecline') as original:
            self.assertEqual(m.resource_reason(), 'strict9GiBdecline')
            original.assert_called_once_with()

    def test_literal_discrepancy_and_unknown_word_times_are_retained(self):
        task = dict(key='take-test', kind='take', expected='벽의 틈을 봅니다.', sceneId='test', offsetSeconds=0., durationSeconds=1.)
        raw = dict(text='벽의 등을 봅니다.', chunks=[dict(text='벽의', timestamp=[None, .2]), dict(text='등을', timestamp=[.2, .6])])
        record = m.qa.recognition_record(dict(fingerprint='a'*64), task, raw)
        self.assertEqual(record['text'], raw['text'])
        self.assertFalse(record['aliasesApplied'])
        self.assertTrue(record['boundaryFlags'])
        self.assertTrue(record['comparison']['characterDifferences'])
        self.assertEqual(record['comparison']['recognizedLiteral'], raw['text'])

    def test_pre_model_resource_decline75_never_imports_recognizer(self):
        with tempfile.TemporaryDirectory(prefix='asr-v4-decline-cpu-') as temp:
            root = Path(temp); task = dict(key='take-x'); identity = dict(tasks=[task])
            job = dict(output=str(root), voiceOutput=str(root), identity=identity, fingerprint=m.digest(identity), sourcePins=[])
            jp = dump(root/'job.json', job); decline = root/'resource-decline-test.json'
            with patch.object(m.qa, 'prepare_job', return_value=job), patch.object(m.qa, 'restore_raw_cache'), \
                 patch.object(m.qa, 'cached', return_value=None), patch.object(m.qa, 'resource_reason', return_value='Another scoped job holds the shared GPU lease'), \
                 patch.object(m.qa, 'module', side_effect=AssertionError('recognizer must not import')):
                self.assertEqual(m.qa.recognize(jp, decline), 75)
            receipt = m.qa.read(decline)
            self.assertFalse(receipt['modelLoaded'])
            self.assertEqual(receipt['phase'], 'before-model')

    def test_real_error_is_not_classified_as_resource75(self):
        source = m.BASE_PATH.read_text(encoding='utf-8')
        segment = source[source.index('def recognize('):source.index('def raw_level_review(')]
        self.assertLess(segment.index('except raw.PreModelResourceDeclined'), segment.index("trusted=module('selected_qa_trusted"))
        self.assertNotIn('except RuntimeError', segment)

    def test_guard_acquisition_race_is_temporary75_before_model(self):
        with tempfile.TemporaryDirectory(prefix='asr-v4-guard-race-cpu-') as temp:
            root = Path(temp); identity = dict(tasks=[dict(key='take-x')])
            job = dict(output=str(root), voiceOutput=str(root), identity=identity, fingerprint=m.digest(identity), sourcePins=[])
            jp = dump(root/'job.json', job); decline = root/'resource-decline-race.json'
            with patch.object(m.qa, 'prepare_job', return_value=job), patch.object(m.qa, 'restore_raw_cache'), \
                 patch.object(m.qa, 'cached', return_value=None), patch.object(m.qa, 'resource_reason', return_value=None), \
                 patch.object(m.qa, 'module', return_value=SimpleNamespace()), \
                 patch.object(m.qa.raw, 'acquire_guard_before_model', side_effect=m.qa.raw.PreModelResourceDeclined('synthetic lease race', 'guard-acquire')):
                self.assertEqual(m.qa.recognize(jp, decline), 75)
            self.assertEqual(m.qa.read(decline)['origin'], 'guard-acquire')

    def test_synthetic_model_failure_remains_fatal_not75(self):
        with tempfile.TemporaryDirectory(prefix='asr-v4-model-error-cpu-') as temp:
            root = Path(temp); identity = dict(tasks=[dict(key='take-x')])
            job = dict(output=str(root), voiceOutput=str(root), identity=identity, fingerprint=m.digest(identity), sourcePins=[])
            jp = dump(root/'job.json', job); decline = root/'resource-decline-not-created.json'
            def fail(device): raise RuntimeError('synthetic actual-model-error class')
            trusted = SimpleNamespace(MODEL=m.MODEL, load_recognizer=fail)
            with patch.object(m.qa, 'prepare_job', return_value=job), patch.object(m.qa, 'restore_raw_cache'), \
                 patch.object(m.qa, 'cached', return_value=None), patch.object(m.qa, 'resource_reason', return_value=None), \
                 patch.object(m.qa, 'module', side_effect=lambda name, path: trusted if 'trusted_blind' in name else SimpleNamespace()), \
                 patch.object(m.qa.raw, 'acquire_guard_before_model'):
                with self.assertRaisesRegex(RuntimeError, 'actual-model-error class'):
                    m.qa.recognize(jp, decline)
            self.assertFalse(decline.exists())

    def test_changed_adapter_source_pin_declines(self):
        with patch.object(m, 'SELF_SHA', '0' * 64):
            with self.assertRaisesRegex(RuntimeError, 'changed after import'): m.check_sources()

    def test_durable_launch_gap_preserves_unregistered_live_child(self):
        with tempfile.TemporaryDirectory(prefix='asr-v4-launchgap-cpu-') as temp:
            folder = Path(temp); job = dict(output=str(folder/'job'), identity={}, fingerprint='a'*64)
            closed = []
            worker = SimpleNamespace(update=lambda **kw: None, close=lambda remove: closed.append(remove))
            factory = SimpleNamespace(acquire=lambda: worker)
            child = SimpleNamespace(pid=9999, poll=lambda: None)
            def process_identity(pid=None):
                if pid is not None: raise RuntimeError('synthetic child registration failure')
                return dict(pid=1, createTime=1., argv=['synthetic'], commandSHA256='a'*64)
            with patch.object(m.qa.runtime, 'SingleWorker', return_value=factory), \
                 patch.object(m.qa, 'STATE', folder/'state.json'), patch.object(m.qa, 'WORKER', folder/'worker.json'), \
                 patch.object(m.qa, 'child_processes', return_value=[]), patch.object(m.qa, 'prepare_job', return_value=job), \
                 patch.object(m.qa, 'restore_raw_cache'), patch.object(m.qa, 'summary', return_value=None), \
                 patch.object(m.qa, 'resource_reason', return_value=None), patch.object(m.qa.voice, 'identity', side_effect=process_identity), \
                 patch.object(m.qa.subprocess, 'Popen', return_value=child):
                with self.assertRaisesRegex(RuntimeError, 'registration failure'): m.qa.execute(.1)
            self.assertEqual(closed, [False])
            self.assertTrue(m.qa.read(folder/'state.json')['childStillAlive'])

    def test_default_cli_pending_no_summary_or_resource_or_launch(self):
        with patch('sys.argv', [str(Path(m.__file__))]), patch.object(m.qa, 'prepare_job', side_effect=m.Pending('missing actual voice')), \
             patch.object(m.qa, 'summary', side_effect=AssertionError('no summary write')), \
             patch.object(m.qa, 'resource_reason', side_effect=AssertionError('no resource queries')), \
             patch.object(m.qa.subprocess, 'Popen', side_effect=AssertionError('no job')):
            text = io.StringIO()
            with redirect_stdout(text): m.qa.main()
            result = json.loads(text.getvalue())
            self.assertFalse(result['ready'])
            self.assertFalse(result['modelLoaded'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
