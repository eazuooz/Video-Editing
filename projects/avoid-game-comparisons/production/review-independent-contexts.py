"""Independent CPU readbacks of ambiguous current PCM; no automatic voice approval."""
from __future__ import annotations
import hashlib, json, os, subprocess, sys, traceback
from datetime import datetime, timezone
from pathlib import Path
import soundfile as sf

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
PROOF = ROOT / 'production/batches/sakurai-planning-game-design/proof-avoid-game-comparisons'
QUEUE = PROOF.parent / 'queue.json'
PREFIX = sys.argv[1] if len(sys.argv) > 1 else 'independent-context'
if PREFIX not in ('independent-context', 'targeted-candidate', 'post-repair'): raise ValueError('Unrecognized readback scope')
STATE = BASE / f'{PREFIX}-asr-execution.json'
REQUEST = BASE / f'{PREFIX}-readback-request.json'
LOG = BASE / f'{PREFIX}-asr.log'
def read(path): return json.loads(path.read_text(encoding='utf-8'))
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def now(): return datetime.now(timezone.utc).isoformat()
def save(path, value):
    tmp=path.with_name(path.name+f'.{os.getpid()}.writing')
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8'); tmp.replace(path)

if STATE.exists(): raise RuntimeError('Inspect the existing execution/results; do not duplicate context readback')
whole=read(BASE/'narration-asr-execution.json')
if not whole['readbackComplete'] or whole.get('exitCode')!=0: raise RuntimeError('Whole current readback is incomplete')
alive=subprocess.run(['powershell','-NoProfile','-Command',f'Get-CimInstance Win32_Process -Filter "ProcessId={whole["pid"]}" | Select-Object -ExpandProperty CommandLine'],capture_output=True,text=True)
if 'review-current-narration.py' in alive.stdout: raise RuntimeError('Whole readback is still alive')
request=read(REQUEST)
for source in request['protectedInputs']:
    if sha(ROOT/source['path'])!=source['sha256']: raise RuntimeError('Changed protected input '+source['path'])
state={'schemaVersion':1,'pid':os.getpid(),'sessionId':None,'startedAt':now(),'status':'loading-local-whisper-CPU','cpuJobs':1,'gpuJobs':0,'request':REQUEST.relative_to(ROOT).as_posix(),'requestSha256':sha(REQUEST),'results':[],'directContextReview':False,'humanWholeListening':'pending','narrationApproved':False,'log':LOG.relative_to(ROOT).as_posix()}
def checkpoint():
    launch=BASE/f'{PREFIX}-asr-session.json'
    if launch.exists():
        s=read(launch)
        if s['pid']==os.getpid(): state['sessionId']=s['sessionId']
    state['updatedAt']=now();save(STATE,state)
    q=read(QUEUE);item=next(i for i in q['items'] if i['slug']=='avoid-game-comparisons')
    previous=item.get('execution',{})
    if previous.get('pid')!=os.getpid(): item.setdefault('executionHistory',[]).append(previous)
    ex=dict(previous);secondary=ex.get('secondaryTasks',[])
    ex.update(phase='independent-ambiguous-PCM-context-ASR',status=state['status'],pid=os.getpid(),sessionId=state['sessionId'],alive=state['cpuJobs']>0,state=STATE.relative_to(ROOT).as_posix(),log=state['log'],activeTasks=[] if not state['cpuJobs'] else [{'kind':'independent-context-CPU-ASR','pid':os.getpid(),'sessionId':state['sessionId']}],gpuSynthesisJobs=0,primaryCpuProductionJobs=state['cpuJobs'],cpuProductionJobs=state['cpuJobs']+sum(x.get('kind') in ['full-decode','source-discovery'] for x in secondary),renderJobs=0,uploads=0,observedAt=now(),newNarrationCreated=True,newSceneCreated=True)
    item.update(stage='independent-context-ASR-and-additional-native-actions',execution=ex,updatedAt=now(),nextAction='Directly compare independent ambiguous contexts and newly acquired unique native actions; preserve all unaffected PCM and explanation duration. Final timing, captions, mix/render/QA/private upload remain pending.')
    key={'independent-context':'independentContextReadback','targeted-candidate':'targetedCandidateReadback','post-repair':'postRepairReadback'}[PREFIX]
    item[key]={'state':STATE.relative_to(ROOT).as_posix(),'status':state['status'],'results':len(state['results']),'directReview':False}
    item['checkpoints']['narration']=False;q['updatedAt']=now();save(QUEUE,q)
    for path in [BASE/'latest-checkpoint.json',PROOF/'latest-checkpoint.json']:
        v=read(path);v.update(stage=item['stage'],execution=ex,independentContextReadback=item['independentContextReadback'],ttsStarted=True,scenesCreated=True,nextAction=item['nextAction'],updatedAt=now());save(path,v)
checkpoint()
class Tee:
    def __init__(self, original, log): self.original=original;self.log=log
    def write(self, value): self.original.write(value);self.original.flush();self.log.write(value);self.log.flush();return len(value)
    def flush(self): self.original.flush();self.log.flush()
original_out,original_err=sys.stdout,sys.stderr
with LOG.open('a',encoding='utf-8') as log:
    sys.stdout=Tee(original_out,log);sys.stderr=sys.stdout
    try:
        import torch
        from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
        torch.set_num_threads(2)
        model_path=ROOT/'qwen3-tts/models/whisper-large-v3-turbo'
        model=AutoModelForSpeechSeq2Seq.from_pretrained(str(model_path),dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager',local_files_only=True).to('cpu')
        processor=AutoProcessor.from_pretrained(str(model_path),local_files_only=True)
        transcriber=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float32,device='cpu')
        folder=BASE/({'independent-context':'asr-context-local','targeted-candidate':'asr-targeted-candidate-local','post-repair':'asr-post-repair-local'}[PREFIX]);folder.mkdir(exist_ok=True)
        for context in request['contexts']:
            path=ROOT/context['audioPath']
            if sha(path)!=context['audioSha256']: raise RuntimeError('PCM changed '+context['id'])
            audio,rate=sf.read(path,dtype='float32',always_2d=True)
            start=round(context['fromSeconds']*rate);end=min(len(audio),round(context['toSeconds']*rate))
            if start<0 or end<=start: raise RuntimeError('Invalid context range')
            wav=folder/(context['id']+'.wav');sf.write(wav,audio[start:end],rate,subtype='PCM_16')
            state['status']='transcribing-'+context['id'];checkpoint();print('Context '+context['id'],flush=True)
            # Deliberately provide no reference text to the recognizer.
            raw=transcriber(str(wav),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
            result={**context,'contextAudioPath':wav.relative_to(ROOT).as_posix(),'contextAudioSha256':sha(wav),'actualFromSeconds':start/rate,'actualToSeconds':end/rate,'text':raw['text'],'words':raw['chunks'],'expectedWasRecognizerPrompt':False,'directReview':False}
            save(folder/(context['id']+'.json'),result);state['results'].append(result);checkpoint()
            print(raw['text'],flush=True)
        for source in request['protectedInputs']:
            if sha(ROOT/source['path'])!=source['sha256']: raise RuntimeError('Protected input changed during context readback')
        state.update(status='finished-awaiting-direct-context-review',cpuJobs=0,exitCode=0,endedAt=now());checkpoint();print('Independent contexts complete; direct review and human listening remain separate.',flush=True)
    except BaseException:
        state.update(status='failed',cpuJobs=0,exitCode=1,endedAt=now(),error=traceback.format_exc());checkpoint();traceback.print_exc();raise
    finally: sys.stdout,sys.stderr=original_out,original_err
