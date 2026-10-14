"""Measure only the24 reviewed additions, preserving original87 PCM and research."""
from pathlib import Path
import hashlib,json,os,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'projects/game-lighting-history-04/production'
sys.path.insert(0,str(ROOT/'qwen3-tts'))
requestPath=(ROOT/sys.argv[sys.argv.index('--request')+1]).resolve() if '--request' in sys.argv else BASE/'additive-tts-request-v1.json'
requestPath.relative_to(BASE)
request=json.loads(requestPath.read_text('utf-8'))
review=json.loads((ROOT/request['scriptReview']).read_text('utf-8'))
dry='--dry-run' in sys.argv
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify():
    if len(request['scenes'])!=24 or not review['full24KoEnDirectlyRead'] or not review['original87TextAndCurrentPcmUnchanged']:
        raise SystemExit('Full24 paired direct read and preserved87 PCM required')
    for f in request['protectedInputs']:
        if sha(ROOT/f['path'])!=f['sha256']:raise SystemExit('Reviewed input changed: '+f['path'])
verify()
checked=subprocess.run(['node','scripts/review-video-duplicates.cjs','game-lighting-history-04','--candidate-file','production/research/game-lighting-history/candidate-04.json','--check'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',creationflags=subprocess.CREATE_NO_WINDOW)
print(checked.stdout,end='',flush=True)
if checked.returncode:print(checked.stderr,file=sys.stderr);raise SystemExit(checked.returncode)
from gpu_tts_hold import check_gpu_tts_hold
from gpu_handoff_guard import schedule_gpu_handoff
check_gpu_tts_hold('game-lighting-history-04','cuda:0',dry)
schedule_gpu_handoff('game-lighting-history-04','cuda:0',dry)
# A cooperative queue wait may outlive a content update. Recheck before loading.
verify()
checked=subprocess.run(['node','scripts/review-video-duplicates.cjs','game-lighting-history-04','--candidate-file','production/research/game-lighting-history/candidate-04.json','--check'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',creationflags=subprocess.CREATE_NO_WINDOW)
if checked.returncode:print(checked.stderr,file=sys.stderr);raise SystemExit(checked.returncode)
import render_narration
if not dry:
    import psutil,torch
    from qwen_tts import Qwen3TTSModel
    torch.set_num_threads(2)
    loader=Qwen3TTSModel.from_pretrained.__func__
    def load(cls,*args,**kwargs):kwargs.setdefault('attn_implementation','sdpa');return loader(cls,*args,**kwargs)
    Qwen3TTSModel.from_pretrained=classmethod(load)
    badness=render_narration._badness
    def passing(tail,decay):
        score=badness(tail,decay)
        return score if render_narration._passes_quality(tail,decay) else 1000000+score
    render_narration._badness=passing
    me=psutil.Process()
    lease=json.loads((ROOT/'shared/output/GPU_HANDOFF.json').read_text('utf-8-sig'))
    state=dict(schemaVersion=1,startedAt=time.time(),actualPid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),cwd=str(ROOT),status='24-reviewed-additions-synthesizing',cpuThreads=2,gpuJobs=1,batchSize=1,leaseToken=lease['token'],results=[],generationComplete=False,original87Regenerated=False,wholeNewAsrApproved=False,independentContextAsrApproved=False,finalMixedAsrApproved=False,finalVideoProduced=False,researchRestoredVerified=False)
    target=BASE/'additive-tts-execution-v1.json'
    def save():
        tmp=target.with_name(target.name+'.writing-'+str(os.getpid()))
        tmp.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(tmp,target)
    if target.exists():raise SystemExit('Preserve existing execution; inspect actual checkpoint before a scoped resume')
    save()
sys.argv=[sys.argv[0],'--project','game-lighting-history-04','--manifest',request['manifestOverride'],'--device','cuda:0','--batch-size','1']+(['--dry-run'] if dry else [])
try:
    render_narration.main()
    if not dry:
        import soundfile as sf
        for s in request['scenes']:
            p=ROOT/s['path'];data,sr=sf.read(p,dtype='float32',always_2d=False)
            tail=render_narration._tail_ratio(data,sr);decay=render_narration._tail_decay_ms(data,sr)
            state['results'].append(dict(id=s['id'],path=s['path'],sha256=sha(p),samples=len(data),sampleRate=sr,seconds=len(data)/sr,tailRatio=tail,tailDecayMs=decay,technicalTailGatePassed=render_narration._passes_quality(tail,decay),asrDirectlyReviewed=False))
        verify()
        bad=[r['id'] for r in state['results'] if not r['technicalTailGatePassed']]
        if bad:raise RuntimeError('Preserve all takes; scoped tail review required: '+','.join(bad))
        state.update(status='24-additions-generated-awaiting-whole-and-independent-ASR',generationComplete=True,exitCode=0,endedAt=time.time(),gpuJobs=0);save()
except BaseException as exc:
    if not dry:state.update(status='failed-preserve-current-takes-and-restore-research',exitCode=1,error=str(exc),endedAt=time.time(),gpuJobs=0);save()
    raise
