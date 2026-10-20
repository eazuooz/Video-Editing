"""One finite six-context ASR check; original41 PCM/ASR caches stay immutable."""
from pathlib import Path
import argparse,importlib.util,json,os,subprocess,sys,time,uuid
import numpy as np
import soundfile as sf
import psutil
H=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('v6_source_asr',H/'voice-review.py');a=importlib.util.module_from_spec(sp);sp.loader.exec_module(a)
v=a.v;R,P,V,LEASE=a.R,a.P,a.O,a.LEASE;D=V/'ambiguities'
def prepare():
 v.selected();assert v.read(V/'source-asr-execution.json')['status']=='ASR-ready-for-direct-full-text-review'
 done=v.read(V/'tts-current.json');by={x['id']:x for x in done['scenes']};rows=[]
 words=v.read(V/'asr/v6-09.json')['words'];last_same=max(w['timestamp'][0] for w in words if w['text'].strip()=='같은')
 specs=[('v6-10.opening',[('v6-09',max(0,last_same-.12),None),('v6-10',0,15.76)]),
  ('v6-12.yaw',[('v6-12',17.05,42.80)]),('v6-13.word',[('v6-13',18.78,28.05)]),
  ('v6-32.definition',[('v6-31',55.14,None),('v6-32',0,18.35)]),
  ('v6-36.overlap',[('v6-36',34.24,None)]),('v6-41.overlap',[('v6-41',17.48,39.26)])]
 D.mkdir(parents=True,exist_ok=True)
 for ident,parts in specs:
  arrays=[];provenance=[];at=0
  for sid,left,right in parts:
   source=R/by[sid]['file'];assert v.sha(source)==by[sid]['sha256'];pcm,rate=sf.read(source,dtype='int16',always_2d=True)
   assert rate==24000 and pcm.shape[1]==1
   start=round(left*rate);end=len(pcm) if right is None else min(len(pcm),round(right*rate));assert end>start
   data=pcm[start:end];arrays.append(data);provenance.append(dict(scene=sid,sourceFile=by[sid]['file'],sourceSha256=by[sid]['sha256'],sourceStartSample=start,sourceEndSample=end,contextStartSample=at,contextEndSample=at+len(data),originalPcmPartSha256=v.hashlib.sha256(data.tobytes()).hexdigest()));at+=len(data)
  clip=np.concatenate(arrays);file=D/(ident+'.wav')
  if file.exists():
   old,rate=sf.read(file,dtype='int16',always_2d=True);assert rate==24000 and np.array_equal(clip,old),'Never replace a different contextual clip'
  else:sf.write(file,clip,24000,subtype='PCM_16')
  rows.append(dict(id=ident,file=file.relative_to(R).as_posix(),sha256=v.sha(file),samples=len(clip),sampleRate=24000,seconds=len(clip)/24000,parts=provenance,sourcePcmSamplesPreserved=True))
 plan=dict(schemaVersion=1,revision='article-flow-v6',scope='Six independent complete instructional contexts only; no full-scene/source rerun, no expected text prompt, no source PCM mutation.',
  inputs=dict(currentTtsReceiptSha256=v.sha(V/'tts-current.json'),currentFullAsrReceiptSha256=v.sha(V/'euler-article-flow-v6.asr-review.json'),koSha256=v.sha(P/'script/revision-v6-article-flow/narration.ko.json')),
  contexts=rows,model=str(a.model_path()),configuration=dict(chunkLengthSeconds=25,strideSeconds=3,batchSize=1,language='korean',prompt=None),humanListening='pending')
 v.save(D/'plan.json',plan);print('Prepared exact-source6 complete contexts:',[round(x['seconds'],2) for x in rows],flush=True)
 return plan
def worker(token):
 lease=v.read(LEASE);owner=lease['coordinator'];me=psutil.Process()
 assert lease['token']==token and lease['project']==P.name and any(x.pid==owner['pid'] and abs(x.create_time()-owner['createTime'])<.02 for x in [me,*me.parents()])
 plan=v.read(D/'plan.json');model=None;pipe=None;rows=[]
 for context in plan['contexts']:
  v.selected();source=R/context['file'];assert v.sha(source)==context['sha256'];cache=D/(context['id']+'.asr.json')
  if cache.exists():
   result=v.read(cache);assert result['audioSha256']==context['sha256'];print('Reused exact successful contextual ASR',context['id'],flush=True)
  else:
   if pipe is None:
    import torch
    from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
    torch.set_num_threads(2);torch.cuda.set_per_process_memory_fraction(a.ASR_CAP_MIB*1048576/torch.cuda.get_device_properties(0).total_memory)
    mid=str(a.model_path());model=AutoModelForSpeechSeq2Seq.from_pretrained(mid,dtype=torch.float16,attn_implementation='eager',local_files_only=True).to('cuda:0');proc=AutoProcessor.from_pretrained(mid,local_files_only=True)
    pipe=pipeline('automatic-speech-recognition',model=model,tokenizer=proc.tokenizer,feature_extractor=proc.feature_extractor,dtype=torch.float16,device='cuda:0',chunk_length_s=25,stride_length_s=3,batch_size=1)
   print('Independent complete context',context['id'],flush=True);raw=pipe(str(source),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
   result=dict(id=context['id'],audioSha256=context['sha256'],text=raw['text'],words=raw['chunks'],configuration=plan['configuration'],parts=context['parts'],humanListening='pending');assert result['text'].strip() and result['words'];v.save(cache,result);del raw;torch.cuda.empty_cache()
  rows.append(result);v.save(D/'results.json',dict(complete=len(rows)==6,contexts=rows,planSha256=v.sha(D/'plan.json'),humanListening='pending'))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--prepare-only',action='store_true');ap.add_argument('--gpu-approved',action='store_true');ap.add_argument('--worker');args=ap.parse_args()
 if args.worker:return worker(args.worker)
 plan=prepare()
 if args.prepare_only:return
 assert args.gpu_approved;control=v.read(R/'shared/publishing/video-production-control.json');assert control['selectedVideo']==P.name and control['newProductionAuthorization']['fullProductionAuthorized']
 assert not LEASE.exists();free,total,util=v.gpu();assert free>=a.ASR_MIN_FREE_MIB
 family={x.pid for x in [psutil.Process(),*psutil.Process().parents()]};clients=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,process_name','--format=csv,noheader'],text=True)
 assert not any('python' in s.lower() and int(s.split(',')[0]) not in family for s in clients.splitlines())
 me=psutil.Process();token=str(uuid.uuid4());state=dict(token=token,project=P.name,state='tts_running',purpose='one finite6-context source-ASR ambiguity batch; no full-scene rerun',coordinator=dict(pid=me.pid,createTime=me.create_time()),startedAt=time.time(),foreignProcessesPaused=[],gpuBefore=dict(freeMiB=free,totalMiB=total),planSha256=v.sha(D/'plan.json'))
 with LEASE.open('x',encoding='utf8') as f:json.dump(state,f)
 code=1
 try:
  with (D/'worker.log').open('ab') as log:
   proc=subprocess.Popen([sys.executable,'-u','-X','utf8',str(Path(__file__).resolve()),'--worker',token],cwd=R,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW);state.update(workerPid=proc.pid,status='running');v.save(D/'execution.json',state);code=proc.wait()
 finally:
  state.update(status='complete-direct-context-review-pending' if code==0 else 'failed',returnCode=code,endedAt=time.time());v.save(D/'execution.json',state)
  if LEASE.exists() and v.read(LEASE).get('token')==token:LEASE.unlink()
 assert code==0,'Preserve contextual caches and inspect explicit worker log'
if __name__=='__main__':main()
