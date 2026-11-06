"""CPU-only literal-comparison/cache/boundary fixtures; never imports an ASR model."""
import copy, importlib.util, json, shutil, struct, sys, tempfile, unittest, wave
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
            timing=dict(sha256='timing'),sceneWavs=[dict(path=f's{i:02}.wav',sha256=str(i),durationSeconds=18,
                pcmSHA256='pcm'+str(i),sampleRate=24000,channels=1,sampleWidthBytes=2,frames=18*24000) for i in range(1,7)])
        with patch.multiple(asr,MODEL=model,TRUSTED=trusted,PROOF=proof),patch.object(asr,'exact_voice',return_value=(self.base,evidence,timing)):
            job=asr.prepare_job()
        joins=[t for t in job['identity']['tasks'] if t['kind']=='boundary']
        s34=next(t for t in joins if t['previousScene']=='s03')
        self.assertEqual(s34['beginSample'],50*24000);self.assertEqual(s34['endSample'],58*24000)
        self.assertIsNone(job['identity']['profile']['expectedPrompt']);self.assertIsNone(job['identity']['profile']['aliases'])
        self.assertEqual(evidence['aggregateWav']['durationSeconds'],total)

    def fixture_reuse(self):
        parent=self.base/'selected03-02';output=parent/'voice-v1';snapshot=parent/'voice-preserved'/'exact-snapshot'
        (output/'chunks').mkdir(parents=True);(snapshot/'chunks').mkdir(parents=True)
        texts=[f'게임플레이 메트릭스 원문 {i}' for i in range(1,7)]
        new_texts=[f'수정된 문단 {i}' if i in (2,3) else texts[i-1] for i in range(1,7)]
        old_identity={'scenes':[dict(id=f's{i:02}',lines=[text]) for i,text in enumerate(texts,1)]}
        new_identity={'scenes':[dict(id=f's{i:02}',lines=[text]) for i,text in enumerate(new_texts,1)]}
        old_fp=asr.digest(old_identity);new_fp=asr.digest(new_identity)
        asr.save(snapshot/'voice-inputs.json',dict(protocol=asr.voice.PROTOCOL,fingerprint=old_fp,identity=old_identity))
        def wav(path,count,value):
            with wave.open(str(path),'wb') as w:
                w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000);w.writeframes(struct.pack('<h',value)*count)
        old_tasks=[];new_tasks=[];entries=[];old_pos=0;new_pos=0
        for i in range(1,7):
            old=snapshot/'chunks'/f's{i:02}-scene.wav';new=output/'chunks'/old.name
            wav(old,4800,i)
            if i in (2,3):wav(new,4800+i*2400,100+i)
            else:shutil.copyfile(old,new)
            oi=asr.voice.wav_info(old);ni=asr.voice.wav_info(new)
            task=dict(key=f'paragraph-s{i:02}',kind='paragraph',sceneId=f's{i:02}',path=str(new),audioSHA256=oi['sha256'],
                      offsetSeconds=old_pos,durationSeconds=oi['durationSeconds'],expected=texts[i-1])
            old_tasks.append(task);entries.append(dict(scene_id=f's{i:02}',text=texts[i-1],start=old_pos,end=old_pos+oi['durationSeconds']))
            old_pos+=oi['durationSeconds']
            new_tasks.append(dict(task,path=str(new),audioSHA256=ni['sha256'],pcmIdentity=asr.pcm_identity(ni),
                offsetSeconds=new_pos,durationSeconds=ni['durationSeconds'],expected=new_texts[i-1]))
            new_pos+=ni['durationSeconds']
        asr.save(snapshot/'narration.timing.json',dict(entries=entries))
        wav(snapshot/'narration.wav',28800,0)
        old_job_identity=dict(voiceFingerprint=old_fp,aggregateSHA256=asr.voice.sha(snapshot/'narration.wav'),
            timingSHA256=asr.voice.sha(snapshot/'narration.timing.json'),modelPins=[{'path':'model.safetensors','sha256':'pinned-model'}],
            trustedUtilitySHA256='pinned-trusted-implementation',profile=copy.deepcopy(asr.PROFILE),tasks=old_tasks)
        old_asr_fp=asr.digest(old_job_identity)
        relative=Path('review/independent-asr-v1')/old_asr_fp[:24]
        old_job=dict(protocol='architectural111-first-asr-v1',fingerprint=old_asr_fp,identity=old_job_identity,
            modelPath=str(asr.MODEL),output=str(output/relative))
        job_path=snapshot/relative/'job.json';asr.save(job_path,old_job)
        for task in old_tasks:
            raw=dict(text='게임플레이 매트릭스 오류 보존',chunks=[dict(text='매트릭스',timestamp=[.02,.10]),dict(text='알수없음',timestamp=[None,.18])])
            asr.save(job_path.parent/(task['key']+'.json'),asr.recognition_record(old_job,task,raw))
        files=[dict(path=p.relative_to(snapshot).as_posix(),sha256=asr.voice.sha(p)) for p in sorted(snapshot.rglob('*')) if p.is_file()]
        proof=snapshot/'archive-proof-explicit.json';asr.save(proof,dict(original=str(output),oldFingerprint=old_fp,newFingerprint=new_fp,files=files))
        new_job_identity=dict(old_job_identity,voiceFingerprint=new_fp,aggregateSHA256='new-aggregate',timingSHA256='new-timing',tasks=new_tasks)
        # All joins intentionally remain new, even though a paragraph is unchanged.
        new_tasks.extend(dict(key=f'join-s{i:02}-s{i+1:02}',kind='boundary',offsetSeconds=i/5,durationSeconds=.2,
                             expectedContextOnly={'previousEnding':'끝','nextBeginning':'시작'}) for i in range(1,6))
        with patch.multiple(asr.voice,VOICE_PARENT=parent,OUTPUT=output):
            source=asr.load_reuse_source(job_path,proof,new_fp)
        new_job_identity['reuseSource']=source['pins'];fp=asr.digest(new_job_identity)
        new_job=dict(fingerprint=fp,identity=new_job_identity,output=str(output/'review/independent-asr-v1'/fp[:24]))
        return parent,output,snapshot,proof,job_path,new_job

    def test_reuse_four_exact_paragraphs_rebases_words_and_preserves_raw_errors(self):
        parent,output,snapshot,proof,old_path,job=self.fixture_reuse()
        original={p:asr.voice.sha(p) for p in snapshot.rglob('*') if p.is_file()}
        with patch.multiple(asr.voice,VOICE_PARENT=parent,OUTPUT=output),patch.object(asr.subprocess,'Popen',side_effect=AssertionError('CPU reuse must not launch model')):
            reused=asr.apply_paragraph_reuse(job)
            self.assertEqual(reused,['paragraph-s01','paragraph-s04','paragraph-s05','paragraph-s06'])
            task=next(t for t in job['identity']['tasks'] if t['key']=='paragraph-s04');new=asr.read_cache(job,task)
            old=asr.read(old_path.parent/'paragraph-s04.json')
            self.assertEqual(new['rawRecognition'],old['rawRecognition'])
            self.assertAlmostEqual(new['globalWords'][0]['timestamp'][0],task['offsetSeconds']+.02)
            self.assertNotEqual(new['globalWords'],old['globalWords'])
            self.assertEqual(new['boundaryFlags'],['unknown-word-boundary'])
            self.assertTrue(new['comparison']['characterDifferences']);self.assertFalse(new['comparison']['automaticSpeechPass'])
            self.assertFalse(new['humanListening']);self.assertFalse(new['reuse']['modelLoadedForThisTask'])
            self.assertEqual(len([t for t in job['identity']['tasks'] if t['kind']=='boundary' and asr.read_cache(job,t) is None]),5)
            self.assertEqual(asr.apply_paragraph_reuse(job),reused)  # Idempotent, no overwrite.
        self.assertEqual({p:asr.voice.sha(p) for p in snapshot.rglob('*') if p.is_file()},original)

    def test_reuse_rejects_unproven_snapshot_profile_and_tampered_archive(self):
        parent,output,snapshot,proof,old_path,job=self.fixture_reuse()
        with patch.multiple(asr.voice,VOICE_PARENT=parent,OUTPUT=output):
            with self.assertRaises(AssertionError):asr.load_reuse_source(old_path,self.base/'archive-proof-outside.json',job['identity']['voiceFingerprint'])
            bad=copy.deepcopy(job);bad['identity']['profile']['dtype']='float32'
            with self.assertRaisesRegex(AssertionError,'profile differs'):asr.apply_paragraph_reuse(bad)
            old_path.write_bytes(old_path.read_bytes()+b' ')
            with self.assertRaisesRegex(AssertionError,'hash mismatch'):asr.apply_paragraph_reuse(job)

    def test_reuse_requires_literal_and_complete_pcm_identity(self):
        parent,output,snapshot,proof,old_path,job=self.fixture_reuse()
        with patch.multiple(asr.voice,VOICE_PARENT=parent,OUTPUT=output):
            changed=copy.deepcopy(job);changed['identity']['tasks'][0]['expected']='새 문장'
            changed['fingerprint']=asr.digest(changed['identity'])
            changed['output']=str(output/'review/independent-asr-v1'/changed['fingerprint'][:24])
            self.assertEqual(asr.apply_paragraph_reuse(changed),['paragraph-s04','paragraph-s05','paragraph-s06'])
            target=Path(job['identity']['tasks'][0]['path']);raw=target.read_bytes();target.write_bytes(raw[:-2]+b'\x7f\x00')
            with self.assertRaisesRegex(AssertionError,'PCM identity'):asr.apply_paragraph_reuse(job)

    def test_reuse_cache_timestamps_cannot_be_changed_after_rebasing(self):
        parent,output,snapshot,proof,old_path,job=self.fixture_reuse()
        with patch.multiple(asr.voice,VOICE_PARENT=parent,OUTPUT=output):
            asr.apply_paragraph_reuse(job);task=job['identity']['tasks'][3]
            cache=Path(job['output'])/(task['key']+'.json');data=asr.read(cache)
            data['globalWords'][0]['timestamp'][0]+=.5;asr.save(cache,data)
            with self.assertRaisesRegex(AssertionError,'timeline or literal'):asr.read_cache(job,task)

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
