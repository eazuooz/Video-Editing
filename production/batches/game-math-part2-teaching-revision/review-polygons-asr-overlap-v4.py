"""Unprompted single-window readback where chunked recognition overlapped itself."""
from pathlib import Path
from datetime import datetime
import os,ctypes,hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent;R=B/'cross-game-review-20261011'
for key in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS']:os.environ[key]='2'
os.environ.update(CUDA_VISIBLE_DEVICES='',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',TOKENIZERS_PARALLELISM='false')
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x00004000)
import psutil
assert psutil.virtual_memory().available>8_000_000_000 and psutil.cpu_percent(interval=1)<90
import torch,soundfile as sf
from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
torch.set_num_threads(2);torch.set_num_interop_threads(1)
modelpath=ROOT/'qwen3-tts/models/whisper-large-v3-turbo'
model=AutoModelForSpeechSeq2Seq.from_pretrained(str(modelpath),dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager',local_files_only=True).to('cpu')
proc=AutoProcessor.from_pretrained(str(modelpath),local_files_only=True)
recognizer=pipeline('automatic-speech-recognition',model=model,tokenizer=proc.tokenizer,feature_extractor=proc.feature_extractor,dtype=torch.float32,device='cpu')
def read(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
rows=[]
out_path=R/'polygons-v4-asr-overlap-windows.json'
for slug,ident,lo in [('game-math-polygon-centers-v2','11',34),('game-math-polygon-centers-v2','12',38),('game-math-polygon-partition-v2','19',None)]:
    P=ROOT/'projects'/slug;m=read(P/'project.json');t=read(P/'production/timeline.json');slot=next(s for s in t['scenes'] if s['id']==ident)
    source=ROOT/m['paths']['videoClean'];hi=slot['seconds'];lo=hi-25 if lo is None else lo;assert 0<hi-lo<30
    digest=sha(source);dest=ROOT/f'shared/output/{slug}/mixed-asr-v4/{ident}-overlap-window.wav'
    subprocess.run(['ffmpeg','-hide_banner','-nostdin','-y','-v','error','-threads','2','-ss',str(slot['start']+lo),'-i',str(source),'-t',str(hi-lo),'-map','0:a:0','-ar','48000','-ac','2','-c:a','pcm_s16le',str(dest)],check=True)
    raw=recognizer(str(dest),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
    rows.append({'slug':slug,'scene':ident,'source':source.relative_to(ROOT).as_posix(),'sourceSha256':digest,'sceneLocalWindow':[lo,hi],'globalStart':slot['start']+lo,'wavSha256':sha(dest),'text':raw['text'],'words':raw['chunks'],'expectedTextUsedAsPrompt':False,'singleWindowWithoutChunkOverlap':True,'humanListening':'pending'})
    assert sha(source)==digest
    out={'recordedAt':datetime.now().astimezone().isoformat(),'rows':rows,'automaticApproval':False,'humanListening':'pending','gpuJobs':0,'researchControlsModified':0,'complete':len(rows)==3}
    out_path.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print('Unprompted single-window readback complete:',slug,ident,flush=True)
