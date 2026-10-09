"""One CPU2/GPU0 worker: three new whole voices and three independent complete contexts.

Expected narration is review data, never a recognizer prompt. Finished original
or earlier guide ASR is not repeated, and no automatic approval is produced.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse, ctypes, hashlib, json, os, subprocess, sys, time, traceback, wave
ROOT=Path(__file__).resolve().parents[3]; BASE=Path(__file__).resolve().parent
STATE=BASE/'fresh-guides-asr-execution-v4.json'; SESSION=BASE/'fresh-guides-asr-session-v4.json'
LOG=BASE/'fresh-guides-asr-v4.log'; DEST=BASE/'fresh-guides-asr-v4'
def now(): return datetime.now(timezone.utc).isoformat()
def read(p): return json.loads(p.read_text('utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p): return p.relative_to(ROOT).as_posix()
def save(p,x):
    t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8')
    for i in range(40):
        try: os.replace(t,p);return
        except OSError:
            if i==39: raise
            time.sleep(.15)
ap=argparse.ArgumentParser();ap.add_argument('--resource',required=True);args=ap.parse_args()
resource=read(ROOT/args.resource)
assert (datetime.now(timezone.utc)-datetime.fromisoformat(resource['observedAt'].replace('Z','+00:00'))).total_seconds()<240
assert resource['ownHeavyJobs']==0 and resource['cpuLoadPercent']<85 and resource['freePhysicalMemoryKiB']>8_000_000
assert not any(p.exists() for p in [STATE,LOG,DEST]),'Inspect existing execution; never repeat completed ASR.'
tts=read(BASE/'fresh-guides-tts-execution-v4.json')
assert tts['exitCode']==0 and tts['generationComplete'] and tts['actualExitObserved'] and len(tts['results'])==3
restored=read(BASE/'fresh-guides-research-resume-verification-v4.json')
assert restored['restorationVerified'] and restored['ownedCoordinatorClosed'] and restored['ttsLeaseToken']==tts['leaseToken']
request=read(BASE/'fresh-guides-tts-request-v4.json')
for x in request['protectedInputs']: assert sha(ROOT/x['path'])==x['sha256'],x['path']
script=read(ROOT/'projects/similar-game-design/script/fresh-observation-guides.ko.v4.json')
assert len(script['scenes'])==3 and sum(len(x['lines']) for x in script['scenes'])==6
subprocess.run(['C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe',
 'scripts/review-video-duplicates.cjs','similar-game-design','--check'],cwd=ROOT,check=True)
for k in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','NUMEXPR_NUM_THREADS']: os.environ[k]='2'
os.environ.update(CUDA_VISIBLE_DEVICES='',TOKENIZERS_PARALLELISM='false',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
if os.name=='nt': ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x00004000)
import psutil
me=psutil.Process();DEST.mkdir()
state=dict(schemaVersion=1,slug='similar-game-design',pid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),
 sessionId=None,startedAt=now(),status='loading-three-fresh-guides-CPU2-ASR',cpuThreads=2,gpuJobs=0,cpuJobs=1,
 completed=0,total=6,resource=resource,ttsExecutionSha256=sha(BASE/'fresh-guides-tts-execution-v4.json'),
 requestSha256=sha(BASE/'fresh-guides-tts-request-v4.json'),exitCode=None,automaticApproval=False,
 original13Retranscribed=False,earlier8GuidesRetranscribed=False,narrationApproved=False,finalMixedAsrApproved=False,
 humanListening='pending',humanPronunciation='pending')
def checkpoint():
    if SESSION.exists():
        launch=read(SESSION)
        if launch.get('pid')==me.pid: state['sessionId']=launch['sessionId']
    state['updatedAt']=now();save(STATE,state)
    job=dict(status=state['status'],pid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),sessionId=state['sessionId'],
     state=rel(STATE),log=rel(LOG),completed=state['completed'],total=6,cpuThreads=2,gpu=0,
     singleJob=True,workerExpectedRunning=state['exitCode'] is None,exitCode=state['exitCode'])
    cp=read(BASE/'latest-checkpoint.json');cp.update(recordedAt=now(),stage='three-fresh-guides-whole-and-independent-CPU-ASR',
     ownedJob=job,nextAction='Read all six expected/actual complete texts and word boundaries. Preserve original13/current joined04/earlier8 PCM and finished ASR. Measure exact source allocation before final 60fps spatial/caption/mix/pair QA.',asrApproved=False,finalMixedAsrApproved=False)
    save(BASE/'latest-checkpoint.json',cp)
    qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json'
    for _ in range(8):
        raw=qp.read_text('utf-8-sig');q=json.loads(raw);item=next(x for x in q['items'] if x['slug']=='similar-game-design')
        item.update(stage=cp['stage'],currentExecution=job,nextAction=cp['nextAction']);q.update(updatedAt=now(),lastProgressAt=now())
        if qp.read_text('utf-8-sig')==raw: save(qp,q);break
        time.sleep(.15)
    else: raise RuntimeError('Concurrent queue mutation; preserve foreign writes.')
class Tee:
    def __init__(self,out,file):self.out=out;self.file=file
    def write(self,s):self.out.write(s);self.out.flush();self.file.write(s);self.file.flush();return len(s)
    def flush(self):self.out.flush();self.file.flush()
sys.stdout.reconfigure(encoding='utf-8');sys.stderr.reconfigure(encoding='utf-8');out,err=sys.stdout,sys.stderr
with LOG.open('x',encoding='utf-8') as log:
    sys.stdout=Tee(out,log);sys.stderr=sys.stdout
    try:
        checkpoint();inputs=[]
        for scene in script['scenes']:
            m=next(x for x in tts['results'] if x['id']==scene['id']);source=ROOT/m['path'];assert sha(source)==m['sha256']
            inputs.append(dict(id=scene['id']+'-whole',sceneId=scene['id'],mode='whole',sourcePath=m['path'],sourceSha256=m['sha256'],
                expectedKo=scene['lines'],sourceSamples=m['samples'],seconds=m['seconds']))
        audio_dir=ROOT/'shared/output/similar-game-design/research/fresh-guides-contexts-v4'
        assert not audio_dir.exists();audio_dir.mkdir(parents=True)
        for row in list(inputs):
            with wave.open(str(ROOT/row['sourcePath']),'rb') as w:
                params=w.getparams();assert (params.framerate,params.nchannels,params.sampwidth)==(24000,1,2)
                assert w.getnframes()==row['sourceSamples'];pcm=w.readframes(w.getnframes())
            pad=9600;target=audio_dir/(row['sceneId']+'-complete-independent.wav');padded=b'\0\0'*pad+pcm+b'\0\0'*pad
            with wave.open(str(target),'wb') as w:w.setparams(params);w.writeframes(padded)
            with wave.open(str(target),'rb') as w:assert w.readframes(w.getnframes())==padded
            inputs.append({**row,'id':row['sceneId']+'-complete-independent','mode':'complete-independent',
              'contextPath':rel(target),'contextSha256':sha(target),'startSample':0,'endSample':row['sourceSamples'],
              'zeroPaddingSamplesEachSide':pad,'exactSourceSampleBytesMatched':True,'pcmSha256':hashlib.sha256(pcm).hexdigest()})
        save(DEST/'pcm-contexts.json',dict(createdAt=now(),inputs=inputs));state['audioInputs']=inputs;checkpoint()
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
            state['status']='transcribing-'+row['id'];checkpoint();audio_path=ROOT/row.get('contextPath',row['sourcePath'])
            audio_sha=row.get('contextSha256',row['sourceSha256']);assert sha(audio_path)==audio_sha
            raw=transcriber(str(audio_path),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
            result={**row,'text':raw['text'],'words':raw['chunks'],'audioSha256':audio_sha,
                    'expectedWasRecognizerPrompt':False,'directReview':False,'approved':False}
            assert sha(audio_path)==audio_sha;results.append(result);save(DEST/(row['id']+'.json'),result)
            save(DEST/'asr.json',dict(complete=len(results)==6,results=results,automaticApproval=False,
              humanListening='pending',humanPronunciation='pending'))
            state['completed']=len(results);checkpoint();print(json.dumps(dict(id=row['id'],text=result['text']),ensure_ascii=False),flush=True)
        state.update(status='closed-three-fresh-guides-ASR-awaiting-direct-review',exitCode=0,cpuJobs=0,finishedAt=now());checkpoint()
    except BaseException:
        state.update(status='closed-three-fresh-guides-ASR-failed',exitCode=1,cpuJobs=0,finishedAt=now(),error=traceback.format_exc());checkpoint();traceback.print_exc();raise
    finally:sys.stdout=out;sys.stderr=err
