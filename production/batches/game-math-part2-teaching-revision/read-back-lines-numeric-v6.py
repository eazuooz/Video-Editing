"""Independent unprompted beam5 recognition of two critical current WAVs."""
from pathlib import Path
import json,hashlib,os
os.environ['CUDA_VISIBLE_DEVICES']='-1';os.environ['OMP_NUM_THREADS']='2'
import torch,soundfile as sf
from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
torch.set_num_threads(2);ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent;slug='game-math-lines-unit-retake-v6';model_path=ROOT/'qwen3-tts/models/whisper-large-v3-turbo'
model=AutoModelForSpeechSeq2Seq.from_pretrained(str(model_path),dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager').to('cpu');processor=AutoProcessor.from_pretrained(str(model_path));asr=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float32,device='cpu')
records=[];m=json.loads((ROOT/f'projects/{slug}/project.json').read_text(encoding='utf8'));script=json.loads((ROOT/f'projects/{slug}/script/narration.ko.json').read_text(encoding='utf8'))
for ident in ['12-03','19-02']:
 p=ROOT/m['tts']['outputDir']/'chunks'/f'{ident}.wav';samples,sr=sf.read(p,dtype='float32');raw=asr({'array':samples,'sampling_rate':sr},generate_kwargs={'language':'korean','task':'transcribe','num_beams':5},return_timestamps='word');scene,line=ident.split('-');expected=next(s for s in script['scenes'] if s['id']==scene)['lines'][int(line)-1]
 records.append({'line':ident,'expected':expected,'audioSha256':hashlib.sha256(p.read_bytes()).hexdigest(),'raw':raw,'meaningReviewed':False});print(ident,raw['text'],flush=True)
(B/'lines-numeric-v6-unprompted-readback.json').write_text(json.dumps({'records':records,'device':'cpu','beam':5,'audioModified':False,'suppliedTranscriptPrompt':False,'humanListeningComplete':False},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
