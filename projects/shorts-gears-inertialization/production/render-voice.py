"""Finite paragraph job. Same Qwen voice; GPU talker and CPU codec preserve live editor."""
from pathlib import Path
import json,os,sys,time,uuid,subprocess,hashlib,importlib.util
import psutil
from audio_revision import P,R,L,VOICE,REVISION,read,guard
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def main():
 cpu='--cpu' in sys.argv; guard(); lease=R/'shared/output/GPU_HANDOFF.json';assert cpu or not lease.exists(),'Foreign GPU lease preserved'
 free,util=map(int,subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip().split(','));assert cpu or (free>=4800 and util<35),(free,util)
 assert not VOICE.exists(); manifest=read(P/'production/tts-manifest.json');doc=read(R/manifest['paths']['script'])
 token=uuid.uuid4().hex; me=psutil.Process(); rec={'project':P.name,'revision':REVISION,'state':'gpu_talker_cpu_codec','token':token,'coordinator':{'pid':me.pid,'createTime':me.create_time()},'startedAt':time.time(),'freeMiBBefore':free,'foreignProcessesPaused':[],'allocatorCapMiB':4352,'scriptSha256':sha(R/manifest['paths']['script']),'voiceReferenceSha256':sha(R/manifest['tts']['reference']),'takes':[]}
 L.mkdir(parents=True,exist_ok=True)
 if not cpu:
  with lease.open('x',encoding='utf8') as f:json.dump(rec,f)
 try:
  os.environ['HF_HUB_OFFLINE']='1';os.environ['TRANSFORMERS_OFFLINE']='1';os.environ['PYTORCH_CUDA_ALLOC_CONF']='expandable_segments:True'
  import torch,numpy as np,soundfile as sf
  from qwen_tts import Qwen3TTSModel
  torch.set_num_threads(3);torch.set_num_interop_threads(2)
  if not cpu:torch.cuda.set_per_process_memory_fraction(4352*1048576/torch.cuda.get_device_properties(0).total_memory)
  rec['state']='cpu-only' if cpu else 'gpu_talker_cpu_codec';rec['device']='cpu' if cpu else 'cuda:0'
  model=Qwen3TTSModel.from_pretrained(str(R/manifest['tts']['model']),device_map='cpu',dtype=torch.bfloat16)
  if not cpu:model.model.talker.to('cuda:0');model.model.speaker_encoder.to('cuda:0');model.device=torch.device('cuda:0')
  model.model.speech_tokenizer.model.to(device='cpu',dtype=torch.float32);model.model.speech_tokenizer.device=torch.device('cpu')
  prompt=model.create_voice_clone_prompt(ref_audio=str(R/manifest['tts']['reference']),ref_text=(R/manifest['tts']['referenceText']).read_text(encoding='utf8').strip(),x_vector_only_mode=False)
  out=VOICE.parent/'chunks';out.mkdir(parents=True,exist_ok=True)
  for scene in doc['scenes']:
   for i,text in enumerate(scene['lines'],1):
    guard(); path=out/f'{scene["id"]}-{i:02}.wav'
    if path.exists():
     saved=read(L/'reuse-takes.json')[path.name];assert saved['sha256']==sha(path) and saved['text']==text
     rec['takes'].append({'key':path.stem,'sha256':sha(path),'text':text,'reusedUnchanged':True});continue
    print('Generating paragraph',i,flush=True);start=time.time()
    waves,sr=model.generate_voice_clone(text=[text],language='Korean',voice_clone_prompt=prompt,non_streaming_mode=True,max_new_tokens=2048)
    samples=np.asarray(waves[0],dtype=np.float32);assert sr==24000 and np.isfinite(samples).all()
    sf.write(path,samples,sr,subtype='FLOAT');rec['takes'].append({'key':f'{scene["id"]}-{i:02}','sha256':sha(path),'seconds':len(samples)/sr,'elapsed':time.time()-start,'text':text})
    save(L/'tts-execution.partial.json',rec);print('Completed',i,len(samples)/sr,flush=True)
  spec=importlib.util.spec_from_file_location('assembly',P/'production/assemble-paragraphs.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.main()
  rec['state']='completed';rec['voiceSha256']=sha(VOICE)
 except BaseException as e:rec['state']='failed';rec['error']=str(e);raise
 finally:
  if 'torch' in locals() and torch.cuda.is_initialized():rec['peakAllocatedMiB']=torch.cuda.max_memory_allocated()/1048576;rec['peakReservedMiB']=torch.cuda.max_memory_reserved()/1048576
  rec['finishedAt']=time.time();save(L/'tts-execution.json',rec)
  if lease.exists() and read(lease).get('token')==token:lease.unlink()
if __name__=='__main__':main()
