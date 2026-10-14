"""Recognize only complete ambiguous sentence contexts, with no text prompt."""
import pathlib,json,hashlib,datetime,os,sys
R=pathlib.Path(__file__).resolve().parents[4];P=R/'projects/game-lighting-history-01'
O=P/'production/local/beginner-revision-v1';D=O/'voice-contexts'
ROWS=[('04-p1',3.34,11.14),('04-p7',5.68,14.0),('04f-p5',0,9.07),
      ('07-p6',4.05,12.18),('09-p5',0,8.4),('g01',0,9.65),
      ('g25',0,8.86),('g29',10.58,22.08),('g38',0,13.07),('g42',25.22,34.64)]
def rd(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def wr(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
 global D,ROWS
 native='--native' in sys.argv
 if native:D=O/'native-guide-contexts';ROWS=[('x29',8.3,11.12),('xsh',9.36,15.28)]
 source_dir='native-guides-asr' if native else 'voice-asr'
 assert not (D/'execution.json').exists(),'Use existing context results; do not repeat.'
 assert rd(O/source_dir/'execution.json')['status']=='complete-awaiting-direct-review'
 assert rd(P/'production/checkpoint.json')['beginnerRevision']['privateUploadAuthorized']
 assert rd(R/'shared/publishing/video-production-control.json')['mode']=='one-video-autonomous-until-private-upload'
 import torch,torchaudio,soundfile as sf,numpy as np,psutil
 from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
 torch.set_num_threads(2);torch.set_num_interop_threads(1)
 D.mkdir(parents=True,exist_ok=True)
 state=dict(status='loading',pid=os.getpid(),createTime=psutil.Process().create_time(),command=psutil.Process().cmdline(),cpuThreads=2,gpuJobs=0,startedAt=now(),completed=[],expectedTextUsedAsPrompt=False)
 wr(D/'execution.json',state)
 ck=rd(P/'production/checkpoint.json');ck.update(stage='beginner-ambiguous-contexts',activeOwnedHeavyJob={**state,'execution':(D/'execution.json').relative_to(R).as_posix()});wr(P/'production/checkpoint.json',ck)
 try:
  modelpath=R/'qwen3-tts/models/whisper-large-v3-turbo'
  model=AutoModelForSpeechSeq2Seq.from_pretrained(str(modelpath),dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,local_files_only=True).to('cpu')
  proc=AutoProcessor.from_pretrained(str(modelpath),local_files_only=True)
  asr=pipeline('automatic-speech-recognition',model=model,tokenizer=proc.tokenizer,feature_extractor=proc.feature_extractor,dtype=torch.float32,device='cpu')
  for key,a,z in ROWS:
   full=rd(O/source_dir/f'{key}.json');p=R/full['audioPath'];assert sha(p)==full['audioSha256']
   data,sr=sf.read(p,dtype='float32');start=round(a*sr);end=min(round(z*sr),len(data))
   # Real complete-sentence PCM, no synthesized or expected speech prepended.
   chunk=np.concatenate([np.zeros(round(.6*sr),dtype=np.float32),data[start:end],np.zeros(round(.3*sr),dtype=np.float32)])
   audio=torchaudio.functional.resample(torch.from_numpy(chunk),sr,16000).numpy()
   result=asr({'raw':audio,'sampling_rate':16000},generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
   wr(D/f'{key}.json',dict(key=key,sourcePath=full['audioPath'],sourceSha256=full['audioSha256'],sourceSamples=[start,end],sourceSeconds=[a,z],paddingSeconds=[.6,.3],recognizerInputPcmSha256=hashlib.sha256(chunk.tobytes()).hexdigest(),expectedTextUsedAsPrompt=False,directlyReviewed=False,**result))
   state['completed'].append(key);state['status']='running';wr(D/'execution.json',state);print('DONE',key,flush=True)
  state.update(status='complete-awaiting-direct-review',finishedAt=now(),exitCode=0);wr(D/'execution.json',state)
 except BaseException as ex:
  state.update(status='failed',error=repr(ex),finishedAt=now());wr(D/'execution.json',state);raise
 finally:
  ck=rd(P/'production/checkpoint.json')
  if (ck.get('activeOwnedHeavyJob') or {}).get('pid')==state['pid']:ck['activeOwnedHeavyJob']=None;wr(P/'production/checkpoint.json',ck)
if __name__=='__main__':main()
