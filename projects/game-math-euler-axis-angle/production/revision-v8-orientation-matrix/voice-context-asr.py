"""One finite selected-context ASR slot after root's explicit GPU handoff.

Eight complete original paragraphs resolve actual source-ASR ambiguities.
No scene/take mutation, expected prompt, blanket ASR repeat or retake.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,json,subprocess,sys,time,uuid
H=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('v8_context_common',H/'audio-common.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
s=importlib.util.spec_from_file_location('v8_context_whisper',c.P/'production/revision-v7-part1/voice-review.py');u=importlib.util.module_from_spec(s);s.loader.exec_module(u)
TARGETS=[('m03',2,'Object-attached frame wording'),('m05',3,'Transpose coordinate(2,0,-1) and initial word'),
 ('m07',2,'Cos60 component one half, not two'),('m08',7,'Canonical transpose term'),('m09',2,'World space term'),
 ('m09',7,'Both coordinate conversion directions'),('m13',3,'Canonical transpose term in summary'),('m13',4,'Posture memory-cost summary opening')]
def worker(token):
 plan=c.validate();c.lease_worker(token);current=c.read(c.O/'tts-current.json');script={x['id']:x for x in c.read(H/'voice-input.json')['scenes']};byid={x['id']:x for x in current['scenes']}
 q=c.O/'context-asr';q.mkdir(exist_ok=True);transcriber=None;rows=[]
 identity=hashlib.sha256(json.dumps(dict(config=u.CONFIG,model=plan['asrIdentity'],scope='complete-original-raw-paragraph-only'),sort_keys=True).encode()).hexdigest()
 for sid,line,reason in TARGETS:
  c.selected();take=byid[sid]['lines'][line-1];file=c.R/take['takeFile'];assert c.sha(file)==take['takeSha256'];ident=f'{sid}.L{line:02}';cache_file=q/(ident+'.json')
  if cache_file.exists():
   row=c.read(cache_file);assert row['audio_sha256']==take['takeSha256']and row['recognitionIdentitySha256']==identity
   print('Reused exact selected paragraph cache',ident,flush=True)
  else:
   if transcriber is None:
    c.wait_memory(plan['resources']['sourceAsr']['minimumFreeMiB'])
    import torch
    from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
    torch.set_num_threads(2);torch.cuda.set_per_process_memory_fraction(plan['resources']['sourceAsr']['allocatorCapMiB']*1048576/torch.cuda.get_device_properties(0).total_memory)
    local=u.model_path();assert c.sha(local/'config.json')==plan['asrIdentity']['configSha256']
    model=AutoModelForSpeechSeq2Seq.from_pretrained(str(local),dtype=torch.float16,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager',local_files_only=True)
    u.suppress_unused_encoder_attention_retention(model);model.to('cuda:0');processor=AutoProcessor.from_pretrained(str(local),local_files_only=True)
    transcriber=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float16,device='cuda:0',chunk_length_s=25,stride_length_s=3,batch_size=1)
   print('Recognizing complete ambiguous source paragraph',ident,reason,flush=True)
   result=transcriber(str(file),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
   row=dict(id=ident,scene=sid,line=line,audioFile=take['takeFile'],audio_sha256=take['takeSha256'],recognitionIdentitySha256=identity,configuration=u.CONFIG,
    expectedPrompt=None,text=result['text'],words=result['chunks'],recognizedAt=time.time(),sourcePcmUnchanged=True,reason=reason,
    expectedForPostRecognitionComparison=script[sid]['lines'][line-1],directFullTextComparison='pending',humanListening='pending')
   c.save(cache_file,row);torch.cuda.empty_cache()
  rows.append(row)
 c.save(c.O/'context-asr-review.json',dict(revision='orientation-matrix-v8',sourceReceiptSha256=c.sha(c.O/'tts-current.json'),
  scope='Only8 previously identified ambiguous complete paragraphs; all raw/current PCM unchanged',complete=len(rows)==len(TARGETS),paragraphs=rows,
  wholeSourceAsrReused=True,newFullSourceAsr=False,automaticAudioRepair=False,humanListening='pending'))
def main():
 p=argparse.ArgumentParser();p.add_argument('--gpu-approved',action='store_true');p.add_argument('--worker');a=p.parse_args()
 if a.worker:return worker(a.worker)
 assert a.gpu_approved,'Wait for explicit root GPU handoff';plan=c.validate();assert not c.LEASE.exists(),'Preserve existing foreign/shared GPU owner'
 import psutil
 before=c.wait_memory(plan['resources']['sourceAsr']['minimumFreeMiB']);me=psutil.Process();token=str(uuid.uuid4());state=dict(schemaVersion=1,project=c.P.name,revision='orientation-matrix-v8',
  purpose='One finite8-complete-paragraph source ambiguity ASR check',token=token,coordinator=dict(pid=me.pid,createTime=me.create_time()),state='running',
  startedAt=time.time(),gpuBefore=before,sourceReceiptSha256=c.sha(c.O/'tts-current.json'),approvedScriptSha256=c.APPROVED,foreignProcessesChanged=False)
 with c.LEASE.open('x',encoding='utf8')as f:json.dump(state,f)
 child=None;code=1
 try:
  with(c.O/'context-asr-worker.log').open('ab')as log:
   child=subprocess.Popen([sys.executable,'-u','-X','utf8',str(Path(__file__)),'--worker',token],cwd=c.R,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
   state['workerPid']=child.pid;c.save(c.O/'context-asr-execution.json',state);code=child.wait()
  assert code==0,'Inspect actual selected-context failure; keep original caches'
 finally:
  state.update(state='complete'if code==0 else'failed',returnCode=code,endedAt=time.time());c.save(c.O/'context-asr-execution.json',state)
  if child is not None and child.poll()is None:state['state']='owned-child-still-running';c.save(c.LEASE,state)
  elif c.LEASE.exists()and c.read(c.LEASE).get('token')==token:c.LEASE.unlink()
 return code
if __name__=='__main__':main()
