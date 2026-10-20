"""One root-dispatched ambiguity-only batch from the existing encoded48k WAV.

Each input retains one whole paragraph and real quiet padding using measured
sample-transfer ranges. Long inserted observation pauses are not ASR inputs.
Expected text is retained for later comparison only, never passed to inference.
No source/whole-video ASR, new audio decode, new voice or video render occurs.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,json,os,subprocess,time,uuid
import psutil

H=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('v6_context_approved_final_asr',H/'final-mix-review.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
R,P,O,LEASE=m.R,m.P,m.O,m.LEASE
BASE=O/'qa/final-mix-contexts';PLAN=H/'final-asr-context-plan.json'


def proof(p):return m.proof(p)
def read(p):return m.v.read(p)
def save(p,d):return m.v.save(p,d)
def selected():return m.selected()
def check(ref):
 p=R/ref['file'];assert p.is_file() and m.v.sha(p)==ref['sha256'],f'Changed context input: {ref["file"]}';return p


def context_array(stream,row):
 import numpy as np
 from scipy.signal import resample_poly
 pieces=[]
 for segment in row['segments48k']:
  first,last=segment['globalStartSample48k'],segment['globalEndSample48k']
  assert 0<=first<last<=stream.frames
  stream.seek(first);piece=stream.read(last-first,dtype='float32',always_2d=True)
  assert piece.shape==(last-first,2);pieces.append(piece)
 data=np.concatenate(pieces,axis=0)
 assert data.shape==(row['selectedSamples48k'],2) and len(data)<=25*48000
 pcm_hash=hashlib.sha256(np.asarray(data,dtype='<f4').tobytes()).hexdigest()
 raw=np.asarray(resample_poly(data.mean(axis=1,dtype=np.float32),1,3),dtype=np.float32)
 assert len(raw)<=25*16000 and np.isfinite(raw).all()
 return raw,pcm_hash,hashlib.sha256(np.asarray(raw,dtype='<f4').tobytes()).hexdigest()


def prepare():
 import soundfile as sf
 selected();plan=read(PLAN)
 assert plan['contextCount']==len(plan['contexts'])==39 and plan['maximumContextSeconds']<=25
 for ref in plan['inputs'].values():check(ref)
 previous=read(R/plan['inputs']['originalPreparation']['file'])
 assert previous['modelConfigurationSha256']==m.obj_sha(m.inference_identity(previous['modelIdentity']))
 assert previous['modelIdentity']['configuration']==m.CONFIG
 decoded=R/plan['decodedFile'];assert m.v.sha(decoded)==plan['decodedSha256']==previous['decodedSha256']
 rows=[];model_hash=previous['modelConfigurationSha256']
 with sf.SoundFile(decoded) as stream:
  assert stream.samplerate==48000 and stream.channels==2 and stream.subtype=='FLOAT'
  for row in plan['contexts']:
   check(row['sourceAsr']);raw,pcm_hash,asr_hash=context_array(stream,row)
   key=m.obj_sha({'contextPcm48kSha256':pcm_hash,'asrMono16kSha256':asr_hash,'modelConfigurationSha256':model_hash})
   cache=BASE/'cache'/f'{key}.json'
   rows.append({**row,'contextPcm48kSha256':pcm_hash,'asrMono16kSha256':asr_hash,'asrSamples':len(raw),
     'cacheKey':key,'cacheFile':m.rel(cache)})
 memory=m.memory_configuration()
 data={'schemaVersion':1,'revision':'article-flow-v6','inputs':{'plan':proof(PLAN),'originalPreparation':plan['inputs']['originalPreparation'],
   'originalWholeAsrReport':plan['inputs']['originalAsrReport'],'decodedFile':{'file':m.rel(decoded),'sha256':plan['decodedSha256']},
   'timeline':proof(H/'timeline.json'),'implementation':proof(Path(__file__)),'approvedAsrRuntime':proof(H/'final-mix-review.py')},
   'modelIdentity':previous['modelIdentity'],'modelConfigurationSha256':model_hash,'memorySafety':memory,
   'memoryExecutionConfigurationSha256':m.obj_sha(memory),'contexts':rows,'contextCount':len(rows),
   'totalSelectedSeconds':sum(x['durationSeconds'] for x in rows),
   'stitchedParagraphContextCount':sum(len(x['segments48k'])>1 for x in rows),
   'selectionScope':'Whole spoken paragraphs in original selected-sample order with at most 0.1s source quiet padding. Long final-only observation pauses are excluded; multi-segment contexts concatenate the documented actual final-audio sample ranges.',
   'validatesOriginalFinalTiming':False,'wholeAsrRepeated':False,'newAudioDecode':False,
   'expectedTextPassedToInference':False,'sourcePcmAsrRepeated':False,'humanWholeListening':'pending','automaticSpeechPass':False}
 path=BASE/'preparation.json'
 if path.exists():assert read(path)==data,'Different previous context preparation preserved; inspect instead of overwriting'
 else:save(path,data)
 return path,data


def cached(row,model_hash):
 file=R/row['cacheFile']
 if not file.exists():return None
 old=read(file)
 assert old['status']=='recognized-context-evidence-only' and old['cacheKey']==row['cacheKey']
 assert old['contextPcm48kSha256']==row['contextPcm48kSha256'] and old['asrMono16kSha256']==row['asrMono16kSha256'] and old['modelConfigurationSha256']==model_hash
 return old


def aggregate(preparation):
 p=read(preparation);rows=[];missing=[]
 for row in p['contexts']:
  result=cached(row,p['modelConfigurationSha256'])
  if result is None:missing.append(row['id']);continue
  rows.append({**row,'recognized':result['text'],'words':result['words'],'cacheSha256':m.v.sha(R/row['cacheFile']),
   'directTextComparison':'pending','humanListening':'pending','automaticSpeechPass':False})
 report={'schemaVersion':1,'revision':'article-flow-v6','inputs':p['inputs'],'preparation':proof(preparation),
  'contextCount':len(p['contexts']),'recognizedContexts':len(rows),'complete':not missing,'missingContexts':missing,'contexts':rows,
  'scope':'One selected complete-paragraph context batch from the actual previous encoded master audio; same decoded WAV reused. Long inserted observation pauses are excluded and documented multi-segment paragraphs are stitched in source-sample order. This is speech-content evidence, not verification of original final timing. Exact AAC equivalence separately binds a later visual-only master.',
  'totalSelectedSeconds':p['totalSelectedSeconds'],'stitchedParagraphContextCount':p['stitchedParagraphContextCount'],
  'validatesOriginalFinalTiming':False,
  'originalWholeAsrRepeated':False,'sourcePcmAsrRepeated':False,'newAudioDecode':False,'expectedTextPassedToInference':False,
  'directFullContextReview':'pending','humanWholeListening':'pending','humanPaceListening':'pending','pronunciation':'pending','automaticSpeechPass':False}
 output=BASE/'context-asr-review.json';save(output,report);return missing,output


def worker(token,preparation,retry_failed):
 import soundfile as sf
 selected();p=read(preparation);lease=read(LEASE);me=psutil.Process();owner=lease['coordinator']
 assert lease['token']==token and lease['purpose']=='one selected complete-context encoded-mix ASR evidence batch' and lease['project']==P.name
 assert any(x.pid==owner['pid'] and abs(x.create_time()-owner['createTime'])<.02 for x in [me,*me.parents()])
 for ref in p['inputs'].values():check(ref)
 assert p['memorySafety']==m.memory_configuration() and p['memoryExecutionConfigurationSha256']==m.obj_sha(p['memorySafety'])
 model=None;transcriber=None
 with sf.SoundFile(R/p['inputs']['decodedFile']['file']) as stream:
  for row in p['contexts']:
   selected()
   if cached(row,p['modelConfigurationSha256']) is not None:
    print('Reused successful selected context',row['id'],flush=True);continue
   raw,pcm_hash,asr_hash=context_array(stream,row)
   assert pcm_hash==row['contextPcm48kSha256'] and asr_hash==row['asrMono16kSha256']
   file=R/row['cacheFile'];attempt=file.with_suffix('.attempt.json')
   if attempt.exists():assert retry_failed and read(attempt)['status']=='failed','Preserve an incomplete/failed attempt; explicit root retry required'
   if transcriber is None:
    m.wait_for_preload_memory('context-worker',BASE)
    import torch
    from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
    torch.set_num_threads(2);torch.cuda.set_per_process_memory_fraction(m.ASR_CAP_MIB*1048576/torch.cuda.get_device_properties(0).total_memory)
    local=m.approved_asr.model_path();assert local.resolve()==Path(p['modelIdentity']['resolvedModelPath']).resolve()
    model=AutoModelForSpeechSeq2Seq.from_pretrained(str(local),dtype=torch.float16,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager',local_files_only=True)
    retention=m.suppress_unused_encoder_attention_retention(model);model.to('cuda:0')
    processor=AutoProcessor.from_pretrained(str(local),local_files_only=True)
    transcriber=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float16,device='cuda:0',chunk_length_s=25,stride_length_s=3,batch_size=1)
    save(BASE/'encoder-retention-execution.json',{'wrapper':retention,'memorySafety':p['memorySafety'],'modelConfigurationSha256':p['modelConfigurationSha256']})
   state={'status':'running','context':row['id'],'cacheKey':row['cacheKey'],'preparationSha256':m.v.sha(preparation),'startedAt':time.time(),'pid':me.pid};save(attempt,state)
   try:
    print('Recognizing selected complete encoded paragraph once',row['id'],flush=True)
    result=transcriber({'raw':raw,'sampling_rate':16000},generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
    save(file,{'status':'recognized-context-evidence-only','cacheKey':row['cacheKey'],'contextPcm48kSha256':pcm_hash,
     'asrMono16kSha256':asr_hash,'modelConfigurationSha256':p['modelConfigurationSha256'],'configuration':m.CONFIG,
     'memorySafety':p['memorySafety'],'text':result['text'],'words':result['chunks'],'recognizedAt':time.time(),
     'expectedTextPassedToInference':False,'automaticSpeechPass':False})
    state.update(status='complete',endedAt=time.time(),cacheSha256=m.v.sha(file));save(attempt,state)
    del result,raw;torch.cuda.empty_cache()
   except BaseException as error:
    state.update(status='failed',endedAt=time.time(),error=repr(error));save(attempt,state);raise
   aggregate(preparation)
 missing,output=aggregate(preparation);assert not missing
 print('Selected context evidence complete; direct comparison/listening remains separate.',m.rel(output),flush=True)


def acquire(preparation,data,retry_failed):
 missing,output=aggregate(preparation)
 if not missing:print('All successful context caches reused; no GPU/model started.');return
 assert not LEASE.exists(),'Foreign/current GPU lease preserved'
 m.wait_for_preload_memory('context-coordinator',BASE)
 me=psutil.Process();token=uuid.uuid4().hex
 state={'token':token,'project':P.name,'purpose':'one selected complete-context encoded-mix ASR evidence batch',
  'coordinator':{'pid':me.pid,'createTime':me.create_time()},'foreignProcessesPaused':[],
  'preparation':proof(preparation),'startedAt':time.time(),'memorySafety':data['memorySafety']}
 with LEASE.open('x',encoding='utf-8') as f:json.dump(state,f)
 code=1
 try:
  command=[str(m.PYTHON),'-u','-X','utf8',str(Path(__file__).resolve()),'--worker',token,'--preparation',str(preparation)]
  if retry_failed:command.append('--retry-failed')
  with (BASE/'worker.log').open('ab') as log:
   proc=subprocess.Popen(command,cwd=R,stdout=log,stderr=subprocess.STDOUT,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0));state['workerPid']=proc.pid;save(BASE/'execution.json',state);code=proc.wait()
 finally:
  state.update(status='complete-evidence-only' if code==0 else 'failed',returnCode=code,endedAt=time.time());save(BASE/'execution.json',state)
  if LEASE.exists() and read(LEASE).get('token')==token:LEASE.unlink()
 assert code==0,'Selected context batch failed; preserve successful caches and inspect its log before an explicit retry'


def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--prepare-only',action='store_true');parser.add_argument('--gpu-approved',action='store_true')
 parser.add_argument('--worker');parser.add_argument('--preparation',type=Path);parser.add_argument('--retry-failed',action='store_true');args=parser.parse_args()
 if args.worker:assert args.preparation;return worker(args.worker,args.preparation,args.retry_failed)
 assert args.prepare_only or args.gpu_approved,'Explicit root CPU preparation or allocated GPU dispatch required'
 preparation,data=prepare()
 if args.prepare_only:print('Selected39 paragraph contexts prepared; no model/GPU/ASR started.',m.rel(preparation));return
 acquire(preparation,data,args.retry_failed)


if __name__=='__main__':main()
