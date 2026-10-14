"""One short immutable PCM diagnostic;CPU2/GPU0,no expected-text prompt."""
from pathlib import Path
import argparse,datetime,hashlib,json,os
os.environ['CUDA_VISIBLE_DEVICES']='-1'
os.environ['OMP_NUM_THREADS']='2'
os.environ['MKL_NUM_THREADS']='2'
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'production/research/game-lighting-history'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def write(p,j):
 p.parent.mkdir(parents=True,exist_ok=True)
 t=p.with_name(p.name+'.tmp-'+str(os.getpid()))
 t.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');os.replace(t,p)
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--label',required=True);args=parser.parse_args()
 plan_path=BASE/'voice-diagnostic-plan-v1.json';plan=read(plan_path)
 job=next(j for j in plan['jobs'] if j['label']==args.label)
 original=read(BASE/'remaining-voice-asr-execution-v2.json')
 if len(original['completed'])!=56 or original['status']!='all56-windows-complete-awaiting-direct-review':raise RuntimeError('Original56windows are still active/incomplete;never overlap')
 audio=ROOT/plan['audio']['path'];timing=ROOT/plan['timing']['path']
 if sha(audio)!=plan['audio']['sha256'] or sha(timing)!=plan['timing']['sha256']:raise RuntimeError('Current input changed')
 for item in plan['scriptInputs']:
  if sha(ROOT/item['path'])!=item['sha256']:raise RuntimeError('Script input changed')
 folder=ROOT/'projects/game-lighting-history-04/production/local/voice-diagnostics-v1'
 out=folder/(job['label']+'.json');exe=folder/(job['label']+'.execution.json')
 if out.exists():raise RuntimeError('Existing completed diagnostic preserved')
 import psutil
 own=psutil.Process();state=dict(startedAt=now(),status='loading-CPU-model',cpuThreads=2,gpuJobs=0,job=job,audio=plan['audio'],actualIdentity=dict(pid=own.pid,createTime=own.create_time(),command=own.cmdline(),executable=own.exe(),cwd=own.cwd()),approved=False)
 write(exe,state)
 try:
  import soundfile as sf,torch,torchaudio
  from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
  torch.set_num_threads(2);torch.set_num_interop_threads(1)
  model_path=ROOT/'qwen3-tts/models/whisper-large-v3-turbo'
  model=AutoModelForSpeechSeq2Seq.from_pretrained(str(model_path),dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,local_files_only=True).to('cpu')
  processor=AutoProcessor.from_pretrained(str(model_path),local_files_only=True)
  asr=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float32,device='cpu')
  with sf.SoundFile(audio) as source:
   sr=source.samplerate;first=round(job['sourceFromSeconds']*sr);last=round(job['sourceToSeconds']*sr);source.seek(first);part=source.read(last-first,dtype='float32')
  if part.ndim!=1 or len(part)!=last-first:raise RuntimeError('PCM range mismatch')
  state.update(status='recognizing',sampleRate=sr,firstSample=first,lastSample=last);write(exe,state)
  result=asr(dict(raw=torchaudio.functional.resample(torch.from_numpy(part),sr,16000).numpy(),sampling_rate=16000),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
  if sha(audio)!=plan['audio']['sha256']:raise RuntimeError('Current input changed during recognition')
  # Useful for later direct listening; sample content stays byte-identical PCM16.
  clip=folder/(job['label']+'.wav')
  with sf.SoundFile(audio) as source:
   source.seek(first);pcm=source.read(last-first,dtype='int16')
  sf.write(clip,pcm,sr,subtype='PCM_16')
  record=dict(completedAt=now(),job=job,audio=plan['audio'],timing=plan['timing'],planSha256=sha(plan_path),sourceSampleRange=[first,last],sampleRate=sr,pcmFloat32Sha256=hashlib.sha256(part.tobytes()).hexdigest(),clip=dict(path=clip.relative_to(ROOT).as_posix(),sha256=sha(clip)),expectedTextUsedAsPrompt=False,mode='independent-short-context-no-chunking',directFullTextCompared=False,currentNarrationApproved=False,humanWholeListeningApproved=False,finalMixedAsr=False,**result)
  write(out,record);state.update(status='complete-awaiting-direct-review',endedAt=now(),exitCode=0,result=out.relative_to(ROOT).as_posix(),resultSha256=sha(out));write(exe,state)
  print('DONE '+job['label'],flush=True)
 except BaseException as error:
  state.update(status='failed-preserving-input',endedAt=now(),error=repr(error));write(exe,state);raise
if __name__=='__main__':main()
