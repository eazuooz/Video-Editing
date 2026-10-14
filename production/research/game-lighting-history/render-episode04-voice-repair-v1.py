"""Six reviewed continuous subchapters only; original fourteen takes remain intact."""
from pathlib import Path
import hashlib,json,subprocess,sys,os,time
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'projects/game-lighting-history-04/production'
sys.path.insert(0,str(ROOT/'qwen3-tts'))
plan=json.loads((BASE/'voice-repair-plan-v1.json').read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
if not plan['allScopedKoEnTextDirectlyRead'] or not plan['allOriginalParagraphsPreserved']:
    raise SystemExit('Direct bilingual scoped review required')
for item in [*plan['inputHashes'],*plan['originalChunks']]:
    if sha(ROOT/item['path'])!=item['sha256']: raise SystemExit('Preserved input changed: '+item['path'])
if sha(ROOT/plan['originalAudio']['path'])!=plan['originalAudio']['sha256']:
    raise SystemExit('Original whole narration changed')
checked=subprocess.run(['node','scripts/review-video-duplicates.cjs','game-lighting-history-04','--candidate-file','production/research/game-lighting-history/candidate-04.json','--check'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',creationflags=subprocess.CREATE_NO_WINDOW)
print(checked.stdout,end='',flush=True)
if checked.returncode: print(checked.stderr,file=sys.stderr);raise SystemExit(checked.returncode)
from gpu_tts_hold import check_gpu_tts_hold
from gpu_handoff_guard import schedule_gpu_handoff
dry='--dry-run' in sys.argv
check_gpu_tts_hold('game-lighting-history-04','cuda:0',dry)
schedule_gpu_handoff('game-lighting-history-04','cuda:0',dry)
import render_narration
if not dry:
    import torch,psutil
    from qwen_tts import Qwen3TTSModel
    torch.set_num_threads(2)
    loader=Qwen3TTSModel.from_pretrained.__func__
    def load(cls,*args,**kwargs):
        kwargs.setdefault('attn_implementation','sdpa');return loader(cls,*args,**kwargs)
    Qwen3TTSModel.from_pretrained=classmethod(load)
    badness=render_narration._badness
    def passing(tail,decay):
        score=badness(tail,decay)
        return score if render_narration._passes_quality(tail,decay) else 1000000+score
    render_narration._badness=passing
    me=psutil.Process()
    state=dict(startedAt=time.time(),pid=me.pid,createTime=me.create_time(),command=me.cmdline(),cwd=str(ROOT),status='six-scoped-chunks-synthesizing',cpuThreads=2,gpuJobs=1,mainManifestChanged=False,fullOriginalNarrationPreserved=True,currentNarrationApproved=False,humanWholeListeningApproved=False,finalVideoProduced=False)
    def save(): (BASE/'voice-repair-execution-v1.json').write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    save()
sys.argv=[sys.argv[0],'--project','game-lighting-history-04','--manifest',plan['manifest'],'--device','cuda:0','--batch-size','1']+(['--dry-run'] if dry else [])
try:
    render_narration.main()
    if not dry:
        for item in plan['originalChunks']:
            if sha(ROOT/item['path'])!=item['sha256']: raise RuntimeError('Original chunk changed')
        if sha(ROOT/plan['originalAudio']['path'])!=plan['originalAudio']['sha256']: raise RuntimeError('Original whole narration changed')
        state.update(status='six-scoped-chunks-generated-awaiting-current-ASR',exitCode=0,endedAt=time.time(),gpuJobs=0)
        save()
except BaseException as exc:
    if not dry: state.update(status='failed-preserve-scoped-chunks-and-restore-research',exitCode=1,error=str(exc),endedAt=time.time());save()
    raise
