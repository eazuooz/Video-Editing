"""Independent unprompted recognition of ambiguous raw takes; preserve full ASR."""
from pathlib import Path
import sys,os,json,hashlib,subprocess
R=Path(__file__).resolve().parents[3];slug=sys.argv[1];p=R/'projects'/slug;L=p/('production/local/audio-v2' if (p/'production/local/audio-v2/voice/narration.wav').exists() else 'production/local/audio-v1')
os.environ['HF_HUB_OFFLINE']='1';os.environ['TRANSFORMERS_OFFLINE']='1'
import torch
from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
torch.set_num_threads(3);torch.set_num_interop_threads(1)
modelid='openai/whisper-large-v3-turbo';m=AutoModelForSpeechSeq2Seq.from_pretrained(modelid,dtype=torch.float32,attn_implementation='eager',local_files_only=True).to('cpu');pr=AutoProcessor.from_pretrained(modelid,local_files_only=True)
recognize=pipeline('automatic-speech-recognition',model=m,tokenizer=pr.tokenizer,feature_extractor=pr.feature_extractor,dtype=torch.float32,device='cpu')
for n in sys.argv[2:]:
 source=L/f'voice/chunks/main-{int(n):02}.wav';out=L/f'take-{n}-independent-asr.json';assert not out.exists()
 wav=L/f'take-{n}-16k.wav';subprocess.run(['ffmpeg','-v','error','-n','-i',str(source),'-ar','16000','-ac','1',str(wav)],check=True)
 result=recognize(str(wav),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
 result.update(source=str(source.relative_to(R)),sourceSHA256=hashlib.sha256(source.read_bytes()).hexdigest(),expectedPromptUsed=False,humanListening='pending');out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(n,result['text'],flush=True)
