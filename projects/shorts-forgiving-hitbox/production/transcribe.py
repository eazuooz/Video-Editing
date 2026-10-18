"""One cached complete ASR per current voice or encoded mix; no expected-text prompt."""
import os
os.environ['HF_HUB_OFFLINE']='1'
os.environ['TRANSFORMERS_OFFLINE']='1'
from pathlib import Path
import os,sys,json,hashlib,subprocess,re,difflib,time
R=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parents[1];L=P/'production/local'
role=sys.argv[1];assert role in ['voice','mix']
source=(L/'narration-timeline.wav' if (L/'narration-timeline.wav').exists() else R/'shared/output/narration/shorts-forgiving-hitbox/hitbox-v2/hitbox-v2.wav') if role=='voice' else L/'final-mix.m4a'
sha=hashlib.sha256(source.read_bytes()).hexdigest();out=L/f'asr-{role}-{sha[:12]}.json'
if out.exists():print(str(out));raise SystemExit(0)
ff=Path('C:/Users/1/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0-full_build/bin/ffmpeg.exe')
os.environ['PATH']=str(ff.parent)+os.pathsep+os.environ.get('PATH','')
wav=L/f'asr-{role}-{sha[:12]}-16k.wav'
if not wav.exists():subprocess.run([str(ff),'-v','error','-n','-i',str(source),'-ac','1','-ar','16000',str(wav)],check=True)
import torch
from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
torch.set_num_threads(3)
dedicated=R/'qwen3-tts/models/whisper-large-v3-turbo';modelId=str(dedicated) if (dedicated/'config.json').exists() else 'openai/whisper-large-v3-turbo'
model=AutoModelForSpeechSeq2Seq.from_pretrained(modelId,dtype=torch.float32,attn_implementation='eager',local_files_only=True).to('cpu');processor=AutoProcessor.from_pretrained(modelId,local_files_only=True)
asr=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float32,device='cpu')
print('Transcribing complete '+role,flush=True)
recognized=asr(str(wav),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
expected=(P/'script/narration.ko.txt').read_text(encoding='utf8').strip();norm=lambda s:re.sub(r'[^0-9a-z가-힣]','',s.lower())
report=dict(role=role,input=str(source.relative_to(R)),sha256=sha,fullInput=True,device='cpu',text=recognized['text'],chunks=recognized.get('chunks',[]),expected=expected,normalizedMatch=norm(expected)==norm(recognized['text']),similarity=difflib.SequenceMatcher(None,norm(expected),norm(recognized['text'])).ratio(),humanListening='pending')
out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'output':str(out),'text':report['text'],'similarity':report['similarity']},ensure_ascii=False))
