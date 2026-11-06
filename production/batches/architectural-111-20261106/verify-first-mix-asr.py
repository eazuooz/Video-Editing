"""CPU-only exact mixed-PCM coverage/cache/resource regression fixtures."""
import copy, importlib.util, sys, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
import soundfile as sf

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
spec=importlib.util.spec_from_file_location('first_mix_asr_cpu_fixture',HERE/'run-first-mix-asr.py')
mix=importlib.util.module_from_spec(spec);spec.loader.exec_module(mix)


class MixAsrTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='yamyam-first-mix-asr-cpu-');self.base=Path(self.tmp.name)
        self.folder=self.base/'audio-preparation-v1'/'version';self.folder.mkdir(parents=True)
        self.model=self.base/'model';self.model.mkdir();(self.model/'model.safetensors').write_bytes(b'not a model; fixture only')
        self.trusted=self.base/'trusted.py';self.trusted.write_text('# CPU fixture',encoding='utf-8')
        self.project=self.base/'project';self.project.mkdir()
        self.context=patch.multiple(mix,BASE=self.base);self.context.start()
        self.raw_context=patch.multiple(mix.raw,MODEL=self.model,TRUSTED=self.trusted,PROJECT=self.project);self.raw_context.start()
        self.evidence,self.levels=self.fixture()
        mix.save(self.project/'narration-draft.json',dict(narrationKo=[p['text'] for p in self.levels['paragraphs']]))
        raw_review=self.base/'raw-review.json';mix.save(raw_review,dict(voiceFingerprint='raw-fp',aggregateSHA256='raw-pcm',paragraphs=[{}]*6))
        self.mix_path=self.folder/'final-mix.wav';sf.write(self.mix_path,np.zeros((12012,2),np.float32),48000,subtype='FLOAT')
        self.level_path=self.folder/'line-levels.json';mix.save(self.level_path,self.levels)
        self.build=dict(status='audio-prepared-final-mix-review-pending',output=str(self.folder),fingerprint='audio-build-fp',
            rawVoiceFingerprint='raw-fp',rawVoiceSha256='raw-pcm',voiceOffsetSeconds=0,insertedSamples=0,trimmedSamples=0,rawPcmModified=False,
            mixRate=48000,mixFrames=12012,artifacts={'line-levels.json':dict(file='line-levels.json',sha256=mix.raw.voice.sha(self.level_path)),
                'final-mix.wav':dict(file='final-mix.wav',sha256=mix.raw.voice.sha(self.mix_path))},
            rawVoiceAsr=dict(path=str(raw_review),sha256=mix.raw.voice.sha(raw_review)))
        self.path=self.folder/'audio-build.json';mix.save(self.path,self.build)
        self.voice_patch=patch.object(mix.raw,'exact_voice',return_value=(self.base,self.evidence,{}));self.voice_patch.start()

    def tearDown(self):self.voice_patch.stop();self.raw_context.stop();self.context.stop();self.tmp.cleanup()

    def fixture(self):
        rows=[];chunks=[];position=0
        for i in range(1,7):
            n=1001;rows.append(dict(sceneId=f's{i:02}',destinationSampleRange=[position,position+n],trimmedSamples=0,insertedSamples=0,
                rawTakeSha256=f'chunk-{i}',rate=24000,text=f'메트릭스 문단 {i}'))
            chunks.append(dict(frames=n,sha256=f'chunk-{i}'));position+=n
        evidence=dict(fingerprint='raw-fp',aggregateWav=dict(sampleRate=24000,frames=position,sha256='raw-pcm'),sceneWavs=chunks)
        levels=dict(rawRate=24000,frames=position,rawVoiceSha256='raw-pcm',voiceFingerprint='raw-fp',allRawPcmPreserved=True,
            allOriginalWordBoundariesPreserved=True,paragraphs=rows)
        return evidence,levels

    def test_all_actual_stereo_mix_samples_covered_once_including_odd_boundaries(self):
        job=mix.prepare_job(self.path);tasks=job['identity']['tasks']
        self.assertEqual(tasks[0]['beginSample'],0);self.assertEqual(tasks[-1]['endSample'],12012)
        self.assertEqual(sum(t['endSample']-t['beginSample'] for t in tasks),12012)
        for a,b in zip(tasks,tasks[1:]):self.assertEqual(a['endSample'],b['beginSample'])
        self.assertEqual(tasks[1]['beginSample'],2002);self.assertIsNone(job['identity']['profile']['expectedPrompt'])
        self.assertFalse(job['rawVoiceAsr']['reusedAsMixedRecognition'])

    def test_overlap_gap_truncation_or_unretained_boundaries_rejected(self):
        info=dict(sampleRate=48000,channels=2,frames=12012)
        for key,value in [('allOriginalWordBoundariesPreserved',False),('frames',6005)]:
            changed=copy.deepcopy(self.levels);changed[key]=value
            with self.assertRaises(AssertionError):mix.coverage(self.evidence,changed,info)
        changed=copy.deepcopy(self.levels);changed['paragraphs'][3]['destinationSampleRange'][0]+=1
        with self.assertRaises(AssertionError):mix.coverage(self.evidence,changed,info)
        with self.assertRaises(AssertionError):mix.coverage(self.evidence,self.levels,dict(info,frames=12010))

    def test_changed_actual_mix_invalidates_job_and_never_accepts_old_raw_or_mix_cache(self):
        old=mix.prepare_job(self.path)
        pcm=np.zeros((12012,2),np.float32);pcm[100,0]=.1
        sf.write(self.mix_path,pcm,48000,subtype='FLOAT')
        with self.assertRaisesRegex(AssertionError,'mixed PCM differs'):mix.prepare_job(self.path)
        self.build['artifacts']['final-mix.wav']['sha256']=mix.raw.voice.sha(self.mix_path);mix.save(self.path,self.build)
        new=mix.prepare_job(self.path);self.assertNotEqual(old['fingerprint'],new['fingerprint'])
        task=new['identity']['tasks'][0]
        mix.save(Path(new['output'])/(task['key']+'.json'),dict(fingerprint=old['fingerprint'],task=task,mixSHA256=old['identity']['mix']['sha256']))
        with self.assertRaises(AssertionError):mix.cached(new,task)

    def test_complete_summary_keeps_literal_ae_e_discrepancy_and_never_approves_speech(self):
        job=mix.prepare_job(self.path)
        for task in job['identity']['tasks']:
            actual=task['expected'].replace('메트릭스','매트릭스')
            mix.save(Path(job['output'])/(task['key']+'.json'),dict(fingerprint=job['fingerprint'],task=task,
                mixSHA256=job['identity']['mix']['sha256'],inputKind='actual-normalized-plus-BGM-final-mix',
                expectedPrompt=None,aliasesApplied=False,comparison=mix.raw.comparison(task['expected'],actual)))
        with patch.object(mix.subprocess,'Popen',side_effect=AssertionError('No model in CPU summary')):result=mix.summary(job)
        self.assertTrue(result['fullActualMixCoverage']);self.assertEqual(result['coveredSamples'],12012)
        self.assertTrue(result['paragraphs'][0]['comparison']['characterDifferences'])
        self.assertFalse(result['automaticSpeechPass']);self.assertFalse(result['humanListening']);self.assertFalse(result['rawRecognitionsReused'])

    def test_temporary_before_model_decline_has_receipt_but_real_model_failure_propagates(self):
        job=mix.prepare_job(self.path);path=Path(job['output'])/'job.json';mix.save(path,job)
        decline=path.parent/'resource-decline-test.json'
        with patch.object(mix,'recognize_job',side_effect=mix.raw.PreModelResourceDeclined('Foreign lease preserved','mixed-child-resource-check')):
            self.assertEqual(mix.recognize_entry(path,decline),75)
        with self.assertRaises(mix.raw.ResourceRetry):mix.raw.accept_child_exit(75,decline,job,'preserved.log')
        with patch.object(mix,'recognize_job',side_effect=RuntimeError('Actual model load error')):
            with self.assertRaisesRegex(RuntimeError,'Actual model load error'):mix.recognize_entry(path,decline)


if __name__=='__main__':unittest.main(verbosity=2)
