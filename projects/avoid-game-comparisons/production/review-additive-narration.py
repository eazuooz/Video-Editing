"""CPU full readback of new13/14, or separately requested ambiguous contexts."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,subprocess,sys,traceback
import soundfile as sf
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
PROOF=ROOT/'production/batches/sakurai-planning-game-design/proof-avoid-game-comparisons';QUEUE=PROOF.parent/'queue.json'
PREFIX=sys.argv[1] if len(sys.argv)>1 else 'additive-whole'
assert PREFIX in ['additive-whole','additive-context']
STATE=BASE/f'{PREFIX}-asr-execution.json';LOG=BASE/f'{PREFIX}-asr.log'
def now():return datetime.now(timezone.utc).isoformat()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text('utf-8-sig'))
def save(p,d):
    t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');t.replace(p)
assert not STATE.exists(),'Read the existing state instead of repeating it.'
tts=read(BASE/'additive-narration-tts-execution.json');assert tts['generationComplete'] and tts['exitCode']==0
request=read(BASE/'additive-narration-request.json')
if PREFIX=='additive-whole':
    contexts=[dict(id=x['id'],audioPath=x['path'],audioSha256=x['sha256'],fromSeconds=0,toSeconds=x['seconds'],expectedKo=x['text']) for x in tts['results']]
else:contexts=read(BASE/'additive-context-readback-request.json')['contexts']
for x in request['protectedInputs']:assert sha(ROOT/x['path'])==x['sha256'],x['path']
for x in contexts:assert sha(ROOT/x['audioPath'])==x['audioSha256']
state=dict(schemaVersion=1,pid=os.getpid(),sessionId=None,startedAt=now(),status='loading-local-whisper-on-CPU',device='cpu',cpuJobs=1,gpuJobs=0,log=LOG.relative_to(ROOT).as_posix(),results=[],readbackComplete=False,directWholeScriptReview=False,humanWholeListening='pending',narrationApproved=False)
def checkpoint():
    launch=BASE/f'{PREFIX}-asr-session.json'
    if launch.exists():
        x=read(launch)
        if x['pid']==os.getpid():state['sessionId']=x['sessionId']
    state['updatedAt']=now();save(STATE,state)
    q=read(QUEUE);task=next(x for x in q['items'] if x['slug']=='avoid-game-comparisons');ex=dict(task.get('execution',{}))
    ex.update(observedAt=now(),phase=PREFIX+'-current-hash-CPU-ASR',status=state['status'],pid=os.getpid(),sessionId=state['sessionId'],alive=bool(state['cpuJobs']),cpuProductionJobs=state['cpuJobs'],primaryCpuProductionJobs=state['cpuJobs'],gpuSynthesisJobs=0,renderJobs=0,uploads=0,state=STATE.relative_to(ROOT).as_posix(),log=state['log'],activeTasks=[] if not state['cpuJobs'] else [{'kind':PREFIX+'-CPU-ASR','pid':os.getpid(),'sessionId':state['sessionId']}])
    task.update(stage=PREFIX+'-ASR-direct-review-pending',execution=ex,updatedAt=now(),nextAction='Directly compare all new6 paragraphs and independent ambiguous readbacks; preserve original12 reviewed PCM. Final timing, fixed-caption/native framing, mix, render, QA, collection and private save are pending.')
    task.setdefault('additiveNarration',{}).update(generationComplete=True,wholeNewAsrDirectReview=False,readbackState=STATE.relative_to(ROOT).as_posix(),readbackComplete=state['readbackComplete'])
    q.update(updatedAt=now(),lastProgressAt=now());save(QUEUE,q)
    for p in [BASE/'latest-checkpoint.json',PROOF/'latest-checkpoint.json']:
        d=read(p)
        for key in ['stage','execution','updatedAt','nextAction','additiveNarration']:d[key]=task[key]
        save(p,d)
checkpoint();original_out=sys.stdout;original_err=sys.stderr
class Tee:
    def __init__(self,f):self.f=f
    def write(self,s):original_out.write(s);original_out.flush();self.f.write(s);self.f.flush();return len(s)
    def flush(self):original_out.flush();self.f.flush()
with LOG.open('a',encoding='utf-8') as log:
    sys.stdout=Tee(log);sys.stderr=sys.stdout
    try:
        import torch
        from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
        torch.set_num_threads(2);model_path=ROOT/'qwen3-tts/models/whisper-large-v3-turbo'
        model=AutoModelForSpeechSeq2Seq.from_pretrained(str(model_path),dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager',local_files_only=True).to('cpu')
        processor=AutoProcessor.from_pretrained(str(model_path),local_files_only=True)
        transcriber=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float32,device='cpu')
        folder=BASE/(PREFIX+'-asr-local');folder.mkdir(exist_ok=True)
        for context in contexts:
            p=ROOT/context['audioPath'];assert sha(p)==context['audioSha256'];audio,rate=sf.read(p,dtype='float32',always_2d=True)
            a=round(context['fromSeconds']*rate);z=min(len(audio),round(context['toSeconds']*rate));assert 0<=a<z
            wav=folder/(context['id']+'.wav');sf.write(wav,audio[a:z],rate,subtype='PCM_16')
            state['status']='transcribing-'+context['id'];checkpoint();print('Transcribing '+context['id'],flush=True)
            raw=transcriber(str(wav),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
            result={**context,'actualFromSeconds':a/rate,'actualToSeconds':z/rate,'text':raw['text'],'words':raw['chunks'],'expectedWasRecognizerPrompt':False,'directReview':False}
            save(folder/(context['id']+'.json'),result);state['results'].append(result);checkpoint();print(raw['text'],flush=True)
        for x in request['protectedInputs']:assert sha(ROOT/x['path'])==x['sha256'],x['path']
        state.update(status='readback-complete-awaiting-direct-text-and-context-review',cpuJobs=0,readbackComplete=True,endedAt=now(),exitCode=0);checkpoint();print('Readback evidence complete; direct review is separate.',flush=True)
    except BaseException:
        state.update(status='failed',cpuJobs=0,endedAt=now(),exitCode=1,error=traceback.format_exc());checkpoint();traceback.print_exc();raise
    finally:sys.stdout=original_out;sys.stderr=original_err
