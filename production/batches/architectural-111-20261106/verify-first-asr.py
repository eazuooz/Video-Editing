"""CPU-only literal-comparison/cache/boundary fixtures; never imports an ASR model."""
import copy, importlib.util, sys, tempfile, unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
spec=importlib.util.spec_from_file_location('first_asr_cpu_test',HERE/'run-first-asr.py')
asr=importlib.util.module_from_spec(spec);spec.loader.exec_module(asr)


class FirstAsrTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='yamyam-first-asr-cpu-');self.base=Path(self.tmp.name)
    def tearDown(self):self.tmp.cleanup()

    def test_literal_errors_and_acronyms_are_not_hidden_by_aliases(self):
        for expected,actual in [('게임플레이 메트릭스입니다','게임플레이 매트릭스입니다'),('API를 씁니다','에이피아이를 씁니다')]:
            result=asr.comparison(expected,actual)
            self.assertTrue(result['characterDifferences']);self.assertFalse(result['aliasesApplied'])
            self.assertFalse(result['automaticSpeechPass']);self.assertEqual(result['recognizedLiteral'],actual)

    def test_formatting_only_view_preserves_literal_word_differences(self):
        result=asr.comparison('수레 옆입니다.','수레옆입니다')
        self.assertEqual(result['rawCharacterSimilarity'],1)
        self.assertTrue(result['wordDifferences']);self.assertFalse(result['automaticSpeechPass'])

    def fixture_job(self):
        tasks=[dict(key=f'paragraph-s{i:02}',kind='paragraph',sceneId=f's{i:02}',expected='원래 문장',offsetSeconds=(i-1)*10,durationSeconds=10) for i in range(1,7)]
        tasks += [dict(key=f'join-s{i:02}-s{i+1:02}',kind='boundary',expectedContextOnly={'previousEnding':'끝입니다','nextBeginning':'다음입니다'}) for i in range(1,6)]
        return dict(fingerprint='test-fingerprint',output=str(self.base/'review'),identity=dict(tasks=tasks,voiceFingerprint='voice',aggregateSHA256='audio'))

    def fill_caches(self,job):
        for task in job['identity']['tasks']:
            words=[]
            if task['kind']=='paragraph':
                start=task['offsetSeconds']+.1;end=task['offsetSeconds']+9.9
                if task['sceneId']=='s03':end=28.4
                if task['sceneId']=='s04':start=31.07
                words=[dict(text='원래 문장',timestamp=[start,end])]
            asr.save(Path(job['output'])/(task['key']+'.json'),dict(fingerprint=job['fingerprint'],task=task,
                text='원래 문장',globalWords=words,expectedPrompt=None,aliasesApplied=False,pcmModified=False))

    def test_missing_or_other_fingerprint_cache_cannot_be_called_complete(self):
        job=self.fixture_job();self.assertIsNone(asr.summary(job));self.fill_caches(job)
        p=Path(job['output'])/'paragraph-s01.json';d=asr.read(p);d['fingerprint']='other';asr.save(p,d)
        with self.assertRaises(AssertionError):asr.summary(job)

    def test_long_boundary_silence_is_observed_without_trim_or_retakes(self):
        job=self.fixture_job();self.fill_caches(job)
        with patch.object(asr.subprocess,'Popen',side_effect=AssertionError('No model child in CPU summary')):
            result=asr.summary(job)
        boundary=next(x for x in result['boundaryObservations'] if x['previous']=='s03')
        self.assertAlmostEqual(boundary['recognizedWordGapSeconds'],2.67)
        self.assertEqual(len(result['boundaryWindows']),5)
        self.assertFalse(result['pcmModified']);self.assertFalse(result['humanListening']);self.assertFalse(result['automaticSpeechPass'])

    def test_boundary_windows_use_real_sample_indices_and_preserve_source_duration(self):
        model=self.base/'model';model.mkdir();(model/'model.safetensors').write_bytes(b'CPU fixture, not a model')
        trusted=self.base/'trusted.py';trusted.write_text('# CPU fixture')
        proof=self.base/'proof.json';asr.save(proof,{'fixture':True})
        total=2728322/24000
        timing={'entries':[dict(scene_id=f's{i:02}',start=(i-1)*18,end=i*18,text=f'문장 {i}') for i in range(1,7)]}
        evidence=dict(fingerprint='voice',aggregateWav=dict(path=str(self.base/'immutable.wav'),sha256='audio',durationSeconds=total,sampleRate=24000),
            timing=dict(sha256='timing'),sceneWavs=[dict(path=f's{i:02}.wav',sha256=str(i),durationSeconds=18) for i in range(1,7)])
        with patch.multiple(asr,MODEL=model,TRUSTED=trusted,PROOF=proof),patch.object(asr,'exact_voice',return_value=(self.base,evidence,timing)):
            job=asr.prepare_job()
        joins=[t for t in job['identity']['tasks'] if t['kind']=='boundary']
        s34=next(t for t in joins if t['previousScene']=='s03')
        self.assertEqual(s34['beginSample'],50*24000);self.assertEqual(s34['endSample'],58*24000)
        self.assertIsNone(job['identity']['profile']['expectedPrompt']);self.assertIsNone(job['identity']['profile']['aliases'])
        self.assertEqual(evidence['aggregateWav']['durationSeconds'],total)

    def test_child_resource_race_emits75_receipt_and_parent_retries(self):
        job=self.fixture_job();job_path=self.base/'job.json';asr.save(job_path,job)
        decline=Path(job['output'])/'resource-decline-test.json'
        with patch.object(asr,'recognize_job',side_effect=asr.PreModelResourceDeclined('Another scoped job holds the shared GPU lease','child-resource-check')):
            self.assertEqual(asr.recognize_entry(job_path,decline),75)
        record=asr.read(decline);self.assertFalse(record['modelLoaded']);self.assertEqual(record['phase'],'before-model')
        with self.assertRaises(asr.ResourceRetry) as ctx:asr.accept_child_exit(75,decline,job,'preserved.log')
        self.assertEqual(ctx.exception.record,record)
        # A bare75 from a model is not evidence of a pre-model resource race.
        with self.assertRaises(RuntimeError):asr.accept_child_exit(75,self.base/'absent.json',job,'model.log')

    def test_guard_acquisition_race_returns_to_finite_parent_and_restores_time(self):
        original_time=SimpleNamespace(time=lambda:123,sleep=lambda seconds:self.fail('No unbounded guard wait'))
        guard=SimpleNamespace(time=original_time)
        guard.schedule_gpu_handoff=lambda *args:guard.time.sleep(10)
        with self.assertRaises(asr.PreModelResourceDeclined):asr.acquire_guard_before_model(guard)
        self.assertIs(guard.time,original_time)
        guard.schedule_gpu_handoff=lambda *args:(_ for _ in ()).throw(SystemExit('GPU capacity is insufficient for this profile: fixture'))
        with self.assertRaises(asr.PreModelResourceDeclined):asr.acquire_guard_before_model(guard)
        self.assertIs(guard.time,original_time)
        guard.schedule_gpu_handoff=lambda *args:(_ for _ in ()).throw(SystemExit('The GPU handoff owner exited unexpectedly. Inspect the unknown lease.'))
        with self.assertRaises(SystemExit):asr.acquire_guard_before_model(guard)

    def test_actual_model_or_recognition_error_is_never_classified_temporary(self):
        job=self.fixture_job();path=self.base/'job.json';asr.save(path,job)
        decline=Path(job['output'])/'resource-decline-error.json'
        with patch.object(asr,'recognize_job',side_effect=RuntimeError('CUDA model load failed')):
            with self.assertRaisesRegex(RuntimeError,'model load failed'):asr.recognize_entry(path,decline)
        self.assertFalse(decline.exists())
        with self.assertRaisesRegex(RuntimeError,'Model/recognition errors are not retried'):
            asr.accept_child_exit(1,decline,job,'actual-error.log')


if __name__=='__main__':unittest.main(verbosity=2)
