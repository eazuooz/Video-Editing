from common import *
import importlib.util
P=R/'projects/game-math-mesh-uv';H=P/'production/concept-fit-v2';O=P/'production/local/concept-fit-v2/audio';authorized('M19')
spec=importlib.util.spec_from_file_location('asr_util',R/'projects/game-math-euler-axis-angle/production/revision-v7-part1/voice-review.py');u=importlib.util.module_from_spec(spec);spec.loader.exec_module(u)
import torch
from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
torch.set_num_threads(4);local=u.model_path();m=AutoModelForSpeechSeq2Seq.from_pretrained(str(local),dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager',local_files_only=True);u.suppress_unused_encoder_attention_retention(m);p=AutoProcessor.from_pretrained(str(local),local_files_only=True);transcribe=pipeline('automatic-speech-recognition',model=m,tokenizer=p.tokenizer,feature_extractor=p.feature_extractor,dtype=torch.float32,device='cpu')
rows=[]
for sid,start,end,line in [('06',18.44,26.2,'03'),('07',17,25.4,'03')]:
 clip=O/f'asr/{sid}-line{line}-targeted.wav';run(['ffmpeg','-v','error','-i',O/f'scenes/{sid}-scene.wav','-af',f'atrim=start={start}:end={end},asetpts=PTS-STARTPTS','-c:a','pcm_f32le','-y',clip]);res=transcribe(str(clip),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word');rows.append(dict(scene=sid,line=line,start=start,end=end,path=rel(clip),sha256=sha(clip),result=res));print(sid,res['text'],flush=True)
save(H/'targeted-asr-boundaries.json',dict(at=now(),reason='Resolve chunk-boundary timestamp overlap and suspected repeated syllable; only complete suspect paragraphs rechecked.',device='cpu',rows=rows,chunking=False,expectedPrompt=None,actualListening=False))
