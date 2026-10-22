"""Screen the adopted official source interval for speech; not a listening signoff."""
from common import *
import importlib.util,psutil
authorized('M07');O=R/'shared/output/private-math-concept-fit-20261023/sources/escape-simulator-official';src=O/'ES_LevelEditor_v3.mp4';dst=O/'doors-7-15.5.wav';receipt=O/'doors-audio-screen.json'
if receipt.exists():
 assert read(receipt)['sourceSha256']==sha(src);print('Existing source screen reused');raise SystemExit
run(['ffmpeg','-v','error','-ss','7','-t','8.5','-i',src,'-vn','-ar','16000','-ac','1',dst])
lease=R/'shared/output/GPU_HANDOFF.json';assert not lease.exists();me=psutil.Process()
gpu=list(map(int,subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,memory.total,utilization.gpu','--format=csv,noheader,nounits'],text=True).splitlines()[0].split(',')));assert gpu[0]>=5120 and gpu[2]<35
state=dict(token=uuid.uuid4().hex,project='game-math-interpolation-paths-v2',state='source-speech-screen',coordinator=dict(pid=me.pid,createTime=me.create_time()),startedAt=now())
with lease.open('x',encoding='utf8') as f:json.dump(state,f)
try:
 import torch
 from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
 spec=importlib.util.spec_from_file_location('asr_util',R/'projects/game-math-euler-axis-angle/production/revision-v7-part1/voice-review.py');u=importlib.util.module_from_spec(spec);spec.loader.exec_module(u)
 torch.set_num_threads(2);torch.cuda.set_per_process_memory_fraction(4608*1048576/torch.cuda.get_device_properties(0).total_memory)
 local=u.model_path();model=AutoModelForSpeechSeq2Seq.from_pretrained(str(local),dtype=torch.float16,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager',local_files_only=True);u.suppress_unused_encoder_attention_retention(model);model.to('cuda:0')
 processor=AutoProcessor.from_pretrained(str(local),local_files_only=True);pipe=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float16,device='cuda:0')
 result=pipe(str(dst),generate_kwargs={'task':'transcribe'},return_timestamps=True)
 save(receipt,dict(sourceSha256=sha(src),source=rel(src),start=7,end=15.5,result=result,actualListening=False,checkedAt=now(),note='Automatic speech screening only; source track remains synchronized and must not be described as isolated game FX.'))
 print(json.dumps(result,ensure_ascii=False))
finally:
 if lease.exists() and read(lease).get('token')==state['token']:lease.unlink()
