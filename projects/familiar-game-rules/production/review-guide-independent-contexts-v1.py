"""One CPU worker: exact current PCM slices, complete contexts, no expected prompt."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, os, sys, time, traceback, wave

ROOT=Path(__file__).resolve().parents[3]
BASE=Path(__file__).resolve().parent
PROOF=ROOT/'production/batches/sakurai-planning-game-design/proof-familiar-game-rules'
STATE=BASE/'observation-guides-independent-asr-execution-v1.json'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
now=lambda:datetime.now(timezone.utc).isoformat()
def write(p,d):
    tmp=p.with_name(p.name+f'.{os.getpid()}.writing')
    tmp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for n in range(40):
        try:os.replace(tmp,p);return
        except OSError:
            if n==39:raise
            time.sleep(.15)

parser=argparse.ArgumentParser();parser.add_argument('--resource',required=True);args=parser.parse_args()
resource=read(ROOT/args.resource)
assert (datetime.now(timezone.utc)-datetime.fromisoformat(resource['observedAt'].replace('Z','+00:00'))).total_seconds()<240
assert resource['ownHeavyJobs']==0 and resource['cpuLoadPercent']<=85
assert not STATE.exists(), 'Read actual execution/caches; never repeat existing worker'
whole=read(BASE/'observation-guides-whole-asr-execution-v2.json')
assert whole['exitCode']==0 and whole['actualExitObserved'] and whole['wholeDirectReview']
plan=read(BASE/'observation-guides-independent-context-plan-v1.json')
assert plan['contextCount']==10 and sha(ROOT/plan['wholeReview'])==plan['wholeReviewSha256']
assert read(ROOT/plan['wholeReview'])['wholeDirectReview']
dest=BASE/'observation-guides-independent-asr-v1'
audio=ROOT/'shared/output/familiar-game-rules/research/observation-guides-independent-asr-v1'
assert not dest.exists() and not audio.exists()
dest.mkdir();audio.mkdir(parents=True)
state=dict(schemaVersion=1,slug='familiar-game-rules',pid=os.getpid(),commandLine=[sys.executable,*sys.argv],startedAt=now(),
           status='extracting10exact-PCM-contexts',cpuThreads=2,gpuJobs=0,resourceObservation=resource,
           totalContexts=10,completed=0,exitCode=None,automaticApproval=False,directReview=False,
           asrApproved=False,narrationApproved=False,humanWholeListening='pending',pronunciation='pending',
           plan=rel(BASE/'observation-guides-independent-context-plan-v1.json'),planSha256=sha(BASE/'observation-guides-independent-context-plan-v1.json'))
def checkpoint():
    sp=STATE.with_name(STATE.stem+'.session.json')
    if sp.exists():
        session=read(sp)
        if session.get('pid')==os.getpid():state['sessionId']=session['sessionId']
    state['updatedAt']=now();write(STATE,state)
    qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qp)
    item=next(x for x in q['items'] if x['slug']=='familiar-game-rules')
    if item.get('execution',{}).get('pid')!=os.getpid():item.setdefault('executionHistory',[]).append(item.get('execution',{}))
    running=state['exitCode'] is None
    item.update(stage='newguide10-independent-CPU-ASR-awaiting-direct-review',updatedAt=state['updatedAt'],
                execution=dict(pid=os.getpid(),commandLine=[sys.executable,*sys.argv],sessionId=state.get('sessionId'),alive=running,
                    state=rel(STATE),log=rel(BASE/'observation-guides-independent-asr-v1.log'),status=state['status'],cpuThreads=2,gpuJobs=0,
                    completed=state['completed'],total=10,activeTasks=['newguide10-independent-CPU-ASR'] if running else []),
                nextAction='Observe actual single CPU worker; after exit directly compare all10complete newguide contexts with8guide whole results and exact current PCM. Keep pronunciation/listening pending and approvals false until direct review; then byte-exact original-guide joins, word/action alignment and final literal-caption pixels.')
    item['checkpoints']['narration']=False;write(qp,q)
    for p in [BASE/'latest-checkpoint.json',PROOF/'latest-checkpoint.json']:
        d=read(p)
        for k in ['stage','updatedAt','execution','nextAction']:d[k]=item[k]
        d.update(asrApproved=False,narrationApproved=False,finalRatioApproved=False);write(p,d)

try:
    checkpoint();slices=[]
    for c in plan['contexts']:
        src=ROOT/c['sourcePath'];assert sha(src)==c['sourceSha256']
        with wave.open(str(src),'rb') as w:
            params=w.getparams();assert params.framerate==24000 and params.nchannels==1 and params.sampwidth==2
            a,b=c['startSample'],c['endSample'];assert 0<=a<b<=w.getnframes()
            w.setpos(a);pcm=w.readframes(b-a);assert len(pcm)==(b-a)*2
        target=audio/(c['id']+'.wav')
        with wave.open(str(target),'wb') as out:
            out.setparams(params);out.writeframes(pcm)
        with wave.open(str(target),'rb') as out:assert out.readframes(out.getnframes())==pcm
        slices.append({**c,'contextPath':rel(target),'contextSha256':sha(target),'pcmSha256':hashlib.sha256(pcm).hexdigest(),'exactSourceSampleBytesMatched':True})
    write(dest/'pcm-slices.json',dict(createdAt=now(),slices=slices))
    import torch
    from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
    torch.set_num_threads(2)
    mp=ROOT/'qwen3-tts/models/whisper-large-v3-turbo'
    model=AutoModelForSpeechSeq2Seq.from_pretrained(str(mp),dtype=torch.float32,low_cpu_mem_usage=True,
        use_safetensors=True,attn_implementation='eager',local_files_only=True).to('cpu')
    processor=AutoProcessor.from_pretrained(str(mp),local_files_only=True)
    transcriber=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,
        feature_extractor=processor.feature_extractor,dtype=torch.float32,device='cpu')
    results=[]
    for c in slices:
        state['status']='transcribing-independent-'+c['id'];checkpoint()
        raw=transcriber(str(ROOT/c['contextPath']),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
        row={**c,'text':raw['text'],'words':raw['chunks'],'expectedWasRecognizerPrompt':False,'directReview':False,'approved':False}
        assert sha(ROOT/c['contextPath'])==c['contextSha256']
        results.append(row);write(dest/(c['id']+'.json'),row)
        write(dest/'asr.json',dict(complete=len(results)==10,results=results,automaticApproval=False,humanWholeListening='pending'))
        state['completed']=len(results);checkpoint()
        print(json.dumps(dict(context=c['id'],text=row['text']),ensure_ascii=False),flush=True)
    state.update(status='closed-newguide10-independent-ASR-awaiting-direct-review',exitCode=0,endedAt=now());checkpoint()
except BaseException:
    state.update(status='closed-newguide10-independent-ASR-failed',exitCode=1,endedAt=now(),error=traceback.format_exc());checkpoint();raise
