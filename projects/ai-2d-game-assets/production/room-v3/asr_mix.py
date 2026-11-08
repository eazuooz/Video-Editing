"""One independent full current AAC-mix readback, complete paragraphs, no prompt."""
from pathlib import Path
import json,hashlib,subprocess,gc,torch
from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
H=Path(__file__).resolve().parent;P=H.parents[1];L=P/'production/local/room-v3';O=Path('C:/Users/1/Videos/YamyamCoding/ai-2d-room-v3/video');Q=L/'asr-mix';Q.mkdir(exist_ok=True)
source=O/'final-mix.m4a';digest=hashlib.file_digest(source.open('rb'),'sha256').hexdigest();rows=json.loads((L/'timeline.json').read_text('utf8'))['scenes'];recognize=None;torch.set_num_threads(2)
for row in rows:
 out=Q/(row['id']+'.json');f=Q/(row['id']+'.wav')
 if out.exists() and json.loads(out.read_text('utf8'))['mix_sha256']==digest:continue
 subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-ss',str(row['start']),'-i',str(source),'-t',str(row['sourceDuration']),'-ar','16000','-ac','1','-c:a','pcm_s16le',str(f)],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
 if recognize is None:
  model=AutoModelForSpeechSeq2Seq.from_pretrained('openai/whisper-large-v3-turbo',dtype=torch.float16,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager',local_files_only=True).to('cuda:0');processor=AutoProcessor.from_pretrained('openai/whisper-large-v3-turbo',local_files_only=True)
  recognize=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float16,device='cuda:0')
 result=recognize(str(f),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
 out.write_text(json.dumps({'id':row['id'],'mix_sha256':digest,'audio_sha256':hashlib.file_digest(f.open('rb'),'sha256').hexdigest(),'sourceInterval':[row['start'],row['speechEnd']],'model':'openai/whisper-large-v3-turbo','prompt':None,**result},ensure_ascii=False,indent=2),'utf8')
 print(row['id'],result['text'],flush=True);del result;gc.collect();torch.cuda.empty_cache()
(H/'mix-asr-execution.json').write_text(json.dumps({'currentEncodedMix':str(source),'sha256':digest,'wholeNarratedContent':True,'completeParagraphs':len(rows),'prompt':None,'humanListening':False,'textReview':'pending'},indent=2),'utf8')
