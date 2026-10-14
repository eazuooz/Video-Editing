"""Only five reviewed framing paragraphs, one cooperative GPU handoff."""
from pathlib import Path
import hashlib,json,os,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'projects/game-lighting-history-04/production'
NODE=Path('C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe')
sys.path.insert(0,str(ROOT/'qwen3-tts'))
request=json.loads((BASE/'physical-framing-tts-request-v49.json').read_text('utf-8'))
review=json.loads((ROOT/request['scriptReview']).read_text('utf-8'))
dry='--dry-run' in sys.argv
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify(check_current_duplicate=True):
    if len(request['scenes'])!=5 or not review['fullFiveKoEnDirectlyRead'] or not review['original111TextAndSelectedPcmPreserved']:
        raise SystemExit('Five paired framing paragraphs and preserved111 PCM required')
    for f in request['protectedInputs']:
        if sha(ROOT/f['path'])!=f['sha256']:raise SystemExit('Reviewed input changed: '+f['path'])
    if check_current_duplicate:
        checked=subprocess.run([str(NODE),'scripts/review-video-duplicates.cjs','game-lighting-history-04','--candidate-file','production/research/game-lighting-history/candidate-04.json','--check'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',creationflags=subprocess.CREATE_NO_WINDOW)
        print(checked.stdout,end='',flush=True)
        if checked.returncode:raise SystemExit(checked.stderr)
verify()
from gpu_tts_hold import check_gpu_tts_hold
from gpu_handoff_guard import schedule_gpu_handoff
check_gpu_tts_hold('game-lighting-history-04','cuda:0',dry)
schedule_gpu_handoff('game-lighting-history-04','cuda:0',dry)
verify()
import render_narration
if not dry:
    import psutil,torch
    from qwen_tts import Qwen3TTSModel
    torch.set_num_threads(2)
    loader=Qwen3TTSModel.from_pretrained.__func__
    def load(cls,*args,**kwargs):
        kwargs.setdefault('attn_implementation','sdpa')
        return loader(cls,*args,**kwargs)
    Qwen3TTSModel.from_pretrained=classmethod(load)
    badness=render_narration._badness
    def passing(tail,decay):
        score=badness(tail,decay)
        return score if render_narration._passes_quality(tail,decay) else 1000000+score
    render_narration._badness=passing
    me=psutil.Process();lease=json.loads((ROOT/'shared/output/GPU_HANDOFF.json').read_text('utf-8-sig'))
    target=BASE/'physical-framing-tts-execution-v49.json'
    if target.exists():raise SystemExit('Preserve existing execution; no repeated batch')
    state=dict(schemaVersion=1,startedAt=time.time(),actualPid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),cwd=str(ROOT),status='five-reviewed-framing-paragraphs-synthesizing',cpuThreads=2,gpuJobs=1,batchSize=1,leaseToken=lease['token'],results=[],generationComplete=False,original111Regenerated=False,wholeNewAsrApproved=False,independentContextAsrApproved=False,finalMixedAsrApproved=False,finalVideoProduced=False,researchRestoredVerified=False)
    def save():
        tmp=target.with_name(target.name+'.writing-'+str(os.getpid()))
        tmp.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(tmp,target)
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
        # The current gate was checked immediately before model creation. A
        # concurrent unrelated inventory change after generation requires a new
        # content review before delivery, not regenerating these preserved takes.
        verify(check_current_duplicate=False)
        bad=[r['id'] for r in state['results'] if not r['technicalTailGatePassed']]
        if bad:raise RuntimeError('Preserve takes for scoped review: '+','.join(bad))
        state.update(status='five-framing-paragraphs-generated-awaiting-whole-and-independent-ASR',generationComplete=True,exitCode=0,endedAt=time.time(),gpuJobs=0);save()
except BaseException as exc:
    if not dry:state.update(status='failed-preserve-takes-and-restore-research',exitCode=1,error=str(exc),endedAt=time.time(),gpuJobs=0);save()
    raise
