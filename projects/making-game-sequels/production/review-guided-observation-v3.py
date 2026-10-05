"""Whole new-guide CPU ASR, without expected text supplied to the recognizer."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,sys,traceback
sys.stdout.reconfigure(encoding='utf-8');sys.stderr.reconfigure(encoding='utf-8')
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
PROOF=ROOT/'production/batches/sakurai-planning-game-design/proof-making-game-sequels'
STATE=BASE/'guided-observation-asr-execution-v3.json';LOG=BASE/'guided-observation-asr-v3.log'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def now():return datetime.now(timezone.utc).isoformat()
def save(p,d):
    tmp=p.with_name(p.name+f'.{os.getpid()}.writing');tmp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');tmp.replace(p)
assert not STATE.exists(),'Inspect actual results instead of repeating ASR.'
tts=read(BASE/'guided-observation-tts-execution-v3.json')
assert tts.get('exitCode')==0 and tts['generationComplete'] and len(tts['results'])==8
request=read(BASE/'guided-observation-tts-request-v3.json')
for x in request['protectedInputs']:assert sha(ROOT/x['path'])==x['sha256'],x['path']
state=dict(schemaVersion=1,pid=os.getpid(),sessionId=None,startedAt=now(),status='loading-Whisper-CPU',cpuJobs=1,gpuJobs=0,cpuThreads=2,results=[],readbackComplete=False,wholeDirectReview=False,expectedWasRecognizerPrompt=False,humanWholeListening='pending',humanPronunciation='pending',baselineCurrent13PcmChanged=False,log=LOG.relative_to(ROOT).as_posix())
def checkpoint():
    session=BASE/'guided-observation-asr-session-v3.json'
    if session.exists():
        s=read(session)
        if s.get('pid')==os.getpid():state['sessionId']=s['sessionId']
    state['updatedAt']=now();save(STATE,state)
    q=read(PROOF.parent/'queue.json');item=next(x for x in q['items'] if x['slug']=='making-game-sequels')
    item.update(stage='current13-new-guide-whole-ASR',updatedAt=now())
    ex=dict(item.get('execution',{}));ex.update(observedAt=now(),phase=item['stage'],status=state['status'],pid=os.getpid(),sessionId=state['sessionId'],alive=bool(state['cpuJobs']),commandLine='review-guided-observation-v3.py --CPU2',cpuProductionJobs=state['cpuJobs'],primaryCpuProductionJobs=state['cpuJobs'],gpuSynthesisJobs=0,renderJobs=0,uploads=0,state=STATE.relative_to(ROOT).as_posix(),log=state['log'],activeTasks=[] if not state['cpuJobs'] else [{'kind':'only-new-guides-whole-CPU-ASR','pid':os.getpid(),'sessionId':state['sessionId']}])
    item.update(execution=ex,guidedObservationAsr={'state':STATE.relative_to(ROOT).as_posix(),'guides':8,'readbacks':len(state['results']),'directReview':False},nextAction='Directly compare all8 new-guide readbacks and any ambiguous complete contexts; align new guide words with native cuts while retaining all509.624s current13 PCM. No final mix, timing, rendering, QA or private delivery yet.')
    q.update(updatedAt=now(),lastProgressAt=now());save(PROOF.parent/'queue.json',q)
    for p in [BASE/'latest-checkpoint.json',PROOF/'latest-checkpoint.json']:
        d=read(p)
        for k in ['stage','updatedAt','execution','guidedObservationAsr','nextAction']:d[k]=item[k]
        save(p,d)
checkpoint();original=sys.stdout
class Tee:
    def __init__(self,f):self.f=f
    def write(self,s):original.write(s);original.flush();self.f.write(s);self.f.flush();return len(s)
    def flush(self):original.flush();self.f.flush()
with LOG.open('a',encoding='utf-8') as log:
    sys.stdout=Tee(log);sys.stderr=sys.stdout
    try:
        import torch
        from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
        torch.set_num_threads(2)
        model_path=ROOT/'qwen3-tts/models/whisper-large-v3-turbo'
        model=AutoModelForSpeechSeq2Seq.from_pretrained(str(model_path),dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager',local_files_only=True).to('cpu')
        processor=AutoProcessor.from_pretrained(str(model_path),local_files_only=True)
        transcriber=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float32,device='cpu')
        out=BASE/'asr-guided-observation-local-v3';out.mkdir(exist_ok=True)
        for g in tts['results']:
            p=ROOT/g['path'];assert sha(p)==g['sha256']
            state['status']='transcribing-'+g['id'];checkpoint();print('Whole new guide '+g['id'],flush=True)
            raw=transcriber(str(p),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
            r=dict(id=g['id'],audioPath=g['path'],audioSha256=g['sha256'],samples=g['samples'],sampleRate=g['sampleRate'],seconds=g['seconds'],expectedKo=g['text'],text=raw['text'],words=raw['chunks'],expectedWasRecognizerPrompt=False,directReview=False)
            save(out/(g['id']+'.json'),r);state['results'].append(r);checkpoint();print(raw['text'],flush=True)
        for x in request['protectedInputs']:assert sha(ROOT/x['path'])==x['sha256'],x['path']
        state.update(status='whole-new-guides-finished-direct-comparison-pending',cpuJobs=0,readbackComplete=True,endedAt=now(),exitCode=0);checkpoint()
    except BaseException:
        state.update(status='failed',cpuJobs=0,endedAt=now(),exitCode=1,error=traceback.format_exc());checkpoint();traceback.print_exc();raise
    finally:sys.stdout=original;sys.stderr=original
