"""One finite independent decode of only ambiguous complete source contexts."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,time
import numpy as np
import soundfile as sf
H=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('v7_context_source_review',H/'voice-review.py')
r=importlib.util.module_from_spec(s);s.loader.exec_module(r);c=r.c
def worker(token):
 plan=c.validate(preserve_pcm=True);c.lease_worker(token)
 full=c.read(c.O/'source-asr-review.json');assert full['complete']and full['sceneCount']==21
 sources={x['id']:x for x in c.read(c.O/'tts-current.json')['scenes']}
 definition=H/'source-context-plan.json';items=c.read(definition)['contexts']
 folder=c.O/'contexts';folder.mkdir(exist_ok=True)
 model=None;transcriber=None;rows=[]
 signature=hashlib.sha256(json.dumps(dict(planSha256=c.sha(definition),recognizer=plan['asrIdentity'],longFileChunking=False,prompt=None,recognitionPad=.75),sort_keys=True).encode()).hexdigest()
 for item in items:
  c.selected();row=sources[item['scene']];file=c.R/row['file'];assert c.sha(file)==row['sha256']
  cache=folder/(item['id']+'.json');clip=folder/(item['id']+'.wav')
  if cache.exists():
   result=c.read(cache);assert result['sourceSha256']==row['sha256']and result['identitySha256']==signature
   assert c.sha(clip)==result['contextSha256']
  else:
   assert not clip.exists(),'Preserve unreceipted independent context before retry'
   raw,rate=sf.read(file,dtype='int16');lo=round(item['start']*rate);hi=min(len(raw),round(item['end']*rate))
   assert 0<=lo<hi<=len(raw)and (hi-lo)/rate<25
   padding=round(.75*rate);x=np.concatenate([np.zeros(padding,dtype=np.int16),raw[lo:hi],np.zeros(padding,dtype=np.int16)])
   sf.write(clip,x,rate,subtype='PCM_16')
   if transcriber is None:
    c.wait_memory(plan['resources']['sourceAsr']['minimumFreeMiB'],'source-context-worker')
    import torch
    from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
    torch.set_num_threads(2);torch.cuda.set_per_process_memory_fraction(plan['resources']['sourceAsr']['allocatorCapMiB']*1048576/torch.cuda.get_device_properties(0).total_memory)
    local=r.model_path();assert c.sha(local/'config.json')==plan['asrIdentity']['configSha256']
    model=AutoModelForSpeechSeq2Seq.from_pretrained(str(local),dtype=torch.float16,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager',local_files_only=True)
    r.suppress_unused_encoder_attention_retention(model);model.to('cuda:0')
    processor=AutoProcessor.from_pretrained(str(local),local_files_only=True)
    transcriber=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float16,device='cuda:0')
   print('Independent complete context',item['id'],flush=True)
   recognized=transcriber(str(clip),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
   result=dict(id=item['id'],scene=item['scene'],sourceFile=row['file'],sourceSha256=row['sha256'],
    sourceRangeSamples=[lo,hi],sourceSampleRate=rate,sourceRangeSeconds=[lo/rate,hi/rate],
    contextFile=c.rel(clip),contextSha256=c.sha(clip),recognitionOnlyLeadingTrailingPadSamples=padding,
    padNotInProduction=True,longFileChunking=False,expectedTextPrompt=None,identitySha256=signature,
    text=recognized['text'],words=recognized['chunks'],recognizedAt=time.time(),humanListening='pending',directContextReview='pending')
   c.save(cache,result);torch.cuda.empty_cache()
  rows.append(result)
 c.save(c.O/'source-context-review.json',dict(schemaVersion=1,part=1,wholeSourceAsrSha256=c.sha(c.O/'source-asr-review.json'),planSha256=c.sha(definition),contexts=rows,sourcePcmUnchanged=True,finalContentDecision='pending direct complete text comparison; independent ASR is not human listening'))
def main():
 p=argparse.ArgumentParser();p.add_argument('--gpu-approved',action='store_true');p.add_argument('--worker');a=p.parse_args()
 if a.worker:return worker(a.worker)
 assert a.gpu_approved;plan=c.validate();rs=plan['resources']['sourceAsr']
 c.run_worker('source-context',Path(__file__).resolve(),rs['allocatorCapMiB'],rs['minimumFreeMiB'])
if __name__=='__main__':main()
