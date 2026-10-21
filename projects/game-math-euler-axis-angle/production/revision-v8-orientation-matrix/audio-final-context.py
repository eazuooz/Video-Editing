"""One bounded actual-AAC m04L01/L02 ambiguity check; no second whole ASR."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,subprocess,sys,time,uuid
import psutil
H=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('v8_final_context_common',H/'audio-common.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
s=importlib.util.spec_from_file_location('v8_final_context_whisper',c.P/'production/revision-v7-part1/voice-review.py');u=importlib.util.module_from_spec(s);s.loader.exec_module(u)
def worker(token):
 plan=c.validate();c.lease_worker(token);selected=c.read(H/'audio-final-input.json');assert c.sha(c.R/selected['master'])==selected['masterSha256']
 level=c.read(c.O/'final-aac-level-review.json');assert level['masterSha256']==selected['masterSha256']and level['actualFinalMasterBindingComplete']
 decoded=c.R/level['decodedFile'];assert c.sha(decoded)==level['decodedSha256'];t=c.read(H/'timeline.json');scene=next(x for x in t['scenes']if x['id']=='m04')
 alignment=next(x for x in c.read(c.O/'source-alignment.json')['scenes']if x['id']=='m04');scripts=c.read(H/'voice-input.json')['scenes'][3]['lines']
 q=c.O/'final-context';q.mkdir(exist_ok=True);rows=[];recognizer=None
 import soundfile as sf
 for line in [1,2]:
  origin=alignment['lines'][line-1];start=scene['startFrame']*800+round(origin['takeStart']*48000);end=scene['startFrame']*800+round(origin['takeEnd']*48000)
  file=q/f'm04.L{line:02}.wav';cachefile=q/f'm04.L{line:02}.json'
  if not file.exists():
   with sf.SoundFile(decoded)as f:f.seek(start);x=f.read(end-start,dtype='float32',always_2d=True);assert len(x)==end-start
   sf.write(file,x,48000,subtype='FLOAT')
  digest=c.sha(file)
  if cachefile.exists():
   row=c.read(cachefile);assert row['audio_sha256']==digest and row['masterSha256']==selected['masterSha256']
  else:
   if recognizer is None:
    c.wait_memory(plan['resources']['sourceAsr']['minimumFreeMiB'])
    import torch
    from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
    torch.set_num_threads(2);torch.cuda.set_per_process_memory_fraction(plan['resources']['sourceAsr']['allocatorCapMiB']*1048576/torch.cuda.get_device_properties(0).total_memory)
    local=u.model_path();assert c.sha(local/'config.json')==plan['asrIdentity']['configSha256']
    model=AutoModelForSpeechSeq2Seq.from_pretrained(str(local),dtype=torch.float16,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager',local_files_only=True)
    u.suppress_unused_encoder_attention_retention(model);model.to('cuda:0');processor=AutoProcessor.from_pretrained(str(local),local_files_only=True)
    recognizer=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float16,device='cuda:0',chunk_length_s=25,stride_length_s=3,batch_size=1)
   print('Recognize actual AAC complete ambiguity paragraph',line,flush=True)
   result=recognizer(str(file),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
   row=dict(scene='m04',line=line,masterSha256=selected['masterSha256'],inputSha256=c.sha(H/'audio-final-input.json'),audioFile=c.rel(file),audio_sha256=digest,
    actualMasterAacPayloadSha256=level['aacPacketPayloadSha256'],exactDecodedProgramFile=level['decodedFile'],exactDecodedProgramSha256=level['decodedSha256'],
    extraction=dict(startSample48k=start,endSample48k=end,range=[start/48000,end/48000],speed=1,completeParagraph=True),configuration=u.CONFIG,
    expectedPrompt=None,text=result['text'],words=result['chunks'],expectedForPostRecognitionComparison=scripts[line-1],humanListening='pending',recognizedAt=time.time())
   c.save(cachefile,row);torch.cuda.empty_cache()
  rows.append(row)
 c.save(c.O/'final-context-review.json',dict(revision='orientation-matrix-v8',masterSha256=selected['masterSha256'],
  inputs=dict(wholeFinalAsrSha256=c.sha(c.O/'final-aac-asr.json'),actualLevelBindingSha256=c.sha(c.O/'final-aac-level-review.json')),
  scope='Only2 complete actualAAC paragraphs m04.L01–L02;one recognition per exact clip;not a second wholeprogram inference',paragraphs=rows,
  originalWholeFinalAsrPreserved=True,sourceOrMixChanged=False,directTextReview='pending',humanListening='pending'))
def main():
 p=argparse.ArgumentParser();p.add_argument('--worker');p.add_argument('--gpu-approved',action='store_true');a=p.parse_args()
 if a.worker:return worker(a.worker)
 assert a.gpu_approved;c.validate();assert not c.LEASE.exists(),'Preserve another finiteGPU owner';plan=c.read(H/'voice-plan.json');before=c.wait_memory(plan['resources']['sourceAsr']['minimumFreeMiB'])
 me=psutil.Process();token=str(uuid.uuid4());state=dict(project=c.P.name,revision='orientation-matrix-v8',token=token,coordinator=dict(pid=me.pid,createTime=me.create_time()),
  purpose='One finite2-complete-paragraph actualAAC m04sign-ambiguity check',state='running',startedAt=time.time(),gpuBefore=before,foreignProcessesChanged=False)
 with c.LEASE.open('x',encoding='utf8')as f:json.dump(state,f)
 child=None;code=1
 try:
  with(c.O/'final-context-worker.log').open('ab')as log:
   child=subprocess.Popen([sys.executable,'-u','-X','utf8',str(Path(__file__)),'--worker',token],cwd=c.R,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
   state['workerPid']=child.pid;c.save(c.O/'final-context-execution.json',state);code=child.wait()
  assert code==0,'Preserve actualAAC clip/cache and inspect actual context failure'
 finally:
  live=child is not None and child.poll()is None;state.update(state='complete'if code==0 else'owned-worker-still-running'if live else'failed',returnCode=code,endedAt=time.time());c.save(c.O/'final-context-execution.json',state)
  if c.LEASE.exists()and c.read(c.LEASE).get('token')==token:
   if live:c.save(c.LEASE,state)
   else:c.LEASE.unlink()
if __name__=='__main__':main()
