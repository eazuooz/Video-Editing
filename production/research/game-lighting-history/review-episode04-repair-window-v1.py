"""One frozen repaired PCM window, CPU2/GPU0, no expected-text prompt or approval."""
from pathlib import Path
import argparse,datetime,hashlib,json,os
os.environ['CUDA_VISIBLE_DEVICES']='-1'
os.environ['OMP_NUM_THREADS']='2'
os.environ['MKL_NUM_THREADS']='2'
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'projects/game-lighting-history-04/production'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def write(p,j):
 p.parent.mkdir(parents=True,exist_ok=True);temp=p.with_name(p.name+'.tmp-'+str(os.getpid()));temp.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');os.replace(temp,p)
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--label',required=True);args=parser.parse_args()
 plan_path=BASE/'voice-repair-asr-plan-v1.json';plan=read(plan_path);job=next(j for j in plan['jobs'] if j['label']==args.label)
 for i in [plan['audio'],plan['timing'],*plan['inputHashes'],*plan['chunkInputs'],*plan['originalInputHashes']]:
  if sha(ROOT/i['path'])!=i['sha256']:raise RuntimeError('Frozen input changed:'+i['path'])
 folder=BASE/'local/voice-repair-asr-v1';output=folder/(job['label']+'.json');execution=folder/(job['label']+'.execution.json')
 if output.exists():raise RuntimeError('Existing completed recognition preserved')
 import psutil
 own=psutil.Process();state=dict(startedAt=now(),status='loading-CPU-model',actualIdentity=dict(pid=own.pid,createTime=own.create_time(),command=own.cmdline(),cwd=own.cwd(),exe=own.exe()),cpuThreads=2,gpuJobs=0,job=job,audio=plan['audio'],currentNarrationApproved=False)
 write(execution,state)
 try:
  import soundfile as sf,torch,torchaudio
  from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
  torch.set_num_threads(2);torch.set_num_interop_threads(1)
  model_path=ROOT/'qwen3-tts/models/whisper-large-v3-turbo'
  model=AutoModelForSpeechSeq2Seq.from_pretrained(str(model_path),dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,local_files_only=True).to('cpu');processor=AutoProcessor.from_pretrained(str(model_path),local_files_only=True)
  asr=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float32,device='cpu')
  with sf.SoundFile(ROOT/plan['audio']['path']) as source:
   sr=source.samplerate;first=round(job['sourceFromSeconds']*sr);last=round(job['sourceToSeconds']*sr);source.seek(first);part=source.read(last-first,dtype='float32')
  if part.ndim!=1 or len(part)!=last-first:raise RuntimeError('PCM range mismatch')
  state.update(status='recognizing',sourceSampleRange=[first,last],sampleRate=sr);write(execution,state)
  opts=dict(generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
  if job['mode']=='whole':opts.update(chunk_length_s=30,stride_length_s=5)
  result=asr(dict(raw=torchaudio.functional.resample(torch.from_numpy(part),sr,16000).numpy(),sampling_rate=16000),**opts)
  if sha(ROOT/plan['audio']['path'])!=plan['audio']['sha256']:raise RuntimeError('Current PCM changed during recognition')
  record=dict(completedAt=now(),job=job,audio=plan['audio'],timing=plan['timing'],planSha256=sha(plan_path),sourceSampleRange=[first,last],sampleRate=sr,pcmFloat32Sha256=hashlib.sha256(part.tobytes()).hexdigest(),mode='chunked30s-stride5s' if job['mode']=='whole' else 'independent-sequential-complete-context',expectedTextUsedAsPrompt=False,directFullTextCompared=False,currentNarrationApproved=False,humanWholeListeningApproved=False,finalMixedAsr=False,**result)
  write(output,record);state.update(status='complete-awaiting-direct-review',endedAt=now(),exitCode=0,result=output.relative_to(ROOT).as_posix(),resultSha256=sha(output));write(execution,state);print('DONE '+job['label'],flush=True)
 except BaseException as error:
  state.update(status='failed-preserving-input',endedAt=now(),error=repr(error));write(execution,state);raise
if __name__=='__main__':main()
