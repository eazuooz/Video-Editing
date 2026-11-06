"""Synthetic CPU-only contextual ASR contracts; no real PCM/model/guard/process."""
import copy,importlib.util,json,tempfile
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace
import numpy as np

HERE=Path(__file__).resolve().parent;s=importlib.util.spec_from_file_location('context_asr_fixture',HERE/'run-zen-view-mix-context-asr.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
checks=[]
def yes(v):
 if not v:raise AssertionError('Expected true')
def rejects(f):
 try:f()
 except(ValueError,RuntimeError,AssertionError):return
 raise AssertionError('Expected rejection')
def check(n,f):f();checks.append(n)

voice=dict(fingerprint='synthetic-only',identity=dict(scenes=[]),aggregateWav=dict(sampleRate=24000,frames=0,sha256='raw'),sceneWavs=[],paragraphMapping=[]);rows=[];paragraphs=[];position=0;draft=dict(narrationKo=[])
for p,count in enumerate([4,5,5,6,4,5,5],1):
 start=position;ids=[];texts=[]
 for c in range(1,count+1):
  sid=f'p{p:03d}-c{c:02d}';n=1000+len(rows)*7;text='canonical '+sid;ids.append(sid);texts.append(text)
  voice['identity']['scenes'].append(dict(id=sid,lines=[text]));voice['sceneWavs'].append(dict(frames=n,sha256='raw-'+sid,pcmSHA256='pcm-'+sid));voice['paragraphMapping'].append(dict(sceneId=sid,canonicalText=text))
  rows.append(dict(sceneId=sid,paragraph=p,text=text,sourceSampleRange=[0,n],destinationSampleRange=[position,position+n],prepared48kSampleRange=[position*2,(position+n)*2],rawTakeSHA256='raw-'+sid,rawPcmSHA256='pcm-'+sid));position+=n
 paragraphs.append(dict(paragraph=p,sceneIds=ids,destinationSampleRange=[start,position]));draft['narrationKo'].append(' '.join(texts))
voice['aggregateWav']['frames']=position
levels=dict(voiceFingerprint=voice['fingerprint'],rawCanonical=voice['aggregateWav'],components=rows,paragraphs=paragraphs,originalRawFilesUnchanged=True,wordBoundariesShifted=False,voiceOffsetSeconds=0,insertedSamples=0,trimmedSamples=0)
mix=dict(path='synthetic-final-mix.wav',sha256='a'*64,sampleRate=48000,channels=2,subtype='FLOAT',frames=position*2)
tasks,original=m.context_tasks(voice,levels,mix,draft)
check('only complete P5 and P7 tasks, not original67 task rerun',lambda:yes(len(tasks)==2 and[t['paragraphIndex']for t in tasks]==[5,7]and len(original)==67))
check('paragraph clocks exactly double accepted raw24k integer boundaries',lambda:yes(all([t['beginSample'],t['endSample']]==[x*2 for x in paragraphs[t['paragraphIndex']-1]['destinationSampleRange']]for t in tasks)))
check('complete context retains all source clauses and quiet lead/tail samples',lambda:yes(all(t['expected']==draft['narrationKo'][t['paragraphIndex']-1]and t['sceneIds']==paragraphs[t['paragraphIndex']-1]['sceneIds']for t in tasks)))
check('larger paragraph inputs differ from original per-take windows',lambda:yes(all(not any(t['beginSample']==x['beginSample']and t['endSample']==x['endSample']for x in original)for t in tasks)))
bad=copy.deepcopy(levels);bad['paragraphs'][4]['destinationSampleRange'][0]+=1
check('one raw sample clipped from full paragraph rejected',lambda:rejects(lambda:m.context_tasks(voice,bad,mix,draft)))
bad=copy.deepcopy(levels);bad['components'][0]['destinationSampleRange'][1]+=1
check('base full-coverage component guards remain active',lambda:rejects(lambda:m.context_tasks(voice,bad,mix,draft)))
bad=copy.deepcopy(draft);bad['narrationKo'][4]+=' rewritten'
check('context cannot rewrite expected full paragraph metadata',lambda:rejects(lambda:m.context_tasks(voice,levels,mix,bad)))
check('raw mono source cannot substitute for actual stereo mix',lambda:rejects(lambda:m.context_tasks(voice,levels,dict(mix,channels=1),draft)))
stereo=np.array([[.2,.4],[.5,-.5],[0.,0.]],dtype=np.float32);before=stereo.copy();mono,hashes=m.full.window_pcm(stereo)
check('same approved stereo downmix has exact mean and does not modify source',lambda:yes(np.array_equal(stereo,before)and np.allclose(mono,[.3,0,0])and set(hashes)=={'slicePcmSHA256','monoPcmSHA256'}))
check('nonfinite contextual stereo input rejected',lambda:rejects(lambda:m.full.window_pcm(np.array([[np.nan,0]],dtype=np.float32))))
for t in tasks:t.update(hashes)
with tempfile.TemporaryDirectory(prefix='yamyam-context-asr-cpu-')as temp:
 root=Path(temp);job=dict(protocol=m.PROTOCOL,fingerprint='b'*64,identity=dict(profile=m.PROFILE,mix=mix,tasks=tasks,modelPins=[dict(path='model',sha256='c'*64)],trustedUtilitySHA256='d'*64,audioBuildFingerprint='synthetic-build',voiceFingerprint='synthetic-only',baselineReview=dict(path='original-review',sha256='f'*64),sourcePins=[]),output=str(root/'context-job'),audioBuildPath=str(root/'audio-build.json'),baselineReviewPath=str(root/'original-review.json'),modelPath=str(m.qa.MODEL),fullActualMixCoverage=False,modelLoaded=False,expectedPrompt=None,hotwords=None,aliasesApplied=False,humanListening=False)
 Path(job['output']).mkdir();result=dict(text='recognizer literal differs',chunks=[dict(text='literal',timestamp=[0,.01])]);record=m.recognition_record(job,tasks[0],result)
 check('context comparison keeps literal difference without aliases or automatic pass',lambda:yes(record['text']==result['text']and record['comparison']['characterDifferences']and record['comparison']['aliasesApplied']is False and record['automaticSpeechPass']is False))
 check('word timestamps retain exact actual-mix global offset',lambda:yes(abs(record['globalWords'][0]['timestamp'][0]-tasks[0]['beginSample']/48000)<1e-12))
 key=m.cache_key(job,tasks[0]);changed=copy.deepcopy(tasks[0]);changed['audioSHA256']='newmix'
 check('changed actual mix invalidates context cache',lambda:yes(m.cache_key(job,changed)!=key))
 changed=copy.deepcopy(tasks[0]);changed['monoPcmSHA256']='newmono'
 check('changed actual downmix invalidates context cache',lambda:yes(m.cache_key(job,changed)!=key))
 changed=copy.deepcopy(tasks[0]);changed['expected']='comparison metadata only changed'
 check('expected text never affects recognizer input cache identity',lambda:yes(m.cache_key(job,changed)==key))
 check('new context profile cannot read original narrow-result cache namespace',lambda:yes('blind-mixed-context-cache-v1'in str(m.cache_path(job,tasks[0]))and m.PROFILE!=m.full.PROFILE))
 check('partial context job cannot complete',lambda:yes(m.summary(job)is None))
 for t in tasks:m.qa.voice.immutable_json(Path(job['output'])/(t['key']+'.json'),m.recognition_record(job,t,result))
 summary=m.summary(job)
 check('two contextual results never claim whole-mix coverage or hearing',lambda:yes(summary['contextCount']==2 and summary['fullActualMixCoverage']is False and summary['automaticSpeechPass']is False and summary['humanListening']is False and summary['baselineResultsReplaced']is False))
 p=Path(job['output'])/(tasks[0]['key']+'.json');value=m.read(p);value['rawRecognition']['text']='edited';m.save(p,value)
 check('raw contextual cache edits rejected',lambda:rejects(lambda:m.cached(job,tasks[0])))
 m.save(p,record)
 decline=root/'resource-decline-fixture.json';m.save(decline,dict(protocol=m.PROTOCOL,fingerprint=job['fingerprint'],phase='before-model',modelLoaded=False,temporary=True,reason='fixture race'))
 def valid_decline():
  try:m.accept_exit(75,decline,job)
  except m.raw.ResourceRetry:return
  raise AssertionError('Expected finite resource retry')
 check('only documented pre-model decline is resource retry',valid_decline)
 check('actual inference failure remains fatal',lambda:rejects(lambda:m.accept_exit(1,decline,job)))
 value=m.read(decline);value['modelLoaded']=True;m.save(decline,value)
 check('post-model failure cannot masquerade as pre-model decline',lambda:rejects(lambda:m.accept_exit(75,decline,job)))
 # Exercise the real new recognizer routing with a synthetic factory only.
 jp=Path(job['output'])/'job.json';m.save(jp,job);calls=[];guarded=[];fakepipe=object()
 class Trusted:
  MODEL=m.qa.MODEL
  @staticmethod
  def load_recognizer(device):yes(guarded==[True]and device=='cuda');return fakepipe
  @staticmethod
  def recognize(*args,**kwargs):yes(len(args)==3 and args[0]is fakepipe and args[2]==48000 and not kwargs);calls.append(args);return result
 fakeguard=SimpleNamespace(time=m.time,schedule_gpu_handoff=lambda *args:guarded.append(True))
 def fake_module(name,path):return fakeguard if Path(path)==m.qa.GUARD else Trusted
 with patch.object(m,'authorize',return_value=None),patch.object(m,'make_job',return_value=job),patch.object(m,'restore_cache',return_value=None),patch.object(m,'cached',return_value=None),patch.object(m.qa,'APPROVED',dict(m.qa.APPROVED,modelPins=[])),patch.object(m.qa,'resource_reason',return_value=None),patch.object(m,'module',side_effect=fake_module),patch.object(m.full,'read_window',return_value=(mono,hashes)),patch.object(m.qa.voice,'immutable_json',return_value=None):
  check('approved factory receives only audio and rate, never expected text or hotwords',lambda:yes(m.recognize(jp,root/'resource-decline-none.json')==0 and len(calls)==2))
 with patch.object(m.runtime,'alive',return_value=False),patch.object(m,'children',return_value=[dict(pid=99)]):
  check('orphaned own recognizer preserves singleton ownership',lambda:yes(m.owned_alive(dict(pid=1))))
 with patch.object(m.runtime,'alive',return_value=False),patch.object(m,'children',return_value=[]),patch.object(m.psutil,'process_iter',return_value=[SimpleNamespace(info=dict(cmdline=['exact','context']))]):
  check('launch-gap exact command preserves worker',lambda:yes(m.owned_alive(dict(phase='launching-context-model',launchCommand=['exact','context']))))
print(json.dumps(dict(passed=len(checks),checks=checks,syntheticOnly=True,actualContextPcmRead=False,actualMediaExtracted=False,modelLoaded=False,gpuGuardCalledOnlySynthetic=True,gpuLeaseMutated=False,externalProcessStarted=False),ensure_ascii=False))
