"""Only20 reviewed native-observation guides; preserve all original84 paragraphs/PCM.

The shared coordinator seals the current research run, grants one TTS lease,
then restores the exact original command and working directory on either outcome.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, os, subprocess, sys, time, traceback
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
REQUEST=BASE/'native-guides-tts-request-v1.json';STATE=BASE/'native-guides-tts-execution-v1.json';SESSION=BASE/'native-guides-tts-session-v1.json'
NODE=Path('C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe')
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return p.relative_to(ROOT).as_posix()
def now():return datetime.now(timezone.utc).isoformat()
def save(p,x):
    temp=p.with_name(p.name+f'.{os.getpid()}.writing');temp.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8')
    for i in range(30):
        try:os.replace(temp,p);return
        except OSError:
            if i==29:raise
            time.sleep(.15)
ap=argparse.ArgumentParser();ap.add_argument('--dry-run',action='store_true');args=ap.parse_args()
request=read(REQUEST)
assert request['pairedWholeTextReview'] and len(request['scenes'])==20
review=read(ROOT/request['scriptReview'])
assert review['full20KoEnDirectlyRead'] and review['contentReadyForApprovedVoiceMeasurement']
def verify():
    for x in request['protectedInputs']:assert sha(ROOT/x['path'])==x['sha256'],x['path']
verify()
subprocess.run([str(NODE),'scripts/review-video-duplicates.cjs','game-lighting-history-03','--candidate-file','production/research/game-lighting-history/candidate-03.json','--check'],cwd=ROOT,check=True)
for k in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[k]='2'
os.environ.update(TOKENIZERS_PARALLELISM='false',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
sys.path.insert(0,str(ROOT/'qwen3-tts'))
import render_narration as rn
rn.configure_project('game-lighting-history-03',str(ROOT/request['manifestOverride']))
items=rn.build_render_items(rn.load_jobs())
assert {rel(x.path.resolve()) for x in items}=={s['path'] for s in request['scenes']}
if args.dry_run:
    print('20 guide-only inputs/protected original84 PCM/current duplicate gate verified. Model0/GPU0.',flush=True)
    raise SystemExit(0)
assert not STATE.exists(),'Existing execution must be inspected, never regenerate completed guides'
assert not rn.OUTPUT_DIR.exists(),'Preserve any existing guide PCM'
from gpu_tts_hold import check_gpu_tts_hold
from gpu_handoff_guard import schedule_gpu_handoff,check_gpu_handoff
check_gpu_tts_hold('game-lighting-history-03','cuda:0',False)
schedule_gpu_handoff('game-lighting-history-03','cuda:0',False)
check_gpu_handoff('game-lighting-history-03','cuda:0',False)
verify()
import psutil
me=psutil.Process();lease=read(ROOT/'shared/output/GPU_HANDOFF.json')
state=dict(schemaVersion=1,slug='game-lighting-history-03',actualPid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),
 sessionId=read(SESSION).get('sessionId') if SESSION.exists() else None,startedAt=now(),stage='loading-approved-Qwen-guide-only',
 device='cuda:0',cpuThreads=2,gpuJobs=1,total=20,results=[],activeScene=None,request=rel(REQUEST),requestSha256=sha(REQUEST),
 leaseToken=lease['token'],log=lease.get('ttsLog'),generationComplete=False,exitCode=None,original84Regenerated=False,
 wholeAsrDirectReview=False,finalMixedAsrApproved=False,heuristicIsApproval=False,humanListening='pending',humanPronunciation='pending')
def checkpoint():
    state['updatedAt']=now();save(STATE,state)
    cp_path=ROOT/'production/research/game-lighting-history/checkpoint.json';cp=read(cp_path)
    cp.update(updatedAt=now(),stage=state['stage'],ownedJobsRunning=[] if state['exitCode'] is not None else [dict(pid=state['actualPid'],createTime=state['createTime'],commandLine=state['commandLine'],sessionId=state['sessionId'],state=rel(STATE),log=state['log'],cpuThreads=2,gpuJobs=state['gpuJobs'],completed=len(state['results']),total=20)],
     next='Observe actual guide-only TTS process/lease/log; verify original research restoration after exit. Directly compare all20 whole ASR and independent contexts, measure PCM and exact60:40, then final animation/native/caption/pair QA. All4 final uploads remain pending.')
    cp['episode03GuideVoiceExecution']={k:state[k] for k in ['actualPid','createTime','commandLine','sessionId','stage','leaseToken','log','generationComplete','exitCode']};cp['episode03GuideVoiceExecution'].update(state=rel(STATE),completed=len(state['results']),total=20)
    save(cp_path,cp)
checkpoint()
try:
    rn.INFERENCE_DEVICE='cuda:0';rn.load_tts_dependencies();rn.torch.set_num_threads(2);rn.torch.set_num_interop_threads(1)
    loader=rn.Qwen3TTSModel.from_pretrained.__func__
    def load(cls,*a,**kw):kw.setdefault('attn_implementation','sdpa');return loader(cls,*a,**kw)
    rn.Qwen3TTSModel.from_pretrained=classmethod(load)
    original_generate=rn.Qwen3TTSModel.generate_voice_clone;bytext={s['text']:s for s in request['scenes']}
    def generate(self,*a,**kw):
        s=bytext[kw['text'][0]];state.update(stage='synthesizing-native-guide-'+s['id'],activeScene=s['id']);checkpoint()
        current=rn.torch.cuda.current_stream(self.device);stream=rn.torch.cuda.Stream(device=self.device,priority=-1);stream.wait_stream(current)
        with rn.torch.cuda.stream(stream):result=original_generate(self,*a,**kw)
        stream.synchronize();current.wait_stream(stream);rn.torch.cuda.empty_cache();return result
    rn.Qwen3TTSModel.generate_voice_clone=generate
    badness=rn._badness;rn._badness=lambda tail,decay:badness(tail,decay) if rn._passes_quality(tail,decay) else 1000000+badness(tail,decay)
    original_write=rn.sf.write
    def write_audio(file,data,samplerate,*a,**kw):
        result=original_write(file,data,samplerate,*a,**kw);p=Path(file).resolve()
        if p.parent==rn.CHUNK_DIR.resolve() and p.name.endswith('-scene.wav'):
            s=next(x for x in request['scenes'] if (ROOT/x['path']).resolve()==p)
            item=dict(id=s['id'],path=rel(p),sha256=sha(p),samples=len(data),sampleRate=samplerate,seconds=len(data)/samplerate,tailRatio=rn._tail_ratio(data,samplerate),tailDecayMs=rn._tail_decay_ms(data,samplerate),heuristicIsApproval=False,wholeAsrApproved=False)
            state['results']=[x for x in state['results'] if x['id']!=s['id']]+[item];checkpoint()
        return result
    rn.sf.write=write_audio
    rn.render_chunks(items,1,set());rn.assemble_outputs(rn.load_jobs());verify();assert len(state['results'])==20
    state.update(stage='20-native-guide-PCM-generated-ASR-and-research-resume-pending',generationComplete=True,gpuJobs=0,finishedAt=now(),exitCode=0,totalRawSceneSeconds=sum(x['seconds'] for x in state['results']),allProtectedInputsUnchanged=True,
     provisionalNarration=dict(path=rel(rn.FINAL_WAV),sha256=sha(rn.FINAL_WAV),timing=rel(rn.TIMING_JSON),koSrt=rel(rn.FINAL_SRT),finalTimelineAdopted=False))
    checkpoint();print('20 guide PCM generated. Whole/context ASR, measured allocation and actual research restoration require verification.',flush=True)
except BaseException:
    state.update(stage='failed-guide-only-TTS-preserve-all-original-media',gpuJobs=0,finishedAt=now(),exitCode=1,error=traceback.format_exc());checkpoint();traceback.print_exc();raise
