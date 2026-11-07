"""Synthetic bounded mixed-ASR protocol checks only; no model or actual media."""
import copy,hashlib,importlib.util,json,tempfile
from pathlib import Path
import numpy as np
import soundfile as sf
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('prospect_mix_asr_fixture',HERE/'run-prospect-refuge-mix-asr.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
checks=[]
def require(value):
 if not value:raise AssertionError('Synthetic mixed-ASR fixture failed')
def check(name,fn):fn();checks.append(name)
def rejected(fn):
 try:fn()
 except(ValueError,RuntimeError,AssertionError):return
 raise AssertionError('Invalid mixed-ASR input accepted')
def fixture():
 voice=dict(fingerprint='synthetic103',identity=dict(scenes=[]),aggregateWav=dict(sampleRate=24000,frames=0,sha256='raw'),sceneWavs=[],paragraphMapping=[]);rows=[];position=0;i=0
 for n in range(1,26):
  for j in range(1,6 if n<=3 else 5):
   sid=f'p{n:03}-c{j:02}';text='합성 문장 '+sid;frames=1001+i
   voice['identity']['scenes'].append(dict(id=sid,lines=[text]));voice['sceneWavs'].append(dict(frames=frames,sha256='raw-'+sid,pcmSHA256='pcm-'+sid));voice['paragraphMapping'].append(dict(sceneId=sid,paragraph=n,canonicalText=text))
   rows.append(dict(sceneId=sid,paragraph=n,text=text,sourceSampleRange=[0,frames],destinationSampleRange=[position,position+frames],prepared48kSampleRange=[position*2,(position+frames)*2],rawTakeSHA256='raw-'+sid,rawPcmSHA256='pcm-'+sid));position+=frames;i+=1
 voice['aggregateWav']['frames']=position
 levels=dict(voiceFingerprint=voice['fingerprint'],rawCanonical=voice['aggregateWav'],components=rows,originalRawFilesUnchanged=True,wordBoundariesShifted=False,voiceOffsetSeconds=0,insertedSamples=0,trimmedSamples=0,voiceSpeed=1,compressorUsed=False,voiceSideDuck=False)
 mix=dict(path='synthetic.wav',sha256='m'*64,sampleRate=48000,channels=2,subtype='FLOAT',frames=position*2)
 return voice,levels,mix
voice,levels,mix=fixture();tasks=m.coverage(voice,levels,mix);takes=tasks[:25];joins=tasks[25:]
check('103 physical units map to25 full paragraphs plus24 joins',lambda:require(len(tasks)==49 and sum(len(t['sourcePhysicalSceneIds'])for t in takes)==103 and len(joins)==24))
check('every mix sample covered exactly once by25 primary windows',lambda:require(takes[0]['beginSample']==0 and takes[-1]['endSample']==mix['frames']and sum(t['endSample']-t['beginSample']for t in takes)==mix['frames']and all(a['endSample']==b['beginSample']for a,b in zip(takes,takes[1:]))))
check('all103 exact source clocks and hashes remain visible',lambda:require([p['sceneId']for t in takes for p in t['sourcePhysicalComponents']]==[s['id']for s in voice['identity']['scenes']]and all(p['mixedSampleRange']==[v*2 for v in p['rawSampleRange']]for t in takes for p in t['sourcePhysicalComponents'])))
check('context joins onlyactual25 paragraph boundaries',lambda:require(all(t['joinType']=='paragraph-boundary'and t['boundarySample']==takes[i+1]['beginSample']for i,t in enumerate(joins))))
for name,mutate in [
 ('one missing source unit',lambda v,l,x:v['identity']['scenes'].pop()),
 ('reordered raw identity',lambda v,l,x:v['identity']['scenes'].reverse()),
 ('one raw sample gap',lambda v,l,x:l['components'][1]['destinationSampleRange'].__setitem__(0,l['components'][1]['destinationSampleRange'][0]+1)),
 ('one mixed sample pad',lambda v,l,x:x.__setitem__('frames',x['frames']+1)),
 ('raw WAV cannotreplace stereo finalmix',lambda v,l,x:x.__setitem__('channels',1)),
 ('altered accepted raw SHA',lambda v,l,x:l['components'][0].__setitem__('rawTakeSHA256','other')),
 ('altered raw PCM SHA',lambda v,l,x:l['components'][0].__setitem__('rawPcmSHA256','other')),
 ('altered spoken text',lambda v,l,x:l['components'][0].__setitem__('text','다른 말')),
 ('paragraph mapping mismatch',lambda v,l,x:v['paragraphMapping'][0].__setitem__('paragraph',2)),
 ('missing finalparagraph',lambda v,l,x:[r.__setitem__('paragraph',24)for r in l['components']if r['paragraph']==25]),
 ('speed adjustment',lambda v,l,x:l.__setitem__('voiceSpeed',1.01)),
 ('compressed speech',lambda v,l,x:l.__setitem__('compressorUsed',True)),
 ('voice-side ducking',lambda v,l,x:l.__setitem__('voiceSideDuck',True)),
 ('inserted silence',lambda v,l,x:l.__setitem__('insertedSamples',1)),
 ('trimmed speech',lambda v,l,x:l.__setitem__('trimmedSamples',1)),
]:
 def case(mutate=mutate):
  v,l,x=copy.deepcopy((voice,levels,mix));mutate(v,l,x);rejected(lambda:m.coverage(v,l,x))
 check(name+' rejected',case)
stereo=np.array([[.2,.4],[.5,-.5],[0.,0.]],dtype=np.float32);before=stereo.copy();mono,hashes=m.window_pcm(stereo)
check('downmix is arithmetic stereo mean and doesnotmodify input',lambda:require(np.array_equal(stereo,before)and np.array_equal(mono,stereo.mean(axis=1,dtype=np.float64).astype('<f4'))))
check('nonfinite PCM declined',lambda:rejected(lambda:m.window_pcm(np.array([[np.nan,0]],dtype=np.float32))))
with tempfile.TemporaryDirectory()as d:
 folder=Path(d);p=folder/'synthetic.wav';sf.write(p,stereo,48000,subtype='FLOAT');small=dict(path=str(p),sha256=m.sha(p),sampleRate=48000,channels=2,frames=3,subtype='FLOAT');task=dict(path=str(p),audioSHA256=m.sha(p),beginSample=0,endSample=3)
 check('exact actual-slice hash read with unchanged sample clock',lambda:require(m.read_window(small,task)[1]==hashes))
 check('one sample outside actualsource rejected',lambda:rejected(lambda:m.read_window(small,dict(task,endSample=4))))
 check('taskfile cannotpoint to raw source',lambda:rejected(lambda:m.read_window(small,dict(task,path='raw.wav'))))
 check('changed actualmix SHA rejected',lambda:rejected(lambda:m.read_window(dict(small,sha256='0'*64),dict(task,audioSHA256='0'*64))))
 job=dict(fingerprint='f'*64,identity=dict(mix=mix,tasks=tasks,componentCount=103,modelPins=[dict(path='model',sha256='a'*64)],trustedUtilitySHA256='t'*64,audioBuildFingerprint='synthetic-audio',voiceFingerprint=voice['fingerprint']),output=str(folder/'job'),audioBuildPath=str(folder/'audio-build.json'),rawVoiceAsr=dict(path='synthetic-raw-review',sha256='r'*64));Path(job['output']).mkdir()
 for t in tasks:t.update(hashes)
 original=m.cache_key(job,takes[0])
 check('changedmix invalidates independentcache',lambda:require(original!=m.cache_key(job,dict(takes[0],audioSHA256='other'))))
 check('changedPCM slice invalidates cache',lambda:require(original!=m.cache_key(job,dict(takes[0],monoPcmSHA256='other'))))
 altered=copy.deepcopy(job);altered['identity']['modelPins'][0]['sha256']='b'*64
 check('changedapproved model invalidates cache',lambda:require(original!=m.cache_key(altered,takes[0])))
 result=dict(text='합성 인식',chunks=[dict(text='합성 인식',timestamp=[0,.001])])
 for t in tasks:
  r=m.recognition_record(job,t,result);m.save(Path(job['output'])/(t['key']+'.json'),r)
 complete=m.summary(job)
 check('completeactualmixedcoverage truthfullydistinguishes raw stem/AAC/hearing',lambda:require(complete['coveredSamples']==mix['frames']and complete['physicalComponentCount']==103 and len(complete['paragraphs'])==25 and complete['rawVoiceRecognitionReusedAsMix']is False and complete['encodedAACChecked']is False and complete['humanListening']is False and complete['automaticSpeechPass']is False))
 rp=Path(job['output'])/(takes[0]['key']+'.json');old=m.read(rp);bad=copy.deepcopy(old);bad['rawRecognition']['text']='변조';m.save(rp,bad)
 check('literalcache mutation rejected',lambda:rejected(lambda:m.cached(job,takes[0])))
 m.save(rp,old);rp.unlink()
 check('incomplete49 tasks cannotreport completion',lambda:require(m.summary(job)is None))
 decline=folder/'resource-decline-fixture.json';good=dict(protocol=m.PROTOCOL,fingerprint=job['fingerprint'],phase='before-model',modelLoaded=False,temporary=True,reason='Synthetic guardrace');m.save(decline,good)
 def temporary():
  try:m.accept_exit(75,decline,job)
  except m.raw.ResourceRetry:return
  raise AssertionError('Pre-model race was not temporary')
 check('proven premodelresource race canretry75',temporary)
 check('actualmodel failure remainsfatal',lambda:rejected(lambda:m.accept_exit(1,decline,job)))
 m.save(decline,dict(good,modelLoaded=True));check('postmodel failure cannotmasquerade resourcewait',lambda:rejected(lambda:m.accept_exit(75,decline,job)))
for value in(float('nan'),float('inf'),-1,6.001):check('invalidfinitewait '+str(value),lambda value=value:rejected(lambda:m.execute('never-read',value)))
print(json.dumps(dict(passed=len(checks),checks=checks,sourceSHA256=m.sha(HERE/'run-prospect-refuge-mix-asr.py'),actualMixDecoded=False,modelLoaded=False,gpuUsed=False,actualListening=False),ensure_ascii=False))
