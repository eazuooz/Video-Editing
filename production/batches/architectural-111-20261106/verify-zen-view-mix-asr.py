"""Synthetic CPU metadata/PCM-array checks; no actual mix decode or recognizer."""
import copy,importlib.util,json,uuid
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('zen_mixed_fixture',HERE/'run-zen-view-mix-asr.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
fixture=m.TOPIC/'mixed-asr-source-preparation/cpu-tests'/uuid.uuid4().hex;fixture.mkdir(parents=True)
m.save(fixture/'fixture-purpose.json',dict(syntheticOnly=True,actualModelResults=False,actualMixedAudio=False))
passed=[]
def require(v):
 if not v:raise AssertionError('Synthetic fixture contract failed')
def check(name,fn):fn();passed.append(name)
def rejected(fn):
 try:fn()
 except(ValueError,RuntimeError,AssertionError):return
 raise AssertionError('Expected explicit rejection')

voice=dict(fingerprint='synthetic-voice',identity=dict(scenes=[]),aggregateWav=dict(sampleRate=24000,frames=0,sha256='raw-canonical-fixture'),sceneWavs=[],paragraphMapping=[])
rows=[];position=0
for i in range(14):
 n=1001+i*3;sid=f'p{i//2+1:03}-c{i%2+1:02}';text='합성 검사 '+str(i)
 voice['sceneWavs'].append(dict(frames=n,sha256='raw-'+str(i),pcmSHA256='rawpcm-'+str(i)));voice['paragraphMapping'].append(dict(sceneId=sid,canonicalText=text))
 voice['identity']['scenes'].append(dict(id=sid,lines=[text]))
 rows.append(dict(sceneId=sid,paragraph=i//2+1,text=text,sourceSampleRange=[0,n],destinationSampleRange=[position,position+n],prepared48kSampleRange=[position*2,(position+n)*2],rawTakeSHA256='raw-'+str(i),rawPcmSHA256='rawpcm-'+str(i)));position+=n
voice['aggregateWav']['frames']=position
levels=dict(voiceFingerprint=voice['fingerprint'],rawCanonical=voice['aggregateWav'],components=rows,originalRawFilesUnchanged=True,wordBoundariesShifted=False,voiceOffsetSeconds=0,insertedSamples=0,trimmedSamples=0)
mix=dict(path='synthetic-final-mix.wav',sha256='m'*64,sampleRate=48000,channels=2,subtype='FLOAT',frames=position*2)
tasks=m.coverage(voice,levels,mix);takes=tasks[:14];joins=tasks[14:]
check('exact 14 takes plus 13 contextual joins',lambda:require(len(takes)==14 and len(joins)==13))
check('all actual mix samples covered once by contiguous take windows',lambda:require(takes[0]['beginSample']==0 and takes[-1]['endSample']==mix['frames']and sum(t['endSample']-t['beginSample']for t in takes)==mix['frames']and all(a['endSample']==b['beginSample']for a,b in zip(takes,takes[1:]))))
check('joins use exact doubled raw boundary samples',lambda:require(all(j['boundarySample']==t['beginSample']for j,t in zip(joins,takes[1:]))))
bad=copy.deepcopy(levels);bad['components'][1]['destinationSampleRange'][0]+=1
check('one shifted component cannot omit a quiet sample',lambda:rejected(lambda:m.coverage(voice,bad,mix)))
check('audio padding by one sample rejected',lambda:rejected(lambda:m.coverage(voice,levels,dict(mix,frames=mix['frames']+1))))
check('raw mono audio cannot substitute for mixed stereo input',lambda:rejected(lambda:m.coverage(voice,levels,dict(mix,channels=1))))
bad=copy.deepcopy(levels);bad['components'][0]['rawTakeSHA256']='other'
check('unaccepted raw component source rejected',lambda:rejected(lambda:m.coverage(voice,bad,mix)))
for alternative_count in [29,33]:
 altvoice=dict(fingerprint='synthetic-alt',identity=dict(scenes=[]),aggregateWav=dict(sampleRate=24000,frames=0,sha256='alt-raw'),sceneWavs=[],paragraphMapping=[]);altrows=[];at=0;index=0
 for paragraph in range(1,8):
  for ordinal in range(alternative_count//7+(1 if paragraph<=alternative_count%7 else 0)):
   n=1003+index;sid=f'alt-p{paragraph:03}-c{ordinal:03}';text='다른 수량 검사 '+sid
   altvoice['identity']['scenes'].append(dict(id=sid,lines=[text]));altvoice['sceneWavs'].append(dict(frames=n,sha256='alt-'+str(index),pcmSHA256='altpcm-'+str(index)));altvoice['paragraphMapping'].append(dict(sceneId=sid,canonicalText=text));altrows.append(dict(sceneId=sid,paragraph=paragraph,text=text,sourceSampleRange=[0,n],destinationSampleRange=[at,at+n],prepared48kSampleRange=[at*2,(at+n)*2],rawTakeSHA256='alt-'+str(index),rawPcmSHA256='altpcm-'+str(index)));at+=n;index+=1
 altvoice['aggregateWav']['frames']=at;altlevels=dict(levels,voiceFingerprint=altvoice['fingerprint'],rawCanonical=altvoice['aggregateWav'],components=altrows);altmix=dict(mix,frames=at*2);alttasks=m.coverage(altvoice,altlevels,altmix)
 check(f'exact{alternative_count} produces N contiguous windows and N-1 joins',lambda:require(len(alttasks)==alternative_count*2-1 and alttasks[alternative_count-1]['endSample']==altmix['frames']))
 bad=copy.deepcopy(altvoice);bad['identity']['scenes'][0],bad['identity']['scenes'][1]=bad['identity']['scenes'][1],bad['identity']['scenes'][0]
 check(f'exact{alternative_count} mixed source order cannot change',lambda:rejected(lambda:m.coverage(bad,altlevels,altmix)))
stereo=np.array([[.2,.4],[.5,-.5],[0.,0.]],dtype=np.float32);before=stereo.copy();mono,hashes=m.window_pcm(stereo)
check('stereo downmix preserves source and has expected mono mean',lambda:require(np.array_equal(stereo,before)and np.allclose(mono,[.3,0,0])))
check('nonfinite mixed PCM rejected',lambda:rejected(lambda:m.window_pcm(np.array([[np.nan,0]],dtype=np.float32))))
job=dict(fingerprint='f'*64,identity=dict(mix=mix,tasks=tasks,componentCount=14,modelPins=[dict(path='model',sha256='a'*64)],trustedUtilitySHA256='t'*64,audioBuildFingerprint='synthetic-audio',voiceFingerprint='synthetic-voice'),output=str(fixture/'job'),audioBuildPath=str(fixture/'audio-build.json'),rawVoiceAsr=dict(path='synthetic-only-raw-review',sha256='r'*64))
Path(job['output']).mkdir()
for t in tasks:t.update(hashes)
key=m.cache_key(job,takes[0]);changed=copy.deepcopy(takes[0]);changed['audioSHA256']='changed-mix'
check('changed final mix SHA invalidates recognition cache',lambda:require(m.cache_key(job,changed)!=key))
changed=copy.deepcopy(takes[0]);changed['slicePcmSHA256']='changed-stereo'
check('changed decoded window invalidates cache',lambda:require(m.cache_key(job,changed)!=key))
altjob=copy.deepcopy(job);altjob['identity']['modelPins'][0]['sha256']='b'*64
check('changed trusted model pins invalidate cache',lambda:require(m.cache_key(altjob,takes[0])!=key))
result=dict(text='합성 검사 0',chunks=[dict(text='합성',timestamp=[0,.001]),dict(text='검사 0',timestamp=[.001,.002])])
record=m.recognition_record(job,takes[0],result);rp=Path(job['output'])/(takes[0]['key']+'.json');m.save(rp,record)
check('mixed cache cannot claim raw or AAC recognition',lambda:require(m.cached(job,takes[0])['rawVoiceAsrReused']is False and record['encodedAACChecked']is False and record['normalizedStemRecognized']is False))
bad=copy.deepcopy(record);bad['rawRecognition']['text']='변조';m.save(rp,bad)
check('raw recognition mutation rejected by cache rederivation',lambda:rejected(lambda:m.cached(job,takes[0])))
m.save(rp,record)
check('partial task results cannot report complete mixed coverage',lambda:require(m.summary(job)is None))
for t in tasks:m.save(Path(job['output'])/(t['key']+'.json'),m.recognition_record(job,t,result))
complete=m.summary(job)
check('full mixed summary retains raw/mix/AAC evidence distinction',lambda:require(complete['coveredSamples']==mix['frames']and complete['rawVoiceRecognitionReusedAsMix']is False and complete['encodedAACChecked']is False and complete['humanListening']is False and complete['automaticSpeechPass']is False))
decline=fixture/'resource-decline-fixture.json';good=dict(protocol=m.PROTOCOL,fingerprint=job['fingerprint'],phase='before-model',modelLoaded=False,temporary=True,reason='synthetic guard race')
m.save(decline,good)
def retry75():
 try:m.accept_exit(75,decline,job)
 except m.raw.ResourceRetry:return
 raise AssertionError('Known pre-model resource decline not classified')
check('known pre-model resource race gets temporary retry only',retry75)
check('actual model failure remains fatal despite a decline file',lambda:rejected(lambda:m.accept_exit(1,decline,job)))
m.save(decline,dict(good,modelLoaded=True))
check('post-model failure cannot masquerade as resource wait',lambda:rejected(lambda:m.accept_exit(75,decline,job)))
receipt=dict(schemaVersion='07-04-mixed-asr-source-cpu-validation-v1',passed=len(passed),checks=passed,fixture=str(fixture),sourcePins=[m.pin(HERE/'run-zen-view-mix-asr.py'),m.pin(Path(__file__)),m.pin(HERE/'run-selected-voice-qa.py')],syntheticOnly=True,actualMixDecoded=False,modelStarted=False,gpuUsed=False,actualRecognition=False,actualListening=False)
m.save(fixture/'receipt.json',receipt);print(json.dumps(receipt,ensure_ascii=False))
