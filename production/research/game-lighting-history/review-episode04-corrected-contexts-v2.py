"""One CPU2/GPU0 worker for only24 corrected complete splice contexts."""
from pathlib import Path
import argparse,datetime,hashlib,json,os,time
os.environ['CUDA_VISIBLE_DEVICES']='-1';os.environ['OMP_NUM_THREADS']='2';os.environ['MKL_NUM_THREADS']='2'
ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'projects/game-lighting-history-04/production'
PLAN=BASE/'additive-context-plan-v2.json';STATE=BASE/'additive-context-execution-v2.json';FOLDER=BASE/'local/additive-context-v2'
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,j):
    p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name(p.name+'.writing-'+str(os.getpid()))
    tmp.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(tmp,p)
def main():
    import psutil
    parser=argparse.ArgumentParser();parser.add_argument('--resume-import-failure',action='store_true');args=parser.parse_args()
    failed=None
    if STATE.exists():
        failed=read(STATE)
        if not(args.resume_import_failure and failed.get('exitCode')==1 and not failed['completed'] and failed.get('error')=='ModuleNotFoundError("No module named \'soundfile\'")'):
            raise RuntimeError('Existing v2 execution/results preserved; only the observed zero-result import failure may resume')
        old=failed['actualIdentity']
        if psutil.pid_exists(old['pid']) and abs(psutil.Process(old['pid']).create_time()-old['createTime'])<.1:raise RuntimeError('Failed worker still alive')
    prior=read(BASE/'additive-asr-execution-v1.json');direct=read(BASE/'additive-asr-direct-progress-v1.json')
    if prior.get('exitCode')!=0 or len(prior['completed'])!=48 or not direct.get('all48DirectlyCompared'):raise RuntimeError('Previous48 windows must finish and receive complete direct comparison first')
    identity=prior['actualIdentity']
    if psutil.pid_exists(identity['pid']):
        p=psutil.Process(identity['pid'])
        if abs(p.create_time()-identity['createTime'])<.1 and p.cmdline()==identity['command']:raise RuntimeError('Prior single CPU recognizer still alive')
    own=psutil.Process()
    ancestors={p.pid for p in own.parents()}
    for p in psutil.process_iter(['pid','name','cmdline']):
        command=' '.join(p.info['cmdline'] or [])
        name=(p.info['name'] or '').lower()
        if p.pid!=own.pid and p.pid not in ancestors and (('review-episode04-' in command and name.startswith('python')) or (name.startswith('ffmpeg') and 'game-lighting-history' in command)):
            raise RuntimeError('Another own heavy media/recognition job is live')
    if psutil.virtual_memory().available<6*1024**3:raise RuntimeError('Available memory below6GiB; preserve plan before any state creation')
    plan=read(PLAN)
    if len(plan['jobs'])!=24 or any(j['mode']!='context' for j in plan['jobs']):raise RuntimeError('Only24 corrected independent contexts allowed')
    for x in [plan['audio'],*plan['inputs']]:
        if sha(ROOT/x['path'])!=x['sha256']:raise RuntimeError('Frozen corrected input changed: '+x['path'])
    import soundfile as sf,torch,torchaudio
    from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
    if failed:
        archive=BASE/'additive-context-import-failure-v2.json'
        if archive.exists():raise RuntimeError('Existing import-failure history preserved')
        write(archive,failed)
    state=dict(startedAt=now(),status='loading-one-CPU-model',actualIdentity=dict(pid=own.pid,createTime=own.create_time(),command=own.cmdline(),cwd=own.cwd(),exe=own.exe()),planSha256=sha(PLAN),expectedWindows=24,completed=[],cpuThreads=2,gpuJobs=0,original87AsrRepeated=False,new24WholeAsrRepeated=False,allDirectlyReviewed=False,correctedContextsApproved=False,finalMixedAsr=False,humanWholeListeningApproved=False,previousExecution=dict(path='projects/game-lighting-history-04/production/additive-asr-execution-v1.json',sha256=sha(BASE/'additive-asr-execution-v1.json')))
    write(STATE,state)
    try:
        if failed:state['importFailureHistory']='projects/game-lighting-history-04/production/additive-context-import-failure-v2.json';write(STATE,state)
        torch.set_num_threads(2);torch.set_num_interop_threads(1)
        model_path=ROOT/'qwen3-tts/models/whisper-large-v3-turbo'
        model=AutoModelForSpeechSeq2Seq.from_pretrained(str(model_path),dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,local_files_only=True).to('cpu')
        processor=AutoProcessor.from_pretrained(str(model_path),local_files_only=True)
        recognizer=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float32,device='cpu')
        for job in plan['jobs']:
            target=FOLDER/(job['label']+'.json')
            if target.exists():raise RuntimeError('Existing corrected context preserved')
            path=ROOT/job['audio']['path']
            if sha(path)!=job['audio']['sha256']:raise RuntimeError('Corrected current PCM changed')
            first,last=job['sourceSampleRange']
            with sf.SoundFile(path) as f:
                if f.samplerate!=24000 or f.channels!=1:raise RuntimeError('Current PCM format changed')
                f.seek(first);part=f.read(last-first,dtype='float32')
            if len(part)!=last-first:raise RuntimeError('Actual complete context range changed')
            state.update(status='recognizing-single-corrected-context',current=job);write(STATE,state)
            result=recognizer(dict(raw=torchaudio.functional.resample(torch.from_numpy(part),24000,16000).numpy(),sampling_rate=16000),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
            if sha(path)!=job['audio']['sha256']:raise RuntimeError('Input changed during recognition')
            output=dict(completedAt=now(),job=job,audio=job['audio'],planSha256=sha(PLAN),sourceSampleRange=[first,last],sampleRate=24000,pcmFloat32Sha256=hashlib.sha256(part.tobytes()).hexdigest(),mode='independent-sequential-complete-measured-context',expectedTextUsedAsPrompt=False,directFullTextCompared=False,narrationApproved=False,humanWholeListeningApproved=False,finalMixedAsr=False,**result)
            write(target,output);state['completed'].append(dict(label=job['label'],result=target.relative_to(ROOT).as_posix(),sha256=sha(target)))
            state.update(status='corrected-window-complete-awaiting-direct-review',current=None,lastWindowEndedAt=now());write(STATE,state)
            print('DONE '+job['label']+' '+str(len(state['completed']))+'/24',flush=True);time.sleep(10)
        state.update(status='24-corrected-contexts-complete-awaiting-direct-review',endedAt=now(),exitCode=0,current=None);write(STATE,state)
    except BaseException as exc:
        state.update(status='failed-preserving-corrected-input-and-results',endedAt=now(),error=repr(exc),exitCode=1);write(STATE,state);raise
if __name__=='__main__':main()
