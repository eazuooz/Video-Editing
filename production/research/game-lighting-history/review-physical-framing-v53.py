"""One CPU2/GPU0 model: five new paragraphs and five independent full joins.

Runs only after the successful cooperative TTS lease restores research. Old111
paragraphs are included only as complete adjacent context, never regenerated.
Results require direct full-text comparison; no approval is inferred here.
"""
from pathlib import Path
import datetime,hashlib,json,os,sys
os.environ['CUDA_VISIBLE_DEVICES']='-1'
os.environ['OMP_NUM_THREADS']='2';os.environ['MKL_NUM_THREADS']='2'
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'projects/game-lighting-history-04/production'
REQUEST=BASE/'physical-framing-tts-request-v49.json'
TTS=BASE/'physical-framing-tts-execution-v49.json'
ASSEMBLY=BASE/'additive-unmixed-review-assembly-v2.json'
STATE=BASE/'physical-framing-asr-execution-v53.json'
FOLDER=BASE/'local/physical-framing-asr-v53'
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,j):
    p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name(p.name+'.writing-'+str(os.getpid()))
    tmp.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(tmp,p)
def main():
    dry='--plan-only' in sys.argv
    if not dry and STATE.exists():raise RuntimeError('Preserve completed results; inspect real identity before scoped resume')
    request=read(REQUEST);tts=read(TTS);assembly=read(ASSEMBLY)
    if len(request['scenes'])!=5 or not tts.get('generationComplete') or tts.get('exitCode')!=0:
        raise RuntimeError('Successful five-paragraph generation required')
    history=ROOT/'shared/output/gpu-handoff'/f"{tts['leaseToken']}.json"
    if read(history).get('state')!='research_resume_verified':raise RuntimeError('Actual research restoration required')
    active=ROOT/'shared/output/GPU_HANDOFF.json'
    if active.exists() and read(active).get('token')==tts['leaseToken']:raise RuntimeError('Own GPU lease still active')
    for f in request['protectedInputs']:
        if sha(ROOT/f['path'])!=f['sha256']:raise RuntimeError('Protected input changed: '+f['path'])
    for f in tts['results']:
        if sha(ROOT/f['path'])!=f['sha256'] or not f['technicalTailGatePassed']:raise RuntimeError('Selected take needs scoped repair')
    if sha(ROOT/assembly['audio']['path'])!=assembly['audio']['sha256']:raise RuntimeError('Retained111 PCM changed')
    def old(scene,last=False):
        candidates=[e for e in assembly['entries'] if e['originalScene']==scene and e['kind']=='preserved-original']
        if not candidates:raise RuntimeError('Missing complete retained neighbour: '+scene)
        e=candidates[-1] if last else candidates[0]
        return dict(path=assembly['audio']['path'],sha256=assembly['audio']['sha256'],sampleRange=[e['startSample'],e['endSample']],id=e['id'],ko=e['text'],en=e['en'],kind='retained-complete-neighbour')
    neighbours={
        'part1-overview':('after',old('overview')),
        'part1-conclusion':('before',old('18m',True)),
        'part2-overview':('after',old('19')),
        'part2-conclusion':('before',old('21a',True)),
        'part3-overview':('after',old('22')),
    }
    selected={r['id']:r for r in tts['results']};jobs=[]
    for s in request['scenes']:
        r=selected[s['id']]
        fresh=dict(path=r['path'],sha256=r['sha256'],sampleRange=[0,r['samples']],id=s['id'],ko=s['ko'],en=s['en'],kind='new-framing')
        order,n=neighbours[s['id']]
        jobs.append(dict(label='whole-'+s['id'],mode='whole',sources=[fresh]))
        jobs.append(dict(label='context-'+s['id'],mode='independent-complete-join',sources=[fresh,n] if order=='after' else [n,fresh],gapSamples=6720))
    plan=dict(schemaVersion=1,preparedAt=now(),request=dict(path=REQUEST.relative_to(ROOT).as_posix(),sha256=sha(REQUEST)),tts=dict(path=TTS.relative_to(ROOT).as_posix(),sha256=sha(TTS)),researchHistory=dict(path=history.relative_to(ROOT).as_posix(),sha256=sha(history)),assembly=dict(path=ASSEMBLY.relative_to(ROOT).as_posix(),sha256=sha(ASSEMBLY)),jobs=jobs,cpuThreads=2,gpuJobs=0,expectedTextUsedAsPrompt=False,original111AsrRepeated=False,allDirectlyReviewed=False,finalMixedAsr=False)
    if dry:
        target=BASE/'physical-framing-asr-plan-v53.json'
        if target.exists():raise RuntimeError('Preserve existing plan')
        write(target,plan);print('Prepared10 windows; no recognition or approval');return
    import psutil
    own=psutil.Process()
    if psutil.virtual_memory().available<6*1024**3:raise RuntimeError('Less than6GiB available; no model started')
    ancestry={p.pid for p in own.parents()}|{own.pid}
    for p in psutil.process_iter(['pid','name','cmdline']):
        if p.pid in ancestry:continue
        command=' '.join(p.info['cmdline'] or []).lower()
        if 'game-lighting-history' in command and (('ffmpeg' in (p.info['name'] or '').lower()) or 'render-physical-framing-v49.py' in command or 'review-physical-framing-v53.py' in command):
            raise RuntimeError('Own media/ASR slot is still live; preserve existing work')
    state=dict(schemaVersion=1,startedAt=now(),actualIdentity=dict(pid=own.pid,createTime=own.create_time(),command=own.cmdline(),cwd=own.cwd()),status='loading-one-CPU-model',plan=plan,expectedWindows=10,completed=[],cpuThreads=2,gpuJobs=0,wholeFiveApproved=False,independentContextsApproved=False,allDirectlyReviewed=False,humanWholeListeningApproved=False,finalMixedAsr=False)
    write(STATE,state)
    try:
        import soundfile as sf,numpy as np,torch,torchaudio
        from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
        torch.set_num_threads(2);torch.set_num_interop_threads(1)
        model_path=ROOT/'qwen3-tts/models/whisper-large-v3-turbo'
        model=AutoModelForSpeechSeq2Seq.from_pretrained(str(model_path),dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,local_files_only=True).to('cpu')
        processor=AutoProcessor.from_pretrained(str(model_path),local_files_only=True)
        recognize=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float32,device='cpu')
        for job in jobs:
            target=FOLDER/(job['label']+'.json')
            if target.exists():raise RuntimeError('Existing result preserved')
            parts=[];ranges=[];offset=0
            for source in job['sources']:
                p=ROOT/source['path'];first,last=source['sampleRange']
                if sha(p)!=source['sha256']:raise RuntimeError('PCM changed before recognition')
                with sf.SoundFile(p) as f:
                    if f.samplerate!=24000 or f.channels!=1:raise RuntimeError('PCM format changed')
                    f.seek(first);part=f.read(last-first,dtype='float32')
                if len(part)!=last-first:raise RuntimeError('Truncated source range')
                if parts:
                    gap=job.get('gapSamples',0);parts.append(np.zeros(gap,dtype=np.float32));offset+=gap
                ranges.append(dict(id=source['id'],windowSampleRange=[offset,offset+len(part)],source=source,pcmFloat32Sha256=hashlib.sha256(part.tobytes()).hexdigest()));parts.append(part);offset+=len(part)
            signal=np.concatenate(parts)
            state.update(status='recognizing-one-window',current=job['label']);write(STATE,state)
            opts=dict(generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
            if job['mode']=='whole':opts.update(chunk_length_s=30,stride_length_s=5)
            result=recognize(dict(raw=torchaudio.functional.resample(torch.from_numpy(signal),24000,16000).numpy(),sampling_rate=16000),**opts)
            for source in job['sources']:
                if sha(ROOT/source['path'])!=source['sha256']:raise RuntimeError('PCM changed during recognition')
            record=dict(completedAt=now(),job=job,sourceRanges=ranges,sampleRate=24000,samples=len(signal),pcmFloat32Sha256=hashlib.sha256(signal.tobytes()).hexdigest(),expectedTextUsedAsPrompt=False,directFullTextCompared=False,narrationApproved=False,humanWholeListeningApproved=False,finalMixedAsr=False,**result)
            write(target,record);state['completed'].append(dict(label=job['label'],result=target.relative_to(ROOT).as_posix(),sha256=sha(target)));state.update(current=None,status='window-complete-awaiting-direct-review');write(STATE,state)
            print('DONE '+job['label']+' '+str(len(state['completed']))+'/10',flush=True)
        state.update(status='ten-windows-complete-awaiting-direct-full-text-review',endedAt=now(),exitCode=0,current=None);write(STATE,state)
    except BaseException as exc:
        state.update(status='failed-preserve-completed-results',endedAt=now(),exitCode=1,error=repr(exc));write(STATE,state);raise
if __name__=='__main__':main()
