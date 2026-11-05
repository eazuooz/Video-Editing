from pathlib import Path
import os,json,subprocess,io,hashlib
os.environ['HF_HUB_OFFLINE']='1';os.environ['TRANSFORMERS_OFFLINE']='1'
R=Path(__file__).resolve().parents[3];P=R/'projects/unreal-engine-6-verse-gameplay';L=P/'research/local'
def main():
 import torch,soundfile as sf
 from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
 audio=L/'reference16.wav'
 if not audio.exists():subprocess.run(['ffmpeg','-v','error','-i',str(L/'reference.mp4'),'-vn','-ac','1','-ar','16000',str(audio)],check=True)
 target=L/'reference-asr.json'
 if target.exists():return
 torch.set_num_threads(4);model=R/'qwen3-tts/models/whisper-large-v3-turbo'
 if not (model/'config.json').exists():
  from huggingface_hub import try_to_load_from_cache
  model=Path(try_to_load_from_cache('openai/whisper-large-v3-turbo','config.json')).parent
 m=AutoModelForSpeechSeq2Seq.from_pretrained(str(model),dtype=torch.float32,attn_implementation='sdpa',local_files_only=True)
 p=AutoProcessor.from_pretrained(str(model),local_files_only=True)
 pipe=pipeline('automatic-speech-recognition',model=m,tokenizer=p.tokenizer,feature_extractor=p.feature_extractor,device=-1)
 y,sr=sf.read(audio,dtype='float32')
 result=pipe({'array':y,'sampling_rate':sr},chunk_length_s=30,stride_length_s=5,generate_kwargs={'language':'english','task':'transcribe','num_beams':1},return_timestamps=True)
 target.write_text(json.dumps({'source':'i0wZCIhqveQ','classification':'research-reference-only','unprompted':True,'result':result},ensure_ascii=False,indent=2),encoding='utf-8')
 (L/'reference-transcript.txt').write_text('\n'.join(f"{c['timestamp']}: {c['text']}" for c in result['chunks']),encoding='utf-8');print('Complete source narration recognized',flush=True)
if __name__=='__main__':main()
