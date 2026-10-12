"""One CPU2 model pass for current splice/complete seam and a bounded alternate."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,hashlib,os,psutil,subprocess,traceback
for k in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[k]='2'
os.environ.update(CUDA_VISIBLE_DEVICES='',TOKENIZERS_PARALLELISM='false',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent;O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();now=lambda:datetime.now(timezone.utc).isoformat()
ap=argparse.ArgumentParser();ap.add_argument('--resource',required=True);a=ap.parse_args()
resource=read(ROOT/a.resource);assert (datetime.now(timezone.utc)-datetime.fromisoformat(resource['observedAt'])).total_seconds()<240 and resource['ownHeavyJobs']==0 and resource['cpuLoadPercent']<85 and resource['freePhysicalMemoryKiB']>8_000_000
planp=O/'post-splice-current-voice-review-plan-v1.json';plan=read(planp);assert len(plan['inputs'])==3
sp=O/'post-splice-current-voice-asr-execution-v1.json';out=O/'post-splice-current-voice-asr-v1';assert not sp.exists() and not out.exists();out.mkdir()
tts=read(O/'narration-cross-game-repair-execution-v1.json')
for x in tts['protectedInputs']+tts['results']+plan['inputs']:assert sha(ROOT/x.get('path'))==x['sha256']
me=psutil.Process();state=dict(pid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),cwd=me.cwd(),sessionId=None,startedAt=now(),cpuThreads=2,cpuJobs=1,gpuJobs=0,plan=planp.relative_to(ROOT).as_posix(),planSha256=sha(planp),total=3,completed=0,results=[],status='loading-CPU2-current-splice-review',exitCode=None,expectedWasRecognizerPrompt=False,automaticApproval=False,humanListeningApproved=False,finalMixedApproved=False)
def checkpoint():
 session=sp.with_name(sp.stem+'.session.json')
 if session.exists():state['sessionId']=read(session)['sessionId']
 state['updatedAt']=now();sp.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n','utf-8')
 cp=read(O/'latest-checkpoint.json');job=dict(pid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),cwd=me.cwd(),sessionId=state['sessionId'],state=sp.relative_to(ROOT).as_posix(),cpuThreads=2,gpuJobs=0,completed=state['completed'],total=3,exitCode=state['exitCode']);cp.update(stage=state['status'],ownedJob=job,activeOwnedWorkers=state['cpuJobs'],next='Actual closure then allthree fulltext directcomparison; adopt21a only if whole/seam complete. One held07b-p06 alternate is not human pronunciation approval.');(O/'latest-checkpoint.json').write_text(json.dumps(cp,ensure_ascii=False,indent=2)+'\n','utf-8')
 qp=B/'queue.json';raw=qp.read_bytes();q=read(qp);q['currentOrientationReview'].update(stage=state['status'],ownedJob=job,activeOwnedWorkers=state['cpuJobs'],next=cp['next']);assert qp.read_bytes()==raw;qp.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n','utf-8')
checkpoint()
try:
 import torch
 from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
 torch.set_num_threads(2);torch.set_num_interop_threads(1);modelpath=ROOT/'qwen3-tts/models/whisper-large-v3-turbo'
 model=AutoModelForSpeechSeq2Seq.from_pretrained(str(modelpath),dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager',local_files_only=True).to('cpu');proc=AutoProcessor.from_pretrained(str(modelpath),local_files_only=True);pipe=pipeline('automatic-speech-recognition',model=model,tokenizer=proc.tokenizer,feature_extractor=proc.feature_extractor,dtype=torch.float32,device='cpu')
 for row in plan['inputs']:
  state['status']='transcribing-'+row['id'];checkpoint();assert sha(ROOT/row['path'])==row['sha256']
  result=pipe(str(ROOT/row['path']),generate_kwargs={'language':'korean','task':'transcribe','num_beams':row['numBeams']},return_timestamps='word' if row['wordTimestamps'] else False)
  r={**row,**result,'expectedWasRecognizerPrompt':False,'directReview':False};state['results'].append(r);state['completed']=len(state['results']);(out/(row['id']+'.json')).write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n','utf-8');checkpoint();print(json.dumps(dict(id=row['id'],text=r['text']),ensure_ascii=False),flush=True)
 for x in tts['protectedInputs']+tts['results']+plan['inputs']:assert sha(ROOT/x['path'])==x['sha256']
 state.update(status='post-splice-current-ASR-closed-awaiting-directcomparison',cpuJobs=0,exitCode=0,finishedAt=now());checkpoint()
except BaseException:
 state.update(status='failed-preserve-post-splice-ASR',cpuJobs=0,exitCode=1,error=traceback.format_exc(),finishedAt=now());checkpoint();raise
