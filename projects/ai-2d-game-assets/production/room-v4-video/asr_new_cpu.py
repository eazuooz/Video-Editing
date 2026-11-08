"""Independent readback of the one new paragraph, no expected-text prompt."""
from pathlib import Path
import json,hashlib,torch,sys,subprocess
from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
H=Path(__file__).resolve().parent;P=H.parents[1];L=P/'production/local/room-v4-video';Q=L/'asr';Q.mkdir(exist_ok=True)
mixed='--mixed' in sys.argv
f=L/'voice/chunks/W36-scene.wav';extra={}
if mixed:
 tm=json.loads((L/'timeline.json').read_text('utf8'));row=next(s for s in tm['scenes'] if s['id']=='W36');mix=Path('C:/Users/1/Videos/YamyamCoding/ai-2d-room-v4-video/video/final-mix.m4a');f=Q/'W36-mix.wav'
 subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-ss',str(row['start']),'-i',str(mix),'-t',str(row['duration']),'-ar','16000','-ac','1','-c:a','pcm_s16le',str(f)],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
 extra={'mixSha256':hashlib.file_digest(mix.open('rb'),'sha256').hexdigest(),'start':row['start'],'duration':row['duration']}
sha=hashlib.file_digest(f.open('rb'),'sha256').hexdigest();torch.set_num_threads(2);torch.set_num_interop_threads(1)
model=AutoModelForSpeechSeq2Seq.from_pretrained('openai/whisper-large-v3-turbo',dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager',local_files_only=True).to('cpu')
processor=AutoProcessor.from_pretrained('openai/whisper-large-v3-turbo',local_files_only=True)
recognize=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float32,device='cpu')
result=recognize(str(f),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
(Q/('W36-mix.json' if mixed else 'W36.json')).write_text(json.dumps({'id':'W36','audio_sha256':sha,'model':'openai/whisper-large-v3-turbo','device':'cpu','prompt':None,**extra,**result},ensure_ascii=False,indent=2),'utf8')
print(result['text'],flush=True)
