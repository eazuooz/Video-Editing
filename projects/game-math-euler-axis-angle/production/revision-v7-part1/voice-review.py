"""One source-ASR cache per exact new PCM; full raw text remains review evidence."""
from pathlib import Path
import argparse,difflib,functools,hashlib,importlib.util,inspect,json,re,time
H=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('v7_audio_common',H/'audio-common.py');c=importlib.util.module_from_spec(sp);sp.loader.exec_module(c)
CONFIG=dict(model='openai/whisper-large-v3-turbo',dtype='float16',attention='eager',chunkLengthSeconds=25,strideSeconds=3,batchSize=1,language='korean',task='transcribe',wordTimestamps=True,prompt=None)
def model_path():
 local=c.R/'qwen3-tts/models/whisper-large-v3-turbo'
 if not (local/'config.json').exists():
  from huggingface_hub import snapshot_download
  local=Path(snapshot_download('openai/whisper-large-v3-turbo',local_files_only=True))
 assert all((local/x).exists() for x in ['config.json','model.safetensors','preprocessor_config.json','tokenizer_config.json','tokenizer.json'])
 return local
def suppress_unused_encoder_attention_retention(model):
 encoder=model.get_encoder()
 assert type(encoder).__name__=='WhisperEncoder' and model.config._attn_implementation=='eager'
 assert not getattr(encoder,'_v6_no_unused_encoder_attention_retention',False)
 original=encoder.forward;signature=inspect.signature(original)
 assert 'output_attentions' in signature.parameters
 @functools.wraps(original)
 def encoder_forward_without_retained_attention(*args,**kwargs):
  bound=signature.bind_partial(*args,**kwargs)
  bound.arguments['output_attentions']=False
  return original(*bound.args,**bound.kwargs)
 encoder.forward=encoder_forward_without_retained_attention
 encoder._v6_no_unused_encoder_attention_retention=True
 assert inspect.signature(encoder.forward)==signature,'HF encoder-kwargs signature filtering must remain unchanged'
 return dict(policy='encoder-no-unused-attention-retention-v1',decoderForwardChanged=False,modelConfigChanged=False,installedLibraryModified=False)
def normalized(text):return re.sub('[^a-z0-9가-힣]','',text.lower())
def worker(token):
 plan=c.validate(preserve_pcm=True);c.lease_worker(token)
 completed=c.read(c.O/'tts-current.json')
 assert completed['status']=='complete-source-ASR-pending' and completed['sceneCount']==21
 script=c.read(H/'voice-input.json');byid={s['id']:s for s in script['scenes']};qa=c.O/'asr';qa.mkdir(exist_ok=True)
 model=None;transcriber=None;summaries=[]
 model_id=plan['asrIdentity'];cache_identity=hashlib.sha256(json.dumps(dict(config=CONFIG,model=model_id),sort_keys=True).encode()).hexdigest()
 for audio in completed['scenes']:
  c.selected();file=c.R/audio['file'];assert c.sha(file)==audio['sha256']
  path=qa/(audio['id']+'.json');cache=c.read(path) if path.exists() else None
  if cache:
   assert cache['audio_sha256']==audio['sha256'] and cache['recognitionIdentitySha256']==cache_identity,'Preserve stale recognition evidence'
   print('Reused exact-PCM successful ASR',audio['id'],flush=True)
  else:
   if transcriber is None:
    c.wait_memory(plan['resources']['sourceAsr']['minimumFreeMiB'],'source-ASR-worker')
    import torch
    from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
    torch.set_num_threads(2)
    torch.cuda.set_per_process_memory_fraction(plan['resources']['sourceAsr']['allocatorCapMiB']*1048576/torch.cuda.get_device_properties(0).total_memory)
    local=model_path()
    assert c.sha(local/'config.json')==model_id['configSha256']
    model=AutoModelForSpeechSeq2Seq.from_pretrained(str(local),dtype=torch.float16,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager',local_files_only=True)
    memory=suppress_unused_encoder_attention_retention(model);model.to('cuda:0')
    processor=AutoProcessor.from_pretrained(str(local),local_files_only=True)
    transcriber=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float16,device='cuda:0',chunk_length_s=25,stride_length_s=3,batch_size=1)
    c.save(c.O/'asr-memory-execution.json',dict(configuration=CONFIG,memory=memory,recognitionIdentitySha256=cache_identity))
   print('Recognizing new source once',audio['id'],flush=True)
   result=transcriber(str(file),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
   cache=dict(scene=audio['id'],audio_sha256=audio['sha256'],recognitionIdentitySha256=cache_identity,configuration=CONFIG,text=result['text'],words=result['chunks'],recognizedAt=time.time(),automaticSpeechPass=False)
   c.save(path,cache);del result
   torch.cuda.empty_cache()
  expected=' '.join(byid[audio['id']]['lines']);a=normalized(expected);b=normalized(cache['text']);match=difflib.SequenceMatcher(None,a,b,autojunk=False)
  summaries.append(dict(scene=audio['id'],audioFile=audio['file'],audioSha256=audio['sha256'],asrFile=c.rel(path),asrSha256=c.sha(path),expected=expected,recognized=cache['text'],similarity=match.ratio(),differences=[dict(kind=t,expected=a[i:j],recognized=b[k:l]) for t,i,j,k,l in match.get_opcodes() if t!='equal'],directFullTextReview='pending',humanListening='pending'))
  c.save(c.O/'source-asr-review.json',dict(schemaVersion=1,part=1,complete=len(summaries)==21,sceneCount=len(summaries),scenes=summaries,kind='Raw recognition evidence; spelling and numerical differences need direct contextual review, not automatic approval.'))
 print('All21 source transcripts available; full text/content and human listening pending',flush=True)
def main():
 p=argparse.ArgumentParser();p.add_argument('--gpu-approved',action='store_true');p.add_argument('--worker');a=p.parse_args()
 if a.worker:return worker(a.worker)
 assert a.gpu_approved,'Root serialized GPU-start message required'
 plan=c.validate();r=plan['resources']['sourceAsr'];model_path()
 c.run_worker('source-asr',Path(__file__).resolve(),r['allocatorCapMiB'],r['minimumFreeMiB'])
if __name__=='__main__':main()

