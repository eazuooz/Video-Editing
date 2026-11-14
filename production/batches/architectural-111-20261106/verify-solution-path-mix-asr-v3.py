"""Synthetic FLOAT/PCM scopes and mocked lifecycle only; no real ASR/model/tools."""
from pathlib import Path
import copy, hashlib, importlib.util, io, json, struct, sys, tempfile, unittest, wave
from contextlib import ExitStack, redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch
import numpy as np
import soundfile as sf
HERE=Path(__file__).resolve().parent
if str(HERE)not in sys.path:sys.path.insert(0,str(HERE))
spec=importlib.util.spec_from_file_location('solution_mixed_cpu',HERE/'run-solution-path-mix-asr-v3.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def dump(path,value):
 path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');return path

def fixture(root,extra=False):
 scenes=[];rows=[];wav=[];mapping=[];position=0;texts=[]
 counts=[4]*9+[3]*5 if not extra else [3]+[2]*13
 for p,count in enumerate(counts,1):
  paragraph=[]
  for c in range(1,count+1):
   sid=f'p{p:03d}-c{c:02d}';text=f'{p}번째 방의 {c}번째 경계를 봅니다.';paragraph.append(text)
   n=601+(p==14 and c==count);a,b=position,position+n;rawsha=hashlib.sha256(sid.encode()).hexdigest();pcmsha=hashlib.sha256((sid+'pcm').encode()).hexdigest()
   scenes.append(dict(id=sid,lines=[text]));wav.append(dict(frames=n,sha256=rawsha,pcmSHA256=pcmsha))
   mapping.append(dict(sceneId=sid,paragraph=p,canonicalText=text))
   rows.append(dict(sceneId=sid,paragraph=p,text=text,frames=n,sourceSampleRange=[0,n],destinationSampleRange=[a,b],
                    prepared48kSampleRange=[2*a,2*b],rawTakeSHA256=rawsha,rawPcmSHA256=pcmsha));position=b
  texts.append(' '.join(paragraph))
 aggregate=dict(path=str(root/'synthetic-raw.wav'),sha256='a'*64,pcmSHA256='b'*64,frames=position)
 voice=dict(identity=dict(scenes=scenes),sceneWavs=wav,paragraphMapping=mapping,aggregateWav=aggregate,fingerprint='c'*64)
 levels=dict(schemaVersion='11.05-line-levels-v8',componentCount=len(rows),rawCanonical=aggregate,components=rows,
             voiceOffsetSeconds=0,insertedSamples=0,trimmedSamples=0,voiceSpeed=1.,wordBoundariesShifted=False)
 values=np.column_stack((np.sin(np.arange(position*2)*.031)*.1,np.cos(np.arange(position*2)*.047)*.08)).astype(np.float32)
 path=root/'actual-synthetic-mix.wav';sf.write(path,values,48000,subtype='FLOAT')
 mix=dict(path=str(path),sha256=m.sha(path),frames=len(values),sampleRate=48000,channels=2,subtype='FLOAT')
 return voice,levels,mix,texts,values

def job_fixture(root):
 voice,levels,mix,texts,values=fixture(root);tasks=m.coverage(voice,levels,mix,texts)
 for task in tasks:_,hashes=m.read_window(mix,task);task.update(hashes)
 folder=root/'audio-preparation-v8'/('a'*24)
 identity=dict(profile=m.PROFILE,modelPins=[dict(path='synthetic-model',sha256='d'*64)],trustedUtilitySHA256='e'*64,
               componentCount=51,mix=mix,tasks=tasks,audioBuildFingerprint='f'*64,voiceFingerprint='c'*64,adapterSHA256=m.SELF_SHA)
 fingerprint=m.digest(identity)
 job=dict(protocol=m.PROTOCOL,identity=identity,fingerprint=fingerprint,output=str(folder/'review/mixed-asr-v3'/fingerprint[:24]),
          audioBuildPath=str(folder/'audio-build.json'),rawVoiceAsr=dict(path='synthetic-raw-review',sha256='0'*64),sourcePins=[])
 return job

class MixedWindows(unittest.TestCase):
 def setUp(self):
  temp=tempfile.TemporaryDirectory(prefix='solution-mixed-cpu-');self.addCleanup(temp.cleanup);self.root=Path(temp.name)
 def test14paragraphs13joins_cover_every_sample_and_all51parts_once(self):
  voice,ledger,mix,texts,_=fixture(self.root);tasks=m.coverage(voice,ledger,mix,texts);takes=tasks[:14]
  self.assertEqual(len(tasks),27);self.assertEqual(takes[0]['beginSample'],0);self.assertEqual(takes[-1]['endSample'],mix['frames'])
  self.assertEqual(sum(t['endSample']-t['beginSample']for t in takes),mix['frames'])
  self.assertEqual([p['sceneId']for t in takes for p in t['sourcePhysicalComponents']],[s['id']for s in voice['identity']['scenes']])
  self.assertEqual(sum(len(t['sourcePhysicalComponents'])for t in takes),51)
  self.assertTrue(all(a['endSample']==b['beginSample']for a,b in zip(takes,takes[1:])))
  self.assertTrue(all(j['boundarySample']==r['beginSample']for j,r in zip(tasks[14:],takes[1:])))
 def test_purecoverage_variableN_has_same14logicalparagraphs_no_last_sample_loss(self):
  voice,ledger,mix,texts,_=fixture(self.root,True);tasks=m.coverage(voice,ledger,mix,texts)
  self.assertEqual(len(voice['identity']['scenes']),29);self.assertEqual(len(tasks),27)
  self.assertEqual(mix['frames'],voice['aggregateWav']['frames']*2);self.assertEqual(tasks[13]['endSample'],mix['frames'])
 def test_wrong_component_identity_pcm_text_or_range_is_rejected(self):
  voice,ledger,mix,texts,_=fixture(self.root)
  for field,value in [('sceneId','p999-c01'),('rawTakeSHA256','x'),('rawPcmSHA256','x'),('text','다른 원문입니다.'),
                       ('destinationSampleRange',[1,602]),('prepared48kSampleRange',[0,1201])]:
   wrong=copy.deepcopy(ledger);wrong['components'][0][field]=value
   self.assertRaises(m.Pending,m.coverage,voice,wrong,mix,texts)
 def test_missing_reordered_component_or_paragraph_cannot_cover_body(self):
  voice,ledger,mix,texts,_=fixture(self.root)
  wrong=copy.deepcopy(ledger);wrong['components'].pop();self.assertRaises(m.Pending,m.coverage,voice,wrong,mix,texts)
  wrong=copy.deepcopy(ledger);wrong['components'][0],wrong['components'][1]=wrong['components'][1],wrong['components'][0]
  self.assertRaises(m.Pending,m.coverage,voice,wrong,mix,texts)
  wrong=copy.deepcopy(ledger);wrong['components'][0]['paragraph']=2;self.assertRaises(m.Pending,m.coverage,voice,wrong,mix,texts)
 def test_audio_grid_or_timewarp_flag_cannot_pass(self):
  voice,ledger,mix,texts,_=fixture(self.root)
  for field,value in [('frames',mix['frames']-1),('sampleRate',24000),('channels',1),('subtype','PCM_16')]:
   bad=dict(mix,**{field:value});self.assertRaises(m.Pending,m.coverage,voice,ledger,bad,texts)
  for field,value in [('voiceOffsetSeconds',.01),('insertedSamples',1),('trimmedSamples',1),('voiceSpeed',1.1),('wordBoundariesShifted',True)]:
   self.assertRaises(m.Pending,m.coverage,voice,dict(ledger,**{field:value}),mix,texts)
 def test_full_paragraph_text_must_reconstruct_current_source(self):
  voice,ledger,mix,texts,_=fixture(self.root);texts[12]+=' 바꾼 문장입니다.'
  self.assertRaises(m.Pending,m.coverage,voice,ledger,mix,texts)
 def test_stereo_downmix_and_hashes_are_actual_f32_no_gain(self):
  values=np.array([[.2,-.4],[.7,.1],[-.8,.2]],dtype=np.float32);before=values.copy();mono,pins=m.window_pcm(values)
  expected=values.mean(axis=1,dtype=np.float64).astype('<f4')
  self.assertTrue(np.array_equal(mono,expected));self.assertTrue(np.array_equal(values,before))
  self.assertEqual(pins['slicePcmSHA256'],hashlib.sha256(values.astype('<f4').tobytes()).hexdigest())
  self.assertEqual(pins['monoPcmSHA256'],hashlib.sha256(expected.tobytes()).hexdigest())
 def test_bad_stereo_or_task_window_rejected(self):
  for x in (np.ones(3),np.zeros((0,2)),np.array([[float('nan'),0.]]),np.ones((2,3))):self.assertRaises(ValueError,m.window_pcm,x)
  voice,ledger,mix,texts,_=fixture(self.root);task=m.coverage(voice,ledger,mix,texts)[0]
  for field,value in [('path','foreign.wav'),('audioSHA256','0'*64),('beginSample',-1),('endSample',mix['frames']+1)]:
   self.assertRaises(ValueError,m.read_window,mix,dict(task,**{field:value}))
 def populate(self,job):
  for task in job['identity']['tasks']:
   result=dict(text='실제 인식의 다른 단어입니다.',chunks=[dict(text='실제 인식의 다른 단어입니다.',timestamp=[.005,min(.02,task['durationSeconds'])])])
   dump(Path(job['output'])/(task['key']+'.json'),m.recognition_record(job,task,result))
 def test_actual_mixed_summary_retains_mismatch_and_allbody_provenance(self):
  job=job_fixture(self.root);self.populate(job);review=m.summary(job)
  self.assertEqual((len(review['takes']),len(review['paragraphs']),len(review['boundaryWindows'])),(14,14,13))
  self.assertEqual(review['coveredSamples'],job['identity']['mix']['frames']);self.assertTrue(review['fullActualMixCoverage'])
  self.assertEqual(review['physicalComponentCount'],51);self.assertFalse(review['rawVoiceRecognitionReusedAsMix'])
  self.assertFalse(review['aliasesApplied']);self.assertFalse(review['automaticSpeechPass']);self.assertFalse(review['humanListening'])
  self.assertEqual(review['paragraphs'][0]['recognizedLiteral'],'실제 인식의 다른 단어입니다.')
  self.assertTrue(review['paragraphs'][0]['comparison']['characterDifferences'])
 def test_incomplete_or_tampered_cache_cannot_become_complete(self):
  job=job_fixture(self.root);self.assertIsNone(m.summary(job));self.populate(job)
  task=job['identity']['tasks'][0];path=Path(job['output'])/(task['key']+'.json');row=m.read(path)
  row['rawRecognition']['text']='원문으로 고쳤습니다.';dump(path,row);self.assertRaises(ValueError,m.summary,job)
 def test_raw_origin_cache_never_reused_as_mixed_recognition(self):
  job=job_fixture(self.root);task=job['identity']['tasks'][0]
  raw=dict(text='합성 인식.',chunks=[dict(text='합성 인식.',timestamp=[.005,.02])])
  path=m.cache_path(job,task)
  dump(path,dict(key=m.cache_key(job,task),profile=m.PROFILE,modelPins=job['identity']['modelPins'],trustedUtilitySHA256=job['identity']['trustedUtilitySHA256'],
                rawRecognition=raw,rawRecognitionSHA256=m.digest(raw),originJob=dict(path=str(self.root/'raw-asr/job.json'),sha256='0'*64)))
  self.assertRaises(m.Pending,m.restore_cache,job);self.assertFalse((Path(job['output'])/(task['key']+'.json')).exists())
 def test_sameaudited_mixed_cache_reuse_and_originmodel_tamper(self):
  job=job_fixture(self.root);task=job['identity']['tasks'][0]
  origin=Path(job['output'])/'job.json';dump(origin,job)
  (origin.parent/'adapter-source.py').write_bytes(Path(m.__file__).read_bytes())
  raw=dict(text='합성 인식.',chunks=[dict(text='합성 인식.',timestamp=[.005,.02])])
  cache=m.cache_path(job,task)
  dump(cache,dict(key=m.cache_key(job,task),profile=m.PROFILE,modelPins=job['identity']['modelPins'],trustedUtilitySHA256=job['identity']['trustedUtilitySHA256'],
                  rawRecognition=raw,rawRecognitionSHA256=m.digest(raw),originJob=m.pin(origin)))
  m.restore_cache(job);self.assertEqual(m.cached(job,task)['text'],raw['text'])
  (Path(job['output'])/(task['key']+'.json')).unlink()
  wrong=copy.deepcopy(job);wrong['identity']['modelPins'][0]['sha256']='0'*64;wrong['fingerprint']=m.digest(wrong['identity']);dump(origin,wrong)
  data=m.read(cache);data['originJob']=m.pin(origin);dump(cache,data)
  self.assertRaises(m.Pending,m.restore_cache,job)
 def raw_prerequisite(self):
  voice,ledger,mix,texts,_=fixture(self.root)
  out=self.root/'raw-voice';voice['output']=str(out);voice['fingerprint']=m.VOICE_FP
  entries=[];payload=[];chunks=[];position=0
  for i,(scene,row)in enumerate(zip(voice['identity']['scenes'],ledger['components'])):
   data=struct.pack('<h',i+1)*row['frames'];path=out/'chunks'/(scene['id']+'-scene.wav');path.parent.mkdir(parents=True,exist_ok=True)
   with wave.open(str(path),'wb')as stream:stream.setparams((1,2,24000,row['frames'],'NONE','not compressed'));stream.writeframes(data)
   start=position;position+=row['frames'];payload.append(data);chunks.append(m.qa.voice.wav_info(path))
   entries.append(dict(scene_id=scene['id'],text=scene['lines'][0],start=start/24000,end=position/24000))
  aggregate=out/'canonical.wav'
  with wave.open(str(aggregate),'wb')as stream:stream.setparams((1,2,24000,position,'NONE','not compressed'));stream.writeframes(b''.join(payload))
  voice['sceneWavs']=chunks;voice['aggregateWav']=m.qa.voice.wav_info(aggregate)
  timing=dict(sample_rate=24000,entries=entries);voice['timing']=m.pin(dump(out/'timing.json',timing))
  dump(out/'voice-complete-proof.json',voice)
  tasks=m.raw_adapter.qa.build_tasks(voice,timing)
  identity=dict(adapterSHA256=m.PINS['run-solution-path-voice-qa-v14.py'],voiceFingerprint=voice['fingerprint'],
                sourceNarration=m.pin(m.NARRATION),profile=m.raw_adapter.PROFILE,modelPins=m.qa.APPROVED['modelPins'],
                trustedUtilitySHA256=m.qa.APPROVED['trustedSHA256'],aggregateSHA256=voice['aggregateWav']['sha256'],
                timingSHA256=voice['timing']['sha256'],tasks=tasks)
  fp=m.digest(identity);folder=out/'review/independent-asr-selected-v1'/fp[:24]
  job=dict(protocol=m.raw_adapter.PROTOCOL,fingerprint=fp,identity=identity,output=str(folder),voiceOutput=str(out),
           voiceEvidence=m.pin(out/'voice-complete-proof.json'),sourcePins=[m.pin(HERE/'run-solution-path-voice-qa-v14.py')])
  dump(folder/'job.json',job);(folder/'adapter-source.py').write_bytes((HERE/'run-solution-path-voice-qa-v14.py').read_bytes())
  for task in tasks:
   text=task.get('expected','연결부의 합성 인식입니다.')
   result=dict(text=text,chunks=[dict(text=text,timestamp=[.003,.02])])
   dump(folder/(task['key']+'.json'),m.raw_adapter.qa.recognition_record(job,task,result))
  review=m.raw_adapter.summary(job)
  return voice,timing,m.pin(folder/'review.json'),job
 def test_current101raw_caches_and_summary_reconstruct_without_write(self):
  voice,timing,record,job=self.raw_prerequisite();before=Path(record['path']).read_bytes()
  review,_=m.verified_raw_review(voice,timing,record)
  self.assertEqual((len(review['takes']),len(review['boundaryWindows']),len(review['paragraphs'])),(51,50,14))
  self.assertEqual(Path(record['path']).read_bytes(),before)
 def test_old_raw_protocol_or_missing_cache_cannot_enable_mixed_recognition(self):
  voice,timing,record,job=self.raw_prerequisite();path=Path(job['output'])/'job.json'
  wrong=copy.deepcopy(job);wrong['protocol']='old-v5';dump(path,wrong)
  self.assertRaises(m.Pending,m.verified_raw_review,voice,timing,record)
  dump(path,job);(path.parent/(job['identity']['tasks'][0]['key']+'.json')).unlink()
  self.assertRaises(m.Pending,m.verified_raw_review,voice,timing,record)

class GuardsAndLifecycle(unittest.TestCase):
 def setUp(self):
  self.assertIs(m.qa.execute.__globals__,m.qa.__dict__,'Lifecycle must use the private mixed module state; never the raw QA module state')
 def test_previous_mixed_owner_live_unknown_and_launch_gap_are_preserved(self):
  with tempfile.TemporaryDirectory(prefix='mixed3-previous-owner-cpu-')as temp:
   media=Path(temp);base=dict(pid=12,createTime=1.,argv=['synthetic'],commandSHA256=m.qa.digest(['synthetic']),protocol='architectural111-11-05-mix-asr-v2',owner='architectural-111-11-05-mix-asr',child=None)
   for changed in (dict(live=True),dict(owner='foreign'),dict(phase='launching')):
    path=dump(media/'11-05-mix-asr-v2-progress.json',dict(base,**changed));before=path.read_bytes()
    with patch.object(m,'MEDIA',media),patch.object(m.raw_adapter,'legacy_barrier'),patch.object(m.qa.psutil,'process_iter',return_value=[]),patch.object(m.qa.voice,'alive',side_effect=lambda x:bool(x and x.get('live'))):
     self.assertRaises(m.Pending,m.raw_worker_barrier)
    self.assertEqual(path.read_bytes(),before)
 def launcher(self):
  job=m.DEST/'625bb091fe67a12bb024df2c'/'review/mixed-asr-v3'/('b'*24)/'job.json'
  tail=['-u','-X','utf8',str(Path(m.__file__).resolve()),'--recognize','--job',str(job),'--resource-decline',str(job.parent/'resource-decline-abcd1234.json')]
  launcher=m.LAUNCHER_RUNTIME_PINS[0]['path'];body=m.LAUNCHER_RUNTIME_PINS[2]['path']
  parent=dict(pid=100,ppid=50,create_time=10.,name='python.exe',exe=launcher,cmdline=[launcher]+tail)
  own=dict(pid=101,ppid=100,create_time=10.1,name='python.exe',exe=body,cmdline=[body]+tail)
  return copy.deepcopy(parent),own,parent
 def test_exact_direct_mixed_launcher_is_allowed(self):self.assertTrue(m.launcher_matches(*self.launcher()))
 def test_raw_or_foreign_job_scope_is_never_exempt(self):
  for path in (m.ROOT/'shared/output/architectural-111-20261106/11-05/voice-attempts'/('a'*24)/'review/independent-asr-selected-v1'/('b'*24)/'job.json',m.DEST/'foreign/job.json'):
   info,own,parent=self.launcher()
   for row in(info,own,parent):row['cmdline'][7]=str(path);row['cmdline'][9]=str(path.parent/'resource-decline-abcd1234.json')
   self.assertFalse(m.launcher_matches(info,own,parent))
 def test_wrong_pid_time_exe_or_extra_cli_rejected(self):
  for mode in ('pid','ppid','ctime','exe','argv','script'):
   info,own,parent=self.launcher()
   if mode=='pid':info['pid']+=1
   elif mode=='ppid':own['ppid']+=1
   elif mode=='ctime':info['create_time']+=1
   elif mode=='exe':own['exe']='C:/foreign/python.exe'
   elif mode=='argv':own['cmdline'].append('--expected-text')
   else:
    for row in(info,own,parent):row['cmdline'][4]=str(HERE/'run-solution-path-voice-qa-v14.py')
   self.assertFalse(m.launcher_matches(info,own,parent))
 def test_fresh_source_and_runtime_pin_checks_precede_unchanged9gib_gate(self):
  with patch.object(m,'check_sources')as sources,patch.object(m.raw_adapter,'check_sources')as runtime,patch.object(m,'_base_resource_reason',return_value='strict9GiB')as guard:
   self.assertEqual(m.resource_reason(),'strict9GiB');sources.assert_called_once();runtime.assert_called_once();guard.assert_called_once()
  self.assertEqual(m.PROFILE['minimumFreeMiB'],9216)
  for key in ('expectedPrompt','hotwords','aliases'):self.assertIsNone(m.PROFILE[key])
  self.assertEqual(m.qa.execute.__code__.co_filename,str(HERE/'run-selected-voice-qa.py'))
 def test_rawV6_live_unknown_or_unregistered_child_is_preserved(self):
  with tempfile.TemporaryDirectory(prefix='mixed-worker-cpu-')as temp:
   media=Path(temp)
   with patch.object(m,'MEDIA',media),patch.object(m.raw_adapter,'legacy_barrier'),patch.object(m.qa.psutil,'process_iter',return_value=[]),patch.object(m.qa.voice,'alive',side_effect=lambda x:bool(x and x.get('live'))):
    marker=dump(media/'11-05-asr-v14-worker.json',dict(live=True));before=marker.read_bytes()
    self.assertRaises(m.Pending,m.raw_worker_barrier);self.assertEqual(marker.read_bytes(),before)
    marker.write_text('{bad',encoding='utf-8');self.assertRaises(m.Pending,m.raw_worker_barrier)
   process=SimpleNamespace(info=dict(pid=999,name='python.exe',cmdline=['python','run-solution-path-voice-qa-v14.py','--recognize']))
   with patch.object(m,'MEDIA',media/'none'),patch.object(m.raw_adapter,'legacy_barrier'),patch.object(m.qa.psutil,'process_iter',return_value=[process]):self.assertRaises(m.Pending,m.raw_worker_barrier)
 def test_default_cli_missing_build_has_no_prepare_resource_model_or_job(self):
  with patch.object(m,'prepare_job',side_effect=AssertionError('No actual prepare')),patch.object(m.qa,'execute',side_effect=AssertionError('No worker')):
   out=io.StringIO()
   with redirect_stdout(out):self.assertEqual(m.main([]),0)
   self.assertFalse(json.loads(out.getvalue())['ready']);self.assertFalse(json.loads(out.getvalue())['jobLaunched'])
 def recognition_case(self,root):
  identity=dict(tasks=[dict(key='mix-paragraph-001')]);job=dict(identity=identity,fingerprint=m.digest(identity),output=str(root),audioBuildPath='synthetic-build',sourcePins=[])
  return job,dump(root/'job.json',job),root/'resource-decline-abcd1234.json'
 def test_premodel_resource_decline75_does_not_import_recognizer(self):
  with tempfile.TemporaryDirectory(prefix='mixed-decline-cpu-')as temp:
   job,path,decline=self.recognition_case(Path(temp))
   with patch.object(m,'prepare_job',return_value=job),patch.object(m,'restore_cache'),patch.object(m,'cached',return_value=None),patch.object(m.qa,'resource_reason',return_value='foreignlease'),patch.object(m,'module',side_effect=AssertionError('No model import')):
    self.assertEqual(m.recognize(path,decline),75)
   self.assertFalse(m.read(decline)['modelLoaded']);self.assertEqual(m.read(decline)['phase'],'before-model')
 def test_guard_race75_and_real_model_failure_are_distinct(self):
  with tempfile.TemporaryDirectory(prefix='mixed-model-cpu-')as temp:
   job,path,decline=self.recognition_case(Path(temp))
   with patch.object(m,'prepare_job',return_value=job),patch.object(m,'restore_cache'),patch.object(m,'cached',return_value=None),patch.object(m.qa,'resource_reason',return_value=None),patch.object(m,'module',return_value=SimpleNamespace()),patch.object(m.raw,'acquire_guard_before_model',side_effect=m.raw.PreModelResourceDeclined('race','guard-acquire')):
    self.assertEqual(m.recognize(path,decline),75)
   decline.unlink()
   trusted=SimpleNamespace(MODEL=m.qa.MODEL,load_recognizer=lambda device:(_ for _ in ()).throw(RuntimeError('synthetic model failure')))
   with patch.object(m,'prepare_job',return_value=job),patch.object(m,'restore_cache'),patch.object(m,'cached',return_value=None),patch.object(m.qa,'resource_reason',return_value=None),patch.object(m,'module',side_effect=lambda name,path:trusted if 'trusted_recognizer' in name else SimpleNamespace()),patch.object(m.raw,'acquire_guard_before_model'):
    self.assertRaisesRegex(RuntimeError,'synthetic model failure',m.recognize,path,decline)
   self.assertFalse(decline.exists())
 def test_durable_launchgap_retains_marker_for_unregistered_live_child(self):
  with tempfile.TemporaryDirectory(prefix='mixed-launchgap-cpu-')as temp:
   root=Path(temp);job=dict(output=str(root/'job'),identity={},fingerprint='a'*64);closed=[]
   worker=SimpleNamespace(update=lambda **kw:None,close=lambda remove:closed.append(remove));factory=SimpleNamespace(acquire=lambda:worker);child=SimpleNamespace(pid=9999,poll=lambda:None)
   def identity(pid=None):
    if pid is not None:raise RuntimeError('synthetic registration failure')
    return dict(pid=1,createTime=1.,argv=['synthetic'],commandSHA256='a'*64)
   with patch.object(m.qa.runtime,'SingleWorker',return_value=factory),patch.object(m.qa,'STATE',root/'state.json'),patch.object(m.qa,'WORKER',root/'worker.json'),patch.object(m.qa,'child_processes',return_value=[]),patch.object(m.qa,'prepare_job',return_value=job),patch.object(m.qa,'restore_raw_cache'),patch.object(m.qa,'summary',return_value=None),patch.object(m.qa,'resource_reason',return_value=None),patch.object(m.qa.voice,'identity',side_effect=identity),patch.object(m.qa.subprocess,'Popen',return_value=child):
    self.assertRaisesRegex(RuntimeError,'registration failure',m.qa.execute,.1)
   self.assertEqual(closed,[False]);self.assertTrue(m.read(root/'state.json')['childStillAlive'])

if __name__=='__main__':unittest.main(verbosity=1)
