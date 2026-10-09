"""Nine fresh observation guides and two unadopted exact-text paragraph takes; original10 PCM scenes are immutable inputs.
An owned job-boundary coordinator must restore research after success/failure.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, os, subprocess, sys, time, traceback
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
STATE=BASE/'observation-candidates-tts-execution-v3.json';REQUEST=BASE/'observation-candidates-tts-request-v3.json'
SESSION=BASE/'observation-candidates-tts-session-v3.json'
def now():return datetime.now(timezone.utc).isoformat()
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return p.relative_to(ROOT).as_posix()
def save(p,x):
    temp=p.with_name(p.name+f'.{os.getpid()}.writing');temp.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8')
    for i in range(40):
        try:os.replace(temp,p);return
        except OSError:
            if i==39:raise
            time.sleep(.15)
parser=argparse.ArgumentParser();parser.add_argument('--dry-run',action='store_true');args=parser.parse_args()
request=read(REQUEST)
assert request['pairedWholeTextReview'] and request['overviewPromiseReview'] and len(request['scenes'])==11
for x in request['protectedInputs']:assert sha(ROOT/x['path'])==x['sha256'],x['path']
assert read(ROOT/request['scriptReview'])['contentReadyForApprovedVoiceMeasurement']
subprocess.run(['C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe',
 'scripts/review-video-duplicates.cjs','presenting-game-scores','--check'],cwd=ROOT,check=True)
sys.path.insert(0,str(ROOT/'qwen3-tts'))
import render_narration as rn
rn.configure_project('presenting-game-scores',str(ROOT/request['manifestOverride']))
items=rn.build_render_items(rn.load_jobs())
assert {rel(x.path.resolve()) for x in items}=={x['path'] for x in request['scenes']}
assert {x.text for x in items}=={x['text'] for x in request['scenes']}
assert not rn.OUTPUT_DIR.exists(),'Preserve any existing candidates; inspect before a new job.'
if args.dry_run:
    print('Prepared9 guides/9 paired paragraphs plus2 exact-text candidates; protected original10 PCM and current duplicate gate verified. Model0/GPU0.',flush=True)
    raise SystemExit(0)
assert not STATE.exists(),'Existing execution must be inspected; never regenerate completed guides'
# Finished ASR is a prerequisite; do not overlap another owned heavy worker.
for mode in ['whole','contexts','targets']:
    r=read(BASE/f'current-{mode}-asr-execution-v1.json')
    assert r['exitCode']==0 and r['actualExitObserved'],mode
sys.path.insert(0,str(ROOT/'qwen3-tts'))
from gpu_tts_hold import check_gpu_tts_hold
from gpu_handoff_guard import schedule_gpu_handoff,check_gpu_handoff
import psutil
me=psutil.Process()
leasep=ROOT/'shared/output/GPU_HANDOFF.json'
lease=read(leasep) if leasep.exists() else None
owner=lease.get('coordinator',{}) if lease else {}
ancestors={p.pid:p.create_time() for p in [me,*me.parents()]}
owned=lease and lease.get('project')=='presenting-game-scores' and abs(ancestors.get(owner.get('pid'),-1)-owner.get('createTime',0))<.01
if not owned:
    resource=read(BASE/'observation-candidates-resource-v3.json')
    assert (datetime.now(timezone.utc)-datetime.fromisoformat(resource['observedAt'])).total_seconds()<240
    assert resource['ownHeavyJobs']==0 and resource['cpuLoadPercent']<85 and resource['freePhysicalMemoryKiB']>8_000_000
    waiting=dict(schemaVersion=1,slug='presenting-game-scores',recordedAt=now(),actualPid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),cwd=me.cwd(),stage='cooperative-job-boundary-wait-before-model',modelLoaded=False,gpuJobs=0,request=rel(REQUEST),requestSha256=sha(REQUEST),resource='projects/presenting-game-scores/production/observation-candidates-resource-v3.json',sessionId=read(SESSION).get('sessionId') if SESSION.exists() else None)
    save(BASE/'observation-candidates-tts-waiting-v3.json',waiting)

check_gpu_tts_hold('presenting-game-scores','cuda:0',False)
schedule_gpu_handoff('presenting-game-scores','cuda:0',False)
check_gpu_handoff('presenting-game-scores','cuda:0',False)
# Inputs/gates above are rechecked by coordinator re-entry after waiting.
for k in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[k]='2'
os.environ.update(TOKENIZERS_PARALLELISM='false',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
import psutil
me=psutil.Process();lease=read(ROOT/'shared/output/GPU_HANDOFF.json')
state=dict(schemaVersion=1,slug='presenting-game-scores',actualPid=os.getpid(),createTime=me.create_time(),commandLine=me.cmdline(),
 sessionId=read(SESSION).get('sessionId') if SESSION.exists() else None,startedAt=now(),stage='loading-approved-guide-Qwen-under-owned-lease',
 device='cuda:0',cpuThreads=2,gpuJobs=1,request=rel(REQUEST),requestSha256=sha(REQUEST),leaseToken=lease['token'],
 researchCoordinator=lease.get('coordinator'),log=lease.get('ttsLog'),total=11,results=[],activeScene=None,
 generationComplete=False,exitCode=None,wholeAsrDirectReview=False,finalMixedAsrApproved=False,
 heuristicIsApproval=False,humanListening='pending',humanPronunciation='pending',originalTenChunksRegenerated=False, candidateParagraphsAdopted=False)
def checkpoint():
    state['updatedAt']=now();save(STATE,state)
    cp_path=BASE/'latest-checkpoint.json';cp=read(cp_path)
    cp.update(recordedAt=now(),stage='single-observation-candidates-voice-measurement-v3' if state['exitCode'] is None else state['stage'],
     ownedJob=dict(pid=state['actualPid'],createTime=state['createTime'],commandLine=state['commandLine'],sessionId=state['sessionId'],
       state=rel(STATE),log=state['log'],gpu=state['gpuJobs'],cpuThreads=2,completed=len(state['results']),total=11,
       workerExpectedRunning=state['exitCode'] is None,exitCode=state['exitCode']),
     nextAction='Observe actual owned lease/process/log; after exit verify original research resumed. Directly compare guide whole ASR and independent contexts, measure every PCM paragraph and exact 60:40, then final animation/caption/pair QA. Final approvals remain false.')
    save(cp_path,cp)
    qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json'
    for _ in range(8):
        raw=qp.read_text('utf-8-sig');q=json.loads(raw);item=next(x for x in q['items'] if x['slug']=='presenting-game-scores')
        item.update(stage=cp['stage'],currentExecution=cp['ownedJob'],nextAction=cp['nextAction']);q.update(updatedAt=now(),lastProgressAt=now())
        if qp.read_text('utf-8-sig')==raw:save(qp,q);break
        time.sleep(.15)
    else:raise RuntimeError('Concurrent queue write; preserve foreign work')
checkpoint()
try:
    import render_narration as rn
    rn.configure_project('presenting-game-scores',str(ROOT/request['manifestOverride']));rn.INFERENCE_DEVICE='cuda:0';rn.load_tts_dependencies()
    rn.torch.set_num_threads(2);rn.torch.set_num_interop_threads(1)
    original_load=rn.Qwen3TTSModel.from_pretrained.__func__
    def load(cls,*a,**kw):kw.setdefault('attn_implementation','sdpa');return original_load(cls,*a,**kw)
    rn.Qwen3TTSModel.from_pretrained=classmethod(load)
    original_generate=rn.Qwen3TTSModel.generate_voice_clone;bytext={s['text']:s for s in request['scenes']}
    def generate(self,*a,**kw):
        s=bytext[kw['text'][0]];state.update(stage='synthesizing-guide-'+s['id'],activeScene=s['id']);checkpoint()
        current=rn.torch.cuda.current_stream(self.device);stream=rn.torch.cuda.Stream(device=self.device,priority=-1);stream.wait_stream(current)
        with rn.torch.cuda.stream(stream):result=original_generate(self,*a,**kw)
        stream.synchronize();current.wait_stream(stream);rn.torch.cuda.empty_cache();return result
    rn.Qwen3TTSModel.generate_voice_clone=generate
    original_badness=rn._badness
    rn._badness=lambda tail,decay:original_badness(tail,decay) if rn._passes_quality(tail,decay) else 1000000+original_badness(tail,decay)
    original_write=rn.sf.write
    def write_audio(file,data,samplerate,*a,**kw):
        out=original_write(file,data,samplerate,*a,**kw);p=Path(file).resolve()
        if p.parent==rn.CHUNK_DIR.resolve() and p.name.endswith('-scene.wav'):
            s=next(x for x in request['scenes'] if (ROOT/x['path']).resolve()==p)
            result=dict(id=s['id'],path=rel(p),sha256=sha(p),samples=len(data),sampleRate=samplerate,seconds=len(data)/samplerate,
             tailRatio=rn._tail_ratio(data,samplerate),tailDecayMs=rn._tail_decay_ms(data,samplerate),heuristicIsApproval=False,wholeAsrApproved=False)
            state['results']=[x for x in state['results'] if x['id']!=s['id']]+[result];checkpoint()
        return out
    rn.sf.write=write_audio
    items=rn.build_render_items(rn.load_jobs())
    assert {rel(x.path.resolve()) for x in items}=={x['path'] for x in request['scenes']}
    assert not rn.OUTPUT_DIR.exists(),'Preserve existing guide PCM'
    rn.render_chunks(items,1,set());rn.assemble_outputs(rn.load_jobs())
    for x in request['protectedInputs']:assert sha(ROOT/x['path'])==x['sha256'],x['path']
    assert len(state['results'])==11
    state.update(stage='observation-candidates-measured-awaiting-full-ASR-and-research-resume-verification',generationComplete=True,
     gpuJobs=0,finishedAt=now(),exitCode=0,totalRawSceneSeconds=sum(x['seconds'] for x in state['results']),allProtectedInputsUnchanged=True,
     provisionalNarration=dict(path=rel(rn.FINAL_WAV),sha256=sha(rn.FINAL_WAV),timing=rel(rn.TIMING_JSON),koSrt=rel(rn.FINAL_SRT),
       paragraphBoundaryMethod='quiet-valley candidate; not final direct ASR timing'))
    checkpoint();print('Guide voice generated; full ASR/contexts and actual research restoration remain pending.',flush=True)
except BaseException:
    state.update(stage='failed-guide-voice-preserve-current-chunks',gpuJobs=0,finishedAt=now(),exitCode=1,error=traceback.format_exc())
    checkpoint();traceback.print_exc();raise
