"""CPU-only first-voice fixtures. Temporary files and mocked child processes only."""
from __future__ import annotations
import copy, importlib.util, json, struct, sys, tempfile, unittest, wave
from pathlib import Path
from unittest.mock import patch

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
spec=importlib.util.spec_from_file_location('first_voice_under_test',HERE/'run-first-voice.py')
voice=importlib.util.module_from_spec(spec);spec.loader.exec_module(voice)
DETECT=voice.same_project_children


class VoiceTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='yamyam-first-voice-cpu-');self.base=Path(self.tmp.name)
        root=self.base/'repo';project=root/'projects'/voice.SLUG
        parent=root/'shared/output/architectural-111-20261106/03-02'
        self.context=patch.multiple(voice,ROOT=root,PROJECT_DIR=project,MANIFEST=project/'voice-manifest.json',
            MEDIA=self.base/'media',VOICE_PARENT=parent,OUTPUT=parent/'voice-v1',STATE=self.base/'state.json',
            WORKER=self.base/'voice-worker.json',ENGINE=root/'engine.py',PYTHON=root/'python.exe')
        self.context.start();self.children=patch.object(voice,'same_project_children',return_value=[]);self.children.start()
        self.scenes=[dict(id=f's{i:02}',title='nonspoken title',lines=[f'spoken line {i}']) for i in range(1,7)]
        self.tts=dict(engine='qwen3-tts',language='Korean',renderMode='scene',sceneGapSeconds=0,edgeFadeSeconds=0,
            outputDir='fixed',filenameStem='narration',model='fixed-model',reference='fixed-ref',referenceText='fixed-text',
            maxNewTokens=1800,gpuMinimumFreeMiB=8192,gpuProfileReason='nonspoken scheduling note')
        self.editing=dict(exampleSeconds=0,narrationPlacement='continuous-across-example-and-explanation')
        self.prov=self.provenance()
        voice.save(project/'project.json',dict(status='native-captured-review-pending',unrelated='keep',humanApproval=False))
        voice.save(project/'checkpoint.json',dict(stage='native-captured-review-pending',completedStages=[],unrelated='keep'))

    def tearDown(self):
        self.children.stop();self.context.stop();self.tmp.cleanup()

    def provenance(self,scenes=None,tts=None,ref='approved-wave',reftext='approved-text'):
        scenes=scenes or self.scenes
        p=voice.synthesis_identity(scenes,tts or self.tts,self.editing,[dict(path='model.safetensors',sha256='weights')],ref,reftext)
        p.update(sceneIds=[s['id'] for s in scenes],spokenLines=[s['lines'][0] for s in scenes],sceneGapSeconds=0,
            audit=dict(nativeFingerprint='native-a',nativeQaSHA256='qa-a',manifestSHA256='raw-manifest',scriptSHA256='raw-script'))
        return p

    def write_wav(self,path,frames):
        path.parent.mkdir(parents=True,exist_ok=True)
        with wave.open(str(path),'wb') as w:
            w.setparams((1,2,8000,frames,'NONE','not compressed'));w.writeframes(struct.pack('<h',1000)*frames)

    def outputs(self):
        out=voice.prepare_output(self.prov)
        for sid in self.prov['sceneIds']:self.write_wav(out/'chunks'/f'{sid}-scene.wav',4000)
        self.write_wav(out/'narration.wav',24000)
        voice.save(out/'narration.timing.json',dict(render_mode='scene',sample_rate=8000,duration_seconds=3,
            entries=[dict(scene_id=sid,text=text,start=i*.5,end=(i+1)*.5) for i,(sid,text) in enumerate(zip(self.prov['sceneIds'],self.prov['spokenLines']))]))
        (out/'narration.srt').write_text('engine-generated fixture, not final caption QA',encoding='utf-8')
        return out

    def fake_main(self,**changes):
        from contextlib import ExitStack
        with ExitStack() as stack:
            stack.enter_context(patch.object(sys,'argv',['run-first-voice.py','--execute','--wait-hours','0']))
            stack.enter_context(patch.object(voice,'preparation',return_value=self.prov))
            stack.enter_context(patch.object(voice.native,'busy_reason',side_effect=AssertionError('GPU probe forbidden')))
            stack.enter_context(patch.object(voice.subprocess,'Popen',side_effect=AssertionError('Native/model child forbidden')))
            for owner,name,value in changes.values():stack.enter_context(patch.object(owner,name,value))
            voice.main()

    def test_nonspoken_titles_scheduling_and_visual_audit_do_not_change_speech_identity(self):
        scenes=copy.deepcopy(self.scenes);scenes[0]['title']='different nonspoken title'
        tts=dict(self.tts,gpuMinimumFreeMiB=12000,gpuProfileReason='different scheduling audit',
                 preparationState='different nonspoken administrative state',sceneGapSeconds=0.0)
        p=self.provenance(scenes=scenes,tts=tts)
        p['audit'].update(nativeFingerprint='new-camera-shader',nativeQaSHA256='new-mobile-qa',manifestSHA256='new-full-json')
        self.assertEqual(p['fingerprint'],self.prov['fingerprint'])

    def test_visual_only_changes_reuse_exact_pcm_without_archive_or_gpu(self):
        out=self.outputs();before=voice.wav_info(out/'narration.wav')
        changed=copy.deepcopy(self.prov);changed['audit'].update(nativeFingerprint='new-view',nativeQaSHA256='qa-b')
        self.assertEqual(voice.prepare_output(changed),out)
        after=voice.verify_voice(changed)['aggregateWav']
        self.assertEqual(before['sha256'],after['sha256']);self.assertEqual(before['pcmSHA256'],after['pcmSHA256'])
        self.assertFalse((voice.VOICE_PARENT/'voice-preserved').exists())
        self.fake_main()
        self.assertFalse(voice.read(voice.STATE)['gpuStarted'])

    def test_spoken_or_reference_or_real_profile_change_changes_identity(self):
        changed=copy.deepcopy(self.scenes);changed[0]['lines']=['different spoken sentence']
        self.assertNotEqual(self.prov['fingerprint'],self.provenance(scenes=changed)['fingerprint'])
        self.assertNotEqual(self.prov['fingerprint'],self.provenance(ref='different-approved-reference')['fingerprint'])
        self.assertNotEqual(self.prov['fingerprint'],self.provenance(tts=dict(self.tts,maxNewTokens=2000))['fingerprint'])

    def test_genuine_input_change_preserves_old_output_bytes_in_checked_version_folder(self):
        out=self.outputs();digest=voice.sha(out/'chunks/s01-scene.wav')
        changed=copy.deepcopy(self.scenes);changed[0]['lines']=['revised speech']
        voice.prepare_output(self.provenance(scenes=changed))
        preserved=list((voice.VOICE_PARENT/'voice-preserved').iterdir())
        self.assertEqual(len(preserved),1)
        self.assertEqual(voice.sha(preserved[0]/'chunks/s01-scene.wav'),digest)
        self.assertFalse((out/'chunks').exists())
        self.assertTrue(preserved[0].resolve().is_relative_to(voice.VOICE_PARENT.resolve()))

    def test_same_pin_partial_chunks_are_not_moved_or_rewritten(self):
        out=voice.prepare_output(self.prov);chunk=out/'chunks/s01-scene.wav';self.write_wav(chunk,4000)
        old=chunk.read_bytes();voice.prepare_output(self.prov)
        self.assertEqual(chunk.read_bytes(),old);self.assertFalse((voice.VOICE_PARENT/'voice-preserved').exists())

    def test_wrong_timing_and_missing_or_truncated_pcm_are_rejected(self):
        out=self.outputs();timing=voice.read(out/'narration.timing.json');timing['entries'][0]['text']='other script'
        voice.save(out/'narration.timing.json',timing)
        with self.assertRaises(ValueError):voice.verify_voice(self.prov)
        timing['entries'][0]['text']=self.prov['spokenLines'][0];voice.save(out/'narration.timing.json',timing)
        (out/'chunks/s06-scene.wav').unlink()
        with self.assertRaises(FileNotFoundError):voice.verify_voice(self.prov)
        self.write_wav(out/'chunks/s06-scene.wav',4000)
        p=out/'chunks/s06-scene.wav';p.write_bytes(p.read_bytes()[:-100])
        with self.assertRaises(ValueError):voice.verify_voice(self.prov)

    def test_later_asr_listening_approval_platform_and_movie_states_survive_repeat_record(self):
        self.outputs();proof=voice.verify_voice(self.prov)
        advanced=dict(proof,asrReviewStatus='passed',listeningReviewStatus='human-reviewed',humanApproval=True,
                      status='voice-human-approved',laterReviewEvidence='keep')
        voice.save(voice.PROJECT_DIR/'project.json',dict(status='scheduled',finalMovieComplete=True,humanApproval=True,
            platformStatus='scheduled',voiceCapture=advanced))
        voice.save(voice.PROJECT_DIR/'checkpoint.json',dict(stage='final-human-reviewed',completedStages=['final-master'],
            finalOutputsVerified=True,humanReview='approved',voiceCapture=advanced))
        voice.complete_record(proof)
        p=voice.read(voice.PROJECT_DIR/'project.json');c=voice.read(voice.PROJECT_DIR/'checkpoint.json')
        self.assertTrue(p['finalMovieComplete']);self.assertTrue(p['humanApproval']);self.assertEqual(p['platformStatus'],'scheduled')
        self.assertEqual(p['status'],'scheduled');self.assertEqual(c['stage'],'final-human-reviewed');self.assertTrue(c['finalOutputsVerified'])
        self.assertEqual(c['humanReview'],'approved');self.assertEqual(p['voiceCapture']['asrReviewStatus'],'passed')
        self.assertEqual(p['voiceCapture']['status'],'voice-human-approved');self.assertEqual(p['voiceCapture']['laterReviewEvidence'],'keep')

    def test_interrupted_qwen_child_is_retained_and_foreign_gpu_lease_untouched(self):
        lease=voice.ROOT/'shared/output/GPU_HANDOFF.json';voice.save(lease,dict(project='foreign-task',token='preserve'))
        lease_bytes=lease.read_bytes();actual_identity=voice.native.identity
        class FakeChild:
            pid=999999999
            def wait(self):raise KeyboardInterrupt('CPU fixture')
            def poll(self):return None
        with self.assertRaises(KeyboardInterrupt):
            self.fake_main(busy=(voice.native,'busy_reason',lambda:None),
                child=(voice.subprocess,'Popen',lambda *a,**k:FakeChild()),
                identity=(voice.native,'identity',lambda pid=None:dict(pid=FakeChild.pid,createTime=123) if pid else actual_identity()))
        self.assertEqual(lease.read_bytes(),lease_bytes)
        state=voice.read(voice.STATE);self.assertTrue(state['childStillAlive']);self.assertFalse(state['externalGpuLeaseAcquired'])
        self.assertEqual(state['child']['pid'],FakeChild.pid);self.assertTrue(voice.WORKER.exists())
        self.assertEqual(voice.read(voice.WORKER)['stage'],'voice')


if __name__=='__main__':unittest.main(verbosity=2)
