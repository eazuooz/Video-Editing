"""Read the two existing repair candidates once, CPU only, without rewriting queues."""
from pathlib import Path
import os, json, hashlib, datetime, traceback, subprocess
for k in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','NUMEXPR_NUM_THREADS']: os.environ[k]='2'
os.environ.update(CUDA_VISIBLE_DEVICES='',TOKENIZERS_PARALLELISM='false',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
import psutil
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
STATE=OUT/'repair-candidate-asr.json'
assert not STATE.exists(), 'No duplicate ASR. Read the saved result.'
now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
me=psutil.Process();me.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
state=dict(startedAt=now(),pid=me.pid,createTime=me.create_time(),command=me.cmdline(),cwd=me.cwd(),cpuThreads=2,gpuJobs=0,status='running',exitCode=None,
    resource=dict(cpu=psutil.cpu_percent(interval=1),availableMemoryBytes=psutil.virtual_memory().available,
      gpu=subprocess.run(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],capture_output=True,text=True).stdout),results=[])
assert state['resource']['cpu']<85 and state['resource']['availableMemoryBytes']>8_000_000_000
def save(): STATE.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
save()
try:
    import torch
    from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
    torch.set_num_threads(2);torch.set_num_interop_threads(1)
    modelpath=ROOT/'qwen3-tts/models/whisper-large-v3-turbo'
    model=AutoModelForSpeechSeq2Seq.from_pretrained(str(modelpath),dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager',local_files_only=True).to('cpu')
    processor=AutoProcessor.from_pretrained(str(modelpath),local_files_only=True)
    transcriber=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float32,device='cpu')
    script=json.loads((ROOT/'projects/hierarchical-game-outlines/revision-teaching-clarity-v1/script/additions.ko.json').read_text(encoding='utf-8-sig'))
    lines=next(x['lines'] for x in script['scenes'] if x['id']=='08a')
    for id,idx in [('08r1',0),('08r4',3)]:
        p=ROOT/f'shared/output/narration/hierarchical-game-outlines/two-paragraph-repair-v1/chunks/{id}-scene.wav'
        digest=hashlib.sha256(p.read_bytes()).hexdigest()
        result=transcriber(str(p),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
        row=dict(id=id,path=p.relative_to(ROOT).as_posix(),sha256=digest,expected=lines[idx],actual=result['text'],words=result['chunks'],expectedWasPrompt=False,directReview=False)
        assert hashlib.sha256(p.read_bytes()).hexdigest()==digest
        state['results'].append(row);save();print(json.dumps({k:row[k] for k in ['id','expected','actual']},ensure_ascii=False),flush=True)
    state.update(status='complete-awaiting-direct-review',exitCode=0,finishedAt=now(),humanListening=False,candidatesAdopted=False);save()
except BaseException:
    state.update(status='failed',exitCode=1,error=traceback.format_exc(),finishedAt=now());save();raise
