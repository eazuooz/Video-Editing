"""Independent CPU read-back of uncertain numeric lines, without modifying audio."""
from pathlib import Path
import json,hashlib,os
os.environ['CUDA_VISIBLE_DEVICES']='-1';os.environ['OMP_NUM_THREADS']='2'
import torch,soundfile as sf
from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
torch.set_num_threads(2)
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent;model_path=ROOT/'qwen3-tts/models/whisper-large-v3-turbo'
model=AutoModelForSpeechSeq2Seq.from_pretrained(str(model_path),dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager').to('cpu')
processor=AutoProcessor.from_pretrained(str(model_path));asr=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float32,device='cpu')
records=[]
for slug,ident in [('game-math-interpolation-worked-checks-v3','02-03'),('game-math-interpolation-teaching-additions-v2','17-01')]:
    m=json.loads((ROOT/f'projects/{slug}/project.json').read_text(encoding='utf8'));path=ROOT/m['tts']['outputDir']/'chunks'/f'{ident}.wav'
    samples,rate=sf.read(path,dtype='float32');result=asr({'array':samples,'sampling_rate':rate},generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
    record={'project':slug,'line':ident,'audioSha256':hashlib.sha256(path.read_bytes()).hexdigest(),'text':result['text'],'words':result['chunks'],'device':'cpu','numericMeaningApproval':False}
    records.append(record);print(slug,ident,result['text'],flush=True)
(B/'interpolation-numerical-line-readback.json').write_text(json.dumps({'records':records,'audioModified':False,'humanListening':'pending'},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
