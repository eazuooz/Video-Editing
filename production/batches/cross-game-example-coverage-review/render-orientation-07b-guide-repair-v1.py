"""One newly clarified observation-guide paragraph candidate; preserve original PCM."""
from pathlib import Path
from datetime import datetime, timezone
import argparse,hashlib,json,os,sys,time,traceback,subprocess

ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
STATE=R/'narration-07b-guide-repair-execution-v1.json'
REQUEST=R/'narration-07b-guide-repair-request-v1.json'
SESSION=R/'narration-07b-guide-repair-session-v1.json'
now=lambda:datetime.now(timezone.utc).isoformat()
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return p.resolve().relative_to(ROOT).as_posix()
def save(p,x):
    temp=p.with_name(p.name+'.'+str(os.getpid())+'.writing')
    temp.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(temp,p)

ap=argparse.ArgumentParser();ap.add_argument('--dry-run',action='store_true');args=ap.parse_args()
import importlib.util
assert all(importlib.util.find_spec(n) is not None for n in ['soundfile','qwen_tts','torch','psutil','numpy']), 'Use approved qwen3-tts/.venv runtime before requesting a GPU handoff'
NODE=Path('C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe')
def current_duplicate_check():
    subprocess.run([str(NODE),'scripts/review-video-duplicates.cjs','game-math-orientation-matrices','--candidate-file','projects/game-math-orientation-matrices/revision-teaching-clarity-v1/duplicate-candidate-v1.json','--check'],cwd=ROOT,check=True)
current_duplicate_check()
retry=read(R/'resource-before-07b-guide-repair-voice-v2.json')
assert retry['protectedShaMatched']
if not args.dry_run: assert retry['voiceEligibleAtObservation'] and retry['stableGpuIdle20SecondsVerified']
# Initial request needs fresh read-only evidence. The scheduled child uses the
# coordinator's newer continuous-idle measurement, not an old pre-wait timestamp.
import psutil
early_me=psutil.Process();early_path=ROOT/'shared/output/GPU_HANDOFF.json'
early_lease=read(early_path) if early_path.exists() else None
early_ancestors={p.pid:p.create_time() for p in [early_me,*early_me.parents()]}
early_owner=early_lease.get('coordinator',{}) if early_lease else {}
early_owned=early_lease and early_lease.get('project')=='game-math-orientation-matrices' and abs(early_ancestors.get(early_owner.get('pid'),-1)-early_owner.get('createTime',0))<.01
if early_owned:
    assert early_lease['state']=='tts_running'
    assert time.time()-early_lease.get('updatedAt',early_lease.get('requestedAt'))<240
    assert early_lease['gpuBeforeTts']['freeMiB']>=18000 and early_lease['gpuBeforeTts']['utilization']<15
elif not args.dry_run:
    assert (datetime.now(timezone.utc)-datetime.fromisoformat(retry['observedAt'])).total_seconds()<240, 'Read fresh resources before another voice request.'
request=read(REQUEST)
assert request['pairedWholeTextReview'] and request['overviewPromiseReview']
assert request['total']==1 and request['paragraphs']==1
assert request['baselineApprovedPcmRegeneration']==0
review=read(ROOT/request['scriptReview'])
assert review['contentReadyForApprovedVoiceMeasurement']
assert review['originalAllWordingAndOrderPreserved']
source_review=read(ROOT/request['sourceReview'])
assert source_review['all217NativeSamplesAnd45BoardsDirectlyRead'] and source_review['exactNativePtsVerified']
assert not STATE.exists(),'Inspect actual existing TTS state/PCM before any retry'
assert not any((ROOT/s['path']).exists() for s in request['scenes']),'Inspect completed additive PCM; do not synthesize it twice'
for x in request['protectedInputs']: assert sha(ROOT/x['path'])==x['sha256'],x['path']
protected=request['protectedInputs']+[dict(path=rel(p),sha256=sha(p)) for p in [REQUEST,R/'duplicate-current-check-verification-v1.json',R/'cross-game-plan-review-flag-transition-v1.json']]
for k in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[k]='2'
os.environ.update(TOKENIZERS_PARALLELISM='false',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
sys.path.insert(0,str(ROOT/'qwen3-tts'))
import render_narration as rn
rn.configure_project('game-math-orientation-matrices',request['manifest'])
items=rn.build_render_items(rn.load_jobs())
assert {rel(i.path) for i in items}=={s['path'] for s in request['scenes']}
assert {i.text for i in items}=={s['text'] for s in request['scenes']}
if args.dry_run:
    print('Prepared1item/1pairedparagraph;24original+6additivePCM preserved. Model/GPU/state creation0.',flush=True)
    raise SystemExit(0)
import psutil
me=psutil.Process();leasePath=ROOT/'shared/output/GPU_HANDOFF.json'
lease=read(leasePath) if leasePath.exists() else None
owner=lease.get('coordinator',{}) if lease else {}
ancestors={p.pid:p.create_time() for p in [me,*me.parents()]}
owned=lease and lease.get('project')=='game-math-orientation-matrices' and abs(ancestors.get(owner.get('pid'),-1)-owner.get('createTime',0))<.01
if not owned:
    save(R/'narration-07b-guide-repair-waiting-v1.json',dict(schemaVersion=1,slug='game-math-orientation-matrices',recordedAt=now(),
        actualPid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),cwd=me.cwd(),
        stage='serialized-one-guide-candidate-request-before-model',modelLoaded=False,gpuJobs=0,
        foreignLease=dict(project=lease.get('project'),token=lease.get('token'),coordinator=owner,state=lease.get('state')) if lease else None,
        sessionId=read(SESSION).get('sessionId') if SESSION.exists() else None,
        protectedInputs=protected,researchPauseOrProcessChanges=0))
from gpu_tts_hold import check_gpu_tts_hold
from gpu_handoff_guard import schedule_gpu_handoff,check_gpu_handoff
check_gpu_tts_hold('game-math-orientation-matrices','cuda:0',False)
schedule_gpu_handoff('game-math-orientation-matrices','cuda:0',False)
check_gpu_handoff('game-math-orientation-matrices','cuda:0',False)
for x in protected: assert sha(ROOT/x['path'])==x['sha256'],x['path']
current_duplicate_check()
lease=read(leasePath)
# The completed research queue is not restarted. Idle ownership still needs
# continuous20s low utilization, with the unchanged600s maximum, before loading.
if lease.get('idleGpu'):
    deadline=time.monotonic()+600;stable=None;samples=[]
    while True:
        assert read(leasePath)['token']==lease['token']
        raw=subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip()
        free,util=map(int,raw.splitlines()[0].replace(' ','').split(','));stamp=time.monotonic()
        samples.append(dict(observedAt=now(),freeMiB=free,utilization=util))
        if free>=18000 and util<15:
            if stable is None:stable=stamp
            if stamp-stable>=20:break
        else:stable=None
        if stamp>=deadline:raise RuntimeError('600s stableGPU idle guard expired before model load')
        time.sleep(2)
    save(R/'07b-guide-repair-owned-idle-guard-v1.json',dict(verifiedAt=now(),leaseToken=lease['token'],continuousIdleSeconds=stamp-stable,samples=samples,stable20SecondsVerified=True,researchRestarted=False))
else:
    assert lease['state']=='tts_running' and time.time()-lease['updatedAt']<240
    assert lease['gpuBeforeTts']['freeMiB']>=18000 and lease['gpuBeforeTts']['utilization']<15
state=dict(schemaVersion=1,slug='game-math-orientation-matrices',actualPid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),
    cwd=me.cwd(),sessionId=read(SESSION).get('sessionId') if SESSION.exists() else None,
    startedAt=now(),stage='loading-approved-Qwen-under-owned-lease',device='cuda:0',cpuThreads=2,gpuJobs=1,
    request=rel(REQUEST),requestSha256=sha(REQUEST),protectedInputs=protected,
    leaseToken=lease['token'],researchCoordinator=lease.get('coordinator'),idleGpu=lease.get('idleGpu',False),log=lease.get('ttsLog') or rel(R/'narration-07b-guide-repair-v1.log'),
    total=1,results=[],activeScene=None,generationComplete=False,exitCode=None,
    wholeAsrDirectReview=False,finalMixedAsrApproved=False,heuristicIsApproval=False,
    original24PcmRegenerated=0,existing6PcmRegenerated=0,humanListeningApproved=False,humanPronunciationApproved=False,publicRightsApproved=False)
def checkpoint():
    state['updatedAt']=now();save(STATE,state)
    p=R/'latest-checkpoint.json';c=read(p)
    c.update(recordedAt=now(),stage=state['stage'],ttsStarted=True,crossGameVoiceStarted=True,activeOwnedWorkers=1,
        ownedJob=dict(pid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),cwd=me.cwd(),
            sessionId=state['sessionId'],state=rel(STATE),log=state['log'],gpuJobs=state['gpuJobs'],cpuThreads=2,
            completed=len(state['results']),total=1,exitCode=state['exitCode']),
        next='After actual outer exit verify owned lease closure and completed research preservation, or exact original queue resume if it was active; compare this one candidate and the complete current07b splice/seam. Final mix/animation/settings/schedule remain pending.')
    save(p,c)
checkpoint()
try:
    rn.INFERENCE_DEVICE='cuda:0';rn.load_tts_dependencies();rn.torch.set_num_threads(2);rn.torch.set_num_interop_threads(1)
    original_load=rn.Qwen3TTSModel.from_pretrained.__func__
    def load(cls,*a,**kw):kw.setdefault('attn_implementation','sdpa');return original_load(cls,*a,**kw)
    rn.Qwen3TTSModel.from_pretrained=classmethod(load)
    original_generate=rn.Qwen3TTSModel.generate_voice_clone;bytext={s['text']:s for s in request['scenes']}
    def generate(self,*a,**kw):
        s=bytext[kw['text'][0]];state.update(stage='synthesizing-'+s['id'],activeScene=s['id']);checkpoint()
        current=rn.torch.cuda.current_stream(self.device);stream=rn.torch.cuda.Stream(device=self.device,priority=-1);stream.wait_stream(current)
        with rn.torch.cuda.stream(stream):result=original_generate(self,*a,**kw)
        stream.synchronize();current.wait_stream(stream);rn.torch.cuda.empty_cache();return result
    rn.Qwen3TTSModel.generate_voice_clone=generate
    old_badness=rn._badness
    rn._badness=lambda tail,decay:old_badness(tail,decay) if rn._passes_quality(tail,decay) else 1000000+old_badness(tail,decay)
    original_write=rn.sf.write
    def write_audio(file,data,samplerate,*a,**kw):
        out=original_write(file,data,samplerate,*a,**kw);p=Path(file)
        if p.parent==rn.CHUNK_DIR and p.name.endswith('-scene.wav'):
            s=next(x for x in request['scenes'] if (ROOT/x['path']).resolve()==p.resolve())
            result=dict(id=s['id'],path=rel(p),sha256=sha(p),samples=len(data),sampleRate=samplerate,seconds=len(data)/samplerate,
                tailRatio=rn._tail_ratio(data,samplerate),tailDecayMs=rn._tail_decay_ms(data,samplerate),heuristicIsApproval=False,wholeAsrApproved=False)
            state['results']=[x for x in state['results'] if x['id']!=s['id']]+[result];checkpoint()
        return out
    rn.sf.write=write_audio
    rn.render_chunks(items,1,set());rn.assemble_outputs(rn.load_jobs())
    for x in protected: assert sha(ROOT/x['path'])==x['sha256'],x['path']
    assert len(state['results'])==1
    state.update(stage='one-guide-candidate-measured-awaiting-current-ASR-and-owned-closure',generationComplete=True,
        gpuJobs=0,finishedAt=now(),exitCode=0,allProtectedInputsUnchanged=True,
        totalRawSceneSeconds=sum(x['seconds'] for x in state['results']),
        provisionalNarration=dict(path=rel(rn.FINAL_WAV),sha256=sha(rn.FINAL_WAV),timing=rel(rn.TIMING_JSON),koSrt=rel(rn.FINAL_SRT),
            paragraphBoundaryMethod='quiet valleys near text weights; final direct current-PCM ASR alignment pending'))
    checkpoint();print('One guide candidate measured; original24+6PCM preserved. Outerexit/researchresume/currentASR/finalmix remain pending.',flush=True)
except BaseException:
    state.update(stage='failed-voice-preserve-current-chunks',gpuJobs=0,finishedAt=now(),exitCode=1,error=traceback.format_exc());checkpoint();raise
