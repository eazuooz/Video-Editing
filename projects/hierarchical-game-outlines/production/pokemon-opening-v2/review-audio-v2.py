"""Read current generated voice or final mixed scene intervals once on CPU."""
from pathlib import Path
import os, sys, json, hashlib, datetime, subprocess, traceback
for k in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','NUMEXPR_NUM_THREADS']: os.environ[k]='2'
os.environ.update(CUDA_VISIBLE_DEVICES='',TOKENIZERS_PARALLELISM='false',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
import psutil
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
control=json.loads((ROOT/'shared/publishing/video-production-control.json').read_text(encoding='utf-8'))
assert control['selectedVideo']=='hierarchical-game-outlines' and control['newProductionAuthorization']['fullProductionAuthorized']
MODE=sys.argv[1] if len(sys.argv)>1 else 'voice'
sys.stdout.reconfigure(encoding='utf-8')
assert MODE in ['voice','mix']
assert MODE=='mix'
STATE=OUT/'mix-asr-v2.json'
assert not STATE.exists(), 'Read the existing request; do not repeat it'
voice=json.loads((OUT/'voice-execution-v1.json').read_text(encoding='utf-8'))
assert voice['status']=='generated-pending-current-asr'
try:
    old=psutil.Process(voice['worker']['pid'])
    assert abs(old.create_time()-voice['worker']['createTime'])>.01, 'Wait for voice process exit and lease release'
except psutil.NoSuchProcess: pass
now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
me=psutil.Process();me.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
state=dict(startedAt=now(),pid=me.pid,createTime=me.create_time(),command=me.cmdline(),cwd=me.cwd(),cpuThreads=2,gpuJobs=0,status='running',exitCode=None,
 resource=dict(cpu=psutil.cpu_percent(interval=1),availableMemoryBytes=psutil.virtual_memory().available,
 gpu=subprocess.run(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],capture_output=True,text=True).stdout),results=[])
assert state['resource']['cpu']<85 and state['resource']['availableMemoryBytes']>8_000_000_000
def save():STATE.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
save()
try:
    import torch
    from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
    torch.set_num_threads(2);torch.set_num_interop_threads(1)
    modelpath=ROOT/'qwen3-tts/models/whisper-large-v3-turbo'
    model=AutoModelForSpeechSeq2Seq.from_pretrained(str(modelpath),dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager',local_files_only=True).to('cpu')
    processor=AutoProcessor.from_pretrained(str(modelpath),local_files_only=True)
    transcriber=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float32,device='cpu')
    scenes=json.loads((OUT/('tts-request.ko.json' if MODE=='voice' else 'narration.ko.json')).read_text(encoding='utf-8'))['scenes']
    for scene in scenes:
        p=OUT/f'generated-narration/chunks/{scene["id"]}-scene.wav' if MODE=='voice' else ROOT/next(x['path'] for x in json.loads((OUT/'mix-final-inputs-v1.json').read_text(encoding='utf-8'))['scenes'] if x['id']==scene['id'])
        digest=sha(p);state['active']=scene['id'];save()
        result=transcriber(str(p),generate_kwargs={'language':'korean','task':'transcribe'},chunk_length_s=30,return_timestamps='word')
        row=dict(id=scene['id'],path=p.relative_to(ROOT).as_posix(),sha256=digest,expected=' '.join(scene['lines']),actual=result['text'],words=result['chunks'],expectedWasPrompt=False,directReview=False)
        assert sha(p)==digest
        state['results'].append(row);save()
        print(json.dumps({k:row[k] for k in ['id','expected','actual']},ensure_ascii=False),flush=True)
    state.update(status='complete-awaiting-direct-review',exitCode=0,finishedAt=now(),humanListening=False);save()
except BaseException:
    state.update(status='failed',exitCode=1,error=traceback.format_exc(),finishedAt=now());save();raise
