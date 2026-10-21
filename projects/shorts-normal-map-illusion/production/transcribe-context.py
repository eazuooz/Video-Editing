"""One targeted pass over three complete sentences flagged by the full ASR.

No expected-text prompt, no whole-file repeat, no PCM or display-text mutation.
"""
from pathlib import Path
import hashlib,json,os,subprocess,time

R=Path(__file__).resolve().parents[3]
P=Path(__file__).resolve().parents[1]
L=P/'production/local'
V=L/'voice/normal-map-v1.wav'
O=L/'asr-context-particles-colour.json'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
 c=json.loads((R/'shared/publishing/video-production-control.json').read_text(encoding='utf8'))
 assert c.get('selectedShortVideo')==P.name and c['shortsDirectSelection']['selectedRevision']=='normal-map-v1'
 assert not O.exists(),'Reuse the existing one-time targeted context evidence.'
 whole=L/f'asr-voice-{sha(V)[:12]}.json'
 assert whole.exists(),'Inspect the full current source ASR first.'
 ranges=[
  {'id':'flat-lighting','range':[2.80,7.25],'reason':'Full ASR 계산의 versus supplied 계산에.'},
  {'id':'rgb-map','range':[13.85,18.75],'reason':'Full ASR 파란 versus supplied 파랑.'},
  {'id':'neutral-normal','range':[18.75,23.20],'reason':'Full ASR 재질이/표면의 versus supplied 재질의/표면에.'},
 ]
 b=Path('C:/Users/1/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0-full_build/bin')
 os.environ['PATH']=str(b)+os.pathsep+os.environ['PATH']
 for key in ['HF_HUB_OFFLINE','TRANSFORMERS_OFFLINE']:os.environ[key]='1'
 for key in ['OMP_NUM_THREADS','MKL_NUM_THREADS']:os.environ[key]='3'
 import torch
 from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
 torch.set_num_threads(3);torch.set_num_interop_threads(1)
 d=R/'qwen3-tts/models/whisper-large-v3-turbo'
 model_id=str(d) if (d/'config.json').exists() else 'openai/whisper-large-v3-turbo'
 started=time.monotonic()
 model=AutoModelForSpeechSeq2Seq.from_pretrained(model_id,dtype=torch.float32,attn_implementation='eager',local_files_only=True).to('cpu')
 processor=AutoProcessor.from_pretrained(model_id,local_files_only=True)
 recognize=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float32,device='cpu')
 results=[]
 for item in ranges:
  clip=L/f"asr-context-{item['id']}.wav"
  start,end=item['range']
  if not clip.exists():subprocess.run([str(b/'ffmpeg.exe'),'-v','error','-n','-ss',str(start),'-i',str(V),'-t',str(end-start),'-ar','16000','-ac','1','-c:a','pcm_s16le',str(clip)],check=True)
  result=recognize(str(clip),generate_kwargs={'language':'korean','task':'transcribe','num_beams':3},return_timestamps='word')
  row={**item,'clip':str(clip.relative_to(R)).replace('\\','/'),'clipSha256':sha(clip),'text':result['text'],'chunks':result['chunks']}
  results.append(row);print(json.dumps({'id':item['id'],'text':result['text']},ensure_ascii=False),flush=True)
 report={'voiceSha256':sha(V),'wholeAsrSha256':sha(whole),'expectedTextPromptUsed':False,'fullAsrRepeated':False,'rawRecognitionUnmodified':True,'device':'cpu','cpuThreads':3,'decoding':'beam3 versus original greedy','contexts':results,'elapsedSeconds':round(time.monotonic()-started,3),'humanListening':'pending'}
 with O.open('x',encoding='utf8') as f:f.write(json.dumps(report,ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':main()
