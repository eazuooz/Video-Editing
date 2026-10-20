"""One source-ASR cache per V6 PCM hash; direct text/listening review stays pending."""
from pathlib import Path
import argparse,difflib,importlib.util,json,os,re,subprocess,sys,time,uuid
import psutil
H=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('voice_render_v6',H/'voice-render.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
R,P,O,LEASE=v.R,v.P,v.O,v.LEASE
def norm(s):return re.sub('[^a-z0-9가-힣]','',s.lower())
def worker(token):
 v.validate();lease=v.read(LEASE);owner=lease['coordinator'];me=psutil.Process()
 assert lease['token']==token and lease['project']==P.name
 assert any(x.pid==owner['pid'] and abs(x.create_time()-owner['createTime'])<.02 for x in [me,*me.parents()])
 done=v.read(O/'tts-current.json');assert done['status']=='complete-source-ASR-pending' and done['sceneCount']==41
 script=v.read(P/'script/revision-v6-article-flow/narration.ko.json');byid={x['id']:x for x in script['scenes']}
 qa=O/'asr';qa.mkdir(exist_ok=True);model=None;transcriber=None;summaries=[]
 for audio in done['scenes']:
  v.selected();path=R/audio['file'];assert v.sha(path)==audio['sha256'];cache=qa/f'{audio["id"]}.json'
  cached=v.read(cache) if cache.exists() else {}
  if cached.get('audio_sha256')!=audio['sha256']:
   assert not cache.exists(),'Stale ASR artifact requires explicit preservation/review, not overwrite'
   if transcriber is None:
    import torch
    from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
    torch.set_num_threads(2);torch.cuda.set_per_process_memory_fraction(6144*1048576/torch.cuda.get_device_properties(0).total_memory)
    model_path=R/'qwen3-tts/models/whisper-large-v3-turbo';assert (model_path/'model.safetensors').exists()
    model=AutoModelForSpeechSeq2Seq.from_pretrained(str(model_path),dtype=torch.float16,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager').to('cuda:0')
    processor=AutoProcessor.from_pretrained(str(model_path))
    transcriber=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float16,device='cuda:0',chunk_length_s=25,stride_length_s=3,batch_size=1)
   print('Recognizing current source PCM once',audio['id'],flush=True)
   raw=transcriber(str(path),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
   cached=dict(scene=audio['id'],audio_sha256=audio['sha256'],text=raw['text'],words=raw['chunks'],configuration=dict(chunkLengthSeconds=25,strideSeconds=3,batchSize=1,prompt=None))
   v.save(cache,cached)
  else:print('Reused exact-PCM successful ASR cache',audio['id'],flush=True)
  expected=' '.join(byid[audio['id']]['lines']);a,b=norm(expected),norm(cached['text']);matcher=difflib.SequenceMatcher(None,a,b,autojunk=False)
  summaries.append(dict(scene=audio['id'],audio_sha256=audio['sha256'],expected=expected,recognized=cached['text'],similarity=matcher.ratio(),
   differences=[dict(kind=t,expected=a[i:j],recognized=b[k:l]) for t,i,j,k,l in matcher.get_opcodes() if t!='equal'],
   directTextReview='pending',humanListening='pending'))
  v.save(O/'euler-article-flow-v6.asr-review.json',dict(complete=len(summaries)==41,sceneCount=len(summaries),scenes=summaries,kind='Raw ASR evidence; spelling/numeral recognition differences are not automatic spoken errors or approval.'))
 print('All41 current source texts available for direct full-text comparison; human listening pending.',flush=True)
def main():
 p=argparse.ArgumentParser();p.add_argument('--gpu-approved',action='store_true');p.add_argument('--worker');a=p.parse_args()
 if a.worker:return worker(a.worker)
 assert a.gpu_approved,'Root GPU allocation required'
 control=v.read(R/'shared/publishing/video-production-control.json')
 assert control['selectedVideo']==P.name and control['newProductionAuthorization']['fullProductionAuthorized']
 v.validate();done=v.read(O/'tts-current.json');assert done['status']=='complete-source-ASR-pending' and done['sceneCount']==41
 assert not LEASE.exists(),'Preserve current GPU lease; source ASR starts only after TTS exits'
 free,total,util=v.gpu();assert free>=5000
 family={x.pid for x in [psutil.Process(),*psutil.Process().parents()]}
 clients=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,process_name','--format=csv,noheader'],text=True)
 assert not any('python' in line.lower() and int(line.split(',')[0]) not in family for line in clients.splitlines()),'Foreign GPU compute remains untouched; do not overlap source ASR'
 me=psutil.Process();token=str(uuid.uuid4());state=dict(token=token,project=P.name,state='tts_running',purpose='one current41-scene source ASR cache batch',coordinator=dict(pid=me.pid,createTime=me.create_time()),startedAt=time.time(),foreignProcessesPaused=[],gpuBefore=dict(freeMiB=free,totalMiB=total,utilization=util))
 with LEASE.open('x',encoding='utf8') as f:json.dump(state,f)
 code=1
 try:
  with (O/'source-asr-worker.log').open('ab') as log:
   proc=subprocess.Popen([sys.executable,'-u','-X','utf8',str(Path(__file__).resolve()),'--worker',token],cwd=R,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
   state.update(workerPid=proc.pid,status='running');v.save(O/'source-asr-execution.json',state);code=proc.wait()
 finally:
  state.update(status='ASR-ready-for-direct-full-text-review' if code==0 else 'failed',returnCode=code,endedAt=time.time());v.save(O/'source-asr-execution.json',state)
  if LEASE.exists() and v.read(LEASE).get('token')==token:LEASE.unlink()
 assert code==0,f'ASR worker exited {code}; preserve cache and inspect explicit worker log'
if __name__=='__main__':main()
