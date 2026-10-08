"""One guarded CPU2 job using the approved Qwen1.7B/reference; ASR remains separate."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, ctypes, hashlib, json, os, subprocess, sys, time, traceback
ROOT=Path(__file__).resolve().parents[3]; BASE=Path(__file__).resolve().parent
STATE=BASE/'narration-tts-execution-v1.json'; LOG=BASE/'narration-tts-v1.log'
REQUEST=BASE/'narration-tts-request-v1.json'; SESSION=BASE/'narration-tts-session-v1.json'
def now(): return datetime.now(timezone.utc).isoformat()
def read(p): return json.loads(p.read_text('utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p): return p.relative_to(ROOT).as_posix()
def save(p,d):
    tmp=p.with_name(p.name+f'.{os.getpid()}.writing')
    tmp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf-8')
    for n in range(40):
        try: os.replace(tmp,p); return
        except OSError:
            if n==39: raise
            time.sleep(.15)
parser=argparse.ArgumentParser(); parser.add_argument('--resource',required=True); args=parser.parse_args()
assert not STATE.exists(),'Inspect existing execution; never repeat an existing worker.'
resource=read(ROOT/args.resource); request=read(REQUEST)
assert (datetime.now(timezone.utc)-datetime.fromisoformat(resource['observedAt'].replace('Z','+00:00'))).total_seconds()<240
assert resource['ownHeavyJobs']==0 and resource['cpuLoadPercent']<85 and resource['freePhysicalMemoryKiB']>16_000_000
assert request['device']=='cpu' and request['cpuThreads']==2 and len(request['scenes'])==8
assert request['pairedWholeTextReview'] and request['overviewPromiseReview']
assert read(ROOT/request['scriptReview'])['contentReadyForApprovedVoiceMeasurement']
for x in request['protectedInputs']: assert sha(ROOT/x['path'])==x['sha256'],x['path']
for s in request['scenes']: assert not (ROOT/s['path']).exists(),s['path']
subprocess.run(['C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe','scripts/review-video-duplicates.cjs','player-customization','--check'],cwd=ROOT,check=True)
for k in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','NUMEXPR_NUM_THREADS']: os.environ[k]='2'
os.environ.update(CUDA_VISIBLE_DEVICES='',TOKENIZERS_PARALLELISM='false',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
if os.name=='nt': ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x00004000)
state=dict(schemaVersion=1,slug='player-customization',pid=os.getpid(),commandLine=[sys.executable,*sys.argv],sessionId=None,startedAt=now(),
 status='loading-approved-Qwen-CPU2',device='cpu',dtype='float32',cpuThreads=2,cpuJobs=1,gpuJobs=0,renderJobs=0,uploads=0,
 request=rel(REQUEST),requestSha256=sha(REQUEST),log=rel(LOG),resource=resource,results=[],total=8,exitCode=None,
 generationComplete=False,wholeAsrDirectReview=False,finalMixedAsrApproved=False,heuristicIsApproval=False,humanListening='pending',humanPronunciation='pending')
def checkpoint():
    if SESSION.exists():
        launch=read(SESSION)
        if launch.get('pid')==os.getpid(): state['sessionId']=launch['sessionId']
    state['updatedAt']=now(); save(STATE,state)
    job=dict(status=state['status'],pid=os.getpid(),commandLine=state['commandLine'],sessionId=state['sessionId'],
        state=rel(STATE),log=rel(LOG),startedAt=state['startedAt'],cpuThreads=2,gpu=0,singleJob=True,
        completed=len(state['results']),total=8,workerExpectedRunning=state['exitCode'] is None,exitCode=state['exitCode'])
    cp=read(BASE/'latest-checkpoint.json')
    cp.update(recordedAt=now(),stage='approved-voice-single-CPU2-measurement',ownedJob=job,ttsStarted=True,
        nextAction='Observe actual process identity and current narration outputs. After exit, full current-hash ASR and independent contexts; measure voice before final footage/white/caption allocation. No final ratio/render/QA/private approval.')
    save(BASE/'latest-checkpoint.json',cp)
    qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json'; q=read(qp); item=next(i for i in q['items'] if i['slug']=='player-customization')
    item.update(stage=cp['stage'],currentExecution=job,ttsStarted=True,narrationMeasurement=dict(state=rel(STATE),completed=len(state['results']),total=8,device='cpu',approved=False),nextAction=cp['nextAction'])
    q.update(updatedAt=now(),lastProgressAt=now()); save(qp,q)
class Tee:
    def __init__(self,original,file): self.original=original; self.file=file
    def write(self,s): self.original.write(s);self.original.flush();self.file.write(s);self.file.flush();return len(s)
    def flush(self): self.original.flush();self.file.flush()
sys.stdout.reconfigure(encoding='utf-8');sys.stderr.reconfigure(encoding='utf-8')
stdout,stderr=sys.stdout,sys.stderr
with LOG.open('x',encoding='utf-8') as log:
    sys.stdout=Tee(stdout,log);sys.stderr=sys.stdout
    try:
        checkpoint();sys.path.insert(0,str(ROOT/'qwen3-tts'));import render_narration as rn
        rn.configure_project('player-customization');rn.INFERENCE_DEVICE='cpu';rn.load_tts_dependencies()
        rn.torch.set_num_threads(2);rn.torch.set_num_interop_threads(1)
        model=rn.Qwen3TTSModel.from_pretrained(str(rn.MODEL_DIR),device_map='cpu',dtype=rn.torch.float32,attn_implementation='eager')
        prompt=model.create_voice_clone_prompt(ref_audio=str(rn.REFERENCE),ref_text=rn.REFERENCE_TEXT_PATH.read_text('utf-8').strip(),x_vector_only_mode=False)
        for s in request['scenes']:
            p=ROOT/s['path'];p.parent.mkdir(parents=True,exist_ok=True);attempts=[];best=None;score=float('inf')
            for attempt in range(1,rn.MAX_RENDER_ATTEMPTS+1):
                state.update(status='synthesizing-'+s['id'],activeScene=s['id'],activeAttempt=attempt);checkpoint();print(f"Scene {s['id']} attempt {attempt}",flush=True)
                wavs,sr=model.generate_voice_clone(text=[s['text']],language=rn.LANGUAGE,voice_clone_prompt=prompt,non_streaming_mode=True,max_new_tokens=rn.MAX_NEW_TOKENS)
                assert len(wavs)==1 and sr==24000 and len(wavs[0])>0
                wav=wavs[0];tail=rn._tail_ratio(wav,sr);decay=rn._tail_decay_ms(wav,sr);badness=rn._badness(tail,decay)
                attemptPath=p.with_name(p.stem+f'-attempt-{attempt}.wav');rn.sf.write(attemptPath,wav,sr,subtype='PCM_16')
                attempts.append(dict(attempt=attempt,path=rel(attemptPath),sha256=sha(attemptPath),seconds=len(wav)/sr,tailRatio=tail,tailDecayMs=decay,heuristicIsApproval=False))
                if badness<score: best=wav;score=badness
                print(json.dumps(attempts[-1]),flush=True)
                if rn._passes_quality(tail,decay): break
            rn.sf.write(p,best,24000,subtype='PCM_16');pcm,sr=rn._read_mono(p)
            state['results'].append(dict(id=s['id'],path=rel(p),sha256=sha(p),samples=len(pcm),sampleRate=sr,seconds=len(pcm)/sr,
                text=s['text'],enLines=s['enLines'],tailRatio=rn._tail_ratio(pcm,sr),tailDecayMs=rn._tail_decay_ms(pcm,sr),attempts=attempts,
                wholeAsrDirectReview=False,heuristicIsApproval=False,humanListening='pending'))
            checkpoint()
        for x in request['protectedInputs']: assert sha(ROOT/x['path'])==x['sha256'],x['path']
        rn.assemble_outputs(rn.load_jobs())
        state.update(status='eight-scenes-measured-awaiting-full-ASR',generationComplete=True,cpuJobs=0,finishedAt=now(),exitCode=0,
            totalRawSceneSeconds=sum(x['seconds'] for x in state['results']),allProtectedInputsUnchanged=True,
            provisionalNarration=dict(path=rel(rn.FINAL_WAV),sha256=sha(rn.FINAL_WAV),timing=rel(rn.TIMING_JSON),koSrt=rel(rn.FINAL_SRT),paragraphBoundaryMethod='quiet valleys near text weights, not final ASR alignment'))
        checkpoint();print('Voice measurements complete; full ASR/contexts and measured allocation pending.',flush=True)
    except BaseException:
        state.update(status='failed-CPU-narration',cpuJobs=0,finishedAt=now(),exitCode=1,error=traceback.format_exc());checkpoint();traceback.print_exc();raise
    finally: sys.stdout=stdout;sys.stderr=stderr
