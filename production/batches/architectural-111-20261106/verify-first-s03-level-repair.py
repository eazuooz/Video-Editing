"""CPU-only S03 semantic-item, unchanged-five and exact-assembly fixtures."""
import copy, importlib.util, sys, tempfile, unittest, wave
from pathlib import Path
from unittest.mock import patch
import numpy as np
import soundfile as sf

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
spec=importlib.util.spec_from_file_location('s03_repair_cpu_fixture',HERE/'run-first-s03-level-repair.py')
repair=importlib.util.module_from_spec(spec);spec.loader.exec_module(repair)


class S03RepairTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='yamyam-s03-repair-cpu-');self.root=Path(self.tmp.name)
        self.output=self.root/'shared/output/architectural-111-20261106/03-02/voice-v1';self.output.mkdir(parents=True)
        self.project=self.root/'projects'/repair.voice.SLUG;self.project.mkdir(parents=True)
        self.base=self.output/'subtakes-v3';self.base.mkdir()
        self.context=patch.multiple(repair,ROOT=self.root);self.context.start()
        self.voice_context=patch.multiple(repair.voice,ROOT=self.root,VOICE_PARENT=self.output.parent,OUTPUT=self.output,
            PROJECT_DIR=self.project,MANIFEST=self.project/'manifest.json',STATE=self.root/'voice-state.json',WORKER=self.root/'voice-worker.json');self.voice_context.start()
        self.scenes=[dict(id=f's{i:02}',lines=[f'변경 없는 문단 {i}.']) for i in range(1,7)]
        self.scenes[2]['lines']=['먼저 상황과 틈을 봅니다. 두 옆으로 나뉘는 거죠.','이 틈보다 몸이 크면 막힙니다. 캡슐과 위쪽 카메라를 봅니다.']
        self.prov=repair.voice.synthesis_identity(self.scenes,dict(engine='qwen3-tts',language='Korean',renderMode='scene',sceneGapSeconds=0,edgeFadeSeconds=0),
            dict(exampleSeconds=0,narrationPlacement='continuous-across-example-and-explanation'),[dict(path='model',sha256='weights')],'reference','reference-text')
        self.prov.update(sceneIds=[s['id'] for s in self.scenes],spokenLines=[' '.join(s['lines']) for s in self.scenes],sceneGapSeconds=0,
            audit=dict(engineSHA256=repair.voice.sha(repair.voice.ENGINE)))
        self.job=repair.validate(self.prov)
        repair.save(repair.voice.MANIFEST,dict(slug=repair.voice.SLUG,paths=dict(script='old-script'),editing={},
            tts=dict(renderMode='scene',reference='same-reference',referenceText='same-reference-text',model='same-model',outputDir='old',filenameStem='narration',edgeFadeSeconds=0)))
        self.pins={}
        for sid in repair.OTHERS:
            path=self.output/'chunks'/f'{sid}-scene.wav';path.parent.mkdir(parents=True,exist_ok=True)
            sf.write(path,np.ones(2401,np.float32)*.03,24000,subtype='PCM_16')
            self.pins[sid]=repair.voice.wav_info(path)
        repair.save(self.output/'voice-inputs.json',dict(protocol=repair.voice.PROTOCOL,fingerprint=self.prov['fingerprint'],identity=self.prov['identity'],
            verifiedSceneReuse=dict(reusedScenes=[dict(sceneId=sid,**pin) for sid,pin in self.pins.items()])))

    def tearDown(self):self.voice_context.stop();self.context.stop();self.tmp.cleanup()

    def completed_parts(self):
        generated=self.base/'attempts/fixture/generated'
        for i,sid in enumerate(repair.PARTS):
            path=generated/'chunks'/f'{sid}-scene.wav';path.parent.mkdir(parents=True,exist_ok=True)
            count=24001+i*2400;values=(.06*np.sin(np.arange(count)*.07)).astype(np.float32)
            values[:101]=0;values[-317:]=0
            sf.write(path,values,24000,subtype='PCM_16')
        repair.capture_completed_components(self.base,self.job,generated,list(repair.PARTS))
        return generated

    def test_two_distinct_semantic_ids_never_group_back_into_one_long_scene(self):
        attempt,manifest,_=repair.subrequest(self.prov,self.job,self.base,list(repair.PARTS))
        doc=repair.read(manifest);script=repair.read(self.root/doc['paths']['script'])
        self.assertEqual([s['id'] for s in script['scenes']],list(repair.PARTS))
        self.assertEqual([len(s['lines']) for s in script['scenes']],[1,1])
        self.assertEqual(' '.join(s['lines'][0] for s in script['scenes']),self.prov['spokenLines'][2])
        self.assertEqual(doc['tts']['renderMode'],'scene');self.assertEqual(doc['tts']['reference'],'same-reference')
        self.assertNotIn('s01',[s['id'] for s in script['scenes']])

    def test_exact_five_originals_and_all_component_samples_survive_derived_join(self):
        self.completed_parts();before=repair.other_pins(self.prov,self.output)
        report=repair.join_s03(self.output,self.base,self.job)
        self.assertEqual(repair.other_pins(self.prov,self.output),before)
        self.assertEqual(report['frames'],50402);self.assertEqual(report['insertedSamples'],0);self.assertEqual(report['trimmedSamples'],0)
        self.assertEqual(report['components'][0]['destinationSampleRange'],[0,24001])
        self.assertEqual(report['components'][1]['destinationSampleRange'],[24001,50402])
        self.assertFalse(report['canonicalS03IsUnprocessedRaw']);self.assertFalse(report['nestedEngineAggregateAdopted'])
        for row in report['components']:
            self.assertEqual(repair.voice.sha(row['raw']['path']),row['raw']['sha256'])
            pcm,_=sf.read(row['normalizedPath'],dtype='float32');self.assertTrue(np.all(pcm[:101]==0));self.assertTrue(np.all(pcm[-317:]==0))
        self.assertEqual(repair.join_s03(self.output,self.base,self.job),report)

    def test_canonical_aggregate_is_exact_six_chunk_pcm_without_hidden_fades(self):
        self.completed_parts();report=repair.join_s03(self.output,self.base,self.job);proof=repair.assemble_exact(self.prov,self.output,report)
        payload=[]
        for sid in self.prov['sceneIds']:
            with wave.open(str(self.output/'chunks'/f'{sid}-scene.wav'),'rb') as source:payload.append(source.readframes(source.getnframes()))
        with wave.open(str(self.output/'narration.wav'),'rb') as source:actual=source.readframes(source.getnframes())
        self.assertEqual(actual,b''.join(payload));self.assertTrue(proof['s03LevelRepair']['aggregateIsExactCanonicalChunkPcmConcatenation'])
        self.assertFalse(proof['s03LevelRepair']['hiddenEdgeFadesApplied']);self.assertFalse(proof['sceneWavs'][2]['canonicalUnprocessedRaw'])
        timing=repair.read(self.output/'narration.timing.json');self.assertEqual(len(timing['entries']),6)
        self.assertEqual(timing['entries'][2]['text'],self.prov['spokenLines'][2])
        self.assertEqual(repair.assemble_exact(self.prov,self.output,report)['aggregateWav']['sha256'],proof['aggregateWav']['sha256'])

    def test_changed_other_scene_or_changed_component_proof_is_fatal(self):
        self.completed_parts();path=self.output/'chunks/s04-scene.wav';data=bytearray(path.read_bytes());data[-1]^=1;path.write_bytes(data)
        with self.assertRaises(AssertionError):repair.other_pins(self.prov,self.output)
        row=repair.components(self.base,self.job)['s03-a'];path=Path(row['path']);data=bytearray(path.read_bytes());data[-1]^=1;path.write_bytes(data)
        with self.assertRaises(AssertionError):repair.components(self.base,self.job)

    def test_resume_request_excludes_a_verified_completed_component(self):
        generated=self.completed_parts();records=repair.read(self.base/'component-progress.json');records['components'].pop('s03-b')
        repair.save(self.base/'component-progress.json',records)
        present=repair.components(self.base,self.job);missing=[s for s in repair.PARTS if s not in present]
        _,manifest,_=repair.subrequest(self.prov,self.job,self.base,missing)
        script=repair.read(self.root/repair.read(manifest)['paths']['script'])
        self.assertEqual([s['id'] for s in script['scenes']],['s03-b'])
        self.assertTrue((generated/'chunks/s03-a-scene.wav').exists())

    def test_interrupted_child_keeps_same_voice_lock_state_and_never_clears_foreign_lease(self):
        lease=self.root/'shared/output/GPU_HANDOFF.json';repair.save(lease,dict(project='foreign',token='keep-exact'))
        before=lease.read_bytes();identity=repair.voice.native.identity
        class Child:
            pid=999999999
            def wait(self):raise KeyboardInterrupt('CPU fixture')
            def poll(self):return None
        with (patch.object(sys,'argv',['run-first-s03-level-repair.py','--execute','--wait-hours','1']),
            patch.object(repair.voice,'preparation',return_value=self.prov),
            patch.object(repair.voice,'prepare_output',return_value=self.output),
            patch.object(repair.voice,'same_project_children',return_value=[]),
            patch.object(repair.voice.native,'busy_reason',return_value=None),
            patch.object(repair.voice.native,'identity',side_effect=lambda pid=None:dict(pid=Child.pid,createTime=123) if pid else identity()),
            patch.object(repair.subprocess,'Popen',return_value=Child())):
            with self.assertRaises(KeyboardInterrupt):repair.main()
        state=repair.read(repair.voice.STATE)
        self.assertTrue(state['childStillAlive']);self.assertTrue(repair.voice.WORKER.exists())
        self.assertEqual(state['child']['pid'],Child.pid);self.assertEqual(lease.read_bytes(),before)

    def pending_fixture(self):
        attempt,_,generated=repair.subrequest(self.prov,self.job,self.base,list(repair.PARTS))
        pending=repair.pending_attempt(self.base,self.job,attempt);pending.update(child=dict(pid=999999999,createTime=123),phase='launched')
        repair.save(self.base/'pending-attempt.json',pending)
        return attempt,generated

    def write_part(self,generated,sid):
        path=generated/'chunks'/f'{sid}-scene.wav';path.parent.mkdir(parents=True,exist_ok=True)
        sf.write(path,np.ones(2401,np.float32)*.03,24000,subtype='PCM_16');return path

    def test_orphan_finished_child_outputs_are_adopted_without_another_launch(self):
        attempt,generated=self.pending_fixture()
        for sid in repair.PARTS:self.write_part(generated,sid)
        with (patch.object(repair.voice.native,'alive',return_value=False),
            patch.object(repair.subprocess,'Popen',side_effect=AssertionError('No duplicate synthesis'))):
            records=repair.recover_pending(self.base,self.job)
        self.assertEqual(set(records),set(repair.PARTS));self.assertFalse((self.base/'pending-attempt.json').exists())
        self.assertEqual(len(list(attempt.glob('resolved-pending-*.json'))),1)
        self.assertTrue((attempt/'recovered-components.json').exists())
        self.assertEqual(set(repair.recover_pending(self.base,self.job)),set(repair.PARTS))

    def test_valid_first_component_is_registered_before_malformed_second_fails(self):
        _,generated=self.pending_fixture();first=self.write_part(generated,'s03-a')
        broken=generated/'chunks/s03-b-scene.wav';broken.write_bytes(b'not a WAV')
        with patch.object(repair.voice.native,'alive',return_value=False):
            with self.assertRaises((wave.Error,EOFError)):repair.recover_pending(self.base,self.job)
        records=repair.components(self.base,self.job);self.assertEqual(set(records),{'s03-a'})
        self.assertEqual(records['s03-a']['sha256'],repair.voice.sha(first));self.assertEqual(broken.read_bytes(),b'not a WAV')
        self.assertTrue((self.base/'pending-attempt.json').exists())

    def test_live_unknown_or_rebound_request_never_gets_adopted_or_resynthesized(self):
        attempt,generated=self.pending_fixture();self.write_part(generated,'s03-a')
        before=(self.base/'pending-attempt.json').read_bytes()
        with patch.object(repair.voice.native,'alive',return_value=True):
            with self.assertRaises(repair.voice.PreparationPending):repair.recover_pending(self.base,self.job)
        self.assertEqual((self.base/'pending-attempt.json').read_bytes(),before)
        pending=repair.read(self.base/'pending-attempt.json');pending['child']=None;repair.save(self.base/'pending-attempt.json',pending)
        with self.assertRaisesRegex(AssertionError,'Unverifiable pending launch'):repair.recover_pending(self.base,self.job)
        pending['child']=dict(pid=999999999,createTime=123);repair.save(self.base/'pending-attempt.json',pending)
        (attempt/'manifest.json').write_text('{}',encoding='utf-8')
        with patch.object(repair.voice.native,'alive',return_value=False):
            with self.assertRaises(AssertionError):repair.recover_pending(self.base,self.job)
        self.assertFalse((self.base/'component-progress.json').exists())

    def test_changed_scalar_processor_pin_rejects_recovery(self):
        self.pending_fixture();actual=repair.voice.sha
        def changed(path):
            return 'changed-scalar-source' if Path(path).resolve()==(HERE/'prepare-first-audio.py').resolve() else actual(path)
        with patch.object(repair.voice.native,'alive',return_value=False),patch.object(repair.voice,'sha',side_effect=changed):
            with self.assertRaises(AssertionError):repair.recover_pending(self.base,self.job)


if __name__=='__main__':unittest.main(verbosity=2)
