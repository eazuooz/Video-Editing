"""One CPU worker for current whole-scene readback; independent contexts follow direct review."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, os, sys, time, traceback

ROOT=Path(__file__).resolve().parents[3]
BASE=Path(__file__).resolve().parent
PROOF=ROOT/'production/batches/sakurai-planning-game-design/proof-familiar-game-rules'
STATE=BASE/'current-whole-asr-execution-v1.json'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
now=lambda:datetime.now(timezone.utc).isoformat()


def write(p,d):
    p.parent.mkdir(parents=True,exist_ok=True)
    tmp=p.with_name(p.name+f'.{os.getpid()}.writing')
    tmp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for n in range(40):
        try:os.replace(tmp,p);return
        except OSError:
            if n==39:raise
            time.sleep(.15)


parser=argparse.ArgumentParser()
parser.add_argument('--resource',required=True)
args=parser.parse_args()
resource=read(ROOT/args.resource)
assert (datetime.now(timezone.utc)-datetime.fromisoformat(resource['observedAt'].replace('Z','+00:00'))).total_seconds()<240
assert resource['ownHeavyJobs']==0 and resource['cpuLoadPercent']<=85
assert not STATE.exists(), 'Read actual execution/caches; never relaunch a completed ASR worker'
measurement=read(BASE/'current-narration-measurement-v1.json')
manifest=read(BASE.parent/'project.json')
script=read(ROOT/manifest['paths']['script'])
assert sha(ROOT/manifest['paths']['script'])==measurement['scriptSha256']
for m in measurement['measurements']:assert sha(ROOT/m['path'])==m['sha256']
dest=BASE/'current-whole-asr-v1'
assert not dest.exists()
dest.mkdir()
state=dict(schemaVersion=1,slug=manifest['slug'],pid=os.getpid(),commandLine=sys.argv,startedAt=now(),
           status='loading-local-CPU-whisper',cpuThreads=2,gpuJobs=0,resourceObservation=resource,
           totalScenes=11,completed=0,exitCode=None,automaticApproval=False,wholeDirectReview=False,
           independentContextReview=False,humanWholeListening='pending',pronunciation='pending',
           audioInputs=measurement['measurements'],scriptSha256=measurement['scriptSha256'])


def checkpoint():
    sp=STATE.with_name(STATE.stem+'.session.json')
    if sp.exists():
        session=read(sp)
        if session.get('pid')==os.getpid():state['sessionId']=session['sessionId']
    state['updatedAt']=now();write(STATE,state)
    qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qp)
    item=next(i for i in q['items'] if i['slug']==state['slug'])
    if item.get('execution',{}).get('pid')!=os.getpid():item.setdefault('executionHistory',[]).append(item.get('execution',{}))
    running=state['exitCode'] is None
    item.update(stage='current11-whole-CPU-ASR-awaiting-direct-review',updatedAt=state['updatedAt'],
                execution=dict(pid=os.getpid(),commandLine=sys.argv,sessionId=state.get('sessionId'),alive=running,
                    state=rel(STATE),log=rel(BASE/'current-whole-asr-v1.log'),status=state['status'],cpuThreads=2,gpuJobs=0,
                    completed=state['completed'],total=11,activeTasks=['current11-whole-CPU-ASR'] if running else []),
                nextAction='Directly compare all11 complete recognized texts/words against46 KO paragraphs; choose complete independent context boundaries from actual ASR/PCM, not estimated paragraph timings. Preserve pending pronunciation/human listening; no automatic approval.')
    item['checkpoints']['narration']=False
    write(qp,q)
    for p in [BASE/'latest-checkpoint.json',PROOF/'latest-checkpoint.json']:
        d=read(p)
        for k in ['stage','updatedAt','execution','nextAction']:d[k]=item[k]
        d.update(asrApproved=False,narrationApproved=False,finalRatioApproved=False)
        write(p,d)


try:
    checkpoint()
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
    for scene in script['scenes']:
        m=next(m for m in measurement['measurements'] if m['scene']==scene['id'])
        state['status']='transcribing-current-scene-'+scene['id'];checkpoint()
        raw=transcriber(str(ROOT/m['path']),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
        row=dict(scene=scene['id'],audioSha256=m['sha256'],expectedKo=scene['lines'],text=raw['text'],words=raw['chunks'],
                 expectedWasRecognizerPrompt=False,directReview=False,seconds=m['seconds'])
        assert sha(ROOT/m['path'])==m['sha256']
        results.append(row);write(dest/(scene['id']+'.json'),row)
        write(dest/'asr.json',dict(complete=len(results)==11,results=results,automaticApproval=False,humanWholeListening='pending'))
        state['completed']=len(results);checkpoint()
        print(json.dumps(dict(scene=scene['id'],text=row['text']),ensure_ascii=False),flush=True)
    state.update(status='closed-current11-whole-ASR-awaiting-direct-and-independent-review',exitCode=0,endedAt=now());checkpoint()
except BaseException:
    state.update(status='closed-current11-whole-ASR-failed',exitCode=1,endedAt=now(),error=traceback.format_exc());checkpoint();raise
