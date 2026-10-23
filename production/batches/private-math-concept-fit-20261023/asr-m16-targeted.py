"""Resolve a chunk-boundary repetition flag using the complete suspect sentence pair, unprompted."""
from common import *
import importlib.util
P=R/'projects/game-math-camera-frustum';H=P/'production/concept-fit-v2';O=P/'production/local/concept-fit-v2/audio';authorized('M16');clip=O/'asr/05-line2-8.58-15.72.wav'
run(['ffmpeg','-v','error','-i',O/'scenes/05-scene.wav','-af','atrim=start=8.58:end=15.72,asetpts=PTS-STARTPTS','-c:a','pcm_f32le','-y',clip])
lease=R/'shared/output/GPU_HANDOFF.json';assert not lease.exists();import psutil
me=psutil.Process();state=dict(token=uuid.uuid4().hex,project=P.name,state='targeted-asr',coordinator=dict(pid=me.pid,createTime=me.create_time()),startedAt=now());free=int(subprocess.check_output(['nvidia-smi','--query-gpu=memory.free','--format=csv,noheader,nounits'],text=True).splitlines()[0]);assert free>5120
with lease.open('x',encoding='utf8') as f:json.dump(state,f)
try:
 spec=importlib.util.spec_from_file_location('asr_util',R/'projects/game-math-euler-axis-angle/production/revision-v7-part1/voice-review.py');u=importlib.util.module_from_spec(spec);spec.loader.exec_module(u)
 import torch
 from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
 torch.set_num_threads(2);torch.cuda.set_per_process_memory_fraction(4608*1048576/torch.cuda.get_device_properties(0).total_memory)
 local=u.model_path();m=AutoModelForSpeechSeq2Seq.from_pretrained(str(local),dtype=torch.float16,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager',local_files_only=True);u.suppress_unused_encoder_attention_retention(m);m.to('cuda:0');p=AutoProcessor.from_pretrained(str(local),local_files_only=True)
 transcribe=pipeline('automatic-speech-recognition',model=m,tokenizer=p.tokenizer,feature_extractor=p.feature_extractor,dtype=torch.float16,device='cuda:0');result=transcribe(str(clip),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps=True)
 save(H/'targeted-asr-boundary.json',dict(path=rel(clip),sha256=sha(clip),scene='05',range=[8.58,15.72],result=result,expectedPrompt=None,chunking=False,actualListening=False));print(result['text'],flush=True)
finally:
 if lease.exists() and read(lease).get('token')==state['token']:lease.unlink()
