"""Single CPU2 ASR for the newly generated guides/localized candidate only.

The old13 voices are never transcribed again. Text is review material, never a
recognizer prompt or automatic narration/final-mix approval.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse, ctypes, hashlib, json, os, subprocess, sys, time, traceback, wave
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
def now():return datetime.now(timezone.utc).isoformat()
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return p.relative_to(ROOT).as_posix()
def save(p,x):
    t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8')
    for retry in range(40):
        try:os.replace(t,p);return
        except OSError:
            if retry==39:raise
            time.sleep(.15)
ap=argparse.ArgumentParser();ap.add_argument('--resource',required=True);ap.add_argument('--mode',choices=['whole','contexts'],required=True)
args=ap.parse_args();prefix=f'guides-{args.mode}-asr-v3'
STATE=BASE/(prefix+'-execution.json');SESSION=BASE/(prefix+'.session.json');LOG=BASE/(prefix+'.log');DEST=BASE/prefix
resource=read(ROOT/args.resource)
assert (datetime.now(timezone.utc)-datetime.fromisoformat(resource['observedAt'].replace('Z','+00:00'))).total_seconds()<240
assert resource['ownHeavyJobs']==0 and resource['cpuLoadPercent']<85 and resource['freePhysicalMemoryKiB']>8_000_000
assert not any(p.exists() for p in [STATE,LOG,DEST]),'Read the existing execution; do not repeat ASR.'
tts=read(BASE/'guides-and-localized-repair-tts-execution-v3.json')
assert tts['exitCode']==0 and tts['generationComplete'] and tts['actualExitObserved'] and len(tts['results'])==9
restored=read(BASE/'guides-research-resume-verification-v3.json')
assert restored['restorationVerified'] and restored['ownedCoordinatorClosed'] and restored['ttsLeaseToken']==tts['leaseToken']
request=read(BASE/'guides-and-localized-repair-tts-request-v3.json')
for x in request['protectedInputs']:assert sha(ROOT/x['path'])==x['sha256'],x['path']
script=read(ROOT/'projects/similar-game-design/script/observation-guides-with-onset-repair.ko.v3.json')
assert len(script['scenes'])==9 and sum(len(x['lines']) for x in script['scenes'])==17
inputs=[]
if args.mode=='whole':
    for scene in script['scenes']:
        m=next(x for x in tts['results'] if x['id']==scene['id']);assert sha(ROOT/m['path'])==m['sha256']
        inputs.append(dict(id=scene['id'],sourcePath=m['path'],sourceSha256=m['sha256'],expectedKo=scene['lines'],
                           sourceSamples=m['samples'],seconds=m['seconds']))
else:
    whole=read(BASE/'guides-whole-asr-v3-execution.json');assert whole['exitCode']==0 and whole['actualExitObserved']
    plan=read(BASE/'guides-independent-context-plan-v3.json')
    assert plan['boundariesDirectlyComparedWithCurrentWordsAndPCM']
    review=read(ROOT/plan['wholeReview']);assert sha(ROOT/plan['wholeReview'])==plan['wholeReviewSha256']
    assert review['allWholeTextsDirectlyCompared'];inputs=plan['contexts'];assert len(inputs)>=8
subprocess.run(['C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe',
 'scripts/review-video-duplicates.cjs','similar-game-design','--check'],cwd=ROOT,check=True)
for k in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[k]='2'
os.environ.update(CUDA_VISIBLE_DEVICES='',TOKENIZERS_PARALLELISM='false',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
if os.name=='nt':ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x00004000)
import psutil
me=psutil.Process();DEST.mkdir()
state=dict(schemaVersion=1,slug='similar-game-design',mode=args.mode,pid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),
 sessionId=None,startedAt=now(),status='loading-new-guide-CPU2-ASR',cpuThreads=2,gpuJobs=0,cpuJobs=1,
 completed=0,total=len(inputs),resource=resource,audioInputs=inputs,ttsExecutionSha256=sha(BASE/'guides-and-localized-repair-tts-execution-v3.json'),
 requestSha256=sha(BASE/'guides-and-localized-repair-tts-request-v3.json'),exitCode=None,automaticApproval=False,
 original13Retranscribed=False,narrationApproved=False,finalMixedAsrApproved=False,humanListening='pending',humanPronunciation='pending')
def checkpoint():
    if SESSION.exists():
        launch=read(SESSION)
        if launch.get('pid')==me.pid:state['sessionId']=launch['sessionId']
    state['updatedAt']=now();save(STATE,state)
    job=dict(status=state['status'],pid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),sessionId=state['sessionId'],
     state=rel(STATE),log=rel(LOG),completed=state['completed'],total=state['total'],cpuThreads=2,gpu=0,
     singleJob=True,workerExpectedRunning=state['exitCode'] is None,exitCode=state['exitCode'])
    cp=read(BASE/'latest-checkpoint.json');cp.update(recordedAt=now(),stage=f'new-guides-and-repair-{args.mode}-CPU-ASR',ownedJob=job,
     narrationApproved=False,asrApproved=False,
     nextAction='Read all new expected/actual full texts and words, then independent complete contexts and original04 PCM-preserving repair join. Original13 whole/context ASR is closed. Final timing/depth/caption/mix/pair/QA/collection/private remain pending.')
    save(BASE/'latest-checkpoint.json',cp)
    qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json'
    for _ in range(8):
        raw=qp.read_text('utf-8-sig');q=json.loads(raw);item=next(x for x in q['items'] if x['slug']=='similar-game-design')
        item.update(stage=cp['stage'],currentExecution=job,nextAction=cp['nextAction']);q.update(updatedAt=now(),lastProgressAt=now())
        if qp.read_text('utf-8-sig')==raw:save(qp,q);break
        time.sleep(.15)
    else:raise RuntimeError('Concurrent queue write; preserve foreign work.')
class Tee:
    def __init__(self,out,file):self.out=out;self.file=file
    def write(self,s):self.out.write(s);self.out.flush();self.file.write(s);self.file.flush();return len(s)
    def flush(self):self.out.flush();self.file.flush()
sys.stdout.reconfigure(encoding='utf-8');sys.stderr.reconfigure(encoding='utf-8');out,err=sys.stdout,sys.stderr
with LOG.open('x',encoding='utf-8') as log:
    sys.stdout=Tee(out,log);sys.stderr=sys.stdout
    try:
        checkpoint()
        if args.mode=='contexts':
            audio_dir=ROOT/'shared/output/similar-game-design/research'/prefix;assert not audio_dir.exists();audio_dir.mkdir(parents=True)
            sliced=[]
            for c in inputs:
                source=ROOT/c['sourcePath'];assert sha(source)==c['sourceSha256']
                with wave.open(str(source),'rb') as w:
                    params=w.getparams();assert (params.framerate,params.nchannels,params.sampwidth)==(24000,1,2)
                    a,b=c['startSample'],c['endSample'];assert 0<=a<b<=w.getnframes();w.setpos(a);pcm=w.readframes(b-a)
                pad=c.get('zeroPaddingSamplesEachSide',0);assert pad>=0
                padded=b'\x00\x00'*pad+pcm+b'\x00\x00'*pad;target=audio_dir/(c['id']+'.wav')
                with wave.open(str(target),'wb') as w:w.setparams(params);w.writeframes(padded)
                with wave.open(str(target),'rb') as w:assert w.readframes(w.getnframes())==padded
                sliced.append({**c,'contextPath':rel(target),'contextSha256':sha(target),'exactSourceSampleBytesMatched':True,
                               'pcmSha256':hashlib.sha256(pcm).hexdigest()})
            inputs=sliced;save(DEST/'pcm-slices.json',dict(createdAt=now(),slices=sliced))
        import torch
        from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
        torch.set_num_threads(2);torch.set_num_interop_threads(1);model_path=ROOT/'qwen3-tts/models/whisper-large-v3-turbo'
        model=AutoModelForSpeechSeq2Seq.from_pretrained(str(model_path),dtype=torch.float32,low_cpu_mem_usage=True,
         use_safetensors=True,attn_implementation='eager',local_files_only=True).to('cpu')
        processor=AutoProcessor.from_pretrained(str(model_path),local_files_only=True)
        transcriber=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,
         feature_extractor=processor.feature_extractor,dtype=torch.float32,device='cpu')
        results=[]
        for row in inputs:
            state['status']='transcribing-new-'+row['id'];checkpoint();audio_path=ROOT/row.get('contextPath',row['sourcePath'])
            audio_sha=row.get('contextSha256',row['sourceSha256']);assert sha(audio_path)==audio_sha
            raw=transcriber(str(audio_path),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
            result={**row,'text':raw['text'],'words':raw['chunks'],'audioSha256':audio_sha,
                    'expectedWasRecognizerPrompt':False,'directReview':False,'approved':False}
            assert sha(audio_path)==audio_sha;results.append(result);save(DEST/(row['id']+'.json'),result)
            save(DEST/'asr.json',dict(complete=len(results)==len(inputs),results=results,automaticApproval=False,
                                      humanListening='pending',humanPronunciation='pending'))
            state['completed']=len(results);checkpoint();print(json.dumps(dict(id=row['id'],text=result['text']),ensure_ascii=False),flush=True)
        state.update(status='closed-new-guide-ASR-awaiting-direct-review',exitCode=0,cpuJobs=0,finishedAt=now());checkpoint()
    except BaseException:
        state.update(status='closed-new-guide-ASR-failed',exitCode=1,cpuJobs=0,finishedAt=now(),error=traceback.format_exc())
        checkpoint();traceback.print_exc();raise
    finally:sys.stdout=out;sys.stderr=err
