"""One alternate bounded decoder diagnostic, without expected words or repeat suppression."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,os,psutil,traceback
for k in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[k]='2'
os.environ.update(CUDA_VISIBLE_DEVICES='',TOKENIZERS_PARALLELISM='false',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
now=lambda:datetime.now(timezone.utc).isoformat()
out=R/'first-paragraph-spliced-whole-asr-v1.json';assert not out.exists()
tts=read(R/'narration-first-paragraph-repair-execution-v1.json')
resume=read(R/'first-paragraph-repair-handoff-verification-v1.json')
assert tts['actualExitObserved'] and tts['actualOuterExitCode']==0 and tts['generationComplete'] and len(tts['results'])==1
assert resume['restorationVerified'] and resume['all71ProtectedInputsMatched']
for x in tts['protectedInputs']+tts['results']:assert sha(ROOT/x['path'])==x['sha256']
row=read(R/'first-paragraph-splice-candidate-v1.json');source=ROOT/row['path']
assert sha(source)==row['sha256']
resource=dict(observedAt=now(),cpuLoadPercent=psutil.cpu_percent(interval=1),freePhysicalMemoryKiB=psutil.virtual_memory().available//1024,ownHeavyCpuJobs=0)
assert resource['cpuLoadPercent']<85 and resource['freePhysicalMemoryKiB']>8_000_000
me=psutil.Process();state=dict(schemaVersion=1,pid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),cwd=me.cwd(),startedAt=now(),cpuThreads=2,gpuJobs=0,
    sourcePath=source.relative_to(ROOT).as_posix(),sourceSha256=sha(source),resource=resource,protectedInputs=tts['protectedInputs'],
    decoder='Whisper local CPU2, default decoder word timestamps; no expected text prompt or anti-repetition constraints',
    expectedWasRecognizerPrompt=False,actualVoiceOrPronunciationFailureConfirmed=False,directReview=False,approved=False,exitCode=None)
def save():out.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n','utf-8')
save()
try:
    import torch
    from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
    torch.set_num_threads(2);torch.set_num_interop_threads(1);modelpath=ROOT/'qwen3-tts/models/whisper-large-v3-turbo'
    model=AutoModelForSpeechSeq2Seq.from_pretrained(str(modelpath),dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager',local_files_only=True).to('cpu')
    proc=AutoProcessor.from_pretrained(str(modelpath),local_files_only=True)
    pipe=pipeline('automatic-speech-recognition',model=model,tokenizer=proc.tokenizer,feature_extractor=proc.feature_extractor,dtype=torch.float32,device='cpu')
    raw=pipe(str(source),generate_kwargs={'language':'korean','task':'transcribe','num_beams':1},return_timestamps='word')
    assert sha(source)==row['sha256']
    state.update(text=raw['text'],words=raw['chunks'],exitCode=0,finishedAt=now());save();print(json.dumps(dict(text=raw['text']),ensure_ascii=False),flush=True)
except BaseException:
    state.update(exitCode=1,error=traceback.format_exc(),finishedAt=now());save();raise
