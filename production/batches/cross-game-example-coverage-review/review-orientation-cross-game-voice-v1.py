"""One CPU2/current-hash ASR job; expected words are never recognizer prompts."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, ctypes, hashlib, json, os, subprocess, sys, traceback, wave
for key in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','NUMEXPR_NUM_THREADS']:
    os.environ[key]='2'
os.environ.update(CUDA_VISIBLE_DEVICES='',TOKENIZERS_PARALLELISM='false',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
import psutil
ROOT=Path(__file__).resolve().parents[3]
B=Path(__file__).resolve().parent
R=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
now=lambda:datetime.now(timezone.utc).isoformat()
def rel(p):return p.resolve().relative_to(ROOT).as_posix()
def save(p,o):
    temp=p.with_name(p.name+f'.{os.getpid()}.writing')
    temp.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(temp,p)

ap=argparse.ArgumentParser();ap.add_argument('--resource',required=True)
ap.add_argument('--mode',choices=['whole','contexts'],required=True);args=ap.parse_args()
statepath=R/f'cross-game-{args.mode}-asr-execution-v1.json'
sessionpath=statepath.with_name(statepath.stem+'.session.json')
dest=R/f'cross-game-{args.mode}-asr-v1';logpath=R/f'cross-game-{args.mode}-asr-v1.log'
assert not statepath.exists() and not dest.exists() and not logpath.exists(), 'Inspect existing results; no repeated model job.'
resource=read(ROOT/args.resource)
assert (datetime.now(timezone.utc)-datetime.fromisoformat(resource['observedAt'])).total_seconds()<240
assert resource['ownHeavyJobs']==0 and resource['cpuLoadPercent']<85
assert resource['freePhysicalMemoryKiB']>8_000_000
tts=read(R/'narration-cross-game-repair-execution-v1.json');resume=read(R/'cross-game-repair-voice-closure-verification-v1.json')
assert tts['exitCode']==0 and tts['generationComplete'] and tts['actualExitObserved']
assert tts['actualOuterSession']==read(R/'narration-cross-game-repair-session-v1.json')['sessionId'] and len(tts['results'])==5
assert resume['restorationVerified'] and resume['leaseToken']==tts['leaseToken']
for row in tts['protectedInputs']+tts['results']:assert sha(ROOT/row['path'])==row['sha256'],row['path']
script=read(R/'script/cross-game-repair-batch.ko.json');english=read(R/'script/cross-game-repair-batch.en.json')
assert len(script['scenes'])==5 and sum(len(x['lines']) for x in script['scenes'])==19
inputs=[]
if args.mode=='whole':
    for scene in script['scenes']:
        audio=next(x for x in tts['results'] if x['id']==scene['id'])
        inputs.append(dict(id=scene['id'],sourcePath=audio['path'],sourceSha256=audio['sha256'],
            sourceSamples=audio['samples'],seconds=audio['seconds'],expectedKo=scene['lines']))
else:
    whole=read(R/'cross-game-whole-asr-execution-v1.json')
    assert whole['exitCode']==0 and whole['actualExitObserved']
    plan=read(R/'cross-game-independent-context-plan-v1.json')
    review=read(ROOT/plan['wholeReview'])
    assert sha(ROOT/plan['wholeReview'])==plan['wholeReviewSha256']
    assert review['allWholeTextsDirectlyCompared'] and plan['boundariesDirectlyComparedWithCurrentWordsAndPCM']
    assert len(plan['contexts'])==19
    inputs=plan['contexts']
if os.name=='nt':ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x00004000)
dest.mkdir();me=psutil.Process()
state=dict(schemaVersion=1,slug='game-math-orientation-matrices',mode=args.mode,pid=me.pid,createTime=me.create_time(),
    commandLine=me.cmdline(),cwd=me.cwd(),sessionId=None,startedAt=now(),status='loading-current-CPU2-whisper',
    cpuThreads=2,cpuJobs=1,gpuJobs=0,total=len(inputs),completed=0,results=[],resource=resource,
    koSha256=sha(R/'script/cross-game-repair-batch.ko.json'),enSha256=sha(R/'script/cross-game-repair-batch.en.json'),
    audioInputs=inputs,exitCode=None,automaticApproval=False,directReview=False,
    finalMixedAsrApproved=False,humanListeningApproved=False,humanPronunciationApproved=False,
    baselinePcmRegenerated=0,scope='Authorized additive revision of existing delivered video; current inventory refresh remains a separate gate.')
def checkpoint():
    if sessionpath.exists():
        session=read(sessionpath)
        assert session['pid']==me.pid and abs(session['createTime']-me.create_time())<.01
        state['sessionId']=session['sessionId']
    state['updatedAt']=now();save(statepath,state)
    cp=read(R/'latest-checkpoint.json')
    cp.update(recordedAt=now(),stage=f'cross-game-{args.mode}-current-CPU-ASR',
        ownedJob=dict(pid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),cwd=me.cwd(),
            sessionId=state['sessionId'],state=rel(statepath),log=rel(logpath),completed=state['completed'],
            total=state['total'],cpuThreads=2,gpuJobs=0,exitCode=state['exitCode']),
        currentUnmixedAsrApproved=False,activeOwnedWorkers=state['cpuJobs'],
        next='Read every whole/complete independent recognized text against current PCM; preserve original24PCM. New moving annotations, full mix ASR, exact ratio and final cues remain pending.')
    save(R/'latest-checkpoint.json',cp)
    qp=B/'queue.json';raw=qp.read_text('utf-8-sig');q=json.loads(raw)
    q['currentOrientationReview'].update(stage=cp['stage'],ownedJob=cp['ownedJob'],activeOwnedWorkers=1 if state['cpuJobs'] else 0,next=cp['next'])
    q['updatedAt']=now();assert qp.read_text('utf-8-sig')==raw,'Preserve a concurrent queue update.';save(qp,q)
class Tee:
    def __init__(self,out,file):self.out=out;self.file=file
    def write(self,s):self.out.write(s);self.out.flush();self.file.write(s);self.file.flush();return len(s)
    def flush(self):self.out.flush();self.file.flush()
with logpath.open('x',encoding='utf-8') as log:
    oldout,olderr=sys.stdout,sys.stderr;sys.stdout=Tee(oldout,log);sys.stderr=sys.stdout
    try:
        checkpoint()
        if args.mode=='contexts':
            audiofolder=ROOT/'shared/output/cross-game-example-coverage-review/orientation/cross-game-contexts-v1'
            audiofolder.mkdir(parents=True,exist_ok=False);sliced=[]
            for row in inputs:
                source=ROOT/row['sourcePath'];assert sha(source)==row['sourceSha256']
                with wave.open(str(source),'rb') as wav:
                    params=wav.getparams();assert params.framerate==24000 and params.nchannels==1 and params.sampwidth==2
                    a,b=row['startSample'],row['endSample'];assert 0<=a<b<=wav.getnframes()
                    wav.setpos(a);pcm=wav.readframes(b-a);assert len(pcm)==(b-a)*2
                pad=row.get('zeroPaddingSamplesEachSide',7200);data=b'\x00\x00'*pad+pcm+b'\x00\x00'*pad
                p=audiofolder/(row['id']+'.wav')
                with wave.open(str(p),'wb') as wav:wav.setparams(params);wav.writeframes(data)
                with wave.open(str(p),'rb') as wav:assert wav.readframes(wav.getnframes())==data
                sliced.append({**row,'contextPath':rel(p),'contextSha256':sha(p),
                    'pcmSha256':hashlib.sha256(pcm).hexdigest(),'exactSourceSampleBytesMatched':True})
            inputs=sliced;save(dest/'pcm-slices.json',dict(slices=sliced,createdAt=now()))
        import torch
        from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
        torch.set_num_threads(2);torch.set_num_interop_threads(1)
        modelpath=ROOT/'qwen3-tts/models/whisper-large-v3-turbo'
        model=AutoModelForSpeechSeq2Seq.from_pretrained(str(modelpath),dtype=torch.float32,
            low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager',local_files_only=True).to('cpu')
        processor=AutoProcessor.from_pretrained(str(modelpath),local_files_only=True)
        transcriber=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,
            feature_extractor=processor.feature_extractor,dtype=torch.float32,device='cpu')
        for row in inputs:
            state['status']='transcribing-current-'+row['id'];checkpoint()
            p=ROOT/row.get('contextPath',row['sourcePath']);digest=row.get('contextSha256',row['sourceSha256'])
            assert sha(p)==digest
            raw=transcriber(str(p),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
            result={**row,'text':raw['text'],'words':raw['chunks'],'audioSha256':digest,
                'expectedWasRecognizerPrompt':False,'directReview':False,'approved':False}
            assert sha(p)==digest;state['results'].append(result);save(dest/(row['id']+'.json'),result)
            state['completed']=len(state['results']);save(dest/'asr.json',dict(complete=state['completed']==len(inputs),results=state['results'],automaticApproval=False))
            checkpoint();print(json.dumps(dict(id=row['id'],text=result['text']),ensure_ascii=False),flush=True)
        for row in tts['protectedInputs']+tts['results']:assert sha(ROOT/row['path'])==row['sha256'],row['path']
        state.update(status='closed-awaiting-direct-current-ASR-review',exitCode=0,cpuJobs=0,finishedAt=now());checkpoint()
    except BaseException:
        state.update(status='failed-preserve-current-ASR',exitCode=1,cpuJobs=0,error=traceback.format_exc(),finishedAt=now());checkpoint();raise
    finally:sys.stdout,sys.stderr=oldout,olderr
