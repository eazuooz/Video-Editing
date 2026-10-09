"""One CPU2 job: current joined04 plus independent complete head and tail."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,ctypes,hashlib,json,os,subprocess,sys,time,traceback,wave
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):
    t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
def now():return datetime.now(timezone.utc).isoformat()
ap=argparse.ArgumentParser();ap.add_argument('--resource',required=True);args=ap.parse_args()
resource=read(ROOT/args.resource)
assert (datetime.now(timezone.utc)-datetime.fromisoformat(resource['observedAt'].replace('Z','+00:00'))).total_seconds()<240
assert resource['ownHeavyJobs']==0 and resource['cpuLoadPercent']<85 and resource['freePhysicalMemoryKiB']>8_000_000
PLAN=BASE/'current-mining-pcm-join-prepared-v1.json';plan=read(PLAN)
assert plan['allRemainderBytesIdentical'] and plan['allOriginal13WavsUnchanged'] and plan['wholeCandidateAndIndependentTextApproved']
review=read(BASE/'guides-contexts-asr-direct-review-v3.json');assert review['candidate22CompleteTextApprovedForPcmJoin']
assert read(BASE/'guides-contexts-asr-v3-execution.json')['actualExitObserved']
subprocess.run(['C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe','scripts/review-video-duplicates.cjs','similar-game-design','--check'],cwd=ROOT,check=True)
STATE=BASE/'current-mining-join-asr-v1-execution.json';LOG=BASE/'current-mining-join-asr-v1.log';DEST=BASE/'current-mining-join-asr-v1'
assert not any(p.exists() for p in [STATE,LOG,DEST]),'Read the existing execution.'
for key in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[key]='2'
os.environ.update(CUDA_VISIBLE_DEVICES='',TOKENIZERS_PARALLELISM='false',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x00004000)
import psutil
me=psutil.Process();DEST.mkdir();inputs=[]
for row in plan['windows']:
    source=ROOT/row['sourcePath'];assert sha(source)==row['sourceSha256']
    with wave.open(str(source),'rb') as w:
        params=w.getparams();w.setpos(row['startSample']);data=w.readframes(row['endSample']-row['startSample'])
    pad=row['zeroPaddingSamplesEachSide'];padded=b'\0\0'*pad+data+b'\0\0'*pad
    p=ROOT/'shared/output/similar-game-design/research/current-mining-join-asr-v1'/(row['id']+'.wav')
    p.parent.mkdir(parents=True,exist_ok=True);assert not p.exists()
    with wave.open(str(p),'wb') as w:w.setparams(params);w.writeframes(padded)
    with wave.open(str(p),'rb') as w:assert w.readframes(w.getnframes())==padded
    inputs.append({**row,'contextPath':p.relative_to(ROOT).as_posix(),'contextSha256':sha(p),'exactSourceSampleBytesMatched':True})
state=dict(schemaVersion=1,slug='similar-game-design',pid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),
 sessionId=None,status='loading-joined04-CPU2-ASR',cpuThreads=2,gpuJobs=0,cpuJobs=1,startedAt=now(),completed=0,total=3,
 planSha256=sha(PLAN),inputs=inputs,exitCode=None,actualExitObserved=False,automaticApproval=False,
 originalOther12Retranscribed=False,currentJoinedVoiceApproved=False,finalMixedAsrApproved=False)
def checkpoint():
    sp=BASE/'current-mining-join-asr-v1.session.json'
    if sp.exists():state['sessionId']=read(sp)['sessionId']
    state['updatedAt']=now();save(STATE,state)
    job=dict(status=state['status'],pid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),sessionId=state['sessionId'],
     state=STATE.relative_to(ROOT).as_posix(),log=LOG.relative_to(ROOT).as_posix(),completed=state['completed'],total=3,
     cpuThreads=2,gpu=0,singleJob=True,workerExpectedRunning=state['exitCode'] is None,exitCode=state['exitCode'])
    cp=read(BASE/'latest-checkpoint.json');cp.update(recordedAt=now(),stage='localized04-exact-PCM-join-CPU-ASR',ownedJob=job,
       guideCompleteContextReview='projects/similar-game-design/production/guides-contexts-asr-direct-review-v3.json',
       nextAction='Directly compare complete joined04/head/tail; preserve all original remaining PCM. Then measured source allocation,60FPS independent spatial/caption pixels, final mix/pair/QA. No new TTS or old13 ASR.')
    save(BASE/'latest-checkpoint.json',cp)
    qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json'
    for _ in range(8):
        raw=qp.read_text('utf-8-sig');q=json.loads(raw);item=next(x for x in q['items'] if x['slug']=='similar-game-design')
        item.update(stage=cp['stage'],currentExecution=job,nextAction=cp['nextAction']);q.update(updatedAt=now(),lastProgressAt=now())
        if qp.read_text('utf-8-sig')==raw:save(qp,q);break
        time.sleep(.15)
    else:raise RuntimeError('Concurrent queue write.')
class Tee:
    def __init__(self,out,log):self.out=out;self.log=log
    def write(self,s):self.out.write(s);self.out.flush();self.log.write(s);self.log.flush();return len(s)
    def flush(self):self.out.flush();self.log.flush()
sys.stdout.reconfigure(encoding='utf-8');sys.stderr.reconfigure(encoding='utf-8');out,err=sys.stdout,sys.stderr
with LOG.open('x',encoding='utf-8') as log:
    sys.stdout=Tee(out,log);sys.stderr=sys.stdout
    try:
        checkpoint()
        import torch
        from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
        torch.set_num_threads(2);torch.set_num_interop_threads(1)
        modelpath=ROOT/'qwen3-tts/models/whisper-large-v3-turbo'
        model=AutoModelForSpeechSeq2Seq.from_pretrained(str(modelpath),dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager',local_files_only=True).to('cpu')
        processor=AutoProcessor.from_pretrained(str(modelpath),local_files_only=True)
        transcriber=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float32,device='cpu')
        results=[]
        for row in inputs:
            state['status']='transcribing-'+row['id'];checkpoint();p=ROOT/row['contextPath'];assert sha(p)==row['contextSha256']
            result=transcriber(str(p),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
            results.append({**row,'text':result['text'],'words':result['chunks'],'expectedWasRecognizerPrompt':False,'directlyCompared':False,'approved':False})
            assert sha(p)==row['contextSha256'];save(DEST/(row['id']+'.json'),results[-1]);save(DEST/'asr.json',dict(complete=len(results)==3,results=results,automaticApproval=False))
            state['completed']=len(results);checkpoint();print(json.dumps(dict(id=row['id'],text=result['text']),ensure_ascii=False),flush=True)
        state.update(status='closed-joined04-ASR-awaiting-direct-review',exitCode=0,cpuJobs=0,finishedAt=now());checkpoint()
    except BaseException:
        state.update(status='closed-joined04-ASR-failed',exitCode=1,cpuJobs=0,error=traceback.format_exc(),finishedAt=now());checkpoint();traceback.print_exc();raise
    finally:sys.stdout=out;sys.stderr=err
