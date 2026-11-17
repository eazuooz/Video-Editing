"""CPU-only rough transcription for our historical Shorts; editorial review still required."""
import json, os, subprocess, sys
from pathlib import Path

ROOT=Path('D:/Github/VideoEditing'); HERE=Path(__file__).resolve().parent
DEPS=HERE/'evidence/python-deps';sys.path.insert(0,str(DEPS))
os.environ['CUDA_VISIBLE_DEVICES']=''
os.environ['HF_HUB_OFFLINE']='1'
os.environ['TOKENIZERS_PARALLELISM']='false'

def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

def main():
    import numpy as np
    import torch
    from transformers import WhisperForConditionalGeneration, WhisperProcessor
    torch.set_num_threads(2);torch.set_num_interop_threads(1)
    model_id='openai/whisper-large-v3-turbo'
    model=WhisperForConditionalGeneration.from_pretrained(model_id,local_files_only=True,dtype=torch.float32).to('cpu').eval()
    processor=WhisperProcessor.from_pretrained(model_id,local_files_only=True)
    rows=json.loads((HERE/'sources.json').read_text(encoding='utf8'))['rows']
    rows=[r for r in rows if (r['status']=='original-video-transcript-needed' and r.get('videoId')) or r['id']=='D04']
    folder=HERE/'evidence/legacy-audio';folder.mkdir(exist_ok=True)
    progress=[]
    for row in rows:
        ident=row['id'];record=folder/(ident+'.json')
        if record.exists():progress.append(json.loads(record.read_text(encoding='utf8')));continue
        template=str(folder/ident)+'.%(ext)s'
        existing=[p for p in folder.glob(ident+'.*') if p.suffix in ['.m4a','.webm','.mp3','.opus']]
        if not existing:
            result=subprocess.run(['yt-dlp','--quiet','--no-progress','--no-warnings','--no-playlist','--retries','1',
                '-f','bestaudio','-o',template,'https://www.youtube.com/watch?v='+row['videoId']],cwd=ROOT,capture_output=True)
            existing=[p for p in folder.glob(ident+'.*') if p.suffix in ['.m4a','.webm','.mp3','.opus']]
        if not existing:
            d=dict(id=ident,status='audio-unavailable',videoId=row['videoId'])
            write(record,d);progress.append(d);continue
        raw=subprocess.check_output(['ffmpeg','-hide_banner','-loglevel','error','-i',str(existing[0]),'-f','f32le','-ar','16000','-ac','1','pipe:1'])
        samples=np.frombuffer(raw,dtype=np.float32).copy()
        chunks=[]
        if len(samples) and float(np.sqrt(np.mean(samples*samples)))>.0005:
            for start in range(0,len(samples),29*16000):
                audio=samples[start:start+29*16000]
                inputs=processor(audio,sampling_rate=16000,return_tensors='pt',return_attention_mask=True)
                with torch.inference_mode():
                    ids=model.generate(**inputs,task='transcribe',max_new_tokens=440,num_beams=1)
                chunks.append(dict(seconds=start/16000,text=processor.batch_decode(ids,skip_special_tokens=True)[0].strip()))
        d=dict(id=ident,status='rough-asr-pending-editorial-and-image-review',videoId=row['videoId'],
            seconds=len(samples)/16000,model=model_id,device='cpu',threads=2,chunks=chunks,
            caution='Machine transcription is not a verified transcript or proof of claims; compare the original screenshots/audio and sources.')
        write(record,d);progress.append(d)
        write(HERE/'legacy-audio-progress.json',dict(total=len(rows),completed=len(progress),rows=progress))
        print(ident,d['status'],flush=True)

if __name__=='__main__':main()
