"""CPU-only, unprompted sentence readbacks for two targeted retake ambiguities."""
from pathlib import Path
import os, json, hashlib, subprocess, time
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['TRANSFORMERS_OFFLINE'] = '1'
os.environ['OMP_NUM_THREADS'] = '2'
os.environ['MKL_NUM_THREADS'] = '2'
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
H = Path(__file__).resolve().parent
L = H / 'local'
Q = L / 'retake-context'
Q.mkdir(exist_ok=True)
torch.set_num_threads(2)
torch.set_num_interop_threads(1)
sha = lambda p: hashlib.file_digest(p.open('rb'), 'sha256').hexdigest()
model_id = 'openai/whisper-large-v3-turbo'
model = AutoModelForSpeechSeq2Seq.from_pretrained(model_id, dtype=torch.float32, low_cpu_mem_usage=True, use_safetensors=True, attn_implementation='sdpa', local_files_only=True).to('cpu')
processor = AutoProcessor.from_pretrained(model_id, local_files_only=True)
recognize = pipeline('automatic-speech-recognition', model=model, tokenizer=processor.tokenizer, feature_extractor=processor.feature_extractor, dtype=torch.float32, device='cpu')
for id, start, end in [('A08',21.74,29.45), ('A11',24.36,30.1)]:
    source = L / 'voice/chunks' / (id + '-scene.wav')
    clip = Q / (id + '.wav')
    subprocess.run(['ffmpeg','-nostdin','-v','error','-y','-ss',str(start),'-i',str(source),'-t',str(end-start),'-ar','16000','-ac','1',str(clip)],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
    began = time.time()
    result = recognize(str(clip), generate_kwargs={'language':'korean','task':'transcribe','max_new_tokens':192}, return_timestamps=True, batch_size=1)
    report = {'id':id,'sourceSha256':sha(source),'source':str(source),'clip':str(clip),'clipSha256':sha(clip),'sourceRange':[start,end],'device':'cpu','threads':2,'contentPromptProvided':False,'text':result['text'],'chunks':result.get('chunks',[]),'elapsedSeconds':time.time()-began,'humanListeningPerformed':False}
    (Q / (id+'.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
    print(id,result['text'],flush=True)
