"""Additional evidence for suspect ASR readings; never edits the source voice."""
from pathlib import Path
import json,hashlib
import numpy as np,soundfile as sf,torch
from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
ROOT=Path(__file__).resolve().parents[3];WORK=Path(__file__).parent
m=json.loads((ROOT/'projects/game-writing/project.json').read_text(encoding='utf-8'))
out=ROOT/m['tts']['outputDir'];report=json.loads((out/(m['tts']['filenameStem']+'.asr-review.json')).read_text(encoding='utf-8'))
assert report['complete'],'Wait until the single full ASR worker finishes.'
model_id=str(ROOT/'qwen3-tts/models/whisper-large-v3-turbo');torch.set_num_threads(2)
model=AutoModelForSpeechSeq2Seq.from_pretrained(model_id,dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager').to('cpu')
processor=AutoProcessor.from_pretrained(model_id)
asr=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float32,device='cpu')
findings=[]
for sid,start,end in [('01',0,8),('07',0,11),('09',48,None),('10',0,9),('11',0,9)]:
    file=out/'chunks'/f'{sid}-scene.wav';data,rate=sf.read(file);end=len(data)/rate if end is None else end
    clip=data[round(start*rate):round(end*rate)];tmp=WORK/f'focused-asr-{sid}.wav';sf.write(tmp,clip,rate)
    raw=asr(str(tmp),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
    tail=data[-round(rate*.08):];entry={'scene':sid,'sourceSha256':hashlib.sha256(file.read_bytes()).hexdigest(),'in':start,'out':end,'text':raw['text'],'words':raw['chunks'],'last80msRms':float(np.sqrt(np.mean(tail**2))),'last80msPeak':float(np.max(np.abs(tail))),'kind':'Evidence for direct review; not human listening'}
    findings.append(entry);print(json.dumps({k:v for k,v in entry.items() if k!='words'},ensure_ascii=False),flush=True)
    (WORK/'focused-asr.json').write_text(json.dumps({'reviewRequired':True,'findings':findings},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
