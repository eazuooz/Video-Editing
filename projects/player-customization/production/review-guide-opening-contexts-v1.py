"""Recognize only two new complete sentences to resolve onset differences.

No expected script is passed to the recognizer. Never grants voice approval.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse, array, ctypes, hashlib, json, os, sys, time, traceback, wave

ROOT=Path(__file__).resolve().parents[3]
BASE=Path(__file__).resolve().parent
STATE=BASE/'observation-guide-opening-asr-execution-v1.json'
SESSION=STATE.with_name(STATE.stem+'.session.json')
DEST=BASE/'observation-guide-opening-asr-v1'
PCM=ROOT/'shared/output/player-customization/research/observation-guide-opening-asr-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
now=lambda:datetime.now(timezone.utc).isoformat()
def save(p,d):
    tmp=p.with_name(p.name+f'.{os.getpid()}.writing')
    tmp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf-8')
    for attempt in range(40):
        try:os.replace(tmp,p);return
        except OSError:
            if attempt==39:raise
            time.sleep(.15)
parser=argparse.ArgumentParser();parser.add_argument('--resource',required=True);args=parser.parse_args()
resource=read(ROOT/args.resource)
assert (datetime.now(timezone.utc)-datetime.fromisoformat(resource['observedAt'].replace('Z','+00:00'))).total_seconds()<240
assert resource['ownHeavyJobs']==0 and resource['cpuLoadPercent']<85 and resource['freePhysicalMemoryKiB']>8_000_000
assert not STATE.exists() and not DEST.exists() and not PCM.exists(),'Read existing results; do not repeat.'
previous=read(BASE/'observation-guide-contexts-asr-execution-v1.json')
assert previous['exitCode']==0 and previous['actualExitObserved'] and previous['completed']==16
plan_path=BASE/'observation-guide-opening-context-plan-v1.json';plan=read(plan_path)
assert sha(ROOT/plan['parentReview'])==plan['parentReviewSha256']
assert len(plan['contexts'])==2 and all(x['containsCompleteSentence'] and x['directWordAndPcmBoundaryReview'] for x in plan['contexts'])
for name in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[name]='2'
os.environ.update(CUDA_VISIBLE_DEVICES='',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',TOKENIZERS_PARALLELISM='false')
if os.name=='nt':ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x00004000)
sys.stdout.reconfigure(encoding='utf-8');sys.stderr.reconfigure(encoding='utf-8')
DEST.mkdir();PCM.mkdir()
state=dict(schemaVersion=1,slug='player-customization',pid=os.getpid(),commandLine=[sys.executable,*sys.argv],sessionId=None,
    startedAt=now(),status='loading-single-CPU2-opening-contexts',cpuThreads=2,gpu=0,singleJob=True,
    completed=0,total=2,planPath=rel(plan_path),planSha256=sha(plan_path),exitCode=None,
    voiceTextIntegrityApproved=False,finalMixedAsrApproved=False,humanListening='pending',humanPronunciation='pending')
def checkpoint():
    if SESSION.exists():
        launch=read(SESSION)
        if launch['pid']==os.getpid():state.update(sessionId=launch['sessionId'],processIdentity=launch['processIdentity'])
    state['updatedAt']=now();save(STATE,state)
    job=dict(status=state['status'],pid=state['pid'],commandLine=state['commandLine'],sessionId=state['sessionId'],
        processIdentity=state.get('processIdentity'),state=rel(STATE),cpuThreads=2,gpu=0,singleJob=True,
        completed=state['completed'],total=2,exitCode=state['exitCode'],workerExpectedRunning=state['exitCode'] is None)
    cp=read(BASE/'latest-checkpoint.json');cp.update(recordedAt=now(),stage=state['status'],ownedJob=job,
        nextAction='Read both current-hash complete opening sentences against whole/half text and PCM before resolving11/16. Preserve all previous audio/results; final voice, white/mix/pair/upload gates false.')
    save(BASE/'latest-checkpoint.json',cp)
    qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qp)
    item=next(i for i in q['items'] if i['slug']=='player-customization');item.update(stage=cp['stage'],currentExecution=job,nextAction=cp['nextAction'])
    q['updatedAt']=now();save(qp,q)
try:
    checkpoint();inputs=[]
    for row in plan['contexts']:
        source=ROOT/row['sourcePath'];assert sha(source)==row['sourceSha256']
        with wave.open(str(source),'rb') as w:
            params=w.getparams();assert params.framerate==24000 and params.nchannels==1 and params.sampwidth==2
            w.setpos(row['startSample']);pcm=w.readframes(row['endSample']-row['startSample'])
        target=PCM/(row['id']+'.wav')
        with wave.open(str(target),'wb') as w:w.setparams(params);w.writeframes(pcm)
        with wave.open(str(target),'rb') as w:assert w.readframes(w.getnframes())==pcm
        inputs.append({**row,'contextPath':rel(target),'contextSha256':sha(target),'exactSourceSampleBytesMatched':True})
    import torch
    from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
    torch.set_num_threads(2);torch.set_num_interop_threads(1)
    model_path=ROOT/'qwen3-tts/models/whisper-large-v3-turbo'
    model=AutoModelForSpeechSeq2Seq.from_pretrained(str(model_path),dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager',local_files_only=True).to('cpu')
    processor=AutoProcessor.from_pretrained(str(model_path),local_files_only=True)
    recognizer=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float32,device='cpu')
    results=[]
    for row in inputs:
        state['status']='recognizing-complete-opening-'+row['sceneId'];checkpoint()
        result=recognizer(str(ROOT/row['contextPath']),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
        record={**row,'text':result['text'],'words':result['chunks'],'expectedWasRecognizerPrompt':False,'directReview':False}
        assert sha(ROOT/row['contextPath'])==row['contextSha256'] and sha(ROOT/row['sourcePath'])==row['sourceSha256']
        results.append(record);save(DEST/(row['id']+'.json'),record)
        save(DEST/'asr.json',dict(complete=len(results)==2,results=results,automaticApproval=False))
        state['completed']=len(results);checkpoint();print(json.dumps(dict(id=row['id'],text=record['text'],words=record['words']),ensure_ascii=False),flush=True)
    state.update(status='opening-contexts-complete-awaiting-direct-review',exitCode=0,finishedAt=now());checkpoint()
except BaseException:
    state.update(status='opening-context-ASR-failed',exitCode=1,error=traceback.format_exc(),finishedAt=now());checkpoint();raise
