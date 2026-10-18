"""One bounded complete ending context to resolve the ASR-only subtitle credit."""
from pathlib import Path
import json,hashlib,wave,os
R=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parents[1];O=P/'production/local'
src=O/'encoded-audio-16k.wav';out=O/'ending-context-asr.json';a,b=22.2,30.2
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
sig=dict(audioSha256=sha(src),range=[a,b])
if out.exists():
 assert json.loads(out.read_text(encoding='utf8'))['inputs']==sig;print('Bounded context cache reused');raise SystemExit(0)
clip=O/'ending-context.wav'
if not clip.exists():
 with wave.open(str(src),'rb') as f:
  params=f.getparams();f.setpos(round(a*params.framerate));pcm=f.readframes(round((b-a)*params.framerate))
 with wave.open(str(clip),'wb') as f:f.setparams(params);f.writeframes(pcm)
F=Path('C:/Users/1/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0-full_build/bin');os.environ['PATH']=str(F)+os.pathsep+os.environ.get('PATH','')
import torch
from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
torch.set_num_threads(4);mid='openai/whisper-large-v3-turbo'
m=AutoModelForSpeechSeq2Seq.from_pretrained(mid,dtype=torch.float32,attn_implementation='eager',local_files_only=True).to('cpu');p=AutoProcessor.from_pretrained(mid,local_files_only=True)
engine=pipeline('automatic-speech-recognition',model=m,tokenizer=p.tokenizer,feature_extractor=p.feature_extractor,dtype=torch.float32,device='cpu')
d=engine(str(clip),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
out.write_text(json.dumps(dict(inputs=sig,text=d['text'],words=d['chunks'],prompt=None,scope='Only ending two complete sentences; not another whole-output ASR',humanListening='pending'),ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(d['text'])
