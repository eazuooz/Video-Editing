"""Synthetic PCM/process-preservation fixtures only; no model/GPU/media source jobs."""
import argparse,copy,hashlib,importlib.util,io,json,sys,tempfile,unittest,wave
from pathlib import Path
from unittest.mock import patch
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('selected_voice_worker',HERE/'run-selected-voice.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)

def wav(path,data):
 path.parent.mkdir(parents=True,exist_ok=True)
 with wave.open(str(path),'wb') as f:f.setparams((1,2,24000,len(data)//2,'NONE','not compressed'));f.writeframes(data)

def fixture(root):
 ident={'protocol':'fixture-preparation','scenes':[{'id':'p001','lines':['벽이 가립니다.']},{'id':'p002','lines':['틈이 열립니다.']}],'tts':{'engine':'qwen3-tts','language':'Korean','renderMode':'scene','edgeFadeSeconds':0,'sceneGapSeconds':0},'rawPcmPolicy':{'speechSpeed':1,'timeStretch':False}}
 fp=v.digest(ident);out=root/'shared/output'/v.prep.BATCH_ID/'07-04/voice-attempts'/fp[:24];stage=root/'projects/shorts-leveldesign-07-04/production/voice-preparation/fixture'
 script={'scenes':[dict(s,title='표시용 제목') for s in ident['scenes']]};manifest={'slug':'shorts-leveldesign-07-04','paths':{'script':(stage/'narration-qwen.json').relative_to(root).as_posix()},'tts':dict(ident['tts'],model='qwen3-tts/models/approved',reference='shared/ref.wav',referenceText='shared/ref.txt',outputDir=out.relative_to(root).as_posix())}
 prov={'topicId':'07.04','slug':'shorts-leveldesign-07-04','fingerprint':fp,'preparationFingerprint':'audit1','identity':ident,'voiceOutputDirectory':str(out),'paragraphMapping':[{'paragraph':1,'sceneId':'p001'},{'paragraph':2,'sceneId':'p002'}],'inputs':[],'manifest':manifest,'script':script,'stagingDirectory':str(stage)}
 prov['qwenSynthesisArgv']=[str(root/'qwen3-tts/.venv/Scripts/python.exe'),'-u','-X','utf8',str(root/'qwen3-tts/render_narration.py'),'--project',prov['slug'],'--manifest',(stage/'voice-manifest.json').relative_to(root).as_posix(),'--batch-size','1','--device','cuda:0']
 v.initialize_output(prov)
 import struct
 raw1=b''.join(struct.pack('<h',x) for x in [1000,-1000,500,-500]*80);raw2=b''.join(struct.pack('<h',x) for x in [2000,0,-2000,0]*120)
 wav(out/'chunks/p001-scene.wav',raw1);wav(out/'chunks/p002-scene.wav',raw2);raw=raw1+raw2
 # Synthetic faded engine aggregate differs while retaining exactly800 frames.
 changed=b'\0'*24+raw[24:-24]+b'\0'*24;wav(out/'narration.wav',changed)
 position=0;entries=[]
 for i,(scene,data) in enumerate(zip(ident['scenes'],[raw1,raw2]),1):
  frames=len(data)//2;entries.append(dict(scene_id=scene['id'],text=scene['lines'][0],start=position/24000,end=(position+frames)/24000));position+=frames
 v.immutable_json(out/'narration.timing.json',dict(render_mode='scene',sample_rate=24000,duration_seconds=position/24000,entries=entries));v.immutable(out/'narration.srt',b'1\n00:00:00,000 --> 00:00:00,013\nfixture1\n\n2\n00:00:00,013 --> 00:00:00,033\nfixture2\n')
 v.immutable_json(stage/'narration-qwen.json',script);v.immutable_json(stage/'voice-manifest.json',manifest)
 return prov,out,raw

def args():return argparse.Namespace(topic='07.04',native_evidence=None,native_qa=None,semantic_components=None,wait_hours=.01)

class SelectedWorker(unittest.TestCase):
 def test_placeholder_preflight_does_not_stage_or_start(self):
  old=sys.argv
  try:
   sys.argv=['run-selected-voice.py']
   with patch.object(v,'prepared',side_effect=v.prep.Pending('placeholder')),patch.object(v.prep,'immutable_stage') as stage,patch.object(v.subprocess,'Popen') as start,patch('sys.stdout',new_callable=io.StringIO) as output:
    v.main();self.assertIn('"ready": false',output.getvalue());stage.assert_not_called();start.assert_not_called()
  finally:sys.argv=old
 def test_variable_scene_raw_concatenation_preserves_engine_and_all_samples(self):
  with tempfile.TemporaryDirectory() as tmp,patch.object(v,'ROOT',Path(tmp)):
   prov,out,raw=fixture(Path(tmp));before=(out/'narration.wav').read_bytes();_,engine=v.validate_engine_outputs(prov,out);proof=v.canonical_outputs(prov,out,engine)
   with wave.open(proof['aggregateWav']['path'],'rb') as f:self.assertEqual(f.readframes(f.getnframes()),raw)
   self.assertEqual((out/'narration.wav').read_bytes(),before);self.assertEqual(proof['aggregateWav']['frames'],800);self.assertNotEqual(proof['aggregateWav']['pcmSHA256'],engine['aggregateWav']['pcmSHA256'])
   self.assertFalse(proof['independentAsrVerified']);self.assertFalse(proof['actualListening'])
 def test_same_voice_metadata_change_reuses_complete_output_without_stage_or_model(self):
  with tempfile.TemporaryDirectory() as tmp,patch.object(v,'ROOT',Path(tmp)),patch.object(v,'MEDIA',Path(tmp)/'media'):
   prov,out,_=fixture(Path(tmp));_,engine=v.validate_engine_outputs(prov,out);proof=v.canonical_outputs(prov,out,engine);v.immutable_json(out/'voice-complete-proof.json',proof)
   new=copy.deepcopy(prov);new['preparationFingerprint']='metadata-only-audit2'
   with patch.object(v,'prepared',return_value=new),patch.object(v,'project_children',return_value=[]),patch.object(v,'busy_reason') as busy,patch.object(v.prep,'immutable_stage') as stage,patch.object(v.subprocess,'Popen') as start,patch('sys.stdout',new_callable=io.StringIO):
    v.execute(args());busy.assert_not_called();stage.assert_not_called();start.assert_not_called()
   state=v.read(Path(tmp)/'media/07-04-voice-progress.json');self.assertTrue(state['completed']);self.assertTrue(state['reusedCompleteVoice'])
 def test_live_worker_record_is_preserved(self):
  with tempfile.TemporaryDirectory() as tmp,patch.object(v,'MEDIA',Path(tmp)):
   ctx=v.configure('07.04');record=dict(protocol=v.PROTOCOL,owner=ctx['owner'],token='known',**v.identity(),child=None);v.save(ctx['worker'],record);before=ctx['worker'].read_bytes()
   with self.assertRaisesRegex(RuntimeError,'Preserve existing'):v.runtime.SingleWorker(ctx['worker'],is_alive=v.alive).acquire()
   self.assertEqual(ctx['worker'].read_bytes(),before)
 def test_foreign_lease_stays_unchanged_and_no_wrapper_acquires_one(self):
  with tempfile.TemporaryDirectory() as tmp:
   lease=Path(tmp)/'GPU_HANDOFF.json';lease.write_text('{"owner":"foreign","token":"keep"}');before=lease.read_bytes()
   with patch.object(v.runtime,'LEASE',lease),patch.object(v.subprocess,'Popen') as start:
    self.assertIn('shared GPU lease',v.busy_reason());start.assert_not_called()
   self.assertEqual(lease.read_bytes(),before)
 def test_only_documented_unchanged_premodel_decline_is_retryable(self):
  with tempfile.TemporaryDirectory() as tmp:
   log=Path(tmp)/'engine.log';log.write_text('GPU capacity is insufficient for this profile: 7000MiB free,8192MiB required. Existing work was preserved.')
   self.assertTrue(v.premodel_decline(1,log,{},{}));self.assertFalse(v.premodel_decline(0,log,{},{}));self.assertFalse(v.premodel_decline(1,log,{}, {'new.wav':'sha'}))
   log.write_text('GPU capacity is insufficient for this profile:\nProject: loaded\nTraceback')
   self.assertFalse(v.premodel_decline(1,log,{},{}))
 def test_orphan_completed_outputs_recover_cpu_only_with_exact_request_pins(self):
  with tempfile.TemporaryDirectory() as tmp,patch.object(v,'ROOT',Path(tmp)):
   prov,out,_=fixture(Path(tmp));attempt=out/'engine-attempts/fixture';attempt.mkdir(parents=True)
   request=dict(protocol=v.PROTOCOL,fingerprint=prov['fingerprint'],identity=prov['identity'],command=prov['qwenSynthesisArgv']);v.immutable_json(attempt/'request.json',request)
   paths=[attempt/'request.json',Path(prov['stagingDirectory'])/'voice-manifest.json',Path(prov['stagingDirectory'])/'narration-qwen.json']
   pending=dict(fingerprint=prov['fingerprint'],identity=prov['identity'],attempt=str(attempt),child={'pid':99999999,'createTime':0,'argv':['fixture'],'commandSHA256':'fixture'},exitCode=None,requestPins=[dict(path=str(p),sha256=v.sha(p)) for p in paths]);v.save(out/'pending-launch.json',pending)
   with patch.object(v,'alive',return_value=False),patch.object(v,'project_children',return_value=[]),patch.object(v.subprocess,'Popen') as start:v.recover_pending(prov,out);start.assert_not_called()
   proof=v.verify_complete(prov,out);self.assertTrue(proof['recovery']['structuralRecoveryOnly']);self.assertIsNone(proof['recovery']['observedEngineExitCode']);self.assertFalse((out/'pending-launch.json').exists())
 def test_tampered_completed_pcm_is_not_silently_reused(self):
  with tempfile.TemporaryDirectory() as tmp,patch.object(v,'ROOT',Path(tmp)):
   prov,out,_=fixture(Path(tmp));_,engine=v.validate_engine_outputs(prov,out);proof=v.canonical_outputs(prov,out,engine);v.immutable_json(out/'voice-complete-proof.json',proof)
   wav(out/'chunks/p001-scene.wav',b'\0\0'*320)
   with self.assertRaisesRegex(RuntimeError,'PCM changed'):v.verify_complete(prov,out)

if __name__=='__main__':unittest.main()
