"""Independent unprompted beam decode of individual disputed new spoken lines."""
from pathlib import Path
import json,hashlib
import torch
from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent;torch.set_num_threads(2)
model_id=ROOT/'qwen3-tts/models/whisper-large-v3-turbo'
model=AutoModelForSpeechSeq2Seq.from_pretrained(str(model_id),dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager').to('cpu')
processor=AutoProcessor.from_pretrained(str(model_id));transcriber=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float32,device='cpu');rows=[]
P=ROOT/'projects/game-math-lines-opening-retake-v4';m=json.loads((P/'project.json').read_text(encoding='utf8'));script=json.loads((P/'script/narration.ko.json').read_text(encoding='utf8'));out=ROOT/m['tts']['outputDir']
for scene,line in [('08',2),('12',3),('19',2)]:
 wav=out/'chunks'/f'{scene}-{line:02}.wav';expected=next(s for s in script['scenes'] if s['id']==scene)['lines'][line-1]
 raw=transcriber(str(wav),generate_kwargs={'language':'korean','task':'transcribe','num_beams':5},return_timestamps='word')
 row={'scene':scene,'line':line,'audioSha256':hashlib.sha256(wav.read_bytes()).hexdigest(),'expected':expected,'unpromptedBeam5':raw,'humanListeningComplete':False};rows.append(row);print(json.dumps(row,ensure_ascii=False),flush=True)
 (B/'lines-critical-numeral-readback.json').write_text(json.dumps({'rows':rows,'recognizer':'same local official Whisper model, independent line context and5 beams, no text prompt','semanticApproval':False,'humanListeningComplete':False},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
