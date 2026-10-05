"""Read all thirteen current mixed chapters and complete independent contexts."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, time, traceback
import soundfile as sf
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent;W=BASE/'final-v1'
DEST=W/'mixed-asr-v1';STATE=W/'mixed-asr-execution.json'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
now=lambda:datetime.now(timezone.utc).isoformat()
def write(p,d):
    temp=p.with_name(p.name+f'.{os.getpid()}.writing')
    for n in range(120):
        try:temp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');os.replace(temp,p);return
        except OSError:
            if n==119:raise
            time.sleep(.25)
assert not STATE.exists() and not DEST.exists()
plan=read(W/'plan.json');mix=W/'final-mix.wav';settings=read(W/'mix-settings.json')
assert sha(mix)==settings['wavSha256'] and settings['planSha256']==sha(W/'plan.json')
assert read(W/'framed-visual-recovery-execution.json')['exitCode']==0
audio,sr=sf.read(mix,dtype='float32',always_2d=True);assert sr==48000 and len(audio)==35583*800
windows=[dict(label='scene-'+s['id'],scene=s['id'],fromSeconds=s['startFrame']/60,
    toSeconds=s['endFrameExclusive']/60,expectedKo=[p['ko'] for p in s['speechEvidence']],
    scope='Entire current final mixed chapter; all expected text is comparison data only.') for s in plan['scenes']]
for sid,a,z,label in [('01',1,3,'overview-clarity'),('04',1,3,'tools-Knight-clarity'),
    ('07',1,3,'retained-core-clarity'),('11',1,4,'two-audiences-clarity'),
    ('02',4,5,'wall-guide-join'),('06',1,3,'named-devices-preparation'),('06',4,6,'combat-and-preview-guides'),
    ('13',1,2,'far-guide-onset'),('13',3,5,'near-then-separate-far-guides'),
    ('08',3,3,'resource-visible-counter'),('12',1,2,'overhead-preview-words'),
    ('12',2,4,'preparation-to-combat-guide-joins'),('12',4,6,'combat-to-three-question-conclusion')]:
    s=next(s for s in plan['scenes'] if s['id']==sid);parts=[p for p in s['speechEvidence'] if a<=p['paragraph']<=z]
    windows.append(dict(label=sid+'-'+label,scene=sid,
        fromSeconds=s['startFrame']/60+max(0,parts[0]['outputSpeechFromSample']/24000-.3),
        toSeconds=min(s['endFrameExclusive']/60,s['startFrame']/60+parts[-1]['outputSpeechToSample']/24000+.3),
        expectedKo=[p['ko'] for p in parts],scope='Independent complete-paragraph context; expected text is never a recognizer prompt.'))
assert len(windows)==26
DEST.mkdir();write(W/'mixed-asr-request.json',dict(createdAt=now(),mixSha256=sha(mix),
    planSha256=sha(W/'plan.json'),windows=windows,expectedWasRecognizerPrompt=False))
state=dict(schemaVersion=1,startedAt=now(),pid=os.getpid(),sessionId=None,status='loading-local-CPU-whisper',
    device='cpu',threads=2,mixSha256=sha(mix),totalScenes=13,totalWindows=26,
    completed=0,exitCode=None,automaticApproval=False,humanWholeListening='pending')
def checkpoint():
    sp=W/'mixed-asr-session.json'
    if sp.exists() and read(sp).get('pid')==os.getpid():state['sessionId']=read(sp)['sessionId']
    state['observedAt']=now();write(STATE,state)
    qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qp);i=next(i for i in q['items'] if i['slug']=='making-game-sequels')
    running=state['exitCode'] is None
    i.update(stage='current13-guided60-final-mix-CPU-ASR',updatedAt=state['observedAt'],
        nextAction='Directly compare all13 mixed chapters and13 independent complete contexts. Encode current fixed captions and inspect every final cue/cut; technical QA, collection, singleprivate save and per-video Git remain pending.')
    i['execution'].update(status=state['status'],phase=i['stage'],observedAt=state['observedAt'],pid=os.getpid(),sessionId=state['sessionId'],
        alive=running,state=rel(STATE),commandLine='review-final-mix-v1.py CPU2/GPU0',
        cpuProductionJobs=int(running),primaryCpuProductionJobs=int(running),gpuSynthesisJobs=0,renderJobs=0,uploads=0,
        activeTasks=[dict(kind='current-final-mixed-ASR',pid=os.getpid(),state=rel(STATE))] if running else [],
        currentFinalMixAsr=dict(state=rel(STATE),completed=state['completed'],total=26,automaticApproval=False))
    q['updatedAt']=i['updatedAt'];write(qp,q)
    for p in [BASE/'latest-checkpoint.json',ROOT/'production/batches/sakurai-planning-game-design/proof-making-game-sequels/latest-checkpoint.json']:
        d=read(p)
        for k in ['stage','updatedAt','nextAction','execution']:d[k]=i[k]
        d.update(finalMixBuilt=True,finalMixAsrApproved=False,rendered=False,qaApproved=False,collected=False,privateUploaded=False)
        write(p,d)
try:
    checkpoint()
    import torch
    from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
    torch.set_num_threads(2);mp=ROOT/'qwen3-tts/models/whisper-large-v3-turbo'
    model=AutoModelForSpeechSeq2Seq.from_pretrained(str(mp),dtype=torch.float32,low_cpu_mem_usage=True,
        use_safetensors=True,attn_implementation='eager',local_files_only=True).to('cpu')
    processor=AutoProcessor.from_pretrained(str(mp),local_files_only=True)
    transcriber=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,
        feature_extractor=processor.feature_extractor,dtype=torch.float32,device='cpu')
    results=[]
    for w in windows:
        wav=DEST/(w['label']+'.wav')
        sf.write(wav,audio[round(w['fromSeconds']*sr):round(w['toSeconds']*sr)].mean(axis=1),sr,subtype='PCM_16')
        state['status']='transcribing-'+w['label'];checkpoint()
        raw=transcriber(str(wav),generate_kwargs={'language':'korean','task':'transcribe'},chunk_length_s=30,return_timestamps='word')
        row={**w,'windowSha256':sha(wav),'text':raw['text'],'words':raw['chunks'],
            'expectedWasRecognizerPrompt':False,'directReview':False}
        results.append(row);write(DEST/(w['label']+'.json'),row)
        write(DEST/'asr.json',dict(mixSha256=settings['wavSha256'],planSha256=sha(W/'plan.json'),
            complete=len(results)==26,results=results,humanWholeListening='pending',automaticallyApproved=False))
        state['completed']=len(results);checkpoint()
        print(json.dumps(dict(label=w['label'],text=row['text']),ensure_ascii=False),flush=True)
    assert sha(mix)==settings['wavSha256']
    state.update(status='closed-current-final-mixed-ASR-awaiting-direct-review',exitCode=0,endedAt=now());checkpoint()
except BaseException:
    state.update(status='closed-current-final-mixed-ASR-failed',exitCode=1,endedAt=now(),error=traceback.format_exc());checkpoint();raise
