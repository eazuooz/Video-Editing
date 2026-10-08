"""Independent CPU readback of ambiguous isolated lines; preserve whole-scene evidence."""
from pathlib import Path
import hashlib,json
import torch
from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
R=Path(__file__).resolve().parents[3]
torch.set_num_threads(2)
model_id=str(R/'qwen3-tts/models/whisper-large-v3-turbo')
model=AutoModelForSpeechSeq2Seq.from_pretrained(model_id,dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager').to('cpu')
p=AutoProcessor.from_pretrained(model_id)
transcriber=pipeline('automatic-speech-recognition',model=model,tokenizer=p.tokenizer,feature_extractor=p.feature_extractor,dtype=torch.float32,device='cpu')
work=R/'shared/output/game-math-mesh-uv/line-repair-13'
provenance=json.loads((work/'provenance.json').read_text(encoding='utf8'))
records=[]
for index in [4,7]:
 line=next(x for x in provenance['lines'] if x['line']==index)
 wav=R/line['source'];digest=hashlib.sha256(wav.read_bytes()).hexdigest()
 assert digest==line['sha256']
 raw=transcriber(str(wav),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
 record={'line':index,'audioSha256':digest,'expected':line['text'],'recognized':raw['text'],'words':raw['chunks'],'meaningReview':'pending','humanListening':'pending'}
 records.append(record)
 print(json.dumps({k:record[k] for k in ['line','expected','recognized']},ensure_ascii=False),flush=True)
(work/'isolated-lines-cpu-asr.json').write_text(json.dumps({'model':model_id,'device':'cpu','lines':records},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
