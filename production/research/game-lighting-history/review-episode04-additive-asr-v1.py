"""One CPU2/GPU0 recognizer for24 new wholes and24 independent splice contexts."""
from pathlib import Path
import datetime,hashlib,json,os,time
os.environ['CUDA_VISIBLE_DEVICES']='-1'
os.environ['OMP_NUM_THREADS']='2';os.environ['MKL_NUM_THREADS']='2'
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'projects/game-lighting-history-04/production'
PLAN=BASE/'additive-asr-plan-v1.json'
STATE=BASE/'additive-asr-execution-v1.json'
FOLDER=BASE/'local/additive-asr-v1'
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,j):
    p.parent.mkdir(parents=True,exist_ok=True);t=p.with_name(p.name+'.writing-'+str(os.getpid()))
    t.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
def main():
    if STATE.exists():raise RuntimeError('Existing ASR state/results preserved; inspect actual identity before scoped resume')
    plan=read(PLAN)
    if len(plan['jobs'])!=48 or sum(j['mode']=='whole' for j in plan['jobs'])!=24:
        raise RuntimeError('Exactly24new wholes+24independent contexts required')
    for x in [plan['audio'],*plan['inputs']]:
        if sha(ROOT/x['path'])!=x['sha256']:raise RuntimeError('Frozen input changed: '+x['path'])
    tts=read(BASE/'additive-tts-selected-execution-v2.json')
    if not tts['generationComplete'] or tts.get('exitCode')!=0:raise RuntimeError('Successful own TTS required')
    h=read(ROOT/'shared/output/gpu-handoff'/f"{tts['leaseToken']}.json")
    if h.get('state')!='research_resume_verified':raise RuntimeError('Actual research restoration required')
    lease=ROOT/'shared/output/GPU_HANDOFF.json'
    if lease.exists() and read(lease).get('token')==tts['leaseToken']:
        raise RuntimeError('Own GPU handoff still active')
    import psutil
    own=psutil.Process()
    if psutil.virtual_memory().available<6*1024**3:raise RuntimeError('Less than6GiB currently available; preserve plan and retry when free')
    for p in psutil.process_iter(['pid','cmdline']):
        command=' '.join(p.info['cmdline'] or [])
        if p.pid not in [own.pid,own.ppid()] and ('render-episode04-additive-v1.py' in command or 'render-episode04-additive-tail-repair-v2.py' in command or ('ffmpeg' in command.lower() and 'game-lighting-history' in command)):
            # Proxy ancestors of this ASR command do not match these names.
            raise RuntimeError('Live own synthesis/render must finish before ASR')
    state=dict(startedAt=now(),status='loading-one-CPU-model',actualIdentity=dict(pid=own.pid,createTime=own.create_time(),command=own.cmdline(),cwd=own.cwd(),exe=own.exe()),planSha256=sha(PLAN),expectedWindows=48,completed=[],cpuThreads=2,gpuJobs=0,original87AsrRepeated=False,allDirectlyReviewed=False,wholeNewAsrApproved=False,independentContextsApproved=False,finalMixedAsr=False,humanWholeListeningApproved=False)
    write(STATE,state)
    try:
        import soundfile as sf,torch,torchaudio
        from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
        torch.set_num_threads(2);torch.set_num_interop_threads(1)
        model_path=ROOT/'qwen3-tts/models/whisper-large-v3-turbo'
        model=AutoModelForSpeechSeq2Seq.from_pretrained(str(model_path),dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,local_files_only=True).to('cpu')
        processor=AutoProcessor.from_pretrained(str(model_path),local_files_only=True)
        recognizer=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float32,device='cpu')
        for job in plan['jobs']:
            target=FOLDER/(job['label']+'.json')
            if target.exists():raise RuntimeError('Existing completed result preserved: '+job['label'])
            path=ROOT/job['audio']['path']
            if sha(path)!=job['audio']['sha256']:raise RuntimeError('Current audio changed')
            first,last=job['sourceSampleRange']
            with sf.SoundFile(path) as f:
                if f.samplerate!=24000 or f.channels!=1:raise RuntimeError('PCM format changed')
                f.seek(first);part=f.read(last-first,dtype='float32')
            if len(part)!=last-first:raise RuntimeError('PCM range changed')
            state.update(status='recognizing-single-new-window',current=job);write(STATE,state)
            opts=dict(generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
            if job['mode']=='whole':opts.update(chunk_length_s=30,stride_length_s=5)
            result=recognizer(dict(raw=torchaudio.functional.resample(torch.from_numpy(part),24000,16000).numpy(),sampling_rate=16000),**opts)
            if sha(path)!=job['audio']['sha256']:raise RuntimeError('Audio changed during recognition')
            record=dict(completedAt=now(),job=job,audio=job['audio'],planSha256=sha(PLAN),sourceSampleRange=[first,last],sampleRate=24000,pcmFloat32Sha256=hashlib.sha256(part.tobytes()).hexdigest(),mode='chunked30s-stride5s' if job['mode']=='whole' else 'independent-sequential-complete-context',expectedTextUsedAsPrompt=False,directFullTextCompared=False,narrationApproved=False,humanWholeListeningApproved=False,finalMixedAsr=False,**result)
            write(target,record);state['completed'].append(dict(label=job['label'],result=target.relative_to(ROOT).as_posix(),sha256=sha(target)))
            state.update(status='window-complete-awaiting-direct-review',current=None,lastWindowEndedAt=now());write(STATE,state)
            print('DONE '+job['label']+' '+str(len(state['completed']))+'/48',flush=True)
            # Return CPU resources cooperatively between independent windows.
            time.sleep(10)
        state.update(status='48-new-whole-and-context-windows-complete-awaiting-direct-review',endedAt=now(),exitCode=0,current=None);write(STATE,state)
    except BaseException as exc:
        state.update(status='failed-preserving-input-and-completed-results',error=repr(exc),endedAt=now(),exitCode=1);write(STATE,state);raise
if __name__=='__main__':main()
