"""Transcribe only added takes without an expected-text prompt; never correct the recorded raw result."""
from pathlib import Path
import os,sys,time,json,hashlib,subprocess
import numpy as np,torch
from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor
here=Path(__file__).resolve().parent;root=here.parents[3]
media=Path(json.loads((here.parent/'batch.json').read_text(encoding='utf8'))['mediaRoot'])
folder=media/'feedback-nov05'/'speech-check';folder.mkdir(exist_ok=True)
modelid=str(root/'qwen3-tts/models/whisper-large-v3-turbo') if (root/'qwen3-tts/models/whisper-large-v3-turbo/config.json').exists() else 'openai/whisper-large-v3-turbo'
torch.set_num_threads(3);model=AutoModelForSpeechSeq2Seq.from_pretrained(modelid,local_files_only=True,dtype=torch.float32).eval()
proc=AutoProcessor.from_pretrained(modelid,local_files_only=True)
for n in (1,2,6,8):
    for j in (1,2):
        raw=root/f'shared/output/tech-ten-feedback-nov05/extra-speech/chunks/{n:02}-{j:02}.wav'
        gpu=root/f'shared/output/tech-ten-feedback-nov05/gpu/chunks/{n:02}-{j:02}-scene.wav'
        while not(raw.exists() or gpu.exists()):time.sleep(4)
        # Write finished only after explicit GPU render release; takes with retry may still change.
        path=gpu if gpu.exists() else raw;time.sleep(1);digest=hashlib.sha256(path.read_bytes()).hexdigest()
        report=folder/f'{n:02}-{j:02}-{digest[:12]}.json'
        if report.exists():continue
        pcm=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-ar','16000','-ac','1','-f','f32le','-']),dtype=np.float32)
        x=proc(pcm,sampling_rate=16000,return_tensors='pt').input_features
        with torch.inference_mode():ids=model.generate(x,language='korean',task='transcribe',max_new_tokens=144)
        st=proc.batch_decode(ids,skip_special_tokens=True)[0]
        print(path.name,st,flush=True);report.write_text(json.dumps(dict(source=str(path),sha256=digest,model=modelid,device='cpu',rawRecognition=st,seconds=len(pcm)/16000,expectedTextPromptUsed=False),ensure_ascii=False,indent=2),encoding='utf8')
