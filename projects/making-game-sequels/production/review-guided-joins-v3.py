"""Whole complete-sentence readbacks across the8 new guide joins in6 contexts."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,sys,traceback
import soundfile as sf
sys.stdout.reconfigure(encoding='utf-8');sys.stderr.reconfigure(encoding='utf-8')
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
PROOF=ROOT/'production/batches/sakurai-planning-game-design/proof-making-game-sequels'
STATE=BASE/'guided-joins-asr-execution-v3.json'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
now=lambda:datetime.now(timezone.utc).isoformat()
def save(p,d):
    tmp=p.with_name(p.name+f'.{os.getpid()}.writing');tmp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');tmp.replace(p)
assert not STATE.exists(),'Inspect completed/current guide joins instead of repeating.'
request=read(BASE/'guided-joins-readback-request-v3.json')
for p in request['protectedInputs']:assert sha(ROOT/p['path'])==p['sha256']
state=dict(schemaVersion=1,pid=os.getpid(),sessionId=None,startedAt=now(),status='loading-CPU-Whisper',cpuJobs=1,cpuThreads=2,gpuJobs=0,results=[],directReview=False,expectedWasRecognizerPrompt=False,finalMixBuilt=False)
def checkpoint():
    session=BASE/'guided-joins-asr-session-v3.json'
    if session.exists() and read(session)['pid']==os.getpid():state['sessionId']=read(session)['sessionId']
    state['updatedAt']=now();save(STATE,state)
    q=read(PROOF.parent/'queue.json');i=next(x for x in q['items'] if x['slug']=='making-game-sequels')
    i.update(stage='current13-guided60-complete-new-join-context-ASR',updatedAt=now(),nextAction='Directly compare all6 complete current candidate guide contexts and changed native/caption pixels. Final timing/body ratio/full mixed13 ASR/render/QA/private delivery remain pending.')
    i['execution']={**i.get('execution',{}),'phase':i['stage'],'status':state['status'],'pid':os.getpid(),'sessionId':state['sessionId'],'alive':bool(state['cpuJobs']),'commandLine':'review-guided-joins-v3.py CPU2','state':STATE.relative_to(ROOT).as_posix(),'cpuProductionJobs':state['cpuJobs'],'primaryCpuProductionJobs':state['cpuJobs'],'gpuSynthesisJobs':0,'renderJobs':0,'uploads':0,'observedAt':now(),'activeTasks':[] if not state['cpuJobs'] else [{'kind':'complete-new-guide-join-ASR','pid':os.getpid(),'sessionId':state['sessionId']}]}
    q['updatedAt']=now();save(PROOF.parent/'queue.json',q)
    for p in [BASE/'latest-checkpoint.json',PROOF/'latest-checkpoint.json']:
        d=read(p)
        for k in ['stage','updatedAt','nextAction','execution']:d[k]=i[k]
        save(p,d)
checkpoint()
try:
    import torch
    from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
    torch.set_num_threads(2);mp=ROOT/'qwen3-tts/models/whisper-large-v3-turbo'
    model=AutoModelForSpeechSeq2Seq.from_pretrained(str(mp),dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager',local_files_only=True).to('cpu')
    processor=AutoProcessor.from_pretrained(str(mp),local_files_only=True)
    transcriber=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float32,device='cpu')
    out=BASE/'asr-guided-joins-local-v3';out.mkdir()
    for c in request['contexts']:
        assert sha(ROOT/c['audio'])==c['audioSha256'];pcm,rate=sf.read(ROOT/c['audio'],dtype='int16');assert rate==24000
        path=out/(c['id']+'.wav');sf.write(path,pcm[c['fromSample']:c['toSample']],rate,subtype='PCM_16')
        state['status']='transcribing-'+c['id'];checkpoint()
        raw=transcriber(str(path),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
        r={**c,'contextAudio':path.relative_to(ROOT).as_posix(),'contextSha256':sha(path),'text':raw['text'],'words':raw['chunks'],'expectedWasRecognizerPrompt':False,'directReview':False}
        save(out/(c['id']+'.json'),r);state['results'].append(r);checkpoint();print(c['id']+' '+raw['text'],flush=True)
    for p in request['protectedInputs']:assert sha(ROOT/p['path'])==p['sha256']
    state.update(status='finished-current-guide-contexts-awaiting-direct-comparison',cpuJobs=0,exitCode=0,endedAt=now());checkpoint()
except BaseException:
    state.update(status='failed',cpuJobs=0,exitCode=1,endedAt=now(),error=traceback.format_exc());checkpoint();raise
