"""One hash-cached independent full encoded-mix ASR on CPU; no new TTS."""
from pathlib import Path
import os,json,hashlib,subprocess,difflib
R=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parents[1];O=P/'production/local';F=Path('C:/Users/1/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0-full_build/bin')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
control=json.loads((R/'shared/publishing/video-production-control.json').read_text(encoding='utf8'));assert control['shortsRecurringAuthorization']['selectedShort']==P.name
video=O/(P.name+'.captioned.mp4');sig=sha(video);out=O/'final-mix-asr.json'
if out.exists():
 d=json.loads(out.read_text(encoding='utf8'));assert d['captionedSha256']==sig,'Preserve previous review and use a distinct revision for changed output.';print('Reusing current complete encoded ASR');raise SystemExit(0)
wav=O/'encoded-audio-16k.wav'
if not wav.exists():subprocess.run([str(F/'ffmpeg.exe'),'-v','error','-n','-i',str(video),'-vn','-ac','1','-ar','16000','-c:a','pcm_s16le',str(wav)],check=True)
import wave
with wave.open(str(wav),'rb') as wf:assert wf.getframerate()==16000 and wf.getnchannels()==1 and abs(wf.getnframes()/16000-30.2)<.08
os.environ['PATH']=str(F)+os.pathsep+os.environ.get('PATH','')
import torch
from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
torch.set_num_threads(4);modelpath=R/'qwen3-tts/models/whisper-large-v3-turbo'
model_id=str(modelpath) if (modelpath/'config.json').exists() else 'openai/whisper-large-v3-turbo'
m=AutoModelForSpeechSeq2Seq.from_pretrained(model_id,dtype=torch.float32,attn_implementation='eager',local_files_only=True).to('cpu')
p=AutoProcessor.from_pretrained(model_id,local_files_only=True)
asr=pipeline('automatic-speech-recognition',model=m,tokenizer=p.tokenizer,feature_extractor=p.feature_extractor,dtype=torch.float32,device='cpu')
result=asr(str(wav),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
expected=(P/'script/narration.ko.txt').read_text(encoding='utf8').strip()
d=dict(schemaVersion=1,captionedSha256=sig,encodedAudioSha256=sha(wav),scope='Entire current30.2second encoded mix with quiet music; no expected transcript prompt',device='cpu',model='whisper-large-v3-turbo',expected=expected,recognized=result['text'],words=result['chunks'],directWholeTextReview='pending',humanListening='pending-final-user-review',noTtsGenerated=True)
out.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(result['text'])
