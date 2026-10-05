"""Read the uncertain new13-g1 onset in complete independent PCM contexts."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,sys,traceback
import numpy as np
import soundfile as sf
sys.stdout.reconfigure(encoding='utf-8');sys.stderr.reconfigure(encoding='utf-8')
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
PROOF=ROOT/'production/batches/sakurai-planning-game-design/proof-making-game-sequels'
STATE=BASE/'guide-onset-context-asr-execution-v3.json'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
now=lambda:datetime.now(timezone.utc).isoformat()
def save(p,d):
    tmp=p.with_name(p.name+f'.{os.getpid()}.writing');tmp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');tmp.replace(p)
assert not STATE.exists(),'Read existing context results instead of repeating the job.'
request=read(BASE/'guided-observation-tts-request-v3.json')
for p in request['protectedInputs']:assert sha(ROOT/p['path'])==p['sha256']
g=next(x for x in read(BASE/'guided-observation-tts-execution-v3.json')['results'] if x['id']=='13-g1')
assert sha(ROOT/g['path'])==g['sha256']
s=next(x for x in read(BASE/'measured-paragraphs-expanded13.json')['scenes'] if x['id']=='13')
assert sha(ROOT/s['audio'])==s['audioSha256']
base,rate=sf.read(ROOT/s['audio'],dtype='int16');guide,gr=sf.read(ROOT/g['path'],dtype='int16');assert rate==gr==24000
contexts=[('13-g1-padded',np.concatenate([np.zeros(19200,dtype='int16'),guide,np.zeros(19200,dtype='int16')]),0.8),('13-p1-then-g1',np.concatenate([base[:s['paragraphs'][0]['pcmToSample']],np.zeros(43200,dtype='int16'),guide]),s['paragraphs'][0]['pcmToSample']/24000+1.8)]
state=dict(schemaVersion=1,pid=os.getpid(),sessionId=None,startedAt=now(),status='loading-CPU-Whisper',cpuJobs=1,cpuThreads=2,gpuJobs=0,results=[],directReview=False,expectedWasRecognizerPrompt=False,originalAudioChanged=False)
def checkpoint():
    session=BASE/'guide-onset-context-asr-session-v3.json'
    if session.exists() and read(session)['pid']==os.getpid():state['sessionId']=read(session)['sessionId']
    state['updatedAt']=now();save(STATE,state)
    q=read(PROOF.parent/'queue.json');i=next(x for x in q['items'] if x['slug']=='making-game-sequels')
    i.update(stage='current13-new-guide-onset-independent-context-ASR',updatedAt=now(),nextAction='Directly compare the new13-g1 uncertain onset in both complete contexts. Preserve all base PCM and the other seven guides; final timing/mix/render remain pending.')
    i['execution']={**i.get('execution',{}),'phase':i['stage'],'status':state['status'],'pid':os.getpid(),'sessionId':state['sessionId'],'alive':bool(state['cpuJobs']),'commandLine':'review-guide-onset-context-v3.py CPU2','state':STATE.relative_to(ROOT).as_posix(),'cpuProductionJobs':state['cpuJobs'],'primaryCpuProductionJobs':state['cpuJobs'],'gpuSynthesisJobs':0,'renderJobs':0,'uploads':0,'observedAt':now(),'activeTasks':[] if not state['cpuJobs'] else [{'kind':'new-guide-onset-context-ASR','pid':os.getpid(),'sessionId':state['sessionId']}]}
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
    out=BASE/'asr-guide-onset-context-local-v3';out.mkdir()
    for ident,pcm,onset in contexts:
        path=out/(ident+'.wav');sf.write(path,pcm,24000,subtype='PCM_16')
        state['status']='transcribing-'+ident;checkpoint()
        raw=transcriber(str(path),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
        r=dict(id=ident,audio=path.relative_to(ROOT).as_posix(),sha256=sha(path),guideAudio=g['path'],guideSha256=g['sha256'],guideStartsAt=onset,text=raw['text'],words=raw['chunks'],expectedWasRecognizerPrompt=False,directReview=False)
        save(out/(ident+'.json'),r);state['results'].append(r);checkpoint();print(raw['text'],flush=True)
    for p in request['protectedInputs']:assert sha(ROOT/p['path'])==p['sha256']
    state.update(status='finished-direct-context-comparison-pending',cpuJobs=0,exitCode=0,endedAt=now());checkpoint()
except BaseException:
    state.update(status='failed',cpuJobs=0,exitCode=1,endedAt=now(),error=traceback.format_exc());checkpoint();raise
