"""CPU synthetic PCM/cache fixtures. No actual ASR/TTS/model/decoder calls."""
import copy,hashlib,importlib.util,io,json,sys,tempfile,unittest,wave
from pathlib import Path
from unittest.mock import patch
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('selected_qa',HERE/'run-selected-voice-qa.py');q=importlib.util.module_from_spec(spec);spec.loader.exec_module(q)

def wavefile(path,pcm):
 path.parent.mkdir(parents=True,exist_ok=True)
 with wave.open(str(path),'wb') as f:f.setparams((1,2,24000,len(pcm)//2,'NONE','not compressed'));f.writeframes(pcm)

def bundle(root):
 out=root/'voice';raws=[];chunks=[];entries=[];mapping=[];position=0
 import struct
 for n in range(4):
  sid=f'p{n//2+1:03d}-c{n%2+1:02d}';pcm=b''.join(struct.pack('<h',v) for v in [1500,-1500,700,-700]*6000);p=out/'chunks'/(sid+'-scene.wav');wavefile(p,pcm);info=q.voice.wav_info(p);chunks.append(info);raws.append(pcm);entries.append(dict(scene_id=sid,text='벽이 보입니다.' if n%2==0 else '틈이 열립니다.',start=position/24000,end=(position+info['frames'])/24000));mapping.append(dict(sceneId=sid,paragraph=n//2+1));position+=info['frames']
 wavefile(out/'canonical/narration.wav',b''.join(raws));proof=dict(fingerprint='voice-fixture',aggregateWav=q.voice.wav_info(out/'canonical/narration.wav'),sceneWavs=chunks,paragraphMapping=mapping);timing={'entries':entries};tasks=q.build_tasks(proof,timing)
 identity=dict(voiceFingerprint='voice-fixture',aggregateSHA256=proof['aggregateWav']['sha256'],timingSHA256='fixture-timing',modelPins=[],trustedUtilitySHA256=q.APPROVED['trustedSHA256'],profile=q.PROFILE,tasks=tasks,adapterSHA256=q.sha(HERE/'run-selected-voice-qa.py'))
 fp=q.digest(identity);folder=out/'review/independent-asr-selected-v1'/fp[:24];job=dict(protocol=q.PROTOCOL,identity=identity,fingerprint=fp,voiceOutput=str(out),output=str(folder));q.voice.immutable_json(folder/'job.json',job);q.voice.immutable(folder/'adapter-source.py',(HERE/'run-selected-voice-qa.py').read_bytes())
 return job,proof,timing

def fill(job):
 for task in job['identity']['tasks']:
  text=task.get('expected','벽이 보입니다. 틈이 열립니다.')
  result={'text':text,'chunks':[{'text':text,'timestamp':[.1,.6]}]}
  q.voice.immutable_json(Path(job['output'])/(task['key']+'.json'),q.recognition_record(job,task,result))

class SelectedQA(unittest.TestCase):
 def test_literal_spelling_difference_is_not_an_alias_or_pass(self):
  job={'fingerprint':'f'};task=dict(kind='take',sceneId='p001-c01',expected='게임플레이 메트릭스',offsetSeconds=3.,durationSeconds=1.)
  result={'text':'게임플레이 매트릭스','chunks':[{'text':' 매트릭스','timestamp':[.1,.5]}]};r=q.recognition_record(job,task,result)
  self.assertEqual(r['rawRecognition'],result);self.assertEqual(r['globalWords'][0]['timestamp'],[3.1,3.5]);self.assertEqual(r['comparison']['characterDifferences'][0]['expected'],'메');self.assertFalse(r['aliasesApplied']);self.assertFalse(r['comparison']['automaticSpeechPass'])
 def test_variable_take_tasks_preserve_internal_and_paragraph_joins(self):
  with tempfile.TemporaryDirectory() as tmp:
   job,proof,_=bundle(Path(tmp));takes=[t for t in job['identity']['tasks'] if t['kind']=='take'];joins=[t for t in job['identity']['tasks'] if t['kind']=='boundary']
   self.assertEqual(len(takes),4);self.assertEqual([j['joinType'] for j in joins],['internal-component','paragraph-boundary','internal-component']);self.assertEqual([j['boundarySample'] for j in joins],[24000,48000,72000])
   for j in joins:self.assertEqual(j['slicePcmSHA256'],hashlib.sha256(q.pcm_bytes(j['path'],j['beginSample'],j['endSample'])).hexdigest())
 def test_seven_style_paragraph_interface_is_explicitly_assembled_not_fresh_asr(self):
  with tempfile.TemporaryDirectory() as tmp:
   job,_,_=bundle(Path(tmp));fill(job);r=q.summary(job)
   self.assertEqual(len(r['takes']),4);self.assertEqual(len(r['paragraphs']),2);self.assertEqual(len(r['boundaryWindows']),3)
   self.assertEqual(r['paragraphs'][0]['sceneIds'],['p001-c01','p001-c02']);self.assertEqual(r['paragraphs'][0]['endSample'],48000);self.assertEqual(r['paragraphs'][0]['recognitionBasis'],'assembled-from-blind-component-takes');self.assertEqual(r['paragraphs'][0]['globalWords'][1]['sourceSceneId'],'p001-c02');self.assertFalse(r['humanListening'])
 def test_scoped_raw_cache_rebases_words_and_rejects_tampered_provenance(self):
  with tempfile.TemporaryDirectory() as tmp:
   job,_,_=bundle(Path(tmp));task=job['identity']['tasks'][0];result={'text':task['expected'],'chunks':[{'text':task['expected'],'timestamp':[.1,.5]}]};origin=Path(job['output'])/'job.json'
   cache=dict(key=q.cache_key(job,task),profile=q.PROFILE,modelPins=[],trustedUtilitySHA256=q.APPROVED['trustedSHA256'],rawRecognition=result,rawRecognitionSHA256=q.digest(result),originJob=q.pin(origin));q.voice.immutable_json(q.raw_cache_path(job,task),cache)
   new=copy.deepcopy(job);new['identity']['tasks']=[dict(task,offsetSample=48000,offsetSeconds=2.)];new['fingerprint']='rebased';new['output']=str(Path(job['voiceOutput'])/'review/independent-asr-selected-v1/rebased')
   self.assertEqual(q.restore_raw_cache(new),1);r=q.cached(new,new['identity']['tasks'][0]);self.assertEqual(r['globalWords'][0]['timestamp'],[2.1,2.5]);self.assertEqual(r['rawRecognition'],result)
   q.raw_cache_path(job,task).write_text(json.dumps(dict(cache,rawRecognitionSHA256='tampered')))
   newer=copy.deepcopy(new);newer['output']+='2'
   with self.assertRaisesRegex(ValueError,'Raw recognition cache changed'):q.restore_raw_cache(newer)
 def test_unknown_word_boundaries_remain_visible(self):
  task=dict(kind='take',sceneId='p1',expected='등대',offsetSeconds=0.,durationSeconds=1.);raw={'text':'등대','chunks':[{'text':'등대','timestamp':[None,.5]}]};r=q.recognition_record({'fingerprint':'f'},task,raw)
  self.assertIn('unknown-word-boundary',r['boundaryFlags']);self.assertIsNone(r['globalWords'][0]['timestamp'][0]);self.assertFalse(r['humanListening'])
 def test_raw_level_and_join_review_changes_no_pcm_and_never_accepts_aac_or_hearing(self):
  with tempfile.TemporaryDirectory() as tmp:
   job,proof,timing=bundle(Path(tmp));fill(job);paths=[Path(c['path']) for c in proof['sceneWavs']]+[Path(proof['aggregateWav']['path'])];before={str(p):q.sha(p) for p in paths}
   with patch.object(q,'prepare_job',return_value=job),patch.object(q,'exact_voice',return_value=(Path(job['voiceOutput']),proof,timing,{})):
    path=q.raw_level_review(Path(job['output'])/'job.json')
   report=q.read(path);self.assertEqual(len(report['joins']),3);self.assertEqual(len(report['takes']),4);self.assertEqual(len(report['paragraphs']),2);self.assertFalse(report['pcmModified']);self.assertFalse(report['actualListening']);self.assertFalse(report['encodedAacChecked']);self.assertEqual(before,{str(p):q.sha(p) for p in paths})
 def test_waiting_voice_preflight_neither_stages_nor_launches(self):
  old=sys.argv
  try:
   sys.argv=['run-selected-voice-qa.py']
   with patch.object(q,'prepare_job',side_effect=q.Pending('voice still running')),patch.object(q.voice,'immutable_json') as writes,patch.object(q.subprocess,'Popen') as launch,patch('sys.stdout',new_callable=io.StringIO) as output:
    q.main();self.assertIn('"ready": false',output.getvalue());writes.assert_not_called();launch.assert_not_called()
  finally:sys.argv=old
 def test_foreign_gpu_lease_is_only_observed(self):
  with tempfile.TemporaryDirectory() as tmp:
   lease=Path(tmp)/'GPU_HANDOFF.json';lease.write_text('{"owner":"foreign","token":"keep"}');before=lease.read_bytes()
   with patch.object(q.voice.runtime,'LEASE',lease),patch.object(q.subprocess,'Popen') as launch:
    self.assertIn('shared GPU lease',q.resource_reason());launch.assert_not_called()
   self.assertEqual(lease.read_bytes(),before)

if __name__=='__main__':unittest.main()
