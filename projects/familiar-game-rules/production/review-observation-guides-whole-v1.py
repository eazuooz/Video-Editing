"""Single CPU2 whole readback of only8new guide PCM; no expected recognizer prompt."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os,sys,time,traceback
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
PROOF=ROOT/'production/batches/sakurai-planning-game-design/proof-familiar-game-rules'
STATE=BASE/'observation-guides-whole-asr-execution-v1.json'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
now=lambda:datetime.now(timezone.utc).isoformat()
def save(p,d):
    p.parent.mkdir(parents=True,exist_ok=True);t=p.with_name(p.name+f'.{os.getpid()}.writing')
    t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for n in range(40):
        try:os.replace(t,p);return
        except OSError:
            if n==39:raise
            time.sleep(.15)
parser=argparse.ArgumentParser();parser.add_argument('--resource',required=True);args=parser.parse_args()
assert not STATE.exists(), 'Read actual existing worker/caches; never repeat whole guide ASR'
resource=read(ROOT/args.resource)
assert (datetime.now(timezone.utc)-datetime.fromisoformat(resource['observedAt'].replace('Z','+00:00'))).total_seconds()<240
assert resource['ownHeavyJobs']==0 and resource['cpuLoadPercent']<=85
tts=read(BASE/'observation-guide-tts-execution-v1.json')
assert tts['generationComplete'] and tts['exitCode']==0 and tts['actualExitObserved'] and len(tts['results'])==8
request=read(BASE/'observation-guide-tts-request-v1.json');assert sha(BASE/'observation-guide-tts-request-v1.json')==tts['requestSha256']
for x in request['protectedInputs']:assert sha(ROOT/x['path'])==x['sha256'],x['path']
for r in tts['results']:assert sha(ROOT/r['path'])==r['sha256'],r['id']
dest=BASE/'observation-guides-whole-asr-v1';assert not dest.exists();dest.mkdir()
state=dict(schemaVersion=1,slug='familiar-game-rules',pid=os.getpid(),sessionId=None,commandLine=[sys.executable,*sys.argv],startedAt=now(),
 status='loading-local-CPU-whisper-for8newguides',cpuThreads=2,gpuJobs=0,resourceObservation=resource,total=8,completed=0,exitCode=None,
 expectedWasRecognizerPrompt=False,automaticApproval=False,wholeDirectReview=False,independentContextReview=False,
 humanWholeListening='pending',pronunciation='pending',audioInputs=tts['results'],ttsExecution=rel(BASE/'observation-guide-tts-execution-v1.json'),
 ttsExecutionSha256=sha(BASE/'observation-guide-tts-execution-v1.json'),original11WholeAsrRepeated=False)
def checkpoint():
    sp=BASE/'observation-guides-whole-asr-session-v1.json'
    if sp.exists():
        s=read(sp)
        if s['pid']==os.getpid():state['sessionId']=s['sessionId']
    state['updatedAt']=now();save(STATE,state)
    qp=PROOF.parent/'queue.json';q=read(qp);item=next(x for x in q['items'] if x['slug']=='familiar-game-rules')
    if item.get('execution',{}).get('pid')!=os.getpid():item.setdefault('executionHistory',[]).append(item.get('execution',{}))
    running=state['exitCode'] is None
    item.update(stage='only8newguide-whole-CPU-ASR-awaiting-direct-review',updatedAt=state['updatedAt'],
        execution=dict(pid=os.getpid(),commandLine=state['commandLine'],sessionId=state['sessionId'],alive=running,
        state=rel(STATE),log=rel(BASE/'observation-guides-whole-asr-v1.log'),status=state['status'],cpuThreads=2,gpuJobs=0,
        completed=state['completed'],total=8,activeTasks=['only8newguide-whole-CPU-ASR'] if running else []),
        nextAction='After actual exit, directly compare all8complete guide texts/words/ends to expected KOEN/currentPCM. Choose complete independent ending/ambiguous contexts from actual ASR/PCM; do not infer approval from endingheuristics. Preserve original11/46PCM and pending human listening/pronunciation.')
    item['checkpoints']['narration']=False;q.update(updatedAt=now(),lastProgressAt=now());save(qp,q)
    for p in [BASE/'latest-checkpoint.json',PROOF/'latest-checkpoint.json']:
        d=read(p)
        for k in ['stage','updatedAt','execution','nextAction']:d[k]=item[k]
        d.update(asrApproved=False,narrationApproved=False,finalRatioApproved=False);save(p,d)
try:
    checkpoint()
    import torch
    from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
    torch.set_num_threads(2);mp=ROOT/'qwen3-tts/models/whisper-large-v3-turbo'
    model=AutoModelForSpeechSeq2Seq.from_pretrained(str(mp),dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager',local_files_only=True).to('cpu')
    processor=AutoProcessor.from_pretrained(str(mp),local_files_only=True)
    transcriber=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float32,device='cpu')
    results=[]
    for pcm in tts['results']:
        g=next(g for g in request['guides'] if g['id']==pcm['id']);state['status']='transcribing-newguide-'+g['id'];checkpoint()
        raw=transcriber(str(ROOT/pcm['path']),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
        row=dict(id=g['id'],parentScene=g['parentScene'],audioPath=pcm['path'],audioSha256=pcm['sha256'],seconds=pcm['seconds'],
            expectedKo=g['ko'],expectedEn=g['en'],text=raw['text'],words=raw['chunks'],expectedWasRecognizerPrompt=False,directReview=False,approved=False)
        assert sha(ROOT/pcm['path'])==pcm['sha256']
        results.append(row);save(dest/(g['id']+'.json'),row)
        save(dest/'asr.json',dict(complete=len(results)==8,results=results,automaticApproval=False,humanWholeListening='pending'))
        state['completed']=len(results);checkpoint();print(json.dumps(dict(id=g['id'],text=row['text']),ensure_ascii=False),flush=True)
    state.update(status='closed8whole-newguide-ASR-awaiting-direct-and-context-review',exitCode=0,endedAt=now());checkpoint()
except BaseException:
    state.update(status='closed8whole-newguide-ASR-failed',exitCode=1,endedAt=now(),error=traceback.format_exc());checkpoint();raise
