"""CPU-only read-back of the new bridges; word-aligned bilingual captions."""
import os,time,re,difflib,argparse,math
from prepare import *
def norm(s):return re.sub('[^가-힣a-z0-9]','',s.lower())
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--watch',action='store_true');args=ap.parse_args()
 os.environ['CUDA_VISIBLE_DEVICES']=''
 import torch,numpy as np,soundfile as sf
 from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
 torch.set_num_threads(2)
 modelpath=pathlib.Path('C:/Users/1/.cache/huggingface/hub/models--openai--whisper-large-v3-turbo/snapshots/41f01f3fe87f28c78e2fbf8b568835947dd65ed9')
 model=AutoModelForSpeechSeq2Seq.from_pretrained(str(modelpath),dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager').to('cpu').eval()
 proc=AutoProcessor.from_pretrained(str(modelpath));pipe=pipeline('automatic-speech-recognition',model=model,tokenizer=proc.tokenizer,feature_extractor=proc.feature_extractor,dtype=torch.float32,device='cpu')
 folder=HERE/'local/asr';folder.mkdir(parents=True,exist_ok=True);started=time.time()
 while True:
  plan=read(HERE/'plan.json');rows=[s for e in plan['episodes'] for s in e['inserts']];done=0
  for s in rows:
   wav=HERE/'local/voice/raw'/(s['key']+'.wav');cache=folder/(s['key']+'.json')
   if not wav.exists() or time.time()-wav.stat().st_mtime<3:continue
   digest=sha(wav)
   if not cache.exists() or read(cache).get('sha256')!=digest:
    result=pipe(str(wav),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
    if sha(wav)!=digest:continue
    save(cache,dict(key=s['key'],sha256=digest,text=result['text'],words=result['chunks'],device='cpu',humanListening=False))
    print('ASR',s['key'],result['text'],flush=True)
   done+=1
  if done==len(rows) and (HERE/'voice.json').exists():break
  if not args.watch:break
  assert time.time()-started<10800,'Finite bridge ASR timeout; preserve every checkpoint'
  time.sleep(5)
 if not (HERE/'voice.json').exists():return
 result={};voices={v['key']:v for v in read(HERE/'voice.json')['items']}
 font=ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf',43)
 def wrap(t,width=1500):
  lines=[];row=''
  for word in t.split():
   v=(row+' '+word).strip()
   if row and font.getlength(v)>width:lines.append(row);row=word
   else:row=v
  if row:lines.append(row)
  return '\n'.join(lines)
 for s in rows:
  rec=read(folder/(s['key']+'.json'));wav=HERE/'local/voice/raw'/(s['key']+'.wav');assert sha(wav)==rec['sha256']
  data,sr=sf.read(wav,dtype='float32');n=max(1,int(sr*.02));rms=np.sqrt(np.array([np.mean(data[i:i+n]**2) for i in range(0,len(data),n)]));active=np.flatnonzero(rms>max(.0005,float(rms.max())*.025));trim=max(0,int(active[0]*n-.10*sr))/sr;offset=.12-trim
  expected=norm(' '.join(s['ko']));recognized='';times=[]
  for w in rec['words']:
   t=norm(w['text']);a,z=w['timestamp']
   if a is None:a=0
   if z is None:z=voices[s['key']]['seconds']-offset
   for k,ch in enumerate(t):recognized+=ch;times.append((float(a)+(float(z)-float(a))*k/max(1,len(t)),float(a)+(float(z)-float(a))*(k+1)/max(1,len(t))))
  matcher=difflib.SequenceMatcher(None,expected,recognized,autojunk=False);mapping={}
  for tag,a,z,b,y in matcher.get_opcodes():
   if a==z:continue
   for k in range(a,z):mapping[k]=min(max(0,len(times)-1),b+int((k-a)*max(1,y-b)/max(1,z-a)))
  cues=[];cursor=0;prev=0
  for ko,en in zip(s['ko'],s['en']):
   length=len(norm(ko));start=max(prev,times[mapping[cursor]][0]+offset);end=max(start+.4,times[mapping[cursor+length-1]][1]+offset);end=min(end,voices[s['key']]['seconds']-.1);cues.append(dict(start=max(.12,start),end=end,ko=wrap(ko),en=wrap(en)));prev=end;cursor+=length
  ratio=matcher.ratio();result[s['key']]=dict(sourceText=' '.join(s['ko']),recognizedText=rec['text'],similarity=ratio,rawAudioSha256=rec['sha256'],voiceSha256=voices[s['key']]['sha256'],cues=cues,humanListening=False,requiresTextReview=ratio<.93)
 save(HERE/'alignment.json',dict(items=result,allOriginalLectureSubtitlesPreservedWithShift=True,status='requires-ASR-text-and-join-review'))
 print('Word-aligned',len(result),'new bilingual bridges',flush=True)
if __name__=='__main__':main()
