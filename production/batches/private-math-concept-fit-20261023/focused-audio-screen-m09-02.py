"""Resolve a chunked-ASR duplication and screen two adopted source intervals."""
from common import *
import importlib.util,psutil
authorized('M08');authorized('M09')
O=R/'shared/output/private-math-concept-fit-20261023/audio-screen-m08-m09';O.mkdir(exist_ok=True)
items=[dict(id='m09-02-last-three-paragraphs',source='projects/game-math-lines-circles-v2/production/local/concept-fit-v2/audio/scenes/02-scene.wav',start=16.78,end=37.3,language='korean')]
for x in items:
 x['sha256']=sha(R/x['source']);x['wav']=O/(x['id']+'.wav')
 if not x['wav'].exists():run(['ffmpeg','-v','error','-ss',x['start'],'-t',x['end']-x['start'],'-i',R/x['source'],'-vn','-ar','16000','-ac','1',x['wav']])
lease=R/'shared/output/GPU_HANDOFF.json';assert not lease.exists();me=psutil.Process()
gpu=list(map(int,subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,memory.total,utilization.gpu','--format=csv,noheader,nounits'],text=True).splitlines()[0].split(',')));assert gpu[0]>=5120 and gpu[2]<35
state=dict(token=uuid.uuid4().hex,project='private-math-concept-fit',state='focused-asr',coordinator=dict(pid=me.pid,createTime=me.create_time()),startedAt=now())
with lease.open('x',encoding='utf8') as f:json.dump(state,f)
try:
 import torch
 from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
 spec=importlib.util.spec_from_file_location('asr_util',R/'projects/game-math-euler-axis-angle/production/revision-v7-part1/voice-review.py');u=importlib.util.module_from_spec(spec);spec.loader.exec_module(u)
 torch.set_num_threads(2);torch.cuda.set_per_process_memory_fraction(4608*1048576/torch.cuda.get_device_properties(0).total_memory)
 local=u.model_path();model=AutoModelForSpeechSeq2Seq.from_pretrained(str(local),dtype=torch.float16,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager',local_files_only=True);u.suppress_unused_encoder_attention_retention(model);model.to('cuda:0')
 processor=AutoProcessor.from_pretrained(str(local),local_files_only=True);pipe=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float16,device='cuda:0')
 results=[]
 for x in items:
  kw={'task':'transcribe'}
  if x.get('language'):kw['language']=x['language']
  result=pipe(str(x['wav']),generate_kwargs=kw,return_timestamps=True)
  row=dict(**{k:v for k,v in x.items() if k!='wav'},audio=rel(x['wav']),result=result,actualListening=False,checkedAt=now());results.append(row)
  save(O/(x['id']+'.json'),row);print(json.dumps(row,ensure_ascii=False),flush=True)
 save(B/'focused-audio-screen-m09-02.json',dict(results=results,actualListening=False,notRightsEvidence=True))
finally:
 if lease.exists() and read(lease).get('token')==state['token']:lease.unlink()
