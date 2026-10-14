"""One CPU2 diagnostic of provisional sentence spans; never a final QA approval."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,wave,os,psutil,subprocess,traceback
for k in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[k]='2'
os.environ.update(CUDA_VISIBLE_DEVICES='',TOKENIZERS_PARALLELISM='false',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
now=lambda:datetime.now(timezone.utc).isoformat()
dest=R/'first-paragraph-repair-contexts-v1';statepath=R/'first-paragraph-repair-contexts-execution-v1.json'
assert not dest.exists() and not statepath.exists()
whole=read(R/'first-paragraph-repair-whole-asr-v1.json');tts=read(R/'narration-first-paragraph-repair-execution-v1.json')
assert whole['actualExitObserved'] and whole['actualOuterExitCode']==0 and tts['researchResumeVerified']
assert not psutil.pid_exists(whole['pid']) or abs(psutil.Process(whole['pid']).create_time()-whole['createTime'])>.01
for x in tts['protectedInputs']+tts['results']:assert sha(ROOT/x['path'])==x['sha256']
resource=dict(observedAt=now(),cpuLoadPercent=psutil.cpu_percent(interval=1),freePhysicalMemoryKiB=psutil.virtual_memory().available//1024,ownHeavyCpuJobs=0,
    gpuObservation=subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip())
assert resource['cpuLoadPercent']<85 and resource['freePhysicalMemoryKiB']>8_000_000
entries=[dict(scene_id='07b-p01',start=0,end=4.10,text='퍼즐에서 방향을 읽는 문제를 포털 투로 이어 보겠습니다.'),dict(scene_id='07b-p01',start=4.10,end=8.16,text='큐브로 레이저를 장치에 보내거나, 큐브를 발판 위에 놓습니다.')]
sceneStarts={'07b-p01':0}
dest.mkdir();me=psutil.Process()
state=dict(schemaVersion=1,pid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),cwd=me.cwd(),sessionId=None,
    startedAt=now(),cpuThreads=2,gpuJobs=0,cpuJobs=1,completed=0,total=2,results=[],exitCode=None,resource=resource,
    purpose='Independent full sentences around observed3.92–4.28 quiet gap in recognizable replacement candidate.',
    provisionalBoundaries=False,completeContextBoundariesApproved=False,wholeAudioContentApproved=False,humanListeningApproved=False,
    finalMixedAudioApproved=False,finalPixelApproved=False,expectedUsedAsRecognizerPrompt=False,originalPcmRegenerated=0)
def save():
    sp=R/'first-paragraph-repair-contexts-execution-v1.session.json'
    if sp.exists():
        session=read(sp);assert session['pid']==me.pid and abs(session['createTime']-me.create_time())<.01;state['sessionId']=session['sessionId']
    state['updatedAt']=now();statepath.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n','utf-8')
save()
try:
    import torch
    from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
    torch.set_num_threads(2);torch.set_num_interop_threads(1)
    modelpath=ROOT/'qwen3-tts/models/whisper-large-v3-turbo'
    model=AutoModelForSpeechSeq2Seq.from_pretrained(str(modelpath),dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager',local_files_only=True).to('cpu')
    processor=AutoProcessor.from_pretrained(str(modelpath),local_files_only=True)
    transcriber=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float32,device='cpu')
    for i,e in enumerate(entries,1):
        source=next(x for x in tts['results'] if x['id']==e['scene_id'])
        with wave.open(str(ROOT/source['path']),'rb') as w:
            assert w.getframerate()==24000 and w.getnchannels()==1 and w.getsampwidth()==2
            a=max(0,round((e['start']-sceneStarts[e['scene_id']])*24000));b=min(w.getnframes(),round((e['end']-sceneStarts[e['scene_id']])*24000))
            assert 0<=a<b<=w.getnframes();w.setpos(a);pcm=w.readframes(b-a)
        identifier=e['scene_id']+'-p'+str(sum(x['scene_id']==e['scene_id'] for x in entries[:i])).zfill(2)
        p=dest/(identifier+'.wav');padded=b'\0\0'*7200+pcm+b'\0\0'*7200
        with wave.open(str(p),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000);w.writeframes(padded)
        state['active']=identifier;save()
        raw=transcriber(str(p),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
        row=dict(id=identifier,sourcePath=source['path'],sourceSha256=source['sha256'],startSample=a,endSample=b,
            exactSourcePcmSha256=hashlib.sha256(pcm).hexdigest(),diagnosticWavSha256=sha(p),expected=e['text'],text=raw['text'],words=raw['chunks'],
            provisionalBoundaries=False,completeContextBoundariesApproved=False,expectedUsedAsRecognizerPrompt=False,directReview=False,approved=False)
        (dest/(identifier+'.json')).write_text(json.dumps(row,ensure_ascii=False,indent=2)+'\n','utf-8')
        state['results'].append(row);state['completed']=len(state['results']);save();print(json.dumps(dict(id=identifier,text=row['text']),ensure_ascii=False),flush=True)
    for x in tts['protectedInputs']+tts['results']:assert sha(ROOT/x['path'])==x['sha256']
    state.update(exitCode=0,cpuJobs=0,finishedAt=now(),status='diagnostic-complete-awaiting-direct-words-and-boundary-review');save()
except BaseException:
    state.update(exitCode=1,cpuJobs=0,error=traceback.format_exc(),finishedAt=now());save();raise
