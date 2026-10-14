"""Six approved additive bridges; serialize before model load and preserve baseline PCM."""
from pathlib import Path
from datetime import datetime, timezone
import argparse,hashlib,json,os,sys,time,traceback

ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
STATE=R/'narration-tts-execution-v2.json'
REQUEST=R/'narration-tts-request-v1.json'
SESSION=R/'narration-tts-session-v2.json'
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
failed=read(R/'narration-tts-execution-v1.json'); restored=read(R/'research-handoff-verification-v1.json')
assert failed['actualOuterExitCode']==1 and failed['actualOuterSession']==18332 and failed['results']==[] and restored['restorationVerified']
request=read(REQUEST)
assert request['pairedWholeTextReview'] and request['overviewPromiseReview']
assert request['total']==6 and request['paragraphs']==22
assert request['baselineApprovedPcmRegeneration']==0
review=read(ROOT/request['scriptReview'])
assert review['contentReadyForApprovedVoiceMeasurement']
assert review['originalAllWordingAndOrderPreserved']
bank=read(R/'source-selection-preflight-v2.json')
assert bank['sourceSelectionPreflightApproved'] and bank['maximumUniqueFrames']==21370
assert bank['all16NormalPlaybackWindowsExecuted'] and not bank['entireFinalPixelsApproved']
assert not STATE.exists(),'Inspect actual existing TTS state/PCM before any retry'
assert not any((ROOT/s['path']).exists() for s in request['scenes']),'Inspect completed additive PCM; do not synthesize it twice'
for x in request['protectedInputs']: assert sha(ROOT/x['path'])==x['sha256'],x['path']
protected=request['protectedInputs']+[dict(path=rel(p),sha256=sha(p)) for p in [
    REQUEST,R/'tts-manifest-v1.json',R/'script/additions.ko.json',R/'script/additions.en.json',
    ROOT/request['scriptReview'],R/'source-selection-preflight-v2.json',
    R/'causal-flow-and-annotation-plan-v1.json',R/'observation-pilot-direct-review-v4.json',R/'observation-point-keyframes-v3.json']]
for k in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[k]='2'
os.environ.update(TOKENIZERS_PARALLELISM='false',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
sys.path.insert(0,str(ROOT/'qwen3-tts'))
import render_narration as rn
rn.configure_project('game-math-orientation-matrices',request['manifest'])
items=rn.build_render_items(rn.load_jobs())
assert {rel(i.path) for i in items}=={s['path'] for s in request['scenes']}
assert {i.text for i in items}=={s['text'] for s in request['scenes']}
if args.dry_run:
    print('Prepared6newbridges/22pairedparagraphs;24approvedPCM preserved. Model/GPU/state creation0.',flush=True)
    raise SystemExit(0)
import psutil
me=psutil.Process();leasePath=ROOT/'shared/output/GPU_HANDOFF.json'
lease=read(leasePath) if leasePath.exists() else None
owner=lease.get('coordinator',{}) if lease else {}
ancestors={p.pid:p.create_time() for p in [me,*me.parents()]}
owned=lease and lease.get('project')=='game-math-orientation-matrices' and abs(ancestors.get(owner.get('pid'),-1)-owner.get('createTime',0))<.01
if not owned:
    save(R/'narration-tts-waiting-v2.json',dict(schemaVersion=1,slug='game-math-orientation-matrices',recordedAt=now(),
        actualPid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),cwd=me.cwd(),
        stage='serialized-six-bridges-request-before-model',modelLoaded=False,gpuJobs=0,
        foreignLease=dict(project=lease.get('project'),token=lease.get('token'),coordinator=owner,state=lease.get('state')) if lease else None,
        sessionId=read(SESSION).get('sessionId') if SESSION.exists() else None,
        protectedInputs=protected,researchPauseOrProcessChanges=0))
from gpu_tts_hold import check_gpu_tts_hold
from gpu_handoff_guard import schedule_gpu_handoff,check_gpu_handoff
check_gpu_tts_hold('game-math-orientation-matrices','cuda:0',False)
schedule_gpu_handoff('game-math-orientation-matrices','cuda:0',False)
check_gpu_handoff('game-math-orientation-matrices','cuda:0',False)
for x in protected: assert sha(ROOT/x['path'])==x['sha256'],x['path']
lease=read(leasePath)
state=dict(schemaVersion=1,slug='game-math-orientation-matrices',actualPid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),
    cwd=me.cwd(),sessionId=read(SESSION).get('sessionId') if SESSION.exists() else None,
    startedAt=now(),stage='loading-approved-Qwen-under-owned-lease',device='cuda:0',cpuThreads=2,gpuJobs=1,
    request=rel(REQUEST),requestSha256=sha(REQUEST),protectedInputs=protected,
    leaseToken=lease['token'],researchCoordinator=lease.get('coordinator'),log=lease.get('ttsLog'),
    total=6,results=[],activeScene=None,generationComplete=False,exitCode=None,
    wholeAsrDirectReview=False,finalMixedAsrApproved=False,heuristicIsApproval=False,
    original24PcmRegenerated=0,humanListeningApproved=False,humanPronunciationApproved=False,publicRightsApproved=False)
def checkpoint():
    state['updatedAt']=now();save(STATE,state)
    p=R/'latest-checkpoint.json';c=read(p)
    c.update(recordedAt=now(),stage=state['stage'],ttsStarted=True,
        ownedJob=dict(pid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),cwd=me.cwd(),
            sessionId=state['sessionId'],state=rel(STATE),log=state['log'],gpuJobs=state['gpuJobs'],cpuThreads=2,
            completed=len(state['results']),total=6,exitCode=state['exitCode']),
        next='After actual outer exit verify own lease history and original research resume; then directly compare six whole current-PCM ASR texts and complete independent contexts. Final mix/animation/settings/schedule remain pending.')
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
    assert len(state['results'])==6
    state.update(stage='six-bridges-measured-awaiting-whole-current-ASR-and-research-resume',generationComplete=True,
        gpuJobs=0,finishedAt=now(),exitCode=0,allProtectedInputsUnchanged=True,
        totalRawSceneSeconds=sum(x['seconds'] for x in state['results']),
        provisionalNarration=dict(path=rel(rn.FINAL_WAV),sha256=sha(rn.FINAL_WAV),timing=rel(rn.TIMING_JSON),koSrt=rel(rn.FINAL_SRT),
            paragraphBoundaryMethod='quiet valleys near text weights; final direct current-PCM ASR alignment pending'))
    checkpoint();print('Six bridges measured; original24PCM preserved. Outerexit/researchresume/currentASR/finalmix remain pending.',flush=True)
except BaseException:
    state.update(stage='failed-voice-preserve-current-chunks',gpuJobs=0,finishedAt=now(),exitCode=1,error=traceback.format_exc());checkpoint();raise
