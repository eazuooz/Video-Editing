"""Approved single GPU voice job, serialized by the inspected research coordinator.

The outer entrypoint allocates no model while another lease exists. The existing
coordinator re-enters this same command after a safe boundary, then restores the
original research queue in its finally path on success or failure.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, os, subprocess, sys, time, traceback
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
STATE=BASE/'narration-tts-execution-v1.json';REQUEST=BASE/'narration-tts-request-v1.json'
SESSION=BASE/'narration-tts-session-v1.json'
def now():return datetime.now(timezone.utc).isoformat()
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):
    t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
def rel(p):return p.relative_to(ROOT).as_posix()
parser=argparse.ArgumentParser();parser.add_argument('--dry-run',action='store_true');parser.add_argument('--resume-preserved-scene-one',action='store_true');args=parser.parse_args()
request=read(REQUEST)
if not request['pairedWholeTextReview'] or not request['overviewPromiseReview']:raise RuntimeError('Whole text review missing')
for x in request['protectedInputs']:
    if sha(ROOT/x['path'])!=x['sha256']:raise RuntimeError('Protected input changed: '+x['path'])
if not read(ROOT/request['scriptReview'])['contentReadyForApprovedVoiceMeasurement']:raise RuntimeError('Current review is not ready')
subprocess.run(['C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe','scripts/review-video-duplicates.cjs','similar-game-design','--check'],cwd=ROOT,check=True)
if args.dry_run:
    print('Prepared13 scenes/51 paragraphs; approved model/reference inputs and current duplicate gate verified. No model loaded.',flush=True);raise SystemExit(0)
recovery=None
if args.resume_preserved_scene_one:
    recovery=read(BASE/'voice-path-recording-recovery-v1.json')
    prior=read(STATE)
    assert prior['stage']=='failed-voice-preserve-current-chunks' and prior['exitCode']==1 and not prior['results']
    assert 'StopIteration' in prior['error'] and sha(STATE)==recovery['failedStateSha256']
    assert sha(ROOT/recovery['preservedScene']['path'])==recovery['preservedScene']['sha256']
    restoration=read(BASE/'research-handoff-failure-verification-v1.json')
    assert restoration['ownedCoordinatorClosed'] and restoration['restorationVerified']
sys.path.insert(0,str(ROOT/'qwen3-tts'))
from gpu_tts_hold import check_gpu_tts_hold
from gpu_handoff_guard import schedule_gpu_handoff,check_gpu_handoff
check_gpu_tts_hold('similar-game-design','cuda:0',False)
schedule_gpu_handoff('similar-game-design','cuda:0',False)
check_gpu_handoff('similar-game-design','cuda:0',False)
# Re-entry through the coordinator rechecks the inputs above after waiting.
if STATE.exists() and recovery is None:raise RuntimeError('An execution already exists: inspect current outputs; do not regenerate finished voice.')
for k in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[k]='2'
os.environ.update(TOKENIZERS_PARALLELISM='false',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
import psutil
me=psutil.Process();lease=read(ROOT/'shared/output/GPU_HANDOFF.json')
state=dict(schemaVersion=1,slug='similar-game-design',actualPid=os.getpid(),createTime=me.create_time(),commandLine=me.cmdline(),
  sessionId=read(SESSION).get('sessionId') if SESSION.exists() else None,startedAt=now(),stage='loading-approved-Qwen-under-owned-lease',
  device='cuda:0',cpuThreads=2,gpuJobs=1,request=rel(REQUEST),requestSha256=sha(REQUEST),leaseToken=lease['token'],
  researchCoordinator=lease.get('coordinator'),log=lease.get('ttsLog'),total=13,results=[],activeScene=None,generationComplete=False,exitCode=None,
  wholeAsrDirectReview=False,finalMixedAsrApproved=False,heuristicIsApproval=False,humanListening='pending',humanPronunciation='pending')
if recovery:
    state.update(results=[recovery['preservedScene']],recovery=dict(evidence=rel(BASE/'voice-path-recording-recovery-v1.json'),
      failedState=recovery['failedStatePreserved'],failedLeaseToken=recovery['failedLeaseToken'],
      failure='Recording callback used numeric-only paths although the renderer names chunks with full scene IDs.',
      preservedFirstSceneRegenerated=False))
def checkpoint():
    state['updatedAt']=now();save(STATE,state)
    p=BASE/'latest-checkpoint.json';c=read(p)
    c.update(recordedAt=now(),stage=state['stage'] if state['exitCode'] is not None else 'single-GPU-approved-voice-measurement',ttsStarted=True,
      ownedJob=dict(pid=state['actualPid'],createTime=state['createTime'],commandLine=state['commandLine'],sessionId=state['sessionId'],
        state=rel(STATE),log=state['log'],gpu=state['gpuJobs'],cpuThreads=2,completed=len(state['results']),total=13,workerExpectedRunning=state['exitCode'] is None,exitCode=state['exitCode']),
      nextAction='Observe actual owned lease/process/log. After TTS exit, verify original research resume from coordinator history, then directly compare complete current-hash ASR plus independent contexts and measure allocation. No final media approval.')
    save(p,c)
    qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json'
    for _ in range(8):
        raw=qp.read_text('utf-8-sig');q=json.loads(raw);item=next(x for x in q['items'] if x['slug']=='similar-game-design')
        item.update(stage=c['stage'],currentExecution=c['ownedJob'],ttsStarted=True,nextAction=c['nextAction']);q.update(updatedAt=now(),lastProgressAt=now())
        if qp.read_text('utf-8-sig')==raw:save(qp,q);break
        time.sleep(.15)
    else:raise RuntimeError('Concurrent queue update; preserve foreign queue and inspect execution state')
checkpoint()
try:
    import render_narration as rn
    rn.configure_project('similar-game-design');rn.INFERENCE_DEVICE='cuda:0';rn.load_tts_dependencies()
    rn.torch.set_num_threads(2);rn.torch.set_num_interop_threads(1)
    original_load=rn.Qwen3TTSModel.from_pretrained.__func__
    def load(cls,*a,**kw):kw.setdefault('attn_implementation','sdpa');return original_load(cls,*a,**kw)
    rn.Qwen3TTSModel.from_pretrained=classmethod(load)
    original_generate=rn.Qwen3TTSModel.generate_voice_clone
    bytext={s['text']:s for s in request['scenes']}
    def generate(self,*a,**kw):
        s=bytext[kw['text'][0]];state.update(stage='synthesizing-'+s['id'],activeScene=s['id']);checkpoint()
        current=rn.torch.cuda.current_stream(self.device);stream=rn.torch.cuda.Stream(device=self.device,priority=-1);stream.wait_stream(current)
        with rn.torch.cuda.stream(stream):result=original_generate(self,*a,**kw)
        stream.synchronize();current.wait_stream(stream);rn.torch.cuda.empty_cache();return result
    rn.Qwen3TTSModel.generate_voice_clone=generate
    original_badness=rn._badness
    rn._badness=lambda tail,decay:original_badness(tail,decay) if rn._passes_quality(tail,decay) else 1000000+original_badness(tail,decay)
    original_write=rn.sf.write
    def write_audio(file,data,samplerate,*a,**kw):
        out=original_write(file,data,samplerate,*a,**kw);p=Path(file)
        if p.parent==rn.CHUNK_DIR and p.name.endswith('-scene.wav'):
            s=next(x for x in request['scenes'] if ROOT/x['path']==p)
            result=dict(id=s['id'],path=rel(p),sha256=sha(p),samples=len(data),sampleRate=samplerate,seconds=len(data)/samplerate,
              tailRatio=rn._tail_ratio(data,samplerate),tailDecayMs=rn._tail_decay_ms(data,samplerate),heuristicIsApproval=False,wholeAsrApproved=False)
            state['results']=[x for x in state['results'] if x['id']!=s['id']]+[result];checkpoint()
        return out
    rn.sf.write=write_audio
    items=rn.build_render_items(rn.load_jobs())
    assert {rel(x.path.resolve()) for x in items}=={x['path'] for x in request['scenes']}, 'Request/renderer paths differ before generation'
    if recovery:
        preserved=ROOT/recovery['preservedScene']['path']
        assert sha(preserved)==recovery['preservedScene']['sha256']
        items=[x for x in items if x.path.resolve()!=preserved.resolve()]
    rn.render_chunks(items,1,set())
    if recovery:assert sha(preserved)==recovery['preservedScene']['sha256']
    rn.assemble_outputs(rn.load_jobs())
    for x in request['protectedInputs']:
        if sha(ROOT/x['path'])!=x['sha256']:raise RuntimeError('Protected input changed during synthesis: '+x['path'])
    state.update(stage='thirteen-scenes-measured-awaiting-full-ASR',generationComplete=True,gpuJobs=0,finishedAt=now(),exitCode=0,
      totalRawSceneSeconds=sum(x['seconds'] for x in state['results']),allProtectedInputsUnchanged=True,
      provisionalNarration=dict(path=rel(rn.FINAL_WAV),sha256=sha(rn.FINAL_WAV),timing=rel(rn.TIMING_JSON),koSrt=rel(rn.FINAL_SRT),
        paragraphBoundaryMethod='quiet valleys near text weights, not final direct ASR alignment'))
    checkpoint();print('Voice generated; complete ASR/contexts and research-resume verification remain pending.',flush=True)
except BaseException:
    state.update(stage='failed-voice-preserve-current-chunks',gpuJobs=0,finishedAt=now(),exitCode=1,error=traceback.format_exc());checkpoint();traceback.print_exc();raise
